"""Funding uzlasmasi ve eksik funding dolgusu (saf). MIMARI Ss2.6 (K1-01, K1-02), Ss5.1 funding_uzlas, Ss5.3.

Ag, dosya, config veya durum erisimi yoktur. Nakit isareti: nakit_i = -q_i * mark_i * oran_i (q > 0 long;
pozitif oranda long oder). Mark vekili: T damgasi icin [T-1h, T) barinin kapanisi (MIMARI Ss2.1); o bar yoksa
T'den once kapanmis son bar (yorum: gercek kayit bar akisi dururken gelebilir).
Bu modul yalniz "hangi kayitlar yazilacak" sorusunu yanitlar; gunluge yazmak cagiranin isidir.
"""
from dataclasses import dataclass

import numpy as np

from .gorunum import GUN_MS, SAAT_MS, FundingSerisi, PiyasaGorunumu, SaatlikSeri, bar_indeksi, ilk_bar_ms, son_kapanis
from .durum import q_once
from .tipler import Parametreler


@dataclass(frozen=True)
class FundingOlayi:
    tur: str            # 'ters_kayit' | 'funding' | 'funding_dolgu'
    tutar: float        # nakde eklenecek (isaretli)
    veri: dict


def mark_vekili(s: SaatlikSeri, t_ms: int):
    if s is None:
        return None
    k = bar_indeksi(s, t_ms - SAAT_MS)
    if k is not None:
        return float(s.kapanis[k])
    return son_kapanis(s, t_ms)


def bar_akisi_suruyor(s: SaatlikSeri, h_ms: int) -> bool:
    """h saat sinirinda coinin bar akisi suruyor mu: [h-1h, h) bari var ve hacmi > 0 (MIMARI Ss2.6)."""
    if s is None:
        return False
    k = bar_indeksi(s, h_ms - SAAT_MS)
    return k is not None and s.hacim[k] > 0


def funding_uzlas(q_once_deger: float, mark: float, oran: float) -> float:
    """MIMARI Ss5.1: nakit_i = -q_i * mark_i * oran_i."""
    return -q_once_deger * mark * oran


def delta_aralik_saat(f: FundingSerisi, t_ms: int, p: Parametreler) -> float:
    """Delta_i(t): son 30 gunde ardisik gercek kayitlar arasindaki en uzun aralik (saat); iki kayit yoksa 8h."""
    pencere = f.damga_ms[(f.damga_ms >= t_ms - p.funding_pencere_gun * GUN_MS) & (f.damga_ms <= t_ms)]
    if len(pencere) < 2:
        return p.funding_varsayilan_aralik_saat
    return float(np.diff(pencere).max()) / SAAT_MS


def _araliklar_saat(f: FundingSerisi, p: Parametreler) -> np.ndarray:
    """Her gercek kaydin araligi (saat): arsiv araligi varsa o; yoksa onceki kayittan gecen sure (ilk kayit 8h)."""
    araliklar = np.empty(len(f))
    if len(f):
        araliklar[0] = p.funding_varsayilan_aralik_saat
        araliklar[1:] = np.diff(f.damga_ms) / SAAT_MS
    if f.aralik_saat is not None:
        bilinen = np.isfinite(f.aralik_saat) & (f.aralik_saat > 0)
        araliklar = np.where(bilinen, f.aralik_saat, araliklar)
    return araliklar


def en_kotu_saatlik_oranlar(f: FundingSerisi, t_ms: int, p: Parametreler) -> tuple:
    """(r*_long, r*_short). Gercek kayitlar saatlik orana cevrilir (oran / aralik saati). long: max(en yuksek,
    +r_taban); short: min(en dusuk, -r_taban)."""
    r_taban = p.funding_r_taban_saatlik
    if len(f) == 0:
        return r_taban, -r_taban
    saatlik = f.oran / _araliklar_saat(f, p)
    secim = (f.damga_ms >= t_ms - p.funding_pencere_gun * GUN_MS) & (f.damga_ms <= t_ms)
    if not secim.any():
        return r_taban, -r_taban
    return max(float(saatlik[secim].max()), r_taban), min(float(saatlik[secim].min()), -r_taban)


