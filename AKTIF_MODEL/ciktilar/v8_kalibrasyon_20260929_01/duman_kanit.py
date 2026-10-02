"""Duman kanıtının kimlik bağı (Codex T17-a). Motor koşulmaz: duman.py'nin (P15) ürettiği iki klasör diskten okunur.

Denetim: iki klasörde (duman_4isci, duman_1isci_ters) birim dosyaları (28) ve ek liste bayt bayt aynı (duman_sonuc.json'un
iddiası yeniden sınanır); bütün zarflardaki dört kimlik (kod, motor, parametre, ortam) tek, iş listelerindekiyle ve
KOD_DONDURMA.json'dakiyle aynı; HAR sonuç dosyası dondurmadakiyle aynı; duman_sonuc.json geçti ve sayısı tutuyor.
Çıktı duman_kanit.json: ortak 'kanit' bloğu (kanit.py; kaynak: duman_sonuc.json ve iki klasörün hash'leri) ve
duman_4isci dosya hash'leri (eşdeğerlik kanıtının girdileri bunlarla eşleşmeli). Yalnız ad, sayı ve hash yazılır.
Kullanım (v8 dışından; duman klasörlerinin bulunduğu kopyada, dizüstü): python duman_kanit.py -> duman_kanit.json"""
import json
import sys
from pathlib import Path

BURASI = Path(__file__).resolve().parent
V8 = BURASI.parents[1] / 'v8'
if str(BURASI) not in sys.path:
    sys.path.insert(0, str(BURASI))
if str(V8) not in sys.path:
    sys.path.insert(1, str(V8))

import kanit  # noqa: E402

KLASORLER = ('duman_4isci', 'duman_1isci_ters')
BEKLENEN_BIRIM = 28
IS_LISTESI, EK_LISTE = 'IS_LISTESI.json', 'IS_LISTESI_EK.jsonl'     # kalibrasyon.kosucu ile aynı adlar


def _ek_ozet(d: Path) -> str:
    """duman._ozet ile aynı: ek listenin satırları sıralanır (işçi sırasından bağımsız)."""
    ek = sorted((d / EK_LISTE).read_text(encoding='ascii').splitlines()) if (d / EK_LISTE).exists() else []
    return kanit.sha_bayt('\n'.join(ek).encode())


def olustur(kok: Path = BURASI, har_sha: str = None) -> dict:
    kok = Path(kok)
    if har_sha is None:
        from kalibrasyon.yurutucu import har_paketi
        har_sha, _ = har_paketi()
    dondurma = json.loads((kok / 'KOD_DONDURMA.json').read_text(encoding='utf-8'))
    beklenen = {k: dondurma['kimlikler'][k] for k in kanit.DORT}
    duman_sonuc = json.loads((kok / 'duman_sonuc.json').read_text(encoding='utf-8'))
    klasor, hashler, kumeler, listeler = {}, {}, [], []
    for ad in KLASORLER:
        d = kok / ad
        hashler[ad] = kanit.dosya_hashleri(d)
        kumeler += kanit.zarf_kimlikleri(sorted(d.glob('d2_*.json')))
        liste = json.loads((d / IS_LISTESI).read_text(encoding='ascii'))['kimlikler']
        listeler.append({k: liste.get(k) for k in kanit.DORT})
        klasor[ad] = {'dosya': len(hashler[ad]), 'birlesik_sha256': kanit.birlesik(hashler[ad]),
                      'is_listesi_sha256': kanit.sha_dosya(d / IS_LISTESI), 'ek_liste_ozet': _ek_ozet(d)}
    tekil = [json.loads(x) for x in sorted({json.dumps(k, sort_keys=True) for k in kumeler})]
    kimlik = kanit.tek_kimlik(tekil)
    a, b = (klasor[k] for k in KLASORLER)
    denetim = {
        'dosyalar_ayni': hashler[KLASORLER[0]] == hashler[KLASORLER[1]],
        'ek_liste_ayni': a['ek_liste_ozet'] == b['ek_liste_ozet'],
        'birim_sayisi': a['dosya'] == b['dosya'] == BEKLENEN_BIRIM == duman_sonuc.get('birim_sayisi_4isci'),
        'duman_sonuc_gecti': bool(duman_sonuc.get('gecti')),
        'tek_kimlik': kimlik is not None,
        'dondurmayla_ayni': kimlik == beklenen and all(x == beklenen for x in listeler),
        'har_dondurmayla_ayni': har_sha == dondurma.get('har_sonuc_sha256'),
    }
    return {'gecti': all(denetim.values()), 'denetim': denetim,
            'kanit': kanit.blok(__file__, kimlik, har_sha,
                                {'duman_sonuc_sha256': kanit.sha_dosya(kok / 'duman_sonuc.json'), 'klasorler': klasor},
                                burasi=kok),
            'dosya_sha256': hashler[KLASORLER[0]]}


def main(argv=None) -> int:
    sonuc = olustur()
    (BURASI / 'duman_kanit.json').write_text(json.dumps(sonuc, indent=1, sort_keys=True), encoding='utf-8')
    print(json.dumps({'gecti': sonuc['gecti'], 'denetim': sonuc['denetim']}), flush=True)
    return 0 if sonuc['gecti'] else 1


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
