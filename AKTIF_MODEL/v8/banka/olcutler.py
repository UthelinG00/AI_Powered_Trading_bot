"""Banka olcutleri (saf; BANKA_ONKAYIT_TASLAK Ss3.1, Ss3.3, Ss3.4). Girdi gunluk basit getiri dizileridir; kaynak
(motor kosusu ya da Duzey 1 ureteci) bilinmez. Kalibrasyon ve banka ayni fonksiyonlari kullanir.

Tanimlar (belgenin acik biraktigi yerlerde bu dosyadaki secim gecerlidir; hicbiri D'ye bakilarak secilmedi):
- Sharpe: ortalama / std (n - 1) * sqrt(365); n < 2 ya da std = 0 ise nan (hicbir esigi gecmez).
- DSR'deki SR: gunluk (yilliklanmamis) ortalama / std (n - 1); carpiklik ve basiklik anlarla (n paydasi), basiklik
  normal = 3; T = gun sayisi.
- eta: ornek otokorelasyonu rho_k = sum (r_t - m)(r_{t-k} - m) / sum (r_t - m)^2; Bartlett agirligi (1 - k/11), k = 1..10.
"""
import math
from statistics import NormalDist

import numpy as np

_N = NormalDist()
GUN_YIL = 365
EULER = 0.5772156649015329


def _dizi(r) -> np.ndarray:
    r = np.asarray(r, dtype=float)
    if r.ndim != 1:
        raise ValueError("getiri dizisi tek boyutlu olmali")
    if np.isnan(r).any():
        raise ValueError("getiri dizisinde nan var")
    return r


def sharpe(r) -> float:
    """Yillik Sharpe (Ss3.1): gunluk ortalama / std * sqrt(365); risksiz oran 0."""
    r = _dizi(r)
    if len(r) < 2:
        return float('nan')
    s = float(np.std(r, ddof=1))
    return float(np.mean(r)) / s * math.sqrt(GUN_YIL) if s > 0 else float('nan')


def anlar(r) -> tuple:
    """(carpiklik g3, basiklik g4; normal = 3). Sabit seride (nan, nan)."""
    r = _dizi(r)
    d = r - r.mean()
    m2 = float(np.mean(d ** 2))
    if m2 <= 0:
        return float('nan'), float('nan')
    return float(np.mean(d ** 3)) / m2 ** 1.5, float(np.mean(d ** 4)) / m2 ** 2


def eta(r, gecikme: int = 10) -> float:
    """Ss3.3 seri bagimlilik duzeltmesi; eta < 1 ise 1."""
    r = _dizi(r)
    d = r - r.mean()
    payda = float(np.sum(d * d))
    if payda <= 0:
        return 1.0
    toplam = 0.0
    for k in range(1, gecikme + 1):
        if k >= len(r):
            break
        rho = float(np.sum(d[k:] * d[:-k])) / payda
        toplam += (1.0 - k / (gecikme + 1)) * rho
    return max(1.0 + 2.0 * toplam, 1.0)


def sr0(N: int, sigma_sr: float) -> float:
    """Ss3.3 SR_0 (gunluk birim). N: deneme sayisi (>= 2); sigma_sr: yillik Sharpe'lar arasi std."""
    if N < 2:
        raise ValueError("N >= 2 olmali")
    s_g = sigma_sr / math.sqrt(GUN_YIL)
    return s_g * ((1.0 - EULER) * _N.inv_cdf(1.0 - 1.0 / N) + EULER * _N.inv_cdf(1.0 - 1.0 / (N * math.e)))


def dsr(r, N: int, sigma_sr: float, gecikme: int = 10) -> dict:
    """Deflated Sharpe (Ss3.3, eta duzeltmeli). Doner: dsr, sr_gunluk, sr0, g3, g4, eta, T."""
    r = _dizi(r)
    T = len(r)
    s = float(np.std(r, ddof=1)) if T >= 2 else 0.0
    sr = float(np.mean(r)) / s if s > 0 else float('nan')
    g3, g4 = anlar(r)
    e = eta(r, gecikme)
    z0 = sr0(N, sigma_sr)
    sonuc = {'sr_gunluk': sr, 'sr0': z0, 'g3': g3, 'g4': g4, 'eta': e, 'T': T, 'dsr': float('nan')}
    if not (math.isfinite(sr) and math.isfinite(g3) and math.isfinite(g4)) or T < 2:
        return sonuc
    payda = e * (1.0 - g3 * sr + (g4 - 1.0) / 4.0 * sr * sr)
    if payda <= 0:
        return sonuc
    sonuc['dsr'] = _N.cdf((sr - z0) * math.sqrt(T - 1) / math.sqrt(payda))
    return sonuc


