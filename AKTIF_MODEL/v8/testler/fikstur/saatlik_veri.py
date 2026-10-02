"""v8 Slice 2 testleri icin sentetik 1h bar ve funding ureticisi. Gercek veri, ag ya da borsa yok.

Her coin bir `CoinTarifi` ile tanimlanir; uretici tohumlu ve deterministiktir. Saat indeksi 0 = bas_ms.
"""
from dataclasses import dataclass, field

import numpy as np

V8_TEST_BAS_MS = 1_688_169_600_000   # 2023-07-01 00:00 UTC (D'nin basi; yalniz takvim, veri sentetik)
SAAT = 3_600_000
GUN = 86_400_000


@dataclass
class CoinTarifi:
    p0: float = 100.0
    gunluk_suruklenme: float = 0.0          # gunluk log getiri ortalamasi (saate bolunur)
    saatlik_vol: float = 0.0                # saatlik log getiri std'si
    saatlik_hacim: float = 5_000_000.0      # quote USDT / saat (gunluk 120M)
    baslangic_saat: int = 0                 # listeleme saati (oncesinde bar yok)
    bitis_saat: int = None                  # delist: bu saatten itibaren bar yok
    eksik_saatler: frozenset = frozenset()  # bar yok
    duz_saatler: frozenset = frozenset()    # hacim 0 ve O=H=L=C
    hacim_carpani: dict = field(default_factory=dict)  # saat -> hacim carpani
    sok: dict = field(default_factory=dict)            # saat -> ek log getiri
    funding_araliklari: tuple = ((0, 8),)   # (baslangic_saati, aralik_saati), artan
    funding_orani: float = 0.0001
    funding_eksik: frozenset = frozenset()  # bu saatlerdeki funding kaydi yok
    funding_bitis_saat: int = None          # bu saatten itibaren funding yok


def coin_uret(t: CoinTarifi, saat_sayisi: int, tohum: int, bas_ms: int = V8_TEST_BAS_MS):
    from motor.gorunum import funding_serisi, saatlik_seri
    rng = np.random.default_rng(tohum)
    bitis = saat_sayisi if t.bitis_saat is None else min(t.bitis_saat, saat_sayisi)
    r = np.full(saat_sayisi, t.gunluk_suruklenme / 24.0)
    if t.saatlik_vol > 0:
        r = r + rng.normal(0.0, t.saatlik_vol, size=saat_sayisi)
    for h, x in t.sok.items():
        r[h] += x
    kapanis = t.p0 * np.exp(np.cumsum(r))
    acilis = np.concatenate([[t.p0], kapanis[:-1]])
    fitil = np.abs(rng.normal(0.0, max(t.saatlik_vol, 1e-4) / 2, size=saat_sayisi))
    yuksek = np.maximum(acilis, kapanis) * (1 + fitil)
    dusuk = np.minimum(acilis, kapanis) * (1 - fitil)
    hacim = np.full(saat_sayisi, t.saatlik_hacim)
    for h, c in t.hacim_carpani.items():
        if 0 <= h < saat_sayisi:
            hacim[h] *= c
    secim = np.zeros(saat_sayisi, dtype=bool)
    secim[t.baslangic_saat:bitis] = True
    for h in t.eksik_saatler:
        if 0 <= h < saat_sayisi:
            secim[h] = False
    for h in t.duz_saatler:
        if 0 <= h < saat_sayisi:
            hacim[h] = 0.0
            acilis[h] = yuksek[h] = dusuk[h] = kapanis[h]
    idx = np.nonzero(secim)[0]
    seri = saatlik_seri(bas_ms + idx * SAAT, acilis[idx], yuksek[idx], dusuk[idx], kapanis[idx], hacim[idx])

    # Funding damgalari: o saatte etkin araligin kati olan her saat (listelemeden sonra, funding bitisinden once).
    damgalar = []
    son = saat_sayisi if t.funding_bitis_saat is None else min(t.funding_bitis_saat, saat_sayisi)
    for h in range(t.baslangic_saat + 1, son):
        ara = [a for b, a in t.funding_araliklari if h >= b][-1]
        if h % ara == 0 and h not in t.funding_eksik:
            damgalar.append(h)
    damgalar = np.array(damgalar, dtype=np.int64)
    fund = funding_serisi(bas_ms + damgalar * SAAT, np.full(len(damgalar), t.funding_orani))
    return seri, fund


