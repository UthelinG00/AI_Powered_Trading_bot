"""Banka veri denetimi T2 (banka_kos/veri_denetim.py; BANKA §2.3, §2.5; 6.11): üç T2 koşulu ayrı ayrı tetiklenir,
eşik sınırları, manifest son satır kuralı, rapor alanları ve kanonik hash. Sentetik carry senaryosu."""
import hashlib
import json
import shutil
import sys as _sys
import tempfile
import unittest
from dataclasses import replace
from pathlib import Path as _Path

import numpy as np

TESTLER_DIR = _Path(__file__).resolve().parent
V8_DIR = TESTLER_DIR.parent
for _dir in (V8_DIR, TESTLER_DIR):
    if str(_dir) not in _sys.path:
        _sys.path.insert(1, str(_dir))

from banka_kos import veri_denetim as VD  # noqa: E402
from fikstur.saatlik_veri import carry_senaryo_verisi, gun_ms  # noqa: E402
from motor.gorunum import SAAT_MS, saatlik_seri  # noqa: E402
from motor.tipler import Parametreler  # noqa: E402

HX, HY, HZ = 'a' * 64, 'b' * 64, 'c' * 64
MANIFEST = [{'yol': 'a.zip', 'sha256': HX, 'checksum': HX, 'durum': 'TAMAM'},
            {'yol': 'b.zip', 'sha256': HY, 'checksum': HY, 'durum': 'TAMAM'}]


def _delik(s, oran: float, bas: int, bit: int):
    """[bas, bit) içindeki saatlerin `oran`'ını düşürür."""
    ms = np.asarray(s.acilis_ms)
    ic = np.flatnonzero((ms >= bas) & (ms < bit))
    at = set(ic[:int(np.ceil(oran * len(ic)))].tolist())
    k = np.array([i not in at for i in range(len(ms))])
    return saatlik_seri(s.acilis_ms[k], s.acilis[k], s.yuksek[k], s.dusuk[k], s.kapanis[k], s.hacim[k])


class VeriDenetimTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.veri = carry_senaryo_verisi()
        cls.t0, cls.bson, cls.bit = gun_ms(92), gun_ms(120), gun_ms(130)
        cls.k = [c for c in sorted(cls.veri.barlar) if c not in ('BTCUSDT', 'ETHUSDT')][:10]
        cls.p = Parametreler()

    def den(self, veri=None, manifest=MANIFEST, k=None):
        return VD.denetle(veri or self.veri, manifest, self.k if k is None else k, self.t0, self.bson, self.bit, self.p,
                          filtresiz_sembol=3, sureklilik_sorunu=1, eylul_funding_kaynagi='arsiv 2026-09')

    def test_temiz_veri_t2_yok(self):
        d = self.den()
        self.assertFalse(d['karar']['T2'], d['karar'])
        self.assertEqual(d['btc_eksik_saat'], 0)
        self.assertEqual(d['k_veri_yok'], 0)
        self.assertEqual((d['filtresiz_sembol'], d['sureklilik_sorunu']), (3, 1))
        self.assertGreaterEqual(d['borsa_capi_bosluk_saati'], 0)
        self.assertEqual(d['checksum']['dosya'], 2)
        json.dumps(d)
        self.assertNotIn('A00', json.dumps(d))                                   # coin adı yok

    def test_checksum(self):
        # Netleştirme 17 a: bağlayıcı ilk hash, geçersiz satır, hata sınıfları.
        def cs(m):
            return VD.checksum_denetimi(m)
        m = MANIFEST + [{'yol': 'c.zip', 'sha256': HZ, 'checksum': HX, 'durum': 'TAMAM'}]              # uyuşmaz
        self.assertEqual(self.den(manifest=m)['karar']['nedenler'], ['onarilamayan CHECKSUM hatasi'])
        m = MANIFEST + [{'yol': 'b.zip', 'sha256': HZ, 'checksum': HY, 'durum': 'CHECKSUM_HATASI'},
                        {'yol': 'b.zip', 'sha256': HY, 'checksum': HY, 'durum': 'TAMAM'}]   # yeniden indirme onardı
        self.assertFalse(self.den(manifest=m)['karar']['T2'])
        self.assertEqual(cs(MANIFEST + [{'yol': 'b.zip', 'sha256': HZ, 'checksum': HZ, 'durum': 'TAMAM'}])
                         ['kimlik_degisti'], 1)                      # bağlayıcı ilk hash sonra başka eşleşen çiftle
        self.assertEqual(cs(MANIFEST + [{'yol': 'b.zip', 'sha256': HZ, 'checksum': HZ, 'durum': 'TAMAM'}])
                         ['onarilamayan'], 1)
        g = cs([{'yol': 'd.zip', 'sha256': None, 'checksum': None, 'durum': 'TAMAM'}])      # None == None geçmez
        self.assertEqual((g['gecersiz_satir'], g['onarilamayan']), (1, 1))
        g = cs(MANIFEST + [{'yol': 'e.zip', 'durum': 'INDIRME_HATASI'}, {'yol': 'f.zip', 'durum': 'YOK'}])
        self.assertEqual((g['indirme_hatasi'], g['yok'], g['onarilamayan']), (1, 1, 0))      # T2 değil (2)-(3) yakalar
        self.assertEqual(cs(MANIFEST + [{'yol': 'b.zip', 'sha256': HY, 'checksum': HY, 'durum': 'TAMAM'}])
                         ['kimlik_degisti'], 0)                      # aynı hash yeniden yazılabilir
        with self.assertRaises(ValueError):
            cs([{'yol': 'g.zip', 'durum': 'HATA'}])

    def test_eksik_funding(self):
        # Sentetik veri aralık saati taşımaz: seri kaydın gerçek aralığıyla kurulur; tek kayıt düşünce 1 boşluk.
        from motor.gorunum import funding_serisi
        c = sorted(self.veri.funding)[0]
        f = self.veri.funding[c]
        d = np.asarray(f.damga_ms)
        ara = float(np.median(np.diff(d))) / SAAT_MS
        tam = funding_serisi(d, np.asarray(f.oran), np.full(len(d), ara))
        ic = np.flatnonzero((d >= self.t0) & (d < self.bit))
        k = np.ones(len(d), dtype=bool)
        k[ic[5]] = False
        eksik = funding_serisi(d[k], np.asarray(f.oran)[k], np.full(int(k.sum()), ara))
        f0 = {c: tam}
        f1 = {c: eksik}
        self.assertEqual(VD.eksik_funding(replace(self.veri, funding=f0), self.t0, self.bit), 0)
        self.assertEqual(VD.eksik_funding(replace(self.veri, funding=f1), self.t0, self.bit), 1)
        self.assertEqual(VD.eksik_funding(self.veri, self.t0, self.bit), 0)              # aralık bilinmiyor: sayılmaz

    def test_btc_eth_eksik_esigi(self):
        for c in ('BTCUSDT', 'ETHUSDT'):
            az = dict(self.veri.barlar, **{c: _delik(self.veri.barlar[c], 0.008, self.t0, self.bson)})
            self.assertFalse(self.den(veri=replace(self.veri, barlar=az))['karar']['T2'], c)          # 6/672 saat = %0,9
            cok = dict(self.veri.barlar, **{c: _delik(self.veri.barlar[c], 0.02, self.t0, self.bson)})
            d = self.den(veri=replace(self.veri, barlar=cok))
            self.assertTrue(d['karar']['T2'])
            self.assertIn(f"{c[:3]} saatlerinin >%1i eksik", d['karar']['nedenler'])

    def test_k_veri_yok_esigi(self):
        bar = dict(self.veri.barlar)
        del bar[self.k[0]]
        self.assertFalse(self.den(veri=replace(self.veri, barlar=bar))['karar']['T2'])            # 1/10 = %10
        del bar[self.k[1]]
        d = self.den(veri=replace(self.veri, barlar=bar))                                          # 2/10 = %20
        self.assertEqual(d['karar']['nedenler'], ['K coinlerinin >%10unda veri yok'])

    def test_yaz_kanonik_hash(self):
        d = self.den()
        k = _Path(tempfile.mkdtemp(prefix='veri_denetim_'))
        try:
            h = VD.yaz(d, k / 'VERI_DENETIM.json')
            self.assertEqual(h, hashlib.sha256((k / 'VERI_DENETIM.json').read_bytes()).hexdigest())
            self.assertEqual(json.loads((k / 'VERI_DENETIM.json').read_text(encoding='ascii')), d)
        finally:
            shutil.rmtree(k, ignore_errors=True)


if __name__ == '__main__':
    unittest.main()
