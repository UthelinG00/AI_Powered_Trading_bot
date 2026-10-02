"""Duzey 1 esik kurallari ve birlesik kabul (kalibrasyon/duzey1_esik.py)."""
import math
import sys as _sys
import unittest
from dataclasses import replace
from pathlib import Path as _Path

import numpy as np

V8_DIR = _Path(__file__).resolve().parent.parent
if str(V8_DIR) not in _sys.path:
    _sys.path.insert(1, str(V8_DIR))

from banka import olcutler as o  # noqa: E402
from kalibrasyon import duzey1 as d1  # noqa: E402
from kalibrasyon import duzey1_esik as e  # noqa: E402
from kalibrasyon.duzey1_olcut import ALANLAR, yol_olculeri  # noqa: E402


def _dizi(n, **alan):
    a = np.zeros((n, len(d1.SR_IZGARASI), len(ALANLAR)))
    for k, v in alan.items():
        a[:, :, e.IX[k]] = np.asarray(v, dtype=float)[:, None] if np.ndim(v) else v
    return a


class EsikTest(unittest.TestCase):
    def test_ayar_esigi(self):
        x = 0.001 * np.arange(1, 101)
        self.assertAlmostEqual(e.ayar_esigi(x, 0.95, 0.01), 0.10)
        t = e.ayar_esigi(x, 0.95, 0.01)
        self.assertGreaterEqual(float(np.mean(x < t)), 0.95)
        self.assertLess(float(np.mean(x < t - 0.01)), 0.95)                 # en kucuk
        self.assertAlmostEqual(e.ayar_esigi(np.full(20, 0.95), 0.95, 0.01), 0.96)   # tam izgara degeri: kesin buyuk
        self.assertEqual(e.ayar_esigi(np.array([0.1] * 90 + [np.nan] * 10), 0.95, 0.01), math.inf)

    def test_kurallar(self):
        s = {0: _dizi(100, b5=np.linspace(0.1, 0.5, 100), b10=np.linspace(0, 0.2, 100), b6=4),
             1: _dizi(100, b5=np.linspace(0.1, 0.7, 100), b10=np.linspace(0, 0.1, 100), b6=np.r_[[2] * 11, [3] * 89])}
        self.assertAlmostEqual(e.e_b5(s), e.ayar_esigi(s[1][:, e.REF, e.IX['b5']], 0.95, 0.01))
        self.assertGreater(e.e_b5(s), 0.6)
        self.assertAlmostEqual(e.e_b10(s), e.ayar_esigi(s[0][:, e.REF, e.IX['b10']], 0.95, 0.01))
        self.assertEqual(e.k_b6(s), 2)                    # ayar 1'de P(>= 3) = 0,89 < 0,90
        s[1][:11, :, e.IX['b6']] = 3
        self.assertEqual(e.k_b6(s), 3)


class KabulTest(unittest.TestCase):
    def test_dsr_vek_olcutlerle_ayni(self):
        yol = d1.yol_uret(9, 2)
        a = yol_olculeri(yol)
        X = d1.portfoy(yol.hatlar, yol.ayar, d1.SR_IZGARASI[3])
        self.assertAlmostEqual(float(e.dsr_vek(a, 300, 0.3)[3]), o.dsr(X, 300, 0.3)['dsr'], places=12)

    def test_her_olcut_veto(self):
        iyi = dict(b3_2=1.0, b3_3=0.5, b4=1.0, b5=0.1, b6=4, b8=1.0, b9=1.0, b10=0.05, b11=0.1,
                   sr_gunluk=0.2, g3=0.0, g4=3.0, eta=1.0, T=1277.0)
        k = e.Kurallar(N=300, sigma_sr=0.3, b2_bagli=True, d=0.5, e_b5=0.5, k_b6=3, e_b10=0.3)
        self.assertTrue(e.kabul(_dizi(1, **iyi), k).all())
        kotu = dict(b3_2=0.29, b3_3=0.0, b4=0.29, b5=0.5, b6=2, b8=0.0, b9=0.0, b10=0.3, b11=0.31, sr_gunluk=-0.1)
        for alan, deger in kotu.items():
            self.assertFalse(e.kabul(_dizi(1, **{**iyi, alan: deger}), k).any(), alan)
        self.assertTrue(e.kabul(_dizi(1, **{**iyi, 'b5': 0.9, 'b10': 0.9}), replace(k, e_b5=None, e_b10=None)).all())
        self.assertTrue(e.kabul(_dizi(1, **{**iyi, 'sr_gunluk': -0.1}), replace(k, b2_bagli=False)).all())
        self.assertFalse(e.kabul(_dizi(1, **{**iyi, 'b4': 0.35}), replace(k, b4_esik=e.AYAR_ESIK)).any())
        self.assertFalse(e.kabul(_dizi(1, **{**iyi, 'b8': np.nan}), k).any())       # nan kalir


if __name__ == '__main__':
    unittest.main()
