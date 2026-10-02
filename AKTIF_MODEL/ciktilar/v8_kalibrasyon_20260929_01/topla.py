"""Kilit Adim 3, 3.10-3.11: toplama surucusu (kalibrasyon.toplama; BANKA_ONKAYIT_TASLAK Ss3.3, Ss3.7).

Bütün birimler bittikten ve bitis denetimi gectikten sonra BIR KEZ kosar (Ss3.7: olcutler ve oranlar butun birimler
bitince bir kez hesaplanir). On kosullar (biri saglanmazsa hicbir sey hesaplanmaz):
- bitis_sonuc.json var ve gecti = true;
- duzey1/ ve duzey2/ is listelerindeki beklenen kimlikler KOD_DONDURMA.json'daki dort kimlikle ayni;
- dondurmadaki deneme defteri (KOD_DONDURMA sha256'si) bugunku defterin bir satir sinirinda biten bas kismi (yalniz
  sona ekleme; BANKA Ss3.7 madde 8, netlestirme 21 f); N = 159 + N_v8 bugunku defterden;
- (Codex T18) bitis_sonuc.json kanit blogu var, dort kimligi ve KOD_DONDURMA sha'si dondurmayla ayni; duzey2/ klasorunun
  girdi ozeti (is listesi, ek liste, birim dosyalarinin birlesik ozeti; kanit.klasor_ozeti) bitis kanitindakiyle AYNI.
  Ozet hesaptan sonra yeniden alinir; hesap sirasinda degistiyse TOPLAMA yazilmaz. Tuketilen ozet TOPLAMA kanitina
  ('duzey2_tuketilen') yazilir; kilit.onkosullar bunu bitis kanitiyla karsilastirir.
- (Codex T19 CIDDI-1) duzey1/ girdileri onceden kaydedilmis DUZEY1_OZET.json'a zorunlu bagli: kimlikler dondurmayla,
  is listesi sha256'si ozetle ayni; birim kumesi = is listesinin birimleri = ozetin birimleri = klasordeki d1_* dosyalari;
  her birimin JSON dosya baytlarinin sha256'si = json_sha256, NPZ dosya baytlarinin sha256'si = npz_sha256 ve zarfin
  govde.npz_sha256'si. Ozet hesaptan sonra yeniden dogrulanir; tuketilen ozet ('duzey1_tuketilen': ozet dosyasinin
  sha256'si, is listesi, dosya sayisi, birlesik ozet) TOPLAMA'ya yazilir, kilit bunu DUZEY1_OZET.json ile karsilastirir.
Sira: Duzey 1 (sigma_SR_bag, N, kurallar ya da KILIT_BEKLER) -> kurallar varsa Duzey 2 (2-a tarama, 2-b betimsel).
Cikti: TOPLAMA.json (ekrana yalniz durumlar yazilir). Kanit zinciri (Codex T17-a): TOPLAMA.json ortak 'kanit' blogunu
(kanit.py) tasir: dogrulanan dort kimlik, HAR ve KOD_DONDURMA sha256'lari; kaynak olarak bitis_sonuc.json, iki is listesi
ve deneme defterinin sha256'lari. Kullanim: python topla.py"""
import os

for _k in ('OMP_NUM_THREADS', 'MKL_NUM_THREADS', 'OPENBLAS_NUM_THREADS', 'NUMEXPR_NUM_THREADS'):
    os.environ[_k] = '1'

import hashlib  # noqa: E402
import json  # noqa: E402
import sys  # noqa: E402
from pathlib import Path  # noqa: E402

import numpy as np  # noqa: E402

BURASI = Path(__file__).resolve().parent
AKTIF = BURASI.parents[1]
V8 = AKTIF / 'v8'
sys.path.insert(0, str(V8))
sys.path.insert(0, str(BURASI))

import kanit  # noqa: E402
from kalibrasyon import toplama as T  # noqa: E402
from kalibrasyon.birim import birim_adi  # noqa: E402
from kalibrasyon.kosucu import EK_LISTE, IS_LISTESI  # noqa: E402

KAYIT = AKTIF.parent / 'GECMIS' / '2026_09_19_oncesi' / 'DENEY_TRIAL_REGISTRY.csv'
DEFTER = AKTIF / 'ciktilar' / 'v8_banka_20260924_01' / 'V8_DENEME_DEFTERI.csv'
N_YOL = 2000
D1_OZET = 'DUZEY1_OZET.json'


class OnKosulHatasi(RuntimeError):
    pass


