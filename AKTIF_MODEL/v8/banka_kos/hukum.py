"""Banka hükmü (BANKA §2.4, §3.3, §3.4, §4, §5.4; BK-3). Denetim listesi (T1–T5) tamamlanıp kullanıcı şifreyi çözdükten
sonra koşar. Çözülmüş her birimin düz metin sha256'sı SONUC_DAMGA.json'daki değerle aynı olmalıdır (aksi T1). Hesap
mekaniktir ve deterministiktir; eşikler kilitten/dondurmadan gelir (kalibrasyon.duzey1_esik.Kurallar).

Bağlayıcı ölçütler (birincil ayar ve birincil örneklem; görülmüş günler düşülmüş):
  B2 DSR ≥ d* (bağlıysa; N_hüküm, σ_SR_bağ)      B3 ×2 SR ≥ b3_esik ve ×3 SR > 0      B4 en iyi dilim hariç SR ≥ b4_esik
  B5 en iyi 3 epizot payı < e_B5 (bağlıysa)       B6 SR > 0 olan Z1 dilimi ≥ k_B6      B7 SR > null q95 (⌈0,95 n⌉'inci)
  B8 fiyat bileşeni SR > 0                         B9 K alt katkısı SR > 0 ([T0_Z1, 2023-06-24) ∪ Z2)
  B10 en büyük SR düşüşü < e_B10 (bağlıysa)        B11 vol ölçekli MDD ≤ %30
Karar: hepsi geçerse KABUL, biri kalırsa RET (teknik geçerlilik ayrı; §2.5).
T1 (birimleri_coz): damganın kök hash'i ve birim sayısı kendi satırlarıyla (ve verilirse itilmiş damganın kök hash'iyle)
tutmalı; her birimin şifreli dosyası ve çözülmüş düz metni damgadaki sha256'larla aynı olmalı; eksik dosya hatadır.
"""
import hashlib
import json
from dataclasses import dataclass
from pathlib import Path

import numpy as np

from banka import olcutler as o
from kalibrasyon.duzey1_esik import B11_ESIK, Kurallar
from kalibrasyon.toplama import b7_gecer

from . import age, ayar, kelly, long_beta, stres
from .kosucu import birim_adi, kanonik

GUN_MS = 86_400_000
B7_ALFA = 0.95


class HukumHatasi(RuntimeError):
    """T1: çözülmüş birim damgayla tutmuyor ya da birim eksik."""


@dataclass(frozen=True)
class HukumBaglami:
    mimari: str
    t0_z1_ms: int
    gorulmus_gunler: tuple
    tohum_banka: int
    kurallar: Kurallar
    N_hukum: int
    birincil_son_ms: int = ayar.BIRINCIL_SON_MS
    z2_bas_ms: int = ayar.Z2_BAS_MS
    z2_son_ms: int = ayar.Z2_SON_MS
    d_bas_ms: int = ayar.D_BAS_MS              # R10 D segmenti (rapor)
    z1_dilim_sinir: tuple = ayar.Z1_DILIM_SINIR   # R2 dilimleri
    d_bit_ms: int = ayar.D_BIT_MS
    kelly_cekis: int = kelly.CEKIS             # Kelly MDD bootstrap çekiş sayısı (§4: 2.000; testlerde küçük)


def birimleri_coz(cikti, kimlik: str, beklenen_kok: str = None) -> dict:
    """SONUC_DAMGA.json'daki her birim çözülür; düz sha damgayla aynı olmalı. Doner {ad: düz sözlük}.
    beklenen_kok: denetim sırasında itilmiş damganın kök sha256'sı (verilirse yerel damga onunla aynı olmalı)."""
    cikti = Path(cikti)
    damga = json.loads((cikti / 'SONUC_DAMGA.json').read_text(encoding='ascii'))
    satirlar = damga['birimler']
    if hashlib.sha256(kanonik(satirlar)).hexdigest() != damga['kok_sha256'] or damga['birim_sayisi'] != len(satirlar):
        raise HukumHatasi("damga kendi icinde tutarsiz (kok hash ya da birim sayisi)")
    if beklenen_kok is not None and damga['kok_sha256'] != beklenen_kok:
        raise HukumHatasi("damga itilmis damgayla ayni degil")
    if len({ad for ad, _, _ in satirlar}) != len(satirlar):
        raise HukumHatasi("damgada tekrarlanan birim")
    out = {}
    for ad, duz_sha, sifreli_sha in satirlar:
        yol = cikti / 'sonuc' / 'birim' / f'{ad}.age'
        if not yol.is_file():
            raise HukumHatasi(f"{ad}: sifreli dosya yok")
        sifreli = yol.read_bytes()
        if hashlib.sha256(sifreli).hexdigest() != sifreli_sha:
            raise HukumHatasi(f"{ad}: sifreli dosya damgayla tutmuyor")
        duz = age.coz(kimlik, sifreli)
        if hashlib.sha256(duz).hexdigest() != duz_sha:
            raise HukumHatasi(f"{ad}: duz metin damgayla tutmuyor")
        out[ad] = json.loads(duz)
    return out


