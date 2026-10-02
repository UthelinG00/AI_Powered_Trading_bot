"""Carry kapisi olcutleri ve karar (CARRY Ss6.1, Ss6.3, Ss7.1, Ss7.2; Ss15; U-05, U-10, U-11, U-12, U-14, U-17, U-18,
U-22, U-27, U-38).

Girdi: kapi_seriler.haftalik sozlukleri (ana kosu m_c = 1 taban delist; m_c = 2; m_c = 3; K8 yeniden kosusu), ana
kosunun aylik F - C serisi, fiyat faktorleri, V koşullarinin disaridan gelen parcalari (V1 test raporu, V2 oranlari,
V5 birebirlik, V6 orani). Cikti iki sozluk (Ss7.2):
- denetim: V1-V6 yalniz gecti/kaldi (olcut degeri yok);
- hukum: K1-K11 degerleri, esikler, gecti/kaldi, V oranlari (U-17), karar.
Trend serileri (T, a_T, T_g) yalniz rho_hat/rho_ust icin okunur; hukume baska hicbir trend degeri yazilmaz (Ss2, U-01).
Hesaplanamayan olcut gecmemis sayilir (Ss7.1): her olcut ValueError'da 'hata' ile kaldi doner.
"""
from dataclasses import dataclass, field

import numpy as np

from . import istatistik as ist

# Ss6.1, Ss6.3 esikleri (kilitle donar)
V2_TOL = 1e-8
V3_SIFIR_PAY = 0.25
V3_AKTIF_MIN = 108
V4A_ORAN = 0.10
V4B_KAT = 1.0
V6_ORAN = 0.10
K2_T = 3.0
K5_PAY = (3, 4)            # pay >= 3/4, tamsayi karsilastirma
K7_T = 2.0
K8_ISIM_MIN = 30
K9_DELTA = 0.15
K10_RHO = 0.30
K11_DELTA = 0.30
DELTA_P_YIL = 0.04         # K3/K4 (betimsel), haftalik delta_P / 52 (U-38)
BAGLAYICI = ('K1', 'K2', 'K5', 'K6', 'K7', 'K8', 'K9', 'K10', 'K11')
FAKTORLER = ('x_B', 'x_A', 'x_R', 'x_S')
KOSULAR = ('ana', 'mc2', 'mc3', 'k8', 'delist50', 'delist90')   # V2 ve V5 her kosuda (U-12)


@dataclass
class KapiGirdisi:
    ana: dict                         # seriler.haftalik, m_c = 1, taban delist
    ana_aylik: dict                   # seriler.aylik_fc (ana kosu)
    mc2: dict
    mc3: dict
    k8: dict                          # None: K8 hesaplanamaz (isim < 30), k8 kosusu yapilmaz (U-52)
    k8_isim_sayisi: int               # ana kosuda en az bir saat q^C,v != 0 olan ayri alt isim sayisi (U-07)
    faktor: dict                      # FAKTORLER -> haftalik dizi (ana haftalarla hizali)
    pazartesi_bos: np.ndarray         # hafta basina: Pazartesi kararinda butun q^C* = 0 (U-14)
    v1: bool                          # dondurulmus motor kimligiyle test raporu, basarisiz 0 (U-15)
    v2_oran: dict                     # kosu adi -> gunluk ozdeslik oranlarinin en buyugu (U-16; her kosu, U-12)
    v5: dict                          # kosu adi -> tek defter birebir mi (U-28)
    v6_oran: float                    # B ve A bant oncesi trend hedefi farkli gun orani (U-13)
    ek: dict = field(default_factory=dict)


def _korumali(f):
    def sar(*a, **k):
        try:
            return f(*a, **k)
        except (ValueError, np.linalg.LinAlgError, ZeroDivisionError) as e:
            return {'gecti': False, 'hata': f"{type(e).__name__}: {e}"}
    sar.__name__ = f.__name__
    return sar


def _sr_k(s: dict, gerceklesen: bool) -> float:
    if gerceklesen:
        return ist.sr_kredili(s['F'], s['C'], s['P'], s['N_g'], s['a_C'])
    return ist.sr_kredili(s['F'], s['C'], s['P'], s['N'])


