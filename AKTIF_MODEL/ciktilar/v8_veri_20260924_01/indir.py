"""v8 geliştirme verisi indirici (kullanıcı onayı 2026-09-24).

Yalnız GELISTIRME_EVRENI.json'daki 122 coin ve 2023-07 → 2026-06 ayları için
data.binance.vision aylık 1h klines ve fundingRate dosyalarını indirir.
- Banka dosyası okunmaz. Geliştirme evreninin hash'i önceden sabittir.
- Her zip resmi .CHECKSUM ile doğrulanır; doğrulanmayan dosya "HATA" olarak kaydedilir.
- MANIFEST.jsonl yalnız sona ekleme yapılarak yazılır. Doğrulanmış dosyalar yeniden indirilmez (devam edilebilir).
Anahtar yok, mainnet API yok; yalnız herkese açık arşiv.

Kullanım: python -X utf8 indir.py [--is-parcacigi 16]
"""
import argparse
import hashlib
import json
import threading
import time
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from pathlib import Path

BURASI = Path(__file__).resolve().parent
BANKA_KLASORU = BURASI.parent / "v8_banka_20260924_01"
GELISTIRME_SHA256 = "343dead42d44c04b86f4e7ce6b08da477b98afa63e626243865fd6cf2d6b815c"
HAM_SHA256 = "5ad6f8958375384738b7bd5df70eb8b019ffc26692483b8264e4ceb3fdf91bc2"
ILK_AY, SON_AY = "2023-07", "2026-06"
KOK = "https://data.binance.vision/data/futures/um/monthly"
KILIT = threading.Lock()


def sha256_bayt(veri):
    return hashlib.sha256(veri).hexdigest()


def aylar(ilk, son):
    y, m = map(int, ilk.split("-"))
    while f"{y:04d}-{m:02d}" <= son:
        yield f"{y:04d}-{m:02d}"
        m += 1
        if m == 13:
            y, m = y + 1, 1


def plan_kur():
    gel_yol = BANKA_KLASORU / "GELISTIRME_EVRENI.json"
    ham_yol = BANKA_KLASORU / "um_1h_aylar_ham.json"
    if sha256_bayt(gel_yol.read_bytes()) != GELISTIRME_SHA256:
        raise SystemExit("DURDU: GELISTIRME_EVRENI hash uyuşmuyor")
    if sha256_bayt(ham_yol.read_bytes()) != HAM_SHA256:
        raise SystemExit("DURDU: ham ay listesi hash uyuşmuyor")
    gelistirme = json.loads(gel_yol.read_text(encoding="utf-8"))["gelistirme"]
    ham = json.loads(ham_yol.read_text(encoding="utf-8"))
    isler = []
    for sym in gelistirme:
        ilk, son, _ = ham[sym]
        for ay in aylar(max(ilk, ILK_AY), min(son, SON_AY)):
            isler.append(("klines", sym, ay, f"{KOK}/klines/{sym}/1h/{sym}-1h-{ay}.zip"))
            isler.append(("fundingRate", sym, ay, f"{KOK}/fundingRate/{sym}/{sym}-fundingRate-{ay}.zip"))
    return isler


def getir(url, deneme=4):
    for i in range(deneme):
        try:
            with urllib.request.urlopen(url, timeout=40) as r:
                return r.read()
        except urllib.error.HTTPError as e:
            if e.code == 404:
                return None
            hata = e
        except Exception as e:  # ağ hatası: bekle, yeniden dene
            hata = e
        time.sleep(2 * (i + 1))
    raise hata


def dogrulanmis_kayitlar(manifest):
    tamam = set()
    if manifest.exists():
        for satir in manifest.read_text(encoding="utf-8").splitlines():
            try:
                k = json.loads(satir)
            except ValueError:
                continue
            if k.get("durum") == "TAMAM":
                tamam.add(k["yol"])
    return tamam


def indir_bir(is_, manifest, tamam):
    tur, sym, ay, url = is_
    yol = Path("ham") / tur / sym / url.rsplit("/", 1)[1]
    if yol.as_posix() in tamam and (BURASI / yol).exists():
        return "ATLA"
    kayit = {"tur": tur, "sym": sym, "ay": ay, "url": url, "yol": yol.as_posix()}
    try:
        veri = getir(url)
        if veri is None:
            kayit["durum"] = "YOK_404"
        else:
            cs = getir(url + ".CHECKSUM")
            beklenen = cs.decode().split()[0].lower() if cs else None
            gercek = sha256_bayt(veri)
            if beklenen != gercek:
                kayit.update(durum="HATA_CHECKSUM", beklenen=beklenen, sha256=gercek)
            else:
                hedef = BURASI / yol
                hedef.parent.mkdir(parents=True, exist_ok=True)
                hedef.write_bytes(veri)
                (hedef.parent / (hedef.name + ".CHECKSUM")).write_bytes(cs)
                kayit.update(durum="TAMAM", sha256=gercek, bayt=len(veri))
    except Exception as e:
        kayit.update(durum="HATA_AG", hata=f"{type(e).__name__}: {e}")
    kayit["zaman_utc"] = datetime.now(timezone.utc).isoformat(timespec="seconds")
    with KILIT:
        with manifest.open("a", encoding="utf-8") as f:
            f.write(json.dumps(kayit, ensure_ascii=False) + "\n")
    return kayit["durum"]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--is-parcacigi", type=int, default=16)
    arg = ap.parse_args()
    isler = plan_kur()
    manifest = BURASI / "MANIFEST.jsonl"
    tamam = dogrulanmis_kayitlar(manifest)
    print(f"plan: {len(isler)} zip ({len(isler)//2} coin-ay), önceden doğrulanmış: {len(tamam)}", flush=True)
    sayac = {}
    with ThreadPoolExecutor(arg.is_parcacigi) as ex:
        for i, durum in enumerate(ex.map(lambda x: indir_bir(x, manifest, tamam), isler), 1):
            sayac[durum] = sayac.get(durum, 0) + 1
            if i % 500 == 0 or i == len(isler):
                print(f"{i}/{len(isler)} {sayac}", flush=True)
    ozet = {"zaman_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"), "plan_zip": len(isler),
            "sonuc_bu_kosu": sayac, "gelistirme_evreni_sha256": GELISTIRME_SHA256, "donem": [ILK_AY, SON_AY]}
    (BURASI / "indirme_ozet.json").write_text(json.dumps(ozet, ensure_ascii=False, indent=1), encoding="utf-8")
    print(json.dumps(ozet, ensure_ascii=False))


if __name__ == "__main__":
    main()
