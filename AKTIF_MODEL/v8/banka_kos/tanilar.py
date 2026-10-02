"""Koşu tanıları: R5, R6, R7, R14 (BANKA §3.4; §3.7 netleştirme 14; ILERLEME_BANKA BK-15). Yürütücü, birincil birimde
(R14 için demo NAV biriminde) koşunun kendi kayıtlarından hesaplar; sonuç şifreli çıktıya girer; hüküm dışıdır.

Pencere: birincil örneklem günleri, görülmüş günler hariç. Durum, günlük olayları `motor.durum.kayit_uygula` ile baştan
uygulayarak her gün sınırında (o günün 'nav' kaydı; sonraki karardan önce) alınır. Gün g'nin sonu = g + 24 saat.
"""
import math

import numpy as np

from motor.durum import StratejiDurumu, kayit_uygula
from motor.gorunum import GUN_MS, SAAT_MS, gorunum_kur, gun_takvimi, ilk_bar_ms, son_kapanis
from motor.hedef import coin_gunluk
from motor.hijyen import MaskeKaydi
from motor.tavanlar import _kayip_s1, _kayip_s2

RV_UFUK = 7


def _q(x, a):
    x = np.asarray(x, dtype=float)
    return float(np.quantile(x, a)) if len(x) else float('nan')


def _oran(pay: int, payda: int) -> float:
    return pay / payda if payda else float('nan')


def durum_izi(gunluk) -> tuple:
    """(gun_sonu, niyetler). gun_sonu: {sınır_ms: (pozisyonlar, devreden kalanları, nav)} her 'nav' kaydında (kayıt
    uygulandıktan sonra; aynı damgadaki uzlaşma ve karardan önce). niyetler: [(karar_ms, coin, kapanis_ms, kapanis_turu,
    yetismedi)]; niyet coinin devreden emri kalkınca kapanır; kapanis_turu 'dolum' | 'uzlasma' | 'iptal:<sebep>';
    yetismedi: sonraki karar kaydı anında emir hâlâ açıktı (netleştirme 17 c). Koşu sonunda açık kalan niyet
    kapanis_ms = kapanis_turu = None."""
    d = StratejiDurumu()
    gun_sonu, acik, niyetler = {}, {}, []
    for k in gunluk.kayitlar():
        d = kayit_uygula(d, k)
        if k.tur == 'nav':
            gun_sonu[k.damga_ms] = (dict(d.pozisyonlar), {c: e.kalan for c, e in d.devreden.items()},
                                    float(k.veri['nav']))
            continue
        if k.tur == 'karar':
            for v in acik.values():
                if v[0] < k.damga_ms:
                    v[1] = True
            continue
        c = k.coin
        if k.tur == 'emir_niyeti':
            acik[c] = [k.damga_ms, False]
        elif c in acik and c not in d.devreden:
            t, yet = acik.pop(c)
            tur = k.tur if k.tur in ('dolum', 'uzlasma') else f"iptal:{k.veri.get('sebep')}"
            niyetler.append((t, c, k.damga_ms, tur, yet))
    niyetler += [(t, c, None, None, yet) for c, (t, yet) in acik.items()]
    return gun_sonu, niyetler


def _pencere_gunleri(pen) -> list:
    haric = set(int(x) for x in pen.haric_gunler)
    return [int(g) for g in pen.gunler().tolist() if int(g) not in haric]


def _kararlar(gunluk, gunler: set) -> dict:
    return {k.damga_ms: k for k in gunluk.kayitlar() if k.tur == 'karar' and k.damga_ms in gunler}


def _gun_sonu_agirlik(veri, q: dict, kalan: dict, nav: float, t: int) -> dict:
    w = {}
    for c in set(q) | set(kalan):
        x = q.get(c, 0.0) + kalan.get(c, 0.0)
        if x == 0.0 or c not in veri.barlar:
            continue
        f = son_kapanis(veri.barlar[c], t)
        if f is not None:
            w[c] = x * f / nav
    return w


