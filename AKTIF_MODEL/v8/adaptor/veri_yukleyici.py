"""v8 D (gelistirme) verisi yukleyicisi. Adaptor: dosya okur; motor/ saf kalir (MIMARI Ss5).

Kaynak (MIMARI Ss2.1): data.binance.vision aylik 1h klines ve fundingRate zip'leri, `v8_veri_20260924_01/ham/`.
"Ilk indirmenin hash'i baglayicidir": her zip, MANIFEST.jsonl'deki sha256 ile dogrulanir; eslesmeyen, eksik ya da
manifestte olmayan dosya hatadir. Temizlik kurallari veri paketinin `paket/isle.py`'si ile aynidir:
basligi algila; open_time/calc_time > 1e14 ise mikrosaniye kabul edip ms'ye cevir; donem [2023-07-01, 2026-07-01);
sirala; tekrar eden zaman damgasinda ilkini tut; sayisal olmayan satiri at. Ek olarak (motorun sozlesmesi):
- Kline acilis zamani saat izgarasinda olmali (degilse hata; isle.py raporunda boyle satir yok).
- Funding damgasi en yakin tam saate yuvarlanir (MIMARI Ss2.1, K1-20.8); yuvarlama sonrasi cakisan kayitlarda ilki
  tutulur ve sayilir. Orani sayisal olmayan kayit atilir. `funding_interval_hours` kaydin kendi araligi olarak
  FundingSerisi.aralik_saat'e verilir (funding.kapsanan_aralik_saat; Slice 2 K2 siniri).
- Kapanis <= 0 olan bar hata sayilir (log getiri tanimsiz).
Gelistirme evreni (aday listesi, MIMARI Ss2.3) GELISTIRME_EVRENI.json'dan okunur; hash'i sabittir. Ayni klasordeki
diger dosyalar okunmaz ve listelenmez.

Veri kimligi: kullanilan her zip icin "yol sha256" satirlarinin sirali birlesiminin sha256'si (dondurma, CARRY Ss3.7).
Ag erisimi yoktur.
"""
import hashlib
import io
import json
import zipfile
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd

from motor.gorunum import SAAT_MS, FundingSerisi, SaatlikSeri, TamVeri, funding_serisi, saatlik_seri

GELISTIRME_SHA256 = "343dead42d44c04b86f4e7ce6b08da477b98afa63e626243865fd6cf2d6b815c"
VERI_KLASORU = Path("AKTIF_MODEL") / "ciktilar" / "v8_veri_20260924_01"
EVREN_YOLU = Path("AKTIF_MODEL") / "ciktilar" / "v8_banka_20260924_01" / "GELISTIRME_EVRENI.json"
BAS_MS = int(datetime(2023, 7, 1, tzinfo=timezone.utc).timestamp() * 1000)
BIT_MS = int(datetime(2026, 7, 1, tzinfo=timezone.utc).timestamp() * 1000)     # haric
KLINES_KOLONLAR = ["open_time", "open", "high", "low", "close", "volume", "close_time", "quote_volume", "count",
                   "taker_buy_volume", "taker_buy_quote_volume", "ignore"]
FUNDING_KOLONLAR = ["calc_time", "funding_interval_hours", "last_funding_rate"]


class VeriYuklemeHatasi(ValueError):
    """Hash uyusmazligi, eksik/fazla dosya, beklenmeyen bicim ya da motor sozlesmesine aykiri veri."""


def depo_koku(baslangic: Path = None) -> Path:
    """Bu dosyanin bulundugu deponun koku (AKTIF_MODEL'in ustu)."""
    p = (baslangic or Path(__file__)).resolve()
    for ust in [p] + list(p.parents):
        if (ust / "AKTIF_MODEL").is_dir():
            return ust
    raise VeriYuklemeHatasi("depo koku bulunamadi")


def veri_koku_bul(kok: Path = None) -> Path:
    """Ham verinin bulundugu v8_veri klasoru. Worktree'de ham/ yoksa ana depo (.claude/worktrees/<ad> ustu) denenir."""
    kok = kok or depo_koku()
    adaylar = [kok / VERI_KLASORU]
    parcalar = kok.parts
    if ".claude" in parcalar:
        ana = Path(*parcalar[:parcalar.index(".claude")])
        adaylar.append(ana / VERI_KLASORU)
    for a in adaylar:
        if (a / "ham").is_dir() and (a / "MANIFEST.jsonl").is_file():
            return a
    raise VeriYuklemeHatasi(f"ham veri bulunamadi: {[str(a) for a in adaylar]}")


def _sha256_dosya(yol: Path) -> str:
    return hashlib.sha256(yol.read_bytes()).hexdigest()


