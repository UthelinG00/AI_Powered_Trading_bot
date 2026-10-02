"""On-kayit kilidi (CARRY Ss2 Adim 4; 4.03). KILIT.json uretimi ve dogrulamasi.

Kullanim (v8 klasorunden):
  python -m kilit uret <cikti_dizini>      -> <cikti_dizini>/KILIT.json (commit + push elle, 4.06)
  python -m kilit dogrula <KILIT.json> <kilit_commit>  -> her seyi yeniden hesaplar; fark varsa hata

KILIT.json alanlari:
  belgeler   : {AKTIF_MODEL'e gore yol: sha256} (KILIT_BELGELERI; biri yoksa uretilmez)
  kod        : motor, kapi, kalibrasyon (kalibrasyon + banka), adaptor, kilit (bu dosya)
  parametre  : varsayilan ve kapi Parametreler kimligi (HAR sonuc sha'siyla; kalibrasyon.birim.parametre_kimligi)
  ortam      : python ve numpy surumu
  veri       : D MANIFEST.jsonl sha256, gelistirme evreni sha256, veri kimligi (tam_veri_yukle; zip hash'leri dogrulanir)
  sabitler   : kapi NAV, L, T0, D sonu, kosu listesi
  defter     : 'A4-carry-kapisi' satiri var olmali (CARRY Ss3.6; satir kilitten once elle eklenir, arsiv once)
  onkosul    : Adim 0-3 kabul durumlari (Codex T15-3): bitis_sonuc gecti, TOPLAMA durum TAMAM, duman gecti, esdegerlik
               gecti; V1 test raporu (motor kimligi guncel, basarisiz 0, butun test_v8_*.py dosyalarini kapsar) adi ve sha256'si.
               Kanit zinciri (Codex T17-a): dort kanitin (duman_kanit, bitis_sonuc, TOPLAMA, esdegerlik_502e) 'kanit' blogu
               KOD_DONDURMA.json'la (dosya sha256'si, dort kimlik, HAR sha256'si) ayni; guncel HAR dondurmadakiyle ayni;
               esdegerligin 'guncel' kimlikleri (kod, motor, parametre, HAR) kilit anindaki girdilerle ayni; kaynak
               hash'leri zincirleme tutar (TOPLAMA -> bitis_sonuc; duman_kanit -> duman_sonuc; esdegerlik girdileri ->
               duman_kanit dosyalari). T18: TOPLAMA'nin tukettigi Duzey 2 girdi ozeti (is listesi, ek liste, birim
               dosyalarinin birlesik ozeti) bitis kanitindakiyle ayni.
  git        : uretim anindaki HEAD ve dal (bilgi; dogrulamada karsilastirilmaz)
Dogrulama belge kumesini KILIT_BELGELERI ile birebir karsilastirir (kilit kendi kapsamini daraltamaz; T15-4) ve istenirse
KILIT.json'un tam hash'le bildirilen, origin'de (fetch --prune + ls-remote) bir dalda bulunan commit'te bayt bayt ayni
oldugunu denetler (T17-c).
Kilitten sonra hicbir esik, olcut, parametre ya da olcut kumesi degismez (CARRY Ss2 baglayici cumle).
"""
import csv
import hashlib
import json
import platform
import re
import subprocess
import sys
import time
from dataclasses import replace
from pathlib import Path

import numpy as np

V8 = Path(__file__).resolve().parent
if str(V8) not in sys.path:
    sys.path.insert(0, str(V8))
AKTIF = V8.parent

