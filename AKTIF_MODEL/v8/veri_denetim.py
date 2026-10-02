"""Koşu öncesi veri denetimi, T2 (BANKA §2.3, §2.5; K2-07; §3.7 netleştirme 17 a, g; 19; 20 c, f, i, j). `banka_kos.py`'den
önce çalışır; kararı `<cikti>/denetim/VERI_DENETIM.json`'a (kanonik) yazar. T2 varsa çıkış kodu 3; koşu başlamaz.
`banka_kos.py` aynı hesabı (`denetim_hesapla`) yeniden yapar ve dosyayla birebir karşılaştırır (20 g).

Kullanım (v8 içinden):
  python veri_denetim.py banka <cikti> <ACILIS.json> <DONDURMA.json>
  python veri_denetim.py kuru  <cikti> <A|B> [--alici <age açık anahtarı>] [--anonim-anahtar <yol>] [--tohum <n>]
Ekrana ve dosyaya yalnız sayılar ve hash'ler yazılır (coin adı ve performans yok). Beklenmeyen hata: iz alıcıya şifreli
(`sonuc/hata/`), ekrana sabit mesaj + düz izin sha256'sı (20 f). Çıkış: 0 tamam; 3 T2; 4 T1/açılış; 6 hata.
"""
import json
import sys
from pathlib import Path

V8 = Path(__file__).resolve().parent
if str(V8) not in sys.path:
    sys.path.insert(0, str(V8))

from banka_kos import acilis as A  # noqa: E402
from banka_kos import veri_denetim as VD  # noqa: E402

T2_CIKIS, T1_CIKIS, HATA_CIKIS = 3, 4, 6


def argumanlar(argv) -> dict:
    if len(argv) < 3 or argv[0] not in ('banka', 'kuru'):
        raise SystemExit(__doc__)
    a = {'mod': argv[0], 'cikti': Path(argv[1])}
    if argv[0] == 'banka':
        if len(argv) < 4:
            raise SystemExit(__doc__)
        a.update(acilis_yolu=argv[2], dondurma_yolu=argv[3])
    else:
        a['mimari'] = argv[2]
    for bayrak, ad, tur in (('--alici', 'alici', str), ('--isci', 'isci', int), ('--anonim-anahtar', 'anonim_anahtar', str),
                            ('--tohum', 'tohum', int)):
        if bayrak in argv:
            a[ad] = tur(argv[argv.index(bayrak) + 1])
    return a


def tanim_hazirla(arg: dict, ek: dict = None) -> tuple:
    return A.hazirla(arg['mod'], arg['cikti'], arg.get('acilis_yolu'), arg.get('dondurma_yolu'), arg.get('mimari'),
                     arg.get('alici'), ek, arg.get('anonim_anahtar'), arg.get('tohum'))


