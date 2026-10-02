"""Banka rapor satırları, 1. parça (BANKA §3.1, §3.4 R9–R13, R16; 6.08). Hükümden sonra, çözülmüş birimlerden hesaplanır;
betimseldir, karara girmez. Görülmüş günler bütün metriklerden düşülür (BK-5).

- Sharpe güven aralığı (§3.1): durağan blok bootstrap (Politis–Romano; ortalama blok 20 gün, dairesel; kelly.duragan_indeksler),
  2.000 çekiş, çekiş uzunluğu = örneklem uzunluğu, %90 yüzdelik aralık (q05, q95). Tohum uretec(tohum_banka, 'sr', etiket);
  etiket birimin adıdır (ve varsa satır/pencere adı), böylece her aralık kendi deterministik akışını kullanır.
- R9: delist uzlaşma senaryoları (h_L = %50, %90) birimlerinin birincil örneklem SR'ı, GA, MDD ve birincilden farkı.
- R10: Z2 ve D segmenti için tam metrik seti (kelly.metrikler + SR GA); hüküm dışı.
- R11: birincil SR, %90 GA ve 0,50'yi geçip geçmediği (bilgi).
- R12: birincil ayarda (L = 1, 1×) D90-1/2/4, SQ-1/2/4, DM-1 bindirmeleri altında SR ve MDD (§5.4).
- R13 (a): lot kapalı koşunun birincil SR'dan farkı. (b) "bugünkü adımın erken fiyat düzeyindeki nominali" veri ister;
  rapor şablonunda (6.09) veri yükleyiciyle (6.01b) hesaplanır.
- R5, R6, R7: birincil birimin koşu tanıları (banka_kos/tanilar.py; netleştirme 14); R14: demo NAV biriminin tanısı.
- 3. parça (netleştirme 15): R2 beta ayrıştırması (birincilin piyasa serileriyle; tüm dilimler), R4 REV1 korelasyonu
  (dışarıdan verilen D dönemi serisi), R13 (b) adım nominali, R15 B9'un D kısmı, R17 null tanıları.
- R16: DSR duyarlılığı: σ_SR ∈ {0,20; 0,30; 0,50} ve σ_SR_bağ; η kestirimli (gecikme 10) ve η = 1; N_hüküm, ×0,8 ve ×1,2
  (en yakın tamsayı, ≥ 2). σ̂_REV1 yoksa satırı yazılmaz (§11).
"""
import math

import numpy as np

from banka import olcutler as o

from . import ayar, kelly, stres
from .hukum import GUN_MS, HukumHatasi, _birim, gunluk_getiri

CEKIS = kelly.CEKIS
SIGMA_IZGARA = (0.20, 0.30, 0.50)
N_CARPAN = (0.8, 1.0, 1.2)
R11_ESIK = 0.50


def sr_ga(r, tohum_banka: int, etiket: str, cekis: int = CEKIS) -> dict:
    """SR ve durağan blok bootstrap %90 aralığı (q05, q95)."""
    from kalibrasyon.tohum import uretec
    r = np.asarray(r, dtype=float)
    sr = o.sharpe(r)
    if len(r) < 2 or not math.isfinite(sr):
        return {'sr': sr, 'q05': float('nan'), 'q95': float('nan'), 'cekis': 0}
    rng = uretec(tohum_banka, 'sr', etiket)
    s = np.array([o.sharpe(r[kelly.duragan_indeksler(len(r), len(r), rng)]) for _ in range(cekis)])
    s = s[np.isfinite(s)]
    return {'sr': sr, 'q05': float(np.quantile(s, 0.05)), 'q95': float(np.quantile(s, 0.95)), 'cekis': int(len(s))}


def _pencere(u: dict, bas_ms: int, bit_ms: int, haric) -> tuple:
    return gunluk_getiri(u, bas_ms, bit_ms, haric)


def _metrik(u: dict, bas_ms: int, bit_ms: int, hb, etiket: str, cekis: int) -> dict:
    try:
        r, g = _pencere(u, bas_ms, bit_ms, hb.gorulmus_gunler)
    except HukumHatasi as h:
        return {'hata': str(h)}
    m = kelly.metrikler(r, g)
    m['ga'] = sr_ga(r, hb.tohum_banka, etiket, cekis)
    m['gun'] = int(len(r))
    return m


