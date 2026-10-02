"""Banka tek atış betiği (BANKA §2.4; K2-07; §3.7 netleştirme 20; BK-1…BK-20). Bir kez çağrılır; kesilirse aynı
komut yeniden verilir (aynı dondurulmuş iş listesinin tamamlanması, BK-1).

Kullanım (v8 içinden; önce veri_denetim.py aynı argümanlarla):
  python banka_kos.py banka <cikti> <ACILIS.json> <DONDURMA.json> [--isci N]
  python banka_kos.py kuru  <cikti> <A|B> [--alici <age açık anahtarı>] [--anonim-anahtar <yol>] [--tohum <n>] [--isci N]
Sıra: T1 (DONDURMA; kuruda kimlikler kaydedilir) → veri denetimi aynı kodla yeniden hesaplanır ve VERI_DENETIM.json ile
birebir aynı olmalı (T2 yok) → bağlam kimlikleri (veri, dönem, filtre, HAR, anonim anahtar) tanıma bağlanır, her işçi
denetler → bütün birimler (kosucu: şifreli sonuç, açık denetim) → SONUC_DAMGA.json → denetim/DENETIM_OZETI.json (T1–T5;
performanssız). Ekrana yalnız sayılar basılır; beklenmeyen hatanın izi şifrelidir (20 f).
Çıkış: 0 tamam; 3 T2; 4 T1/açılış; 5 kesildi (aynı komutla sürer); 6 koşu hatası; 7 T5 (parite hatası).
"""
import functools
import json
import sys
from pathlib import Path

V8 = Path(__file__).resolve().parent
if str(V8) not in sys.path:
    sys.path.insert(0, str(V8))

from banka_kos import acilis as A  # noqa: E402
from banka_kos import anonim, ayar  # noqa: E402
from banka_kos import kosucu as K  # noqa: E402
from banka_kos import yurutucu as Y  # noqa: E402
from banka_kos.veri_denetim import kanonik  # noqa: E402
from veri_denetim import argumanlar, denetim_hesapla, sinirli, tanim_hazirla  # noqa: E402

T5_CIKIS = 7


def _esleme_yolu(tanim: dict, cikti: Path) -> Path:
    return (cikti / 'ANONIM_ESLEME.json' if tanim['mod'] == 'kuru'
            else Path(tanim['anonim_anahtar']).with_suffix('.esleme.json'))


def hazirla(arg: dict, ek: dict = None, durum: dict = None) -> tuple:
    """(tanim, iş listesi kimlikleri). T1 ve T2 kapıları; aykırılık A.AcilisHatasi."""
    durum = {} if durum is None else durum
    cikti = arg['cikti']
    tanim, guncel, meta = tanim_hazirla(arg, ek)
    durum['alici'] = tanim['alici']
    vd_yol = cikti / 'denetim' / 'VERI_DENETIM.json'
    if not vd_yol.exists():
        raise A.AcilisHatasi("VERI_DENETIM.json yok: once veri_denetim.py")
    vd_bayt = vd_yol.read_bytes()
    sonuc, veri, r, frapor = denetim_hesapla(tanim, guncel, meta)
    if kanonik(sonuc) != vd_bayt:
        raise A.AcilisHatasi("VERI_DENETIM.json bu acilisin yeniden hesaplanan denetimiyle ayni degil")
    if sonuc['denetim']['karar']['T2']:
        raise A.AcilisHatasi("T2: veri denetimi teknik gecersizlik verdi; kosu baslamaz")
    tanim = A.bagla(tanim, veri, r, frapor)
    anahtar = Path(tanim['anonim_anahtar'])
    es_sha = anonim.esleme_yaz(_esleme_yolu(tanim, cikti), anonim.kimlikler(anahtar.read_bytes(), veri.adaylar))
    kimlik = {'mod': tanim['mod'], 'mimari': tanim['mimari'], 'kimlikler': guncel, **meta,
              'veri_kimligi': tanim['veri_kimligi'], 'veri_denetim_json_sha256': A.sha_bayt(vd_bayt),
              'donem': tanim['donem'], 'filtre_tablo_sha256': tanim['filtre_tablo_sha256'],
              'har_sonuc_sha256': tanim['har_sonuc_sha256'], 'anonim_anahtar_sha256': tanim['anonim_anahtar_sha256'],
              'anonim_esleme_sha256': es_sha, 'tohum_banka': tanim['tohum_banka']}
    return tanim, kimlik


