"""Kilit Adim 3, P15: tekrarlanabilirlik duman denetimi (BANKA_ONKAYIT_TASLAK Ss3.7 "Tekrarlanabilirlik denetimi" madde 1).

Duzey 2-a'nin 1. yolunun butun birimleri (A ve B: birincil, x2, x3 ve turetilen 10 cikarma = 26) ve Duzey 2-b'nin iki
null birimi (ayar 0, yol 1, null 1-2):
  klasor 4isci: 4 isciyle koşulur, 5 birimden sonra durdurulur (kesinti), sonra devam ettirilir;
  klasor 1isci_ters: 1 isciyle ters sirada.
Iki klasordeki butun birim dosyalari ve ek listeler bayt bayt ayni olmali. Yalniz sayilar ve hash esitligi yazilir;
sonuc degeri (SR vb.) yazilmaz ve incelenmez. Kullanim (v8 disindan): python duman.py -> duman_sonuc.json"""
import os

for _k in ('OMP_NUM_THREADS', 'MKL_NUM_THREADS', 'OPENBLAS_NUM_THREADS', 'NUMEXPR_NUM_THREADS'):
    os.environ[_k] = '1'

import hashlib  # noqa: E402
import json  # noqa: E402
import sys  # noqa: E402
import time  # noqa: E402
from concurrent.futures import ThreadPoolExecutor  # noqa: E402
from pathlib import Path  # noqa: E402

BURASI = Path(__file__).resolve().parent
V8 = BURASI.parents[1] / 'v8'
sys.path.insert(0, str(V8))

from kalibrasyon import birim as B  # noqa: E402
from kalibrasyon import kosucu as K  # noqa: E402
from kalibrasyon.yurutucu import har_paketi  # noqa: E402
from motor.tipler import Parametreler  # noqa: E402

BIRIMLER = ([{'duzey': 2, 'ayar_no': 0, 'yol_no': 1, 'mimari': m, 'tur': t}
             for m in ('A', 'B') for t in ('birincil', 'x2', 'x3')]
            + [{'duzey': 2, 'ayar_no': 0, 'yol_no': 1, 'mimari': 'A', 'tur': 'null', 'null_no': p} for p in (1, 2)])


def _kos(ad, **kw):
    sha, beta = har_paketi()
    kim = B.beklenen_kimlikler(Parametreler(), sha)
    t = time.perf_counter()
    s = K.calistir(BURASI / ad, BIRIMLER, kim, beta=beta, **kw)
    return {**s, 'sure_sn': round(time.perf_counter() - t, 1)}


def _ozet(ad):
    d = BURASI / ad
    dosya = {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(d.glob('d2_*.json'))}
    ek = sorted((d / K.EK_LISTE).read_text(encoding='ascii').splitlines()) if (d / K.EK_LISTE).exists() else []
    return dosya, hashlib.sha256('\n'.join(ek).encode()).hexdigest()


def main():
    with ThreadPoolExecutor(max_workers=2) as h:             # iki klasor ayni anda (toplam 5 isci sureci)
        f4 = h.submit(_kos_4)
        f1 = h.submit(_kos, 'duman_1isci_ters', isci=1, ters=True)
        k4, k1 = f4.result(), f1.result()
    d4, e4 = _ozet('duman_4isci')
    d1, e1 = _ozet('duman_1isci_ters')
    fark = sorted(set(d4) ^ set(d1)) + sorted(a for a in set(d4) & set(d1) if d4[a] != d1[a])
    sonuc = {'birim_sayisi_4isci': len(d4), 'birim_sayisi_1isci': len(d1), 'ek_liste_ayni': e4 == e1,
             'farkli_dosya': fark, 'gecti': (not fark) and e4 == e1 and len(d4) == 28,
             'kosu_4isci': k4, 'kosu_1isci_ters': k1}
    (BURASI / 'duman_sonuc.json').write_text(json.dumps(sonuc, indent=1), encoding='utf-8')
    print(json.dumps({k: v for k, v in sonuc.items() if k != 'farkli_dosya'}), 'farkli:', len(fark), flush=True)
    return 0 if sonuc['gecti'] else 1


def _kos_4():
    ilk = _kos('duman_4isci', isci=4, max_birim=5)            # kesinti
    son = _kos('duman_4isci', isci=4)                         # devam
    return {'kesinti_oncesi': ilk, 'devam': son}


if __name__ == '__main__':
    sys.exit(main())
