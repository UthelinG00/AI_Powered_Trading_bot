"""Carry kapisi kosusu (CARRY Ss3, Ss6, Ss7; Ss15; 5.04). D'de P&L ureten ILK kosudur: YALNIZ kilitten (KILIT.json) sonra
kosulur (Ss2). Ekrana ve ciktiya metrik basilmaz; yalniz dosya adlari, sureler ve hash'ler (Ss7.2).

Kullanim (v8 klasorunden, kilitten sonra): python -m kapi.kosu <cikti_dizini> --kilit <KILIT.json>
  --kilit_commit <kilidin itildigi commit'in tam 40 haneli hash'i> (HEAD/dal adi kabul edilmez; T17-c)

Kosular (hepsi tam; Ss3.6, U-05, U-21, U-40): ana (m_c = 1, taban delist h_L %10 / h_S %5), mc2, mc3, delist50,
delist90 (h_L %50, %90), k8 (ana kosunun isim katkisina gore en iyi 3 + en kotu 3 alt isim yalniz carry adayligindan
cikar; < 30 isimde kosulmaz, U-52). Her kosuda: ayristirma, V2 (gunluk ozdeslik orani), V5 (tek defter; gunluk
muhur klasorune yazilip bagimsiz okunur), haftalik seriler.
Yalniz ana kosuda: aylik F - C (K5), Pazartesi bos kitap (V3), fiyat faktorleri (Pazartesi R30/s^trend; K9/K11), V6
(A'nin bant oncesi hedefi), betimsel raporlar.
Cikti (Ss7.2 kor hukum): DENETIM.json (V gecti/kaldi, veri raporu, dolgu sayilari; olcut degeri yok), HUKUM.json
(K1-K11, betimsel, karar; denetim listesi tamamlanmadan acilmaz), muhur/ (ana kosu trend satirlari, butun kosularin
gunlukleri ve NAV yollari; yalniz hash'leri acik, banka hukmune kadar acilmaz), KOSU_OZETI.json (hash'ler, sureler,
kimlikler).
"""
import os

for _k in ('OMP_NUM_THREADS', 'MKL_NUM_THREADS', 'OPENBLAS_NUM_THREADS', 'NUMEXPR_NUM_THREADS'):
    os.environ[_k] = '1'

import argparse  # noqa: E402
import gc  # noqa: E402
import traceback  # noqa: E402
import hashlib  # noqa: E402
import io  # noqa: E402
import json  # noqa: E402
import sys  # noqa: E402
import time  # noqa: E402
from dataclasses import replace  # noqa: E402
from datetime import datetime, timezone  # noqa: E402
from pathlib import Path  # noqa: E402

import numpy as np  # noqa: E402

V8 = Path(__file__).resolve().parents[1]
if str(V8) not in sys.path:
    sys.path.insert(0, str(V8))
AKTIF = V8.parent

from kapi import betimsel as bt  # noqa: E402
from kapi import betimsel_kayit as bk  # noqa: E402
from kapi import denetim as dn  # noqa: E402
from kapi import isim  # noqa: E402
from kapi import olcutler as olc  # noqa: E402
from kapi import seriler as sr  # noqa: E402
from kapi.faktorler import faktorler  # noqa: E402
from motor.ayristirma import ayristir  # noqa: E402
from motor.geri_test import KosuAyarlari, kos  # noqa: E402
from motor.har import HarTakvimi  # noqa: E402
from motor.tipler import Parametreler  # noqa: E402

NAV0 = 100_000.0                 # U-30
L = 1.0                          # Ss3.1
BIT_MS = int(datetime(2026, 7, 1, tzinfo=timezone.utc).timestamp() * 1000)   # D sonu (haric)
SAAT_MS = 3_600_000
HAR_SONUC = AKTIF / 'ciktilar' / 'v8_har_secimi_20260929_01' / 'sonuc.json'
FILTRE = AKTIF / 'ciktilar' / 'v8_sembol_filtreleri_20260930_01' / 'SEMBOL_FILTRELERI.json'
KOSULAR = (('ana', {'maliyet_k': 1.0}, {}),
           ('mc2', {'maliyet_k': 2.0}, {}),
           ('mc3', {'maliyet_k': 3.0}, {}),
           ('delist50', {}, {'delist_h_long': 0.50}),
           ('delist90', {}, {'delist_h_long': 0.90}))


