"""Banka birim yürütücüsü (BANKA §3.1, §3.4–§3.6, §4, §5.4; BK-1…BK-10). Her birim bir tam motor koşusudur;
dondurulmuş kod ve birim kimliğinden hesaplanır. R3 (long_beta) kendi motor koşusudur, hedefi pasif long kitaptır
(banka_kos/long_beta.py; BANKA §3.7 netleştirme 13). Çıktı iki parçadır:
  düz  (kapalı grup; kosucu şifreler, BK-2): günlük NAV, birincil pencere ölçümü, stres nesneleri, B9 serisi, SR ...
  açık (denetim): muhasebe kapısı hataları, karar sayısı, günlük son hash'i, null değişmezleri ve ortak pay (performans
  içermez).
Motor verinin ilk gününden Z2 sonuna kadar kesintisiz koşar (§3.1); null yolları birincil örneklem sonunda biter
(§3.5.6). HAR: banka modu (dondurulmuş β, yolun kendi yürüyen ŝ²'si; kalibrasyonla aynı). Lot kapalı koşu (R13):
bütün sembollerde adım 0, minNotional aynı (BK-10). Görülmüş günler bütün pencere ölçümlerinden düşülür (BK-5).
"""
from dataclasses import dataclass, field, replace

import numpy as np

from banka.degerlendirme import Pencere, birincil_olcum, sadece_sharpe
from banka.har_banka import banka_takvimi
from banka.pnl import coin_pnl
from banka.rejim_null import null_yolu
from kalibrasyon.tohum import uretec
from kalibrasyon.yurutucu import muhasebe_kapisi
from motor.ayristirma import ayristir
from motor.geri_test import KosuAyarlari, kos
from motor.gorunum import GUN_MS, SAAT_MS, TamVeri, funding_serisi, saatlik_seri, son_kapanis
from motor.tipler import Parametreler

from . import ayar
from . import parite
from . import stres
from . import tanilar


B5_GRUPLARI = ('birincil', 'a_ayristirma')


class BirimHatasi(RuntimeError):
    """Null değişmez ihlali ya da bilinmeyen birim: T4/T3 (§2.5); koşu durur."""


