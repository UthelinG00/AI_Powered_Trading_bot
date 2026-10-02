"""Kanal stres bindirmeleri (BANKA §5.4; R12, Kelly sütunları; BK-4, BK-8). Deterministik; motor koşusu değildir.

Girdi: birincil örneklemin günleri için gün sonu gerçekleşen net kitap ağırlıkları (koşunun L'siyle; q·kapanış/NAV) ve
günlük basit getiri. Aileler:
  D90-k: nesne en büyük tek alt long ağırlığı w_max;          çarpan 1 − 0,90·w_max        (k ∈ {1, 2, 4} olay/yıl)
  SQ-k : nesne en büyük tek alt short'un mutlak ağırlığı;      çarpan 1 − 3,00·|w_min|
  DM-1 : nesne en büyük üç alt long ağırlığının toplamı;        çarpan 1 − 0,90·(w₁ + w₂ + w₃)  (1 olay/yıl)
Kurallar: örneklem baştan ⌊365/k⌋ günlük ardışık bloklara bölünür (BK-8); son blok kısmiysa uzunluğu blok uzunluğunun
en az yarısıysa olay uygulanır. Her blokta nesnenin en yüksek olduğu gün seçilir (eşitlikte önceki gün); nesne 0 ise
"boş olay". Çarpan olay gününden SONRAKİ ilk ölçüte dahil günün getirisine uygulanır (BK-8; görülmüş gün dışlaması
şoku silmesin); öyle gün yoksa olay gününün kendisine. Sonraki getiriler değişmez (bindirme). Karşı tarafa kredi yok.
"""
import numpy as np

AILELER = {'D90': 0.90, 'SQ': 3.00, 'DM': 0.90}
SIKLIK = {'D90': (1, 2, 4), 'SQ': (1, 2, 4), 'DM': (1,)}


def nesneler(agirliklar: list, btc_eth=('BTCUSDT', 'ETHUSDT')) -> dict:
    """agirliklar: gün başına {coin: w} (gün sonu). Doner {'D90', 'SQ', 'DM'} -> gün dizisi (≥ 0)."""
    d90, sq, dm = [], [], []
    for w in agirliklar:
        alt = [float(v) for c, v in w.items() if c not in btc_eth]
        uzun = sorted((v for v in alt if v > 0), reverse=True)
        kisa = [-v for v in alt if v < 0]
        d90.append(uzun[0] if uzun else 0.0)
        sq.append(max(kisa) if kisa else 0.0)
        dm.append(float(sum(uzun[:3])))
    return {'D90': np.array(d90), 'SQ': np.array(sq), 'DM': np.array(dm)}


def bloklar(n_gun: int, k: int) -> list:
    L = 365 // k
    out = []
    for a in range(0, n_gun, L):
        b = min(a + L, n_gun)
        if b - a == L or 2 * (b - a) >= L:
            out.append((a, b))
    return out


def olaylar(nesne: np.ndarray, k: int) -> list:
    """Blok başına (olay günü indeksi ya da None = boş olay)."""
    out = []
    for a, b in bloklar(len(nesne), k):
        i = a + int(np.argmax(nesne[a:b]))              # argmax ilk en büyüğü verir: eşitlikte önceki gün
        out.append(i if nesne[i] > 0 else None)
    return out


def bindir(r: np.ndarray, nesne: np.ndarray, aile: str, k: int, dahil: np.ndarray = None) -> dict:
    """r: örneklem günlerinin basit getirisi; dahil: ölçüte giren günler (görülmüş günler False). Doner stresli getiri,
    olay günleri, boş olay sayısı."""
    r = np.asarray(r, dtype=float).copy()
    dahil = np.ones(len(r), dtype=bool) if dahil is None else np.asarray(dahil, dtype=bool)
    sok = AILELER[aile]
    gunler, bos = [], 0
    for i in olaylar(np.asarray(nesne, dtype=float), k):
        if i is None:
            bos += 1
            continue
        j = next((x for x in range(i + 1, len(r)) if dahil[x]), i)
        carpan = 1.0 - sok * float(nesne[i])
        r[j] = (1.0 + r[j]) * carpan - 1.0
        gunler.append(i)
    return {'r': r, 'olay_gunleri': gunler, 'bos_olay': bos}
