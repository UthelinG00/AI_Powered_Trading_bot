"""MIMARI Ss1b HAR tahmincisi ve QLIKE (motor/har.py). Sentetik veri; D verisi yok."""
import math
import sys as _sys
import unittest
from pathlib import Path as _Path

import numpy as np

TESTLER_DIR = _Path(__file__).resolve().parent
V8_DIR = TESTLER_DIR.parent
for _dir in (V8_DIR, TESTLER_DIR):
    if str(_dir) not in _sys.path:
        _sys.path.insert(1, str(_dir))

from motor.gorunum import GUN_MS, SAAT_MS, saatlik_seri  # noqa: E402
from motor.har import (YILLIK_HAFTA, dairesel_blok_bootstrap, gunluk_rv, har_katsayi, har_log_tahmin,  # noqa: E402
                       har_ozellik, har_varyans, haftalik_hedef, qlike)
from motor.tipler import Parametreler  # noqa: E402

P = Parametreler()


def _seri(saatler, getiri):
    """saatler: bar acilis saat indeksleri; her bar kapanisi exp(getiri * sira)."""
    ms = np.array(saatler, dtype=np.int64) * SAAT_MS
    kap = np.exp(getiri * np.arange(len(ms)))
    return saatlik_seri(ms, kap, kap, kap, kap, np.ones(len(ms)))


class RvTest(unittest.TestCase):
    def test_tam_gun_ve_olcekleme(self):
        # 3 gun tam bar: gun 1 ve 2 icin 24 saatlik getiri (gece yarisini asan dahil).
        s = _seri(range(72), 0.01)
        rv = gunluk_rv(s, np.array([GUN_MS, 2 * GUN_MS, 3 * GUN_MS]), P)
        self.assertTrue(math.isclose(rv[1], 24 * 0.01 ** 2, rel_tol=1e-12))
        self.assertTrue(math.isclose(rv[2], 24 * 0.01 ** 2, rel_tol=1e-12))
        self.assertTrue(math.isclose(rv[0], 24 * 0.01 ** 2, rel_tol=1e-12))   # 23 getiri, 24/23 olcekli

    def test_eksik_getiri_esigi(self):
        # Gun 2'de ardisik k bar eksik -> k+1 getiri eksik. 7 bar -> 8 eksik: tanimli; 8 bar -> 9 eksik: tanimsiz.
        s4 = _seri([h for h in range(72) if not 30 <= h < 37], 0.01)
        s5 = _seri([h for h in range(72) if not 30 <= h < 38], 0.01)
        g = np.array([2 * GUN_MS])
        self.assertFalse(math.isnan(gunluk_rv(s4, g, P)[0]))
        self.assertTrue(math.isnan(gunluk_rv(s5, g, P)[0]))

    def test_donuk_fiyat_tanimsiz(self):
        s = _seri(range(48), 0.0)
        self.assertTrue(math.isnan(gunluk_rv(s, np.array([2 * GUN_MS]), P)[0]))


class OzellikHedefTest(unittest.TestCase):
    def test_ozellik_esikleri(self):
        rv = np.full(120, 1e-3)
        o = har_ozellik(rv, 100, P)
        for x in o:
            self.assertAlmostEqual(x, math.log(1e-3), places=12)
        self.assertIsNone(har_ozellik(rv, 88, P))            # 89 gun < 90 (capa)
        rv2 = rv.copy()
        rv2[97:100] = np.nan                                  # son 7 gunde 4 tanimli: yeter
        self.assertIsNotNone(har_ozellik(rv2, 100, P))
        rv2[96] = np.nan                                      # 3 tanimli: yetmez
        self.assertIsNone(har_ozellik(rv2, 100, P))
        rv3 = rv.copy()
        rv3[100] = np.nan
        self.assertIsNone(har_ozellik(rv3, 100, P))           # l1 tanimsiz

    def test_haftalik_hedef(self):
        r = np.full(20, 0.02)
        self.assertAlmostEqual(haftalik_hedef(r, 5), 7 * 0.0004, places=15)
        r[9] = np.nan
        self.assertIsNone(haftalik_hedef(r, 5))
        self.assertIsNone(haftalik_hedef(r, 15))              # yetersiz ileri gun


class RegresyonTest(unittest.TestCase):
    def test_bilinen_katsayilar_geri_bulunur(self):
        rng = np.random.default_rng(3)
        m = rng.normal(-8, 0.5, 400)
        l = m[:, None] + rng.normal(0, 0.4, (400, 3))
        oz = np.column_stack([l, m])
        beta = np.array([0.1, 0.3, 0.2, 0.35])
        y = m + beta[0] + (l - m[:, None]) @ beta[1:]
        np.testing.assert_allclose(har_katsayi(oz, y), beta, atol=1e-10)
        np.testing.assert_allclose(har_log_tahmin(oz, beta), y, atol=1e-10)

    def test_varyans_ve_qlike(self):
        self.assertAlmostEqual(float(har_varyans(math.log(0.01), 0.0)), YILLIK_HAFTA * 0.01, places=12)
        self.assertAlmostEqual(float(har_varyans(0.0, 0.2)), YILLIK_HAFTA * math.exp(0.1), places=12)
        self.assertEqual(float(qlike(2.0, 2.0)), 0.0)
        self.assertGreater(float(qlike(1.0, 2.0)), 0.0)
        self.assertGreater(float(qlike(3.0, 2.0)), 0.0)


class BootstrapTest(unittest.TestCase):
    def test_sabit_fark_ve_tohum(self):
        haftalar = [np.full(5, -0.1) for _ in range(40)]
        b = dairesel_blok_bootstrap(haftalar, 4, 200, 20260927)
        np.testing.assert_allclose(b, -0.1)
        hafta2 = [np.array([float(i)]) for i in range(40)]
        b1 = dairesel_blok_bootstrap(hafta2, 4, 50, 7)
        b2 = dairesel_blok_bootstrap(hafta2, 4, 50, 7)
        np.testing.assert_array_equal(b1, b2)
        self.assertTrue(np.all((b1 >= 0) & (b1 <= 39)))


class TurYediTest(unittest.TestCase):
    """Codex T7 on-kayit incelemesi: yetersiz egitim, bos takvim haftalari."""

    def test_yetersiz_egitim_tanimsiz(self):
        rng = np.random.default_rng(5)
        oz = np.column_stack([rng.normal(-8, 0.4, (40, 3)), np.full(40, -8.0)])
        y = rng.normal(-7, 0.5, 40)
        self.assertIsNone(har_katsayi(oz[:29], y[:29], P))                 # 29 < 30 gozlem
        self.assertIsNotNone(har_katsayi(oz, y, P))
        tekrarli = np.tile(oz[:1], (40, 1))                                  # rank 1
        self.assertIsNone(har_katsayi(tekrarli, y, P))
        self.assertIsNotNone(har_katsayi(oz[:5], y[:5]))                     # p verilmezse denetim yok

    def test_bos_takvim_haftasi(self):
        haftalar = [np.full(3, -0.1) if i % 2 == 0 else np.array([]) for i in range(40)]
        b = dairesel_blok_bootstrap(haftalar, 4, 100, 1)
        np.testing.assert_allclose(b, -0.1)


if __name__ == '__main__':
    unittest.main()
