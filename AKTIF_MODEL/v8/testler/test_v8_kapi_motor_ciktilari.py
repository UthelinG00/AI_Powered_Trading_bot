"""Kapi icin motor ciktilari (5.02e; CARRY Ss15, U-07, U-13, U-24, U-25; Ss4.2 madde 6): isim basi carry P&L'i ve icra
artigi satir toplamlarina esit; bacak funding'inin tur dokumu satirlara esit; Pazartesi carry tanisinda R30/s^trend;
gunluk tanida bant oncesi trend hedefi; carry_haric yalniz carry adayligini kaldirir. Sentetik carry senaryosu."""
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

from fikstur.saatlik_veri import CARRY_GUN, carry_senaryo_verisi, gun_ms, saat_ms  # noqa: E402
from motor.ayristirma import ayristir  # noqa: E402
from motor.geri_test import KosuAyarlari, kos  # noqa: E402
from motor.tipler import Parametreler  # noqa: E402

P = replace(Parametreler(), mimari='B')
AYAR = KosuAyarlari(t0_ms=gun_ms(92), t_son_ms=saat_ms(CARRY_GUN * 24 - 1))


def _karar_carry(s):
    return [k for k in s.gunluk.kayitlar() if k.tur == 'karar']


_KOSU = {}


def _kosu():
    if not _KOSU:
        veri = carry_senaryo_verisi()
        s = kos(veri, AYAR, P)
        _KOSU.update(veri=veri, s=s, a=ayristir(s.gunluk, veri, P))
    return _KOSU


