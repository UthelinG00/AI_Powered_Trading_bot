"""Carry kapisi istatistikleri (saf; CARRY Ss6.2, Ss15; BELIRSIZLIK_COZUMLERI U-02, U-03, U-04, U-09, U-22, U-35, U-36,
U-38). Girdi haftalik (K5'te aylik) dizilerdir; kaynak (motor ayristirmasi ya da sentetik fikstur) bilinmez.

Tanimlar (hicbiri D'ye bakilarak secilmedi):
- Sharpe: ortalama / std (ddof 1) * sqrt(52); n < 2 ya da seri sabitse nan (hicbir esigi gecmez; Ss7.1). Sabitlik
  kesin denetlenir (max = min): ortalamanin kayan nokta gurultusu sabit seride sifir olmayan std/SE uretebilir.
- Newey-West (U-02): Bartlett w_j = 1 - j/(l + 1); gamma_j = (1/n) sum (x_t - m)(x_{t-j} - m); ortalamanin varyansi
  (gamma_0 + 2 sum w_j gamma_j) / n; kucuk orneklem duzeltmesi yok. Regresyonda HAC sandvic
  (X'X)^-1 S (X'X)^-1, S = sum_t u_t^2 x_t x_t' + sum_j w_j sum_t u_t u_{t-j} (x_t x_{t-j}' + x_{t-j} x_t') (toplamlar;
  sabit-yalniz regresyonda ortalamanin NW varyansina esittir). "Buyuk SE" parametre basina, l in {4, 12}.
- Belge sabitleri harfiyen: Fisher tek tarafli %90 icin 1,2816 (Ss6.2), TOST/%90 aralik icin 1,645 (Ss6.2).
- Aralik olcutleri acik aralik ister: uc toleransa esitse gecmez (Ss7.1).
"""
import math

import numpy as np

HAFTA_YIL = 52
GECIKMELER = (4, 12)            # Ss6.2: 4 = floor(4 * (143/100)^(2/9)); 12 = 84 gun
Z_FISHER_90 = 1.2816            # Ss6.2 rho_ust
Z_90_IKI = 1.645                # Ss6.2 TOST ve %90 aralik
BOOT_TOHUM = 20260928           # Ss6.2, U-03
BOOT_BLOKLAR = (4, 12)          # U-03: once 4, sonra 12; tek Generator
BOOT_CEKIS = 10000
BOOT_KANTIL = 0.05              # tek tarafli %95 alt sinir
SR_BOOT_TOHUM = 20260929        # U-36 (K2'den ayri akis)
SR_T_REF = 0.85                 # Ss6.3 K1*
K_ORAN = 1.0 / 3.0              # sigma_C / sigma_T
RHO_K1_ALT, RHO_K1_UST = 0.0, 0.30
RHO_KIRP = 1.0 - 1e-12          # U-22


def _dizi(x) -> np.ndarray:
    x = np.asarray(x, dtype=float)
    if x.ndim != 1:
        raise ValueError("dizi tek boyutlu olmali")
    if not np.isfinite(x).all():
        raise ValueError("dizide sonlu olmayan deger var")
    return x


def _sabit(x: np.ndarray) -> bool:
    return len(x) == 0 or float(np.max(x)) == float(np.min(x))


def sharpe(r) -> float:
    """Yillik Sharpe (Ss6.2): haftalik ortalama / std (ddof 1) * sqrt(52)."""
    r = _dizi(r)
    if len(r) < 2 or _sabit(r):
        return float('nan')
    s = float(np.std(r, ddof=1))
    return float(np.mean(r)) / s * math.sqrt(HAFTA_YIL) if s > 0 else float('nan')


