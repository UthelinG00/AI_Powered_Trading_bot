"""R3 long-beta kitabı (BANKA §3.4 R3, §3.7 netleştirme 13; ILERLEME_BANKA BK-14). Betimsel satırdır; kapıya ve hükme
girmez.

Birim kendi motor koşusudur: motorun funding, uzlaşma, bant dışı icra (devreden emir, katılım sınırı, kısmi dolum),
maliyet ve günlük kayıt döngüsü aynen kullanılır; yalnız günlük karar adımının HEDEFİ değişir (`r3_karar`):
  - Aylık evren seçimi gününde (ve ilk kararda): o günkü karar kaydının `a_t` kümesi (güncel evren, işlem dışı değil,
    maskeli değil); σ̂ aynı gün aynı kümede `hedef.boyut_sigmalari` (HAR banka takvimi, taban %20);
    w_i = Bütçe · (1/σ̂_i) / Σ_j (1/σ̂_j), yalnız long, o günün NAV'ına göre; Bütçe = max(0, 1 − a_t dışında hâlâ
    tutulan pozisyonların ağırlığı) (Codex T20); `a_t` dışındaki serbest isimlere hedef 0.
    Devreden emirler motordaki gibi yeni hedefle değiştirilir.
  - Aradaki günlerde hedef miktar sabittir (yeni emir yok, devreden emir sürer); `a_t` dışına düşen (evrenden çıkan,
    maskelenen) serbest isimde hedef 0 emri verilir. İşlem dışı isimde yeni emir yok; devreden emrin risk artıran
    parçası motorun kuralıyla iptal edilir. Serbest nakit dağıtılmaz; yeni ya da maskeden dönen isim sonraki aylık
    seçimde girer.
  - Borsa çapı boşlukta (reduce-only) hedef mevcut ağırlığı aşamaz (motorun boşluk kuralı).
M = A ve M = B'de aynı kitaptır: koşu her zaman Mimari A hedef girdileriyle (a_t, σ̂) kurulur.
Çıktı (düz, şifrelenir): gün sınırı NAV'ı, günlük brüt/net devir, maliyet ve funding payı (NAV'a oranla).
Karşılaştırma (`r3_karsilastirma`): birincil örneklem, görülmüş günler hariç; R3 getirisi birincilin gerçekleşen
vol'üne doğrusal ölçeklenir; SR farkı, korelasyon, β, α (günlük ve ×365) ve α'nın Newey-West t'si (gecikme 10).
"""
import math
from dataclasses import replace

import numpy as np

from kalibrasyon.yurutucu import muhasebe_kapisi
from motor.durum import Emir, StratejiDurumu
from motor.emir import artiran_iptali, filtre_al, lot_niyeti
from motor.evren import evren_sec
from motor.funding import funding_budama_ms
from motor.geri_test import GeriTestHatasi, KosuAyarlari, KosuSonucu, _Kosucu
from motor.gorunum import GUN_MS, SAAT_MS, aylik_secim_gunu_mu, gorunum_kur, gun_takvimi, ilk_bar_ms, sigma_1h
from motor.hedef import boyut_sigmalari, hedef_agirlik_ayrintili, karar_bosluklari
from motor.hijyen import MaskeKaydi, maske_json
from motor.karar import KararSonucu, KayitTaslagi, maliyet_baglami, maske_ilerlet

from banka import olcutler as o

NW_GECIKME = 10


def ters_sigma_agirlik(sigma) -> np.ndarray:
    """w_i = (1/σ̂_i) / Σ_j (1/σ̂_j); σ̂ > 0 (taban %20 sonrası)."""
    s = np.asarray(sigma, dtype=float)
    if not len(s) or not np.all(np.isfinite(s)) or np.any(s <= 0):
        raise ValueError("sigma sonlu ve pozitif olmali")
    t = 1.0 / s
    return t / t.sum()


def r3_butce(w_mevcut: dict, a_kume) -> float:
    """Aylık tahsis bütçesi (netleştirme 13 c; Codex T20): 1 − a_t dışında hâlâ tutulan pozisyonların ağırlığı, ≥ 0."""
    return max(0.0, 1.0 - sum(abs(w) for c, w in w_mevcut.items() if c not in a_kume))