class _Kosu(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        k = _kosu()
        cls.veri, cls.s, cls.a = k['veri'], k['s'], k['a']


class CiktiTest(_Kosu):

    def test_carry_coin_toplami(self):
        st = self.a.satirlar
        beklenen = (st['carry_fiyat'] + st['hedge_fiyat'] + st['carry_funding'] + st['hedge_funding']
                    - st['carry_maliyet'])
        toplam = sum(self.a.carry_coin.values())
        np.testing.assert_allclose(toplam, beklenen, rtol=0, atol=1e-9 * AYAR.nav0)
        self.assertIn(P.btc, self.a.carry_coin)
        self.assertGreater(len(self.a.carry_coin), 2)

    def test_carry_eski_yeni(self):
        for c, v in self.a.carry_coin.items():
            np.testing.assert_allclose(self.a.carry_eski[c] + self.a.carry_yeni[c], v, rtol=0, atol=1e-9)

    def test_artik_coin_toplami(self):
        np.testing.assert_allclose(sum(self.a.artik_coin.values()), self.a.satirlar['icra_artigi'], rtol=0,
                                   atol=1e-9 * AYAR.nav0)

    def test_funding_tur_dokumu(self):
        for b, satirlar in (('C', ('carry_funding', 'hedge_funding')), ('T', ('trend_funding',))):
            dok = sum(v[1] for tur in self.a.bacak_funding_tur[b].values() for v in tur.values())
            self.assertAlmostEqual(dok, sum(self.a.toplam[x] for x in satirlar), delta=1e-9 * AYAR.nav0)
            self.assertIn('funding', self.a.bacak_funding_tur[b])

    def test_pazartesi_r30_s_trend(self):
        haftalik = [k for k in _karar_carry(self.s) if 'r30' in k.veri['hedef']['carry'].get('tanilar', {})]
        self.assertGreater(len(haftalik), 0)
        for k in haftalik:
            cr = k.veri['hedef']['carry']
            self.assertEqual(set(cr['tanilar']['r30']), set(cr['adaylar']))
            self.assertEqual(set(cr['tanilar']['s_trend']), set(cr['adaylar']))
            for v in list(cr['tanilar']['r30'].values()) + list(cr['tanilar']['s_trend'].values()):
                self.assertTrue(v is None or isinstance(v, float))

    def test_bant_oncesi_trend_hedefi(self):
        kk = _karar_carry(self.s)
        self.assertTrue(all('w_trend_yildiz' in k.veri['hedef']['tanilar'] for k in kk if k.veri['hedef']['coinler']))
        self.assertTrue(any(k.veri['hedef']['tanilar'].get('w_trend_yildiz') for k in kk))


class IsimTest(_Kosu):
    """kapi/isim.py gercek kosu uzerinde (CiktiTest'in kosusu)."""

    def test_tutulan_ve_katki(self):
        from kapi import betimsel_kayit as bk
        from kapi import isim
        kk = bk.karar_kayitlari(self.s.gunluk, AYAR.t0_ms, gun_ms(CARRY_GUN))
        tut = isim.tutulan_isimler(kk, P.btc)
        self.assertGreater(len(tut), 0)
        self.assertNotIn(P.btc, tut)
        katki = isim.isim_katkilari(self.a, AYAR.t0_ms, gun_ms(CARRY_GUN), tut)
        a0 = int(np.searchsorted(self.a.saat_ms, AYAR.t0_ms))
        a1 = int(np.searchsorted(self.a.saat_ms, gun_ms(CARRY_GUN)))
        self.assertAlmostEqual(sum(katki.values()) + float(np.sum(self.a.carry_coin[P.btc][a0:a1])),
                               float(sum(np.sum(v[a0:a1]) for v in self.a.carry_coin.values())), delta=1e-6)

    def test_sifir_sifir_ve_bacak(self):
        from kapi import betimsel_kayit as bk
        from kapi import isim
        from kapi.seriler import NavOkuyucu
        kk = bk.karar_kayitlari(self.s.gunluk, AYAR.t0_ms, gun_ms(CARRY_GUN))
        t = isim.sifir_sifir_tanisi(self.a, kk)
        self.assertGreaterEqual(t['mutlak'], abs(t['toplam']))
        pz = [k.damga_ms for k in kk if (k.damga_ms // bk.GUN_MS + 3) % 7 == 0][:4]
        nav = NavOkuyucu(self.s.nav_ms, self.s.nav, AYAR.nav0)
        b = isim.bacak_serileri(self.a, kk, pz, nav, AYAR.L, P.carry_omega, P.btc)
        self.assertEqual(len(b['long']), len(pz))
        self.assertTrue(np.any(b['long'] != 0.0) and np.any(b['short'] != 0.0))
        for w, t in enumerate(pz):                           # T15-13: long + short + hedge = haftalik carry toplami
            a0 = int(np.searchsorted(self.a.saat_ms, t))
            a1 = int(np.searchsorted(self.a.saat_ms, t + 7 * bk.GUN_MS))
            top = sum(float(np.sum(v[a0:a1])) for v in self.a.carry_coin.values()) / (P.carry_omega * AYAR.L * nav(t))
            self.assertAlmostEqual(b['long'][w] + b['short'][w] + b['hedge'][w], top, delta=1e-12)


class V6ReferansTest(_Kosu):
    def test_a_referansi_sanal_trend(self):
        # T15-6: A referansinda pozisyonlar sanal trend bacagi, devreden yok, NAV korunur.
        from kapi import betimsel_kayit as bk
        from kapi import denetim as dn
        from motor.durum import nav_hesapla
        from motor.gorunum import gorunum_kur
        sayac = 0
        for k, d in bk.karar_oncesi_durumlar(self.s.gunluk, AYAR.t0_ms, gun_ms(CARRY_GUN)):
            if not d.sanal_carry:
                continue
            g = gorunum_kur(self.veri, k.damga_ms)
            a = dn.a_referans_durumu(d, g)
            self.assertEqual(a.pozisyonlar, {c: q for c, q in d.sanal_trend.items() if q != 0.0})
            self.assertEqual(a.devreden, {})
            self.assertAlmostEqual(nav_hesapla(a, g), nav_hesapla(d, g), delta=1e-6)
            sayac += 1
            if sayac >= 3:
                break
        self.assertEqual(sayac, 3)

    def test_v6_hedefleri(self):
        from kapi import denetim as dn
        w_b, w_a = dn.v6_hedefleri(self.veri, self.s.gunluk, P, AYAR.L, AYAR.t0_ms, gun_ms(CARRY_GUN))
        self.assertEqual(len(w_b), len(w_a))
        self.assertEqual(len(w_b), (gun_ms(CARRY_GUN) - AYAR.t0_ms) // 86_400_000)


class V5SaatlikTest(_Kosu):
    def test_saatlik_tuketim_ve_bozma(self):
        import copy
        import tempfile
        from kapi import denetim as dn
        d = tempfile.mkdtemp(prefix='v5_')
        try:
            yol = d + '/g.jsonl'
            dn.gunluk_yaz(self.s.gunluk, yol)
            v = dn.v5_tek_defter(self.s, yol, self.a)
            self.assertTrue(v['gecti'], v)
            kararlar, _, _ = dn.gunluk_oku_dogrula(yol)
            b = copy.copy(self.a)
            b.carry_q = {c: x.copy() for c, x in self.a.carry_q.items()}
            c0 = next(c for c, x in b.carry_q.items() if np.any(x != 0))
            i = int(np.nonzero(b.carry_q[c0])[0][5])
            b.carry_q[c0][i] *= 1.001
            self.assertEqual(dn.v5_saatlik(b, kararlar)['q_farkli_saat'], 1)
            b2 = copy.copy(self.a)
            b2.satirlar = dict(self.a.satirlar, artik_carry=self.a.satirlar['artik_carry'] + 1.0)
            self.assertFalse(dn.v5_saatlik(b2, kararlar)['gecti'])
            self.assertGreater(dn.v5_saatlik(b2, kararlar)['artik_farkli_saat'], 0)
        finally:
            import shutil
            shutil.rmtree(d, ignore_errors=True)


class ScBirebirTest(_Kosu):
    """T17-e: ayrıştırmanın tükettiği s^C (sc_q) isim/saat bazında diskten türetilenle birebir; toplamı koruyan
    ya da artığı sıfır saatteki yanlış pay yakalanır."""

    def _hazir(self):
        import copy
        import tempfile
        from kapi import denetim as dn
        d = tempfile.mkdtemp(prefix='sc_')
        dn.gunluk_yaz(self.s.gunluk, d + '/g.jsonl')
        kararlar, _, _ = dn.gunluk_oku_dogrula(d + '/g.jsonl')
        import shutil
        shutil.rmtree(d, ignore_errors=True)
        b = copy.copy(self.a)
        b.sc_q = {c: x.copy() for c, x in self.a.sc_q.items()}
        return dn, kararlar, b

    def test_sc_q_artik_carry_ile_ayni(self):
        st = self.a.satirlar
        toplam = sum(self.a.sc_q.get(c, 0.0) * x for c, x in self.a.artik_coin.items())
        np.testing.assert_allclose(st['artik_carry'], toplam, rtol=0, atol=1e-9 * AYAR.nav0)
        self.assertGreater(len(self.a.sc_q), 2)
        dn, kararlar, _ = self._hazir()
        v = dn.v5_saatlik(self.a, kararlar)
        self.assertEqual((v['sc_farkli_saat'], v['artik_farkli_saat'], v['gecti']), (0, 0, True))

    def test_artigi_sifir_saatte_yanlis_pay(self):
        dn, kararlar, b = self._hazir()
        c, i = next((c, int(i)) for c, x in b.sc_q.items() if c in b.artik_coin
                    for i in np.nonzero((x != 0) & (b.artik_coin[c] == 0))[0][:1])
        b.sc_q[c][i] += 0.2                                   # artık 0: artik_carry değişmez, pay yanlış
        v = dn.v5_saatlik(b, kararlar)
        self.assertEqual((v['sc_farkli_saat'], v['artik_farkli_saat']), (1, 0))
        self.assertFalse(v['gecti'])

    def test_toplami_koruyan_pay_degisimi(self):
        # Codex T17-e örneği: A = (1, -1) olan iki isimde paylar birlikte aynı miktar değişirse toplam değişmez.
        dn, kararlar, b = self._hazir()
        saat = len(b.saat_ms)
        b.artik_coin = {c: x.copy() for c, x in self.a.artik_coin.items()}
        b.satirlar = dict(self.a.satirlar)
        c1, c2 = sorted(c for c, x in b.sc_q.items() if np.any(x != 0))[:2]
        i = next(int(j) for j in range(saat) if b.sc_q[c1][j] != 0 and b.sc_q[c2][j] != 0)
        for c in (c1, c2):
            b.artik_coin.setdefault(c, np.zeros(saat))
        eski1, eski2 = b.artik_coin[c1][i], b.artik_coin[c2][i]
        b.artik_coin[c1][i], b.artik_coin[c2][i] = 1.0, -1.0
        ac = b.satirlar['artik_carry'].copy()
        ac[i] += (b.sc_q[c1][i] - b.sc_q[c2][i]) - (b.sc_q[c1][i] * eski1 + b.sc_q[c2][i] * eski2)
        b.satirlar['artik_carry'] = ac
        self.assertTrue(dn.v5_saatlik(b, kararlar)['gecti'])  # tutarlı sahte satır: geçer
        b.sc_q[c1][i] += 0.2
        b.sc_q[c2][i] += 0.2                                  # toplam (1·Δ − 1·Δ) değişmez
        v = dn.v5_saatlik(b, kararlar)
        self.assertEqual((v['sc_farkli_saat'], v['artik_farkli_saat']), (2, 0))
        self.assertFalse(v['gecti'])


class V5SonlulukTest(_Kosu):
    """T17-d: NaN/inf ve şekil/kapsam hataları V5'te eşit sayılmaz; karşılaştırmadan önce reddedilir."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        import tempfile
        from kapi import denetim as dn
        d = tempfile.mkdtemp(prefix='v5s_')
        dn.gunluk_yaz(cls.s.gunluk, d + '/g.jsonl')
        cls.kararlar, _, _ = dn.gunluk_oku_dogrula(d + '/g.jsonl')
        import shutil
        shutil.rmtree(d, ignore_errors=True)

    def _ayr(self, **deg):
        import copy
        b = copy.copy(self.a)
        b.carry_q = {c: x.copy() for c, x in self.a.carry_q.items()}
        b.artik_coin = {c: x.copy() for c, x in self.a.artik_coin.items()}
        b.satirlar = dict(self.a.satirlar)
        for k, v in deg.items():
            setattr(b, k, v)
        return b

    def _kararlar(self, alan, deger):
        import copy
        kk = copy.deepcopy(self.kararlar)
        c = next(k for k in kk if k['veri']['hedef']['carry'][alan])
        ad = next(iter(c['veri']['hedef']['carry'][alan]))
        c['veri']['hedef']['carry'][alan][ad] = deger
        return kk

    def _red(self, ayr=None, kararlar=None, neden=None):
        from kapi import denetim as dn
        v = dn.v5_saatlik(self.a if ayr is None else ayr, self.kararlar if kararlar is None else kararlar)
        self.assertFalse(v['gecti'], v)
        if neden:
            self.assertIn(neden, v['neden'])

    def test_temel_gecer(self):
        from kapi import denetim as dn
        self.assertTrue(dn.v5_saatlik(self.a, self.kararlar)['gecti'])

    def test_nan_inf_miktar_ve_artik(self):
        c0 = next(c for c, x in self.a.carry_q.items() if np.any(x != 0))
        i = int(np.nonzero(self.a.carry_q[c0])[0][3])
        for v in (np.nan, np.inf):
            b = self._ayr()
            b.carry_q[c0][i] = v
            self._red(b, neden='sonlu olmayan')
            b = self._ayr()
            b.satirlar['artik_carry'] = b.satirlar['artik_carry'].copy()
            b.satirlar['artik_carry'][i] = v
            self._red(b, neden='artik_carry')
            b = self._ayr()
            a0 = next(iter(b.artik_coin))
            b.artik_coin[a0][i] = v
            self._red(b, neden='artik_coin')

    def test_nan_inf_karar_kaydi(self):
        for alan in ('sanal_carry', 'sc'):
            for v in (float('nan'), float('inf')):
                self._red(kararlar=self._kararlar(alan, v), neden='karar kayitlari')

    def test_sekil_ve_kapsam(self):
        c0 = next(iter(self.a.carry_q))
        b = self._ayr()
        b.carry_q[c0] = b.carry_q[c0][:-1]
        self._red(b, neden='sekil')
        self._red(self._ayr(saat_ms=self.a.saat_ms[::-1].copy()), neden='izgarasi')
        self._red(self._ayr(saat_ms=np.array([], dtype=np.int64)), neden='bos')
        self._red(kararlar=self.kararlar[::-1], neden='artan')
        self._red(kararlar=[], neden='karar kaydi yok')
        n = len(self.a.saat_ms) // 2                                        # ızgara kararların yarısını kapsıyor
        b = self._ayr(saat_ms=self.a.saat_ms[n:].copy(), carry_q={c: x[n:] for c, x in self.a.carry_q.items()},
                      artik_coin={c: x[n:] for c, x in self.a.artik_coin.items()},
                      satirlar=dict(self.a.satirlar, artik_carry=self.a.satirlar['artik_carry'][n:]))
        self._red(b, neden='disinda')

    def test_gunluk_karsilastirma_nan_esit_sayilmaz(self):
        from kapi import denetim as dn
        c = {'kappa': 1.0, 'kappa_etkin': 1.0, 'sc': {'X': float('nan')}, 'sanal_carry': {'X': 1.0}}
        self.assertFalse(dn._carry_esit(c, c))
        c2 = dict(c, sc={'X': 0.5}, sanal_carry={'X': float('inf')})
        self.assertFalse(dn._carry_esit(c2, c2))
        self.assertFalse(dn._carry_esit(dict(c2, sanal_carry={'X': 1.0}, kappa=float('nan')),
                                        dict(c2, sanal_carry={'X': 1.0}, kappa=float('nan'))))
        self.assertTrue(dn._carry_esit(dict(c2, sanal_carry={'X': 1.0}), dict(c2, sanal_carry={'X': 1.0})))


class BacakGecFundingTest(unittest.TestCase):
    """U-49/U-64, T17-f: eski payın funding kısmı ayrıştırmanın özgün yön ayrımıyla (carry_fon_long/short) bacağa gider;
    kalan (fiyat, kapanan kısmın maliyeti) saat başındaki miktarın işaretine."""
    H = 3_600_000
    bas = 1_696_204_800_000                                              # Pazartesi 00:00

    def _ayr(self, eski, yeni, fl=None, fs=None):
        from types import SimpleNamespace
        n = 24 * 7
        saat = self.bas + np.arange(n, dtype=np.int64) * self.H
        ek = {}
        if fl is not None:
            ek['carry_fon_long'] = {'A': fl}
        if fs is not None:
            ek['carry_fon_short'] = {'A': fs}
        return SimpleNamespace(saat_ms=saat, carry_coin={'A': eski + yeni}, carry_eski={'A': eski},
                               carry_yeni={'A': yeni}, **ek)

    def _karar(self, t, q):
        from types import SimpleNamespace
        return SimpleNamespace(damga_ms=t, veri={'hedef': {'carry': {'sanal_carry': q}}})

    def test_kapanmis_pozisyonun_gec_funding_i_ozgun_yone(self):
        from kapi import isim
        n = 24 * 7
        eski, yeni, fl = np.zeros(n), np.zeros(n), np.zeros(n)
        eski[30] = fl[30] = -5.0                                          # kapanıştan sonra long döneminin dolgusu
        yeni[2] = 7.0
        kk = [self._karar(self.bas, {'A': 2.0}), self._karar(self.bas + 24 * self.H, {})]
        b = isim.bacak_serileri(self._ayr(eski, yeni, fl=fl), kk, [self.bas], lambda t: 1.0, 1.0, 1.0, 'BTCUSDT')
        self.assertAlmostEqual(b['long'][0], 2.0, places=12)
        self.assertEqual(b['short'][0], 0.0)

    def test_short_acikken_gelen_long_dolgusu_long_a(self):
        # T17-f: long 01:00'e kadar, sonra short; long saatlerinin dolgusu short açıkken yazılır. Eski kural (T16, son
        # işaret) hepsini short'a yazardı; özgün yön ayrımıyla long payı long'a, short payı short'a gider.
        from kapi import isim
        n = 24 * 7
        eski, yeni, fl, fs = np.zeros(n), np.zeros(n), np.zeros(n), np.zeros(n)
        fl[28], fs[28] = -3.0, -1.0                                       # 04:00 (ertesi gün) dolgusu: iki yön
        fl[32], fs[32] = 0.5, 2.0                                         # 08:00 ters kayıt (+ gerçek kayıt)
        eski[28], eski[32] = fl[28] + fs[28], fl[32] + fs[32]
        eski[40] = -0.25                                                  # short'un fiyat payı
        kk = [self._karar(self.bas, {'A': 2.0}), self._karar(self.bas + 24 * self.H, {'A': -3.0})]
        b = isim.bacak_serileri(self._ayr(eski, yeni, fl=fl, fs=fs), kk, [self.bas], lambda t: 1.0, 1.0, 1.0,
                                'BTCUSDT')
        self.assertAlmostEqual(b['long'][0], -3.0 + 0.5, places=12)
        self.assertAlmostEqual(b['short'][0], -1.0 + 2.0 - 0.25, places=12)


class FonYonuBirimTest(unittest.TestCase):
    """motor.ayristirma.fon_yonu: olayın (long, short) payı özgün saatin bacak miktarı işaretinden (T17-f)."""
    H = 3_600_000

    def _o(self, tur, tutar, **veri):
        from motor.funding import FundingOlayi
        return FundingOlayi(tur, tutar, dict(veri, tutar=tutar))

    def test_gercek_kayit(self):
        from motor.ayristirma import fon_yonu
        self.assertEqual(fon_yonu(self._o('funding', -2.5, q=4.0, damga_ms=0), (), ()), (-2.5, 0.0))
        self.assertEqual(fon_yonu(self._o('funding', 1.5, q=-4.0, damga_ms=0), (), ()), (0.0, 1.5))
        self.assertEqual(fon_yonu(self._o('funding', 0.0, q=0.0, damga_ms=0), (), ()), (0.0, 0.0))

    def test_dolgu_ve_ters_kayit_yon_degisimini_boler(self):
        from motor.ayristirma import fon_yonu
        H = self.H
        gecmis = ((0, 2.0), (10 * H, -3.0))                              # 10:00'da long -> short
        d = self._o('funding_dolgu', -7.0, saatler=[[9 * H, -1.0], [10 * H, -2.0], [11 * H, -4.0]])
        self.assertEqual(fon_yonu(d, (), gecmis), (-3.0, -4.0))           # q(10:00-) hâlâ long
        bekleyen = ((9 * H, -1.0), (10 * H, -2.0), (11 * H, -4.0), (20 * H, -8.0))
        t = self._o('ters_kayit', 7.0, damga_ms=16 * H, aralik_saat=8.0, dolgu_sayisi=3)
        self.assertEqual(fon_yonu(t, bekleyen, gecmis), (3.0, 4.0))       # (8:00, 16:00]; 20:00 kapsam dışı

    def test_parcalar(self):
        from motor.ayristirma import fon_parcalari
        H = self.H
        self.assertEqual(fon_parcalari('funding', {'tutar': -2.5, 'damga_ms': 8 * H, 'q': 4.0}, ()), [(8 * H, -2.5)])
        self.assertEqual(fon_parcalari('funding', {'tutar': 0.0, 'damga_ms': 8 * H}, ()), [])
        self.assertEqual(fon_parcalari('funding_dolgu', {'tutar': -3.0, 'saatler': [[H, -1.0], [2 * H, -2.0]]}, ()),
                         [(H, -1.0), (2 * H, -2.0)])
        bekleyen = ((9 * H, -1.0), (11 * H, -4.0), (20 * H, -8.0))
        self.assertEqual(fon_parcalari('ters_kayit', {'tutar': 5.0, 'damga_ms': 16 * H, 'aralik_saat': 8.0}, bekleyen),
                         [(9 * H, 1.0), (11 * H, 4.0)])

    def test_tutarsizlik_hata(self):
        from motor.ayristirma import AyristirmaHatasi, fon_yonu
        H = self.H
        with self.assertRaises(AyristirmaHatasi):                         # kapsanan küme olay tutarıyla tutmuyor
            fon_yonu(self._o('ters_kayit', 6.0, damga_ms=16 * H, aralik_saat=8.0), ((9 * H, -1.0), (11 * H, -4.0),
                                                                                    (12 * H, -2.0)), ((0, 2.0),))
        with self.assertRaises(AyristirmaHatasi):                         # dolgu saatinde bacak miktarı 0
            fon_yonu(self._o('funding_dolgu', -1.0, saatler=[[H, -1.0]]), (), ((2 * H, 1.0),))


YON_COIN, YON_GUN = 'A02', 107                                          # oran gün 95'ten sonra +0,0015: gün 107 long -> short


def _yon_kosusu():
    """Carry senaryosunun değişik hali: A02'nin funding oranı gün 95'ten itibaren +0,0015 (carry bacağı gün 107
    Pazartesi kararıyla long'dan short'a döner) ve gün 107 00:00 kaydı yok. Son gerçek kayıt 106 16:00; 107 04:00'te
    eksik tespit edilir (dolgu 17:00-04:00: 01:00'e kadar long, sonra short); 107 08:00 kaydı (00:00, 08:00]
    dolgularını ters kaydeder (01:00 long, 02:00-07:00 short)."""
    if 'yon' not in _KOSU:
        from motor.gorunum import TamVeri, funding_serisi
        veri = carry_senaryo_verisi()
        f = veri.funding[YON_COIN]
        r = f.oran.copy()
        r[f.damga_ms >= gun_ms(95)] = 0.0015
        tut = f.damga_ms != gun_ms(YON_GUN)
        fund = dict(veri.funding)
        fund[YON_COIN] = funding_serisi(f.damga_ms[tut], r[tut])
        v2 = TamVeri(barlar=veri.barlar, funding=fund, adaylar=veri.adaylar)
        s = kos(v2, AYAR, P)
        _KOSU['yon'] = (v2, s, ayristir(s.gunluk, v2, P))
    return _KOSU['yon']


class FonYonuKosuTest(unittest.TestCase):
    """Uçtan uca (sentetik): yön değişimini kapsayan dolgu ve ters kayıt özgün yönlere bölünür; bacak serileri izler."""

    @classmethod
    def setUpClass(cls):
        cls.veri, cls.s, cls.a = _yon_kosusu()
        cls.n4 = int(np.searchsorted(cls.a.saat_ms, gun_ms(YON_GUN) + 4 * 3_600_000))
        cls.n8 = int(np.searchsorted(cls.a.saat_ms, gun_ms(YON_GUN) + 8 * 3_600_000))

    def test_senaryo_kuruldu(self):
        tur = self.a.bacak_funding_tur['C']
        self.assertGreaterEqual(tur['funding_dolgu'][YON_COIN][0], 1)
        self.assertGreaterEqual(tur['ters_kayit'][YON_COIN][0], 1)
        q = self.a.carry_q[YON_COIN]
        self.assertGreater(q[self.n4 - 4], 0.0)                           # 00:00 saatinde long
        self.assertLess(q[self.n4 - 1], 0.0)                              # 03:00'ten önce short (04:00'te short)

    def test_toplam_ozdesligi(self):
        tur = self.a.bacak_funding_tur['C']
        for c in set(self.a.carry_fon_long) | set(self.a.carry_fon_short):
            beklenen = sum(v[c][1] for v in tur.values() if c in v)
            z = np.zeros(len(self.a.saat_ms))
            toplam = float(np.sum(self.a.carry_fon_long.get(c, z) + self.a.carry_fon_short.get(c, z)))
            self.assertAlmostEqual(toplam, beklenen, delta=1e-9 * max(1.0, abs(beklenen)))

    def test_dolgu_ve_ters_kayit_iki_yone(self):
        fl, fs = self.a.carry_fon_long[YON_COIN], self.a.carry_fon_short[YON_COIN]
        self.assertLess(fl[self.n4], 0.0)                                 # 17:00-01:00 long saatleri (short açıkken)
        self.assertLess(fs[self.n4], 0.0)                                 # 02:00-04:00 short saatleri
        self.assertGreater(fl[self.n8], 0.0)                              # 01:00 long dolgusunun tersi
        saatlik_long = fl[self.n4] / 9.0                                  # 9 long saatin ortalaması
        self.assertLess(abs(fl[self.n8] + saatlik_long), 0.05 * abs(saatlik_long))

    def test_bacak_serileri_ozgun_yonu_izler(self):
        import copy
        from kapi import betimsel_kayit as bk
        from kapi import isim
        from kapi.seriler import NavOkuyucu
        kk = bk.karar_kayitlari(self.s.gunluk, AYAR.t0_ms, gun_ms(CARRY_GUN))
        nav = NavOkuyucu(self.s.nav_ms, self.s.nav, AYAR.nav0)
        hafta = [gun_ms(YON_GUN)]
        yeni = isim.bacak_serileri(self.a, kk, hafta, nav, AYAR.L, P.carry_omega, P.btc)
        b = copy.copy(self.a)                                             # eski davranış: funding'in tamamı short'ta
        fl, fs = self.a.carry_fon_long[YON_COIN].copy(), self.a.carry_fon_short[YON_COIN].copy()
        for n in (self.n4, self.n8):
            fs[n] += fl[n]
            fl[n] = 0.0
        b.carry_fon_long = dict(self.a.carry_fon_long, **{YON_COIN: fl})
        b.carry_fon_short = dict(self.a.carry_fon_short, **{YON_COIN: fs})
        eski = isim.bacak_serileri(b, kk, hafta, nav, AYAR.L, P.carry_omega, P.btc)
        payda = P.carry_omega * AYAR.L * nav(hafta[0])
        fark = (self.a.carry_fon_long[YON_COIN][self.n4] + self.a.carry_fon_long[YON_COIN][self.n8]) / payda
        self.assertAlmostEqual(yeni['long'][0] - eski['long'][0], fark, delta=1e-12)
        self.assertAlmostEqual(yeni['short'][0] - eski['short'][0], -fark, delta=1e-12)
        a0, a1 = int(np.searchsorted(self.a.saat_ms, hafta[0])), int(np.searchsorted(self.a.saat_ms,
                                                                                       hafta[0] + 7 * 86_400_000))
        top = sum(float(np.sum(v[a0:a1])) for v in self.a.carry_coin.values()) / payda
        self.assertAlmostEqual(yeni['long'][0] + yeni['short'][0] + yeni['hedge'][0], top, delta=1e-12)


if __name__ == '__main__':
    unittest.main()