KILIT_BELGELERI = (
    'ciktilar/v8_asama4_20260927_01/MIMARI.md',
    'ciktilar/v8_asama4_20260927_01/CARRY_KAPISI_ONKAYIT_TASLAK.md',
    'ciktilar/v8_asama4_20260927_01/BANKA_ONKAYIT_TASLAK.md',
    'ciktilar/v8_asama4_20260927_01/ACIK_SORU_YANITLARI.md',
    'ciktilar/v8_asama4_20260927_01/ASAMA4B_KARAR.md',
    'ciktilar/v8_asama4_20260927_01/KARARLAR.md',
    'ciktilar/v8_kapi_20260929_01/OLCUT_LISTESI.md',
    'ciktilar/v8_kapi_20260929_01/BELIRSIZLIK_COZUMLERI.md',
    'ciktilar/v8_har_secimi_20260929_01/ONKAYIT.md',
    'ciktilar/v8_har_secimi_20260929_01/sonuc.json',
    'ciktilar/v8_har_secimi_20260929_01/RAPOR.md',
    'ciktilar/v8_kalibrasyon_20260929_01/KOD_DONDURMA.json',
    'ciktilar/v8_kalibrasyon_20260929_01/duman_sonuc.json',
    'ciktilar/v8_kalibrasyon_20260929_01/duman_kanit.json',
    'ciktilar/v8_kalibrasyon_20260929_01/DUZEY1_OZET.json',
    'ciktilar/v8_kalibrasyon_20260929_01/bitis_sonuc.json',
    'ciktilar/v8_kalibrasyon_20260929_01/TOPLAMA.json',
    'ciktilar/v8_kalibrasyon_20260929_01/RAPOR.md',
    'ciktilar/v8_kalibrasyon_20260929_01/esdegerlik_502e.json',
    'ciktilar/v8_b5_a_esdegerlik_20260930_01/ONKAYIT.md',
    'ciktilar/v8_b5_a_esdegerlik_20260930_01/b5_a_esdegerlik.json',
    'ciktilar/v8_sembol_filtreleri_20260930_01/SEMBOL_FILTRELERI.json',
    'ciktilar/v8_sembol_filtreleri_20260930_01/exchangeInfo_ham.json',
    'ciktilar/v8_banka_20260924_01/V8_DENEME_DEFTERI.csv',
    'ciktilar/v8_kapi_sentetik_20261001/kapi_sentetik.py',
    'ciktilar/v8_kapi_sentetik_20261001/sonuc.json',
    'ciktilar/v8_kapi_sentetik_20261001/RAPOR.md',
    'ciktilar/v8_kapi_sentetik_20261001/ONKAYIT_OLCEK.md',
    'ciktilar/v8_kapi_sentetik_20261001/duyarlilik_olcek.json',
)
DEFTER = 'ciktilar/v8_banka_20260924_01/V8_DENEME_DEFTERI.csv'
DEFTER_SATIRI = 'A4-carry-kapisi'
KAPI_SENTETIK = 'ciktilar/v8_kapi_sentetik_20261001/'           # CARRY Ss8.5, Ss15 madde 16 c (BX-08)
KAPI_SENTETIK_TEKRAR = 10000
TEKNIK_TURLER = ('kapi', 'banka_oncesi', 'banka_sonrasi')        # BANKA Ss3.7 21 g revizyonu: her biri en fazla 1


class KilitHatasi(RuntimeError):
    pass


def _sha(yol: Path) -> str:
    return hashlib.sha256(Path(yol).read_bytes()).hexdigest()


def duzey1_ozet_bagi(ozet: dict) -> dict:
    """DUZEY1_OZET.json'dan TOPLAMA'nin 'duzey1_tuketilen' alanlarinin beklenen degeri (Codex T19 CIDDI-1): is listesi,
    dosya sayisi ve JSON + NPZ dosya hash'lerinin birlesik ozeti (kanit.birlesik ile ayni tanim)."""
    h = {}
    for b in ozet.get('birimler', []):
        h[f"{b['birim']}.json"], h[f"{b['birim']}.npz"] = b['json_sha256'], b['npz_sha256']
    birlesik = hashlib.sha256(json.dumps(sorted(h.items()), separators=(',', ':')).encode('ascii')).hexdigest()
    return {'is_listesi_sha256': ozet.get('is_listesi_sha256'), 'dosya': len(h), 'birlesik_sha256': birlesik}


def belge_hashleri(aktif: Path = AKTIF, belgeler=KILIT_BELGELERI) -> dict:
    eksik = [b for b in belgeler if not (aktif / b).is_file()]
    if eksik:
        raise KilitHatasi(f"kilit belgesi yok: {eksik}")
    return {b: _sha(aktif / b) for b in belgeler}


def kod_kimlikleri() -> dict:
    from kalibrasyon import birim as B
    return {'motor': B.motor_kimligi(), 'kapi': B._birlesik_sha256(B._py(V8 / 'kapi')), 'kalibrasyon': B.kod_kimligi(),
            'adaptor': B._birlesik_sha256(B._py(V8 / 'adaptor')), 'kilit': _sha(Path(__file__))}


def parametre_kimlikleri() -> dict:
    from kalibrasyon import birim as B
    from kalibrasyon.yurutucu import har_paketi
    from kapi.kosu import kapi_parametreleri
    from motor.tipler import Parametreler
    har_sha, _ = har_paketi()
    return {'varsayilan': B.parametre_kimligi(Parametreler(), har_sha),
            'kapi': B.parametre_kimligi(replace(kapi_parametreleri(), har_takvimi=None), har_sha), 'har_sonuc': har_sha}


def ortam() -> dict:
    import cryptography
    import pandas
    return {'python': platform.python_version(), 'numpy': np.__version__, 'pandas': pandas.__version__,
            'cryptography': cryptography.__version__}


def _json(aktif: Path, yol: str) -> dict:
    p = aktif / yol
    if not p.is_file():
        raise KilitHatasi(f"onkosul dosyasi yok: {yol}")
    return json.loads(p.read_text(encoding='utf-8'))


