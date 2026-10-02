"""PIT trend evreni: aylik secim, histerezis ve oncelik kurali (saf). MIMARI Ss2.3, Ss2.4.

Ag, dosya, config veya durum erisimi yoktur.
"""
from dataclasses import dataclass

from .gorunum import GUN_MS, PiyasaGorunumu, ilk_bar_ms, v60
from .tipler import Parametreler


@dataclass(frozen=True)
class EvrenSonucu:
    uyeler: tuple          # BTC, ETH (uygunsa), sonra altlar alt-sirasi duzeninde
    alt_sira: dict         # uygun alt -> sira (1'den baslar)
    v60: dict              # uygunluk degerlendirilen her coin -> V60
    uygun: tuple           # uygunluk kosulunu saglayan butun coinler


def uygun_mu(g: PiyasaGorunumu, coin: str, t_ms: int, maskeli: bool, v60_deger: float,
             p: Parametreler) -> bool:
    """Isinma (ilk bardan 90 gun), maskesiz, V60 >= 20M (giris ve kalis tabani)."""
    s = g.barlar.get(coin)
    if s is None or len(s) == 0 or maskeli:
        return False
    if ilk_bar_ms(s) > t_ms - p.isinma_gun * GUN_MS:
        return False
    return v60_deger >= p.hacim_taban_v60


def evren_sec(g: PiyasaGorunumu, t_ms: int, onceki_uyeler: tuple, maske: dict, p: Parametreler) -> EvrenSonucu:
    """MIMARI Ss2.3 oncelik kurali:
    1. Mevcut alt uyelerden alt-sirasi <= 20 olanlar sira duzeninde tutulur.
    2. Bunlar 13'u asarsa en kotu siradakiler cikar.
    3. Bos yuvalar alt-sirasi <= 15 olan yeni adaylarla sira duzeninde dolar.
    4. Esitlikte alfabetik sira. 5. Yetersiz aday varsa yuva bos kalir.
    """
    v60ler = {}
    uygunlar = []
    for coin in sorted(set(g.adaylar)):
        s = g.barlar.get(coin)
        if s is None:
            continue
        v = v60(s, t_ms, p.v60_gun)
        v60ler[coin] = v
        m = maske.get(coin)
        if uygun_mu(g, coin, t_ms, bool(m and m.maskeli), v, p):
            uygunlar.append(coin)

    sabitler = [c for c in (p.btc, p.eth) if c in uygunlar]
    altlar = [c for c in uygunlar if c not in (p.btc, p.eth)]
    altlar.sort(key=lambda c: (-v60ler[c], c))
    alt_sira = {c: i + 1 for i, c in enumerate(altlar)}

    yuva = p.evren_n - 2
    tutulan = [c for c in onceki_uyeler if c in alt_sira and alt_sira[c] <= p.alt_kalis_sira]
    tutulan.sort(key=lambda c: alt_sira[c])
    tutulan = tutulan[:yuva]
    yeni = [c for c in altlar if c not in tutulan and alt_sira[c] <= p.alt_giris_sira]
    secilen = tutulan + yeni[:max(0, yuva - len(tutulan))]
    secilen.sort(key=lambda c: alt_sira[c])
    return EvrenSonucu(uyeler=tuple(sabitler + secilen), alt_sira=alt_sira, v60=v60ler, uygun=tuple(uygunlar))
