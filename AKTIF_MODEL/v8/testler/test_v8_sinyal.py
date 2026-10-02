"""MIMARI Ss3.1 trend sinyali; sentetik fiyat, gercek islem veya ag yok."""
import math
import sys as _sys
import unittest
from pathlib import Path as _Path

V8_DIR = _Path(__file__).resolve().parents[1]
if str(V8_DIR) not in _sys.path:
    _sys.path.insert(1, str(V8_DIR))

from motor.sinyal import SinyalGirdiHatasi, trend_sinyali  # noqa: E402
from motor.tipler import Parametreler  # noqa: E402

P = Parametreler()


def sabit_buyume_serisi(n: int, gunluk_oran: float, p0: float = 100.0):
    """P_t = p0 * exp(oran * t); log getiri her ufukta tam oran*h olur (elle dogrulama icin)."""
    return [p0 * math.exp(gunluk_oran * t) for t in range(n)]


class TrendSinyaliTest(unittest.TestCase):
    def test_duz_fiyatta_sinyal_sifir(self):
        n = 100
        fiyatlar = [100.0] * n
        gecerli = [True] * n
        s = trend_sinyali(fiyatlar, gecerli, sigma_ewma=0.30, p=P)
        self.assertAlmostEqual(s, 0.0, places=12)

    def test_sabit_buyume_elle_hesapla(self):
        oran = 0.002  # gunluk log getiri
        n = 200
        fiyatlar = sabit_buyume_serisi(n, oran)
        gecerli = [True] * n
        sigma_ewma = 0.30
        sigma_sig = max(sigma_ewma, P.sigma_taban)
        beklenen = sum(
            math.tanh((oran * h) / (sigma_sig * math.sqrt(h / 365.0))) for h in P.ufuklar
        ) / len(P.ufuklar)
        s = trend_sinyali(fiyatlar, gecerli, sigma_ewma, P)
        self.assertAlmostEqual(s, beklenen, places=12)
        self.assertGreater(s, 0.0)  # yukselen fiyatta sinyal pozitif

    def test_dusen_fiyatta_sinyal_negatif(self):
        n = 200
        fiyatlar = sabit_buyume_serisi(n, -0.002)
        gecerli = [True] * n
        s = trend_sinyali(fiyatlar, gecerli, sigma_ewma=0.30, p=P)
        self.assertLess(s, 0.0)

    def test_eksik_ufuk_terimi_sifir_payda_sabit(self):
        # Yalnix 50 gunluk gecmis: h=84 ufku yok (index<0) -> o terim 0, payda yine 3.
        n = 50
        fiyatlar = sabit_buyume_serisi(n, 0.003)
        gecerli = [True] * n
        sigma_sig = max(0.30, P.sigma_taban)
        beklenen = 0.0
        for h in P.ufuklar:
            idx = n - 1 - h
            if idx < 0:
                continue
            getiri = math.log(fiyatlar[-1] / fiyatlar[idx])
            beklenen += math.tanh(getiri / (sigma_sig * math.sqrt(h / 365.0)))
        beklenen /= len(P.ufuklar)
        s = trend_sinyali(fiyatlar, gecerli, sigma_ewma=0.30, p=P)
        self.assertAlmostEqual(s, beklenen, places=12)

    def test_maskeli_gun_terimi_sifirlar(self):
        n = 200
        fiyatlar = sabit_buyume_serisi(n, 0.002)
        gecerli = [True] * n
        idx14 = n - 1 - 14
        gecerli[idx14] = False  # h=14 gunu maskeli -> o terim disarida kalmali
        s_maskeli = trend_sinyali(fiyatlar, gecerli, sigma_ewma=0.30, p=P)
        gecerli_tam = [True] * n
        s_tam = trend_sinyali(fiyatlar, gecerli_tam, sigma_ewma=0.30, p=P)
        self.assertNotAlmostEqual(s_maskeli, s_tam, places=6)
        sigma_sig = max(0.30, P.sigma_taban)
        beklenen = 0.0
        for h in P.ufuklar:
            if h == 14:
                continue
            getiri = math.log(fiyatlar[-1] / fiyatlar[n - 1 - h])
            beklenen += math.tanh(getiri / (sigma_sig * math.sqrt(h / 365.0)))
        beklenen /= len(P.ufuklar)
        self.assertAlmostEqual(s_maskeli, beklenen, places=12)

    def test_sigma_taban_kirpar(self):
        n = 200
        fiyatlar = sabit_buyume_serisi(n, 0.002)
        gecerli = [True] * n
        s_kucuk_sigma = trend_sinyali(fiyatlar, gecerli, sigma_ewma=0.01, p=P)
        s_daha_kucuk_sigma = trend_sinyali(fiyatlar, gecerli, sigma_ewma=0.001, p=P)
        # Ikisi de tabanin (0.20) altinda; sonuc ayni olmali (taban kirpiyor).
        self.assertAlmostEqual(s_kucuk_sigma, s_daha_kucuk_sigma, places=12)

    def test_sinyal_araligi(self):
        n = 200
        for oran in (0.05, -0.05, 0.002, -0.002, 0.0):
            fiyatlar = sabit_buyume_serisi(n, oran)
            gecerli = [True] * n
            s = trend_sinyali(fiyatlar, gecerli, sigma_ewma=0.30, p=P)
            with self.subTest(oran=oran):
                self.assertGreater(s, -1.0)
                self.assertLess(s, 1.0)

    def test_uzunluk_uyumsuzlugu_hata(self):
        with self.assertRaises(SinyalGirdiHatasi):
            trend_sinyali([100.0, 101.0], [True], sigma_ewma=0.3, p=P)

    def test_bugun_gecersiz_hata(self):
        n = 100
        fiyatlar = sabit_buyume_serisi(n, 0.001)
        gecerli = [True] * n
        gecerli[-1] = False
        with self.assertRaises(SinyalGirdiHatasi):
            trend_sinyali(fiyatlar, gecerli, sigma_ewma=0.3, p=P)

    def test_bugun_negatif_fiyat_hata(self):
        with self.assertRaises(SinyalGirdiHatasi):
            trend_sinyali([100.0, -5.0], [True, True], sigma_ewma=0.3, p=P)


if __name__ == '__main__':
    unittest.main()
