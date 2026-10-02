"""Kilit adim 2 sonucu HAR'in motora entegrasyonu (on-kayit madde 12): HarTakvimi zamanlamasi, boyutlama sigmasi,
EWMA'ya donus, varsayilan EWMA yolunun degismemesi. Sentetik veri; D verisi yok."""
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

from fikstur.saatlik_veri import CoinTarifi, gun_ms, saat_ms, tam_veri_uret  # noqa: E402
from motor.geri_test import KosuAyarlari, kos  # noqa: E402
from motor.gorunum import gorunum_kur, gun_takvimi  # noqa: E402
from motor.har import (HarTakvimi, gunluk_rv, har_log_tahmin, har_ozellik, har_sigma,  # noqa: E402
                       har_varyans)
from motor.hedef import HedefHatasi, boyut_sigmalari, coin_gunluk  # noqa: E402
from motor.hijyen import MaskeKaydi  # noqa: E402
from motor.tipler import Parametreler  # noqa: E402

P = Parametreler()
BETA = (1.9, 0.2, 0.0, 0.45)


def _takvim(ilk_ay_gun=120, s2_gun=126):
    return HarTakvimi(aylar=((gun_ms(ilk_ay_gun), BETA),), s2=((gun_ms(s2_gun), 0.8),))


class TakvimTest(unittest.TestCase):
    def test_zamanlama_t_dahil_son_deger(self):
        tk = HarTakvimi(aylar=((gun_ms(10), (1, 0, 0, 0)), (gun_ms(40), None), (gun_ms(70), (2, 0, 0, 0))),
                        s2=((gun_ms(14), 0.5), (gun_ms(21), 0.6)))
        self.assertIsNone(tk.katsayi(gun_ms(9)))
        self.assertEqual(tk.katsayi(gun_ms(10)), (1, 0, 0, 0))        # ay basi gunu dahil (M <= t)
        self.assertIsNone(tk.katsayi(gun_ms(50)))                     # tanimsiz ay
        self.assertEqual(tk.katsayi(gun_ms(80)), (2, 0, 0, 0))
        self.assertIsNone(tk.artik_varyansi(gun_ms(13)))
        self.assertEqual(tk.artik_varyansi(gun_ms(20)), 0.5)
        self.assertEqual(tk.artik_varyansi(gun_ms(21)), 0.6)

    def test_sonuctan_ve_kimlik(self):
        sonuc = {'katsayi_yolu': {str(gun_ms(10)): {'beta': list(BETA), 'n_egitim': 50},
                                  str(gun_ms(40)): {'beta': None, 'n_egitim': 3}},
                 's2_yolu': {str(gun_ms(14)): 0.5}}
        tk = HarTakvimi.sonuctan(sonuc)
        self.assertEqual(tk.katsayi(gun_ms(20)), BETA)
        self.assertIsNone(tk.katsayi(gun_ms(45)))
        self.assertEqual(tk.kimlik(), HarTakvimi.sonuctan(sonuc).kimlik())


class HarSigmaTest(unittest.TestCase):
    def setUp(self):
        self.veri = tam_veri_uret({'X': CoinTarifi(saatlik_vol=0.01)}, 131)
        self.t = gun_ms(130)
        self.g = gorunum_kur(self.veri, self.t)
        s = self.g.barlar['X']
        self.gunler = gun_takvimi(int(s.acilis_ms[0]) + 3_600_000, self.t)
        self.cg = coin_gunluk(self.g, 'X', self.gunler, MaskeKaydi(), P)

    def test_formul_ve_geri_donus(self):
        s = self.g.barlar['X']
        h = har_sigma(s, self.gunler, self.cg.gun_gecerli, _takvim(), P)
        rv = gunluk_rv(s, self.gunler, P)
        oz = har_ozellik(rv, len(self.gunler) - 1, P)
        beklenen = math.sqrt(float(har_varyans(har_log_tahmin([oz], BETA)[0], 0.8)))
        self.assertAlmostEqual(h, beklenen, places=12)
        self.assertTrue(math.isnan(har_sigma(s, self.gunler, self.cg.gun_gecerli, _takvim(ilk_ay_gun=131), P)))
        self.assertTrue(math.isnan(har_sigma(s, self.gunler, self.cg.gun_gecerli, _takvim(s2_gun=131), P)))

    def test_boyut_sigmalari_har_ve_taban(self):
        ph = replace(P, sigma_tahmincisi='HAR', har_takvimi=_takvim())
        sig_h, n = boyut_sigmalari(self.g, ('X',), self.gunler, {'X': self.cg}, ph)
        sig_e, n_e = boyut_sigmalari(self.g, ('X',), self.gunler, {'X': self.cg}, P)
        self.assertEqual((n, n_e), (1, 0))
        h = har_sigma(self.g.barlar['X'], self.gunler, self.cg.gun_gecerli, _takvim(), P)
        self.assertAlmostEqual(sig_h[0], max(h, P.sigma_taban), places=12)
        self.assertAlmostEqual(sig_e[0], max(self.cg.sigma_ewma, P.sigma_taban), places=12)
        with self.assertRaises(HedefHatasi):
            boyut_sigmalari(self.g, ('X',), self.gunler, {'X': self.cg}, replace(P, sigma_tahmincisi='HAR'))


class KosuTest(unittest.TestCase):
    def test_har_kosusu_farkli_ewma_kosusu_ayni(self):
        tar = {c: CoinTarifi(saatlik_vol=0.006 + 0.001 * i, gunluk_suruklenme=0.004, saatlik_hacim=5e6)
               for i, c in enumerate(('BTCUSDT', 'ETHUSDT', 'A1', 'A2'))}
        veri = tam_veri_uret(tar, 100)
        ayar = KosuAyarlari(t0_ms=gun_ms(92), t_son_ms=saat_ms(100 * 24 - 1))
        e1 = kos(veri, ayar, P)
        e2 = kos(veri, ayar, replace(P, sigma_tahmincisi='EWMA'))
        self.assertEqual(e1.gunluk.son_hash, e2.gunluk.son_hash)
        tk = HarTakvimi(aylar=((gun_ms(90), BETA),), s2=((gun_ms(90), 0.8),))
        h = kos(veri, ayar, replace(P, sigma_tahmincisi='HAR', har_takvimi=tk))
        self.assertNotEqual(h.gunluk.son_hash, e1.gunluk.son_hash)
        self.assertTrue(all(k.hedef.tanilar.get('har_sigma_sayisi', 0) > 0 for k in h.kararlar))
        self.assertTrue(np.all(np.isfinite(h.nav)))


if __name__ == '__main__':
    unittest.main()