def r9_delist(birimler: dict, hb, cekis: int = CEKIS) -> dict:
    b = _birim(birimler, grup='birincil', mimari=hb.mimari)
    sr_b = b['olcum']['sr']
    out = {}
    for h in ayar.DELIST_H_L:
        u = _birim(birimler, grup='delist', mimari=hb.mimari, h_L=h)
        m = _metrik(u, hb.t0_z1_ms, hb.birincil_son_ms, hb, f'delist_{hb.mimari}_{h}', cekis)
        m['sr_farki'] = m.get('sr', float('nan')) - sr_b
        out[f'{h:.2f}'] = m
    return out


def r10_segmentler(birimler: dict, hb, cekis: int = CEKIS) -> dict:
    b = _birim(birimler, grup='birincil', mimari=hb.mimari)
    return {'Z2': _metrik(b, hb.z2_bas_ms, hb.z2_son_ms, hb, f'birincil_{hb.mimari}_Z2', cekis),
            'D': _metrik(b, hb.d_bas_ms, hb.d_bit_ms, hb, f'birincil_{hb.mimari}_D', cekis)}


def r11_birincil(birimler: dict, hb, cekis: int = CEKIS) -> dict:
    b = _birim(birimler, grup='birincil', mimari=hb.mimari)
    ga = sr_ga(b['olcum']['r'], hb.tohum_banka, f'birincil_{hb.mimari}', cekis)
    return dict(ga, esik=R11_ESIK, esik_ustu=bool(ga['sr'] >= R11_ESIK))


def r12_kanal_stresleri(birimler: dict, hb, cekis: int = CEKIS) -> dict:
    b = _birim(birimler, grup='birincil', mimari=hb.mimari)
    r_tam, g_tam = gunluk_getiri(b, hb.t0_z1_ms, hb.birincil_son_ms)
    dahil = ~np.isin(g_tam, np.asarray(hb.gorulmus_gunler, dtype=np.int64))
    nes = {a: np.asarray(v, dtype=float) for a, v in b['stres_nesneleri'].items()}
    if set(nes) != set(stres.SIKLIK) or any(v.shape != r_tam.shape for v in nes.values()):
        raise HukumHatasi("stres nesneleri birincil orneklem gunleriyle ayni sekilde degil")
    out = {'stressiz': {'sr': o.sharpe(r_tam[dahil]), 'mdd': o.mdd(kelly._nav(r_tam[dahil])),
                        'ga': sr_ga(r_tam[dahil], hb.tohum_banka, f'r12_{hb.mimari}_stressiz', cekis)}}
    for aile, siklar in stres.SIKLIK.items():
        for k in siklar:
            s = stres.bindir(r_tam, nes[aile], aile, k, dahil)
            rs = s['r'][dahil]
            out[f'{aile}-{k}'] = {'sr': o.sharpe(rs), 'mdd': o.mdd(kelly._nav(rs)), 'olay': len(s['olay_gunleri']),
                                  'bos_olay': s['bos_olay'],
                                  'ga': sr_ga(rs, hb.tohum_banka, f'r12_{hb.mimari}_{aile}-{k}', cekis)}
    return out


def r13_lot(birimler: dict, hb) -> dict:
    b = _birim(birimler, grup='birincil', mimari=hb.mimari)
    u = _birim(birimler, grup='lot_kapali', mimari=hb.mimari, lot=False)
    return {'sr_birincil': b['olcum']['sr'], 'sr_lot_kapali': u['olcum']['sr'],
            'sr_farki': b['olcum']['sr'] - u['olcum']['sr']}


def r16_dsr(birimler: dict, hb, sigma_rev1: float = None) -> dict:
    b = _birim(birimler, grup='birincil', mimari=hb.mimari)
    r = b['olcum']['r']
    sigmalar = {f'{s:.2f}': s for s in SIGMA_IZGARA}
    sigmalar['bag'] = hb.kurallar.sigma_sr
    if sigma_rev1 is not None:
        sigmalar['rev1'] = sigma_rev1
    out = {}
    for ad, s in sigmalar.items():
        for c in N_CARPAN:
            N = max(2, int(round(hb.N_hukum * c)))
            for eta_ad, gecikme in (('eta', 10), ('eta1', 0)):
                d = o.dsr(r, N, s, gecikme=gecikme)
                out[f'{ad}|{c}|{eta_ad}'] = {'sigma_sr': s, 'N': N, 'sr0': d['sr0'], 'dsr': d['dsr'], 'eta': d['eta']}
    return out


