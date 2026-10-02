"""Kesintiye dayanikli kalibrasyon kosucusu (BANKA_ONKAYIT_TASLAK Ss3.7 "Kesinti ve devam", 3. revizyon).

Kullanim (v8 klasorunden):
  python -m kalibrasyon.kosucu <cikti_dizini> duzey1 [--isci N] [--n_yol 2000]
  python -m kalibrasyon.kosucu <cikti_dizini> duzey2 [--isci N]
  python -m kalibrasyon.kosucu <cikti_dizini> durum
Duraklatma: cikti dizinine `DUR` adli bos dosya koy (yeni birim baslamaz, suren birimler biter) ya da sureci kapat
(yalniz yarim birimler kaybolur). Ayni komutla yeniden baslatilinca kaldigi yerden devam eder. Sirasi ve isci sayisi
sonucu degistirmez. Ekrana ve ilerleme.log'a yalniz birim sayilari yazilir (sonuc degeri yazilmaz)."""
import os

for _k in ('OMP_NUM_THREADS', 'MKL_NUM_THREADS', 'OPENBLAS_NUM_THREADS', 'NUMEXPR_NUM_THREADS'):
    os.environ[_k] = '1'

import argparse  # noqa: E402
import hashlib  # noqa: E402
import json  # noqa: E402
import sys  # noqa: E402
import time  # noqa: E402
from concurrent.futures import FIRST_COMPLETED, ProcessPoolExecutor, wait  # noqa: E402
from pathlib import Path  # noqa: E402

V8 = Path(__file__).resolve().parents[1]
if str(V8) not in sys.path:
    sys.path.insert(0, str(V8))

from kalibrasyon import birim as B  # noqa: E402

IS_LISTESI = 'IS_LISTESI.json'
EK_LISTE = 'IS_LISTESI_EK.jsonl'
DUR = 'DUR'


class KosucuHatasi(RuntimeError):
    """Is listesi degisti, kimlik uyusmazligi ya da birim hatasi: kosu durur."""


# --- is listeleri (Ss3.7 Duzey 2-a, 2-b; Duzey 1) ---

def duzey1_listesi(n_yol: int) -> list:
    return [{'duzey': 1, 'ayar_no': a, 'tur': 'ayar', 'n_yol': n_yol} for a in range(128)]


def duzey2_listesi() -> list:
    out = []
    for yol in range(1, 101):                                         # 2-a: kappa = 0, A ve B
        for m in ('A', 'B'):
            for tur in ('birincil', 'x2', 'x3'):
                out.append({'duzey': 2, 'ayar_no': 0, 'yol_no': yol, 'mimari': m, 'tur': tur})
    for ayar in range(1, 5):                                          # 2-b: kappa > 0 birincil A
        for yol in range(1, 11):
            out.append({'duzey': 2, 'ayar_no': ayar, 'yol_no': yol, 'mimari': 'A', 'tur': 'birincil'})
    for ayar in range(0, 5):                                          # 2-b null (kappa = 0: 2-a'nin 1-10. yollari)
        for yol in range(1, 11):
            for p in range(1, 51):
                out.append({'duzey': 2, 'ayar_no': ayar, 'yol_no': yol, 'mimari': 'A', 'tur': 'null', 'null_no': p})
    return out


def cikarma_turet(k: dict, govde: dict, govde_sha: str) -> list:
    """Duzey 2-a birincil biriminden B10 birimleri: alt katki sirasinin ilk 10'u (esitlikte kucuk coin no)."""
    if k['duzey'] != 2 or k['tur'] != 'birincil' or k['ayar_no'] != 0:
        return []
    return [{'duzey': 2, 'ayar_no': 0, 'yol_no': k['yol_no'], 'mimari': k['mimari'], 'tur': 'cikarma',
             'cikan': int(c), 'birincil_sha': govde_sha} for c in govde['alt_katki_no'][:10]]


# --- isci ---

_ISCI = {}


