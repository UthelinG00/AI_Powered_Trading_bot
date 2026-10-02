"""Duzey 2 fiyat ureteci (BANKA_ONKAYIT_TASLAK Ss3.7 Duzey 2; 3. revizyon). Parametreler belgede dondurulmustur;
bu dosya yalniz uygular. Takvim yalniz takvimdir (veri sentetik): BAS_MS = 2019-01-01 00:00 UTC, 365 gun isinma,
degerlendirme dilimleri 264 / 365 / 365 / 174 gun.

Coinler: c1 = BTCUSDT, c2 = ETHUSDT (beta 1, sigma_I 0,010); c3..c30 = C03USDT..C30USDT (beta ~ U[0,6; 1,4],
sigma_I 0,035). Saatlik log getiri r = beta*m + g_d/24 + (sigma_I/sqrt24)*sqrt(1/2)*t4; m = (sigma_M/sqrt24)*sqrt(1/2)*t4,
sigma_M 0,030. Trend g gunluk AR(1), phi = 2^(-1/HL), duragan std kappa*sigma_tot. OHLC, hacim ve funding Ss3.7'deki
formullerle.

Cekis sirasi (sabit; tek Generator, tohum hash(tohum_kal, 2, ayar_no, yol_no)):
  1. beta, 28 alt (U[0,6; 1,4])            2. hacim merkezi, 28 alt (log-tekduze [10M; 400M])
  3. yasam dongusu: alt permutasyonu (ilk 6 listelenen, sonraki 3 olen, sonraki 2 funding 4h); listelenme gunleri (6),
     olum gunleri (3), 4h baslangic gunleri (2), borsa capi bosluk ilk saati (1)
  4. piyasa faktoru t4 (butun saatler)
  5. coin basina, c1..c30 sirasiyla: [kappa > 0 ise] trend zeta (butun gunler); idiyosenkratik t4 (saatler); fitil
     n1, n2 (2 x saatler); hacim AR zeta (gunler); saatlik hacim n (saatler); funding n (saatler; damga saatinde okunur)."""
import math
from dataclasses import dataclass

import numpy as np

from banka.degerlendirme import Pencere
from motor.gorunum import GUN_MS, SAAT_MS, TamVeri, funding_serisi, saatlik_seri

from .tohum import TOHUM_KAL, uretec

BAS_MS = 1_546_300_800_000                     # 2019-01-01 00:00 UTC
ISINMA_GUN = 365
DILIM_GUN = (264, 365, 365, 174)
GUN = ISINMA_GUN + sum(DILIM_GUN)              # 1533
SAAT = GUN * 24
COINLER = ('BTCUSDT', 'ETHUSDT') + tuple(f'C{i:02d}USDT' for i in range(3, 31))
ALTLAR = COINLER[2:]
SIGMA_M = 0.030
SIGMA_I_ALT = 0.035
SIGMA_I_BUYUK = 0.010
BETA_ARALIK = (0.6, 1.4)
HACIM_ALT = (10e6, 400e6)                      # USDT / gun, log-tekduze merkez
HACIM_BUYUK = 5000e6
HACIM_YARI_OMUR = 60
HACIM_STD = 0.5
FUNDING_ORT, FUNDING_STD = 0.0001, 0.00005
AYARLAR = {0: (0.0, None), 1: (0.0262, 30), 2: (0.0262, 90), 3: (0.0523, 30), 4: (0.0523, 90)}   # ayar_no -> (kappa, HL)
LISTELENEN, OLEN, FUNDING_4H = 6, 3, 2
FUNDING_4H_GUN = 60
BOSLUK_SAAT = 12
OLUM_HACIM_GUN, OLUM_HACIM_CARPAN = 10, 0.05


def pencere() -> Pencere:
    return Pencere(bas_ms=BAS_MS + ISINMA_GUN * GUN_MS, dilim_gun=DILIM_GUN)


