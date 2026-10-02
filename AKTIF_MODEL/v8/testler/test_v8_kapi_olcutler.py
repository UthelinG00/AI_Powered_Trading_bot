"""Carry kapisi olcutleri ve karar (CARRY Ss6.1, Ss6.3, Ss7.1; Ss15): sentetik haftalik dunyalar. H1-dogru dunyada karar
B; her baglayici olcut ve V kosulu tek tek bozulunca A; esik sinirlari."""
import sys as _sys
import unittest
from pathlib import Path as _Path
from types import SimpleNamespace

import numpy as np

V8_DIR = _Path(__file__).resolve().parent.parent
if str(V8_DIR) not in _sys.path:
    _sys.path.insert(1, str(V8_DIR))

from kapi import olcutler as o  # noqa: E402

NW = 143


def _dik(x, *Z):
    """x'i [1, Z...] uzayina dik yap (katsayilar tam 0 olsun)."""
    A = np.column_stack([np.ones(len(x))] + list(Z))
    return x - A @ np.linalg.lstsq(A, x, rcond=None)[0]


def _seri(F, C, P, a_C, T, a_T):
    N = F - C + P
    return {'F': F, 'C': C, 'P': P, 'a_C': a_C, 'N': N, 'N_g': N + a_C, 'T': T, 'a_T': a_T, 'T_g': T + a_T}


def _dunya(tohum=1, fc_yil=0.07, p_ort_yil=0.0, a_kat=0.03):
    rng = np.random.default_rng(tohum)
    F = 0.08 / 52 + rng.standard_normal(NW) * 0.002
    C = np.full(NW, 0.01 / 52) + (0.08 - 0.01 - fc_yil) / 52
    e = rng.standard_normal(NW)
    P = (e - e.mean()) / e.std(ddof=1) * 0.10 / np.sqrt(52) + p_ort_yil / 52
    N = F - C + P
    a_C = a_kat * _dik(rng.standard_normal(NW) * 0.01, N)
    T = _dik(rng.standard_normal(NW) * 0.02, N, N + a_C)
    ana = _seri(F, C, P, a_C, T, np.zeros(NW))
    Z = (ana['N'], ana['N_g'], ana['P'])
    faktor = {f: _dik(rng.standard_normal(NW) * 0.05, *Z) for f in o.FAKTORLER}

    def varyant(c_kat):
        return _seri(F, C * c_kat, P, a_C, T, np.zeros(NW))
    return o.KapiGirdisi(
        ana=ana, ana_aylik={'FC': np.full(33, 0.005)}, mc2=varyant(2.0), mc3=varyant(3.0), k8=varyant(1.0),
        k8_isim_sayisi=40, faktor=faktor, pazartesi_bos=np.arange(NW) < 10, v1=True,
        v2_oran={k: 1e-12 for k in o.KOSULAR}, v5={k: True for k in o.KOSULAR}, v6_oran=0.02)


class H1DogruTest(unittest.TestCase):
    def test_karar_b(self):
        d, h = o.degerlendir(_dunya())
        self.assertTrue(all(d['V'].values()), d)
        for k in o.BAGLAYICI:
            self.assertTrue(h['K'][k]['gecti'], (k, h['K'][k]))
        self.assertEqual(h['karar'], 'B')
        self.assertEqual(d['teknik_ihlal'], [])
        self.assertTrue(o.hukum_trend_icermez(h))
        self.assertFalse(h['betimsel_K3_K4']['K3']['baglayici'])
        self.assertAlmostEqual(h['K']['K1']['sanal']['rho_hat'], 0.0, places=12)

    def test_denetim_olcut_degeri_icermez(self):
        d, _ = o.degerlendir(_dunya())
        self.assertEqual(set(d), {'V', 'teknik_ihlal', 'esas_ihlal'})
        self.assertTrue(all(isinstance(v, bool) for v in d['V'].values()))


