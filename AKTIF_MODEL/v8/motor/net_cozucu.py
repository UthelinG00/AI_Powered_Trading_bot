"""Mimari B net kitap cozucusu (saf). MIMARI Ss4.5 adim 1-4; CARRY_KAPISI Ss3.3.

Net aday kitap w_i = cT_i * wT_i + kappa * wC_i + sabit_i. Kucultme once trend bacagina uygulanir; carry blogu (alt
isimleri + BTC hedge) yalniz trend payi tukenince tek katsayi kappa ile kuculur, boylece blok ici oranlar (dolar ve
beta notrlugu) degismez. Sabit (islem disi) isimlerin net agirligi degismez (K8, Y9).

1. Isim tavanlari (net): tavani asan coinde trend bileseni net tavana inene kadar kuculur (isaret degistirmez);
   carry bileseni tek basina tavani asarsa degismez ihlalidir (teknik hata).
2. Brut: trend bacagi c_g ile; c_g = 0 yetmezse kappa.
3. S1/S2: pozitif trend bilesenleri c1, negatif trend bilesenleri c2 ile (en fazla 5 tur); surerse kappa; yine
   surerse butun serbest net kitap tek katsayiyla (MIMARI Ss3.5 son care).

Sayisal sozlesme (Codex 5. tur / inceleme B2): ikiye bolme sinirin KENDISINI hedefler (kayip <= sinir, toleranssiz);
ihlal denetimleri tek ortak mutlak tolerans TOL ile yapilir (`ihlaller`). hedef_b'nin yeniden sinamasi ayni
fonksiyonu kullanir; boylece cozucunun uygun buldugu kitap sonraki denetimde ihlal sayilmaz.

kappa (inceleme B11): net w_i(kappa) = a_i + kappa*b_i dogrusal; S1, S2 (0,5*sum short + 0,5*max short), brut ve isim
tavanlari kappa'da disbukey oldugundan uygun kappa kumesi bir araliktir ve 0'i icermeyebilir (carry short'u kuculunce
ters yonlu trendli isim tavani asabilir). Once en kucuk ihlal noktasi (ucte bolme) bulunur; uygunsa ondan yukari en
buyuk uygun kappa ikiye bolmeyle bulunur. Uygun kappa yoksa kappa en kucuk ihlal noktasinda kalir ve son care
uygulanir (Y11 revizyonu).
"""
from dataclasses import dataclass

import numpy as np

from .tavanlar import _dis_bukey_katsayi, _kayip_s1, _kayip_s2
from .tipler import Parametreler

TOL = 1e-12   # ihlal denetimlerinin ortak mutlak toleransi (NAV kesri)
KESIN = 0.1 * TOL   # kappa aramasinda "uygun" esigi (isim tavani kapali bicimindeki ulp artigini tolere eder)


class NetCozucuHatasi(ValueError):
    """Carry bileseni tek basina net isim tavanini asiyor (degismez ihlali)."""


def net_isim_tavanlari(btc_eth: np.ndarray, p: Parametreler) -> tuple:
    """(ust, alt) B net isim tavanlari: BTC/ETH %35; alt long %6; alt short S4 ile %3,33 (MIMARI Ss4.5 adim 1)."""
    alt_short = p.s4_sinir / p.s4_artis
    ust = np.where(btc_eth, p.isim_tavan_btc_eth, p.isim_tavan_alt_long)
    alt = np.where(btc_eth, -p.isim_tavan_btc_eth, -alt_short)
    return ust, alt


def asimlar(w, serbest, btc_eth, p: Parametreler) -> dict:
    """Her kisitin asim miktari (pozitif = ihlal): isim (yalniz serbest isimler), brut, S1, S2."""
    w = np.asarray(w, dtype=float)
    ust, alt = net_isim_tavanlari(btc_eth, p)
    isim = np.where(serbest, np.maximum(w - ust, alt - w), -np.inf)
    return {'isim': float(isim.max()) if len(w) else -np.inf,
            'brut': float(np.abs(w).sum()) - p.brut_tavan,
            'S1': _kayip_s1(w, btc_eth, p) - p.s1_sinir,
            'S2': _kayip_s2(w, btc_eth, p) - p.s2_sinir}