def r3_karar(g, durum: StratejiDurumu, p, filtreler: dict = None) -> KararSonucu:
    """R3 günlük karar adımı; karar_ver ile aynı sıra ve aynı kayıt biçimi, farklı hedef (modül belgesi)."""
    filtreler = filtreler or {}
    t = g.t_ms
    bosluklar, bosluk_ref = karar_bosluklari(g, durum, p)
    maske = maske_ilerlet(g, durum, t, p, bosluklar)
    aylik = aylik_secim_gunu_mu(t) or durum.evren_ms is None
    if aylik:
        evren = evren_sec(g, t, durum.evren, maske, p).uyeler
        evren_ms = t
    else:
        evren, evren_ms = durum.evren, durum.evren_ms
    durum_bugun = replace(durum, maske=maske, evren=evren, evren_ms=evren_ms)
    hedef, girdiler = hedef_agirlik_ayrintili(g, durum_bugun, 1.0, p, bosluklar=bosluklar)

    a_t = tuple(hedef.a_t)
    a_kume = set(a_t)
    sabit = set(hedef.sabit)
    serbest = [c for c in hedef.coinler if c not in sabit]
    w_hedef = {}
    if aylik:
        if a_t:
            ilkler = [ilk_bar_ms(g.barlar[c]) for c in hedef.coinler if c in g.barlar]
            gunler = gun_takvimi(min(ilkler) + SAAT_MS, t) if ilkler else np.array([t], dtype=np.int64)
            sig, _ = boyut_sigmalari(g, a_t, gunler, girdiler.gunluk, p)
            butce = r3_butce(hedef.w_mevcut, a_kume)
            w_hedef = dict(zip(a_t, (butce * ters_sigma_agirlik(sig)).tolist()))
        for c in serbest:
            w_hedef.setdefault(c, 0.0)
    else:
        for c in serbest:
            if c not in a_kume and (durum.pozisyonlar.get(c, 0.0) != 0.0 or c in durum.devreden):
                w_hedef[c] = 0.0
    if hedef.reduce_only:                            # borsa çapı boşluk: risk artıran hedef yok (long-only kitap)
        w_hedef = {c: min(w, hedef.w_mevcut[c]) for c, w in w_hedef.items()}

    btc_s = g.barlar.get(p.btc)
    btc_sigma = sigma_1h(btc_s, t, p.sigma_1h_gun) if btc_s is not None else float('nan')

    adaylar = {}
    for c, w in w_hedef.items():
        if hedef.fiyat_ref[c] <= 0:
            continue
        adim, min_not = filtre_al(filtreler, c, p)
        dq = lot_niyeti(w, durum.pozisyonlar.get(c, 0.0), hedef.nav, hedef.fiyat_ref[c], adim, min_not)
        if dq != 0.0:
            adaylar[c] = dq

    # Devreden emirler: hedefi yenilenen isimde motorun öncelik kuralı (karar_ver); yenilenmeyen isimde emir sürer,
    # yalnız işlem dışı / reduce-only'de risk artıran parçası iptal edilir.
    iptaller = []
    for c in sorted(durum.devreden):
        e = durum.devreden[c]
        q = durum.pozisyonlar.get(c, 0.0)
        koru = c in sabit or hedef.reduce_only
        if c not in w_hedef:
            if koru:
                iptal = artiran_iptali(e.kalan, q, 'islem_disi' if c in sabit else 'borsa_bosluk')
                if iptal is not None:
                    iptaller.append((c, iptal))
            continue
        if koru and c in adaylar:
            yeni = adaylar[c]
            azaltan = e.kalan - (artiran_iptali(e.kalan, q, '') or {'iptal': 0.0})['iptal']
            if azaltan != 0.0 and not (yeni * azaltan > 0 and abs(yeni) >= abs(azaltan)):
                del adaylar[c]
            else:
                iptaller.append((c, {'iptal': e.kalan, 'tamami': True, 'tam_kapanis': False, 'sebep': 'yeni_niyet'}))
                continue
        if koru:
            iptal = artiran_iptali(e.kalan, q, 'islem_disi' if c in sabit else 'borsa_bosluk')
            if iptal is not None:
                iptaller.append((c, iptal))
        else:
            iptaller.append((c, {'iptal': e.kalan, 'tamami': True, 'tam_kapanis': False, 'sebep': 'yeni_karar'}))

    niyetler = {}
    for c, dq in adaylar.items():
        niyetler[c] = Emir(kalan=dq, karar_ms=t, maske_cikisi=bool(maske.get(c, MaskeKaydi()).maskeli and w_hedef[c] == 0.0),
                           tam_kapanis=w_hedef[c] == 0.0,
                           baglam=maliyet_baglami(g, c, t, girdiler.gunluk[c].sigma_ewma, btc_sigma, p))

    gecmis_bas = t - p.bosluk_gecmis_gun * GUN_MS
    kayitlar = [KayitTaslagi('karar', veri={
        'evren': list(evren), 'evren_ms': evren_ms, 'maske': {c: maske_json(m) for c, m in sorted(maske.items())},
        'hedef': hedef.json(), 'bantli': w_hedef, 'bosluk_ref': bosluk_ref, 'funding_budama_ms': funding_budama_ms(t, p),
        'bosluk_gecmis': sorted(h for h in bosluklar if h >= gecmis_bas), 'r3': {'aylik': aylik, 'a_t': list(a_t)}})]
    for c, iptal in iptaller:
        kayitlar.append(KayitTaslagi('devreden_iptal', coin=c, veri=iptal))
    for c, e in niyetler.items():
        kayitlar.append(KayitTaslagi('emir_niyeti', coin=c, miktar=e.kalan, veri={'emir': e.json()}))
    return KararSonucu(hedef=hedef, bantli=w_hedef, niyetler=niyetler, iptaller=tuple(iptaller), evren=evren,
                       evren_ms=evren_ms, maske=maske, kayitlar=tuple(kayitlar))


