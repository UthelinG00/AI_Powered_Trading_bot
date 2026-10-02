"""T5 parite tekrarı (BANKA §2.5 T5, §3.7 netleştirme 20 d; MIMARI §5.6 senaryo 1). Birincil birimin karar günlerinden
20'si uretec(tohum_banka, 'parite') ile yerine koymadan seçilir. Her T'de durum, günlüğün T'deki ilk karar kaydından
önceki öneğinden (T'deki funding ve delist uzlaşması dahil; 20 h) `durum_turet` ile kurulur (canlı yol) ve `karar_ver` geri test kararıyla karşılaştırılır:
ağırlıklar (w*, w^u, w0, bantlı) mutlak fark ≤ 1e-12; niyetler, iptaller, evren ve maske birebir. Çıktı açık gruba
gider: yalnız sayılar ve seçilen günlerin sha256'sı (performans yok)."""
import hashlib
import math

import numpy as np

from kalibrasyon.tohum import uretec
from motor.durum import durum_turet
from motor.gorunum import gorunum_kur
from motor.gunluk import OlayGunlugu
from motor.karar import karar_ver

N_PARITE = 20
TOL = 1e-12
AGIRLIK = ('w_yildiz', 'w_birim', 'w_mevcut')


def _agirlik_esit(a: dict, b: dict) -> bool:
    return set(a) == set(b) and all(math.isclose(a[c], b[c], rel_tol=0.0, abs_tol=TOL) for c in a)


def karar_esit(a, b) -> bool:
    ha, hb = a.hedef.json(), b.hedef.json()
    if not all(_agirlik_esit(ha.pop(k), hb.pop(k)) for k in AGIRLIK):
        return False
    return (ha == hb and _agirlik_esit(a.bantli, b.bantli)
            and {c: e.json() for c, e in a.niyetler.items()} == {c: e.json() for c, e in b.niyetler.items()}
            and a.iptaller == b.iptaller and tuple(a.evren) == tuple(b.evren) and a.evren_ms == b.evren_ms
            and a.maske == b.maske)


def _onek(kayitlar: tuple, t_ms: int) -> OlayGunlugu:
    for i, k in enumerate(kayitlar):
        if k.damga_ms == t_ms and k.tur == 'karar':
            return OlayGunlugu.kayitlardan(kayitlar[:i])
    raise ValueError("karar kaydi bulunamadi")


def karar_paritesi(s, veri, i: int, L: float, p, filtreler: dict, kayitlar: tuple = None) -> bool:
    """i'inci geri test kararı canlı yolla aynı mı."""
    kayitlar = s.gunluk.kayitlar() if kayitlar is None else kayitlar
    t = int(s.kararlar[i].hedef.t_ms)
    g = gorunum_kur(veri, t)
    return karar_esit(karar_ver(g, durum_turet(g, _onek(kayitlar, t)), L, p, filtreler), s.kararlar[i])


def parite(s, veri, L: float, p, filtreler: dict, tohum_banka: int, n: int = N_PARITE) -> dict:
    """s: geri test sonucu (KosuSonucu). Doner {'secilen', 'hata', 'gunler_sha256'} (T5 = hata > 0)."""
    kararlar = s.kararlar
    rng = uretec(tohum_banka, 'parite')
    sec = sorted(int(i) for i in rng.choice(len(kararlar), size=min(n, len(kararlar)), replace=False))
    kayitlar = s.gunluk.kayitlar()
    hata = sum(0 if karar_paritesi(s, veri, i, L, p, filtreler, kayitlar) else 1 for i in sec)
    gunler = [int(kararlar[i].hedef.t_ms) for i in sec]
    return {'secilen': len(sec), 'hata': hata,
            'gunler_sha256': hashlib.sha256(np.asarray(gunler, dtype=np.int64).tobytes()).hexdigest()}
