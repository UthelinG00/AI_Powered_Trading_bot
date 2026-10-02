"""Carry kapisi istatistikleri (CARRY Ss6.2, Ss15; U-02, U-03, U-09, U-22): elle hesaplanmis degerler ve belge sayilari."""
import math
import sys as _sys
import unittest
from pathlib import Path as _Path

import numpy as np

V8_DIR = _Path(__file__).resolve().parent.parent
if str(V8_DIR) not in _sys.path:
    _sys.path.insert(1, str(V8_DIR))

from kapi import istatistik as s  # noqa: E402


class SharpeTest(unittest.TestCase):
    def test_elle(self):
        r = [0.01, -0.01, 0.02, 0.0]
        m, sd = 0.005, math.sqrt((0.005 ** 2 + 0.015 ** 2 + 0.015 ** 2 + 0.005 ** 2) / 3)
        self.assertAlmostEqual(s.sharpe(r), m / sd * math.sqrt(52), places=12)

    def test_tanimsiz(self):
        self.assertTrue(math.isnan(s.sharpe([0.01])))
        self.assertTrue(math.isnan(s.sharpe([0.02, 0.02, 0.02])))
        with self.assertRaises(ValueError):
            s.sharpe([0.01, float('nan')])


class KrediliSharpeTest(unittest.TestCase):
    def _seri(self, fc, fiyat, vol, n=143, tohum=5):
        # Birim olcekte yillik: funding - maliyet fc, fiyat ortalamasi fiyat, toplam vol vol.
        rng = np.random.default_rng(tohum)
        e = rng.standard_normal(n)
        e = (e - e.mean()) / e.std(ddof=1) * vol / math.sqrt(52)
        r_f = np.full(n, fc / 52 + 0.001)
        r_c = np.full(n, 0.001)
        r_p = fiyat / 52 + e
        return r_f, r_c, r_p, r_f - r_c + r_p

    def test_kc06_ornegi(self):
        # Ss6.2: funding - maliyet %1, fiyat %3, vol %15 -> SR^K = 0,01 / 0,15 ~ 0,07 (fiyat kazanci kredilenmez).
        r_f, r_c, r_p, r = self._seri(0.01, 0.03, 0.15)
        self.assertAlmostEqual(s.sr_kredili(r_f, r_c, r_p, r), 0.01 / 0.15, places=12)
        self.assertGreater(s.sharpe(r), 0.25)

    def test_fiyat_kaybi_dusulur(self):
        r_f, r_c, r_p, r = self._seri(0.05, -0.02, 0.10)
        self.assertAlmostEqual(s.sr_kredili(r_f, r_c, r_p, r), (0.05 - 0.02) / 0.10, places=12)

    def test_artik_yalniz_aleyhe(self):
        # U-09: gerceklesen seride min(ort(a), 0).
        r_f, r_c, r_p, r = self._seri(0.05, 0.0, 0.10)
        for a_ort, beklenen_ek in ((0.01, 0.0), (-0.01, -0.01)):
            a = np.full(len(r), a_ort / 52)
            rg = r + a
            sd = float(np.std(rg, ddof=1)) * math.sqrt(52)
            self.assertAlmostEqual(s.sr_kredili(r_f, r_c, r_p, rg, a), (0.05 + beklenen_ek) / sd, places=12)

    def test_seri_eslesmesi_denetlenir(self):
        r_f, r_c, r_p, r = self._seri(0.05, 0.0, 0.10)
        with self.assertRaises(ValueError):
            s.sr_kredili(r_f, r_c, r_p, r + 1e-6)


