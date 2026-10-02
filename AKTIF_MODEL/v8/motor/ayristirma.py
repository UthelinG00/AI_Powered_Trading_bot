"""Mimari B P&L ayristirmasi (saf). MIMARI Ss4.7; CARRY_KAPISI Ss5.1-Ss5.6 (kapi bu fonksiyonun ciktisini okur; ayni
kuralin ikinci uygulamasi yazilmaz).

Girdi: kosunun olay gunlugu ve verisi. Sanal miktarlar karar kaydindan (hedef.carry) okunur ve kararin 1 saat
sonrasi (01:00 acilisi) gecerli olur. Her saat T (T'de acilan bar, T+1h'de degerleme) ve her coin icin:
- Fiyat: guncelleme saatinde eski miktar sk(T) -> acilis, yeni miktar acilis -> sk(T+1h); diger saatlerde
  q * (sk(T+1h) - sk(T)). sk: T'den once kapanmis son barin kapanisi (NAV degerlemesiyle ayni).
- Funding: her bacak (trend, carry) her coin icin kendi miktar gecmisiyle motorun AYNI kuralindan gecer
  (funding.funding_saati + durum.kayit_uygula; gercek kayit, eksik funding dolgusu, ters kayit, budama). Boylece
  bacak funding'i gercek net pozisyondan bagimsizdir (inceleme B8): net 0 iken de sanal bacaklar dolgu oder/alir.
- Bacak maliyeti: guncelleme saatinde |dq_bacak| * acilis * c_i / 1e4; c_i MIMARI Ss6.1 (karekok teriminde Q =
  bacagin kendi dolum nominali; maske cikisi ve stres carpani ayni).
- Gercek: pozisyon dolumlarla degisir; dolum fiyatinin acilistan farki gercek maliyettir.
- Netleme kazanci = bacak maliyetleri - gercek maliyet. Icra artigi A_i = e_i = q_i - qT_i - qC_i miktarinin
  fiyat + funding P&L'i (+ delist uzlasmasinin son kapanistan farki). A^C = sum s^C_i A_i; s^C karar kaydindan,
  [D 01:00, D+1 01:00) araligina uygulanir.
- Maliyet carpani k gunlugun baslangic kaydindan okunur (B7). Canli miktarli duzeltme: nakit + miktar * acilis
  icra artigina yazilir (B12).
Gec gelen gercek funding kaydi (yalniz canli): veri gorunumu kaydi damgasinda gosterdigi icin bacaklar damga
saatinde, gercek nakit gelis saatinde yazilir; fark iki saat arasinda icra artigina duser (ozdeslik bozulmaz).
Geri testte gelis = damga.
Carry bacagi funding'inin yonu (Codex T17-f): olay isledigi saatte yazilir ama long/short payi OZGUN saatin bacak
miktarinin isaretinden gelir (carry_fon_long / carry_fon_short): gercek kayit q(d-), dolgu her saatin q(h-), ters kayit
kapsadigi her dolgunun kendi saatinin yonu (tersi). Boylece yon degisimini kapsayan dolgu ya da ters kayit tek bacaga
yigilmaz.
Ozdeslik (CARRY Ss5.5): dNAV = trend satirlari + carry satirlari (alt + hedge) - bacak maliyetleri + netleme +
icra artigi; her saat.
"""
import math
from bisect import bisect_right
from dataclasses import dataclass, field

import numpy as np

from types import SimpleNamespace

from .durum import MaliyetBaglami, StratejiDurumu, kayit_uygula, q_once
from .funding import funding_budama_ms, funding_saati
from .gorunum import GUN_MS, SAAT_MS, TamVeri, bar_indeksi, gorunum_kur, son_kapanis
from .maliyet import maliyet_hesapla
from .tipler import Parametreler

SATIRLAR = ('trend_fiyat', 'trend_funding', 'trend_maliyet', 'carry_fiyat', 'carry_funding', 'carry_maliyet',
            'hedge_fiyat', 'hedge_funding', 'netleme', 'icra_artigi', 'artik_carry', 'artik_trend', 'dnav')


class AyristirmaHatasi(ValueError):
    """Gunluk Mimari B karar kaydi icermiyor ya da ozdeslik bozuk."""


