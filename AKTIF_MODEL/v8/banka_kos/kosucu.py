"""Banka koşucusu (BANKA §2.4; BK-1, BK-2, BK-3, BK-6). Tek çağrılık iş listesinin kesintiye dayanıklı yürütülmesi.

Klasör düzeni (cikti):
  IS_LISTESI.json                     açık: taban birimler, beklenen kimlikler, alıcı (age açık anahtarı)
  denetim/birim/<ad>.json             açık: birim tanımı, düz metin sha256, şifreli dosya sha256, açık denetim sözlüğü
  sonuc/birim/<ad>.age                kapalı: birim düz sonucu (kanonik JSON), kullanıcının açık anahtarına şifreli
  sonuc/hata/<ad>.age                 kapalı: hata ayrıntısı (motor istisnası NAV taşıyabilir); açık günlüğe yalnız hash
  denetim/ilerleme.log                açık: yalnız sayılar ve adlar
  SONUC_DAMGA.json                    açık: bütün birimlerin (ad, düz sha, şifreli sha) listesi ve kök hash'i
Bitmiş birim: açık kayıt var, şifreli dosya var ve sha256'sı kayıttakiyle aynı. Düz metin diske yazılmaz.
B10 (BK-6): birincil birimin alt katkı sırasının ilk 10'u çıkarma birimi olur. Birim tanımında coin adı yoktur (opak
'sira' + birincil düz sha); sıra→coin eşlemesi yalnız bellektedir. Birincil bu süreçte hesaplanmadıysa (kesintiden
sonra) bellekte yeniden yürütülür ve düz sha'sı kayıttakiyle aynı olmalıdır (deterministiklik denetimi).
Hata sınırı (Codex T17-b): birim hesabı, işçi başlatma, birincilin yeniden yürütülmesi ve koşucunun kendisi aynı sınırdan
geçer. Her istisnanın izi şifreli yazılır (sonuc/hata/<etiket>.age); dışarı yalnız sabit mesaj + düz izin sha256'sı çıkar,
özgün bağlam bastırılır. Mühürleme de başarısız olursa mesaj 'yazilamadi' der; düz iz yine dışarı çıkmaz.
"""
import hashlib
import json
import os
import time
import traceback
from concurrent.futures import FIRST_COMPLETED, ProcessPoolExecutor, wait
from pathlib import Path

from . import age

IS_LISTESI = 'IS_LISTESI.json'
DUR = 'DUR'


class BankaKosuHatasi(RuntimeError):
    pass


def kanonik(x) -> bytes:
    return json.dumps(x, sort_keys=True, separators=(',', ':'), ensure_ascii=True, allow_nan=True).encode('ascii')


