"""B5 ozgun epizot atfinin Duzey 2 A birincil esdegerligi (ON KAYIT: ONKAYIT.md; Codex T19 CIDDI-2, T20 CIDDI x3).
Dondurulmus kodla uretilmis Duzey 2 A birincil zarflari (eski) guncel kodla yeniden hesaplanir; govdenin son_hash
DISINDAKI butun alanlari birebir ayni olmali. Yalniz alan adlari ve esitlik yazilir; sonuc degeri yazilmaz.
Her birim bitince satir <cikti>.jsonl'a eklenir (erken fark gorulebilsin). Yeniden baslatmada bir satir yalniz ayni
guncel kimlikler, ayni betik sha256'si ve bugunku girdi dosyasinin sha256'si ile ayniysa kullanilir (T20).
Kabul (T20): is listesindeki A birincil kumesi tam BEKLENEN (140) benzersiz birim; her birimin satiri var ve 'ayni';
her zarf butun (birim kimligi, govde_sha256), eski dort kimlik KOD_DONDURMA'dakiyle ayni, guncel ortam dondurmayla ayni,
guncel kimlikler kosu boyunca sabit. Kanit blogu duzey2/ klasor ozetini (kanit.klasor_ozeti) tasir; kilit bunu bitis
kanitiyla karsilastirir.
Kullanim (v8 disindan, kalibrasyon klasoru v8_kalibrasyon_20260929_01'in yaninda):
  python b5_a_esdegerlik.py <duzey2_klasoru> [--isci N]  -> b5_a_esdegerlik.json (+ .jsonl)"""
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
from kalibrasyon.kosucu import EK_LISTE, IS_LISTESI  # noqa: E402
from kalibrasyon import yurutucu as Y  # noqa: E402
from motor.tipler import Parametreler  # noqa: E402

HARIC = {'son_hash'}
BEKLENEN = 140
CIKTI = BURASI / 'b5_a_esdegerlik.json'
SATIRLAR = BURASI / 'b5_a_esdegerlik.jsonl'


def guncel_kimlikler() -> dict:
    har_sha, _ = Y.har_paketi()
    return {'kod': B.kod_kimligi(), 'motor': B.motor_kimligi(), 'parametre': B.parametre_kimligi(Parametreler(), har_sha),
            'ortam': B.ortam_kimligi(), 'har_sonuc_sha256': har_sha}


def a_birincil_birimleri(kaynak: Path) -> list:
    liste = json.loads((Path(kaynak) / IS_LISTESI).read_text(encoding='ascii'))['birimler']
    return [k for k in liste if k['mimari'] == 'A' and k['tur'] == 'birincil']


def zarf_butun(zarf: dict, k: dict) -> bool:
    return (zarf.get('birim') == k and isinstance(zarf.get('govde'), dict)
            and zarf.get('govde_sha256') == B.sha256_metin(B.kanonik(zarf['govde'])))


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
            'zarf_butun': zarf_butun(zarf, k), 'alan': len(alanlar), 'farkli': farkli, 'ayni': not farkli,
            'son_hash_farkli': eski.get('son_hash') != yeni.get('son_hash'), 'sure_sn': round(time.perf_counter() - t, 1)}


def kabul(birimler: list, satirlar: dict, dondurma: dict, guncel: dict, guncel_sabit: bool) -> dict:
    """Saf kabul denetimi (T20). satirlar: ad -> satir. Doner {denetim adi: bool, ..., 'gecti': bool}."""
    adlar = [B.birim_adi(k) for k in birimler]
    dort = {a: dondurma['kimlikler'][a] for a in kanit.DORT}
    d = {'birim_sayisi': len(adlar) == BEKLENEN and len(set(adlar)) == BEKLENEN,
         'satir_tam': set(satirlar) == set(adlar),
         'hepsi_ayni': bool(adlar) and all(satirlar.get(a, {}).get('ayni') is True for a in adlar),
         'zarflar_butun': bool(adlar) and all(satirlar.get(a, {}).get('zarf_butun') is True for a in adlar),
         'eski_kimlik_dondurma': bool(adlar) and all(satirlar.get(a, {}).get('kimlikler') == dort for a in adlar),
         'ortam_dondurma': guncel.get('ortam') == dort['ortam'],
         'har_dondurma': guncel.get('har_sonuc_sha256') == dondurma.get('har_sonuc_sha256'),
         'guncel_sabit': bool(guncel_sabit)}
    d['gecti'] = all(d.values())
    return d


