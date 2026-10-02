"""v8 banka indirme listesi (BANKA_ONKAYIT §2.3; netleştirme 19, 20 i; değerlendirici oturum, 2 Ekim 2026).

Dondurulmuş kodun parçası değildir; çıktısı BANKA_MANIFEST.jsonl ile bağlanır. Mühür belgesini (yeniden üretilmiş
BANKA_MUHURLU.json) okur, listeyi data.binance.vision S3 klasör listesinden kurar. Coin adı içeren çıktılar
(`liste.jsonl`, `sureklilik.json`) git dışındaki klasöre yazılır; ekrana ve `LISTE_OZETI.json`'a yalnız sayılar ve
hash'ler çıkar.

Kapsam (§2.3):
- K (80): aylık 1h klines ilk dosya → 2026-08; aylık fundingRate ilk dosya → 2026-08; 2026-09-01 → 09-23 günlük 1h
  klines; Eylül funding.
- D (120) ve BTC/ETH: Z1 ayları (ilk dosya → 2023-06) ve Z2 (2026-07, 2026-08 aylık; Eylül günlük klines; Eylül
  funding). D dönemi mevcut paketten.
- Eylül funding: sembolde 2026-09 aylık fundingRate arşivi varsa o; yoksa ve sembol Eylül'de işlem gördüyse kamu
  fundingRate uç noktası tek anlık görüntü (`ham/fundingRate_api/<sym>.json`, ayrı satır).
- Her zip'in resmi .CHECKSUM dosyası (listede `checksum_url`).
Süreklilik denetimi (mühür §8): aylık klines dizisinde iç boşluk, son aylık dosyanın 2026-08'den önce bitmesi
(listeden çıkma / taşınma), Eylül günlük dosyalarının eksikliği, arşivin mühürdeki ham listeden (2026-09-24) farklı
başlaması. Sorunlu semboller çıkarılmaz; sayılır.

Kullanım: python -X utf8 indirme_listesi.py --muhur M --evren E --ham H --cikti DIZIN
"""
import argparse
import hashlib
import json
import re
import urllib.request
import xml.etree.ElementTree as ET
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

MUHUR_SHA256 = "420dfc2a4a122a8183b2feecd229fca05c79eb06eff39398a156f94ff7bde9dd"
EVREN_SHA256 = "9148fb8e02271f33196b92c4fedcb031e3cf91aad202f51547543e2d9d70bac3"
HAM_SHA256 = "5ad6f8958375384738b7bd5df70eb8b019ffc26692483b8264e4ceb3fdf91bc2"
BTC_ETH = ("BTCUSDT", "ETHUSDT")
S3 = "https://s3-ap-northeast-1.amazonaws.com/data.binance.vision"
KOK = "https://data.binance.vision/"
Z1_SON_AY, Z2_AYLAR, K_SON_AY, EYLUL = "2023-06", ("2026-07", "2026-08"), "2026-08", "2026-09"
EYLUL_GUNLER = tuple(f"2026-09-{g:02d}" for g in range(1, 24))
FUNDING_API = "https://fapi.binance.com/fapi/v1/fundingRate"
EYLUL_BAS_MS, Z2_SON_MS = 1788220800000, 1790208000000          # 2026-09-01, 2026-09-24 00:00 UTC
NS = {"s": "http://s3.amazonaws.com/doc/2006-03-01/"}


def sha256_dosya(yol) -> str:
    return hashlib.sha256(Path(yol).read_bytes()).hexdigest()


def s3_liste(onek: str) -> dict:
    """{anahtar: boyut} (sayfalı)."""
    out, isaret = {}, ""
    while True:
        url = f"{S3}?prefix={onek}&marker={isaret}"
        with urllib.request.urlopen(url, timeout=60) as r:
            kok = ET.fromstring(r.read())
        for c in kok.findall("s:Contents", NS):
            out[c.find("s:Key", NS).text] = int(c.find("s:Size", NS).text)
        if kok.find("s:IsTruncated", NS).text != "true":
            return out
        isaret = max(out)


