"""Banka uçtan uca boru hattı (6.12; BANKA §2.4, BK-1…BK-12): gerçek yürütücü çıktı yapısı → koşucu (tam birim listesi,
şifreleme, B10 türetmesi, devam) → SONUC_DAMGA → birimleri_coz → hüküm. Sentetik carry senaryosu; performans değildir.

Tam motorla 530 birim bu testte koşturulamaz (birim başına saniyeler). Bunun yerine gerçek yürütücü şablon koşuları yapar
(birincil, null, K-evren; B'de ayrıca birincil dışı yapı için ızgara); öteki birimler şablonun yapısını birim kimliğiyle ve
deterministik SR sapmasıyla taşır. A ve B ayrı sınıflarda (Codex T18: önceki sürüm yalnız A şablonlarıyla B açığını
yakalayamıyordu).
Denenen: birim adlarının ve sözlük yapısının koşucu ile hüküm arasında uyumu (ızgara, Kelly, 500 null, türetilen 10 B10
birimi), pencere uzunlukları, damga ve gerçek age şifrelemesi. R3 (long_beta) ve B'de R8'in bağımsız A birimi
(a_ayristirma) gerçek yürütücüyle koşan kendi şablonlarından gelir (Codex T19: a_ayristirma_A önceden B yan-birim
şablonundan kopyalanıyordu)."""
import functools
import hashlib
import json
import shutil
import sys as _sys
import tempfile
import unittest
from pathlib import Path as _Path

TESTLER_DIR = _Path(__file__).resolve().parent
V8_DIR = TESTLER_DIR.parent
for _dir in (V8_DIR, TESTLER_DIR):
    if str(_dir) not in _sys.path:
        _sys.path.insert(1, str(_dir))

from banka_kos import age, ayar  # noqa: E402
from banka_kos import hukum as H  # noqa: E402
from banka_kos import kosucu as K  # noqa: E402
from banka_kos import yurutucu as Y  # noqa: E402
from fikstur.saatlik_veri import CARRY_GUN, gun_ms  # noqa: E402
from kalibrasyon.duzey1_esik import Kurallar  # noqa: E402

G = 86_400_000


def sablon_oku(yol: str) -> dict:
    return json.loads(_Path(yol).read_text(encoding='utf-8'))


def _sapma(b: dict) -> float:
    return int(hashlib.sha256(K.kanonik(b)).hexdigest()[:6], 16) / 2 ** 24 - 0.5


def sablon_yurut(b: dict, bag: dict) -> tuple:
    """Gerçek yürütücü çıktısının yapısı, birim kimliğiyle; SR deterministik sapmalı (B7 ve B10 çeşitliliği)."""
    g = b['grup']
    if g == 'null':
        return {'birim': b, 'sr': bag['null']['sr'] + 0.5 * _sapma(b), 'r17': bag['null']['r17']}, bag['null_acik']
    if g in ('long_beta', 'a_ayristirma', 'demo_nav') or (g == 'kelly' and 'kelly' in bag and b['maliyet_k'] == 1.0):
        duz = json.loads(json.dumps(bag[g]))
        duz['birim'] = b
        return duz, bag['acik']
    kaynak = bag['k_evren'] if g == 'k_evren' else (bag['birincil'] if g == 'birincil' else bag.get('diger',
                                                                                                    bag['birincil']))
    duz = json.loads(json.dumps(kaynak))
    duz['birim'] = b
    duz['olcum']['sr'] = kaynak['olcum']['sr'] + (0.0 if g == 'birincil' else 0.3 * _sapma(b))
    return duz, bag['acik']