def main(argv):
    kaynak = Path(argv[0])
    isci = int(argv[argv.index('--isci') + 1]) if '--isci' in argv else 1
    betik = kanit.sha_dosya(__file__)
    guncel = guncel_kimlikler()
    dondurma = json.loads((KAL / 'KOD_DONDURMA.json').read_text(encoding='utf-8'))
    birimler = a_birincil_birimleri(kaynak)
    biten = {}
    if SATIRLAR.exists():
        for s in SATIRLAR.read_text(encoding='utf-8').splitlines():
            if not s.strip():
                continue
            r = json.loads(s)
            yol = kaynak / f"{r['ad']}.json"
            if (r.get('guncel') == guncel and r.get('betik_sha256') == betik and yol.exists()
                    and kanit.sha_dosya(yol) == r.get('girdi_sha256')):
                biten[r['ad']] = r
    isler = [(k, str(kaynak / f'{B.birim_adi(k)}.json')) for k in birimler if B.birim_adi(k) not in biten]
    print(f'A birincil {len(birimler)}; biten {len(biten)}; kalan {len(isler)}; isci {isci}', flush=True)
    with get_context('spawn').Pool(isci) as havuz, SATIRLAR.open('a', encoding='utf-8') as f:
        for r in havuz.imap_unordered(_karsilastir, isler):
            r['guncel'], r['betik_sha256'] = guncel, betik
            f.write(json.dumps(r) + '\n')
            f.flush()
            biten[r['ad']] = r
            print(r['ad'], 'ayni' if r['ayni'] else f"FARKLI {r['farkli']}", f"({len(biten)}/{len(birimler)})", flush=True)
    adlar = {B.birim_adi(k) for k in birimler}
    satirlar = {a: r for a, r in biten.items() if a in adlar}
    sabit = guncel_kimlikler() == guncel and kanit.sha_dosya(__file__) == betik
    denetim = kabul(birimler, satirlar, dondurma, guncel, sabit)
    kumeler = [json.loads(x) for x in sorted({B.kanonik(r['kimlikler']) for r in satirlar.values()})]
    eski_kimlik = kanit.tek_kimlik(kumeler)
    sonuc = {'guncel': guncel, 'birim_sayisi': len(birimler), 'ayni_sayisi': sum(bool(r['ayni']) for r in satirlar.values()),
             'farkli': {a: r['farkli'] for a, r in sorted(satirlar.items()) if not r['ayni']}, 'denetim': denetim,
             'motor_kimligi_eski': eski_kimlik['motor'] if eski_kimlik else None,
             'kanit': kanit.blok(__file__, eski_kimlik, guncel['har_sonuc_sha256'], {
                 'klasor': kaynak.name, 'duzey2_ozet': kanit.klasor_ozeti(kaynak, IS_LISTESI, EK_LISTE),
                 'dosya_sha256': {f'{a}.json': r['girdi_sha256'] for a, r in sorted(satirlar.items())}}),
             'gecti': denetim['gecti'] and eski_kimlik is not None}
    CIKTI.write_text(json.dumps(sonuc, indent=1), encoding='utf-8')
    print('GECTI' if sonuc['gecti'] else 'GECMEDI', sonuc['ayni_sayisi'], '/', len(birimler), denetim, flush=True)
    return 0 if sonuc['gecti'] else 1


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
