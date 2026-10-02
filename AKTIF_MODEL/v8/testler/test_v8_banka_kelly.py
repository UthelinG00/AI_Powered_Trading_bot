"""Kelly tablosu (banka_kos/kelly.py; BANKA §4, BK-9): metrikler, DD süresi, en kötü ay, durağan bootstrap, 𝓛*."""
import math
import sys as _sys
import unittest
from datetime import datetime, timezone
from pathlib import Path as _Path

import numpy as np

V8_DIR = _Path(__file__).resolve().parent.parent
if str(V8_DIR) not in _sys.path:
    _sys.path.insert(1, str(V8_DIR))

from banka_kos import kelly  # noqa: E402

G = 86_400_000
BAS = int(datetime(2020, 1, 30, tzinfo=timezone.utc).timestamp() * 1000)


class MetrikTest(unittest.TestCase):
    def test_dd_suresi(self):
        self.assertEqual(kelly.en_uzun_dd_gun([0.1, -0.1, -0.1, 0.3, 0.01]), 2)
        self.assertEqual(kelly.en_uzun_dd_gun([0.1, 0.1]), 0)
        self.assertEqual(kelly.en_uzun_dd_gun([0.1, -0.1, 0.01]), 2)          # geri alınmadı: sona kadar

    def test_metrikler(self):
        r = np.array([0.1, -0.5, 0.2, 0.0, 0.05])
        g = BAS + np.arange(5) * G                                             # 30 Oca - 3 Şub
        m = kelly.metrikler(r, g)
        self.assertAlmostEqual(m['mdd'], 0.5, places=12)
        self.assertEqual(m['en_kotu_gun'], -0.5)
        self.assertAlmostEqual(m['en_kotu_ay'], 1.1 * 0.5 - 1, places=12)      # Ocak: 0,1 ve -0,5
        self.assertAlmostEqual(m['cagr'], float(np.prod(1 + r)) ** (365 / 5) - 1, places=9)
        self.assertAlmostEqual(m['calmar'], m['cagr'] / 0.5, places=12)
        self.assertIn('hata', kelly.metrikler([0.1], g[:1]))


class BootstrapTest(unittest.TestCase):
    def test_duragan_ortalama_blok(self):
        ix = kelly.duragan_indeksler(1000, 200_000, np.random.default_rng(1))
        yeni = np.sum(np.diff(ix) != 1) - np.sum(np.diff(ix) == -999)
        self.assertAlmostEqual(200_000 / max(yeni, 1), 20, delta=1.5)
        np.testing.assert_array_equal(ix[:50], kelly.duragan_indeksler(1000, 200_000, np.random.default_rng(1))[:50])

    def test_mdd_bootstrap_sabit_pozitif(self):
        b = kelly.mdd_bootstrap(np.full(500, 0.001), np.random.default_rng(2), cekis=20)
        self.assertEqual((b['q50'], b['q95'], b['p_asim']), (0.0, 0.0, 0.0))


class TabloTest(unittest.TestCase):
    def test_kume_ve_oneri(self):
        rng = np.random.default_rng(3)
        r1 = rng.standard_normal(1200) * 0.01 + 0.0006
        r_L = {L: np.clip(L * r1, -0.99, None) for L in (0.5, 1.0, 2.0, 4.0)}
        g = BAS + np.arange(1200) * G
        t = kelly.kelly_tablosu(r_L, g, tohum_banka=123, cekis=30)
        self.assertAlmostEqual(t['f_yildiz'], float(np.mean(r1)) / float(np.var(r1, ddof=1)), places=12)
        self.assertAlmostEqual(t['satirlar'][2.0]['kelly_kesri'], 2.0 / t['f_yildiz'], places=9)
        for L in t['uygun_L']:
            self.assertTrue(t['satirlar'][L]['dd_gercek_ok'] and t['satirlar'][L]['dd_boot_ok'])
        self.assertNotIn(4.0, t['uygun_L'])
        self.assertEqual(t['satirlar'][4.0]['etiket'], kelly.KARSILAMIYOR)
        if t['uygun_L']:
            self.assertEqual(t['varsayilan_oneri'], max(t['uygun_L'], key=lambda L: t['satirlar'][L]['cagr']))
        bos = kelly.kelly_tablosu({1.0: np.full(400, -0.01)}, g[:400], 1, cekis=5)
        self.assertEqual((bos['uygun_L'], bos['cumle']), ([], kelly.BOS_CUMLE))
        with self.assertRaises(ValueError):
            kelly.kelly_tablosu({2.0: r1}, g, 1)


if __name__ == '__main__':
    unittest.main()
