"""Banka koşucusu (banka_kos/kosucu.py; BANKA §2.4, BK-1/2/3/6): sahte yürütücüyle. Şifreli sonuç, açık kayıtta
performans ve coin adı yok, devam, B10 yeniden türetmesi, deterministiklik denetimi, mühürlü hata, damga.
Hata enjeksiyonu (Codex T17-b): şifreleme/yazım hatasında, devamdaki yeniden yürütmede ve işçi başlatmada da dışarı düz
iz ve özgün bağlam çıkmaz."""
import hashlib
import json
import os
import shutil
import sys as _sys
import tempfile
import traceback
import unittest
from pathlib import Path as _Path

V8_DIR = _Path(__file__).resolve().parent.parent
if str(V8_DIR) not in _sys.path:
    _sys.path.insert(1, str(V8_DIR))

from banka_kos import age, ayar  # noqa: E402
from banka_kos import kosucu as K  # noqa: E402

GIZLI_COINLER = [f'ZZGIZLI{i:02d}' for i in range(12)]


def sahte_bag():
    return {'bag': True}


def sahte_yurut(b, bag):
    if b['grup'] == 'hata':
        raise ValueError('NAV <= 0: 123.456')
    x = int(hashlib.sha256(K.kanonik(b)).hexdigest()[:8], 16) / 2 ** 32
    duz = {'birim': b, 'sr_gizli': x}
    if b['grup'] == 'birincil':
        duz['olcum'] = {'alt_katki_sirasi': GIZLI_COINLER}
    return duz, {'muhasebe': {'coin_pnl_hata': 0.0}}


GIZLI = 'NAV 987.654 ZZGIZLI99'


def hatali_yurut(b, bag):
    raise ValueError(GIZLI)


def birincil_hatali_yurut(b, bag):
    if b['grup'] == 'birincil':
        raise ValueError(GIZLI)
    return sahte_yurut(b, bag)


def hatali_bag():
    raise RuntimeError(GIZLI)


def rastgele_yurut(b, bag):
    duz, acik = sahte_yurut(b, bag)
    duz['gurultu'] = os.urandom(8).hex()
    return duz, acik


def _birimler():
    return [ayar._birim('birincil', 'A'), ayar._birim('izgara', 'A', nav0=1e6, maliyet_k=2.0),
            ayar._birim('null', 'A', null_no=1), ayar._birim('null', 'A', null_no=2)]


