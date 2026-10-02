"""MIMARI Ss3.2 sigma/kovaryans; KC-13 PSD duzeltmesi. Sentetik veri, gercek islem yok."""
import sys as _sys
import unittest
from pathlib import Path as _Path

import numpy as np

TESTLER_DIR = _Path(__file__).resolve().parent
V8_DIR = TESTLER_DIR.parent
for _dir in (V8_DIR, TESTLER_DIR):
    if str(_dir) not in _sys.path:
        _sys.path.insert(1, str(_dir))

from motor.risk import (  # noqa: E402
    RiskGirdiHatasi,
    ciftli_ham_korelasyon,
    kovaryans_hazirla,
    psd_duzelt,
    sabit_korelasyon_matrisi,
    sigma_ewma_tahmin,
)
from motor.tipler import Parametreler  # noqa: E402
from fikstur.sentetik_veri import KC13_KARSI_ORNEK_KORELASYON, gunluk_fiyat_serisi  # noqa: E402

P = Parametreler()


class SigmaEwmaTest(unittest.TestCase):
    def test_sabit_getiride_sqrt365_carpi_c(self):
        c = 0.02
        r = np.full(400, c)
        sigma = sigma_ewma_tahmin(r, P)
        self.assertAlmostEqual(sigma, np.sqrt(365.0) * c, places=9)

    def test_elle_agirlikli_ortalama_dogrulama(self):
        rng = np.random.default_rng(20260927)
        r = rng.normal(0, 0.03, size=150)
        sigma = sigma_ewma_tahmin(r, P)
        n = len(r)
        yas = np.arange(n - 1, -1, -1)
        en_buyuk = 0.0
        for h in P.ewma_yariomurleri:
            a = 0.5 ** (yas / h)
            ewma_r2 = (a * r * r).sum() / a.sum()
            en_buyuk = max(en_buyuk, np.sqrt(365.0 * ewma_r2))
        self.assertAlmostEqual(sigma, en_buyuk, places=9)

    def test_eksik_gun_nan_disarida_kalir(self):
        r = np.array([0.01, np.nan, 0.01, np.nan, 0.01] * 40)
        sigma = sigma_ewma_tahmin(r, P)
        self.assertTrue(np.isfinite(sigma))
        self.assertGreater(sigma, 0.0)

    def test_bos_dizi_hata(self):
        with self.assertRaises(RiskGirdiHatasi):
            sigma_ewma_tahmin(np.array([np.nan, np.nan]), P)


class CiftliKorelasyonTest(unittest.TestCase):
    def test_tam_pozitif_korelasyon(self):
        rng = np.random.default_rng(1)
        r0 = rng.normal(0, 0.02, 100)
        R = ciftli_ham_korelasyon([r0, r0.copy()], P)
        self.assertAlmostEqual(R[0, 1], 1.0, places=9)
        self.assertEqual(R[0, 0], 1.0)
        self.assertEqual(R[1, 1], 1.0)

    def test_tam_negatif_korelasyon(self):
        rng = np.random.default_rng(2)
        r0 = rng.normal(0, 0.02, 100)
        R = ciftli_ham_korelasyon([r0, -r0], P)
        self.assertAlmostEqual(R[0, 1], -1.0, places=9)

    def test_az_ortak_gunde_r_sabit(self):
        n = 100
        r0 = np.full(n, np.nan)
        r1 = np.full(n, np.nan)
        r0[-30:] = 0.01
        r1[-30:] = 0.01  # yalniz 30 ortak gun, min_ortak_gun=60'in altinda
        R = ciftli_ham_korelasyon([r0, r1], P)
        self.assertEqual(R[0, 1], P.r_sabit)

    def test_simetrik_ve_kosegen_bir(self):
        rng = np.random.default_rng(3)
        getiriler = [rng.normal(0, 0.02, 90) for _ in range(4)]
        R = ciftli_ham_korelasyon(getiriler, P)
        np.testing.assert_array_equal(np.diag(R), np.ones(4))
        np.testing.assert_allclose(R, R.T)


