"""Platform esitligi denetimi (30 Eylul 2026): Duzey 2 kosusu dizustunden (Windows, i7-11800H) Linux hesap sunucusuna
(Hetzner CPX52, AMD EPYC Genoa) tasinmadan once. Birim ortam kimligi yalniz python/numpy surumunu tasir, isletim
sistemini ve islemciyi tasimaz; bu yuzden dizustunde biten birimlerle karisik bir Duzey 2 ancak ayni birimler sunucuda
bayt bayt ayni uretiliyorsa kabul edilir (3.09 bitis denetimi rastgele secilen birimleri bayt bayt karsilastirir).

Secim (sabit kural, sonuca bakmadan): dizustunde biten birimlerden kanonik JSON sirasinda her kategoriden ilki:
A birincil, B birincil (ayristirma + carry yolu), B x2, A null, A cikarma (bitmis olanlar). Secilenler ayri klasorde (platform_tekrar) turetme olmadan yeniden kosulur.
Karar: hepsi ayni -> dizustu birimleriyle devam; biri bile farkli -> Duzey 2 sunucuda bastan (dizustu birimleri
silinmez, ayri klasore tasinir). Yalniz adlar ve hash esitligi yazilir; sonuc degeri okunmaz.
Kullanim (v8 disindan): python platform_esitlik.py [--isci N] -> platform_esitlik_sonuc.json"""
import os

for _k in ('OMP_NUM_THREADS', 'MKL_NUM_THREADS', 'OPENBLAS_NUM_THREADS', 'NUMEXPR_NUM_THREADS'):
    os.environ[_k] = '1'

import argparse  # noqa: E402
import hashlib  # noqa: E402
import json  # noqa: E402
import platform  # noqa: E402
import sys  # noqa: E402
import time  # noqa: E402
from pathlib import Path  # noqa: E402

BURASI = Path(__file__).resolve().parent
V8 = BURASI.parents[1] / 'v8'
sys.path.insert(0, str(V8))

from kalibrasyon import birim as B  # noqa: E402
from kalibrasyon import kosucu as K  # noqa: E402

KATEGORILER = (('A', 'birincil'), ('B', 'birincil'), ('B', 'x2'), ('A', 'null'), ('A', 'cikarma'))


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument('--kaynak', default=str(BURASI / 'duzey2'))
    ap.add_argument('--hedef', default=str(BURASI / 'platform_tekrar'))
    ap.add_argument('--isci', type=int, default=4)
    a = ap.parse_args(argv)
    kaynak, hedef = Path(a.kaynak), Path(a.hedef)
    liste = json.loads((kaynak / K.IS_LISTESI).read_text(encoding='ascii'))
    ek_yol = kaynak / K.EK_LISTE
    ek = [json.loads(x) for x in ek_yol.read_text(encoding='ascii').splitlines() if x.strip()] if ek_yol.exists() else []
    biten = [k for k in sorted(liste['birimler'] + ek, key=B.kanonik) if (kaynak / f'{B.birim_adi(k)}.json').exists()]
    secilen = []
    for m, t in KATEGORILER:
        aday = [k for k in biten if k.get('mimari') == m and k['tur'] == t]
        if aday:
            secilen.append(aday[0])
    from kalibrasyon.yurutucu import har_paketi
    _, beta = har_paketi()
    t0 = time.perf_counter()
    kosu = K.calistir(hedef, secilen, liste['kimlikler'], beta=beta, isci=a.isci, turet=lambda *x: [], sessiz=True)
    ayni = {}
    for k in secilen:
        ad = B.birim_adi(k) + '.json'
        h1 = hashlib.sha256((kaynak / ad).read_bytes()).hexdigest()
        h2 = hashlib.sha256((hedef / ad).read_bytes()).hexdigest() if (hedef / ad).exists() else None
        ayni[ad] = h1 == h2
    sonuc = {'platform': platform.platform(), 'islemci': platform.processor() or platform.machine(),
             'secilen': [B.birim_adi(k) for k in secilen], 'kosu': kosu, 'sure_sn': round(time.perf_counter() - t0, 1),
             'ayni': ayni, 'gecti': bool(secilen) and all(ayni.values())}
    (BURASI / 'platform_esitlik_sonuc.json').write_text(json.dumps(sonuc, indent=1, ensure_ascii=False), encoding='utf-8')
    print(json.dumps({'gecti': sonuc['gecti'], 'ayni': ayni, 'sure_sn': sonuc['sure_sn']}), flush=True)
    return 0 if sonuc['gecti'] else 1


if __name__ == '__main__':
    sys.exit(main())
