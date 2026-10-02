"""MIMARI Ss3.3 adim 8 (N_t = 0 / 1), Ss3.1 islem disi coin (sabit tavan girdisi), Ss5.8 kacirilan karar,
Ss5.1 dis bayrak modu. Sentetik veri, gercek islem yok."""
import sys as _sys
import unittest
from pathlib import Path as _Path

import numpy as np

TESTLER_DIR = _Path(__file__).resolve().parent
V8_DIR = TESTLER_DIR.parent
for _dir in (V8_DIR, TESTLER_DIR):
    if str(_dir) not in _sys.path:
        _sys.path.insert(1, str(_dir))

from fikstur.saatlik_veri import CoinTarifi, gun_ms, tam_veri_uret  # noqa: E402
from dataclasses import replace  # noqa: E402

from motor.durum import Emir, MaliyetBaglami, StratejiDurumu, durum_turet  # noqa: E402
from motor.gorunum import gorunum_kur  # noqa: E402
from motor.gunluk import OlayGunlugu  # noqa: E402
from motor.hijyen import DisBayraklar, HijyenBayraklari, gunluk_hijyen  # noqa: E402
from motor.karar import kacirilan_karar, karar_ver  # noqa: E402
from motor.tavanlar import tavan_coz  # noqa: E402
from motor.tipler import Parametreler  # noqa: E402

P = Parametreler()
BAGLAM = MaliyetBaglami(1e6, 1e6, 1e8, 10.0, 0.01, False, 0.01)


def _bos_durum(t_ms, nav0=100_000.0):
    g = OlayGunlugu()
    g.ekle('baslangic', t_ms, veri={'nav0': nav0})
    return durum_turet(gorunum_kur_bos(t_ms), g)


def gorunum_kur_bos(t_ms):
    from motor.gorunum import PiyasaGorunumu
    return PiyasaGorunumu(t_ms=t_ms, barlar={}, funding={}, adaylar=())


def _tarifler(hacimler: dict, **kw):
    return {c: CoinTarifi(saatlik_hacim=h, gunluk_suruklenme=0.01, saatlik_vol=0.005, **kw)
            for c, h in hacimler.items()}


class BosVeTekEvrenTest(unittest.TestCase):
    def test_n_sifir_isinmada_kitap_bos(self):
        veri = tam_veri_uret(_tarifler({'BTCUSDT': 50e6, 'ETHUSDT': 30e6, 'A1': 5e6}), 50)
        t = gun_ms(49)
        kr = karar_ver(gorunum_kur(veri, t), _bos_durum(t), 1.0, P)
        self.assertEqual(kr.evren, ())
        self.assertEqual((kr.hedef.a_t, kr.hedef.coinler, kr.niyetler), ((), (), {}))
        self.assertEqual(kr.hedef.tanilar['n_t'], 0)
        self.assertEqual(kr.hedef.tanilar['v_net'], 0.0)

    def test_n_bir_tek_coin_r_birim(self):
        # Yalniz BTC hacim tabanini gecer: R_hat = [1], M = 1, V(w^u) = tau * |s|.
        veri = tam_veri_uret(_tarifler({'BTCUSDT': 50e6, 'ETHUSDT': 0.5e6, 'A1': 0.5e6}), 100)
        t = gun_ms(95)
        kr = karar_ver(gorunum_kur(veri, t), _bos_durum(t), 1.0, P)
        h = kr.hedef
        self.assertEqual(h.a_t, ('BTCUSDT',))
        self.assertEqual(h.tanilar['m'], 1.0)
        s = h.tanilar['sinyal']['BTCUSDT']
        self.assertGreater(s, 0.5)
        self.assertAlmostEqual(h.tanilar['v_birim'], P.tau * abs(s), places=12)
        self.assertIn('BTCUSDT', kr.niyetler)
        self.assertTrue(kr.niyetler['BTCUSDT'].kalan > 0)


class SabitTavanTest(unittest.TestCase):
    def test_sabitsiz_cagri_slice1_ile_ayni(self):
        w = np.array([0.30, 0.06, 0.06, 0.06, 0.06, -0.04])
        be = np.array([True, False, False, False, False, False])
        a = tavan_coz(w, be, P)
        b = tavan_coz(w, be, P, sabit_mi=np.zeros(6, dtype=bool))
        np.testing.assert_array_equal(a.w, b.w)
        self.assertEqual((a.s1_katsayi, a.s2_katsayi, a.brut_katsayi), (b.s1_katsayi, b.s2_katsayi, b.brut_katsayi))

    def test_sabit_isim_degismez_serbestler_kuculur(self):
        # Sabit alt long 0.25 (isim tavaninin ustunde, kirpilmaz): S1 kaybi 0.175. Serbest 5 x 0.06: 0.21.
        w = np.array([0.25, 0.06, 0.06, 0.06, 0.06, 0.06])
        be = np.zeros(6, dtype=bool)
        sabit = np.array([True, False, False, False, False, False])
        ts = tavan_coz(w, be, P, sabit_mi=sabit)
        self.assertEqual(ts.w[0], 0.25)
        self.assertFalse(ts.isim_kirpildi[0])
        np.testing.assert_allclose(ts.w[1:], 0.06 * 0.025 / 0.21, rtol=1e-12)
        self.assertAlmostEqual(ts.s1_kayip_son, P.s1_sinir, places=12)
        self.assertTrue(ts.sabit_ihlal)          # sabit %25 alt long %6 isim tavanini asar (Codex K8)
        ts2 = tavan_coz(np.array([0.05, 0.06, 0.06]), np.zeros(3, dtype=bool), P,
                        sabit_mi=np.array([True, False, False]))
        self.assertFalse(ts2.sabit_ihlal)

    def test_sabit_tek_basina_ihlalse_serbestler_sifir(self):
        w = np.array([0.30, 0.06, 0.06])
        ts = tavan_coz(w, np.zeros(3, dtype=bool), P, sabit_mi=np.array([True, False, False]))
        np.testing.assert_array_equal(ts.w, [0.30, 0.0, 0.0])
        self.assertTrue(ts.sabit_ihlal)


