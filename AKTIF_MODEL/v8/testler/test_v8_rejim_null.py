"""Rejim-null (banka/rejim_null.py; BANKA_ONKAYIT_TASLAK Ss3.5). P6: blok atamasi (Y2 kenar bloklar, Y3 ortak ve
ikincil esleme), saat eslemesinin permutasyon ve dilim-ici olmasi."""
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

from banka.rejim_null import (BLOK_SAAT, SONSUZ, coin_blok_atamasi, degismezler, dilim_bloklari,  # noqa: E402
                              n1_farki, null_yolu, ro_getirileri, saat_eslemesi, sentetik_veri, yasamlar)
from fikstur.saatlik_veri import CoinTarifi, V8_TEST_BAS_MS, tam_veri_uret  # noqa: E402
from kalibrasyon import duzey2_uretec as u  # noqa: E402
from kalibrasyon.tohum import TOHUM_KAL, uretec  # noqa: E402
from motor.geri_test import KosuAyarlari, kos  # noqa: E402
from motor.gorunum import GUN_MS, SAAT_MS  # noqa: E402
from motor.tipler import Parametreler  # noqa: E402

DILIMLER = [(240, 240 + 264 * 24), (240 + 264 * 24, 240 + 629 * 24)]      # 52 tam + 96 saat kuyruk; 73 tam
H = 240 + 629 * 24 + 48


def perm_u(j):
    return np.random.Generator(np.random.PCG64(1000 + j))


def ikincil_u(j, i):
    return np.random.Generator(np.random.PCG64(2000 + 100 * j + i))


class BlokTest(unittest.TestCase):
    def test_dilim(self):
        db = dilim_bloklari(*DILIMLER[0])
        self.assertEqual(db.n_tam, 52)
        self.assertEqual(db.bit - (db.bas + db.n_tam * BLOK_SAAT), 96)
        self.assertEqual(db.blok(db.bas + 52 * 120), -1)                  # kuyruk
        with self.assertRaises(ValueError):
            dilim_bloklari(5, 100)

    def test_surekli_coin_ortak_permutasyon(self):
        db = dilim_bloklari(*DILIMLER[0])
        pi = perm_u(1).permutation(db.n_tam)

        def cagrilmamali():
            raise AssertionError("surekli coinde ikincil permutasyon gerekmez")
        atama, ortak, toplam = coin_blok_atamasi(0, SONSUZ, db, pi, cagrilmamali)
        self.assertEqual(atama, {k: int(pi[k]) for k in range(db.n_tam)})
        self.assertEqual(ortak, toplam)

    def test_listelenen_ve_olen(self):
        db = dilim_bloklari(*DILIMLER[1])
        pi = perm_u(2).permutation(db.n_tam)
        a = db.blok_bas(10) + 30                    # blok 10 kenar
        d = db.blok_bas(60) + 5                     # blok 60 kenar
        atama, ortak, toplam = coin_blok_atamasi(a, d, db, pi, lambda: ikincil_u(2, 7))
        R = list(range(11, 60))
        self.assertEqual(sorted(atama), R)
        self.assertEqual(sorted(atama.values()), R)              # her blok bir kez
        self.assertEqual(toplam, len(R))
        self.assertTrue(0 <= ortak <= toplam)
        for k, b in atama.items():
            if int(pi[k]) in set(R):
                self.assertEqual(b, int(pi[k]))                  # ortak eslesme korunur

    def test_blok_basinda_listelenme_kenardir(self):
        db = dilim_bloklari(*DILIMLER[1])
        pi = perm_u(2).permutation(db.n_tam)
        atama, _, _ = coin_blok_atamasi(db.blok_bas(5), SONSUZ, db, pi, lambda: ikincil_u(2, 1))
        self.assertNotIn(5, atama)
        self.assertEqual(sorted(atama), list(range(6, db.n_tam)))


