"""Kosu -> olcut girdileri (banka/degerlendirme.py): gunluk getiri NAV'la, net katkilar pencere P&L'iyle, B'nin B5
paydasi trend satirlariyla tutarli. Sentetik senaryolar; performans olcumu degildir."""
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

from banka import olcutler as o  # noqa: E402
from banka.degerlendirme import DegerlendirmeHatasi, Pencere, birincil_olcum, gunluk_getiri, sadece_sharpe  # noqa: E402
from fikstur.saatlik_veri import (CARRY_GUN, SENARYO_GUN, carry_senaryo_verisi, gun_ms, saat_ms,  # noqa: E402
                                  senaryo_verisi)
from motor.ayristirma import ayristir  # noqa: E402
from motor.geri_test import KosuAyarlari, kos  # noqa: E402
from motor.tipler import Parametreler  # noqa: E402


class ATest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.veri = senaryo_verisi()
        cls.s = kos(cls.veri, KosuAyarlari(t0_ms=gun_ms(92), t_son_ms=saat_ms(SENARYO_GUN * 24 - 1)), Parametreler())
        cls.pen = Pencere(bas_ms=gun_ms(92), dilim_gun=(10, 20, 20, 8))       # kosu pencere basinda baslar
        cls.ol = birincil_olcum(cls.s, cls.veri, cls.pen, 'A')

    def test_getiri_nav(self):
        r = np.array(self.ol['r'])
        self.assertEqual(len(r), 58)
        nav_son = float(self.s.nav[-1])
        self.assertAlmostEqual(float(np.prod(1 + r)) * 100_000.0, nav_son, places=4)
        self.assertAlmostEqual(self.ol['sr'], o.sharpe(r), places=12)
        self.assertAlmostEqual(sadece_sharpe(self.s, self.pen), self.ol['sr'], places=12)

    def test_haric_gunler(self):
        # BK-5: haric gunlerin getirisi olcutlerden, P&L'i katki ve B5 paydasindan dusulur.
        haric = (gun_ms(95), gun_ms(120))
        pen = replace(self.pen, haric_gunler=haric)
        ol = birincil_olcum(self.s, self.veri, pen, 'A')
        g = self.pen.gunler()
        tut = ~np.isin(g, haric)
        np.testing.assert_array_equal(np.array(ol['r']), np.array(self.ol['r'])[tut])
        self.assertEqual(ol['T'], 56)
        nav = {int(t): float(v) for t, v in zip(self.s.nav_ms, self.s.nav)}
        dusen = sum(nav[h + 86_400_000] - nav[h] for h in haric)
        self.assertAlmostEqual(sum(ol['katki'].values()), sum(self.ol['katki'].values()) - dusen, places=4)
        self.assertAlmostEqual(ol['b5_payda'], self.ol['b5_payda'] - dusen, places=4)
        self.assertEqual(birincil_olcum(self.s, self.veri, replace(self.pen, haric_gunler=()), 'A'), self.ol)

    def test_null_sharpe_haric_gunler(self):
        # Codex T18-CIDDI-2: sadece_sharpe (x2/x3, çıkarma, null) birincil ölçümle aynı günleri düşer; haric gün yoksa
        # sonuç eski formülle bit düzeyinde aynı (kalibrasyon).
        eski = o.sharpe(gunluk_getiri(self.s, self.pen))
        self.assertEqual(sadece_sharpe(self.s, self.pen), eski)
        self.assertEqual(sadece_sharpe(self.s, replace(self.pen, haric_gunler=())), eski)
        haric = (gun_ms(95), gun_ms(120))
        pen = replace(self.pen, haric_gunler=haric)
        self.assertEqual(sadece_sharpe(self.s, pen), birincil_olcum(self.s, self.veri, pen, 'A')['sr'])
        self.assertNotEqual(sadece_sharpe(self.s, pen), eski)

    def test_haric_gundeki_uc_getiri_null_sr_etkilemez(self):
        from types import SimpleNamespace
        pen = Pencere(bas_ms=gun_ms(92), dilim_gun=(5, 5), haric_gunler=(gun_ms(95),))
        rng = np.random.default_rng(3)

        def sahte(uc):
            r = rng.normal(0.001, 0.01, 10)
            r[3] = uc                                                 # gün 95 (haric)
            nav = 100_000.0 * np.concatenate(([1.0], np.cumprod(1 + r)))      # gün sınırları 92 ... 102
            return SimpleNamespace(nav_ms=gun_ms(92) + np.arange(11, dtype=np.int64) * 86_400_000, nav=nav,
                                   gunluk=SimpleNamespace(kayitlar=lambda: [SimpleNamespace(
                                       tur='baslangic', veri={'nav0': 100_000.0})]))
        rng = np.random.default_rng(3)
        a = sadece_sharpe(sahte(0.9), pen)
        rng = np.random.default_rng(3)
        b = sadece_sharpe(sahte(-0.9), pen)
        self.assertAlmostEqual(a, b, places=12)                       # NAV oranından: yalnız yuvarlama farkı
        rng = np.random.default_rng(3)
        self.assertGreater(abs(sadece_sharpe(sahte(0.9), replace(pen, haric_gunler=())) - a), 0.1)

    def test_katki_toplami(self):
        self.assertAlmostEqual(sum(self.ol['katki'].values()), float(self.s.nav[-1]) - 100_000.0, places=4)
        self.assertAlmostEqual(self.ol['b5_payda'], sum(self.ol['katki'].values()), places=4)
        alt = self.ol['alt_katki_sirasi']
        self.assertNotIn('BTCUSDT', alt)
        self.assertEqual(alt, sorted(alt, key=lambda c: (-abs(self.ol['katki'][c]), c)))

    def test_ara_pencere_ve_kapsam(self):
        pen = Pencere(bas_ms=gun_ms(100), dilim_gun=(20, 20, 10, 0))
        r = gunluk_getiri(self.s, pen)
        nav_ms = self.s.nav_ms.tolist()
        beklenen = self.s.nav[nav_ms.index(gun_ms(150))] / self.s.nav[nav_ms.index(gun_ms(100))]
        self.assertAlmostEqual(float(np.prod(1 + r)), float(beklenen), places=10)
        with self.assertRaises(DegerlendirmeHatasi):
            gunluk_getiri(self.s, Pencere(bas_ms=gun_ms(80), dilim_gun=(10,)))

    def test_alanlar_sonlu(self):
        for k in ('sr', 'b4_sr', 'b8_sr', 'b11_mdd', 'eta', 'g3', 'g4'):
            self.assertTrue(math.isfinite(self.ol[k]), k)
        self.assertEqual(len(self.ol['dilim_sr']), 4)


