"""MIMARI Ss5.2 olay sirasi, Ss5.6 parite ve bakis-ileri testleri, Ss5.8 gunlukten durum kurulumu; uctan uca
sentetik senaryo (borsa capi bosluk, islem disi coin, maske cikisi, delist uzlasmasi, aylik + gunluk ayni gun).
Gercek veri, ag ya da borsa yok."""
import math
import sys as _sys
import unittest
from pathlib import Path as _Path

import numpy as np

TESTLER_DIR = _Path(__file__).resolve().parent
V8_DIR = TESTLER_DIR.parent
for _dir in (V8_DIR, TESTLER_DIR):
    if str(_dir) not in _sys.path:
        _sys.path.insert(1, str(_dir))

from fikstur.saatlik_veri import (GUN, SAAT, SENARYO_DELIST_GUN, SENARYO_GUN, SENARYO_ISLEM_DISI_GUN,  # noqa: E402
                                  SENARYO_T0_GUN, gun_ms, saat_ms, senaryo_verisi)
from motor.durum import durum_turet  # noqa: E402
from fikstur.saatlik_veri import CoinTarifi, tam_veri_uret  # noqa: E402
from motor.geri_test import KosuAyarlari, _Kosucu, kos  # noqa: E402
from motor.durum import Emir, MaliyetBaglami  # noqa: E402
from motor.gorunum import (FundingSerisi, TamVeri, bar_indeksi, gorunum_kur, saatlik_seri,  # noqa: E402
                           son_kapanis)
from motor.gunluk import OlayGunlugu  # noqa: E402
from motor.hedef import isim_tavani  # noqa: E402
from motor.karar import karar_ver  # noqa: E402
from motor.tavanlar import _kayip_s1, _kayip_s2  # noqa: E402
from motor.tipler import Parametreler  # noqa: E402

P = Parametreler()
AYAR = KosuAyarlari(t0_ms=gun_ms(SENARYO_T0_GUN), t_son_ms=saat_ms(SENARYO_GUN * 24 - 1))
NAKIT_TURLERI = ('funding', 'funding_dolgu', 'ters_kayit')


def _gun(t_ms):
    return (t_ms - gun_ms(0)) // GUN


