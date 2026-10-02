"""Mimari B carry uydusu (saf). MIMARI Ss4.1-Ss4.5 adim 0, Ss1d; CARRY_KAPISI Ss3.2.

Ag, dosya, config veya durum erisimi yoktur. Hesap sirasi (Pazartesi):
  adaylar (Ss4.1) -> F30, sigma^C, c (Ss4.2) -> sira-OLS notrleme -> bacaklar (Ss4.3) -> haftalik kitap Ss4.4 adim 1-7.
Her gun: hafta ici cikislar + yeniden notrleme (Ss4.4 son kisim) -> gunluk blok ve BTC hedge'i (Ss4.5 adim 0) + T4-c.
Net kitap cozucusu `net_cozucu.py`'dedir.

Belgenin acik biraktigi yerlerde yorumlar (spesifikasyonu genisletmeyen secimler; ILERLEME_SLICE3.md Y1-Y8):
- Y1 Aday ayrica V60 >= 20M ister; V60 < 20M olunca hafta ici cikar (<20M maliyet dilimi yalniz cikista, Ss6.1;
  cikis olmasa kappa'nin gunluk artisi <20M'de sanal bacak girisi yaratir ve bacak maliyeti tanimsiz kalir).
- Y2 Histerezis carry EVRENI uyeligine aittir (Codex 5. tur / B14): "mevcut" = onceki Pazartesi'nin aday listesi ya da
  q^C* != 0 isimleri; mevcut isim V30 >= 10M ile kalir, yeni isim V30 >= 20M ister. Hafta ici cikis: maske,
  V30 < 10M, V60 < 20M, bar yok.
- Y3 Bacak buyuklugu k = floor(0,30 * n_C); esit z'de alfabetik.
- Y4 Siralar ortalama sira; R30 eksikse o ismin R30 sirasi tanimli siralarin medyani (B17).
- Y5 beta_hat: son 60 gunun ortak tanimli gunluk getirileri; < 2 gozlem ya da BTC varyansi 0 ise beta_hat = 1.
- Y6 Genislik x0,5 adim 2'de (butce) uygulanir, isim tavanlarindan once.
- Y7 Pazartesi islem disi ya da bugunku kapanisi olmayan isim yeni secilmez; mevcut miktari korunur.
- Eksik funding olayi sayimi: Ss2.6 tanimi, funding.py ile ayni kural: Delta her saat h icin h'deki 30 gunluk
  pencereden hesaplanir (B1; onceki "gap basindaki Delta" yaklasimi olay kaciriyordu).
"""
import math
from dataclasses import dataclass, field

import numpy as np

from .gorunum import GUN_MS, SAAT_MS, FundingSerisi, PiyasaGorunumu, bar_indeksi, ilk_bar_ms, v60
from .tipler import Parametreler


class CarryHatasi(ValueError):
    """Teknik hata: T4-b ihlali, gecersiz girdi."""


# ---------------------------------------------------------------------------------------------------------
# Ss4.1 evren
# ---------------------------------------------------------------------------------------------------------

def v30(g: PiyasaGorunumu, coin: str, t_ms: int, p: Parametreler) -> float:
    s = g.barlar.get(coin)
    return 0.0 if s is None else v60(s, t_ms, p.carry_v30_gun)