def r5(s, veri, p, pen, iz=None) -> dict:
    gunler = _pencere_gunleri(pen)
    kararlar = _kararlar(s.gunluk, set(gunler))
    gun_sonu, _ = iz or durum_izi(s.gunluk)
    bag = {}
    n_birim = mmax = t4a = t4a_kayit = 0
    for k in kararlar.values():
        h = k.veri['hedef']
        for ad in h.get('baglayan', []):
            bag[ad] = bag.get(ad, 0) + 1
        ta = h.get('tanilar', {})
        if 'm' in ta and 'm_tilde' in ta:
            n_birim += 1
            mmax += int(ta['m_tilde'] < ta['m'])
            if 't4a_olcekleme' in ta:                         # B karar kaydı bayrağı taşımaz (netleştirme 17 f)
                t4a_kayit += 1
                t4a += int(bool(ta['t4a_olcekleme']))
    s1_asim, s2_asim, ulasilamayan, n_gs = [], [], 0, 0
    btc_eth = (p.btc, p.eth)
    for g in gunler:
        t = g + GUN_MS
        if t not in gun_sonu:
            continue
        q, kalan, nav = gun_sonu[t]
        n_gs += 1
        ulasilamayan += int(bool(kalan))
        w = _gun_sonu_agirlik(veri, q, kalan, nav, t)
        coinler = sorted(w)
        vek = np.array([w[c] for c in coinler])
        be = np.array([c in btc_eth for c in coinler], dtype=bool)
        s1_asim.append(_kayip_s1(vek, be, p) - p.s1_sinir if len(vek) else -p.s1_sinir)
        s2_asim.append(_kayip_s2(vek, be, p) - p.s2_sinir if len(vek) else -p.s2_sinir)
    n = len(kararlar)
    return {'karar_gunu': n, 'hedef_baglama_orani': {a: _oran(v, n) for a, v in sorted(bag.items())},
            'birim_gunu': n_birim, 'mmax_baglama_orani': _oran(mmax, n_birim), 't4a_orani': _oran(t4a, t4a_kayit) if t4a_kayit == n_birim else None,
            'gun_sonu': n_gs,
            's1_asim_orani': _oran(sum(x > 0 for x in s1_asim), n_gs), 's1_en_buyuk_asim': max([0.0] + s1_asim),
            's2_asim_orani': _oran(sum(x > 0 for x in s2_asim), n_gs), 's2_en_buyuk_asim': max([0.0] + s2_asim),
            'hedefe_ulasilamayan_orani': _oran(ulasilamayan, n_gs)}