@dataclass
class AyristirmaSonucu:
    saat_ms: np.ndarray
    satirlar: dict                       # satir -> saatlik dizi
    gunluk: dict                         # satir -> {gun_ms: toplam}
    ozdeslik_max_hata: float
    toplam: dict = field(default_factory=dict)
    # Coin basi trend sanal bacagi (banka B5 epizotu, M = B; BANKA Ss3.4): saatlik fiyat + funding - bacak maliyeti ve
    # saat boyunca tutulan sanal trend miktari. sum_c trend_coin = trend_fiyat + trend_funding - trend_maliyet.
    trend_coin: dict = field(default_factory=dict)
    trend_q: dict = field(default_factory=dict)
    # trend_coin = trend_eski + trend_yeni: saat basindaki sanal trend miktarinin payi (fiyat sk(T) -> acilis, funding,
    # kapanan kismin bacak maliyeti) ve saat sonundakinin payi (acilis -> sk(T+1h), acilan kismin maliyeti); isaret
    # degistirme saatinde maliyet |q0| : |q1| oraninda (banka B5; Codex T12-1).
    trend_eski: dict = field(default_factory=dict)
    trend_yeni: dict = field(default_factory=dict)
    # Coin basi carry sanal bacagi (CARRY Ss15 madde 3, U-07; K8 isim katkisi N_i = F_i + P_i - C_i): saatlik fiyat +
    # funding - bacak maliyeti; BTC hedge kendi anahtarinda. sum_c carry_coin = carry_fiyat + hedge_fiyat + carry_funding
    # + hedge_funding - carry_maliyet.
    carry_coin: dict = field(default_factory=dict)
    # carry_coin = carry_eski + carry_yeni: saat basindaki sanal carry miktarinin payi (fiyat sk(T) -> acilis, funding,
    # kapanan kismin bacak maliyeti) ve saat sonundakinin payi (trend_eski/trend_yeni ile ayni kural; Codex T15-13).
    carry_eski: dict = field(default_factory=dict)
    carry_yeni: dict = field(default_factory=dict)
    # Saat boyunca (saat sonunda) gecerli sanal carry miktari; ayristirmanin fiilen tukettigi deger (V5, Codex T16).
    carry_q: dict = field(default_factory=dict)
    # Saat T'de icra artigiyla carpilan s^C vektoru (isim/saat bazinda; artik_carry = sum_c sc_q * artik_coin). Artik
    # sifir olsa da yazilir: V5 diskten turetilen s^C ile birebir karsilastirir (Codex T17-e).
    sc_q: dict = field(default_factory=dict)
    # Carry bacagi funding'inin (gercek kayit, dolgu, ters kayit) ozgun saatin yonune gore long ve short payi; olayin
    # islendigi saatte (T17-f). carry_fon_long + carry_fon_short = carry_eski'nin funding kismi.
    carry_fon_long: dict = field(default_factory=dict)
    carry_fon_short: dict = field(default_factory=dict)
    # Trend bacagi funding parcalarindan ozgun saati kayit saatinden farkli olanlar (banka B5 epizot atfi; Codex T18):
    # coin -> [(kayit satiri n, ozgun_ms, tutar), ...]. Tutar trend_eski'de kayit satirinda kalir; B5 yeniden atar.
    trend_fon_ozgun: dict = field(default_factory=dict)
    # Coin basi icra artigi A_i (MIMARI Ss4.7; U-25 sifir/sifir tanisi). sum_c artik_coin = icra_artigi.
    artik_coin: dict = field(default_factory=dict)
    # Bacak funding'inin kayit turune gore dokumu (CARRY Ss4.2 madde 6: bacak ve isim bazinda):
    # {'T'|'C': {tur: {coin: [sayi, tutar]}}}; tur in funding, funding_dolgu, ters_kayit.
    bacak_funding_tur: dict = field(default_factory=dict)


def _bolus(q_a: float, q_b: float) -> tuple:
    """banka.pnl.bolus ile ayni kural (motor banka'yi ice aktarmaz)."""
    if q_a == 0.0:
        return 0.0, 1.0
    if q_b == 0.0 or (q_a > 0) == (q_b > 0):
        return (1.0, 0.0) if abs(q_b) <= abs(q_a) else (0.0, 1.0)
    t = abs(q_a) + abs(q_b)
    return abs(q_a) / t, abs(q_b) / t