class SaatEslemesiTest(unittest.TestCase):
    def setUp(self):
        db2 = dilim_bloklari(*DILIMLER[1])
        self.yasam = {'BTC': (0, SONSUZ), 'L': (db2.blok_bas(3) + 7, SONSUZ), 'O': (0, db2.blok_bas(40) + 100),
                      'LO': (db2.blok_bas(2) + 1, db2.blok_bas(50) + 3)}
        self.no = {'BTC': 1, 'L': 2, 'O': 3, 'LO': 4}
        self.k, self.pay = saat_eslemesi(self.yasam, self.no, DILIMLER, perm_u, ikincil_u, H)

    def test_permutasyon_ve_dilim_ici(self):
        for c, k in self.k.items():
            self.assertTrue(np.array_equal(np.sort(k), np.arange(H)), c)
            for bas, bit in DILIMLER:
                self.assertTrue(np.all((k[bas:bit] >= bas) & (k[bas:bit] < bit)), c)
            self.assertTrue(np.array_equal(k[:DILIMLER[0][0]], np.arange(DILIMLER[0][0])))   # isinma kimlik
            self.assertTrue(np.array_equal(k[DILIMLER[-1][1]:], np.arange(DILIMLER[-1][1], H)))

    def test_yasam_korunur(self):
        for c, (a, d) in self.yasam.items():
            k = self.k[c]
            icinde = (np.arange(H) >= a) & (np.arange(H) < min(d, H))
            self.assertTrue(np.all((k[icinde] >= a) & (k[icinde] < min(d, H))), c)   # yasam ici saat yasam icine
            self.assertEqual(int(k[a]), a)                                              # listelenme bari yerinde
            if d != SONSUZ:
                self.assertEqual(int(k[d - 1]), d - 1)                                  # olum bari yerinde

    def test_blok_ici_sira_ve_ortak_pay(self):
        k = self.k['BTC']
        for bas, bit in DILIMLER:
            for h in range(bas, bas + ((bit - bas) // 120) * 120, 120):
                self.assertTrue(np.array_equal(np.diff(k[h:h + 120]), np.ones(119)))
        self.assertGreater(self.pay['toplam'], 0)
        self.assertLessEqual(self.pay['ortak'], self.pay['toplam'])

    def test_belirlenimli(self):
        k2, pay2 = saat_eslemesi(self.yasam, self.no, DILIMLER, perm_u, ikincil_u, H)
        self.assertEqual(pay2, self.pay)
        for c in self.k:
            self.assertTrue(np.array_equal(k2[c], self.k[c]))


def duzey2_dilimleri():
    bas = u.ISINMA_GUN * 24
    out = []
    for g in u.DILIM_GUN:
        out.append((bas, bas + g * 24))
        bas += g * 24
    return out


class YenidenKurmaTest(unittest.TestCase):
    """P7: Duzey 2 yolundan (ayar 0, yol 1) bir null yolu; N1-N6 ve yeniden kurma kurallari."""

    @classmethod
    def setUpClass(cls):
        cls.veri, cls.ham = u.yol_verisi(0, 1)
        cls.dilimler = duzey2_dilimleri()
        no = {c: i + 1 for i, c in enumerate(u.COINLER)}
        cls.sent, cls.pay, cls.deg = null_yolu(
            cls.veri, u.BAS_MS, u.SAAT, cls.dilimler, no,
            lambda j: uretec(TOHUM_KAL, 2, 0, 1, 1, j), lambda j, i: uretec(TOHUM_KAL, 2, 0, 1, 1, j, i))

    def test_degismezler(self):
        self.assertTrue(self.deg['gecti'], self.deg['ihlaller'][:5])
        self.assertGreater(self.pay['ortak'], 0.8 * self.pay['toplam'])

    def test_yasamlar(self):
        y = yasamlar(self.veri, u.BAS_MS, u.SAAT)
        self.assertEqual(y['BTCUSDT'], (0, SONSUZ))
        for c, g in self.ham.yasam.olen:
            self.assertEqual(y[c][1], g * 24)
        for c, g in self.ham.yasam.listelenen:
            self.assertEqual(y[c][0], g * 24)

    def test_isinma_ayni_dilim_farkli(self):
        s, z = self.veri.barlar['C05USDT'], self.sent.barlar['C05USDT']
        n = u.ISINMA_GUN * 24
        self.assertTrue(np.array_equal(s.acilis_ms[:n], z.acilis_ms[:n]))
        self.assertTrue(np.allclose(z.kapanis[:n], s.kapanis[:n], rtol=1e-12, atol=0))
        ic = slice(n + 200, n + 2000)
        self.assertFalse(np.allclose(z.kapanis[ic], s.kapanis[ic], rtol=1e-6))

    def test_funding_tasinir(self):
        f, g = self.veri.funding['BTCUSDT'], self.sent.funding['BTCUSDT']
        self.assertEqual(len(f), len(g))
        self.assertTrue(np.all(np.diff(g.damga_ms) > 0))
        self.assertTrue(np.array_equal(np.sort(f.oran), np.sort(g.oran)))
        saat = (g.damga_ms - u.BAS_MS) // SAAT_MS
        self.assertTrue(np.all(saat % 8 == 0))              # 00:00 hizali bloklar uzlasma fazini korur

    def test_motor_null_yolunda_kosar(self):
        pen = u.pencere()
        s = kos(self.sent, KosuAyarlari(t0_ms=pen.bas_ms, t_son_ms=pen.bas_ms + 3 * GUN_MS - SAAT_MS), Parametreler())
        self.assertTrue(np.all(np.isfinite(s.nav)))
        self.assertEqual(len(s.kararlar), 3)


class DuzBarTest(unittest.TestCase):
    def test_duz_bar_ve_bosluk_korunur(self):
        duz = frozenset(range(15 * 24 + 3, 15 * 24 + 9))
        eksik = frozenset({22 * 24 + 5})
        veri = tam_veri_uret({'X': CoinTarifi(saatlik_vol=0.01, duz_saatler=duz, eksik_saatler=eksik),
                              'Y': CoinTarifi(saatlik_vol=0.01)}, 40)
        dilimler = [(10 * 24, 25 * 24), (25 * 24, 40 * 24)]
        kaynak, _ = saat_eslemesi(yasamlar(veri, V8_TEST_BAS_MS, 40 * 24), {'X': 1, 'Y': 2}, dilimler,
                                  lambda j: np.random.Generator(np.random.PCG64(j)),
                                  lambda j, i: np.random.Generator(np.random.PCG64(100 * j + i)), 40 * 24)
        sent = sentetik_veri(veri, kaynak, V8_TEST_BAS_MS)
        self.assertTrue(degismezler(veri, sent, dilimler, V8_TEST_BAS_MS)['gecti'])
        z = sent.barlar['X']
        esit = (z.acilis == z.yuksek) & (z.yuksek == z.dusuk) & (z.dusuk == z.kapanis)
        self.assertEqual(int(esit.sum()), len(duz))              # O = H = L = C bit duzeyinde korunur
        self.assertEqual(len(z), len(veri.barlar['X']))          # bosluk sayisi korunur


class N3BoslukTasimaTest(unittest.TestCase):
    """Codex T12-6: yasam ici bosluk dilimin ilk konumuna tasininca N3 ihlal sayilmaz."""

    def test_ilk_konuma_tasinan_bosluk(self):
        bas, b = 240, 3
        dilimler = [(bas, bas + 30 * 24)]                        # 6 tam blok
        veri = tam_veri_uret({'X': CoinTarifi(saatlik_vol=0.01, eksik_saatler=frozenset({bas + b * 120})),
                              'Y': CoinTarifi(saatlik_vol=0.01)}, 40)
        tohum = next(t for t in range(10_000) if np.random.Generator(np.random.PCG64(t)).permutation(6)[0] == b)
        kaynak, _ = saat_eslemesi(yasamlar(veri, V8_TEST_BAS_MS, 40 * 24), {'X': 1, 'Y': 2}, dilimler,
                                  lambda j: np.random.Generator(np.random.PCG64(tohum)),
                                  lambda j, i: np.random.Generator(np.random.PCG64(100 + i)), 40 * 24)
        sent = sentetik_veri(veri, kaynak, V8_TEST_BAS_MS)
        h = (sent.barlar['X'].acilis_ms - V8_TEST_BAS_MS) // SAAT_MS
        ilk_sentetik = int(h[(h >= bas) & (h < bas + 30 * 24)][0])
        self.assertEqual(ilk_sentetik, bas + 1)                  # bosluk dilimin ilk saatine tasindi
        d = degismezler(veri, sent, dilimler, V8_TEST_BAS_MS)
        self.assertTrue(d['gecti'], d['ihlaller'])


class N1BagSirasiTest(unittest.TestCase):
    """Teknik ek banka_oncesi (kuru koşu 2 Ekim; ciktilar/v8_kuru_20261002b/HATA_N1.md). D'den bağımsız fikstür: fiyatlar
    kaba tik ızgarasında ve açılış = önceki kapanış → rho dörtlülerinde çok sayıda tam bağ. Sentetikte exp/log
    yuvarlaması bağları ~1e-16 bozar; eski N1 (ham değerle lexsort) satırları kaydırıp yanlış alarm verir."""

    @staticmethod
    def _tikli(veri, tik):
        barlar = {}
        for c, s in veri.barlar.items():
            k = np.maximum(np.round(np.asarray(s.kapanis) / tik), 1.0) * tik
            o = np.concatenate(([k[0]], k[:-1]))
            hi = np.maximum(np.round(np.asarray(s.yuksek) / tik) * tik, np.maximum(o, k))
            lo = np.minimum(np.maximum(np.round(np.asarray(s.dusuk) / tik), 1.0) * tik, np.minimum(o, k))
            barlar[c] = replace(s, acilis=o, yuksek=hi, dusuk=lo, kapanis=k)
        return replace(veri, barlar=barlar)

    @staticmethod
    def _eski_n1_gecer(veri, sent, dilimler, tol=1e-9):
        for c in veri.barlar:
            s, z = veri.barlar[c], sent.barlar[c]
            hs = (np.asarray(s.acilis_ms) - V8_TEST_BAS_MS) // SAAT_MS
            hz = (np.asarray(z.acilis_ms) - V8_TEST_BAS_MS) // SAAT_MS
            rs, rz = np.column_stack(ro_getirileri(s)[:4]), np.column_stack(ro_getirileri(z)[:4])
            for bas, bit in dilimler:
                a, b = rs[(hs >= bas) & (hs < bit)], rz[(hz >= bas) & (hz < bit)]
                if not np.allclose(a[np.lexsort(a.T[::-1])], b[np.lexsort(b.T[::-1])], rtol=0.0, atol=tol):
                    return False
        return True

    def test_tik_bagli_veride_yanlis_alarm_yok(self):
        veri = self._tikli(tam_veri_uret({'X': CoinTarifi(p0=2.0, saatlik_vol=0.01),
                                          'Y': CoinTarifi(p0=3.0, saatlik_vol=0.01)}, 40), 0.01)
        dilimler = [(10 * 24, 25 * 24), (25 * 24, 40 * 24)]
        kaynak, _ = saat_eslemesi(yasamlar(veri, V8_TEST_BAS_MS, 40 * 24), {'X': 1, 'Y': 2}, dilimler,
                                  lambda j: np.random.Generator(np.random.PCG64(j)),
                                  lambda j, i: np.random.Generator(np.random.PCG64(100 * j + i)), 40 * 24)
        sent = sentetik_veri(veri, kaynak, V8_TEST_BAS_MS)
        self.assertFalse(self._eski_n1_gecer(veri, sent, dilimler))             # hata: eski denetim alarm verir
        d = degismezler(veri, sent, dilimler, V8_TEST_BAS_MS)
        self.assertTrue(d['gecti'], d['ihlaller'][:5])                          # düzeltilmiş denetim geçer

    def test_n1_gercek_farki_yakalar(self):
        rng = np.random.default_rng(3)
        a = np.round(rng.normal(0, 0.01, (500, 4)), 3)                          # bol tam bağ
        b = a[rng.permutation(500)] + rng.normal(0, 1e-16, (500, 4))            # yalnız yuvarlama gürültüsü
        self.assertIsNone(n1_farki(a, b, 1e-9))
        b2 = b.copy()
        b2[7, 2] += 1e-6                                                        # gerçek fark
        self.assertGreater(n1_farki(a, b2, 1e-9), 1e-7)
        t, e = 1e-9, 1e-16                                                      # Codex T32-1 karşı örneği
        a4 = np.array([[0, .01, -.01, 0], [0, .02, -.01, 0], [t / 2, .03, -.01, 0], [t / 2, .04, -.01, 0]])
        b4 = np.array([[e, .01, -.01, 0], [-e, .02, -.01, 0], [t / 2 + e, .03, -.01, 0], [t / 2 - e, .04, -.01, 0]])
        self.assertIsNone(n1_farki(a4, b4, t))                                  # iki ızgara kaçırır, zincir bulur
        b5 = b4.copy()
        b5[3, 1] = .05
        self.assertIsNotNone(n1_farki(a4, b5, t))
        for tohum in range(20):                                                 # Codex T33: yaprakta yakın değerler
            r = np.random.default_rng(tohum)
            a6 = r.uniform(0, 3 * t, (12, 4))                                   # bütün sütunlar tol zincirinde
            b6 = a6[r.permutation(12)] + r.uniform(-0.4 * t, 0.4 * t, (12, 4))  # gerçek eşleşme tol içinde
            self.assertIsNone(n1_farki(a6, b6, t), tohum)
            b6[0, 1] += 10 * t                                                  # bir satır tol dışına
            self.assertIsNotNone(n1_farki(a6, b6, t), tohum)
        b3 = b.copy()
        b3[[1, 2], 0] = b3[[2, 1], 0]                                           # dörtlü bağı bozan sütun takası
        if not np.allclose(a[1], a[2]):
            self.assertIsNotNone(n1_farki(a, b3, 1e-9))

if __name__ == '__main__':
    unittest.main()
