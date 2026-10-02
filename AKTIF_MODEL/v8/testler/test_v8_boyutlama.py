"""MIMARI Ss3.3 birim risk; N=15/R_EW=I Codex ornegi dahil. Sentetik veri, gercek islem yok."""
import sys as _sys
import unittest
from pathlib import Path as _Path

import numpy as np

V8_DIR = _Path(__file__).resolve().parents[1]
if str(V8_DIR) not in _sys.path:
    _sys.path.insert(1, str(V8_DIR))

from motor.boyutlama import BoyutlamaGirdiHatasi, birim_kitap  # noqa: E402
from motor.risk import sabit_korelasyon_matrisi  # noqa: E402
from motor.tipler import Parametreler  # noqa: E402

P = Parametreler()


class BirimKitapTest(unittest.TestCase):
    def test_codex_n15_rew_birim_ornegi(self):
        """R_EW = I (N=15) -> R_hat disi kosegen 0.35, 1'R_hat1=88.5, M~=1.59>1.5, referans vol ~%14.1."""
        n = 15
        r_ew = np.eye(n)
        r_s = sabit_korelasyon_matrisi(n, P)
        r_hat = 0.5 * r_ew + 0.5 * r_s
        toplam = float(np.ones(n) @ r_hat @ np.ones(n))
        self.assertAlmostEqual(toplam, 88.5, places=6)

        sigma = np.full(n, 0.20)
        sigma_hat_matris = np.diag(sigma) @ r_hat @ np.diag(sigma)
        sigma_sifir_matris = np.diag(sigma) @ np.eye(n) @ np.diag(sigma)
        s = np.ones(n)  # tam sinyalde, ayni yon (referans kitap)

        sonuc = birim_kitap(s, sigma, r_hat, sigma_hat_matris, sigma_sifir_matris, P)
        self.assertAlmostEqual(sonuc.m, 15 / np.sqrt(88.5), places=6)
        self.assertGreater(sonuc.m, P.m_max)  # M ~= 1.59, tavani asiyor
        self.assertAlmostEqual(sonuc.m_tilde, P.m_max, places=9)
        # s_i=1 hepsinde ayni yonde -> w_u tam referans kitaptir; V(w_u) = tau*m_tilde/m (referans vol formulu).
        beklenen_v = P.tau * sonuc.m_tilde / sonuc.m
        self.assertAlmostEqual(sonuc.v_oncesi, beklenen_v, places=6)
        self.assertAlmostEqual(sonuc.v_oncesi, 0.1411, places=3)  # Codex: ~%14.1
        self.assertFalse(sonuc.guvenlik_olceklemesi_uygulandi)  # V < tau, guvenlik tetiklenmez
        self.assertLessEqual(sonuc.v_sonrasi, P.tau + 1e-9)  # T4-a degismezi

    def test_n1_ozel_durum_m_bir(self):
        r_hat = np.array([[1.0]])
        sigma = np.array([0.25])
        sigma_hat_matris = np.diag(sigma) @ r_hat @ np.diag(sigma)
        sigma_sifir_matris = sigma_hat_matris.copy()
        s = np.array([0.5])
        sonuc = birim_kitap(s, sigma, r_hat, sigma_hat_matris, sigma_sifir_matris, P)
        self.assertAlmostEqual(sonuc.m, 1.0, places=9)
        self.assertAlmostEqual(sonuc.m_tilde, 1.0, places=9)

    def test_guvenlik_olceklemesi_tetiklenir(self):
        """Sigma_hat matrisini yapay buyuterek V(w_u) > tau durumunu zorla; T4-a sonrasi V<=tau olmali."""
        n = 3
        r_hat = sabit_korelasyon_matrisi(n, P)
        sigma = np.full(n, 0.20)
        buyutme = 100.0  # V'yi tau'nun cok uzerine tasimak icin yapay carpan
        sigma_hat_matris = buyutme * (np.diag(sigma) @ r_hat @ np.diag(sigma))
        sigma_sifir_matris = buyutme * (np.diag(sigma) @ np.eye(n) @ np.diag(sigma))
        s = np.ones(n)
        sonuc = birim_kitap(s, sigma, r_hat, sigma_hat_matris, sigma_sifir_matris, P)
        self.assertGreater(sonuc.v_oncesi, P.tau)
        self.assertTrue(sonuc.guvenlik_olceklemesi_uygulandi)
        self.assertLessEqual(sonuc.v_sonrasi, P.tau * (1 + 1e-9))
        # Olcekleme orantili: w_u_son = w_u_once * (tau/v_oncesi)
        oran_beklenen = P.tau / sonuc.v_oncesi
        w_u_once = sonuc.k * (s / sigma)
        np.testing.assert_allclose(sonuc.w_u, w_u_once * oran_beklenen, rtol=1e-9)

    def test_bos_evren_hata(self):
        with self.assertRaises(BoyutlamaGirdiHatasi):
            birim_kitap([], [], np.zeros((0, 0)), np.zeros((0, 0)), np.zeros((0, 0)), P)

    def test_uzunluk_uyumsuzlugu_hata(self):
        with self.assertRaises(BoyutlamaGirdiHatasi):
            birim_kitap([0.1, 0.2], [0.2], np.eye(2), np.eye(2), np.eye(2), P)


if __name__ == '__main__':
    unittest.main()
