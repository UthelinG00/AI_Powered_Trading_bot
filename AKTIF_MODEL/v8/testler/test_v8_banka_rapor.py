"""Banka rapor satırları (banka_kos/rapor.py; 6.08 1. parça): Sharpe güven aralığı bootstrap'ı. Satırların yapısı
uçtan uca testte (test_v8_banka_uctan_uca.test_rapor_satirlari) gerçek çözülmüş birimlerle denenir."""
import sys as _sys
import unittest
from pathlib import Path as _Path

import numpy as np

V8_DIR = _Path(__file__).resolve().parent.parent
if str(V8_DIR) not in _sys.path:
    _sys.path.insert(1, str(V8_DIR))

from banka import olcutler as o  # noqa: E402
from banka_kos import rapor  # noqa: E402


class NwRegresyonTest(unittest.TestCase):
    def test_ols_ile_ayni_katsayi(self):
        rng = np.random.default_rng(4)
        x1, x2 = rng.normal(0, 0.02, 600), rng.normal(0, 0.01, 600)
        y = 0.0005 + 0.7 * x1 - 0.3 * x2 + rng.normal(0, 0.01, 600)
        r = rapor.nw_regresyon(y, [x1, x2])
        b = np.linalg.lstsq(np.column_stack([np.ones(600), x1, x2]), y, rcond=None)[0]
        np.testing.assert_allclose(r['katsayi'], b, atol=1e-12)
        self.assertGreater(r['t'][1], 10)
        self.assertLess(r['t'][2], -3)
        self.assertEqual(rapor.nw_regresyon(y[:3], [x1[:3], x2[:3]])['n'], 3)          # az gözlem: nan, hata yok


class SrGaTest(unittest.TestCase):
    def test_deterministik_ve_akis_ayri(self):
        r = np.random.default_rng(1).normal(0.001, 0.02, 400)
        a = rapor.sr_ga(r, 12345, 'birincil_A', cekis=200)
        self.assertEqual(a, rapor.sr_ga(r, 12345, 'birincil_A', cekis=200))
        self.assertNotEqual(a, rapor.sr_ga(r, 12345, 'delist_A_0.5', cekis=200))
        self.assertNotEqual(a, rapor.sr_ga(r, 54321, 'birincil_A', cekis=200))
        self.assertAlmostEqual(a['sr'], o.sharpe(r), places=15)
        self.assertLess(a['q05'], a['sr'])
        self.assertGreater(a['q95'], a['sr'])
        self.assertEqual(a['cekis'], 200)

    def test_aralik_genisligi_blok_bagimliligiyla_artar(self):
        rng = np.random.default_rng(2)
        e = rng.normal(0, 0.02, 1200)
        ar = np.empty_like(e)
        ar[0] = e[0]
        for t in range(1, len(e)):
            ar[t] = 0.8 * ar[t - 1] + e[t]                      # pozitif otokorelasyon: blok bootstrap daha geniş
        g_iid = rapor.sr_ga(e, 7, 'x', cekis=400)
        g_ar = rapor.sr_ga(ar, 7, 'x', cekis=400)
        self.assertGreater(g_ar['q95'] - g_ar['q05'], g_iid['q95'] - g_iid['q05'])

    def test_kisa_seri(self):
        g = rapor.sr_ga([0.01], 1, 'x', cekis=10)
        self.assertEqual(g['cekis'], 0)



class R4Test(unittest.TestCase):
    """Netleştirme 17 e: D başına bağlı 30 takvim günlük bloklar (≥ 25 ortak gün), stres eşiği D'nin bütününden."""

    def test_bloklar_ve_esik(self):
        from types import SimpleNamespace
        from banka_kos import ayar
        G = 86_400_000
        n = 180
        rng = np.random.default_rng(9)
        r = rng.normal(0.001, 0.01, n)
        nav = np.concatenate(([1e5], 1e5 * np.cumprod(1 + r)))
        rbtc = rng.normal(0, 0.03, n)
        d0 = 1_700_000_000_000 // G * G
        b = {'nav_bas_ms': d0, 'nav_gunluk': nav.tolist(),
             'piyasa': {'bas_ms': d0, 'r_btc': rbtc.tolist(), 'r_alt': [None] * n, 'btc_katki': [0.0] * n,
                        'artik_katki': [0.0] * n, 'beta_coin': 0, 'beta_yok': 0}}
        from banka_kos.kosucu import birim_adi
        birimler = {birim_adi(ayar._birim('birincil', 'A')): b}
        hb = SimpleNamespace(mimari='A', d_bas_ms=d0, d_bit_ms=d0 + n * G, gorulmus_gunler=())
        gunler = [d0 + i * G for i in range(n)]
        seri = {g: float(0.5 * r[i] + 0.001) for i, g in enumerate(gunler) if not (30 <= i < 38)}   # 2. blokta 22 gün
        k = rapor.r4_rev1(birimler, hb, {'seri': seri, 'dosya': 'rev1.json', 'sha256': '0' * 64})
        self.assertEqual(k['otuz_gunluk_n'], 5)                  # 6 bloktan biri < 25 ortak gün
        self.assertEqual(k['otuz_gunluk_dusen_blok'], 1)
        self.assertAlmostEqual(k['stres_esigi_btc'], float(np.quantile(rbtc, 0.05)), places=12)   # ortaklıktan önce
        self.assertEqual(k['ortak_gun'], n - 8)
        self.assertGreater(k['gunluk'], 0.9)
        self.assertEqual(rapor.r4_rev1(birimler, hb, None), {'durum': 'REV1 serisi yok'})


if __name__ == '__main__':
    unittest.main()
