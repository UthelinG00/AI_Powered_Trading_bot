"""HAR banka modu (HAR on-kaydi madde 12; BANKA_ONKAYIT_TASLAK Ss3.7 "Motor yapilandirmasi"): katsayi dondurulmus,
s^2 verinin kendi Pazartesi haftalarindan dondurulmus katsayiyla yuruyen artiklardan (PIT; son 52 hafta, en az 8).
Kume ve tanimlar kilit Adim 2'nin baglayici betigiyle (`ciktilar/v8_har_secimi_20260929_01/har_secimi.py`) aynidir;
yalniz tarih sabitleri parametredir. Esitlik testi: testler/test_v8_har_banka.py.

P1: pazartesi_kumesi (betikteki pit_evren, madde 1). P2: s^2 yolu (madde 2, 4, 7)."""
import math
from dataclasses import replace
from datetime import datetime, timezone

import numpy as np

from motor.durum import StratejiDurumu
from motor.evren import evren_sec
from motor.gorunum import GUN_MS, SAAT_MS, aylik_secim_gunu_mu, bar_indeksi, gorunum_kur, gun_takvimi
from motor.har import HarTakvimi, gunluk_rv, har_log_tahmin, har_ozellik, haftalik_hedef
from motor.hedef import coin_gunluk, karar_bosluklari
from motor.hijyen import MaskeKaydi, gunluk_hijyen
from motor.karar import maske_ilerlet

HAFTA = 7 * GUN_MS


def pazartesi_mi(t_ms: int) -> bool:
    return datetime.fromtimestamp(t_ms / 1000, tz=timezone.utc).weekday() == 0


def pazartesi_kumesi(veri, t0_ms: int, son_pazartesi_ms: int, p) -> tuple:
    """HAR on-kaydi madde 1: t0'dan her gun maske + aylik evren (islem yok). Maske gecmisi son hedef haftasinin sonuna
    (son_pazartesi + 7g) kadar ilerletilir; Pazartesi degerlendirme coinleri (evren ∩ maskesiz ∩ t-1h bari var ∩
    gunluk hijyen (d) degil) son_pazartesi'ye kadar kaydedilir. Doner: ({pazartesi_ms: [coin, ...]}, son maske)."""
    d = StratejiDurumu()
    pazartesi = {}
    t = t0_ms
    while t <= son_pazartesi_ms + HAFTA:
        g = gorunum_kur(veri, t)
        bos, ref = karar_bosluklari(g, d, p)
        maske = maske_ilerlet(g, d, t, p, bos)
        if aylik_secim_gunu_mu(t) or d.evren_ms is None:
            evren, evren_ms = evren_sec(g, t, d.evren, maske, p).uyeler, t
        else:
            evren, evren_ms = d.evren, d.evren_ms
        d = replace(d, maske=maske, maske_ms=t, evren=evren, evren_ms=evren_ms, bosluk_ref=ref,
                    bosluk_gecmis=tuple(sorted(h for h in bos if h >= t - p.bosluk_gecmis_gun * GUN_MS)),
                    son_karar_ms=t)
        if t <= son_pazartesi_ms and pazartesi_mi(t):
            uyeler = []
            for c in evren:
                s = g.barlar.get(c)
                m = maske.get(c, MaskeKaydi())
                if s is None or m.maskeli or bar_indeksi(s, t - SAAT_MS) is None:
                    continue
                if gunluk_hijyen(g, c, t, bos, p).d:
                    continue
                uyeler.append(c)
            pazartesi[t] = uyeler
        t += GUN_MS
    return pazartesi, d.maske


