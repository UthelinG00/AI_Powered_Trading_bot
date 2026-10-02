"""MIMARI Ss4.1-Ss4.5 carry uydusu birim testleri: siralar/notrleme, beta, bacaklar, haftalik kitap (olcekleme,
genislik, tavanlar, bant, yeniden notrleme), gunluk blok ve hedge, net cozucu (trend onceligi, kappa, S4), s^C.
Sentetik girdiler; gercek veri yok."""
import math
import sys as _sys
import unittest
from dataclasses import replace
from pathlib import Path as _Path

import numpy as np

TESTLER_DIR = _Path(__file__).resolve().parent
V8_DIR = TESTLER_DIR.parent
for _dir in (V8_DIR, TESTLER_DIR):
    if str(_dir) not in _sys.path:
        _sys.path.insert(1, str(_dir))

from fikstur.saatlik_veri import CoinTarifi, gun_ms, tam_veri_uret  # noqa: E402
from motor.carry import (CarryHatasi, bacaklar, beta_tahmin, eksik_funding_olay_sayisi, f30,  # noqa: E402
                         gunluk_blok, hafta_ici_guncelle, haftalik_kitap, notrle, siralar, yeniden_notrle)
from motor.gorunum import gorunum_kur  # noqa: E402
from motor.hedef_b import pazartesi_mi, sc_paylari  # noqa: E402
from motor.net_cozucu import NetCozucuHatasi, net_coz  # noqa: E402
from motor.tavanlar import _kayip_s1  # noqa: E402
from motor.tipler import Parametreler  # noqa: E402

P = replace(Parametreler(), mimari='B')


def _v_kosegen(sigma=0.5):
    """Kosegen Sigma ile V: sqrt(sum (w sigma)^2)."""
    return lambda w: math.sqrt(sum((x * sigma) ** 2 for x in w.values()))


class SiraNotrlemeTest(unittest.TestCase):
    def test_ortalama_sira_ve_eksik_medyan(self):
        np.testing.assert_array_equal(siralar([3.0, 1.0, 1.0, 5.0]), [3.0, 1.5, 1.5, 4.0])
        np.testing.assert_array_equal(siralar([2.0, float('nan'), 1.0]), [2.0, 1.5, 1.0])

    def test_artik_regresorlere_dik(self):
        rng = np.random.default_rng(1)
        c, r30, s, b = (rng.normal(size=20) for _ in range(4))
        z = notrle(c, r30, s, b)
        for x in (np.ones(20), siralar(r30), siralar(s), siralar(b)):
            self.assertAlmostEqual(float(z @ x), 0.0, places=9)

    def test_f30_yalniz_gercek_kayit_ve_yillik(self):
        veri = tam_veri_uret({'X': CoinTarifi(funding_orani=0.0001)}, 40)
        g = gorunum_kur(veri, gun_ms(35))
        self.assertAlmostEqual(f30(g.funding['X'], gun_ms(35), P), 90 * 0.0001 * 365 / 30, places=12)


class BetaTest(unittest.TestCase):
    def test_buzulme_ve_yedek(self):
        rng = np.random.default_rng(2)
        rb = rng.normal(0, 0.02, 60)
        bh, b = beta_tahmin(2.0 * rb, rb, P)
        self.assertAlmostEqual(bh, 2.0, places=9)
        self.assertAlmostEqual(b, 1.5, places=9)
        self.assertEqual(beta_tahmin(np.full(60, np.nan), rb, P), (1.0, 1.0))


class BacakTest(unittest.TestCase):
    def setUp(self):
        self.isim = [f'A{i:02d}' for i in range(10)]
        self.z = {c: float(i) for i, c in enumerate(self.isim)}         # A09 en yuksek z
        self.f = {c: 0.1 for c in self.isim}

    def test_yuzde_otuz_ve_histerezis(self):
        long_, short = bacaklar(self.isim, self.z, self.f, {}, P)
        self.assertEqual((long_, short), (('A00', 'A01', 'A02'), ('A07', 'A08', 'A09')))
        # Mevcut short A05 (z = 5 >= medyan 4,5) kalir; mevcut long A04 (z = 4 <= 4,5) kalir; A06 short z >= medyan.
        long_, short = bacaklar(self.isim, self.z, self.f, {'A05': -1, 'A04': 1, 'A03': -1}, P)
        self.assertIn('A05', short)
        self.assertIn('A04', long_)
        self.assertNotIn('A03', short)             # z = 3 < medyan: short'tan cikar

    def test_long_funding_tabani_mevcut_longa_da(self):
        self.f['A00'] = -0.6
        self.f['A04'] = -0.6
        long_, _ = bacaklar(self.isim, self.z, self.f, {'A04': 1}, P)
        self.assertNotIn('A00', long_)
        self.assertNotIn('A04', long_)