def ay_dizisi(ilk: str, son: str) -> list:
    y, m = map(int, ilk.split("-"))
    out = []
    while f"{y:04d}-{m:02d}" <= son:
        out.append(f"{y:04d}-{m:02d}")
        y, m = (y + 1, 1) if m == 12 else (y, m + 1)
    return out


def sembol_plani(sym: str, grup: str) -> tuple:
    """(satırlar, süreklilik bulguları, eylül funding kaynağı)."""
    kl = s3_liste(f"data/futures/um/monthly/klines/{sym}/1h/")
    fr = s3_liste(f"data/futures/um/monthly/fundingRate/{sym}/")
    gk = s3_liste(f"data/futures/um/daily/klines/{sym}/1h/{sym}-1h-2026-09-")

    def aylik(liste, desen):
        out = {}
        for k, b in liste.items():
            m = re.fullmatch(desen, k.rsplit("/", 1)[1])
            if m:
                out[m.group(1)] = (k, b, (k + ".CHECKSUM") in liste)
        return out
    kl_ay = aylik(kl, rf"{sym}-1h-(\d{{4}}-\d{{2}})\.zip")
    fr_ay = aylik(fr, rf"{sym}-fundingRate-(\d{{4}}-\d{{2}})\.zip")
    gk_gun = aylik(gk, rf"{sym}-1h-(2026-09-\d{{2}})\.zip")

    if grup == "K":
        kl_sec = [a for a in kl_ay if a <= K_SON_AY]
        fr_sec = [a for a in fr_ay if a <= K_SON_AY]
    else:
        kl_sec = [a for a in kl_ay if a <= Z1_SON_AY or a in Z2_AYLAR]
        fr_sec = [a for a in fr_ay if a <= Z1_SON_AY or a in Z2_AYLAR]
    gun_sec = [g for g in EYLUL_GUNLER if g in gk_gun]

    satirlar = []

    def ekle(tur, donem, anahtar, bayt, cs):
        ad = anahtar.rsplit("/", 1)[1]
        satirlar.append({"grup": grup, "sym": sym, "tur": tur, "donem": donem, "url": KOK + anahtar,
                         "checksum_url": KOK + anahtar + ".CHECKSUM" if cs else None, "bayt": bayt,
                         "yol": f"ham/{tur}/{sym}/{ad}"})
    for a in sorted(kl_sec):
        ekle("klines", a, *kl_ay[a])
    for g in gun_sec:
        ekle("klines", g, *gk_gun[g])
    for a in sorted(fr_sec):
        ekle("fundingRate", a, *fr_ay[a])
    if EYLUL in fr_ay:
        ekle("fundingRate", EYLUL, *fr_ay[EYLUL])
        eylul = "arsiv"
    elif gun_sec:
        satirlar.append({"grup": grup, "sym": sym, "tur": "fundingRate_api", "donem": EYLUL,
                         "url": f"{FUNDING_API}?symbol={sym}&startTime={EYLUL_BAS_MS}&endTime={Z2_SON_MS - 1}&limit=1000",
                         "checksum_url": None, "bayt": None, "yol": f"ham/fundingRate_api/{sym}.json"})
        eylul = "api"
    else:
        eylul = "yok"

    bulgu = []
    tum = sorted(kl_ay)
    if tum:
        if len(tum) != len(ay_dizisi(tum[0], tum[-1])):
            bulgu.append("aylik_ic_bosluk")
        if tum[-1] < K_SON_AY:
            bulgu.append("erken_bitis")
        elif len(gun_sec) < len(EYLUL_GUNLER):
            bulgu.append("eylul_gunluk_eksik")
    else:
        bulgu.append("aylik_yok")
    if any(not s["checksum_url"] for s in satirlar if s["tur"] != "fundingRate_api"):
        bulgu.append("checksum_dosyasi_yok")
    return satirlar, bulgu, eylul, (tum[0] if tum else None)


