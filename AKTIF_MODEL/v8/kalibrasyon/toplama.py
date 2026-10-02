"""Kalibrasyon toplamasi (BANKA_ONKAYIT_TASLAK Ss3.3, Ss3.7; 3. revizyon). Butun birimler bittikten sonra bir kez
kosar; birim sonuclarini (butunlugu dogrulanmis) okur ve kararlari mekanik olarak uretir.

1. Duzey 1: sigma_SR_bag (sigma_sr.py), N = 159 + N_v8 (defter), duzey1_karari -> kurallar ya da KILIT_BEKLER;
   P(KABUL | SR) ayar basina; B9'un gecme olasiligi (rapor); B seyreltme egrileri; R16 DSR duyarlilik tablosu.
2. Duzey 2-a (Duzey 1 TAMAM ise): A ve B icin KABUL_B7siz (Duzey 1'de bagli kalan olcutler, Duzey 1'in son esikleri)
   -> p = k/100 ("ust sinirin nokta tahmini") ve Wilson %95; p > %5 -> KILIT_BEKLER (tarama kurali).
3. Duzey 2-b (betimsel): ayar basina B7'nin q90 ve q95 ile gecme orani, sira yuzdeligi, taban olcutlerle birlikte
   B7 (q95) orani, Wilson; ortak eslesme payi."""
import json
import math
from dataclasses import replace
from pathlib import Path
from statistics import NormalDist

import numpy as np

from banka import olcutler as o

from . import birim as B
from .duzey1 import SR_IZGARASI
from .duzey1_esik import IX, Kurallar, kabul, kabul_oranlari
from .duzey1_karar import FAR_HEDEF, duzey1_karari, n_v8
from .duzey1_olcut import ALANLAR, SEYRELTME
from .kosucu import cikarma_turet, duzey1_listesi, duzey2_listesi
from .sigma_sr import N_REV1, sigma_sr_bag

_N = NormalDist()


class ToplamaHatasi(RuntimeError):
    """Eksik ya da gecersiz birim: toplama yapilmaz."""


# --- saf fonksiyonlar ---

def b7_gecer(sr: float, null_sr, alfa: float) -> bool:
    """Ss3.5.6: SR > q_alfa; q_alfa sirali null degerlerinin ceil(alfa n)'inci elemani. nan SR kalir."""
    x = np.sort(np.asarray(null_sr, dtype=float))
    if not math.isfinite(sr) or np.isnan(x).any():
        return False
    return sr > float(x[math.ceil(alfa * len(x)) - 1])


def duzey2_satiri(birincil: dict, x2_sr=None, x3_sr=None, cikarma_sr=None) -> np.ndarray:
    """Duzey 2 birincil biriminden Duzey 1 ALANLAR bicimli satir (kabul() ile ayni esiklerle degerlendirilir). B9
    Duzey 2'de yoktur: b9 = +1 (etkisiz; B9 Duzey 1'den raporlanir)."""
    r = np.full(len(ALANLAR), np.nan)
    d = {'sr': birincil['sr'], 'sr_gunluk': birincil['sr_gunluk'], 'g3': birincil['g3'], 'g4': birincil['g4'],
         'eta': birincil['eta'], 'T': float(birincil['T']), 'b4': birincil['b4_sr'], 'b5': birincil['b5_pay'],
         'b6': float(sum(1 for x in birincil['dilim_sr'] if x is not None and x > 0)), 'b8': birincil['b8_sr'],
         'b9': 1.0, 'b11': birincil['b11_mdd'],
         'b3_2': np.nan if x2_sr is None else x2_sr, 'b3_3': np.nan if x3_sr is None else x3_sr,
         'b10': np.nan if cikarma_sr is None else o.en_buyuk_dusus(birincil['sr'], cikarma_sr)}
    for k, v in d.items():
        r[IX[k]] = np.nan if v is None else float(v)
    return r


def duzey2a_ozeti(satirlar: np.ndarray, k: Kurallar) -> dict:
    """satirlar: (n_yol, ALANLAR). Doner k, n, p, wilson, kural sonucu."""
    ok = kabul(satirlar, k)
    n, kk = len(ok), int(ok.sum())
    p, alt, ust = o.wilson(kk, n)
    return {'kabul': kk, 'n': n, 'ust_sinirin_nokta_tahmini': p, 'wilson_alt': alt, 'wilson_ust': ust,
            'tarama_gecti': p <= FAR_HEDEF}


def duzey2b_ozeti(yollar: list, k: Kurallar) -> dict:
    """yollar: [(birincil govde, [null sr, ...], ortak, toplam), ...] tek ayar icin."""
    g90 = g95 = birlikte = 0
    sira, ortak, toplam = [], 0, 0
    for bir, nulls, o_, t_ in yollar:
        sr = bir['sr']
        a90, a95 = b7_gecer(sr, nulls, 0.90), b7_gecer(sr, nulls, 0.95)
        g90, g95 = g90 + a90, g95 + a95
        x = np.asarray(nulls, dtype=float)
        sira.append(float(np.mean(x < sr)) if math.isfinite(sr) else float('nan'))
        # Taban olcutler: birincil kosudan hesaplanabilenler (B2, B4, B5, B6, B8, B11); B3 ve B10 icin kosu yok ->
        # satirda etkisiz degerler (x2/x3 SR = +inf, cikarma dususu 0); B9 zaten etkisiz.
        taban = duzey2_satiri(bir, math.inf, math.inf, [])
        birlikte += int(a95 and bool(kabul(taban[None, :], replace(k, e_b10=None))[0]))
        ortak, toplam = ortak + o_, toplam + t_
    n = len(yollar)
    return {'n': n, 'b7_q90': o.wilson(g90, n), 'b7_q95': o.wilson(g95, n),
            'taban_ve_b7_q95': o.wilson(birlikte, n), 'sira_yuzdeligi_ort': float(np.nanmean(sira)) if sira else None,
            'ortak_pay': ortak / toplam if toplam else None}