class PsdDuzeltmeTest(unittest.TestCase):
    def test_kc13_karsi_ornegi_harman_sonrasi_psd(self):
        """Codex'in karsi ornegi: R_ham disi kosegenleri (0.9, 0.9, -0.9). Duzeltmeden once harman
        (0.8, 0.8, -0.1) v=(-1, 0.5, 0.5) icin -0.15 verir (PSD degil). Duzeltmeden sonra PSD olmali."""
        r_ham = KC13_KARSI_ORNEK_KORELASYON
        # Ham matrisin gercekten PSD olmadigini dogrula (sanity check).
        self.assertLess(np.linalg.eigvalsh(r_ham).min(), 0.0)
        # Harmanlanmamis (duzeltilmemis) haliyle sorunu yeniden uret: Codex'in v'siyle -0.15.
        r_s = sabit_korelasyon_matrisi(3, P)
        harman_duzeltmesiz = 0.5 * r_ham + 0.5 * r_s
        v = np.array([-1.0, 0.5, 0.5])
        self.assertAlmostEqual(float(v @ harman_duzeltmesiz @ v), -0.15, places=9)

        # Duzeltmeden sonra: R_EW PSD, kosegen 1, simetrik.
        sonuc = psd_duzelt(r_ham, P)
        r_ew = sonuc.r_ew
        self.assertGreaterEqual(np.linalg.eigvalsh(r_ew).min(), -1e-10)
        np.testing.assert_allclose(np.diag(r_ew), np.ones(3), atol=1e-9)
        np.testing.assert_allclose(r_ew, r_ew.T)
        self.assertGreater(sonuc.kirpilan_ozdeger_sayisi, 0)

        # Harman (0.5*R_EW + 0.5*R_S) artik PSD; ayni v icin negatif deger uretmemeli.
        r_hat = 0.5 * r_ew + 0.5 * r_s
        self.assertGreaterEqual(float(v @ r_hat @ v), -1e-9)
        self.assertGreaterEqual(np.linalg.eigvalsh(r_hat).min(), 0.15 - 1e-9)

    def test_zaten_psd_matriste_kirpma_yok(self):
        r_ham = sabit_korelasyon_matrisi(5, P)
        sonuc = psd_duzelt(r_ham, P)
        self.assertEqual(sonuc.kirpilan_ozdeger_sayisi, 0)
        np.testing.assert_allclose(sonuc.r_ew, r_ham, atol=1e-8)

    def test_n1_ozel_durum(self):
        sonuc = psd_duzelt(np.array([[1.0]]), P)
        np.testing.assert_array_equal(sonuc.r_ew, np.array([[1.0]]))


class SabitKorelasyonTest(unittest.TestCase):
    def test_ozdegerler_spesifikasyonla_eslesir(self):
        n = 6
        R = sabit_korelasyon_matrisi(n, P)
        ozdegerler = np.sort(np.linalg.eigvalsh(R))
        self.assertAlmostEqual(ozdegerler[0], 1 - P.r_sabit, places=9)
        self.assertAlmostEqual(ozdegerler[-1], 1 + (n - 1) * P.r_sabit, places=9)


class KovaryansHazirlaTest(unittest.TestCase):
    def test_n0_hata(self):
        with self.assertRaises(RiskGirdiHatasi):
            kovaryans_hazirla([], [], P)

    def test_n1_ozel_durum(self):
        sonuc = kovaryans_hazirla([np.array([0.01, 0.02])], [0.25], P)
        np.testing.assert_array_equal(sonuc.r_hat, np.array([[1.0]]))
        self.assertAlmostEqual(sonuc.sigma_hat[0, 0], 0.0625, places=9)

    def test_genel_durum_psd_ve_boyut(self):
        n = 8
        # Sekiz sentetik varlik: farkli trend/volatilite/tek-seferlik sok ile (paylasilan uretici).
        getiriler_log = [
            gunluk_fiyat_serisi(200, gunluk_oran=0.001 * (i - n / 2), volatilite=0.03,
                                 sok_gunu=150 if i == 3 else None, sok_buyuklugu=-0.15, tohum=100 + i)
            for i in range(n)
        ]
        getiriler = [np.diff(np.log(fiyat)) for fiyat in getiriler_log]
        # np.diff(log(...)) 199 uzunlukta; ciftli_ham_korelasyon icin butun dizilerin ayni uzunlukta
        # olmasi yeterli (n=200 fiyat -> 199 getiri), asagidaki cagrilar bunu zaten varsayar.
        sigma = np.full(n, 0.30)
        sonuc = kovaryans_hazirla(getiriler, sigma, P)
        self.assertEqual(sonuc.r_hat.shape, (n, n))
        self.assertGreaterEqual(np.linalg.eigvalsh(sonuc.r_hat).min(), 0.15 - 1e-9)
        np.testing.assert_allclose(np.diag(sonuc.r_hat), np.ones(n), atol=1e-9)
        # Sigma_hat = diag(sigma) R_hat diag(sigma)
        beklenen_sigma_hat = np.diag(sigma) @ sonuc.r_hat @ np.diag(sigma)
        np.testing.assert_allclose(sonuc.sigma_hat, beklenen_sigma_hat)
        # Sigma_0 kosegen, sigma^2
        np.testing.assert_allclose(np.diag(sonuc.sigma_sifir), sigma ** 2)


if __name__ == '__main__':
    unittest.main()
