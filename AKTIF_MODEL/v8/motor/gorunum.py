"""Piyasa gorunumu: t'ye kadar kapanmis 1h barlar ve funding kayitlari (saf veri + PIT okuma yardimcilari).
MIMARI Ss2.1-Ss2.2, Ss5.1 (gorunum), Ss2.6 (borsa capi bosluk tespiti).

Ag, dosya, config veya durum erisimi yoktur. Bakis-ileri korumasi yapisaldir: `gorunum_kur(veri, t)` yalniz
`acilis + 1h <= t` olan barlari ve `damga <= t` olan funding kayitlarini dilimler; bu modulun butun okuma
fonksiyonlari yalniz gorunumun icindekini gorur. Zaman birimi UTC milisaniyedir.
"""
from dataclasses import dataclass, field
from datetime import datetime, timezone

import numpy as np

SAAT_MS = 3_600_000
GUN_MS = 86_400_000


class GorunumGirdiHatasi(ValueError):
    """Bar/funding dizileri tutarsiz, siralanmamis ya da saat izgarasinda degil."""


@dataclass(frozen=True)
class SaatlikSeri:
    """Bir coinin 1h barlari. Eksik saat = dizide olmayan saat (0 yazilmaz). hacim = quote hacmi (USDT)."""
    acilis_ms: np.ndarray       # int64, kesin artan, SAAT_MS kati
    acilis: np.ndarray
    yuksek: np.ndarray
    dusuk: np.ndarray
    kapanis: np.ndarray
    hacim: np.ndarray
    hacim_kum: np.ndarray       # uzunluk n+1; hacim_kum[k] = hacim[:k].sum() (onek toplami; PIT guvenli)

    def __len__(self):
        return len(self.acilis_ms)


def saatlik_seri(acilis_ms, acilis, yuksek, dusuk, kapanis, hacim) -> SaatlikSeri:
    ms = np.asarray(acilis_ms, dtype=np.int64)
    diziler = [np.asarray(x, dtype=float) for x in (acilis, yuksek, dusuk, kapanis, hacim)]
    if any(len(d) != len(ms) for d in diziler):
        raise GorunumGirdiHatasi("bar dizileri ayni uzunlukta olmali")
    if len(ms) and (np.any(ms % SAAT_MS != 0) or np.any(np.diff(ms) <= 0)):
        raise GorunumGirdiHatasi("acilis_ms saat izgarasinda ve kesin artan olmali")
    if np.any(diziler[4] < 0):
        raise GorunumGirdiHatasi("hacim negatif olamaz")
    kum = np.concatenate([[0.0], np.cumsum(diziler[4])])
    return SaatlikSeri(ms, *diziler, hacim_kum=kum)


def _seri_dilimle(s: SaatlikSeri, n: int) -> SaatlikSeri:
    return SaatlikSeri(s.acilis_ms[:n], s.acilis[:n], s.yuksek[:n], s.dusuk[:n], s.kapanis[:n], s.hacim[:n],
                       s.hacim_kum[:n + 1])


@dataclass(frozen=True)
class FundingSerisi:
    damga_ms: np.ndarray        # int64, en yakin tam saate yuvarlanmis, kesin artan (MIMARI Ss2.1)
    oran: np.ndarray
    aralik_saat: np.ndarray = None  # istege bagli: kaydin kendi araligi (arsivde funding_interval_hours); nan = bilinmiyor

    def __len__(self):
        return len(self.damga_ms)


