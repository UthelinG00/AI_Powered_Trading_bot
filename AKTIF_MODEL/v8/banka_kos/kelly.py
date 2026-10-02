"""Kelly tablosu ve uygun kaldıraç kümesi (BANKA §4; KC-10; BK-9). Girdi: her L için birincil örneklemin günlük basit
getirisi (görülmüş günler düşülmüş) ve gün damgaları.

- Metrikler: CAGR = Π(1 + r)^(365/n) − 1; vol = std(ddof 1)·√365; SR (banka.olcutler.sharpe); MDD (NAV 1'den bileşik);
  en uzun DD süresi (tepeden tepeyi geri alana kadar gün; geri alınmadıysa örneklem sonuna kadar); Calmar = CAGR/MDD;
  en kötü gün; en kötü takvim ayı (ay içi bileşik).
- Bootstrap MDD (BK-9): durağan blok bootstrap (Politis–Romano; geometrik blok, ortalama 20 gün, dairesel), 2.000 çekiş,
  her çekiş 3 yıllık (1.095 gün) yol; q50, q95 ve P(MDD > %30). Tohum uretec(tohum_banka, 'kelly', 10·L, maliyet_k)
  (§3.1'deki Sharpe bootstrap'ıyla aynı biçim).
- Kelly: L = 1 koşusundan f* = μ/σ² (günlük; oran yıllıklandırmadan bağımsız). L'nin Kelly kesri = vol_L / (f*·vol_1).
  0,25 / 0,5 / 0,75 / 1 kesirlerine en yakın L işaretlenir.
- 𝓛* = {L : MDD_gerçekleşen(L) ≤ %30 ve q95_bootstrap(L) ≤ %30}; varsayılan öneri 𝓛* içinde CAGR'ı en yüksek L,
  eşitlikte küçük L; boşsa zorunlu cümle.
"""
import math
from datetime import datetime, timezone

import numpy as np

from banka.olcutler import mdd, sharpe

DD_SINIRI = 0.30
UFUK_GUN = 1095
CEKIS = 2000
BLOK_ORT = 20
BOS_CUMLE = "Kullanıcı hedefine (%30 DD) uygun kaldıraç yok."
KARSILAMIYOR = "kullanıcı hedefini (%30 DD) KARŞILAMIYOR"


def _nav(r) -> np.ndarray:
    return np.concatenate(([1.0], np.cumprod(1.0 + np.asarray(r, dtype=float))))


def en_uzun_dd_gun(r) -> int:
    """Önceki tepenin altında geçen en uzun ardışık gün sayısı (geri alınmadıysa örneklem sonuna kadar)."""
    nav = _nav(r)
    tepe_i, en_uzun = 0, 0
    for i in range(1, len(nav)):
        if nav[i] >= nav[tepe_i]:
            en_uzun = max(en_uzun, i - tepe_i - 1)
            tepe_i = i
    return max(en_uzun, len(nav) - 1 - tepe_i)


def en_kotu_ay(r, gunler_ms) -> float:
    aylar = {}
    for x, t in zip(np.asarray(r, dtype=float), np.asarray(gunler_ms, dtype=np.int64)):
        d = datetime.fromtimestamp(int(t) / 1000, timezone.utc)
        aylar[(d.year, d.month)] = aylar.get((d.year, d.month), 1.0) * (1.0 + x)
    return min(v - 1.0 for v in aylar.values()) if aylar else float('nan')


def metrikler(r, gunler_ms) -> dict:
    r = np.asarray(r, dtype=float)
    n = len(r)
    if n < 2 or not np.isfinite(r).all():
        return {'hata': 'seri kisa ya da sonlu degil'}
    buyume = float(np.prod(1.0 + r))
    cagr = buyume ** (365.0 / n) - 1.0 if buyume > 0 else -1.0
    m = mdd(_nav(r))
    return {'cagr': cagr, 'vol': float(np.std(r, ddof=1)) * math.sqrt(365), 'sr': sharpe(r), 'mdd': m,
            'en_uzun_dd_gun': en_uzun_dd_gun(r), 'calmar': cagr / m if m > 0 else float('inf'),
            'en_kotu_gun': float(r.min()), 'en_kotu_ay': en_kotu_ay(r, gunler_ms)}


