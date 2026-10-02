"""v8 D verisi yukleyicisi (adaptor/veri_yukleyici.py): hash dogrulamasi, isle.py temizlik kurallari, funding
araligi, motor sozlesmesi. Sentetik zip + manifest fikstuuru; gercek D verisi okunmaz (yalniz git'te izlenen
GELISTIRME_EVRENI.json'un hash'i ve sembol listesi sinanir)."""
import hashlib
import io
import json
import shutil
import sys as _sys
import tempfile
import unittest
import zipfile
from pathlib import Path as _Path

import numpy as np

TESTLER_DIR = _Path(__file__).resolve().parent
V8_DIR = TESTLER_DIR.parent
for _dir in (V8_DIR, TESTLER_DIR):
    if str(_dir) not in _sys.path:
        _sys.path.insert(1, str(_dir))

from adaptor.veri_yukleyici import (BAS_MS, BIT_MS, VeriYuklemeHatasi, coin_yukle, gelistirme_evreni,  # noqa: E402
                                    manifest_tamam, tam_veri_yukle)

H = 3_600_000
KL_BASLIK = "open_time,open,high,low,close,volume,close_time,quote_volume,count,taker_buy_volume,taker_buy_quote_volume,ignore"
FU_BASLIK = "calc_time,funding_interval_hours,last_funding_rate"


def _kline_satir(t, p=10.0, qv=1000.0):
    return f"{t},{p},{p * 1.01},{p * 0.99},{p},1,{t + H - 1},{qv},5,0.5,{qv / 2},0"


class _GeciciVeri:
    """Gecici veri koku: ham/<tur>/<SYM>/*.zip ve MANIFEST.jsonl."""

    def __init__(self):
        self.kok = _Path(tempfile.mkdtemp(prefix='v8_veri_'))
        self.manifest = []

    def zip_yaz(self, tur, sym, ad, icerik: str, manifeste=True, sha=None):
        klasor = self.kok / 'ham' / tur / sym
        klasor.mkdir(parents=True, exist_ok=True)
        yol = klasor / ad
        b = io.BytesIO()
        with zipfile.ZipFile(b, 'w') as zf:
            zf.writestr(ad.replace('.zip', '.csv'), icerik)
        yol.write_bytes(b.getvalue())
        if manifeste:
            self.manifest.append({'tur': tur, 'sym': sym, 'yol': f'ham/{tur}/{sym}/{ad}', 'durum': 'TAMAM',
                                  'sha256': sha or hashlib.sha256(yol.read_bytes()).hexdigest()})
        return yol

    def manifest_yaz(self, ek=()):
        with (self.kok / 'MANIFEST.jsonl').open('w', encoding='utf-8') as f:
            for r in list(self.manifest) + list(ek):
                f.write(json.dumps(r) + '\n')

    def sil(self):
        shutil.rmtree(self.kok, ignore_errors=True)