def eksik_funding_olay_sayisi(g: PiyasaGorunumu, coin: str, t_ms: int, p: Parametreler) -> int:
    """Son 30 gunde (tespit ani (t-30g, t]) Ss2.6 eksik funding olayi sayisi. Bir boslukta (son gercek kayit a,
    sonraki kayit b) olay, h - a >= 1,5*Delta(h) ve h'de bar akisi suren ilk saat h'dir (a < h < b, h <= t);
    Delta(h) h'deki 30 gunluk pencereden (funding.funding_saati ile ayni kural)."""
    s = g.barlar.get(coin)
    f = g.funding.get(coin)
    if s is None or f is None or len(f) == 0:
        return 0
    from .funding import bar_akisi_suruyor, delta_aralik_saat
    bas = t_ms - p.funding_pencere_gun * GUN_MS
    d = f.damga_ms
    # Olay en gec bir sonraki kayittan once olusur; tespiti pencereye dusebilecek bosluklar: b > bas.
    j0 = max(int(np.searchsorted(d, bas, side='right')) - 1, 0)
    sayi = 0
    for j in range(j0, len(d)):
        a = int(d[j])
        b = int(d[j + 1]) if j + 1 < len(d) else t_ms + SAAT_MS
        h = a + SAAT_MS
        while h < b and h <= t_ms:
            if h - a >= p.funding_eksik_carpan * delta_aralik_saat(f, h, p) * SAAT_MS and bar_akisi_suruyor(s, h):
                if h > bas:
                    sayi += 1
                break
            h += SAAT_MS
    return sayi


@dataclass(frozen=True)
class AdayBilgisi:
    v30: float
    v60: float
    eksik_olay: int
    uygun: bool
    sebep: str


def aday_degerlendir(g: PiyasaGorunumu, coin: str, t_ms: int, mevcut: bool, maskeli: bool, islem_disi: bool,
                     p: Parametreler) -> AdayBilgisi:
    """Ss4.1 uygunluk. mevcut: onceki haftanin carry ismi (histerezis, Y2)."""
    s = g.barlar.get(coin)
    if coin in (p.btc, p.eth) or s is None or len(s) == 0:
        return AdayBilgisi(0.0, 0.0, 0, False, 'btc_eth_ya_da_veri_yok')
    v_30 = v30(g, coin, t_ms, p)
    v_60 = v60(s, t_ms, p.v60_gun)
    olay = eksik_funding_olay_sayisi(g, coin, t_ms, p)
    if ilk_bar_ms(s) > t_ms - p.isinma_gun * GUN_MS:
        return AdayBilgisi(v_30, v_60, olay, False, 'isinma')
    if maskeli:
        return AdayBilgisi(v_30, v_60, olay, False, 'maske')
    if islem_disi:
        return AdayBilgisi(v_30, v_60, olay, False, 'islem_disi')
    if olay > p.carry_eksik_olay_max:
        return AdayBilgisi(v_30, v_60, olay, False, 'eksik_funding')
    if v_60 < p.hacim_taban_v60:
        return AdayBilgisi(v_30, v_60, olay, False, 'v60')
    esik = p.carry_cikis_v30 if mevcut else p.carry_giris_v30
    if v_30 < esik:
        return AdayBilgisi(v_30, v_60, olay, False, 'v30')
    return AdayBilgisi(v_30, v_60, olay, True, '')


def hafta_ici_cikis_mi(g: PiyasaGorunumu, coin: str, t_ms: int, maskeli: bool, p: Parametreler) -> bool:
    """Ss4.4 hafta ici cikis (Y2): maske, V30 < 10M, V60 < 20M ya da hic bar yok."""
    s = g.barlar.get(coin)
    if s is None or len(s) == 0 or maskeli:
        return True
    return v30(g, coin, t_ms, p) < p.carry_cikis_v30 or v60(s, t_ms, p.v60_gun) < p.hacim_taban_v60


# ---------------------------------------------------------------------------------------------------------
# Ss4.2 skor ve notrleme
# ---------------------------------------------------------------------------------------------------------

def f30(f: FundingSerisi, t_ms: int, p: Parametreler) -> float:
    """F30 = son 30 gunun gercek funding oranlari toplami * 365/30 (yalniz gercek kayit; dolgu yok)."""
    if f is None or len(f) == 0:
        return 0.0
    secim = (f.damga_ms > t_ms - p.carry_f30_gun * GUN_MS) & (f.damga_ms <= t_ms)
    return float(f.oran[secim].sum()) * 365.0 / p.carry_f30_gun