def tam_veri_uret(tarifler: dict, gun_sayisi: int, tohum: int = 20260928, bas_ms: int = V8_TEST_BAS_MS,
                  adaylar=None):
    from motor.gorunum import TamVeri
    saat = gun_sayisi * 24
    barlar, funding = {}, {}
    for i, (coin, t) in enumerate(sorted(tarifler.items())):
        barlar[coin], funding[coin] = coin_uret(t, saat, tohum + i, bas_ms)
    return TamVeri(barlar=barlar, funding=funding, adaylar=tuple(sorted(adaylar or tarifler)))


# Uctan uca senaryo (MIMARI Ss5.6 sentetik fikstur listesinin Mimari A kismi). 150 gun, 5 coin, hepsi yukari
# egilimli (long kitap). Gun 92 = 2023-10-01 (T0, aylik + gunluk ayni gun); gun 123 = 2023-11-01.
SENARYO_GUN = 150
SENARYO_T0_GUN = 92
SENARYO_BOSLUK_SAATI = 100 * 24 - 5        # BTC, ETH, ALT1 eksik (3/5): borsa capi bosluk -> gun 100 reduce-only
SENARYO_ISLEM_DISI_GUN = 105               # ALT1'in [t-1h, t) bari yok: gun 105'te islem disi
SENARYO_HACIM_COKUS_GUN = 115              # ALT2 hacmi %2'ye iner: (a) -> maske, m=3 cikis
SENARYO_DELIST_GUN = 110                   # ALT3 bar ve funding akisi durur: 30 gun sonra uzlasma


def senaryo_tarifleri() -> dict:
    t = {
        'BTCUSDT': CoinTarifi(p0=30000, gunluk_suruklenme=0.010, saatlik_vol=0.005, saatlik_hacim=50e6),
        'ETHUSDT': CoinTarifi(p0=2000, gunluk_suruklenme=0.008, saatlik_vol=0.006, saatlik_hacim=30e6),
        'ALT1': CoinTarifi(p0=5, gunluk_suruklenme=0.012, saatlik_vol=0.008,
                           eksik_saatler=frozenset({SENARYO_ISLEM_DISI_GUN * 24 - 1})),
        'ALT2': CoinTarifi(p0=1, gunluk_suruklenme=0.010, saatlik_vol=0.008,
                           hacim_carpani={h: 0.02 for h in range(SENARYO_HACIM_COKUS_GUN * 24, SENARYO_GUN * 24)}),
        'ALT3': CoinTarifi(p0=0.5, gunluk_suruklenme=0.015, saatlik_vol=0.008, bitis_saat=SENARYO_DELIST_GUN * 24,
                           funding_bitis_saat=SENARYO_DELIST_GUN * 24),
    }
    for c in ('BTCUSDT', 'ETHUSDT', 'ALT1'):
        t[c].eksik_saatler = frozenset(t[c].eksik_saatler | {SENARYO_BOSLUK_SAATI})
    return t


def senaryo_verisi():
    return tam_veri_uret(senaryo_tarifleri(), SENARYO_GUN)


def gun_ms(gun: int, bas_ms: int = V8_TEST_BAS_MS) -> int:
    return bas_ms + gun * GUN


def saat_ms(saat: int, bas_ms: int = V8_TEST_BAS_MS) -> int:
    return bas_ms + saat * SAAT


# Mimari B senaryosu (MIMARI Ss4; Ss5.6 sentetik fikstur listesinin carry kismi). 130 gun, BTC/ETH + 14 alt;
# altlarin funding oranlari farkli (skor dagilimi). Gun 93 = 2023-10-02 (ilk Pazartesi carry karari).
# CARRY_CIKIS_GUNU: en yuksek funding'li alt (A13, short bacak adayi) gun 95'te 6 duz bar -> gun 96'da maske,
# hafta ici cikis.
CARRY_GUN = 130
CARRY_CIKIS_GUNU = 95


def carry_senaryo_tarifleri() -> dict:
    t = {'BTCUSDT': CoinTarifi(p0=30000, gunluk_suruklenme=0.004, saatlik_vol=0.005, saatlik_hacim=50e6),
         'ETHUSDT': CoinTarifi(p0=2000, gunluk_suruklenme=0.003, saatlik_vol=0.006, saatlik_hacim=30e6)}
    for i in range(14):
        t[f'A{i:02d}'] = CoinTarifi(p0=1 + i, gunluk_suruklenme=0.002 * (i % 5 - 2), saatlik_vol=0.008,
                                    saatlik_hacim=5e6, funding_orani=0.0001 * (i - 6))
    t['A13'].duz_saatler = frozenset(range(CARRY_CIKIS_GUNU * 24 + 2, CARRY_CIKIS_GUNU * 24 + 8))
    return t


def carry_senaryo_verisi():
    return tam_veri_uret(carry_senaryo_tarifleri(), CARRY_GUN)
