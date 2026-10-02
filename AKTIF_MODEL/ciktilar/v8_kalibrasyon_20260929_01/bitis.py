"""Kilit Adim 3, 3.09: bitis tekrarlanabilirlik denetimi (BANKA_ONKAYIT_TASLAK Ss3.7 "Tekrarlanabilirlik denetimi" madde 2).

1. Butunluk: IS_LISTESI.json + IS_LISTESI_EK.jsonl'deki her birimin dosyasi var ve zarfi gecerli (govde hash'i; npz yok,
   Duzey 2). Kalan 0 olmali.
2. Kimlik tekligi: butun d2_*.json dosyalarindaki dort kimlik (kod, motor, parametre, ortam) tek deger ve
   KOD_DONDURMA.json'daki degerle ayni.
3. Yeniden kosu: uretec(TOHUM_KAL, 2, "tekrar") ile 10 birim secilir: once su sirayla her kategoriden biri
   (A birincil, B birincil, A x2, B x2, A x3, B x3, A cikarma, B cikarma, A null; kategori icinde birimler kanonik JSON
   sirasiyla dizilir, indeks rng.integers(n)), sonra kalanlardan (ayni sira) biri. Secilenler ayri klasorde (bitis_tekrar)
   1 isciyle, turetme olmadan yeniden kosulur; birim dosyalari bayt bayt ayni olmali.
4. Kanit zinciri (Codex T17-a): ortak 'kanit' blogu (kanit.py) tek dort kimligi, HAR sonuc sha256'sini (dondurmadakiyle
   ayni olmali), KOD_DONDURMA sha256'sini ve kaynak hash'lerini (is listesi, ek liste, birim dosyalarinin birlesik ozeti)
   tasir; kilit.onkosullar bunlari KOD_DONDURMA ile karsilastirir.
Yalniz sayilar, adlar ve hash esitligi yazilir; sonuc degeri (SR vb.) okunmaz ve yazilmaz.
Kullanim (v8 disindan): python bitis.py [--kuru] -> bitis_sonuc.json   (--kuru: 3. adimi koşmaz, secimi yazar)"""
import os

for _k in ('OMP_NUM_THREADS', 'MKL_NUM_THREADS', 'OPENBLAS_NUM_THREADS', 'NUMEXPR_NUM_THREADS'):
    os.environ[_k] = '1'

import argparse  # noqa: E402
import hashlib  # noqa: E402
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
from kalibrasyon import kosucu as K  # noqa: E402
from kalibrasyon.tohum import TOHUM_KAL, uretec  # noqa: E402

KATEGORILER = (('A', 'birincil'), ('B', 'birincil'), ('A', 'x2'), ('B', 'x2'), ('A', 'x3'), ('B', 'x3'),
               ('A', 'cikarma'), ('B', 'cikarma'), ('A', 'null'))
N_SECIM = 10


def tum_birimler(d: Path) -> tuple:
    liste = json.loads((d / K.IS_LISTESI).read_text(encoding='ascii'))
    ek_yol = d / K.EK_LISTE
    ek = [json.loads(x) for x in ek_yol.read_text(encoding='ascii').splitlines() if x.strip()] if ek_yol.exists() else []
    return liste['birimler'] + ek, liste['kimlikler']


def sec(birimler: list, n: int = N_SECIM) -> list:
    rng = uretec(TOHUM_KAL, 2, 'tekrar')
    sirali = sorted(birimler, key=B.kanonik)
    secilen, adlar = [], set()
    for m, t in KATEGORILER:
        aday = [k for k in sirali if k.get('mimari') == m and k['tur'] == t and B.birim_adi(k) not in adlar]
        if not aday:
            raise ValueError(f"kategori bos: {m} {t}")
        k = aday[int(rng.integers(len(aday)))]
        secilen.append(k)
        adlar.add(B.birim_adi(k))
    while len(secilen) < n:
        kalan = [k for k in sirali if B.birim_adi(k) not in adlar]
        k = kalan[int(rng.integers(len(kalan)))]
        secilen.append(k)
        adlar.add(B.birim_adi(k))
    return secilen