# ---- V kosullari -------------------------------------------------------------------------------------------------

def v3(bos) -> dict:
    """Carry kitabinin bos oldugu Pazartesi payi <= %25 ve aktif hafta >= 108 (Ss6.1, U-14)."""
    bos = np.asarray(bos, dtype=bool)
    n, n_bos = len(bos), int(bos.sum())
    pay = n_bos / n if n else float('nan')
    return {'sifir_pay': pay, 'aktif': n - n_bos, 'gecti': bool(n > 0 and pay <= V3_SIFIR_PAY and n - n_bos >= V3_AKTIF_MIN)}


def v4(s: dict) -> dict:
    """V4a: sum |a^C| <= 0,10 sum |r^N|; V4b: her hafta |a^C_w| <= 1,0 sd(r^N) (tek sd, ddof 1; U-27)."""
    a, r = np.asarray(s['a_C'], dtype=float), np.asarray(s['N'], dtype=float)
    if not (np.isfinite(a).all() and np.isfinite(r).all()) or len(r) < 2:
        return {'v4a': {'gecti': False}, 'v4b': {'gecti': False}}
    top_a, top_r = float(np.sum(np.abs(a))), float(np.sum(np.abs(r)))
    sd = float(np.std(r, ddof=1))
    enb = float(np.max(np.abs(a)))
    return {'v4a': {'oran': top_a / top_r if top_r > 0 else float('inf'), 'gecti': top_a <= V4A_ORAN * top_r},
            'v4b': {'oran': enb / sd if sd > 0 else float('inf'), 'gecti': enb <= V4B_KAT * sd}}


# ---- Karar olcutleri ---------------------------------------------------------------------------------------------

@_korumali
def k1(s: dict) -> dict:
    """SR^K >= K1*(rho_ust) iki seride; rho_ust her seri icin kendi trend ciftiyle (U-10)."""
    out = {}
    for ad, g, (n_ad, t_ad) in (('sanal', False, ('N', 'T')), ('gerceklesen', True, ('N_g', 'T_g'))):
        sr = _sr_k(s, g)
        r = ist.rho_ust(s[n_ad], s[t_ad])
        esik = ist.k1_esik(r['rho_ust'])
        out[ad] = {'sr_k': sr, 'rho_hat': r['rho_hat'], 'rho_ust': r['rho_ust'], 'n_w': r['n_w'], 'esik': esik,
                   'gecti': bool(sr >= esik)}
    out['gecti'] = out['sanal']['gecti'] and out['gerceklesen']['gecti']
    return out


@_korumali
def k2(s: dict) -> dict:
    """NW t(r^F - r^C) >= 3,0 (buyuk SE) ve bootstrap alt sinir > 0 (sanal)."""
    x = np.asarray(s['F'], dtype=float) - np.asarray(s['C'], dtype=float)
    t = ist.nw_t(x)
    b = ist.k2_bootstrap_alt(x)
    return {'t': t['t_buyuk'], 't_l': t['t'], 'boot_alt': b['alt'], 'boot_blok': b['blok'],
            'gecti': bool(t['t_buyuk'] >= K2_T and b['alt'] > 0)}


def k3_k4(s: dict) -> dict:
    """Betimsel (Ss6.3): mu_P'nin tek tarafli %95 sinirlari +-1,645 SE (buyuk NW SE) ve delta_P / 52 (U-38)."""
    try:
        t = ist.nw_t(s['P'])
    except ValueError as e:
        return {'K3': {'gecti': False, 'baglayici': False, 'hata': str(e)},
                'K4': {'gecti': False, 'baglayici': False, 'hata': str(e)}}
    m, se = t['ortalama'], t['se_buyuk']
    d = DELTA_P_YIL / ist.HAFTA_YIL
    alt, ust = ist.aralik90(m, se)
    return {'K3': {'alt': alt, 'delta': d, 'gecti': bool(alt > -d), 'baglayici': False},
            'K4': {'ust': ust, 'delta': d, 'gecti': bool(ust < d), 'baglayici': False}}


