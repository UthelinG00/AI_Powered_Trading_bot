"""MIMARI Ss2.6 eksik funding (dolgu, ters kayit), Ss5.3 aralik degisimi, K1-02 delist. Sentetik veri."""
import sys as _sys
import unittest
from pathlib import Path as _Path

TESTLER_DIR = _Path(__file__).resolve().parent
V8_DIR = TESTLER_DIR.parent
for _dir in (V8_DIR, TESTLER_DIR):
    if str(_dir) not in _sys.path:
        _sys.path.insert(1, str(_dir))

from fikstur.saatlik_veri import CoinTarifi, saat_ms, tam_veri_uret  # noqa: E402
from motor.funding import (bar_akisi_suruyor, delta_aralik_saat, en_kotu_saatlik_oranlar,  # noqa: E402
                           funding_saati, funding_uzlas, mark_vekili)
from motor.durum import StratejiDurumu, kayit_uygula  # noqa: E402
from motor.gorunum import PiyasaGorunumu, funding_serisi, gorunum_kur  # noqa: E402
from motor.gunluk import OlayGunlugu  # noqa: E402
from motor.tipler import Parametreler  # noqa: E402

P = Parametreler()
ORAN = 0.0001


def _yuru(veri, coin, bas_saat, bit_saat, q, gecmis=None, islenen=None):
    """bas..bit saatlerini sirayla isler; funding durumunu gunlugun gercek indirgeyicisiyle (kayit_uygula) tutar.
    islenen: baslangicta islenmis sayilan gercek kayit damgalari (varsayilan: bas saatinden oncekiler).
    Doner: [(saat, olay)]."""
    gecmis = gecmis if gecmis is not None else ((saat_ms(0) - 1, q),)
    f = veri.funding[coin]
    if islenen is None:
        islenen = tuple(int(x) for x in f.damga_ms if x < saat_ms(bas_saat))
    d = StratejiDurumu(nav0=0.0, funding_islenen={coin: islenen})
    g = OlayGunlugu()
    cikti = []
    for h in range(bas_saat, bit_saat + 1):
        T = saat_ms(h)
        for o in funding_saati(gorunum_kur(veri, T), coin, T, gecmis, d.funding_dolgu.get(coin, ()), P,
                               islenen=d.funding_islenen.get(coin, ()), dolgu_kadar=d.funding_dolgu_kadar.get(coin)):
            cikti.append((h, o))
            d = kayit_uygula(d, g.ekle(o.tur, T, coin=coin, veri=o.veri))
    return cikti


def _dolgu_saatleri(olaylar):
    """{saat_indeksi: tutar} (butun dolgu kayitlarinin saat kirilimi)."""
    return {(a - saat_ms(0)) // 3_600_000: b for _, o in olaylar if o.tur == 'funding_dolgu'
            for a, b in o.veri['saatler']}


def _gercek_toplam(veri, coin, olaylar, q):
    """Yalniz gercek kayitlarin -q*mark*oran toplami (dolgusuz ideal muhasebe)."""
    toplam = 0.0
    for h, o in olaylar:
        if o.tur == 'funding':
            T = saat_ms(h)
            toplam += funding_uzlas(q, mark_vekili(gorunum_kur(veri, T).barlar[coin], T), o.veri['oran'])
    return toplam


