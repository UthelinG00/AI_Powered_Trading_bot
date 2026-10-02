"""Anonim coin kimliği (BANKA §8.1 K1-16; §3.5.2 Y3 ikincil permütasyon tohumu).

Coin düzeyindeki bütün tablolar C001… kimliği kullanır. Sıra, yerel ve gizli bir anahtarla HMAC-SHA256(anahtar, sembol)
değerine göredir (küçükten büyüğe). BTC ve ETH adlarıyla kalır (raporda yalnız onların adı geçer). Anahtar ve eşleme
dosyası yerel kalır, depoya girmez; yalnız sha256'ları raporlanır. Anahtar bankadan önce bir kez üretilir; null
tohumları bu kimliğe bağlı olduğundan koşu sırasında değişmez.
"""
import hashlib
import hmac
import json
import os
from pathlib import Path

ADLI = ('BTCUSDT', 'ETHUSDT')


def anahtar_uret(yol) -> str:
    """32 rastgele bayt; dosya zaten varsa üzerine yazılmaz. Doner: anahtarin sha256'si."""
    yol = Path(yol)
    if yol.exists():
        raise FileExistsError("anonim kimlik anahtari zaten var")
    a = os.urandom(32)
    yol.write_bytes(a)
    return hashlib.sha256(a).hexdigest()


def kimlikler(anahtar: bytes, semboller) -> dict:
    """{sembol: kimlik}. BTC/ETH kendi adı; ötekiler HMAC sırasıyla C001, C002, ..."""
    if len(anahtar) < 32:
        raise ValueError("anahtar en az 32 bayt olmali")
    digerleri = sorted((s for s in set(semboller) if s not in ADLI),
                       key=lambda s: hmac.new(anahtar, s.encode('ascii'), hashlib.sha256).hexdigest())
    out = {s: f"C{i:03d}" for i, s in enumerate(digerleri, start=1)}
    out.update({s: s for s in ADLI if s in set(semboller)})
    return out


def esleme_yaz(yol, esleme: dict) -> str:
    """Eşleme dosyası (yerel). Doner: sha256."""
    b = json.dumps(esleme, sort_keys=True, ensure_ascii=True, separators=(',', ':')).encode('ascii')
    Path(yol).write_bytes(b)
    return hashlib.sha256(b).hexdigest()
