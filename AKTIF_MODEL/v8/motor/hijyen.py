"""Veri hijyeni: donma/delist/coine ozgu bosluk olcutleri ve maske durumu (saf). MIMARI Ss2.5, Ss2.6, Ss1c.

Ag, dosya, config veya durum erisimi yoktur. Olcutler gunluk, yalniz t'ye kadar kapanmis verilerle
hesaplanir. Belgenin acik birakmadigi pencere secimleri (yorum; spesifikasyonu genisletmez, daraltmaz):
- Borsa capi bosluk saatleri donma sayaclarina girmez (MIMARI Ss2.6 "Donma sayaclari bosluk saatlerini
  saymaz"): (b)'de seriyi ne artirir ne sifirlar, (c)'nin 16 saati bosluk disi saatlerle sayilir, (d)'de eksik
  saat sayilmaz. `bosluklar` cagirandan gelir ve pencereleri kapsamalidir (kararda tam tarama).
- (b): son gune degen (en az bir bari [t-24h, t) icinde olan) >= 6 ardisik bosluk-disi bar; seri gece yarisini
  ve bosluk saatlerini asabilir (Codex K11). Pencere t-24h'den geriye 5 bosluk-disi saat uzar.
- (d): son gunun [t-24h, t) toplam eksik saati > 8 (Codex K11 ile degisti; onceki yorum "en uzun ardisik"
  olcutu daraltiyordu). Coinin ilk barindan onceki saatler eksik sayilmaz.
- (a) coinin >= 90 gunluk gecmisi yoksa degerlendirilmez (isinmadaki coin zaten evrende degildir).
- (c) "bar akisi suruyor" = son 16 bosluk-disi saatte hacmi > 0 en az bir bar var.
- (d) gunleri maske kaydinda tutulur: o gunun kapanisi getiri hesabina girmez (MIMARI Ss3.2 "islem disi gun").
- "Temiz gun" = (a)-(d)'nin hicbiri tetiklenmedi.
"""
from dataclasses import dataclass, replace

import numpy as np

from .gorunum import (GUN_MS, SAAT_MS, PiyasaGorunumu, SaatlikSeri, aylik_secim_gunu_mu, gunluk_hacimler,
                      ilk_bar_ms, saat_indeksleri, son_gunler)
from .tipler import Parametreler


@dataclass(frozen=True)
class HijyenBayraklari:
    a: bool = False   # hacim cokusu (7g medyan < 90g medyanin %10'u)
    b: bool = False   # >= 6 ardisik sifir-hacim ya da O=H=L=C bar
    c: bool = False   # bar akisi surerken son 16 saatte gercek funding kaydi yok
    d: bool = False   # son gunde > 8 saat bar boslugu (islem disi; maske degil)

    @property
    def maske_tetik(self) -> bool:
        return self.a or self.b or self.c

    @property
    def temiz(self) -> bool:
        return not (self.a or self.b or self.c or self.d)


@dataclass(frozen=True)
class DisBayraklar:
    """MIMARI Ss5.1 dis bayrak modu (K1-14 kancasi). Verilen alanlar yeniden turetilmez.
    hijyen: {(coin, gun_ms): HijyenBayraklari}; bosluk_saatleri: borsa capi bosluk saatleri kumesi."""
    hijyen: dict = None
    bosluk_saatleri: frozenset = None


def _olcut_a(s: SaatlikSeri, t_ms: int, p: Parametreler) -> bool:
    ilk = ilk_bar_ms(s)
    if ilk is None or ilk > t_ms - p.donma_a_uzun_gun * GUN_MS:
        return False
    kisa = gunluk_hacimler(s, son_gunler(t_ms, p.donma_a_kisa_gun))
    uzun = gunluk_hacimler(s, son_gunler(t_ms, p.donma_a_uzun_gun))
    medyan_uzun = float(np.median(uzun))
    return medyan_uzun > 0 and float(np.median(kisa)) < p.donma_a_oran * medyan_uzun


def _b_baslangici(t_ms: int, bosluklar: frozenset, p: Parametreler) -> int:
    """t-24h'den geriye (n-1) bosluk-disi saat; n barlik bir seri boylece son gune degmek zorundadir."""
    h, sayac = t_ms - GUN_MS, 0
    alt_sinir = t_ms - p.bosluk_gecmis_gun * GUN_MS
    while sayac < p.donma_b_ardisik_bar - 1 and h > alt_sinir:
        h -= SAAT_MS
        if h not in bosluklar:
            sayac += 1
    return h


def _olcut_b(s: SaatlikSeri, t_ms: int, bosluklar: frozenset, p: Parametreler) -> bool:
    saatler = [h for h in range(_b_baslangici(t_ms, bosluklar, p), t_ms, SAAT_MS) if h not in bosluklar]
    k = saat_indeksleri(s, saatler)
    kg = np.maximum(k, 0)
    duz = (k >= 0) & ((s.hacim[kg] == 0) | ((s.acilis[kg] == s.yuksek[kg]) & (s.yuksek[kg] == s.dusuk[kg])
                                          & (s.dusuk[kg] == s.kapanis[kg])))
    seri = 0
    for d in duz:
        seri = seri + 1 if d else 0
        if seri >= p.donma_b_ardisik_bar:
            return True
    return False


