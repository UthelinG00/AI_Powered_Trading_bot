"""Carry kapisi serileri (saf; CARRY Ss4.1, Ss5.2-Ss5.6; U-01, U-06, U-16, U-23, U-29). Girdi: motor.ayristirma.ayristir
sonucu (saatlik satirlar; saat T = [T, T+1h) bari, T damgali funding dahil) ve kosunun NAV'i (KosuSonucu.nav_ms/nav:
bar kapanis damgalari; kosu basinda nav0).

- Hafta: Pazartesi 00:00 -> sonraki Pazartesi 00:00; kapi takvimi 2023-10-02 -> 2026-06-29, 143 tam hafta (Ss4.1).
- Ay: UTC takvim ayi 2023-10 ... 2026-06 (33); T0 = 2023-10-01 00:00 sonrasi butun saatler (U-06).
- Carry bilesenleri (Ss5.2, U-23): F = carry_funding + hedge_funding, P = carry_fiyat + hedge_fiyat, C = carry_maliyet
  (hedge dahil), N = F + P - C. Olcek r^X_w = X_w / (omega_C * L * NAV_{w basi}) (Ss5.3); a^C ayni olcekte (Ss5.6).
- Trend (U-01): r^T_w = (trend_fiyat + trend_funding - trend_maliyet)_w / (L * NAV_{w basi}); a^T = artik_trend ayni
  olcekte. Trend serileri YALNIZ bellekte rho_hat/rho_ust icin kullanilir; yazilmaz, raporlanmaz (Ss2 muhur).
- NAV_{sinir} = sinir anindaki NAV (U-29: Pazartesi 00:00 = Pazar 23:00 barinin kapanisi); kosu basinda nav0.
"""
from dataclasses import dataclass
from datetime import datetime, timezone

import numpy as np

GUN_MS = 86_400_000
SAAT_MS = 3_600_000
HAFTA_MS = 7 * GUN_MS


def _ms(y: int, a: int, g: int) -> int:
    return int(datetime(y, a, g, tzinfo=timezone.utc).timestamp() * 1000)


class SeriHatasi(ValueError):
    """Kosu kapi takvimini kapsamiyor ya da NAV siniri eksik."""


@dataclass(frozen=True)
class Takvim:
    t0_ms: int                   # degerlendirme baslangici (Ss4.1)
    hafta_bas_ms: int            # ilk Pazartesi 00:00
    n_hafta: int
    ay_sinirlari: tuple          # (ay_0 basi, ..., son ay sonu); ilk sinir max(t0, ay basi)

    def hafta_sinirlari(self) -> np.ndarray:
        return self.hafta_bas_ms + np.arange(self.n_hafta + 1, dtype=np.int64) * HAFTA_MS


def _ay_sinirlari(y0: int, a0: int, y1: int, a1: int) -> tuple:
    out, y, a = [], y0, a0
    while (y, a) <= (y1, a1):
        out.append(_ms(y, a, 1))
        y, a = (y + 1, 1) if a == 12 else (y, a + 1)
    out.append(_ms(y, a, 1))
    return tuple(out)


KAPI_TAKVIMI = Takvim(t0_ms=_ms(2023, 10, 1), hafta_bas_ms=_ms(2023, 10, 2), n_hafta=143,
                      ay_sinirlari=_ay_sinirlari(2023, 10, 2026, 6))

CARRY_BILESEN = {'F': (('carry_funding', 1.0), ('hedge_funding', 1.0)),
                 'P': (('carry_fiyat', 1.0), ('hedge_fiyat', 1.0)),
                 'C': (('carry_maliyet', 1.0),),
                 'a_C': (('artik_carry', 1.0),)}
TREND_BILESEN = {'T': (('trend_fiyat', 1.0), ('trend_funding', 1.0), ('trend_maliyet', -1.0)),
                 'a_T': (('artik_trend', 1.0),)}
OZDESLIK_BILESEN = (('trend_fiyat', 1.0), ('trend_funding', 1.0), ('carry_fiyat', 1.0), ('carry_funding', 1.0),
                    ('hedge_fiyat', 1.0), ('hedge_funding', 1.0), ('trend_maliyet', -1.0), ('carry_maliyet', -1.0),
                    ('netleme', 1.0), ('icra_artigi', 1.0))


class NavOkuyucu:
    """Sinir anindaki NAV: kosu basinda nav0, sonra bar kapanis damgasindaki NAV (U-29)."""

    def __init__(self, nav_ms, nav, nav0: float):
        self.ms = np.asarray(nav_ms, dtype=np.int64)
        self.nav = np.asarray(nav, dtype=float)
        if len(self.ms) == 0 or len(self.ms) != len(self.nav):
            raise SeriHatasi("NAV dizisi bos ya da boyutlar farkli")
        self.bas_ms = int(self.ms[0]) - SAAT_MS
        self.nav0 = float(nav0)

    def __call__(self, t_ms: int) -> float:
        t_ms = int(t_ms)
        if t_ms == self.bas_ms:
            return self.nav0
        i = int(np.searchsorted(self.ms, t_ms))
        if i < len(self.ms) and int(self.ms[i]) == t_ms:
            return float(self.nav[i])
        raise SeriHatasi(f"kosu {t_ms} anindaki NAV'i icermiyor")