class _Senaryo(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.veri = senaryo_verisi()
        cls.s = kos(cls.veri, AYAR, P)
        cls.kararlar = {_gun(k.hedef.t_ms): k for k in cls.s.kararlar}
        cls.kayitlar = cls.s.gunluk.kayitlar()


class GunlukVeDurumTest(_Senaryo):
    def test_zincir_dogrulanir_ve_kosu_deterministik(self):
        self.assertTrue(self.s.gunluk.dogrula())
        self.assertEqual(kos(self.veri, AYAR, P).gunluk.son_hash, self.s.gunluk.son_hash)

    def test_durum_gunlukten_birebir_yeniden_kurulur(self):
        g = gorunum_kur(self.veri, int(self.s.nav_ms[-1]))
        d = durum_turet(g, self.s.gunluk)
        self.assertEqual(d.pozisyonlar, self.s.durum.pozisyonlar)
        self.assertEqual(d.nakit, self.s.durum.nakit)
        self.assertEqual({c: e.json() for c, e in d.devreden.items()},
                         {c: e.json() for c, e in self.s.durum.devreden.items()})
        self.assertEqual((d.evren, d.maske, d.uzlasilan), (self.s.durum.evren, self.s.durum.maske,
                                                           self.s.durum.uzlasilan))

    def test_muhasebe_ozdesligi(self):
        nakit = AYAR.nav0
        poz = {}
        for k in self.kayitlar:
            if k.tur in ('dolum', 'uzlasma'):
                nakit -= k.miktar * k.fiyat
                poz[k.coin] = poz.get(k.coin, 0.0) + k.miktar
            elif k.tur in NAKIT_TURLERI:
                nakit += k.veri['tutar']
        self.assertAlmostEqual(nakit, self.s.durum.nakit, delta=1e-6)
        for c, q in poz.items():
            self.assertAlmostEqual(q, self.s.durum.pozisyonlar.get(c, 0.0), delta=1e-9 * max(1.0, abs(q)))
        son = int(self.s.nav_ms[-1])
        nav = self.s.durum.nakit + sum(q * son_kapanis(self.veri.barlar[c], son)
                                       for c, q in self.s.durum.pozisyonlar.items())
        self.assertAlmostEqual(nav, self.s.nav[-1], delta=1e-6)


class OlaySirasiTest(_Senaryo):
    def test_isinmada_islem_yok_ilk_karar_t0(self):
        self.assertEqual(min(self.kararlar), SENARYO_T0_GUN)
        self.assertTrue(all(k.damga_ms >= AYAR.t0_ms for k in self.kayitlar))

    def test_00_00_da_dolum_yok_ve_katilim_siniri(self):
        dolumlar = [k for k in self.kayitlar if k.tur == 'dolum']
        self.assertGreater(len(dolumlar), 20)
        for k in dolumlar:
            self.assertNotEqual(k.damga_ms % GUN, 0)
            s = self.veri.barlar[k.coin]
            acilis = float(s.acilis[bar_indeksi(s, k.damga_ms)])
            self.assertLessEqual(abs(k.miktar) * acilis, k.veri['q_max'] * (1 + 1e-9))

    def test_ayni_damgada_once_funding_sonra_dolum(self):
        sira = {}
        for i, k in enumerate(self.kayitlar):
            sira.setdefault((k.damga_ms, k.coin, k.tur), i)
        for (damga, coin, tur), i in sira.items():
            if tur == 'dolum' and (damga, coin, 'funding') in sira:
                self.assertLess(sira[(damga, coin, 'funding')], i)

    def test_aylik_ve_gunluk_ayni_gun(self):
        self.assertEqual(self.kararlar[SENARYO_T0_GUN].evren_ms, gun_ms(SENARYO_T0_GUN))
        self.assertEqual(self.kararlar[122].evren_ms, gun_ms(SENARYO_T0_GUN))
        self.assertEqual(self.kararlar[123].evren_ms, gun_ms(123))            # 2023-11-01
        self.assertEqual(len(self.kararlar[SENARYO_T0_GUN].evren), 5)
        self.assertNotIn('ALT2', self.kararlar[123].evren)                    # maskeli: uygun degil
        self.assertNotIn('ALT3', self.kararlar[123].evren)


class HedefDegismezleriTest(_Senaryo):
    def test_tavanlar_ve_t4(self):
        for gun, kr in self.kararlar.items():
            h = kr.hedef
            self.assertLessEqual(h.tanilar['v_net'], AYAR.L * P.tau * (1 + 1e-9), gun)
            if 'v_birim' in h.tanilar:
                self.assertLessEqual(h.tanilar['v_birim'], P.tau * (1 + 1e-9), gun)
            if h.sabit:
                continue
            w = np.array([h.w_yildiz[c] for c in h.coinler])
            be = np.array([c in (P.btc, P.eth) for c in h.coinler])
            for c, x in h.w_yildiz.items():
                self.assertLessEqual(abs(x), isim_tavani(c, x, P) * (1 + 1e-12), (gun, c))
            self.assertLessEqual(float(np.abs(w).sum()), P.brut_tavan)
            self.assertLessEqual(_kayip_s1(w, be, P), P.s1_sinir * (1 + 1e-12))
            self.assertLessEqual(_kayip_s2(w, be, P), P.s2_sinir * (1 + 1e-12))


class SenaryoTest(_Senaryo):
    def test_borsa_capi_bosluk_reduce_only(self):
        kr = self.kararlar[100]
        self.assertTrue(kr.hedef.reduce_only)
        self.assertFalse(self.kararlar[99].hedef.reduce_only)
        self.assertFalse(self.kararlar[101].hedef.reduce_only)
        h = kr.hedef
        for c in h.coinler:
            self.assertLessEqual(abs(h.w_yildiz[c]), abs(h.w_mevcut[c]) + 1e-15, c)
            self.assertGreaterEqual(h.w_yildiz[c] * h.w_mevcut[c], 0.0, c)
        for c, e in kr.niyetler.items():
            self.assertLess(e.kalan * h.w_mevcut[c], 0.0, c)       # yalniz risk azaltan emir

    def test_islem_disi_coin_mevcut_agirlikta_sabit(self):
        h = self.kararlar[SENARYO_ISLEM_DISI_GUN].hedef
        self.assertIn('ALT1', h.sabit)
        self.assertNotIn('ALT1', self.kararlar[SENARYO_ISLEM_DISI_GUN].niyetler)
        self.assertEqual(h.w_yildiz['ALT1'], h.w_mevcut['ALT1'])
        self.assertNotIn('ALT1', self.kararlar[SENARYO_ISLEM_DISI_GUN + 1].hedef.sabit)

    def test_maske_cikisi_uc_kat_maliyetle(self):
        ilk = min(g for g, kr in self.kararlar.items() if 'ALT2' in kr.hedef.maskeli)
        self.assertGreater(ilk, 115)
        kr = self.kararlar[ilk]
        self.assertEqual(kr.hedef.w_yildiz['ALT2'], 0.0)
        e = kr.niyetler['ALT2']
        self.assertTrue(e.maske_cikisi and e.tam_kapanis)
        cikislar = [k for k in self.kayitlar if k.tur == 'dolum' and k.coin == 'ALT2' and k.damga_ms > gun_ms(ilk)]
        self.assertTrue(cikislar)
        for k in cikislar:
            self.assertLess(k.miktar, 0.0)
            self.assertGreaterEqual(k.veri['maliyet_bps'], P.ucret_bps + 3 * P.dilim_50_200m_bps)
        self.assertNotIn('ALT2', self.s.durum.pozisyonlar)

    def test_delist_uzlasmasi_ve_funding_tahakkuku_durur(self):
        uz = [k for k in self.kayitlar if k.tur == 'uzlasma']
        self.assertEqual([(k.coin, _gun(k.damga_ms)) for k in uz], [('ALT3', SENARYO_DELIST_GUN + 30)])
        kap = son_kapanis(self.veri.barlar['ALT3'], gun_ms(SENARYO_DELIST_GUN + 30))
        self.assertAlmostEqual(uz[0].fiyat, kap * (1 - P.delist_h_long), places=12)
        self.assertGreater(uz[0].veri['q'], 0.0)
        bitis = saat_ms(SENARYO_DELIST_GUN * 24)
        self.assertFalse([k for k in self.kayitlar if k.coin == 'ALT3' and k.tur in NAKIT_TURLERI
                          and k.damga_ms > bitis])
        for gun in range(SENARYO_DELIST_GUN + 1, SENARYO_DELIST_GUN + 30):
            self.assertIn('ALT3', self.kararlar[gun].hedef.sabit, gun)
            self.assertNotIn('ALT3', self.kararlar[gun].niyetler, gun)
        self.assertNotIn('ALT3', self.s.durum.pozisyonlar)


def _karar_oncesi_gunluk(kayitlar, t_ms):
    """t'deki uzlasma/karar kayitlarindan onceki onek (funding adimi dahil)."""
    for i, k in enumerate(kayitlar):
        if k.damga_ms == t_ms and k.tur in ('uzlasma', 'karar'):
            return OlayGunlugu.kayitlardan(kayitlar[:i])
    raise AssertionError('karar kaydi bulunamadi')


def _karar_json(kr):
    return (kr.hedef.json(), kr.bantli, {c: e.json() for c, e in kr.niyetler.items()}, kr.iptaller, kr.evren)


def _bozuk_veri(veri: TamVeri, t_ms: int) -> TamVeri:
    """t'den sonra kapanan butun barlari ve t'den sonraki funding'i bozar."""
    barlar = {}
    for c, s in veri.barlar.items():
        gelecek = s.acilis_ms + SAAT > t_ms
        carp = np.where(gelecek, 3.0, 1.0)
        barlar[c] = saatlik_seri(s.acilis_ms, s.acilis * carp, s.yuksek * carp, s.dusuk * carp, s.kapanis * carp,
                                 np.where(gelecek, 0.0, s.hacim))
    funding = {c: FundingSerisi(f.damga_ms, np.where(f.damga_ms > t_ms, f.oran * 100, f.oran))
               for c, f in veri.funding.items()}
    return TamVeri(barlar=barlar, funding=funding, adaylar=veri.adaylar)


class PariteTest(_Senaryo):
    def test_gunlukten_kurulan_durum_ayni_karari_uretir(self):
        # Canli yol: durum her karardan once gunlukten yeniden kurulur (MIMARI Ss5.8). Geri test yolu artimsal.
        for gun in (SENARYO_T0_GUN, 100, SENARYO_ISLEM_DISI_GUN, 111, 119, 123, 141):
            t = gun_ms(gun)
            g = gorunum_kur(self.veri, t)
            d = durum_turet(g, _karar_oncesi_gunluk(self.kayitlar, t))
            self.assertEqual(_karar_json(karar_ver(g, d, AYAR.L, P, AYAR.filtreler)),
                             _karar_json(self.kararlar[gun]), gun)

    def test_bakis_ileri_gelecek_veri_karari_degistirmez(self):
        for gun in (100, 119, 123):
            t = gun_ms(gun)
            d = durum_turet(gorunum_kur(self.veri, t), _karar_oncesi_gunluk(self.kayitlar, t))
            temiz = karar_ver(gorunum_kur(self.veri, t), d, AYAR.L, P)
            bozuk = karar_ver(gorunum_kur(_bozuk_veri(self.veri, t), t), d, AYAR.L, P)
            self.assertEqual(_karar_json(bozuk), _karar_json(temiz), gun)


class KosuVaryantlariTest(_Senaryo):
    def test_katilimsiz_golge_yol_ilk_saatte_dolar(self):
        g = kos(self.veri, KosuAyarlari(t0_ms=AYAR.t0_ms, t_son_ms=AYAR.t_son_ms, katilimsiz=True), P)
        dolumlar = [k for k in g.gunluk.kayitlar() if k.tur == 'dolum']
        self.assertTrue(dolumlar)
        self.assertTrue(all(k.damga_ms % GUN == SAAT for k in dolumlar))
        self.assertNotEqual(g.nav[-1], self.s.nav[-1])

    def test_maliyet_carpani_k3_ayri_tam_kosu(self):
        k3 = kos(self.veri, KosuAyarlari(t0_ms=AYAR.t0_ms, t_son_ms=AYAR.t_son_ms, maliyet_k=3.0), P)
        bps = [k.veri['maliyet_bps'] for k in k3.gunluk.kayitlar() if k.tur == 'dolum']
        self.assertGreaterEqual(min(bps), P.ucret_bps + 3 * P.dilim_btc_eth_bps)
        self.assertLess(k3.nav[-1], self.s.nav[-1])
        self.assertNotEqual(k3.gunluk.son_hash, self.s.gunluk.son_hash)


class CodexOrkestrasyonTest(unittest.TestCase):
    """Codex 2026-09-28 Slice 2 incelemesi: K3 (kapanmis pozisyonun eksik funding borcu), K5 (gun ici bosluk)."""

    def test_k3_kapanmis_pozisyon_dongude_kalir_ve_dolgu_alir(self):
        veri = tam_veri_uret({'X': CoinTarifi(saatlik_vol=0.002, funding_eksik=frozenset({400}))}, 20)
        k = _Kosucu(veri, KosuAyarlari(t0_ms=gun_ms(16), t_son_ms=saat_ms(410)), P)
        baglam = MaliyetBaglami(1e9, 1e9, 1e9, 10.0, float('nan'), False, float('nan'))
        k.yaz('baslangic', saat_ms(389), veri={'nav0': 1e5})
        for h in range(389, 410):
            T = saat_ms(h)
            k.funding_adimi(gorunum_kur(veri, T), T)          # MIMARI Ss5.2: funding, sonra dolum
            if h in (390, 398):
                q = 3.0 if h == 390 else -3.0
                k.yaz('emir_niyeti', T, coin='X', miktar=q, veri={'emir': Emir(q, 0, False, False, baglam).json()})
                k.yaz('dolum', T, coin='X', miktar=q, fiyat=100.0, veri={})
        self.assertNotIn('X', k.durum.pozisyonlar)
        self.assertEqual([x.damga_ms for x in k.gunluk.kayitlar() if x.tur == 'funding'], [saat_ms(392)])
        dolgu = [x for x in k.gunluk.kayitlar() if x.tur == 'funding_dolgu']
        self.assertEqual(len(dolgu), 1)
        self.assertEqual(dolgu[0].damga_ms, saat_ms(404))
        self.assertEqual([s for s, _ in dolgu[0].veri['saatler']], [saat_ms(h) for h in range(393, 399)])
        # 408 kaydi (400, 408] araligini kapsar: bu dolgulari geri almaz (400 uzlasmasina aittir; gec gelirse
        # geri alinir). q(408-) = 0 oldugundan 408 kaydi yazilmaz; dolgular gec kayit penceresinde bekler.
        self.assertFalse(any(x.tur in ('ters_kayit', 'funding') for x in k.gunluk.kayitlar()
                             if x.damga_ms > saat_ms(398)))
        self.assertEqual([h for h, _ in k.durum.funding_dolgu['X']], [saat_ms(h) for h in range(393, 399)])

    def test_k5_gun_ici_boslukta_giris_emri_iptal(self):
        # Dusuk hacim (V60 24M): giris emirleri saatlerce devreder. T0 + 5h'de BTC ve ETH bari yok (2/3).
        t = {c: CoinTarifi(saatlik_hacim=1e6, gunluk_suruklenme=0.01, saatlik_vol=0.005)
             for c in ('BTCUSDT', 'ETHUSDT', 'A1')}
        bosluk = 92 * 24 + 5
        for c in ('BTCUSDT', 'ETHUSDT'):
            t[c].eksik_saatler = frozenset({bosluk})
        veri = tam_veri_uret(t, 93)
        s = kos(veri, KosuAyarlari(t0_ms=gun_ms(92), t_son_ms=saat_ms(92 * 24 + 10)), P)
        kayitlar = s.gunluk.kayitlar()
        self.assertTrue(any(x.tur == 'emir_niyeti' and x.miktar > 0 for x in kayitlar))
        iptal = [x for x in kayitlar if x.tur == 'devreden_iptal' and x.veri.get('sebep') == 'borsa_bosluk']
        self.assertTrue(iptal)
        self.assertTrue(all(x.damga_ms == saat_ms(bosluk + 1) for x in iptal))
        self.assertEqual(s.durum.devreden, {})              # butun giris emirleri iptal
        self.assertFalse(any(x.tur == 'dolum' and x.damga_ms > saat_ms(bosluk + 1) for x in kayitlar))
        self.assertTrue(any(x.tur == 'dolum' and x.damga_ms < saat_ms(bosluk) for x in kayitlar))

if __name__ == '__main__':
    unittest.main()