class TekTekBozmaTest(unittest.TestCase):
    def _a(self, g, beklenen_kalan):
        d, h = o.degerlendir(g)
        self.assertEqual(h['karar'], 'A')
        kalan = [k for k in o.BAGLAYICI if not h['K'][k]['gecti']] + [k for k, v in d['V'].items() if not v]
        self.assertIn(beklenen_kalan, kalan)
        return d, h

    def test_fiyat_kazanci_kredilenmez(self):
        # Funding - maliyet ~0, fiyat ortalamasi %15/yil: ham Sharpe yuksek, SR^K dusuk -> K1 kalir.
        g = _dunya(fc_yil=0.001, p_ort_yil=0.15)
        from kapi.istatistik import sharpe
        self.assertGreater(sharpe(g.ana['N']), 1.0)
        self._a(g, 'K1')

    def test_k2_zayif_funding(self):
        g = _dunya(fc_yil=0.004)
        self._a(g, 'K2')

    def test_k5_sinir(self):
        g = _dunya()
        fc = np.full(33, 0.005)
        fc[:8] = -0.001                                     # 25/33 arti -> gecer
        g.ana_aylik = {'FC': fc}
        self.assertTrue(o.k5(g.ana_aylik)['gecti'])
        fc[8] = -0.001                                      # 24/33 -> kalir
        self.assertFalse(o.k5({'FC': fc})['gecti'])

    def test_k8_hesaplanamazsa_k8_kosusu_gerekmez(self):
        g = _dunya()
        g.k8, g.k8_isim_sayisi = None, 12
        del g.v2_oran['k8']
        del g.v5['k8']
        d, h = self._a(g, 'K8')
        self.assertTrue(d['V']['V2'] and d['V']['V5'])

    def test_k8_isim_sayisi(self):
        g = _dunya()
        g.k8_isim_sayisi = 29
        d, h = self._a(g, 'K8')
        self.assertIn('hata', h['K']['K8'])

    def test_k9_beta(self):
        g = _dunya()
        g.faktor['x_B'] = g.ana['N'] * 4.0 + _dik(np.random.default_rng(3).standard_normal(NW) * 0.01, g.ana['N'])
        self._a(g, 'K9')

    def test_k10_trend_kopyasi(self):
        g = _dunya()
        for s in (g.ana,):
            s['T'] = s['N'] * 2.0
            s['T_g'] = s['T'] + s['a_T']
        d, h = self._a(g, 'K10')
        self.assertGreater(h['K']['K1']['sanal']['esik'], 0.36)     # rho_ust >= 0,30 -> K1* doyar

    def test_k11_faktor_yuklemesi(self):
        g = _dunya()
        g.faktor['x_S'] = g.ana['P'] * 1.0 + np.random.default_rng(4).standard_normal(NW) * 0.001
        self._a(g, 'K11')

    def test_k6_k7_maliyet(self):
        g = _dunya(fc_yil=0.02)
        g.mc2 = dict(g.mc2)
        C2 = g.ana['C'] + 0.05 / 52
        g.mc2 = _seri(g.ana['F'], C2, g.ana['P'], g.ana['a_C'], g.ana['T'], g.ana['a_T'])
        self._a(g, 'K6')
        g.mc3 = g.mc2
        self._a(g, 'K7')

    def test_v4b_tek_hafta_sapmasi(self):
        g = _dunya()
        a = g.ana['a_C'].copy()
        a[50] = 5 * np.std(g.ana['N'], ddof=1)
        g.ana = _seri(g.ana['F'], g.ana['C'], g.ana['P'], a, g.ana['T'], g.ana['a_T'])
        d, _ = self._a(g, 'V4b')
        self.assertIn('V4b', d['esas_ihlal'])

    def test_v4a_zit_isaretli_artiklar_silinmez(self):
        g = _dunya()
        a = np.where(np.arange(NW) % 2 == 0, 1.0, -1.0) * 0.2 * np.abs(g.ana['N'])
        g.ana = _seri(g.ana['F'], g.ana['C'], g.ana['P'], a, g.ana['T'], g.ana['a_T'])
        self.assertAlmostEqual(float(np.sum(a)) / float(np.sum(np.abs(a))), 0.0, delta=0.2)
        self.assertFalse(o.v4(g.ana)['v4a']['gecti'])

    def test_v3_sinir(self):
        self.assertTrue(o.v3(np.arange(NW) < 35)['gecti'])       # aktif 108, pay 0,245
        self.assertFalse(o.v3(np.arange(NW) < 36)['gecti'])      # aktif 107

    def test_v2_eksik_kosu_teknik(self):
        g = _dunya()
        del g.v2_oran['delist90']
        d, _ = self._a(g, 'V2')
        self.assertEqual(d['teknik_ihlal'], ['V2'])

    def test_v5_ve_v6(self):
        g = _dunya()
        g.v5['mc3'] = False
        d, _ = self._a(g, 'V5')
        self.assertIn('V5', d['teknik_ihlal'])
        g = _dunya()
        g.v6_oran = 0.11
        d, _ = self._a(g, 'V6')
        self.assertIn('V6', d['esas_ihlal'])
        g.v6_oran = float('nan')
        self._a(g, 'V6')

    def test_hesaplanamayan_olcut_kalir(self):
        g = _dunya()
        g.faktor['x_A'] = g.faktor['x_A'].copy()
        g.faktor['x_A'][3] = np.nan
        d, h = self._a(g, 'K9')
        self.assertIn('hata', h['K']['K9'])
        self.assertIn('hata', h['K']['K11'])


class PazartesiBosTest(unittest.TestCase):
    def test_q_yildiz(self):
        def kayit(t, q):
            return SimpleNamespace(tur='karar', damga_ms=t, veri={'hedef': {'carry': {'q_yildiz': q}}})
        g = SimpleNamespace(kayitlar=lambda: [kayit(0, {}), kayit(7, {'A': 0.0, 'B': 0.0}), kayit(14, {'A': 1.5})])
        np.testing.assert_array_equal(o.pazartesi_bos_haftalar(g, [0, 7, 14]), [True, True, False])
        with self.assertRaises(ValueError):
            o.pazartesi_bos_haftalar(g, [21])


if __name__ == '__main__':
    unittest.main()