class NeweyWestTest(unittest.TestCase):
    x = np.array([0.3, -0.1, 0.4, 0.2, -0.5, 0.1, 0.0, 0.6])

    def test_gecikme0_orneklem_varyansi_n(self):
        d = self.x - self.x.mean()
        self.assertAlmostEqual(s.nw_ortalama_se(self.x, 0), math.sqrt(np.mean(d * d) / len(self.x)), places=15)

    def test_gecikme2_elle(self):
        n, d = len(self.x), self.x - self.x.mean()
        g = [float(np.sum(d[j:] * d[:n - j])) / n for j in range(3)]
        uzun = g[0] + 2 * (2 / 3) * g[1] + 2 * (1 / 3) * g[2]
        self.assertAlmostEqual(s.nw_ortalama_se(self.x, 2), math.sqrt(uzun / n), places=15)

    def test_buyuk_se_secilir(self):
        rng = np.random.default_rng(3)
        x = np.cumsum(rng.standard_normal(143)) * 0.01 + 0.002   # kalici seri: l = 12 SE'si buyuk
        t = s.nw_t(x)
        self.assertEqual(t['se_buyuk'], max(t['se'][4], t['se'][12]))
        self.assertAlmostEqual(t['t_buyuk'], t['ortalama'] / t['se_buyuk'], places=15)

    def test_sabit_seri_t_nan(self):
        t = s.nw_t(np.full(10, 0.01))
        self.assertTrue(math.isnan(t['t_buyuk']))

    def test_ols_sabit_yalniz_ortalama_ile_ayni(self):
        rng = np.random.default_rng(4)
        y = rng.standard_normal(50)
        for l in (0, 4, 12):
            o = s.ols_nw(y, np.empty((50, 0)), l)
            self.assertAlmostEqual(o['katsayi'][0], y.mean(), places=14)
            self.assertAlmostEqual(o['se'][0], s.nw_ortalama_se(y, l), places=14)

    def test_ols_katsayi_ve_hc0(self):
        rng = np.random.default_rng(6)
        X = rng.standard_normal((80, 2))
        y = 0.1 + X @ np.array([0.5, -0.2]) + rng.standard_normal(80) * 0.3
        o = s.ols_nw(y, X, 0)
        Z = np.column_stack([np.ones(80), X])
        b = np.linalg.lstsq(Z, y, rcond=None)[0]
        np.testing.assert_allclose(o['katsayi'], b, rtol=0, atol=1e-12)
        u = y - Z @ b
        A = np.linalg.inv(Z.T @ Z)
        V = A @ (Z.T * u ** 2) @ Z @ A
        np.testing.assert_allclose(o['se'], np.sqrt(np.diag(V)), rtol=1e-12)

    def test_parametre_basina_buyuk(self):
        rng = np.random.default_rng(7)
        X = np.cumsum(rng.standard_normal((143, 2)), axis=0) * 0.01
        y = X @ np.array([0.1, 0.1]) + np.cumsum(rng.standard_normal(143)) * 0.01
        o = s.ols_nw_buyuk(y, X)
        np.testing.assert_array_equal(o['se_buyuk'], np.maximum(o['se'][4], o['se'][12]))


class AralikTest(unittest.TestCase):
    def test_acik_aralik_ucu_gecmez(self):
        # Ss7.1: aralik ucu toleransa esitse gecmez.
        self.assertFalse(s.esdeger(0.0, 0.15 / 1.645, 0.15))
        self.assertTrue(s.esdeger(0.0, 0.15 / 1.645 * 0.999, 0.15))
        self.assertFalse(s.esdeger(0.10, 0.04, 0.15))      # 0,10 + 0,0658 > 0,15
        self.assertFalse(s.esdeger(0.0, float('nan'), 0.15))


class RhoUstTest(unittest.TestCase):
    def test_belge_ek_terimi(self):
        # Ss6.2: n_w = 143 -> ek terim ~ 0,108.
        self.assertAlmostEqual(1.2816 / math.sqrt(140), 0.108, delta=0.0005)
        rng = np.random.default_rng(8)
        x = rng.standard_normal(143)
        y = rng.standard_normal(143)
        r = s.rho_ust(x, y)
        self.assertEqual(r['n_w'], 143)
        self.assertAlmostEqual(r['rho_ust'], math.tanh(math.atanh(r['rho_hat']) + 1.2816 / math.sqrt(140)), places=15)

    def test_tanimsiz_arti_bir(self):
        # U-22: sifir varyans ya da n_w < 4 -> rho_ust = +1.
        self.assertEqual(s.rho_ust(np.ones(20), np.arange(20.0))['rho_ust'], 1.0)
        self.assertEqual(s.rho_ust(np.arange(3.0), np.arange(3.0))['rho_ust'], 1.0)

    def test_tam_korelasyon_kirpilir(self):
        r = s.rho_ust(np.arange(10.0), -2 * np.arange(10.0))
        self.assertEqual(r['rho_hat'], -1.0)
        self.assertTrue(math.isfinite(r['rho_ust']))

    def test_eksik_hafta_cift_duser(self):
        x = np.array([1.0, 2.0, np.nan, 4.0, 5.0, 7.0])
        y = np.array([2.0, 1.0, 3.0, np.nan, 6.0, 5.0])
        self.assertEqual(s.rho_ust(x, y)['n_w'], 4)


