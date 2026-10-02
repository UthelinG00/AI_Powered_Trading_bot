"""hedef_agirlik, Mimari B (saf). MIMARI Ss4.5 sira ozeti:
trend birim kitabi (Ss3.3) -> L -> [Pazartesi: carry Ss4.4 adim 1-7] -> carry adim 0 (hafta ici cikis + yeniden
notrleme + hedge + T4-c) -> net isim tavani -> brut -> S1/S2 -> kappa -> trend bandi -> yeniden sinama (tavanlar,
T4-d) -> (karar adiminda) lot yuvarlama.

Ag, dosya, config veya durum erisimi yoktur. Ortak Sigma_hat (Ss3.2): o gun hedefe giren butun coinler (A_t, son
Pazartesi'nin carry adaylari ve tutulan carry isimleri, BTC, sifir-disi sabitler) tek matriste; trend ve carry alt
bloklarini kullanir. Hafta icinde de son Pazartesi aday listesi kapsamda kalir (inceleme B15).

Sira ve yorumlar (ILERLEME_SLICE3.md Y9-Y10 ve Tur-5 B1-B17; spesifikasyonu genisletmez):
- Y9 Islem disi coin net agirliginda sabittir (K8); cozucude degismez; sanal trend miktari degismez.
- K13 (V60 < 20M) iki yerde: (i) trend bilesenine, CozucuDEN ONCE, onceki sanal trend degerine gore yalniz azaltma
  (sanal bacak girisi olmaz; §6.1 <20M dilimi yalniz cikista tanimli); (ii) net kitaba, gercek agirliga (w0) gore
  yalniz azaltma (gercek dusuk hacimli giris olmaz; A ile ayni). Inceleme B4.
- Reduce-only (Ss2.6) ve K13(ii) yeniden sinamadan sonra, T4-d'den ONCE uygulanir; T4-d nihai HedefKitap uzerinde
  denetlenir (A ile ayni sira; inceleme B5). Bu sira ve asagidaki istisnalar MIMARI Ss4.1, Ss4.5 sira ozeti ve Ss4.7'ye
  yazildi (2026-09-29). Sanal bacaklar reduce-only/K13(ii)'den etkilenmez (fark icra artigina
  gider, Ss4.7); T4-d olceklemesi ise net kitapla birlikte sanal bacaklara da uygulanir.
- Adim 6 yeniden sinamasi net_cozucu.ihlaller ile (ayni tolerans; B2). Ihlal eden taraf NET isaretten (ve trend
  isaretinden) belirlenir; ihlal surerse butun trend bantlari kapanir ve kitap cozucu ciktisina doner (B3).
- Bantta ya da K13(i)'de onceki degerde tutulan sanal trend miktari birebir onceki miktardir (B6).
- Sanal carry: q^C,v_alt = kappa_etkin * q^C*, kappa_etkin = kappa * son care * T4-d * T4-c katsayilari; BTC hedge
  q^C,v_BTC = kappa * son care * T4-d * w^C_BTC,t * NAV / P_BTC (w^C_BTC,t T4-c sonrasi). Ss4.7'deki "kappa^C * q^C*"
  tanimi guvenlik olceklemeleri baglamadiginda kappa_etkin = kappa ile aynidir (B16). Net hedef = sanal trend +
  sanal carry (serbest isimler, yalniz azaltma uygulanmayan gunler).
"""
import math
from datetime import datetime, timezone

import numpy as np

from .bant import bant_uygula
from .boyutlama import birim_kitap
from .carry import (aday_degerlendir, beta_tahmin, f30, gunluk_blok, hafta_ici_cikis_mi, hafta_ici_guncelle,
                    haftalik_kitap, notrle)
from .durum import StratejiDurumu, nav_hesapla
from .gorunum import GUN_MS, SAAT_MS, PiyasaGorunumu, bar_indeksi, gun_takvimi, ilk_bar_ms, son_kapanis, v60
from .hedef import (HedefHatasi, HedefKitap, KararGirdileri, boyut_sigmalari, coin_gunluk, karar_bosluklari,
                    v_norm)