def gelistirme_evreni(kok: Path = None) -> tuple:
    """GELISTIRME_EVRENI.json'daki 'gelistirme' listesi (hash dogrulamali)."""
    yol = (kok or depo_koku()) / EVREN_YOLU
    b = yol.read_bytes()
    if hashlib.sha256(b).hexdigest() != GELISTIRME_SHA256:
        raise VeriYuklemeHatasi("GELISTIRME_EVRENI.json hash'i uyusmuyor")
    return tuple(json.loads(b)["gelistirme"])


def manifest_tamam(veri_kok: Path) -> dict:
    """yol -> sha256 (durum TAMAM). Ayni yol birden cok kez yazilmissa hash'leri ayni olmali."""
    sonuc = {}
    with (veri_kok / "MANIFEST.jsonl").open(encoding="utf-8") as f:
        for satir in f:
            satir = satir.strip()
            if not satir:
                continue
            r = json.loads(satir)
            if r.get("durum") != "TAMAM":
                continue
            onceki = sonuc.get(r["yol"])
            if onceki is not None and onceki != r["sha256"]:
                raise VeriYuklemeHatasi(f"manifestte ayni yol icin farkli hash: {r['yol']}")
            sonuc[r["yol"]] = r["sha256"]
    return sonuc


def _zip_csv(yol: Path, kolonlar: list) -> pd.DataFrame:
    with zipfile.ZipFile(yol) as zf:
        isimler = [n for n in zf.namelist() if n.endswith(".csv")]
        if len(isimler) != 1:
            raise VeriYuklemeHatasi(f"zip icinde tek csv beklenirdi: {yol.name} {zf.namelist()}")
        ham = zf.read(isimler[0])
    baslik_var = ham.split(b"\n", 1)[0].split(b",")[0].strip() == kolonlar[0].encode()
    df = pd.read_csv(io.BytesIO(ham), header=0 if baslik_var else None, names=None if baslik_var else kolonlar)
    if list(df.columns) != kolonlar:
        raise VeriYuklemeHatasi(f"beklenmeyen kolonlar {yol.name}: {list(df.columns)}")
    return df


def _zaman_temizle(df: pd.DataFrame, kol: str, rapor: dict) -> pd.DataFrame:
    df = df.copy()
    df[kol] = pd.to_numeric(df[kol], errors="coerce")
    rapor["gecersiz_zaman"] = int(df[kol].isna().sum())
    df = df.dropna(subset=[kol])
    mikro = df[kol] > 1e14
    rapor["mikrosaniye"] = int(mikro.sum())
    df.loc[mikro, kol] = (df.loc[mikro, kol] / 1000).round()
    df[kol] = df[kol].astype("int64")
    df = df.sort_values(kol, kind="mergesort")
    donem_disi = ~df[kol].between(BAS_MS, BIT_MS - 1)
    rapor["donem_disi"] = int(donem_disi.sum())
    df = df.loc[~donem_disi]
    tekrar = df.duplicated(kol, keep="first")
    rapor["tekrar"] = int(tekrar.sum())
    return df.loc[~tekrar].reset_index(drop=True)


@dataclass
class CoinRaporu:
    klines_dosya: int = 0
    funding_dosya: int = 0
    klines: dict = field(default_factory=dict)
    funding: dict = field(default_factory=dict)


def _dosyalar(veri_kok: Path, tur: str, sym: str) -> list:
    klasor = veri_kok / "ham" / tur / sym
    return sorted(klasor.glob("*.zip")) if klasor.is_dir() else []


