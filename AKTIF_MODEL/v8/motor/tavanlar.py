"""Mimari A tavan cozucusu (saf). MIMARI Ss3.5.

Ag, dosya, config veya durum erisimi yoktur. Kaldirac sonrasi NAV agirliklariyla (w^L) calisir. Uygulama sirasi:
isim tavanlari -> brut -> sok senaryolari (S1/S2), en fazla 5 tur; sonra hala ihlal varsa tum kitap tek
katsayiyla kucultulur.

Slice 2 eki: `sabit_mi` (istege bagli). "Islem disi" coin (MIMARI Ss3.1) tavan hesaplarina mevcut agirligiyla
girer ama degistirilemez; butun kucultmeler yalniz serbest isimlere uygulanir. Katsayilar dis bukeylikten
turetilir: kayip(c) = kayip(serbest*c + sabit) c'de dis bukey oldugundan c = (sinir - K0)/(K1 - K0) secimi
kayip(c) <= sinir verir (K0: serbestler sifirken, K1: simdiki). Sabit isim yoksa K0 = 0 ve katsayi Slice 1'deki
sinir/kayip ile ayni sayidir.
"""
from dataclasses import dataclass

import numpy as np

from .tipler import Parametreler


class TavanGirdiHatasi(ValueError):
    """Girdi dizileri bos/uyumsuz."""


@dataclass(frozen=True)
class TavanSonucu:
    w: np.ndarray
    isim_kirpildi: np.ndarray       # bool, hangi isimler isim tavanindan kirpildi
    brut_katsayi: float             # uygulanan c (1.0 ise etkisiz)
    s1_katsayi: float               # her turun c1'lerinin bilesik carpimi (1.0 ise hic uygulanmadi)
    s2_katsayi: float
    global_katsayi: float           # 5 tur sonrasi hala ihlalse uygulanan son care carpani (1.0 ise gerekmedi)
    turlar: int
    s1_kayip_son: float
    s2_kayip_son: float
    sabit_ihlal: bool = False       # yalniz sabit isimler bile bir siniri asiyor (serbestler 0'a indi)


def _kayip_s1(w, btc_eth, p: Parametreler) -> float:
    long_w = np.where(w > 0, w, 0.0)
    alt_long = float(long_w[~btc_eth].sum())
    be_long = float(long_w[btc_eth].sum())
    return p.s1_alt_dusus * alt_long + p.s1_btc_eth_dusus * be_long


def _kayip_s2(w, btc_eth, p: Parametreler) -> float:
    short_w = np.where(w < 0, -w, 0.0)  # pozitif buyukluk
    alt_short = short_w[~btc_eth]
    be_short = short_w[btc_eth]
    en_buyuk_alt = float(alt_short.max()) if alt_short.size else 0.0
    diger_alt_toplam = float(alt_short.sum() - en_buyuk_alt) if alt_short.size else 0.0
    be_toplam = float(be_short.sum())
    return (p.s2_en_buyuk_short_artis * en_buyuk_alt
            + p.s2_diger_short_artis * diger_alt_toplam
            + p.s2_btc_eth_artis * be_toplam)


def _dis_bukey_katsayi(sinir: float, k0: float, k1: float) -> float:
    """kayip(0)=k0, kayip(1)=k1 > sinir iken kayip(c) <= sinir veren c in [0, 1)."""
    if k0 >= sinir or k1 <= k0:
        return 0.0
    return (sinir - k0) / (k1 - k0)


