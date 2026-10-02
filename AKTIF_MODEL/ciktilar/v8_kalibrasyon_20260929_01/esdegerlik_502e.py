"""5.02e motor degisikliginin kalibrasyonla esdegerligi: dondurulmus motorla (7e2320f4) uretilmis duman birimleri, yeni
motorla (carry_coin, artik_coin, funding turu, R30/s^trend ve w^T* tanilari, carry_haric = ()) yeniden hesaplanir; govde'nin
son_hash DISINDAKI butun alanlari birebir ayni olmali (son_hash karar kaydina eklenen tanilar yuzunden degisir; P&L,
olcut ve sayimlar degismez). Yalniz alan adlari ve esitlik yazilir; sonuc degeri yazilmaz.
Kanit zinciri (Codex T17-a): ortak 'kanit' blogu (kanit.py) eski birimlerin dort kimligini (tek olmali), HAR sha256'sini
ve girdi zarflarinin sha256'larini tasir; 'guncel' yeni kosunun kod, motor, parametre (varsayilan + HAR), ortam ve HAR
kimlikleridir (kosu basinda ve sonunda ayni olmali). kilit.onkosullar eskiyi KOD_DONDURMA'yla, guncelini kilit anindaki
girdilerle, girdi hash'lerini duman_kanit.json'la karsilastirir.
Kullanim (v8 disindan): python esdegerlik_502e.py <dondurulmus_duman_klasoru> -> esdegerlik_502e.json"""
import os

for _k in ('OMP_NUM_THREADS', 'MKL_NUM_THREADS', 'OPENBLAS_NUM_THREADS', 'NUMEXPR_NUM_THREADS'):
    os.environ[_k] = '1'

import json  # noqa: E402
import sys  # noqa: E402
import time  # noqa: E402
from pathlib import Path  # noqa: E402

BURASI = Path(__file__).resolve().parent
V8 = BURASI.parents[1] / 'v8'
sys.path.insert(0, str(V8))
sys.path.insert(0, str(BURASI))

import kanit  # noqa: E402
from kalibrasyon import birim as B  # noqa: E402
from kalibrasyon import yurutucu as Y  # noqa: E402
from motor.tipler import Parametreler  # noqa: E402

BIRIMLER = [{'duzey': 2, 'ayar_no': 0, 'yol_no': 1, 'mimari': 'A', 'tur': 'birincil'},
            {'duzey': 2, 'ayar_no': 0, 'yol_no': 1, 'mimari': 'B', 'tur': 'birincil'},
            {'duzey': 2, 'ayar_no': 0, 'yol_no': 1, 'mimari': 'B', 'tur': 'x2'},
            {'duzey': 2, 'ayar_no': 0, 'yol_no': 1, 'mimari': 'A', 'tur': 'null', 'null_no': 1}]
HARIC = {'son_hash'}


def guncel_kimlikler() -> dict:
    har_sha, _ = Y.har_paketi()
    return {'kod': B.kod_kimligi(), 'motor': B.motor_kimligi(), 'parametre': B.parametre_kimligi(Parametreler(), har_sha),
            'ortam': B.ortam_kimligi(), 'har_sonuc_sha256': har_sha}


def main(argv):
    kaynak = Path(argv[0])
    guncel = guncel_kimlikler()
    _, beta = Y.har_paketi()
    sonuc = {'motor_kimligi_yeni': guncel['motor'], 'guncel': guncel, 'birimler': {}}
    eski_kumeler, girdi = [], {}
    for k in BIRIMLER:
        ad = B.birim_adi(k)
        bayt = (kaynak / f'{ad}.json').read_bytes()
        girdi[f'{ad}.json'] = kanit.sha_bayt(bayt)
        zarf = json.loads(bayt.decode('ascii'))
        eski = zarf['govde']
        eski_kumeler.append(zarf['kimlikler'])
        t = time.perf_counter()
        yeni = Y.duzey2_birimi(k, beta)
        alanlar = sorted(set(eski) | set(yeni))
        farkli = [a for a in alanlar if a not in HARIC and B.kanonik(eski.get(a)) != B.kanonik(yeni.get(a))]
        sonuc['birimler'][ad] = {'alan': len(alanlar), 'farkli': farkli, 'ayni': not farkli,
                                 'son_hash_farkli': eski.get('son_hash') != yeni.get('son_hash'),
                                 'sure_sn': round(time.perf_counter() - t, 1)}
        print(ad, 'ayni' if not farkli else f'FARKLI {farkli}', flush=True)
    eski_kimlik = kanit.tek_kimlik([json.loads(x) for x in sorted({B.kanonik(z) for z in eski_kumeler})])
    sonuc['motor_kimligi_eski'] = eski_kimlik['motor'] if eski_kimlik else None
    sonuc['guncel_sabit'] = guncel_kimlikler() == guncel          # kosu sirasinda kod/HAR degismedi
    sonuc['kanit'] = kanit.blok(__file__, eski_kimlik, guncel['har_sonuc_sha256'],
                                {'klasor': kaynak.name, 'dosya_sha256': girdi})
    sonuc['gecti'] = (all(v['ayni'] for v in sonuc['birimler'].values()) and eski_kimlik is not None
                      and sonuc['guncel_sabit'])
    (BURASI / 'esdegerlik_502e.json').write_text(json.dumps(sonuc, indent=1), encoding='utf-8')
    return 0 if sonuc['gecti'] else 1


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
