"""MIMARI Ss2.5 donma olcutleri (a)-(d), Ss2.6 borsa capi bosluk, maske donusu ve Ss2.3 PIT evren.
Sentetik 1h barlar."""
import sys as _sys
import unittest
from pathlib import Path as _Path

TESTLER_DIR = _Path(__file__).resolve().parent
V8_DIR = TESTLER_DIR.parent
for _dir in (V8_DIR, TESTLER_DIR):
    if str(_dir) not in _sys.path:
        _sys.path.insert(1, str(_dir))

from fikstur.saatlik_veri import CoinTarifi, gun_ms, saat_ms, tam_veri_uret  # noqa: E402
from motor.evren import evren_sec  # noqa: E402
from motor.gorunum import (aylik_secim_gunu_mu, borsa_bosluk_saati_mi, bosluk_saatleri, bosluk_taramasi,  # noqa: E402
                           gorunum_kur)
from motor.hedef import coin_gunluk  # noqa: E402
import numpy as np  # noqa: E402
from motor.hijyen import (HijyenBayraklari, MaskeKaydi, gunluk_hijyen, maske_gunu_ilerle,  # noqa: E402
                          maske_json, maske_jsondan)
from motor.tipler import Parametreler  # noqa: E402

P = Parametreler()
GUN = 100
T = gun_ms(GUN)
SON_GUN_SAAT = GUN * 24          # t'nin saat indeksi


def _hijyen(tarif, gun_sayisi=GUN + 1, t=T, diger=None):
    # Komsu coinler: tek coinli evrende coinin kendi boslugu borsa capi bosluk (1/1) sayilir ve atlanirdi.
    tarifler = {'X': tarif, 'Y': CoinTarifi(), 'Z': CoinTarifi()}
    tarifler.update(diger or {})
    veri = tam_veri_uret(tarifler, gun_sayisi)
    g = gorunum_kur(veri, t)
    return gunluk_hijyen(g, 'X', t, bosluk_saatleri(g, t - 86_400_000, t, P.borsa_bosluk_oran), P)


class OlcutATest(unittest.TestCase):
    def test_hacim_cokusu_tetikler(self):
        carpan = {h: 0.05 for h in range(SON_GUN_SAAT - 7 * 24, SON_GUN_SAAT)}
        self.assertTrue(_hijyen(CoinTarifi(hacim_carpani=carpan)).a)

    def test_normal_hacim_tetiklemez(self):
        self.assertEqual(_hijyen(CoinTarifi()), HijyenBayraklari())

    def test_kisa_gecmis_degerlendirilmez(self):
        carpan = {h: 0.05 for h in range(SON_GUN_SAAT - 7 * 24, SON_GUN_SAAT)}
        self.assertFalse(_hijyen(CoinTarifi(hacim_carpani=carpan, baslangic_saat=20 * 24)).a)


class OlcutBTest(unittest.TestCase):
    def test_alti_ardisik_duz_bar(self):
        duz = frozenset(range(SON_GUN_SAAT - 10, SON_GUN_SAAT - 4))
        self.assertTrue(_hijyen(CoinTarifi(duz_saatler=duz)).b)

    def test_bes_ardisik_duz_bar_yetmez(self):
        duz = frozenset(range(SON_GUN_SAAT - 10, SON_GUN_SAAT - 5))
        self.assertFalse(_hijyen(CoinTarifi(duz_saatler=duz)).b)


class OlcutCTest(unittest.TestCase):
    def test_on_alti_saat_funding_yoksa_tetikler(self):
        self.assertTrue(_hijyen(CoinTarifi(funding_bitis_saat=SON_GUN_SAAT - 16)).c)

    def test_sekiz_saatlik_normal_akis_tetiklemez(self):
        self.assertFalse(_hijyen(CoinTarifi()).c)

    def test_aralik_degisimi_sahte_donma_uretmez(self):
        # 8h -> 4h -> 1h -> 8h gecisleri (K1-01): mutlak 16 saat esigi hicbir gun tetiklenmez.
        tarif = CoinTarifi(funding_araliklari=((0, 8), (95 * 24, 4), (97 * 24 + 3, 1), (99 * 24 + 5, 8)))
        veri = tam_veri_uret({'X': tarif}, GUN + 3)
        for gun in range(94, GUN + 3):
            t = gun_ms(gun)
            g = gorunum_kur(veri, t)
            self.assertFalse(gunluk_hijyen(g, 'X', t, frozenset(), P).c, f"gun {gun}")

    def test_bar_akisi_yoksa_tetiklemez(self):
        # Delist: bar ve funding birlikte durur; (c) degil (d) tetiklenir.
        h = _hijyen(CoinTarifi(bitis_saat=SON_GUN_SAAT - 20, funding_bitis_saat=SON_GUN_SAAT - 20))
        self.assertFalse(h.c)
        self.assertTrue(h.d)


