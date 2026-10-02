"""B5 A birincil eşdeğerliği betiğinin (ciktilar/v8_b5_a_esdegerlik_20260930_01/b5_a_esdegerlik.py) kabul denetimi
(Codex T20): tam 140 benzersiz birim, her satır "aynı", zarf bütünlüğü, dondurulmuş kimlik/ortam/HAR, sabit güncel
kimlik. Motor koşulmaz."""
import importlib.util
import sys as _sys
import unittest
from pathlib import Path as _Path

TESTLER_DIR = _Path(__file__).resolve().parent
V8_DIR = TESTLER_DIR.parent
if str(V8_DIR) not in _sys.path:
    _sys.path.insert(1, str(V8_DIR))
BETIK = V8_DIR.parent / 'ciktilar' / 'v8_b5_a_esdegerlik_20260930_01' / 'b5_a_esdegerlik.py'

_spec = importlib.util.spec_from_file_location('b5_a_esdegerlik', BETIK)
E = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(E)

DORT = {'kod': 'k0', 'motor': 'm0', 'parametre': 'p0', 'ortam': 'python 3.12.14; numpy 2.5.1'}
DONDURMA = {'kimlikler': DORT, 'har_sonuc_sha256': 'h' * 64}
GUNCEL = {'kod': 'k1', 'motor': 'm1', 'parametre': 'p1', 'ortam': DORT['ortam'], 'har_sonuc_sha256': 'h' * 64}


def _birimler(n=140):
    return [{'duzey': 2, 'ayar_no': 0, 'yol_no': i, 'mimari': 'A', 'tur': 'birincil'} for i in range(1, n + 1)]


def _satirlar(birimler, **deg):
    return {E.B.birim_adi(k): dict({'ayni': True, 'zarf_butun': True, 'kimlikler': DORT}, **deg) for k in birimler}


class KabulTest(unittest.TestCase):
    def test_tam_ve_ayni_gecer(self):
        b = _birimler()
        d = E.kabul(b, _satirlar(b), DONDURMA, GUNCEL, True)
        self.assertTrue(d['gecti'], d)

    def test_ret_durumlari(self):
        b = _birimler()
        ad = E.B.birim_adi(b[5])
        self.assertFalse(E.kabul(b[:1], _satirlar(b[:1]), DONDURMA, GUNCEL, True)['birim_sayisi'])     # 1/1 geçmez
        self.assertFalse(E.kabul(b + b[:1], _satirlar(b), DONDURMA, GUNCEL, True)['birim_sayisi'])     # yinelenen
        s = _satirlar(b)
        del s[ad]
        self.assertFalse(E.kabul(b, s, DONDURMA, GUNCEL, True)['satir_tam'])
        for alan, deger, denetim in (('ayni', False, 'hepsi_ayni'), ('zarf_butun', False, 'zarflar_butun'),
                                     ('kimlikler', dict(DORT, motor='baska'), 'eski_kimlik_dondurma')):
            s = _satirlar(b)
            s[ad] = dict(s[ad], **{alan: deger})
            d = E.kabul(b, s, DONDURMA, GUNCEL, True)
            self.assertFalse(d[denetim])
            self.assertFalse(d['gecti'])
        self.assertFalse(E.kabul(b, _satirlar(b), DONDURMA, dict(GUNCEL, ortam='python 3.13'), True)['gecti'])
        self.assertFalse(E.kabul(b, _satirlar(b), DONDURMA, dict(GUNCEL, har_sonuc_sha256='x'), True)['gecti'])
        self.assertFalse(E.kabul(b, _satirlar(b), DONDURMA, GUNCEL, False)['gecti'])

    def test_zarf_butunlugu(self):
        k = _birimler(1)[0]
        govde = {'sr': 0.5, 'son_hash': 'a'}
        z = {'birim': k, 'kimlikler': DORT, 'govde': govde, 'govde_sha256': E.B.sha256_metin(E.B.kanonik(govde))}
        self.assertTrue(E.zarf_butun(z, k))
        self.assertFalse(E.zarf_butun(dict(z, govde=dict(govde, sr=0.6)), k))
        self.assertFalse(E.zarf_butun(z, dict(k, yol_no=2)))


if __name__ == '__main__':
    unittest.main()
