"""Islem bandi (saf). MIMARI Ss3.6.

Ag, dosya, config veya durum erisimi yoktur.
"""
from dataclasses import dataclass

import numpy as np

from .tipler import Parametreler


class BantGirdiHatasi(ValueError):
    """Girdi dizileri bos/uyumsuz."""


@dataclass(frozen=True)
class BandSonucu:
    w: np.ndarray
    band_genisligi: np.ndarray
    gecersiz: np.ndarray      # bool: dogrudan hedefe gidildi (band atlandi)
    islem_yapildi: np.ndarray  # bool: agirlik degisti (gecersiz ya da sinir disi)


def bant_uygula(w_hedef, w_mevcut, ekstra_gecersiz, p: Parametreler) -> BandSonucu:
    """b_i = max(0.20*|w*_i|, 0.002). w_mevcut band icindeyse degismez; disindaysa en yakin sinira gider.

    Band gecersiz (dogrudan w_hedef'e): w_hedef=0; isaret uyusmazligi (w_mevcut=0 dahil); ekstra_gecersiz
    (evrenden cikis / maske / mevcut pozisyonun bir isim tavanini asmasi -- cagiran taraftan gelir).
    """
    w_hedef = np.asarray(w_hedef, dtype=float)
    w_mevcut = np.asarray(w_mevcut, dtype=float)
    ekstra_gecersiz = np.asarray(ekstra_gecersiz, dtype=bool)
    n = len(w_hedef)
    if not (len(w_mevcut) == n and len(ekstra_gecersiz) == n) or n == 0:
        raise BantGirdiHatasi("w_hedef, w_mevcut, ekstra_gecersiz ayni, sifirdan buyuk uzunlukta olmali")

    b = np.maximum(p.bant_oran * np.abs(w_hedef), p.bant_taban)
    isaret_uyumsuz = np.sign(w_hedef) != np.sign(w_mevcut)
    gecersiz = (w_hedef == 0) | isaret_uyumsuz | ekstra_gecersiz

    ust = w_hedef + b
    alt = w_hedef - b
    icinde = (~gecersiz) & (w_mevcut >= alt) & (w_mevcut <= ust)
    disinda = (~gecersiz) & (~icinde)

    w = np.where(gecersiz, w_hedef, w_mevcut)
    w = np.where(disinda, np.where(w_mevcut > ust, ust, alt), w)

    return BandSonucu(w=w, band_genisligi=b, gecersiz=gecersiz, islem_yapildi=(gecersiz | disinda))
