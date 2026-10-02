"""v8 D kisa kesit bicim ve ozdeslik denetimi (ON-KAYIT: ONKAYIT.md, koşudan once yazildi).

Yalniz bicim/ozdeslik/sure hesaplanir ve yazilir. NAV, getiri, P&L satir toplamlari ve hicbir performans olcutu
hesaplanip yazdirilmaz ya da diske yazilmaz. Ag erisimi yoktur.
Kullanim: python kesit_denetim.py
"""
import json
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
from motor.ayristirma import ayristir  # noqa: E402
from motor.durum import durum_turet  # noqa: E402
from motor.geri_test import KosuAyarlari, kos  # noqa: E402
from motor.gorunum import GUN_MS, SAAT_MS, gorunum_kur  # noqa: E402
from motor.gunluk import OlayGunlugu  # noqa: E402
from motor.hedef import isim_tavani  # noqa: E402
from motor.karar import karar_ver  # noqa: E402
from motor.net_cozucu import ihlaller  # noqa: E402
from motor.tavanlar import _kayip_s1, _kayip_s2  # noqa: E402
from motor.tipler import Parametreler  # noqa: E402

T0 = int(datetime(2023, 10, 1, tzinfo=timezone.utc).timestamp() * 1000)
GUN_SAYISI = 7
AYAR = KosuAyarlari(t0_ms=T0, t_son_ms=T0 + GUN_SAYISI * GUN_MS - SAAT_MS, L=1.0, maliyet_k=1.0, nav0=100_000.0)


def _karar_oncesi(kayitlar, t_ms):
    for i, k in enumerate(kayitlar):
        if k.damga_ms == t_ms and k.tur in ('uzlasma', 'karar'):
            return OlayGunlugu.kayitlardan(kayitlar[:i])
    raise AssertionError('karar kaydi yok')


def _karar_json(kr):
    return (kr.hedef.json(), kr.bantli, {c: e.json() for c, e in kr.niyetler.items()}, kr.iptaller, kr.evren)


def _a_degismez(h, p, L):
    w = np.array([h.w_yildiz[c] for c in h.coinler])
    if not len(w):
        return True
    be = np.array([c in (p.btc, p.eth) for c in h.coinler], bool)
    ok = h.tanilar.get('v_net', 0.0) <= L * p.tau * (1 + 1e-9)
    if 'sabit_tavan_ihlali' not in h.tanilar or not h.tanilar['sabit_tavan_ihlali']:
        for i, c in enumerate(h.coinler):
            if c not in h.sabit and abs(w[i]) > isim_tavani(c, w[i], p) + 1e-12:
                ok = False
        ok = ok and float(np.abs(w).sum()) <= p.brut_tavan + 1e-12 and _kayip_s1(w, be, p) <= p.s1_sinir + 1e-12 \
            and _kayip_s2(w, be, p) <= p.s2_sinir + 1e-12
    return bool(ok)


def _b_degismez(h, p, L):
    w = np.array([h.w_yildiz[c] for c in h.coinler])
    if not len(w):
        return True
    serbest = np.array([c not in h.sabit for c in h.coinler], bool)
    be = np.array([c in (p.btc, p.eth) for c in h.coinler], bool)
    ok = h.tanilar.get('v_net', 0.0) <= L * (1 + p.carry_omega) * p.tau * (1 + 1e-9)
    if not h.tanilar.get('sabit_tavan_ihlali'):
        ok = ok and not ihlaller(w, serbest, be, p)
    return bool(ok)


def kosu(veri, mimari):
    p = replace(Parametreler(), mimari=mimari)
    t = time.perf_counter()
    s = kos(veri, AYAR, p)
    sure_kos = time.perf_counter() - t
    kayitlar = s.gunluk.kayitlar()
    kararlar = {(k.hedef.t_ms - T0) // GUN_MS: k for k in s.kararlar}
    sonuc = {
        'mimari': mimari, 'istisna': None, 'sure_kos_sn': round(sure_kos, 1),
        'zincir_dogru': s.gunluk.dogrula(), 'kayit_sayisi': len(kayitlar),
        'kayit_turleri': dict(sorted(Counter(k.tur for k in kayitlar).items())),
        'evren_boyutu': {int(g): len(k.evren) for g, k in sorted(kararlar.items())},
        'son_hash': s.gunluk.son_hash,
    }
    if mimari == 'B':
        sonuc['carry_n_c'] = {int(g): k.hedef.carry['tanilar'].get('n_c') for g, k in sorted(kararlar.items())
                              if k.hedef.carry['tanilar'].get('n_c') is not None}
        sonuc['carry_isim_sayisi'] = {int(g): len(k.hedef.carry['q_yildiz']) for g, k in sorted(kararlar.items())}
    degismez = _b_degismez if mimari == 'B' else _a_degismez
    sonuc['degismez_ihlal_gunleri'] = [int(g) for g, k in sorted(kararlar.items()) if not degismez(k.hedef, p, AYAR.L)]
    parite = {}
    for g in (0, 1, GUN_SAYISI - 1):
        tt = T0 + g * GUN_MS
        gv = gorunum_kur(veri, tt)
        d = durum_turet(gv, _karar_oncesi(kayitlar, tt))
        parite[g] = _karar_json(karar_ver(gv, d, AYAR.L, p, AYAR.filtreler)) == _karar_json(kararlar[g])
    sonuc['parite'] = parite
    if mimari == 'B':
        t = time.perf_counter()
        a = ayristir(s.gunluk, veri, p)
        sonuc['ayristirma_ozdeslik_max_hata'] = a.ozdeslik_max_hata
        sonuc['ayristirma_ozdeslik_esik'] = 1e-8 * AYAR.nav0
        sonuc['sure_ayristirma_sn'] = round(time.perf_counter() - t, 1)
    return sonuc


def main():
    t = time.perf_counter()
    veri, rapor = tam_veri_yukle()
    yukleme_sn = time.perf_counter() - t
    toplam = Counter()
    for r in rapor.coin.values():
        for tur in ('klines', 'funding'):
            for k, v in r[tur].items():
                if isinstance(v, int):
                    toplam[f'{tur}.{k}'] += v
    yukleme = {'veri_kimligi': rapor.veri_kimligi, 'dosya_sayisi': rapor.dosya_sayisi, 'sembol': len(rapor.semboller),
               'bar_serisi': len(veri.barlar), 'funding_serisi': len(veri.funding), 'sure_sn': round(yukleme_sn, 1),
               'toplamlar': dict(sorted(toplam.items()))}
    (BURASI / 'yukleme_raporu.json').write_text(json.dumps(rapor.json(), ensure_ascii=False, indent=1),
                                                encoding='utf-8')
    sonuclar = {'onkayit': 'ONKAYIT.md', 'yukleme': yukleme, 'kosular': []}
    print(json.dumps(yukleme, ensure_ascii=False, indent=1))
    for mimari in ('A', 'B'):
        try:
            r = kosu(veri, mimari)
        except Exception as e:  # istisna denetimin sonucudur; ayrinti kaydedilir
            import traceback
            r = {'mimari': mimari, 'istisna': f'{type(e).__name__}: {e}', 'iz': traceback.format_exc()[-3000:]}
        sonuclar['kosular'].append(r)
        print(json.dumps(r, ensure_ascii=False, indent=1, default=str))
    (BURASI / 'sonuc.json').write_text(json.dumps(sonuclar, ensure_ascii=False, indent=1, default=str),
                                       encoding='utf-8')


if __name__ == '__main__':
    main()
