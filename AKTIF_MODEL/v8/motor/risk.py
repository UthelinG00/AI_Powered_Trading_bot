"""Sigma ve kovaryans (saf). MIMARI Ss3.2 (KC-13 PSD duzeltmesi dahil).

Ag, dosya, config veya durum erisimi yoktur. Getiri dizilerinde eksik gun np.nan ile isaretlenir (0 yazilmaz);
merkezleme yapilmaz (ortalama sifir varsayilir).
"""
from dataclasses import dataclass

import numpy as np

from .tipler import Parametreler


class RiskGirdiHatasi(ValueError):
    """Getiri dizileri bos, uzunluk uyumsuz ya da matris boyutu gecersiz."""


def sigma_ewma_tahmin(gunluk_getiriler, p: Parametreler) -> float:
    """sigma_EW(H) = sqrt(365 * EWMA_H(r^2)), iki yariomrun buyugu. Taban bu fonksiyonda uygulanmaz.

    gunluk_getiriler: kronolojik, np.nan eksik gunu isaretler (son eleman = en yeni). En az bir gecerli
    gozlem gerekir.
    """
    r = np.asarray(gunluk_getiriler, dtype=float)
    gecerli = ~np.isnan(r)
    if not gecerli.any():
        raise RiskGirdiHatasi("en az bir gecerli getiri gozlemi gerekli")
    n = len(r)
    yas = np.arange(n - 1, -1, -1)  # 0 = en yeni
    en_buyuk = 0.0
    for h in p.ewma_yariomurleri:
        agirlik = np.where(gecerli, 0.5 ** (yas / h), 0.0)
        toplam_agirlik = agirlik.sum()
        if toplam_agirlik <= 0:
            continue
        r2 = np.where(gecerli, r * r, 0.0)
        ewma_r2 = (agirlik * r2).sum() / toplam_agirlik
        sigma_h = np.sqrt(365.0 * ewma_r2)
        en_buyuk = max(en_buyuk, float(sigma_h))
    return en_buyuk


def _agirlik_dizisi(n: int, yariomur: float) -> np.ndarray:
    yas = np.arange(n - 1, -1, -1)
    return 0.5 ** (yas / yariomur)


def ciftli_ham_korelasyon(getiriler: list, p: Parametreler) -> np.ndarray:
    """R_cift: cift bazli, yasla agirlikli ham korelasyon. PSD garantisi yoktur (KC-13); psd_duzelt ile duzelt.

    getiriler: N adet, ayni takvim uzunluguna hizali kronolojik dizi (np.nan = eksik gun).
    """
    if len(getiriler) == 0:
        raise RiskGirdiHatasi("en az bir varlik gerekli")
    n_varlik = len(getiriler)
    diziler = [np.asarray(g, dtype=float) for g in getiriler]
    uzunluk = len(diziler[0])
    if any(len(d) != uzunluk for d in diziler):
        raise RiskGirdiHatasi("butun getiri dizileri ayni uzunlukta olmali")
    agirlik_tum = _agirlik_dizisi(uzunluk, p.korelasyon_yariomur)

    R = np.eye(n_varlik)
    for i in range(n_varlik):
        gecerli_i = ~np.isnan(diziler[i])
        for j in range(i + 1, n_varlik):
            gecerli_j = ~np.isnan(diziler[j])
            ortak = gecerli_i & gecerli_j
            ortak_gun = int(ortak.sum())
            if ortak_gun < p.min_ortak_gun:
                rho = p.r_sabit
            else:
                a = agirlik_tum[ortak]
                ri = diziler[i][ortak]
                rj = diziler[j][ortak]
                c_ij = float((a * ri * rj).sum())
                v_i = float((a * ri * ri).sum())
                v_j = float((a * rj * rj).sum())
                if v_i <= 0 or v_j <= 0:
                    rho = p.r_sabit
                else:
                    rho = c_ij / np.sqrt(v_i * v_j)
                    rho = max(-1.0, min(1.0, rho))
            R[i, j] = rho
            R[j, i] = rho
    return R


@dataclass(frozen=True)
class PsdDuzeltmeSonucu:
    r_ew: np.ndarray
    kirpilan_ozdeger_sayisi: int
    frobenius_duzeltme: float