def tavan_coz(w_ham, btc_eth_mi, p: Parametreler, sabit_mi=None) -> TavanSonucu:
    """w_ham: kaldirac uygulanmis (w^L) ham agirliklar. btc_eth_mi: ayni uzunlukta bool, True=BTC/ETH.
    sabit_mi: istege bagli bool dizisi; True olan isimler hic degistirilmez (islem disi coin, MIMARI Ss3.1)."""
    w = np.asarray(w_ham, dtype=float).copy()
    btc_eth = np.asarray(btc_eth_mi, dtype=bool)
    n = len(w)
    if n == 0 or len(btc_eth) != n:
        raise TavanGirdiHatasi("w_ham ve btc_eth_mi ayni, sifirdan buyuk uzunlukta olmali")
    sabit = np.zeros(n, dtype=bool) if sabit_mi is None else np.asarray(sabit_mi, dtype=bool)
    if len(sabit) != n:
        raise TavanGirdiHatasi("sabit_mi w_ham ile ayni uzunlukta olmali")
    serbest = ~sabit

    # 1) Isim tavanlari (tek adim; kirpma sinyal isaretini korur). Sabit isim kirpilmaz.
    ust = np.where(btc_eth, p.isim_tavan_btc_eth, p.isim_tavan_alt_long)
    alt = np.where(btc_eth, -p.isim_tavan_btc_eth, -p.isim_tavan_alt_short)
    kirpilmamis = w.copy()
    w = np.where(serbest, np.clip(w, alt, ust), w)
    isim_kirpildi = ~np.isclose(w, kirpilmamis)

    # 2) Brut. Serbestler tek katsayiyla kuculur.
    brut_katsayi = 1.0
    toplam_brut = float(np.abs(w).sum())
    if toplam_brut > p.brut_tavan:
        sabit_brut = float(np.abs(w[sabit]).sum())
        brut_katsayi = _dis_bukey_katsayi(p.brut_tavan, sabit_brut, toplam_brut)
        w = np.where(serbest, w * brut_katsayi, w)

    def _k0(kayip_fn, taraf_maske):
        return kayip_fn(np.where(serbest & taraf_maske, 0.0, w), btc_eth, p)

    # 3) Sok senaryolari, en fazla 5 tur. S1 yalniz long, S2 yalniz short tarafi kucultur.
    s1_katsayi_bilesik = 1.0
    s2_katsayi_bilesik = 1.0
    tur = 0
    s1_kayip = _kayip_s1(w, btc_eth, p)
    s2_kayip = _kayip_s2(w, btc_eth, p)
    while tur < p.tavan_max_tur and (s1_kayip > p.s1_sinir or s2_kayip > p.s2_sinir):
        tur += 1
        if s1_kayip > p.s1_sinir:
            long_maske = w > 0
            c1 = _dis_bukey_katsayi(p.s1_sinir, _k0(_kayip_s1, long_maske), s1_kayip)
            w = np.where(long_maske & serbest, w * c1, w)
            s1_katsayi_bilesik *= c1
        s2_kayip_guncel = _kayip_s2(w, btc_eth, p)  # S1 kucultmesinden sonra guncel
        if s2_kayip_guncel > p.s2_sinir:
            short_maske = w < 0
            c2 = _dis_bukey_katsayi(p.s2_sinir, _k0(_kayip_s2, short_maske), s2_kayip_guncel)
            w = np.where(short_maske & serbest, w * c2, w)
            s2_katsayi_bilesik *= c2
        s1_kayip = _kayip_s1(w, btc_eth, p)
        s2_kayip = _kayip_s2(w, btc_eth, p)

    global_katsayi = 1.0
    if s1_kayip > p.s1_sinir or s2_kayip > p.s2_sinir:
        # Son care: butun (serbest) kitabi en siki ihlale gore tek katsayiyla kucult.
        tum = np.ones(n, dtype=bool)
        adaylar = []
        if s1_kayip > p.s1_sinir:
            adaylar.append(_dis_bukey_katsayi(p.s1_sinir, _k0(_kayip_s1, tum), s1_kayip))
        if s2_kayip > p.s2_sinir:
            adaylar.append(_dis_bukey_katsayi(p.s2_sinir, _k0(_kayip_s2, tum), s2_kayip))
        global_katsayi = min(adaylar)
        w = np.where(serbest, w * global_katsayi, w)
        s1_kayip = _kayip_s1(w, btc_eth, p)
        s2_kayip = _kayip_s2(w, btc_eth, p)

    # Sabit isim kendi isim tavanini asiyorsa da ihlaldir (kirpilamaz; Codex K8).
    sabit_isim_asimi = bool(np.any(sabit & ((w > ust + 1e-12) | (w < alt - 1e-12))))
    sabit_ihlal = bool(sabit.any() and (s1_kayip > p.s1_sinir + 1e-12 or s2_kayip > p.s2_sinir + 1e-12
                                         or float(np.abs(w).sum()) > p.brut_tavan + 1e-12 or sabit_isim_asimi))
    return TavanSonucu(w=w, isim_kirpildi=isim_kirpildi, brut_katsayi=brut_katsayi,
                        s1_katsayi=s1_katsayi_bilesik, s2_katsayi=s2_katsayi_bilesik,
                        global_katsayi=global_katsayi, turlar=tur,
                        s1_kayip_son=s1_kayip, s2_kayip_son=s2_kayip, sabit_ihlal=sabit_ihlal)