def r16_tablosu(N: int, T_yillar=(3.0, 3.5), sigmalar=(0.20, 0.30, 0.50), dler=(0.50, 0.75, 0.90, 0.95)) -> list:
    """Ss3.3 duyarlilik tablosu (kalem-kagit; eta = 1, g3 = 0, g4 = 3): SR0 ve DSR = d icin gereken yillik SR."""
    out = []
    for T in T_yillar:
        se = 1.0 / math.sqrt(T)
        for s in sigmalar:
            z0 = o.sr0(N, s) * math.sqrt(365)
            out.append({'T_yil': T, 'sigma_sr': s, 'sr0_yillik': z0,
                        'gereken_sr': {str(d): z0 + _N.inv_cdf(d) * se for d in dler},
                        'p_b2_d050_sr0': _N.cdf(-z0 / se), 'p_b2_d050_sr1': _N.cdf((1.0 - z0) / se)})
    return out


# --- dosyalardan toplama ---

def _oku(dizin, k, kim, npz=False):
    s = B.sonuc_oku(dizin, k, kim, npz=npz)
    if s is None:
        raise ToplamaHatasi(f"eksik ya da gecersiz birim: {B.birim_adi(k)}")
    return s


def duzey1_topla(dizin, kim: dict, n_yol: int, kayit_yolu, defter_yolu) -> dict:
    sonuclar, seyr = {}, {}
    for k in duzey1_listesi(n_yol):
        _, d = _oku(dizin, k, kim, npz=True)
        sonuclar[k['ayar_no']], seyr[k['ayar_no']] = d['olcut'], d['seyreltme']
    sig = sigma_sr_bag(kayit_yolu)
    N = N_REV1 + n_v8(defter_yolu)
    karar = duzey1_karari(sonuclar, N, sig['sigma_sr_bag'])
    rapor = {'sigma_sr': sig, 'N': N, 'karar': {x: y for x, y in karar.items() if x != 'kurallar'},
             'kurallar': None if karar['kurallar'] is None else karar['kurallar'].__dict__,
             'r16': r16_tablosu(N)}
    k = karar['kurallar']
    ref = SR_IZGARASI.index(1.0)
    rapor['b9_gecme_ref'] = {no: float(np.mean(a[:, ref, IX['b9']] > 0)) for no, a in sonuclar.items()}
    if k is not None:
        oranA = kabul_oranlari(sonuclar, k)
        rapor['p_kabul_A_ort'] = np.mean(list(oranA.values()), axis=0).tolist()
        rapor['seyreltme'] = {}
        for i, (rho, src) in enumerate(SEYRELTME):
            oranB = [kabul(s[:, :, i, :], k).mean(axis=0) for s in seyr.values()]
            rapor['seyreltme'][f'rho={rho};SR_C={src}'] = np.mean(oranB, axis=0).tolist()
    return {'rapor': rapor, 'kurallar': k, 'durum': karar['durum']}


def duzey2_topla(dizin, kim: dict, k: Kurallar) -> dict:
    liste = duzey2_listesi()
    bir = {}
    for x in liste:
        if x['tur'] == 'birincil':
            bir[(x['ayar_no'], x['yol_no'], x['mimari'])] = _oku(dizin, x, kim)[0]

    def sr_of(x):
        return _oku(dizin, x, kim)[0]['sr']
    out = {}
    for m in ('A', 'B'):
        satirlar = []
        for yol in range(1, 101):
            b = bir[(0, yol, m)]
            k0 = {'duzey': 2, 'ayar_no': 0, 'yol_no': yol, 'mimari': m}
            zarf = json.loads((Path(dizin) / f"{B.birim_adi({**k0, 'tur': 'birincil'})}.json").read_text('ascii'))
            cik = [sr_of(c) for c in cikarma_turet({**k0, 'tur': 'birincil'}, b, zarf['govde_sha256'])]
            satirlar.append(duzey2_satiri(b, sr_of({**k0, 'tur': 'x2'}), sr_of({**k0, 'tur': 'x3'}), cik))
        out[m] = duzey2a_ozeti(np.array(satirlar), k)
    b2 = {}
    for ayar in range(0, 5):
        yollar = []
        for yol in range(1, 11):
            b = bir[(ayar, yol, 'A')]
            nulls = [_oku(dizin, {'duzey': 2, 'ayar_no': ayar, 'yol_no': yol, 'mimari': 'A', 'tur': 'null',
                                  'null_no': p}, kim)[0] for p in range(1, 51)]
            yollar.append((b, [z['sr'] for z in nulls], sum(z['ortak'] for z in nulls), sum(z['toplam'] for z in nulls)))
        b2[ayar] = duzey2b_ozeti(yollar, k)
    durum = 'TAMAM' if all(v['tarama_gecti'] for v in out.values()) else 'KILIT_BEKLER'
    return {'duzey2a': out, 'duzey2b': b2, 'durum': durum}
