"""Anonim coin kimliği (banka_kos/anonim.py; BANKA §8.1 K1-16)."""
import hashlib
import hmac
import shutil
import sys as _sys
import tempfile
import unittest
from pathlib import Path as _Path

V8_DIR = _Path(__file__).resolve().parent.parent
if str(V8_DIR) not in _sys.path:
    _sys.path.insert(1, str(V8_DIR))

from banka_kos import anonim  # noqa: E402


class AnonimTest(unittest.TestCase):
    def test_hmac_sirasi_ve_adli(self):
        a = bytes(range(32))
        s = ['XUSDT', 'YUSDT', 'ZUSDT', 'BTCUSDT', 'ETHUSDT']
        k = anonim.kimlikler(a, s)
        self.assertEqual(k['BTCUSDT'], 'BTCUSDT')
        self.assertEqual(k['ETHUSDT'], 'ETHUSDT')
        sira = sorted(['XUSDT', 'YUSDT', 'ZUSDT'], key=lambda x: hmac.new(a, x.encode(), hashlib.sha256).hexdigest())
        self.assertEqual([k[x] for x in sira], ['C001', 'C002', 'C003'])
        self.assertEqual(anonim.kimlikler(a, list(reversed(s))), k)            # girdi sirasindan bagimsiz

    def test_anahtar_tek_sefer(self):
        d = _Path(tempfile.mkdtemp(prefix='anonim_'))
        try:
            h = anonim.anahtar_uret(d / 'k.bin')
            self.assertEqual(h, hashlib.sha256((d / 'k.bin').read_bytes()).hexdigest())
            with self.assertRaises(FileExistsError):
                anonim.anahtar_uret(d / 'k.bin')
            with self.assertRaises(ValueError):
                anonim.kimlikler(b'kisa', ['XUSDT'])
        finally:
            shutil.rmtree(d, ignore_errors=True)


if __name__ == '__main__':
    unittest.main()
