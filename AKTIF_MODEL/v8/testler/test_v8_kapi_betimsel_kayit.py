"""Carry kapisi betimsel raporlari, karar kaydi tabanli kisim (CARRY Ss5.1, Ss6.6; U-43...U-47): sahte kayitlarla elle
ve gercek Mimari B kosusunda (sentetik carry senaryosu)."""
import sys as _sys
import unittest
from dataclasses import replace
from pathlib import Path as _Path
from types import SimpleNamespace

import numpy as np

TESTLER_DIR = _Path(__file__).resolve().parent
V8_DIR = TESTLER_DIR.parent
for _dir in (V8_DIR, TESTLER_DIR):
    if str(_dir) not in _sys.path:
        _sys.path.insert(1, str(_dir))

from kapi import betimsel_kayit as bk  # noqa: E402
from motor.tipler import Parametreler  # noqa: E402

P = replace(Parametreler(), mimari='B')
G = bk.GUN_MS


def _karar(t, kappa=1.0, kappa_etkin=1.0, baglayan=(), w_yildiz=None, w_mevcut=None, sanal_carry=None, nav=1e5,
           n_c=None):
    carry = {'kappa': kappa, 'kappa_etkin': kappa_etkin, 'sanal_carry': sanal_carry or {},
             'tanilar': {} if n_c is None else {'n_c': n_c}}
    return SimpleNamespace(tur='karar', damga_ms=t, coin=None, miktar=None, karar_ms=t, veri={'hedef': {
        'baglayan': list(baglayan), 'w_yildiz': w_yildiz or {}, 'w_mevcut': w_mevcut or {}, 'nav': nav, 'carry': carry}})


def _gunluk(kayitlar):
    return SimpleNamespace(kayitlar=lambda: list(kayitlar))


class ElleTest(unittest.TestCase):
    def test_kappa(self):
        k = [_karar(i * G, kappa=v, kappa_etkin=(0.9 if i == 2 else 1.0)) for i, v in enumerate([1, 0.8, 0.7, 0.5, 0.5, 0])]
        t = bk.kappa_tanisi(k)
        self.assertEqual(t['gun'], 6)
        self.assertAlmostEqual(t['kappa_lt1_oran'], 5 / 6, places=15)
        self.assertAlmostEqual(t['kappa_etkin_lt1_oran'], 1 / 6, places=15)
        self.assertEqual(t['goreli_degisim_gun'], 2)                    # 0,7 -> 0,5 ve 0,5 -> 0
        self.assertAlmostEqual(t['bant_izleme']['en_buyuk'], 0.2, places=15)
        self.assertEqual(t['bant_izleme']['farkli_gun'], 1)

    def test_baglama_ve_s4(self):
        s4 = P.s4_sinir / P.s4_artis
        k = [_karar(0, baglayan=('S1', 'kappa'), w_yildiz={'ALT': -s4}),
             _karar(G, baglayan=('S1',), w_yildiz={'ALT': -s4 / 2, P.btc: -0.5}),
             _karar(2 * G, baglayan=(), w_yildiz={})]
        b = bk.baglama_sikliklari(k, P)
        self.assertAlmostEqual(b['etiket']['S1'], 2 / 3, places=15)
        self.assertAlmostEqual(b['etiket']['kappa'], 1 / 3, places=15)
        self.assertAlmostEqual(b['S4_baglama'], 1 / 3, places=15)
        self.assertEqual(b['S4_asim'], 0.0)
        b2 = bk.baglama_sikliklari([_karar(0, w_yildiz={'ALT': -2 * s4})], P)          # T15-14: asim temas degil
        self.assertEqual((b2['S4_baglama'], b2['S4_asim']), (0.0, 1.0))

    def test_tavan_s4(self):
        s4 = P.s4_sinir / P.s4_artis
        k = [_karar(0, w_mevcut={'ALT': -0.05, P.btc: 0.1}), _karar(G, w_mevcut={'ALT': -0.01})]
        t = bk.tavan_asimlari(k, P)['gerceklesen']
        self.assertAlmostEqual(t['S4']['en_buyuk'], 0.05 - s4, places=15)
        self.assertAlmostEqual(t['S4']['gun_orani'], 0.5, places=15)
        self.assertIn('S1', t)

    def test_hedefe_ulasilamayan(self):
        k = [_karar(0), _karar(G)]
        kay = k + [SimpleNamespace(tur='emir_niyeti', damga_ms=0, coin='A', miktar=2.0, karar_ms=0, veri={}),
                   SimpleNamespace(tur='dolum', damga_ms=3_600_000, coin='A', miktar=2.0, karar_ms=0, veri={}),
                   SimpleNamespace(tur='emir_niyeti', damga_ms=G, coin='B', miktar=-3.0, karar_ms=G, veri={}),
                   SimpleNamespace(tur='dolum', damga_ms=G + 3_600_000, coin='B', miktar=-1.0, karar_ms=G, veri={})]
        self.assertEqual(bk.hedefe_ulasilamayan(_gunluk(kay), k)['oran'], 0.5)

    def test_hedge_yuvarlama(self):
        k = [_karar(0, sanal_carry={P.btc: 0.0005}), _karar(G, sanal_carry={P.btc: -0.01}), _karar(2 * G)]
        h = bk.hedge_yuvarlama(k, 0.001, P.btc)
        self.assertEqual(h['hedge_gun'], 2)
        self.assertEqual(h['kapi_orani'], 0.5)
        self.assertEqual(h['demo_orani'], 1.0)

    def test_v6(self):
        v = bk.v6_fark_tanisi([{'A': 0.1, 'B': 0.2}, {'A': 0.1}], [{'A': 0.1, 'B': 0.2}, {'A': 0.05, 'C': 0.01}])
        self.assertEqual(v['fark_gun'], 1)
        self.assertAlmostEqual(v['ort_brut_fark'], 0.06, places=15)
        self.assertEqual(v['oran'], 0.5)

    def test_mimari_a_kaydi_reddedilir(self):
        a = SimpleNamespace(tur='karar', damga_ms=0, veri={'hedef': {}})
        with self.assertRaises(ValueError):
            bk.karar_kayitlari(_gunluk([a]), 0, G)


class MotorKosusuTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from fikstur.saatlik_veri import CARRY_GUN, carry_senaryo_verisi, gun_ms, saat_ms
        from motor.ayristirma import ayristir
        from motor.geri_test import KosuAyarlari, kos
        cls.bas, cls.bit = gun_ms(92), gun_ms(CARRY_GUN)
        veri = carry_senaryo_verisi()
        cls.s = kos(veri, KosuAyarlari(t0_ms=cls.bas, t_son_ms=saat_ms(CARRY_GUN * 24 - 1)), P)
        cls.ayr = ayristir(cls.s.gunluk, veri, P)
        cls.k = bk.karar_kayitlari(cls.s.gunluk, cls.bas, cls.bit)

    def test_uctan_uca(self):
        self.assertEqual(len(self.k), (self.bit - self.bas) // G)
        t = bk.kappa_tanisi(self.k)
        self.assertEqual(t['gun'], len(self.k))
        self.assertTrue(0.0 <= t['kappa_lt1_oran'] <= 1.0)
        b = bk.baglama_sikliklari(self.k, P)
        self.assertTrue(all(0.0 < v <= 1.0 for v in b['etiket'].values()))
        pz = [t_ for t_ in range(self.bas, self.bit, G) if (t_ // G + 3) % 7 == 0]       # 1970-01-05 (gun 4) Pazartesi
        n = bk.n_c_serisi(self.k, pz)
        self.assertTrue(any(x['n_c'] is not None for x in n))
        h = bk.hedefe_ulasilamayan(self.s.gunluk, self.k)
        self.assertTrue(0.0 <= h['oran'] <= 1.0)
        na = bk.netleme_ve_artik(self.ayr, self.bas, self.bit)
        beklenen = sum(abs(v) for g, v in self.ayr.gunluk['artik_carry'].items() if self.bas <= g < self.bit)
        self.assertAlmostEqual(na['abs_artik_carry_gunluk'], beklenen, places=9)
        ta = bk.tavan_asimlari(self.k, P, self.s.gunluk, self.bas, self.bit)
        self.assertEqual(set(ta), {'gerceklesen', 'devreden'})
        self.assertEqual(set(ta['devreden']), {'S1', 'S2', 'S4'})
        hy = bk.hedge_yuvarlama(self.k, 0.001, P.btc)
        self.assertGreater(hy['hedge_gun'], 0)


if __name__ == '__main__':
    unittest.main()