def butunluk(d: Path, birimler: list, kimlikler: dict) -> dict:
    """Salt okuma: dosya var mi ve zarf gecerli mi (sonuc_oku'nun karantina yan etkisi olmadan)."""
    eksik, bozuk = [], []
    for k in birimler:
        yol = d / f'{B.birim_adi(k)}.json'
        if not yol.exists():
            eksik.append(B.birim_adi(k))
            continue
        z = json.loads(yol.read_text(encoding='ascii'))
        if not (z['birim'] == k and z['kimlikler'] == kimlikler and z['govde_sha256'] == B.sha256_metin(B.kanonik(z['govde']))):
            bozuk.append(B.birim_adi(k))
    return {'birim': len(birimler), 'eksik': len(eksik), 'bozuk': len(bozuk), 'ilk_eksik': eksik[:5], 'ilk_bozuk': bozuk[:5]}


def kimlik_tekligi(d: Path, dondurma: dict) -> dict:
    kume = set()
    n = 0
    for yol in sorted(d.glob('d2_*.json')):
        kume.add(B.kanonik(json.loads(yol.read_text(encoding='ascii'))['kimlikler']))
        n += 1
    beklenen = {k: dondurma['kimlikler'][k] for k in ('kod', 'motor', 'parametre', 'ortam')}
    tek = kanit.tek_kimlik([json.loads(x) for x in sorted(kume)])
    return {'dosya': n, 'farkli_kimlik': len(kume), 'dondurmayla_ayni': kume == {B.kanonik(beklenen)}, 'kimlikler': tek}


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument('--kaynak', default=str(BURASI / 'duzey2'))
    ap.add_argument('--hedef', default=str(BURASI / 'bitis_tekrar'))
    ap.add_argument('--kuru', action='store_true')
    a = ap.parse_args(argv)
    kaynak, hedef = Path(a.kaynak), Path(a.hedef)
    birimler, kimlikler = tum_birimler(kaynak)
    dondurma = json.loads((BURASI / 'KOD_DONDURMA.json').read_text(encoding='utf-8'))
    sonuc = {'butunluk': butunluk(kaynak, birimler, kimlikler), 'kimlik': kimlik_tekligi(kaynak, dondurma)}
    from kalibrasyon.yurutucu import har_paketi
    har_sha, beta = har_paketi()
    # T18: toplama ayni ozeti kendi okudugu klasorden yeniden hesaplar ve bununla karsilastirir (kanit.klasor_ozeti).
    sonuc['kanit'] = kanit.blok(__file__, sonuc['kimlik']['kimlikler'], har_sha,
                                kanit.klasor_ozeti(kaynak, K.IS_LISTESI, K.EK_LISTE))
    secilen = sec(birimler)
    sonuc['secilen'] = [B.birim_adi(k) for k in secilen]
    if not a.kuru:
        t = time.perf_counter()
        sonuc['kosu'] = K.calistir(hedef, secilen, kimlikler, beta=beta, isci=1, turet=lambda *x: [], sessiz=True)
        sonuc['kosu']['sure_sn'] = round(time.perf_counter() - t, 1)
        esit = {}
        for k in secilen:
            ad = B.birim_adi(k) + '.json'
            h1 = hashlib.sha256((kaynak / ad).read_bytes()).hexdigest()
            h2 = hashlib.sha256((hedef / ad).read_bytes()).hexdigest() if (hedef / ad).exists() else None
            esit[ad] = h1 == h2
        sonuc['ayni'] = esit
    b, km = sonuc['butunluk'], sonuc['kimlik']
    sonuc['gecti'] = (b['eksik'] == 0 and b['bozuk'] == 0 and km['farkli_kimlik'] == 1 and km['dondurmayla_ayni']
                      and har_sha == dondurma['har_sonuc_sha256'] and (a.kuru or all(sonuc['ayni'].values())))
    ad = 'bitis_kuru.json' if a.kuru else 'bitis_sonuc.json'
    (BURASI / ad).write_text(json.dumps(sonuc, indent=1, ensure_ascii=False), encoding='utf-8')
    print(json.dumps({'gecti': sonuc['gecti'], 'butunluk': b, 'kimlik': km, 'secilen': len(secilen)}), flush=True)
    return 0 if sonuc['gecti'] else 1


if __name__ == '__main__':
    sys.exit(main())
