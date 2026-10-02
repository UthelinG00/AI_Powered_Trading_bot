"""Gunluk karar adimi ve kacirilan karar (saf). MIMARI Ss5.2 adim 2, Ss5.4, Ss5.8, Ss2.3, Ss2.5, Ss3.6.

Ag, dosya, config veya durum erisimi yoktur. Canli ve geri test ayni `karar_ver`'i cagirir (MIMARI Ss5.5); fark
yalniz adaptordedir. Cikti, gunluge yazilacak kayitlarin tam listesidir; `karar_ver` gunluge kendisi yazmaz.
Sira: maske sayaclari son islenen gunden bugune ilerletilir -> varsa aylik evren -> hedef_agirlik -> bant ->
lot_yuvarlama -> devreden emir oncelik kurali -> yeni niyetler.
"""
import math
from dataclasses import dataclass, replace

import numpy as np

from .bant import bant_uygula
from .durum import Emir, MaliyetBaglami, StratejiDurumu
from .emir import artiran_iptali, filtre_al, lot_niyeti
from .evren import evren_sec
from .funding import funding_budama_ms
from .gorunum import (GUN_MS, SAAT_MS, PiyasaGorunumu, aylik_secim_gunu_mu, gun_takvimi, medyan_saatlik_hacim,
                      sigma_1h, v60, veri_baslangici_ms)
from .hedef import HedefKitap, hedef_agirlik_ayrintili, isim_tavani, karar_bosluklari, v_norm
from .hijyen import MaskeKaydi, gunluk_hijyen, maske_gunu_ilerle, maske_json
from .tavanlar import _kayip_s1, _kayip_s2
from .tipler import Parametreler


@dataclass(frozen=True)
class KayitTaslagi:
    tur: str
    coin: object = None
    miktar: object = None
    fiyat: object = None
    veri: dict = None


@dataclass(frozen=True)
class KararSonucu:
    hedef: HedefKitap
    bantli: dict              # coin -> bant sonrasi agirlik (serbest isimler)
    niyetler: dict            # coin -> Emir (yeni)
    iptaller: tuple           # (coin, iptal kaydi verisi: iptal, tamami, tam_kapanis, sebep)
    evren: tuple
    evren_ms: object
    maske: dict
    kayitlar: tuple           # KayitTaslagi dizisi, yazim sirasiyla: karar, iptaller, niyetler


def maske_ilerlet(g: PiyasaGorunumu, durum: StratejiDurumu, t_ms: int, p: Parametreler,
                  bosluklar: frozenset = None) -> dict:
    """Maske kayitlarini son islenen gunden (haric) t'ye (dahil) kadar gun gun ilerletir. Kacirilan gunler de
    gorunumden islenir; karar kacsa da donma sayaclari gunluktur. Ilk kararda (maske_ms yok) verinin ilk
    gununden itibaren islenir: isinma gecmisindeki donma ve maske T0'a tasinir (MIMARI Ss2.4-Ss2.5; Codex K4).
    bosluklar: karar_bosluklari kumesi (islenen gunleri kapsar)."""
    maske = dict(durum.maske)
    if bosluklar is None:
        bosluklar = karar_bosluklari(g, durum, p)[0]
    if durum.maske_ms is None:
        bas = veri_baslangici_ms(g)
        gunler = list(gun_takvimi(bas + SAAT_MS, t_ms)) if bas is not None else [t_ms]
    else:
        gunler = list(range(durum.maske_ms + GUN_MS, t_ms + 1, GUN_MS))
    coinler = sorted(set(g.adaylar) | set(durum.evren) | set(durum.pozisyonlar) | set(durum.devreden))
    for d in gunler:
        d = int(d)
        for c in coinler:
            s = g.barlar.get(c)
            if s is None or int(s.acilis_ms[0]) >= d:
                continue
            onceki = maske.get(c, MaskeKaydi())
            maske[c] = maske_gunu_ilerle(onceki, gunluk_hijyen(g, c, d, bosluklar, p), d, p)
    return maske


def maliyet_baglami(g: PiyasaGorunumu, coin: str, t_ms: int, sigma_ewma: float, btc_sigma: float,
                    p: Parametreler) -> MaliyetBaglami:
    s = g.barlar[coin]
    return MaliyetBaglami(
        v1h30=medyan_saatlik_hacim(s, t_ms, p.katilim_30g_gun), v1h7=medyan_saatlik_hacim(s, t_ms, p.katilim_7g_gun),
        v60=v60(s, t_ms, p.v60_gun),
        sigma_d_bps=0.0 if math.isnan(sigma_ewma) else sigma_ewma / math.sqrt(365.0) * 10_000.0,
        sigma_1h=sigma_1h(s, t_ms, p.sigma_1h_gun), btc_eth=coin in (p.btc, p.eth), btc_sigma_1h=btc_sigma)


