"""Carry kapisi kosu betigi (5.04; CARRY Ss7.2 kor hukum): sentetik carry senaryosunda uctan uca. Dosyalar, hash'ler,
denetim/hukum ayrimi, muhur, tek atis. D verisi kullanilmaz."""
import hashlib
import json
import shutil
import sys as _sys
import tempfile
import unittest
from dataclasses import replace
from datetime import datetime, timezone
from pathlib import Path as _Path

TESTLER_DIR = _Path(__file__).resolve().parent
V8_DIR = TESTLER_DIR.parent
for _dir in (V8_DIR, TESTLER_DIR):
    if str(_dir) not in _sys.path:
        _sys.path.insert(1, str(_dir))

from fikstur.saatlik_veri import CARRY_GUN, carry_senaryo_verisi, gun_ms  # noqa: E402
from kapi import kosu  # noqa: E402
from kapi import olcutler as olc  # noqa: E402
from kapi import seriler as sr  # noqa: E402
from motor.tipler import Parametreler  # noqa: E402


def _ms(y, a, g):
    return int(datetime(y, a, g, tzinfo=timezone.utc).timestamp() * 1000)


class KapiKosuTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.dizin = _Path(tempfile.mkdtemp(prefix='kapi_kosu_'))
        cls.tak = sr.Takvim(t0_ms=_ms(2023, 10, 1), hafta_bas_ms=_ms(2023, 10, 2), n_hafta=5,
                            ay_sinirlari=(_ms(2023, 10, 1), _ms(2023, 11, 1)))
        cls.p = replace(Parametreler(), mimari='B')
        cls.ozet = kosu.kapi_kos(carry_senaryo_verisi(), {'sentetik': True}, cls.dizin, p=cls.p,
                                 v1={'gecti': True}, bit_ms=gun_ms(CARRY_GUN), takvim=cls.tak, btc_adim=0.001)

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.dizin, ignore_errors=True)

    def test_dosyalar_ve_hashler(self):
        for ad, h in self.ozet['hash'].items():
            self.assertEqual(hashlib.sha256((self.dizin / ad).read_bytes()).hexdigest(), h)
        for ad in ('ana', 'mc2', 'mc3', 'delist50', 'delist90'):
            k = self.ozet['kosular'][ad]
            self.assertEqual(hashlib.sha256((self.dizin / 'muhur' / f'gunluk_{ad}.jsonl').read_bytes()).hexdigest(),
                             k['hash']['gunluk'])
        self.assertTrue((self.dizin / 'muhur' / 'trend_satirlari_ana.npz').exists())
        self.assertNotIn('k8', self.ozet['kosular'])                    # < 30 isim: kosulmaz (U-52)

    def test_denetim_ve_hukum(self):
        d = json.loads((self.dizin / 'DENETIM.json').read_text(encoding='utf-8'))
        h = json.loads((self.dizin / 'HUKUM.json').read_text(encoding='utf-8'))
        self.assertTrue(d['V']['V1'] and d['V']['V2'] and d['V']['V5'], d['V'])
        self.assertIn(h['karar'], ('A', 'B'))
        self.assertFalse(h['K']['K8']['gecti'])
        self.assertTrue(olc.hukum_trend_icermez(h))
        self.assertIn('kayit', h['betimsel'])
        self.assertNotIn('K', d)

    def test_tek_atis(self):
        with self.assertRaises(FileExistsError):
            kosu.kapi_kos(carry_senaryo_verisi(), {}, self.dizin, p=self.p, v1={'gecti': True},
                          bit_ms=gun_ms(CARRY_GUN), takvim=self.tak)


class OnKosulVeHataTest(unittest.TestCase):
    def test_v1_gecmeden_kosu_baslamaz(self):
        d = _Path(tempfile.mkdtemp(prefix='kapi_v1_'))
        try:
            with self.assertRaises(kosu.KapiKosuHatasi):
                kosu.kapi_kos(None, {}, d / 'c', p=replace(Parametreler(), mimari='B'), v1={'gecti': False})
            self.assertFalse((d / 'c').exists())
        finally:
            shutil.rmtree(d, ignore_errors=True)

    def test_hata_yolu_muhurlenir(self):
        d = _Path(tempfile.mkdtemp(prefix='kapi_hata_'))
        try:
            with self.assertRaises(kosu.KapiKosuHatasi) as h:
                kosu.kapi_kos(None, {}, d / 'c', p=replace(Parametreler(), mimari='B'), v1={'gecti': True})
            iz = (d / 'c' / 'muhur' / 'HATA.txt').read_bytes()
            self.assertIn(hashlib.sha256(iz).hexdigest(), str(h.exception))
            self.assertIsNone(h.exception.__cause__)
            self.assertTrue(h.exception.__suppress_context__)
        finally:
            shutil.rmtree(d, ignore_errors=True)

    def test_muhur_yazilamasa_da_baglam_bastirilir(self):
        # T16 CIDDI: HATA.txt yazımı başarısız olsa da özgün istisna dışarı çıkmaz.
        d = _Path(tempfile.mkdtemp(prefix='kapi_hata2_'))
        eski = _Path.write_bytes
        try:
            _Path.write_bytes = lambda self, b: (_ for _ in ()).throw(OSError('disk'))
            with self.assertRaises(kosu.KapiKosuHatasi) as h:
                kosu.kapi_kos(None, {}, d / 'c', p=replace(Parametreler(), mimari='B'), v1={'gecti': True})
            self.assertIn('yazilamadi', str(h.exception))
            self.assertTrue(h.exception.__suppress_context__)
        finally:
            _Path.write_bytes = eski
            shutil.rmtree(d, ignore_errors=True)


if __name__ == '__main__':
    unittest.main()