class KacirilanKararTest(unittest.TestCase):
    def test_risk_artiran_iptal_azaltan_korunur(self):
        d = StratejiDurumu(pozisyonlar={'X': 2.0, 'Y': -1.0, 'W': 2.0}, devreden={
            'X': Emir(1.0, 0, False, False, BAGLAM),      # ayni yon: tamami artiran -> tamamen iptal
            'Y': Emir(3.0, 0, False, False, BAGLAM),      # -1'den +2'ye: 1 azaltan, 2 artiran
            'Z': Emir(-1.0, 0, False, False, BAGLAM),     # pozisyonsuz acilis: artiran
            'W': Emir(-0.5, 0, False, False, BAGLAM),     # yalniz azaltan: korunur
        })
        kayitlar = kacirilan_karar(d, gun_ms(10))
        self.assertEqual(kayitlar[0].tur, 'kacirilan_karar')
        iptal = {k.coin: (k.veri['iptal'], k.veri['tamami']) for k in kayitlar[1:]}
        self.assertEqual(iptal, {'X': (1.0, True), 'Y': (2.0, False), 'Z': (-1.0, True)})

    def test_kacirilan_karar_gunluge_islenir_ve_azaltan_kalir(self):
        g = OlayGunlugu()
        g.ekle('baslangic', 0, veri={'nav0': 1000.0})
        g.ekle('emir_niyeti', 0, coin='Y', miktar=-1.0, veri={'emir': Emir(-1.0, 0, False, False, BAGLAM).json()})
        g.ekle('dolum', 1, coin='Y', miktar=-1.0, fiyat=10.0, veri={})           # q = -1
        g.ekle('emir_niyeti', 2, coin='Y', miktar=3.0, veri={'emir': Emir(3.0, 2, False, False, BAGLAM).json()})
        d = durum_turet(gorunum_kur_bos(9), g)
        for k in kacirilan_karar(d, 10):
            g.ekle(k.tur, 10, coin=k.coin, veri=k.veri)
        d = durum_turet(gorunum_kur_bos(10), g)
        self.assertEqual(d.pozisyonlar, {'Y': -1.0})
        self.assertEqual(d.devreden['Y'].kalan, 1.0)     # yalniz 0'a kadar olan risk azaltan parca
        self.assertEqual(d.son_kacirilan_ms, 10)


class DisBayrakModuTest(unittest.TestCase):
    def test_dis_bayraklar_yeniden_turetilmez(self):
        veri = tam_veri_uret(_tarifler({'X': 5e6, 'Y': 5e6}), 100)
        t = gun_ms(95)
        zorla = HijyenBayraklari(b=True)
        g = gorunum_kur(veri, t, dis_bayraklar=DisBayraklar(hijyen={('X', t): zorla}, bosluk_saatleri=frozenset()))
        self.assertEqual(gunluk_hijyen(g, 'X', t, frozenset(), P), zorla)
        self.assertEqual(gunluk_hijyen(g, 'Y', t, frozenset(), P), HijyenBayraklari())


def _gunluk_durum(t_ms, kayitlar, nav0=100_000.0):
    """baslangic + verilen (tur, damga, coin, miktar, fiyat, veri) kayitlariyla gunlukten kurulan durum."""
    g = OlayGunlugu()
    g.ekle('baslangic', 0, veri={'nav0': nav0})
    for tur, damga, coin, miktar, fiyat, veri in kayitlar:
        g.ekle(tur, damga, coin=coin, miktar=miktar, fiyat=fiyat, veri=veri)
    return durum_turet(gorunum_kur_bos(t_ms), g)


def _niyet(c, q, damga=0):
    return ('emir_niyeti', damga, c, q, None, {'emir': Emir(q, damga, False, False, BAGLAM).json()})


