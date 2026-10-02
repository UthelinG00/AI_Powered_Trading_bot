"""hedef_agirlik: gorunum + durum -> kaldiracli, tavanlardan gecmis net hedef kitap (saf). MIMARI Ss5.1,
Ss3.1-Ss3.5, Ss2.5(d), Ss2.6 (reduce-only), T4-a / T4-d denetimleri. Yalniz Mimari A; carry Slice 3'tedir.

Ag, dosya, config veya durum erisimi yoktur. Siralama deterministiktir: evren sirasi (BTC, ETH, altlar
alt-sirasiyla), sonra evren disi coinler alfabetik.

Yorumlar (belgenin acik birakmadigi, spesifikasyonu genisletmeyen secimler):
- "Islem disi" coin (gunluk kapanisi yok ya da Ss2.5(d)) tavan cozucusune mevcut agirligiyla SABIT girer;
  kucultmeler yalniz serbest isimlere uygulanir (tavanlar.tavan_coz sabit_mi).
- Reduce-only rejiminde (borsa capi bosluk) serbest isimler |w_yeni| <= |w_eski|, isaret korunur ya da 0.
- Karar aninda V60 < 20M olan coinde (aylik secimler arasinda hacim tabanin altina dusen uye) ayni "yalniz
  azaltma" kirpmasi uygulanir: taban giris ve kalis icindir (Ss2.3), <20M maliyet dilimi yalniz cikista
  tanimlidir (Ss6.1). Cikis aylik secimi beklemez ama zorlanmaz da; hedef sinyalden gelir (Codex K13).
- T4-d toplam risk kurali: V(w*) <= L*tau (A). Ihlalde serbest isimler tek katsayiyla kuculur; katsayi V'nin
  dis bukeyliginden (sabit kisim V0, simdiki V1). Sabit isim yoksa katsayi lim/V1'dir ("tek katsayi").
- Sabit (islem disi) isimler bir tavani ya da T4-d'yi asiyorsa ihlal teknik hata sayilmaz: islem disi coinde
  emir yasaktir (Ss3.1), ihlal piyasa kaynaklidir; teknik hata kosuyu piyasa verisi yuzunden durdururdu. Toplam
  tavanlarda (brut, S1, S2, T4-d) serbest isimler sinira ya da 0'a kadar kuculur; sabit ismin kendi isim tavani
  asimi baska isimleri etkilemez. Tanilara 'sabit_tavan_ihlali' / 'sabit_t4d_ihlali' yazilir ve raporlanir.
  Kullanici karari K8 (2026-09-28) ile MIMARI Ss3.5'e istisna olarak yazildi.
- Getiri (sigma, korelasyon) islem disi gunlerde eksiktir: maske kaydindaki (d) gunlerinin kapanisi getiriye
  girmez (Ss3.2 KC-13; Codex K12). Sinyaldeki gecmis fiyat kurali (Ss3.1) yalniz eksik/maskeli gunu dislar.
"""
import math
from dataclasses import dataclass

import numpy as np

from .boyutlama import birim_kitap
from .durum import StratejiDurumu, nav_hesapla
from .gorunum import (BILINMIYOR, GUN_MS, SAAT_MS, PiyasaGorunumu, bar_indeksi, bosluk_taramasi, gun_takvimi,
                      gunluk_kapanislar, ilk_bar_ms, son_kapanis, v60, veri_baslangici_ms)
from .hijyen import MaskeKaydi, gunluk_hijyen
from .risk import kovaryans_hazirla, sigma_ewma_tahmin
from .sinyal import trend_sinyali
from .tavanlar import _dis_bukey_katsayi, tavan_coz
from .tipler import Parametreler


class HedefHatasi(ValueError):
    """Teknik hata: NAV <= 0, T4-a/T4-d degismezi olcekleme sonrasi ihlal, eksik fiyat."""


