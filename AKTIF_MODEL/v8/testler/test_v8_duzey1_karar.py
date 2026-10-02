"""sigma_SR_bag betigi (kalibrasyon/sigma_sr.py; yalniz gecici sentetik CSV'ler) ve Duzey 1 karar sirasi
(kalibrasyon/duzey1_karar.py; Ss3.3 kural 2-4, tek ayar, kilit bekler)."""
import atexit
import os
import sys as _sys
import tempfile
import unittest
from pathlib import Path as _Path

import numpy as np

V8_DIR = _Path(__file__).resolve().parent.parent
if str(V8_DIR) not in _sys.path:
    _sys.path.insert(1, str(V8_DIR))

from kalibrasyon import duzey1 as d1  # noqa: E402
from kalibrasyon.duzey1_esik import IX  # noqa: E402
from kalibrasyon.duzey1_karar import SR0_IX, duzey1_karari, n_v8  # noqa: E402
from kalibrasyon.duzey1_olcut import ALANLAR  # noqa: E402
from kalibrasyon.sigma_sr import SIGMA_VARSAYIM, VARSAYIM_CUMLESI, sigma_sr_bag  # noqa: E402

REF = d1.SR_IZGARASI.index(1.0)


def _yaz(metin):
    f = tempfile.NamedTemporaryFile('w', suffix='.csv', delete=False, encoding='utf-8', newline='')
    f.write(metin)
    f.close()
    atexit.register(os.unlink, f.name)
    return f.name


class SigmaSrTest(unittest.TestCase):
    def test_sayi_kaydi_varsayim(self):
        yol = _yaz('registry_id,phase,family,trial_count,included_primary_dsr,note\n'
                   'a,1,x,100,yes,n\nb,2,y,59,yes,n\n')
        s = sigma_sr_bag(yol)
        self.assertEqual((s['sigma_sr_bag'], s['kaynak'], s['cumle']), (SIGMA_VARSAYIM, 'varsayim', VARSAYIM_CUMLESI))
        self.assertEqual(s['trial_count_toplami'], 159)
        self.assertIn('sharpe', s['gerekce'])

    def test_sharpe_sutunlu_kayit_incelemesiz_okunmaz(self):
        yol = _yaz('deneme_id,sharpe_yillik,getiri_gun,siklik,teknik_hata\n1,0.1,400,gunluk,0\n')
        with self.assertRaises(NotImplementedError):
            sigma_sr_bag(yol)

    def test_n_v8(self):
        yol = _yaz('kayit_id,asama,tarih_utc,tur,kapsam,aile,varyant_sayisi,aciklama\n'
                   'a,,,,,,0,\nb,,,,,,144,\nc,,,,,,5,\nd,,,,,,,\n')
        self.assertEqual(n_v8(yol), 1 + 144 + 5 + 1)


def _sonuclar(n_ayar=3, n=200, gecen_sr0=0.10, gecen_ayarla=0.03, b2_guclu=False):
    """SR = 0'da yollarin gecen_sr0 kadari butun olcutleri gecer; bunlarin (gecen_sr0 - gecen_ayarla) kadari B4'u
    0,35 ile gecer (0,40 ayarinda kalir). SR >= 0,3'te hepsi gecer."""
    out = {}
    for no in range(n_ayar):
        a = np.zeros((n, len(d1.SR_IZGARASI), len(ALANLAR)))
        for ad, v in dict(b3_2=1.0, b3_3=1.0, b4=1.0, b5=0.1, b6=4, b8=1.0, b9=1.0, b10=0.01, b11=0.1,
                          g3=0.0, g4=3.0, eta=1.0, T=1277.0).items():
            a[:, :, IX[ad]] = v
        a[:, :, IX['sr_gunluk']] = 0.2 if b2_guclu else -0.1
        k1, k2 = int(gecen_sr0 * n), int(gecen_ayarla * n)
        a[k1:, SR0_IX, IX['b8']] = -1.0                  # SR = 0: yalniz ilk k1 yol gecer
        a[k2:k1, SR0_IX, IX['b4']] = 0.35                 # bunlarin bir kismi 0,40 ayarinda kalir
        out[no] = a
    return out


class KararTest(unittest.TestCase):
    def test_dogrudan_tamam(self):
        k = duzey1_karari(_sonuclar(gecen_sr0=0.04), N=327, sigma_sr=0.30)
        self.assertEqual(k['durum'], 'TAMAM')
        self.assertFalse(k['kurallar'].b2_bagli)                   # B2 gucu < 0,25 -> rapor
        self.assertEqual(k['kurallar'].b4_esik, 0.30)

    def test_tek_ayar(self):
        k = duzey1_karari(_sonuclar(gecen_sr0=0.10, gecen_ayarla=0.03), N=327, sigma_sr=0.30)
        self.assertEqual(k['durum'], 'TAMAM')
        self.assertEqual((k['kurallar'].b3_esik, k['kurallar'].b4_esik), (0.40, 0.40))
        self.assertEqual([x['ayarli'] for x in k['denemeler']], [False, True])

    def test_kilit_bekler(self):
        k = duzey1_karari(_sonuclar(gecen_sr0=0.10, gecen_ayarla=0.10), N=327, sigma_sr=0.30)
        self.assertEqual(k['durum'], 'KILIT_BEKLER')
        self.assertIsNone(k['kurallar'])

    def test_b2_bagli_en_kucuk_d(self):
        k = duzey1_karari(_sonuclar(gecen_sr0=0.04, b2_guclu=True), N=327, sigma_sr=0.30)
        self.assertTrue(k['kurallar'].b2_bagli)
        self.assertEqual(k['kurallar'].d, 0.50)
        self.assertGreaterEqual(k['b2_guc_d050_sr1'], 0.25)


if __name__ == '__main__':
    unittest.main()
