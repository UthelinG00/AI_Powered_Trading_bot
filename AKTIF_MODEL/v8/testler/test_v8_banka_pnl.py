"""Coin basi P&L (banka/pnl.py) ve B'nin coin basi trend bacagi (ayristirma.trend_coin): NAV ozdesligi, funding
toplami, epizot atamasi. Sentetik senaryolar (A: 150 gun 5 coin, delist uzlasmasi ve maske cikisi dahil; B: 130 gun)."""
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

from banka.pnl import bolus, coin_pnl, epizot_pnl, gunluk_topla  # noqa: E402
from fikstur.saatlik_veri import (CARRY_GUN, SENARYO_GUN, SENARYO_T0_GUN, CoinTarifi, carry_senaryo_verisi,  # noqa: E402
                                  gun_ms, saat_ms, senaryo_verisi, tam_veri_uret)
from motor.gorunum import bar_indeksi, son_kapanis  # noqa: E402
from motor.gunluk import OlayGunlugu  # noqa: E402
from motor.ayristirma import ayristir  # noqa: E402
from motor.geri_test import KosuAyarlari, kos  # noqa: E402
from motor.tipler import Parametreler  # noqa: E402


class EpizotTest(unittest.TestCase):
    def test_atama(self):
        q = [0, 1, 1, 0, 0, -2, -2, 3, 0]
        e = [100.0, 0, 2, 4, 8, 0, 32, 64, 128]          # saat basindaki pozisyonun payi
        y = [0.0, 1, 0, 0, 0, 16, 0, 1000, 0]            # saat sonundakinin payi
        # h0 epizotsuz: yazilmaz. h3 kapanis, h4 gec funding -> ep0; h7 isaret degisimi: eski 64 -> ep1, yeni 1000 -> ep2.
        self.assertEqual(epizot_pnl(q, e, y), [1 + 2 + 4 + 8, 16 + 32 + 64, 1000 + 128])
        self.assertEqual(epizot_pnl([0, 0], [1.0, 2.0], [0.0, 0.0]), [])

    def test_pencere_oncesi_pozisyon_ve_gec_funding(self):
        # Codex T13-1: pencere ilk saatinde kapanan pozisyonun eski payi kaybolmaz.
        self.assertEqual(epizot_pnl([0.0], [7.0], [0.0]), [])
        self.assertEqual(epizot_pnl([0.0], [7.0], [0.0], q_onceki=1.0), [7.0])
        # Codex T13-2: yeniden acilis saatinde eski long'a gelen gec funding (5) long epizotunda kalir.
        self.assertEqual(epizot_pnl([1.0, 0.0, -1.0], [0.0, 2.0, 5.0], [1.0, 0.0, 30.0]), [1.0 + 2.0 + 5.0, 30.0])

    def test_bolus(self):
        self.assertEqual(bolus(0.0, 5.0), (0.0, 1.0))
        self.assertEqual(bolus(5.0, 0.0), (1.0, 0.0))
        self.assertEqual(bolus(5.0, 2.0), (1.0, 0.0))
        self.assertEqual(bolus(2.0, 5.0), (0.0, 1.0))
        self.assertEqual(bolus(2.0, -3.0), (0.4, 0.6))


H = 3_600_000
BAS = gun_ms(0)