def v1_raporu(motor_kimligi: str, testler: Path = V8 / 'testler', ciktilar: Path = V8 / 'ciktilar',
              kod_kimlikleri: dict = None) -> dict:
    """Motor kimligi guncel, basarisiz 0, butun test_v8_*.py dosyalarini kapsayan ve butun kod kimlikleri (motor,
    adaptor, kapi, kalibrasyon, banka, banka_kos, testler, kilit.py, v8_calistir.py) guncel olan en yeni test raporu
    (U-15, T15-5, T16)."""
    if kod_kimlikleri is None:
        from v8_calistir import kod_kimlikleri_hepsi
        kod_kimlikleri = kod_kimlikleri_hepsi()
    beklenen = {p.stem for p in Path(testler).glob('test_v8_*.py')}
    for yol in sorted(Path(ciktilar).glob('test_*/sonuc.json'), reverse=True):
        d = json.loads(yol.read_text(encoding='utf-8'))
        if d.get('motor_kimligi') != motor_kimligi:
            continue
        kapsanan = {Path(k).stem for k in d.get('sonuclar', {})}
        if (d.get('basarisiz') == 0 and (d.get('toplam') or 0) > 0 and beklenen <= kapsanan
                and d.get('kod_kimlikleri') == kod_kimlikleri):
            return {'rapor': yol.parent.name, 'sha256': _sha(yol), 'toplam': d['toplam'], 'test_dosyasi': len(beklenen)}
        raise KilitHatasi(f"guncel motor icin en yeni test raporu gecmiyor ya da eksik: {yol.parent.name}")
    raise KilitHatasi("guncel motor kimligiyle test raporu yok (v8_calistir.py test)")


DORT = ('kod', 'motor', 'parametre', 'ortam')
GUNCEL = ('kod', 'motor', 'parametre', 'har_sonuc_sha256')
B5_A_ESDEGERLIK = 'ciktilar/v8_b5_a_esdegerlik_20260930_01/b5_a_esdegerlik.json'
B5_A_BEKLENEN = 140                                                        # Duzey 2 A birincil birim sayisi (ONKAYIT)
D2_OZET = ('is_listesi_sha256', 'ek_liste_sha256', 'birim_dosyalari')    # kanit.klasor_ozeti (T18)


def guncel_girdiler() -> dict:
    """Kanit zincirinin kilit anindaki ucu: kalibrasyon kodu (kalibrasyon + banka), motor, varsayilan parametre
    kimligi (HAR sonuc sha'siyla) ve HAR sonuc dosyasinin sha256'si."""
    from kalibrasyon import birim as B
    from kalibrasyon.yurutucu import har_paketi
    from motor.tipler import Parametreler
    har_sha, _ = har_paketi()
    return {'kod': B.kod_kimligi(), 'motor': B.motor_kimligi(), 'parametre': B.parametre_kimligi(Parametreler(), har_sha),
            'har_sonuc_sha256': har_sha}