class OlcutDTest(unittest.TestCase):
    def test_dokuz_saat_bosluk_tetikler(self):
        eksik = frozenset(range(SON_GUN_SAAT - 12, SON_GUN_SAAT - 3))
        h = _hijyen(CoinTarifi(eksik_saatler=eksik))
        self.assertTrue(h.d)
        self.assertFalse(h.maske_tetik)      # (d) maske degil, islem disi

    def test_sekiz_saat_bosluk_yetmez(self):
        eksik = frozenset(range(SON_GUN_SAAT - 12, SON_GUN_SAAT - 4))
        self.assertFalse(_hijyen(CoinTarifi(eksik_saatler=eksik)).d)

    def test_borsa_bosluk_saatleri_sayilmaz(self):
        # X 9 saat eksik; bunun 2 saatinde diger iki coin de eksik (3/3 >= %50: borsa capi bosluk).
        eksik = frozenset(range(SON_GUN_SAAT - 12, SON_GUN_SAAT - 3))
        ortak = frozenset({SON_GUN_SAAT - 12, SON_GUN_SAAT - 11})
        diger = {'Y': CoinTarifi(eksik_saatler=ortak), 'Z': CoinTarifi(eksik_saatler=ortak)}
        h = _hijyen(CoinTarifi(eksik_saatler=eksik), diger=diger)
        self.assertFalse(h.d)


class BorsaBoslukTest(unittest.TestCase):
    def _veri(self, eksik_coin_sayisi):
        h = SON_GUN_SAAT - 5
        tarifler = {f'C{i}': CoinTarifi(eksik_saatler=frozenset({h}) if i < eksik_coin_sayisi else frozenset())
                    for i in range(4)}
        return tam_veri_uret(tarifler, GUN + 1), saat_ms(h)

    def test_yarisi_eksikse_bosluk(self):
        veri, h = self._veri(2)
        self.assertTrue(borsa_bosluk_saati_mi(gorunum_kur(veri, T), h, P.borsa_bosluk_oran))

    def test_ceyregi_eksikse_bosluk_degil(self):
        veri, h = self._veri(1)
        self.assertFalse(borsa_bosluk_saati_mi(gorunum_kur(veri, T), h, P.borsa_bosluk_oran))

    def test_cok_saatlik_kesintinin_her_saati_bosluk(self):
        kesinti = frozenset(range(SON_GUN_SAAT - 10, SON_GUN_SAAT - 6))   # 4 saat, butun coinlerde
        tarifler = {f'C{i}': CoinTarifi(eksik_saatler=kesinti) for i in range(4)}
        g = gorunum_kur(tam_veri_uret(tarifler, GUN + 1), T)
        bosluk = bosluk_saatleri(g, T - 86_400_000, T, P.borsa_bosluk_oran)
        self.assertEqual(bosluk, frozenset(saat_ms(h) for h in kesinti))

    def test_kapanmamis_saat_sorulamaz(self):
        veri, _ = self._veri(0)
        with self.assertRaises(ValueError):
            borsa_bosluk_saati_mi(gorunum_kur(veri, T), T, P.borsa_bosluk_oran)