from .hijyen import MaskeKaydi, gunluk_hijyen
from .net_cozucu import TOL, ihlaller, net_coz, net_isim_tavanlari
from .risk import kovaryans_hazirla
from .sinyal import trend_sinyali
from .tavanlar import _dis_bukey_katsayi
from .tipler import Parametreler


def pazartesi_mi(t_ms: int) -> bool:
    return t_ms % GUN_MS == 0 and datetime.fromtimestamp(t_ms / 1000, tz=timezone.utc).weekday() == 0


def sc_paylari(q_t: dict, q_c: dict, sc_son: dict, coinler) -> tuple:
    """MIMARI Ss4.7 carry payi s^C_i = |q^C,v| / (|q^T,v| + |q^C,v|); ikisi 0 ise son sifir-disi pay, yoksa 0.
    Doner (s^C, guncel sc_son). Tek fonksiyon (CARRY Ss5.1 V5)."""
    sc, son = {}, dict(sc_son)
    for c in coinler:
        a, b = abs(q_t.get(c, 0.0)), abs(q_c.get(c, 0.0))
        if a + b > 0:
            sc[c] = b / (a + b)
            son[c] = sc[c]
        else:
            sc[c] = sc_son.get(c, 0.0)
    return sc, son


def _yalniz_azalt(x: float, ref: float) -> float:
    """|x| <= |ref|, isaret korunur ya da 0. |x| >= |ref| ise sonuc birebir ref'tir (float gidis-donusu yok)."""
    if ref == 0.0 or x * ref <= 0:
        return 0.0
    return ref if abs(x) >= abs(ref) else x


