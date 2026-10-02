"""v8 banka indirici (BANKA_ONKAYIT §2.3; netleştirme 19, 20 i; kullanıcı onayı 2 Ekim 2026).

`indirme_listesi.py` çıktısını (liste.jsonl; sha256'sı LISTE_OZETI.json'daki ile aynı olmalı) indirir. Dondurulmuş kodun
parçası değildir. `BANKA_MANIFEST.jsonl` yalnız sona ekleme yapılarak yazılır; satır {yol, sha256, checksum, durum, ...};
durum ∈ TAMAM, CHECKSUM_HATASI, INDIRME_HATASI, YOK (banka_kos.veri_denetim.DURUMLAR). Bir dosyanın ilk TAMAM satırının
sha256'sı bağlayıcıdır. Zip'ler resmi .CHECKSUM ile doğrulanır (checksum = dosyadaki sha256); uyuşmazlıkta en fazla 3
deneme, her deneme ayrı satır. API görüntüsünde resmi checksum yoktur: checksum = sha256. TAMAM ve diskte bağlayıcı hash'le
duran dosya yeniden indirilmez (devam). Ekrana yalnız sayılar.

Kullanım: python -X utf8 banka_indir.py --liste L/liste.jsonl --ozet L/LISTE_OZETI.json --kok /opt/v8/banka_veri
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

MANIFEST_ADI = "BANKA_MANIFEST.jsonl"
KILIT = threading.Lock()


def sha(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def getir(url: str, deneme: int = 4):
    hata = None
    for i in range(deneme):
        try:
            with urllib.request.urlopen(url, timeout=60) as r:
                return r.read()
        except urllib.error.HTTPError as e:
            if e.code == 404:
                return None
            hata = e
        except Exception as e:  # ağ hatası: bekle, yeniden dene
            hata = e
        time.sleep(2 * (i + 1))
    raise hata


def yaz(manifest: Path, kayit: dict):
    kayit["zaman_utc"] = datetime.now(timezone.utc).isoformat(timespec="seconds")
    with KILIT, manifest.open("a", encoding="utf-8") as f:
        f.write(json.dumps(kayit, ensure_ascii=True, sort_keys=True) + "\n")


def indir_bir(r: dict, kok: Path, manifest: Path, baglayici: dict) -> str:
    hedef = kok / r["yol"]
    if r["yol"] in baglayici and hedef.is_file() and sha(hedef.read_bytes()) == baglayici[r["yol"]]:
        return "ATLA"
    taban = {"yol": r["yol"], "url": r["url"]}
    for _ in range(3):
        try:
            veri = getir(r["url"])
            if veri is None:
                yaz(manifest, dict(taban, durum="YOK"))
                return "YOK"
            if r["tur"] == "fundingRate_api":
                kayit = json.loads(veri)
                if not isinstance(kayit, list) or len(kayit) >= 1000:
                    yaz(manifest, dict(taban, durum="INDIRME_HATASI", hata="api yaniti liste degil ya da sinirda"))
                    return "INDIRME_HATASI"
                beklenen, cs = sha(veri), None
            else:
                cs = getir(r["checksum_url"]) if r["checksum_url"] else None
                beklenen = cs.decode("ascii").split()[0].lower() if cs else None
            gercek = sha(veri)
            if beklenen != gercek:
                yaz(manifest, dict(taban, durum="CHECKSUM_HATASI", sha256=gercek, checksum=beklenen))
                continue
            hedef.parent.mkdir(parents=True, exist_ok=True)
            hedef.write_bytes(veri)
            if cs:
                (hedef.parent / (hedef.name + ".CHECKSUM")).write_bytes(cs)
            yaz(manifest, dict(taban, durum="TAMAM", sha256=gercek, checksum=beklenen, bayt=len(veri)))
            return "TAMAM"
        except Exception as e:
            yaz(manifest, dict(taban, durum="INDIRME_HATASI", hata=type(e).__name__))
            return "INDIRME_HATASI"
    return "CHECKSUM_HATASI"


def main():
    ap = argparse.ArgumentParser()
    for a in ("--liste", "--ozet", "--kok"):
        ap.add_argument(a, required=True)
    ap.add_argument("--is-parcacigi", type=int, default=16)
    arg = ap.parse_args()
    liste_b = Path(arg.liste).read_bytes()
    if sha(liste_b) != json.loads(Path(arg.ozet).read_text(encoding="utf-8"))["liste_sha256"]:
        raise SystemExit("DURDU: liste sha256 LISTE_OZETI ile ayni degil")
    satirlar = [json.loads(s) for s in liste_b.decode("ascii").splitlines() if s.strip()]
    kok = Path(arg.kok)
    kok.mkdir(parents=True, exist_ok=True)
    manifest = kok / MANIFEST_ADI
    baglayici = {}
    if manifest.exists():
        for s in manifest.read_text(encoding="utf-8").splitlines():
            k = json.loads(s)
            if k.get("durum") == "TAMAM":
                baglayici.setdefault(k["yol"], k["sha256"])
    sayac = {}
    with ThreadPoolExecutor(arg.is_parcacigi) as ex:
        for i, d in enumerate(ex.map(lambda r: indir_bir(r, kok, manifest, baglayici), satirlar), 1):
            sayac[d] = sayac.get(d, 0) + 1
            if i % 2000 == 0 or i == len(satirlar):
                print(f"{i}/{len(satirlar)} {sayac}", flush=True)
    ozet = {"zaman_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"), "liste_sha256": sha(liste_b),
            "plan": len(satirlar), "bu_kosu": sayac, "betik_sha256": sha(Path(__file__).read_bytes()),
            "manifest_sha256": sha(manifest.read_bytes())}
    (kok / "INDIRME_OZETI.json").write_text(json.dumps(ozet, indent=1, sort_keys=True), encoding="utf-8")
    print(json.dumps(ozet))


if __name__ == "__main__":
    main()
