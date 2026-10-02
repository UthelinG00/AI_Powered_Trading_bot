"""Duzey 1 esik kurallari ve birlesik kabul (BANKA_ONKAYIT_TASLAK Ss3.7 "Esik kurallari", "Birlesik yanlis kabul ve
guc"; Ss3.3 kural 2-4). Girdi: ayar basina (n_yol, len(SR_IZGARASI), len(ALANLAR)) dizileri (duzey1_olcut).

- e_B5: her ayarda P(B5 gecer | SR_ref) >= 0,95 saglayan en kucuk esik (B5 gecer <=> pay < e), yuzde puanina yukari;
  128 ayarin en buyugu. > %60 ise B5 rapora iner.
- e_B10: ayni kural (B10 gecer <=> dusus < e), 0,01'e yukari; > 0,40 ise B10 rapora iner.
- k_B6: her ayarda P(B6 >= 3 | SR_ref) >= 0,90 ise 3, degilse 2.
- Birlesik kabul (B7 yok; Duzey 1): B2 (bagliysa DSR >= d), B3 (x2 SR >= b3_esik, x3 SR > 0), B4 (>= b4_esik),
  B5 (bagliysa pay < e_B5), B6 (sayi >= k_B6), B8 (> 0), B9 (> 0), B10 (bagliysa dusus < e_B10), B11 (MDD <= %30).
  nan her karsilastirmada kalir (muhafazakar)."""
import math
from dataclasses import dataclass
from statistics import NormalDist

import numpy as np

from banka.olcutler import sr0

from .duzey1 import SR_IZGARASI, SR_REF
from .duzey1_olcut import ALANLAR

_N = NormalDist()
IX = {a: i for i, a in enumerate(ALANLAR)}
REF = SR_IZGARASI.index(SR_REF)
E_B5_UST, E_B10_UST = 0.60, 0.40
B3_ESIK, B4_ESIK, AYAR_ESIK = 0.30, 0.30, 0.40
B11_ESIK = 0.30


def _yukari(x: float, adim: float) -> float:
    """x'ten kesin buyuk, adimin kati en kucuk esik (x inf ise inf). Epsilon yok: aday izgara degeri (10 basamaga
    yuvarlanmis) kesin x < e ile dogrulanir (Codex T12-11)."""
    if not math.isfinite(x):
        return math.inf
    n = math.floor(x / adim) - 1
    while True:
        e = round(n * adim, 10)
        if x < e:
            return e
        n += 1


def ayar_esigi(degerler: np.ndarray, olasilik: float, adim: float) -> float:
    """frac(deger < e) >= olasilik saglayan, adimin kati en kucuk e. nan deger kalir sayilir."""
    x = np.sort(np.where(np.isnan(degerler), np.inf, degerler))
    k = math.ceil(olasilik * len(x))
    return _yukari(float(x[k - 1]), adim)


def e_b5(sonuclar: dict) -> float:
    return max(ayar_esigi(a[:, REF, IX['b5']], 0.95, 0.01) for a in sonuclar.values())


def e_b10(sonuclar: dict) -> float:
    return max(ayar_esigi(a[:, REF, IX['b10']], 0.95, 0.01) for a in sonuclar.values())


def k_b6(sonuclar: dict) -> int:
    return 3 if all(float(np.mean(a[:, REF, IX['b6']] >= 3)) >= 0.90 for a in sonuclar.values()) else 2


def dsr_vek(a: np.ndarray, N: int, sigma_sr: float) -> np.ndarray:
    """a: (..., ALANLAR) dizisi; Ss3.3 DSR (eta duzeltmeli), vektorel. Tanimsizsa nan."""
    sr, g3, g4, eta, T = (a[..., IX[k]] for k in ('sr_gunluk', 'g3', 'g4', 'eta', 'T'))
    z0 = sr0(N, sigma_sr)
    payda = eta * (1.0 - g3 * sr + (g4 - 1.0) / 4.0 * sr * sr)
    with np.errstate(invalid='ignore', divide='ignore'):
        z = (sr - z0) * np.sqrt(T - 1.0) / np.sqrt(payda)
    out = np.full(z.shape, np.nan)
    ok = np.isfinite(z) & (payda > 0)
    out[ok] = [_N.cdf(float(x)) for x in z[ok]]
    return out


@dataclass(frozen=True)
class Kurallar:
    N: int
    sigma_sr: float
    b2_bagli: bool
    d: float                       # b2_bagli ise DSR esigi
    b3_esik: float = B3_ESIK
    b4_esik: float = B4_ESIK
    e_b5: float = None             # None: B5 rapor
    k_b6: int = 2
    e_b10: float = None            # None: B10 rapor


def kabul(a: np.ndarray, k: Kurallar) -> np.ndarray:
    """a: (n_yol, len(SR), ALANLAR) ya da (n_yol, ALANLAR). Doner ayni on boyutlarda bool dizi."""
    g = lambda ad: a[..., IX[ad]]
    ok = (g('b3_2') >= k.b3_esik) & (g('b3_3') > 0) & (g('b4') >= k.b4_esik) & (g('b6') >= k.k_b6)
    ok &= (g('b8') > 0) & (g('b9') > 0) & (g('b11') <= B11_ESIK)
    if k.b2_bagli:
        ok &= dsr_vek(a, k.N, k.sigma_sr) >= k.d
    if k.e_b5 is not None:
        ok &= g('b5') < k.e_b5
    if k.e_b10 is not None:
        ok &= g('b10') < k.e_b10
    return ok


def kabul_oranlari(sonuclar: dict, k: Kurallar) -> dict:
    """ayar -> P(KABUL | SR) dizisi (len(SR_IZGARASI))."""
    return {no: kabul(a, k).mean(axis=0) for no, a in sonuclar.items()}