def denetim_ozeti(cikti: Path, birimler: list, damga: dict, kimlik: dict) -> dict:
    """T1–T5 (§2.4 denetim listesi; performanssız). T3/T4 ihlali koşuyu zaten durdurur (kosucu, muhasebe kapısı,
    null değişmezleri); burada tamamlanma ve açık kayıtlar sayılır. T5 birincil birimin paritesidir (20 d, h)."""
    birincil = next(b for b in birimler if b['grup'] == 'birincil')
    par = K.kayit_oku(cikti, K.birim_adi(birincil))['acik'].get('parite')
    muhasebe = sum(1 for s in damga['birimler'] if 'muhasebe' in K.kayit_oku(cikti, s[0])['acik'])
    return {'T1': 'yok' if kimlik['mod'] == 'banka' else 'kuru: DONDURMA yok, kimlikler kaydedildi',
            'T2': 'yok', 'T3': 'yok', 'T4': {'muhasebe_kapisi_gecen_birim': muhasebe},
            'T5': {'parite': par, 'durum': 'yok' if par and par['hata'] == 0 else 'VAR'},
            'birim_sayisi': damga['birim_sayisi'], 'damga_kok_sha256': damga['kok_sha256'],
            'is_listesi_kimlik_sha256': A.sha_bayt(kanonik(kimlik))}


def _kos(arg: dict, ek: dict, durum: dict) -> dict:
    cikti = arg['cikti']
    tanim, kimlik = hazirla(arg, ek, durum)
    birimler = ayar.birimler(tanim['mimari'])
    kosu = K.calistir(cikti, birimler, kimlik, tanim['alici'], Y.birim_yurut,
                      functools.partial(A.baglam_kur, tanim), isci=arg.get('isci', 1), sessiz=True)
    if kosu['kalan']:
        return {'durum': 'KESILDI', **kosu}
    damga = K.damga_yaz(cikti, birimler)
    ozet = denetim_ozeti(cikti, birimler, damga, kimlik)
    (cikti / 'denetim' / 'DENETIM_OZETI.json').write_bytes(kanonik(ozet))
    return {'durum': 'TAMAM' if ozet['T5']['durum'] == 'yok' else 'T5', 'birim': damga['birim_sayisi'],
            'damga_kok_sha256': damga['kok_sha256'], 'T5_hata': (ozet['T5']['parite'] or {}).get('hata')}


def main(argv, ek: dict = None) -> int:
    try:
        arg = argumanlar(argv)
    except (ValueError, IndexError):                              # 20 m: argüman hatası sabit mesajla
        print(json.dumps({'durum': 'DUR', 'neden': 'arguman hatasi (kullanim: betik basligi)'}), flush=True)
        return 2
    durum = {}
    try:
        sonuc = sinirli(arg, durum, 'banka_kos', _kos, arg, ek, durum)
    except A.AcilisHatasi as e:
        print(json.dumps({'durum': 'DUR', 'neden': str(e)}), flush=True)
        return 3 if str(e).startswith('T2') else 4
    except K.BankaKosuHatasi as e:
        print(json.dumps({'durum': 'HATA', 'neden': str(e)}), flush=True)
        return 6
    print(json.dumps(sonuc), flush=True)
    return {'TAMAM': 0, 'KESILDI': 5, 'T5': T5_CIKIS}[sonuc['durum']]


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