def fon_parcalari(tur: str, veri: dict, dolgular) -> list:
    """Bacak ya da net pozisyon funding olayinin OZGUN saat parcalari [(ozgun_ms, tutar), ...] (Codex T17-f, T18 B5).
    Pozisyonun ozgun saati h'deki miktari q(h-)'dir (o saatin satirinin basindaki pozisyon).
    - funding: [(d, tutar)] (d = veri['damga_ms']; geri testte kayit saatiyle ayni); tutar 0 ise bos.
    - funding_dolgu: her dolgu saati (h, t).
    - ters_kayit: (d - aralik, d] kapsamindaki bekleyen dolgular (funding_saati ve kayit_uygula ile ayni kume), her biri
      kendi saatinde, eksi isaretle. Kume toplami olay tutariyla tutmazsa AyristirmaHatasi.
    dolgular: olay uygulanmadan onceki bekleyen dolgular ((saat_ms, tutar), ...)."""
    if tur == 'funding':
        t = float(veri.get('tutar', 0.0))
        return [(int(veri['damga_ms']), t)] if t != 0.0 else []
    if tur == 'funding_dolgu':
        return [(int(h), float(t)) for h, t in veri['saatler']]
    if tur == 'ters_kayit':
        d = int(veri['damga_ms'])
        aralik_ms = int(round(float(veri['aralik_saat']) * SAAT_MS))
        kapsanan = [(int(h), float(t)) for h, t in dolgular if d - aralik_ms < h <= d]
        tutar = float(veri.get('tutar', 0.0))
        if abs(-sum(t for _, t in kapsanan) - tutar) > 1e-9 * max(1.0, abs(tutar)):
            raise AyristirmaHatasi("ters kaydin kapsadigi dolgular olay tutariyla tutmuyor")
        return [(h, -t) for h, t in kapsanan]
    raise AyristirmaHatasi(f"bilinmeyen funding olayi: {tur}")


def fon_yonu(o, dolgular, gecmis) -> tuple:
    """Bacak funding olayinin (long, short) payi, OZGUN saatin bacak miktari isaretine gore (Codex T17-f).
    o: funding.FundingOlayi; dolgular: olay uygulanmadan onceki bekleyen dolgular (bacak durumu); gecmis: bacagin miktar
    gecmisi ((etkin_ms, q_sonra), ...; funding_saati'ne verilenle ayni). Gercek kayit q(d-) = veri['q'] isaretine;
    dolgu ve ters kayit parcalari (fon_parcalari) kendi saatlerinin q(h-) = q_once(gecmis, h) isaretine (dolgu yalniz
    q != 0 saatlerde yazilir)."""
    if o.tur == 'funding':
        q = float(o.veri.get('q', 0.0))
        return (o.tutar, 0.0) if q > 0 else ((0.0, o.tutar) if q < 0 else (0.0, 0.0))
    long_, short = 0.0, 0.0
    for h, t in fon_parcalari(o.tur, o.veri, dolgular):
        q = q_once(gecmis, h)
        if q > 0:
            long_ += t
        elif q < 0:
            short += t
        else:
            raise AyristirmaHatasi("dolgu saatinde bacak miktari 0")
    return long_, short


def _sk(veri, c, t):
    s = veri.barlar.get(c)
    return None if s is None else son_kapanis(s, t)


def _acilis(veri, c, t):
    s = veri.barlar.get(c)
    if s is None:
        return None
    k = bar_indeksi(s, t)
    return None if k is None else float(s.acilis[k])


def _azaltan(q_eski, dq):
    q_yeni = q_eski + dq
    return abs(q_yeni) < abs(q_eski) and q_yeni * q_eski >= 0


