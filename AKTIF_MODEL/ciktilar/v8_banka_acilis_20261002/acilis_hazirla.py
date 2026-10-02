"""ACILIS.json hazırlığı (BANKA_ONKAYIT §3.7 netleştirme 20 a, j; UYGULAMA_EK rev 2; değerlendirici oturum).

Dondurulmuş kodun parçası değildir. Mühürden (yeniden üretilmiş BANKA_MUHURLU.json) K ve D listelerini, uygun evrenden
adayları alır; görülmüş 7 gün mühür §4'tür (BTC/ETH 2023-06-24 → 06-30). Anonim anahtar `banka_kos.anonim.anahtar_uret`
ile bir kez üretilir (varsa üzerine yazılmaz). Sonuç `banka_kos.acilis.acilis_oku` ile (DONDURMA'ya karşı) denetlenir.
Çıktılar git dışındadır (coin adı içerir); ekrana yalnız sayılar ve hash'ler.

Kullanım (v8 içinden çalıştırılır ki banka_kos içe aktarılabilsin):
  python -X utf8 <bu betik> --muhur M --evren E --liste-ozeti L --banka-kok K --cikti DIZIN --dondurma D
"""
import argparse
import hashlib
import json
import sys
from pathlib import Path

MUHUR_SHA256 = "420dfc2a4a122a8183b2feecd229fca05c79eb06eff39398a156f94ff7bde9dd"
EVREN_SHA256 = "9148fb8e02271f33196b92c4fedcb031e3cf91aad202f51547543e2d9d70bac3"
DONDURMA_COMMIT = "de596953cadbad43c1cc699d6391ed8693de821c"
GORULMUS = [f"2023-06-{g}" for g in range(24, 31)]
BTC_ETH = ("BTCUSDT", "ETHUSDT")


def main():
    ap = argparse.ArgumentParser()
    for a in ("--muhur", "--evren", "--liste-ozeti", "--banka-kok", "--cikti", "--dondurma"):
        ap.add_argument(a, required=True)
    arg = ap.parse_args()
    sys.path.insert(0, str(Path.cwd()))
    from banka_kos import acilis, anonim
    for yol, beklenen in ((arg.muhur, MUHUR_SHA256), (arg.evren, EVREN_SHA256)):
        if hashlib.sha256(Path(yol).read_bytes()).hexdigest() != beklenen:
            raise SystemExit("DURDU: girdi hash'i uyusmuyor (T1)")
    muhur = json.loads(Path(arg.muhur).read_text(encoding="utf-8"))
    evren = json.loads(Path(arg.evren).read_text(encoding="utf-8"))
    ozet = json.loads(Path(arg.liste_ozeti).read_text(encoding="utf-8"))
    cikti = Path(arg.cikti)
    anahtar = cikti / "ANONIM_ANAHTAR.bin"
    anahtar_sha = (anonim.anahtar_uret(anahtar) if not anahtar.exists()
                   else hashlib.sha256(anahtar.read_bytes()).hexdigest())
    a = {"mimari": "A", "adaylar": sorted(evren["uygun"]), "k_coinleri": sorted(muhur["banka"]),
         "d_coinleri": sorted(set(muhur["gelistirme"]) - set(BTC_ETH)), "gorulmus_gunler": GORULMUS,
         "banka_kok": str(Path(arg.banka_kok)), "anonim_anahtar": str(anahtar),
         "sureklilik_sorunu": int(ozet["sureklilik_sorunu"]), "dondurma_commit": DONDURMA_COMMIT}
    yol = cikti / "ACILIS.json"
    if yol.exists():
        raise SystemExit("DURDU: ACILIS.json zaten var")
    yol.write_text(json.dumps(a, ensure_ascii=True, indent=1), encoding="utf-8")
    dondurma = json.loads(Path(arg.dondurma).read_text(encoding="utf-8"))
    _, kanonik_sha = acilis.acilis_oku(yol, dondurma)
    print(json.dumps({"aday": len(a["adaylar"]), "K": len(a["k_coinleri"]), "D": len(a["d_coinleri"]),
                      "gorulmus_gun": len(GORULMUS), "sureklilik_sorunu": a["sureklilik_sorunu"],
                      "acilis_kanonik_sha256": kanonik_sha, "anonim_anahtar_sha256": anahtar_sha}))


if __name__ == "__main__":
    main()