def kosu_olcegi(gunluk) -> tuple:
    """(nav0, L) gunlugun baslangic kaydindan."""
    bas = next(k for k in gunluk.kayitlar() if k.tur == 'baslangic')
    return float(bas.veri['nav0']), float(bas.veri['L'])


def _pencere_toplami(ayr, bilesen, sinirlar: np.ndarray) -> np.ndarray:
    """Her [sinir_k, sinir_{k+1}) icin bilesen satirlarinin saatlik toplamlari (isaretli). Pencere kosunun saatlerini
    tam kapsamali."""
    saat = np.asarray(ayr.saat_ms, dtype=np.int64)
    if len(saat) == 0 or int(sinirlar[0]) < int(saat[0]) or int(sinirlar[-1]) > int(saat[-1]) + SAAT_MS:
        raise SeriHatasi("ayristirma kapi takvimini kapsamiyor")
    ix = np.searchsorted(saat, sinirlar)
    out = np.zeros(len(sinirlar) - 1)
    for ad, isaret in bilesen:
        dizi = np.asarray(ayr.satirlar[ad], dtype=float)
        if not np.isfinite(dizi).all():
            raise SeriHatasi(f"{ad} satirinda sonlu olmayan deger")
        out += isaret * np.array([float(np.sum(dizi[a:b])) for a, b in zip(ix[:-1], ix[1:])])
    return out


def haftalik(ayr, nav: NavOkuyucu, L: float, omega_c: float, takvim: Takvim = KAPI_TAKVIMI) -> dict:
    """Haftalik carry birim serileri r^F, r^C, r^P, r^N, a^C, r^{N,g} ve trend serileri r^T, a^T, r^{T,g}.
    r^N = r^F - r^C + r^P (sr_kredili'nin bilesen denetimiyle ayni toplama sirasi)."""
    sinir = takvim.hafta_sinirlari()
    nav_bas = np.array([nav(t) for t in sinir[:-1].tolist()])
    if not (nav_bas > 0).all():
        raise SeriHatasi("hafta basi NAV'i pozitif degil")
    payda_c = omega_c * L * nav_bas
    payda_t = L * nav_bas
    s = {k: _pencere_toplami(ayr, b, sinir) / payda_c for k, b in CARRY_BILESEN.items()}
    s.update({k: _pencere_toplami(ayr, b, sinir) / payda_t for k, b in TREND_BILESEN.items()})
    s['N'] = s['F'] - s['C'] + s['P']
    s['N_g'] = s['N'] + s['a_C']
    s['T_g'] = s['T'] + s['a_T']
    s['hafta_ms'] = sinir[:-1]
    s['nav_bas'] = nav_bas
    return s


def aylik_fc(ayr, nav: NavOkuyucu, L: float, omega_c: float, takvim: Takvim = KAPI_TAKVIMI) -> dict:
    """K5 (U-06): ay basina (F - C)_m / (omega_C * L * NAV_{ay basi}); ilk ay T0'dan baslar."""
    sinir = np.array(takvim.ay_sinirlari, dtype=np.int64)
    sinir[0] = max(int(sinir[0]), takvim.t0_ms)
    nav_bas = np.array([nav(t) for t in sinir[:-1].tolist()])
    if not (nav_bas > 0).all():
        raise SeriHatasi("ay basi NAV'i pozitif degil")
    payda = omega_c * L * nav_bas
    fc = _pencere_toplami(ayr, CARRY_BILESEN['F'], sinir) / payda - _pencere_toplami(ayr, CARRY_BILESEN['C'], sinir) / payda
    return {'ay_ms': sinir[:-1], 'FC': fc, 'nav_bas': nav_bas}


def gunluk_ozdeslik_orani(ayr, nav: NavOkuyucu) -> dict:
    """V2 (U-16): her gun |sum dnav - sum bilesenler| / NAV_{gun basi}. Gun sonu NAV'i (dnav) hic bilinmeyen gun ve
    sonlu olmayan fark inf'tir (her gun denetlenir; Codex T15-9, U-57). Doner {gun_ms: oran}."""
    saat = np.asarray(ayr.saat_ms, dtype=np.int64)
    bilesen = np.zeros(len(saat))
    for ad, isaret in OZDESLIK_BILESEN:
        bilesen += isaret * np.asarray(ayr.satirlar[ad], dtype=float)
    dnav = np.asarray(ayr.satirlar['dnav'], dtype=float)
    gun = (saat // GUN_MS) * GUN_MS
    out = {}
    for g in np.unique(gun).tolist():
        ix = gun == g
        dn = dnav[ix]
        if np.isnan(dn).all():
            out[int(g)] = float('inf')
            continue
        fark = abs(float(np.nansum(dn)) - float(bilesen[ix].sum()))
        nb = nav(max(int(g), nav.bas_ms))
        out[int(g)] = fark / nb if np.isfinite(fark) and nb > 0 else float('inf')
    return out
