"""Kanal stres bindirmeleri (banka_kos/stres.py; BANKA §5.4, BK-8): nesneler, bloklar, olay seçimi, çarpan."""
import sys as _sys
import unittest
from pathlib import Path as _Path

import numpy as np

V8_DIR = _Path(__file__).resolve().parent.parent
if str(V8_DIR) not in _sys.path:
    _sys.path.insert(1, str(V8_DIR))

from banka_kos import stres  # noqa: E402


class NesneTest(unittest.TestCase):
    def test_nesneler(self):
        w = [{'BTCUSDT': 0.5, 'A': 0.03, 'B': 0.02, 'C': 0.01, 'D': 0.005, 'E': -0.02, 'F': -0.035},
             {'BTCUSDT': -0.3}, {}]
        n = stres.nesneler(w)
        np.testing.assert_allclose(n['D90'], [0.03, 0.0, 0.0])
        np.testing.assert_allclose(n['SQ'], [0.035, 0.0, 0.0])
        np.testing.assert_allclose(n['DM'], [0.06, 0.0, 0.0])


class BlokTest(unittest.TestCase):
    def test_bloklar(self):
        self.assertEqual(stres.bloklar(800, 1), [(0, 365), (365, 730)])          # 70 < 182,5: son blok yok
        self.assertEqual(stres.bloklar(913, 1), [(0, 365), (365, 730), (730, 913)])  # 183 ≥ 182,5
        self.assertEqual(stres.bloklar(400, 4)[-1], (273, 364))                  # L = 91; artık 36 < 45,5: olay yok
        self.assertEqual(len(stres.bloklar(410, 4)), 5)                          # artık 46 ≥ 45,5: olay var

    def test_olay_secimi_esitlikte_onceki(self):
        n = np.zeros(730)
        n[10] = n[20] = 0.05
        n[400] = 0.02
        self.assertEqual(stres.olaylar(n, 1), [10, 400])
        self.assertEqual(stres.olaylar(np.zeros(365), 1), [None])


class BindirmeTest(unittest.TestCase):
    def test_carpan_ve_sonraki_dahil_gun(self):
        r = np.full(365, 0.001)
        n = np.zeros(365)
        n[100] = 0.04
        dahil = np.ones(365, dtype=bool)
        dahil[101] = False                                                     # görülmüş gün: şok bir sonrakine
        s = stres.bindir(r, n, 'D90', 1, dahil)
        self.assertAlmostEqual(s['r'][102], 1.001 * (1 - 0.9 * 0.04) - 1, places=15)
        self.assertEqual(s['r'][101], 0.001)
        self.assertEqual(s['olay_gunleri'], [100])
        sq = stres.bindir(r, n, 'SQ', 1)
        self.assertAlmostEqual(sq['r'][101], 1.001 * (1 - 3.0 * 0.04) - 1, places=15)
        bos = stres.bindir(r, np.zeros(365), 'DM', 1)
        self.assertEqual(bos['bos_olay'], 1)
        np.testing.assert_array_equal(bos['r'], r)

    def test_son_gun_olay(self):
        r = np.zeros(365)
        n = np.zeros(365)
        n[364] = 0.1
        s = stres.bindir(r, n, 'D90', 1)
        self.assertAlmostEqual(s['r'][364], -0.09, places=15)


if __name__ == '__main__':
    unittest.main()