class KosucuTest(unittest.TestCase):
    def setUp(self):
        self.d = _Path(tempfile.mkdtemp(prefix='banka_kosucu_'))
        self.kimlik, self.alici = age.anahtar_uret()

    def tearDown(self):
        shutil.rmtree(self.d, ignore_errors=True)

    def _kos(self, **k):
        return K.calistir(self.d, _birimler(), {'motor': 'm'}, self.alici, k.pop('yurut', sahte_yurut), sahte_bag,
                          sessiz=True, **k)

    def test_tam_kosu_sifreli_ve_damga(self):
        s = self._kos(isci=2)
        self.assertEqual((s['bitmis'], s['kalan']), (14, 0))
        acik = ''.join(p.read_text(encoding='ascii') for p in (self.d / 'denetim').rglob('*.json'))
        self.assertNotIn('sr_gizli', acik)
        self.assertFalse(any(c in acik for c in GIZLI_COINLER))                 # B10 opak (BK-6)
        k = K.kayit_oku(self.d, 'birincil_A')
        duz = age.coz(self.kimlik, (self.d / 'sonuc' / 'birim' / 'birincil_A.age').read_bytes())
        self.assertEqual(hashlib.sha256(duz).hexdigest(), k['duz_sha256'])
        self.assertEqual(json.loads(duz)['olcum']['alt_katki_sirasi'], GIZLI_COINLER)
        c1 = age.coz(self.kimlik, (self.d / 'sonuc' / 'birim' / 'cikarma_A_s01.age').read_bytes())
        self.assertEqual(json.loads(c1)['birim']['cikan'], GIZLI_COINLER[0])    # coin yalnız şifreli içerikte
        dm = K.damga_yaz(self.d, _birimler())
        self.assertEqual(dm['birim_sayisi'], 14)
        self.assertEqual(dm['kok_sha256'], K.sha(K.kanonik(dm['birimler'])))

    def test_devam_ve_b10_yeniden_turetme(self):
        s1 = self._kos(max_birim=1)
        self.assertEqual(s1['bu_kosuda'], 1)
        self.assertTrue(K.bitmis_mi(self.d, 'birincil_A'))
        s2 = self._kos()
        self.assertEqual((s2['bitmis'], s2['kalan'], s2['bu_kosuda']), (14, 0, 13))
        self.assertEqual(self._kos()['bu_kosuda'], 0)

    def test_deterministik_olmayan_birincil_yakalanir(self):
        self._kos(max_birim=1, yurut=rastgele_yurut)
        with self.assertRaises(K.BankaKosuHatasi):
            self._kos(yurut=rastgele_yurut)

    def test_is_listesi_degisemez(self):
        self._kos(max_birim=1)
        with self.assertRaises(K.BankaKosuHatasi):
            K.calistir(self.d, _birimler()[:3], {'motor': 'm'}, self.alici, sahte_yurut, sahte_bag, sessiz=True)

    def test_hata_muhurlenir(self):
        b = _birimler() + [ayar._birim('hata', 'A')]
        with self.assertRaises(K.BankaKosuHatasi) as h:
            K.calistir(self.d, b, {'motor': 'm'}, self.alici, sahte_yurut, sahte_bag, sessiz=True)
        self.assertNotIn('123.456', str(h.exception))
        iz = age.coz(self.kimlik, (self.d / 'sonuc' / 'hata' / 'hata_A.age').read_bytes())
        self.assertIn(b'123.456', iz)
        self.assertIn(hashlib.sha256(iz).hexdigest(), str(h.exception))
        self._sizinti_yok(h.exception, '123.456')                              # işçinin uzak izi de bastırılır

    def _sizinti_yok(self, exc, gizli=GIZLI):
        self.assertIsInstance(exc, K.BankaKosuHatasi)
        self.assertIsNone(exc.__cause__)
        self.assertTrue(exc.__suppress_context__)
        self.assertNotIn(gizli, ''.join(traceback.format_exception(exc)))

    def test_sifreleme_hatasi_baglami_acmaz(self):
        with self.assertRaises(K.BankaKosuHatasi) as h:                        # alıcı bozuk: mühürleme de başarısız
            K.birim_hesapla(ayar._birim('birincil', 'A'), None, hatali_yurut, {}, 'age1bozuk', str(self.d))
        self.assertIn('hata dosyasi yazilamadi', str(h.exception))
        self._sizinti_yok(h.exception)
        self.assertFalse((self.d / 'sonuc' / 'hata').exists())

    def test_yazim_hatasi_baglami_acmaz(self):
        (self.d / 'sonuc').write_bytes(b'')                                    # klasör yerine dosya: her yazım düşer
        for yurut in (hatali_yurut, lambda b, bag: ({'gizli': GIZLI}, {})):   # yürütme hatası; başarılı sonucun yazımı
            with self.assertRaises(K.BankaKosuHatasi) as h:
                K.birim_hesapla(ayar._birim('birincil', 'A'), None, yurut, {}, self.alici, str(self.d))
            self.assertIn('hata dosyasi yazilamadi', str(h.exception))
            self._sizinti_yok(h.exception)

    def test_devamda_yeniden_yurutme_muhurlenir(self):
        self._kos(max_birim=1)
        with self.assertRaises(K.BankaKosuHatasi) as h:
            self._kos(yurut=birincil_hatali_yurut)
        self.assertIn('birincil yeniden yurutulemedi', str(h.exception))
        self._sizinti_yok(h.exception)
        iz = age.coz(self.kimlik, (self.d / 'sonuc' / 'hata' / 'yeniden_birincil_A.age').read_bytes())
        self.assertIn(GIZLI.encode(), iz)
        self.assertIn(hashlib.sha256(iz).hexdigest(), str(h.exception))
        (self.d / 'sonuc' / 'hata' / 'yeniden_birincil_A.age').unlink()       # mühürleme de düşerse
        (self.d / 'sonuc' / 'hata').rmdir()
        (self.d / 'sonuc' / 'hata').write_bytes(b'')
        with self.assertRaises(K.BankaKosuHatasi) as h:
            self._kos(yurut=birincil_hatali_yurut)
        self.assertIn('hata dosyasi yazilamadi', str(h.exception))
        self._sizinti_yok(h.exception)

    def test_isci_baslatma_hatasi_muhurlenir(self):
        with self.assertRaises(K.BankaKosuHatasi) as h:
            K.calistir(self.d, _birimler(), {'motor': 'm'}, self.alici, sahte_yurut, hatali_bag, sessiz=True)
        self.assertIn('isci baslatilamadi', str(h.exception))
        self._sizinti_yok(h.exception)
        dosyalar = sorted((self.d / 'sonuc' / 'hata').glob('isci_baslat_*.age'))
        self.assertTrue(dosyalar)
        self.assertIn(GIZLI.encode(), age.coz(self.kimlik, dosyalar[0].read_bytes()))

    def test_devamda_baglam_hatasi_muhurlenir(self):
        self._kos(max_birim=1)
        with self.assertRaises(K.BankaKosuHatasi) as h:                        # BK-6 yolu ana süreçte bağlam kurar
            K.calistir(self.d, _birimler(), {'motor': 'm'}, self.alici, sahte_yurut, hatali_bag, sessiz=True)
        self.assertIn('birincil yeniden yurutulemedi', str(h.exception))
        self._sizinti_yok(h.exception)


if __name__ == '__main__':
    unittest.main()