@dataclass(frozen=True)
class CoinGunluk:
    """Ortak gun takvimine hizali gunluk veriler (MIMARI Ss3.2 KC-13: eksik getiri nan, 0 yazilmaz)."""
    kapanislar: np.ndarray
    gecerli: np.ndarray       # kapanis var ve o gun maskesiz
    getiriler: np.ndarray     # r_d = ln(P_d/P_{d-1}); iki ardisik gecerli kapanis yoksa nan
    sigma_ewma: float         # tabansiz sigma_EWMA (maliyet sigma_d icin); gozlem yoksa nan
    gun_gecerli: np.ndarray = None   # kapanis var, maskesiz, islem disi degil (getiri ve HAR RV gun kumesi)


def coin_gunluk(g: PiyasaGorunumu, coin: str, gunler: np.ndarray, maske: MaskeKaydi, p: Parametreler) -> CoinGunluk:
    s = g.barlar.get(coin)
    if s is None:
        bos = np.full(len(gunler), np.nan)
        return CoinGunluk(bos, np.zeros(len(gunler), dtype=bool), bos, float('nan'), np.zeros(len(gunler), dtype=bool))
    kap = gunluk_kapanislar(s, gunler)
    maskeli = np.array([maske.gunde_maskeli(int(d)) for d in gunler], dtype=bool) if maske.donemler else \
        np.zeros(len(gunler), dtype=bool)
    gecerli = ~np.isnan(kap) & ~maskeli
    getiri_gecerli = gecerli
    if maske.islem_disi_gunler:
        getiri_gecerli = gecerli & ~np.isin(gunler, np.asarray(maske.islem_disi_gunler, dtype=np.int64))
    getiri = np.full(len(gunler), np.nan)
    if len(gunler) > 1:
        ikisi = getiri_gecerli[1:] & getiri_gecerli[:-1]
        with np.errstate(invalid='ignore', divide='ignore'):
            r = np.log(kap[1:] / kap[:-1])
        getiri[1:] = np.where(ikisi, r, np.nan)
    sigma = sigma_ewma_tahmin(getiri, p) if np.any(~np.isnan(getiri)) else float('nan')
    return CoinGunluk(kap, gecerli, getiri, sigma, getiri_gecerli)


def boyut_sigmalari(g: PiyasaGorunumu, coinler, gunler: np.ndarray, gunluk: dict, p: Parametreler) -> tuple:
    """Boyutlama sigma vektoru (MIMARI Ss3.2): sigma_EWMA ya da (kilit adim 2 sonucu HAR ise) sigma_HAR; HAR
    tanimsizken sigma_EWMA; her durumda taban %20. Doner (sigma dizisi, HAR kullanilan coin sayisi)."""
    if p.sigma_tahmincisi not in ('EWMA', 'HAR'):
        raise HedefHatasi(f"bilinmeyen sigma tahmincisi: {p.sigma_tahmincisi}")
    if p.sigma_tahmincisi == 'HAR' and p.har_takvimi is None:
        raise HedefHatasi("sigma_tahmincisi HAR ama har_takvimi yok")
    from .har import har_sigma
    sonuc, har_n = [], 0
    for c in coinler:
        sig = gunluk[c].sigma_ewma
        if p.sigma_tahmincisi == 'HAR':
            h = har_sigma(g.barlar.get(c), gunler, gunluk[c].gun_gecerli, p.har_takvimi, p)
            if not math.isnan(h):
                sig, har_n = h, har_n + 1
        sonuc.append(p.sigma_taban if math.isnan(sig) else max(sig, p.sigma_taban))
    return np.array(sonuc), har_n


def v_norm(x: np.ndarray, sigma_hat: np.ndarray, sigma_sifir: np.ndarray) -> float:
    """V(x) = max(sqrt(x' Sigma_hat x), sqrt(x' Sigma_0 x)) (MIMARI Ss3.5)."""
    if len(x) == 0:
        return 0.0
    return max(math.sqrt(max(float(x @ sigma_hat @ x), 0.0)), math.sqrt(max(float(x @ sigma_sifir @ x), 0.0)))