@dataclass
class BankaBaglami:
    veri: object                          # TamVeri; adaylar = uygun evren + BTC/ETH
    k_adaylar: tuple                      # B9: K coinleri + BTC/ETH
    motor_bas_ms: int                     # verinin ilk günü 00:00 (sürekli koşu)
    t0_z1_ms: int
    gorulmus_gunler: tuple                # BK-5
    filtreler: dict
    beta: tuple                           # dondurulmuş HAR β
    tohum_banka: int
    anonim: dict                          # sembol -> kimlik (null ikincil tohumu, coin tabloları)
    birincil_son_ms: int = ayar.BIRINCIL_SON_MS
    z1_dilim_sinir: tuple = ayar.Z1_DILIM_SINIR
    z2_son_ms: int = ayar.Z2_SON_MS
    parametreler: object = field(default_factory=Parametreler)

    def dilimler(self) -> tuple:
        s = (self.t0_z1_ms,) + tuple(self.z1_dilim_sinir) + (self.birincil_son_ms,)
        return tuple((s[i], s[i + 1]) for i in range(len(s) - 1))

    def pencere(self) -> Pencere:
        return Pencere(bas_ms=self.t0_z1_ms, dilim_gun=tuple((b - a) // GUN_MS for a, b in self.dilimler()),
                       haric_gunler=tuple(self.gorulmus_gunler))


def veri_kes(veri, bit_ms: int):
    """bit_ms'ten (haric) sonraki barlari ve funding kayitlarini atar; bari kalmayan coin cikar (null yolu birincil
    orneklem sonunda biter; §3.5.6)."""
    barlar, funding = {}, {}
    for c, s in veri.barlar.items():
        k = int(np.searchsorted(s.acilis_ms, bit_ms))
        if k:
            barlar[c] = saatlik_seri(s.acilis_ms[:k], s.acilis[:k], s.yuksek[:k], s.dusuk[:k], s.kapanis[:k],
                                     s.hacim[:k])
    for c, f in veri.funding.items():
        if c not in barlar:
            continue
        k = int(np.searchsorted(f.damga_ms, bit_ms))
        funding[c] = funding_serisi(f.damga_ms[:k], f.oran[:k], None if f.aralik_saat is None else f.aralik_saat[:k])
    return TamVeri(barlar=barlar, funding=funding, adaylar=veri.adaylar)


def _takvim(veri, bag: BankaBaglami, t_son_ms: int):
    return banka_takvimi(veri, bag.motor_bas_ms, t_son_ms, bag.beta, bag.parametreler)


def _nav_gunluk(s, bas_ms: int, bit_ms: int, nav0: float) -> list:
    """Gün sınırlarındaki NAV (bas_ms dahil, bit_ms dahil); koşu bas_ms'ten sonra başladıysa hata."""
    nav_ms = np.asarray(s.nav_ms, dtype=np.int64)
    nav = np.asarray(s.nav, dtype=float)
    out = []
    for t in range(bas_ms, bit_ms + 1, GUN_MS):
        i = int(np.searchsorted(nav_ms, t))
        if i < len(nav_ms) and nav_ms[i] == t:
            out.append(float(nav[i]))
        elif t == nav_ms[0] - SAAT_MS:
            out.append(float(nav0))
        else:
            raise BirimHatasi(f"NAV {t} aninda yok")
    return out


def pozisyon_gecmisleri(gunluk) -> dict:
    """{coin: (damga dizisi, q_sonrasi dizisi)}; motor.durum.pozisyon_gecmisi ile aynı kural (dolum, uzlaşma, miktarlı
    düzeltme), bütün coinler için tek geçişte."""
    q, ms, qq = {}, {}, {}
    for k in gunluk.kayitlar():
        c = k.coin
        if k.tur == 'dolum':
            q[c] = 0.0 if k.veri.get('tam_kapanis_son') else q.get(c, 0.0) + k.miktar
        elif k.tur == 'uzlasma':
            q[c] = 0.0
        elif k.tur == 'duzeltme' and k.miktar is not None and k.miktar != 0.0:
            q[c] = q.get(c, 0.0) + k.miktar
        else:
            continue
        ms.setdefault(c, []).append(k.damga_ms)
        qq.setdefault(c, []).append(q[c])
    return {c: (np.asarray(ms[c], dtype=np.int64), np.asarray(qq[c], dtype=float)) for c in sorted(ms)}


def gun_sonu_agirliklari(s, veri, gunler_ms, nav_fn) -> list:
    """Her günün sonunda (t + 24h) gerçekleşen net kitap ağırlıkları q·kapanış/NAV (§5.4)."""
    gecmis = pozisyon_gecmisleri(s.gunluk)
    out = []
    for g in np.asarray(gunler_ms, dtype=np.int64).tolist():
        t = g + GUN_MS
        nav = nav_fn(t)
        w = {}
        for c, (ms, q) in gecmis.items():
            if not len(ms):
                continue
            i = int(np.searchsorted(ms, t, side='left')) - 1     # sınırdan kesin önceki son olay (17 d)
            if i < 0 or q[i] == 0.0:
                continue
            f = son_kapanis(veri.barlar[c], t) if c in veri.barlar else None
            if f is not None:
                w[c] = q[i] * f / nav
        out.append(w)
    return out


def _k_alt_serisi(s, veri, k_adaylar, gunler_ms, nav_gunluk) -> list:
    """B9: K altlarının günlük fiyat + funding − maliyet katkısı / NAV(gün başı)."""
    cp = coin_pnl(s, veri)
    k_alt = [c for c in k_adaylar if c not in ('BTCUSDT', 'ETHUSDT')]
    gun = (np.asarray(cp.saat_ms, dtype=np.int64) // GUN_MS) * GUN_MS
    toplam = np.zeros(len(cp.saat_ms))
    for c in k_alt:
        if c in cp.pnl:
            toplam += cp.pnl[c]
    ix = {int(g): i for i, g in enumerate(np.asarray(gunler_ms, dtype=np.int64).tolist())}
    gunluk = np.zeros(len(ix))
    for g, x in zip(gun.tolist(), toplam.tolist()):
        if g in ix:
            gunluk[ix[g]] += x
    return (gunluk / np.asarray(nav_gunluk[:-1], dtype=float)).tolist()


def _veri(b: dict, bag: BankaBaglami):
    v = bag.veri
    if b['grup'] == 'cikarma_btc_eth' or (b['grup'] == 'cikarma' and 'cikan' in b):
        return replace(v, adaylar=tuple(c for c in v.adaylar if c != b['cikan']))
    if b['evren'] == 'K':
        return replace(v, adaylar=tuple(bag.k_adaylar))
    return v


def birim_yurut(b: dict, bag: BankaBaglami) -> tuple:
    """Doner (duz, acik). b: ayar.birimler kimliği (B10 çıkarması için 'cikan' kosucu tarafından çözülmüş olmalı)."""
    grup = b['grup']
    if grup == 'long_beta':
        from .long_beta import r3_yurut
        return r3_yurut(b, bag)
    acik = {}
    if grup == 'null':
        p_ = b['null_no']
        taban = bag.motor_bas_ms
        H = (bag.birincil_son_ms - taban) // SAAT_MS
        dil = tuple(((a - taban) // SAAT_MS, (z - taban) // SAAT_MS) for a, z in bag.dilimler())
        veri, pay, deg = null_yolu(veri_kes(bag.veri, bag.birincil_son_ms), taban, H, dil, bag.anonim,
                                   lambda j: uretec(bag.tohum_banka, p_, j),
                                   lambda j, i: uretec(bag.tohum_banka, p_, j, i))
        acik.update({'null_degismez': {'gecti': deg['gecti'], 'ihlal_sayisi': len(deg['ihlaller'])},
                     'ortak': pay['ortak'], 'toplam': pay['toplam']})
        if not deg['gecti']:
            raise BirimHatasi(f"null degismez ihlali (T4-f): {deg['ihlaller'][:5]}")
        t_son = bag.birincil_son_ms - SAAT_MS
    else:
        veri = _veri(b, bag)
        t_son = bag.z2_son_ms - SAAT_MS
    takvim = _takvim(veri, bag, t_son)
    p = replace(bag.parametreler, mimari=b['mimari'], sigma_tahmincisi='HAR', har_takvimi=takvim,
                delist_h_long=b['h_L'])
    filtreler = bag.filtreler if b['lot'] else {c: (0.0, mn) for c, (_, mn) in bag.filtreler.items()}
    s = kos(veri, KosuAyarlari(t0_ms=bag.motor_bas_ms, t_son_ms=t_son, L=b['L'], maliyet_k=b['maliyet_k'],
                               nav0=b['nav0'], filtreler=filtreler), p)
    a = ayristir(s.gunluk, veri, p) if (b['mimari'] == 'B' and grup == 'birincil') else None
    # R8 (K1-09): B'nin 1× maliyetli Kelly birimleri yalnız carry bacağı serisi için ayrıştırılır (ölçüm B5'siz, BK-13).
    a_r8 = (ayristir(s.gunluk, veri, p) if (b['mimari'] == 'B' and grup == 'kelly' and b['maliyet_k'] == 1.0)
            else None)
    acik.update({'muhasebe': muhasebe_kapisi(s, veri, a), 'karar_sayisi': len(s.kararlar),
                 'son_hash': s.gunluk.son_hash, 's2_pazartesi': len(takvim.s2)})
    pen = bag.pencere()
    if grup == 'null':                                            # R17 (netleştirme 15 f)
        r17 = dict(tanilar.r17_sayimlar(s, pen, veri, p), ortak_pay=acik['ortak'] / acik['toplam'] if acik['toplam'] else None)
        return {'birim': b, 'sr': sadece_sharpe(s, pen), 'r17': r17}, acik
    nav_g = _nav_gunluk(s, bag.t0_z1_ms, bag.z2_son_ms, b['nav0'])
    # B5 (ve B'de ayrıştırma) yalnız birincilde ve R8'in bağımsız A koşusunda (BANKA §3.4; Codex T18, BK-13).
    duz = {'birim': b, 'nav_bas_ms': bag.t0_z1_ms, 'nav_gunluk': nav_g,
           'olcum': birincil_olcum(s, veri, pen, b['mimari'], a, b5=grup in B5_GRUPLARI)}
    duz['olcum']['alt_katki_anonim'] = [bag.anonim.get(c, c) for c in duz['olcum']['alt_katki_sirasi']]
    if grup in ('birincil', 'kelly', 'izgara'):
        gunler = pen.gunler()
        nav_ms = np.asarray(s.nav_ms, dtype=np.int64)
        nav = np.asarray(s.nav, dtype=float)

        def nav_fn(t):
            return float(nav[int(np.searchsorted(nav_ms, t))])
        w = gun_sonu_agirliklari(s, veri, gunler, nav_fn)
        duz['stres_nesneleri'] = {k: v.tolist() for k, v in stres.nesneler(w).items()}
    if a is not None:                                             # R8 (netleştirme 16)
        duz['r8_satirlar'] = tanilar.r8_satirlari(a, bag.t0_z1_ms, bag.z2_son_ms, nav_g)
        duz['r8_carry_epizot'] = tanilar.carry_epizot_payi(a, pen)
    if a_r8 is not None:
        duz['r8_carry'] = tanilar.carry_bacagi(tanilar.r8_satirlari(a_r8, bag.t0_z1_ms, bag.z2_son_ms, nav_g))
    if grup == 'birincil':                                        # R5, R6, R7 (BANKA §3.7 netleştirme 14)
        duz['tanilar'] = tanilar.birincil_tanilari(s, veri, p, pen, duz['olcum']['r'], b['L'], t_son, b['mimari'])
        duz['piyasa'] = tanilar.piyasa_serileri(s, veri, p, pen, bag.t0_z1_ms, bag.z2_son_ms)      # R2, R4
        duz['r13b'] = tanilar.r13b(veri, filtreler, bag.t0_z1_ms, bag.z2_son_ms, b['nav0'])
        duz['r17'] = tanilar.r17_sayimlar(s, pen, veri, p)
        duz['b8_r'] = tanilar.b8_serisi(s, veri, bag.t0_z1_ms, bag.z2_son_ms, nav_g)          # B8 %90 GA (17 h)
        acik['parite'] = parite.parite(s, veri, b['L'], p, filtreler, bag.tohum_banka)         # T5 (20 d)
    if grup == 'demo_nav':                                        # R14
        duz['r14'] = tanilar.r14(s, pen, b['mimari'], p.btc)
    if grup == 'k_evren':
        gunler = np.arange(bag.t0_z1_ms, bag.z2_son_ms, GUN_MS, dtype=np.int64)
        duz['b9_seri'] = _k_alt_serisi(s, veri, bag.k_adaylar, gunler, nav_g)
    return duz, acik
