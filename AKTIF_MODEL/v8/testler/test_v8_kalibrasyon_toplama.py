"""Kalibrasyon toplamasi (kalibrasyon/toplama.py): B7 kuantil tanimi, Duzey 2 satiri, 2-a tarama kurali ve Wilson,
2-b taban olcutleri, R16 tablosu; sahte birim dosyalariyla uctan uca Duzey 1 ve Duzey 2 toplamasi."""
import math
import shutil
import sys as _sys
import tempfile
import unittest
from pathlib import Path as _Path

import numpy as np

V8_DIR = _Path(__file__).resolve().parent.parent
if str(V8_DIR) not in _sys.path:
    _sys.path.insert(1, str(V8_DIR))

from kalibrasyon import birim as B  # noqa: E402
from kalibrasyon import toplama as T  # noqa: E402
from kalibrasyon.duzey1 import SR_IZGARASI  # noqa: E402
from kalibrasyon.duzey1_esik import IX, Kurallar  # noqa: E402
from kalibrasyon.duzey1_olcut import ALANLAR, SEYRELTME  # noqa: E402
from kalibrasyon.kosucu import cikarma_turet, duzey1_listesi, duzey2_listesi  # noqa: E402

KIM = {'kod': 'k', 'motor': 'm', 'parametre': 'p', 'ortam': 'o'}
K = Kurallar(N=327, sigma_sr=0.30, b2_bagli=False, d=0.5, b3_esik=0.30, b4_esik=0.30, e_b5=0.5, k_b6=2, e_b10=0.3)


def birincil(sr=1.0, iyi=True, alt=range(3, 20)):
    return {'sr': sr, 'sr_gunluk': sr / math.sqrt(365), 'g3': 0.0, 'g4': 3.0, 'eta': 1.0, 'T': 1168,
            'b4_sr': 1.0 if iyi else 0.1, 'b5_pay': 0.2, 'dilim_sr': [1.0, 1.0, -1.0, float('nan')],
            'b8_sr': 1.0, 'b11_mdd': 0.1, 'alt_katki_no': list(alt)}


class SafTest(unittest.TestCase):
    def test_b7_kuantil(self):
        nulls = np.arange(1.0, 51.0)
        self.assertTrue(T.b7_gecer(48.5, nulls, 0.95))          # ceil(47,5) = 48'inci deger = 48
        self.assertFalse(T.b7_gecer(48.0, nulls, 0.95))
        self.assertTrue(T.b7_gecer(45.5, nulls, 0.90))
        self.assertFalse(T.b7_gecer(float('nan'), nulls, 0.90))
        self.assertTrue(T.b7_gecer(476.0, np.arange(1.0, 501.0), 0.95))      # n = 500 -> 475'inci
        self.assertFalse(T.b7_gecer(475.0, np.arange(1.0, 501.0), 0.95))

    def test_satir(self):
        r = T.duzey2_satiri(birincil(), 0.5, 0.2, [0.9, 0.7])
        self.assertEqual(r[IX['b6']], 2.0)
        self.assertAlmostEqual(r[IX['b10']], 0.3)
        self.assertEqual((r[IX['b3_2']], r[IX['b9']]), (0.5, 1.0))
        self.assertTrue(np.isnan(T.duzey2_satiri(birincil())[IX['b3_2']]))

    def test_2a_tarama(self):
        iyi = T.duzey2_satiri(birincil(), 0.5, 0.2, [0.9])
        kotu = T.duzey2_satiri(birincil(iyi=False), 0.5, 0.2, [0.9])
        for kabul_sayisi, beklenen in ((5, True), (6, False)):
            satir = np.array([iyi] * kabul_sayisi + [kotu] * (100 - kabul_sayisi))
            oz = T.duzey2a_ozeti(satir, K)
            self.assertEqual((oz['kabul'], oz['tarama_gecti']), (kabul_sayisi, beklenen))
        self.assertAlmostEqual(T.duzey2a_ozeti(np.array([iyi] * 5 + [kotu] * 95), K)['wilson_ust'], 0.1118, places=4)

    def test_2b_taban_b3_b10_etkisiz(self):
        yollar = [(birincil(sr=60.0), list(np.arange(1.0, 51.0)), 9, 10)] * 3 + \
                 [(birincil(sr=10.0), list(np.arange(1.0, 51.0)), 9, 10)]
        oz = T.duzey2b_ozeti(yollar, K)
        self.assertEqual(oz['n'], 4)
        self.assertEqual(oz['b7_q95'][0], 0.75)
        self.assertEqual(oz['taban_ve_b7_q95'][0], 0.75)           # B3/B10 kosusu olmadan taban gecer
        self.assertAlmostEqual(oz['ortak_pay'], 0.9)

    def test_r16(self):
        t = T.r16_tablosu(323)
        s30 = [x for x in t if x['sigma_sr'] == 0.30 and x['T_yil'] == 3.0][0]
        self.assertAlmostEqual(s30['sr0_yillik'], 0.88, delta=0.01)
        self.assertAlmostEqual(s30['gereken_sr']['0.5'], s30['sr0_yillik'])