def kosu_tanilari(birimler: dict, hb) -> dict:
    b = _birim(birimler, grup='birincil', mimari=hb.mimari)
    d = _birim(birimler, grup='demo_nav', mimari=hb.mimari, nav0=ayar.DEMO_NAV)
    if 'tanilar' not in b or 'r14' not in d:
        raise HukumHatasi("birincil tanilari ya da demo NAV R14 tanisi yok")
    return {**b['tanilar'], 'R14': d['r14']}


def nw_regresyon(y, X, gecikme: int = 10) -> dict:
    """y = X b + e (X sabit sütunu içermez; eklenir). OLS katsayıları ve Newey-West (Bartlett) t değerleri."""
    y = np.asarray(y, dtype=float)
    X = np.column_stack([np.ones(len(y))] + [np.asarray(x, dtype=float) for x in X])
    n, k = X.shape
    if n <= k + 1:
        return {'n': int(n), 'katsayi': [float('nan')] * k, 't': [float('nan')] * k}
    xtx_inv = np.linalg.pinv(X.T @ X)
    b = xtx_inv @ X.T @ y
    u = X * (y - X @ b)[:, None]
    S = u.T @ u
    for j in range(1, min(gecikme, n - 1) + 1):
        G = u[j:].T @ u[:-j]
        S += (1.0 - j / (gecikme + 1)) * (G + G.T)
    se = np.sqrt(np.maximum(np.diag(xtx_inv @ S @ xtx_inv), 0.0))
    return {'n': int(n), 'katsayi': [float(x) for x in b],
            't': [float(b[i] / se[i]) if se[i] > 0 else float('nan') for i in range(k)]}


def _seri(duz: dict, ad: str, gunler) -> np.ndarray:
    p = duz['piyasa']
    x = np.array([np.nan if v is None else v for v in p[ad]], dtype=float)
    i = (np.asarray(gunler, dtype=np.int64) - p['bas_ms']) // GUN_MS
    return x[i]


def r2_beta(birimler: dict, hb) -> dict:
    b = _birim(birimler, grup='birincil', mimari=hb.mimari)
    s = (hb.t0_z1_ms,) + tuple(hb.z1_dilim_sinir) + (hb.birincil_son_ms,)
    pencereler = {'birincil': (hb.t0_z1_ms, hb.birincil_son_ms)}
    pencereler.update({f'dilim{i + 1}': (s[i], s[i + 1]) for i in range(len(s) - 1)})
    out = {}
    for ad, (a, z) in pencereler.items():
        r, g = gunluk_getiri(b, a, z, hb.gorulmus_gunler)
        rb, ra = _seri(b, 'r_btc', g), _seri(b, 'r_alt', g)
        m = np.isfinite(rb) & np.isfinite(ra)
        reg = nw_regresyon(r[m], [rb[m], (ra - rb)[m]])
        bk, ak = _seri(b, 'btc_katki', g), _seri(b, 'artik_katki', g)
        out[ad] = {'n': reg['n'], 'alfa': reg['katsayi'][0], 'beta_btc': reg['katsayi'][1], 'beta_d': reg['katsayi'][2],
                   't_alfa': reg['t'][0], 't_btc': reg['t'][1], 't_d': reg['t'][2],
                   'btc_katki_yillik': 365.0 * float(np.nanmean(bk)) if len(bk) else float('nan'),
                   'artik_katki_yillik': 365.0 * float(np.nanmean(ak)) if len(ak) else float('nan')}
    out['beta_yok_coin'] = b['piyasa']['beta_yok']
    return out


R4_BLOK_GUN = 30
R4_BLOK_EN_AZ = 25