def _json(x):
    if isinstance(x, dict):
        return {str(k): _json(v) for k, v in x.items()}
    if isinstance(x, (list, tuple)):
        return [_json(v) for v in x]
    if isinstance(x, np.ndarray):
        return _json(x.tolist())
    if isinstance(x, (np.floating, float)):
        v = float(x)
        return v if np.isfinite(v) else repr(v)
    if isinstance(x, (np.integer,)):
        return int(x)
    if isinstance(x, (np.bool_,)):
        return bool(x)
    if hasattr(x, '__dict__') and not isinstance(x, type):
        return _json(vars(x))
    return x


def girdi_ozeti(d: Path) -> dict:
    return kanit.klasor_ozeti(d, IS_LISTESI, EK_LISTE)


def defter_bas_kismi(bayt: bytes, beklenen_sha: str) -> bool:
    """Dondurmadaki defter bugunkunun satir sinirinda biten bas kismi mi (21 f; yalniz sona ekleme)."""
    sinirlar = [i + 1 for i, b in enumerate(bayt) if b == 0x0A] + [len(bayt)]
    return any(hashlib.sha256(bayt[:k]).hexdigest() == beklenen_sha for k in sinirlar)


def on_kosullar(burasi: Path = BURASI, defter: Path = DEFTER) -> tuple:
    """Doner (kimlikler, dondurma, duzey2 girdi ozeti, duzey1 bagi). Biri saglanmazsa OnKosulHatasi; hicbir sey
    hesaplanmaz."""
    b = burasi / 'bitis_sonuc.json'
    if not b.exists():
        raise OnKosulHatasi("bitis denetimi yok ya da gecmedi")
    bitis = json.loads(b.read_text(encoding='utf-8'))
    if not bitis.get('gecti'):
        raise OnKosulHatasi("bitis denetimi yok ya da gecmedi")
    dondurma = json.loads((burasi / 'KOD_DONDURMA.json').read_text(encoding='utf-8'))
    beklenen = {k: dondurma['kimlikler'][k] for k in ('kod', 'motor', 'parametre', 'ortam')}
    kim = {}
    for d in ('duzey1', 'duzey2'):
        k = json.loads((burasi / d / IS_LISTESI).read_text(encoding='ascii'))['kimlikler']
        if k != beklenen:
            raise OnKosulHatasi(f"{d} kimlikleri dondurmadan farkli")
        kim[d] = k
    if not defter_bas_kismi(Path(defter).read_bytes(), dondurma['deneme_defteri_sha256']):
        raise OnKosulHatasi("deneme defteri dondurmadan beri degismis (yalniz sona satir eklenebilir)")
    bk = bitis.get('kanit')
    if not isinstance(bk, dict) or not isinstance(bk.get('kaynak'), dict):
        raise OnKosulHatasi("bitis kaniti yok (bitis.py'nin kanit blogu yazan surumuyle kos)")
    if bk.get('kimlikler') != beklenen or bk.get('kod_dondurma_sha256') != kanit.sha_dosya(burasi / 'KOD_DONDURMA.json'):
        raise OnKosulHatasi("bitis kaniti baska kimliklerle ya da baska bir KOD_DONDURMA ile")
    ozet = girdi_ozeti(burasi / 'duzey2')
    fark = sorted(k for k in ozet if ozet[k] != bk['kaynak'].get(k))
    if fark:
        raise OnKosulHatasi(f"duzey2 girdileri bitis kanitindakinden farkli: {fark}")
    return kim, dondurma, ozet, duzey1_bagi(burasi, beklenen)


