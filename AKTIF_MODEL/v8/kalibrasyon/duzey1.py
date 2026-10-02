"""Duzey 1 P&L ureteci (BANKA_ONKAYIT_TASLAK Ss3.7 Duzey 1). Parametreler belgede dondurulmustur; bu dosya uygular.

Izgara (2^7 = 128 ayar): T_yil {3,0; 3,5}, l_e {30; 60}, s {0,75; 1,25}, rho_f {0,3; 0,6}, delta {0,05; 0,10},
phi {0,5; 1,5}, g {-1; +1}. ayar_no 0..127: bitler sirasiyla (bit 6 = T_yil ... bit 0 = g); 0 ilk deger, 1 ikinci.
J = 15 hat, esit agirlik. Hat gunluk fiyat P&L'i x_{j,t} = mu_{j,e(j,t)} + eps_{j,t};
eps = sqrt(rho_f) u_t + sqrt(1 - rho_f) v_{j,t}; u, v ~ sqrt(1/2) t4. Epizot uzunlugu geometrik (p = 1/l_e);
mu_{j,e} = m + a (exp(s Z) - exp(s^2/2)), a = phi / (sd_s sqrt(l_e)), sd_s = sqrt(exp(s^2)(exp(s^2) - 1)).
sigma_P = sqrt(rho_f + (1 - rho_f)/J + a^2 sd_s^2 / J); K = delta sigma_P / sqrt365 (x2, x3: 2K, 3K);
F = g 0,05 sigma_P / sqrt365; m = SR_hedef sigma_P / sqrt365 - F + K; X_t = (1/J) sum_j (x_{j,t} + F - K).
T = floor(365 T_yil) gun (1095; 1277): B4 dilimleri 365 T_yil - 904, 365, 365, 174.

Ortak rastgele sayilar: bir (ayar, yol) icin gurultu ve epizotlar bir kez uretilir; SR_hedef yalniz m'yi kaydirir
(tohum belgede ayar ve yola baglidir, SR'a degil).

Cekis sirasi (sabit; tek Generator, tohum hash(tohum_kal, 1, ayar_no, yol_no)); "hat uretimi" = T geometrik
uzunluk, T tane Z (epizot basina bir; kullanilmayan atilir), T tane v:
  1. ana ortak faktor u (T)            2. ana 15 hat, j = 1..15
  3. B9 portfoyu Y: kendi ortak faktoru u_Y (T) ve 15 hat
  4. B10 ikame hatlari r = 1..10 (ana ortak faktor u ile)
  5. B seyreltme raporu icin carry gurultusu w (T; sqrt(1/2) t4), butun (rho, SR_C) birlesimlerinde ortak
Yorum (belgenin acik biraktigi yer; Codex incelemesine sunulur): B10'un "ayni ayarla bagimsiz uretilmis yeni hat"i ana
portfoyun ortak faktorunu (u_t) paylasir, kendi v, epizot ve Z'sine sahiptir. Gerekce: bankadaki tek coin cikarma
kosusunda bosalan risk piyasa faktorunu paylasan baska coinlere gider; ortak faktorsuz bir ikame portfoy vol'unu yapay
olarak dusururdu."""
import math
from dataclasses import dataclass

import numpy as np

from .tohum import TOHUM_KAL, uretec

J = 15
GUN_YIL = 365
IZGARA = (('T_yil', (3.0, 3.5)), ('l_e', (30, 60)), ('s', (0.75, 1.25)), ('rho_f', (0.3, 0.6)),
          ('delta', (0.05, 0.10)), ('phi', (0.5, 1.5)), ('g', (-1, 1)))
SR_IZGARASI = (0.0, 0.3, 0.5, 0.8, 1.0, 1.2)
SR_REF = 1.0
FUNDING_PAY = 0.05
B10_HAT = 10
B9_KARISIM = 0.7


