"""Carry kapisi betimsel raporlari, seri tabanli kisim (CARRY Ss6.6; U-33, U-34, U-35, U-37): elle ve sentetik dunyada."""
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

from kapi import betimsel as bt  # noqa: E402
from kapi import istatistik as ist  # noqa: E402
from kapi import olcutler as o  # noqa: E402
from kapi.seriler import KAPI_TAKVIMI  # noqa: E402
from test_v8_kapi_olcutler import _dunya  # noqa: E402


class ElleTest(unittest.TestCase):
    def test_phi(self):
        s = {'F': np.array([0.03, 0.05]), 'C': np.array([0.01, 0.01]), 'P': np.array([0.02, 0.0])}
        self.assertAlmostEqual(bt.phi(s), 0.03 / 0.04, places=15)
        s['P'] = np.array([-0.02, 0.0])
        self.assertAlmostEqual(bt.phi(s), 1.0, places=15)

    def test_bilesik_mdd(self):
        self.assertAlmostEqual(bt.bilesik_mdd([0.1, -0.5, 0.2]), 0.5, places=15)
        self.assertEqual(bt.bilesik_mdd([0.1, -1.0]), 1.0)
        self.assertEqual(bt.bilesik_mdd([0.1, 0.2]), 0.0)

    def test_k1_duyarlilik(self):
        d = bt.k1_duyarlilik({'sanal': {'rho_ust': -0.2}, 'gerceklesen': {'rho_ust': 0.5}})
        self.assertAlmostEqual(d['sanal']['0.45|0.27'], 0.45 * ist.g_seyreltme(0.0, 0.27), places=15)
        self.assertAlmostEqual(d['gerceklesen']['0.6|0.43'], 0.60 * ist.g_seyreltme(0.30, 0.43), places=15)
        self.assertEqual(len(d['sanal']), 4)

    def test_artik_en_buyuk(self):
        s = {'a_C': np.array([0.1, -0.5, 0.3, 0.5]), 'hafta_ms': np.arange(4) * 10}
        e = bt.artik_tanisi(s)['en_buyuk']
        self.assertEqual([x['hafta_ms'] for x in e], [10, 30, 20])          # esit |a|'da erken hafta once


class DunyaTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.g = _dunya()
        cls.g.ana['hafta_ms'] = KAPI_TAKVIMI.hafta_sinirlari()[:-1]
        cls.d, cls.h = o.degerlendir(cls.g)
        cls.r = bt.seri_raporlari(cls.g, cls.h, {'delist50': cls.g.mc2, 'delist90': cls.g.mc3})

    def test_ceyrek(self):
        c = self.r['ceyrek']
        self.assertEqual(len(c), 11)
        self.assertEqual(c[0]['ceyrek'], '2023-Q4')
        self.assertEqual(c[-1]['ceyrek'], '2026-Q2')
        self.assertEqual(sum(x['hafta'] for x in c), 143)

    def test_wald_elle(self):
        X = np.column_stack([self.g.faktor[f] for f in o.FAKTORLER])
        ol = ist.ols_nw(self.g.ana['P'], X, 12)
        b, V = ol['katsayi'][1:], ol['V'][1:, 1:]
        w = float(b @ np.linalg.inv(V) @ b)
        self.assertAlmostEqual(self.r['k11']['l12']['wald'], w, places=9)
        self.assertAlmostEqual(self.r['k11']['l12']['wald_p'], math.exp(-w / 2) * (1 + w / 2), places=12)
        # Faktorler r^P'ye dik kuruldu: katsayilar ~0, p ~1.
        self.assertGreater(self.r['k11']['l12']['wald_p'], 0.99)

    def test_nw_t_ve_andrews(self):
        t = self.r['nw_t']['F-C']
        x = self.g.ana['F'] - self.g.ana['C']
        self.assertAlmostEqual(t['t12'], ist.nw_t(x)['t'][12], places=15)
        self.assertGreaterEqual(t['andrews_l'], 0)
        self.assertEqual(len([k for k in self.r['nw_t'] if k.startswith('beta')]), 4)

    def test_trend_yazilmaz(self):
        self.assertTrue(o.hukum_trend_icermez(self.r))
        self.assertIn('delist90', self.r['delist_k1'])
        self.assertIn('rho_ust', self.r['delist_k1']['delist50']['sanal'])


if __name__ == '__main__':
    unittest.main()