def _ihlaller(w_vek, coinler, sabit, girdiler, L, p):
    btc_eth = np.array([c in (p.btc, p.eth) for c in coinler], dtype=bool)
    ihlal = set()
    if float(np.abs(w_vek).sum()) > p.brut_tavan * (1 + 1e-12):
        ihlal.add('brut')
    if _kayip_s1(w_vek, btc_eth, p) > p.s1_sinir * (1 + 1e-12):
        ihlal.add('S1')
    if _kayip_s2(w_vek, btc_eth, p) > p.s2_sinir * (1 + 1e-12):
        ihlal.add('S2')
    idx_k = [coinler.index(c) for c in girdiler.k_coinler]
    if idx_k and v_norm(w_vek[idx_k], girdiler.sigma_hat, girdiler.sigma_sifir) > L * p.tau * (1 + 1e-12):
        ihlal.add('T4d')
    return ihlal


def karar_ver(g: PiyasaGorunumu, durum: StratejiDurumu, L: float, p: Parametreler,
              filtreler: dict = None) -> KararSonucu:
    """Yapilan gunluk karar. durum: funding adimi (T'deki) uygulanmis durum (MIMARI Ss5.2 adim 1 -> 2)."""
    filtreler = filtreler or {}
    t = g.t_ms
    bosluklar, bosluk_ref = karar_bosluklari(g, durum, p)
    maske = maske_ilerlet(g, durum, t, p, bosluklar)
    if aylik_secim_gunu_mu(t) or durum.evren_ms is None:
        evren = evren_sec(g, t, durum.evren, maske, p).uyeler
        evren_ms = t
    else:
        evren, evren_ms = durum.evren, durum.evren_ms
    durum_bugun = replace(durum, maske=maske, evren=evren, evren_ms=evren_ms)
    hedef, girdiler = hedef_agirlik_ayrintili(g, durum_bugun, L, p, bosluklar=bosluklar)

    coinler = hedef.coinler
    sabit = set(hedef.sabit)
    serbest = [c for c in coinler if c not in sabit]
    evren_kume = set(evren)
    bantli = {}
    if serbest and hedef.carry is not None:
        # Mimari B: trend bandi ve yeniden sinama hedef_b icinde (MIMARI Ss4.5 adim 5-6).
        bantli = {c: hedef.w_yildiz[c] for c in serbest}
    elif serbest:
        w_y = np.array([hedef.w_yildiz[c] for c in serbest])
        w_m = np.array([hedef.w_mevcut[c] for c in serbest])
        ekstra = np.array([
            c not in evren_kume or maske.get(c, MaskeKaydi()).maskeli
            or abs(hedef.w_mevcut[c]) > isim_tavani(c, hedef.w_mevcut[c], p) * (1 + 1e-12)
            for c in serbest], dtype=bool)
        bs = bant_uygula(w_y, w_m, ekstra, p)
        w_b = dict(zip(serbest, bs.w.tolist()))
        # Bant sonrasi kitap butun tavanlarla (ve T4-d) yeniden sinanir; ihlal eden tarafin bandi kapanir.
        for _ in range(3):
            w_vek = np.array([w_b[c] if c in w_b else hedef.w_mevcut[c] for c in coinler])
            ihlal = _ihlaller(w_vek, coinler, sabit, girdiler, L, p)
            if not ihlal:
                break
            for c in serbest:
                taraf_long = hedef.w_yildiz[c] > 0 or w_b[c] > 0
                taraf_short = hedef.w_yildiz[c] < 0 or w_b[c] < 0
                if ({'brut', 'T4d'} & ihlal) or ('S1' in ihlal and taraf_long) or ('S2' in ihlal and taraf_short):
                    w_b[c] = hedef.w_yildiz[c]
        bantli = w_b

    btc_s = g.barlar.get(p.btc)
    btc_sigma = sigma_1h(btc_s, t, p.sigma_1h_gun) if btc_s is not None else float('nan')

    # Yeni niyetler (gerceklesmis pozisyondan; MIMARI Ss5.4 oncelik 3).
    adaylar = {}
    for c in serbest:
        adim, min_not = filtre_al(filtreler, c, p)
        q = durum.pozisyonlar.get(c, 0.0)
        if hedef.fiyat_ref[c] <= 0:
            continue
        dq = lot_niyeti(bantli[c], q, hedef.nav, hedef.fiyat_ref[c], adim, min_not)
        if dq != 0.0:
            adaylar[c] = dq

    # Devreden emir oncelik kurali (MIMARI Ss5.4). Islem disi coinde ve borsa capi boslukta (reduce-only) eski
    # emrin risk azaltan parcasi korunur, risk artiran parcasi iptal edilir; reduce-only'de yeni niyet eski
    # azaltan parcanin yerine en az onun kadar azaltiyorsa gecer (Codex K6; onceki Y4 yorumu geri alindi).
    # Esitlikte yeni niyet secilir: bugunun maliyet baglami ve maske cikisi (m=3) ona aittir (Codex 2. tur).
    # Normal kararda eski emrin tamami iptal edilir.
    iptaller = []
    for c in sorted(durum.devreden):
        e = durum.devreden[c]
        q = durum.pozisyonlar.get(c, 0.0)
        koru = c in sabit or hedef.reduce_only
        if koru and c in adaylar:
            yeni = adaylar[c]
            azaltan = e.kalan - (artiran_iptali(e.kalan, q, '') or {'iptal': 0.0})['iptal']
            if azaltan != 0.0 and not (yeni * azaltan > 0 and abs(yeni) >= abs(azaltan)):
                del adaylar[c]              # eski azaltan parca yeterli; yeni niyet yazilmaz
            else:
                iptaller.append((c, {'iptal': e.kalan, 'tamami': True, 'tam_kapanis': False,
                                     'sebep': 'yeni_niyet'}))
                continue
        if koru:
            iptal = artiran_iptali(e.kalan, q, 'islem_disi' if c in sabit else 'borsa_bosluk')
            if iptal is not None:
                iptaller.append((c, iptal))
        else:
            iptaller.append((c, {'iptal': e.kalan, 'tamami': True, 'tam_kapanis': False, 'sebep': 'yeni_karar'}))

    niyetler = {}
    for c, dq in adaylar.items():
        niyetler[c] = Emir(kalan=dq, karar_ms=t, maske_cikisi=bool(maske.get(c, MaskeKaydi()).maskeli and bantli[c] == 0.0),
                           tam_kapanis=bantli[c] == 0.0,
                           baglam=maliyet_baglami(g, c, t, girdiler.gunluk[c].sigma_ewma, btc_sigma, p))

    # Mimari B: sanal bacak miktari degisen coinlerin maliyet baglami (bacak maliyeti, MIMARI Ss4.7).
    sanal_baglam = {}
    if hedef.carry is not None:
        yeni_t, yeni_c = hedef.carry['sanal_trend'], hedef.carry['sanal_carry']
        for c in sorted(set(yeni_t) | set(yeni_c) | set(durum.sanal_trend) | set(durum.sanal_carry)):
            if (yeni_t.get(c, 0.0) != durum.sanal_trend.get(c, 0.0) or yeni_c.get(c, 0.0) != durum.sanal_carry.get(c, 0.0))                     and c in g.barlar and c in girdiler.gunluk:
                sanal_baglam[c] = maliyet_baglami(g, c, t, girdiler.gunluk[c].sigma_ewma, btc_sigma, p).json()
    gecmis_bas = t - p.bosluk_gecmis_gun * GUN_MS
    kayitlar = [KayitTaslagi('karar', veri={
        'evren': list(evren), 'evren_ms': evren_ms, 'maske': {c: maske_json(m) for c, m in sorted(maske.items())},
        'hedef': hedef.json(), 'bantli': bantli, 'bosluk_ref': bosluk_ref, 'funding_budama_ms': funding_budama_ms(t, p),
        'bosluk_gecmis': sorted(h for h in bosluklar if h >= gecmis_bas),
        **({'sanal_baglam': sanal_baglam} if hedef.carry is not None else {})})]
    for c, iptal in iptaller:
        kayitlar.append(KayitTaslagi('devreden_iptal', coin=c, veri=iptal))
    for c, e in niyetler.items():
        kayitlar.append(KayitTaslagi('emir_niyeti', coin=c, miktar=e.kalan, veri={'emir': e.json()}))
    return KararSonucu(hedef=hedef, bantli=bantli, niyetler=niyetler, iptaller=tuple(iptaller), evren=evren,
                       evren_ms=evren_ms, maske=maske, kayitlar=tuple(kayitlar))


def kacirilan_karar(durum: StratejiDurumu, t_ms: int) -> tuple:
    """MIMARI Ss5.8: kacirilan planli karar yetisme kosusuyla telafi edilmez. Risk artiran parcalar iptal,
    risk azaltan parcalar korunur; yeni risk yok. Donen: KayitTaslagi dizisi."""
    kayitlar = [KayitTaslagi('kacirilan_karar', veri={'t_ms': t_ms})]
    for c in sorted(durum.devreden):
        iptal = artiran_iptali(durum.devreden[c].kalan, durum.pozisyonlar.get(c, 0.0), 'kacirilan_karar')
        if iptal is not None:
            kayitlar.append(KayitTaslagi('devreden_iptal', coin=c, veri=iptal))
    return tuple(kayitlar)
