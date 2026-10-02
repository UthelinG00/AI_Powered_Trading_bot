"""age v1 X25519 şifreleme (banka_kos/age.py; BANKA §2.4, BK-2): Bech32 (BIP-173 vektörleri), anahtar metinleri,
parça sınırlarında gidiş-dönüş, kurcalama ve yanlış kimlik. Resmi age aracıyla uyum dondurmadan önce kullanıcının
anahtarıyla ayrıca doğrulanır (ILERLEME_BANKA 6.10)."""
import sys as _sys
import unittest
from pathlib import Path as _Path

V8_DIR = _Path(__file__).resolve().parent.parent
if str(V8_DIR) not in _sys.path:
    _sys.path.insert(1, str(V8_DIR))

from banka_kos import age  # noqa: E402

BIP173_GECERLI = ('A12UEL5L', 'a12uel5l', 'abcdef1qpzry9x8gf2tvdw0s3jn54khce6mua7lmqqqxw',
                  'split1checkupstagehandshakeupstreamerranterredcaperred2y9e3w', '?1ezyfcl')


class Bech32Test(unittest.TestCase):
    def test_bip173_saglama(self):
        for s in BIP173_GECERLI:
            low = s.lower()
            hrp, veri = low[:low.rfind('1')], low[low.rfind('1') + 1:]
            d = [age._ALFABE.index(x) for x in veri]
            self.assertEqual(age._polymod(age._hrp_genislet(hrp) + d), 1, s)

    def test_gidis_donus_ve_bozuk(self):
        for n in (0, 1, 20, 32):
            b = bytes(range(n))
            s = age.bech32_kodla('age', b)
            self.assertEqual(age.bech32_coz(s), ('age', b))
        s = age.bech32_kodla('age', bytes(32))
        bozuk = s[:-1] + ('q' if s[-1] != 'q' else 'p')
        with self.assertRaises(age.AgeHatasi):
            age.bech32_coz(bozuk)
        with self.assertRaises(age.AgeHatasi):
            age.bech32_coz(s[:5] + s[5:].upper())


class AnahtarTest(unittest.TestCase):
    def test_metinler(self):
        kimlik, alici = age.anahtar_uret()
        self.assertTrue(kimlik.startswith('AGE-SECRET-KEY-1'))
        self.assertTrue(alici.startswith('age1'))
        self.assertEqual(len(age.alici_coz(alici)), 32)
        self.assertEqual(len(age.kimlik_coz('# yorum\n' + kimlik + '\n')), 32)


class SifrelemeTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.kimlik, cls.alici = age.anahtar_uret()

    def test_gidis_donus_parca_sinirlari(self):
        for n in (0, 1, age.PARCA - 1, age.PARCA, age.PARCA + 1, 3 * age.PARCA, 200_000):
            duz = bytes((i * 7 + 3) % 256 for i in range(n))
            sifreli = age.sifrele(self.alici, duz)
            self.assertTrue(sifreli.startswith(b'age-encryption.org/v1\n-> X25519 '))
            self.assertEqual(age.coz(self.kimlik, sifreli), duz, n)

    def test_her_sifreleme_farkli(self):
        self.assertNotEqual(age.sifrele(self.alici, b'x'), age.sifrele(self.alici, b'x'))

    def test_kurcalama(self):
        s = bytearray(age.sifrele(self.alici, b'gizli sonuc' * 100))
        s[-5] ^= 1                                            # yük
        with self.assertRaises(Exception):
            age.coz(self.kimlik, bytes(s))
        t = age.sifrele(self.alici, b'gizli')
        i = t.index(b'--- ') + 6
        t2 = t[:i] + (b'A' if t[i:i + 1] != b'A' else b'B') + t[i + 1:]  # MAC
        with self.assertRaises(age.AgeHatasi):
            age.coz(self.kimlik, t2)

    def test_yanlis_kimlik(self):
        baska, _ = age.anahtar_uret()
        with self.assertRaises(age.AgeHatasi):
            age.coz(baska, age.sifrele(self.alici, b'gizli'))

    def test_yuk_kesilmesi(self):
        s = age.sifrele(self.alici, bytes(3 * age.PARCA))
        with self.assertRaises(Exception):
            age.coz(self.kimlik, s[:-(age.PARCA + 16)])       # son parça atıldı: önceki parça "son" değil


class KatiBicimTest(unittest.TestCase):
    """Codex T16: çözücü biçim dışı dosyaları reddeder."""

    @classmethod
    def setUpClass(cls):
        cls.kimlik, cls.alici = age.anahtar_uret()
        cls.s = age.sifrele(cls.alici, b'veri')

    def _satirlar(self):
        i = self.s.index(b'--- ')
        j = self.s.index(b'\n', i)
        return self.s[:j].split(b'\n'), self.s[j:]

    def test_kanonik_olmayan_b64(self):
        sat, kalan = self._satirlar()
        govde = sat[2]                                                   # 43 karakter: son karakterde 2 kullanılmayan bit
        alfabe = b'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/'
        v = alfabe.index(govde[-1:])
        bozuk = govde[:-1] + alfabe[v ^ 1:(v ^ 1) + 1]                    # yalnız kullanılmayan en düşük biti değiştir
        with self.assertRaises(age.AgeHatasi):
            age.coz(self.kimlik, b'\n'.join(sat[:2] + [bozuk] + sat[3:]) + kalan)

    def test_uzun_govde_satiri(self):
        sat, kalan = self._satirlar()
        with self.assertRaises(age.AgeHatasi):
            age.coz(self.kimlik, b'\n'.join(sat[:2] + [sat[2] + b'A' * 30] + sat[3:]) + kalan)

    def test_x25519_arguman_ve_mac_satiri(self):
        sat, kalan = self._satirlar()
        with self.assertRaises(age.AgeHatasi):
            age.coz(self.kimlik, b'\n'.join(sat[:1] + [sat[1] + b' fazla'] + sat[2:]) + kalan)
        with self.assertRaises(age.AgeHatasi):
            age.coz(self.kimlik, b'\n'.join(sat[:-1] + [sat[-1] + b'A']) + kalan)
        self.assertEqual(age.coz(self.kimlik, self.s), b'veri')


if __name__ == '__main__':
    unittest.main()