class MaskeDonusTest(unittest.TestCase):
    TETIK = HijyenBayraklari(a=True)
    TEMIZ = HijyenBayraklari()

    def test_aylik_secim_ve_otuz_temiz_gun(self):
        # Gun 0 = 2023-07-01 (tetik). Gun 31 = 2023-08-01: 31 temiz gun + aylik secim -> maske kalkar.
        self.assertTrue(aylik_secim_gunu_mu(gun_ms(31)))
        k = maske_gunu_ilerle(MaskeKaydi(), self.TETIK, gun_ms(0), P)
        self.assertTrue(k.maskeli)
        for gun in range(1, 31):
            k = maske_gunu_ilerle(k, self.TEMIZ, gun_ms(gun), P)
        self.assertTrue(k.maskeli)
        k = maske_gunu_ilerle(k, self.TEMIZ, gun_ms(31), P)
        self.assertFalse(k.maskeli)
        self.assertEqual(k.donemler, ((gun_ms(0), gun_ms(31)),))
        self.assertTrue(k.gunde_maskeli(gun_ms(30)))
        self.assertFalse(k.gunde_maskeli(gun_ms(31)))

    def test_seri_yetmezse_sonraki_aya_kalir(self):
        k = maske_gunu_ilerle(MaskeKaydi(), self.TETIK, gun_ms(0), P)
        for gun in range(1, 63):
            k = maske_gunu_ilerle(k, self.TETIK if gun == 10 else self.TEMIZ, gun_ms(gun), P)
            if gun == 31:
                self.assertTrue(k.maskeli)          # 2023-08-01'de seri 21
        self.assertTrue(aylik_secim_gunu_mu(gun_ms(62)))   # 2023-09-01
        self.assertFalse(k.maskeli)

    def test_islem_disi_gunu_temiz_sayilmaz(self):
        k = maske_gunu_ilerle(MaskeKaydi(temiz_seri=5), HijyenBayraklari(d=True), gun_ms(3), P)
        self.assertEqual(k.temiz_seri, 0)
        self.assertFalse(k.maskeli)

    def test_json_gidis_donus(self):
        k = maske_gunu_ilerle(MaskeKaydi(), self.TETIK, gun_ms(0), P)
        self.assertEqual(maske_jsondan(maske_json(k)), k)


class EvrenTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        tarifler = {'BTCUSDT': CoinTarifi(saatlik_hacim=50e6), 'ETHUSDT': CoinTarifi(saatlik_hacim=40e6)}
        for i in range(1, 26):   # A01 en yuksek hacim ... A25 en dusuk; hepsi >= 20M/gun
            tarifler[f'A{i:02d}'] = CoinTarifi(saatlik_hacim=(30 - i) * 1e6)
        tarifler['GENC'] = CoinTarifi(saatlik_hacim=99e6, baslangic_saat=20 * 24)   # isinmada
        tarifler['INCE'] = CoinTarifi(saatlik_hacim=0.5e6)                          # 12M/gun < 20M
        tarifler['ESIT_B'] = CoinTarifi(saatlik_hacim=28.5e6)
        tarifler['ESIT_A'] = CoinTarifi(saatlik_hacim=28.5e6)
        cls.g = gorunum_kur(tam_veri_uret(tarifler, GUN + 1), T)

    def test_ilk_secim_btc_eth_ve_en_iyi_on_uc_alt(self):
        e = evren_sec(self.g, T, (), {}, P)
        self.assertEqual(e.uyeler[:2], ('BTCUSDT', 'ETHUSDT'))
        self.assertEqual(len(e.uyeler), 15)
        self.assertEqual(e.uyeler[2:4], ('A01', 'ESIT_A'))   # esitlikte alfabetik: ESIT_A, ESIT_B
        self.assertEqual(e.alt_sira['ESIT_B'], 3)
        self.assertNotIn('GENC', e.uygun)
        self.assertNotIn('INCE', e.uygun)

    def test_kalis_sirasi_yirmi(self):
        ilk = evren_sec(self.g, T, (), {}, P)
        sira = ilk.alt_sira
        yirminci = [c for c, s in sira.items() if s == 20][0]
        yirmi_ikinci = [c for c, s in sira.items() if s == 22][0]
        onceki = tuple(c for c, s in sira.items() if s <= 12) + (yirminci, yirmi_ikinci)
        e = evren_sec(self.g, T, onceki, {}, P)
        self.assertIn(yirminci, e.uyeler)              # <= 20: tutulur
        self.assertNotIn(yirmi_ikinci, e.uyeler)       # > 20: cikar
        on_ucuncu = [c for c, s in sira.items() if s == 13][0]
        self.assertNotIn(on_ucuncu, e.uyeler)          # 13 yuva dolu (12 + 20.)
        self.assertEqual(len(e.uyeler), 15)

    def test_yeni_giris_on_bes_ile_sinirli(self):
        # Onceki evren yalniz 1..5; bos 8 yuva sira <= 15 adaylarla (6..13) dolar.
        sira = evren_sec(self.g, T, (), {}, P).alt_sira
        onceki = tuple(c for c, s in sira.items() if s <= 5)
        e = evren_sec(self.g, T, onceki, {}, P)
        self.assertEqual(sorted(e.alt_sira[c] for c in e.uyeler[2:]), list(range(1, 14)))

    def test_maskeli_coin_uygun_degil(self):
        maske = {'A01': MaskeKaydi(maskeli=True, donemler=((T, None),))}
        e = evren_sec(self.g, T, (), maske, P)
        self.assertNotIn('A01', e.uyeler)