class GercekKayitTest(unittest.TestCase):
    def setUp(self):
        self.veri = tam_veri_uret({'X': CoinTarifi(saatlik_vol=0.002, funding_orani=ORAN)}, 20)

    def test_long_oder_short_alir(self):
        T = saat_ms(200)   # 8'in kati
        g = gorunum_kur(self.veri, T)
        mark = float(g.barlar['X'].kapanis[-1])
        once = tuple(int(x) for x in g.funding['X'].damga_ms if x < T)
        long_ = funding_saati(g, 'X', T, ((0, 2.0),), (), P, islenen=once)
        short = funding_saati(g, 'X', T, ((0, -2.0),), (), P, islenen=once)
        self.assertEqual([o.tur for o in long_], ['funding'])
        self.assertAlmostEqual(long_[0].tutar, -2.0 * mark * ORAN, places=12)
        self.assertAlmostEqual(short[0].tutar, 2.0 * mark * ORAN, places=12)

    def test_uzlasmadan_sonra_dolan_emir_odemez(self):
        # T'deki dolum funding'den sonradir: q(T-) T damgali degisikligi gormez; sifir tutarli kayit yazilmaz.
        T = saat_ms(200)
        g = gorunum_kur(self.veri, T)
        self.assertEqual(funding_saati(g, 'X', T, ((T, 5.0),), (), P), [])

    def test_gec_gelen_kayit_geldigi_saatte_islenir(self):
        # Codex K1: 200 damgali kayit gorunume 203'te girer (canli gecikme). Son islenen 192 iken 203'te
        # 200 kaydi q(200-) ve mark(200) ile islenir; nakit 203'te yazilir.
        T = saat_ms(203)
        g = gorunum_kur(self.veri, T)
        once = tuple(int(x) for x in g.funding['X'].damga_ms if x < saat_ms(200))
        olaylar = funding_saati(g, 'X', T, ((0, 2.0), (saat_ms(201), 5.0)), (), P, islenen=once)
        self.assertEqual([o.tur for o in olaylar], ['funding'])
        self.assertEqual(olaylar[0].veri['damga_ms'], saat_ms(200))
        self.assertEqual(olaylar[0].veri['q'], 2.0)
        mark = mark_vekili(g.barlar['X'], saat_ms(200))
        self.assertAlmostEqual(olaylar[0].tutar, -2.0 * mark * ORAN, places=12)
        # Ayni kayit ikinci kez islenmez.
        self.assertEqual(funding_saati(g, 'X', T, ((0, 2.0),), (), P, islenen=once + (saat_ms(200),)), [])

    def test_eski_kayit_yenisinden_sonra_gelirse_islenir(self):
        # Codex 2. tur K1: 208 islendikten sonra 200 gelir; islenen kume 200'u icermedigi icin islenir.
        T = saat_ms(209)
        g = gorunum_kur(self.veri, T)
        islenen = tuple(int(x) for x in g.funding['X'].damga_ms if x != saat_ms(200))
        olaylar = funding_saati(g, 'X', T, ((0, 2.0),), (), P, islenen=islenen)
        self.assertEqual([o.veri['damga_ms'] for o in olaylar], [saat_ms(200)])

    def test_ilk_kayit_gec_gelse_de_islenir(self):
        # Codex 2. tur K1: islenmis kayit yokken 8 damgali ilk kayit 9'da gorulur.
        T = saat_ms(9)
        olaylar = funding_saati(gorunum_kur(self.veri, T), 'X', T, ((0, 1.0),), (), P)
        self.assertEqual([(o.tur, o.veri['damga_ms']) for o in olaylar], [('funding', saat_ms(8))])

    def test_ara_saatte_olay_yok(self):
        T = saat_ms(203)
        g = gorunum_kur(self.veri, T)
        once = tuple(int(x) for x in g.funding['X'].damga_ms)
        self.assertEqual(funding_saati(g, 'X', T, ((0, 1.0),), (), P, islenen=once), [])