class CodexKararTest(unittest.TestCase):
    """Codex 2026-09-28 Slice 2 incelemesi: K4, K6, K13."""

    def test_k4_ilk_kararda_isinma_donmasi_maskede_kalir(self):
        # A1 gun 89'da 6 duz bar: gun 90'da maske. Ilk karar gun 92 (aylik secim gunu): hala maskeli, evrende yok.
        t = _tarifler({'BTCUSDT': 50e6, 'ETHUSDT': 30e6, 'A1': 5e6})
        t['A1'].duz_saatler = frozenset(range(89 * 24 + 2, 89 * 24 + 8))
        veri = tam_veri_uret(t, 93)
        g = gorunum_kur(veri, gun_ms(92))
        kr = karar_ver(g, _bos_durum(gun_ms(92)), 1.0, P)
        self.assertTrue(kr.maske['A1'].maskeli)
        self.assertEqual(kr.maske['A1'].donemler[0][0], gun_ms(90))
        self.assertNotIn('A1', kr.evren)
        self.assertIn('BTCUSDT', kr.evren)

    def _bosluklu_veri(self):
        t = _tarifler({'BTCUSDT': 50e6, 'ETHUSDT': 30e6, 'A1': 5e6})
        for c in ('BTCUSDT', 'ETHUSDT'):
            t[c].eksik_saatler = frozenset({95 * 24 - 5})          # 2/3 aday: borsa capi bosluk
        return tam_veri_uret(t, 96)

    def test_k6_reduce_only_eski_azaltan_emri_korur(self):
        veri = self._bosluklu_veri()
        T = gun_ms(95)
        fiyat = son_kapanis_(veri, 'BTCUSDT', T)
        d = _gunluk_durum(T, [_niyet('BTCUSDT', 100.0), ('dolum', 1, 'BTCUSDT', 100.0, fiyat, {}),
                              _niyet('BTCUSDT', -50.0, 2),                                 # yari kapatma (azaltan)
                              _niyet('ETHUSDT', 10.0, 2)])                                 # giris (artiran)
        kr = karar_ver(gorunum_kur(veri, T), replace(d, t_ms=T), 1.0, P)
        self.assertTrue(kr.hedef.reduce_only)
        iptal = {c: v for c, v in kr.iptaller}
        self.assertNotIn('BTCUSDT', iptal)                 # azaltan parca korunur, yerine yeni niyet yazilmaz
        self.assertNotIn('BTCUSDT', kr.niyetler)
        self.assertEqual((iptal['ETHUSDT']['iptal'], iptal['ETHUSDT']['tamami'], iptal['ETHUSDT']['sebep']),
                         (10.0, True, 'borsa_bosluk'))
        self.assertNotIn('ETHUSDT', kr.niyetler)           # pozisyonsuz coinde reduce-only hedef 0

    def test_k13_hacim_tabani_altinda_giris_yok(self):
        veri = tam_veri_uret(_tarifler({'BTCUSDT': 50e6, 'ETHUSDT': 30e6, 'A1': 0.5e6}), 96)   # A1: 12M/gun
        T = gun_ms(95)
        d = replace(_bos_durum(T), evren=('BTCUSDT', 'ETHUSDT', 'A1'), evren_ms=gun_ms(92), maske_ms=T - 86_400_000)
        kr = karar_ver(gorunum_kur(veri, T), d, 1.0, P)
        self.assertEqual(kr.hedef.tanilar['hacim_tabani_alti'], ['A1'])
        self.assertIn('A1', kr.hedef.a_t)
        self.assertEqual(kr.hedef.w_yildiz['A1'], 0.0)
        self.assertNotIn('A1', kr.niyetler)
        self.assertIn('BTCUSDT', kr.niyetler)


class CodexIkinciTurKararTest(unittest.TestCase):
    """Codex 2. tur yeni bulgu: reduce-only kararinda maskelenen coinde yeni tam kapanis niyeti (m=3) eski esit
    azaltan emrin yerine gecer."""

    def test_esit_azaltmada_yeni_niyet_maske_cikisini_tasir(self):
        t = _tarifler({'BTCUSDT': 50e6, 'ETHUSDT': 30e6, 'A1': 5e6})
        for c in ('BTCUSDT', 'ETHUSDT'):
            t[c].eksik_saatler = frozenset({95 * 24 - 5})
        t['A1'].duz_saatler = frozenset(range(95 * 24 - 12, 95 * 24 - 6))    # (b): bugun maske
        veri = tam_veri_uret(t, 96)
        T = gun_ms(95)
        fiyat = son_kapanis_(veri, 'A1', T)
        d = _gunluk_durum(T, [_niyet('A1', 100.0), ('dolum', 1, 'A1', 100.0, fiyat, {}),
                              _niyet('A1', -100.0, 2)])                     # eski tam kapanis (maske_cikisi yok)
        kr = karar_ver(gorunum_kur(veri, T), replace(d, t_ms=T), 1.0, P)
        self.assertTrue(kr.hedef.reduce_only)
        self.assertTrue(kr.maske['A1'].maskeli)
        self.assertIn('A1', kr.niyetler)
        self.assertTrue(kr.niyetler['A1'].maske_cikisi)
        self.assertEqual(dict(kr.iptaller)['A1']['sebep'], 'yeni_niyet')


def son_kapanis_(veri, c, t):
    from motor.gorunum import son_kapanis
    return son_kapanis(veri.barlar[c], t)

if __name__ == '__main__':
    unittest.main()