class BTest(unittest.TestCase):
    def test_b5_paydasi_trend_satirlari(self):
        veri = carry_senaryo_verisi()
        p = replace(Parametreler(), mimari='B')
        s = kos(veri, KosuAyarlari(t0_ms=gun_ms(92), t_son_ms=saat_ms(CARRY_GUN * 24 - 1)), p)
        a = ayristir(s.gunluk, veri, p)
        pen = Pencere(bas_ms=gun_ms(95), dilim_gun=(10, 10, 10, 5))
        ol = birincil_olcum(s, veri, pen, 'B', ayristirma=a)
        ic = (a.saat_ms >= pen.bas_ms) & (a.saat_ms < pen.bit_ms)
        sat = a.satirlar
        beklenen = float((sat['trend_fiyat'] + sat['trend_funding'] - sat['trend_maliyet'])[ic].sum())
        self.assertAlmostEqual(ol['b5_payda'], beklenen, places=6)
        with self.assertRaises(DegerlendirmeHatasi):
            birincil_olcum(s, veri, pen, 'B')
        # Codex T18-CIDDI-3: birincil dışı B birimleri (ızgara, Kelly, çıkarma, K-evren) B5'siz ölçülür; ayrıştırma
        # gerekmez; öteki alanlar B5'li ölçümle aynı.
        yan = birincil_olcum(s, veri, pen, 'B', b5=False)
        self.assertEqual((yan['b5_pay'], yan['b5_epizot_sayisi'], yan['b5_payda']), (None, None, None))
        B5 = ('b5_pay', 'b5_epizot_sayisi', 'b5_payda')
        self.assertEqual({k: v for k, v in yan.items() if k not in B5}, {k: v for k, v in ol.items() if k not in B5})
        with self.assertRaises(DegerlendirmeHatasi):
            birincil_olcum(s, veri, pen, 'C', b5=False)


if __name__ == '__main__':
    unittest.main()
