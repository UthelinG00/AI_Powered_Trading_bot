"""age v1 (age-encryption.org/v1) X25519 alıcısıyla şifreleme ve çözme (BANKA §2.4 kör hüküm; BK-2).

Yalnız `cryptography` kullanır (X25519, HKDF-SHA256, HMAC-SHA256, ChaCha20-Poly1305). Biçim, resmi `age` aracının
dosyasıyla birebir uyumlu olacak şekilde yazılmıştır; kullanıcı `age -d -i anahtar.txt dosya.age` ile çözebilir.
Uyum dondurmadan önce kullanıcının age-keygen anahtarıyla gidiş-dönüş testinde doğrulanır (ILERLEME_BANKA 6.10).

Biçim özeti:
  başlık:  "age-encryption.org/v1\\n"
           "-> X25519 " b64(E) "\\n" b64(gövde) "\\n"          (gövde 64 sütunda sarılır, son satır < 64)
           "--- " b64(HMAC) "\\n"
    E = X25519(e, taban), paylaşılan = X25519(e, alıcı), anahtar = HKDF(paylaşılan, tuz = E || alıcı,
    bilgi "age-encryption.org/v1/X25519"), gövde = ChaCha20Poly1305(anahtar, sıfır nonce, dosya_anahtarı[16]).
    HMAC anahtarı = HKDF(dosya_anahtarı, tuz boş, bilgi "header"); HMAC başlığın "---" dahil ilk kısmı üzerinde.
  yük:     nonce[16] + STREAM: yük_anahtarı = HKDF(dosya_anahtarı, tuz nonce, bilgi "payload"); 64 KiB parçalar,
           parça nonce'u = 11 bayt büyük uçlu sayaç || son bayrağı (0x01 son parça). Boş düz metin tek boş son parçadır.
  b64: standart alfabe, dolgusuz. Anahtar metinleri Bech32 (BIP-173): alıcı "age1…", kimlik "AGE-SECRET-KEY-1…".
"""
import base64
import hmac
import hashlib
import os

from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric.x25519 import X25519PrivateKey, X25519PublicKey
from cryptography.hazmat.primitives.ciphers.aead import ChaCha20Poly1305
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.primitives.serialization import Encoding, NoEncryption, PrivateFormat, PublicFormat

SURUM = b'age-encryption.org/v1'
X25519_BILGI = b'age-encryption.org/v1/X25519'
PARCA = 64 * 1024


class AgeHatasi(ValueError):
    pass


# ---- Bech32 (BIP-173) ---------------------------------------------------------------------------------------------

_ALFABE = 'qpzry9x8gf2tvdw0s3jn54khce6mua7l'


def _polymod(degerler) -> int:
    gen = (0x3b6a57b2, 0x26508e6d, 0x1ea119fa, 0x3d4233dd, 0x2a1462b3)
    chk = 1
    for v in degerler:
        b = chk >> 25
        chk = ((chk & 0x1ffffff) << 5) ^ v
        for i in range(5):
            chk ^= gen[i] if ((b >> i) & 1) else 0
    return chk


def _hrp_genislet(hrp: str) -> list:
    return [ord(x) >> 5 for x in hrp] + [0] + [ord(x) & 31 for x in hrp]


def _bitleri_cevir(veri, kaynak: int, hedef: int, dolgu: bool) -> list:
    acc = bits = 0
    out = []
    maks = (1 << hedef) - 1
    for v in veri:
        if v < 0 or v >> kaynak:
            raise AgeHatasi("bech32: gecersiz deger")
        acc = (acc << kaynak) | v
        bits += kaynak
        while bits >= hedef:
            bits -= hedef
            out.append((acc >> bits) & maks)
    if dolgu:
        if bits:
            out.append((acc << (hedef - bits)) & maks)
    elif bits >= kaynak or ((acc << (hedef - bits)) & maks):
        raise AgeHatasi("bech32: gecersiz dolgu")
    return out


def bech32_kodla(hrp: str, veri: bytes) -> str:
    d = _bitleri_cevir(veri, 8, 5, True)
    pm = _polymod(_hrp_genislet(hrp) + d + [0] * 6) ^ 1
    chk = [(pm >> 5 * (5 - i)) & 31 for i in range(6)]
    return hrp + '1' + ''.join(_ALFABE[x] for x in d + chk)


