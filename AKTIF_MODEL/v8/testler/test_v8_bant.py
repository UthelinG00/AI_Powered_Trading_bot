"""MIMARI Ss3.6 islem bandi. Sentetik agirliklar, gercek islem yok."""
import sys as _sys
import unittest
from pathlib import Path as _Path

import numpy as np

V8_DIR = _Path(__file__).resolve().parents[1]
if str(V8_DIR) not in _sys.path:
    _sys.path.insert(1, str(V8_DIR))

from motor.bant import BantGirdiHatasi, bant_uygula  # noqa: E402
from motor.tipler import Parametreler  # noqa: E402

P = Parametreler()


class BandIcindeTest(unittest.TestCase):
    def test_band_icindeyse_degismez(self):
        # w_hedef=0.10 -> b=max(0.20*0.10, 0.002)=0.02; [0.08, 0.12] araligi.
        w_hedef = np.array([0.10])
        w_mevcut = np.array([0.09])
        ekstra = np.array([False])
        sonuc = bant_uygula(w_hedef, w_mevcut, ekstra, P)
        np.testing.assert_allclose(sonuc.w, w_mevcut)
        self.assertFalse(sonuc.islem_yapildi[0])
        self.assertAlmostEqual(sonuc.band_genisligi[0], 0.02, places=9)

    def test_band_disinda_en_yakin_sinira_gider_ust(self):
        w_hedef = np.array([0.10])
        w_mevcut = np.array([0.15])  # ust sinir 0.12'nin uzerinde
        sonuc = bant_uygula(w_hedef, w_mevcut, np.array([False]), P)
        self.assertAlmostEqual(sonuc.w[0], 0.12, places=9)
        self.assertTrue(sonuc.islem_yapildi[0])

    def test_band_disinda_en_yakin_sinira_gider_alt(self):
        w_hedef = np.array([0.10])
        w_mevcut = np.array([0.05])  # alt sinir 0.08'in altinda
        sonuc = bant_uygula(w_hedef, w_mevcut, np.array([False]), P)
        self.assertAlmostEqual(sonuc.w[0], 0.08, places=9)

    def test_kucuk_hedefte_taban_genislik(self):
        # w_hedef=0.005 -> 0.20*0.005=0.001 < taban 0.002, taban kullanilir.
        w_hedef = np.array([0.005])
        sonuc = bant_uygula(w_hedef, np.array([0.005]), np.array([False]), P)
        self.assertAlmostEqual(sonuc.band_genisligi[0], P.bant_taban, places=9)


class BandGecersizTest(unittest.TestCase):
    def test_hedef_sifir_dogrudan_kapanir(self):
        sonuc = bant_uygula(np.array([0.0]), np.array([0.10]), np.array([False]), P)
        self.assertAlmostEqual(sonuc.w[0], 0.0, places=12)
        self.assertTrue(sonuc.gecersiz[0])

    def test_isaret_uyumsuzlugu_dogrudan_hedefe(self):
        sonuc = bant_uygula(np.array([0.10]), np.array([-0.10]), np.array([False]), P)
        self.assertAlmostEqual(sonuc.w[0], 0.10, places=12)
        self.assertTrue(sonuc.gecersiz[0])

    def test_sifirdan_acilis_dogrudan_hedefe(self):
        # w_mevcut=0 (pozisyon yok), w_hedef>0 -> sign(0)=0 != sign(hedef) -> gecersiz, direkt hedefe.
        sonuc = bant_uygula(np.array([0.10]), np.array([0.0]), np.array([False]), P)
        self.assertAlmostEqual(sonuc.w[0], 0.10, places=12)
        self.assertTrue(sonuc.gecersiz[0])

    def test_ekstra_gecersiz_bayragi_dogrudan_hedefe(self):
        # Band icinde olsa bile ekstra_gecersiz=True (maske/evren cikisi/isim tavani asimi) -> dogrudan hedef.
        sonuc = bant_uygula(np.array([0.10]), np.array([0.10]), np.array([True]), P)
        self.assertAlmostEqual(sonuc.w[0], 0.10, places=12)
        self.assertTrue(sonuc.gecersiz[0])


class CokluIsimTest(unittest.TestCase):
    def test_karisik_durumlar_birlikte(self):
        w_hedef = np.array([0.10, 0.0, 0.10, 0.10])
        w_mevcut = np.array([0.09, 0.05, -0.10, 0.20])
        ekstra = np.array([False, False, False, False])
        sonuc = bant_uygula(w_hedef, w_mevcut, ekstra, P)
        self.assertAlmostEqual(sonuc.w[0], 0.09)   # band icinde
        self.assertAlmostEqual(sonuc.w[1], 0.0)    # hedef sifir
        self.assertAlmostEqual(sonuc.w[2], 0.10)   # isaret uyumsuz -> dogrudan hedef
        self.assertAlmostEqual(sonuc.w[3], 0.12)   # band disi, en yakin (ust) sinir


class GirdiHatasiTest(unittest.TestCase):
    def test_uzunluk_uyumsuzlugu_hata(self):
        with self.assertRaises(BantGirdiHatasi):
            bant_uygula(np.array([0.1, 0.2]), np.array([0.1]), np.array([False, False]), P)

    def test_bos_girdi_hata(self):
        with self.assertRaises(BantGirdiHatasi):
            bant_uygula(np.array([]), np.array([]), np.array([]), P)


if __name__ == '__main__':
    unittest.main()