def ihlaller(w, serbest, btc_eth, p: Parametreler) -> set:
    """TOL'u asan ihlal kumesi (cozucu ve hedef_b yeniden sinamasi ayni fonksiyonu kullanir)."""
    return {k for k, v in asimlar(w, serbest, btc_eth, p).items() if v > TOL}


@dataclass(frozen=True)
class NetSonuc:
    c_trend: np.ndarray      # coin basina trend katsayisi (isim, brut, S1/S2 birlesik)
    kappa: float
    global_katsayi: float
    w: np.ndarray            # net kitap (bant oncesi)
    baglayan: tuple
    tanilar: dict


def _ikiye_bol(kosul, lo: float, hi: float, adim: int) -> float:
    """kosul(lo) dogru, kosul(hi) yanlis ve [lo, hi] uzerinde tekduze iken kosulu saglayan en buyuk deger."""
    for _ in range(adim):
        orta = (lo + hi) / 2.0
        if kosul(orta):
            lo = orta
        else:
            hi = orta
    return lo


def _ucte_bol_min(f, lo: float, hi: float, adim: int) -> float:
    """Disbukey f'nin [lo, hi] uzerindeki (bir) en kucuk noktasi (altin oran olmayan basit ucte bolme)."""
    for _ in range(adim):
        m1 = lo + (hi - lo) / 3.0
        m2 = hi - (hi - lo) / 3.0
        if f(m1) <= f(m2):
            hi = m2
        else:
            lo = m1
    return (lo + hi) / 2.0