def funding_budama_ms(t_ms: int, p: Parametreler) -> int:
    """Gec kayit penceresinin alt ucu eksi en uzun borsa araligi: pencereye giren en eski kaydin kapsadigi saatten
    once kalan dolgu ve islenen damga artik hicbir kayitla eslesmez; durumdan budanir (Codex 3. tur)."""
    return t_ms - p.funding_gec_kayit_gun * GUN_MS - int(max(p.funding_borsa_araliklari) * SAAT_MS)


def kapsanan_aralik_saat(f: FundingSerisi, j: int, p: Parametreler) -> float:
    """j. gercek kaydin kapsadigi aralik (saat); MIMARI Ss2.6 "kaydin kapsadigi araliktaki dolgular ters
    kaydedilir".

    Arsiv kaydin araligini tasiyorsa (funding_interval_hours) o kullanilir. Tasimiyorsa: onceki kayittan gecen
    sureye esit ya da ondan kucuk en buyuk borsa araligi {1, 4, 8} (MIMARI Ss5.3). Boylece aralik degisiminde
    (1h/4h -> 8h) dolgular tamamen geri alinir (cift sayim yok); gercekten eksik kalmis uzlasmalarin dolgusu
    (8h duzende 16 saatlik ya da 1h duzende 3 saatlik bosluk) kalir (Codex K2, 2. tur). Kalan belirsizlik: arsiv
    araligi yoksa 4h duzende tek eksik kayit (8 saatlik bosluk) 4h->8h gecisinden ayrilamaz ve geri alinir."""
    if f.aralik_saat is not None and np.isfinite(f.aralik_saat[j]) and f.aralik_saat[j] > 0:
        return float(f.aralik_saat[j])
    if j == 0:
        return p.funding_varsayilan_aralik_saat
    bosluk = float(f.damga_ms[j] - f.damga_ms[j - 1]) / SAAT_MS
    adaylar = [a for a in p.funding_borsa_araliklari if a <= bosluk + 1e-9]
    return float(max(adaylar)) if adaylar else bosluk