def onkosullar(aktif: Path = AKTIF, v1: bool = True, guncel: dict = None) -> dict:
    """Adim 0-3 kabul durumlari ve kanit kimlik zinciri (T16, T17-a). Her kanitin 'kanit' blogu kanit uretilirken
    okunan KOD_DONDURMA.json'un sha256'sini, HAR sonuc sha256'sini ve dayandigi birimlerin dort kimligini tasir; hepsi
    bugunku KOD_DONDURMA.json'la ayni olmali. Esdegerlik dondurulmus birimlerden (eski = dondurma) guncel girdilere
    (kilit anindaki kod, motor, parametre, HAR) kopru kurar; bunlardan biri degistiyse esdegerlik yeniden kosulur."""
    kal = 'ciktilar/v8_kalibrasyon_20260929_01/'
    guncel = guncel_girdiler() if guncel is None else guncel
    dondurma = _json(aktif, kal + 'KOD_DONDURMA.json')
    d_sha = _sha(aktif / kal / 'KOD_DONDURMA.json')
    dort = {k: dondurma['kimlikler'][k] for k in DORT}
    har = dondurma.get('har_sonuc_sha256')
    if not har or guncel['har_sonuc_sha256'] != har:
        raise KilitHatasi("HAR sonuc dosyasi kalibrasyondan (KOD_DONDURMA) beri degisti")

    def kanit(ad: str, d: dict) -> dict:
        k = d.get('kanit')
        if not isinstance(k, dict):
            raise KilitHatasi(f"{ad}: kanit blogu yok (kaniti guncel betikle yeniden uret)")
        if k.get('kod_dondurma_sha256') != d_sha:
            raise KilitHatasi(f"{ad}: kanit baska bir KOD_DONDURMA.json ile uretilmis")
        if k.get('har_sonuc_sha256') != har:
            raise KilitHatasi(f"{ad}: kanitin HAR sonuc dosyasi dondurmadakinden farkli")
        if k.get('kimlikler') != dort:
            raise KilitHatasi(f"{ad}: kanitin dayandigi birimlerin kimlikleri dondurmadan farkli")
        if not isinstance(k.get('kaynak'), dict):
            raise KilitHatasi(f"{ad}: kanitin kaynak hash'leri yok")
        return k

    bitis = _json(aktif, kal + 'bitis_sonuc.json')
    if not (bitis.get('gecti') and bitis.get('kimlik', {}).get('farkli_kimlik') == 1
            and bitis.get('kimlik', {}).get('dondurmayla_ayni')):
        raise KilitHatasi("bitis denetimi gecmedi ya da kimlik zinciri eksik")
    kanit('bitis_sonuc', bitis)
    toplama = _json(aktif, kal + 'TOPLAMA.json')
    if toplama.get('durum') != 'TAMAM':
        raise KilitHatasi("kalibrasyon toplamasi TAMAM degil (KILIT_BEKLER: kullaniciya sor)")
    tk = kanit('TOPLAMA', toplama)['kaynak']
    n_simdi = n_kilit(aktif)                                       # BANKA Ss3.7 netlestirme 21 f
    if ((toplama.get('duzey1') or {}).get('rapor') or {}).get('N') != n_simdi or tk.get('defter_sha256') != _sha(aktif / DEFTER):
        raise KilitHatasi(f"TOPLAMA'nin N'si / defteri guncel defterle ayni degil (guncel N {n_simdi}); topla.py'yi yeniden kos")
    ks = _json(aktif, KAPI_SENTETIK + 'sonuc.json')               # CARRY Ss15 madde 16 c (BX-08)
    if (ks.get('tekrar') != KAPI_SENTETIK_TEKRAR or len(ks.get('senaryolar') or {}) != 7
            or ks.get('betik_sha256') != _sha(aktif / KAPI_SENTETIK / 'kapi_sentetik.py')):
        raise KilitHatasi("kapi sentetik dogrulamasi (BX-08) tam degil ya da betik degisti")
    if tk.get('bitis_sonuc_sha256') != _sha(aktif / kal / 'bitis_sonuc.json'):
        raise KilitHatasi("TOPLAMA bugunku bitis_sonuc.json'a dayanmiyor")
    bitis_kaynak = bitis['kanit']['kaynak']
    if tk.get('duzey2_tuketilen') != {k: bitis_kaynak.get(k) for k in D2_OZET}:
        raise KilitHatasi("TOPLAMA'nin tukettigi Duzey 2 girdileri bitis kanitindakiyle ayni degil")
    d1_ozet = _json(aktif, kal + 'DUZEY1_OZET.json')
    if d1_ozet.get('kimlikler') != dort or d1_ozet.get('gecersiz') != 0:
        raise KilitHatasi("DUZEY1_OZET.json kimlikleri dondurmadan farkli ya da gecersiz birim var")
    beklenen_d1 = dict(duzey1_ozet_bagi(d1_ozet), ozet_sha256=_sha(aktif / kal / 'DUZEY1_OZET.json'))
    if tk.get('duzey1_tuketilen') != beklenen_d1:
        raise KilitHatasi("TOPLAMA'nin tukettigi Duzey 1 girdileri DUZEY1_OZET.json ile ayni degil")
    if not _json(aktif, kal + 'duman_sonuc.json').get('gecti'):
        raise KilitHatasi("duman denetimi gecmedi")
    dk = _json(aktif, kal + 'duman_kanit.json')
    if not dk.get('gecti'):
        raise KilitHatasi("duman kanit denetimi gecmedi")
    if kanit('duman_kanit', dk)['kaynak'].get('duman_sonuc_sha256') != _sha(aktif / kal / 'duman_sonuc.json'):
        raise KilitHatasi("duman kaniti bugunku duman_sonuc.json'a dayanmiyor")
    es = _json(aktif, kal + 'esdegerlik_502e.json')
    if not es.get('gecti'):
        raise KilitHatasi("motor esdegerligi gecmedi")
    girdi = kanit('esdegerlik', es)['kaynak'].get('dosya_sha256') or {}
    duman_dosya = dk.get('dosya_sha256') or {}
    if not girdi or any(duman_dosya.get(ad) != h for ad, h in girdi.items()):
        raise KilitHatasi("esdegerlik girdileri duman kanitindaki dondurulmus birim dosyalari degil")
    fark = [k for k in GUNCEL if (es.get('guncel') or {}).get(k) != guncel[k]]
    if fark:
        raise KilitHatasi(f"esdegerlik kaniti guncel girdiler icin degil: {fark} (esdegerligi yeniden kos)")
    # Codex T19/T20: B5 ozgun epizot atfinin Duzey 2 A birincil esdegerligi (ONKAYIT: ciktilar/v8_b5_a_esdegerlik_...).
    b5 = _json(aktif, B5_A_ESDEGERLIK)
    if not (b5.get('gecti') and b5.get('birim_sayisi') == B5_A_BEKLENEN and b5.get('ayni_sayisi') == B5_A_BEKLENEN
            and (b5.get('denetim') or {}).get('gecti')):
        raise KilitHatasi("B5 A birincil esdegerligi gecmedi ya da tam degil")
    b5_kaynak = kanit('b5_a_esdegerlik', b5)['kaynak']
    if b5_kaynak.get('duzey2_ozet') != {k: bitis_kaynak.get(k) for k in D2_OZET}:
        raise KilitHatasi("B5 A esdegerligi bitis kanitindaki Duzey 2 klasorunde kosulmamis")
    fark = [k for k in GUNCEL if (b5.get('guncel') or {}).get(k) != guncel[k]]
    if fark:
        raise KilitHatasi(f"B5 A esdegerligi guncel girdiler icin degil: {fark} (yeniden kos)")
    out = {'bitis': True, 'toplama': 'TAMAM', 'duman': True, 'esdegerlik': True, 'b5_a_esdegerlik': True,
           'motor_dondurulmus': dort['motor'], 'motor_guncel': guncel['motor'],
           'kanit': {'kod_dondurma_sha256': d_sha, 'dondurulmus': dort, 'guncel': {k: guncel[k] for k in GUNCEL}}}
    if v1:
        out['v1'] = v1_raporu(guncel['motor'])
    return out