def coin_yukle(veri_kok: Path, sym: str, manifest: dict, dogrula: bool = True) -> tuple:
    """(SaatlikSeri | None, FundingSerisi | None, CoinRaporu, [(yol, sha256), ...])."""
    rapor = CoinRaporu()
    kullanilan = []

    def _dogrulanmis(yol: Path) -> None:
        goreli = yol.relative_to(veri_kok).as_posix()
        beklenen = manifest.get(goreli)
        if beklenen is None:
            raise VeriYuklemeHatasi(f"manifestte TAMAM kaydi olmayan dosya: {goreli}")
        if dogrula and _sha256_dosya(yol) != beklenen:
            raise VeriYuklemeHatasi(f"sha256 uyusmuyor: {goreli}")
        kullanilan.append((goreli, beklenen))

    # Klines.
    kd = _dosyalar(veri_kok, "klines", sym)
    rapor.klines_dosya = len(kd)
    seri = None
    if kd:
        parca = []
        for y in kd:
            _dogrulanmis(y)
            parca.append(_zip_csv(y, KLINES_KOLONLAR))
        df = _zaman_temizle(pd.concat(parca, ignore_index=True), "open_time", rapor.klines)
        for k in ("open", "high", "low", "close", "quote_volume"):
            df[k] = pd.to_numeric(df[k], errors="coerce")
        nan = df[["open", "high", "low", "close", "quote_volume"]].isna().any(axis=1)
        rapor.klines["sayisal_gecersiz"] = int(nan.sum())
        df = df.loc[~nan].reset_index(drop=True)
        if (df["open_time"] % SAAT_MS != 0).any():
            raise VeriYuklemeHatasi(f"{sym}: saat izgarasinda olmayan kline acilisi")
        if (df["close"] <= 0).any() or (df["open"] <= 0).any():
            raise VeriYuklemeHatasi(f"{sym}: sifir ya da negatif fiyat")
        rapor.klines["gecersiz_ohlc"] = int(((df["high"] < df[["open", "close"]].max(axis=1))
                                             | (df["low"] > df[["open", "close"]].min(axis=1))).sum())
        rapor.klines["satir"] = len(df)
        seri = saatlik_seri(df["open_time"].to_numpy(np.int64), df["open"].to_numpy(float), df["high"].to_numpy(float),
                            df["low"].to_numpy(float), df["close"].to_numpy(float),
                            df["quote_volume"].to_numpy(float))

    # Funding.
    fd = _dosyalar(veri_kok, "fundingRate", sym)
    rapor.funding_dosya = len(fd)
    fon = None
    if fd:
        parca = []
        for y in fd:
            _dogrulanmis(y)
            parca.append(_zip_csv(y, FUNDING_KOLONLAR))
        df = _zaman_temizle(pd.concat(parca, ignore_index=True), "calc_time", rapor.funding)
        df["last_funding_rate"] = pd.to_numeric(df["last_funding_rate"], errors="coerce")
        df["funding_interval_hours"] = pd.to_numeric(df["funding_interval_hours"], errors="coerce")
        nan = df["last_funding_rate"].isna()
        rapor.funding["oran_gecersiz"] = int(nan.sum())
        df = df.loc[~nan].reset_index(drop=True)
        yuv = ((df["calc_time"] + SAAT_MS // 2) // SAAT_MS) * SAAT_MS
        cakisma = yuv.duplicated(keep="first")
        rapor.funding["yuvarlama_cakismasi"] = int(cakisma.sum())
        df = df.loc[~cakisma].reset_index(drop=True)
        rapor.funding["aralik_bilinmiyor"] = int(df["funding_interval_hours"].isna().sum())
        rapor.funding["satir"] = len(df)
        fon = funding_serisi(df["calc_time"].to_numpy(np.int64), df["last_funding_rate"].to_numpy(float),
                             df["funding_interval_hours"].to_numpy(float))
    return seri, fon, rapor, kullanilan


@dataclass
class YuklemeRaporu:
    veri_kok: str
    veri_kimligi: str
    dosya_sayisi: int
    semboller: tuple
    coin: dict                   # sym -> CoinRaporu.__dict__

    def json(self) -> dict:
        return {'veri_kok': self.veri_kok, 'veri_kimligi': self.veri_kimligi, 'dosya_sayisi': self.dosya_sayisi,
                'semboller': list(self.semboller), 'coin': self.coin}


def tam_veri_yukle(veri_kok: Path = None, semboller=None, dogrula: bool = True, kok: Path = None,
                   evren: tuple = None) -> tuple:
    """(TamVeri, YuklemeRaporu). semboller verilmezse gelistirme evreninin tamami; adaylar her durumda gelistirme
    evreni ile verilen sembollerin kesisimi (MIMARI Ss2.3 aday listesi). evren: yalniz testler icin (verilmezse
    hash dogrulamali GELISTIRME_EVRENI.json)."""
    veri_kok = Path(veri_kok) if veri_kok is not None else veri_koku_bul(kok)
    evren = tuple(evren) if evren is not None else gelistirme_evreni(kok)
    istenen = tuple(evren) if semboller is None else tuple(semboller)
    disarida = sorted(set(istenen) - set(evren))
    if disarida:
        raise VeriYuklemeHatasi(f"gelistirme evreninde olmayan sembol: {disarida}")
    manifest = manifest_tamam(veri_kok)
    barlar, funding, raporlar, kullanilan = {}, {}, {}, []
    for sym in sorted(istenen):
        seri, fon, rapor, dosyalar = coin_yukle(veri_kok, sym, manifest, dogrula)
        if seri is not None and len(seri):
            barlar[sym] = seri
        if fon is not None:
            funding[sym] = fon
        raporlar[sym] = rapor.__dict__
        kullanilan.extend(dosyalar)
    ozet = "\n".join(f"{y} {h}" for y, h in sorted(kullanilan)).encode("utf-8")
    veri = TamVeri(barlar=barlar, funding=funding, adaylar=tuple(sorted(istenen)))
    return veri, YuklemeRaporu(veri_kok=str(veri_kok), veri_kimligi=hashlib.sha256(ozet).hexdigest(),
                               dosya_sayisi=len(kullanilan), semboller=tuple(sorted(istenen)), coin=raporlar)
