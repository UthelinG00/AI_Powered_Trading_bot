"""Kalibrasyon is birimi (kalibrasyon/birim.py): kanonik zarf, atomik yazma, butunluk dogrulamasi, karantina,
motor kimliginin v8_calistir ile ayni tanimi."""
import importlib.util
import json
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

from kalibrasyon import birim as b  # noqa: E402

K = {'duzey': 2, 'ayar_no': 0, 'yol_no': 7, 'mimari': 'A', 'tur': 'birincil'}
KIM = {'kod': 'k', 'motor': 'm', 'parametre': 'p', 'ortam': 'o'}


class BirimTest(unittest.TestCase):
    def setUp(self):
        self.d = _Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.d, True)

    def test_ad(self):
        self.assertEqual(b.birim_adi(K), 'd2_a000_y007_A_birincil')
        self.assertEqual(b.birim_adi({**K, 'tur': 'null', 'null_no': 12}), 'd2_a000_y007_A_null_p012')
        self.assertEqual(b.birim_adi({**K, 'tur': 'cikarma', 'cikan': 7}), 'd2_a000_y007_A_cikarma_c07')
        self.assertEqual(b.birim_adi({'duzey': 1, 'ayar_no': 17, 'tur': 'ayar'}), 'd1_a017_ayar')

    def test_gidis_donus_ve_kanonik(self):
        govde = {'sr': 0.123456789012345678, 'x': [1.0, float('nan'), float('inf')], 'y': {'b': 1, 'a': 2}}
        yol = b.sonuc_yaz(self.d, K, govde, KIM)
        metin = yol.read_text(encoding='ascii')
        self.assertEqual(metin, b.kanonik(json.loads(metin)))
        g, _ = b.sonuc_oku(self.d, K, KIM)
        self.assertEqual(g['sr'], govde['sr'])
        self.assertTrue(math.isnan(g['x'][1]) and math.isinf(g['x'][2]))
        self.assertFalse(list(self.d.glob('*.gecici')))

    def test_yok_bozuk_ve_farkli_kimlik(self):
        self.assertIsNone(b.sonuc_oku(self.d, K, KIM))
        yol = b.sonuc_yaz(self.d, K, {'sr': 1.0}, KIM)
        zarf = json.loads(yol.read_text())
        zarf['govde']['sr'] = 2.0                                  # govde ozeti tutmaz
        yol.write_text(b.kanonik(zarf))
        self.assertIsNone(b.sonuc_oku(self.d, K, KIM))
        self.assertFalse(yol.exists())
        self.assertTrue((self.d / b.KARANTINA / (yol.name + '.0')).exists())
        b.sonuc_yaz(self.d, K, {'sr': 1.0}, KIM)
        self.assertIsNone(b.sonuc_oku(self.d, K, {**KIM, 'motor': 'baska'}))     # eski surum
        b.sonuc_yaz(self.d, K, {'sr': 1.0}, KIM)
        (self.d / (b.birim_adi(K) + '.json')).write_text('{yarim')
        self.assertIsNone(b.sonuc_oku(self.d, K, KIM))
        self.assertEqual(len(list((self.d / b.KARANTINA).iterdir())), 3)

    def test_npz(self):
        k1 = {'duzey': 1, 'ayar_no': 3, 'tur': 'ayar'}
        a = np.arange(12.0).reshape(3, 4)
        b.sonuc_yaz(self.d, k1, {'n': 3}, KIM, diziler={'olcut': a})
        g, dz = b.sonuc_oku(self.d, k1, KIM, npz=True)
        self.assertEqual(g, {'n': 3})
        self.assertTrue(np.array_equal(dz['olcut'], a))
        (self.d / (b.birim_adi(k1) + '.npz')).write_bytes(b'bozuk')
        self.assertIsNone(b.sonuc_oku(self.d, k1, KIM, npz=True))

    def test_zarfsiz_npz_karantina(self):
        k1 = {'duzey': 1, 'ayar_no': 9, 'tur': 'ayar'}
        (self.d / (b.birim_adi(k1) + '.npz')).write_bytes(b'yarim')
        self.assertIsNone(b.sonuc_oku(self.d, k1, KIM, npz=True))
        self.assertFalse((self.d / (b.birim_adi(k1) + '.npz')).exists())
        self.assertTrue((self.d / b.KARANTINA / (b.birim_adi(k1) + '.npz.0')).exists())

    def test_motor_kimligi_calistirici_ile_ayni(self):
        spec = importlib.util.spec_from_file_location('v8_calistir_m', V8_DIR / 'v8_calistir.py')
        m = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(m)
        self.assertEqual(b.motor_kimligi(), m._birlesik_sha256(m._tum_py_dosyalari(m.MOTOR_DIR)))
        self.assertEqual(len(b.kod_kimligi()), 64)
        self.assertIn('numpy', b.ortam_kimligi())


if __name__ == '__main__':
    unittest.main()
