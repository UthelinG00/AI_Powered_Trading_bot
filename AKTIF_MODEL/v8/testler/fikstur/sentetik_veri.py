"""v8 testleri icin sentetik gunluk fiyat serisi ve sabit fikstürler. Gercek veri, ag ya da borsa yok.

REV1'in testler/test_rev1_inputs.py'deki bars() deseniyle ayni ruhtadir: tek, merkezi, tohumlu bir uretici;
her test dosyasi kendi ozel senaryosunu (sabit buyume, sifir getiri vb.) ayrica kurar.
"""
import numpy as np


def gunluk_fiyat_serisi(n: int, gunluk_oran: float = 0.0, volatilite: float = 0.0,
                         sok_gunu: int | None = None, sok_buyuklugu: float = 0.0,
                         tohum: int | None = None, p0: float = 100.0) -> np.ndarray:
    """Gunluk log-getiri = gunluk_oran + N(0, volatilite) + (sok_gunu'nde sok_buyuklugu bir kez).

    tohum verilmezse volatilite=0 oldugu surece deterministiktir (rastgelelik yalniz volatilite>0 ise
    devreye girer, testte sabit tohumla kullanilmalidir).
    """
    if n <= 0:
        raise ValueError("n > 0 olmali")
    getiriler = np.full(n, gunluk_oran, dtype=float)
    if volatilite > 0:
        rng = np.random.default_rng(tohum)
        getiriler = getiriler + rng.normal(0.0, volatilite, size=n)
    if sok_gunu is not None:
        if not (0 <= sok_gunu < n):
            raise ValueError("sok_gunu dizinin icinde olmali")
        getiriler[sok_gunu] += sok_buyuklugu
    fiyatlar = p0 * np.exp(np.cumsum(getiriler))
    return fiyatlar


# KC-13 (Codex karsi ornegi, MIMARI Ss3.2): cift bazli ham korelasyonun PSD olmadigi 3x3 durum.
# Dis kosegenler (0.9, 0.9, -0.9); harman (0.5*bu + 0.5*R_S(0.7)) v=(-1,0.5,0.5) icin -0.15 verir.
KC13_KARSI_ORNEK_KORELASYON = np.array([
    [1.0, 0.9, 0.9],
    [0.9, 1.0, -0.9],
    [0.9, -0.9, 1.0],
])