def n_kilit(aktif: Path = AKTIF) -> int:
    """N_kilit = N_REV1 + N_v8, defterin son halinden (BANKA Ss3.3 sayim kurali; netlestirme 21 f)."""
    from kalibrasyon.duzey1_karar import n_v8
    from kalibrasyon.sigma_sr import N_REV1
    return N_REV1 + n_v8(aktif / DEFTER)


def veri_kimlikleri(yukle: bool = True) -> dict:
    from adaptor import veri_yukleyici as vy
    kok = vy.veri_koku_bul()
    out = {'manifest': _sha(kok / 'MANIFEST.jsonl'), 'gelistirme_evreni': vy.GELISTIRME_SHA256}
    if yukle:
        _, rapor = vy.tam_veri_yukle(kok)
        out['veri_kimligi'] = rapor.veri_kimligi
        out['dosya_sayisi'] = rapor.dosya_sayisi
    return out


def sabitler() -> dict:
    from kapi import kosu
    return {'kapi_nav0': kosu.NAV0, 'L': kosu.L, 't0_ms': kosu.sr.KAPI_TAKVIMI.t0_ms, 'bit_ms': kosu.BIT_MS,
            'kosular': [k[0] for k in kosu.KOSULAR] + ['k8']}


def defter_denetimi(aktif: Path = AKTIF) -> dict:
    with open(aktif / DEFTER, encoding='utf-8', newline='') as f:
        satirlar = list(csv.DictReader(f))
    var = any(r['kayit_id'] == DEFTER_SATIRI for r in satirlar)
    if not var:
        raise KilitHatasi(f"deneme defterinde {DEFTER_SATIRI} satiri yok (kilitten once eklenir)")
    return {'satir': DEFTER_SATIRI, 'satir_sayisi': len(satirlar)}


def _git() -> dict:
    def g(*a):
        return subprocess.run(['git', *a], cwd=V8, capture_output=True, text=True, check=True).stdout.strip()
    return {'head': g('rev-parse', 'HEAD'), 'dal': g('rev-parse', '--abbrev-ref', 'HEAD')}


def kilit_icerigi(aktif: Path = AKTIF, belgeler=KILIT_BELGELERI, veri_yukle: bool = True, onkosul: bool = True) -> dict:
    icerik = {'belgeler': belge_hashleri(aktif, belgeler), 'kod': kod_kimlikleri(), 'parametre': parametre_kimlikleri(),
              'ortam': ortam(), 'veri': veri_kimlikleri(veri_yukle), 'sabitler': sabitler(),
              'defter': defter_denetimi(aktif)}
    if onkosul:
        icerik['onkosul'] = onkosullar(aktif)
    return icerik


def uret(cikti, aktif: Path = AKTIF, belgeler=KILIT_BELGELERI, veri_yukle: bool = True, git: bool = True,
         onkosul: bool = True) -> dict:
    cikti = Path(cikti)
    yol = cikti / 'KILIT.json'
    if yol.exists():
        raise KilitHatasi("KILIT.json zaten var; kilit bir kez vurulur")
    icerik = kilit_icerigi(aktif, belgeler, veri_yukle, onkosul)
    icerik['zaman_utc'] = time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())
    icerik['git'] = _git() if git else None
    cikti.mkdir(parents=True, exist_ok=True)
    yol.write_text(json.dumps(icerik, indent=1, sort_keys=True, ensure_ascii=True), encoding='ascii')
    return icerik


def _farklar(a, b, yol='') -> list:
    if isinstance(a, dict) and isinstance(b, dict):
        out = []
        for k in sorted(set(a) | set(b)):
            out += _farklar(a.get(k), b.get(k), f'{yol}/{k}')
        return out
    return [] if a == b else [yol]