class YukleyiciTest(unittest.TestCase):
    def setUp(self):
        self.v = _GeciciVeri()

    def tearDown(self):
        self.v.sil()

    def _standart(self):
        t0 = BAS_MS
        # Basliksiz dosya (eski arsiv bicimi); ikinci dosya basllikli, bir satiri mikrosaniye, bir tekrar, donem disi.
        self.v.zip_yaz('klines', 'XUSDT', 'XUSDT-1h-2023-07.zip',
                       '\n'.join(_kline_satir(t0 + i * H) for i in range(3)) + '\n')
        satirlar = [KL_BASLIK, _kline_satir(t0 + 2 * H, p=99.0),          # tekrar: ilki (10.0) tutulur
                    _kline_satir((t0 + 3 * H) * 1000),                     # mikrosaniye
                    _kline_satir(BAS_MS - H),                               # donem disi
                    _kline_satir(t0 + 4 * H)]
        self.v.zip_yaz('klines', 'XUSDT', 'XUSDT-1h-2023-08.zip', '\n'.join(satirlar) + '\n')
        fu = [FU_BASLIK, f'{t0 + 8 * H + 3},8,0.0001', f'{t0 + 8 * H + 7},8,0.0009',   # yuvarlama cakismasi
              f'{t0 + 16 * H},4,abc', f'{t0 + 20 * H},4,-0.0002']
        self.v.zip_yaz('fundingRate', 'XUSDT', 'XUSDT-fundingRate-2023-07.zip', '\n'.join(fu) + '\n')
        self.v.manifest_yaz()

    def test_temizlik_kurallari_ve_rapor(self):
        self._standart()
        seri, fon, rapor, dosyalar = coin_yukle(self.v.kok, 'XUSDT', manifest_tamam(self.v.kok))
        np.testing.assert_array_equal(seri.acilis_ms, [BAS_MS + i * H for i in range(5)])
        self.assertEqual(seri.kapanis[2], 10.0)                      # tekrarda ilki
        self.assertEqual(seri.hacim[0], 1000.0)                      # quote hacmi
        self.assertEqual((rapor.klines['tekrar'], rapor.klines['mikrosaniye'], rapor.klines['donem_disi']), (1, 1, 1))
        np.testing.assert_array_equal(fon.damga_ms, [BAS_MS + 8 * H, BAS_MS + 20 * H])
        np.testing.assert_array_equal(fon.oran, [0.0001, -0.0002])
        np.testing.assert_array_equal(fon.aralik_saat, [8.0, 4.0])
        self.assertEqual((rapor.funding['yuvarlama_cakismasi'], rapor.funding['oran_gecersiz']), (1, 1))
        self.assertEqual(len(dosyalar), 3)

    def test_hash_uyusmazligi_ve_manifest_disi_dosya(self):
        self._standart()
        self.v.manifest[0] = dict(self.v.manifest[0], sha256='1' * 64)    # manifestteki hash dosyayla uyusmaz
        self.v.manifest_yaz()
        with self.assertRaises(VeriYuklemeHatasi):
            coin_yukle(self.v.kok, 'XUSDT', manifest_tamam(self.v.kok))
        seri, _, _, _ = coin_yukle(self.v.kok, 'XUSDT', manifest_tamam(self.v.kok), dogrula=False)
        self.assertEqual(len(seri), 5)
        self.v.zip_yaz('klines', 'YUSDT', 'YUSDT-1h-2023-07.zip', _kline_satir(BAS_MS) + '\n', manifeste=False)
        with self.assertRaises(VeriYuklemeHatasi):
            coin_yukle(self.v.kok, 'YUSDT', manifest_tamam(self.v.kok))

    def test_manifest_ayni_yol_farkli_hash_hata_ayni_hash_serbest(self):
        self._standart()
        tekrar = dict(self.v.manifest[0])
        self.v.manifest_yaz(ek=[tekrar])
        self.assertEqual(len(manifest_tamam(self.v.kok)), 3)
        bozuk = dict(tekrar, sha256='0' * 64)
        self.v.manifest_yaz(ek=[bozuk])
        with self.assertRaises(VeriYuklemeHatasi):
            manifest_tamam(self.v.kok)

    def test_motor_sozlesmesi_izgara_ve_fiyat(self):
        self.v.zip_yaz('klines', 'XUSDT', 'XUSDT-1h-2023-07.zip', _kline_satir(BAS_MS + 5) + '\n')
        self.v.zip_yaz('klines', 'ZUSDT', 'ZUSDT-1h-2023-07.zip', _kline_satir(BAS_MS, p=0.0) + '\n')
        self.v.manifest_yaz()
        m = manifest_tamam(self.v.kok)
        for sym in ('XUSDT', 'ZUSDT'):
            with self.assertRaises(VeriYuklemeHatasi):
                coin_yukle(self.v.kok, sym, m)

    def test_tam_veri_ve_veri_kimligi(self):
        self._standart()
        self.v.zip_yaz('klines', 'YUSDT', 'YUSDT-1h-2023-07.zip', _kline_satir(BAS_MS) + '\n')
        self.v.manifest_yaz()
        veri, rapor = tam_veri_yukle(self.v.kok, evren=('XUSDT', 'YUSDT'))
        self.assertEqual(veri.adaylar, ('XUSDT', 'YUSDT'))
        self.assertEqual(set(veri.barlar), {'XUSDT', 'YUSDT'})
        self.assertEqual(set(veri.funding), {'XUSDT'})
        self.assertEqual(rapor.dosya_sayisi, 4)
        _, rapor2 = tam_veri_yukle(self.v.kok, evren=('XUSDT', 'YUSDT'))
        self.assertEqual(rapor.veri_kimligi, rapor2.veri_kimligi)
        _, rapor3 = tam_veri_yukle(self.v.kok, semboller=('XUSDT',), evren=('XUSDT', 'YUSDT'))
        self.assertNotEqual(rapor.veri_kimligi, rapor3.veri_kimligi)
        with self.assertRaises(VeriYuklemeHatasi):
            tam_veri_yukle(self.v.kok, semboller=('QUSDT',), evren=('XUSDT', 'YUSDT'))


class GelistirmeEvreniTest(unittest.TestCase):
    def test_hash_ve_icerik(self):
        evren = gelistirme_evreni()
        self.assertEqual(len(evren), 122)
        self.assertIn('BTCUSDT', evren)
        self.assertIn('ETHUSDT', evren)
        self.assertLess(BAS_MS, BIT_MS)


if __name__ == '__main__':
    unittest.main()
