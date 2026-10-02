"""Kanonik tohum turetimi (BANKA_ONKAYIT_TASLAK Ss3.7 "Tohum", 3. revizyon, Codex T10-3).

hash(x1, ..., xk) = SHA-256 ozetinin ilk 8 bayti, buyuk uclu tamsayi; ozetlenen bayt dizisi
json.dumps([x1, ..., xk], separators=(',', ':'), ensure_ascii=True)'nin UTF-8 hali; x'ler tamsayi ya da ASCII dize.
Her alt tohum numpy.random.Generator(PCG64(tohum)) baslatir."""
import hashlib
import json

import numpy as np

TOHUM_KAL = int(hashlib.sha256(b'v8_asama4b_kalibrasyon').hexdigest()[:16], 16) % 2 ** 32


def kanonik_json(x) -> str:
    return json.dumps(x, separators=(',', ':'), ensure_ascii=True)


def hash_tohum(*parcalar) -> int:
    for x in parcalar:
        if isinstance(x, bool) or not isinstance(x, (int, str)):
            raise TypeError(f"tohum parcasi tamsayi ya da dize olmali: {x!r}")
        if isinstance(x, str) and not x.isascii():
            raise ValueError(f"tohum dizesi ASCII olmali: {x!r}")
    ozet = hashlib.sha256(kanonik_json(list(parcalar)).encode('utf-8')).digest()
    return int.from_bytes(ozet[:8], 'big')


def uretec(*parcalar) -> np.random.Generator:
    return np.random.Generator(np.random.PCG64(hash_tohum(*parcalar)))
