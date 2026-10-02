"""Carry kapisi serileri (CARRY Ss4.1, Ss5.2-Ss5.6; U-01, U-06, U-16, U-29): sentetik ayristirma satirlariyla elle."""
import sys as _sys
import unittest
from datetime import datetime, timezone
from pathlib import Path as _Path
from types import SimpleNamespace

import numpy as np

TESTLER_DIR = _Path(__file__).resolve().parent
V8_DIR = TESTLER_DIR.parent
for _dir in (V8_DIR, TESTLER_DIR):
    if str(_dir) not in _sys.path:
        _sys.path.insert(1, str(_dir))

from kapi import seriler as sr  # noqa: E402
from motor.ayristirma import SATIRLAR  # noqa: E402

H, G = sr.SAAT_MS, sr.GUN_MS


def _ms(y, a, g):
    return int(datetime(y, a, g, tzinfo=timezone.utc).timestamp() * 1000)


def _kur(bas_ms, n_saat, tohum=1):
    """Sentetik ayristirma (her saat rastgele satirlar; dnav gun sonunda gunun bilesen toplami) ve saatlik NAV."""
    rng = np.random.default_rng(tohum)
    saat = bas_ms + np.arange(n_saat, dtype=np.int64) * H
    sat = {s: rng.standard_normal(n_saat) for s in SATIRLAR}
    bil = sum(i * sat[a] for a, i in sr.OZDESLIK_BILESEN)
    sat['dnav'] = np.full(n_saat, np.nan)
    nav0 = 100_000.0
    nav_ms = saat + H
    nav = nav0 + np.cumsum(bil)                   # saatlik NAV bilesenlerle tutarli
    gun_sonu = (nav_ms % G) == 0
    onceki = nav0
    for n in np.nonzero(gun_sonu)[0]:
        sat['dnav'][n] = nav[n] - onceki
        onceki = nav[n]
    ayr = SimpleNamespace(saat_ms=saat, satirlar=sat)
    return ayr, sr.NavOkuyucu(nav_ms, nav, nav0), nav0


class TakvimTest(unittest.TestCase):
    def test_kapi_takvimi(self):
        t = sr.KAPI_TAKVIMI
        s = t.hafta_sinirlari()
        self.assertEqual(len(s), 144)
        self.assertEqual(int(s[0]), _ms(2023, 10, 2))
        self.assertEqual(int(s[-1]), _ms(2026, 6, 29))
        self.assertTrue(all(datetime.fromtimestamp(x / 1000, timezone.utc).weekday() == 0 for x in s.tolist()))
        self.assertEqual(t.t0_ms, _ms(2023, 10, 1))
        self.assertEqual(len(t.ay_sinirlari), 34)
        self.assertEqual(t.ay_sinirlari[0], _ms(2023, 10, 1))
        self.assertEqual(t.ay_sinirlari[-1], _ms(2026, 7, 1))


class NavOkuyucuTest(unittest.TestCase):
    def test_bas_ve_eksik(self):
        nav = sr.NavOkuyucu([1000 + H, 1000 + 2 * H], [11.0, 12.0], 10.0)
        self.assertEqual(nav(1000), 10.0)
        self.assertEqual(nav(1000 + 2 * H), 12.0)
        with self.assertRaises(sr.SeriHatasi):
            nav(1000 + 3 * H)


class HaftalikTest(unittest.TestCase):
    def setUp(self):
        # Kosu Pazar 2024-01-07 00:00'da baslar, 20 gun; takvim: t0 = kosu basi, 2 hafta (Pzt 01-08 -> 01-22).
        self.bas = _ms(2024, 1, 7)
        self.ayr, self.nav, self.nav0 = _kur(self.bas, 20 * 24)
        self.tak = sr.Takvim(t0_ms=self.bas, hafta_bas_ms=_ms(2024, 1, 8), n_hafta=2,
                             ay_sinirlari=(_ms(2024, 1, 1), _ms(2024, 1, 20)))

    def test_elle(self):
        L, om = 1.5, 0.2
        s = sr.haftalik(self.ayr, self.nav, L, om, self.tak)
        sat = self.ayr.satirlar
        for w in range(2):
            a = (_ms(2024, 1, 8) + w * 7 * G - self.bas) // H
            b = a + 7 * 24
            nb = self.nav(_ms(2024, 1, 8) + w * 7 * G)
            self.assertEqual(s['nav_bas'][w], nb)
            dc, dt = om * L * nb, L * nb
            F = (sat['carry_funding'][a:b].sum() + sat['hedge_funding'][a:b].sum()) / dc
            P = (sat['carry_fiyat'][a:b].sum() + sat['hedge_fiyat'][a:b].sum()) / dc
            C = sat['carry_maliyet'][a:b].sum() / dc
            aC = sat['artik_carry'][a:b].sum() / dc
            T = (sat['trend_fiyat'][a:b].sum() + sat['trend_funding'][a:b].sum() - sat['trend_maliyet'][a:b].sum()) / dt
            aT = sat['artik_trend'][a:b].sum() / dt
            for k, v in (('F', F), ('P', P), ('C', C), ('a_C', aC), ('T', T), ('a_T', aT),
                         ('N', F - C + P), ('N_g', F - C + P + aC), ('T_g', T + aT)):
                self.assertAlmostEqual(s[k][w], v, places=14, msg=k)
        np.testing.assert_array_equal(s['N'], s['F'] - s['C'] + s['P'])

    def test_takvim_kosuyu_asarsa_hata(self):
        tak = sr.Takvim(t0_ms=self.bas, hafta_bas_ms=_ms(2024, 1, 8), n_hafta=3, ay_sinirlari=())
        with self.assertRaises(sr.SeriHatasi):
            sr.haftalik(self.ayr, self.nav, 1.0, 0.2, tak)

    def test_sonlu_olmayan_satir_hata(self):
        self.ayr.satirlar['carry_fiyat'][30] = np.nan
        with self.assertRaises(sr.SeriHatasi):
            sr.haftalik(self.ayr, self.nav, 1.0, 0.2, self.tak)

    def test_aylik_ilk_sinir_t0(self):
        L, om = 2.0, 0.25
        m = sr.aylik_fc(self.ayr, self.nav, L, om, self.tak)
        self.assertEqual(int(m['ay_ms'][0]), self.bas)
        self.assertEqual(m['nav_bas'][0], self.nav0)
        sat = self.ayr.satirlar
        b = (_ms(2024, 1, 20) - self.bas) // H
        fc = (sat['carry_funding'][:b].sum() + sat['hedge_funding'][:b].sum() - sat['carry_maliyet'][:b].sum())
        self.assertAlmostEqual(m['FC'][0], fc / (om * L * self.nav0), places=13)