def r4_rev1(birimler: dict, hb, rev1: dict = None) -> dict:
    """rev1: {'seri': {gün_ms: getiri}, 'dosya': ad, 'sha256': ...} ya da None. Netleştirme 15 c ve 17 e: D başından
    30 takvim günlük bloklar (blokta ortak ve görülmemiş ≥ 25 gün); stres eşiği D'nin bütün görülmemiş günlerindeki
    r_BTC'nin %5 yüzdeliği (REV1 ortaklığından önce)."""
    if not rev1:
        return {'durum': 'REV1 serisi yok'}
    b = _birim(birimler, grup='birincil', mimari=hb.mimari)
    r, g = gunluk_getiri(b, hb.d_bas_ms, hb.d_bit_ms, hb.gorulmus_gunler)
    rb_d = _seri(b, 'r_btc', g)
    ok_d = np.isfinite(rb_d)
    esik = float(np.quantile(rb_d[ok_d], 0.05)) if ok_d.any() else float('nan')
    seri = {int(k): float(v) for k, v in rev1['seri'].items()}
    m = np.array([int(x) in seri for x in g.tolist()], dtype=bool)
    rv, rp, gg, rb = np.array([seri[int(x)] for x in g[m].tolist()]), r[m], g[m], rb_d[m]

    def kor(a, c):
        return float(np.corrcoef(a, c)[0, 1]) if len(a) > 2 and np.std(a) > 0 and np.std(c) > 0 else float('nan')
    blok = (gg - hb.d_bas_ms) // (R4_BLOK_GUN * GUN_MS)
    ay_p, ay_v, dusen = [], [], 0
    for j in range(int((hb.d_bit_ms - hb.d_bas_ms) // (R4_BLOK_GUN * GUN_MS)) + 1):
        ic = blok == j
        if not ic.any():
            continue
        if ic.sum() < R4_BLOK_EN_AZ:
            dusen += 1
            continue
        ay_p.append(float(np.prod(1 + rp[ic]) - 1))
        ay_v.append(float(np.prod(1 + rv[ic]) - 1))
    st = np.isfinite(rb) & (rb <= esik)
    return {'dosya': rev1.get('dosya'), 'sha256': rev1.get('sha256'), 'ortak_gun': int(len(rp)),
            'gunluk': kor(rp, rv), 'otuz_gunluk': kor(np.array(ay_p), np.array(ay_v)), 'otuz_gunluk_n': len(ay_p),
            'otuz_gunluk_dusen_blok': dusen, 'stres_esigi_btc': esik, 'stres': kor(rp[st], rv[st]),
            'stres_gun': int(st.sum())}


def r13b_adim(birimler: dict, hb) -> dict:
    return _birim(birimler, grup='birincil', mimari=hb.mimari)['r13b']


def r15_b9_d(birimler: dict, hb, cekis: int = CEKIS) -> dict:
    kv = _birim(birimler, grup='k_evren', mimari=hb.mimari, evren='K')
    g = kv['nav_bas_ms'] + np.arange(len(kv['b9_seri']), dtype=np.int64) * GUN_MS
    m = (g >= hb.d_bas_ms) & (g < hb.d_bit_ms) & ~np.isin(g, np.asarray(hb.gorulmus_gunler, dtype=np.int64))
    x = np.asarray(kv['b9_seri'], dtype=float)[m]
    return dict(sr_ga(x, hb.tohum_banka, f'k_evren_{hb.mimari}_D', cekis), gun=int(m.sum()), etiket='görülmüş zaman')


def r17_null(birimler: dict, hb) -> dict:
    b = _birim(birimler, grup='birincil', mimari=hb.mimari)
    nuller = [v['r17'] for ad, v in sorted(birimler.items()) if ad.startswith(f'null_{hb.mimari}_p') and 'r17' in v]
    if len(nuller) != ayar.N_NULL:
        raise HukumHatasi(f"R17: null tanisi {len(nuller)} birimde")
    out = {}
    for a in ('maske_gunu', 'dolgu_saati', 'bosluk_saati', 'evren_ort', 'ortak_pay'):
        x = np.array([n[a] for n in nuller if n.get(a) is not None], dtype=float)
        out[a] = {'gercek': b['r17'].get(a), 'null_ort': float(np.mean(x)) if len(x) else float('nan'),
                  'null_q5': _qq(x, 0.05), 'null_q95': _qq(x, 0.95)}
    return out


def _qq(x, a):
    return float(np.quantile(x, a)) if len(x) else float('nan')


def _pencere_serisi(duz: dict, x, hb) -> np.ndarray:
    """[T0_Z1, Z2_son) günlük dizisinden birincil örneklem günleri, görülmüş günler hariç."""
    x = np.asarray(x, dtype=float)
    g = duz['nav_bas_ms'] + np.arange(len(x), dtype=np.int64) * GUN_MS
    m = (g >= hb.t0_z1_ms) & (g < hb.birincil_son_ms) & ~np.isin(g, np.asarray(hb.gorulmus_gunler, dtype=np.int64))
    return x[m], g[m]


def r8_b(birimler: dict, hb, cekis: int = CEKIS) -> dict:
    """Netleştirme 16: yalnız M = B."""
    from .tanilar import R8_SATIRLARI, carry_bacagi, trend_bacagi
    if hb.mimari != 'B':
        return {'durum': 'M = A: R8 yok'}
    b = _birim(birimler, grup='birincil', mimari='B')
    sat = b['r8_satirlar']
    out = {'satir_yillik': {sa: 365.0 * float(np.mean(_pencere_serisi(b, sat[sa], hb)[0])) for sa in R8_SATIRLARI}}
    out['trend_bacagi'] = sr_ga(_pencere_serisi(b, trend_bacagi(sat), hb)[0], hb.tohum_banka, 'r8_trend_B', cekis)
    out['carry_bacagi'] = sr_ga(_pencere_serisi(b, carry_bacagi(sat), hb)[0], hb.tohum_banka, 'r8_carry_B', cekis)
    a = _birim(birimler, grup='a_ayristirma', mimari='A')
    ga = sr_ga(a['olcum']['r'], hb.tohum_banka, 'a_ayristirma_A', cekis)
    out['bagimsiz_A'] = dict(ga, b5_pay=a['olcum'].get('b5_pay'), sr_farki_B_eksi_A=b['olcum']['sr'] - ga['sr'])
    kelly = {}
    for L in ayar.KELLY_L:
        u = b if L == 1.0 else _birim(birimler, grup='kelly', mimari='B', L=L, maliyet_k=1.0)
        seri = carry_bacagi(sat) if L == 1.0 else u['r8_carry']
        rc, g = _pencere_serisi(b, seri, hb)
        rb, ra = _seri(b, 'r_btc', g), _seri(b, 'r_alt', g)
        m = np.isfinite(rb) & np.isfinite(ra)
        reg = nw_regresyon(rc[m], [rb[m], (ra - rb)[m]])
        kelly[f'{L:g}'] = {'n': reg['n'], 'beta_btc': reg['katsayi'][1], 'beta_d': reg['katsayi'][2],
                           't_btc': reg['t'][1], 't_d': reg['t'][2]}
    out['kelly_carry_beta'] = kelly
    out['carry_epizot'] = b.get('r8_carry_epizot')                    # netleştirme 16 d
    return out


def sharpe_ga_tablosu(birimler: dict, hb, cekis: int = CEKIS) -> dict:
    """Netleştirme 17 h: §3.1 "her Sharpe için %90 GA" — serisi birim çıktısında bulunan bütün Sharpe'lar."""
    M, h = hb.mimari, tuple(hb.gorulmus_gunler)
    b = _birim(birimler, grup='birincil', mimari=M)
    out = {'B7_birincil': sr_ga(b['olcum']['r'], hb.tohum_banka, f'birincil_{M}', cekis)}
    r, g = gunluk_getiri(b, hb.t0_z1_ms, hb.birincil_son_ms, h)
    s = (hb.t0_z1_ms,) + tuple(hb.z1_dilim_sinir) + (hb.birincil_son_ms,)
    etiket = np.searchsorted(np.asarray(s[1:-1], dtype=np.int64), g, side='right')
    for j in range(len(s) - 1):
        out[f'B6_dilim{j + 1}'] = sr_ga(r[etiket == j], hb.tohum_banka, f'birincil_{M}_dilim{j + 1}', cekis)
    cikan = b['olcum'].get('b4_cikan')
    if cikan is not None:
        out['B4'] = sr_ga(r[etiket != int(cikan)], hb.tohum_banka, f'birincil_{M}_b4', cekis)
    if 'b8_r' in b:
        x, _ = _pencere_serisi(b, b['b8_r'], hb)
        out['B8'] = sr_ga(x, hb.tohum_banka, f'birincil_{M}_b8', cekis)
    for n in ayar.NAV_IZGARA:
        for m in ayar.MALIYET:
            if n == ayar.NAV_BIRINCIL and m == 1.0:
                continue
            u = _birim(birimler, grup='izgara', mimari=M, nav0=n, maliyet_k=m)
            if 'nav_gunluk' in u:
                ru, _ = gunluk_getiri(u, hb.t0_z1_ms, hb.birincil_son_ms, h)
                out[f'R1_{int(n)}|{int(m)}'] = sr_ga(ru, hb.tohum_banka, f'izgara_{M}_{int(n)}_{int(m)}', cekis)
    out[f'R1_{int(ayar.NAV_BIRINCIL)}|1'] = out['B7_birincil']                    # R1 birincil hücresi (T22)
    out['B3_x2'] = out.get(f'R1_{int(ayar.NAV_BIRINCIL)}|2')
    out['B3_x3'] = out.get(f'R1_{int(ayar.NAV_BIRINCIL)}|3')
    kv = _birim(birimler, grup='k_evren', mimari=M, evren='K')
    gk = kv['nav_bas_ms'] + np.arange(len(kv['b9_seri']), dtype=np.int64) * GUN_MS
    pk = (((gk >= hb.t0_z1_ms) & (gk < hb.birincil_son_ms)) | ((gk >= hb.z2_bas_ms) & (gk < hb.z2_son_ms)))
    pk &= ~np.isin(gk, np.asarray(h, dtype=np.int64))
    out['B9'] = sr_ga(np.asarray(kv['b9_seri'], dtype=float)[pk], hb.tohum_banka, f'k_evren_{M}_B9', cekis)
    lot = _birim(birimler, grup='lot_kapali', mimari=M, lot=False)
    if 'nav_gunluk' in lot:
        rl, _ = gunluk_getiri(lot, hb.t0_z1_ms, hb.birincil_son_ms, h)
        out['R13_lot_kapali'] = sr_ga(rl, hb.tohum_banka, f'lot_kapali_{M}', cekis)
    r3 = _birim(birimler, grup='long_beta', mimari=M)
    rr, _ = gunluk_getiri(r3, hb.t0_z1_ms, hb.birincil_son_ms, h)
    out['R3_long_beta'] = sr_ga(rr, hb.tohum_banka, f'long_beta_{M}', cekis)
    from .hukum import _kelly_birimi
    for m in ayar.KELLY_MALIYET:
        for L in ayar.KELLY_L:
            u = _kelly_birimi(birimler, hb, L, m)
            if 'nav_gunluk' in u:
                rk, _ = gunluk_getiri(u, hb.t0_z1_ms, hb.birincil_son_ms, h)
                out[f'Kelly_{L:g}|{int(m)}'] = sr_ga(rk, hb.tohum_banka, f'kelly_{M}_{L:g}_{int(m)}', cekis)
    return out


def rapor_satirlari(birimler: dict, hb, cekis: int = CEKIS, sigma_rev1: float = None, rev1: dict = None) -> dict:
    return {**kosu_tanilari(birimler, hb), 'R2': r2_beta(birimler, hb), 'R4': r4_rev1(birimler, hb, rev1),
            'R8': r8_b(birimler, hb, cekis),
            'R13b': r13b_adim(birimler, hb), 'R15': r15_b9_d(birimler, hb, cekis), 'R17': r17_null(birimler, hb),
            'GA': sharpe_ga_tablosu(birimler, hb, cekis), 'R12': r12_kanal_stresleri(birimler, hb, cekis),
            'R9': r9_delist(birimler, hb, cekis), 'R10': r10_segmentler(birimler, hb, cekis),
            'R11': r11_birincil(birimler, hb, cekis),
            'R13': r13_lot(birimler, hb), 'R16': r16_dsr(birimler, hb, sigma_rev1)}
