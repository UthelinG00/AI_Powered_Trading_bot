"""Mimari B butunlesik testleri (MIMARI Ss4, Ss5.6, Ss5.8): parite, bakis-ileri, ilk Pazartesi, net = sanal trend +
sanal carry, blok beta-notrlugu, kacirilan ve yapilan Pazartesi, hafta ici cikis, P&L ayristirma ozdesligi.
Sentetik veri; gercek veri, ag ya da borsa yok. Carry kapisi KOSULMAZ."""
import sys as _sys
import unittest
from dataclasses import replace
from pathlib import Path as _Path

TESTLER_DIR = _Path(__file__).resolve().parent
V8_DIR = TESTLER_DIR.parent
for _dir in (V8_DIR, TESTLER_DIR):
    if str(_dir) not in _sys.path:
        _sys.path.insert(1, str(_dir))

from fikstur.saatlik_veri import CARRY_CIKIS_GUNU, CARRY_GUN, GUN, carry_senaryo_verisi, gun_ms, saat_ms  # noqa: E402
from motor.ayristirma import ayristir  # noqa: E402
from motor.durum import StratejiDurumu, durum_turet, kayit_uygula  # noqa: E402
from motor.geri_test import KosuAyarlari, kos  # noqa: E402
from motor.gorunum import gorunum_kur  # noqa: E402
from motor.karar import kacirilan_karar, karar_ver  # noqa: E402
from motor.tipler import Parametreler  # noqa: E402
from test_v8_geri_test import _bozuk_veri, _karar_json, _karar_oncesi_gunluk  # noqa: E402

P = replace(Parametreler(), mimari='B')
T0_GUN = 92
AYAR = KosuAyarlari(t0_ms=gun_ms(T0_GUN), t_son_ms=saat_ms(CARRY_GUN * 24 - 1))


def _gun(t_ms):
    return (t_ms - gun_ms(0)) // GUN


