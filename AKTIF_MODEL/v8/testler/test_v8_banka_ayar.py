"""Banka koşusu ayarları (banka_kos/ayar.py; BANKA §3.1, §3.4, §4; BK-1, BK-7): T0_Z1 yuvarlaması, dilimler, birim listesi."""
import json
import sys as _sys
import unittest
from pathlib import Path as _Path

V8_DIR = _Path(__file__).resolve().parent.parent
if str(V8_DIR) not in _sys.path:
    _sys.path.insert(1, str(V8_DIR))

from banka_kos import ayar  # noqa: E402

G = ayar.GUN_MS


class DonemTest(unittest.TestCase):
    def test_t0_yuvarlama(self):
        # max(...) + 92 gün = 2020-02-27 -> 2020-03-01; tam ay başı 00:00 ise kendisi (BK-7).
        self.assertEqual(ayar.t0_z1(ayar._ms(2019, 9, 8), ayar._ms(2019, 11, 27)), ayar._ms(2020, 3, 1))
        self.assertEqual(ayar.t0_z1(ayar._ms(2019, 12, 1) - 92 * G, 0), ayar._ms(2019, 12, 1))
        self.assertEqual(ayar.t0_z1(ayar._ms(2019, 12, 1) - 92 * G + 3_600_000, 0), ayar._ms(2020, 1, 1))
        self.assertEqual(ayar.t0_z1(ayar._ms(2019, 12, 5) - 92 * G, 0), ayar._ms(2020, 1, 1))

    def test_dilimler(self):
        d = ayar.z1_dilimleri(ayar._ms(2020, 3, 1))
        self.assertEqual([x[0] for x in d], ['2020', '2021', '2022', '2023H1'])
        self.assertEqual(d[0][1], ayar._ms(2020, 3, 1))
        self.assertEqual(d[-1][2], ayar._ms(2023, 6, 24))
        self.assertTrue(all(d[i][2] == d[i + 1][1] for i in range(3)))


class BirimTest(unittest.TestCase):
    def test_sayilar_ve_teklik(self):
        for m, beklenen in (('A', 529), ('B', 530)):
            b = ayar.birimler(m)
            self.assertEqual(len(b), beklenen)
            self.assertEqual(len({json.dumps(x, sort_keys=True) for x in b}), len(b))
            self.assertEqual(sum(x['grup'] == 'null' for x in b), 500)
            self.assertEqual(b[0]['grup'], 'birincil')
        self.assertEqual(sum(x['grup'] == 'a_ayristirma' for x in ayar.birimler('B')), 1)

    def test_izgara_ve_kelly(self):
        b = ayar.birimler('A')
        iz = {(x['nav0'], x['maliyet_k']) for x in b if x['grup'] == 'izgara'}
        self.assertEqual(len(iz), 8)
        self.assertNotIn((ayar.NAV_BIRINCIL, 1.0), iz)
        ke = {(x['L'], x['maliyet_k']) for x in b if x['grup'] == 'kelly'}
        self.assertEqual(len(ke), 12)
        self.assertTrue(all(L != 1.0 for L, _ in ke))

    def test_gecersiz_mimari(self):
        with self.assertRaises(ValueError):
            ayar.birimler('C')


if __name__ == '__main__':
    unittest.main()