class K1EsikTest(unittest.TestCase):
    def test_belge_uclari(self):
        # Ss6.3: 0,138 (rho_ust <= 0) ile 0,370 (rho_ust >= 0,30).
        self.assertAlmostEqual(s.k1_esik(-0.5), 0.138, delta=0.0005)
        self.assertAlmostEqual(s.k1_esik(0.0), 0.138, delta=0.0005)
        self.assertAlmostEqual(s.k1_esik(0.30), 0.370, delta=0.0005)
        self.assertEqual(s.k1_esik(0.9), s.k1_esik(0.30))
        self.assertEqual(s.k1_esik(1.0), s.k1_esik(0.30))
        self.assertLess(s.k1_esik(0.1), s.k1_esik(0.2))


class BootstrapTest(unittest.TestCase):
    def test_cekis_bicimi_elle(self):
        x = np.array([1.0, 2.0, 3.0, 4.0, 5.0])
        rng = np.random.default_rng(11)
        o = s.dairesel_blok_ortalamalari(x, 2, 3, rng)
        rng2 = np.random.default_rng(11)
        for c in range(3):
            bas = rng2.integers(0, 5, size=3)
            idx = [(b + k) % 5 for b in bas for k in range(2)][:5]
            self.assertAlmostEqual(o[c], x[idx].mean(), places=15)

    def test_k2_tek_akis_sirasi(self):
        rng = np.random.default_rng(12)
        x = rng.standard_normal(143) * 0.01 + 0.002
        k = s.k2_bootstrap_alt(x, cekis=500)
        g = np.random.default_rng(20260928)
        a4 = np.quantile(s.dairesel_blok_ortalamalari(x, 4, 500, g), 0.05)
        a12 = np.quantile(s.dairesel_blok_ortalamalari(x, 12, 500, g), 0.05)
        self.assertEqual(k['blok'][4], a4)
        self.assertEqual(k['blok'][12], a12)
        self.assertEqual(k['alt'], min(a4, a12))
        self.assertEqual(k, s.k2_bootstrap_alt(x, cekis=500))

    def test_sr_araligi(self):
        rng = np.random.default_rng(13)
        r = rng.standard_normal(143) * 0.02 + 0.004
        alt, ust = s.sr_bootstrap_araligi(r, cekis=300)
        self.assertLess(alt, s.sharpe(r))
        self.assertGreater(ust, s.sharpe(r))


class DigerTest(unittest.TestCase):
    def test_andrews(self):
        self.assertEqual(s.andrews_gecikme(np.ones(10)), 0)
        rng = np.random.default_rng(14)
        e = rng.standard_normal(500)
        x = np.empty(500)
        x[0] = e[0]
        for t in range(1, 500):
            x[t] = 0.5 * x[t - 1] + e[t]
        d = x - x.mean()
        rho = float(np.dot(d[1:], d[:-1])) / float(np.dot(d[:-1], d[:-1]))
        alfa = 4 * rho ** 2 / ((1 - rho) ** 2 * (1 + rho) ** 2)
        self.assertEqual(s.andrews_gecikme(x), math.ceil(1.1447 * (alfa * 500) ** (1 / 3)))

    def test_standart_yukleme(self):
        self.assertEqual(s.standart_yukleme(0.5, 0.1, 0.04, 0.02), (1.0, 0.2))
        self.assertTrue(math.isnan(s.standart_yukleme(0.5, 0.1, 0.04, 0.0)[0]))


class T15Test(unittest.TestCase):
    def test_ondalik_sabit_trend_tanimsiz(self):
        # T15-7: tekrarlanan ondalik degerde ortalama gurultusu korelasyonu "yaklasik sifir" yapmamali.
        r = s.rho_ust(np.linspace(0.0, 1.0, 50), np.full(50, 0.1))
        self.assertTrue(np.isnan(r['rho_hat']))
        self.assertEqual(r['rho_ust'], 1.0)

    def test_buyuk_gecikme_bellek(self):
        # T15-11: ±1'e kirpilan AR'de Andrews gecikmesi cok buyuk olsa da ag irliklar n - 1 ile sinirli.
        x = np.array([-1.0, 2.0, -3.0, 2.0])
        l = s.andrews_gecikme(x)
        self.assertGreater(l, 1000)
        self.assertTrue(np.isfinite(s.nw_ortalama_se(x, l)))
        self.assertEqual(len(s._bartlett(10**9, 4)), 3)

if __name__ == '__main__':
    unittest.main()