def funding_saati(g: PiyasaGorunumu, coin: str, t_ms: int, gecmis, dolgular: tuple, p: Parametreler,
                  islenen=(), dolgu_kadar=None) -> list:
    """Saat siniri T (= t_ms) icin coinin funding olaylari (MIMARI Ss5.2 adim 1). g.t_ms == T olmali.

    gecmis: pozisyon gecmisi ((damga, q_sonrasi), ...), damgaya gore sirali; q(h-) icin.
    dolgular: ters kaydi bekleyen dolgular ((saat_ms, tutar), ...). islenen: son `funding_gec_kayit_gun` gunde
    islenmis gercek kayit damgalari. dolgu_kadar: son dolgu kaydinin damgasi.
    - Gercek kayitlar: pencere [T - funding_gec_kayit_gun, T] icindeki islenmemis her kayit, damga sirasiyla
      (canlida kayit gec, hatta daha yeni bir kayittan sonra gelebilir; duzeltme kaydin geldigi saatte nakde
      islenir, Ss2.6; Codex K1). Her kayit icin once kapsadigi (d - aralik, d] saatlerinin dolgularinin tersi
      (tek kalem), sonra gercek tutar -q(d-)*mark(d)*oran. Tutar 0 ve kapsanan dolgu yoksa kayit yazilmaz
      (pozisyonsuz donemin kayitlari gunlugu sismez; islenmemis kalir ve etkisizdir).
    - Sonra: bar akisi suruyor ve son gercek kayittan bu yana >= 1,5*Delta gectiyse eksik olay. Henuz dolgu
      almamis saatler (son gercek kayit ya da son dolgu kaydindan sonra, T dahil) saat saat hesaplanir ve tek
      kayitta yazilir: -q(h-)*mark(h)*r*. Ilk tespitte birikmis saatler, sonra her saat bir saat.
    Yalniz bar akisinin surdugu saatler dolgu alir; bar akisi durunca funding yazilmaz (K1-02).
    """
    s = g.barlar.get(coin)
    f = g.funding.get(coin, FundingSerisi(np.array([], dtype=np.int64), np.array([])))
    olaylar = []

    alt = int(np.searchsorted(f.damga_ms, t_ms - p.funding_gec_kayit_gun * GUN_MS, side='left'))
    ust = int(np.searchsorted(f.damga_ms, t_ms, side='right'))
    islenmis = set(islenen)
    bekleyen = list(dolgular)
    for j in range(alt, ust):
        d = int(f.damga_ms[j])
        if d in islenmis:
            continue
        aralik_ms = int(round(kapsanan_aralik_saat(f, j, p) * SAAT_MS))
        kapsanan = [x for x in bekleyen if d - aralik_ms < x[0] <= d]
        q = q_once(gecmis, d)
        mark = mark_vekili(s, d)
        oran = float(f.oran[j])
        tutar = funding_uzlas(q, mark, oran) if (q != 0.0 and mark is not None) else 0.0
        if tutar == 0.0 and not kapsanan:
            continue
        if kapsanan:
            ters = -sum(t for _, t in kapsanan)
            olaylar.append(FundingOlayi('ters_kayit', ters, {'tutar': ters, 'damga_ms': d, 'dolgu_sayisi': len(kapsanan),
                                                             'aralik_saat': aralik_ms / SAAT_MS}))
            bekleyen = [x for x in bekleyen if not (d - aralik_ms < x[0] <= d)]
        olaylar.append(FundingOlayi('funding', tutar, {'tutar': tutar, 'damga_ms': d, 'kapsam_bas_ms': d - aralik_ms,
                                                        'budama_ms': funding_budama_ms(t_ms, p),
                                                        'oran': oran, 'mark': mark, 'q': q}))

    if s is None or not bar_akisi_suruyor(s, t_ms):
        return olaylar
    son_gercek = int(f.damga_ms[ust - 1]) if ust > 0 else ilk_bar_ms(s)
    if son_gercek == t_ms:
        return olaylar
    delta = delta_aralik_saat(f, t_ms, p)
    if t_ms - son_gercek < p.funding_eksik_carpan * delta * SAAT_MS:
        return olaylar
    r_long, r_short = en_kotu_saatlik_oranlar(f, t_ms, p)

    def _saat_tutari(h):
        q = q_once(gecmis, h)
        if q == 0.0:
            return 0.0
        mark = mark_vekili(s, h)
        if mark is None:
            return 0.0
        return -q * mark * (r_long if q > 0 else r_short)

    bas = son_gercek if dolgu_kadar is None else max(son_gercek, dolgu_kadar)
    bit = t_ms
    if gecmis and gecmis[-1][1] == 0.0:
        bit = min(bit, int(gecmis[-1][0]))   # pozisyon kapandiktan sonraki saatlerde q(h-) = 0
    saatler = [(h, _saat_tutari(h)) for h in range(bas + SAAT_MS, bit + SAAT_MS, SAAT_MS)
               if bar_akisi_suruyor(s, h)]
    saatler = [(h, t) for h, t in saatler if t != 0.0]
    if saatler:
        tutar = sum(t for _, t in saatler)
        olaylar.append(FundingOlayi('funding_dolgu', tutar, {'tutar': tutar, 'saatler': [[h, t] for h, t in saatler],
                                                              'r_long': r_long, 'r_short': r_short,
                                                              'delta_saat': delta}))
    return olaylar
