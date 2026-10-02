"""Havuzlu, capali log-HAR volatilite tahmincisi ve QLIKE (saf). MIMARI Ss1b.

Ag, dosya, config veya durum erisimi yoktur. Tanimlar:
- RV_d: [d-1g, d) gununun saatlik log getiri karelerinin toplami. Saatlik getiri r_h = ln(C_h / C_{h-1}) yalniz iki
  ardisik saatin bari varsa tanimlidir (ilk saatin oncesi onceki gunun son bari). Eksik getiri sayisi
  donma_d_saat'i (8) asarsa RV_d tanimsizdir (MIMARI Ss2.5(d) ile ayni esik); aksi halde toplam 24/n ile olceklenir.
  RV_d = 0 (donuk fiyat) tanimsizdir. Maskeli ve islem disi gunleri cagiran taraf tanimsiz yapar (gunluk getiri
  tanimiyla ayni kume; hedef.coin_gunluk).
- Ozellikler (t gunu): l1 = ln RV_t; l7 = ln(son 7 gunun ort. RV); l30 = ln(son 30 gunun ort. RV);
  m = son en fazla 365 gunun ln RV ortalamasi (en az 90 tanimli gun). l7 icin en az 4/7, l30 icin en az 15/30
  tanimli gun gerekir (cogunluk).
- Hedef (Ss1b.2, K1-12): sonraki 7 gunun gunluk log getiri kareleri toplami; yedisi de tanimli olmali. Degerlendirme
  hedefi Y = toplam * 365/7. HAR'in sol tarafi y = ln(toplam) (yedi gunluk log varyans; iki tahminci ayni hedefe
  karsi sinanir).
- Capali regresyon: y - m = c + b1 (l1 - m) + b7 (l7 - m) + b30 (l30 - m) + e (havuzlu OLS).
- Tahmin: sigma^2_HAR = (365/7) * exp(y_hat + s2/2); s2 yuruyen tahmin artiklarinin varyansi (cagirandan).
- QLIKE(Y, F) = Y/F - ln(Y/F) - 1.
"""
import hashlib
import json
import math
from bisect import bisect_right
from dataclasses import dataclass

import numpy as np

from .gorunum import GUN_MS, SAAT_MS, SaatlikSeri
from .tipler import Parametreler

YILLIK_HAFTA = 365.0 / 7.0