def _el_gunlugu(ters_aralik: float = 4.0):
    """Elle kurulmuş A günlüğü (tek coin X, 48 saat, düz artan fiyat): 1'de long aç, 3'te kapat, 5'te AYNI YÖNDE yeniden
    aç (iki ayrı long epizot). 7'de dolgu 2/3 (ilk epizot) ve 6/7 (ikinci) saatlerini kapsar; 8'de gerçek kayıt: aralık 4
    ise (4, 8] (yalnız 6/7) ters kaydedilir, 2/3 dolgusu kalır; aralık 8 ise hepsi ters kaydedilir."""
    from motor.gorunum import TamVeri, saatlik_seri
    n = 48
    ac = 100.0 + 0.1 * np.arange(n)
    kap = ac + 0.1
    veri = TamVeri(barlar={'X': saatlik_seri(BAS + np.arange(n, dtype=np.int64) * H, ac, kap + 0.05, ac - 0.05, kap,
                                             np.full(n, 1e6))}, funding={}, adaylar=('X',))
    ters = [(h, t) for h, t in ((6, -0.2), (7, -0.2), (2, -0.1), (3, -0.1)) if 8 - ters_aralik < h]
    olay = {1: [('dolum', 1.0, None)], 3: [('dolum', -1.0, None)], 5: [('dolum', 1.0, None)],
            7: [('funding_dolgu', None, {'tutar': -0.6, 'saatler': [[BAS + 2 * H, -0.1], [BAS + 3 * H, -0.1],
                                                                     [BAS + 6 * H, -0.2], [BAS + 7 * H, -0.2]]})],
            8: [('ters_kayit', None, {'tutar': -sum(t for _, t in ters), 'damga_ms': BAS + 8 * H,
                                      'aralik_saat': ters_aralik, 'dolgu_sayisi': len(ters)}),
                ('funding', None, {'tutar': -0.3, 'damga_ms': BAS + 8 * H,
                                   'kapsam_bas_ms': BAS + int(8 - ters_aralik) * H, 'q': 1.0})]}
    kayit = [SimpleNamespace(tur='baslangic', damga_ms=BAS, coin=None, miktar=None, fiyat=None,
                             veri={'nav0': 100_000.0})]
    nakit, q, nav = 100_000.0, 0.0, []
    for T in range(n):
        for tur, m, v in olay.get(T, ()):
            if tur == 'dolum':
                kayit.append(SimpleNamespace(tur='dolum', damga_ms=BAS + T * H, coin='X', miktar=m, fiyat=ac[T],
                                             veri={}))
                nakit -= m * ac[T]
                q += m
            else:
                kayit.append(SimpleNamespace(tur=tur, damga_ms=BAS + T * H, coin='X', miktar=None, fiyat=None, veri=v))
                nakit += v['tutar']
        nav.append(nakit + q * kap[T])
    sonuc = SimpleNamespace(gunluk=SimpleNamespace(kayitlar=lambda: kayit),
                            nav_ms=BAS + np.arange(1, n + 1, dtype=np.int64) * H, nav=np.array(nav))
    return sonuc, veri