def har_satirlari(veri, pazartesiler: dict, maske: dict, t_son_ms: int, p) -> list:
    """Madde 2 ve 4: her Pazartesi x degerlendirme coini icin ozellik (t'de) ve hedef toplami (sum r^2, t+1..t+7).
    Gunluk seri t_son'daki gorunumden; maskeli, (d) ve gunluk kapanisi olmayan gunun RV'si tanimsiz (betikle ayni)."""
    g_son = gorunum_kur(veri, t_son_ms)
    coinler = sorted({c for u in pazartesiler.values() for c in u})
    if not coinler:
        return []
    ilk = min(int(g_son.barlar[c].acilis_ms[0]) for c in coinler)
    gunler = gun_takvimi(ilk + SAAT_MS, t_son_ms)
    gun_idx = {int(x): i for i, x in enumerate(gunler)}
    seri = {}
    for c in coinler:
        m = maske.get(c, MaskeKaydi())
        cg = coin_gunluk(g_son, c, gunler, m, p)
        rv = gunluk_rv(g_son.barlar[c], gunler, p)
        isd = set(m.islem_disi_gunler)
        gecersiz = np.array([m.gunde_maskeli(int(x)) or int(x) in isd for x in gunler]) | np.isnan(cg.kapanislar)
        rv[gecersiz] = np.nan
        seri[c] = (cg.getiriler, rv)
    satirlar = []
    for t, uyeler in sorted(pazartesiler.items()):
        i = gun_idx[t]
        for c in uyeler:
            getiri, rv = seri[c]
            satirlar.append({'t': t, 'c': c, 'oz': har_ozellik(rv, i, p), 'toplam': haftalik_hedef(getiri, i)})
    return satirlar


def s2_yolu(satirlar: list, katsayi, pazartesiler, p, bas_ms=None, hepsi: bool = False) -> dict:
    """Madde 7: artik e = ln(toplam) - y_hat (y_hat s'de gecerli katsayiyla; katsayi(s) None ise yok). Pazartesi t'de
    s^2 = hedefi t'ye kadar tamamlanmis (s + 7g <= t) son har_artik_hafta haftanin butun artiklarinin varyansi
    (havuzlu, ddof = 0); en az har_artik_min_hafta hafta yoksa tanimsiz. pazartesiler: s^2'nin hesaplanacagi
    Pazartesiler (artan); bas_ms verilirse ondan oncekiler atlanir. hepsi=True ise tanimsiz Pazartesiler None degeriyle
    yazilir: takvim onceki degeri tasimaz, motor o hafta EWMA'ya doner (Codex T12-5)."""
    artik_hafta = {}
    for r in satirlar:
        beta = katsayi(r['t'])
        if beta is None or r['oz'] is None or not r['toplam']:
            continue
        y_hat = float(har_log_tahmin([r['oz']], beta)[0])
        artik_hafta.setdefault(r['t'], []).append(math.log(r['toplam']) - y_hat)
    yol = {}
    for t in pazartesiler:
        if bas_ms is not None and t < bas_ms:
            continue
        haftalar = [s for s in artik_hafta if t - HAFTA - (p.har_artik_hafta - 1) * HAFTA <= s <= t - HAFTA]
        if len(haftalar) >= p.har_artik_min_hafta:
            yol[t] = float(np.var(np.concatenate([artik_hafta[s] for s in sorted(haftalar)])))
        elif hepsi:
            yol[t] = None
    return yol


def banka_takvimi(veri, t0_ms: int, t_son_ms: int, beta, p) -> HarTakvimi:
    """Banka modu takvimi: dondurulmus katsayi (her t'de) ve verinin kendi yuruyen s^2'si. Artik haftalari hedefi
    t_son'a kadar biten Pazartesiler (s + 7g <= t_son); s^2, t0'dan t_son'a kadarki butun takvim Pazartesilerinde
    (t'den once tamamlanmis haftalarla; PIT). beta None ise HAR tanimsiz (motor EWMA'ya doner)."""
    ilk_pzt = t0_ms + ((7 - datetime.fromtimestamp(t0_ms / 1000, tz=timezone.utc).weekday()) % 7) * GUN_MS
    son_pzt = t_son_ms - HAFTA
    son_pzt -= datetime.fromtimestamp(son_pzt / 1000, tz=timezone.utc).weekday() * GUN_MS
    son_pzt -= son_pzt % GUN_MS
    if son_pzt < ilk_pzt:
        return HarTakvimi(aylar=((0, None if beta is None else tuple(float(x) for x in beta)),), s2=())
    kume, maske = pazartesi_kumesi(veri, t0_ms, son_pzt, p)
    satirlar = har_satirlari(veri, kume, maske, t_son_ms, p)
    b = None if beta is None else tuple(float(x) for x in beta)
    takvim_pzt = range(ilk_pzt, t_son_ms + 1, HAFTA)
    yol = s2_yolu(satirlar, lambda t: b, takvim_pzt, p, hepsi=True)
    return HarTakvimi(aylar=((0, b),), s2=tuple(sorted(yol.items())))