def _uzak_dallar(g, uzak: str, canli: bool) -> dict:
    """Uzak dalların {ad: commit} sözlüğü, yalnız `uzak` için. canli: `git ls-remote --heads` ile uzaktaki güncel
    dallar; her biri yerel izleme referansıyla (fetch --prune sonrası) aynı olmalı, değilse (arada push) sayılmaz.
    canli değilse yerel refs/remotes/<uzak>/ referansları (HEAD sembolik referansı hariç)."""
    yerel = {}
    for satir in g('for-each-ref', '--format=%(objectname) %(refname)', f'refs/remotes/{uzak}/').splitlines():
        sha, ref = satir.split(' ', 1)
        ad = ref[len(f'refs/remotes/{uzak}/'):]
        if ad != 'HEAD':
            yerel[ad] = sha
    if not canli:
        return yerel
    out = {}
    for satir in g('ls-remote', '--heads', uzak).splitlines():
        sha, ref = satir.split('\t', 1)
        ad = ref[len('refs/heads/'):]
        if yerel.get(ad) == sha:
            out[ad] = sha
    return out


def git_denetimi(kilit_yolu, beklenen_commit: str, fetch: bool = True, uzak: str = 'origin') -> dict:
    """KILIT.json, onceden bildirilen commit'te bayt bayt ayni ve o commit uzak depoda mi (T15-4, T16, T17-c):
    commit tam 40 haneli kucuk harf hash olmali (HEAD, dal adi, kisa hash kabul edilmez); `uzak` git fetch --prune ile
    tazelenir ve ls-remote ile dogrulanir; commit yalniz o uzaktaki bir dalin atasi olmali (baska remote'lar ve
    silinmis dallarin bayat referanslari sayilmaz); `git show commit:yol` dosyayla ayni olmali."""
    yol = Path(kilit_yolu).resolve()

    def g(*a, metin=True):
        r = subprocess.run(['git', *a], cwd=yol.parent, capture_output=True, text=metin, check=True)
        return r.stdout.strip() if metin else r.stdout

    def ata_mi(commit, uc) -> bool:
        return subprocess.run(['git', 'merge-base', '--is-ancestor', commit, uc], cwd=yol.parent,
                              capture_output=True).returncode == 0
    if not beklenen_commit:
        raise KilitHatasi("kilit commit'i bildirilmedi (--kilit_commit)")
    if not (isinstance(beklenen_commit, str) and re.fullmatch(r'[0-9a-f]{40}', beklenen_commit)):
        raise KilitHatasi("kilit commit'i tam 40 haneli kucuk harf hash olmali (HEAD, dal adi, kisa hash kabul edilmez)")
    if fetch:
        g('fetch', '--quiet', '--prune', uzak)
    try:
        commit = g('rev-parse', '--verify', '--quiet', f'{beklenen_commit}^{{commit}}')
    except subprocess.CalledProcessError:
        raise KilitHatasi("kilit commit'i yerel depoda yok") from None
    if commit != beklenen_commit:
        raise KilitHatasi("kilit commit'i cozulen commit'le ayni degil")
    dallar = _uzak_dallar(g, uzak, canli=fetch)
    iceren = sorted(ad for ad, uc in dallar.items() if ata_mi(commit, uc))
    if not iceren:
        raise KilitHatasi(f"kilit commit'i {uzak} uzak deposunda yok (push edilmedi ya da dal silindi)")
    goreli = g('ls-files', '--full-name', '--', yol.name)
    if not goreli:
        raise KilitHatasi("KILIT.json izlenmiyor")
    if g('show', f'{commit}:{goreli}', metin=False) != yol.read_bytes():
        raise KilitHatasi("KILIT.json bildirilen commit'teki halinden farkli")
    return {'commit': commit, 'sha256': _sha(yol), 'uzak': uzak, 'uzak_dallar': iceren}


def dogrula(kilit_yolu, aktif: Path = AKTIF, belgeler=KILIT_BELGELERI, veri_yukle: bool = False, git: bool = False,
            onkosul: bool = True, kilit_commit: str = None) -> dict:
    """Kilitteki her sey yeniden hesaplanir (git ve zaman haric). Belge kumesi `belgeler` ile birebir olmali.
    veri_yukle False ise veri_kimligi karsilastirilmaz (kapi kosusu D'yi kendisi yukler ve kimligi kilittekiyle
    karsilastirir). Doner: kilit icerigi (git=True ise 'git_kilit' eklenir)."""
    kilit = json.loads(Path(kilit_yolu).read_text(encoding='ascii'))
    if set(kilit['belgeler']) != set(belgeler):
        raise KilitHatasi(f"kilit belge kumesi beklenenden farkli: {sorted(set(kilit['belgeler']) ^ set(belgeler))}")
    simdi = kilit_icerigi(aktif, belgeler, veri_yukle, onkosul)
    beklenen = {k: kilit[k] for k in simdi}
    if not veri_yukle:
        beklenen['veri'] = {k: v for k, v in beklenen['veri'].items() if k not in ('veri_kimligi', 'dosya_sayisi')}
    fark = _farklar(beklenen, simdi)
    if fark:
        raise KilitHatasi(f"kilitten sonra degisen: {fark}")
    if git:
        kilit['git_kilit'] = git_denetimi(kilit_yolu, kilit_commit)
    return kilit