def _kitap(n=16, q_eski=None, v30=100e6, sigma=None, beta=None, nav=1e5, L=1.0):
    isim = [f'A{i:02d}' for i in range(n)]
    z = {c: float(i) for i, c in enumerate(isim)}
    return haftalik_kitap(isim, z, {c: 0.1 for c in isim}, sigma or {c: 0.5 for c in isim},
                          beta or {c: 1.0 for c in isim}, {c: v30 for c in isim}, q_eski or {}, {},
                          {c: 1.0 for c in isim}, nav, L, _v_kosegen(), P)


class HaftalikKitapTest(unittest.TestCase):
    def test_genislik(self):
        self.assertEqual(_kitap(n=9).q_yildiz, {})
        tam, yarim = _kitap(n=20), _kitap(n=12)
        self.assertEqual(tam.tanilar['butce'], P.carry_omega)
        self.assertEqual(yarim.tanilar['butce'], 0.5 * P.carry_omega)

    def test_olcekleme_t4b_ve_dolar_notr(self):
        hk = _kitap(n=20)
        self.assertAlmostEqual(hk.tanilar['v_birim'], P.tau, places=12)
        nl = sum(q for q in hk.q_yildiz.values() if q > 0)
        ns = -sum(q for q in hk.q_yildiz.values() if q < 0)
        self.assertAlmostEqual(nl, ns, places=9)

    def test_isim_tavani_ve_yarim_tavan(self):
        # Tek coin agirligi tavani asacak kadar buyuk olsun: yuksek sigma yerine az isim (n=10, k=3).
        hk = _kitap(n=10, v30=30e6)                 # V30 < 50M: tavanlar yarida
        for c, q in hk.q_yildiz.items():
            tavan = (P.carry_tavan_long if q > 0 else P.carry_tavan_short) / 2
            self.assertLessEqual(abs(q) * 1.0 / 1e5, tavan + 1e-15)

    def test_haftalik_bant(self):
        # L = 0,1: tavan baglamaz, lambda = 1 (bant karsilastirmasi adim 4 miktariyla yapilir).
        ilk = _kitap(n=20, L=0.1)
        self.assertEqual(ilk.lam, 1.0)
        yakin = {c: q * 1.1 for c, q in ilk.q_yildiz.items()}     # %10 fark: bantta tutulur
        ikinci = _kitap(n=20, q_eski=yakin, L=0.1)
        self.assertEqual(sorted(ikinci.tanilar['bantli']), sorted(ilk.q_yildiz))
        self.assertEqual(ikinci.q_yildiz, yakin)
        uzak = {c: q * 2.0 for c, q in ilk.q_yildiz.items()}
        self.assertEqual(_kitap(n=20, q_eski=uzak, L=0.1).tanilar['bantli'], [])
        ters = {c: -q for c, q in ilk.q_yildiz.items()}           # isaret degisimi her zaman islenir
        self.assertEqual(_kitap(n=20, q_eski=ters, L=0.1).tanilar['bantli'], [])

    def test_codex_kc04_ornegi(self):
        # beta = 1, +%2 / -%2; tavanlar sonrasi +%1,5 / -%1: adim 6 long'u lambda = 1/1,5 ile %1'e indirir; hedge 0.
        q, lam, bagli = yeniden_notrle({'L': 1.5, 'S': -1.0}, {'L': 1.0, 'S': 1.0})
        self.assertAlmostEqual(lam, 1 / 1.5, places=12)
        self.assertEqual(bagli, 'long')
        self.assertAlmostEqual(q['L'], 1.0, places=12)
        blok = gunluk_blok(q, {'L': 1.0, 'S': 1.0}, {'L': 1.0, 'S': 1.0}, 100.0, 1.0, _v_kosegen(), P)
        self.assertAlmostEqual(blok.w_btc, 0.0, places=12)
        # Hafta ici long cikarsa bacak bosalir: lambda = 0, blok kapanir.
        q2, lam2, _ = hafta_ici_guncelle(q, {'L'}, {'L': 1.0, 'S': 1.0})
        self.assertEqual((q2, lam2), ({}, 0.0))

    def test_blok_beta_notr_ve_t4c(self):
        q = {'A': 3000.0, 'B': -2000.0}
        beta = {'A': 1.2, 'B': 0.8}
        blok = gunluk_blok(q, beta, {'A': 1.0, 'B': 1.0}, 1e5, 1.0, _v_kosegen(), P)
        self.assertAlmostEqual(sum(beta[c] * w for c, w in blok.w_alt.items()) + blok.w_btc, 0.0, places=15)
        self.assertEqual(blok.t4c_katsayi, 1.0)
        buyuk = gunluk_blok({c: v * 100 for c, v in q.items()}, beta, {'A': 1.0, 'B': 1.0}, 1e5, 1.0, _v_kosegen(), P)
        self.assertLess(buyuk.t4c_katsayi, 1.0)
        v = _v_kosegen()({**buyuk.w_alt, P.btc: buyuk.w_btc})
        self.assertAlmostEqual(v, P.carry_omega * P.tau, places=12)