def bech32_coz(metin: str) -> tuple:
    if metin.lower() != metin and metin.upper() != metin:
        raise AgeHatasi("bech32: karisik buyuk/kucuk harf")
    s = metin.lower()
    ayrac = s.rfind('1')
    if ayrac < 1 or ayrac + 7 > len(s):
        raise AgeHatasi("bech32: bicim")
    hrp, veri = s[:ayrac], s[ayrac + 1:]
    try:
        d = [_ALFABE.index(x) for x in veri]
    except ValueError:
        raise AgeHatasi("bech32: gecersiz karakter") from None
    if _polymod(_hrp_genislet(hrp) + d) != 1:
        raise AgeHatasi("bech32: saglama toplami")
    return hrp, bytes(_bitleri_cevir(d[:-6], 5, 8, False))


# ---- anahtarlar -----------------------------------------------------------------------------------------------------

def anahtar_uret() -> tuple:
    """(kimlik 'AGE-SECRET-KEY-1…', alıcı 'age1…'). Yalnız testler için; gerçek anahtarı kullanıcı age-keygen ile üretir."""
    k = X25519PrivateKey.generate()
    gizli = k.private_bytes(Encoding.Raw, PrivateFormat.Raw, NoEncryption())
    return kimlik_metni(gizli), alici_metni(k.public_key().public_bytes(Encoding.Raw, PublicFormat.Raw))


def alici_metni(acik: bytes) -> str:
    return bech32_kodla('age', acik)


def kimlik_metni(gizli: bytes) -> str:
    return bech32_kodla('age-secret-key-', gizli).upper()


def alici_coz(metin: str) -> bytes:
    hrp, acik = bech32_coz(metin.strip())
    if hrp != 'age' or len(acik) != 32:
        raise AgeHatasi("gecersiz alici")
    return acik


def kimlik_coz(metin: str) -> bytes:
    satir = [x.strip() for x in metin.strip().splitlines() if x.strip() and not x.strip().startswith('#')]
    if len(satir) != 1:
        raise AgeHatasi("kimlik dosyasinda tek anahtar satiri olmali")
    hrp, gizli = bech32_coz(satir[0])
    if hrp != 'age-secret-key-' or len(gizli) != 32:
        raise AgeHatasi("gecersiz kimlik")
    return gizli


# ---- yardımcılar ----------------------------------------------------------------------------------------------------

def _b64(b: bytes) -> bytes:
    return base64.b64encode(b).rstrip(b'=')


def _b64_coz(s: bytes) -> bytes:
    """Kanonik, dolgusuz standart Base64 (Codex T16): cozulen deger yeniden kodlaninca birebir ayni olmali (kullanilmayan
    son bitler sifir)."""
    if b'=' in s or b'\r' in s:
        raise AgeHatasi("b64: dolgu ya da CR")
    try:
        b = base64.b64decode(s + b'=' * (-len(s) % 4), validate=True)
    except ValueError:
        raise AgeHatasi("b64: gecersiz") from None
    if _b64(b) != s:
        raise AgeHatasi("b64: kanonik degil")
    return b


def _hkdf(ikm: bytes, tuz: bytes, bilgi: bytes) -> bytes:
    return HKDF(algorithm=hashes.SHA256(), length=32, salt=tuz or None, info=bilgi).derive(ikm)


def _sar(b: bytes) -> bytes:
    """Gövdeyi 64 sütunda sarar; son satır 64'ten kısa (gerekirse boş) olur."""
    s = _b64(b)
    satirlar = [s[i:i + 64] for i in range(0, len(s), 64)]
    if not satirlar or len(satirlar[-1]) == 64:
        satirlar.append(b'')
    return b'\n'.join(satirlar)


# ---- şifreleme / çözme ----------------------------------------------------------------------------------------------