def siralar(x) -> np.ndarray:
    """Ortalama sira (1'den, esitlikte ortalama). nan degerler tanimli siralarin medyanini alir (Y4)."""
    x = np.asarray(x, dtype=float)
    tanimli = np.nonzero(~np.isnan(x))[0]
    m = len(tanimli)
    r = np.full(len(x), 1.0)
    if m == 0:
        return r
    deg = x[tanimli]
    sira = np.argsort(deg, kind='mergesort')
    ranks = np.empty(m)
    i = 0
    while i < m:
        j = i
        while j + 1 < m and deg[sira[j + 1]] == deg[sira[i]]:
            j += 1
        ranks[sira[i:j + 1]] = (i + j) / 2.0 + 1.0
        i = j + 1
    r[:] = float(np.median(ranks))           # eksik degerler: tanimli siralarin gercek medyani
    r[tanimli] = ranks
    return r


def notrle(c, r30, s_trend, beta) -> np.ndarray:
    """rank(c) = a + b1 rank(R30) + b2 rank(s) + b3 rank(beta) + e; z = e (kesitsel OLS, siralar uzerinde)."""
    y = siralar(c)
    X = np.column_stack([np.ones(len(y)), siralar(r30), siralar(s_trend), siralar(beta)])
    katsayi, *_ = np.linalg.lstsq(X, y, rcond=None)
    return y - X @ katsayi


def beta_tahmin(r_coin: np.ndarray, r_btc: np.ndarray, p: Parametreler) -> tuple:
    """(beta_hat, beta). Son `carry_beta_gun` gunun ortak tanimli gunluk log getirileriyle BTC'ye OLS betasi
    (sabitli); beta = 0,5*beta_hat + 0,5 (Y5)."""
    n = p.carry_beta_gun
    a, b = np.asarray(r_coin, dtype=float)[-n:], np.asarray(r_btc, dtype=float)[-n:]
    ortak = ~np.isnan(a) & ~np.isnan(b)
    beta_hat = 1.0
    if ortak.sum() >= 2:
        x, y = b[ortak], a[ortak]
        vx = float(np.var(x))
        if vx > 0:
            beta_hat = float(np.mean((x - x.mean()) * (y - y.mean()))) / vx
    return beta_hat, p.carry_beta_buzulme * beta_hat + (1.0 - p.carry_beta_buzulme)


# ---------------------------------------------------------------------------------------------------------
# Ss4.3 bacaklar
# ---------------------------------------------------------------------------------------------------------

def bacaklar(isimler: list, z: dict, f30_d: dict, onceki_isaret: dict, p: Parametreler) -> tuple:
    """(long isimleri, short isimleri). Short: z'nin en yuksek %30'u; long: en dusuk %30'u (k = floor(0,3 n), Y3).
    Histerezis: mevcut short z >= medyan iken, mevcut long z <= medyan iken tutulur. Long sarti F30 >= -%50, mevcut
    long'a da. Yeni secim histerezisten onceliklidir (ayni isim iki bacakta olamaz)."""
    n = len(isimler)
    if n == 0:
        return (), ()
    k = int(math.floor(p.carry_bacak_oran * n))
    medyan = float(np.median([z[c] for c in isimler]))
    azalan = sorted(isimler, key=lambda c: (-z[c], c))
    artan = sorted(isimler, key=lambda c: (z[c], c))
    yeni_short = set(azalan[:k])
    yeni_long = set(artan[:k]) - yeni_short
    short = set(yeni_short)
    long_ = set(yeni_long)
    for c in isimler:
        if c in short or c in long_:
            continue
        if onceki_isaret.get(c, 0) < 0 and z[c] >= medyan:
            short.add(c)
        elif onceki_isaret.get(c, 0) > 0 and z[c] <= medyan:
            long_.add(c)
    long_ = {c for c in long_ if f30_d[c] >= p.carry_long_funding_taban}
    return tuple(sorted(long_)), tuple(sorted(short))


# ---------------------------------------------------------------------------------------------------------
# Ss4.4 haftalik kitap
# ---------------------------------------------------------------------------------------------------------