def sr_kredili(r_f, r_c, r_p, r, a=None, tol: float = 1e-12) -> float:
    """Kredilenen Sharpe (Ss6.2, KC-06; U-09): [ort(r_f - r_c) + min(ort(r_p), 0) + min(ort(a), 0)] / std(r) * sqrt(52).
    Sanal seride a = None (terim 0, r = r^N); gerceklesen seride a = a^C, r = r^{N,g}. r'nin bilesenlerin toplamina
    esitligi tol icinde denetlenir (yanlis seri eslesmesine karsi)."""
    r_f, r_c, r_p, r = _dizi(r_f), _dizi(r_c), _dizi(r_p), _dizi(r)
    a = np.zeros_like(r) if a is None else _dizi(a)
    if not (len(r_f) == len(r_c) == len(r_p) == len(r) == len(a)):
        raise ValueError("seri uzunluklari farkli")
    if len(r) and float(np.max(np.abs(r - (r_f - r_c + r_p + a)))) > tol:
        raise ValueError("r, r_f - r_c + r_p + a toplamina esit degil")
    if len(r) < 2 or _sabit(r):
        return float('nan')
    s = float(np.std(r, ddof=1))
    if not s > 0:
        return float('nan')
    pay = float(np.mean(r_f - r_c)) + min(float(np.mean(r_p)), 0.0) + min(float(np.mean(a)), 0.0)
    return pay / s * math.sqrt(HAFTA_YIL)


def _bartlett(gecikme: int, n: int) -> np.ndarray:
    """w_j = 1 - j/(l + 1), j = 1..min(l, n - 1) (daha uzun gecikmenin katkisi yok; Codex T15-11 bellek)."""
    return 1.0 - np.arange(1, min(int(gecikme), n - 1) + 1) / (gecikme + 1.0)


def nw_ortalama_se(x, gecikme: int) -> float:
    """Ortalamanin Newey-West standart hatasi (U-02). n < 2 ise nan."""
    x = _dizi(x)
    n = len(x)
    if n < 2:
        return float('nan')
    if _sabit(x):
        return 0.0
    d = x - x.mean()
    uzun = float(np.dot(d, d)) / n
    for j, w in enumerate(_bartlett(gecikme, n), start=1):
        uzun += 2.0 * w * float(np.dot(d[j:], d[:-j])) / n
    return math.sqrt(uzun / n) if uzun > 0 else 0.0


def nw_t(x, gecikmeler=GECIKMELER) -> dict:
    """Ortalamanin NW t'si; her gecikme icin ve buyuk SE ile (Ss6.2 secim kurali: anlamlilik isteyen olcutte buyuk SE).
    SE 0 ya da nan ise t nan (esigi gecmez)."""
    x = _dizi(x)
    m = float(np.mean(x)) if len(x) else float('nan')
    se = {l: nw_ortalama_se(x, l) for l in gecikmeler}
    t = {l: (m / s if s > 0 else float('nan')) for l, s in se.items()}
    buyuk = max(se.values()) if all(s == s for s in se.values()) else float('nan')
    return {'ortalama': m, 'se': se, 't': t, 'se_buyuk': buyuk,
            't_buyuk': m / buyuk if buyuk > 0 else float('nan')}


def ols_nw(y, X, gecikme: int) -> dict:
    """y = c + X b + e (sabit eklenir). Doner: katsayi (sabit ilk), NW HAC standart hatalari, artiklar, kovaryans V."""
    y = _dizi(y)
    X = np.asarray(X, dtype=float)
    if X.ndim == 1:
        X = X[:, None]
    if X.shape[0] != len(y) or not np.isfinite(X).all():
        raise ValueError("X boyutu ya da degerleri gecersiz")
    Z = np.column_stack([np.ones(len(y)), X])
    n, k = Z.shape
    if n <= k:
        raise ValueError("gozlem sayisi parametre sayisindan fazla olmali")
    ZtZ_ters = np.linalg.inv(Z.T @ Z)
    b = ZtZ_ters @ (Z.T @ y)
    u = y - Z @ b
    g = Z * u[:, None]
    S = g.T @ g
    for j, w in enumerate(_bartlett(gecikme, n), start=1):
        G = g[j:].T @ g[:-j]
        S += w * (G + G.T)
    V = ZtZ_ters @ S @ ZtZ_ters
    return {'katsayi': b, 'se': np.sqrt(np.maximum(np.diag(V), 0.0)), 'artik': u, 'V': V}