def main():
    ap = argparse.ArgumentParser()
    for a in ("--muhur", "--evren", "--ham", "--cikti"):
        ap.add_argument(a, required=True)
    arg = ap.parse_args()
    for yol, beklenen in ((arg.muhur, MUHUR_SHA256), (arg.evren, EVREN_SHA256), (arg.ham, HAM_SHA256)):
        if sha256_dosya(yol) != beklenen:
            raise SystemExit("DURDU: girdi hash'i uyusmuyor (T1)")
    muhur = json.loads(Path(arg.muhur).read_text(encoding="utf-8"))
    evren = json.loads(Path(arg.evren).read_text(encoding="utf-8"))
    ham = json.loads(Path(arg.ham).read_text(encoding="utf-8"))
    k = sorted(muhur["banka"])
    d = sorted(set(muhur["gelistirme"]) - set(BTC_ETH))
    if len(k) != 80 or len(d) != 120 or set(k) & set(d) or set(k) | set(d) != set(evren["uygun"]):
        raise SystemExit("DURDU: K/D bolumlemesi mühürle tutarsiz (T1)")
    gruplar = [(s, "K") for s in k] + [(s, "D") for s in d] + [(s, "BE") for s in BTC_ETH]
    with ThreadPoolExecutor(16) as ex:
        sonuc = list(ex.map(lambda x: sembol_plani(*x), gruplar))

    satirlar, sureklilik, kaynak = [], {}, {"arsiv": 0, "api": 0, "yok": 0}
    for (sym, grup), (s, bulgu, eylul, ilk) in zip(gruplar, sonuc):
        satirlar += s
        kaynak[eylul] += 1
        if sym in ham and ilk is not None and ilk != ham[sym][0]:
            bulgu.append("arsiv_ilk_ay_degisti")
        if bulgu:
            sureklilik[sym] = bulgu
    cikti = Path(arg.cikti)
    cikti.mkdir(parents=True, exist_ok=True)
    liste_b = "".join(json.dumps(r, ensure_ascii=True, sort_keys=True) + "\n" for r in satirlar).encode("ascii")
    (cikti / "liste.jsonl").write_bytes(liste_b)
    (cikti / "sureklilik.json").write_text(json.dumps(sureklilik, indent=1, sort_keys=True), encoding="utf-8")

    def say(f):
        return sum(1 for r in satirlar if f(r))
    tur_say = {}
    for bulgu in sureklilik.values():
        for b in bulgu:
            tur_say[b] = tur_say.get(b, 0) + 1
    ozet = {
        "coin": {"K": len(k), "D": len(d), "BTC_ETH": 2},
        "veri_dosyasi": len(satirlar),
        "checksum_dosyasi": say(lambda r: r["checksum_url"]),
        "toplam_dosya": len(satirlar) + say(lambda r: r["checksum_url"]),
        "toplam_bayt_zip": sum(r["bayt"] or 0 for r in satirlar),
        "grup_dosya": {g: say(lambda r, g=g: r["grup"] == g) for g in ("K", "D", "BE")},
        "tur_dosya": {t: say(lambda r, t=t: r["tur"] == t) for t in ("klines", "fundingRate", "fundingRate_api")},
        "eylul_gunluk_kline": say(lambda r: r["tur"] == "klines" and len(r["donem"]) == 10),
        "eylul_funding_kaynagi": kaynak,
        "sureklilik_sorunu": len(sureklilik),
        "sureklilik_turleri": tur_say,
        "liste_sha256": hashlib.sha256(liste_b).hexdigest(),
        "betik_sha256": sha256_dosya(__file__),
        "girdi_sha256": {"muhur": MUHUR_SHA256, "evren": EVREN_SHA256, "ham": HAM_SHA256},
    }
    (cikti / "LISTE_OZETI.json").write_text(json.dumps(ozet, indent=1, sort_keys=True), encoding="utf-8")
    print(json.dumps(ozet, ensure_ascii=False))


if __name__ == "__main__":
    main()