def sifrele(alici: str, duz: bytes) -> bytes:
    alici_acik = alici_coz(alici)
    dosya_anahtari = os.urandom(16)
    e = X25519PrivateKey.generate()
    E = e.public_key().public_bytes(Encoding.Raw, PublicFormat.Raw)
    paylasilan = e.exchange(X25519PublicKey.from_public_bytes(alici_acik))
    if paylasilan == bytes(32):
        raise AgeHatasi("X25519: sifir paylasilan anahtar")
    sarma = _hkdf(paylasilan, E + alici_acik, X25519_BILGI)
    govde = ChaCha20Poly1305(sarma).encrypt(bytes(12), dosya_anahtari, None)
    baslik = SURUM + b'\n-> X25519 ' + _b64(E) + b'\n' + _sar(govde) + b'\n---'
    mac = hmac.new(_hkdf(dosya_anahtari, b'', b'header'), baslik, hashlib.sha256).digest()
    nonce = os.urandom(16)
    yuk_anahtari = ChaCha20Poly1305(_hkdf(dosya_anahtari, nonce, b'payload'))
    parcalar = [duz[i:i + PARCA] for i in range(0, len(duz), PARCA)] or [b'']
    out = [baslik, b' ', _b64(mac), b'\n', nonce]
    for i, p in enumerate(parcalar):
        n = i.to_bytes(11, 'big') + (b'\x01' if i == len(parcalar) - 1 else b'\x00')
        out.append(yuk_anahtari.encrypt(n, p, None))
    return b''.join(out)


def coz(kimlik: str, veri: bytes) -> bytes:
    gizli = X25519PrivateKey.from_private_bytes(kimlik_coz(kimlik))
    acik = gizli.public_key().public_bytes(Encoding.Raw, PublicFormat.Raw)
    satirlar = []
    i = 0
    while True:
        j = veri.find(b'\n', i)
        if j < 0:
            raise AgeHatasi("baslik bitmedi")
        satir = veri[i:j]
        satirlar.append(satir)
        i = j + 1
        if satir.startswith(b'---'):
            break
    if satirlar[0] != SURUM:
        raise AgeHatasi("surum satiri")
    dosya_anahtari = None
    k = 1
    while not satirlar[k].startswith(b'---'):
        arg = satirlar[k].split(b' ')
        if arg[0] != b'->':
            raise AgeHatasi("stanza bicimi")
        govde = b''
        k += 1
        while True:
            if k >= len(satirlar) or len(satirlar[k]) > 64:
                raise AgeHatasi("stanza govdesi: satir 64 karakteri asiyor ya da eksik")
            govde += satirlar[k]
            son = len(satirlar[k]) < 64
            k += 1
            if son:
                break
        if arg[1:2] == [b'X25519']:
            if len(arg) != 3:
                raise AgeHatasi("X25519 stanzasi: arguman sayisi")
            E = _b64_coz(arg[2])
            sarili = _b64_coz(govde)
            if len(E) != 32 or len(sarili) != 32:
                raise AgeHatasi("X25519 stanzasi: uzunluk")
            if dosya_anahtari is None:
                paylasilan = gizli.exchange(X25519PublicKey.from_public_bytes(E))
                try:
                    dosya_anahtari = ChaCha20Poly1305(_hkdf(paylasilan, E + acik, X25519_BILGI)).decrypt(
                        bytes(12), sarili, None)
                except Exception:
                    dosya_anahtari = None
                if dosya_anahtari is not None and len(dosya_anahtari) != 16:
                    raise AgeHatasi("dosya anahtari 16 bayt degil")
    if dosya_anahtari is None:
        raise AgeHatasi("bu kimlige ait alici yok")
    son_satir = satirlar[k]
    if not son_satir.startswith(b'--- ') or len(son_satir) != 4 + 43:
        raise AgeHatasi("MAC satiri")
    baslik = b'\n'.join(satirlar[:k]) + b'\n---'
    beklenen = hmac.new(_hkdf(dosya_anahtari, b'', b'header'), baslik, hashlib.sha256).digest()
    if not hmac.compare_digest(beklenen, _b64_coz(son_satir[4:])):
        raise AgeHatasi("baslik MAC'i tutmuyor")
    nonce, sifreli = veri[i:i + 16], veri[i + 16:]
    if len(nonce) != 16:
        raise AgeHatasi("nonce eksik")
    yuk = ChaCha20Poly1305(_hkdf(dosya_anahtari, nonce, b'payload'))
    boy = PARCA + 16
    parcalar = [sifreli[x:x + boy] for x in range(0, len(sifreli), boy)]
    if not parcalar:
        raise AgeHatasi("yuk bos")
    out = []
    for n_, p in enumerate(parcalar):
        son = n_ == len(parcalar) - 1
        duz = yuk.decrypt(n_.to_bytes(11, 'big') + (b'\x01' if son else b'\x00'), p, None)
        if son and not duz and n_ > 0:
            raise AgeHatasi("bos son parca")
        out.append(duz)
    return b''.join(out)