class UctanUcaTest(unittest.TestCase):
    M = 'A'
    N_TABAN = 529

    @classmethod
    def setUpClass(cls):
        from test_v8_banka_yurutucu import _bag, _birim
        M = cls.M
        cls.d = _Path(tempfile.mkdtemp(prefix=f'banka_uu_{M}_'))
        bag = _bag()
        cls.bag = bag
        b, acik = Y.birim_yurut(_birim('birincil', M), bag)
        n, n_acik = Y.birim_yurut(_birim('null', M, null_no=1), bag)
        k, _ = Y.birim_yurut(_birim('k_evren', M, evren='K'), bag)
        r3, _ = Y.birim_yurut(_birim('long_beta', M), bag)
        demo, _ = Y.birim_yurut(_birim('demo_nav', M, nav0=ayar.DEMO_NAV), bag)
        sablon = {'birincil': b, 'null': n, 'k_evren': k, 'long_beta': r3, 'demo_nav': demo, 'acik': acik,
                  'null_acik': n_acik}
        if M == 'B':                                                                    # birincil dışı gerçek yapı
            sablon['diger'], _ = Y.birim_yurut(_birim('izgara', M, nav0=1e6, maliyet_k=2.0), bag)
            sablon['a_ayristirma'], _ = Y.birim_yurut(_birim('a_ayristirma', 'A'), bag)    # R8 bağımsız A
            sablon['kelly'], _ = Y.birim_yurut(_birim('kelly', M, L=2.0, maliyet_k=1.0), bag)  # R8 carry serisi
        yol = cls.d / 'sablon.json'
        yol.write_text(json.dumps(sablon), encoding='utf-8')
        cls.kur = functools.partial(sablon_oku, str(yol))
        cls.kimlik, cls.alici = age.anahtar_uret()
        cls.birimler = ayar.birimler(M)
        cls.cikti = cls.d / 'kosu'
        cls.ilk = K.calistir(cls.cikti, cls.birimler, {'motor': 'm'}, cls.alici, sablon_yurut, cls.kur, isci=2,
                             max_birim=3, sessiz=True)                                  # kesinti
        cls.son = K.calistir(cls.cikti, cls.birimler, {'motor': 'm'}, cls.alici, sablon_yurut, cls.kur, isci=2,
                             sessiz=True)                                               # devam (BK-6 dahil)
        cls.damga = K.damga_yaz(cls.cikti, cls.birimler)
        cls.hb = H.HukumBaglami(mimari=M, t0_z1_ms=bag.t0_z1_ms, gorulmus_gunler=bag.gorulmus_gunler,
                                tohum_banka=bag.tohum_banka, kurallar=Kurallar(N=327, sigma_sr=0.5, b2_bagli=True,
                                                                               d=0.5, e_b5=0.6, e_b10=0.8),
                                N_hukum=330, birincil_son_ms=bag.birincil_son_ms, z2_bas_ms=gun_ms(125),
                                z2_son_ms=bag.z2_son_ms, kelly_cekis=5, z1_dilim_sinir=bag.z1_dilim_sinir)
        cls.cozulen = H.birimleri_coz(cls.cikti, cls.kimlik, beklenen_kok=cls.damga['kok_sha256'])
        cls.h = H.hukum(cls.cozulen, cls.hb)

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.d, ignore_errors=True)

    def test_kosu_ve_damga(self):
        self.assertEqual(len(self.birimler), self.N_TABAN)                             # R3 dahil
        self.assertEqual(self.ilk['bu_kosuda'], 3)
        self.assertEqual(self.son['kalan'], 0)
        self.assertEqual(self.damga['birim_sayisi'], len(self.birimler) + ayar.B10_N)
        self.assertEqual(len(self.cozulen), self.damga['birim_sayisi'])
        acik = ''.join(p.read_text(encoding='ascii') for p in (self.cikti / 'denetim').rglob('*.json'))
        alt = self.cozulen[f'birincil_{self.M}']['olcum']['alt_katki_sirasi']
        self.assertFalse(any(f'"{c}"' in acik for c in alt))                          # coin adı açık grupta yok

    def test_b10_turetmesi_gercek_siradan(self):
        alt = self.cozulen[f'birincil_{self.M}']['olcum']['alt_katki_sirasi'][:ayar.B10_N]
        cik = [self.cozulen[f'cikarma_{self.M}_s{i:02d}']['birim']['cikan'] for i in range(1, ayar.B10_N + 1)]
        self.assertEqual(cik, alt)

    def test_rapor_satirlari(self):
        from dataclasses import replace
        from banka_kos import rapor
        hb = replace(self.hb, d_bas_ms=gun_ms(94), d_bit_ms=gun_ms(112))       # görülmüş gün 95 içeride
        r = rapor.rapor_satirlari(self.cozulen, hb, cekis=50)
        self.assertEqual(set(r), {'GA', 'R2', 'R4', 'R5', 'R8', 'R6', 'R7', 'R9', 'R10', 'R11', 'R12', 'R13', 'R13b', 'R14', 'R15',
                                  'R16', 'R17'})
        self.assertEqual(r['R4'], {'durum': 'REV1 serisi yok'})
        n_dahil = (self.bag.birincil_son_ms - self.bag.t0_z1_ms) // G - len(self.bag.gorulmus_gunler)
        if self.M == 'A':
            self.assertEqual(r['R8'], {'durum': 'M = A: R8 yok'})
        else:
            r8 = r['R8']
            self.assertEqual(set(r8['kelly_carry_beta']), {f'{L:g}' for L in ayar.KELLY_L})
            self.assertEqual(r8['kelly_carry_beta']['1']['n'], n_dahil)
            self.assertIn('b5_pay', r8['bagimsiz_A'])
            self.assertEqual(len(r8['satir_yillik']), 12)
        self.assertEqual(set(r['R2']), {'birincil', 'dilim1', 'dilim2', 'dilim3', 'dilim4', 'beta_yok_coin'})
        self.assertGreater(r['R2']['birincil']['n'], 10)
        self.assertEqual(r['R15']['gun'], 18 - 1)
        self.assertEqual(r['R17']['evren_ort']['gercek'], self.cozulen[f'birincil_{self.M}']['r17']['evren_ort'])
        b = self.cozulen[f'birincil_{self.M}']
        _, g = __import__('banka_kos.hukum', fromlist=['x']).gunluk_getiri(b, hb.d_bas_ms, hb.d_bit_ms, hb.gorulmus_gunler)
        rev1 = {'dosya': 'rev1_sentetik.json', 'sha256': '0' * 64,
                'seri': {int(x): 0.001 * ((i % 7) - 3) for i, x in enumerate(g.tolist())}}
        r4 = rapor.r4_rev1(self.cozulen, hb, rev1)
        self.assertEqual(r4['ortak_gun'], len(g))
        self.assertTrue(-1.0 <= r4['gunluk'] <= 1.0)
        self.assertEqual(r4['sha256'], '0' * 64)
        self.assertIn('lot_minnotional_alti_orani', r['R14'])
        self.assertEqual('btc_sifir_orani' in r['R14'], self.M == 'B')
        self.assertEqual('rv_sigma2_q50' in r['R7'], self.M == 'A')
        self.assertEqual(set(r['R9']), {'0.50', '0.90'})
        self.assertEqual(r['R9']['0.50']['gun'], n_dahil)
        self.assertEqual(r['R10']['Z2']['gun'], (self.bag.z2_son_ms - gun_ms(125)) // G)
        self.assertEqual(r['R10']['D']['gun'], 18 - 1)                                  # görülmüş gün (95) düşüldü
        r11 = r['R11']
        self.assertEqual(r11['sr'], self.cozulen[f'birincil_{self.M}']['olcum']['sr'])
        self.assertLessEqual(r11['q05'], r11['q95'])
        self.assertEqual(set(r['R12']), {'stressiz', 'D90-1', 'D90-2', 'D90-4', 'SQ-1', 'SQ-2', 'SQ-4', 'DM-1'})
        self.assertAlmostEqual(r['R12']['stressiz']['sr'], r11['sr'], places=12)
        self.assertEqual(len(r['R16']), 4 * 3 * 2)
        self.assertEqual(r['R16']['bag|1.0|eta']['N'], self.hb.N_hukum)
        self.assertEqual(r['R16']['0.30|1.0|eta1']['eta'], 1.0)
        self.assertEqual(r['R16']['bag|1.2|eta']['N'], round(self.hb.N_hukum * 1.2))
        json.dumps(r)
        self.assertEqual(rapor.rapor_satirlari(self.cozulen, hb, cekis=50)['R11'], r11)     # deterministik

    def test_banka_raporu_md(self):
        # 6.09: §8.2'nin 13 bölümü, zorunlu cümleler, B'ye özgü kısımlar, coin adı yok (BTC/ETH hariç).
        import re
        from dataclasses import replace
        from banka_kos import rapor, rapor_md
        hb = replace(self.hb, d_bas_ms=gun_ms(94), d_bit_ms=gun_ms(112))
        sat = rapor.rapor_satirlari(self.cozulen, hb, cekis=30)
        ga = sat['GA']
        for a in ('B7_birincil', 'B3_x2', 'B3_x3', 'B4', 'B6_dilim1', 'B6_dilim4', 'B8', 'B9', 'R13_lot_kapali',
                  'R3_long_beta', 'Kelly_1|1', 'Kelly_4|2', 'R1_5000000|3', 'R1_100000|1'):
            self.assertIn(a, ga)
            self.assertLessEqual(ga[a]['q05'], ga[a]['q95'], a)
        self.assertTrue(all('ga' in v for v in sat['R12'].values()))
        bag = {'hukum_turu': self.h['karar'], 'mimari': self.M, 'b2_turu': 'B', 'sigma_kaynak': 'varsayim',
               'N_hukum': hb.N_hukum, 'hashler': {'KILIT.json': 'k' * 64, 'DONDURMA.json': 'd' * 64},
               'stres_secenegi': {'secenek': 'i', 'hash': 'h' * 64}, 'kalibrasyon': {'e_B5': 0.6},
               'teknik': {'T1': 'geçti'}, 'veri_denetimi': {'karar': {'T2': False}, 'eksik_funding_kaydi': 3,
                                                            'checksum': {'onarilamayan': 0}}}
        bir = rapor_md.birincil_metrikler(self.cozulen, hb)
        md = rapor_md.banka_raporu(self.h, sat, bir, bag)
        for parca in ('γ₃', 'η =', 'boot q50', 'P(MDD>%30)', 'MDD D90-1', 'MDD DM-1', 'eksik_funding_kaydi',
                      'Tahminci tanıları (R7)', 'SR %90 GA', '| h_L | SR | %90 GA |'):
            self.assertIn(parca, md)
        self.assertEqual('Carry bacağı epizot payı' in md, self.M == 'B')
        with self.assertRaises(rapor_md.RaporHatasi):                                   # serbest alanda sembol
            rapor_md.banka_raporu(self.h, sat, bir, dict(bag, teknik={'not': 'XRPUSDT dosyasi eksik'}))
        with self.assertRaises(rapor_md.RaporHatasi):
            rapor_md.banka_raporu(self.h, dict(sat, R4={'dosya': 'rev1_SOLUSDT.json'}), bir, bag)
        rapor_md.banka_raporu(self.h, sat, bir, dict(bag, teknik={'not': 'BTCUSDT ve ETHUSDT izinli'}))
        for i in range(1, 14):
            self.assertIn(f'## {i}. ', md)
        for c in rapor_md.CUMLELER_HAYATTA_KALAN + (rapor_md.CUMLE_YENIDEN_ORNEKLEME, rapor_md.CUMLE_DSR,
                                                    rapor_md.CUMLE_SIGMA_VARSAYIM, rapor_md.CUMLE_B_FIYAT):
            self.assertIn(c, md)
        self.assertEqual('B ayrıştırması (R8)' in md, self.M == 'B')
        self.assertEqual(re.findall(r'\bA\d\d\b', md), [])                           # sentetik coin adları sızmaz
        with self.assertRaises(ValueError):
            rapor_md.banka_raporu(self.h, sat, {}, dict(bag, hukum_turu='BELKI'))

    def test_hukum_yapisi(self):
        h = self.h
        self.assertIn(h['karar'], ('KABUL', 'RET'))
        ol = h['olcutler']
        self.assertEqual(set(ol), {f'B{i}' for i in range(2, 12)})
        pencere_gun = (self.bag.birincil_son_ms - self.bag.t0_z1_ms) // G + (self.bag.z2_son_ms - gun_ms(125)) // G
        self.assertEqual(ol['B9']['gun'], pencere_gun - len(self.bag.gorulmus_gunler))
        self.assertEqual(len(h['R1']), len(ayar.NAV_IZGARA) * len(ayar.MALIYET))
        self.assertEqual(h['R1']['100000|1'], self.cozulen[f'birincil_{self.M}']['olcum']['sr'])
        n_dahil = (self.bag.birincil_son_ms - self.bag.t0_z1_ms) // G - len(self.bag.gorulmus_gunler)
        for m in ayar.KELLY_MALIYET:
            ks = h['kelly_stres'][int(m)]
            self.assertEqual(set(ks['kelly']['satirlar']), set(ayar.KELLY_L))
            self.assertEqual(set(ks['stres']), set(ayar.KELLY_L))
            self.assertEqual(ks['kelly']['satirlar'][1.0]['bootstrap']['q50'] >= 0, True)
        self.assertEqual(len(self.cozulen[f'birincil_{self.M}']['olcum']['r']), n_dahil)
        self.assertIsNotNone(self.cozulen[f'birincil_{self.M}']['olcum']['b5_pay'])
        r3 = h['R3']
        self.assertEqual(r3['gun'], n_dahil)
        self.assertEqual(r3['nw_gecikme'], 10)
        self.assertEqual(set(r3), {'gun', 'olcek', 'sr_birincil', 'sr_r3', 'sr_farki', 'korelasyon', 'beta',
                                   'alfa_gunluk', 'alfa_yillik', 't_alfa_nw', 'nw_gecikme', 'nan_yok'})
        self.assertAlmostEqual(r3['sr_birincil'], self.cozulen[f'birincil_{self.M}']['olcum']['sr'], places=12)


class UctanUcaBTest(UctanUcaTest):
    """Aynı boru hattı M = B ile (birincil dışı birimler ayrıştırmasız, B5 yalnız birincilde; R8 bağımsız A birimi dahil)."""
    M = 'B'
    N_TABAN = 530

    def test_birincil_disi_b5_yok(self):
        self.assertIsNone(self.cozulen['izgara_B_n1000000_k2']['olcum']['b5_pay'])
        a = self.cozulen['a_ayristirma_A']
        self.assertEqual(a['birim']['mimari'], 'A')
        self.assertIsNotNone(a['olcum']['b5_pay'])                                      # bağımsız A: B5 ölçülür
        self.assertNotEqual(a['nav_gunluk'], self.cozulen['birincil_B']['nav_gunluk'])  # B şablonundan kopya değil


if __name__ == '__main__':
    unittest.main()
