"""Carry kapisi betimsel raporlari, seri tabanli kisim (baglayici degil; CARRY Ss6.6; U-18, U-33, U-34, U-35, U-36, U-37,
U-38). Karar kaydi tabanli (kappa, baglama sikliklari, tavan asimlari, hedge yuvarlama, funding dolgu) ve isim tabanli
(long/short bacak, en kotu isim-hafta, sifir/sifir tanisi) raporlar ayri parcadir (5.02f2, 5.02f3).
Trend serileri yalniz rho_ust uzerinden girer (K1* duyarliligi, delist senaryolarinda K1); trend P&L'i yazilmaz (Ss2).
"""
import math
from datetime import datetime, timezone

import numpy as np

from banka.olcutler import mdd
from . import istatistik as ist
from . import olcutler as olc

K1_DUYARLILIK = ((0.45, 0.27), (0.45, 0.43), (0.60, 0.27), (0.60, 0.43))     # U-37: SR_T,ref x k


def phi(s: dict) -> float:
    """phi = (F - C) / (F - C + max(P, 0)) ortalamalarla (Ss6.6); payda 0 ise nan."""
    fc = float(np.mean(s['F'])) - float(np.mean(s['C']))
    payda = fc + max(float(np.mean(s['P'])), 0.0)
    return fc / payda if payda != 0 else float('nan')


def _ceyrek(t_ms: int) -> str:
    d = datetime.fromtimestamp(int(t_ms) / 1000, timezone.utc)
    return f"{d.year}-Q{(d.month - 1) // 3 + 1}"


def ceyrek_tablosu(s: dict) -> list:
    """U-33: haftanin Pazartesi tarihine gore takvim ceyregi; hafta sayisi, ort r^F, r^C, r^P, r^N, SR^K(r^N)."""
    etiket = [_ceyrek(t) for t in np.asarray(s['hafta_ms']).tolist()]
    out = []
    for q in sorted(set(etiket)):
        ix = np.array([e == q for e in etiket])
        sub = {k: np.asarray(s[k])[ix] for k in ('F', 'C', 'P', 'N')}
        try:
            srk = ist.sr_kredili(sub['F'], sub['C'], sub['P'], sub['N'])
        except ValueError:
            srk = float('nan')
        out.append({'ceyrek': q, 'hafta': int(ix.sum()), **{f"ort_{k}": float(np.mean(v)) for k, v in sub.items()},
                    'sr_k': srk})
    return out


def bilesik_mdd(r) -> float:
    """U-34: haftalik bilesik yol (1'den baslar), carry birim olceginde; getiri <= -1 ise 1 (banka B11 bicimi)."""
    r = np.asarray(r, dtype=float)
    if not np.isfinite(r).all():
        return float('nan')
    if np.any(r <= -1.0):
        return 1.0
    return mdd(np.concatenate(([1.0], np.cumprod(1.0 + r))))


def _t(m, se):
    return m / se if se > 0 else float('nan')


def nw_t_tablosu(s: dict, s3: dict, faktor: dict) -> dict:
    """Ss6.6: l = 4 ve 12 icin butun NW t'leri (K2, K7, K3/K4 fiyat ortalamasi, K9 betalari, K11 katsayilari) ve
    Andrews otomatik gecikmesiyle t'ler (U-35)."""
    out = {}
    for ad, x in (('F-C', np.asarray(s['F']) - np.asarray(s['C'])), ('F-C|mc3', np.asarray(s3['F']) - np.asarray(s3['C'])),
                  ('P', np.asarray(s['P'])), ('N', np.asarray(s['N'])), ('N_g', np.asarray(s['N_g']))):
        t = ist.nw_t(x)
        la = ist.andrews_gecikme(x)
        out[ad] = {'t4': t['t'][4], 't12': t['t'][12], 'andrews_l': la,
                   't_andrews': _t(float(np.mean(x)), ist.nw_ortalama_se(x, la))}
    for seri in ('N', 'N_g'):
        for f in ('x_B', 'x_A'):
            o = {l: ist.ols_nw(s[seri], faktor[f], l) for l in ist.GECIKMELER}
            out[f"beta {seri}|{f}"] = {f"t{l}": _t(float(o[l]['katsayi'][1]), float(o[l]['se'][1])) for l in o}
    return out