def _isci_hazirla(kimlikler: dict, beta, parametre_denetimi: bool = True):
    gercek = {'kod': B.kod_kimligi(), 'motor': B.motor_kimligi(), 'ortam': B.ortam_kimligi()}
    if parametre_denetimi:                   # Codex T12-9: parametre kimligi ve beta ayni HAR baytlarindan
        from kalibrasyon.yurutucu import har_paketi
        from motor.tipler import Parametreler
        sha, beta_d = har_paketi()
        gercek['parametre'] = B.parametre_kimligi(Parametreler(), sha)
        if tuple(beta) != beta_d:
            raise KosucuHatasi("isciye verilen beta HAR sonuc dosyasindakiyle ayni degil")
    for ad, deger in gercek.items():
        if kimlikler[ad] != deger:
            raise KosucuHatasi(f"isci {ad} kimligi beklenenden farkli (kod kosu sirasinda degismis olabilir)")
    _ISCI.update({'kimlikler': kimlikler, 'beta': beta})


def _gercek_yurut(k: dict):
    from kalibrasyon import yurutucu as Y
    if k['duzey'] == 1:
        return Y.duzey1_birimi(k['ayar_no'], k['n_yol'])
    return Y.duzey2_birimi(k, _ISCI['beta']), None


def _calis(k: dict, cikti: str, yurut):
    govde, diziler = yurut(k)
    B.sonuc_yaz(cikti, k, govde, _ISCI['kimlikler'], diziler=diziler)
    return k, govde


# --- kosucu cekirdegi ---

def _liste_hash(liste) -> str:
    return B.sha256_metin(B.kanonik(liste))


def is_listesi_yaz_ya_da_dogrula(cikti: Path, birimler: list, kimlikler: dict) -> str:
    yol = cikti / IS_LISTESI
    icerik = {'birimler': birimler, 'kimlikler': kimlikler}
    if yol.exists():
        eski = json.loads(yol.read_text(encoding='ascii'))
        if B.kanonik(eski) != B.kanonik(icerik):
            raise KosucuHatasi("is listesi ya da beklenen kimlikler degisti; eski kosuyla karistirilamaz")
    else:
        cikti.mkdir(parents=True, exist_ok=True)
        B._atomik(yol, B.kanonik(icerik).encode('ascii'))
    return hashlib.sha256(yol.read_bytes()).hexdigest()


def _gunluk(cikti: Path, metin: str):
    with open(cikti / 'ilerleme.log', 'a', encoding='utf-8') as f:
        f.write(time.strftime('%Y-%m-%dT%H:%M:%SZ ', time.gmtime()) + metin + '\n')