@dataclass(frozen=True)
class HedefKitap:
    t_ms: int
    coinler: tuple            # hedefi tanimli butun coinler (evren + pozisyonlu + devredenli), deterministik sira
    w_yildiz: dict            # coin -> nihai hedef (kaldiracli, tavan + T4-d sonrasi, bant oncesi)
    w_birim: dict             # A_t coin -> w^u (T4-a nesnesi)
    w_mevcut: dict            # coin -> w0 = q * fiyat_ref / nav
    fiyat_ref: dict           # coin -> karar anindaki son 1h kapanis
    nav: float
    a_t: tuple
    sabit: tuple              # islem disi (mevcut agirlikta sabit, yeni emir yok)
    maskeli: tuple
    reduce_only: bool
    baglayan: tuple           # bu karar bagladigi tavanlar
    tanilar: dict
    carry: object = None      # Mimari B: carry durumu ve sanal bacaklar (hedef_b); A'da None. B'de trend bandi
                              # hedefin icindedir (MIMARI Ss4.5 adim 5), w_yildiz bant sonrasidir.

    def json(self) -> dict:
        d = {'t_ms': self.t_ms, 'coinler': list(self.coinler), 'w_yildiz': self.w_yildiz,
             'w_birim': self.w_birim, 'w_mevcut': self.w_mevcut, 'fiyat_ref': self.fiyat_ref, 'nav': self.nav,
             'a_t': list(self.a_t), 'sabit': list(self.sabit), 'maskeli': list(self.maskeli),
             'reduce_only': self.reduce_only, 'baglayan': list(self.baglayan), 'tanilar': self.tanilar}
        if self.carry is not None:
            d['carry'] = self.carry
        return d


@dataclass(frozen=True)
class KararGirdileri:
    """hedef_agirlik'in ara hesaplari; karar adimi (bant/lot/maliyet baglami) ayni sayilari yeniden kullanir."""
    gunluk: dict              # coin -> CoinGunluk
    bosluklar: frozenset
    islem_disi: dict          # coin -> bool
    k_coinler: tuple          # kovaryans matrisinin coinleri (A_t + sifir-disi sabitler)
    sigma_hat: np.ndarray     # K uzerinde Sigma_hat
    sigma_sifir: np.ndarray


def isim_tavani(coin: str, isaret: float, p: Parametreler) -> float:
    if coin in (p.btc, p.eth):
        return p.isim_tavan_btc_eth
    return p.isim_tavan_alt_long if isaret > 0 else p.isim_tavan_alt_short


def karar_bosluklari(g: PiyasaGorunumu, durum: StratejiDurumu, p: Parametreler) -> tuple:
    """Kararin borsa capi bosluk taramasi: (kume, ref_son). Son islenen gunden (maske_ms) t'ye, kaydedilmis
    kesinti durumuyla (bosluk_ref) surer; ilk kararda verinin basindan taranir (Codex K4, K7). Onceki kararlarin
    kaydettigi son gunlerin bosluk saatleri (bosluk_gecmis) kumeye eklenir: (c)'nin 16 saatlik penceresi gun
    sinirini asabilir (Codex K10)."""
    if durum.maske_ms is not None:
        yeni, ref = bosluk_taramasi(g, durum.maske_ms, g.t_ms, p.borsa_bosluk_oran, durum.bosluk_ref)
        return frozenset(durum.bosluk_gecmis) | yeni, ref
    bas = veri_baslangici_ms(g)
    if bas is None:
        return frozenset(), None
    return bosluk_taramasi(g, min(bas, g.t_ms - GUN_MS), g.t_ms, p.borsa_bosluk_oran,
                           None if bas <= g.t_ms - GUN_MS else BILINMIYOR)


def _coin_sirasi(durum: StratejiDurumu) -> tuple:
    diger = sorted((set(k for k, q in durum.pozisyonlar.items() if q != 0.0) | set(durum.devreden))
                   - set(durum.evren))
    return tuple(durum.evren) + tuple(diger)


