"""Banka hükmü (banka_kos/hukum.py; BANKA §2.4, §3.3, §3.4, §4, §5.4; BK-3): sentetik çözülmüş birim sözlükleriyle.
B2–B11 mekaniği, B7 kantili (⌈0,95 n⌉'inci, katı büyük), B9 penceresi (birincil ∪ Z2, görülmüş günler hariç), B10,
bağlı/bağsız ölçüt ve karar, R1 ızgarası, Kelly/stres şekli (görülmüş gün dışlaması, çekiş sayısı), birimleri_coz damga
denetimi (gerçek age şifrelemesiyle, banka koşucusu üzerinden). Gerçek banka verisi yok."""
import hashlib
import json
import math
import shutil
import sys as _sys
import tempfile
import unittest
from dataclasses import replace
from datetime import datetime, timezone
from pathlib import Path as _Path

import numpy as np

V8_DIR = _Path(__file__).resolve().parent.parent
if str(V8_DIR) not in _sys.path:
    _sys.path.insert(1, str(V8_DIR))

from banka import olcutler as o  # noqa: E402
from banka_kos import age, ayar, stres  # noqa: E402
from banka_kos import hukum as H  # noqa: E402
from banka_kos import kosucu as K  # noqa: E402
from kalibrasyon.duzey1_esik import Kurallar  # noqa: E402

G = 86_400_000
T0 = int(datetime(2020, 10, 1, tzinfo=timezone.utc).timestamp() * 1000)
BSON = T0 + 240 * G                      # birincil örneklem [T0, BSON)
Z2B, Z2S = T0 + 300 * G, T0 + 340 * G    # Z2 [Z2B, Z2S)
GORULMUS = (T0 + 10 * G, T0 + 100 * G, Z2B + 5 * G)
N_GUN = (Z2S - T0) // G
KURAL = Kurallar(N=327, sigma_sr=0.5, b2_bagli=True, d=0.0, e_b5=0.6, k_b6=2, e_b10=0.8)
HB = H.HukumBaglami(mimari='A', t0_z1_ms=T0, gorulmus_gunler=GORULMUS, tohum_banka=11, kurallar=KURAL, N_hukum=400,
                    birincil_son_ms=BSON, z2_bas_ms=Z2B, z2_son_ms=Z2S, kelly_cekis=10)


def ad(**k) -> str:
    return K.birim_adi(ayar._birim(**k))


def _nav(rng, L: float) -> list:
    r = rng.normal(0.0008 * L, 0.01 * L, N_GUN)
    r[10] = -0.5                          # görülmüş gün (T0 + 10 gün): Kelly/stres ölçütüne girmemeli
    return (100_000.0 * np.concatenate(([1.0], np.cumprod(1.0 + r)))).tolist()


def _stres(rng) -> dict:
    n = (BSON - T0) // G
    return {'D90': rng.uniform(0, 0.2, n).tolist(), 'SQ': rng.uniform(0, 0.1, n).tolist(),
            'DM': rng.uniform(0, 0.4, n).tolist()}