class CodexBulgularTest(unittest.TestCase):
    """Codex 2026-09-28 Slice 2 incelemesi: K7, K10, K11, K12."""

    def test_k11_gece_yarisini_asan_alti_duz_bar(self):
        duz = frozenset(range(SON_GUN_SAAT - 27, SON_GUN_SAAT - 21))    # 3 dun + 3 bugun
        self.assertTrue(_hijyen(CoinTarifi(duz_saatler=duz)).b)

    def test_k11_d_toplam_eksik_saat(self):
        eksik = frozenset(range(SON_GUN_SAAT - 22, SON_GUN_SAAT - 4, 2))  # 9 ayri eksik saat
        self.assertEqual(len(eksik), 9)
        self.assertTrue(_hijyen(CoinTarifi(eksik_saatler=eksik)).d)
        self.assertFalse(_hijyen(CoinTarifi(eksik_saatler=frozenset(list(eksik)[:8]))).d)

    def test_k10_c_penceresi_bosluk_saatlerini_saymaz(self):
        # Son gercek kayit SON-24; SON-15..SON-2 butun coinlerde ortak kesinti (14 saat); SON-16 ve SON-1 barlari
        # var. Takvim penceresi [SON-16, SON) kayitsiz olurdu; bosluk-disi 16 saat SON-24 kaydini kapsar.
        ortak = frozenset(range(SON_GUN_SAAT - 15, SON_GUN_SAAT - 1))
        x = CoinTarifi(funding_bitis_saat=SON_GUN_SAAT - 23, eksik_saatler=ortak)
        diger = {'Y': CoinTarifi(eksik_saatler=ortak), 'Z': CoinTarifi(eksik_saatler=ortak)}
        self.assertFalse(_hijyen(x, diger=diger).c)
        # Kesinti yoksa ayni funding boslugu (c)'yi tetikler.
        self.assertTrue(_hijyen(CoinTarifi(funding_bitis_saat=SON_GUN_SAAT - 23)).c)

    def test_k7_uzun_kesinti_zincirli_taramada_surer(self):
        # 5 adaydan 3'u 72 saat kesik: gun gun, onceki gunun kesinti durumuyla surdurulen tarama tek parca
        # taramayla ayni 72 saati bulur; durumsuz (24 saat geri bakisli) son gun taramasi hic bulamazdi.
        kesinti = frozenset(range(SON_GUN_SAAT - 72, SON_GUN_SAAT))
        tarifler = {f'C{i}': CoinTarifi(eksik_saatler=kesinti if i < 3 else frozenset()) for i in range(5)}
        veri = tam_veri_uret(tarifler, GUN + 1)
        g = gorunum_kur(veri, T)
        tek, ref_tek = bosluk_taramasi(g, T - 4 * 86_400_000, T, P.borsa_bosluk_oran, None)
        self.assertEqual(tek, frozenset(saat_ms(h) for h in kesinti))
        zincir, ref = set(), None
        for gun in range(GUN - 4, GUN):
            k, ref = bosluk_taramasi(g, gun_ms(gun), gun_ms(gun + 1), P.borsa_bosluk_oran, ref)
            zincir |= k
        self.assertEqual(frozenset(zincir), tek)
        self.assertEqual(ref, ref_tek)
        self.assertIsNotNone(ref)                      # kesinti suruyor
        self.assertEqual(bosluk_saatleri(g, T - 86_400_000, T, P.borsa_bosluk_oran), frozenset())

    def test_k12_islem_disi_gun_kaydedilir_ve_getiriye_girmez(self):
        k = maske_gunu_ilerle(MaskeKaydi(), HijyenBayraklari(d=True), gun_ms(3), P)
        self.assertEqual(k.islem_disi_gunler, (gun_ms(3),))
        self.assertFalse(k.maskeli)
        self.assertEqual(maske_jsondan(maske_json(k)), k)
        veri = tam_veri_uret({'X': CoinTarifi(saatlik_vol=0.01)}, 10)
        g = gorunum_kur(veri, gun_ms(9))
        gunler = np.array([gun_ms(d) for d in range(1, 10)], dtype=np.int64)
        temiz = coin_gunluk(g, 'X', gunler, MaskeKaydi(), P)
        isd = coin_gunluk(g, 'X', gunler, k, P)
        self.assertTrue(np.all(~np.isnan(temiz.getiriler[1:])))
        self.assertTrue(np.isnan(isd.getiriler[2]) and np.isnan(isd.getiriler[3]))   # gun 3 ve gun 4 getirisi
        np.testing.assert_array_equal(isd.gecerli, temiz.gecerli)                     # sinyal fiyatlari degismez