DEGISMEZ = ('parametre', 'ortam', 'veri', 'sabitler')        # 21 g revizyonu: ilk kilitle ayni kalir


def _bas_kismi(bayt: bytes, beklenen_sha: str) -> bool:
    sinirlar = [i + 1 for i, x in enumerate(bayt) if x == 0x0A] + [len(bayt)]
    return any(hashlib.sha256(bayt[:k]).hexdigest() == beklenen_sha for k in sinirlar)


def _ek_icerigi(aktif: Path, belgeler, veri_yukle: bool) -> dict:
    """Ek kaydin icerigi (21 g revizyonu): kilit icerigi, kalibrasyon on kosullari olmadan; yerine guncel motorla V1."""
    icerik = kilit_icerigi(aktif, belgeler, veri_yukle, onkosul=False)
    icerik['v1'] = v1_raporu(icerik['kod']['motor'])
    return icerik


def _ek_denetimi(ilk: dict, icerik: dict, aktif: Path, belgeler, sira: int) -> list:
    """Ilk kilide gore izin disi degisiklikler (bos ise uygun)."""
    hata = [f'belgeler/{x}' for x in belgeler if x != DEFTER and ilk['belgeler'].get(x) != icerik['belgeler'].get(x)]
    for alan in DEGISMEZ:
        i, c = ilk.get(alan), icerik.get(alan)
        if alan == 'veri':
            i = {k: v for k, v in (i or {}).items() if k not in ('veri_kimligi', 'dosya_sayisi')}
            c = {k: v for k, v in (c or {}).items() if k not in ('veri_kimligi', 'dosya_sayisi')}
        if i != c:
            hata.append(alan)
    if not _bas_kismi((aktif / DEFTER).read_bytes(), ilk['belgeler'][DEFTER]):
        hata.append('defter_yalniz_sona_ekleme')
    if icerik['defter']['satir_sayisi'] != ilk['defter']['satir_sayisi'] + sira:
        hata.append('defter_satir_sayisi')
    return hata


def _ekler(cikti: Path) -> list:
    return sorted(Path(cikti).glob('KILIT_TEKNIK_*.json'), key=lambda y: int(y.stem.rsplit('_', 1)[1]))


def teknik_ek(ilk_kilit, cikti, tur: str, gerekce: str, hata_testi: str, aktif: Path = AKTIF,
              belgeler=KILIT_BELGELERI, veri_yukle: bool = False) -> dict:
    """BANKA Ss3.7 netlestirme 21 g (revizyon): teknik duzeltmenin ek kilit kaydi. Ilk KILIT.json degismez. Tur basina en
    fazla bir ek (kapi, banka_oncesi, banka_sonrasi). Degismezler ilk kilitle ayni; kod degisebilir; defter yalniz sona
    ve satir sayisi ilk + sira. Kalibrasyon on kosullari yerine guncel motorla V1 raporu. Commit + push elle."""
    if tur not in TEKNIK_TURLER:
        raise KilitHatasi(f"teknik ek turu {TEKNIK_TURLER} disinda")
    if not (gerekce and hata_testi):
        raise KilitHatasi("gerekce ve hatayi gosteren test zorunlu")
    ilk_yol, cikti = Path(ilk_kilit), Path(cikti)
    ilk = json.loads(ilk_yol.read_text(encoding='ascii'))
    onceki = _ekler(cikti)
    if any(json.loads(y.read_text(encoding='ascii'))['tur'] == tur for y in onceki):
        raise KilitHatasi(f"{tur} icin teknik ek zaten var (en fazla 1)")
    icerik = _ek_icerigi(aktif, belgeler, veri_yukle)
    hata = _ek_denetimi(ilk, icerik, aktif, belgeler, len(onceki) + 1)
    defter = (aktif / DEFTER).read_bytes()
    hata += [f'defter_{y.name}' for y in onceki
             if not _bas_kismi(defter, json.loads(y.read_text(encoding='ascii'))['icerik']['belgeler'][DEFTER])]
    if hata:
        raise KilitHatasi(f"teknik ekte izin disi degisiklik: {hata}")
    ek = {'ilk_kilit_sha256': _sha(ilk_yol), 'onceki_sha256': _sha(onceki[-1]) if onceki else _sha(ilk_yol),
          'sira': len(onceki) + 1, 'tur': tur, 'gerekce': gerekce, 'hata_testi': hata_testi, 'icerik': icerik,
          'degisen': _farklar({k: ilk.get(k) for k in icerik if k != 'v1'}, {k: v for k, v in icerik.items() if k != 'v1'}),
          'zaman_utc': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())}
    yol = cikti / f'KILIT_TEKNIK_{len(onceki) + 1}.json'
    yol.write_text(json.dumps(ek, indent=1, sort_keys=True, ensure_ascii=True), encoding='ascii')
    return ek