def hedef_b(g: PiyasaGorunumu, durum: StratejiDurumu, L: float, p: Parametreler, bosluklar=None) -> tuple:
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
    haftalik = pazartesi_mi(t)
    btc = p.btc
    tanilar = {'bosluk_saat_sayisi': len(bosluklar), 'haftalik': haftalik}

    # Coin kumesi: evren, pozisyon, devreden, tutulan carry, son Pazartesi adaylari, BTC; Pazartesi butun alt adaylar.
    temel = set(durum.evren) | {c for c, q in durum.pozisyonlar.items() if q != 0.0} | set(durum.devreden) \
        | set(durum.carry_q) | set(durum.sanal_trend) | set(durum.sanal_carry) | set(durum.carry_adaylar)
    if btc in g.barlar:
        temel.add(btc)
    alt_adaylar = sorted(c for c in g.adaylar if c not in (p.btc, p.eth) and c not in p.carry_haric) if haftalik else []
    diger = sorted((temel | set(alt_adaylar)) - set(durum.evren))
    coinler = tuple(durum.evren) + tuple(diger)
    ilkler = [ilk_bar_ms(g.barlar[c]) for c in coinler if c in g.barlar]
    gunler = gun_takvimi(min(ilkler) + SAAT_MS, t) if ilkler else np.array([t], dtype=np.int64)

    gunluk, islem_disi, w0, fiyat_ref, maskeli = {}, {}, {}, {}, {}
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

    evren = set(durum.evren)
    a_t = tuple(c for c in coinler if c in evren and not islem_disi[c] and not maskeli[c])
    sabit = tuple(c for c in coinler if islem_disi[c] and w0[c] != 0.0)

    # ---- Carry adaylari (Pazartesi). Histerezisteki "mevcut" = onceki Pazartesi adayi ya da tutulan isim (B14).
    q_eski = dict(durum.carry_q)
    onceki_adaylar = set(durum.carry_adaylar) | set(q_eski)
    uygun, bilgi = [], {}
    if haftalik:
        for c in alt_adaylar:
            b = aday_degerlendir(g, c, t, c in onceki_adaylar, maskeli.get(c, False), islem_disi.get(c, True), p)
            bilgi[c] = b
            if b.uygun:
                uygun.append(c)
        aday_listesi = tuple(uygun)
    else:
        aday_listesi = tuple(c for c in durum.carry_adaylar if c in g.barlar)
    carry_kume = set(aday_listesi) | set(q_eski)
    k_coinler = tuple(dict.fromkeys(list(a_t) + sorted(carry_kume) + ([btc] if btc in g.barlar else [])
                                    + [c for c in sabit]))
    sigma_k, har_n = boyut_sigmalari(g, k_coinler, gunler, gunluk, p)
    if p.sigma_tahmincisi == 'HAR':
        tanilar['har_sigma_sayisi'] = har_n
    kov = None
    if k_coinler:
        kov = kovaryans_hazirla([gunluk[c].getiriler for c in k_coinler], sigma_k, p)
        sh, s0 = kov.sigma_hat, kov.sigma_sifir
        tanilar.update({'psd_kirpilan': kov.kirpilan_ozdeger_sayisi, 'psd_frobenius': kov.frobenius_duzeltme})
    else:
        sh = s0 = np.zeros((0, 0))
    k_idx = {c: i for i, c in enumerate(k_coinler)}

    def v_fn(w: dict) -> float:
        x = np.zeros(len(k_coinler))
        for c, v in w.items():
            x[k_idx[c]] += v
        return v_norm(x, sh, s0)

    # ---- Trend birim kitabi (Ss3.3) ----
    w_birim = {}
    if a_t:
        ia = np.array([k_idx[c] for c in a_t])
        s_vek = np.array([trend_sinyali(gunluk[c].kapanislar, gunluk[c].gecerli,
                                        0.0 if math.isnan(gunluk[c].sigma_ewma) else gunluk[c].sigma_ewma, p)
                          for c in a_t])
        bk = birim_kitap(s_vek, sigma_k[ia], kov.r_hat[np.ix_(ia, ia)], sh[np.ix_(ia, ia)], s0[np.ix_(ia, ia)], p)
        if bk.v_sonrasi > p.tau * (1 + 1e-9):
            raise HedefHatasi("T4-a: guvenlik olceklemesi sonrasi V(w^u) > tau (teknik hata)")
        w_birim = {c: float(bk.w_u[i]) for i, c in enumerate(a_t)}
        tanilar.update({'n_t': len(a_t), 'm': bk.m, 'm_tilde': bk.m_tilde, 'k': bk.k, 'v_birim': bk.v_sonrasi,
                        'sinyal': {c: float(s_vek[i]) for i, c in enumerate(a_t)}})
    else:
        tanilar['n_t'] = 0

    # ---- Carry: haftalik kitap ya da hafta ici guncelleme (Ss4.4) ----
    beta = dict(durum.carry_beta)
    hafta_ms = durum.carry_hafta_ms
    lam, bagli = durum.carry_lam, durum.carry_bagli       # hafta icinde son Pazartesi degeri tasinir (B9, Ss5.8)
    carry_tan = {}
    carry_aktif = btc in g.barlar and fiyat_ref.get(btc, 0.0) > 0
    if haftalik and carry_aktif:
        btc_r = gunluk[btc].getiriler
        f30_d, sig_c, v30_d = {}, {}, {}
        r30, s_tr, beta_yeni = [], [], {}
        for c in uygun:
            cg = gunluk[c]
            f30_d[c] = f30(g.funding.get(c), t, p)
            sig_c[c] = max(cg.sigma_ewma, p.carry_sigma_taban) if not math.isnan(cg.sigma_ewma) else p.carry_sigma_taban
            v30_d[c] = bilgi[c].v30
            k30 = len(cg.kapanislar) - 1 - p.carry_r30_gun
            r = math.log(cg.kapanislar[-1] / cg.kapanislar[k30]) if k30 >= 0 and cg.gecerli[k30] else float('nan')
            r30.append(r)
            s_tr.append(trend_sinyali(cg.kapanislar, cg.gecerli,
                                      0.0 if math.isnan(cg.sigma_ewma) else cg.sigma_ewma, p))
            beta_yeni[c] = beta_tahmin(cg.getiriler, btc_r, p)[1]
        z = {}
        if uygun:
            c_skor = [f30_d[c] / sig_c[c] for c in uygun]
            z_vek = notrle(c_skor, r30, s_tr, [beta_yeni[c] for c in uygun])
            z = {c: float(z_vek[i]) for i, c in enumerate(uygun)}
        # Tutulan ama bugun uygun olmayan isimler: islem disi ise korunur (Y7), aksi halde cikar. Long funding tabani
        # bu isimlere de uygulanir (CARRY Ss3.2.2; B13); beta'lari da bu Pazartesi hesaplanir (Ss4.3; B10).
        sabit_mevcut = {}
        for c, q in q_eski.items():
            if c in z or bilgi.get(c) is None or bilgi[c].sebep != 'islem_disi' \
                    or hafta_ici_cikis_mi(g, c, t, maskeli.get(c, False), p):
                continue
            if q > 0 and f30(g.funding.get(c), t, p) < p.carry_long_funding_taban:
                continue
            sabit_mevcut[c] = q
            if c in gunluk:
                beta_yeni[c] = beta_tahmin(gunluk[c].getiriler, btc_r, p)[1]
        beta = dict(beta_yeni)
        for c in sabit_mevcut:
            beta.setdefault(c, durum.carry_beta.get(c, 1.0))
        hk = haftalik_kitap(list(uygun), z, f30_d, sig_c, beta, v30_d, q_eski, sabit_mevcut, fiyat_ref, nav, L,
                            v_fn, p)
        q_yildiz, lam, bagli = hk.q_yildiz, hk.lam, hk.bagli_bacak
        beta = {c: beta[c] for c in q_yildiz}
        hafta_ms = t
        carry_tan = {**hk.tanilar, 'z': z, 'f30': f30_d, 'olcek': hk.olcek, 'sabit_mevcut': sorted(sabit_mevcut),
                     # Kapi fiyat faktorleri x_R, x_S icin PIT siralama degerleri (CARRY Ss6.2, U-24; tek kaynak)
                     'r30': {c: (float(r30[i]) if math.isfinite(r30[i]) else None) for i, c in enumerate(uygun)},
                     's_trend': {c: (float(s_tr[i]) if math.isfinite(s_tr[i]) else None) for i, c in enumerate(uygun)}}
    else:
        q_yildiz = dict(q_eski) if carry_aktif else {}
    # Hafta ici (ve Pazartesi ayni gun) cikislar + yeniden notrleme. Hafta ici lambda ayri kaydedilir (B9).
    cikanlar = {c for c in q_yildiz if hafta_ici_cikis_mi(g, c, t, maskeli.get(c, False), p)}
    if cikanlar:
        q_yildiz, lam2, bagli2 = hafta_ici_guncelle(q_yildiz, cikanlar, fiyat_ref)
        carry_tan.update({'hafta_ici_cikis': sorted(cikanlar), 'lambda_hafta_ici': lam2, 'bagli_hafta_ici': bagli2})
    blok = gunluk_blok(q_yildiz, beta, fiyat_ref, nav, L, v_fn, p) if q_yildiz else None

    # ---- Trend bileseni, K13(i): cozucuden once, onceki sanal trend degerine gore yalniz azaltma (B4) ----
    sabit_mi = np.array([islem_disi[c] for c in coinler], dtype=bool)
    sabit_w = np.array([w0[c] if islem_disi[c] else 0.0 for c in coinler])
    btc_eth = np.array([c in (p.btc, p.eth) for c in coinler], dtype=bool)
    vT0 = np.array([durum.sanal_trend.get(c, 0.0) * fiyat_ref[c] / nav if fiyat_ref[c] > 0 else 0.0
                    for c in coinler])
    taban_alti = {c for c in coinler if c in g.barlar and v60(g.barlar[c], t, p.v60_gun) < p.hacim_taban_v60}
    wT = np.array([L * w_birim.get(c, 0.0) for c in coinler])
    for i, c in enumerate(coinler):
        if c in taban_alti and not sabit_mi[i]:
            wT[i] = _yalniz_azalt(wT[i], vT0[i])
    tanilar['hacim_tabani_alti'] = sorted(c for c in taban_alti if not islem_disi[c])
    wC = np.array([(blok.w_alt.get(c, 0.0) + (blok.w_btc if c == btc else 0.0)) if blok else 0.0 for c in coinler])

    # ---- Net cozucu (Ss4.5 adim 1-4) ----
    serbest = ~sabit_mi
    if len(coinler):
        ns = net_coz(wT, wC, sabit_w, sabit_mi, btc_eth, p)
        kappa = ns.kappa
        carry_kat = kappa * ns.global_katsayi       # net kitaba giren carry blogunun toplam katsayisi (T4-c haric)
        wT_star = np.where(sabit_mi, 0.0, ns.c_trend * wT * ns.global_katsayi)
        wC_net = np.where(sabit_mi, 0.0, kappa * wC * ns.global_katsayi)
        baglayan = list(ns.baglayan)
        tanilar.update({'cozucu': ns.tanilar, 'global_katsayi': ns.global_katsayi,
                        # Bant oncesi trend hedefi w^T* (MIMARI Ss4.5 adim 5 girdisi; CARRY V6, U-13)
                        'w_trend_yildiz': {c: float(wT_star[i]) for i, c in enumerate(coinler) if wT_star[i] != 0.0}})
    else:
        kappa, carry_kat, wT_star, wC_net, baglayan = 1.0, 1.0, np.array([]), np.array([]), []

    # ---- Trend bandi (Ss4.5 adim 5): cozucuden gecmis trend hedefine, onceki sanal trend degerine gore ----
    ust, alt = net_isim_tavanlari(btc_eth, p)
    serbest_idx = [i for i in range(len(coinler)) if serbest[i]]
    wT_b = wT_star.copy()
    if serbest_idx:
        ekstra = np.array([coinler[i] not in evren or maskeli[coinler[i]]
                           or w0[coinler[i]] > ust[i] + TOL or w0[coinler[i]] < alt[i] - TOL
                           for i in serbest_idx], dtype=bool)
        bs = bant_uygula(wT_star[serbest_idx], vT0[serbest_idx], ekstra, p)
        wT_b[serbest_idx] = bs.w

    # ---- Adim 6: yeniden sinama; ihlal eden (net) tarafin trend isimlerinde bant kapanir (B2, B3) ----
    w = wT_b + wC_net + sabit_w
    for tur in range(4):
        ih = ihlaller(w, serbest, btc_eth, p)
        if not ih:
            break
        for i in serbest_idx:
            if tur == 3:
                wT_b[i] = wT_star[i]            # son tur: butun bantlar kapanir (cozucu ciktisi)
                continue
            uzun = w[i] > 0 or wT_star[i] > 0 or wT_b[i] > 0
            kisa = w[i] < 0 or wT_star[i] < 0 or wT_b[i] < 0
            if ({'brut', 'isim'} & ih) or ('S1' in ih and uzun) or ('S2' in ih and kisa):
                wT_b[i] = wT_star[i]
        w = wT_b + wC_net + sabit_w
    if ihlaller(w, serbest, btc_eth, p):
        baglayan.append('bant_kapandi')

    # ---- Yalniz azaltma: reduce-only (Ss2.6) ve K13(ii) net kitaba, gercek agirliga gore (B4, B5) ----
    kirpilan = []
    for i, c in enumerate(coinler):
        if serbest[i] and (reduce_only or c in taban_alti):
            yeni = _yalniz_azalt(w[i], w0[c])
            if yeni != w[i]:
                kirpilan.append(c)
            w[i] = yeni
    tanilar['yalniz_azaltma'] = kirpilan        # net != sanal bacak toplami olan isimler (MIMARI Ss4.7 istisnasi)

    # ---- T4-d toplam risk kurali, nihai kitap uzerinde: V(w*) <= L*(1 + omega_C)*tau (B) ----
    lim = L * (1.0 + p.carry_omega) * p.tau
    k_pos = [coinler.index(c) for c in k_coinler]

    def v_net(vek):
        return v_norm(np.array([vek[j] for j in k_pos]), sh, s0) if k_pos else 0.0
    v1 = v_net(w)
    c_t4 = 1.0
    if v1 > lim * (1 + 1e-12):
        c_t4 = _dis_bukey_katsayi(lim, v_net(np.where(sabit_mi, w, 0.0)), v1)
        w = np.where(sabit_mi, w, w * c_t4)
        wT_b = np.where(sabit_mi, wT_b, wT_b * c_t4)
        carry_kat *= c_t4
        baglayan.append('T4d')
        v1 = v_net(w)
        if v1 > lim * (1 + 1e-9):
            if not sabit_mi.any():
                raise HedefHatasi("T4-d: olcekleme sonrasi toplam risk kurali ihlali (teknik hata)")
            tanilar['sabit_t4d_ihlali'] = True
    kalan_ih = ihlaller(w, serbest, btc_eth, p)
    if kalan_ih:
        if not sabit_mi.any():
            raise HedefHatasi(f"T4-d: net kitap tavan ihlali (teknik hata): {sorted(kalan_ih)}")
        tanilar['sabit_tavan_ihlali'] = sorted(kalan_ih)
    if sabit_mi.any() and np.any(sabit_mi & ((sabit_w > ust + TOL) | (sabit_w < alt - TOL))):
        tanilar['sabit_tavan_ihlali'] = sorted(set(tanilar.get('sabit_tavan_ihlali', [])) | {'isim'})
    tanilar['v_net'] = v1

    # ---- Sanal bacaklar (Ss4.7) ve carry payi ----
    t4c = blok.t4c_katsayi if blok else 1.0
    kappa_etkin = carry_kat * t4c
    sanal_trend, sanal_carry = {}, {}
    for i, c in enumerate(coinler):
        onceki = durum.sanal_trend.get(c, 0.0)
        if sabit_mi[i] or (wT_b[i] == vT0[i] and c_t4 == 1.0):
            q_t = onceki                                   # degismeyen bacak: birebir onceki miktar (B6)
        elif fiyat_ref[c] > 0:
            q_t = float(wT_b[i]) * nav / fiyat_ref[c]
        else:
            q_t = 0.0
        if q_t != 0.0:
            sanal_trend[c] = q_t
    for c, q in q_yildiz.items():
        v = kappa_etkin * q
        if v != 0.0:
            sanal_carry[c] = v
    if blok and blok.w_btc != 0.0 and fiyat_ref.get(btc, 0.0) > 0:
        sanal_carry[btc] = carry_kat * blok.w_btc * nav / fiyat_ref[btc]
    pay_coinler = sorted(set(sanal_trend) | set(sanal_carry) | set(durum.sc_son)
                         | {c for c, q in durum.pozisyonlar.items() if q != 0.0})
    sc, sc_son = sc_paylari(sanal_trend, sanal_carry, durum.sc_son, pay_coinler)

    carry_json = {
        'q_yildiz': {c: float(q) for c, q in sorted(q_yildiz.items())},
        'beta': {c: float(beta[c]) for c in sorted(q_yildiz)},
        'adaylar': list(aday_listesi),
        'hafta_ms': hafta_ms, 'lam': lam, 'bagli_bacak': bagli, 'kappa': kappa, 't4c_katsayi': t4c,
        'carry_katsayi': carry_kat, 'kappa_etkin': kappa_etkin, 't4d_katsayi': c_t4,
        'w_btc_hedge': (blok.w_btc if blok else 0.0), 'notr_sapma': (blok.notr_sapma if blok else 0.0),
        'sanal_trend': {c: float(v) for c, v in sorted(sanal_trend.items())},
        'sanal_carry': {c: float(v) for c, v in sorted(sanal_carry.items())},
        'sc': {c: float(v) for c, v in sorted(sc.items())}, 'sc_son': {c: float(v) for c, v in sorted(sc_son.items())},
        'tanilar': carry_tan,
    }
    hedef = HedefKitap(
        t_ms=t, coinler=coinler, w_yildiz={c: float(w[i]) for i, c in enumerate(coinler)}, w_birim=w_birim,
        w_mevcut=w0, fiyat_ref=fiyat_ref, nav=nav, a_t=a_t, sabit=tuple(c for c in coinler if islem_disi[c]),
        maskeli=tuple(c for c in coinler if maskeli[c]), reduce_only=reduce_only, baglayan=tuple(baglayan),
        tanilar=tanilar, carry=carry_json)
    girdiler = KararGirdileri(gunluk=gunluk, bosluklar=bosluklar, islem_disi=islem_disi, k_coinler=k_coinler,
                              sigma_hat=sh, sigma_sifir=s0)
    return hedef, girdiler
