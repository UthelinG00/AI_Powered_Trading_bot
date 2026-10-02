"""Duzey 1 olcut eslemesi (kalibrasyon/duzey1_olcut.py; BANKA_ONKAYIT_TASLAK Ss3.7 esleme tablosu)."""
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
from kalibrasyon.duzey1_olcut import ALANLAR, SEYRELTME, seyreltme_olculeri, sr_olculeri, yol_olculeri  # noqa: E402


class EslemeTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.yol = d1.yol_uret(0b1000001, 3)            # T 3,5; g = +1
        cls.ol = sr_olculeri(cls.yol, 1.0)

    def test_temel(self):
        ay = self.yol.ayar
        X = d1.portfoy(self.yol.hatlar, ay, 1.0)
        self.assertAlmostEqual(self.ol['sr'], o.sharpe(X), places=12)
        self.assertEqual(self.ol['T'], 1277.0)
        self.assertLess(self.ol['b3_2'], self.ol['sr'])
        self.assertLess(self.ol['b3_3'], self.ol['b3_2'])
        self.assertLess(self.ol['b8'], self.ol['sr'])              # g = +1: funding katkisi cikinca SR duser
        self.assertAlmostEqual(self.ol['b8'], o.sharpe(X - ay.F()), places=12)
        self.assertIn(self.ol['b6'], (0.0, 1.0, 2.0, 3.0, 4.0))

    def test_b5_epizot_toplami(self):
        ay = self.yol.ayar
        net = np.array([d1.hat_net(h, ay, 1.0) for h in self.yol.hatlar])
        ep = []
        for j, h in enumerate(self.yol.hatlar):
            ep += np.bincount(h.epizot, weights=net[j] / d1.J).tolist()
        X = net.mean(axis=0)
        self.assertAlmostEqual(sum(ep), float(X.sum()), places=8)
        beklenen = o.epizot_payi(ep, float(X.sum()))
        self.assertAlmostEqual(self.ol['b5'], beklenen, places=12)

    def test_b10_kendi_hattiyla_ikame_dusus_sifir(self):
        ay = self.yol.ayar
        net = np.array([d1.hat_net(h, ay, 1.0) for h in self.yol.hatlar])
        katki = net.sum(axis=1) / d1.J
        sira = sorted(range(d1.J), key=lambda j: (-abs(katki[j]), j))[:10]
        kopya = replace(self.yol, ikame=[self.yol.hatlar[j] for j in sira])
        self.assertEqual(sr_olculeri(kopya, 1.0)['b10'], 0.0)
        self.assertGreater(self.ol['b10'], -10.0)

    def test_b9_populasyon(self):
        no = 0b0000010                                    # phi 1,5
        b9 = [sr_olculeri(d1.yol_uret(no, y), 1.0)['b9'] for y in range(1, 151)]
        self.assertAlmostEqual(float(np.mean(b9)), 1.0, delta=0.12)

    def test_boyut(self):
        a = yol_olculeri(self.yol)
        self.assertEqual(a.shape, (len(d1.SR_IZGARASI), len(ALANLAR)))
        self.assertTrue(np.all(np.diff(a[:, ALANLAR.index('sr')]) > 0))     # SR kaydirmasi tekduze


class SeyreltmeTest(unittest.TestCase):
    def test_kopyalanan_ve_yeniden_hesaplanan(self):
        yol = d1.yol_uret(0b0000011, 4)
        a = sr_olculeri(yol, 1.0)
        b = seyreltme_olculeri(yol, 1.0, a)
        self.assertEqual(b.shape, (len(SEYRELTME), len(ALANLAR)))
        ix = {k: i for i, k in enumerate(ALANLAR)}
        for k in ('b5', 'b8', 'T'):
            self.assertTrue(np.all(b[:, ix[k]] == a[k]), k)
        for k in ('sr', 'b9', 'b10'):
            self.assertTrue(np.all(b[:, ix[k]] != a[k]), k)
        sr = {s: b[i, ix['sr']] for i, s in enumerate(SEYRELTME)}
        self.assertLess(sr[(0.0, -0.3)], sr[(0.0, 0.0)])
        self.assertLess(sr[(0.0, 0.0)], sr[(0.0, 0.3)])
        self.assertTrue(np.array_equal(b, seyreltme_olculeri(yol, 1.0)))

    def test_b10_ikame_kendi_hatti_ise_sifir(self):
        yol = d1.yol_uret(0b0000011, 4)
        ay = yol.ayar
        net = np.array([d1.hat_net(h, ay, 1.0) for h in yol.hatlar])
        katki = net.sum(axis=1) / d1.J
        sira = sorted(range(d1.J), key=lambda j: (-abs(katki[j]), j))[:10]
        kopya = replace(yol, ikame=[yol.hatlar[j] for j in sira])
        b = seyreltme_olculeri(kopya, 1.0)
        self.assertTrue(np.all(b[:, {k: i for i, k in enumerate(ALANLAR)}['b10']] == 0.0))

    def test_korelasyon(self):
        no = 0b0000000
        k = []
        for y in range(1, 41):
            yol = d1.yol_uret(no, y)
            ay = yol.ayar
            X0 = d1.portfoy(yol.hatlar, ay, 0.0)
            s_c = ay.sigma_P / 3
            C = s_c * (0.3 * X0 / ay.sigma_P + math.sqrt(1 - 0.09) * yol.carry_w)
            k.append(np.corrcoef(C, X0)[0, 1])
        self.assertAlmostEqual(float(np.mean(k)), 0.30, delta=0.03)


if __name__ == '__main__':
    unittest.main()
