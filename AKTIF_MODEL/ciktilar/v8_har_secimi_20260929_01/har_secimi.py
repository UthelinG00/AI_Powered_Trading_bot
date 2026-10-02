"""v8 kilit adim 2: HAR/EWMA secimi (ON-KAYIT: ONKAYIT.md; MIMARI Ss1b). P&L'siz: strateji kosulmaz.

Kullanim: python har_secimi.py              -> sonuc.json (ayrinti), ekrana ozet. BAGLAYICI D kosusu.
          python har_secimi.py --sentetik  -> sonuc_sentetik.json; SENTETIK veriyle tesisat denemesi (D okunmaz).
"""
import json
import math
import sys
import time
from collections import Counter
from dataclasses import replace
from datetime import datetime, timezone
from pathlib import Path

import numpy as np

BURASI = Path(__file__).resolve().parent
V8 = BURASI.parents[1] / 'v8'
sys.path.insert(0, str(V8))

from adaptor.veri_yukleyici import tam_veri_yukle  # noqa: E402
from motor.durum import StratejiDurumu  # noqa: E402
from motor.evren import evren_sec  # noqa: E402
from motor.gorunum import (GUN_MS, SAAT_MS, aylik_secim_gunu_mu, bar_indeksi, gorunum_kur,  # noqa: E402
                           gun_takvimi)
from motor.har import (dairesel_blok_bootstrap, gunluk_rv, har_katsayi, har_log_tahmin, har_ozellik,  # noqa: E402
                       har_varyans, haftalik_hedef, qlike)
from motor.hedef import coin_gunluk, karar_bosluklari  # noqa: E402
from motor.hijyen import MaskeKaydi, gunluk_hijyen  # noqa: E402
from motor.karar import maske_ilerlet  # noqa: E402
from motor.risk import sigma_ewma_tahmin  # noqa: E402
from motor.tipler import Parametreler  # noqa: E402


def ms(y, a, g):
    return int(datetime(y, a, g, tzinfo=timezone.utc).timestamp() * 1000)


T0 = ms(2023, 10, 1)
DEGERLENDIRME_BAS = ms(2024, 1, 1)
D_SON = ms(2026, 7, 1)
HAFTA = 7 * GUN_MS
SON_PAZARTESI = D_SON - HAFTA - ((D_SON - HAFTA - ms(2024, 1, 1)) % HAFTA)      # hedefi D icinde biten son Pazartesi
VERI_KIMLIGI = '5907a89bbe56adc0c65a80ad06c9e852b4e7bb58c40b000cab7615e7ddfd23f7'   # on-kayit; zorunlu (Codex T7)


class TeknikHata(RuntimeError):
    """Sonlu olmayan tahmin/kayip ya da veri kimligi uyusmazligi: karar uretilmez (on-kayit madde 11)."""


def pit_evren(veri, p):
    """T0'dan her gun maske + aylik evren (islem yok). Maske gecmisi son hedef haftasinin sonuna (SON_PAZARTESI + 7g)
    kadar ilerletilir (Codex T7); Pazartesi evreni SON_PAZARTESI'ye kadar kaydedilir.
    Doner: {pazartesi_ms: [coin, ...]}, son maske."""
    d = StratejiDurumu()
    pazartesi = {}
    t = T0
    while t <= SON_PAZARTESI + HAFTA:
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
        if t <= SON_PAZARTESI and datetime.fromtimestamp(t / 1000, tz=timezone.utc).weekday() == 0:
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