def ols_nw_buyuk(y, X, gecikmeler=GECIKMELER) -> dict:
    """ols_nw her gecikmeyle; 'se_buyuk' parametre basina en buyuk SE (U-02)."""
    sonuc = {l: ols_nw(y, X, l) for l in gecikmeler}
    ilk = sonuc[gecikmeler[0]]
    return {'katsayi': ilk['katsayi'], 'se': {l: s['se'] for l, s in sonuc.items()},
            'se_buyuk': np.max(np.vstack([s['se'] for s in sonuc.values()]), axis=0)}


def aralik90(theta: float, se: float) -> tuple:
    """%90 guven araligi theta +- 1,645 * SE (Ss6.2)."""
    return theta - Z_90_IKI * se, theta + Z_90_IKI * se


def esdeger(theta: float, se: float, delta: float) -> bool:
    """TOST (Ss6.2): %90 aralik tamamen acik (-delta, +delta) icinde. SE nan ise gecmez."""
    if not (se == se and theta == theta):
        return False
    alt, ust = aralik90(theta, se)
    return alt > -delta and ust < delta


def rho_ust(x, y) -> dict:
    """rho_hat = rho(x, y) (haftalik; iki serinin de sonlu oldugu haftalar, U-10) ve tek tarafli %90 ust sinir
    tanh(atanh(rho_hat) + 1,2816 / sqrt(n_w - 3)) (Ss6.2). Tanimsizsa (n_w < 4 ya da sifir varyans) rho_hat nan,
    rho_ust = +1 (U-22). |rho_hat| = 1 ise atanh girisi +-(1 - 1e-12)."""
    x, y = np.asarray(x, dtype=float), np.asarray(y, dtype=float)
    if x.shape != y.shape or x.ndim != 1:
        raise ValueError("seriler ayni uzunlukta tek boyutlu olmali")
    m = np.isfinite(x) & np.isfinite(y)
    x, y = x[m], y[m]
    n = len(x)
    if n < 4 or _sabit(x) or _sabit(y):                  # kesin sabitlik (Codex T15-7)
        return {'rho_hat': float('nan'), 'rho_ust': 1.0, 'n_w': n}
    dx, dy = x - x.mean(), y - y.mean()
    sxx, syy = float(np.dot(dx, dx)), float(np.dot(dy, dy))
    if not (sxx > 0 and syy > 0):
        return {'rho_hat': float('nan'), 'rho_ust': 1.0, 'n_w': n}
    r = float(np.dot(dx, dy)) / math.sqrt(sxx * syy)
    r = min(max(r, -1.0), 1.0)
    rk = min(max(r, -RHO_KIRP), RHO_KIRP)
    return {'rho_hat': r, 'rho_ust': math.tanh(math.atanh(rk) + Z_FISHER_90 / math.sqrt(n - 3)), 'n_w': n}


def g_seyreltme(rho: float, k: float) -> float:
    """g(rho, k) = (sqrt(1 + k^2 + 2 rho k) - 1) / k (Ss6.3, Ss8.4)."""
    return (math.sqrt(1.0 + k * k + 2.0 * rho * k) - 1.0) / k


def k1_esik(rho_ust_deger: float, sr_ref: float = SR_T_REF, k: float = K_ORAN) -> float:
    """K1*(rho_ust) = SR_T,ref * g(rho_K1, k); rho_K1 = min(0,30; max(0; rho_ust)) (Ss6.3). 0,138 ... 0,370."""
    rho = min(RHO_K1_UST, max(RHO_K1_ALT, rho_ust_deger))
    return sr_ref * g_seyreltme(rho, k)


