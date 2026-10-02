"""Birim risk (saf). MIMARI Ss3.3.

Ag, dosya, config veya durum erisimi yoktur. N_t=0 (bos evren) dali bu modulun disindadir; cagiran taraf
bos evrende bu fonksiyonlari hic cagirmamalidir (MIMARI Ss3.3 adim 8).
"""
from dataclasses import dataclass

import numpy as np

from .tipler import Parametreler


class BoyutlamaGirdiHatasi(ValueError):
    """Girdi dizileri bos/uyumsuz ya da 1^T R_hat 1 <= 0 (beklenmeyen sayisal durum)."""


@dataclass(frozen=True)
class BirimKitapSonucu:
    w_u: np.ndarray
    n: int
    m: float               # cesitlendirme carpani (tavansiz)
    m_tilde: float          # min(m, m_max)
    k: float                # olcek
    v_oncesi: float         # guvenlik olceklemesinden once V(w_u)
    v_sonrasi: float        # sonrasi (T4-a degismezini karsilamali: <= tau)
    guvenlik_olceklemesi_uygulandi: bool


def birim_kitap(s, sigma_hat, r_hat, sigma_hat_matris, sigma_sifir_matris, p: Parametreler) -> BirimKitapSonucu:
    """MIMARI Ss3.3 adim 1-7. N>=1 varsayar (N=0 cagiran tarafta ele alinir).

    s: sinyal vektoru (trend_sinyali cikisi, her varlik icin). sigma_hat: boyutlama sigma vektoru (taban
    uygulanmis). r_hat, sigma_hat_matris, sigma_sifir_matris: risk.kovaryans_hazirla cikislari.
    """
    s = np.asarray(s, dtype=float)
    sigma_hat = np.asarray(sigma_hat, dtype=float)
    n = len(s)
    if n == 0:
        raise BoyutlamaGirdiHatasi("bos evren icin birim_kitap cagrilmamali (N_t=0 dali ust katmanda)")
    if len(sigma_hat) != n:
        raise BoyutlamaGirdiHatasi("s ve sigma_hat ayni uzunlukta olmali")
    if np.any(sigma_hat <= 0):
        raise BoyutlamaGirdiHatasi("sigma_hat pozitif olmali")

    u = s / sigma_hat
    bir = np.ones(n)
    toplam_r = float(bir @ r_hat @ bir)  # = f^T Sigma_hat f (f_i = 1/sigma_i)
    if toplam_r <= 0:
        raise BoyutlamaGirdiHatasi("1^T R_hat 1 <= 0 (beklenmeyen)")
    ref_vol = np.sqrt(toplam_r)
    m = n / ref_vol
    m_tilde = min(m, p.m_max)
    k = p.tau * m_tilde / n
    w_u = k * u

    v_hat = float(np.sqrt(w_u @ sigma_hat_matris @ w_u))
    v_sifir = float(np.sqrt(w_u @ sigma_sifir_matris @ w_u))
    v_oncesi = max(v_hat, v_sifir)

    guvenlik = False
    w_u_son = w_u
    v_son = v_oncesi
    if v_oncesi > p.tau:
        w_u_son = w_u * (p.tau / v_oncesi)
        v_hat2 = float(np.sqrt(w_u_son @ sigma_hat_matris @ w_u_son))
        v_sifir2 = float(np.sqrt(w_u_son @ sigma_sifir_matris @ w_u_son))
        v_son = max(v_hat2, v_sifir2)
        guvenlik = True

    return BirimKitapSonucu(w_u=w_u_son, n=n, m=m, m_tilde=m_tilde, k=k,
                             v_oncesi=v_oncesi, v_sonrasi=v_son,
                             guvenlik_olceklemesi_uygulandi=guvenlik)
