"""Trend sinyali (saf). MIMARI Ss3.1.

Ag, dosya, config veya durum erisimi yoktur. Girdi yalniz tamamlanmis gunluk kapanislardir; donmus/eksik gunler
disaridan `gecerli` maskesiyle bildirilir, bu modul maske uretmez.
"""
import math

from .tipler import Parametreler


class SinyalGirdiHatasi(ValueError):
    """Fiyat/gecerlilik dizileri tutarsiz ya da bugunun fiyati gecersiz."""


def trend_sinyali(fiyatlar, gecerli, sigma_ewma: float, p: Parametreler) -> float:
    """s_i,t = (1/3) * sum_h tanh( ln(P_t/P_{t-h}) / (sigma_sig * sqrt(h/365)) ), sigma_sig = max(sigma_ewma, taban).

    fiyatlar: kronolojik gunluk kapanis dizisi, fiyatlar[-1] = P_t (bugun).
    gecerli: ayni uzunlukta, gecerli[k]=False ise o gunun kapanisi sinyale girmez (mask/isinma disi/eksik bar).
    Ufuk h icin P_{t-h} yoksa (index<0) ya da o gun gecersizse terim 0'dir; payda daima len(ufuklar)'dir.
    """
    if len(fiyatlar) != len(gecerli):
        raise SinyalGirdiHatasi("fiyatlar ve gecerli ayni uzunlukta olmali")
    if len(fiyatlar) == 0 or not gecerli[-1] or fiyatlar[-1] <= 0:
        raise SinyalGirdiHatasi("bugunun (t) fiyati gecerli ve pozitif olmali")
    sigma_sig = max(sigma_ewma, p.sigma_taban)
    n = len(fiyatlar)
    p_t = fiyatlar[-1]
    toplam = 0.0
    for h in p.ufuklar:
        idx = n - 1 - h
        if idx < 0 or not gecerli[idx] or fiyatlar[idx] <= 0:
            continue  # terim 0; donmus/eksik fiyat sinyale girmez
        getiri = math.log(p_t / fiyatlar[idx])
        toplam += math.tanh(getiri / (sigma_sig * math.sqrt(h / 365.0)))
    return toplam / len(p.ufuklar)