@dataclass(frozen=True)
class YasamTarifi:
    listelenen: tuple            # ((coin, gun), ...): ilk bar o gunun 00:00'i
    olen: tuple                  # ((coin, gun), ...): o gun 00:00'dan itibaren bar yok
    funding_4h: tuple            # ((coin, bas_gun), ...): [bas_gun, bas_gun + 60) araliginda 4h funding
    bosluk_saat: int             # borsa capi bosluk ilk saati (BOSLUK_SAAT saat)


@dataclass
class HamYol:
    ayar_no: int
    yol_no: int
    beta: dict
    hacim_merkezi: dict
    yasam: YasamTarifi
    g: dict                      # coin -> gunluk trend (uzunluk GUN)
    r: dict                      # coin -> saatlik log getiri (uzunluk SAAT)
    acilis: dict
    yuksek: dict
    dusuk: dict
    kapanis: dict
    hacim: dict
    funding_n: dict              # coin -> saatlik standart normal (damga saatinde okunur)


def _ar1(z: np.ndarray, phi: float, std: float) -> np.ndarray:
    """Duragan AR(1): x_0 = std*z_0; x_d = phi*x_{d-1} + sqrt(1-phi^2)*std*z_d."""
    x = np.empty(len(z))
    x[0] = std * z[0]
    k = math.sqrt(1.0 - phi * phi) * std
    for d in range(1, len(z)):
        x[d] = phi * x[d - 1] + k * z[d]
    return x


def sigma_toplam(beta: float, sigma_i: float) -> float:
    return math.sqrt(beta * beta * SIGMA_M * SIGMA_M + sigma_i * sigma_i)


def ham_yol(ayar_no: int, yol_no: int, tohum_kal: int = TOHUM_KAL) -> HamYol:
    kappa, hl = AYARLAR[ayar_no]
    rng = uretec(tohum_kal, 2, ayar_no, yol_no)
    beta_alt = rng.uniform(*BETA_ARALIK, size=len(ALTLAR))
    merkez_alt = np.exp(rng.uniform(math.log(HACIM_ALT[0]), math.log(HACIM_ALT[1]), size=len(ALTLAR)))
    perm = rng.permutation(len(ALTLAR))
    list_gun = rng.integers(ISINMA_GUN, GUN, size=LISTELENEN)
    olum_gun = rng.integers(ISINMA_GUN, GUN, size=OLEN)
    f4_gun = rng.integers(ISINMA_GUN, GUN - FUNDING_4H_GUN, size=FUNDING_4H)
    bosluk = int(rng.integers(ISINMA_GUN * 24, SAAT - BOSLUK_SAAT))
    sec = [ALTLAR[i] for i in perm]
    yasam = YasamTarifi(
        listelenen=tuple((sec[k], int(list_gun[k])) for k in range(LISTELENEN)),
        olen=tuple((sec[LISTELENEN + k], int(olum_gun[k])) for k in range(OLEN)),
        funding_4h=tuple((sec[LISTELENEN + OLEN + k], int(f4_gun[k])) for k in range(FUNDING_4H)),
        bosluk_saat=bosluk)
    m = (SIGMA_M / math.sqrt(24.0)) * math.sqrt(0.5) * rng.standard_t(4, SAAT)

    beta, merkez, gd, rd, ac, yu, du, ka, ha, fn = {}, {}, {}, {}, {}, {}, {}, {}, {}, {}
    phi_v = 2.0 ** (-1.0 / HACIM_YARI_OMUR)
    for i, c in enumerate(COINLER):
        if i < 2:
            b, s_i, v0 = 1.0, SIGMA_I_BUYUK, HACIM_BUYUK
        else:
            b, s_i, v0 = float(beta_alt[i - 2]), SIGMA_I_ALT, float(merkez_alt[i - 2])
        s_tot = sigma_toplam(b, s_i)
        if kappa > 0:
            g = _ar1(rng.standard_normal(GUN), 2.0 ** (-1.0 / hl), kappa * s_tot)
        else:
            g = np.zeros(GUN)
        e = rng.standard_t(4, SAAT)
        n12 = rng.standard_normal((2, SAAT))
        zv = rng.standard_normal(GUN)
        nh = rng.standard_normal(SAAT)
        fn[c] = rng.standard_normal(SAAT)
        r = b * m + np.repeat(g, 24) / 24.0 + (s_i / math.sqrt(24.0)) * math.sqrt(0.5) * e
        kap = np.exp(np.cumsum(r))
        aci = np.concatenate(([1.0], kap[:-1]))
        s_h = s_tot / math.sqrt(24.0)
        yu[c] = np.maximum(aci, kap) * np.exp(0.5 * s_h * np.abs(n12[0]))
        du[c] = np.minimum(aci, kap) * np.exp(-0.5 * s_h * np.abs(n12[1]))
        vbar = v0 * np.exp(_ar1(zv, phi_v, HACIM_STD))
        ha[c] = np.repeat(vbar, 24) / 24.0 * np.exp(0.5 * nh - 0.125 + 0.3 * (np.abs(r) / s_h - 0.8))
        beta[c], merkez[c], gd[c], rd[c], ac[c], ka[c] = b, v0, g, r, aci, kap
    return HamYol(ayar_no=ayar_no, yol_no=yol_no, beta=beta, hacim_merkezi=merkez, yasam=yasam, g=gd, r=rd,
                  acilis=ac, yuksek=yu, dusuk=du, kapanis=ka, hacim=ha, funding_n=fn)


