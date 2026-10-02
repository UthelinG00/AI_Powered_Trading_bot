"""Carry kapisi fiyat faktorleri (saf; CARRY Ss6.2 K9/K11; U-19, U-24; U-41).

- Haftalik basit getiri: Pazartesi 00:00'daki son kapanistan (motorun sk degerlemesi, gorunum.son_kapanis) bir sonraki
  Pazartesi 00:00'daki son kapanisa. Hafta icinde bari biten isim son kapanisiyla kalir (U-19).
- x_B: BTC. x_A: o Pazartesinin carry aday evrenindeki alt isimlerin (BTC haric) esit agirlikli ortalamasi.
- x_R, x_S: Pazartesi PIT R30 ve s^trend siralamasi (motorun o Pazartesi carry siralamasinda kullandigi degerler),
  ayni haftanin getirisi (r^P_w ile hizali); ust/alt floor(0,30 n) isim (en az 1; tamsayi aritmetigi), uzun - kisa =
  ort(uzun) - ort(kisa); siralama butun carry adaylarinda (U-24). Esitlikte alfabetik (Ss6.3 K8 notuyla ayni).
  Degeri tanimsiz (nan) isim o faktorun siralamasina girmez (U-41). n < 2 ya da aday yoksa faktor nan (K9/K11
  hesaplanamaz -> kaldi, Ss7.1).
"""
import math

import numpy as np

from motor.gorunum import son_kapanis

HAFTA_MS = 7 * 86_400_000


def hafta_getirisi(barlar: dict, coin: str, t0_ms: int, t1_ms: int) -> float:
    s = barlar.get(coin)
    if s is None:
        return float('nan')
    a, b = son_kapanis(s, t0_ms), son_kapanis(s, t1_ms)
    if a is None or b is None or not a > 0:
        return float('nan')
    return b / a - 1.0


def uzun_kisa(deger: dict, getiri: dict) -> float:
    """deger: isim -> PIT siralama degeri; getiri: isim -> ayni haftanin getirisi."""
    adlar = [c for c, v in deger.items() if v is not None and math.isfinite(v) and math.isfinite(getiri.get(c, math.nan))]
    n = len(adlar)
    if n < 2:
        return float('nan')
    k = max(1, (3 * n) // 10)
    ust = sorted(adlar, key=lambda c: (-deger[c], c))[:k]
    alt = sorted(adlar, key=lambda c: (deger[c], c))[:k]
    return float(np.mean([getiri[c] for c in ust])) - float(np.mean([getiri[c] for c in alt]))


def faktorler(barlar: dict, pazartesiler: list, hafta_ms, btc: str = 'BTCUSDT') -> dict:
    """pazartesiler[w] = {'adaylar': [...], 'r30': {isim: deger}, 's_trend': {isim: deger}} (hafta_ms[w] karari).
    Doner: {'x_B', 'x_A', 'x_R', 'x_S'} haftalik diziler."""
    hafta_ms = np.asarray(hafta_ms, dtype=np.int64)
    if len(pazartesiler) != len(hafta_ms):
        raise ValueError("Pazartesi kaydi sayisi hafta sayisina esit degil")
    out = {k: np.full(len(hafta_ms), np.nan) for k in ('x_B', 'x_A', 'x_R', 'x_S')}
    for w, (t, pz) in enumerate(zip(hafta_ms.tolist(), pazartesiler)):
        t1 = t + HAFTA_MS
        out['x_B'][w] = hafta_getirisi(barlar, btc, t, t1)
        adaylar = sorted(c for c in pz['adaylar'] if c != btc)
        g = {c: hafta_getirisi(barlar, c, t, t1) for c in adaylar}
        tanimli = [g[c] for c in adaylar if math.isfinite(g[c])]
        if tanimli and len(tanimli) == len(adaylar):
            out['x_A'][w] = float(np.mean(tanimli))
        out['x_R'][w] = uzun_kisa({c: pz['r30'].get(c, math.nan) for c in adaylar}, g)
        out['x_S'][w] = uzun_kisa({c: pz['s_trend'].get(c, math.nan) for c in adaylar}, g)
    return out