def kapi_parametreleri(har_sonuc_yolu=HAR_SONUC) -> Parametreler:
    """Mimari B, HAR yuruyen aylik katsayilar (Ss3.4; tam-D katsayilari kullanilmaz)."""
    sonuc = json.loads(Path(har_sonuc_yolu).read_text(encoding='utf-8'))
    return replace(Parametreler(), mimari='B', sigma_tahmincisi='HAR', har_takvimi=HarTakvimi.sonuctan(sonuc))


def _sha(bayt: bytes) -> str:
    return hashlib.sha256(bayt).hexdigest()


def _json_yaz(yol: Path, x) -> str:
    bayt = json.dumps(bt_json(x), indent=1, ensure_ascii=False, sort_keys=True).encode('utf-8')
    yol.write_bytes(bayt)
    return _sha(bayt)


def bt_json(x):
    """numpy ve sonlu olmayan degerleri JSON'a uygun hale getirir (nan/inf dize)."""
    if isinstance(x, dict):
        return {str(k): bt_json(v) for k, v in x.items()}
    if isinstance(x, (list, tuple)):
        return [bt_json(v) for v in x]
    if isinstance(x, np.ndarray):
        return bt_json(x.tolist())
    if isinstance(x, (bool, np.bool_)):
        return bool(x)
    if isinstance(x, (int, np.integer)):
        return int(x)
    if isinstance(x, (float, np.floating)):
        v = float(x)
        return v if np.isfinite(v) else repr(v)
    return x


def _npz_yaz(yol: Path, diziler: dict) -> str:
    tampon = io.BytesIO()
    np.savez(tampon, **diziler)
    bayt = tampon.getvalue()
    yol.write_bytes(bayt)
    return _sha(bayt)


def tek_kosu(ad: str, veri, p, ayar_ek: dict, t0_ms: int, bit_ms: int, filtreler: dict, muhur: Path,
             takvim: sr.Takvim) -> dict:
    t = time.perf_counter()
    ayar = KosuAyarlari(t0_ms=t0_ms, t_son_ms=bit_ms - SAAT_MS, L=L, nav0=NAV0, filtreler=filtreler, **ayar_ek)
    s = kos(veri, ayar, p)
    a = ayristir(s.gunluk, veri, p)
    nav = sr.NavOkuyucu(s.nav_ms, s.nav, NAV0)
    oranlar = sr.gunluk_ozdeslik_orani(a, nav)
    beklenen_gunler = range(t0_ms, bit_ms, 86_400_000)                 # V2 her gun (T16: eksik gun = inf)
    gunluk_sha = dn.gunluk_yaz(s.gunluk, muhur / f'gunluk_{ad}.jsonl')
    nav_sha = _npz_yaz(muhur / f'nav_{ad}.npz', {'nav_ms': s.nav_ms, 'nav': s.nav})
    v5 = dn.v5_tek_defter(s, muhur / f'gunluk_{ad}.jsonl', a)
    haftalik = sr.haftalik(a, nav, L, p.carry_omega, takvim)
    return {'ad': ad, 's': s, 'a': a, 'nav': nav, 'haftalik': haftalik,
            'v2': max(oranlar.get(g, float('inf')) for g in beklenen_gunler), 'v5': v5,
            'hash': {'gunluk': gunluk_sha, 'nav': nav_sha}, 'sure_sn': round(time.perf_counter() - t, 1)}


class KapiKosuHatasi(RuntimeError):
    """Kosu durdu. Mesaj yalniz sabit kod ve muhurlu ayrinti dosyasinin hash'ini tasir (Codex T15-2)."""


def kapi_kos(veri, veri_raporu: dict, cikti, p=None, filtreler=None, v1=None, t0_ms: int = None, bit_ms: int = BIT_MS,
             takvim: sr.Takvim = sr.KAPI_TAKVIMI, btc_adim: float = None, kimlikler: dict = None) -> dict:
    """Butun prosedur. Testlerde sentetik veri ve kisa takvimle cagrilir; D'de yalniz main() uzerinden (kilit denetimiyle).
    V1 gecmeden hicbir motor kosusu baslamaz (teknik on kosul). Her istisna muhur klasorune yazilir; disari yalniz
    'HATA <sha256>' cikar (motor istisnalari NAV degeri tasiyabilir)."""
    if not (v1 and v1.get('gecti')):
        raise KapiKosuHatasi("V1 gecmedi: D kosusu baslamaz")
    cikti = Path(cikti)
    muhur = cikti / 'muhur'
    muhur.mkdir(parents=True, exist_ok=False)                 # tek atis: var olan klasorun ustune yazilmaz
    try:
        return _kapi_kos(veri, veri_raporu, cikti, muhur, p, filtreler, v1, t0_ms, bit_ms, takvim, btc_adim, kimlikler)
    except Exception:
        # Mühürleme ya da bildirim de başarısız olabilir; her durumda özgün istisna bağlamı bastırılır (Codex T16).
        h = 'yazilamadi'
        try:
            iz = traceback.format_exc().encode('utf-8')
            h = _sha(iz)
            (muhur / 'HATA.txt').write_bytes(iz)
        except Exception:
            h = h + ' (HATA.txt yazilamadi)'
        try:
            print(f"HATA: kapi kosusu durdu; ayrinti muhur/HATA.txt (sha256 {h})", flush=True)
        except Exception:
            pass
        raise KapiKosuHatasi(f"kosu durdu (muhur/HATA.txt sha256 {h})") from None