def net_coz(wT, wC, sabit_w, sabit_mi, btc_eth, p: Parametreler) -> NetSonuc:
    """wT: trend bileseni (kaldiracli, serbest isimlerde); wC: gunluk carry blogu (alt + BTC hedge; serbest isimlerde);
    sabit_w: sabit isimlerin net agirligi (serbestlerde 0); sabit_mi: bool dizisi."""
    wT = np.asarray(wT, dtype=float).copy()
    wC = np.asarray(wC, dtype=float)
    sabit_w = np.asarray(sabit_w, dtype=float)
    sabit = np.asarray(sabit_mi, dtype=bool)
    btc_eth = np.asarray(btc_eth, dtype=bool)
    serbest = ~sabit
    wT = np.where(serbest, wT, 0.0)
    wC = np.where(serbest, wC, 0.0)
    n = len(wT)
    ust, alt = net_isim_tavanlari(btc_eth, p)
    c = np.ones(n)
    kappa = 1.0
    baglayan = []
    adim = p.cozucu_ikiye_bolme_adim

    def net(cc=None, kk=None):
        cc = c if cc is None else cc
        kk = kappa if kk is None else kk
        return cc * wT + kk * wC + sabit_w

    def s1(w):
        return _kayip_s1(w, btc_eth, p)

    def s2(w):
        return _kayip_s2(w, btc_eth, p)

    # 1. Isim tavanlari (net).
    for i in np.nonzero(serbest)[0]:
        if wC[i] > ust[i] + TOL or wC[i] < alt[i] - TOL:
            raise NetCozucuHatasi(f"carry bileseni net isim tavanini asiyor (indeks {i})")
        x = wT[i] + wC[i]
        if x > ust[i] and wT[i] > 0:
            c[i] = max(0.0, (ust[i] - wC[i]) / wT[i])
        elif x < alt[i] and wT[i] < 0:
            c[i] = max(0.0, (alt[i] - wC[i]) / wT[i])
    if np.any(c < 1.0):
        baglayan.append('isim')

    # 2. Brut (ikiye bolme sinirin kendisini hedefler).
    def brut_ok(cg=1.0, kk=None):
        return float(np.abs(net(c * cg, kk)).sum()) <= p.brut_tavan
    c_g = 1.0
    if float(np.abs(net()).sum()) > p.brut_tavan + TOL:
        baglayan.append('brut')
        if brut_ok(0.0):
            c_g = _ikiye_bol(lambda x: brut_ok(x), 0.0, 1.0, adim)
        else:
            c_g = 0.0
            baglayan.append('kappa_brut')
            kappa = _ikiye_bol(lambda k: brut_ok(0.0, k), 0.0, 1.0, adim) if brut_ok(0.0, 0.0) else 0.0
        c = c * c_g

    # 3. S1/S2 (en fazla 5 tur), trend tarafi.
    c1_bilesik = c2_bilesik = 1.0
    tur = 0
    while tur < p.tavan_max_tur and (s1(net()) > p.s1_sinir + TOL or s2(net()) > p.s2_sinir + TOL):
        tur += 1
        if s1(net()) > p.s1_sinir + TOL:
            poz = serbest & (wT > 0)
            def ok1(x, poz=poz):
                return s1(net(np.where(poz, c * x, c))) <= p.s1_sinir
            c1 = _ikiye_bol(ok1, 0.0, 1.0, adim) if ok1(0.0) else 0.0
            c = np.where(poz, c * c1, c)
            c1_bilesik *= c1
        if s2(net()) > p.s2_sinir + TOL:
            neg = serbest & (wT < 0)
            def ok2(x, neg=neg):
                return s2(net(np.where(neg, c * x, c))) <= p.s2_sinir
            c2 = _ikiye_bol(ok2, 0.0, 1.0, adim) if ok2(0.0) else 0.0
            c = np.where(neg, c * c2, c)
            c2_bilesik *= c2
    if c1_bilesik < 1.0:
        baglayan.append('S1')
    if c2_bilesik < 1.0:
        baglayan.append('S2')

    def asim(kk):
        return max(asimlar(net(None, kk), serbest, btc_eth, p).values())

    # 4. kappa: carry blogu tek katsayi; uygun kume bir aralik (disbukeylik).
    kappa_tan = {}
    if asim(kappa) > TOL:
        baglayan.append('kappa')
        k_ust = kappa
        k_min = _ucte_bol_min(asim, 0.0, k_ust, 2 * adim)
        for aday in (0.0, k_ust):          # uclar da denenir (en kucuk ihlal ucta olabilir)
            if asim(aday) < asim(k_min):
                k_min = aday
        kappa_tan = {'kappa_min_ihlal': k_min, 'min_ihlal': asim(k_min)}
        if asim(k_min) <= KESIN:
            kappa = _ikiye_bol(lambda k: asim(k) <= KESIN, k_min, k_ust, adim)
        else:
            kappa = k_min                   # uygun kappa yok (ya da yalniz TOL icinde): son care karar verir

    # Son care: butun serbest net kitap tek katsayiyla.
    g_kat = 1.0
    w = net()
    if ihlaller(w, serbest, btc_eth, p):
        baglayan.append('global')
        w0 = np.where(serbest, 0.0, w)
        adaylar = []
        if s1(w) > p.s1_sinir + TOL:
            adaylar.append(_dis_bukey_katsayi(p.s1_sinir, s1(w0), s1(w)))
        if s2(w) > p.s2_sinir + TOL:
            adaylar.append(_dis_bukey_katsayi(p.s2_sinir, s2(w0), s2(w)))
        brut = float(np.abs(w).sum())
        if brut > p.brut_tavan + TOL:
            adaylar.append(_dis_bukey_katsayi(p.brut_tavan, float(np.abs(w0).sum()), brut))
        for i in np.nonzero(serbest & ((w > ust + TOL) | (w < alt - TOL)))[0]:
            adaylar.append((ust[i] if w[i] > 0 else -alt[i]) / abs(w[i]))
        g_kat = min(adaylar) if adaylar else 1.0
        w = np.where(serbest, w * g_kat, w)
    return NetSonuc(c_trend=c, kappa=kappa, global_katsayi=g_kat, w=w, baglayan=tuple(baglayan),
                    tanilar={'c_g': c_g, 'c1': c1_bilesik, 'c2': c2_bilesik, 'turlar': tur,
                             's1_kayip': s1(w), 's2_kayip': s2(w), **kappa_tan})