def yeniden_notrle(q: dict, fiyat_ref: dict) -> tuple:
    """Ss4.4 adim 6: agir bacagin butun isimleri lambda = min(N_L, N_S)/max(N_L, N_S) ile carpilir. Bir bacak bossa
    kitap 0. Doner: (q, lambda, bagli_bacak)."""
    nl = sum(v * fiyat_ref[c] for c, v in q.items() if v > 0)
    ns = sum(-v * fiyat_ref[c] for c, v in q.items() if v < 0)
    if nl <= 0 or ns <= 0:
        return {c: 0.0 for c in q}, 0.0, 'bos_bacak'
    if nl == ns:
        return dict(q), 1.0, ''
    lam = min(nl, ns) / max(nl, ns)
    agir_long = nl > ns
    yeni = {c: (v * lam if (v > 0) == agir_long and v != 0 else v) for c, v in q.items()}
    return yeni, lam, 'long' if agir_long else 'short'


@dataclass(frozen=True)
class HaftalikCarry:
    q_yildiz: dict           # alt -> q^C* (yalniz sifir-disi)
    beta: dict               # alt -> beta (hafta boyunca sabit)
    lam: float
    bagli_bacak: str
    olcek: float             # adim 1 olcegi (tau / V)
    n_c: int
    tanilar: dict = field(default_factory=dict)


def haftalik_kitap(adaylar: list, z: dict, f30_d: dict, sigma_c: dict, beta: dict, v30_d: dict, q_eski: dict,
                   sabit_mevcut: dict, fiyat_ref: dict, nav: float, L: float, v_fn, p: Parametreler) -> HaftalikCarry:
    """MIMARI Ss4.4 adim 1-7. adaylar: bugun uygun isimler (n_C). q_eski: onceki haftanin q^C*. sabit_mevcut:
    mevcut olup bugun yeni secilemeyen ama tutulan isimler -> q (Y7). v_fn(w: dict) -> V (ortak Sigma ile, BTC dahil)."""
    n_c = len(adaylar)
    tan = {'n_c': n_c}
    if n_c < p.carry_genislik_sifir:
        return HaftalikCarry({}, dict(beta), 0.0, 'genislik', 0.0, n_c, tan)      # carry kitabi 0 (Ss4.1)
    isaret = {c: (1 if v > 0 else -1) for c, v in q_eski.items() if v != 0.0}
    long_, short = bacaklar(adaylar, z, f30_d, isaret, p)
    tan.update({'long': list(long_), 'short': list(short)})
    if not long_ or not short:
        return HaftalikCarry({}, dict(beta), 0.0, 'bos_bacak', 0.0, n_c, tan)     # bir bacak bos: kitap 0 (Ss4.4)

    # Birim bacaklar: bacak ici 1/sigma^C, iki bacak esit nominal (her biri 1).
    w = {}
    for bacak, isaret_b in ((long_, 1.0), (short, -1.0)):
        ters = {c: 1.0 / sigma_c[c] for c in bacak}
        toplam = sum(ters.values())
        for c in bacak:
            w[c] = isaret_b * ters[c] / toplam
    # Adim 1: gecici BTC hedge ile olcekleme (T4-b).
    w_btc = -sum(beta[c] * w[c] for c in w)
    v = v_fn({**w, p.btc: w_btc})
    if not v > 0:
        raise CarryHatasi("carry birim kitabinin V'si 0")
    olcek = p.tau / v
    w = {c: x * olcek for c, x in w.items()}
    v_sonra = v_fn({**w, p.btc: w_btc * olcek})
    if v_sonra > p.tau * (1 + 1e-9):
        raise CarryHatasi("T4-b: olcekleme sonrasi V(w^C) > tau (teknik hata)")
    # Adim 2: butce L*omega_C (genislik x0,5, Y6).
    butce = L * p.carry_omega * (0.5 if n_c < p.carry_genislik_yarim else 1.0)
    w = {c: x * butce for c, x in w.items()}
    # Adim 3: carry isim tavanlari (V30 < 50M isimlerde yarisi). Kirpilan pay dagitilmaz.
    kirpilan = []
    for c, x in w.items():
        tavan = p.carry_tavan_long if x > 0 else p.carry_tavan_short
        if v30_d[c] < p.carry_yarim_tavan_v30:
            tavan *= 0.5
        if abs(x) > tavan:
            w[c] = math.copysign(tavan, x)
            kirpilan.append(c)
    # Adim 4: miktar. Adim 5: haftalik bant (isim basina). Bant, carry isim tavanini asan eski miktari tutmaz
    # (adim 6: "carry isim tavanlari korunur"; Codex 4. tur).
    q = {}
    bantli = []
    for c, x in w.items():
        q_ham = x * nav / fiyat_ref[c]
        eski = q_eski.get(c, 0.0)
        tavan = (p.carry_tavan_long if x > 0 else p.carry_tavan_short) * (0.5 if v30_d[c] < p.carry_yarim_tavan_v30 else 1.0)
        if q_ham != 0.0 and eski != 0.0 and (q_ham > 0) == (eski > 0) and abs(q_ham - eski) / abs(q_ham) < p.carry_bant                 and abs(eski) * fiyat_ref[c] / nav <= tavan * (1 + 1e-12):
            q_ham = eski
            bantli.append(c)
        q[c] = q_ham
    for c, v_sabit in sabit_mevcut.items():
        q[c] = v_sabit
    # Adim 6: alt sepetinin yeniden dolar-notrlenmesi (notrluk banttan once gelir).
    q, lam, bagli = yeniden_notrle(q, fiyat_ref)
    tan.update({'kirpilan': sorted(kirpilan), 'bantli': sorted(bantli), 'olcek': olcek, 'v_birim': v_sonra,
                'butce': butce})
    return HaftalikCarry({c: v for c, v in q.items() if v != 0.0}, dict(beta), lam, bagli, olcek, n_c, tan)