def duragan_indeksler(n: int, uzunluk: int, rng: np.random.Generator, blok_ort: float = BLOK_ORT) -> np.ndarray:
    """Politis–Romano: her adımda 1/blok_ort olasılıkla yeni tekdüze başlangıç, aksi halde dairesel devam."""
    p = 1.0 / blok_ort
    out = np.empty(uzunluk, dtype=np.int64)
    i = int(rng.integers(0, n))
    yeni = rng.random(uzunluk)
    bas = rng.integers(0, n, size=uzunluk)
    for t in range(uzunluk):
        if t > 0:
            i = int(bas[t]) if yeni[t] < p else (i + 1) % n
        out[t] = i
    return out


def mdd_bootstrap(r, rng: np.random.Generator, ufuk: int = UFUK_GUN, cekis: int = CEKIS) -> dict:
    r = np.asarray(r, dtype=float)
    m = np.array([mdd(_nav(r[duragan_indeksler(len(r), ufuk, rng)])) for _ in range(cekis)])
    return {'q50': float(np.quantile(m, 0.50)), 'q95': float(np.quantile(m, 0.95)),
            'p_asim': float(np.mean(m > DD_SINIRI))}


def kelly_tablosu(r_L: dict, gunler_ms, tohum_banka: int, maliyet_k: float = 1.0, cekis: int = CEKIS) -> dict:
    """r_L: {L: günlük getiri}. L = 1 bulunmalı. Doner satırlar, işaretler, 𝓛* ve öneri."""
    from kalibrasyon.tohum import uretec
    if 1.0 not in r_L:
        raise ValueError("L = 1 koşusu gerekli")
    r1 = np.asarray(r_L[1.0], dtype=float)
    var1 = float(np.var(r1, ddof=1))
    f_yildiz = float(np.mean(r1)) / var1 if var1 > 0 else float('nan')
    vol1 = float(np.std(r1, ddof=1))
    satirlar = {}
    for L in sorted(r_L):
        r = np.asarray(r_L[L], dtype=float)
        s = metrikler(r, gunler_ms)
        s['bootstrap'] = mdd_bootstrap(r, uretec(tohum_banka, 'kelly', int(round(10 * L)), int(maliyet_k)), cekis=cekis)
        s['kelly_kesri'] = (float(np.std(r, ddof=1)) / (f_yildiz * vol1)
                            if f_yildiz and math.isfinite(f_yildiz) and f_yildiz > 0 and vol1 > 0 else float('nan'))
        s['dd_gercek_ok'] = bool(s.get('mdd', 1.0) <= DD_SINIRI)
        s['dd_boot_ok'] = bool(s['bootstrap']['q95'] <= DD_SINIRI)
        s['etiket'] = None if (s['dd_gercek_ok'] and s['dd_boot_ok']) else KARSILAMIYOR
        satirlar[L] = s
    isaret = {}
    for hedef in (0.25, 0.5, 0.75, 1.0):
        adaylar = [(abs(v['kelly_kesri'] - hedef), L) for L, v in satirlar.items() if math.isfinite(v['kelly_kesri'])]
        isaret[hedef] = min(adaylar)[1] if adaylar else None
    uygun = sorted(L for L, v in satirlar.items() if v['dd_gercek_ok'] and v['dd_boot_ok'])
    oneri = max(uygun, key=lambda L: (satirlar[L]['cagr'], -L)) if uygun else None
    return {'satirlar': satirlar, 'f_yildiz': f_yildiz, 'kesir_isaretleri': isaret, 'uygun_L': uygun,
            'varsayilan_oneri': oneri, 'cumle': None if uygun else BOS_CUMLE}