def _c_penceresi(t_ms: int, bosluklar: frozenset, p: Parametreler) -> list:
    """(c) penceresi: t'den geriye son `donma_c_saat` bosluk-disi saat (en fazla bosluk_gecmis_gun geri; karar
    kaydi ayni sureyi tasir, boylece ilk kurulum ve gunluk ilerleme ayni kumeyi gorur)."""
    saatler = []
    h = t_ms - SAAT_MS
    alt_sinir = t_ms - p.bosluk_gecmis_gun * GUN_MS
    while len(saatler) < p.donma_c_saat and h >= alt_sinir:
        if h not in bosluklar:
            saatler.append(h)
        h -= SAAT_MS
    return saatler


def _olcut_c(g: PiyasaGorunumu, coin: str, s: SaatlikSeri, t_ms: int, bosluklar: frozenset,
             p: Parametreler) -> bool:
    saatler = _c_penceresi(t_ms, bosluklar, p)
    if not saatler:
        return False
    bas = saatler[-1]
    k = saat_indeksleri(s, saatler)
    if not bool(np.any((k >= 0) & (s.hacim[np.maximum(k, 0)] > 0))):
        return False
    f = g.funding.get(coin)
    if f is None or len(f) == 0:
        return True
    kayit_var = bool(np.any((f.damga_ms > bas) & (f.damga_ms <= t_ms)))
    return not kayit_var


def _olcut_d(s: SaatlikSeri, t_ms: int, bosluklar: frozenset, p: Parametreler) -> bool:
    ilk = ilk_bar_ms(s)
    if ilk is None:
        return False
    saatler = [h for h in range(t_ms - GUN_MS, t_ms, SAAT_MS) if h >= ilk and h not in bosluklar]
    eksik = int((saat_indeksleri(s, saatler) < 0).sum())
    return eksik > p.donma_d_saat


def gunluk_hijyen(g: PiyasaGorunumu, coin: str, t_ms: int, bosluklar: frozenset,
                  p: Parametreler) -> HijyenBayraklari:
    """Gun siniri t_ms icin (t_ms <= g.t_ms) coinin hijyen bayraklari. Coinin hic bari yoksa bos bayrak."""
    if g.dis_bayraklar is not None and g.dis_bayraklar.hijyen is not None:
        return g.dis_bayraklar.hijyen.get((coin, t_ms), HijyenBayraklari())
    s = g.barlar.get(coin)
    if s is None or len(s) == 0 or ilk_bar_ms(s) >= t_ms:
        return HijyenBayraklari()
    return HijyenBayraklari(a=_olcut_a(s, t_ms, p), b=_olcut_b(s, t_ms, bosluklar, p),
                            c=_olcut_c(g, coin, s, t_ms, bosluklar, p), d=_olcut_d(s, t_ms, bosluklar, p))


@dataclass(frozen=True)
class MaskeKaydi:
    maskeli: bool = False
    temiz_seri: int = 0
    donemler: tuple = ()          # ((bas_ms, bit_ms|None), ...); bit None = suruyor
    islem_disi_gunler: tuple = () # (d) tetiklenen gun sinirlari (getiri hesabindan dislanir; MIMARI Ss3.2)

    def gunde_maskeli(self, gun_ms: int) -> bool:
        for bas, bit in self.donemler:
            if bas <= gun_ms and (bit is None or gun_ms < bit):
                return True
        return False


def maske_gunu_ilerle(kayit: MaskeKaydi, bayrak: HijyenBayraklari, gun_ms: int, p: Parametreler) -> MaskeKaydi:
    """Bir gunluk maske adimi (MIMARI Ss2.5). (a)-(c) tetiklenirse maske (hedef 0). Maskeden donus: aylik
    secim gunu ve >= 30 ardisik temiz gun. Aylik secim gunu burada gun_ms'ten okunur."""
    seri = kayit.temiz_seri + 1 if bayrak.temiz else 0
    if bayrak.d and gun_ms not in kayit.islem_disi_gunler:
        kayit = replace(kayit, islem_disi_gunler=kayit.islem_disi_gunler + (gun_ms,))
    if bayrak.maske_tetik:
        if kayit.maskeli:
            return replace(kayit, temiz_seri=seri)
        return replace(kayit, maskeli=True, temiz_seri=seri, donemler=kayit.donemler + ((gun_ms, None),))
    if kayit.maskeli and aylik_secim_gunu_mu(gun_ms) and seri >= p.maske_temiz_gun:
        donemler = kayit.donemler[:-1] + ((kayit.donemler[-1][0], gun_ms),)
        return replace(kayit, maskeli=False, temiz_seri=seri, donemler=donemler)
    return replace(kayit, temiz_seri=seri)


def maske_json(kayit: MaskeKaydi) -> dict:
    return {'maskeli': kayit.maskeli, 'temiz_seri': kayit.temiz_seri,
            'donemler': [[b, e] for b, e in kayit.donemler], 'islem_disi_gunler': list(kayit.islem_disi_gunler)}


def maske_jsondan(d: dict) -> MaskeKaydi:
    return MaskeKaydi(maskeli=bool(d['maskeli']), temiz_seri=int(d['temiz_seri']),
                      donemler=tuple((int(b), None if e is None else int(e)) for b, e in d['donemler']),
                      islem_disi_gunler=tuple(int(x) for x in d.get('islem_disi_gunler', ())))
