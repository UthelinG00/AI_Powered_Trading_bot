"""v8 mühürlü test bankası seçimi (ONKAYIT.md §5).

Girdiler:
- ONKAYIT.md: SHA-256'sı DAMGA.json'daki değerle eşleşmeli.
- uygun_evren.json: SHA-256'sı sabit.
- drand turu JSON'u: tur numarası DAMGA.json'daki hedef turla eşleşmeli; randomness = sha256(signature).
Seed ile oynama olmasın diye tohum, belge hash'i ile önceden sabitlenmiş drand turunun birleşiminden türetilir.

Çıktılar:
- BANKA_MUHURLU.json: banka ve geliştirme listeleri, tohum, girdi hash'leri. Ajanlar bu dosyayı OKUMAZ.
- GELISTIRME_EVRENI.json: yalnız geliştirme coinleri. Ajanlara verilecek dosya budur.

Kullanım: python -X utf8 banka_sec.py --drand drand_tur.json
Yedek yol (drand erişilemezse, raporlanır): python -X utf8 banka_sec.py --drand-yok
Ağ erişimi yok. Aynı girdilerle her koşu aynı listeyi üretir.
"""
import argparse
import hashlib
import json
import random
import sys
from pathlib import Path

BURASI = Path(__file__).resolve().parent
EVREN_SHA256 = "9148fb8e02271f33196b92c4fedcb031e3cf91aad202f51547543e2d9d70bac3"
DRAND_ZINCIR = "8990e7a9aaed2ffed73dbd7092123d6f289930540d7651336225dc172e51b2ce"
# Kohort payları %40'ın en büyük kalan yöntemiyle 80'e tamamlanmış hâli (ONKAYIT §4).
KOHORT_PAY = {"2020": 30, "2021": 20, "2022": 8, "2023": 22}
BANKA_SAYISI = 80
GELISTIRME_EK = ["BTCUSDT", "ETHUSDT"]


def sha256_dosya(yol):
    return hashlib.sha256(Path(yol).read_bytes()).hexdigest()


def dur(kod):
    sys.exit(f"DURDU: {kod}")


def drand_randomness(yol, hedef_tur):
    tur = json.loads(Path(yol).read_text(encoding="utf-8"))
    if int(tur["round"]) != int(hedef_tur):
        dur("DRAND_TUR_UYUSMUYOR")
    # Zincirli şemada randomness, imzanın SHA-256'sıdır; tutarlılık yerelde denetlenir.
    if hashlib.sha256(bytes.fromhex(tur["signature"])).hexdigest() != tur["randomness"]:
        dur("DRAND_RANDOMNESS_TUTARSIZ")
    return tur["randomness"]


def main():
    ap = argparse.ArgumentParser()
    grup = ap.add_mutually_exclusive_group(required=True)
    grup.add_argument("--drand")
    grup.add_argument("--drand-yok", action="store_true")
    arg = ap.parse_args()

    damga = json.loads((BURASI / "DAMGA.json").read_text(encoding="utf-8"))
    onkayit_sha = sha256_dosya(BURASI / "ONKAYIT.md")
    if onkayit_sha != damga["onkayit_sha256"]:
        dur("ONKAYIT_HASH_UYUSMUYOR")
    if sha256_dosya(BURASI / "uygun_evren.json") != EVREN_SHA256:
        dur("EVREN_HASH_UYUSMUYOR")
    if damga.get("drand_zincir") != DRAND_ZINCIR:
        dur("DRAND_ZINCIR_UYUSMUYOR")

    randomness = "" if arg.drand_yok else drand_randomness(arg.drand, damga["drand_hedef_tur"])
    tohum_hex = hashlib.sha256((onkayit_sha + randomness).encode("ascii")).hexdigest()
    tohum = int(tohum_hex[:16], 16)

    evren = json.loads((BURASI / "uygun_evren.json").read_text(encoding="utf-8"))
    uygun, aylar = evren["uygun"], evren["aylar"]
    rng = random.Random(tohum)
    banka = []
    for kohort in sorted(KOHORT_PAY):
        liste = sorted(s for s in uygun if aylar[s][0][:4] == kohort)
        banka += sorted(rng.sample(liste, KOHORT_PAY[kohort]))
    if len(banka) != BANKA_SAYISI or len(set(banka)) != BANKA_SAYISI:
        dur("BANKA_SAYISI")
    gelistirme = sorted(set(uygun) - set(banka)) + GELISTIRME_EK

    ortak = {
        "onkayit_sha256": onkayit_sha,
        "uygun_evren_sha256": EVREN_SHA256,
        "gelistirme_donemi_utc": ["2023-07-01T00:00:00Z", "2026-07-01T00:00:00Z"],
    }
    muhur = dict(ortak, drand_tur=None if arg.drand_yok else damga["drand_hedef_tur"],
                 drand_randomness=randomness or None, drand_yedek_yol=bool(arg.drand_yok),
                 tohum_hex=tohum_hex, tohum=tohum, banka=banka, gelistirme=gelistirme,
                 not_="Ajanlar bu dosyayı OKUMAZ. Banka verisi banka testine kadar indirilmez.")
    (BURASI / "BANKA_MUHURLU.json").write_text(json.dumps(muhur, ensure_ascii=False, indent=1), encoding="utf-8")
    (BURASI / "GELISTIRME_EVRENI.json").write_text(json.dumps(dict(ortak, gelistirme=gelistirme), ensure_ascii=False, indent=1), encoding="utf-8")
    # Banka içeriği ekrana yazılmaz; yalnız sayılar ve hash'ler.
    print(json.dumps({"banka_sayisi": len(banka), "gelistirme_sayisi": len(gelistirme),
                      "banka_muhurlu_sha256": sha256_dosya(BURASI / "BANKA_MUHURLU.json"),
                      "gelistirme_evreni_sha256": sha256_dosya(BURASI / "GELISTIRME_EVRENI.json"),
                      "drand_yedek_yol": bool(arg.drand_yok)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