class EpizotOzgunTest(unittest.TestCase):
    """Codex T18 (B5): funding özgün saatin EPİZOTUNA gider (yön değil kimlik); tam ters kayıtta sonuç bit eşit."""

    def test_yon_degisimi_saf(self):
        q = [1, 1, 1, -1, -1, -1]
        e = [0.0, 0.0, 0.0, 0.0, -0.5, 0.0]                     # satır 4'te kayda geçen, satır 1'e ait -0.5 funding
        y = [0.0] * 6
        self.assertEqual(epizot_pnl(q, e, y), [0.0, -0.5])     # eski kural: short epizotu
        self.assertEqual(epizot_pnl(q, e, y, ozgun=[(4, 1, -0.5)]), [-0.5, 0.0])
        self.assertEqual(epizot_pnl(q, e, y, ozgun=[(4, None, -0.5)]), [0.0, 0.0])   # hiçbir epizota
        self.assertEqual(epizot_pnl(q, e, y, ozgun=[(4, 1, -0.5), (4, 1, 0.5)]), epizot_pnl(q, e, y))

    def test_ayni_yonde_yeniden_acilis(self):
        s, veri = _el_gunlugu(4.0)
        cp = coin_pnl(s, veri)
        self.assertLess(cp.ozdeslik_max_hata, 1e-9)
        oz = cp.fon_ozgun['X']
        self.assertEqual(sorted((i, (h - BAS) // H, t) for i, h, t in oz),       # 7'deki dolgu saati = kayıt saati
                         [(7, 2, -0.1), (7, 3, -0.1), (7, 6, -0.2), (8, 6, 0.2), (8, 7, 0.2)])
        eski = epizot_pnl(cp.q['X'], cp.eski['X'], cp.yeni['X'])
        yeni = epizot_pnl(cp.q['X'], cp.eski['X'], cp.yeni['X'],
                          ozgun=[(i, (h - BAS) // H, t) for i, h, t in oz])
        self.assertEqual(len(yeni), 2)                                           # iki ayrı long epizot
        self.assertAlmostEqual(yeni[0] - eski[0], -0.2, places=12)               # 2/3 dolgusu ilk epizota
        self.assertAlmostEqual(yeni[1] - eski[1], 0.2, places=12)
        self.assertAlmostEqual(sum(yeni), sum(eski), places=12)

    def test_tam_ters_kayit_bit_esit(self):
        s, veri = _el_gunlugu(8.0)
        cp = coin_pnl(s, veri)
        oz = [(i, (h - BAS) // H, t) for i, h, t in cp.fon_ozgun['X']]
        self.assertEqual(len(oz), 7)
        self.assertEqual(epizot_pnl(cp.q['X'], cp.eski['X'], cp.yeni['X'], ozgun=oz),
                         epizot_pnl(cp.q['X'], cp.eski['X'], cp.yeni['X']))

    def test_birincil_olcum_baglantisi(self):
        # A: coin_pnl.fon_ozgun, B: ayrıştırma.trend_fon_ozgun; birincil_olcum epizot_pnl'e pencere dilimi
        # indeksleriyle geçirir (pencere 1. saatten başlar: satır i -> i - 1).
        from banka import degerlendirme as D
        s, veri = _el_gunlugu(4.0)
        pen = D.Pencere(bas_ms=BAS + H, dilim_gun=(1,))
        cp = coin_pnl(s, veri)
        cagri = []
        asil = D.epizot_pnl

        def kayit(*a, **k):
            cagri.append(k.get('ozgun'))
            return asil(*a, **k)
        D.epizot_pnl = kayit
        try:
            D.birincil_olcum(s, veri, pen, 'A')
            ayr = SimpleNamespace(saat_ms=cp.saat_ms, trend_coin=cp.pnl, trend_q=cp.q, trend_eski=cp.eski,
                                  trend_yeni=cp.yeni, trend_fon_ozgun=cp.fon_ozgun)
            D.birincil_olcum(s, veri, replace(pen, dilim_gun=(1,)), 'B', ayr)
        finally:
            D.epizot_pnl = asil
        beklenen = [(6, 1, -0.1), (6, 2, -0.1), (6, 5, -0.2), (7, 5, 0.2), (7, 6, 0.2)]
        self.assertEqual([sorted(c) for c in cagri], [beklenen, beklenen])

    def test_pencere_oncesi_ozgun_saat(self):
        from banka.degerlendirme import _ozgun_dilim
        saat = BAS + np.arange(10, dtype=np.int64) * H
        icinde = np.arange(10) >= 5
        sm = np.ones(10)
        q_surer = np.array([0, 1, 1, 1, 1, 1, 1, 1, 1, 1.0])       # 1'de açılan epizot pencere başına kadar sürer
        q_kesik = np.array([0, 1, 1, 0, 1, 1, 1, 1, 1, 1.0])       # 3'te kapanıp yeniden açılmış
        par = [(7, BAS + 2 * H, -0.1), (8, BAS + 6 * H, -0.2), (3, BAS + 2 * H, -9.0)]   # sonuncusu pencere dışı kayıt
        self.assertEqual(_ozgun_dilim(par, saat, q_surer, icinde, sm), [(2, 0, -0.1), (3, 1, -0.2)])
        self.assertEqual(_ozgun_dilim(par, saat, q_kesik, icinde, sm), [(2, None, -0.1), (3, 1, -0.2)])
        sm[7] = 0.0                                                  # hariç gün saati: parça düşer
        self.assertEqual(_ozgun_dilim(par, saat, q_surer, icinde, sm), [(3, 1, -0.2)])


class IsaretDegisimiTest(unittest.TestCase):
    """Elle kurulmus gunluk: +2 al (saat 1), -5 sat (saat 5: +2 -> -3), +3 al (saat 9: kapanis)."""

    def test_eski_yeni_paylari(self):
        veri = tam_veri_uret({'X': CoinTarifi(p0=100.0, saatlik_vol=0.01)}, 1)
        s = veri.barlar['X']
        T = lambda h: saat_ms(h)
        ac = lambda h: float(s.acilis[bar_indeksi(s, T(h))])
        sk = lambda h: son_kapanis(s, T(h))
        islemler = {1: (2.0, ac(1) * 1.001), 5: (-5.0, ac(5) * 0.999), 9: (3.0, ac(9) * 1.001)}
        g = OlayGunlugu()
        g.ekle('baslangic', T(0), veri={'nav0': 1000.0})
        nakit, q, nav_ms, nav = 1000.0, 0.0, [], []
        for h in range(0, 12):
            if h in islemler:
                m, f = islemler[h]
                g.ekle('dolum', T(h), coin='X', miktar=m, fiyat=f)
                nakit -= m * f
                q += m
            nav_ms.append(T(h + 1))
            nav.append(nakit + q * sk(h + 1))
        cp = coin_pnl(SimpleNamespace(gunluk=g, nav_ms=np.array(nav_ms), nav=np.array(nav)), veri)
        self.assertLess(cp.ozdeslik_max_hata, 1e-9)
        m5, f5 = islemler[5]
        x = m5 * ac(5) - m5 * f5                                  # islemin acilisa gore P&L'i (maliyet)
        self.assertAlmostEqual(cp.eski['X'][5], 2.0 * (ac(5) - sk(5)) + 0.4 * x, places=10)
        self.assertAlmostEqual(cp.yeni['X'][5], -3.0 * (sk(6) - ac(5)) + 0.6 * x, places=10)
        ep = epizot_pnl(cp.q['X'], cp.eski['X'], cp.yeni['X'])
        self.assertEqual(len(ep), 2)
        long_ = sum(cp.pnl['X'][1:5]) + cp.eski['X'][5]
        short_ = cp.yeni['X'][5] + sum(cp.pnl['X'][6:9]) + cp.pnl['X'][9]
        self.assertAlmostEqual(ep[0], long_, places=9)
        self.assertAlmostEqual(ep[1], short_, places=9)
        self.assertAlmostEqual(sum(ep), float(cp.pnl['X'].sum()), places=9)

    def test_gunluk_topla(self):
        gunler = np.array([0, 24, 48]) * 3_600_000
        saatler = np.arange(0, 72) * 3_600_000
        out = gunluk_topla(saatler, np.ones(72), gunler)
        self.assertEqual(out.tolist(), [24.0, 24.0, 24.0])
        # Netleştirme 18: son günden sonraki ve ilk günden önceki saatler toplanmaz (önce son güne yığılıyordu).
        saatler = np.arange(-5, 100) * 3_600_000
        self.assertEqual(gunluk_topla(saatler, np.ones(105), gunler).tolist(), [24.0, 24.0, 24.0])
        self.assertEqual(gunluk_topla(saatler, np.ones(105), np.array([], dtype=np.int64)).tolist(), [])


class ASenaryoTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.veri = senaryo_verisi()
        cls.s = kos(cls.veri, KosuAyarlari(t0_ms=gun_ms(SENARYO_T0_GUN), t_son_ms=saat_ms(SENARYO_GUN * 24 - 1)),
                    Parametreler())
        cls.cp = coin_pnl(cls.s, cls.veri)

    def test_nav_ozdesligi(self):
        self.assertLess(self.cp.ozdeslik_max_hata, 1e-6)
        self.assertEqual(len(self.cp.saat_ms), len(self.s.nav))
        self.assertTrue(any(np.any(v != 0) for v in self.cp.pnl.values()))

    def test_funding_toplami(self):
        beklenen = sum(float(k.veri.get('tutar', 0.0)) for k in self.s.gunluk.kayitlar()
                       if k.tur in ('funding', 'funding_dolgu', 'ters_kayit'))
        self.assertAlmostEqual(sum(float(v.sum()) for v in self.cp.funding.values()), beklenen, places=8)

    def test_uzlasma_ve_epizot_toplami(self):
        turler = {k.tur for k in self.s.gunluk.kayitlar()}
        self.assertIn('uzlasma', turler)                       # delist uzlasmasi senaryoda var (ALT3)
        for c, x in self.cp.pnl.items():
            self.assertTrue(np.allclose(self.cp.eski[c] + self.cp.yeni[c], x, rtol=0, atol=1e-9))
            ep = epizot_pnl(self.cp.q[c], self.cp.eski[c], self.cp.yeni[c])
            self.assertAlmostEqual(sum(ep), float(x.sum()), places=6, msg=c)

    def test_pozisyon_gunlukle_ayni(self):
        son = {c: float(v[-1]) for c, v in self.cp.q.items() if v[-1] != 0.0}
        self.assertEqual(set(son), set(self.s.durum.pozisyonlar))
        for c, v in son.items():
            self.assertAlmostEqual(v, self.s.durum.pozisyonlar[c], places=12)


class BSenaryoTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.veri = carry_senaryo_verisi()
        cls.p = replace(Parametreler(), mimari='B')
        cls.s = kos(cls.veri, KosuAyarlari(t0_ms=gun_ms(92), t_son_ms=saat_ms(CARRY_GUN * 24 - 1)), cls.p)
        cls.a = ayristir(cls.s.gunluk, cls.veri, cls.p)

    def test_trend_coin_ozdesligi(self):
        sat = self.a.satirlar
        beklenen = sat['trend_fiyat'] + sat['trend_funding'] - sat['trend_maliyet']
        toplam = np.zeros(len(self.a.saat_ms))
        for v in self.a.trend_coin.values():
            toplam += v
        self.assertLess(float(np.max(np.abs(toplam - beklenen))), 1e-6)
        self.assertTrue(self.a.trend_coin)

    def test_trend_epizotlari(self):
        for c, x in self.a.trend_coin.items():
            self.assertTrue(np.allclose(self.a.trend_eski[c] + self.a.trend_yeni[c], x, rtol=0, atol=1e-8), c)
            ep = epizot_pnl(self.a.trend_q.get(c, np.zeros(len(x))), self.a.trend_eski[c], self.a.trend_yeni[c])
            self.assertAlmostEqual(sum(ep), float(x.sum()), places=6, msg=c)

    def test_coin_pnl_b(self):
        self.assertLess(coin_pnl(self.s, self.veri).ozdeslik_max_hata, 1e-6)


if __name__ == '__main__':
    unittest.main()