def sha(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def birim_adi(b: dict) -> str:
    g, m = b['grup'], b['mimari']
    if g == 'izgara':
        return f"izgara_{m}_n{int(b['nav0'])}_k{int(b['maliyet_k'])}"
    if g == 'kelly':
        return f"kelly_{m}_L{b['L']:g}_k{int(b['maliyet_k'])}"
    if g == 'cikarma_btc_eth':
        return f"cikarma_{m}_{b['cikan']}"
    if g == 'cikarma':
        return f"cikarma_{m}_s{b['sira']:02d}"
    if g == 'delist':
        return f"delist_{m}_h{b['h_L']:g}"
    if g == 'null':
        return f"null_{m}_p{b['null_no']:03d}"
    return f"{g}_{m}"


def _atomik(yol: Path, veri: bytes):
    yol.parent.mkdir(parents=True, exist_ok=True)
    gecici = yol.with_name(yol.name + '.gecici')
    with open(gecici, 'wb') as f:
        f.write(veri)
        f.flush()
        os.fsync(f.fileno())
    os.replace(gecici, yol)


def bitmis_mi(cikti: Path, ad: str) -> bool:
    k, s = cikti / 'denetim' / 'birim' / f'{ad}.json', cikti / 'sonuc' / 'birim' / f'{ad}.age'
    if not (k.exists() and s.exists()):
        return False
    try:
        return json.loads(k.read_text(encoding='ascii'))['sifreli_sha256'] == sha(s.read_bytes())
    except (ValueError, KeyError):
        return False


def kayit_oku(cikti: Path, ad: str) -> dict:
    return json.loads((cikti / 'denetim' / 'birim' / f'{ad}.json').read_text(encoding='ascii'))


# ---- hata sınırı (Codex T17-b) -------------------------------------------------------------------------------------

def _muhurle(cikti, alici: str, etiket: str) -> str:
    """Etkin istisnanın izini şifreli yazar; düz izin sha256'sını döner. Kendisi hiçbir istisnayı dışarı sızdırmaz."""
    try:
        iz = traceback.format_exc().encode('utf-8')
        h = sha(iz)
    except Exception:
        return 'yazilamadi'
    try:
        _atomik(Path(cikti) / 'sonuc' / 'hata' / f'{etiket}.age', age.sifrele(alici, iz))
    except Exception:
        return h + ' (hata dosyasi yazilamadi)'
    return h


def _sinirli(cikti, alici: str, etiket: str, mesaj: str, fn, *a):
    """Ortak hata sınırı: fn'in her istisnası mühürlenir; dışarı yalnız sabit mesaj + hash çıkar, bağlam bastırılır."""
    try:
        return fn(*a)
    except Exception:
        h = _muhurle(cikti, alici, etiket)
    raise BankaKosuHatasi(f"{mesaj} (ayrinti sonuc/hata/{etiket}.age; duz sha256 {h})") from None


# ---- işçi -----------------------------------------------------------------------------------------------------------

_ISCI = {}


def _isci_hazirla(baglam_kur, alici: str, cikti: str):
    """İşçi başlatıcısı hiç istisna fırlatmaz (havuz başlatıcı hatasını düz iz olarak stderr'e yazardı); hata mühürlenir
    ve işçinin her birimi bu sabit hatayla durur."""
    _ISCI.update({'alici': alici, 'hata': None})
    try:
        _ISCI['bag'] = _sinirli(cikti, alici, f'isci_baslat_{os.getpid()}', 'isci baslatilamadi', baglam_kur)
    except BankaKosuHatasi as e:
        _ISCI['hata'] = str(e)


def _birim_govde(b: dict, cikan, yurut, bag, alici: str, cikti: Path) -> tuple:
    ad = birim_adi(b)
    calis = dict(b, cikan=cikan) if cikan is not None else b
    duz, acik = yurut(calis, bag)
    duz_b = kanonik(duz)
    sifreli = age.sifrele(alici, duz_b)
    _atomik(cikti / 'sonuc' / 'birim' / f'{ad}.age', sifreli)
    _atomik(cikti / 'denetim' / 'birim' / f'{ad}.json', kanonik(
        {'birim': b, 'duz_sha256': sha(duz_b), 'sifreli_sha256': sha(sifreli), 'acik': acik}))
    b10 = None
    if b['grup'] == 'birincil':
        b10 = list(duz['olcum']['alt_katki_sirasi'][:10])
    return ad, sha(duz_b), b10


def birim_hesapla(b: dict, cikan, yurut, bag, alici: str, cikti: str) -> tuple:
    """Birimi yürütür, düz sonucu şifreler ve yazar. Doner (ad, düz sha, b10 listesi | None). Yürütme, serileştirme,
    şifreleme ve yazımın hepsi hata sınırının içindedir."""
    ad = birim_adi(b)
    return _sinirli(cikti, alici, ad, f"{ad}: birim hatasi", _birim_govde, b, cikan, yurut, bag, alici, Path(cikti))


def _isci_calis(b, cikan, yurut, cikti):
    if _ISCI.get('hata'):
        raise BankaKosuHatasi(_ISCI['hata'])
    return birim_hesapla(b, cikan, yurut, _ISCI['bag'], _ISCI['alici'], cikti)


# ---- koşucu ---------------------------------------------------------------------------------------------------------

def _gunluk(cikti: Path, metin: str):
    (cikti / 'denetim').mkdir(parents=True, exist_ok=True)
    with open(cikti / 'denetim' / 'ilerleme.log', 'a', encoding='utf-8') as f:
        f.write(time.strftime('%Y-%m-%dT%H:%M:%SZ ', time.gmtime()) + metin + '\n')


def b10_birimleri(birincil: dict, duz_sha: str, liste: list) -> list:
    """Opak B10 birimleri (coin adı yok) ve sıra -> coin eşlemesi (yalnız bellek)."""
    tanim, esleme = [], {}
    for i, c in enumerate(liste, start=1):
        b = dict(birincil, grup='cikarma', sira=i, birincil_sha=duz_sha)
        tanim.append(b)
        esleme[birim_adi(b)] = c
    return tanim, esleme


def calistir(cikti, birimler: list, kimlikler: dict, alici: str, yurut, baglam_kur, isci: int = 1,
             max_birim: int = None, sessiz: bool = False) -> dict:
    """birimler: ayar.birimler(M); yurut(b, bag) -> (duz, acik); baglam_kur() -> bag (işçi başına bir kez).
    Dışarı yalnız BankaKosuHatasi çıkar; mesajı sabittir, bağlamı (işçinin uzak izi dahil) bastırılır."""
    try:
        return _calistir(Path(cikti), birimler, kimlikler, alici, yurut, baglam_kur, isci, max_birim, sessiz)
    except BankaKosuHatasi as e:
        mesaj = str(e)                          # kendi hatalarımız: sabit mesaj (ad, hash; coin/performans yok)
    except Exception:
        etiket = 'kosucu_' + time.strftime('%Y%m%dT%H%M%SZ', time.gmtime())
        mesaj = f"kosucu hatasi (ayrinti sonuc/hata/{etiket}.age; duz sha256 {_muhurle(cikti, alici, etiket)})"
    raise BankaKosuHatasi(mesaj) from None


def _yeniden_yurut(yurut, baglam_kur, birincil: dict) -> tuple:
    duz, _ = yurut(birincil, baglam_kur())
    return sha(kanonik(duz)), list(duz['olcum']['alt_katki_sirasi'][:10])


def _calistir(cikti: Path, birimler, kimlikler, alici, yurut, baglam_kur, isci, max_birim, sessiz) -> dict:
    icerik = kanonik({'birimler': birimler, 'kimlikler': kimlikler, 'alici': alici})
    yol = cikti / IS_LISTESI
    if yol.exists():
        if yol.read_bytes() != icerik:
            raise BankaKosuHatasi("is listesi, kimlikler ya da alici degisti")
    else:
        _atomik(yol, icerik)
    for artik in sorted(cikti.rglob('*.gecici')):
        artik.replace(artik.with_name(artik.name + '.karantina'))
    birincil = next(b for b in birimler if b['grup'] == 'birincil')
    b_ad = birim_adi(birincil)
    kuyruk = [b for b in birimler if not bitmis_mi(cikti, birim_adi(b))]
    b10_esleme, b10_gerekli = {}, True
    bitti = len(birimler) - len(kuyruk)

    def b10_ekle(duz_sha, liste):
        nonlocal b10_gerekli
        tanim, esleme = b10_birimleri(birincil, duz_sha, liste)
        b10_esleme.update(esleme)
        kuyruk.extend(b for b in tanim if not bitmis_mi(cikti, birim_adi(b)))
        b10_gerekli = False

    if bitmis_mi(cikti, b_ad):
        kayit = kayit_oku(cikti, b_ad)
        tanim, _ = b10_birimleri(birincil, kayit['duz_sha256'], [None] * 10)
        if all(bitmis_mi(cikti, birim_adi(b)) for b in tanim):
            b10_gerekli = False
        else:                                   # BK-6: birincil bellekte yeniden yürütülür, sha denetlenir
            y_sha, liste = _sinirli(cikti, alici, f'yeniden_{b_ad}', 'birincil yeniden yurutulemedi', _yeniden_yurut,
                                    yurut, baglam_kur, birincil)
            if y_sha != kayit['duz_sha256']:
                raise BankaKosuHatasi("birincil yeniden yurutmede ayni sonucu vermedi (deterministiklik)")
            b10_ekle(kayit['duz_sha256'], liste)
    if not sessiz:
        print(f"banka: taban {len(birimler)}; bitmis {bitti}; kuyruk {len(kuyruk)}", flush=True)
    _gunluk(cikti, f"basla: bitmis {bitti}, kuyruk {len(kuyruk)}, isci {isci}")
    tamamlanan = 0
    with ProcessPoolExecutor(max_workers=isci, initializer=_isci_hazirla,
                             initargs=(baglam_kur, alici, str(cikti))) as havuz:
        suren = {}
        while kuyruk or suren:
            durdur = (cikti / DUR).exists() or (max_birim is not None and tamamlanan + len(suren) >= max_birim)
            while kuyruk and len(suren) < isci and not durdur:
                b = kuyruk.pop(0)
                cikan = b10_esleme.get(birim_adi(b))
                if b['grup'] == 'cikarma' and cikan is None:
                    raise BankaKosuHatasi("B10 esleme bellekte yok")
                suren[havuz.submit(_isci_calis, b, cikan, yurut, str(cikti))] = b
                durdur = max_birim is not None and tamamlanan + len(suren) >= max_birim
            if not suren:
                break
            biten, _ = wait(suren, return_when=FIRST_COMPLETED)
            for f in biten:
                suren.pop(f)
                ad, duz_sha, b10 = f.result()
                tamamlanan += 1
                bitti += 1
                if b10 is not None and b10_gerekli:
                    b10_ekle(duz_sha, b10)
            if not sessiz:
                print(f"banka: tamamlanan {bitti}; kuyruk {len(kuyruk)}; suren {len(suren)}", flush=True)
    _gunluk(cikti, f"dur: bitmis {bitti}, kalan {len(kuyruk)}")
    return {'bitmis': bitti, 'bu_kosuda': tamamlanan, 'kalan': len(kuyruk) + (10 if b10_gerekli else 0)}


def damga_yaz(cikti, birimler: list) -> dict:
    """Bütün birimler (taban + B10) bitmişse SONUC_DAMGA.json (BK-3)."""
    cikti = Path(cikti)
    birincil = next(b for b in birimler if b['grup'] == 'birincil')
    kayit = kayit_oku(cikti, birim_adi(birincil))
    tanim, _ = b10_birimleri(birincil, kayit['duz_sha256'], [None] * 10)
    satirlar = []
    for b in list(birimler) + tanim:
        ad = birim_adi(b)
        if not bitmis_mi(cikti, ad):
            raise BankaKosuHatasi(f"birim bitmemis: {ad}")
        k = kayit_oku(cikti, ad)
        satirlar.append([ad, k['duz_sha256'], k['sifreli_sha256']])
    satirlar.sort()
    damga = {'birim_sayisi': len(satirlar), 'birimler': satirlar, 'kok_sha256': sha(kanonik(satirlar)),
             'zaman_utc': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())}
    _atomik(cikti / 'SONUC_DAMGA.json', json.dumps(damga, indent=1).encode('ascii'))
    return damga