class DosyaTest(unittest.TestCase):
    def setUp(self):
        self.d = _Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.d, True)

    def test_duzey1_topla(self):
        rng = np.random.default_rng(1)
        n = 40
        for k in duzey1_listesi(n):
            a = np.zeros((n, len(SR_IZGARASI), len(ALANLAR)))
            for ad, v in dict(b3_2=1.0, b3_3=1.0, b4=1.0, b6=4, b8=1.0, b9=1.0, b11=0.1, g3=0.0, g4=3.0, eta=1.0,
                              T=1277.0, sr_gunluk=-0.1).items():
                a[:, :, IX[ad]] = v
            a[:, :, IX['b5']] = rng.uniform(0.1, 0.3, (n, 1))
            a[:, :, IX['b10']] = rng.uniform(0.0, 0.1, (n, 1))
            a[:, 0, IX['b8']] = -1.0                              # SR = 0'da hicbiri gecmez
            s = np.repeat(a[:, :, None, :], len(SEYRELTME), axis=2)
            B.sonuc_yaz(self.d, k, {'n_yol': n}, KIM, diziler={'olcut': a, 'seyreltme': s})
        kayit = self.d / 'kayit.csv'
        kayit.write_text('registry_id,phase,family,trial_count,included_primary_dsr,note\na,1,x,159,yes,n\n')
        defter = self.d / 'defter.csv'
        defter.write_text('kayit_id,asama,tarih_utc,tur,kapsam,aile,varyant_sayisi,aciklama\na,,,,,,0,\nb,,,,,,144,\n')
        sonuc = T.duzey1_topla(self.d, KIM, n, kayit, defter)
        self.assertEqual(sonuc['durum'], 'TAMAM')
        self.assertEqual(sonuc['rapor']['N'], 159 + 145)
        self.assertEqual(sonuc['rapor']['sigma_sr']['sigma_sr_bag'], 0.30)
        self.assertEqual(sonuc['kurallar'].k_b6, 3)
        self.assertEqual(len(sonuc['rapor']['seyreltme']), len(SEYRELTME))
        self.assertEqual(sonuc['rapor']['p_kabul_A_ort'][0], 0.0)

    def test_duzey2_topla(self):
        for k in duzey2_listesi():
            if k['tur'] == 'birincil':
                iyi = not (k['ayar_no'] == 0 and k['mimari'] == 'B' and k['yol_no'] <= 6)
                g = birincil(sr=60.0 if k['ayar_no'] > 0 else 1.0, iyi=iyi)
                yol = B.sonuc_yaz(self.d, k, g, KIM)
                if k['ayar_no'] == 0:
                    import json
                    sha = json.loads(yol.read_text())['govde_sha256']
                    for c in cikarma_turet(k, g, sha):
                        B.sonuc_yaz(self.d, c, {'sr': 0.9}, KIM)
            elif k['tur'] in ('x2', 'x3'):
                B.sonuc_yaz(self.d, k, {'sr': 0.5}, KIM)
            else:
                B.sonuc_yaz(self.d, k, {'sr': float(k['null_no']), 'ortak': 9, 'toplam': 10}, KIM)
        s = T.duzey2_topla(self.d, KIM, K)
        # A: 100 yolun hepsi gecer (sahte): p = 1 -> tarama kalir; B'de 6 kotu yol.
        self.assertEqual(s['duzey2a']['A']['kabul'], 100)
        self.assertEqual(s['duzey2a']['B']['kabul'], 94)
        self.assertEqual(s['durum'], 'KILIT_BEKLER')
        self.assertEqual(s['duzey2b'][1]['b7_q95'][0], 1.0)            # SR 60 > 48'inci null (48)
        self.assertEqual(s['duzey2b'][0]['b7_q95'][0], 0.0)


if __name__ == '__main__':
    unittest.main()