class EksikFundingTest(unittest.TestCase):
    def setUp(self):
        self.veri = tam_veri_uret({'X': CoinTarifi(saatlik_vol=0.002, funding_orani=ORAN,
                                                   funding_eksik=frozenset({400}))}, 20)

    def test_tespit_tek_kalem_sonra_saatlik_sonra_ters_kayit(self):
        olaylar = _yuru(self.veri, 'X', 393, 408, q=3.0)
        turler = [(h, o.tur) for h, o in olaylar]
        # 392 son gercek kayit; 1,5*8 = 12 saat -> tespit 404'te; 405-407 saatlik; 408 gercek kayit gelir.
        self.assertEqual(turler, [(404, 'funding_dolgu'), (405, 'funding_dolgu'), (406, 'funding_dolgu'),
                                  (407, 'funding_dolgu'), (408, 'ters_kayit'), (408, 'funding')])
        self.assertEqual(len(olaylar[0][1].veri['saatler']), 12)
        self.assertEqual(len(olaylar[1][1].veri['saatler']), 1)
        r_long = P.funding_r_taban_saatlik          # oran/8 = taban: en kotu saatlik oran
        g = gorunum_kur(self.veri, saat_ms(404))
        beklenen = sum(-3.0 * mark_vekili(g.barlar['X'], saat_ms(h)) * r_long for h in range(393, 405))
        self.assertAlmostEqual(olaylar[0][1].tutar, beklenen, places=12)
        # Codex K2: 408 kaydi yalniz kapsadigi (400, 408] saatlerinin dolgusunu geri alir; 393-400 dolgusu
        # eksik kalan 400 uzlasmasinin karsiligidir ve kalir.
        saatlik = _dolgu_saatleri(olaylar)
        self.assertEqual(sorted(saatlik), list(range(393, 408)))
        self.assertAlmostEqual(olaylar[4][1].tutar, -sum(saatlik[h] for h in range(401, 408)), places=12)
        self.assertEqual(olaylar[4][1].veri['aralik_saat'], 8.0)

    def test_ters_kayit_sonrasi_net_gercek_arti_eksik_uzlasma(self):
        olaylar = _yuru(self.veri, 'X', 393, 408, q=3.0)
        net = sum(o.tutar for _, o in olaylar)
        kalan_dolgu = sum(t for h, t in _dolgu_saatleri(olaylar).items() if h <= 400)
        self.assertLess(kalan_dolgu, 0.0)
        self.assertAlmostEqual(net, _gercek_toplam(self.veri, 'X', olaylar, 3.0) + kalan_dolgu, places=12)

    def test_tespitten_once_kapanan_pozisyonun_borcu_yazilir(self):
        # Codex K3: pozisyon 398'de kapanir, eksik olay 404'te saptanir: 393-398 saatleri q(h-)=3 ile dolgu alir,
        # 408 kaydi bunlari kapsamaz (400 uzlasmasina aittir), kayit 0 tutarla islenir.
        gecmis = ((saat_ms(0) - 1, 3.0), (saat_ms(398), 0.0))
        olaylar = _yuru(self.veri, 'X', 393, 408, q=None, gecmis=gecmis)
        self.assertEqual(sorted(_dolgu_saatleri(olaylar)), list(range(393, 399)))
        self.assertEqual([o.tur for h, o in olaylar if h == 408], [])     # q = 0 ve kapsanan dolgu yok

    def test_short_en_kotu_oran_negatif_taraf(self):
        olaylar = _yuru(self.veri, 'X', 393, 404, q=-3.0)
        self.assertEqual(olaylar[0][1].tur, 'funding_dolgu')
        self.assertLess(olaylar[0][1].tutar, 0.0)    # short icin en kotu: oder


class AralikDegisimiTest(unittest.TestCase):
    def test_8_4_1_8_gecisinde_net_muhasebe_cift_saymaz(self):
        # 30 gunden uzun 1h donemi Delta'yi 1 saate indirir; 8h'ye donuste dolgu yazilir ve gercek kayitla
        # tamamen ters kaydedilir. Net nakit = yalniz gercek kayitlarin toplami.
        tarif = CoinTarifi(saatlik_vol=0.002, funding_orani=ORAN,
                           funding_araliklari=((0, 8), (100, 4), (200, 1), (200 + 31 * 24, 8)))
        veri = tam_veri_uret({'X': tarif}, 40)
        olaylar = _yuru(veri, 'X', 90, 40 * 24 - 1, q=1.5)   # 1h -> 8h gecisi saat 944'te
        self.assertTrue(any(o.tur == 'funding_dolgu' for _, o in olaylar))
        net = sum(o.tutar for _, o in olaylar)
        self.assertAlmostEqual(net, _gercek_toplam(veri, 'X', olaylar, 1.5), places=10)
        # Son olay gercek kayit olmali: acik dolgu kalmamali (son 8h kaydindan sonra).
        son_gercek = max(h for h, o in olaylar if o.tur == 'funding')
        self.assertFalse(any(o.tur == 'funding_dolgu' and h > son_gercek for h, o in olaylar))

    def test_delta_ve_en_kotu_oran(self):
        tarif = CoinTarifi(funding_orani=ORAN, funding_araliklari=((0, 8), (100, 4)))
        g = gorunum_kur(tam_veri_uret({'X': tarif}, 10), saat_ms(200))
        f = g.funding['X']
        self.assertEqual(delta_aralik_saat(f, saat_ms(200), P), 8.0)
        r_long, r_short = en_kotu_saatlik_oranlar(f, saat_ms(200), P)
        self.assertAlmostEqual(r_long, ORAN / 4, places=15)       # 4h araliginda saatlik oran daha yuksek
        self.assertAlmostEqual(r_short, -P.funding_r_taban_saatlik, places=15)