def ayristir(gunluk, veri: TamVeri, p: Parametreler, maliyet_k=None) -> AyristirmaSonucu:
    """maliyet_k: verilmezse gunlugun baslangic kaydindaki deger; verilip farkliysa hata (B7)."""
    kayitlar = gunluk.kayitlar()
    kararlar = [k for k in kayitlar if k.tur == 'karar']
    if not kararlar or 'carry' not in kararlar[0].veri['hedef']:
        raise AyristirmaHatasi("gunlukte Mimari B karar kaydi yok")
    bas = next(k for k in kayitlar if k.tur == 'baslangic')
    k_gunluk = float(bas.veri.get('maliyet_k', 1.0))
    if maliyet_k is not None and float(maliyet_k) != k_gunluk:
        raise AyristirmaHatasi(f"maliyet_k {maliyet_k} gunlukteki kosu degeriyle ({k_gunluk}) ayni degil")
    maliyet_k = k_gunluk
    nav = float(bas.veri['nav0'])
    son_ms = max(k.damga_ms for k in kayitlar if k.tur == 'nav')

    # Sanal miktar takvimi: (gecerlilik_ms, qT, qC, sC, baglam, maske kumesi).
    takvim = []
    for k in kararlar:
        cr = k.veri['hedef']['carry']
        maskeli = {c for c, m in k.veri['maske'].items() if m['maskeli']}
        takvim.append((k.damga_ms + SAAT_MS, cr['sanal_trend'], cr['sanal_carry'], cr['sc'],
                       k.veri.get('sanal_baglam', {}), maskeli))
    etkinler = [x[0] for x in takvim]
    etkin_kume = set(etkinler)

    def bacak(t):
        """t aninda (t dahil sonrasi gecerli olan) sanal miktarlar; t'den once gecerli olmus son karar."""
        i = bisect_right(etkinler, t) - 1
        return ({}, {}, {}) if i < 0 else (takvim[i][1], takvim[i][2], takvim[i][3])

    # Bacak miktar gecmisi (funding_saati icin): (b, coin) -> [(etkin_ms, q_sonra)], yalniz degisimler.
    gecmis_tam = {}
    onceki = {'T': {}, 'C': {}}
    for etkin, qT, qC, *_ in takvim:
        for b, qd in (('T', qT), ('C', qC)):
            for c in sorted(set(qd) | set(onceki[b])):
                v = qd.get(c, 0.0)
                if v != onceki[b].get(c, 0.0):
                    gecmis_tam.setdefault((b, c), []).append((etkin, v))
            onceki[b] = qd
    bacak_durum = {'T': StratejiDurumu(nav0=0.0), 'C': StratejiDurumu(nav0=0.0)}

    olaylar = {}
    for k in kayitlar:
        olaylar.setdefault(k.damga_ms, []).append(k)

    q = {}                                  # gercek pozisyon
    saatler = list(range(bas.damga_ms, son_ms, SAAT_MS))
    satir = {s: np.zeros(len(saatler)) for s in SATIRLAR}
    trend_coin, trend_q, trend_eski, trend_yeni = {}, {}, {}, {}
    carry_coin, carry_eski, carry_yeni, artik_coin, carry_q, sc_q = {}, {}, {}, {}, {}, {}
    carry_fon_long, carry_fon_short, trend_fon_ozgun = {}, {}, {}
    bacak_funding_tur = {'T': {}, 'C': {}}

    def _dizi(d, c):
        # Dizi yalniz ilk eriste ayrilir (setdefault her cagrida sifir dizisi kurardi; Codex T15-12).
        x = d.get(c)
        if x is None:
            x = d[c] = np.zeros(len(saatler))
        return x

    def _cc(c):
        return _dizi(carry_coin, c)

    def _ce(c):
        return _dizi(carry_eski, c)

    def _cy(c):
        return _dizi(carry_yeni, c)

    def _ac(c):
        return _dizi(artik_coin, c)

    def _cq(c):
        return _dizi(carry_q, c)

    def _scq(c):
        return _dizi(sc_q, c)

    def _cfl(c):
        return _dizi(carry_fon_long, c)

    def _cfs(c):
        return _dizi(carry_fon_short, c)

    def _tc(c):
        return _dizi(trend_coin, c)

    def _tq(c):
        return _dizi(trend_q, c)

    def _te(c):
        return _dizi(trend_eski, c)

    def _ty(c):
        return _dizi(trend_yeni, c)
    nav_onceki = nav
    nav_seri = {k.damga_ms: float(k.veri['nav']) for k in kayitlar if k.tur == 'nav'}
    btc = p.btc
    pencere = p.funding_gec_kayit_gun * GUN_MS

    for n, T in enumerate(saatler):
        guncelleme = T in etkin_kume
        i_t = bisect_right(etkinler, T) - 1
        eskiT, eskiC, _ = bacak(T - 1)
        yeniT, yeniC, sc = bacak(T)
        coinler = set(q) | set(eskiT) | set(eskiC) | set(yeniT) | set(yeniC)
        ev = olaylar.get(T, [])

        # --- Funding: gercek (gunluk) ve bacaklar (motorun kurali, bacak miktar gecmisiyle; B8) ---
        gercek_fund = {}
        for k in ev:
            if k.tur in ('funding', 'funding_dolgu', 'ters_kayit'):
                gercek_fund[k.coin] = gercek_fund.get(k.coin, 0.0) + float(k.veri.get('tutar', 0.0))
        bacak_fund = {'T': {}, 'C': {}}
        if T % GUN_MS == 0:                 # gunluk budama (motorun karar kaydindaki budamayla ayni)
            for b in ('T', 'C'):
                bacak_durum[b] = kayit_uygula(bacak_durum[b], SimpleNamespace(
                    tur='karar', damga_ms=T, coin=None, miktar=None, fiyat=None,
                    veri={'evren': [], 'evren_ms': None, 'maske': {}, 'funding_budama_ms': funding_budama_ms(T, p)}))
        for b in ('T', 'C'):
            d_b = bacak_durum[b]
            for (bb, c), gec in gecmis_tam.items():
                if bb != b or c not in veri.barlar:
                    continue
                gec_t = [x for x in gec if x[0] <= T]
                if not gec_t and c not in d_b.funding_dolgu:
                    continue
                if not (gec_t and gec_t[-1][1] != 0.0) and c not in d_b.funding_dolgu \
                        and not (gec_t and gec_t[-1][0] >= T - pencere):
                    continue
                g_c = gorunum_kur(TamVeri({c: veri.barlar[c]}, {c: veri.funding[c]} if c in veri.funding else {},
                                          ()), T)
                for o in funding_saati(g_c, c, T, gec_t, d_b.funding_dolgu.get(c, ()), p,
                                       islenen=d_b.funding_islenen.get(c, ()),
                                       dolgu_kadar=d_b.funding_dolgu_kadar.get(c)):
                    bacak_fund[b][c] = bacak_fund[b].get(c, 0.0) + o.tutar
                    ft = bacak_funding_tur[b].setdefault(o.tur, {}).setdefault(c, [0, 0.0])
                    ft[0] += 1
                    ft[1] += o.tutar
                    if b == 'T':                # B5: ozgun saati kayit saatinden farkli parcalar (T18)
                        for h, t in fon_parcalari(o.tur, o.veri, d_b.funding_dolgu.get(c, ())):
                            if h != T:
                                trend_fon_ozgun.setdefault(c, []).append((n, h, t))
                    if b == 'C':                # ozgun saatin yonu (T17-f); olay uygulanmadan onceki dolgularla
                        fl, fs = fon_yonu(o, d_b.funding_dolgu.get(c, ()), gec_t)
                        if fl != 0.0:
                            _cfl(c)[n] += fl
                        if fs != 0.0:
                            _cfs(c)[n] += fs
                    d_b = kayit_uygula(d_b, SimpleNamespace(tur=o.tur, damga_ms=T, coin=c, miktar=None, fiyat=None,
                                                            veri=o.veri))
            bacak_durum[b] = d_b

        # --- Gercek dolum / uzlasma ---
        q_once = dict(q)
        gercek_maliyet = {}
        uzlasma_farki = {}
        for k in ev:
            if k.tur == 'dolum':
                c = k.coin
                ac = _acilis(veri, c, T)
                q[c] = 0.0 if k.veri.get('tam_kapanis_son') else q.get(c, 0.0) + k.miktar
                dm = (-q_once.get(c, 0.0) if k.veri.get('tam_kapanis_son') else k.miktar)
                gercek_maliyet[c] = gercek_maliyet.get(c, 0.0) + dm * (k.fiyat - ac)
            elif k.tur == 'uzlasma':
                c = k.coin
                uzlasma_farki[c] = uzlasma_farki.get(c, 0.0) + q.get(c, 0.0) * (k.fiyat - _sk(veri, c, T))
                q[c] = 0.0
            elif k.tur == 'duzeltme':
                # Canli borsa uzlasmasi: nakit farki ve miktar duzeltmesi icra artigidir (bacaklara yazilmaz).
                # Eklenen miktar T'de acilis fiyatindan girer: artik += tutar + miktar * acilis (B12).
                c = k.coin
                x = float(k.veri.get('tutar', 0.0))
                if k.miktar:
                    q[c] = q.get(c, 0.0) + k.miktar
                    orta = _acilis(veri, c, T)
                    orta = _sk(veri, c, T) if orta is None else orta
                    x += k.miktar * (orta or 0.0)
                uzlasma_farki[c] = uzlasma_farki.get(c, 0.0) + x
        q_sonra = dict(q)
        for k in ev:                        # uzlasmada pozisyon T aninda kapanir: eski miktar fiyat P&L'i almaz
            if k.tur == 'uzlasma':
                q_once[k.coin] = 0.0

        # --- Fiyat ve bacak maliyeti ---
        coinler |= set(q_once) | set(q_sonra)
        bacak_maliyet = {'T': {}, 'C': {}}
        artik = {}
        for c in sorted(coinler):
            q_cv = (yeniC if guncelleme else eskiC).get(c, 0.0)
            if q_cv != 0.0 or c in carry_q:
                _cq(c)[n] = q_cv
            sk0, sk1 = _sk(veri, c, T), _sk(veri, c, T + SAAT_MS)
            if sk0 is None or sk1 is None:
                continue
            ac = _acilis(veri, c, T)
            orta = ac if ac is not None else sk0

            def fiyat(q0, q1):
                return q0 * (orta - sk0) + q1 * (sk1 - orta)
            qT0, qC0 = eskiT.get(c, 0.0), eskiC.get(c, 0.0)
            qT1, qC1 = (yeniT.get(c, 0.0), yeniC.get(c, 0.0)) if guncelleme else (qT0, qC0)
            pt, pc = fiyat(qT0, qT1), fiyat(qC0, qC1)
            if pt != 0.0 or qT0 != 0.0 or qT1 != 0.0:
                _tc(c)[n] += pt
                _tq(c)[n] = qT1
                _te(c)[n] += qT0 * (orta - sk0)
                _ty(c)[n] += qT1 * (sk1 - orta)
            if pc != 0.0 or qC0 != 0.0 or qC1 != 0.0:
                _cc(c)[n] += pc
                _ce(c)[n] += qC0 * (orta - sk0)
                _cy(c)[n] += qC1 * (sk1 - orta)
            if c == btc:
                satir['trend_fiyat'][n] += pt
                satir['hedge_fiyat'][n] += pc
            else:
                satir['trend_fiyat'][n] += pt
                satir['carry_fiyat'][n] += pc
            if guncelleme and ac is not None:
                for b, q0, q1 in (('T', qT0, qT1), ('C', qC0, qC1)):
                    dq = q1 - q0
                    if abs(dq) <= 1e-12 * max(abs(q0), abs(q1)):     # sayisal artik; islem degil
                        continue
                    bg = takvim[i_t][4].get(c)
                    if bg is None:
                        raise AyristirmaHatasi(f"sanal bacak maliyet baglami yok: {c}")
                    bg = MaliyetBaglami.jsondan(bg)
                    s = veri.barlar[c]
                    kb = bar_indeksi(s, T)
                    ln_hl = abs(math.log(s.yuksek[kb] / s.dusuk[kb])) if s.dusuk[kb] > 0 else 0.0
                    sb = veri.barlar.get(btc)
                    kbb = bar_indeksi(sb, T) if sb is not None else None
                    btc_hl = abs(math.log(sb.yuksek[kbb] / sb.dusuk[kbb])) if kbb is not None and sb.dusuk[kbb] > 0 else 0.0
                    maske = c in takvim[i_t][5] and q1 == 0.0
                    ml = maliyet_hesapla(maliyet_k, bg.v60, bg.btc_eth, _azaltan(q0, dq), maske, ln_hl, bg.sigma_1h,
                                         btc_hl, bg.btc_sigma_1h, bg.sigma_d_bps, abs(dq) * ac, p)
                    bacak_maliyet[b][c] = abs(dq) * ac * ml.toplam_bps / 10_000.0
                    if b == 'C':
                        _cc(c)[n] -= bacak_maliyet[b][c]
                        we, wy = _bolus(q0, q1)
                        _ce(c)[n] -= we * bacak_maliyet[b][c]
                        _cy(c)[n] -= wy * bacak_maliyet[b][c]
                    if b == 'T':
                        _tc(c)[n] -= bacak_maliyet[b][c]
                        we, wy = _bolus(q0, q1)
                        _te(c)[n] -= we * bacak_maliyet[b][c]
                        _ty(c)[n] -= wy * bacak_maliyet[b][c]
            # Icra artigi: e = q - qT - qC.
            e0 = q_once.get(c, 0.0) - qT0 - qC0
            e1 = q_sonra.get(c, 0.0) - qT1 - qC1
            artik[c] = fiyat(e0, e1)
        # Sirali: kayan nokta toplama sirasi surec hash tohumundan bagimsiz olmali (Codex T12-2).
        for c in sorted(set(gercek_fund) | set(bacak_fund['T']) | set(bacak_fund['C'])):
            fund_t, fund_c = bacak_fund['T'].get(c, 0.0), bacak_fund['C'].get(c, 0.0)
            satir['trend_funding'][n] += fund_t
            if fund_t != 0.0:
                _tc(c)[n] += fund_t
                _te(c)[n] += fund_t
            satir['hedge_funding' if c == btc else 'carry_funding'][n] += fund_c
            if fund_c != 0.0:
                _cc(c)[n] += fund_c
                _ce(c)[n] += fund_c
            artik[c] = artik.get(c, 0.0) + gercek_fund.get(c, 0.0) - fund_t - fund_c
        for c, x in uzlasma_farki.items():
            artik[c] = artik.get(c, 0.0) + x
        for c in sorted(artik):
            if artik[c] != 0.0 or c in artik_coin:
                _ac(c)[n] += artik[c]
        lm_t, lm_c = sum(bacak_maliyet['T'].values()), sum(bacak_maliyet['C'].values())
        satir['trend_maliyet'][n] = lm_t
        satir['carry_maliyet'][n] = lm_c
        satir['netleme'][n] = lm_t + lm_c - sum(gercek_maliyet.values())
        satir['icra_artigi'][n] = sum(artik.values())
        # s^C: T'de gecerli olan son kararin payi ([D 01:00, D+1 01:00) araligi). Tuketilen vektor sc_q'ya yazilir
        # (artigi olmayan isimler dahil; T17-e); toplam ayni degerlerle ayni sirada alinir.
        sc_n = {c: sc.get(c, 0.0) for c in sorted(set(sc) | set(artik))}
        for c, v in sc_n.items():
            if v != 0.0:
                _scq(c)[n] = v
        satir['artik_carry'][n] = sum(sc_n[c] * a for c, a in artik.items())
        satir['artik_trend'][n] = satir['icra_artigi'][n] - satir['artik_carry'][n]
        nav_simdi = nav_seri.get(T + SAAT_MS)
        satir['dnav'][n] = np.nan if nav_simdi is None else nav_simdi - nav_onceki
        if nav_simdi is not None:
            nav_onceki = nav_simdi

    toplam_bilesen = (satir['trend_fiyat'] + satir['trend_funding'] + satir['carry_fiyat'] + satir['carry_funding']
                      + satir['hedge_fiyat'] + satir['hedge_funding'] - satir['trend_maliyet'] - satir['carry_maliyet']
                      + satir['netleme'] + satir['icra_artigi'])
    # dnav yalniz gun sonu NAV kayitlarinda bilinir; ozdeslik gunluk toplamda sinanir.
    gun = {}
    for n, T in enumerate(saatler):
        gun.setdefault((T // GUN_MS) * GUN_MS, []).append(n)
    gunluk_t = {s: {g_: float(np.nansum(satir[s][ix])) for g_, ix in gun.items()} for s in SATIRLAR}
    hata = 0.0
    for g_, ix in gun.items():
        dn = satir['dnav'][ix]
        if np.isnan(dn).all():
            continue
        fark = abs(float(np.nansum(dn)) - float(toplam_bilesen[ix].sum()))
        hata = max(hata, fark) if math.isfinite(fark) else math.inf      # NaN gizlenmez (Codex T13-3)
    return AyristirmaSonucu(saat_ms=np.array(saatler, dtype=np.int64), satirlar=satir, gunluk=gunluk_t,
                            ozdeslik_max_hata=hata, toplam={s: float(np.nansum(satir[s])) for s in SATIRLAR},
                            trend_coin=trend_coin, trend_q=trend_q, trend_eski=trend_eski, trend_yeni=trend_yeni,
                            carry_coin=carry_coin, carry_eski=carry_eski, carry_yeni=carry_yeni, artik_coin=artik_coin,
                            bacak_funding_tur=bacak_funding_tur, carry_q=carry_q, sc_q=sc_q,
                            carry_fon_long=carry_fon_long, carry_fon_short=carry_fon_short,
                            trend_fon_ozgun=trend_fon_ozgun)
