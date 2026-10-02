"""Geri test adaptoru: saatlik olay dongusu (MIMARI Ss5.2, Ss5.5, Ss1c, Ss6.4). Mimari A.

Ag, config ya da .env erisimi yoktur; veri cagirandan `TamVeri` olarak gelir. Her saat siniri T icin:
  1. Funding: T damgali gercek uzlasmalar, ters kayitlar ve dolgular, q(T-) ile.
  2. T = 00:00 ise: delist uzlasmasi (30 gun islem gormeyen pozisyon), sonra karar_ver; kayitlar gunluge.
     00:00'da dolum yoktur.
  3. T != 00:00 ise: T-1h saati borsa capi bosluksa devreden emirlerin risk artiran parcalari iptal edilir
     (MIMARI Ss2.6, Ss5.4; Codex K5); sonra devreden emirler T'de acilan barin acilisinda doldurulur.
  4. Degerleme: barin kapanisinda (T+1h) NAV = nakit + sum q * son kapanis. Gun kapanisinda 'nav' kaydi.
Durum, gunluge yazilan her kayit ayni `kayit_uygula` indirgeyicisiyle artimsal guncellenir; gunluk tek yetkili
kayittir ve `durum_turet` ile ayni durum yeniden kurulur. Ayni veri + Parametreler + ayarlar ayni gunlugu
(ayni son hash'i) uretir.
"""
from dataclasses import dataclass, field, replace

import numpy as np

from .durum import StratejiDurumu, kayit_uygula
from .emir import artiran_iptali, filtre_al, saat_dolumu
from .funding import funding_saati
from .gorunum import (GUN_MS, SAAT_MS, TamVeri, bar_indeksi, bosluk_taramasi, gorunum_kur, son_islem_goren_bar_ms,
                      son_kapanis)
from .gunluk import OlayGunlugu
from .karar import karar_ver
from .tipler import Parametreler


class GeriTestHatasi(ValueError):
    """Gecersiz kosu ayari (t0 gun basi degil, t_son < t0, nav0 <= 0)."""


@dataclass(frozen=True)
class KosuAyarlari:
    t0_ms: int                     # ilk karar (00:00 UTC); D'de T0 = 2023-10-01
    t_son_ms: int                  # son islenen saat siniri (dahil)
    L: float = 1.0                 # Kelly adayi kaldirac (MIMARI Ss3.4)
    maliyet_k: float = 1.0         # maliyet carpani k in {1,2,3}; her k ayri tam kosu (MIMARI Ss6.2)
    nav0: float = 100_000.0        # birincil NAV 0,1M (ACIK_SORU_YANITLARI soru 4)
    katilimsiz: bool = False       # golge yol: Q_max = sonsuz (MIMARI Ss6.4)
    filtreler: dict = field(default_factory=dict)  # coin -> (adim, minNotional)


@dataclass
class KosuSonucu:
    gunluk: OlayGunlugu
    durum: StratejiDurumu
    nav_ms: np.ndarray             # bar kapanis damgalari
    nav: np.ndarray                # saatlik NAV
    kararlar: list                 # KararSonucu listesi (tani ve parite testleri icin)