def veri_kur(ham: HamYol, yasam: bool = True) -> TamVeri:
    """TamVeri. Funding damgalari etkin araligin kati olan saatler (8h: 00/08/16; 4h araliginda her 4 saat), coinin ilk
    barindan sonra ve olumunden once. yasam=True ise yasam dongusu fikstürleri (Ss3.7):
    - listelenen coin: ilk bar listelenme gunu 00:00;
    - olen coin: son 10 gunde hacim x0,05, olum gunu 00:00'dan itibaren bar ve funding yok;
    - funding 4h: [bas_gun, bas_gun + 60) araliginda 4 saatlik damgalar (aralik_saat 4);
    - borsa capi bosluk: [bosluk_saat, bosluk_saat + 12) saatlerinde hicbir coinin bari yok (funding surer)."""
    barlar, funding = {}, {}
    saatler = np.arange(SAAT, dtype=np.int64)
    y = ham.yasam
    liste = dict(y.listelenen) if yasam else {}
    olum = dict(y.olen) if yasam else {}
    f4 = dict(y.funding_4h) if yasam else {}
    bosluk = np.zeros(SAAT, dtype=bool)
    if yasam:
        bosluk[y.bosluk_saat:y.bosluk_saat + BOSLUK_SAAT] = True
    for c in COINLER:
        bas = liste.get(c, 0) * 24
        son = olum.get(c, GUN) * 24
        hacim = ham.hacim[c].copy()
        if c in olum:
            hacim[max(bas, son - OLUM_HACIM_GUN * 24):son] *= OLUM_HACIM_CARPAN
        var = (saatler >= bas) & (saatler < son) & ~bosluk
        ix = saatler[var]
        barlar[c] = saatlik_seri(BAS_MS + ix * SAAT_MS, ham.acilis[c][ix], ham.yuksek[c][ix], ham.dusuk[c][ix],
                                 ham.kapanis[c][ix], hacim[ix])
        aralik = np.full(SAAT, 8, dtype=np.int64)
        if c in f4:
            aralik[f4[c] * 24:(f4[c] + FUNDING_4H_GUN) * 24] = 4
        damga = saatler[(saatler > bas) & (saatler < son) & (saatler % aralik == 0)]
        funding[c] = funding_serisi(BAS_MS + damga * SAAT_MS, FUNDING_ORT + FUNDING_STD * ham.funding_n[c][damga],
                                    aralik_saat=aralik[damga].astype(float))
    return TamVeri(barlar=barlar, funding=funding, adaylar=COINLER)


def yol_verisi(ayar_no: int, yol_no: int, tohum_kal: int = TOHUM_KAL) -> tuple:
    """(TamVeri, HamYol): Duzey 2'nin (ayar_no, yol_no) yolu, yasam dongusu fikstürleriyle."""
    ham = ham_yol(ayar_no, yol_no, tohum_kal)
    return veri_kur(ham), ham