def birimler_kur(birincil_sr: float = 1.2, b5_pay: float = 0.3, cikarma=None, null_n: int = ayar.N_NULL) -> dict:
    rng = np.random.default_rng(5)
    B = {}
    r = rng.normal(0.002, 0.01, (BSON - T0) // G - 2).tolist()
    B[ad(grup='birincil', mimari='A')] = {
        'nav_bas_ms': T0, 'nav_gunluk': _nav(rng, 1.0), 'stres_nesneleri': _stres(rng),
        'olcum': {'r': r, 'sr': birincil_sr, 'b4_sr': 0.5, 'b5_pay': b5_pay, 'dilim_sr': [0.5, float('nan'), -0.1, 0.8],
                  'b8_sr': 0.4, 'b11_mdd': 0.2}}
    for n in ayar.NAV_IZGARA:
        for m in ayar.MALIYET:
            if n == ayar.NAV_BIRINCIL and m == 1.0:
                continue
            u = {'olcum': {'sr': {2.0: 0.6, 3.0: 0.2}.get(m, 0.9) if n == ayar.NAV_BIRINCIL else 1.0 + n / 1e7 + m}}
            if n == ayar.NAV_BIRINCIL and m == 2.0:          # L = 1, maliyet ×2 Kelly satırı
                u.update(nav_bas_ms=T0, nav_gunluk=_nav(rng, 1.0), stres_nesneleri=_stres(rng))
            B[ad(grup='izgara', mimari='A', nav0=n, maliyet_k=m)] = u
    for L in ayar.KELLY_L:
        if L == 1.0:
            continue
        for m in ayar.KELLY_MALIYET:
            B[ad(grup='kelly', mimari='A', L=L, maliyet_k=m)] = {'nav_bas_ms': T0, 'nav_gunluk': _nav(rng, L),
                                                                 'stres_nesneleri': _stres(rng)}
    nuller = rng.permutation(np.arange(null_n) / 1000.0)
    for p in range(1, null_n + 1):
        B[ad(grup='null', mimari='A', null_no=p)] = {'sr': float(nuller[p - 1])}
    g = T0 + np.arange(N_GUN, dtype=np.int64) * G
    pencere = ((g < BSON) | ((g >= Z2B) & (g < Z2S))) & ~np.isin(g, GORULMUS)
    b9 = np.where(pencere, 0.001 + rng.normal(0, 0.0005, N_GUN), -1.0)   # pencere dışı ve görülmüş gün çok negatif
    B[ad(grup='k_evren', mimari='A', evren='K')] = {'nav_bas_ms': T0, 'b9_seri': b9.tolist()}
    cik = [1.2 - 0.05 * i for i in range(1, 11)] if cikarma is None else cikarma
    for i, x in enumerate(cik, start=1):
        B[K.birim_adi(dict(ayar._birim('birincil', 'A'), grup='cikarma', sira=i))] = {'olcum': {'sr': x}}
    B[ad(grup='long_beta', mimari='A')] = {'nav_bas_ms': T0, 'nav_gunluk': _nav(np.random.default_rng(6), 1.0)}  # R3
    return B


class OlcutTest(unittest.TestCase):
    def test_kabul_ve_olcut_mekanigi(self):
        B = birimler_kur()
        s = H.olcutler(B, HB)
        ol = s['olcutler']
        self.assertEqual(s['karar'], 'KABUL')
        r = B[ad(grup='birincil', mimari='A')]['olcum']['r']
        self.assertEqual(ol['B2']['dsr'], o.dsr(r, 400, 0.5)['dsr'])               # N_hüküm, kalibrasyon N'i değil
        self.assertNotEqual(ol['B2']['dsr'], o.dsr(r, 327, 0.5)['dsr'])
        self.assertEqual((ol['B3']['sr_x2'], ol['B3']['sr_x3'], ol['B3']['gecti']), (0.6, 0.2, True))
        self.assertEqual((ol['B6']['pozitif'], ol['B6']['gecti']), (2, True))       # nan ve negatif dilim sayılmaz
        self.assertEqual(ol['B7']['q95'], 0.474)                                     # 500 null: 475'inci değer
        self.assertEqual(ol['B10']['en_buyuk_dusus'], 1.2 - (1.2 - 0.5))
        self.assertTrue(all(v['gecti'] for v in ol.values()))

    def test_b7_kantil_siniri(self):
        self.assertFalse(H.olcutler(birimler_kur(birincil_sr=0.474), HB)['olcutler']['B7']['gecti'])   # katı >
        s = H.olcutler(birimler_kur(birincil_sr=0.4741), HB)
        self.assertTrue(s['olcutler']['B7']['gecti'])
        B = birimler_kur()
        B[ad(grup='null', mimari='A', null_no=7)]['sr'] = float('nan')
        s = H.olcutler(B, HB)
        self.assertFalse(s['olcutler']['B7']['gecti'])
        self.assertEqual(s['karar'], 'RET')

    def test_b9_penceresi(self):
        B = birimler_kur()
        b9 = H.olcutler(B, HB)['olcutler']['B9']
        self.assertEqual(b9['gun'], 240 + 40 - 3)
        seri = np.asarray(B[ad(grup='k_evren', mimari='A', evren='K')]['b9_seri'])
        g = T0 + np.arange(N_GUN, dtype=np.int64) * G
        secim = ((g < BSON) | (g >= Z2B)) & ~np.isin(g, GORULMUS)
        self.assertEqual(b9['sr'], o.sharpe(seri[secim]))
        self.assertTrue(b9['gecti'])

    def test_bagli_bagsiz_ve_b10(self):
        B = birimler_kur(b5_pay=0.99)
        self.assertEqual(H.olcutler(B, HB)['karar'], 'RET')                         # e_B5 = 0,6 bağlı
        s = H.olcutler(B, replace(HB, kurallar=replace(KURAL, e_b5=None)))
        self.assertIsNone(s['olcutler']['B5']['gecti'])
        self.assertEqual(s['karar'], 'KABUL')                                       # bağsız: rapor
        cik = [1.0] * 9 + [0.3]                                                     # düşüş 0,9 > e_B10 0,8
        self.assertFalse(H.olcutler(birimler_kur(cikarma=cik), HB)['olcutler']['B10']['gecti'])
        cik = [1.0] * 9 + [float('nan')]                                            # nan çıkarma: düşüş inf
        self.assertEqual(H.olcutler(birimler_kur(cikarma=cik), HB)['olcutler']['B10']['en_buyuk_dusus'], math.inf)
        with self.assertRaises(H.HukumHatasi):
            H.olcutler(birimler_kur(cikarma=[1.0] * 9), HB)
        s = H.olcutler(birimler_kur(), replace(HB, kurallar=replace(KURAL, d=1.01)))  # DSR ≤ 1: B2 kalır
        self.assertEqual((s['olcutler']['B2']['gecti'], s['karar']), (False, 'RET'))

    def test_eksik_birimler(self):
        B = birimler_kur()
        del B[ad(grup='k_evren', mimari='A', evren='K')]
        with self.assertRaises(H.HukumHatasi):
            H.olcutler(B, HB)
        with self.assertRaises(H.HukumHatasi):
            H.olcutler(birimler_kur(null_n=ayar.N_NULL - 1), HB)


class R1KellyStresTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.B = birimler_kur()
        cls.h = H.hukum(cls.B, HB)

    def test_r1(self):
        r1 = self.h['R1']
        self.assertEqual(len(r1), len(ayar.NAV_IZGARA) * len(ayar.MALIYET))
        self.assertEqual(r1['100000|1'], 1.2)
        self.assertEqual(r1['100000|2'], 0.6)
        self.assertEqual(r1['5000000|3'], 1.0 + 0.5 + 3.0)

    def test_kelly_stres_sekli(self):
        ks = self.h['kelly_stres']
        self.assertEqual(set(ks), {1, 2})
        n_dahil = (BSON - T0) // G - 2                                              # birincilde 2 görülmüş gün
        aileler = {f'{a}-{k}' for a, s in stres.SIKLIK.items() for k in s}
        for m, v in ks.items():
            satir = v['kelly']['satirlar']
            self.assertEqual(set(satir), set(ayar.KELLY_L))
            for L, x in satir.items():
                self.assertGreater(x['en_kotu_gun'], -0.5)                          # görülmüş gün şoku dışarıda
                self.assertEqual(round(x['bootstrap']['p_asim'] * HB.kelly_cekis, 9) % 1, 0.0)   # çekiş = 10
            self.assertEqual(set(v['stres']), set(ayar.KELLY_L))
            for L, st in v['stres'].items():
                self.assertEqual(set(st), aileler)
                self.assertTrue(all(math.isfinite(z['mdd']) for z in st.values()))
                self.assertEqual(st['DM-1']['olay'] + st['DM-1']['bos_olay'], len(stres.bloklar(n_dahil + 2, 1)))

    def test_stres_nesnesi_sekli_denetlenir(self):
        B = dict(self.B)
        u = dict(B[ad(grup='kelly', mimari='A', L=2.0, maliyet_k=1.0)])
        u['stres_nesneleri'] = dict(u['stres_nesneleri'], SQ=u['stres_nesneleri']['SQ'][:-1])
        B[ad(grup='kelly', mimari='A', L=2.0, maliyet_k=1.0)] = u
        with self.assertRaises(H.HukumHatasi):
            H.kelly_ve_stres(B, HB)

    def test_hukum_alanlari(self):
        self.assertEqual(set(self.h), {'olcutler', 'karar', 'birincil_sr', 'R1', 'R3', 'kelly_stres'})
        self.assertEqual(self.h['R3']['nw_gecikme'], 10)


def sahte_bag():
    return {}


def sahte_yurut(b, bag):
    duz = {'birim': b, 'sr': int(hashlib.sha256(K.kanonik(b)).hexdigest()[:6], 16) / 2 ** 24}
    if b['grup'] == 'birincil':
        duz['olcum'] = {'alt_katki_sirasi': [f'ZZ{i:02d}' for i in range(12)]}
    return duz, {}


class BirimleriCozTest(unittest.TestCase):
    def setUp(self):
        self.d = _Path(tempfile.mkdtemp(prefix='hukum_coz_'))
        self.kimlik, self.alici = age.anahtar_uret()
        self.taban = [ayar._birim('birincil', 'A'), ayar._birim('izgara', 'A', nav0=1e6, maliyet_k=2.0)]
        K.calistir(self.d, self.taban, {'motor': 'm'}, self.alici, sahte_yurut, sahte_bag, sessiz=True)
        self.damga = K.damga_yaz(self.d, self.taban)

    def tearDown(self):
        shutil.rmtree(self.d, ignore_errors=True)

    def _damga_yaz(self, satirlar):
        d = dict(self.damga, birimler=satirlar, kok_sha256=K.sha(K.kanonik(satirlar)))
        (self.d / 'SONUC_DAMGA.json').write_text(json.dumps(d), encoding='ascii')

    def test_cozer_ve_kok_denetler(self):
        out = H.birimleri_coz(self.d, self.kimlik, beklenen_kok=self.damga['kok_sha256'])
        self.assertEqual(len(out), 12)
        self.assertEqual(out['birincil_A']['birim'], self.taban[0])
        with self.assertRaises(H.HukumHatasi):
            H.birimleri_coz(self.d, self.kimlik, beklenen_kok='0' * 64)

    def test_sifreli_dosya_degisirse(self):
        yol = self.d / 'sonuc' / 'birim' / 'izgara_A_n1000000_k2.age'
        yol.write_bytes(yol.read_bytes() + b'x')
        with self.assertRaises(H.HukumHatasi):
            H.birimleri_coz(self.d, self.kimlik)

    def test_duz_metin_degisirse(self):
        # Şifreli dosya başka bir düz metinle yeniden üretilip damga (şifreli sha + kök) buna göre güncellense de
        # düz sha damgadaki kalır: yakalanır.
        ad_ = 'izgara_A_n1000000_k2'
        yeni = age.sifrele(self.alici, K.kanonik({'birim': 'sahte', 'sr': 9.9}))
        (self.d / 'sonuc' / 'birim' / f'{ad_}.age').write_bytes(yeni)
        satirlar = [[a, dz, K.sha(yeni) if a == ad_ else sf] for a, dz, sf in self.damga['birimler']]
        self._damga_yaz(satirlar)
        with self.assertRaises(H.HukumHatasi) as h:
            H.birimleri_coz(self.d, self.kimlik)
        self.assertIn('duz metin', str(h.exception))

    def test_damga_ic_tutarlilik_ve_eksik_dosya(self):
        satirlar = [list(x) for x in self.damga['birimler']]
        satirlar[0][1] = '0' * 64
        d = dict(self.damga, birimler=satirlar)                                     # kök güncellenmedi
        (self.d / 'SONUC_DAMGA.json').write_text(json.dumps(d), encoding='ascii')
        with self.assertRaises(H.HukumHatasi):
            H.birimleri_coz(self.d, self.kimlik)
        self._damga_yaz([list(x) for x in self.damga['birimler']])
        (self.d / 'sonuc' / 'birim' / 'birincil_A.age').unlink()
        with self.assertRaises(H.HukumHatasi) as h:
            H.birimleri_coz(self.d, self.kimlik)
        self.assertIn('sifreli dosya yok', str(h.exception))


if __name__ == '__main__':
    unittest.main()