def funding_serisi(damga_ms, oran, aralik_saat=None) -> FundingSerisi:
    """Damgalar en yakin tam saate yuvarlanir (ms sapmalari; K1-20.8). Yuvarlama sonrasi cakisma hatadir.
    aralik_saat: istege bagli kayit araligi (saat); yoksa ters kayit kapsami damgalardan cikarilir (funding.py)."""
    d = np.asarray(damga_ms, dtype=np.int64)
    r = np.asarray(oran, dtype=float)
    if len(d) != len(r):
        raise GorunumGirdiHatasi("funding damga ve oran ayni uzunlukta olmali")
    a = None
    if aralik_saat is not None:
        a = np.asarray(aralik_saat, dtype=float)
        if len(a) != len(d):
            raise GorunumGirdiHatasi("funding aralik_saat damga ile ayni uzunlukta olmali")
    d = ((d + SAAT_MS // 2) // SAAT_MS) * SAAT_MS
    if len(d) and np.any(np.diff(d) <= 0):
        raise GorunumGirdiHatasi("funding damgalari yuvarlama sonrasi kesin artan olmali")
    return FundingSerisi(d, r, a)


@dataclass(frozen=True)
class TamVeri:
    """Kosunun butun verisi (geri test adaptoru). Karar fonksiyonlari bunu dogrudan gormez; gorunum_kur ile
    t'ye kadar dilimlenmis hali verilir."""
    barlar: dict
    funding: dict
    adaylar: tuple


@dataclass(frozen=True)
class PiyasaGorunumu:
    t_ms: int
    barlar: dict                 # coin -> SaatlikSeri (yalniz acilis + 1h <= t)
    funding: dict                # coin -> FundingSerisi (yalniz damga <= t)
    adaylar: tuple               # aday liste (gelistirmede 122, bankada banka listesi)
    dis_bayraklar: object = None  # MIMARI Ss5.1 dis bayrak modu (K1-14 kancasi); None = uretim modu


def gorunum_kur(veri: TamVeri, t_ms: int, dis_bayraklar=None) -> PiyasaGorunumu:
    barlar = {}
    for coin, s in veri.barlar.items():
        n = int(np.searchsorted(s.acilis_ms, t_ms - SAAT_MS, side='right'))
        if n > 0:
            barlar[coin] = _seri_dilimle(s, n)
    funding = {}
    for coin, f in veri.funding.items():
        n = int(np.searchsorted(f.damga_ms, t_ms, side='right'))
        funding[coin] = FundingSerisi(f.damga_ms[:n], f.oran[:n],
                                      None if f.aralik_saat is None else f.aralik_saat[:n])
    return PiyasaGorunumu(t_ms=t_ms, barlar=barlar, funding=funding, adaylar=tuple(veri.adaylar),
                          dis_bayraklar=dis_bayraklar)


# ---------------------------------------------------------------------------------------------------------
# PIT okuma yardimcilari. Hepsi yalniz verilen seriyi okur; `t_ms` parametresi pencerenin (haric) ust ucudur
# ve gorunum.t_ms'ten buyuk olamaz (gecmis bir gunu yeniden degerlendirirken daha kucuk olabilir).
# ---------------------------------------------------------------------------------------------------------

def gun_basi_mi(t_ms: int) -> bool:
    return t_ms % GUN_MS == 0


def aylik_secim_gunu_mu(t_ms: int) -> bool:
    """Her ayin 1'i 00:00 UTC (MIMARI Ss2.2)."""
    if not gun_basi_mi(t_ms):
        return False
    return datetime.fromtimestamp(t_ms / 1000, tz=timezone.utc).day == 1


def bar_indeksi(s: SaatlikSeri, acilis_ms: int):
    """acilis_ms'te acilan barin indeksi; bar yoksa None."""
    k = int(np.searchsorted(s.acilis_ms, acilis_ms, side='left'))
    if k < len(s.acilis_ms) and int(s.acilis_ms[k]) == acilis_ms:
        return k
    return None


def saat_indeksleri(s: SaatlikSeri, saatler) -> np.ndarray:
    """Her saat icin o saatte acilan barin indeksi; bar yoksa -1 (bar_indeksi'nin vektor hali)."""
    saatler = np.asarray(saatler, dtype=np.int64)
    if len(s) == 0 or len(saatler) == 0:
        return np.full(len(saatler), -1, dtype=np.int64)
    k = np.searchsorted(s.acilis_ms, saatler, side='left')
    k_guvenli = np.minimum(k, len(s) - 1)
    return np.where((k < len(s)) & (s.acilis_ms[k_guvenli] == saatler), k_guvenli, -1)


def ilk_bar_ms(s: SaatlikSeri):
    return int(s.acilis_ms[0]) if len(s) else None


def son_kapanis(s: SaatlikSeri, t_ms: int):
    """t'den once kapanmis son barin kapanisi (acilis + 1h <= t); yoksa None. Deger/fiyat_ref icin."""
    k = int(np.searchsorted(s.acilis_ms, t_ms - SAAT_MS, side='right'))
    if k == 0:
        return None
    return float(s.kapanis[k - 1])


def son_islem_goren_bar_ms(s: SaatlikSeri, t_ms: int):
    """t'den once kapanmis, hacmi > 0 son barin acilis zamani; yoksa None (MIMARI Ss1c.5)."""
    k = int(np.searchsorted(s.acilis_ms, t_ms - SAAT_MS, side='right'))
    pozitif = np.nonzero(s.hacim[:k] > 0)[0]
    if len(pozitif) == 0:
        return None
    return int(s.acilis_ms[pozitif[-1]])


def gunluk_kapanislar(s: SaatlikSeri, gunler_ms: np.ndarray) -> np.ndarray:
    """P_i,d = [d-1h, d) barinin kapanisi; bar yoksa nan (MIMARI Ss2.2: coin o gun 'islem disi')."""
    hedef = np.asarray(gunler_ms, dtype=np.int64) - SAAT_MS
    k = np.searchsorted(s.acilis_ms, hedef, side='left')
    k_guvenli = np.minimum(k, max(len(s) - 1, 0))
    if len(s) == 0:
        return np.full(len(hedef), np.nan)
    var = (k < len(s)) & (s.acilis_ms[k_guvenli] == hedef)
    return np.where(var, s.kapanis[k_guvenli], np.nan)


def gunluk_hacimler(s: SaatlikSeri, gunler_ms: np.ndarray) -> np.ndarray:
    """[d-1g, d) araligindaki barlarin quote hacmi toplami; bar yoksa 0."""
    gunler = np.asarray(gunler_ms, dtype=np.int64)
    alt = np.searchsorted(s.acilis_ms, gunler - GUN_MS, side='left')
    ust = np.searchsorted(s.acilis_ms, gunler, side='left')
    return s.hacim_kum[ust] - s.hacim_kum[alt]


def gun_takvimi(bas_ms: int, t_ms: int) -> np.ndarray:
    """bas'tan (dahil, gun basina yukari yuvarlanir) t'ye (dahil) kadar gun sinirlari."""
    ilk = -(-bas_ms // GUN_MS) * GUN_MS
    if ilk > t_ms:
        return np.array([], dtype=np.int64)
    return np.arange(ilk, t_ms + 1, GUN_MS, dtype=np.int64)


def son_gunler(t_ms: int, gun: int, ilk_ms=None) -> np.ndarray:
    """t dahil son `gun` gun siniri (t-(gun-1)g ... t); ilk_ms verilirse ondan sonraki tam gunler."""
    gunler = t_ms - GUN_MS * np.arange(gun - 1, -1, -1, dtype=np.int64)
    if ilk_ms is not None:
        gunler = gunler[gunler - GUN_MS >= ilk_ms]
    return gunler


def v60(s: SaatlikSeri, t_ms: int, gun: int) -> float:
    """Son `gun` gunun medyan gunluk quote hacmi (V60). Coinin ilk barindan onceki gunler girmez."""
    gunler = son_gunler(t_ms, gun, ilk_bar_ms(s))
    if len(gunler) == 0:
        return 0.0
    return float(np.median(gunluk_hacimler(s, gunler)))


def saatlik_hacim_dizisi(s: SaatlikSeri, bas_ms: int, bit_ms: int) -> np.ndarray:
    """[bas, bit) saatlerinin quote hacmi; eksik saat 0 (muhafazakar). Ilk bardan onceki saatler girmez."""
    ilk = ilk_bar_ms(s)
    if ilk is None:
        return np.array([])
    bas = max(bas_ms, ilk)
    if bas >= bit_ms:
        return np.array([])
    saatler = np.arange(bas, bit_ms, SAAT_MS, dtype=np.int64)
    k = np.searchsorted(s.acilis_ms, saatler, side='left')
    k_guvenli = np.minimum(k, len(s) - 1)
    var = (k < len(s)) & (s.acilis_ms[k_guvenli] == saatler)
    return np.where(var, s.hacim[k_guvenli], 0.0)


def medyan_saatlik_hacim(s: SaatlikSeri, t_ms: int, gun: int) -> float:
    """V1h30 / V1h7: son `gun` gunun medyan saatlik quote hacmi (MIMARI Ss3.7)."""
    h = saatlik_hacim_dizisi(s, t_ms - gun * GUN_MS, t_ms)
    return float(np.median(h)) if len(h) else 0.0


def sigma_1h(s: SaatlikSeri, t_ms: int, gun: int) -> float:
    """Son `gun` gunun saatlik log getiri std'si (ddof=0); yalniz ardisik iki saatin barlari varsa getiri
    tanimlidir. Ikiden az getiri varsa nan (stres olcutu tetiklenmez)."""
    alt = int(np.searchsorted(s.acilis_ms, t_ms - gun * GUN_MS, side='left'))
    ust = int(np.searchsorted(s.acilis_ms, t_ms - SAAT_MS, side='right'))
    ms = s.acilis_ms[alt:ust]
    kap = s.kapanis[alt:ust]
    if len(ms) < 3:
        return float('nan')
    ardisik = np.diff(ms) == SAAT_MS
    r = np.log(kap[1:] / kap[:-1])[ardisik]
    if len(r) < 2:
        return float('nan')
    return float(np.std(r))


def borsa_bosluk_saati_mi(g: PiyasaGorunumu, h_ms: int, p_oran: float, ref_ms=None) -> bool:
    """MIMARI Ss2.6: h-1'de bari olan aday listenin >= %50'sinde h'de bar yoksa h borsa capi bosluktur.
    ref_ms: referans saat (varsayilan h-1h; cok saatlik kesintide bosluk_saatleri son temiz saati verir).
    h'deki bar h+1h'de kapanir; bu yuzden h + 1h <= g.t_ms olmali."""
    if h_ms + SAAT_MS > g.t_ms:
        raise GorunumGirdiHatasi("h saatinin bari gorunumde henuz kapanmadi")
    ref = h_ms - SAAT_MS if ref_ms is None else ref_ms
    once = 0
    yok = 0
    for coin in g.adaylar:
        s = g.barlar.get(coin)
        if s is None:
            continue
        if bar_indeksi(s, ref) is None:
            continue
        once += 1
        if bar_indeksi(s, h_ms) is None:
            yok += 1
    return once > 0 and yok >= p_oran * once


BOSLUK_GERI_BAKIS_MS = GUN_MS
BILINMIYOR = object()   # bosluk_taramasi: tarama basindaki kesinti durumu bilinmiyor (geri bakisla kurulur)


def bosluk_taramasi(g: PiyasaGorunumu, bas_ms: int, bit_ms: int, p_oran: float, bas_ref=BILINMIYOR) -> tuple:
    """[bas, bit) icindeki borsa capi bosluk saatleri ve tarama sonundaki kesinti durumu: (kume, ref_son).

    Yorum (tanim boslugu; Codex 2026-09-28 K7 ile kabul): "h-1'de bari olan" referansi cok saatlik bir kesintide
    ikinci saatten itibaren bos kume olur ve kesinti yalniz ilk saatinde bosluk sayilirdi. Bu yuzden kesinti
    surerken referans, kesintiden onceki son bosluk-disi saatte sabit tutulur. Durum sirali oldugu icin
    taramanin basindaki durum verilir: bas_ref None = bas'ta kesinti yok; int = surmekte olan kesintinin
    referans saati (onceki taramanin ref_son'u; karar kaydinda tasinir); BILINMIYOR = bas'tan 24 saat geriden
    kurulur (yalniz durum kaydi yoksa). ref_son: son taranan saat bosluksa referans saati, degilse None.
    Dis bayrak modunda verilen kume kullanilir ve yeniden turetilmez (MIMARI Ss5.1)."""
    if g.dis_bayraklar is not None and getattr(g.dis_bayraklar, 'bosluk_saatleri', None) is not None:
        return frozenset(h for h in g.dis_bayraklar.bosluk_saatleri if bas_ms <= h < bit_ms), None
    bit = min(bit_ms, g.t_ms - SAAT_MS + 1)
    if bas_ref is BILINMIYOR:
        tarama_bas, ref = bas_ms - BOSLUK_GERI_BAKIS_MS, None
    else:
        tarama_bas, ref = bas_ms, bas_ref
    sonuc = set()
    if tarama_bas >= bit:
        return frozenset(sonuc), ref
    # borsa_bosluk_saati_mi ile ayni tanim, vektor hali: adaylar x saatler varlik matrisi (hiz; sonuc ayni).
    saatler = np.arange(tarama_bas - SAAT_MS, bit, SAAT_MS, dtype=np.int64)   # sutun 0 = ilk saatin h-1'i
    seriler = [g.barlar[c] for c in g.adaylar if c in g.barlar]
    if not seriler:
        return frozenset(sonuc), None
    var = np.array([saat_indeksleri(s, saatler) >= 0 for s in seriler], dtype=bool)
    ek_ref = {}
    if ref is not None and not (saatler[0] <= ref < bit):
        ek_ref[ref] = np.array([bar_indeksi(s, ref) is not None for s in seriler], dtype=bool)
    for j in range(1, len(saatler)):
        h = int(saatler[j])
        r = h - SAAT_MS if ref is None else ref
        onceki = ek_ref[r] if r in ek_ref else var[:, (r - int(saatler[0])) // SAAT_MS]
        once = int(onceki.sum())
        yok = int((onceki & ~var[:, j]).sum())
        if once > 0 and yok >= p_oran * once:
            ref = r
            if h >= bas_ms:
                sonuc.add(h)
        else:
            ref = None
    return frozenset(sonuc), ref


def bosluk_saatleri(g: PiyasaGorunumu, bas_ms: int, bit_ms: int, p_oran: float, bas_ref=BILINMIYOR) -> frozenset:
    """bosluk_taramasi'nin yalniz kume ciktisi."""
    return bosluk_taramasi(g, bas_ms, bit_ms, p_oran, bas_ref)[0]


def veri_baslangici_ms(g: PiyasaGorunumu):
    """Gorunumdeki en erken bar acilisi (ilk karar icin gecmisin basi); bar yoksa None."""
    ilkler = [int(s.acilis_ms[0]) for s in g.barlar.values() if len(s)]
    return min(ilkler) if ilkler else None