class _Kosucu:
    def __init__(self, veri: TamVeri, ayar: KosuAyarlari, p: Parametreler):
        self.veri, self.ayar, self.p = veri, ayar, p
        self.gunluk = OlayGunlugu()
        self.durum = StratejiDurumu()
        self.gecmis: dict = {}   # coin -> [(damga, q_sonrasi)] (funding q(h-) icin)
        self.bosluk_tarandi = None   # gun ici bosluk taramasinin ulastigi saat (haric) ve oradaki kesinti durumu
        self.bosluk_ref = None

    def yaz(self, tur, damga, coin=None, miktar=None, fiyat=None, karar_ms=None, veri=None):
        k = self.gunluk.ekle(tur, damga, coin=coin, miktar=miktar, fiyat=fiyat, karar_ms=karar_ms, veri=veri)
        self.durum = kayit_uygula(self.durum, k)
        if tur in ('dolum', 'uzlasma') or (tur == 'duzeltme' and miktar):
            self.gecmis.setdefault(coin, []).append((damga, self.durum.pozisyonlar.get(coin, 0.0)))
        return k

    def funding_adimi(self, g, T):
        # Pozisyonu, bekleyen dolgusu ya da gec kayit penceresi icinde pozisyon degisikligi olan her coin
        # (kapanmis pozisyonun eksik ya da gec gelen funding'i de yazilir; Codex K1, K3).
        d = self.durum
        pencere_bas = T - self.p.funding_gec_kayit_gun * GUN_MS
        coinler = set(d.pozisyonlar) | set(d.funding_dolgu)
        coinler |= {c for c, gec in self.gecmis.items() if gec[-1][0] >= pencere_bas}
        for c in sorted(coinler):
            olaylar = funding_saati(g, c, T, self.gecmis.get(c, ()), d.funding_dolgu.get(c, ()), self.p,
                                    islenen=d.funding_islenen.get(c, ()), dolgu_kadar=d.funding_dolgu_kadar.get(c))
            for o in olaylar:
                self.yaz(o.tur, T, coin=c, veri=o.veri)

    def uzlasma_adimi(self, g, T):
        p = self.p
        for c in sorted(self.durum.pozisyonlar):
            s = g.barlar.get(c)
            son = son_islem_goren_bar_ms(s, T) if s is not None else None
            if son is None or T - (son + SAAT_MS) < p.delist_bekleme_gun * GUN_MS:
                continue
            q = self.durum.pozisyonlar[c]
            kap = son_kapanis(s, T)
            fiyat = kap * (1.0 - p.delist_h_long) if q > 0 else kap * (1.0 + p.delist_h_short)
            self.yaz('uzlasma', T, coin=c, miktar=-q, fiyat=fiyat,
                     veri={'son_kapanis': kap, 'son_islem_bar_ms': son, 'q': q})

    def karar_adimi(self, g, T):
        sonuc = karar_ver(g, replace(self.durum, t_ms=T), self.ayar.L, self.p, self.ayar.filtreler)
        for k in sonuc.kayitlar:
            self.yaz(k.tur, T, coin=k.coin, miktar=k.miktar, fiyat=k.fiyat, karar_ms=T, veri=k.veri)
        self.bosluk_tarandi, self.bosluk_ref = T, self.durum.bosluk_ref
        return sonuc

    def bosluk_iptal_adimi(self, g, T):
        """Gun ici: T-1h saati (T'de kapanan bar) borsa capi bosluksa devreden emirlerin risk artiran parcalari
        iptal edilir; azaltan parcalar korunur (MIMARI Ss2.6, Ss5.4). Tarama karardaki kesinti durumundan
        saat saat surer (karar_bosluklari ile ayni sirali tanim)."""
        if self.bosluk_tarandi is None:
            return
        kume, self.bosluk_ref = bosluk_taramasi(g, self.bosluk_tarandi, T, self.p.borsa_bosluk_oran, self.bosluk_ref)
        self.bosluk_tarandi = T
        if T - SAAT_MS not in kume:
            return
        for c in sorted(self.durum.devreden):
            iptal = artiran_iptali(self.durum.devreden[c].kalan, self.durum.pozisyonlar.get(c, 0.0), 'borsa_bosluk')
            if iptal is not None:
                self.yaz('devreden_iptal', T, coin=c, veri=iptal)

    def dolum_adimi(self, T):
        p, veri = self.p, self.veri
        btc = veri.barlar.get(p.btc)
        kb = bar_indeksi(btc, T) if btc is not None else None
        btc_ln_hl = float(abs(np.log(btc.yuksek[kb] / btc.dusuk[kb]))) if kb is not None and btc.dusuk[kb] > 0 else 0.0
        for c in sorted(self.durum.devreden):
            e = self.durum.devreden[c]
            s = veri.barlar.get(c)
            k = bar_indeksi(s, T) if s is not None else None
            k_once = bar_indeksi(s, T - SAAT_MS) if s is not None else None
            bar = None if k is None else (float(s.acilis[k]), float(s.yuksek[k]), float(s.dusuk[k]), float(s.hacim[k]))
            onceki_hacim = float(s.hacim[k_once]) if k_once is not None else 0.0
            adim, min_not = filtre_al(self.ayar.filtreler, c, p)
            q = self.durum.pozisyonlar.get(c, 0.0)
            d = saat_dolumu(e, q, bar, onceki_hacim, btc_ln_hl, self.ayar.maliyet_k, adim, min_not, p,
                            katilimsiz=self.ayar.katilimsiz)
            if d.miktar != 0.0:
                self.yaz('dolum', T, coin=c, miktar=d.miktar, fiyat=d.fiyat, karar_ms=e.karar_ms,
                         veri={'maliyet_bps': d.maliyet_bps, 'q_max': d.q_max if np.isfinite(d.q_max) else -1.0,
                               'tam_kapanis_son': d.tam_kapanis_son, 'sebep': d.sebep})
            elif d.tam_kapanis_son:
                self.yaz('devreden_iptal', T, coin=c, veri={'iptal': e.kalan, 'tamami': True, 'sebep': 'pozisyon_0'})

    def nav_adimi(self, T_kapanis):
        toplam = self.durum.nakit
        for c, q in self.durum.pozisyonlar.items():
            fiyat = son_kapanis(self.veri.barlar[c], T_kapanis)
            toplam += q * fiyat
        return toplam


def kos(veri: TamVeri, ayar: KosuAyarlari, p: Parametreler) -> KosuSonucu:
    if ayar.t0_ms % GUN_MS != 0:
        raise GeriTestHatasi("t0 00:00 UTC olmali")
    if ayar.t_son_ms < ayar.t0_ms or ayar.t_son_ms % SAAT_MS != 0:
        raise GeriTestHatasi("t_son >= t0 ve saat izgarasinda olmali")
    if not ayar.nav0 > 0:
        raise GeriTestHatasi("nav0 > 0 olmali")
    k = _Kosucu(veri, ayar, p)
    k.yaz('baslangic', ayar.t0_ms, veri={'nav0': ayar.nav0, 'L': ayar.L, 'maliyet_k': ayar.maliyet_k,
                                         'katilimsiz': ayar.katilimsiz})
    nav_ms, navlar, kararlar = [], [], []
    for T in range(ayar.t0_ms, ayar.t_son_ms + 1, SAAT_MS):
        g = gorunum_kur(veri, T)
        k.funding_adimi(g, T)
        if T % GUN_MS == 0:
            k.uzlasma_adimi(g, T)
            kararlar.append(k.karar_adimi(g, T))
        else:
            k.bosluk_iptal_adimi(g, T)
            k.dolum_adimi(T)
        nav = k.nav_adimi(T + SAAT_MS)
        nav_ms.append(T + SAAT_MS)
        navlar.append(nav)
        if (T + SAAT_MS) % GUN_MS == 0:
            k.yaz('nav', T + SAAT_MS, veri={'nav': nav})
    return KosuSonucu(gunluk=k.gunluk, durum=k.durum, nav_ms=np.array(nav_ms, dtype=np.int64),
                      nav=np.array(navlar), kararlar=kararlar)