def gunluk_rv(s: SaatlikSeri, gunler: np.ndarray, p: Parametreler) -> np.ndarray:
    """gunler (gun sinirlari, artan) icin RV_d; tanimsiz gunde nan."""
    gunler = np.asarray(gunler, dtype=np.int64)
    rv = np.full(len(gunler), np.nan)
    if len(s) < 2 or len(gunler) == 0:
        return rv
    ardisik = np.diff(s.acilis_ms) == SAAT_MS
    r = np.log(s.kapanis[1:] / s.kapanis[:-1])[ardisik]
    saat = s.acilis_ms[1:][ardisik]
    gun_sonu = (saat // GUN_MS + 1) * GUN_MS          # saat h, [d-1g, d) gunune aittir
    k = np.searchsorted(gunler, gun_sonu)
    ic = (k < len(gunler)) & (gunler[np.minimum(k, len(gunler) - 1)] == gun_sonu)
    toplam = np.zeros(len(gunler))
    sayi = np.zeros(len(gunler))
    np.add.at(toplam, k[ic], r[ic] ** 2)
    np.add.at(sayi, k[ic], 1.0)
    yeterli = sayi >= 24 - p.donma_d_saat
    with np.errstate(divide='ignore', invalid='ignore'):
        rv = np.where(yeterli, toplam * 24.0 / sayi, np.nan)
    rv[~(rv > 0)] = np.nan
    return rv


def har_ozellik(rv: np.ndarray, i: int, p: Parametreler):
    """rv (gun takvimine hizali) ve t'nin indeksi i icin (l1, l7, l30, m); tanimsizsa None."""
    if i < 0 or i >= len(rv) or not rv[i] > 0:
        return None
    son7 = rv[max(0, i - 6):i + 1]
    son30 = rv[max(0, i - 29):i + 1]
    son365 = rv[max(0, i - p.har_m_gun + 1):i + 1]
    if np.sum(~np.isnan(son7)) < p.har_l7_min or np.sum(~np.isnan(son30)) < p.har_l30_min:
        return None
    ln365 = np.log(son365[~np.isnan(son365)])
    if len(ln365) < p.har_m_min_gun:
        return None
    return (math.log(rv[i]), math.log(np.nanmean(son7)), math.log(np.nanmean(son30)), float(ln365.mean()))


def haftalik_hedef(getiriler: np.ndarray, i: int):
    """Gunluk getiri dizisinde t'nin indeksi i icin sonraki 7 gunun getiri kareleri toplami; tanimsizsa None."""
    sonraki = getiriler[i + 1:i + 8]
    if len(sonraki) < 7 or np.any(np.isnan(sonraki)):
        return None
    toplam = float(np.sum(sonraki ** 2))
    return toplam if toplam > 0 else None


def har_tasarim(ozellikler) -> tuple:
    """[(l1, l7, l30, m), ...] -> (X, m) capali regresyon tasarimi: X = [1, l1-m, l7-m, l30-m]."""
    o = np.asarray(ozellikler, dtype=float).reshape(-1, 4)
    m = o[:, 3]
    X = np.column_stack([np.ones(len(o)), o[:, 0] - m, o[:, 1] - m, o[:, 2] - m])
    return X, m


def har_katsayi(ozellikler, y, p: Parametreler = None):
    """Havuzlu OLS: (c, b1, b7, b30). y: ln(7 gunluk getiri kareleri toplami). Egitim yetersizse (p verilmisse
    en az p.har_egitim_min gozlem ve tam rank 4 gerekir) None: o ayin HAR tahmini tanimsizdir (Codex T7)."""
    X, m = har_tasarim(ozellikler)
    if p is not None and (len(X) < p.har_egitim_min or np.linalg.matrix_rank(X) < X.shape[1]):
        return None
    beta, *_ = np.linalg.lstsq(X, np.asarray(y, dtype=float) - m, rcond=None)
    return beta


def har_log_tahmin(ozellikler, beta) -> np.ndarray:
    """y_hat = m + X beta."""
    X, m = har_tasarim(ozellikler)
    return m + X @ np.asarray(beta, dtype=float)


def har_varyans(y_hat, s2: float) -> np.ndarray:
    """Yillik varyans tahmini sigma^2_HAR = (365/7) exp(y_hat + s2/2)."""
    return YILLIK_HAFTA * np.exp(np.asarray(y_hat, dtype=float) + 0.5 * s2)


def qlike(Y, F) -> np.ndarray:
    """QLIKE(Y, F) = Y/F - ln(Y/F) - 1 (Y > 0, F > 0)."""
    oran = np.asarray(Y, dtype=float) / np.asarray(F, dtype=float)
    return oran - np.log(oran) - 1.0


def dairesel_blok_bootstrap(hafta_farki: list, blok: int, cekis: int, tohum: int) -> np.ndarray:
    """hafta_farki: TAKVIM haftasi basina (QLIKE_HAR - QLIKE_EWMA) dizileri (kesitsel butun; satiri olmayan hafta bos
    dizi, blok takvim haftasidir). Her cekiste ceil(W/blok) blok baslangici esit olasilikla secilir, blok dairesel
    devam eder, ilk W hafta alinir; istatistik secilen haftalarin butun satirlarinin ortalamasidir (havuzlu
    ortalama; hic satir yoksa nan). Doner: cekis istatistikleri."""
    W = len(hafta_farki)
    toplam = np.array([float(np.sum(x)) for x in hafta_farki])
    adet = np.array([len(x) for x in hafta_farki], dtype=float)
    rng = np.random.default_rng(tohum)
    n_blok = -(-W // blok)
    sonuc = np.empty(cekis)
    for b in range(cekis):
        bas = rng.integers(0, W, size=n_blok)
        idx = ((bas[:, None] + np.arange(blok)[None, :]) % W).ravel()[:W]
        n = adet[idx].sum()
        sonuc[b] = toplam[idx].sum() / n if n > 0 else np.nan
    return sonuc


@dataclass(frozen=True)
class HarTakvimi:
    """Kilit adim 2 sonucunun motorda kullanilan hali (on-kayit madde 12; ciktilar/v8_har_secimi_20260929_01/
    sonuc.json). D icindeki kosularda: katsayi = t'ye kadar (t dahil) son ay basi yuruyen tahmini; s^2 = t'ye kadar
    son Pazartesinin yuruyen artik varyansi (t'ye kadar hedefi tamamlanmis son 52 hafta). Tanimsizsa None (EWMA)."""
    aylar: tuple                 # ((ay_ms, (c, b1, b7, b30) | None), ...) artan
    s2: tuple                    # ((pazartesi_ms, s2), ...) artan

    @classmethod
    def sonuctan(cls, sonuc: dict) -> 'HarTakvimi':
        aylar = tuple(sorted((int(k), None if v['beta'] is None else tuple(float(x) for x in v['beta']))
                             for k, v in sonuc['katsayi_yolu'].items()))
        s2 = tuple(sorted((int(k), float(v)) for k, v in sonuc['s2_yolu'].items()))
        return cls(aylar=aylar, s2=s2)

    def katsayi(self, t_ms: int):
        i = bisect_right([a for a, _ in self.aylar], t_ms) - 1
        return None if i < 0 else self.aylar[i][1]

    def artik_varyansi(self, t_ms: int):
        i = bisect_right([a for a, _ in self.s2], t_ms) - 1
        return None if i < 0 else self.s2[i][1]

    def kimlik(self) -> str:
        return hashlib.sha256(json.dumps({'aylar': self.aylar, 's2': self.s2}, sort_keys=True).encode()).hexdigest()


def har_sigma(s: SaatlikSeri, gunler: np.ndarray, gun_gecerli: np.ndarray, takvim: HarTakvimi,
              p: Parametreler) -> float:
    """Karar gunu t = gunler[-1] icin yillik sigma_HAR; tanimsizsa nan (cagiran sigma_EWMA'ya doner). gun_gecerli:
    kapanisi olan, maskesiz ve islem disi olmayan gunler (hedef.coin_gunluk; secim betigiyle ayni kume)."""
    t = int(gunler[-1])
    beta = takvim.katsayi(t)
    s2 = takvim.artik_varyansi(t)
    if beta is None or s2 is None or s is None:
        return float('nan')
    rv = gunluk_rv(s, gunler, p)
    rv[~np.asarray(gun_gecerli, dtype=bool)] = np.nan
    oz = har_ozellik(rv, len(gunler) - 1, p)
    if oz is None:
        return float('nan')
    v = float(har_varyans(har_log_tahmin([oz], beta)[0], s2))
    return math.sqrt(v) if math.isfinite(v) and v > 0 else float('nan')