def gunluk_getiri(duz: dict, bas_ms: int, bit_ms: int, haric=()) -> tuple:
    """Birimin gün sınırı NAV'ından [bas, bit) günlerinin basit getirisi; haric günler düşülür. Doner (r, gün damgaları)."""
    nav = np.asarray(duz['nav_gunluk'], dtype=float)
    i0 = (bas_ms - duz['nav_bas_ms']) // GUN_MS
    i1 = (bit_ms - duz['nav_bas_ms']) // GUN_MS
    if i0 < 0 or i1 >= len(nav) or i1 <= i0:
        raise HukumHatasi("NAV serisi pencereyi kapsamiyor")
    r = nav[i0 + 1:i1 + 1] / nav[i0:i1] - 1.0
    g = duz['nav_bas_ms'] + np.arange(i0, i1, dtype=np.int64) * GUN_MS
    m = ~np.isin(g, np.asarray(haric, dtype=np.int64))
    return r[m], g[m]


def _birim(birimler: dict, **k) -> dict:
    ad = birim_adi(ayar._birim(**k))
    if ad not in birimler:
        raise HukumHatasi(f"birim eksik: {ad}")
    return birimler[ad]


def olcutler(birimler: dict, hb: HukumBaglami) -> dict:
    k, M = hb.kurallar, hb.mimari
    b = _birim(birimler, grup='birincil', mimari=M)
    ol = b['olcum']
    out = {}
    d = o.dsr(ol['r'], hb.N_hukum, k.sigma_sr)
    out['B2'] = {'dsr': d['dsr'], 'sr0': d['sr0'], 'd': k.d, 'bagli': k.b2_bagli, 'g3': d['g3'], 'g4': d['g4'],
                 'eta': d['eta'], 'T': d['T'],
                 'gecti': bool(d['dsr'] >= k.d) if k.b2_bagli else None}
    x2 = _birim(birimler, grup='izgara', mimari=M, nav0=ayar.NAV_BIRINCIL, maliyet_k=2.0)['olcum']['sr']
    x3 = _birim(birimler, grup='izgara', mimari=M, nav0=ayar.NAV_BIRINCIL, maliyet_k=3.0)['olcum']['sr']
    out['B3'] = {'sr_x2': x2, 'sr_x3': x3, 'gecti': bool(x2 >= k.b3_esik and x3 > 0)}
    out['B4'] = {'sr': ol['b4_sr'], 'esik': k.b4_esik, 'gecti': bool(ol['b4_sr'] >= k.b4_esik)}
    out['B5'] = {'pay': ol['b5_pay'], 'esik': k.e_b5, 'bagli': k.e_b5 is not None,
                 'gecti': bool(ol['b5_pay'] < k.e_b5) if k.e_b5 is not None else None}
    pozitif = int(sum(1 for x in ol['dilim_sr'] if x == x and x > 0))
    out['B6'] = {'dilim_sr': ol['dilim_sr'], 'pozitif': pozitif, 'k': k.k_b6, 'gecti': pozitif >= k.k_b6}
    nuller = [v['sr'] for ad, v in birimler.items() if ad.startswith(f'null_{M}_p')]
    if len(nuller) != ayar.N_NULL:
        raise HukumHatasi(f"null birim sayisi {len(nuller)}")
    out['B7'] = {'sr': ol['sr'], 'q95': float(np.sort(nuller)[int(np.ceil(B7_ALFA * len(nuller))) - 1]),
                 'gecti': b7_gecer(ol['sr'], nuller, B7_ALFA)}
    out['B8'] = {'sr': ol['b8_sr'], 'gecti': bool(ol['b8_sr'] > 0)}
    kv = _birim(birimler, grup='k_evren', mimari=M, evren='K')
    g = kv['nav_bas_ms'] + np.arange(len(kv['b9_seri']), dtype=np.int64) * GUN_MS
    pencere = (((g >= hb.t0_z1_ms) & (g < hb.birincil_son_ms)) | ((g >= hb.z2_bas_ms) & (g < hb.z2_son_ms)))
    pencere &= ~np.isin(g, np.asarray(hb.gorulmus_gunler, dtype=np.int64))
    b9 = o.sharpe(np.asarray(kv['b9_seri'], dtype=float)[pencere])
    out['B9'] = {'sr': b9, 'gun': int(pencere.sum()), 'gecti': bool(b9 > 0)}
    cik = [v['olcum']['sr'] for ad, v in sorted(birimler.items()) if ad.startswith(f'cikarma_{M}_s')]
    if len(cik) != ayar.B10_N:
        raise HukumHatasi(f"B10 birim sayisi {len(cik)}")
    dusus = o.en_buyuk_dusus(ol['sr'], cik)
    out['B10'] = {'en_buyuk_dusus': dusus, 'esik': k.e_b10, 'bagli': k.e_b10 is not None,
                  'gecti': bool(dusus < k.e_b10) if k.e_b10 is not None else None}
    out['B11'] = {'mdd': ol['b11_mdd'], 'gecti': bool(ol['b11_mdd'] <= B11_ESIK)}
    bagli = [x for x in out.values() if x['gecti'] is not None]
    return {'olcutler': out, 'karar': 'KABUL' if all(x['gecti'] for x in bagli) else 'RET', 'birincil_sr': ol['sr']}


