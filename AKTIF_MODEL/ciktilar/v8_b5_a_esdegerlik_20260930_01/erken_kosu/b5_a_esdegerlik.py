"""B5 ozgun epizot atfinin Duzey 2 A birincil esdegerligi (ON KAYIT: ONKAYIT.md; Codex T19 CIDDI-2).
Dondurulmus kodla uretilmis Duzey 2 A birincil zarflari (eski) guncel kodla yeniden hesaplanir; govdenin son_hash
DISINDAKI butun alanlari birebir ayni olmali. Yalniz alan adlari ve esitlik yazilir; sonuc degeri yazilmaz.
Her birim bitince satir <cikti>.jsonl'a eklenir (erken fark gorulebilsin; yeniden baslatmada bitenler atlanir).
Kullanim (v8 disindan, kalibrasyon klasoru v8_kalibrasyon_20260929_01'in yaninda):
  python b5_a_esdegerlik.py <eski_duzey2_klasoru> [--isci N]  -> b5_a_esdegerlik.json (+ .jsonl)"""
import os

for _k in ('OMP_NUM_THREADS', 'MKL_NUM_THREADS', 'OPENBLAS_NUM_THREADS', 'NUMEXPR_NUM_THREADS'):
    os.environ[_k] = '1'

import json  # noqa: E402
import sys  # noqa: E402
import time  # noqa: E402
from multiprocessing import get_context  # noqa: E402
from pathlib import Path  # noqa: E402

BURASI = Path(__file__).resolve().parent
KAL = BURASI.parent / 'v8_kalibrasyon_20260929_01'
V8 = BURASI.parents[1] / 'v8'
sys.path.insert(0, str(V8))
sys.path.insert(0, str(KAL))

import kanit  # noqa: E402
from kalibrasyon import birim as B  # noqa: E402
from kalibrasyon import yurutucu as Y  # noqa: E402
from motor.tipler import Parametreler  # noqa: E402

HARIC = {'son_hash'}
CIKTI = BURASI / 'b5_a_esdegerlik.json'
SATIRLAR = BURASI / 'b5_a_esdegerlik.jsonl'


def guncel_kimlikler() -> dict:
    har_sha, _ = Y.har_paketi()
    return {'kod': B.kod_kimligi(), 'motor': B.motor_kimligi(), 'parametre': B.parametre_kimligi(Parametreler(), har_sha),
            'ortam': B.ortam_kimligi(), 'har_sonuc_sha256': har_sha}


def a_birincil_birimleri(kaynak: Path) -> list:
    liste = json.loads((kaynak / 'IS_LISTESI.json').read_text(encoding='utf-8'))['birimler']
    return [k for k in liste if k['mimari'] == 'A' and k['tur'] == 'birincil']


def _karsilastir(is_):
    k, yol = is_
    bayt = Path(yol).read_bytes()
    zarf = json.loads(bayt.decode('ascii'))
    eski = zarf['govde']
    _, beta = Y.har_paketi()
    t = time.perf_counter()
    yeni = Y.duzey2_birimi(k, beta)
    alanlar = sorted(set(eski) | set(yeni))
    farkli = [a for a in alanlar if a not in HARIC and B.kanonik(eski.get(a)) != B.kanonik(yeni.get(a))]
    return {'ad': B.birim_adi(k), 'girdi_sha256': kanit.sha_bayt(bayt), 'kimlikler': zarf['kimlikler'],
            'alan': len(alanlar), 'farkli': farkli, 'ayni': not farkli,
            'son_hash_farkli': eski.get('son_hash') != yeni.get('son_hash'), 'sure_sn': round(time.perf_counter() - t, 1)}


def main(argv):
    kaynak = Path(argv[0])
    isci = int(argv[argv.index('--isci') + 1]) if '--isci' in argv else 1
    guncel = guncel_kimlikler()
    birimler = a_birincil_birimleri(kaynak)
    biten = {}
    if SATIRLAR.exists():
        for s in SATIRLAR.read_text(encoding='utf-8').splitlines():
            if s.strip():
                r = json.loads(s)
                if r.get('guncel') == guncel:
                    biten[r['ad']] = r
    isler = [(k, str(kaynak / f'{B.birim_adi(k)}.json')) for k in birimler if B.birim_adi(k) not in biten]
    print(f'A birincil {len(birimler)}; biten {len(biten)}; kalan {len(isler)}; isci {isci}', flush=True)
    with get_context('spawn').Pool(isci) as havuz, SATIRLAR.open('a', encoding='utf-8') as f:
        for r in havuz.imap_unordered(_karsilastir, isler):
            r['guncel'] = guncel
            f.write(json.dumps(r) + '\n')
            f.flush()
            biten[r['ad']] = r
            print(r['ad'], 'ayni' if r['ayni'] else f"FARKLI {r['farkli']}", f"({len(biten)}/{len(birimler)})", flush=True)
    sonuclar = [biten[B.birim_adi(k)] for k in birimler]
    eski_kimlik = kanit.tek_kimlik([json.loads(x) for x in sorted({B.kanonik(r['kimlikler']) for r in sonuclar})])
    sonuc = {'guncel': guncel, 'guncel_sabit': guncel_kimlikler() == guncel, 'birim_sayisi': len(birimler),
             'ayni_sayisi': sum(r['ayni'] for r in sonuclar),
             'farkli': {r['ad']: r['farkli'] for r in sonuclar if not r['ayni']},
             'motor_kimligi_eski': eski_kimlik['motor'] if eski_kimlik else None,
             'kanit': kanit.blok(__file__, eski_kimlik, guncel['har_sonuc_sha256'],
                                 {'klasor': kaynak.name, 'dosya_sha256': {f"{r['ad']}.json": r['girdi_sha256']
                                                                         for r in sonuclar}})}
    sonuc['gecti'] = (sonuc['ayni_sayisi'] == len(birimler) and len(birimler) > 0 and eski_kimlik is not None
                      and sonuc['guncel_sabit'])
    CIKTI.write_text(json.dumps(sonuc, indent=1), encoding='utf-8')
    print('GECTI' if sonuc['gecti'] else 'GECMEDI', sonuc['ayni_sayisi'], '/', len(birimler), flush=True)
    return 0 if sonuc['gecti'] else 1


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
