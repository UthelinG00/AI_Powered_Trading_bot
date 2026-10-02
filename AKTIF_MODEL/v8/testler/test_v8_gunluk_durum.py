"""MIMARI Ss5.8 olay gunlugu (hash zinciri, yalniz ekleme) ve Ss5.1 durum_turet indirgeyicisi. Sentetik kayit."""
import sys as _sys
import unittest
from pathlib import Path as _Path

TESTLER_DIR = _Path(__file__).resolve().parent
V8_DIR = TESTLER_DIR.parent
for _dir in (V8_DIR, TESTLER_DIR):
    if str(_dir) not in _sys.path:
        _sys.path.insert(1, str(_dir))

from motor.durum import (DurumHatasi, Emir, MaliyetBaglami, StratejiDurumu, durum_turet,  # noqa: E402
                         kayit_uygula, pozisyon_gecmisi, q_once)
from motor.gorunum import PiyasaGorunumu  # noqa: E402
from motor.gunluk import KOK_HASH, GunlukHatasi, OlayGunlugu  # noqa: E402

BAGLAM = MaliyetBaglami(v1h30=1e6, v1h7=1e6, v60=1e8, sigma_d_bps=10.0, sigma_1h=float('nan'), btc_eth=False,
                        btc_sigma_1h=0.01)


def _emir(kalan, tam=False):
    return Emir(kalan=kalan, karar_ms=0, maske_cikisi=False, tam_kapanis=tam, baglam=BAGLAM)


def _katla(gunluk):
    d = StratejiDurumu()
    for k in gunluk.kayitlar():
        d = kayit_uygula(d, k)
    return d


class ZincirTest(unittest.TestCase):
    def test_bos_gunluk_dogrulanir(self):
        g = OlayGunlugu()
        self.assertTrue(g.dogrula())
        self.assertEqual(g.son_hash, KOK_HASH)

    def test_her_kayit_oncekinin_hashini_tasir(self):
        g = OlayGunlugu()
        a = g.ekle('baslangic', 0, veri={'nav0': 100.0})
        b = g.ekle('nav', 10, veri={'nav': 101.0})
        self.assertEqual(a.onceki_hash, KOK_HASH)
        self.assertEqual(b.onceki_hash, a.hash)
        self.assertTrue(g.dogrula())

    def test_degistirilen_kayit_zinciri_bozar(self):
        g = OlayGunlugu()
        g.ekle('baslangic', 0, veri={'nav0': 100.0})
        g.ekle('nav', 10, veri={'nav': 101.0})
        g.kayitlar()[0].veri['nav0'] = 999.0   # sonradan degistirme girisimi
        self.assertFalse(g.dogrula())
        with self.assertRaises(GunlukHatasi):
            OlayGunlugu.kayitlardan(g.kayitlar())

    def test_damga_geri_gidemez(self):
        g = OlayGunlugu()
        g.ekle('baslangic', 10, veri={'nav0': 1.0})
        with self.assertRaises(GunlukHatasi):
            g.ekle('nav', 5, veri={'nav': 1.0})

    def test_bilinmeyen_tur_ve_nan_reddedilir(self):
        g = OlayGunlugu()
        with self.assertRaises(GunlukHatasi):
            g.ekle('uydurma', 0)
        with self.assertRaises(GunlukHatasi):
            g.ekle('nav', 0, veri={'nav': float('nan')})
        self.assertEqual(len(g), 0)

    def test_ayni_dizi_ayni_hash_ve_yukleme(self):
        def uret():
            g = OlayGunlugu()
            g.ekle('baslangic', 0, veri={'nav0': 100.0, 'L': 1.0})
            g.ekle('emir_niyeti', 5, coin='X', miktar=2.0, veri={'emir': _emir(2.0).json()})
            return g
        a, b = uret(), uret()
        self.assertEqual(a.son_hash, b.son_hash)
        c = OlayGunlugu.kayitlardan(a.kayitlar())
        self.assertEqual(c.son_hash, a.son_hash)

    def test_zaman_kesimi(self):
        g = OlayGunlugu()
        g.ekle('baslangic', 0, veri={'nav0': 1.0})
        g.ekle('nav', 10, veri={'nav': 1.0})
        g.ekle('nav', 20, veri={'nav': 1.0})
        self.assertEqual(len(g.kayitlar(10)), 2)