class _R3Kosucu(_Kosucu):
    def karar_adimi(self, g, T):
        sonuc = r3_karar(g, replace(self.durum, t_ms=T), self.p, self.ayar.filtreler)
        for k in sonuc.kayitlar:
            self.yaz(k.tur, T, coin=k.coin, miktar=k.miktar, fiyat=k.fiyat, karar_ms=T, veri=k.veri)
        self.bosluk_tarandi, self.bosluk_ref = T, self.durum.bosluk_ref
        return sonuc


def kos_r3(veri, ayar: KosuAyarlari, p) -> KosuSonucu:
    """motor.geri_test.kos ile birebir aynı saat döngüsü; yalnız karar adımı r3_karar."""
    if ayar.t0_ms % GUN_MS != 0:
        raise GeriTestHatasi("t0 00:00 UTC olmali")
    if ayar.t_son_ms < ayar.t0_ms or ayar.t_son_ms % SAAT_MS != 0:
        raise GeriTestHatasi("t_son >= t0 ve saat izgarasinda olmali")
    if not ayar.nav0 > 0:
        raise GeriTestHatasi("nav0 > 0 olmali")
    k = _R3Kosucu(veri, ayar, p)
    k.yaz('baslangic', ayar.t0_ms, veri={'nav0': ayar.nav0, 'L': ayar.L, 'maliyet_k': ayar.maliyet_k,
                                         'katilimsiz': ayar.katilimsiz, 'r3': True})
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