def psd_duzelt(r_ham: np.ndarray, p: Parametreler) -> PsdDuzeltmeSonucu:
    """Ozdeger kirpma (KC-13): R_ham = Q*Lambda*Q^T; Lambda+ = max(Lambda, eps); B = Q*Lambda+*Q^T;
    R_EW = D^-1/2 * B * D^-1/2, D = diag(B). Sonuc simetrik, kosegeni 1 ve PSD'dir.
    """
    r_ham = np.asarray(r_ham, dtype=float)
    n = r_ham.shape[0]
    if n == 1:
        return PsdDuzeltmeSonucu(r_ew=np.array([[1.0]]), kirpilan_ozdeger_sayisi=0, frobenius_duzeltme=0.0)
    ozdeger, ozvektor = np.linalg.eigh(r_ham)  # simetrik matris icin kararli ozayrisim
    kirpilan = int((ozdeger < p.eps_psd).sum())
    ozdeger_kirpik = np.maximum(ozdeger, p.eps_psd)
    b = (ozvektor * ozdeger_kirpik) @ ozvektor.T
    d = np.diag(b)
    if np.any(d <= 0):
        raise RiskGirdiHatasi("PSD duzeltmesi sonrasi kosegen pozitif olmali (beklenmeyen sayisal hata)")
    d_yarim_ters = 1.0 / np.sqrt(d)
    r_ew = b * np.outer(d_yarim_ters, d_yarim_ters)
    r_ew = (r_ew + r_ew.T) / 2.0  # sayisal simetri (yuvarlama hatasi giderme)
    np.fill_diagonal(r_ew, 1.0)
    frobenius = float(np.linalg.norm(r_ew - r_ham, ord='fro'))
    return PsdDuzeltmeSonucu(r_ew=r_ew, kirpilan_ozdeger_sayisi=kirpilan, frobenius_duzeltme=frobenius)


def sabit_korelasyon_matrisi(n: int, p: Parametreler) -> np.ndarray:
    """R_S: kosegen 1, digerleri r_sabit (varsayilan 0.7). PSD (ozdegerler (1-r_sabit) ve 1+(n-1)*r_sabit)."""
    if n <= 0:
        raise RiskGirdiHatasi("n > 0 olmali")
    r = np.full((n, n), p.r_sabit)
    np.fill_diagonal(r, 1.0)
    return r


@dataclass(frozen=True)
class KovaryansSonucu:
    r_hat: np.ndarray
    sigma_hat: np.ndarray  # Sigma_hat = diag(sigma) R_hat diag(sigma)
    sigma_sifir: np.ndarray  # Sigma_0 = diag(sigma) I diag(sigma)  (hedge cokusu senaryosu)
    kirpilan_ozdeger_sayisi: int
    frobenius_duzeltme: float


def kovaryans_hazirla(getiriler: list, sigma_vektor, p: Parametreler) -> KovaryansSonucu:
    """Tam boru hatti: R_cift -> psd_duzelt -> R_EW; R_S; R_hat = harman*R_EW + (1-harman)*R_S; Sigma_hat, Sigma_0.

    N=0 cagiran tarafca ele alinmalidir (bu fonksiyon N>=1 varsayar). N=1 icin R_hat=[[1]].
    """
    n = len(getiriler)
    if n == 0:
        raise RiskGirdiHatasi("bos evren icin kovaryans kurulmaz; cagiran N_t=0 dalini kullanmali")
    sigma = np.asarray(sigma_vektor, dtype=float)
    if len(sigma) != n:
        raise RiskGirdiHatasi("sigma_vektor uzunlugu varlik sayisiyla eslesmeli")
    if n == 1:
        r_hat = np.array([[1.0]])
        sigma_hat = sigma.reshape(1, 1) ** 2
        return KovaryansSonucu(r_hat=r_hat, sigma_hat=sigma_hat, sigma_sifir=sigma_hat.copy(),
                                kirpilan_ozdeger_sayisi=0, frobenius_duzeltme=0.0)
    r_cift = ciftli_ham_korelasyon(getiriler, p)
    duzeltme = psd_duzelt(r_cift, p)
    r_s = sabit_korelasyon_matrisi(n, p)
    w = p.harman_agirligi
    r_hat = w * duzeltme.r_ew + (1.0 - w) * r_s
    diag_sigma = np.diag(sigma)
    sigma_hat = diag_sigma @ r_hat @ diag_sigma
    sigma_sifir = diag_sigma @ diag_sigma  # R_0 = birim matris
    return KovaryansSonucu(r_hat=r_hat, sigma_hat=sigma_hat, sigma_sifir=sigma_sifir,
                            kirpilan_ozdeger_sayisi=duzeltme.kirpilan_ozdeger_sayisi,
                            frobenius_duzeltme=duzeltme.frobenius_duzeltme)