class DelistTest(unittest.TestCase):
    def test_bar_akisi_durunca_dolgu_yazilmaz(self):
        tarif = CoinTarifi(saatlik_vol=0.002, bitis_saat=300, funding_bitis_saat=300)
        veri = tam_veri_uret({'X': tarif}, 20)
        olaylar = _yuru(veri, 'X', 290, 400, q=2.0)
        self.assertFalse(any(h > 300 for h, _ in olaylar))
        self.assertFalse(bar_akisi_suruyor(gorunum_kur(veri, saat_ms(310)).barlar['X'], saat_ms(310)))


class GecKayitBudamaTest(unittest.TestCase):
    def test_pencere_sinirindaki_gec_kayit_kapsadigi_dolgulari_geri_alir(self):
        # Codex 3. tur: 400 damgali 8h kayit 400 + 30 gun - 1 saatte gelir; kapsadigi 393-400 dolgulari budanmamis
        # olmali (budama sinirina en uzun aralik kadar pay).
        from motor.funding import funding_budama_ms
        T = saat_ms(400) + P.funding_gec_kayit_gun * 86_400_000 - 3_600_000
        self.assertLess(funding_budama_ms(T, P), saat_ms(393))


class KisaAralikKapsamTest(unittest.TestCase):
    """Codex 2. tur K2: 1h duzende 400 ve 401 eksik, 402 gelir: eksik iki uzlasmanin dolgusu geri alinmaz."""

    def _veri(self, aralik_sutunu):
        tarif = CoinTarifi(saatlik_vol=0.002, funding_orani=ORAN, funding_araliklari=((0, 1),),
                           funding_eksik=frozenset({400, 401}))
        veri = tam_veri_uret({'X': tarif}, 20)
        if aralik_sutunu:
            f = veri.funding['X']
            yeni = funding_serisi(f.damga_ms, f.oran, [1.0] * len(f))
            veri = type(veri)(barlar=veri.barlar, funding={'X': yeni}, adaylar=veri.adaylar)
        return veri

    def test_bosluktan_cikan_kapsam_1h(self):
        for aralik_sutunu in (False, True):
            olaylar = _yuru(self._veri(aralik_sutunu), 'X', 398, 403, q=2.0)
            self.assertEqual(sorted(_dolgu_saatleri(olaylar)), [400, 401], aralik_sutunu)
            self.assertFalse(any(o.tur == 'ters_kayit' for _, o in olaylar), aralik_sutunu)

    def test_arsiv_araligi_4h_tek_eksik_kaydi_ayirir(self):
        # 4h duzende 400 eksik: bosluk 8 saat. Arsiv araligi (4h) varsa 400 dolgusu kalir; yoksa 4h->8h gecisi
        # sanilip geri alinir (bilinen belirsizlik, kapsanan_aralik_saat).
        tarif = CoinTarifi(saatlik_vol=0.002, funding_orani=ORAN, funding_araliklari=((0, 4),),
                           funding_eksik=frozenset({400}))
        veri = tam_veri_uret({'X': tarif}, 20)
        f = veri.funding['X']
        veri4 = type(veri)(barlar=veri.barlar, funding={'X': funding_serisi(f.damga_ms, f.oran, [4.0] * len(f))},
                           adaylar=veri.adaylar)
        for v, kalan_beklenir in ((veri4, True), (veri, False)):
            olaylar = _yuru(v, 'X', 397, 404, q=2.0)
            net_dolgu = sum(o.tutar for _, o in olaylar if o.tur in ('funding_dolgu', 'ters_kayit'))
            self.assertEqual(net_dolgu < -1e-9, kalan_beklenir)


if __name__ == '__main__':
    unittest.main()
