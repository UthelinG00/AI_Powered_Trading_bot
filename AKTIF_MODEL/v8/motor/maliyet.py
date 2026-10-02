"""Maliyet modeli (saf). MIMARI Ss6.1-Ss6.2 (uc belgede tek tanim).

Ag, dosya, config veya durum erisimi yoktur.
"""
import math
from dataclasses import dataclass

from .tipler import Parametreler


class MaliyetGirdiHatasi(ValueError):
    """Girdi degerleri negatif ya da 20M altinda giris islemi (yalniz cikis tanimli)."""


def dilim_bps(v60: float, btc_eth_mi: bool, cikis_mi: bool, p: Parametreler) -> float:
    """V60'a gore dilim tablosu (bps). <20M yalniz cikis icin tanimlidir (MIMARI Ss6.1)."""
    if v60 < 0:
        raise MaliyetGirdiHatasi("v60 negatif olamaz")
    if btc_eth_mi:
        return p.dilim_btc_eth_bps
    if v60 >= p.dilim_200m_esik:
        return p.dilim_200m_ustu_bps
    if v60 >= p.dilim_50m_esik:
        return p.dilim_50_200m_bps
    if v60 >= p.dilim_20m_esik:
        return p.dilim_20_50m_bps
    if cikis_mi:
        return p.dilim_20m_alti_bps
    raise MaliyetGirdiHatasi("V60 < 20M'de giris tanimsizdir; evren kurali bunu zaten disliyor (MIMARI Ss2.3)")


def etki_bps(sigma_d_bps: float, q_nominal: float, v60: float, p: Parametreler) -> float:
    """etki_i = Y * sigma_d,i * sqrt(Q / V60_i)."""
    if sigma_d_bps < 0 or q_nominal < 0:
        raise MaliyetGirdiHatasi("sigma_d_bps ve q_nominal negatif olamaz")
    if v60 <= 0:
        raise MaliyetGirdiHatasi("v60 > 0 olmali")
    return p.karekok_y * sigma_d_bps * math.sqrt(q_nominal / v60)


def m_carpani(maske_cikisi_mi: bool, ln_hl_coin: float, sigma_1h_coin: float,
              ln_hl_btc: float, sigma_1h_btc: float, p: Parametreler) -> float:
    """m_i: maske cikisi ya da stres barinda (coin |ln(H/L)|>5*sigma_1h ya da BTC>4*sigma_1h_BTC) 3;
    aksi halde 1. Kosullar birlikte saglansa da 3'tur, carpilmaz."""
    stres = (abs(ln_hl_coin) > p.stres_esik_coin_sigma * sigma_1h_coin
             or abs(ln_hl_btc) > p.stres_esik_btc_sigma * sigma_1h_btc)
    return p.m_stres if (maske_cikisi_mi or stres) else 1.0


@dataclass(frozen=True)
class MaliyetSonucu:
    toplam_bps: float
    ucret_bps: float
    dilim_bps: float
    etki_bps: float
    m: float
    k: float


def maliyet_hesapla(k: float, v60: float, btc_eth_mi: bool, cikis_mi: bool, maske_cikisi_mi: bool,
                     ln_hl_coin: float, sigma_1h_coin: float, ln_hl_btc: float, sigma_1h_btc: float,
                     sigma_d_bps: float, q_nominal: float, p: Parametreler) -> MaliyetSonucu:
    """c_i(k) = ucret + k*m_i*(dilim_i + etki_i). k carpani yalniz dilim+etkiye uygulanir, ucret sabit."""
    if k <= 0:
        raise MaliyetGirdiHatasi("maliyet carpani k > 0 olmali")
    dilim = dilim_bps(v60, btc_eth_mi, cikis_mi, p)
    etki = etki_bps(sigma_d_bps, q_nominal, v60, p) if v60 > 0 else 0.0
    m = m_carpani(maske_cikisi_mi, ln_hl_coin, sigma_1h_coin, ln_hl_btc, sigma_1h_btc, p)
    toplam = p.ucret_bps + k * m * (dilim + etki)
    return MaliyetSonucu(toplam_bps=toplam, ucret_bps=p.ucret_bps, dilim_bps=dilim, etki_bps=etki, m=m, k=k)
