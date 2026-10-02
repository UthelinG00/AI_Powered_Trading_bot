"""MIMARI Ss3.5 Mimari A tavan cozucusu. Sentetik agirliklar, gercek islem yok."""
import dataclasses
import sys as _sys
import unittest
from pathlib import Path as _Path

import numpy as np

V8_DIR = _Path(__file__).resolve().parents[1]
if str(V8_DIR) not in _sys.path:
    _sys.path.insert(1, str(V8_DIR))

from motor.tavanlar import TavanGirdiHatasi, tavan_coz  # noqa: E402
from motor.tipler import Parametreler  # noqa: E402

P = Parametreler()


class IsimTavaniTest(unittest.TestCase):
    def test_asan_agirliklar_kirpilir(self):
        w = np.array([0.50, -0.50, 0.10, -0.08])   # BTC, ETH, alt-long, alt-short
        btc_eth = np.array([True, True, False, False])
        sonuc = tavan_coz(w, btc_eth, P)
        np.testing.assert_allclose(sonuc.w[:2], [0.35, -0.35])
        np.testing.assert_allclose(sonuc.w[2:], [0.06, -0.04])
        np.testing.assert_array_equal(sonuc.isim_kirpildi, [True, True, True, True])

    def test_tavan_icinde_degismez(self):
        w = np.array([0.10, -0.10, 0.03, -0.02])
        btc_eth = np.array([True, True, False, False])
        sonuc = tavan_coz(w, btc_eth, P)
        np.testing.assert_allclose(sonuc.w, w)
        np.testing.assert_array_equal(sonuc.isim_kirpildi, [False, False, False, False])


class BrutTavaniTest(unittest.TestCase):
    def test_asinca_tek_katsayiyla_kucultulur(self):
        # btc_eth=True -> isim tavani 0.35 (alt tavanindan (0.06) once bu testte devreye girmesin diye).
        n = 10
        w = np.full(n, 0.35)  # isim tavaninda tam; toplam brut = 3.5 > 2.0
        btc_eth = np.ones(n, dtype=bool)
        sonuc = tavan_coz(w, btc_eth, P)
        # Brut adiminin kendisi dogru katsayiyi uretir. (Bu senaryoda hepsi long ve BTC/ETH oldugundan,
        # brut sonrasi S1 da tetiklenip toplami daha da kucultur -- bu iki adimin ayri calistigini,
        # birbirini iptal etmedigini gosterir; nihai toplam bu yuzden 2.0'dan az olabilir.)
        self.assertAlmostEqual(sonuc.brut_katsayi, P.brut_tavan / 3.5, places=9)
        self.assertLessEqual(float(np.abs(sonuc.w).sum()), P.brut_tavan + 1e-9)


class SokSenaryolariTest(unittest.TestCase):
    def test_s1_tetiklenir_yalniz_long_kucultulur(self):
        # BTC, ETH tam tavanda long; 3 alt long tam tavanda -> Kayip_S1 = 0.7*0.18+0.3*0.70=0.336 > 0.20
        w = np.array([0.35, 0.35, 0.06, 0.06, 0.06])
        btc_eth = np.array([True, True, False, False, False])
        sonuc = tavan_coz(w, btc_eth, P)
        self.assertEqual(sonuc.turlar, 1)
        self.assertAlmostEqual(sonuc.s1_kayip_son, P.s1_sinir, places=6)
        self.assertAlmostEqual(sonuc.s2_kayip_son, 0.0, places=9)
        self.assertEqual(sonuc.s2_katsayi, 1.0)
        c1_beklenen = P.s1_sinir / 0.336
        self.assertAlmostEqual(sonuc.s1_katsayi, c1_beklenen, places=6)
        np.testing.assert_allclose(sonuc.w, w * c1_beklenen, rtol=1e-9)

    def test_s2_tetiklenir_yalniz_short_kucultulur(self):
        w = np.array([-0.35, -0.35, -0.04, -0.04, -0.04, -0.04])
        btc_eth = np.array([True, True, False, False, False, False])
        sonuc = tavan_coz(w, btc_eth, P)
        self.assertAlmostEqual(sonuc.s2_kayip_son, P.s2_sinir, places=6)
        self.assertEqual(sonuc.s1_katsayi, 1.0)
        self.assertAlmostEqual(sonuc.s1_kayip_son, 0.0, places=9)
        self.assertLess(sonuc.s2_katsayi, 1.0)
        # Kucultmeden sonra kitap hala isim tavanlarini asmiyor (S2 kucultmesi yalniz azaltir).
        self.assertTrue(np.all(np.abs(sonuc.w[2:]) <= P.isim_tavan_alt_short + 1e-9))

    def test_s1_ve_s2_ayni_anda_bagimsiz_uygulanir(self):
        w_long = np.array([0.35, 0.35, 0.06, 0.06, 0.06])
        w_short = np.array([-0.35, -0.35, -0.04, -0.04, -0.04, -0.04])
        w = np.concatenate([w_long, w_short])
        btc_eth = np.array([True, True, False, False, False, True, True, False, False, False, False])
        sonuc = tavan_coz(w, btc_eth, P)
        self.assertLess(sonuc.s1_katsayi, 1.0)
        self.assertLess(sonuc.s2_katsayi, 1.0)
        self.assertAlmostEqual(sonuc.s1_kayip_son, P.s1_sinir, places=5)
        self.assertAlmostEqual(sonuc.s2_kayip_son, P.s2_sinir, places=5)

    def test_ihlal_yoksa_katsayilar_bir(self):
        w = np.array([0.05, -0.05, 0.01, -0.01])
        btc_eth = np.array([True, True, False, False])
        sonuc = tavan_coz(w, btc_eth, P)
        self.assertEqual(sonuc.s1_katsayi, 1.0)
        self.assertEqual(sonuc.s2_katsayi, 1.0)
        self.assertEqual(sonuc.brut_katsayi, 1.0)
        self.assertEqual(sonuc.global_katsayi, 1.0)
        self.assertEqual(sonuc.turlar, 0)

    def test_dongu_tukenirse_son_care_global_kucultme(self):
        # tavan_max_tur=0 vererek dongu hic calismadan "hala ihlal" dalini test et.
        p0 = dataclasses.replace(P, tavan_max_tur=0)
        w = np.array([0.35, 0.35, 0.06, 0.06, 0.06])  # ayni S1 ornegi, Kayip_S1=0.336
        btc_eth = np.array([True, True, False, False, False])
        sonuc = tavan_coz(w, btc_eth, p0)
        self.assertEqual(sonuc.turlar, 0)
        self.assertLess(sonuc.global_katsayi, 1.0)
        self.assertAlmostEqual(sonuc.global_katsayi, p0.s1_sinir / 0.336, places=6)
        self.assertLessEqual(sonuc.s1_kayip_son, p0.s1_sinir + 1e-6)


class GirdiHatasiTest(unittest.TestCase):
    def test_bos_girdi_hata(self):
        with self.assertRaises(TavanGirdiHatasi):
            tavan_coz(np.array([]), np.array([], dtype=bool), P)

    def test_uzunluk_uyumsuzlugu_hata(self):
        with self.assertRaises(TavanGirdiHatasi):
            tavan_coz(np.array([0.1, 0.2]), np.array([True]), P)


if __name__ == '__main__':
    unittest.main()