def r1_izgarasi(birimler: dict, hb: HukumBaglami) -> dict:
    out = {}
    for n in ayar.NAV_IZGARA:
        for m in ayar.MALIYET:
            u = (_birim(birimler, grup='birincil', mimari=hb.mimari) if (n == ayar.NAV_BIRINCIL and m == 1.0) else
                 _birim(birimler, grup='izgara', mimari=hb.mimari, nav0=n, maliyet_k=m))
            out[f'{int(n)}|{int(m)}'] = u['olcum']['sr']
    return out


def _kelly_birimi(birimler, hb, L, m):
    if L == 1.0:
        if m == 1.0:
            return _birim(birimler, grup='birincil', mimari=hb.mimari)
        return _birim(birimler, grup='izgara', mimari=hb.mimari, nav0=ayar.NAV_BIRINCIL, maliyet_k=m)
    return _birim(birimler, grup='kelly', mimari=hb.mimari, L=L, maliyet_k=m)


def kelly_ve_stres(birimler: dict, hb: HukumBaglami) -> dict:
    """Her maliyet için Kelly tablosu (§4) ve her L için stres altında MDD (§5.4)."""
    out = {}
    for m in ayar.KELLY_MALIYET:
        r_L, stres_L, gunler = {}, {}, None
        for L in ayar.KELLY_L:
            u = _kelly_birimi(birimler, hb, L, m)
            r_tam, g_tam = gunluk_getiri(u, hb.t0_z1_ms, hb.birincil_son_ms)
            dahil = ~np.isin(g_tam, np.asarray(hb.gorulmus_gunler, dtype=np.int64))
            r_L[L] = r_tam[dahil]
            gunler = g_tam[dahil]
            nes = {a: np.asarray(v, dtype=float) for a, v in u['stres_nesneleri'].items()}
            if set(nes) != set(stres.SIKLIK) or any(v.shape != r_tam.shape for v in nes.values()):
                raise HukumHatasi("stres nesneleri birincil orneklem gunleriyle ayni sekilde degil")
            satir = {}
            for aile, siklar in stres.SIKLIK.items():
                for kk in siklar:
                    b = stres.bindir(r_tam, nes[aile], aile, kk, dahil)
                    satir[f'{aile}-{kk}'] = {'mdd': o.mdd(np.concatenate(([1.0], np.cumprod(1 + b['r'][dahil])))),
                                             'olay': len(b['olay_gunleri']), 'bos_olay': b['bos_olay']}
            stres_L[L] = satir
        out[int(m)] = {'kelly': kelly.kelly_tablosu(r_L, gunler, hb.tohum_banka, m, cekis=hb.kelly_cekis),
                       'stres': stres_L}
    return out


def r3_satiri(birimler: dict, hb: HukumBaglami) -> dict:
    """R3 (betimsel; §3.4, §3.7 netleştirme 13 g): birincil örneklem, görülmüş günler hariç; birincil ile long-beta
    kitabının aynı günlerdeki getirileri."""
    b = _birim(birimler, grup='birincil', mimari=hb.mimari)
    r3 = _birim(birimler, grup='long_beta', mimari=hb.mimari)
    rp, gp = gunluk_getiri(b, hb.t0_z1_ms, hb.birincil_son_ms, hb.gorulmus_gunler)
    rr, gr = gunluk_getiri(r3, hb.t0_z1_ms, hb.birincil_son_ms, hb.gorulmus_gunler)
    if not np.array_equal(gp, gr):
        raise HukumHatasi("R3 ve birincil ayni gunleri tasimiyor")
    return long_beta.r3_karsilastirma(rp, rr)


def hukum(birimler: dict, hb: HukumBaglami) -> dict:
    sonuc = olcutler(birimler, hb)
    sonuc['R1'] = r1_izgarasi(birimler, hb)
    sonuc['R3'] = r3_satiri(birimler, hb)
    sonuc['kelly_stres'] = kelly_ve_stres(birimler, hb)
    return sonuc