@dataclass(frozen=True)
class Ayar:
    T_yil: float
    l_e: int
    s: float
    rho_f: float
    delta: float
    phi: float
    g: int

    @property
    def T(self) -> int:
        return int(math.floor(GUN_YIL * self.T_yil))

    @property
    def sd_s(self) -> float:
        e = math.exp(self.s * self.s)
        return math.sqrt(e * (e - 1.0))

    @property
    def a(self) -> float:
        return self.phi / (self.sd_s * math.sqrt(self.l_e))

    @property
    def sigma_P(self) -> float:
        return math.sqrt(self.rho_f + (1.0 - self.rho_f) / J + self.a ** 2 * self.sd_s ** 2 / J)

    def K(self) -> float:
        return self.delta * self.sigma_P / math.sqrt(GUN_YIL)

    def F(self) -> float:
        return self.g * FUNDING_PAY * self.sigma_P / math.sqrt(GUN_YIL)

    def m(self, sr_hedef: float) -> float:
        return sr_hedef * self.sigma_P / math.sqrt(GUN_YIL) - self.F() + self.K()

    def dilim_gun(self) -> tuple:
        return (self.T - 904, 365, 365, 174)


def ayar(no: int) -> Ayar:
    if not 0 <= no < 2 ** len(IZGARA):
        raise ValueError("ayar_no 0..127")
    deg = {}
    for k, (ad, secenek) in enumerate(IZGARA):
        bit = (no >> (len(IZGARA) - 1 - k)) & 1
        deg[ad] = secenek[bit]
    return Ayar(**deg)


@dataclass
class Hat:
    x0: np.ndarray        # m = 0 iken gunluk fiyat P&L'i (T)
    epizot: np.ndarray    # gun -> epizot numarasi (T)


def _t4(rng, n):
    return math.sqrt(0.5) * rng.standard_t(4, n)


def hat_uret(rng, u: np.ndarray, ay: Ayar) -> Hat:
    T = ay.T
    uzunluk = rng.geometric(1.0 / ay.l_e, size=T)
    Z = rng.standard_normal(T)
    v = _t4(rng, T)
    sinir = np.cumsum(uzunluk)
    epizot = np.searchsorted(sinir, np.arange(T), side='right')
    mu0 = ay.a * (np.exp(ay.s * Z[epizot]) - math.exp(ay.s * ay.s / 2.0))
    eps = math.sqrt(ay.rho_f) * u + math.sqrt(1.0 - ay.rho_f) * v
    return Hat(x0=mu0 + eps, epizot=epizot)


@dataclass
class Duzey1Yol:
    ayar_no: int
    yol_no: int
    ayar: Ayar
    hatlar: list          # 15 Hat (ana)
    y_hatlar: list        # 15 Hat (B9 portfoyu)
    ikame: list           # 10 Hat (B10)
    carry_w: np.ndarray = None   # B seyreltme raporu (T)


def yol_uret(ayar_no: int, yol_no: int, tohum_kal: int = TOHUM_KAL) -> Duzey1Yol:
    ay = ayar(ayar_no)
    rng = uretec(tohum_kal, 1, ayar_no, yol_no)
    u = _t4(rng, ay.T)
    hatlar = [hat_uret(rng, u, ay) for _ in range(J)]
    u_y = _t4(rng, ay.T)
    y_hatlar = [hat_uret(rng, u_y, ay) for _ in range(J)]
    ikame = [hat_uret(rng, u, ay) for _ in range(B10_HAT)]
    carry_w = _t4(rng, ay.T)
    return Duzey1Yol(ayar_no=ayar_no, yol_no=yol_no, ayar=ay, hatlar=hatlar, y_hatlar=y_hatlar, ikame=ikame,
                     carry_w=carry_w)


def hat_net(h: Hat, ay: Ayar, sr_hedef: float, maliyet_k: int = 1) -> np.ndarray:
    """Hattin gunluk net P&L'i: x + F - k K, x = x0 + m(SR_hedef). Maliyet carpani yalniz K'yi olcekler (m 1x ile)."""
    return h.x0 + ay.m(sr_hedef) + ay.F() - maliyet_k * ay.K()


def portfoy(hatlar: list, ay: Ayar, sr_hedef: float, maliyet_k: int = 1) -> np.ndarray:
    """X_t = (1/J) sum_j (x_{j,t} + F - kK)."""
    return np.mean([hat_net(h, ay, sr_hedef, maliyet_k) for h in hatlar], axis=0)