def _kapi_kos(veri, veri_raporu, cikti, muhur, p, filtreler, v1, t0_ms, bit_ms, takvim, btc_adim, kimlikler) -> dict:
    p = p or kapi_parametreleri()
    filtreler = filtreler or {}
    t0_ms = takvim.t0_ms if t0_ms is None else t0_ms
    btc_adim = filtreler.get(p.btc, (0.0, 5.0))[0] if btc_adim is None else btc_adim
    ozet = {'baslangic_utc': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()), 'kosular': {}, 'kimlikler': kimlikler}
    v2, v5, seri, k8_bilgi = {}, {}, {}, None

    def _kaydet(k):
        v2[k['ad']] = k['v2']
        v5[k['ad']] = k['v5']['gecti']
        seri[k['ad']] = k['haftalik']
        ozet['kosular'][k['ad']] = {'sure_sn': k['sure_sn'], 'hash': k['hash']}
        print(f"kosu {k['ad']}: {k['sure_sn']} sn", flush=True)

    # ---- ana kosu ----
    ana = tek_kosu('ana', veri, p, KOSULAR[0][1], t0_ms, bit_ms, filtreler, muhur, takvim)
    _kaydet(ana)
    s, a, nav = ana['s'], ana['a'], ana['nav']
    kararlar = bk.karar_kayitlari(s.gunluk, t0_ms, bit_ms)
    hafta_ms = takvim.hafta_sinirlari()[:-1]
    son_hafta = int(takvim.hafta_sinirlari()[-1])
    aylik = sr.aylik_fc(a, nav, L, p.carry_omega, takvim)
    bos = olc.pazartesi_bos_haftalar(s.gunluk, hafta_ms)
    kix = {k.damga_ms: k for k in kararlar}
    pazartesiler = []
    for t in hafta_ms.tolist():
        cr = kix[int(t)].veri['hedef']['carry']
        tan = cr.get('tanilar', {})
        pazartesiler.append({'adaylar': cr['adaylar'], 'r30': tan.get('r30', {}), 's_trend': tan.get('s_trend', {})})
    faktor = faktorler(veri.barlar, pazartesiler, hafta_ms, p.btc)
    tutulan = isim.tutulan_isimler(kararlar, p.btc)
    katki = isim.isim_katkilari(a, t0_ms, son_hafta, tutulan)
    k8_bilgi = isim.k8_cikarilacaklar(katki)
    w_b, w_a = dn.v6_hedefleri(veri, s.gunluk, p, L, t0_ms, bit_ms)
    v6 = bk.v6_fark_tanisi(w_b, w_a)
    gv = bt.guvenli
    kayit_rap = {'kappa': gv(bk.kappa_tanisi, kararlar), 'baglama': gv(bk.baglama_sikliklari, kararlar, p),
                 'n_c': gv(bk.n_c_serisi, kararlar, hafta_ms),
                 'tavan': gv(bk.tavan_asimlari, kararlar, p, s.gunluk, t0_ms, bit_ms),
                 'hedefe_ulasilamayan': gv(bk.hedefe_ulasilamayan, s.gunluk, kararlar),
                 'hedge_yuvarlama': gv(bk.hedge_yuvarlama, kararlar, btc_adim, p.btc),
                 'netleme_artik': gv(bk.netleme_ve_artik, a, t0_ms, bit_ms), 'v6': v6,
                 'bacak': gv(isim.bacak_serileri, a, kararlar, hafta_ms, nav, L, p.carry_omega, p.btc),
                 'sifir_sifir': gv(isim.sifir_sifir_tanisi, a, kararlar),
                 'funding_tur': {b: {tur: {c: v[1] for c, v in d.items()} for tur, d in x.items()}
                                 for b, x in a.bacak_funding_tur.items() if b == 'C'}}
    dolgu_sayilari = {b: {tur: sum(v[0] for v in d.values()) for tur, d in x.items()}
                      for b, x in a.bacak_funding_tur.items()}
    ozet['kosular']['ana']['hash']['trend_satirlari'] = _npz_yaz(
        muhur / 'trend_satirlari_ana.npz',
        {'saat_ms': a.saat_ms, **{k: a.satirlar[k] for k in ('trend_fiyat', 'trend_funding', 'trend_maliyet',
                                                             'artik_trend')}})
    del ana, s
    gc.collect()

    # ---- yeniden kosular ----
    for ad, ayar_ek, p_ek in KOSULAR[1:]:
        k = tek_kosu(ad, veri, replace(p, **p_ek), ayar_ek, t0_ms, bit_ms, filtreler, muhur, takvim)
        _kaydet(k)
        del k
        gc.collect()
    if k8_bilgi is not None:
        k = tek_kosu('k8', veri, replace(p, carry_haric=k8_bilgi['haric']), {}, t0_ms, bit_ms, filtreler, muhur, takvim)
        _kaydet(k)
        del k
        gc.collect()

    # ---- olcutler ve karar ----
    g = olc.KapiGirdisi(ana=seri['ana'], ana_aylik=aylik, mc2=seri['mc2'], mc3=seri['mc3'], k8=seri.get('k8'),
                        k8_isim_sayisi=len(tutulan), faktor=faktor, pazartesi_bos=bos, v1=bool(v1 and v1.get('gecti')),
                        v2_oran=v2, v5=v5, v6_oran=v6['oran'])
    denetim, hukum = olc.degerlendir(g)
    hukum['betimsel'] = {'seri': bt.seri_raporlari(g, hukum, {'delist50': seri['delist50'], 'delist90': seri['delist90']}),
                         'kayit': kayit_rap, 'k8_cikan': k8_bilgi}
    if not olc.hukum_trend_icermez(hukum):
        raise RuntimeError("hukum trend alani iceriyor (Ss2 muhur)")
    denetim.update({'v1': v1, 'v5_gun': {k: v5[k] for k in v5}, 'veri_raporu': veri_raporu,
                    'dolgu_sayilari': dolgu_sayilari, 'kosular': sorted(seri)})
    ozet['hash'] = {'DENETIM.json': _json_yaz(cikti / 'DENETIM.json', denetim),
                    'HUKUM.json': _json_yaz(cikti / 'HUKUM.json', hukum)}
    ozet['bitis_utc'] = time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())
    _json_yaz(cikti / 'KOSU_OZETI.json', ozet)
    for ad_, h in ozet['hash'].items():
        print(f"{ad_} sha256 {h}", flush=True)
    return ozet


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument('cikti')
    ap.add_argument('--kilit', required=True)
    ap.add_argument('--kilit_commit', required=True)          # kilidin itildigi commit, tam hash (T16, T17-c)
    ap.add_argument('--ek_commit', action='append', default=[])  # teknik ek kayitlarinin commit'leri, sirayla (21 g)
    a = ap.parse_args(argv)
    import kilit
    kd = kilit.zincir_dogrula(a.kilit, git=True, kilit_commit=a.kilit_commit,
                              ek_commitler=tuple(a.ek_commit), izinli_turler=('kapi',))   # ek yoksa dogrula
    from adaptor.sembol_filtreleri import filtreler_yukle
    from adaptor.veri_yukleyici import tam_veri_yukle
    veri, rapor = tam_veri_yukle()
    if rapor.veri_kimligi != kd['veri']['veri_kimligi']:
        raise RuntimeError("D veri kimligi kilittekinden farkli")
    v1 = {**kd['onkosul']['v1'], 'gecti': True}           # kilitli rapor; dogrula adi ve sha'yi yeniden denetledi
    kapi_kos(veri, {'veri_kimligi': rapor.veri_kimligi, 'dosya_sayisi': rapor.dosya_sayisi,
                    'sembol': len(rapor.semboller)}, a.cikti, filtreler=filtreler_yukle(FILTRE), v1=v1,
             kimlikler={'kod': kd['kod'], 'parametre': kd['parametre'], 'kilit_zaman': kd['zaman_utc'],
                        'kilit_git': kd['git_kilit']})
    return 0


if __name__ == '__main__':
    sys.exit(main())
