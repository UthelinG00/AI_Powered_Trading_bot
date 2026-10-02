"""Lot yuvarlama, devreden emir oncelik kurali ve saatlik emir zinciri (saf). MIMARI Ss5.1, Ss5.4, Ss3.7, Ss6.1.

Ag, dosya, config veya durum erisimi yoktur. Katilim/maliyet matematigi Slice 1 modullerinden (katilim,
maliyet) gelir; burada coklu-coin, durumlu cagri ve oncelik kurali vardir.
"""
import math
from dataclasses import dataclass

from .durum import Emir
from .katilim import katilim_siniri, lot_delta
from .maliyet import maliyet_hesapla
from .tipler import Parametreler


class EmirGirdiHatasi(ValueError):
    """Gecersiz fiyat/adim ya da tutarsiz emir."""


def filtre_al(filtreler: dict, coin: str, p: Parametreler) -> tuple:
    """(adim, minNotional). Goruntude olmayan sembolde adim 0 (yuvarlama yok), minNotional 5 USDT (MIMARI Ss5.1)."""
    return filtreler.get(coin, (p.varsayilan_adim, p.varsayilan_min_notional))


def lot_niyeti(w_hedef: float, q_mevcut: float, nav: float, fiyat_ref: float, adim: float,
               min_notional: float) -> float:
    """Delta_q = yuvarla_sifira_dogru((w*nav/fiyat_ref - q)/adim)*adim; adim 0 ise yuvarlama yok.
    |Delta_q|*fiyat_ref < minNotional ise emir yok; hedef 0 ise tam kapanis (MIMARI Ss5.1)."""
    if adim > 0:
        return lot_delta(w_hedef, q_mevcut, nav, fiyat_ref, adim, min_notional)
    if fiyat_ref <= 0:
        raise EmirGirdiHatasi("fiyat_ref > 0 olmali")
    if w_hedef == 0.0:
        return -q_mevcut
    delta = w_hedef * nav / fiyat_ref - q_mevcut
    if abs(delta) * fiyat_ref < min_notional:
        return 0.0
    return delta


def risk_parcalari(kalan: float, q: float) -> tuple:
    """MIMARI Ss5.4 siniflama: (risk azaltan, risk artiran). Isaret degistiren emir 0'a kadar risk azaltan,
    0'dan sonrasi risk artirandir. Toplam = kalan."""
    if q == 0.0 or kalan == 0.0 or (kalan > 0) == (q > 0):
        return 0.0, kalan
    azaltan = math.copysign(min(abs(kalan), abs(q)), kalan)
    return azaltan, kalan - azaltan


def artiran_iptali(kalan: float, q: float, sebep: str):
    """Devreden emrin risk artiran parcasinin iptal kaydi verisi (MIMARI Ss5.4 oncelik 1-2); artiran yoksa None.
    Korunan azaltan parca pozisyonu tam kapatiyorsa 'tam_kapanis' isaretlenir (Codex K14)."""
    azaltan, artiran = risk_parcalari(kalan, q)
    if artiran == 0.0:
        return None
    return {'iptal': artiran, 'tamami': azaltan == 0.0, 'tam_kapanis': azaltan != 0.0 and azaltan == -q,
            'sebep': sebep}


@dataclass(frozen=True)
class DolumSonucu:
    miktar: float             # isaretli
    fiyat: float
    maliyet_bps: float
    q_max: float
    tam_kapanis_son: bool     # bu dolum tam kapanisi tamamladi (pozisyon tam 0)
    sebep: str                # 'doldu' | 'kismi' | 'bar_yok' | 'hacim_0' | 'min_notional' | 'adim_alti'


def saat_dolumu(emir: Emir, q: float, bar, onceki_saat_hacmi: float, btc_ln_hl: float, maliyet_k: float,
                adim: float, min_notional: float, p: Parametreler, katilimsiz: bool = False) -> DolumSonucu:
    """MIMARI Ss5.1 emir_zinciri, tek coin, tek saat h.

    bar: (acilis, yuksek, dusuk, hacim) ya da None (bar yok). onceki_saat_hacmi: h-1 barinin quote hacmi
    (bar yoksa 0). btc_ln_hl: BTC'nin h barindaki |ln(H/L)| (bar yoksa 0). katilimsiz: golge yol (Q_max = sonsuz,
    MIMARI Ss6.4).
      ham = min(|kalan|, Q_max / acilis); dolum = sign * floor(ham/adim)*adim (kismi dolum adim katina asagi)
      dolum nominali < minNotional ise 0 (tam kapanisin son parcasi haric); fiyat = acilis * (1 +/- c_i).
    """
    b = emir.baglam
    q_max = math.inf if katilimsiz else katilim_siniri(b.v1h30, b.v1h7, onceki_saat_hacmi, p)
    if bar is None:
        return DolumSonucu(0.0, 0.0, 0.0, q_max, False, 'bar_yok')
    acilis, yuksek, dusuk, hacim = bar
    if hacim <= 0:
        return DolumSonucu(0.0, 0.0, 0.0, q_max, False, 'hacim_0')
    if acilis <= 0:
        raise EmirGirdiHatasi("acilis fiyati > 0 olmali")
    isaret = 1.0 if emir.kalan > 0 else -1.0
    ham = min(abs(emir.kalan), q_max / acilis)
    tamamlar = ham >= abs(emir.kalan)
    if emir.tam_kapanis and tamamlar:
        miktar = -q                                       # pozisyon tam 0'a iner (float artigi birakmaz)
        tam_son = True
    else:
        if adim > 0:
            miktar = isaret * math.floor(ham / adim + 1e-9) * adim
        else:
            miktar = isaret * ham
        tam_son = False
        if miktar == 0.0:
            return DolumSonucu(0.0, 0.0, 0.0, q_max, False, 'adim_alti')
        if abs(miktar) * acilis < min_notional:
            return DolumSonucu(0.0, 0.0, 0.0, q_max, False, 'min_notional')
    if miktar == 0.0:
        return DolumSonucu(0.0, 0.0, 0.0, q_max, tam_son, 'doldu')

    azaltan = abs(q + miktar) < abs(q) and (q + miktar) * q >= 0
    ln_hl = abs(math.log(yuksek / dusuk)) if dusuk > 0 else 0.0
    # <20M dilimi yalniz cikista tanimlidir (MIMARI Ss6.1); karar V60 < 20M coinde risk artiran emir uretmez
    # (hedef.py, Codex K13). Aksi bir emir maliyet modulunde hata verir.
    ml = maliyet_hesapla(maliyet_k, b.v60, b.btc_eth, azaltan, emir.maske_cikisi, ln_hl, b.sigma_1h, btc_ln_hl,
                         b.btc_sigma_1h, b.sigma_d_bps, abs(miktar) * acilis, p)
    c = ml.toplam_bps / 10_000.0
    fiyat = acilis * (1.0 + c) if miktar > 0 else acilis * (1.0 - c)
    return DolumSonucu(miktar, fiyat, ml.toplam_bps, q_max, tam_son, 'doldu' if tamamlar else 'kismi')