def main():
    p = Parametreler()
    sentetik = '--sentetik' in sys.argv
    t_bas = time.perf_counter()
    if sentetik:
        sys.path.insert(0, str(V8 / 'testler'))
        sys.path.insert(0, str(BURASI.parent / 'v8_hiz_20260929_01'))
        from hiz_profil import veri_uret
        from types import SimpleNamespace
        veri = veri_uret((D_SON - ms(2023, 7, 1)) // GUN_MS)
        rapor = SimpleNamespace(veri_kimligi='SENTETIK')
    else:
        veri, rapor = tam_veri_yukle()
        if rapor.veri_kimligi != VERI_KIMLIGI:
            raise TeknikHata(f"veri kimligi on-kayittakiyle ayni degil: {rapor.veri_kimligi}")
    print(f"yukleme {time.perf_counter() - t_bas:.0f} sn; veri kimligi {rapor.veri_kimligi}")
    t_bas = time.perf_counter()
    pazartesiler, maske = pit_evren(veri, p)
    print(f"PIT evren {time.perf_counter() - t_bas:.0f} sn; {len(pazartesiler)} Pazartesi")

    g_son = gorunum_kur(veri, D_SON)
    coinler = sorted({c for u in pazartesiler.values() for c in u})
    ilk = min(int(g_son.barlar[c].acilis_ms[0]) for c in coinler)
    gunler = gun_takvimi(ilk + SAAT_MS, D_SON)
    gun_idx = {int(x): i for i, x in enumerate(gunler)}
    seri = {}
    for c in coinler:
        m = maske.get(c, MaskeKaydi())
        cg = coin_gunluk(g_son, c, gunler, m, p)
        rv = gunluk_rv(g_son.barlar[c], gunler, p)
        isd = set(m.islem_disi_gunler)
        gecersiz = np.array([m.gunde_maskeli(int(x)) or int(x) in isd for x in gunler]) | np.isnan(cg.kapanislar)
        rv[gecersiz] = np.nan                     # maskeli, (d) ve gunluk kapanisi olmayan gun (Codex T7)
        seri[c] = (cg.getiriler, rv)
    btc_kapanis = coin_gunluk(g_son, p.btc, gunler, maske.get(p.btc, MaskeKaydi()), p).kapanislar

    # Satirlar: her Pazartesi x degerlendirme coini.
    satirlar, disari = [], Counter()
    for t, uyeler in sorted(pazartesiler.items()):
        i = gun_idx[t]
        for c in uyeler:
            getiri, rv = seri[c]
            oz = har_ozellik(rv, i, p)
            hedef = haftalik_hedef(getiri, i)
            gecmis = getiri[:i + 1]
            sig = sigma_ewma_tahmin(gecmis, p) if np.any(~np.isnan(gecmis)) else float('nan')
            satirlar.append({'t': t, 'c': c, 'oz': oz, 'toplam': hedef,
                             'F_E': sig * sig if sig == sig else float('nan')})

    # Yuruyen aylik katsayilar.
    aylar = []
    a = DEGERLENDIRME_BAS
    while a <= SON_PAZARTESI:
        aylar.append(a)
        y_, m_ = datetime.fromtimestamp(a / 1000, tz=timezone.utc).year, datetime.fromtimestamp(a / 1000, tz=timezone.utc).month
        a = ms(y_ + (m_ == 12), m_ % 12 + 1, 1)
    katsayi = {}
    for M in aylar:
        egitim = [r for r in satirlar if r['t'] + HAFTA <= M and r['oz'] is not None and r['toplam'] is not None]
        beta = har_katsayi([r['oz'] for r in egitim], [math.log(r['toplam']) for r in egitim], p)
        katsayi[M] = {'beta': None if beta is None else beta.tolist(), 'n_egitim': len(egitim)}

    def gecerli_ay(t):
        onceki = [M for M in aylar if M <= t]
        return onceki[-1] if onceki else None

    # Yuruyen tahmin ve artiklar.
    for r in satirlar:
        M = gecerli_ay(r['t'])
        tanimli = M is not None and r['oz'] is not None and katsayi[M]['beta'] is not None
        r['y_hat'] = float(har_log_tahmin([r['oz']], katsayi[M]['beta'])[0]) if tanimli else None
        r['katsayi_yok'] = M is not None and r['oz'] is not None and katsayi[M]['beta'] is None
        r['artik'] = (math.log(r['toplam']) - r['y_hat']) if (r['y_hat'] is not None and r['toplam']) else None

    artik_hafta = {}
    for r in satirlar:
        if r['artik'] is not None:
            artik_hafta.setdefault(r['t'], []).append(r['artik'])

    s2_yol = {}
    for t in sorted(pazartesiler):
        if t < DEGERLENDIRME_BAS:
            continue
        haftalar = [s for s in artik_hafta if t - HAFTA - (p.har_artik_hafta - 1) * HAFTA <= s <= t - HAFTA]
        if len(haftalar) >= p.har_artik_min_hafta:
            e = np.concatenate([artik_hafta[s] for s in haftalar])
            s2_yol[t] = float(np.var(e))

    # Degerlendirme.
    deger = []
    for r in satirlar:
        t = r['t']
        if t < DEGERLENDIRME_BAS or t > SON_PAZARTESI:
            continue
        if r['toplam'] is None:
            disari['hedef_tanimsiz'] += 1
            continue
        if not r['F_E'] > 0:
            disari['ewma_tanimsiz'] += 1
            continue
        if r['y_hat'] is None:
            disari['har_katsayi_tanimsiz' if r['katsayi_yok'] else 'har_ozellik_tanimsiz'] += 1
            continue
        if t not in s2_yol:
            disari['har_s2_tanimsiz'] += 1
            continue
        Y = r['toplam'] * 365.0 / 7.0
        F_H = float(har_varyans(r['y_hat'], s2_yol[t]))
        q_H, q_E = float(qlike(Y, F_H)), float(qlike(Y, r['F_E']))
        if not all(math.isfinite(x) and x > 0 for x in (Y, F_H, r['F_E'])) or not (math.isfinite(q_H) and math.isfinite(q_E)):
            raise TeknikHata(f"sonlu olmayan tahmin/kayip: {r['c']} {t} F_H={F_H} F_E={r['F_E']}")
        deger.append({'t': t, 'c': r['c'], 'Y': Y, 'F_H': F_H, 'F_E': r['F_E'], 'q_H': q_H, 'q_E': q_E})

    haftalar = sorted({d['t'] for d in deger})
    W = len(haftalar)
    sonuc = {'onkayit': 'ONKAYIT.md', 'veri_kimligi': rapor.veri_kimligi, 'satir': len(deger), 'hafta': W,
             'disarida': dict(disari), 'katsayi_yolu': {str(k): v for k, v in katsayi.items()},
             's2_yolu': {str(k): v for k, v in s2_yol.items()}}
    if W < p.har_min_hafta:
        sonuc.update({'karar': 'EWMA', 'gerekce': f'degerlendirme kumesi {W} hafta < {p.har_min_hafta}'})
    else:
        qH = np.array([d['q_H'] for d in deger])
        qE = np.array([d['q_E'] for d in deger])
        takvim = list(range(haftalar[0], haftalar[-1] + 1, HAFTA))           # takvim haftalari (bos olabilir)
        fark_hafta = [np.array([d['q_H'] - d['q_E'] for d in deger if d['t'] == t]) for t in takvim]
        boot = dairesel_blok_bootstrap(fark_hafta, p.har_boot_blok, p.har_boot_cekis, p.har_boot_tohum)
        if np.any(np.isnan(boot)):
            raise TeknikHata(f"satirsiz bootstrap cekisi: {int(np.isnan(boot).sum())}")
        ust = float(np.quantile(boot, 0.95))
        kosul_i = float(qH.mean()) <= p.har_qlike_oran * float(qE.mean())
        kosul_iv = ust < 0.0
        # Betimsel: stres haftalari (BTC'nin hedef haftasi getirisi ln(P_t+7 / P_t) en kotu %10; kapanis eksikse o
        # hafta siralamaya girmez; esitlikte erken tarih).
        btc_hafta = {}
        for t in haftalar:
            a_, b_ = btc_kapanis[gun_idx[t]], btc_kapanis[gun_idx[t] + 7]
            if a_ > 0 and b_ > 0:
                btc_hafta[t] = math.log(b_ / a_)
        n_stres = math.ceil(0.10 * W)
        stres = sorted(btc_hafta, key=lambda t: (btc_hafta[t], t))[:n_stres]
        stres_fark = [d['q_H'] - d['q_E'] for d in deger if d['t'] in set(stres)]
        oran = lambda k: {q: float(np.quantile([d['Y'] / d[k] for d in deger], q)) for q in (0.95, 0.99)}
        sonuc.update({
            'qlike_har': float(qH.mean()), 'qlike_ewma': float(qE.mean()),
            'oran_har_ewma': float(qH.mean() / qE.mean()),
            'bootstrap_takvim_hafta': len(takvim),
            'bootstrap_fark_kantil': {'0.05': float(np.quantile(boot, 0.05)), '0.5': float(np.quantile(boot, 0.5)),
                                      '0.95': ust},
            'kosul_i': bool(kosul_i), 'kosul_iv': bool(kosul_iv),
            'karar': 'HAR' if (kosul_i and kosul_iv) else 'EWMA',
            'betimsel': {'stres_hafta_hedef': n_stres, 'stres_hafta_sayisi': len(stres),
                         'stres_ort_qlike_farki': float(np.mean(stres_fark)) if stres_fark else None,
                         'stres_haftalari': [str(t) for t in stres],
                         'Y_F_har_kantil': oran('F_H'), 'Y_F_ewma_kantil': oran('F_E')},
        })
    # Banka/canli icin dondurulacak katsayi (on-kayit madde 12): D'nin tamaminda ayni OLS. s^2 dondurulmaz (banka/
    # canlida yuruyen artiklardan); D sonundaki yuruyen s^2 yalniz bilgi. Karar HAR degilse yalniz kayit icindir.
    tam = [r for r in satirlar if r['t'] + HAFTA <= D_SON and r['oz'] is not None and r['toplam'] is not None]
    beta_tam = har_katsayi([r['oz'] for r in tam], [math.log(r['toplam']) for r in tam], p)
    son_t = max(s2_yol) if s2_yol else None
    sonuc['dondurulan'] = {'beta': None if beta_tam is None else beta_tam.tolist(), 'n_egitim': len(tam),
                           'son_pazartesi_yuruyen_s2_bilgi': None if son_t is None else s2_yol[son_t],
                           'son_pazartesi_ms': son_t}
    (BURASI / ('sonuc_sentetik.json' if sentetik else 'sonuc.json')).write_text(json.dumps(sonuc, ensure_ascii=False, indent=1), encoding='utf-8')
    ozet = {k: v for k, v in sonuc.items() if k not in ('katsayi_yolu', 's2_yolu')}
    print(json.dumps(ozet, ensure_ascii=False, indent=1))


if __name__ == '__main__':
    main()
