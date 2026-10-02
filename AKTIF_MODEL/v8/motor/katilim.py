"""Katilim siniri, lot yuvarlama ve tek saatlik dolum (saf). MIMARI Ss3.7, Ss5.1 (saf kismi).

Ag, dosya, config veya durum erisimi yoktur. Tam olay-gunlugu/durum orkestrasyonu (hedef_agirlik,
emir_zinciri'nin coklu-saat cagrimi) Slice 2'dedir; burada yalniz tekil-adim, saf matematik var.
"""
import math
from dataclasses import dataclass

from .tipler import Parametreler


class KatilimGirdiHatasi(ValueError):
    """Girdi degerleri negatif ya da adim/min_notional <= 0."""


def katilim_siniri(v1h30: float, v1h7: float, onceki_saat_hacmi: float, p: Parametreler) -> float:
    """Q_max = min(0.001*V1h30, 0.001*V1h7, 0.10*onceki_saat_hacmi). Hepsi USDT quote hacmidir."""
    if v1h30 < 0 or v1h7 < 0 or onceki_saat_hacmi < 0:
        raise KatilimGirdiHatasi("hacimler negatif olamaz")
    return min(p.katilim_oran_30g * v1h30, p.katilim_oran_7g * v1h7,
               p.katilim_oran_onceki_saat * onceki_saat_hacmi)


def _sifira_yuvarla(x: float) -> int:
    return math.trunc(x)


def lot_delta(w_hedef: float, q_mevcut: float, nav: float, fiyat_ref: float, adim: float,
              min_notional: float) -> float:
    """Delta_q = trunc((w_hedef*nav/fiyat_ref - q_mevcut) / adim) * adim.

    |Delta_q|*fiyat_ref < min_notional ise emir yok (0), istisna: w_hedef=0 ise tam kapanis (reduce-only,
    minNotional denetlenmez).
    """
    if adim <= 0 or min_notional < 0 or fiyat_ref <= 0:
        raise KatilimGirdiHatasi("adim>0, fiyat_ref>0, min_notional>=0 olmali")
    hedef_miktar = w_hedef * nav / fiyat_ref
    delta_ham = hedef_miktar - q_mevcut
    delta = _sifira_yuvarla(delta_ham / adim) * adim
    if w_hedef == 0.0:
        return -q_mevcut  # tam kapanis; minNotional istisnasi
    if abs(delta) * fiyat_ref < min_notional:
        return 0.0
    return delta


@dataclass(frozen=True)
class DolumSonucu:
    miktar: float     # isaretli, adim katina yuvarlanmis
    fiyat: float


def tek_saat_dolum(kalan_miktar: float, q_max: float, acilis_fiyati: float, adim: float,
                    min_notional: float, bar_var_mi: bool, hacim_var_mi: bool, maliyet_c_i: float,
                    tam_kapanisin_son_parcasi_mi: bool = False) -> DolumSonucu:
    """MIMARI Ss5.1 emir_zinciri'nin tek-saat, saf kismi.

    kalan_miktar: isaretli (kalan_i), dolmasi gereken. q_max: o saatin USDT katilim siniri.
    acilis_fiyati: barin acilisi. maliyet_c_i: fiyata uygulanacak kayma (bps DEGIL, oran; ornegin 0.0011).
    Fiyat = acilis*(1 + c_i) alis (kalan_miktar>0, dolum artiriyor) icin, (1 - c_i) satis icin.
    Bar yoksa ya da hacim 0 ise dolum 0 (fiyat yine acilis olarak donulur, referans amacli).
    """
    if adim <= 0 or acilis_fiyati <= 0:
        raise KatilimGirdiHatasi("adim>0, acilis_fiyati>0 olmali")
    if not bar_var_mi or not hacim_var_mi or kalan_miktar == 0.0:
        return DolumSonucu(miktar=0.0, fiyat=acilis_fiyati)
    isaret = 1.0 if kalan_miktar > 0 else -1.0
    ham = min(abs(kalan_miktar), q_max / acilis_fiyati)
    dolum = isaret * math.floor(ham / adim) * adim
    if not tam_kapanisin_son_parcasi_mi and abs(dolum) * acilis_fiyati < min_notional:
        dolum = 0.0
    fiyat = acilis_fiyati * (1.0 + maliyet_c_i if dolum > 0 else 1.0 - maliyet_c_i)
    return DolumSonucu(miktar=dolum, fiyat=fiyat)