def dilim_sharpeleri(r, etiket, dilimler=(0, 1, 2, 3)) -> list:
    """Her dilimin (etiket == j gunleri) Sharpe'i."""
    r, etiket = _dizi(r), np.asarray(etiket)
    return [sharpe(r[etiket == j]) for j in dilimler]


def en_iyi_dilim_haric(r, etiket, dilimler=(0, 1, 2, 3)) -> tuple:
    """B4: toplam log getirisi en yuksek dilim cikarilir; kalan dilim gunlerinin Sharpe'i. Doner (sr, cikan)."""
    r, etiket = _dizi(r), np.asarray(etiket)
    if np.any(r <= -1.0):
        raise ValueError("getiri <= -1 (log tanimsiz)")
    loglar = [float(np.sum(np.log1p(r[etiket == j]))) for j in dilimler]
    cikan = dilimler[int(np.argmax(loglar))]
    kalan = np.isin(etiket, [j for j in dilimler if j != cikan])
    return sharpe(r[kalan]), cikan


def epizot_payi(epizot_pnl, toplam_net: float) -> float:
    """B5: en iyi 3 epizot P&L'i / toplam net P&L. Toplam <= 0 ise inf (B5 kalir)."""
    if not toplam_net > 0:
        return float('inf')
    x = np.sort(np.asarray(epizot_pnl, dtype=float))[::-1]
    return float(np.sum(x[:3])) / float(toplam_net)


def en_buyuk_dusus(sr_ana: float, sr_cikarilmis) -> float:
    """B10: ana Sharpe'tan tek cikarma kosularinin en buyuk dususu. nan cikarma kosusu dusus = inf sayilir."""
    x = np.asarray(sr_cikarilmis, dtype=float)
    if len(x) == 0:
        return 0.0
    if np.isnan(x).any() or not math.isfinite(sr_ana):
        return float('inf')
    return float(np.max(sr_ana - x))


def mdd(nav) -> float:
    """En buyuk dusus (pozitif oran); nav zaten baslangic degeriyle baslar."""
    nav = np.asarray(nav, dtype=float)
    tepe = np.maximum.accumulate(nav)
    return float(np.max(1.0 - nav / tepe))


def vol_olcekli_mdd(r, hedef_vol: float = 0.15) -> float:
    """B11: gunluk getiri serisi gerceklesen vol'u hedef_vol'e dogrusal olceklenir, bilesik NAV'in MDD'si.
    NAV 1'den baslar; olcekli getiri <= -1 olursa MDD 1 (iflas)."""
    r = _dizi(r)
    s = float(np.std(r, ddof=1)) if len(r) >= 2 else 0.0
    if not s > 0:
        return float('nan')
    x = r * (hedef_vol / (s * math.sqrt(GUN_YIL)))
    if np.any(x <= -1.0):
        return 1.0
    nav = np.concatenate(([1.0], np.cumprod(1.0 + x)))
    return mdd(nav)


def wilson(k: int, n: int, z: float = 1.959963984540054) -> tuple:
    """Wilson %95 araligi (alt, ust) ve nokta kestirimi: (p, alt, ust)."""
    if n <= 0:
        return float('nan'), float('nan'), float('nan')
    p = k / n
    z2 = z * z
    merkez = (p + z2 / (2 * n)) / (1 + z2 / n)
    yari = z * math.sqrt(p * (1 - p) / n + z2 / (4 * n * n)) / (1 + z2 / n)
    alt = 0.0 if k == 0 else max(0.0, merkez - yari)
    ust = 1.0 if k == n else min(1.0, merkez + yari)
    return p, alt, ust