def r6(s, veri, pen, iz=None) -> dict:
    gunler = _pencere_gunleri(pen)
    gs = set(gunler)
    gun_sonu, niyetler = iz or durum_izi(s.gunluk)
    nav_bas = {}
    for g in gunler:
        if g in gun_sonu:
            nav_bas[g] = gun_sonu[g][2]
    brut = {g: 0.0 for g in nav_bas}
    maliyet = {g: 0.0 for g in nav_bas}
    fon = {g: 0.0 for g in nav_bas}
    dolgu = ters = 0
    for k in s.gunluk.kayitlar():
        g = int(k.damga_ms // GUN_MS * GUN_MS)
        if g not in nav_bas:
            continue
        if k.tur == 'dolum':
            brut[g] += abs(k.miktar * k.fiyat)
            c = k.veri['maliyet_bps'] / 10_000.0
            acilis = k.fiyat / (1.0 + c) if k.miktar > 0 else k.fiyat / (1.0 - c)
            maliyet[g] += abs(k.miktar) * acilis * c
        elif k.tur in ('funding', 'funding_dolgu', 'ters_kayit'):
            fon[g] += float(k.veri['tutar'])
            dolgu += int(k.tur == 'funding_dolgu')
            ters += int(k.tur == 'ters_kayit')
    def yillik(x):
        v = [x[g] / nav_bas[g] for g in nav_bas]
        return 365.0 * float(np.mean(v)) if v else float('nan')
    gecikme, yetismeyen, n_niyet, turler = [], 0, 0, {}
    for karar_ms, _c, kapanis, tur, yet in niyetler:
        if int(karar_ms // GUN_MS * GUN_MS) not in gs:
            continue
        n_niyet += 1
        yetismeyen += int(yet)
        if kapanis is not None:
            gecikme.append((kapanis - karar_ms) / SAAT_MS)
        tur = tur or 'acik'
        turler[tur] = turler.get(tur, 0) + 1
    artik = []
    for g in gunler:
        t = g + GUN_MS
        if t in gun_sonu:
            q, kalan, nav = gun_sonu[t]
            artik.append(sum(abs(x) * son_kapanis(veri.barlar[c], t) for c, x in kalan.items()
                             if c in veri.barlar and son_kapanis(veri.barlar[c], t) is not None) / nav)
    return {'gun': len(nav_bas), 'tek_yon_devir_yillik': yillik(brut) / 2.0, 'maliyet_payi_yillik': yillik(maliyet),
            'funding_payi_yillik': yillik(fon), 'funding_dolgu_sayisi': dolgu, 'ters_kayit_sayisi': ters,
            'niyet': n_niyet, 'gecikme_saat_ort': float(np.mean(gecikme)) if gecikme else float('nan'),
            'gecikme_saat_q50': _q(gecikme, 0.5), 'gecikme_saat_q95': _q(gecikme, 0.95),
            'sonraki_karara_yetismeyen_orani': _oran(yetismeyen, n_niyet), 'kapanis_turleri': turler,
            'icra_artigi_ort': float(np.mean(artik)) if artik else float('nan'), 'icra_artigi_q95': _q(artik, 0.95)}


def rv_hedefleri(veri, p, maske: dict, t_son_ms: int) -> tuple:
    """Her coin için ortak gün takviminde `hedef.coin_gunluk` getirileri (koşu sonundaki görünüm ve maske geçmişi;
    maske dönemleri ve işlem dışı günler kaydın kendisinden). Doner (gunler, {coin: getiriler})."""
    g = gorunum_kur(veri, t_son_ms)
    ilkler = [ilk_bar_ms(s) for s in veri.barlar.values()]
    gunler = gun_takvimi(min(ilkler) + SAAT_MS, t_son_ms)
    return gunler, {c: coin_gunluk(g, c, gunler, maske.get(c, MaskeKaydi()), p).getiriler for c in veri.barlar}


def r7(s, veri, p, pen, r_birincil, L: float, t_son_ms: int, mimari: str) -> dict:
    r = np.asarray(r_birincil, dtype=float)
    out = {'gerceklesen_vol_orani': float(np.std(r, ddof=1)) * math.sqrt(365) / (L * p.tau) if len(r) > 1
           else float('nan')}
    if mimari != 'A':
        return out
    gunler_p = _pencere_gunleri(pen)
    kararlar = _kararlar(s.gunluk, set(gunler_p))
    gunler, getiri = rv_hedefleri(veri, p, s.durum.maske, t_son_ms)
    ix = {int(g): i for i, g in enumerate(gunler.tolist())}
    oran, n_t4a, n_gun = [], 0, 0
    for t, k in sorted(kararlar.items()):
        ta = k.veri['hedef'].get('tanilar', {})
        if 'k' not in ta:
            continue
        n_gun += 1
        if ta.get('t4a_olcekleme'):
            n_t4a += 1
            continue
        wu, sinyal = k.veri['hedef']['w_birim'], ta.get('sinyal', {})
        for c, w in wu.items():
            sg = sinyal.get(c, 0.0)
            if w == 0.0 or sg == 0.0 or c not in getiri or t not in ix:
                continue
            sigma = ta['k'] * sg / w
            i = ix[t]
            if sigma <= 0 or i + RV_UFUK >= len(gunler):
                continue
            rr = getiri[c][i + 1:i + 1 + RV_UFUK]
            if len(rr) < RV_UFUK or np.isnan(rr).any():
                continue
            y = float(np.sum(rr * rr)) * 365.0 / RV_UFUK
            if y > 0:
                oran.append(y / (sigma * sigma))
    out.update({'rv_sigma2_q50': _q(oran, 0.5), 'rv_sigma2_q95': _q(oran, 0.95), 'rv_sigma2_q99': _q(oran, 0.99),
                'gozlem': len(oran), 'karar_gunu': n_gun, 't4a_disarida_orani': _oran(n_t4a, n_gun)})
    return out


def r14(s, pen, mimari: str, btc: str = 'BTCUSDT', iz=None) -> dict:
    gunler = _pencere_gunleri(pen)
    gs = set(gunler)
    niyet = {}
    for k in s.gunluk.kayitlar():
        if k.tur == 'emir_niyeti' and k.damga_ms in gs:
            niyet.setdefault(k.damga_ms, set()).add(k.coin)
    fark = uretilmeyen = 0
    btc_gun = btc_sifir = 0
    gun_sonu, _ = iz or durum_izi(s.gunluk)
    for t, k in sorted(_kararlar(s.gunluk, gs).items()):
        h = k.veri['hedef']
        sabit = set(h.get('sabit', []))
        for c, w in k.veri['bantli'].items():
            if c in sabit or abs(w - h['w_mevcut'].get(c, 0.0)) == 0.0:
                continue
            fark += 1
            uretilmeyen += int(c not in niyet.get(t, set()))
        if mimari == 'B' and k.veri['bantli'].get(btc, 0.0) != 0.0 and t + GUN_MS in gun_sonu:
            btc_gun += 1
            btc_sifir += int(gun_sonu[t + GUN_MS][0].get(btc, 0.0) == 0.0)
    out = {'fark_olan': fark, 'lot_minnotional_alti_orani': _oran(uretilmeyen, fark)}
    if mimari == 'B':
        out.update({'btc_hedefli_gun': btc_gun, 'btc_sifir_orani': _oran(btc_sifir, btc_gun)})
    return out


def birincil_tanilari(s, veri, p, pen, r_birincil, L: float, t_son_ms: int, mimari: str) -> dict:
    iz = durum_izi(s.gunluk)
    return {'R5': r5(s, veri, p, pen, iz), 'R6': r6(s, veri, pen, iz),
            'R7': r7(s, veri, p, pen, r_birincil, L, t_son_ms, mimari)}


# ---- 3. parça (BANKA §3.7 netleştirme 15; BK-16): R2/R4 piyasa serileri, R13 (b), R17 ------------------------------

def _gun_kapanislari(veri, c, gunler_ms: np.ndarray) -> np.ndarray:
    from motor.gorunum import gunluk_kapanislar
    s = veri.barlar.get(c)
    return gunluk_kapanislar(s, gunler_ms) if s is not None else np.full(len(gunler_ms), np.nan)


def piyasa_serileri(s, veri, p, pen, bas_ms: int, bit_ms: int, iz=None) -> dict:
    """(a) r_BTC, r_alt (PIT evren, BTC/ETH hariç, eşit ağırlıklı) ve (b) pozisyon bazında BTC katkısı ile artık katkı;
    gün g ∈ [bas, bit). Gün başı ağırlık: g sınırındaki 'nav' kaydı anındaki durum (aynı damgadaki uzlaşmadan önce;
    netleştirme 17 d). Tanımsız değer None."""
    from banka.pnl import coin_pnl
    gun_sonu, _ = iz or durum_izi(s.gunluk)
    gunler = np.arange(bas_ms, bit_ms, GUN_MS, dtype=np.int64)
    uzun = np.append(gunler, bit_ms)
    btc_eth = {p.btc, p.eth}
    kap_btc = _gun_kapanislari(veri, p.btc, uzun)
    r_btc = kap_btc[1:] / kap_btc[:-1] - 1.0
    evrenler = {k.damga_ms: k.veri['evren'] for k in s.gunluk.kayitlar() if k.tur == 'karar'}
    uyeler = sorted({c for g in gunler.tolist() for c in evrenler.get(int(g), []) if c not in btc_eth})
    kap = {c: _gun_kapanislari(veri, c, uzun) for c in uyeler}
    r_alt = np.full(len(gunler), np.nan)
    for i, g in enumerate(gunler.tolist()):
        rr = [kap[c][i + 1] / kap[c][i] - 1.0 for c in evrenler.get(int(g), []) if c in kap
              and np.isfinite(kap[c][i]) and np.isfinite(kap[c][i + 1]) and kap[c][i] > 0]
        if rr:
            r_alt[i] = float(np.mean(rr))
    # (b) Pozisyon bazında katkı: gün başı ağırlık (önceki gün sonu), coinin günlük P&L'i / NAV_gün başı.
    nav_ms = np.asarray(s.nav_ms, dtype=np.int64)
    nav = np.asarray(s.nav, dtype=float)
    nav0 = next(float(k.veri['nav0']) for k in s.gunluk.kayitlar() if k.tur == 'baslangic')

    def nav_fn(t):
        i = int(np.searchsorted(nav_ms, t))
        return float(nav[i]) if i < len(nav_ms) and nav_ms[i] == t else nav0
    w_bas = []
    for g in gunler.tolist():
        q, _, nv = gun_sonu.get(int(g), ({}, {}, nav_fn(int(g))))
        w = {}
        for c, x in q.items():
            f = son_kapanis(veri.barlar[c], int(g)) if x != 0.0 and c in veri.barlar else None
            if f is not None:
                w[c] = x * f / nv
        w_bas.append(w)
    nav_bas = np.array([nav_fn(int(g)) for g in gunler.tolist()])
    cp = coin_pnl(s, veri)
    gun_ix = (np.asarray(cp.saat_ms, dtype=np.int64) // GUN_MS) * GUN_MS
    pnl_gun = {}
    ix = {int(g): i for i, g in enumerate(gunler.tolist())}
    for c, x in cp.pnl.items():
        a = np.zeros(len(gunler))
        for g, v in zip(gun_ix.tolist(), np.asarray(x, dtype=float).tolist()):
            if g in ix:
                a[ix[g]] += v
        pnl_gun[c] = a / nav_bas
    haric = set(int(x) for x in pen.haric_gunler)
    ornek = np.array([pen.bas_ms <= int(g) < pen.bit_ms and int(g) not in haric for g in gunler.tolist()])
    beta, beta_yok = {}, 0
    for c in sorted(set(pnl_gun) | {c for w in w_bas for c in w}):
        kc = _gun_kapanislari(veri, c, uzun)
        rc = kc[1:] / kc[:-1] - 1.0
        m = ornek & np.isfinite(rc) & np.isfinite(r_btc)
        if m.sum() >= 30 and np.var(r_btc[m]) > 0:
            beta[c] = float(np.cov(rc[m], r_btc[m], ddof=1)[0, 1] / np.var(r_btc[m], ddof=1))
        else:
            beta[c], beta_yok = 0.0, beta_yok + 1
    btc_katki = np.array([sum(w.get(c, 0.0) * beta.get(c, 0.0) for c in w) for w in w_bas]) * np.nan_to_num(r_btc)
    toplam = np.sum([pnl_gun[c] for c in pnl_gun], axis=0) if pnl_gun else np.zeros(len(gunler))

    def liste(x):
        return [float(v) if np.isfinite(v) else None for v in np.asarray(x, dtype=float).tolist()]
    return {'bas_ms': int(bas_ms), 'r_btc': liste(r_btc), 'r_alt': liste(r_alt), 'btc_katki': liste(btc_katki),
            'artik_katki': liste(toplam - btc_katki), 'beta_coin': len(beta), 'beta_yok': beta_yok}


def r13b(veri, filtreler: dict, bas_ms: int, bit_ms: int, nav0: float) -> dict:
    gunler = np.arange(bas_ms, bit_ms, GUN_MS, dtype=np.int64)
    nom = []
    for c in sorted(veri.adaylar):
        adim = (filtreler.get(c) or (0.0, 0.0))[0]
        if not adim or adim <= 0:
            continue
        k = _gun_kapanislari(veri, c, gunler)
        ok = np.flatnonzero(np.isfinite(k))
        if len(ok):
            nom.append(adim * float(k[ok[0]]))
    return {'coin': len(nom), 'q50': _q(nom, 0.5), 'q95': _q(nom, 0.95), 'en_buyuk': max(nom) if nom else float('nan'),
            'nav_yuzde1_ustu': int(sum(x > 0.01 * nav0 for x in nom))}


def r17_sayimlar(s, pen, veri, p) -> dict:
    gunler = _pencere_gunleri(pen)
    gs = set(gunler)
    maske_gunu = 0
    for m in s.durum.maske.values():
        if m.donemler:
            maske_gunu += sum(1 for g in gunler if m.gunde_maskeli(g))
    dolgu = 0
    evren_n = []
    for k in s.gunluk.kayitlar():
        g = int(k.damga_ms // GUN_MS * GUN_MS)
        if k.tur == 'funding_dolgu' and g in gs:
            dolgu += len(k.veri.get('saatler', []))
        elif k.tur == 'karar' and g in gs:
            evren_n.append(len(k.veri['evren']))
    # Netleştirme 17 g (T22): boşluk saatleri birimin kendi verisinde motorun taramasıyla, pencerenin tamamı.
    from motor.gorunum import bosluk_taramasi
    kume, _ = bosluk_taramasi(gorunum_kur(veri, pen.bit_ms), pen.bas_ms, pen.bit_ms, p.borsa_bosluk_oran, None)
    bosluk_kume = sum(1 for h in kume if int(h // GUN_MS * GUN_MS) in gs)
    return {'maske_gunu': maske_gunu, 'dolgu_saati': dolgu, 'bosluk_saati': bosluk_kume,
            'evren_ort': float(np.mean(evren_n)) if evren_n else float('nan')}


# ---- R8, B ayrıştırması (BANKA §3.7 netleştirme 16; BK-17) --------------------------------------------------------

R8_SATIRLARI = ('trend_fiyat', 'trend_funding', 'trend_maliyet', 'carry_fiyat', 'carry_funding', 'carry_maliyet',
                'hedge_fiyat', 'hedge_funding', 'netleme', 'icra_artigi', 'artik_carry', 'artik_trend')


def r8_satirlari(a, bas_ms: int, bit_ms: int, nav_gunluk) -> dict:
    """Ayrıştırma satırlarının günlük toplamı / NAV_gün başı, gün g ∈ [bas, bit)."""
    gunler = np.arange(bas_ms, bit_ms, GUN_MS, dtype=np.int64).tolist()
    nav = np.asarray(nav_gunluk, dtype=float)[:len(gunler)]
    return {sa: [float(a.gunluk[sa].get(int(g), 0.0)) / float(nav[i]) for i, g in enumerate(gunler)]
            for sa in R8_SATIRLARI}


def trend_bacagi(sat: dict) -> list:
    return (np.asarray(sat['trend_fiyat']) + np.asarray(sat['trend_funding']) - np.asarray(sat['trend_maliyet'])).tolist()


def carry_bacagi(sat: dict) -> list:
    return (np.asarray(sat['carry_fiyat']) + np.asarray(sat['carry_funding']) - np.asarray(sat['carry_maliyet'])
            + np.asarray(sat['hedge_fiyat']) + np.asarray(sat['hedge_funding'])).tolist()


# ---- Codex T21 2. parça (netleştirme 16 d, 17 h) -----------------------------------------------------------------

def b8_serisi(s, veri, bas_ms: int, bit_ms: int, nav_gunluk) -> list:
    """B8 girdisi, gün g ∈ [bas, bit): (ΔNAV − gerçek funding nakdi) / NAV_gün başı (BANKA §3.7 netleştirme 3;
    `banka.degerlendirme.birincil_olcum`'un r_b8'iyle aynı tanım; %90 GA için saklanır)."""
    from banka.pnl import coin_pnl
    gunler = np.arange(bas_ms, bit_ms, GUN_MS, dtype=np.int64)
    ix = {int(g): i for i, g in enumerate(gunler.tolist())}
    cp = coin_pnl(s, veri)
    fon = np.zeros(len(gunler))
    gun = (np.asarray(cp.saat_ms, dtype=np.int64) // GUN_MS) * GUN_MS
    for v in cp.funding.values():
        for g, x in zip(gun.tolist(), np.asarray(v, dtype=float).tolist()):
            if g in ix:
                fon[ix[g]] += x
    nav = np.asarray(nav_gunluk, dtype=float)[:len(gunler) + 1]
    return ((np.diff(nav) - fon) / nav[:-1]).tolist()


def carry_epizot_payi(a, pen) -> dict:
    """R8 (netleştirme 16 d): carry sanal bacağının B5 kuralıyla epizotları (`banka.pnl.epizot_pnl`; özgün saat funding
    atfı yok); pay = en iyi 3 epizot / carry bacağı net P&L'i (pencere, görülmüş saatler maskeli)."""
    from banka import olcutler as o
    from banka.pnl import epizot_pnl
    sm_tam = pen.saat_maskesi(a.saat_ms)
    ic = (a.saat_ms >= pen.bas_ms) & (a.saat_ms < pen.bit_ms)
    sm = sm_tam[ic]
    ilk = int(np.argmax(ic)) if ic.any() else 0
    epizotlar, payda = [], 0.0
    for c in sorted(a.carry_coin):
        q_tam = a.carry_q.get(c, np.zeros(len(a.saat_ms)))
        q_once = float(q_tam[ilk - 1]) if ilk > 0 else 0.0
        epizotlar += epizot_pnl(q_tam[ic], a.carry_eski[c][ic] * sm, a.carry_yeni[c][ic] * sm, q_once)
        payda += float((a.carry_coin[c][ic] * sm).sum())
    return {'pay': o.epizot_payi(epizotlar, payda) if epizotlar else None, 'epizot': len(epizotlar), 'payda': payda}