class NetCozucuTest(unittest.TestCase):
    BE = np.array([True, False, False])            # BTC, alt1, alt2

    def test_isim_tavaninda_yalniz_trend_kuculur(self):
        ns = net_coz([0.0, 0.08, 0.0], [0.0, -0.01, 0.0], np.zeros(3), np.zeros(3, bool), self.BE, P)
        self.assertAlmostEqual(ns.w[1], P.isim_tavan_alt_long, places=12)
        self.assertEqual(ns.kappa, 1.0)

    def test_s4_alt_short_tavani(self):
        ns = net_coz([0.0, -0.05, 0.0], [0.0, 0.0, 0.0], np.zeros(3), np.zeros(3, bool), self.BE, P)
        self.assertAlmostEqual(ns.w[1], -P.s4_sinir / P.s4_artis, places=12)

    def test_carry_tek_basina_tavani_asarsa_hata(self):
        with self.assertRaises(NetCozucuHatasi):
            net_coz([0.0, 0.0, 0.0], [0.0, -0.05, 0.0], np.zeros(3), np.zeros(3, bool), self.BE, P)

    def test_s1_once_trend_sonra_kappa_blok_oranlari_korunur(self):
        # Trend long'lari S1'i asar; ikiye bolme trend long katsayisini bulur, carry degismez.
        wT = np.array([0.30, 0.06, 0.06, 0.06, 0.06, 0.06])
        wC = np.array([-0.004, 0.01, -0.01, 0.0, 0.0, 0.0])
        be = np.array([True] + [False] * 5)
        ns = net_coz(wT, wC, np.zeros(6), np.zeros(6, bool), be, P)
        self.assertEqual(ns.kappa, 1.0)
        self.assertLessEqual(_kayip_s1(ns.w, be, P), P.s1_sinir + 1e-12)
        self.assertGreater(_kayip_s1(ns.w, be, P), P.s1_sinir - 1e-9)
        # Trend 0'a inse de ihlal suren kitap (carry long'lari tek basina buyuk): kappa < 1, oranlar sabit.
        wC2 = np.array([-0.2, 0.06, 0.06, 0.06, 0.06, 0.06]) * 1.0
        ns2 = net_coz(np.zeros(6), wC2, np.zeros(6), np.zeros(6, bool), be, P)
        self.assertLess(ns2.kappa, 1.0)
        np.testing.assert_allclose(ns2.w, ns2.kappa * wC2 * ns2.global_katsayi, rtol=1e-12)


class ScPayiTest(unittest.TestCase):
    def test_sifir_sifir_son_pay(self):
        sc, son = sc_paylari({'X': 3.0}, {'X': 1.0, 'Y': 2.0}, {}, ['X', 'Y', 'Z'])
        self.assertEqual(sc, {'X': 0.25, 'Y': 1.0, 'Z': 0.0})
        sc2, _ = sc_paylari({}, {}, son, ['X', 'Y', 'Z'])
        self.assertEqual(sc2, {'X': 0.25, 'Y': 1.0, 'Z': 0.0})

    def test_pazartesi(self):
        self.assertTrue(pazartesi_mi(gun_ms(93)))       # 2023-10-02
        self.assertFalse(pazartesi_mi(gun_ms(92)))


class EksikOlayTest(unittest.TestCase):
    def test_iki_eksik_olay_sayilir(self):
        # Ilk bosluk 24 saat (Delta = 8 -> olay); sonra Delta = 24 olur, ikinci olay >= 36 saatlik bosluk ister
        # (Ss2.6: Delta son 30 gunun en uzun araligi). Ikinci bosluk 40 saat.
        eksik = frozenset({30 * 24, 30 * 24 + 8} | {35 * 24 + 8 * j for j in range(4)})
        veri = tam_veri_uret({'X': CoinTarifi(funding_eksik=eksik)}, 45)
        g = gorunum_kur(veri, gun_ms(44))
        self.assertEqual(eksik_funding_olay_sayisi(g, 'X', gun_ms(44), P), 2)
        g0 = gorunum_kur(tam_veri_uret({'X': CoinTarifi()}, 45), gun_ms(44))
        self.assertEqual(eksik_funding_olay_sayisi(g0, 'X', gun_ms(44), P), 0)


