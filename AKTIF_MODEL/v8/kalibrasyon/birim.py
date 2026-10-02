"""Kalibrasyon is birimi: kimlik, dort beklenen kimlik, kanonik sonuc dosyasi, atomik yazma ve butunluk dogrulamasi
(BANKA_ONKAYIT_TASLAK Ss3.7 "Kesinti ve devam", 3. revizyon; Codex T10-3/T10-4).

Sonuc dosyasi kanonik JSON'dur (anahtarlar sirali, sabit ayiricilar, float Python repr, nan/inf izinli):
  {"birim": kimlik, "kimlikler": {kod, motor, parametre, ortam}, "govde": ..., "govde_sha256": sha256(kanonik(govde))}.
Buyuk diziler (Duzey 1) ayni adli .npz dosyasina yazilir; govde npz'nin sha256'sini tasir. Yazma: gecici dosya +
os.replace (atomik); npz once, zarf JSON sonra (zarf tamamlanma isaretidir). Okuma: zarf ayristirilamiyor, govde ya da
npz ozeti tutmuyor, birim ya da kimlikler beklenenden farkliysa dosyalar karantinaya tasinir (silinmez) ve None doner."""
import hashlib
import io
import json
import os
import sys
from pathlib import Path

import numpy as np

V8 = Path(__file__).resolve().parents[1]
KARANTINA = '_karantina'


def kanonik(x) -> str:
    return json.dumps(x, sort_keys=True, separators=(',', ':'), ensure_ascii=True, allow_nan=True)


def sha256_metin(s: str) -> str:
    return hashlib.sha256(s.encode('utf-8')).hexdigest()


def _birlesik_sha256(dosyalar) -> str:
    """v8_calistir._birlesik_sha256 ile ayni tanim (yol V8'e gore + bayt icerik, sirali)."""
    h = hashlib.sha256()
    for p in dosyalar:
        h.update(str(p.relative_to(V8)).replace('\\', '/').encode('utf-8'))
        h.update(p.read_bytes())
    return h.hexdigest()


def _py(kok: Path) -> list:
    return sorted(p for p in kok.rglob('*.py') if '__pycache__' not in p.parts)


def motor_kimligi() -> str:
    return _birlesik_sha256(_py(V8 / 'motor'))


def kod_kimligi() -> str:
    """Kalibrasyon kodu: v8/kalibrasyon ve v8/banka (degerlendirme kutuphanesi)."""
    return _birlesik_sha256(_py(V8 / 'kalibrasyon') + _py(V8 / 'banka'))


def ortam_kimligi() -> str:
    return f"python {sys.version.split()[0]}; numpy {np.__version__}"


def parametre_kimligi(p, har_sha: str) -> str:
    """Parametreler (har_takvimi haric; yol basina kurulur) + HAR sonuc dosyasinin sha256'si (yurutucu.har_paketi)."""
    from dataclasses import fields
    d = {f.name: getattr(p, f.name) for f in fields(p) if f.name != 'har_takvimi'}
    return sha256_metin(kanonik({'parametreler': {k: repr(v) for k, v in sorted(d.items())}, 'har_sonuc': har_sha}))


def beklenen_kimlikler(p, har_sha: str) -> dict:
    return {'kod': kod_kimligi(), 'motor': motor_kimligi(), 'parametre': parametre_kimligi(p, har_sha),
            'ortam': ortam_kimligi()}


def birim_adi(k: dict) -> str:
    """Kimlikten dosya adi (uzantisiz). Anahtarlar: duzey, ayar_no, yol_no?, mimari?, tur, null_no?, cikan?."""
    parca = [f"d{k['duzey']}", f"a{k['ayar_no']:03d}"]
    if k.get('yol_no') is not None:
        parca.append(f"y{k['yol_no']:03d}")
    if k.get('mimari'):
        parca.append(k['mimari'])
    parca.append(k['tur'])
    if k.get('null_no') is not None:
        parca.append(f"p{k['null_no']:03d}")
    if k.get('cikan') is not None:
        parca.append(f"c{k['cikan']:02d}")
    return '_'.join(parca)


def _atomik(yol: Path, veri: bytes):
    gecici = yol.with_name(yol.name + '.gecici')
    with open(gecici, 'wb') as f:
        f.write(veri)
        f.flush()
        os.fsync(f.fileno())
    os.replace(gecici, yol)


def sonuc_yaz(dizin, kimlik: dict, govde, kimlikler: dict, diziler: dict = None) -> Path:
    dizin = Path(dizin)
    dizin.mkdir(parents=True, exist_ok=True)
    ad = birim_adi(kimlik)
    if diziler is not None:
        tampon = io.BytesIO()
        np.savez(tampon, **diziler)
        npz = tampon.getvalue()
        _atomik(dizin / f'{ad}.npz', npz)
        govde = {'npz_sha256': hashlib.sha256(npz).hexdigest(), 'ek': govde}
    zarf = {'birim': kimlik, 'kimlikler': kimlikler, 'govde': govde, 'govde_sha256': sha256_metin(kanonik(govde))}
    yol = dizin / f'{ad}.json'
    _atomik(yol, kanonik(zarf).encode('ascii'))
    return yol


def karantina_dosya(dizin, yol):
    """Tek dosyayi karantinaya tasir (silinmez): _karantina/<ad>.<n>."""
    dizin, yol = Path(dizin), Path(yol)
    k = dizin / KARANTINA
    k.mkdir(exist_ok=True)
    n = 0
    while (k / f'{yol.name}.{n}').exists():
        n += 1
    os.replace(yol, k / f'{yol.name}.{n}')


def _karantina(dizin: Path, ad: str):
    k = dizin / KARANTINA
    k.mkdir(exist_ok=True)
    for uz in ('.json', '.npz'):
        kaynak = dizin / f'{ad}{uz}'
        if kaynak.exists():
            n = 0
            while (k / f'{ad}{uz}.{n}').exists():
                n += 1
            os.replace(kaynak, k / f'{ad}{uz}.{n}')


def sonuc_oku(dizin, kimlik: dict, kimlikler: dict, npz: bool = False):
    """Gecerli ise (govde, diziler|None); yoksa None (dosya yoksa dokunulmaz; bozuksa karantina)."""
    dizin = Path(dizin)
    ad = birim_adi(kimlik)
    yol = dizin / f'{ad}.json'
    if not yol.exists():
        if (dizin / f'{ad}.npz').exists():           # zarfsiz npz (yarim yazim): karantina (Codex T12-4)
            _karantina(dizin, ad)
        return None
    try:
        zarf = json.loads(yol.read_text(encoding='ascii'))
        gecerli = (zarf['birim'] == kimlik and zarf['kimlikler'] == kimlikler
                   and zarf['govde_sha256'] == sha256_metin(kanonik(zarf['govde'])))
        diziler = None
        if gecerli and npz:
            veri = (dizin / f'{ad}.npz').read_bytes()
            gecerli = hashlib.sha256(veri).hexdigest() == zarf['govde']['npz_sha256']
            if gecerli:
                with np.load(io.BytesIO(veri)) as z:
                    diziler = {k: z[k] for k in z.files}
    except (ValueError, KeyError, TypeError, OSError):
        gecerli = False
    if not gecerli:
        _karantina(dizin, ad)
        return None
    govde = zarf['govde']['ek'] if npz else zarf['govde']
    return govde, diziler