def hafta_ici_guncelle(q_yildiz: dict, cikanlar: set, fiyat_ref: dict) -> tuple:
    """Ss4.4 hafta ici: cikan isim 0; ayni gun yeniden notrleme (yalniz kucultur). Doner (q, lambda, bagli)."""
    if not cikanlar & set(q_yildiz):
        return dict(q_yildiz), 1.0, ''
    q = {c: (0.0 if c in cikanlar else v) for c, v in q_yildiz.items()}
    q, lam, bagli = yeniden_notrle(q, fiyat_ref)
    return {c: v for c, v in q.items() if v != 0.0}, lam, bagli


@dataclass(frozen=True)
class GunlukBlok:
    w_alt: dict              # alt -> w^C_i,t (T4-c sonrasi)
    w_btc: float             # BTC hedge (T4-c sonrasi)
    t4c_katsayi: float       # 1 = baglamadi
    notr_sapma: float        # |sum w| / sum |w| (alt sepeti; rapor)


def gunluk_blok(q_yildiz: dict, beta: dict, fiyat_ref: dict, nav: float, L: float, v_fn,
                p: Parametreler) -> GunlukBlok:
    """MIMARI Ss4.5 adim 0: w^C_i,t = q^C*_i P_i,t / NAV; BTC hedge o gunku gercek alt sepetinden; T4-c."""
    w = {c: q * fiyat_ref[c] / nav for c, q in q_yildiz.items() if q != 0.0}
    if not w:
        return GunlukBlok({}, 0.0, 1.0, 0.0)
    w_btc = -sum(beta[c] * x for c, x in w.items())
    lim = p.carry_omega * L * p.tau
    v = v_fn({**w, p.btc: w_btc})
    kat = 1.0
    if v > lim * (1 + 1e-12):
        kat = lim / v
        w = {c: x * kat for c, x in w.items()}
        w_btc *= kat
        if v_fn({**w, p.btc: w_btc}) > lim * (1 + 1e-9):
            raise CarryHatasi("T4-c: olcekleme sonrasi blok V > omega_C*L*tau (teknik hata)")
    brut = sum(abs(x) for x in w.values())
    return GunlukBlok(w, w_btc, kat, abs(sum(w.values())) / brut if brut > 0 else 0.0)
