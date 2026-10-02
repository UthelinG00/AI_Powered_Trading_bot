"""Olay gunlugu: yalniz eklemeli, zaman damgali, hash zincirli kayit dizisi. MIMARI Ss5.8 (K1-17, KC-12).

Dosya ya da ag erisimi yoktur; gunluk bellekte tutulur, kalici yazim adaptorun isidir. Her kayit oncekinin
hash'ini tasir; `dogrula()` zinciri bastan hesaplar, sonradan degistirilmis bir kayit zinciri bozar.
Hash girdisi kanonik JSON'dur (sirali anahtar, NaN/Infinity yasak): ayni kayit dizisi her platformda ayni
hash'i uretir.
"""
import hashlib
import json
import math
from dataclasses import dataclass

import numpy as np

KOK_HASH = '0' * 64

KAYIT_TURLERI = frozenset({
    'baslangic',        # kosu basi: nav0 (nakit)
    'funding',          # gercek funding uzlasmasi (nakit)
    'funding_dolgu',    # eksik funding dolgusu (MIMARI Ss2.6)
    'ters_kayit',       # gercek kayit gelince dolgularin tersi
    'karar',            # yapilan gunluk karar: HedefKitap, evren, maske, tanilar
    'kacirilan_karar',  # MIMARI Ss5.8
    'devreden_iptal',   # devreden emrin (bir kisminin) iptali
    'emir_niyeti',      # yeni emir (devreden olur)
    'dolum',            # gerceklesen dolum
    'uzlasma',          # delist 30 gun uzlasmasi (MIMARI Ss1c.5)
    'nav',              # gunluk NAV kapanisi
    'duzeltme',         # canli: borsa kaydiyla uyusmazlik duzeltmesi (MIMARI Ss5.8)
})


class GunlukHatasi(ValueError):
    """Bilinmeyen tur, geri giden damga, JSON'a cevrilemeyen veri ya da bozuk zincir."""


def jsonlastir(x):
    """numpy/tuple/dict degerlerini kanonik JSON'a uygun saf Python'a cevirir. NaN/sonsuz yasak."""
    if isinstance(x, dict):
        return {str(k): jsonlastir(v) for k, v in x.items()}
    if isinstance(x, (list, tuple)):
        return [jsonlastir(v) for v in x]
    if isinstance(x, np.ndarray):
        return [jsonlastir(v) for v in x.tolist()]
    if isinstance(x, (bool, np.bool_)):
        return bool(x)
    if isinstance(x, (int, np.integer)):
        return int(x)
    if isinstance(x, (float, np.floating)):
        f = float(x)
        if math.isnan(f) or math.isinf(f):
            raise GunlukHatasi("gunluge NaN/sonsuz yazilamaz")
        return f
    if x is None or isinstance(x, str):
        return x
    raise GunlukHatasi(f"JSON'a cevrilemeyen tur: {type(x).__name__}")


def _kanonik(obj) -> str:
    return json.dumps(obj, sort_keys=True, separators=(',', ':'), ensure_ascii=True, allow_nan=False)


@dataclass(frozen=True)
class Kayit:
    sira: int
    tur: str
    damga_ms: int
    coin: object          # str | None
    miktar: object        # float | None (dolum/uzlasma: isaretli miktar)
    fiyat: object         # float | None
    karar_ms: object      # int | None (ilgili karar damgasi)
    veri: dict
    onceki_hash: str
    hash: str

    def govde(self) -> dict:
        return {'sira': self.sira, 'tur': self.tur, 'damga_ms': self.damga_ms, 'coin': self.coin,
                'miktar': self.miktar, 'fiyat': self.fiyat, 'karar_ms': self.karar_ms, 'veri': self.veri,
                'onceki_hash': self.onceki_hash}


def _hash(govde: dict) -> str:
    return hashlib.sha256(_kanonik(govde).encode('ascii')).hexdigest()


class OlayGunlugu:
    """Yalniz eklemeli. `ekle` disinda degistirici yontem yoktur."""

    def __init__(self):
        self._kayitlar: list = []

    def __len__(self):
        return len(self._kayitlar)

    @property
    def son_hash(self) -> str:
        return self._kayitlar[-1].hash if self._kayitlar else KOK_HASH

    def ekle(self, tur: str, damga_ms: int, coin=None, miktar=None, fiyat=None, karar_ms=None,
             veri=None) -> Kayit:
        if tur not in KAYIT_TURLERI:
            raise GunlukHatasi(f"bilinmeyen kayit turu: {tur}")
        damga_ms = int(damga_ms)
        if self._kayitlar and damga_ms < self._kayitlar[-1].damga_ms:
            raise GunlukHatasi("gunluk yalniz eklemeli: damga geri gidemez")
        govde = {'sira': len(self._kayitlar), 'tur': tur, 'damga_ms': damga_ms, 'coin': coin,
                 'miktar': jsonlastir(miktar), 'fiyat': jsonlastir(fiyat),
                 'karar_ms': None if karar_ms is None else int(karar_ms),
                 'veri': jsonlastir(veri or {}), 'onceki_hash': self.son_hash}
        kayit = Kayit(hash=_hash(govde), **govde)
        self._kayitlar.append(kayit)
        return kayit

    def kayitlar(self, t_ms=None) -> tuple:
        """Damgasi <= t olan kayitlar (t None ise hepsi), ekleme sirasiyla."""
        if t_ms is None:
            return tuple(self._kayitlar)
        return tuple(k for k in self._kayitlar if k.damga_ms <= t_ms)

    def dogrula(self) -> bool:
        onceki = KOK_HASH
        for i, k in enumerate(self._kayitlar):
            if k.sira != i or k.onceki_hash != onceki or _hash(k.govde()) != k.hash:
                return False
            onceki = k.hash
        return True

    @classmethod
    def kayitlardan(cls, kayitlar) -> 'OlayGunlugu':
        """Kalici kopyadan yeniden yukleme (canli adaptor). Zincir dogrulanmazsa hata."""
        g = cls()
        g._kayitlar = list(kayitlar)
        if not g.dogrula():
            raise GunlukHatasi("yuklenen gunlugun hash zinciri bozuk")
        return g
