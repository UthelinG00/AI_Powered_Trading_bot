"""Carry kapisi fiyat faktorleri (CARRY Ss6.2; U-19, U-24, U-41): elle kurulmus barlarla."""
import math
import sys as _sys
import unittest
from pathlib import Path as _Path

import numpy as np

V8_DIR = _Path(__file__).resolve().parent.parent
if str(V8_DIR) not in _sys.path:
    _sys.path.insert(1, str(V8_DIR))

from kapi import faktorler as fk  # noqa: E402
from motor.gorunum import saatlik_seri  # noqa: E402

H = 3_600_000
BAS = 1_696_204_800_000          # 2023-10-02 00:00 UTC (Pazartesi)


def _seri(kapanis, bas=BAS - 24 * H):
    """Saatlik barlar; kapanis[i] = (bas + i h) barinin kapanisi."""
    k = np.asarray(kapanis, dtype=float)
    ms = bas + np.arange(len(k), dtype=np.int64) * H
    return saatlik_seri(ms, k, k, k, k, np.ones(len(k)))


def _dogrusal(bas_fiyat, haftalik_carpan, n_saat, bas=BAS - 24 * H):
    # Saat basina sabit bilesik buyume: hafta sinirlari arasinda getiri = carpan - 1.
    g = haftalik_carpan ** (1.0 / (7 * 24))
    return _seri(bas_fiyat * g ** np.arange(1, n_saat + 1), bas)


class HaftaGetirisiTest(unittest.TestCase):
    def test_son_kapanis_ile(self):
        s = _seri(np.arange(1.0, 24 * 10 + 1))
        barlar = {'X': s}
        t0, t1 = BAS, BAS + fk.HAFTA_MS
        # sk(t0) = t0 - 1h barinin kapanisi = indeks 23 -> 24; sk(t1) = indeks 24 + 168 - 1 -> 192.
        self.assertAlmostEqual(fk.hafta_getirisi(barlar, 'X', t0, t1), 192.0 / 24.0 - 1.0, places=14)

    def test_hafta_icinde_biten_son_kapanista_kalir(self):
        s = _seri(np.r_[np.full(24, 10.0), np.full(48, 12.0)])       # t0 + 47h'de biter
        self.assertAlmostEqual(fk.hafta_getirisi({'X': s}, 'X', BAS, BAS + fk.HAFTA_MS), 0.2, places=14)

    def test_yok(self):
        self.assertTrue(math.isnan(fk.hafta_getirisi({}, 'X', BAS, BAS + fk.HAFTA_MS)))


class UzunKisaTest(unittest.TestCase):
    def test_otuz_yuzde_ve_tamsayi(self):
        deger = {f"C{i:02d}": float(i) for i in range(10)}
        getiri = {f"C{i:02d}": 0.01 * i for i in range(10)}
        # n = 10 -> k = 3: uzun C07-C09 (0,08), kisa C00-C02 (0,01).
        self.assertAlmostEqual(fk.uzun_kisa(deger, getiri), 0.08 - 0.01, places=15)
        # n = 30 -> k = 9 (0,3 * 30 kayan noktada 8,999... degil).
        d30 = {f"C{i:02d}": float(i) for i in range(30)}
        g30 = {c: 1.0 if int(c[1:]) >= 21 else (-1.0 if int(c[1:]) <= 8 else 0.0) for c in d30}
        self.assertEqual(fk.uzun_kisa(d30, g30), 2.0)

    def test_en_az_bir_ve_tanimsiz(self):
        self.assertEqual(fk.uzun_kisa({'A': 1.0, 'B': 2.0}, {'A': -0.1, 'B': 0.3}), 0.4)
        self.assertTrue(math.isnan(fk.uzun_kisa({'A': 1.0, 'B': float('nan')}, {'A': 0.1, 'B': 0.3})))

    def test_esitlikte_alfabetik(self):
        deger = {'D': 1.0, 'C': 1.0, 'B': 1.0, 'A': 1.0}
        getiri = {'A': 1.0, 'B': 2.0, 'C': 3.0, 'D': 4.0}
        # k = 1: ust (-deger, ad) -> A; alt (deger, ad) -> A: fark 0.
        self.assertEqual(fk.uzun_kisa(deger, getiri), 0.0)


class FaktorlerTest(unittest.TestCase):
    def test_iki_hafta(self):
        n = 24 + 2 * 168 + 5
        barlar = {'BTCUSDT': _dogrusal(100.0, 1.10, n)}
        carp = {'A1': 1.02, 'A2': 0.97, 'A3': 1.05, 'A4': 1.00}
        for c, m in carp.items():
            barlar[c] = _dogrusal(10.0, m, n)
        pz = [{'adaylar': ['A1', 'A2', 'A3', 'A4', 'BTCUSDT'],
               'r30': {'A1': 3.0, 'A2': 1.0, 'A3': 2.0, 'A4': float('nan')},
               's_trend': {'A1': 0.1, 'A2': 0.4, 'A3': 0.3, 'A4': 0.2}},
              {'adaylar': ['A1', 'A2'], 'r30': {'A1': 1.0, 'A2': 2.0}, 's_trend': {'A1': 0.0, 'A2': 0.0}}]
        f = fk.faktorler(barlar, pz, [BAS, BAS + fk.HAFTA_MS])
        np.testing.assert_allclose(f['x_B'], [0.10, 0.10], rtol=0, atol=1e-12)
        self.assertAlmostEqual(f['x_A'][0], np.mean([0.02, -0.03, 0.05, 0.0]), places=12)
        self.assertAlmostEqual(f['x_A'][1], np.mean([0.02, -0.03]), places=12)
        # x_R hafta 0: A4 (nan) disarida, n = 3 -> k = 1: uzun A1 (+0,02), kisa A2 (-0,03).
        self.assertAlmostEqual(f['x_R'][0], 0.05, places=12)
        # x_S hafta 0: n = 4 -> k = 1: uzun A2 (-0,03), kisa A1 (+0,02).
        self.assertAlmostEqual(f['x_S'][0], -0.05, places=12)
        self.assertAlmostEqual(f['x_R'][1], -0.03 - 0.02, places=12)
        self.assertAlmostEqual(f['x_S'][1], 0.0, places=12)             # esitlik: A1 hem uzun hem kisa

    def test_sayi_uyusmazligi(self):
        with self.assertRaises(ValueError):
            fk.faktorler({}, [], [BAS])


if __name__ == '__main__':
    unittest.main()
