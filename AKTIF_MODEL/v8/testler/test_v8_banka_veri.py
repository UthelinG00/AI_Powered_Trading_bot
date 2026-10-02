"""Banka veri yükleyicisi (banka_kos/veri.py; 6.01b; BANKA §3.7 netleştirme 19): sentetik iki paket (banka indirmesi +
D paketi) zip'leriyle birleştirme, D penceresi dışlaması, dönem sonu, API funding görüntüsü, bağlayıcı hash, hata
durumları ve veri kimliği. Gerçek banka verisi okunmaz."""
import hashlib
import io
import json
import shutil
import sys as _sys
import tempfile
import unittest
import zipfile
from datetime import datetime, timezone
from pathlib import Path as _Path

import numpy as np

V8_DIR = _Path(__file__).resolve().parent.parent
if str(V8_DIR) not in _sys.path:
    _sys.path.insert(1, str(V8_DIR))

from banka_kos import veri as V  # noqa: E402

H = 3_600_000


def _ms(y, a, g, s=0, d=0):
    return int(datetime(y, a, g, s, d, tzinfo=timezone.utc).timestamp() * 1000)


def _kline_zip(yol: _Path, saatler, fiyat=100.0):
    satir = ['open_time,open,high,low,close,volume,close_time,quote_volume,count,taker_buy_volume,'
             'taker_buy_quote_volume,ignore']
    for i, t in enumerate(saatler):
        p = fiyat + i
        satir.append(f'{t},{p},{p + 1},{p - 1},{p + 0.5},10,{t + H - 1},{1000 + i},5,1,1,0')
    _zip(yol, '\n'.join(satir) + '\n')


def _funding_zip(yol: _Path, damgalar, oran=0.0001):
    satir = ['calc_time,funding_interval_hours,last_funding_rate'] + [f'{t},8,{oran}' for t in damgalar]
    _zip(yol, '\n'.join(satir) + '\n')


def _zip(yol: _Path, metin: str):
    yol.parent.mkdir(parents=True, exist_ok=True)
    b = io.BytesIO()
    with zipfile.ZipFile(b, 'w') as z:
        z.writestr(yol.with_suffix('.csv').name, metin)
    yol.write_bytes(b.getvalue())


