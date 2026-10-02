"""3.12 rapor taslağı üreteci (ciktilar/v8_kalibrasyon_20260929_01/rapor_uret.py): TOPLAMA biçiminde (gerçek
toplama fonksiyonlarının çıktılarıyla kurulmuş sahte değerler) bütün tablolar, kanıt ve TASLAK bölümleri; KILIT_BEKLER
dalı. Performans değildir."""
import importlib.util
import json
import sys as _sys
import unittest
from pathlib import Path as _Path

V8_DIR = _Path(__file__).resolve().parent.parent
if str(V8_DIR) not in _sys.path:
    _sys.path.insert(1, str(V8_DIR))
BETIK = V8_DIR.parent / 'ciktilar' / 'v8_kalibrasyon_20260929_01' / 'rapor_uret.py'
_spec = importlib.util.spec_from_file_location('rapor_uret', BETIK)
R = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(R)

from kalibrasyon import toplama as T  # noqa: E402
from kalibrasyon.duzey1_esik import Kurallar  # noqa: E402
from banka import olcutler as o  # noqa: E402


def _toplama(kurallar=True):
    k = Kurallar(N=327, sigma_sr=0.30, b2_bagli=True, d=0.75, e_b5=0.6, k_b6=2, e_b10=0.8)
    rapor = {'sigma_sr': {'sigma_sr_bag': 0.30, 'kaynak': 'varsayim', 'cumle': 'σ_SR = 0,30 varsayımdır, doğrulanmadı'},
             'N': 327, 'karar': {'durum': 'TAMAM' if kurallar else 'KILIT_BEKLER', 'denemeler': [1, 2]},
             'kurallar': k.__dict__ if kurallar else None, 'r16': T.r16_tablosu(327),
             'b9_gecme_ref': {0: 0.9, 1: 0.8}}
    if kurallar:
        rapor['p_kabul_A_ort'] = [0.01, 0.05, 0.2, 0.5, 0.7, 0.85]
        rapor['seyreltme'] = {'rho=0.0;SR_C=0.0': [0.0, 0.1, 0.2, 0.4, 0.6, 0.8]}
    t = {'durum': 'TAMAM' if kurallar else 'KILIT_BEKLER',
         'duzey1': {'durum': 'TAMAM' if kurallar else 'KILIT_BEKLER', 'rapor': rapor},
         'kanit': {'kod_dondurma_sha256': 'a' * 64, 'har_sonuc_sha256': 'b' * 64, 'betik_sha256': 'c' * 64,
                   'kimlikler': {'kod': 'k', 'motor': 'm', 'parametre': 'p', 'ortam': 'o'},
                   'kaynak': {'duzey2_tuketilen': {'birim_dosyalari': {'dosya': 5140}}}}}
    if kurallar:
        t['duzey2'] = {'durum': 'TAMAM', 'duzey2a': {m: {'kabul': 2, 'n': 100, 'ust_sinirin_nokta_tahmini': 0.02,
                                                          'wilson_alt': 0.005, 'wilson_ust': 0.07, 'tarama_gecti': True}
                                                      for m in ('A', 'B')},
                       'duzey2b': {a: {'n': 10, 'b7_q90': o.wilson(6, 10), 'b7_q95': o.wilson(4, 10),
                                       'taban_ve_b7_q95': o.wilson(3, 10), 'sira_yuzdeligi_ort': 0.8, 'ortak_pay': 0.3}
                                   for a in range(5)}}
    return json.loads(json.dumps(t))                                             # disk biçimi (anahtarlar dize)


class RaporUretTest(unittest.TestCase):
    def test_tam(self):
        md = R.uret(_toplama(), 'f' * 64)
        for parca in ('f' * 64, '## 1. Düzey 1 kararları', 'P(KABUL | gerçek SR)', 'B seyreltme', 'R16 kalem-kâğıt',
                      '### 2-a', '### 2-b', '## 3. Kararlar ve gerekçe', 'σ_SR = 0,30 varsayımdır', '| e_b5 | 0.600 |'):
            self.assertIn(parca, md)
        self.assertEqual(md.count(R.TASLAK), 3)
        self.assertEqual(md.count('| A | 2 | 100 |'), 1)

    def test_kilit_bekler(self):
        md = R.uret(_toplama(kurallar=False), 'f' * 64)
        self.assertIn('KILIT_BEKLER', md)
        self.assertIn('Düzey 2 toplanmadı', md)
        self.assertNotIn('P(KABUL | gerçek SR)', md)


if __name__ == '__main__':
    unittest.main()
