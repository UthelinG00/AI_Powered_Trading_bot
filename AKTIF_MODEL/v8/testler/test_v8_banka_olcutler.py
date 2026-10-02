"""Banka olcutleri (BANKA_ONKAYIT_TASLAK Ss3.1, Ss3.3, Ss3.4): elle hesaplanmis degerler ve belgedeki sayilarla."""
import math
import sys as _sys
import unittest
from pathlib import Path as _Path

import numpy as np

V8_DIR = _Path(__file__).resolve().parent.parent
if str(V8_DIR) not in _sys.path:
    _sys.path.insert(1, str(V8_DIR))

from banka import olcutler as o  # noqa: E402


class SharpeTest(unittest.TestCase):
    def test_elle(self):
        r = [0.01, -0.01, 0.02, 0.0]
        m, s = 0.005, math.sqrt(((0.005) ** 2 + (0.015) ** 2 + (0.015) ** 2 + (0.005) ** 2) / 3)
        self.assertAlmostEqual(o.sharpe(r), m / s * math.sqrt(365), places=12)

    def test_tanimsiz(self):
        self.assertTrue(math.isnan(o.sharpe([0.01])))
        self.assertTrue(math.isnan(o.sharpe([0.01, 0.01, 0.01])))
        with self.assertRaises(ValueError):
            o.sharpe([0.01, float('nan')])


class DsrTest(unittest.TestCase):
    def test_sr0_belge_tablosu(self):
        # Ss3.3 tablosu: N = 323, sigma_SR 0,20/0,30/0,50 -> SR0 ~ 0,58/0,88/1,46 (yillik, kalem-kagit).
        for sig, beklenen in ((0.20, 0.58), (0.30, 0.88), (0.50, 1.46)):
            self.assertAlmostEqual(o.sr0(323, sig) * math.sqrt(365), beklenen, delta=0.01)

    def test_sr_esit_sr0_ise_yarim(self):
        rng = np.random.default_rng(1)
        r = rng.standard_normal(1000) * 0.01
        d = o.dsr(r, 323, 0.30)
        z = d['sr_gunluk']
        # sigma_SR'yi, SR0 = gozlenen SR olacak bicimde sec: DSR = 0,5 olmali.
        k = o.sr0(323, 1.0)
        d2 = o.dsr(r, 323, z / k)
        self.assertAlmostEqual(d2['dsr'], 0.5, places=12)

    def test_formul_elle(self):
        rng = np.random.default_rng(2)
        r = 0.001 + rng.standard_normal(500) * 0.02
        d = o.dsr(r, 100, 0.3)
        sr = np.mean(r) / np.std(r, ddof=1)
        g3, g4 = o.anlar(r)
        beklenen = o._N.cdf((sr - o.sr0(100, 0.3)) * math.sqrt(499)
                            / math.sqrt(d['eta'] * (1 - g3 * sr + (g4 - 1) / 4 * sr * sr)))
        self.assertAlmostEqual(d['dsr'], beklenen, places=12)
        self.assertEqual(d['T'], 500)

    def test_eta(self):
        rng = np.random.default_rng(3)
        e = rng.standard_normal(20000)
        self.assertAlmostEqual(o.eta(e), 1.0, delta=0.05)
        ar = np.zeros(20000)
        for t in range(1, len(ar)):
            ar[t] = 0.5 * ar[t - 1] + e[t]
        # rho_k = 0,5^k: 1 + 2 * sum (1 - k/11) 0,5^k
        beklenen = 1 + 2 * sum((1 - k / 11) * 0.5 ** k for k in range(1, 11))
        self.assertAlmostEqual(o.eta(ar), beklenen, delta=0.15)
        alt = np.array([(-1) ** t for t in range(100)], dtype=float)
        self.assertEqual(o.eta(alt), 1.0)          # negatif bagimlilik asagi duzeltmez


class DilimTest(unittest.TestCase):
    def test_en_iyi_dilim_haric(self):
        r = np.array([0.01, 0.02, -0.01, 0.005, 0.03, 0.04, -0.02, 0.0])
        et = np.array([0, 0, 1, 1, 2, 2, 3, 3])
        sr, cikan = o.en_iyi_dilim_haric(r, et)
        self.assertEqual(cikan, 2)
        self.assertAlmostEqual(sr, o.sharpe(r[et != 2]), places=12)
        self.assertEqual([math.isnan(x) for x in o.dilim_sharpeleri(r, et)], [False] * 4)


class DigerTest(unittest.TestCase):
    def test_epizot_payi(self):
        self.assertEqual(o.epizot_payi([5, 1, 3, -2], 0.0), float('inf'))
        self.assertAlmostEqual(o.epizot_payi([5, 1, 3, -2, 4], 11.0), 12 / 11)
        self.assertAlmostEqual(o.epizot_payi([2], 4.0), 0.5)

    def test_en_buyuk_dusus(self):
        self.assertAlmostEqual(o.en_buyuk_dusus(1.0, [0.9, 0.6, 1.1]), 0.4)
        self.assertEqual(o.en_buyuk_dusus(1.0, [0.9, float('nan')]), float('inf'))
        self.assertEqual(o.en_buyuk_dusus(1.0, []), 0.0)

    def test_mdd_ve_olcek(self):
        self.assertAlmostEqual(o.mdd([1.0, 1.2, 0.9, 1.3, 1.04]), 0.25)
        r = np.array([0.01, -0.02, 0.015, -0.01, 0.005] * 20)
        c = 0.15 / (np.std(r, ddof=1) * math.sqrt(365))
        nav = np.concatenate(([1.0], np.cumprod(1 + c * r)))
        self.assertAlmostEqual(o.vol_olcekli_mdd(r), o.mdd(nav), places=12)

    def test_wilson(self):
        p, alt, ust = o.wilson(0, 100)
        self.assertEqual((p, alt), (0.0, 0.0))
        self.assertAlmostEqual(ust, 0.0370, places=4)          # belge Ss3.7: %3,70
        self.assertAlmostEqual(o.wilson(5, 100)[2], 0.1118, places=4)   # belge Ss3.7: %11,18


if __name__ == '__main__':
    unittest.main()