def _sha(p: _Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


class BankaVeriTest(unittest.TestCase):
    def setUp(self):
        self.k = _Path(tempfile.mkdtemp(prefix='banka_veri_'))
        self.b, self.d = self.k / 'banka', self.k / 'd'
        z1 = [_ms(2023, 6, 30) + i * H for i in range(24)]
        # K coini: D penceresini aşan kesintisiz banka indirmesi; Z2 sonrası bir bar (atılmalı).
        _kline_zip(self.b / 'ham/klines/KKUSDT/KKUSDT-1h-2023-06.zip', z1 + [_ms(2023, 7, 1) + i * H for i in range(3)])
        _kline_zip(self.b / 'ham/klines/KKUSDT/KKUSDT-1h-2026-09-23.zip', [_ms(2026, 9, 23, 23), _ms(2026, 9, 24)])
        (self.b / 'ham/fundingRate_api').mkdir(parents=True)
        (self.b / 'ham/fundingRate_api/KKUSDT.json').write_text(json.dumps(
            [{'fundingTime': _ms(2026, 9, 23, 8), 'fundingRate': '0.0001', 'fundingIntervalHours': 8},
             {'fundingTime': _ms(2026, 9, 24, 0), 'fundingRate': '0.0002', 'fundingIntervalHours': 8}]), encoding='utf-8')
        # D coini: banka indirmesinde Z1 + D penceresine sızmış 2 satır (atılmalı); D paketinde D penceresi.
        _kline_zip(self.b / 'ham/klines/DDUSDT/DDUSDT-1h-2023-06.zip', z1 + [_ms(2023, 7, 1, 5), _ms(2023, 7, 1, 6)])
        _funding_zip(self.b / 'ham/fundingRate/DDUSDT/DDUSDT-fundingRate-2023-06.zip',
                     [_ms(2023, 6, 30, 8), _ms(2023, 6, 30, 16)])
        _kline_zip(self.d / 'ham/klines/DDUSDT/DDUSDT-1h-2023-07.zip', [_ms(2023, 7, 1) + i * H for i in range(4)], 200.0)
        _funding_zip(self.d / 'ham/fundingRate/DDUSDT/DDUSDT-fundingRate-2023-07.zip', [_ms(2023, 7, 1, 0)])
        self.manifest_yaz()

    def tearDown(self):
        shutil.rmtree(self.k, ignore_errors=True)

    def manifest_yaz(self, ek=()):
        satir = []
        for p in sorted(self.b.rglob('*')):
            if p.is_file() and p.name != V.MANIFEST_ADI:
                h = _sha(p)
                satir.append({'yol': p.relative_to(self.b).as_posix(), 'sha256': h, 'checksum': h, 'durum': 'TAMAM'})
        satir += list(ek)
        (self.b / V.MANIFEST_ADI).write_text('\n'.join(json.dumps(s) for s in satir) + '\n', encoding='utf-8')
        d = [{'yol': p.relative_to(self.d).as_posix(), 'sha256': _sha(p), 'durum': 'TAMAM'}
             for p in sorted(self.d.rglob('*.zip'))]
        (self.d / 'MANIFEST.jsonl').write_text('\n'.join(json.dumps(s) for s in d) + '\n', encoding='utf-8')

    def yukle(self, **k):
        return V.banka_veri_yukle(self.b, self.d, ('KKUSDT', 'DDUSDT'), {'DDUSDT'}, **k)

    def test_birlestirme_ve_donem(self):
        veri, r = self.yukle()
        kk, dd = veri.barlar['KKUSDT'], veri.barlar['DDUSDT']
        self.assertEqual(len(kk), 24 + 3 + 1)                                    # Z2_son (2026-09-24 00:00) atıldı
        self.assertEqual(int(kk.acilis_ms[-1]), _ms(2026, 9, 23, 23))
        self.assertEqual(r['coin']['KKUSDT']['klines']['donem_disi'], 1)
        self.assertEqual(len(dd), 24 + 4)                                        # Z1 bankadan, D penceresi D paketinden
        self.assertEqual(r['coin']['DDUSDT']['klines']['d_penceresi_atilan'], 2)
        self.assertTrue(np.all(np.diff(dd.acilis_ms) == H))
        self.assertEqual(float(dd.acilis[24]), 200.0)                            # D penceresi D paketinin fiyatı
        self.assertEqual(len(veri.funding['DDUSDT'].damga_ms), 3)
        self.assertEqual(len(veri.funding['KKUSDT'].damga_ms), 1)                # API görüntüsü; Z2_son kaydı atıldı
        self.assertTrue(r['coin']['KKUSDT']['funding']['api_goruntusu'])
        self.assertEqual(veri.adaylar, ('DDUSDT', 'KKUSDT'))
        self.assertEqual(r['veri_kimligi'], self.yukle()[1]['veri_kimligi'])     # deterministik
        self.assertEqual(r['dosya_sayisi'], 7)

    def test_hash_ve_manifest_hatalari(self):
        p = self.b / 'ham/klines/KKUSDT/KKUSDT-1h-2023-06.zip'
        _kline_zip(p, [_ms(2023, 6, 30)], 999.0)                                 # dosya sonradan değişti
        with self.assertRaises(V.BankaVeriHatasi):
            self.yukle()
        self.manifest_yaz()
        _kline_zip(self.b / 'ham/klines/KKUSDT/KKUSDT-1h-2023-05.zip', [_ms(2023, 5, 31)])   # manifestte yok
        with self.assertRaises(V.BankaVeriHatasi):
            self.yukle()
        (self.b / 'ham/klines/KKUSDT/KKUSDT-1h-2023-05.zip').unlink()
        self.manifest_yaz(ek=[{'yol': 'ham/x.zip', 'sha256': 'a' * 64, 'checksum': 'b' * 64, 'durum': 'TAMAM'}])
        with self.assertRaises(V.BankaVeriHatasi):                               # onarılamayan satır (T2)
            self.yukle()

    def test_eylul_kaynagi_ve_eksik_dosya(self):
        # 20 i: API görüntüsünden yalnız Eylül; hem arşiv hem API → hata; manifestte TAMAM olup diskte olmayan → hata.
        api = self.b / 'ham/fundingRate_api/KKUSDT.json'
        api.write_text(json.dumps([{'fundingTime': _ms(2026, 8, 31, 16), 'fundingRate': '0.0003'},
                                   {'fundingTime': _ms(2026, 9, 23, 8), 'fundingRate': '0.0001'}]), encoding='utf-8')
        self.manifest_yaz()
        veri, _ = self.yukle()
        self.assertEqual(len(veri.funding['KKUSDT'].damga_ms), 1)                # Ağustos kaydı alınmadı
        _funding_zip(self.b / 'ham/fundingRate/KKUSDT/KKUSDT-fundingRate-2026-09.zip', [_ms(2026, 9, 1, 0)])
        self.manifest_yaz()
        with self.assertRaises(V.BankaVeriHatasi):
            self.yukle()
        (self.b / 'ham/fundingRate/KKUSDT/KKUSDT-fundingRate-2026-09.zip').unlink()
        self.manifest_yaz(ek=[{'yol': 'ham/klines/DDUSDT/DDUSDT-1h-2023-05.zip', 'sha256': 'c' * 64, 'checksum': 'c' * 64,
                               'durum': 'TAMAM'}])
        self.assertEqual(V.eksik_dosyalar(self.b, V.banka_manifest(self.b), ('KKUSDT', 'DDUSDT')),
                         ['ham/klines/DDUSDT/DDUSDT-1h-2023-05.zip'])
        with self.assertRaises(V.BankaVeriHatasi):
            self.yukle()

    def test_iki_kaynakta_ayni_damga(self):
        # Banka funding'i D başlangıcından 20 dk önce: pencere dışı kalır ama saate yuvarlanınca D paketinin 00:00
        # kaydıyla çakışır → hata.
        _funding_zip(self.b / 'ham/fundingRate/DDUSDT/DDUSDT-fundingRate-2023-06.zip', [_ms(2023, 6, 30, 23, 40)])
        self.manifest_yaz()
        with self.assertRaises(V.BankaVeriHatasi):
            self.yukle()


if __name__ == '__main__':
    unittest.main()