class CodexIkinciTurTest(unittest.TestCase):
    """Codex 2. tur: K10 (uzun kesintide (c) penceresi), K11 (bosluklu gece gecisinde (b))."""

    def test_k11_bosluk_araya_girse_de_alti_duz_bar(self):
        # 3 duz bar dun (SON-30..SON-28), 6 saat borsa capi bosluk (SON-27..SON-22), 3 duz bar bugun (SON-21..SON-19).
        ortak = frozenset(range(SON_GUN_SAAT - 27, SON_GUN_SAAT - 21))
        duz = frozenset(range(SON_GUN_SAAT - 30, SON_GUN_SAAT - 27)) | frozenset(range(SON_GUN_SAAT - 21, SON_GUN_SAAT - 18))
        x = CoinTarifi(duz_saatler=duz, eksik_saatler=ortak)
        diger = {'Y': CoinTarifi(eksik_saatler=ortak), 'Z': CoinTarifi(eksik_saatler=ortak)}
        veri = tam_veri_uret({'X': x, **diger}, GUN + 1)
        g = gorunum_kur(veri, T)
        bosluk = bosluk_taramasi(g, T - 3 * 86_400_000, T, P.borsa_bosluk_oran, None)[0]
        self.assertTrue(gunluk_hijyen(g, 'X', T, bosluk, P).b)

    def test_k10_uzun_kesintide_c_penceresi_karar_zinciriyle_ayni(self):
        # 5 adaydan 3'u 120 saat kesik; X (calisan) funding'i kesintiyle ayni anda durur. Tam gecmisle ve karar
        # kayitlarinin tasidigi bosluk gecmisiyle (bosluk_gecmis_gun) ayni (c) sonucu cikmali.
        kesinti = frozenset(range(SON_GUN_SAAT - 120, SON_GUN_SAAT - 1))
        tarifler = {f'C{i}': CoinTarifi(eksik_saatler=kesinti) for i in range(3)}
        tarifler['X'] = CoinTarifi(funding_bitis_saat=SON_GUN_SAAT - 121)
        tarifler['W'] = CoinTarifi()
        g = gorunum_kur(tam_veri_uret(tarifler, GUN + 1), T)
        tam = bosluk_taramasi(g, T - 20 * 86_400_000, T, P.borsa_bosluk_oran, None)[0]
        zincir, ref = set(), None
        for gun in range(GUN - 20, GUN):
            k, ref = bosluk_taramasi(g, gun_ms(gun), gun_ms(gun + 1), P.borsa_bosluk_oran, ref)
            zincir = {h for h in zincir | k if h >= gun_ms(gun + 1) - P.bosluk_gecmis_gun * 86_400_000}
        self.assertEqual(frozenset(zincir), tam)
        self.assertEqual(gunluk_hijyen(g, 'X', T, frozenset(zincir), P).c, gunluk_hijyen(g, 'X', T, tam, P).c)
        self.assertFalse(gunluk_hijyen(g, 'X', T, tam, P).c)


if __name__ == '__main__':
    unittest.main()
