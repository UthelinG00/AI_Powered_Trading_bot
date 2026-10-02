"""Kalibrasyon kanıt dosyalarının ortak kimlik bloğu (Codex T17-a).

Duman (duman_kanit.py), bitiş (bitis.py), toplama (topla.py) ve eşdeğerlik (esdegerlik_502e.py) kanıtları aynı 'kanit'
bloğunu taşır:
  betik_sha256         kanıtı üreten betiğin sha256'sı
  kod_dondurma_sha256  kanıt üretilirken okunan KOD_DONDURMA.json'un sha256'sı
  har_sonuc_sha256     kanıt üretilirken okunan HAR sonuç dosyasının sha256'sı (kalibrasyon.yurutucu.har_paketi)
  kimlikler            kanıtın dayandığı birim dosyalarının dört kimliği (kod, motor, parametre, ortam); tek değilse None
  kaynak               kanıtın girdi dosyalarının sha256'ları (betiğe özgü)
kilit.onkosullar bloğu KOD_DONDURMA.json ile (dosyanın kendi sha256'sı, dört kimlik, HAR) ve eşdeğerlikte güncel girdilerle
karşılaştırır. Yalnız ad, sayı ve hash yazılır; sonuç değeri yazılmaz."""
import hashlib
import json
from pathlib import Path

BURASI = Path(__file__).resolve().parent
DORT = ('kod', 'motor', 'parametre', 'ortam')


def sha_bayt(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def sha_dosya(yol) -> str:
    return sha_bayt(Path(yol).read_bytes())


def dosya_hashleri(klasor, desen: str = 'd2_*.json') -> dict:
    return {p.name: sha_dosya(p) for p in sorted(Path(klasor).glob(desen))}


def birlesik(hashler: dict) -> str:
    """Ad -> sha256 sözlüğünün sıradan bağımsız tek özeti."""
    return sha_bayt(json.dumps(sorted(hashler.items()), separators=(',', ':')).encode('ascii'))


def zarf_kimlikleri(yollar) -> list:
    """Birim zarflarındaki farklı dört-kimlik kümeleri (kanonik sırayla)."""
    kume = {json.dumps(json.loads(Path(y).read_text(encoding='ascii'))['kimlikler'], sort_keys=True) for y in yollar}
    return [json.loads(k) for k in sorted(kume)]


def tek_kimlik(kumeler: list):
    return {k: kumeler[0].get(k) for k in DORT} if len(kumeler) == 1 else None


def klasor_ozeti(d, is_listesi: str = 'IS_LISTESI.json', ek_liste: str = 'IS_LISTESI_EK.jsonl',
                 desen: str = 'd2_*.json') -> dict:
    """Kosu klasorunun girdi ozeti (Codex T18: bitis ve toplama ayni tanimi kullanir): is listesinin ve ek listenin
    sha256'si (yoksa None), birim dosyalarinin sayisi ve birlesik ozeti."""
    d = Path(d)
    ek = d / ek_liste
    h = dosya_hashleri(d, desen)
    return {'is_listesi_sha256': sha_dosya(d / is_listesi), 'ek_liste_sha256': sha_dosya(ek) if ek.exists() else None,
            'birim_dosyalari': {'dosya': len(h), 'birlesik_sha256': birlesik(h)}}


def blok(betik, kimlikler, har_sha: str, kaynak: dict, burasi: Path = BURASI) -> dict:
    return {'betik_sha256': sha_dosya(betik), 'kod_dondurma_sha256': sha_dosya(Path(burasi) / 'KOD_DONDURMA.json'),
            'har_sonuc_sha256': har_sha, 'kimlikler': None if kimlikler is None else {k: kimlikler[k] for k in DORT},
            'kaynak': kaynak}