class IndirgeyiciTest(unittest.TestCase):
    def _gunluk(self):
        g = OlayGunlugu()
        g.ekle('baslangic', 0, veri={'nav0': 1000.0})
        g.ekle('emir_niyeti', 0, coin='X', miktar=2.0, veri={'emir': _emir(2.0).json()})
        g.ekle('dolum', 1, coin='X', miktar=1.5, fiyat=10.0, veri={})
        g.ekle('funding', 2, coin='X', veri={'tutar': -0.5, 'damga_ms': 2})
        g.ekle('devreden_iptal', 3, coin='X', veri={'iptal': 0.5, 'tamami': False})
        return g

    def test_dolum_funding_iptal(self):
        d = _katla(self._gunluk())
        self.assertEqual(d.pozisyonlar, {'X': 1.5})
        self.assertAlmostEqual(d.nakit, 1000.0 - 15.0 - 0.5, places=12)
        self.assertEqual(d.devreden, {})

    def test_uzlasma_pozisyonu_kapatir(self):
        g = self._gunluk()
        g.ekle('uzlasma', 4, coin='X', miktar=-1.5, fiyat=9.0, veri={})
        d = _katla(g)
        self.assertEqual(d.pozisyonlar, {})
        self.assertAlmostEqual(d.nakit, 984.5 + 13.5, places=12)
        self.assertEqual(d.uzlasilan, ('X',))

    def test_kismi_dolum_devredeni_azaltir(self):
        g = OlayGunlugu()
        g.ekle('baslangic', 0, veri={'nav0': 1000.0})
        g.ekle('emir_niyeti', 0, coin='X', miktar=-3.0, veri={'emir': _emir(-3.0).json()})
        g.ekle('dolum', 1, coin='X', miktar=-1.0, fiyat=10.0, veri={})
        d = _katla(g)
        self.assertAlmostEqual(d.devreden['X'].kalan, -2.0, places=12)
        self.assertAlmostEqual(d.nakit, 1010.0, places=12)

    def test_tam_kapanis_son_parcasi_pozisyonu_tam_sifirlar(self):
        g = OlayGunlugu()
        g.ekle('baslangic', 0, veri={'nav0': 1000.0})
        g.ekle('emir_niyeti', 0, coin='X', miktar=0.1, veri={'emir': _emir(0.1).json()})
        g.ekle('dolum', 1, coin='X', miktar=0.1, fiyat=10.0, veri={})
        g.ekle('emir_niyeti', 1, coin='X', miktar=0.2, veri={'emir': _emir(0.2).json()})
        g.ekle('dolum', 2, coin='X', miktar=0.2, fiyat=10.0, veri={})
        q = _katla(g).pozisyonlar['X']            # 0.1 + 0.2 = 0.30000000000000004
        g.ekle('emir_niyeti', 3, coin='X', miktar=-q, veri={'emir': _emir(-q, tam=True).json()})
        g.ekle('dolum', 4, coin='X', miktar=-q, fiyat=10.0, veri={'tam_kapanis_son': True})
        d = _katla(g)
        self.assertNotIn('X', d.pozisyonlar)
        self.assertEqual(d.devreden, {})

    def test_funding_dolgu_listesi_gercek_kayitla_temizlenir(self):
        g = OlayGunlugu()
        g.ekle('baslangic', 0, veri={'nav0': 1000.0})
        g.ekle('funding_dolgu', 5, coin='X', veri={'tutar': -1.0, 'saatler': [[4, -0.75], [5, -0.25]]})
        g.ekle('funding_dolgu', 6, coin='X', veri={'tutar': -0.25, 'saatler': [[6, -0.25]]})
        d = _katla(g)
        self.assertEqual(d.funding_dolgu, {'X': ((4, -0.75), (5, -0.25), (6, -0.25))})
        self.assertEqual(d.funding_dolgu_kadar, {'X': 6})
        g.ekle('ters_kayit', 8, coin='X', veri={'tutar': 1.25})
        g.ekle('funding', 8, coin='X', veri={'tutar': -0.4, 'damga_ms': 8, 'kapsam_bas_ms': 0, 'budama_ms': 0})
        d = _katla(g)
        self.assertEqual(d.funding_dolgu, {})
        self.assertEqual(d.funding_islenen, {'X': (8,)})
        self.assertAlmostEqual(d.nakit, 1000.0 - 0.4, places=12)

    def test_gec_gelen_gercek_kayit_yalniz_damgasina_kadarki_dolgulari_kesinlestirir(self):
        # Kayit 8 damgali, 10'da gelir (Codex K1): 9 ve 10 saatlerinin dolgusu beklemeye devam eder.
        g = OlayGunlugu()
        g.ekle('baslangic', 0, veri={'nav0': 1000.0})
        g.ekle('funding_dolgu', 10, coin='X', veri={'tutar': -3.0, 'saatler': [[8, -1.0], [9, -1.0], [10, -1.0]]})
        g.ekle('ters_kayit', 10, coin='X', veri={'tutar': 1.0})
        g.ekle('funding', 10, coin='X', veri={'tutar': -0.4, 'damga_ms': 8, 'kapsam_bas_ms': 0, 'budama_ms': 0})
        d = _katla(g)
        self.assertEqual(d.funding_dolgu, {'X': ((9, -1.0), (10, -1.0))})
        self.assertEqual(d.funding_islenen, {'X': (8,)})

    def test_kapsanmayan_dolgu_bekler_pencere_disinda_budanir(self):
        # Codex 2. tur K1/K2: kayit yalniz kapsadigi saatlerin dolgusunu dusurur; eski eksik uzlasmanin dolgusu
        # gec kayit penceresi boyunca bekler, pencere disina cikinca budanir.
        g = OlayGunlugu()
        g.ekle('baslangic', 0, veri={'nav0': 1000.0})
        g.ekle('funding_dolgu', 10, coin='X', veri={'tutar': -2.0, 'saatler': [[3, -1.0], [9, -1.0]]})
        g.ekle('funding', 10, coin='X', veri={'tutar': -0.4, 'damga_ms': 10, 'kapsam_bas_ms': 8, 'budama_ms': 0})
        self.assertEqual(_katla(g).funding_dolgu, {'X': ((3, -1.0),)})
        g.ekle('funding', 20, coin='X', veri={'tutar': -0.4, 'damga_ms': 18, 'kapsam_bas_ms': 10, 'budama_ms': 5})
        d = _katla(g)
        self.assertEqual(d.funding_dolgu, {})
        self.assertEqual(d.funding_islenen, {'X': (10, 18)})

    def test_karar_kaydi_funding_durumunu_budar(self):
        # Codex 3. tur: funding olayi gelmeyen coinde de eski dolgu/islenen damga gunluk kararla temizlenir.
        g = OlayGunlugu()
        g.ekle('baslangic', 0, veri={'nav0': 1000.0})
        g.ekle('funding_dolgu', 10, coin='X', veri={'tutar': -2.0, 'saatler': [[3, -1.0], [9, -1.0]]})
        g.ekle('funding', 10, coin='Y', veri={'tutar': -0.4, 'damga_ms': 4, 'kapsam_bas_ms': 0, 'budama_ms': 0})
        g.ekle('karar', 20, veri={'evren': [], 'evren_ms': None, 'maske': {}, 'funding_budama_ms': 5})
        d = _katla(g)
        self.assertEqual(d.funding_dolgu, {'X': ((9, -1.0),)})
        self.assertEqual(d.funding_islenen, {})

    def test_duzeltme_miktari_pozisyonu_degistirir(self):
        # Canli borsa uzlasmasi (Codex K9): eksik dolum duzeltmesi pozisyonu ve pozisyon gecmisini degistirir.
        g = self._gunluk()
        g.ekle('duzeltme', 5, coin='X', miktar=0.5, veri={'tutar': -5.0})
        d = _katla(g)
        self.assertEqual(d.pozisyonlar, {'X': 2.0})
        self.assertAlmostEqual(d.nakit, 984.5 - 5.0, places=12)
        self.assertEqual(pozisyon_gecmisi(g, 'X'), ((1, 1.5), (5, 2.0)))

    def test_korunan_kapanis_parcasi_tam_kapanis_olur(self):
        # q = 0.3, eski emir -0.8: 0'dan sonraki -0.5 iptal, korunan -0.3 tam kapanis (Codex K14).
        g = OlayGunlugu()
        g.ekle('baslangic', 0, veri={'nav0': 1000.0})
        g.ekle('emir_niyeti', 0, coin='X', miktar=0.3, veri={'emir': _emir(0.3).json()})
        g.ekle('dolum', 1, coin='X', miktar=0.3, fiyat=10.0, veri={})
        g.ekle('emir_niyeti', 1, coin='X', miktar=-0.8, veri={'emir': _emir(-0.8).json()})
        from motor.emir import artiran_iptali
        iptal = artiran_iptali(-0.8, 0.3, 'islem_disi')
        self.assertTrue(iptal['tam_kapanis'])
        self.assertAlmostEqual(iptal['iptal'], -0.5, places=12)
        g.ekle('devreden_iptal', 2, coin='X', veri=iptal)
        e = _katla(g).devreden['X']
        self.assertTrue(e.tam_kapanis)
        self.assertAlmostEqual(e.kalan, -0.3, places=12)

    def test_bozuk_zincirden_durum_turetilmez(self):
        # Codex K15: veri sozlugu sonradan degistirilirse durum_turet hata verir.
        g = self._gunluk()
        g.kayitlar()[0].veri['nav0'] = 999.0
        self.assertFalse(g.dogrula())
        with self.assertRaises(DurumHatasi):
            durum_turet(PiyasaGorunumu(t_ms=10, barlar={}, funding={}, adaylar=()), g)

    def test_baslangicsiz_gunluk_hata(self):
        g = OlayGunlugu()
        g.ekle('nav', 0, veri={'nav': 1.0})
        with self.assertRaises(DurumHatasi):
            _katla(g)

    def test_iptalsiz_yeni_niyet_hata(self):
        g = OlayGunlugu()
        g.ekle('baslangic', 0, veri={'nav0': 1.0})
        g.ekle('emir_niyeti', 0, coin='X', miktar=1.0, veri={'emir': _emir(1.0).json()})
        g.ekle('emir_niyeti', 0, coin='X', miktar=1.0, veri={'emir': _emir(1.0).json()})
        with self.assertRaises(DurumHatasi):
            _katla(g)

    def test_durum_turet_gorunum_zamanina_kadar_katlar(self):
        g = self._gunluk()
        gor = PiyasaGorunumu(t_ms=1, barlar={}, funding={}, adaylar=())
        d = durum_turet(gor, g)
        self.assertEqual(d.pozisyonlar, {'X': 1.5})
        self.assertAlmostEqual(d.nakit, 985.0, places=12)   # funding (t=2) henuz yok
        self.assertEqual(d.t_ms, 1)

    def test_pozisyon_gecmisi_ve_q_once(self):
        gec = pozisyon_gecmisi(self._gunluk(), 'X')
        self.assertEqual(gec, ((1, 1.5),))
        self.assertEqual(q_once(gec, 1), 0.0)     # t=1'deki dolum funding'den sonradir
        self.assertEqual(q_once(gec, 2), 1.5)

    def test_emir_json_gidis_donus(self):
        e = _emir(-2.5, tam=True)
        e2 = Emir.jsondan(e.json())
        self.assertEqual(e2.json(), e.json())


if __name__ == '__main__':
    unittest.main()