def calistir(cikti, birimler: list, kimlikler: dict, beta=None, isci: int = 1, yurut=None, turet=cikarma_turet,
             ters: bool = False, max_birim: int = None, sessiz: bool = False) -> dict:
    """Birimleri koser; bitenleri (butunlugu dogrulanmis) atlar; turetilen birimleri ekler. max_birim: bu kosuda en
    fazla bu kadar yeni birim tamamlanir (parcali calisma ve testler). Doner sayim sozlugu."""
    cikti = Path(cikti)
    parametre_denetimi = yurut is None
    yurut = yurut or _gercek_yurut
    for artik in sorted(cikti.glob('*.gecici')):          # yarim atomik yazimlar; is listesinden once (Codex T13-4)
        B.karantina_dosya(cikti, artik)
    liste_sha = is_listesi_yaz_ya_da_dogrula(cikti, birimler, kimlikler)
    npz = lambda k: k['duzey'] == 1
    kuyruk, bitti, ek = [], 0, []

    def kontrol(k):
        nonlocal bitti
        s = B.sonuc_oku(cikti, k, kimlikler, npz=npz(k))
        if s is None:
            return False
        bitti += 1
        zarf = json.loads((cikti / f'{B.birim_adi(k)}.json').read_text(encoding='ascii'))
        for t in turet(k, s[0], zarf['govde_sha256']):
            ek.append(t)
        return True

    for k in (reversed(birimler) if ters else birimler):
        if not kontrol(k):
            kuyruk.append(k)
    # Turetilen birimler: onceki kosularda yazilanlar da ek listeye islenir (tekrar yazilmaz).
    ek_yol = cikti / EK_LISTE
    yazilmis = set()
    if ek_yol.exists():
        # Ek liste yalniz kayittir; turetilen birimler dogrulanmis birincillerden her baslangicta yeniden kurulur.
        # Yarim satir (kesinti) varsa dosya karantinaya alinir ve bastan yazilir (Codex T12-4).
        try:
            yazilmis = {B.kanonik(json.loads(x)) for x in ek_yol.read_text(encoding='ascii').splitlines() if x.strip()}
        except (ValueError, UnicodeDecodeError):
            B.karantina_dosya(cikti, ek_yol)
            yazilmis = set()

    def ek_isle(liste):
        yeni = []
        for t in liste:
            s = B.kanonik(t)
            if s not in yazilmis:
                with open(ek_yol, 'a', encoding='ascii') as f:
                    f.write(s + '\n')
                yazilmis.add(s)
            if not kontrol(t):
                yeni.append(t)
        return yeni

    kuyruk += ek_isle(list(ek))
    ek.clear()
    toplam_taban = len(birimler)
    tamamlanan = 0
    if not sessiz:
        print(f"is listesi {liste_sha[:12]}; taban {toplam_taban}; bitmis {bitti}; kuyruk {len(kuyruk)}", flush=True)
    _gunluk(cikti, f"basla: bitmis {bitti}, kuyruk {len(kuyruk)}, isci {isci}")
    with ProcessPoolExecutor(max_workers=isci, initializer=_isci_hazirla,
                             initargs=(kimlikler, beta, parametre_denetimi)) as havuz:
        suren = {}
        while kuyruk or suren:
            durdur = (cikti / DUR).exists() or (max_birim is not None and tamamlanan + len(suren) >= max_birim)
            while kuyruk and len(suren) < isci and not durdur:
                k = kuyruk.pop(0)
                suren[havuz.submit(_calis, k, str(cikti), yurut)] = k
                durdur = max_birim is not None and tamamlanan + len(suren) >= max_birim
            if not suren:
                break
            biten, _ = wait(suren, return_when=FIRST_COMPLETED)
            for f in biten:
                k = suren.pop(f)
                f.result()                                  # hata -> kosu durur (T4 dahil)
                tamamlanan += 1
                bitti += 1
                zarf = json.loads((cikti / f'{B.birim_adi(k)}.json').read_text(encoding='ascii'))
                govde = B.sonuc_oku(cikti, k, kimlikler, npz=npz(k))[0]
                kuyruk += ek_isle(turet(k, govde, zarf['govde_sha256']))
            if not sessiz:
                print(f"tamamlanan {bitti} (bu kosuda {tamamlanan}); kuyruk {len(kuyruk)}; suren {len(suren)}",
                      flush=True)
    _gunluk(cikti, f"dur: bitmis {bitti}, kalan {len(kuyruk)}")
    return {'bitmis': bitti, 'bu_kosuda': tamamlanan, 'kalan': len(kuyruk), 'liste_sha': liste_sha}


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument('cikti')
    ap.add_argument('is_', choices=('duzey1', 'duzey2', 'durum'))
    ap.add_argument('--isci', type=int, default=max(1, (os.cpu_count() or 2) - 2))
    ap.add_argument('--n_yol', type=int, default=2000)
    ap.add_argument('--max_birim', type=int, default=None)
    ap.add_argument('--ters', action='store_true')
    a = ap.parse_args(argv)
    from kalibrasyon.yurutucu import har_paketi
    from motor.tipler import Parametreler
    har_sha, beta = har_paketi()
    kimlikler = B.beklenen_kimlikler(Parametreler(), har_sha)
    cikti = Path(a.cikti)
    if a.is_ == 'durum':
        liste = json.loads((cikti / IS_LISTESI).read_text(encoding='ascii'))['birimler']
        tamam = sum(1 for k in liste if (cikti / f'{B.birim_adi(k)}.json').exists())
        print(f"taban birim {len(liste)}; dosyasi olan {tamam}")
        return 0
    birimler = duzey1_listesi(a.n_yol) if a.is_ == 'duzey1' else duzey2_listesi()
    sonuc = calistir(cikti, birimler, kimlikler, beta=beta, isci=a.isci, ters=a.ters, max_birim=a.max_birim)
    print(json.dumps(sonuc))
    return 0


if __name__ == '__main__':
    sys.exit(main())