def dairesel_blok_ortalamalari(x, blok: int, cekis: int, rng: np.random.Generator) -> np.ndarray:
    """Dairesel blok bootstrap (U-03): her cekiste ceil(n/blok) baslangic {0..n-1} uzerinde tekduze (cekis basina bir
    rng.integers cagrisi), blok sarar, ilk n alinir; istatistik ortalama."""
    x = _dizi(x)
    n = len(x)
    if n < 1:
        raise ValueError("bos seri")
    n_blok = -(-n // blok)
    ofset = np.arange(blok)
    sonuc = np.empty(cekis)
    for c in range(cekis):
        bas = rng.integers(0, n, size=n_blok)
        sonuc[c] = x[((bas[:, None] + ofset[None, :]) % n).ravel()[:n]].mean()
    return sonuc


def k2_bootstrap_alt(x, tohum: int = BOOT_TOHUM, bloklar=BOOT_BLOKLAR, cekis: int = BOOT_CEKIS) -> dict:
    """K2 (Ss6.2, U-03): ort(x) icin blok basina tek tarafli %95 alt sinir (cekis ortalamalarinin 0,05 kantili, numpy
    dogrusal); tek Generator(PCG64(tohum)) bloklar sirasiyla. 'alt' = alt sinirlarin kucugu."""
    rng = np.random.default_rng(tohum)
    alt = {b: float(np.quantile(dairesel_blok_ortalamalari(x, b, cekis, rng), BOOT_KANTIL)) for b in bloklar}
    return {'blok': alt, 'alt': min(alt.values())}


def sr_bootstrap_araligi(r, tohum: int = SR_BOOT_TOHUM, blok: int = 4, cekis: int = BOOT_CEKIS) -> tuple:
    """BR-20 (U-36): Sharpe icin %90 yuzdelik aralik, dairesel blok, ayri akis (betimsel)."""
    r = _dizi(r)
    n = len(r)
    rng = np.random.default_rng(tohum)
    n_blok = -(-n // blok)
    ofset = np.arange(blok)
    sr = np.empty(cekis)
    for c in range(cekis):
        bas = rng.integers(0, n, size=n_blok)
        sr[c] = sharpe(r[((bas[:, None] + ofset[None, :]) % n).ravel()[:n]])
    sr = sr[np.isfinite(sr)]
    if not len(sr):
        return float('nan'), float('nan')
    return float(np.quantile(sr, 0.05)), float(np.quantile(sr, 0.95))


def andrews_gecikme(x) -> int:
    """BR-09 (U-35): Andrews (1991) Bartlett, AR(1): l = ceil(1,1447 (alpha n)^(1/3)),
    alpha = 4 rho^2 / ((1 - rho)^2 (1 + rho)^2); rho = sum d_t d_{t-1} / sum d_{t-1}^2 (betimsel)."""
    x = _dizi(x)
    n = len(x)
    d = x - x.mean()
    payda = float(np.dot(d[:-1], d[:-1])) if n > 1 else 0.0
    if payda <= 0:
        return 0
    rho = min(max(float(np.dot(d[1:], d[:-1])) / payda, -RHO_KIRP), RHO_KIRP)
    alfa = 4.0 * rho * rho / ((1.0 - rho) ** 2 * (1.0 + rho) ** 2)
    return int(math.ceil(1.1447 * (alfa * n) ** (1.0 / 3.0)))


def standart_yukleme(b: float, se_b: float, sd_x: float, sd_rp: float) -> tuple:
    """K11 (Ss6.2): b~ = b * sd(x) / sd(r^P), SE(b~) = SE_NW(b) * sd(x) / sd(r^P); sd'ler ddof 1."""
    if not sd_rp > 0:
        return float('nan'), float('nan')
    return b * sd_x / sd_rp, se_b * sd_x / sd_rp