def denetim_hesapla(tanim: dict, guncel: dict, meta: dict) -> tuple:
    """(VERI_DENETIM sözlüğü, veri | None, yükleme raporu | None, filtre raporu | None). T2 (1) yükleyiciden önce."""
    from motor.tipler import Parametreler
    sonuc = {'mod': tanim['mod'], 'mimari': tanim['mimari'], 'kimlikler': guncel, **meta}
    d_eks = A.d_eksik(tanim)
    if d_eks:                                                  # 20 l (3): D paketinde kayıp dosya
        sonuc['denetim'] = {'karar': {'T2': True, 'nedenler': ['D paketinde manifestte olup diskte olmayan dosya']},
                            'd_eksik_dosya': d_eks}
        return sonuc, None, None, None
    if tanim['mod'] == 'banka':
        from banka_kos.veri import MANIFEST_ADI, eksik_dosyalar
        kok = Path(tanim['acilis']['banka_kok'])
        satir = [json.loads(s) for s in (kok / MANIFEST_ADI).read_text(encoding='utf-8').splitlines() if s.strip()]
        cs = VD.checksum_denetimi(satir)
        if not cs['onarilamayan']:
            bag = {}
            for r in satir:
                if r['durum'] == 'TAMAM':
                    bag.setdefault(r['yol'], r['sha256'])
            cs['eksik_dosya'] = len(eksik_dosyalar(kok, bag, A.veri_adaylari(tanim['acilis'])))
            cs['onarilamayan'] += cs['eksik_dosya']
        if cs['onarilamayan']:
            sonuc['denetim'] = {'karar': {'T2': True, 'nedenler': ['onarilamayan CHECKSUM hatasi']}, 'checksum': cs}
            return sonuc, None, None, None
    veri, r = A.veri_yukle(tanim)
    dm = A.donem_kur(tanim, veri)
    _, frapor = A.filtreler_kur(veri.adaylar, Path(tanim.get('filtre_klasoru') or A.FILTRE_KLASORU))
    k = A.k_coinleri(tanim, veri)
    surek = tanim['acilis']['sureklilik_sorunu'] if tanim['mod'] == 'banka' else 0
    sonuc.update(veri_kimligi=r['veri_kimligi'], dosya_sayisi=r['dosya_sayisi'], aday=len(veri.adaylar),
                 yukleyici_ozeti=r['ozet'], donem=dm.json(), filtre=frapor,
                 denetim=VD.denetle(veri, r['manifest'], k, dm.t0_z1_ms, dm.birincil_son_ms, dm.z2_son_ms,
                                    Parametreler(), frapor['filtresiz_sembol'], surek, r['eylul_funding']))
    return sonuc, veri, r, frapor


def sinirli(arg: dict, durum: dict, etiket: str, fn, *a):
    """20 f: AcilisHatasi (sabit metin) dışındaki her istisna mühürlenir; dışarı sabit mesaj + düz iz sha256'sı."""
    import hashlib
    import traceback
    from banka_kos import kosucu as K
    try:
        return fn(*a)
    except (A.AcilisHatasi, K.BankaKosuHatasi):
        raise
    except Exception:
        if durum.get('alici'):
            h = K._muhurle(arg['cikti'], durum['alici'], etiket)
        else:
            h = hashlib.sha256(traceback.format_exc().encode('utf-8')).hexdigest() + ' (alici yok; iz yazilmadi)'
    raise K.BankaKosuHatasi(f"{etiket} hatasi (ayrinti sonuc/hata/{etiket}.age; duz sha256 {h})") from None


def _calis(arg: dict, ek: dict, durum: dict) -> tuple:
    tanim, guncel, meta = tanim_hazirla(arg, ek)
    durum['alici'] = tanim['alici']
    sonuc = denetim_hesapla(tanim, guncel, meta)[0]
    yol = arg['cikti'] / 'denetim' / 'VERI_DENETIM.json'           # yazım da sınırda (20 l (2))
    yol.parent.mkdir(parents=True, exist_ok=True)
    return sonuc, VD.yaz(sonuc, yol)


def main(argv, ek: dict = None) -> int:
    from banka_kos import kosucu as K
    try:
        arg = argumanlar(argv)
    except (ValueError, IndexError):                              # 20 m: argüman hatası sabit mesajla
        print(json.dumps({'durum': 'DUR', 'neden': 'arguman hatasi (kullanim: betik basligi)'}), flush=True)
        return 2
    durum = {}
    try:
        sonuc, h = sinirli(arg, durum, 'veri_denetim', _calis, arg, ek, durum)
    except A.AcilisHatasi as e:
        print(json.dumps({'durum': 'DUR', 'neden': str(e)}), flush=True)
        return T1_CIKIS
    except K.BankaKosuHatasi as e:
        print(json.dumps({'durum': 'HATA', 'neden': str(e)}), flush=True)
        return HATA_CIKIS
    t2 = sonuc['denetim']['karar']['T2']
    print(json.dumps({'VERI_DENETIM_sha256': h, 'T2': t2, 'dosya_sayisi': sonuc.get('dosya_sayisi'),
                      'aday': sonuc.get('aday')}), flush=True)
    return T2_CIKIS if t2 else 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