def gunluk_akislar(s, gunler_ms, nav_gunluk) -> dict:
    """Her gün [g, g+24h) için dolum ve funding kayıtlarından: brüt devir Σ|Δq·fiyat| / NAV(gün başı), net devir
    |Σ Δq·fiyat| / NAV, maliyet payı Σ|Δq|·açılış·c / NAV, funding payı Σ funding nakdi / NAV (işaretli, gelir > 0)."""
    gunler = np.asarray(gunler_ms, dtype=np.int64)
    ix = {int(g): i for i, g in enumerate(gunler.tolist())}
    brut, net, maliyet, fon = (np.zeros(len(gunler)) for _ in range(4))
    for k in s.gunluk.kayitlar():
        i = ix.get(int(k.damga_ms // GUN_MS * GUN_MS))
        if i is None:
            continue
        if k.tur == 'dolum':
            nom = k.miktar * k.fiyat
            brut[i] += abs(nom)
            net[i] += nom
            c = k.veri['maliyet_bps'] / 10_000.0
            acilis = k.fiyat / (1.0 + c) if k.miktar > 0 else k.fiyat / (1.0 - c)
            maliyet[i] += abs(k.miktar) * acilis * c
        elif k.tur == 'uzlasma':
            nom = k.miktar * k.fiyat
            brut[i] += abs(nom)
            net[i] += nom
        elif k.tur in ('funding', 'funding_dolgu', 'ters_kayit'):
            fon[i] += float(k.veri['tutar'])
    nav = np.asarray(nav_gunluk[:len(gunler)], dtype=float)
    return {'brut_devir': (brut / nav).tolist(), 'net_devir': (np.abs(net) / nav).tolist(),
            'maliyet_payi': (maliyet / nav).tolist(), 'funding_payi': (fon / nav).tolist()}


def r3_yurut(b: dict, bag) -> tuple:
    """R3 birimi (banka_kos.yurutucu.birim_yurut'tan çağrılır). Doner (duz, acik)."""
    from .yurutucu import _nav_gunluk, _takvim
    veri = bag.veri
    t_son = bag.z2_son_ms - SAAT_MS
    takvim = _takvim(veri, bag, t_son)
    p = replace(bag.parametreler, mimari='A', sigma_tahmincisi='HAR', har_takvimi=takvim, delist_h_long=b['h_L'])
    filtreler = bag.filtreler if b['lot'] else {c: (0.0, mn) for c, (_, mn) in bag.filtreler.items()}
    s = kos_r3(veri, KosuAyarlari(t0_ms=bag.motor_bas_ms, t_son_ms=t_son, L=b['L'], maliyet_k=b['maliyet_k'],
                                  nav0=b['nav0'], filtreler=filtreler), p)
    nav_g = _nav_gunluk(s, bag.t0_z1_ms, bag.z2_son_ms, b['nav0'])
    gunler = np.arange(bag.t0_z1_ms, bag.z2_son_ms, GUN_MS, dtype=np.int64)
    aylik = sum(1 for k in s.gunluk.kayitlar() if k.tur == 'karar' and k.veri.get('r3', {}).get('aylik'))
    acik = {'muhasebe': muhasebe_kapisi(s, veri, None), 'karar_sayisi': len(s.kararlar), 'aylik_karar_sayisi': aylik,
            'son_hash': s.gunluk.son_hash, 's2_pazartesi': len(takvim.s2)}
    duz = {'birim': b, 'nav_bas_ms': bag.t0_z1_ms, 'nav_gunluk': nav_g, **gunluk_akislar(s, gunler, nav_g)}
    return duz, acik


def nw_ols(y, x, gecikme: int = NW_GECIKME) -> dict:
    """y = α + β x + ε; OLS katsayıları ve Newey-West (Bartlett, gecikme L) standart hatalarıyla t değerleri."""
    y = np.asarray(y, dtype=float)
    X = np.column_stack([np.ones(len(y)), np.asarray(x, dtype=float)])
    n = len(y)
    if n < 3:
        raise ValueError("en az 3 gozlem gerekli")
    xtx_inv = np.linalg.inv(X.T @ X)
    b = xtx_inv @ X.T @ y
    e = y - X @ b
    u = X * e[:, None]
    S = u.T @ u
    for k in range(1, min(gecikme, n - 1) + 1):
        w = 1.0 - k / (gecikme + 1)
        G = u[k:].T @ u[:-k]
        S += w * (G + G.T)
    V = xtx_inv @ S @ xtx_inv
    se = np.sqrt(np.maximum(np.diag(V), 0.0))
    t = [float(b[i] / se[i]) if se[i] > 0 else float('nan') for i in range(2)]
    return {'alfa': float(b[0]), 'beta': float(b[1]), 't_alfa': t[0], 't_beta': t[1]}


def r3_karsilastirma(r_birincil, r_r3) -> dict:
    """Aynı günler (birincil örneklem, görülmüş günler hariç) üzerinde R3 karşılaştırması (§3.4 R3; netleştirme 13 g)."""
    rp = np.asarray(r_birincil, dtype=float)
    r3 = np.asarray(r_r3, dtype=float)
    if rp.shape != r3.shape:
        raise ValueError("birincil ve R3 getirileri ayni gunlerde olmali")
    # Netleştirme 17 b: betimsel satır hükmü durdurmaz; yetersiz gözlem ya da sıfır vol "tanımsız".
    if len(rp) < 3 or not (np.isfinite(rp).all() and np.isfinite(r3).all()):
        return {'durum': 'tanimsiz', 'neden': 'gozlem < 3 ya da sonlu olmayan getiri', 'gun': int(len(rp))}
    if not (float(np.std(rp, ddof=1)) > 0 and float(np.std(r3, ddof=1)) > 0):
        return {'durum': 'tanimsiz', 'neden': 'birincil ya da R3 serisinin std si 0', 'gun': int(len(rp))}
    sd3 = float(np.std(r3, ddof=1))
    olcek = float(np.std(rp, ddof=1)) / sd3 if sd3 > 0 else float('nan')
    r3s = r3 * olcek
    reg = nw_ols(rp, r3s)
    sr_p, sr_3 = o.sharpe(rp), o.sharpe(r3s)
    kor = float(np.corrcoef(rp, r3s)[0, 1]) if sd3 > 0 else float('nan')
    return {'gun': int(len(rp)), 'olcek': olcek, 'sr_birincil': sr_p, 'sr_r3': sr_3, 'sr_farki': sr_p - sr_3,
            'korelasyon': kor, 'beta': reg['beta'], 'alfa_gunluk': reg['alfa'], 'alfa_yillik': reg['alfa'] * 365.0,
            't_alfa_nw': reg['t_alfa'], 'nw_gecikme': NW_GECIKME, 'nan_yok': bool(math.isfinite(kor))}
