"""Kalibrasyon kosucusu (kalibrasyon/kosucu.py): kesinti/devam, isci sayisi ve sira bagimsizligi, turetilen birimler,
bozuk dosyanin yeniden kosulmasi, is listesi degisikligi. Sahte hizli birimlerle (motor kosulmaz)."""
import hashlib
import shutil
import sys as _sys
import tempfile
import unittest
from pathlib import Path as _Path

V8_DIR = _Path(__file__).resolve().parent.parent
if str(V8_DIR) not in _sys.path:
    _sys.path.insert(1, str(V8_DIR))

from kalibrasyon import birim as B  # noqa: E402
from kalibrasyon import kosucu as K  # noqa: E402


def sahte_yurut(k):
    """Kimlikten belirlenimli govde; birincil birimler 'alt_katki_no' tasir."""
    h = int(hashlib.sha256(B.kanonik(k).encode()).hexdigest()[:8], 16)
    g = {'sr': (h % 1000) / 1000.0, 'x': h}
    if k['tur'] == 'birincil':
        g['alt_katki_no'] = [3 + (h + i) % 28 for i in range(12)]
    return g, None


def sahte_turet(k, govde, sha):
    if k['tur'] != 'birincil':
        return []
    return [{**{a: k[a] for a in ('duzey', 'ayar_no', 'yol_no', 'mimari')}, 'tur': 'cikarma', 'cikan': c,
             'birincil_sha': sha} for c in govde['alt_katki_no'][:3]]


BIRIMLER = [{'duzey': 2, 'ayar_no': 0, 'yol_no': y, 'mimari': m, 'tur': t}
            for y in (1, 2) for m in ('A', 'B') for t in ('birincil', 'x2')]


def kimlikler():
    return {'kod': B.kod_kimligi(), 'motor': B.motor_kimligi(), 'parametre': 'test', 'ortam': B.ortam_kimligi()}


def _dosyalar(d):
    return {p.name: p.read_bytes() for p in sorted(_Path(d).glob('d2_*.json'))}


class KosucuTest(unittest.TestCase):
    def setUp(self):
        self.d1, self.d2 = _Path(tempfile.mkdtemp()), _Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.d1, True)
        self.addCleanup(shutil.rmtree, self.d2, True)
        self.kim = kimlikler()

    def _kos(self, d, **kw):
        return K.calistir(d, BIRIMLER, self.kim, isci=kw.pop('isci', 2), yurut=sahte_yurut, turet=sahte_turet,
                          sessiz=True, **kw)

    def test_kesinti_devam_ve_sira_bagimsizligi(self):
        s = self._kos(self.d1, max_birim=3, isci=2)
        self.assertEqual(s['bu_kosuda'], 3)
        self.assertGreater(s['kalan'], 0)
        s = self._kos(self.d1, isci=3)
        self.assertEqual(s['kalan'], 0)
        self.assertEqual(s['bitmis'], len(BIRIMLER) + 4 * 3)            # 4 birincil x 3 turetilen
        self._kos(self.d2, isci=1, ters=True)
        a, b = _dosyalar(self.d1), _dosyalar(self.d2)
        self.assertEqual(set(a), set(b))
        self.assertEqual(a, b)                                           # bayt bayt ayni
        ek1 = sorted((self.d1 / K.EK_LISTE).read_text().splitlines())
        ek2 = sorted((self.d2 / K.EK_LISTE).read_text().splitlines())
        self.assertEqual(ek1, ek2)

    def test_bitmis_birim_atlanir_bozuk_yeniden(self):
        self._kos(self.d1)
        s = self._kos(self.d1)
        self.assertEqual((s['bu_kosuda'], s['kalan']), (0, 0))
        hedef = self.d1 / f"{B.birim_adi(BIRIMLER[1])}.json"
        hedef.write_text('{bozuk')
        s = self._kos(self.d1)
        self.assertEqual(s['bu_kosuda'], 1)
        self.assertTrue((self.d1 / B.KARANTINA).exists())

    def test_dur_dosyasi(self):
        (self.d1 / K.DUR).write_text('')
        s = self._kos(self.d1)
        self.assertEqual(s['bu_kosuda'], 0)
        (self.d1 / K.DUR).unlink()
        self.assertEqual(self._kos(self.d1)['kalan'], 0)

    def test_yarim_ek_satir_ve_gecici_dosya(self):
        self._kos(self.d1)
        with open(self.d1 / K.EK_LISTE, 'a', encoding='ascii') as f:
            f.write('{"duzey": 2, "ya')                        # kesintide yarim kalmis satir
        (self.d1 / 'd2_a000_y001_A_x2.json.gecici').write_text('yarim')
        s = self._kos(self.d1)
        self.assertEqual((s['bu_kosuda'], s['kalan']), (0, 0))
        kar = {p.name for p in (self.d1 / B.KARANTINA).iterdir()}
        self.assertIn(K.EK_LISTE + '.0', kar)
        self.assertIn('d2_a000_y001_A_x2.json.gecici.0', kar)
        satirlar = (self.d1 / K.EK_LISTE).read_text().splitlines()
        self.assertEqual(len(satirlar), 4 * 3)                   # dogrulanmis birincillerden yeniden kuruldu

    def test_is_listesi_gecicisi_ezilmez(self):
        self.d1.mkdir(exist_ok=True)
        (self.d1 / (K.IS_LISTESI + '.gecici')).write_text('onceki kesintiden')
        self._kos(self.d1, max_birim=1)
        self.assertTrue((self.d1 / B.KARANTINA / (K.IS_LISTESI + '.gecici.0')).exists())
        self.assertTrue((self.d1 / K.IS_LISTESI).exists())

    def test_liste_degisirse_red(self):
        self._kos(self.d1, max_birim=1)
        with self.assertRaises(K.KosucuHatasi):
            K.calistir(self.d1, BIRIMLER[:-1], self.kim, yurut=sahte_yurut, turet=sahte_turet, sessiz=True)
        with self.assertRaises(K.KosucuHatasi):
            K.calistir(self.d1, BIRIMLER, {**self.kim, 'parametre': 'baska'}, yurut=sahte_yurut, sessiz=True)

    def test_gercek_listeler(self):
        d2 = K.duzey2_listesi()
        self.assertEqual(sum(1 for k in d2 if k['ayar_no'] == 0 and k['tur'] != 'null'), 100 * 2 * 3)
        self.assertEqual(sum(1 for k in d2 if k['tur'] == 'null'), 5 * 10 * 50)
        self.assertEqual(sum(1 for k in d2 if k['ayar_no'] > 0 and k['tur'] == 'birincil'), 40)
        self.assertEqual(len(K.duzey1_listesi(2000)), 128)
        t = K.cikarma_turet({'duzey': 2, 'ayar_no': 0, 'yol_no': 5, 'mimari': 'B', 'tur': 'birincil'},
                            {'alt_katki_no': list(range(3, 20))}, 'ab')
        self.assertEqual([x['cikan'] for x in t], list(range(3, 13)))
        self.assertEqual(K.cikarma_turet({'duzey': 2, 'ayar_no': 2, 'yol_no': 5, 'mimari': 'A', 'tur': 'birincil'},
                                         {'alt_katki_no': [3]}, 'ab'), [])


if __name__ == '__main__':
    unittest.main()