class CodexDorduncuTurTest(unittest.TestCase):
    """Codex 4. tur (limit nedeniyle kesildi) karsi ornekleri."""

    def test_kappa_isim_tavanini_bozmaz(self):
        # Sabit BTC %35 / ETH %31; alt trend -%5, carry +%1: kappa carry'yi kucultunce net short S4 tavanini asiyordu.
        be = np.array([True, True, False, False, False, False])
        ns = net_coz([0, 0, -.05, 0, 0, 0], [0, 0, .01, .01, -.01, -.01], [.35, .31, 0, 0, 0, 0],
                     be.copy(), be, P)
        self.assertLessEqual(P.s4_artis * max(-ns.w[2:]), P.s4_sinir + 1e-12)
        self.assertLessEqual(_kayip_s1(ns.w, be, P), P.s1_sinir + 1e-12)

    def test_bant_carry_isim_tavanini_asan_eski_miktari_tutmaz(self):
        names = [f'X{i:02}' for i in range(10)]
        vfn = lambda w: float(np.linalg.norm(list(w.values())) * 0.2)
        eski = {**{c: 1000.0 for c in names[:3]}, **{c: -1100.0 for c in names[-3:]}}
        h = haftalik_kitap(names, {c: float(i) for i, c in enumerate(names)}, {c: .1 for c in names},
                           {c: .3 for c in names}, {c: 1.0 for c in names}, {c: 1e8 for c in names}, eski, {},
                           {c: 1.0 for c in names}, 1e5, 1.0, vfn, P)
        self.assertLessEqual(max(-q for q in h.q_yildiz.values()), P.carry_tavan_short * 1e5 + 1e-9)
        self.assertLessEqual(max(h.q_yildiz.values()), P.carry_tavan_long * 1e5 + 1e-9)


class TurBesTest(unittest.TestCase):
    """Inceleme wf_94f2a3aa-9a3 (Codex 5. tur + Claude inceleyiciler) bulgulari: B1, B2, B11, B17."""

    def test_b1_eksik_olay_delta_tespit_aninda(self):
        # Eski 24h bosluk pencerenin kenarinda; a = 960'tan 32h bosluk (tespit anindaki Delta = 8 -> olay);
        # a + 48'den 56h bosluk. Dogru sayi 2 (funding.py kurali); gap basindaki Delta ile 1 sayiliyordu.
        a, r1 = 960, 960 - 720
        eksik = frozenset({r1 + 8, r1 + 16} | {a + 8, a + 16, a + 24} | {a + 48 + 8 * j for j in range(1, 7)})
        veri = tam_veri_uret({'X': CoinTarifi(funding_eksik=eksik)}, 50)
        g = gorunum_kur(veri, gun_ms(46))
        self.assertEqual(eksik_funding_olay_sayisi(g, 'X', gun_ms(46), P), 2)

    def test_b2_cozucu_ciktisi_yeniden_sinamada_ihlal_sayilmaz(self):
        from motor.net_cozucu import ihlaller
        n = 13
        be = np.zeros(n, bool)
        be[12] = True
        for w_t in (-0.04, 0.05):
            wT = np.zeros(n)
            wT[:12] = w_t
            ns = net_coz(wT, np.zeros(n), np.zeros(n), np.zeros(n, bool), be, P)
            self.assertEqual(ihlaller(ns.w, np.ones(n, bool), be, P), set())
        rng = np.random.default_rng(1)
        for _ in range(300):
            m = 30
            w = rng.uniform(-0.04, 0.06, m)
            b = np.zeros(m, bool)
            b[:2] = True
            w[:2] = rng.uniform(-0.3, 0.3, 2)
            wc = rng.uniform(-0.01, 0.01, m) * (rng.uniform(size=m) < 0.4)
            ns = net_coz(w, wc, np.zeros(m), np.zeros(m, bool), b, P)
            self.assertEqual(ihlaller(ns.w, np.ones(m, bool), b, P), set())

    def test_b11_kappa_ic_aralikta_bulunur(self):
        # Codex 5. tur: sabit BTC %35 / ETH %29,8; alt A trend -%4 + carry +%1; B +%1, C, D -%1.
        # Uygun kappa araligi [2/3, 0,8] (0'i icermiyor): eski kod kappa = 0 + son careye gidiyordu.
        from motor.net_cozucu import ihlaller
        be = np.array([True, True, False, False, False, False])
        sabit = np.array([True, True, False, False, False, False])
        ns = net_coz([0, 0, -0.04, 0, 0, 0], [0, 0, 0.01, 0.01, -0.01, -0.01], [0.35, 0.298, 0, 0, 0, 0],
                     sabit, be, P)
        self.assertNotIn('global', ns.baglayan)
        self.assertAlmostEqual(ns.kappa, 0.8, places=9)
        self.assertEqual(ihlaller(ns.w, ~sabit, be, P), set())

    def test_b17_eksik_sira_gercek_medyan(self):
        np.testing.assert_array_equal(siralar([2.0, 2.0, 2.0, 4.0, float('nan')]), [2.0, 2.0, 2.0, 4.0, 2.0])


if __name__ == '__main__':
    unittest.main()