@_korumali
def k5(aylik: dict) -> dict:
    """(F - C) > 0 olan ay payi >= %75 (Ss6.3; U-06)."""
    fc = np.asarray(aylik['FC'], dtype=float)
    if len(fc) == 0 or not np.isfinite(fc).all():
        raise ValueError("aylik seri bos ya da sonlu degil")
    arti = int(np.sum(fc > 0))
    return {'arti_ay': arti, 'ay': len(fc), 'pay': arti / len(fc), 'gecti': K5_PAY[1] * arti >= K5_PAY[0] * len(fc)}


@_korumali
def k6(s2: dict) -> dict:
    """SR^K(m_c = 2) > 0, iki seride."""
    a, b = _sr_k(s2, False), _sr_k(s2, True)
    return {'sanal': a, 'gerceklesen': b, 'gecti': bool(a > 0 and b > 0)}


@_korumali
def k7(s3: dict) -> dict:
    """NW t(r^F - r^C; m_c = 3) >= 2,0 (buyuk SE, sanal)."""
    t = ist.nw_t(np.asarray(s3['F'], dtype=float) - np.asarray(s3['C'], dtype=float))
    return {'t': t['t_buyuk'], 't_l': t['t'], 'gecti': bool(t['t_buyuk'] >= K7_T)}


@_korumali
def k8(s8: dict, isim_sayisi: int) -> dict:
    """Yeniden kosuda SR^K > 0 iki seride; hic tutulmus ayri alt isim < 30 ise hesaplanamaz (kaldi)."""
    if isim_sayisi < K8_ISIM_MIN or s8 is None:
        return {'isim': isim_sayisi, 'gecti': False, 'hata': 'hic tutulmus isim sayisi < 30'}
    a, b = _sr_k(s8, False), _sr_k(s8, True)
    return {'isim': isim_sayisi, 'sanal': a, 'gerceklesen': b, 'gecti': bool(a > 0 and b > 0)}


@_korumali
def k9(s: dict, faktor: dict) -> dict:
    """beta_BTC ve beta_alt ayri regresyonlar; %90 aralik (buyuk NW SE) acik (-0,15; +0,15) icinde; iki seride."""
    out, hepsi = {}, True
    for seri in ('N', 'N_g'):
        for f in ('x_B', 'x_A'):
            o = ist.ols_nw_buyuk(s[seri], faktor[f])
            b, se = float(o['katsayi'][1]), float(o['se_buyuk'][1])
            gec = ist.esdeger(b, se, K9_DELTA)
            out[f"{seri}|{f}"] = {'beta': b, 'se': se, 'aralik': ist.aralik90(b, se), 'gecti': gec}
            hepsi = hepsi and gec
    out['gecti'] = hepsi
    return out


@_korumali
def k10(s: dict) -> dict:
    """|rho_hat(r^N, r^T)| <= 0,30, iki seride; rho_hat tanimsizsa kaldi."""
    out = {}
    for ad, (n_ad, t_ad) in (('sanal', ('N', 'T')), ('gerceklesen', ('N_g', 'T_g'))):
        r = ist.rho_ust(s[n_ad], s[t_ad])['rho_hat']
        out[ad] = {'rho_hat': r, 'gecti': bool(abs(r) <= K10_RHO)}
    out['gecti'] = out['sanal']['gecti'] and out['gerceklesen']['gecti']
    return out


@_korumali
def k11(s: dict, faktor: dict) -> dict:
    """r^P = a + sum b_k x_k (ortak); standart yuklemelerin %90 araligi acik (-0,30; +0,30) icinde (her biri)."""
    X = np.column_stack([np.asarray(faktor[f], dtype=float) for f in FAKTORLER])
    rp = np.asarray(s['P'], dtype=float)
    o = ist.ols_nw_buyuk(rp, X)
    sd_rp = float(np.std(rp, ddof=1))
    out, hepsi = {}, True
    for j, f in enumerate(FAKTORLER, start=1):
        b, se = float(o['katsayi'][j]), float(o['se_buyuk'][j])
        bt, set_ = ist.standart_yukleme(b, se, float(np.std(X[:, j - 1], ddof=1)), sd_rp)
        gec = ist.esdeger(bt, set_, K11_DELTA)
        out[f] = {'b': b, 'se': se, 'b_std': bt, 'se_std': set_, 'aralik': ist.aralik90(bt, set_), 'gecti': gec}
        hepsi = hepsi and gec
    out['gecti'] = hepsi
    return out