def k11_ayrinti(s: dict, faktor: dict) -> dict:
    """Ss6.3 K11 notu: ham katsayilar, NW t'leri ve ortak Wald p (chi^2_4) her gecikme (l = 4, 12) icin kendi HAC
    kovaryansiyla; faktorlerin acikladigi fiyat ortalamasi sum_k b_k ort(x_k)."""
    X = np.column_stack([np.asarray(faktor[f], dtype=float) for f in olc.FAKTORLER])
    rp = np.asarray(s['P'], dtype=float)
    out = {}
    for l in ist.GECIKMELER:
        o = ist.ols_nw(rp, X, l)
        b, V = o['katsayi'][1:], o['V'][1:, 1:]
        try:
            w = float(b @ np.linalg.solve(V, b))
            p = math.exp(-w / 2.0) * (1.0 + w / 2.0)          # chi^2 4 sd kuyrugu (kapali bicim)
        except np.linalg.LinAlgError:
            w, p = float('nan'), float('nan')
        out[f"l{l}"] = {'b': {f: float(b[j]) for j, f in enumerate(olc.FAKTORLER)},
                        't': {f: _t(float(b[j]), float(o['se'][j + 1])) for j, f in enumerate(olc.FAKTORLER)},
                        'wald': w, 'wald_p': p}
    b1 = ist.ols_nw(rp, X, ist.GECIKMELER[0])['katsayi'][1:]
    out['aciklanan_fiyat_ortalamasi'] = float(sum(b1[j] * float(np.mean(X[:, j])) for j in range(X.shape[1])))
    return out


def k1_duyarlilik(k1_sonuc: dict) -> dict:
    """U-37: iki serinin rho_ust'u ile K1*(SR_T,ref, k) 2 x 2 izgarasi; rho_K1 kirpmasi korunur."""
    out = {}
    for seri in ('sanal', 'gerceklesen'):
        r = k1_sonuc.get(seri, {}).get('rho_ust', float('nan'))
        out[seri] = {f"{sr}|{k}": (ist.k1_esik(r, sr, k) if r == r else float('nan')) for sr, k in K1_DUYARLILIK}
    return out


def artik_tanisi(s: dict, n_en_buyuk: int = 3) -> dict:
    """Ss6.6 2. tur: a^C_w serisi ve en buyuk uc haftalik sapma (|a^C_w|)."""
    a = np.asarray(s['a_C'], dtype=float)
    sira = sorted(range(len(a)), key=lambda i: (-abs(a[i]), i))[:n_en_buyuk]
    return {'a_C': [float(x) for x in a],
            'en_buyuk': [{'hafta_ms': int(s['hafta_ms'][i]), 'a_C': float(a[i])} for i in sira]}


def en_kotu_hafta(s: dict) -> dict:
    out = {}
    for k in ('N', 'N_g'):
        x = np.asarray(s[k], dtype=float)
        i = int(np.argmin(x))
        out[k] = {'hafta_ms': int(s['hafta_ms'][i]), 'r': float(x[i])}
    return out


def guvenli(f, *a, **k):
    """Betimsel kalem hesaplanamazsa kosu durmaz; kalem {'hata': ...} olur (baglayici degil)."""
    try:
        return f(*a, **k)
    except (ValueError, KeyError, ZeroDivisionError, np.linalg.LinAlgError) as e:
        return {'hata': f"{type(e).__name__}: {e}"}


def seri_raporlari(g, hukum: dict, delist: dict = None) -> dict:
    """g: olcutler.KapiGirdisi; hukum: olcutler.degerlendir ciktisi; delist: {'delist50': haftalik, 'delist90': ...}."""
    s = g.ana
    rapor = {
        'phi': guvenli(phi, s),
        'ceyrek': guvenli(ceyrek_tablosu, s),
        'mdd': {'N': bilesik_mdd(s['N']), 'N_g': bilesik_mdd(s['N_g'])},
        'en_kotu_hafta': guvenli(en_kotu_hafta, s),
        'sr_kredisiz': {'N': guvenli(ist.sharpe, s['N']), 'N_g': guvenli(ist.sharpe, s['N_g'])},
        'sr_bootstrap_90': guvenli(ist.sr_bootstrap_araligi, s['N']),
        'nw_t': guvenli(nw_t_tablosu, s, g.mc3, g.faktor),
        'k11': guvenli(k11_ayrinti, s, g.faktor),
        'k1_duyarlilik': guvenli(k1_duyarlilik, hukum['K']['K1']),
        'artik': guvenli(artik_tanisi, s),
        'k3_k4': hukum.get('betimsel_K3_K4'),
    }
    if delist:
        rapor['delist_k1'] = {ad: olc.k1(d) for ad, d in sorted(delist.items())}
    return rapor