class _BSenaryo(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.veri = carry_senaryo_verisi()
        cls.s = kos(cls.veri, AYAR, P)
        cls.kararlar = {_gun(k.hedef.t_ms): k for k in cls.s.kararlar}
        cls.kayitlar = cls.s.gunluk.kayitlar()


class TemelTest(_BSenaryo):
    def test_zincir_ve_ilk_pazartesi(self):
        self.assertTrue(self.s.gunluk.dogrula())
        self.assertEqual(self.kararlar[92].hedef.carry['q_yildiz'], {})      # 1 Ekim Pazar: carry yok
        ilk = self.kararlar[93].hedef.carry
        self.assertTrue(ilk['q_yildiz'])
        self.assertEqual(ilk['hafta_ms'], gun_ms(93))
        self.assertEqual(self.kararlar[94].hedef.carry['hafta_ms'], gun_ms(93))

    def test_a_varsayilani_carry_uretmez(self):
        g = gorunum_kur(self.veri, gun_ms(93))
        d = durum_turet(g, _karar_oncesi_gunluk(self.kayitlar, gun_ms(93)))
        self.assertIsNone(karar_ver(g, d, 1.0, Parametreler()).hedef.carry)

    def test_net_sanal_trend_arti_sanal_carry(self):
        for gun, kr in self.kararlar.items():
            h = kr.hedef
            if h.reduce_only:
                continue
            c_ = h.carry
            for c in h.coinler:
                if c in h.sabit or h.fiyat_ref[c] <= 0:
                    continue
                q_net = h.w_yildiz[c] * h.nav / h.fiyat_ref[c]
                q_bacak = c_['sanal_trend'].get(c, 0.0) + c_['sanal_carry'].get(c, 0.0)
                self.assertAlmostEqual(q_net, q_bacak, delta=1e-9 * max(1.0, abs(q_net)), msg=(gun, c))

    def test_carry_blogu_beta_notr(self):
        for gun, kr in self.kararlar.items():
            c_ = kr.hedef.carry
            if not c_['q_yildiz']:
                continue
            fr = kr.hedef.fiyat_ref
            beta_maruz = sum(c_['beta'][c] * c_['sanal_carry'].get(c, 0.0) * fr[c] for c in c_['q_yildiz'])
            hedge = c_['sanal_carry'].get(P.btc, 0.0) * fr[P.btc]
            self.assertAlmostEqual(beta_maruz + hedge, 0.0, delta=1e-9 * kr.hedef.nav, msg=gun)

    def test_hafta_ici_cikis_ve_yeniden_notrleme(self):
        once = self.kararlar[CARRY_CIKIS_GUNU].hedef.carry
        sonra = self.kararlar[CARRY_CIKIS_GUNU + 1].hedef.carry
        self.assertIn('A13', once['q_yildiz'])
        self.assertNotIn('A13', sonra['q_yildiz'])
        self.assertEqual(sonra['tanilar']['hafta_ici_cikis'], ['A13'])
        self.assertLessEqual(sonra['tanilar']['lambda_hafta_ici'], 1.0)
        for c, q in sonra['q_yildiz'].items():                 # hafta icinde hicbir alt miktari buyumez
            self.assertLessEqual(abs(q), abs(once['q_yildiz'][c]) + 1e-12, c)
        fr = self.kararlar[CARRY_CIKIS_GUNU + 1].hedef.fiyat_ref
        nl = sum(q * fr[c] for c, q in sonra['q_yildiz'].items() if q > 0)
        ns = -sum(q * fr[c] for c, q in sonra['q_yildiz'].items() if q < 0)
        self.assertAlmostEqual(nl, ns, delta=1e-9 * nl)


class PariteBTest(_BSenaryo):
    def test_gunlukten_kurulan_durum_ayni_karari_uretir(self):
        for gun in (92, 93, 94, CARRY_CIKIS_GUNU + 1, 100, 107, 121):
            t = gun_ms(gun)
            g = gorunum_kur(self.veri, t)
            d = durum_turet(g, _karar_oncesi_gunluk(self.kayitlar, t))
            self.assertEqual(_karar_json(karar_ver(g, d, AYAR.L, P, AYAR.filtreler)),
                             _karar_json(self.kararlar[gun]), gun)

    def test_bakis_ileri_gelecek_veri_karari_degistirmez(self):
        for gun in (93, 100, 107):
            t = gun_ms(gun)
            d = durum_turet(gorunum_kur(self.veri, t), _karar_oncesi_gunluk(self.kayitlar, t))
            temiz = karar_ver(gorunum_kur(self.veri, t), d, AYAR.L, P)
            bozuk = karar_ver(gorunum_kur(_bozuk_veri(self.veri, t), t), d, AYAR.L, P)
            self.assertEqual(_karar_json(bozuk), _karar_json(temiz), gun)

    def test_kacirilan_ve_yapilan_pazartesi_ayni_gorunumde_farkli_qc(self):
        # MIMARI Ss5.8: gun 100 (Pazartesi) karari yapilan ve kacirilan iki gecmis; gun 101'de ayni gorunum.
        pzt, sal = gun_ms(100), gun_ms(101)
        onek = _karar_oncesi_gunluk(self.kayitlar, pzt)
        g_pzt = gorunum_kur(self.veri, pzt)
        d0 = durum_turet(g_pzt, onek)
        yapilan = karar_ver(g_pzt, replace(d0, t_ms=pzt), AYAR.L, P)
        d_yap = d0
        for k in yapilan.kayitlar:
            d_yap = kayit_uygula(d_yap, onek.ekle(k.tur, pzt, coin=k.coin, miktar=k.miktar, veri=k.veri))
        onek2 = _karar_oncesi_gunluk(self.kayitlar, pzt)
        d_kac = d0
        for k in kacirilan_karar(d0, pzt):
            d_kac = kayit_uygula(d_kac, onek2.ekle(k.tur, pzt, coin=k.coin, veri=k.veri))
        g_sal = gorunum_kur(self.veri, sal)
        a = karar_ver(g_sal, replace(d_yap, t_ms=sal), AYAR.L, P).hedef.carry
        b = karar_ver(g_sal, replace(d_kac, t_ms=sal), AYAR.L, P).hedef.carry
        self.assertEqual(a['hafta_ms'], pzt)
        self.assertEqual(b['hafta_ms'], gun_ms(93 + 7 * ((100 - 93) // 7) - 7))
        self.assertNotEqual(a['q_yildiz'], b['q_yildiz'])
        for c, q in b['q_yildiz'].items():                      # kacirilan hafta: eski miktarlar (yalniz kucultur)
            self.assertLessEqual(abs(q), abs(d0.carry_q[c]) + 1e-12, c)


class AyristirmaTest(_BSenaryo):
    def test_ozdeslik_ve_artik_bolusumu(self):
        a = ayristir(self.s.gunluk, self.veri, P)
        self.assertLess(a.ozdeslik_max_hata, 1e-8 * AYAR.nav0)
        self.assertAlmostEqual(a.toplam['artik_carry'] + a.toplam['artik_trend'], a.toplam['icra_artigi'], places=9)
        self.assertAlmostEqual(a.toplam['dnav'], float(self.s.nav[-1]) - AYAR.nav0, places=6)
        self.assertNotEqual(a.toplam['carry_funding'], 0.0)
        self.assertGreater(a.toplam['carry_maliyet'], 0.0)
        self.assertGreater(a.toplam['trend_maliyet'], 0.0)


class AyristirmaDuzeltmeTest(unittest.TestCase):
    def test_duzeltme_nakdi_ozdeslige_girer(self):
        # Codex 4. tur: canli duzeltme kaydinin nakdi icra artigina yazilir; ozdeslik bozulmaz.
        import numpy as np
        from motor.gorunum import TamVeri, funding_serisi, saatlik_seri
        from motor.gunluk import OlayGunlugu
        H = 3_600_000
        a = np.ones(49) * 100
        s = saatlik_seri(np.arange(49) * H, a, a, a, a, np.ones(49) * 5e6)
        veri = TamVeri({'X': s}, {'X': funding_serisi([], [])}, ('X',))
        g = OlayGunlugu()
        g.ekle('baslangic', 0, veri={'nav0': 100000})
        g.ekle('karar', 0, veri={'hedef': {'carry': {'sanal_trend': {}, 'sanal_carry': {}, 'sc': {}}}, 'maske': {}})
        g.ekle('duzeltme', H, coin='X', veri={'tutar': 5})
        g.ekle('nav', 24 * H, veri={'nav': 100005})
        r = ayristir(g, veri, P)
        self.assertEqual(r.toplam['icra_artigi'], 5.0)
        self.assertLess(r.ozdeslik_max_hata, 1e-9)



def _bar_sil(veri, coin, saat):
    """coin'in `saat` indeksli barini siler (islem disi gun kurmak icin)."""
    import numpy as np
    from motor.gorunum import TamVeri, saatlik_seri
    s = veri.barlar[coin]
    tut = s.acilis_ms != saat_ms(saat)
    yeni = saatlik_seri(s.acilis_ms[tut], s.acilis[tut], s.yuksek[tut], s.dusuk[tut], s.kapanis[tut], s.hacim[tut])
    return TamVeri(barlar={**veri.barlar, coin: yeni}, funding=veri.funding, adaylar=veri.adaylar)


class TurBesBTest(_BSenaryo):
    """Inceleme wf_94f2a3aa-9a3 bulgulari (butunlesik): B2-B7, B9, B10, B13-B16."""

    def test_b9_lambda_hafta_icinde_tasinir_ve_durumda(self):
        pzt, sal = self.kararlar[100].hedef.carry, self.kararlar[101].hedef.carry
        self.assertEqual((sal['lam'], sal['bagli_bacak']), (pzt['lam'], pzt['bagli_bacak']))
        d = durum_turet(gorunum_kur(self.veri, gun_ms(101)), _karar_oncesi_gunluk(self.kayitlar, gun_ms(101)))
        self.assertEqual(d.carry_lam, pzt['lam'])
        self.assertEqual(d.carry_adaylar, tuple(pzt['adaylar']))

    def test_b16_kappa_etkin_sanal_carryi_uretir(self):
        for gun, kr in self.kararlar.items():
            c_ = kr.hedef.carry
            for c, q in c_['q_yildiz'].items():
                self.assertAlmostEqual(c_['sanal_carry'].get(c, 0.0), c_['kappa_etkin'] * q,
                                       delta=1e-12 * abs(q), msg=(gun, c))

    def test_b6_degismeyen_sanal_trend_birebir(self):
        gunler = sorted(self.kararlar)
        for a, b in zip(gunler, gunler[1:]):
            s0 = self.kararlar[a].hedef.carry['sanal_trend']
            s1 = self.kararlar[b].hedef.carry['sanal_trend']
            for c in set(s0) & set(s1):
                fark = abs(s1[c] - s0[c])
                self.assertFalse(0.0 < fark <= 1e-12 * abs(s0[c]), (b, c, s0[c], s1[c]))

    def _degismezler(self, kararlar, L):
        import numpy as np
        from motor.net_cozucu import ihlaller
        lim = L * (1 + P.carry_omega) * P.tau
        for gun, kr in kararlar.items():
            h = kr.hedef
            self.assertLessEqual(h.tanilar['v_net'], lim * (1 + 1e-9), gun)
            w = np.array([h.w_yildiz[c] for c in h.coinler])
            serbest = np.array([c not in h.sabit for c in h.coinler], bool)
            be = np.array([c in (P.btc, P.eth) for c in h.coinler], bool)
            if 'sabit_tavan_ihlali' not in h.tanilar:
                self.assertEqual(ihlaller(w, serbest, be, P), set(), gun)

    def test_b2_b5_nihai_kitap_degismezleri(self):
        self._degismezler(self.kararlar, AYAR.L)

    def test_b2_b3_yuksek_kaldiracta_kosu_tamamlanir(self):
        # Onceden S1/S2 baglayan her gun teknik hatayla duruyordu (L = 4).
        s4 = kos(self.veri, replace(AYAR, L=4.0), P)
        k4 = {_gun(k.hedef.t_ms): k for k in s4.kararlar}
        self.assertTrue(any('S1' in k.hedef.baglayan or 'S2' in k.hedef.baglayan or 'kappa' in k.hedef.baglayan
                            for k in k4.values()))
        self._degismezler(k4, 4.0)

    def test_b10_b13_islem_disi_tutulan_isim(self):
        # Pazartesi (gun 100) A00 (F30 ~ -%66) ve A12 islem disi (son bar yok). Tutulan A00 long'u funding tabanina
        # takilir (B13); tutulan A12 short'u korunur ve beta'si bu Pazartesi yeniden hesaplanir (B10).
        from dataclasses import replace as rp
        pzt = gun_ms(100)
        veri2 = _bar_sil(_bar_sil(self.veri, 'A00', 100 * 24 - 1), 'A12', 100 * 24 - 1)
        g = gorunum_kur(veri2, pzt)
        d0 = durum_turet(g, _karar_oncesi_gunluk(self.kayitlar, pzt))
        d = rp(d0, t_ms=pzt, carry_q={**d0.carry_q, 'A00': 500.0, 'A12': -500.0},
               carry_beta={**d0.carry_beta, 'A00': 9.99, 'A12': 9.99})
        c_ = karar_ver(g, d, AYAR.L, P).hedef.carry
        self.assertIn('A12', c_['tanilar']['sabit_mevcut'])
        self.assertNotIn('A00', c_['tanilar']['sabit_mevcut'])
        self.assertNotIn('A00', c_['q_yildiz'])
        self.assertIn('A12', c_['q_yildiz'])
        self.assertNotEqual(c_['beta']['A12'], 9.99)

    def test_b14_aday_histerezisi_evren_uyeligine_gore(self):
        # A05 hacmi gun 75'ten sonra 15M/gun: V30 = 15M (10M ile 20M arasi), V60 >= 20M. Onceki Pazartesi adayiysa
        # kalir, degilse giremez; A05'in pozisyon tasimasi gerekmez.
        from dataclasses import replace as rp
        from fikstur.saatlik_veri import carry_senaryo_tarifleri, tam_veri_uret
        t = carry_senaryo_tarifleri()
        t['A05'].hacim_carpani = {h: 0.125 for h in range(75 * 24, CARRY_GUN * 24)}
        veri3 = tam_veri_uret(t, CARRY_GUN)
        pzt = gun_ms(100)
        g = gorunum_kur(veri3, pzt)
        d0 = durum_turet(g, _karar_oncesi_gunluk(self.kayitlar, pzt))
        q = {c: v for c, v in d0.carry_q.items() if c != 'A05'}
        ile = karar_ver(g, rp(d0, t_ms=pzt, carry_q=q, carry_adaylar=tuple(sorted(set(d0.carry_adaylar) | {'A05'}))),
                        AYAR.L, P).hedef.carry
        siz = karar_ver(g, rp(d0, t_ms=pzt, carry_q=q, carry_adaylar=tuple(c for c in d0.carry_adaylar if c != 'A05')),
                        AYAR.L, P).hedef.carry
        self.assertIn('A05', ile['adaylar'])
        self.assertNotIn('A05', siz['adaylar'])

    def test_b15_hafta_ici_matris_pazartesi_adaylarini_kapsar(self):
        from dataclasses import replace as rp
        from motor.hedef import hedef_agirlik_ayrintili, karar_bosluklari
        from motor.karar import maske_ilerlet
        sal = gun_ms(101)
        g = gorunum_kur(self.veri, sal)
        d = rp(durum_turet(g, _karar_oncesi_gunluk(self.kayitlar, sal)), t_ms=sal)
        bos = karar_bosluklari(g, d, P)[0]
        d_b = rp(d, maske=maske_ilerlet(g, d, sal, P, bos))
        _, girdiler = hedef_agirlik_ayrintili(g, d_b, AYAR.L, P, bosluklar=bos)
        self.assertTrue(set(d.carry_adaylar) <= set(girdiler.k_coinler))

    def test_b7_maliyet_k_gunlukten(self):
        from motor.ayristirma import AyristirmaHatasi
        with self.assertRaises(AyristirmaHatasi):
            ayristir(self.s.gunluk, self.veri, P, maliyet_k=3.0)


class TurBesAyristirmaTest(unittest.TestCase):
    """B8 (bacak funding'i gercek net pozisyondan bagimsiz), B12 (miktarli duzeltme)."""

    def _dunya(self, qT, qC):
        import numpy as np
        from motor.funding import funding_saati
        from motor.gorunum import TamVeri, funding_serisi, saatlik_seri
        from motor.gunluk import OlayGunlugu
        H, N = 3_600_000, 48
        a = np.ones(N) * 10.0
        veri = TamVeri({'X': saatlik_seri(np.arange(N) * H, a, a, a, a, np.ones(N) * 1e7)},
                       {'X': funding_serisi([0, 8 * H, 16 * H], [1e-4] * 3)}, ('X',))   # 16. saatten sonra kayit yok
        bg = {'v1h30': 1e6, 'v1h7': 1e6, 'v60': 3e8, 'sigma_d_bps': 300.0, 'sigma_1h': 0.01, 'btc_eth': False,
              'btc_sigma_1h': 0.005}
        q = qT + qC
        g = OlayGunlugu()
        g.ekle('baslangic', 0, veri={'nav0': 100000, 'maliyet_k': 1.0})
        g.ekle('karar', 0, veri={'hedef': {'carry': {'sanal_trend': ({'X': qT} if qT else {}), 'sanal_carry': {'X': qC},
                                                     'sc': {'X': abs(qC) / (abs(qT) + abs(qC))}}},
                                 'maske': {}, 'sanal_baglam': {'X': bg}})
        d = StratejiDurumu(nav0=0.0)
        gecmis, nakit = [], 100000.0
        for T in range(0, N * H, H):
            if T > 0:
                for o in funding_saati(gorunum_kur(veri, T), 'X', T, tuple(gecmis), d.funding_dolgu.get('X', ()), P,
                                       islenen=d.funding_islenen.get('X', ()),
                                       dolgu_kadar=d.funding_dolgu_kadar.get('X')):
                    d = kayit_uygula(d, g.ekle(o.tur, T, coin='X', veri=o.veri))
                    nakit += o.tutar
            if T == H and q != 0:
                g.ekle('dolum', T, coin='X', miktar=q, fiyat=10.0, veri={'tam_kapanis_son': False})
                nakit -= q * 10
                gecmis.append((T, q))
            if (T + H) % (24 * H) == 0:
                g.ekle('nav', T + H, veri={'nav': nakit + q * 10})
        return ayristir(g, veri, P)

    def test_b8_carry_funding_net_pozisyondan_bagimsiz(self):
        yalniz_carry = self._dunya(0.0, -1000.0)              # gercek q = -1000
        netlenmis = self._dunya(1000.0, -1000.0)              # gercek q = 0 (dolgu kaydi yok)
        self.assertAlmostEqual(netlenmis.toplam['carry_funding'], yalniz_carry.toplam['carry_funding'], places=12)
        self.assertLess(yalniz_carry.toplam['carry_funding'], 0.0)
        for r in (yalniz_carry, netlenmis):
            self.assertLess(r.ozdeslik_max_hata, 1e-9)

    def test_b12_miktarli_duzeltme_ozdeslige_girer(self):
        import numpy as np
        from motor.gorunum import TamVeri, funding_serisi, saatlik_seri
        from motor.gunluk import OlayGunlugu
        H = 3_600_000
        a = np.ones(49) * 100
        veri = TamVeri({'X': saatlik_seri(np.arange(49) * H, a, a, a, a, np.ones(49) * 5e6)},
                       {'X': funding_serisi([], [])}, ('X',))
        g = OlayGunlugu()
        g.ekle('baslangic', 0, veri={'nav0': 100000})
        g.ekle('karar', 0, veri={'hedef': {'carry': {'sanal_trend': {}, 'sanal_carry': {}, 'sc': {}}}, 'maske': {}})
        g.ekle('duzeltme', H, coin='X', miktar=1.0, veri={'tutar': -100.0})   # fiyat 100: NAV degismez
        g.ekle('nav', 24 * H, veri={'nav': 100000})
        r = ayristir(g, veri, P)
        self.assertLess(r.ozdeslik_max_hata, 1e-9)
        self.assertAlmostEqual(r.toplam['icra_artigi'], 0.0, places=9)


if __name__ == '__main__':
    unittest.main()
