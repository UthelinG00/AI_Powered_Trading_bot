"""Duzey 1 P&L ureteci (kalibrasyon/duzey1.py; BANKA_ONKAYIT_TASLAK Ss3.7): izgara, belgedeki sayilar, sigma_P,
hedef Sharpe, epizot uzunlugu, B9/B10 yardimci hatlari."""
import math
import sys as _sys
import unittest
from pathlib import Path as _Path

import numpy as np

V8_DIR = _Path(__file__).resolve().parent.parent
if str(V8_DIR) not in _sys.path:
    _sys.path.insert(1, str(V8_DIR))

from kalibrasyon import duzey1 as d1  # noqa: E402


class AyarTest(unittest.TestCase):
    def test_izgara(self):
        a0, a127 = d1.ayar(0), d1.ayar(127)
        self.assertEqual((a0.T_yil, a0.l_e, a0.s, a0.rho_f, a0.delta, a0.phi, a0.g), (3.0, 30, 0.75, 0.3, 0.05, 0.5, -1))
        self.assertEqual((a127.T_yil, a127.l_e, a127.s, a127.rho_f, a127.delta, a127.phi, a127.g),
                         (3.5, 60, 1.25, 0.6, 0.10, 1.5, 1))
        self.assertEqual(d1.ayar(64).T_yil, 3.5)
        self.assertEqual(d1.ayar(1).g, 1)
        self.assertEqual(len({d1.ayar(i) for i in range(128)}), 128)
        with self.assertRaises(ValueError):
            d1.ayar(128)

    def test_belge_sayilari(self):
        self.assertAlmostEqual(d1.ayar(0).sd_s, 1.151, places=3)
        self.assertAlmostEqual(d1.ayar(0b0010000).sd_s, 4.240, delta=0.002)     # belge "≈ 4,240"; kesin 4,2414
        self.assertEqual((d1.ayar(0).T, d1.ayar(64).T), (1095, 1277))
        self.assertEqual((d1.ayar(0).dilim_gun()[0], d1.ayar(64).dilim_gun()[0]), (191, 373))
        self.assertEqual(sum(d1.ayar(64).dilim_gun()), 1277)
        ay = d1.ayar(5)
        self.assertAlmostEqual(ay.m(1.0) + ay.F() - ay.K(), ay.sigma_P / math.sqrt(365))


class UretecTest(unittest.TestCase):
    def test_belirlenimli(self):
        a, b = d1.yol_uret(3, 7), d1.yol_uret(3, 7)
        self.assertTrue(np.array_equal(a.hatlar[4].x0, b.hatlar[4].x0))
        self.assertTrue(np.array_equal(a.ikame[9].epizot, b.ikame[9].epizot))
        self.assertFalse(np.array_equal(a.hatlar[0].x0, d1.yol_uret(3, 8).hatlar[0].x0))

    def test_sigma_P_ve_hedef_sharpe(self):
        for no in (0, 0b1010101):
            ay = d1.ayar(no)
            std, sr = [], []
            for y in range(1, 201):
                yol = d1.yol_uret(no, y)
                X = d1.portfoy(yol.hatlar, ay, 1.0)
                std.append(np.std(X))
                sr.append(np.mean(X) / np.std(X, ddof=1) * math.sqrt(365))
            self.assertAlmostEqual(float(np.mean(std)) / ay.sigma_P, 1.0, delta=0.05, msg=no)
            self.assertAlmostEqual(float(np.mean(sr)), 1.0, delta=0.1, msg=no)

    def test_epizot_uzunlugu(self):
        for no, l_e in ((0, 30), (0b0100000, 60)):
            yol = d1.yol_uret(no, 1)
            say = [len(np.unique(h.epizot)) for h in yol.hatlar]
            self.assertAlmostEqual(yol.ayar.T / float(np.mean(say)), l_e, delta=0.25 * l_e)

    def test_yardimci_hatlar(self):
        no = 0b0001000                               # rho_f 0,6; s 0,75; phi 0,5
        ay = d1.ayar(no)
        k_ikame, k_y = [], []
        for y in range(1, 41):
            yol = d1.yol_uret(no, y)
            k_ikame.append(np.corrcoef(yol.hatlar[0].x0, yol.ikame[0].x0)[0, 1])
            k_y.append(np.corrcoef(d1.portfoy(yol.hatlar, ay, 0.0), d1.portfoy(yol.y_hatlar, ay, 0.0))[0, 1])
        self.assertAlmostEqual(float(np.mean(k_ikame)), 0.6 / (1 + ay.a ** 2 * ay.sd_s ** 2), delta=0.05)
        self.assertAlmostEqual(float(np.mean(k_y)), 0.0, delta=0.03)

    def test_maliyet_carpani(self):
        yol = d1.yol_uret(2, 1)
        ay = yol.ayar
        X1, X3 = d1.portfoy(yol.hatlar, ay, 0.5, 1), d1.portfoy(yol.hatlar, ay, 0.5, 3)
        self.assertTrue(np.allclose(X1 - X3, 2 * ay.K()))


if __name__ == '__main__':
    unittest.main()