def zincir_dogrula(ilk_kilit, cikti=None, aktif: Path = AKTIF, belgeler=KILIT_BELGELERI, veri_yukle: bool = False,
                   onkosul: bool = True, git: bool = False, kilit_commit: str = None, ek_commitler=(),
                   izinli_turler=TEKNIK_TURLER) -> dict:
    """Ilk kilit + teknik ekler (21 g revizyonu). Ek yoksa `dogrula`. Varsa: zincir (ilk sha, onceki sha, sira), tur
    tekrari yok, her ek izin disi degisiklik icermez, son ekin icerigi bugunku durumla ayni; git=True ise ilk kilidin ve
    her ekin uzak commit'i (sirayla `ek_commitler`) dogrulanir. Doner: gecerli icerik ('ek' alaninda son ek)."""
    ilk_yol = Path(ilk_kilit)
    ekler = _ekler(cikti if cikti is not None else ilk_yol.parent)
    if not ekler:
        return dogrula(ilk_yol, aktif, belgeler, veri_yukle, git=git, onkosul=onkosul, kilit_commit=kilit_commit)
    if git and len(ek_commitler) != len(ekler):
        raise KilitHatasi(f"{len(ekler)} teknik ek var; her biri icin commit bildirilmeli")
    ilk = json.loads(ilk_yol.read_text(encoding='ascii'))
    if set(ilk['belgeler']) != set(belgeler):
        raise KilitHatasi("kilit belge kumesi beklenenden farkli")
    onceki_sha, turler, son, defterler = _sha(ilk_yol), [], None, []
    for i, y in enumerate(ekler, start=1):
        e = json.loads(y.read_text(encoding='ascii'))
        if (y.name != f'KILIT_TEKNIK_{i}.json' or e.get('sira') != i or e['ilk_kilit_sha256'] != _sha(ilk_yol)
                or e['onceki_sha256'] != onceki_sha):
            raise KilitHatasi(f"teknik ek zinciri bozuk: {y.name}")
        if e['tur'] in turler or e['tur'] not in TEKNIK_TURLER:
            raise KilitHatasi(f"teknik ek turu tekrar ya da gecersiz: {e['tur']}")
        if e['tur'] not in izinli_turler:
            raise KilitHatasi(f"bu asama {e['tur']} turundeki teknik eki kabul etmez (izinli: {izinli_turler})")
        c = e['icerik']
        defterler.append((y.name, c['belgeler'][DEFTER]))
        if any(c['belgeler'].get(b) != ilk['belgeler'].get(b) for b in belgeler if b != DEFTER):
            raise KilitHatasi(f"{y.name}: ekonomik belge ilk kilitten farkli")
        if any(c.get(alan) != ilk.get(alan) for alan in ('parametre', 'ortam', 'sabitler')):
            raise KilitHatasi(f"{y.name}: degismez alan ilk kilitten farkli")
        if c['defter']['satir_sayisi'] != ilk['defter']['satir_sayisi'] + i:
            raise KilitHatasi(f"{y.name}: defter satir sayisi ilk + sira degil")
        turler.append(e['tur'])
        onceki_sha, son = _sha(y), e
    simdi = _ek_icerigi(aktif, belgeler, veri_yukle)
    hata = _ek_denetimi(ilk, simdi, aktif, belgeler, len(ekler))
    defter = (aktif / DEFTER).read_bytes()
    hata += [f'defter_{ad}' for ad, h in defterler if not _bas_kismi(defter, h)]
    beklenen = {k: son['icerik'][k] for k in simdi}
    if not veri_yukle:
        beklenen['veri'] = {k: v for k, v in beklenen['veri'].items() if k not in ('veri_kimligi', 'dosya_sayisi')}
    fark = _farklar(beklenen, simdi)
    if hata or fark:
        raise KilitHatasi(f"son teknik ekten sonra degisen ya da izin disi: {hata + fark}")
    out = dict(ilk)
    out.update({k: son['icerik'][k] for k in ('kod', 'defter', 'belgeler')})
    out['onkosul'] = dict(ilk.get('onkosul') or {}, v1=son['icerik']['v1'])
    out['ek'] = {'sira': son['sira'], 'tur': son['tur'], 'sha256': onceki_sha}
    if git:
        out['git_kilit'] = git_denetimi(ilk_yol, kilit_commit)
        out['git_ekler'] = [git_denetimi(y, c) for y, c in zip(ekler, ek_commitler)]
    return out


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    if len(argv) not in (2, 3) or argv[0] not in ('uret', 'dogrula'):
        print(__doc__)
        return 2
    if argv[0] == 'uret':
        k = uret(argv[1])
        print(json.dumps({'KILIT': str(Path(argv[1]) / 'KILIT.json'), 'belge': len(k['belgeler']), 'kod': k['kod']}))
    else:
        dogrula(argv[1], veri_yukle=True, git=True, kilit_commit=argv[2] if len(argv) == 3 else None)
        print('KILIT dogrulandi')
    return 0


if __name__ == '__main__':
    sys.exit(main())