# ---- Karar -------------------------------------------------------------------------------------------------------

def degerlendir(g: KapiGirdisi) -> tuple:
    """(denetim, hukum). Karar B yalniz V1-V6 ve BAGLAYICI olcutlerin hepsi gecerse (Ss7.1); aksi A.
    V1, V2, V5 ihlali teknik (Ss7.3 hukum oncesi dali), V3, V4, V6 ihlali esas (U-11); ikisi de burada A'dir,
    'teknik' alani kosucuya dali bildirir."""
    s = g.ana
    gerekli = [k for k in KOSULAR if not (k == 'k8' and g.k8 is None)]       # U-52
    v2_gec = {k: bool(g.v2_oran.get(k, float('inf')) <= V2_TOL) for k in gerekli}
    v3_ = v3(g.pazartesi_bos)
    v4_ = v4(s)
    v6_gec = bool(g.v6_oran <= V6_ORAN)          # nan -> kaldi
    V = {'V1': bool(g.v1), 'V2': all(v2_gec.values()), 'V3': v3_['gecti'],
         'V4a': v4_['v4a']['gecti'], 'V4b': v4_['v4b']['gecti'],
         'V5': all(g.v5.get(k) is True for k in gerekli), 'V6': v6_gec}
    teknik = [k for k in ('V1', 'V2', 'V5') if not V[k]]
    esas = [k for k in ('V3', 'V4a', 'V4b', 'V6') if not V[k]]
    K = {'K1': k1(s), 'K2': k2(s), 'K5': k5(g.ana_aylik), 'K6': k6(g.mc2), 'K7': k7(g.mc3),
         'K8': k8(g.k8, g.k8_isim_sayisi), 'K9': k9(s, g.faktor), 'K10': k10(s), 'K11': k11(s, g.faktor)}
    k_gec = all(K[k]['gecti'] for k in BAGLAYICI)
    karar = 'B' if all(V.values()) and k_gec else 'A'
    denetim = {'V': V, 'teknik_ihlal': teknik, 'esas_ihlal': esas}
    hukum = {'karar': karar, 'K': K, 'betimsel_K3_K4': k3_k4(s),
             'V_oran': {'V2': dict(g.v2_oran), 'V3': {'sifir_pay': v3_['sifir_pay'], 'aktif': v3_['aktif']},
                        'V4a': v4_['v4a'].get('oran'), 'V4b': v4_['v4b'].get('oran'), 'V6': g.v6_oran}}
    return denetim, hukum


def pazartesi_bos_haftalar(gunluk, hafta_ms) -> np.ndarray:
    """U-14: her haftanin Pazartesi 00:00 karar kaydinda butun q^C* = 0 (ya da q_yildiz bos) mu. Kayit yoksa hata."""
    kararlar = {k.damga_ms: k for k in gunluk.kayitlar() if k.tur == 'karar'}
    out = []
    for t in np.asarray(hafta_ms, dtype=np.int64).tolist():
        k = kararlar.get(int(t))
        if k is None or 'carry' not in k.veri['hedef']:
            raise ValueError(f"{t} Pazartesi karar kaydi yok")
        q = k.veri['hedef']['carry']['q_yildiz']
        out.append(all(float(v) == 0.0 for v in q.values()))
    return np.array(out, dtype=bool)


def hukum_trend_icermez(hukum: dict) -> bool:
    """Ss2 muhur denetimi: hukum sozlugunde rho_hat/rho_ust disinda trend alani yok (anahtar adlariyla)."""
    yasak = ('T', 'a_T', 'T_g', 'trend')

    def gez(x):
        if isinstance(x, dict):
            return all(k not in yasak and not str(k).startswith('trend') and gez(v) for k, v in x.items())
        if isinstance(x, (list, tuple)):
            return all(gez(v) for v in x)
        return True
    return gez(hukum)