def hedef_agirlik_ayrintili(g: PiyasaGorunumu, durum: StratejiDurumu, L: float, p: Parametreler,
                            bosluklar=None) -> tuple:
    """(HedefKitap, KararGirdileri). durum'un evren ve maske alanlari bugune guncellenmis olmalidir.
    bosluklar: karar_bosluklari(...)[0] (karar adimi bir kez hesaplar); None ise burada hesaplanir.
    p.mimari == 'B' ise Mimari B yolu (hedef_b.py); A yolu aynen asagidadir."""
    if p.mimari == 'B':
        from .hedef_b import hedef_b
        return hedef_b(g, durum, L, p, bosluklar=bosluklar)
    if p.mimari != 'A':
        raise HedefHatasi(f"bilinmeyen mimari: {p.mimari}")
    t = g.t_ms
    if t % GUN_MS != 0:
        raise HedefHatasi("gunluk karar yalniz 00:00 UTC'de verilir")
    nav = nav_hesapla(durum, g)
    if not nav > 0:
        raise HedefHatasi(f"NAV <= 0: {nav}")

    bas = durum.son_karar_ms if durum.son_karar_ms is not None else t - GUN_MS
    if bosluklar is None:
        bosluklar = karar_bosluklari(g, durum, p)[0]
    reduce_only = any(bas <= h < t for h in bosluklar)

    coinler = _coin_sirasi(durum)
    ilkler = [ilk_bar_ms(g.barlar[c]) for c in coinler if c in g.barlar]
    gunler = gun_takvimi(min(ilkler) + SAAT_MS, t) if ilkler else np.array([t], dtype=np.int64)

    gunluk, islem_disi, w0, fiyat_ref, maskeli, taban_alti = {}, {}, {}, {}, {}, {}
    for c in coinler:
        s = g.barlar.get(c)
        m = durum.maske.get(c, MaskeKaydi())
        maskeli[c] = m.maskeli
        gunluk[c] = coin_gunluk(g, c, gunler, m, p)
        hij = gunluk_hijyen(g, c, t, bosluklar, p)
        islem_disi[c] = s is None or bar_indeksi(s, t - SAAT_MS) is None or hij.d
        fr = son_kapanis(s, t) if s is not None else None
        q = durum.pozisyonlar.get(c, 0.0)
        if fr is None:
            if q != 0.0:
                raise HedefHatasi(f"pozisyonlu coinin fiyati yok: {c}")
            fr = 0.0
        fiyat_ref[c] = fr
        w0[c] = q * fr / nav if q != 0.0 else 0.0
        taban_alti[c] = s is not None and v60(s, t, p.v60_gun) < p.hacim_taban_v60

    evren = set(durum.evren)
    a_t = tuple(c for c in coinler if c in evren and not islem_disi[c] and not maskeli[c])
    sabit = tuple(c for c in coinler if islem_disi[c])
    k_coinler = a_t + tuple(c for c in sabit if w0[c] != 0.0)

    tanilar = {'n_t': len(a_t), 'bosluk_saat_sayisi': len(bosluklar)}
    if k_coinler:
        sigma_k, har_n = boyut_sigmalari(g, k_coinler, gunler, gunluk, p)
        if p.sigma_tahmincisi == 'HAR':
            tanilar['har_sigma_sayisi'] = har_n
        kov = kovaryans_hazirla([gunluk[c].getiriler for c in k_coinler], sigma_k, p)
        sigma_hat_k, sigma_sifir_k = kov.sigma_hat, kov.sigma_sifir
        tanilar.update({'psd_kirpilan': kov.kirpilan_ozdeger_sayisi, 'psd_frobenius': kov.frobenius_duzeltme})
    else:
        sigma_k = np.array([])
        sigma_hat_k = sigma_sifir_k = np.zeros((0, 0))

    w_birim = {}
    if a_t:
        ia = np.arange(len(a_t))
        s_vek = np.array([trend_sinyali(gunluk[c].kapanislar, gunluk[c].gecerli,
                                        0.0 if math.isnan(gunluk[c].sigma_ewma) else gunluk[c].sigma_ewma, p)
                          for c in a_t])
        r_hat_a = kov.r_hat[np.ix_(ia, ia)]
        bk = birim_kitap(s_vek, sigma_k[ia], r_hat_a, sigma_hat_k[np.ix_(ia, ia)], sigma_sifir_k[np.ix_(ia, ia)], p)
        if bk.v_sonrasi > p.tau * (1 + 1e-9):
            raise HedefHatasi("T4-a: guvenlik olceklemesi sonrasi V(w^u) > tau (teknik hata)")
        w_birim = {c: float(bk.w_u[i]) for i, c in enumerate(a_t)}
        tanilar.update({'sinyal': {c: float(s_vek[i]) for i, c in enumerate(a_t)}, 'm': bk.m, 'm_tilde': bk.m_tilde,
                        'k': bk.k, 'v_birim': bk.v_sonrasi, 't4a_olcekleme': bk.guvenlik_olceklemesi_uygulandi})

    # Kaldirac ve tavanlar (MIMARI Ss3.4-Ss3.5).
    w_ham = np.array([L * w_birim[c] if c in w_birim else (w0[c] if islem_disi[c] else 0.0) for c in coinler])
    btc_eth = np.array([c in (p.btc, p.eth) for c in coinler], dtype=bool)
    sabit_mi = np.array([islem_disi[c] for c in coinler], dtype=bool)
    baglayan = []
    if len(coinler):
        ts = tavan_coz(w_ham, btc_eth, p, sabit_mi=sabit_mi)
        w = ts.w.copy()
        if ts.isim_kirpildi.any():
            baglayan.append('isim')
        for ad, katsayi in (('brut', ts.brut_katsayi), ('S1', ts.s1_katsayi), ('S2', ts.s2_katsayi),
                            ('global', ts.global_katsayi)):
            if katsayi < 1.0:
                baglayan.append(ad)
        tanilar.update({'s1_kayip': ts.s1_kayip_son, 's2_kayip': ts.s2_kayip_son, 'sabit_tavan_ihlali': ts.sabit_ihlal})
    else:
        w = np.array([])

    # Reduce-only rejimi (MIMARI Ss2.6) ve hacim tabani alti coin (Ss2.3/Ss6.1): yalniz azaltma.
    for i, c in enumerate(coinler):
        if not sabit_mi[i] and (reduce_only or taban_alti[c]):
            eski = w0[c]
            if eski == 0.0 or w[i] * eski <= 0:
                w[i] = 0.0
            else:
                w[i] = math.copysign(min(abs(w[i]), abs(eski)), eski)
    tanilar['hacim_tabani_alti'] = sorted(c for c in coinler if taban_alti[c] and not islem_disi[c])

    # T4-d toplam risk kurali: V(w*) <= L*tau (A).
    lim = L * p.tau
    idx_k = [coinler.index(c) for c in k_coinler]
    x1 = w[idx_k] if idx_k else np.array([])
    v1 = v_norm(x1, sigma_hat_k, sigma_sifir_k)
    if v1 > lim * (1 + 1e-12):
        x0 = np.where(sabit_mi[idx_k], x1, 0.0)
        c_t4 = _dis_bukey_katsayi(lim, v_norm(x0, sigma_hat_k, sigma_sifir_k), v1)
        w = np.where(sabit_mi, w, w * c_t4)
        baglayan.append('T4d')
        x1 = w[idx_k]
        v1 = v_norm(x1, sigma_hat_k, sigma_sifir_k)
        if v1 > lim * (1 + 1e-9):
            if not sabit_mi.any():
                raise HedefHatasi("T4-d: olcekleme sonrasi toplam risk kurali ihlali (teknik hata)")
            tanilar['sabit_t4d_ihlali'] = True
    tanilar['v_net'] = v1

    hedef = HedefKitap(
        t_ms=t, coinler=coinler, w_yildiz={c: float(w[i]) for i, c in enumerate(coinler)}, w_birim=w_birim,
        w_mevcut=w0, fiyat_ref=fiyat_ref, nav=nav, a_t=a_t, sabit=sabit,
        maskeli=tuple(c for c in coinler if maskeli[c]), reduce_only=reduce_only, baglayan=tuple(baglayan),
        tanilar=tanilar)
    girdiler = KararGirdileri(gunluk=gunluk, bosluklar=bosluklar, islem_disi=islem_disi, k_coinler=k_coinler,
                              sigma_hat=sigma_hat_k, sigma_sifir=sigma_sifir_k)
    return hedef, girdiler


def hedef_agirlik(g: PiyasaGorunumu, durum: StratejiDurumu, L: float, p: Parametreler) -> HedefKitap:
    """MIMARI Ss5.1 imzasi."""
    return hedef_agirlik_ayrintili(g, durum, L, p)[0]