def duzey1_bagi(burasi: Path, beklenen: dict) -> dict:
    """Duzey 1 girdilerinin DUZEY1_OZET.json'a zorunlu bagi (Codex T19 CIDDI-1); saglanmazsa OnKosulHatasi.
    Doner: tuketilen ozet (ozet dosyasinin sha256'si, is listesi sha256'si, dosya sayisi, JSON + NPZ birlesik ozeti)."""
    d = Path(burasi) / 'duzey1'
    oy = Path(burasi) / D1_OZET
    if not oy.exists():
        raise OnKosulHatasi("duzey1: DUZEY1_OZET.json yok")
    oz = json.loads(oy.read_text(encoding='utf-8'))
    if oz.get('kimlikler') != beklenen:
        raise OnKosulHatasi("duzey1: DUZEY1_OZET kimlikleri dondurmadan farkli")
    is_sha = kanit.sha_dosya(d / IS_LISTESI)
    if oz.get('is_listesi_sha256') != is_sha:
        raise OnKosulHatasi("duzey1: is listesi DUZEY1_OZET'tekinden farkli")
    if oz.get('gecersiz') != 0:
        raise OnKosulHatasi("duzey1: DUZEY1_OZET gecersiz birim bildiriyor")
    adlar = sorted(birim_adi(k) for k in json.loads((d / IS_LISTESI).read_text(encoding='ascii'))['birimler'])
    kayit = {b['birim']: b for b in oz.get('birimler', [])}
    diskte = {p.name for p in d.glob('d1_*.json')} | {p.name for p in d.glob('d1_*.npz')}
    if (sorted(kayit) != adlar or oz.get('birim_sayisi') != len(adlar) or len(kayit) != len(oz.get('birimler', []))
            or diskte != {f'{a}{u}' for a in adlar for u in ('.json', '.npz')}):
        raise OnKosulHatasi("duzey1: birim kumesi (is listesi, DUZEY1_OZET, klasor) ayni degil")
    h = {}
    for ad in adlar:
        jb, nb = (d / f'{ad}.json').read_bytes(), (d / f'{ad}.npz').read_bytes()
        js, ns = kanit.sha_bayt(jb), kanit.sha_bayt(nb)
        if js != kayit[ad].get('json_sha256') or ns != kayit[ad].get('npz_sha256'):
            raise OnKosulHatasi(f"duzey1: {ad} dosyalari DUZEY1_OZET'tekinden farkli")
        if json.loads(jb.decode('ascii'))['govde'].get('npz_sha256') != ns:
            raise OnKosulHatasi(f"duzey1: {ad} zarfinin npz_sha256'si npz dosyasiyla ayni degil")
        h[f'{ad}.json'], h[f'{ad}.npz'] = js, ns
    return {'ozet_sha256': kanit.sha_dosya(oy), 'is_listesi_sha256': is_sha, 'dosya': len(h),
            'birlesik_sha256': kanit.birlesik(h)}


def main(burasi: Path = BURASI, defter: Path = DEFTER, kayit: Path = KAYIT):
    kim, dondurma, ozet, d1_ozet = on_kosullar(burasi, defter)
    d1 = T.duzey1_topla(burasi / 'duzey1', kim['duzey1'], N_YOL, kayit, defter)
    if d1['rapor']['N'] < dondurma['N']:                       # 21 f: defter yalniz buyur; N bugunku defterden
        raise OnKosulHatasi(f"N {d1['rapor']['N']} dondurmadaki {dondurma['N']}'den kucuk")
    sonuc = {'duzey1': {'durum': d1['durum'], 'rapor': d1['rapor']}}
    if d1['kurallar'] is not None:
        sonuc['duzey2'] = T.duzey2_topla(burasi / 'duzey2', kim['duzey2'], d1['kurallar'])
        sonuc['durum'] = 'TAMAM' if d1['durum'] == 'TAMAM' and sonuc['duzey2']['durum'] == 'TAMAM' else 'KILIT_BEKLER'
    else:
        sonuc['durum'] = 'KILIT_BEKLER'
    try:
        d1_sonra = duzey1_bagi(burasi, {k: dondurma['kimlikler'][k] for k in ('kod', 'motor', 'parametre', 'ortam')})
    except OnKosulHatasi:
        d1_sonra = None
    if girdi_ozeti(burasi / 'duzey2') != ozet or d1_sonra != d1_ozet:
        raise OnKosulHatasi("girdiler toplama sirasinda degisti; TOPLAMA yazilmadi")
    from kalibrasyon.yurutucu import har_paketi
    sonuc['kanit'] = kanit.blok(__file__, kim['duzey2'], har_paketi()[0], {
        'bitis_sonuc_sha256': kanit.sha_dosya(burasi / 'bitis_sonuc.json'),
        'duzey1_is_listesi_sha256': kanit.sha_dosya(burasi / 'duzey1' / IS_LISTESI),
        'duzey2_is_listesi_sha256': kanit.sha_dosya(burasi / 'duzey2' / IS_LISTESI),
        'defter_sha256': kanit.sha_dosya(defter), 'defter_dondurma_sha256': dondurma['deneme_defteri_sha256'],
        'duzey2_tuketilen': ozet, 'duzey1_tuketilen': d1_ozet}, burasi=burasi)
    (burasi / 'TOPLAMA.json').write_text(json.dumps(_json(sonuc), indent=1, ensure_ascii=False), encoding='utf-8')
    print(json.dumps({'duzey1': d1['durum'], 'duzey2': sonuc.get('duzey2', {}).get('durum'), 'durum': sonuc['durum']}),
          flush=True)
    return 0


if __name__ == '__main__':
    sys.exit(main())