class OzdeslikTest(unittest.TestCase):
    def test_tutarli_ve_bozuk(self):
        bas = _ms(2024, 1, 7)
        ayr, nav, _ = _kur(bas, 5 * 24)
        o = sr.gunluk_ozdeslik_orani(ayr, nav)
        self.assertEqual(len(o), 5)
        self.assertLess(max(o.values()), 1e-12)
        ayr.satirlar['netleme'][30] += 2.0                # 2. gun
        o = sr.gunluk_ozdeslik_orani(ayr, nav)
        self.assertAlmostEqual(o[bas + G], 2.0 / nav(bas + G), delta=1e-12)
        ayr.satirlar['dnav'][24 * 3 + 23] = np.inf
        self.assertEqual(sr.gunluk_ozdeslik_orani(ayr, nav)[bas + 3 * G], float('inf'))
        ayr.satirlar['dnav'][24 * 4 + 23] = np.nan                  # T15-9: gun sonu NAV'i yok -> inf
        self.assertEqual(sr.gunluk_ozdeslik_orani(ayr, nav)[bas + 4 * G], float('inf'))


class MotorKosusuTest(unittest.TestCase):
    """Gercek Mimari B kosusu (sentetik carry senaryosu, T0 = 2023-10-01): NAV sinirlari, olcek ve V2 orani."""

    @classmethod
    def setUpClass(cls):
        from dataclasses import replace
        from fikstur.saatlik_veri import CARRY_GUN, carry_senaryo_verisi, gun_ms, saat_ms
        from motor.ayristirma import ayristir
        from motor.geri_test import KosuAyarlari, kos
        from motor.tipler import Parametreler
        cls.P = replace(Parametreler(), mimari='B')
        cls.ayar = KosuAyarlari(t0_ms=gun_ms(92), t_son_ms=saat_ms(CARRY_GUN * 24 - 1))
        veri = carry_senaryo_verisi()
        cls.s = kos(veri, cls.ayar, cls.P)
        cls.ayr = ayristir(cls.s.gunluk, veri, cls.P)
        cls.tak = sr.Takvim(t0_ms=_ms(2023, 10, 1), hafta_bas_ms=_ms(2023, 10, 2), n_hafta=5,
                            ay_sinirlari=(_ms(2023, 10, 1), _ms(2023, 11, 1)))

    def test_olcek_ve_seriler(self):
        nav0, L = sr.kosu_olcegi(self.s.gunluk)
        self.assertEqual((nav0, L), (self.ayar.nav0, self.ayar.L))
        nav = sr.NavOkuyucu(self.s.nav_ms, self.s.nav, nav0)
        self.assertEqual(nav.bas_ms, self.tak.t0_ms)
        w = sr.haftalik(self.ayr, nav, L, self.P.carry_omega, self.tak)
        den = self.P.carry_omega * L * w['nav_bas']
        a = int(np.searchsorted(self.ayr.saat_ms, self.tak.hafta_bas_ms))
        b = a + 5 * 7 * 24
        carry = sum(float(self.ayr.satirlar[k][a:b].sum()) for k in
                    ('carry_funding', 'hedge_funding', 'carry_fiyat', 'hedge_fiyat'))             - float(self.ayr.satirlar['carry_maliyet'][a:b].sum())
        self.assertAlmostEqual(float(np.sum(w['N'] * den)), carry, delta=1e-9 * nav0)
        self.assertTrue(np.any(w['F'] != 0.0))
        m = sr.aylik_fc(self.ayr, nav, L, self.P.carry_omega, self.tak)
        self.assertEqual(m['nav_bas'][0], nav0)

    def test_v2_orani(self):
        nav = sr.NavOkuyucu(self.s.nav_ms, self.s.nav, self.ayar.nav0)
        o = sr.gunluk_ozdeslik_orani(self.ayr, nav)
        self.assertGreaterEqual(len(o), 37)
        self.assertLessEqual(max(o.values()), 1e-8)


if __name__ == '__main__':
    unittest.main()
