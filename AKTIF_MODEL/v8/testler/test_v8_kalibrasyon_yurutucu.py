"""Kalibrasyon yurutuculeri (kalibrasyon/yurutucu.py): Duzey 1 ayar birimi ve Duzey 2 birim turleri, kisa pencerede
(yalniz mekanik; performans olcumu degildir)."""
import sys as _sys
import unittest
from pathlib import Path as _Path

import numpy as np

V8_DIR = _Path(__file__).resolve().parent.parent
if str(V8_DIR) not in _sys.path:
    _sys.path.insert(1, str(V8_DIR))

from banka.degerlendirme import Pencere  # noqa: E402
from kalibrasyon import birim as b  # noqa: E402
from kalibrasyon import duzey2_uretec as u  # noqa: E402
from kalibrasyon import yurutucu as y  # noqa: E402
from kalibrasyon.duzey1 import SR_IZGARASI, yol_uret  # noqa: E402
from kalibrasyon.duzey1_olcut import ALANLAR, SEYRELTME, sr_olculeri  # noqa: E402

KISA = Pencere(bas_ms=u.pencere().bas_ms, dilim_gun=(3, 3, 3, 1))     # testlerde motor pencere basinda baslar


class Duzey1BirimTest(unittest.TestCase):
    def test_boyut_ve_icerik(self):
        g, d = y.duzey1_birimi(5, n_yol=3)
        self.assertEqual(d['olcut'].shape, (3, len(SR_IZGARASI), len(ALANLAR)))
        self.assertEqual(d['seyreltme'].shape, (3, len(SR_IZGARASI), len(SEYRELTME), len(ALANLAR)))
        a = sr_olculeri(yol_uret(5, 2), SR_IZGARASI[4])
        self.assertTrue(np.array_equal(d['olcut'][1, 4], np.array([a[k] for k in ALANLAR]), equal_nan=True))
        self.assertEqual(g['alanlar'], list(ALANLAR))


class Duzey2BirimTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.beta = y.har_beta()
        cls.k = {'duzey': 2, 'ayar_no': 0, 'yol_no': 1, 'mimari': 'A', 'tur': 'birincil'}
        cls.bir = y.duzey2_birimi(cls.k, cls.beta, KISA, KISA.bas_ms)

    def test_birincil(self):
        g = self.bir
        self.assertEqual(len(self.beta), 4)
        self.assertEqual(len(g['r']), 10)
        self.assertEqual(g['har_karar'], 10)
        self.assertGreater(g['s2_pazartesi'], 100)
        self.assertEqual(len(g['alt_katki_no']), len(g['alt_katki_sirasi']))
        self.assertTrue(all(3 <= n <= 30 for n in g['alt_katki_no']))
        self.assertEqual(b.kanonik(g), b.kanonik(y.duzey2_birimi(self.k, self.beta, KISA, KISA.bas_ms)))   # belirlenimli (nan dahil)

    def test_maliyet_ve_cikarma(self):
        x2 = y.duzey2_birimi({**self.k, 'tur': 'x2'}, self.beta, KISA, KISA.bas_ms)
        self.assertNotEqual(x2['son_hash'], self.bir['son_hash'])
        cik = y.duzey2_birimi({**self.k, 'tur': 'cikarma', 'cikan': 5}, self.beta, KISA, KISA.bas_ms)
        self.assertIn('sr', cik)
        self.assertEqual(len(cik['son_hash']), 64)

    def test_null(self):
        g = y.duzey2_birimi({**self.k, 'tur': 'null', 'null_no': 1}, self.beta, KISA, KISA.bas_ms)
        self.assertGreater(g['toplam'], 0)
        self.assertLessEqual(g['ortak'], g['toplam'])
        self.assertNotEqual(g['son_hash'], self.bir['son_hash'])


class VarsayilanBaslangicTest(unittest.TestCase):
    def test_motor_verinin_ilk_gunundan(self):
        """Codex T12-7: varsayilan kosu verinin ilk gunundan kesintisiz (365 isinma + 10 pencere gunu = 375 karar);
        olcutler yalniz pencereden."""
        k = {'duzey': 2, 'ayar_no': 0, 'yol_no': 1, 'mimari': 'A', 'tur': 'birincil'}
        g = y.duzey2_birimi(k, y.har_beta(), KISA)
        self.assertEqual(g['karar_sayisi'], u.ISINMA_GUN + KISA.gun_sayisi)
        self.assertEqual(len(g['r']), KISA.gun_sayisi)


if __name__ == '__main__':
    unittest.main()
