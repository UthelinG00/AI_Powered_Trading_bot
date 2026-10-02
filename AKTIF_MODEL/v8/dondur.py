"""DONDURMA.json üretimi (BANKA §1.4; 7.01; UYGULAMA_EK U1). Kilit zinciri uzak commit'lerle doğrulanır (U2 ile aynı
denetim: acilis.kilit_tam); kapı çıktısı ve kuru koşu içerikleriyle denetlenir. DONDURMA.json zaten varsa üretilmez.

Kullanım (v8 içinden):
  python dondur.py <cikti> --kilit <KILIT.json> --kilit_commit <40 hane> [--ek_commit <40 hane> ...]
                   --kapi <kapı çıktısı> --kuru <kuru koşu çıktısı> --alici <age açık anahtarı> --onay dondur
§1.4 `git_commit`: dosya kendi commit'ini taşıyamaz; DONDURMA.json commit edilip itildikten sonra o commit ACILIS'e
(`dondurma_commit`) yazılır ve banka girişi `kilit.git_denetimi` ile doğrular. Burada `git_commit_ust` = üretim anındaki
HEAD (dondurma commit'inin atası).
"""
import csv
import json
import sys
import time
from pathlib import Path

V8 = Path(__file__).resolve().parent
if str(V8) not in sys.path:
    sys.path.insert(0, str(V8))

from banka_kos import acilis as A  # noqa: E402
from banka_kos import ayar  # noqa: E402
from banka_kos import kosucu as K  # noqa: E402
from banka_kos.veri_denetim import kanonik  # noqa: E402

AKTIF = V8.parent
KAL = AKTIF / 'ciktilar' / 'v8_kalibrasyon_20260929_01'
HAR = AKTIF / 'ciktilar' / 'v8_har_secimi_20260929_01'
ONKAYIT = AKTIF / 'ciktilar' / 'v8_asama4_20260927_01' / 'BANKA_ONKAYIT_TASLAK.md'
UYGULAMA_EK = AKTIF / 'ciktilar' / 'v8_dondurma_hazirlik_20261001' / 'UYGULAMA_EK.md'
B7_KUANTIL = 0.95
D_DOGRULAMA_SAYIMI = 1      # §3.3 'D doğrulama +1'; kullanıcı kararı B (2 Ekim): defterde değil, dondurmada sayılır
V_KAPI = ('V1', 'V2', 'V3', 'V4a', 'V4b', 'V5', 'V6')


class DondurmaHatasi(RuntimeError):
    pass


def _oku(yol) -> tuple:
    b = Path(yol).read_bytes()
    return json.loads(b.decode('utf-8')), A.sha_bayt(b)


def _goreli(yol: Path) -> str:
    return Path(yol).resolve().relative_to(AKTIF.resolve()).as_posix()


def defter_ozeti(aktif: Path = AKTIF) -> dict:
    import kilit
    from kalibrasyon.duzey1_karar import n_v8
    yol = aktif / kilit.DEFTER
    with open(yol, encoding='utf-8', newline='') as f:
        satir = len(list(csv.DictReader(f)))
    nv = n_v8(yol)
    return {'sha256': A.sha_bayt(yol.read_bytes()), 'satir': satir, 'N_v8': nv, 'N_defter': 159 + nv}


def kapi_kaniti(kapi: Path, kilit_icerik: dict, kilit_commit: str) -> dict:
    """Kapı: HUKUM ve DENETIM, KOSU_OZETI'ndeki hash'lerle aynı; V1–V6 geçti, ihlal yok; koşunun kod/parametre
    kimlikleri ve kilit commit'i kilitle aynı; karar A ya da B."""
    kapi = Path(kapi)
    oz, oz_sha = _oku(kapi / 'KOSU_OZETI.json')
    hukum, h_sha = _oku(kapi / 'HUKUM.json')
    den, den_sha = _oku(kapi / 'DENETIM.json')
    if oz.get('hash') != {'DENETIM.json': den_sha, 'HUKUM.json': h_sha}:
        raise DondurmaHatasi("kapi HUKUM/DENETIM kosu ozetindeki hash'lerle ayni degil")
    if any((den.get('V') or {}).get(v) is not True for v in V_KAPI) or den.get('esas_ihlal') or den.get('teknik_ihlal'):
        raise DondurmaHatasi("kapi denetimi temiz degil (V1-V6 ya da ihlal)")
    km = oz.get('kimlikler') or {}
    if (km.get('kod') != kilit_icerik['kod'] or km.get('parametre') != kilit_icerik['parametre']
            or (km.get('kilit_git') or {}).get('commit') != kilit_commit):
        raise DondurmaHatasi("kapi kosusunun kimlikleri kilitle ayni degil")
    if hukum.get('karar') not in ('A', 'B'):
        raise DondurmaHatasi("kapi hukmunde karar A ya da B degil")
    return {'karar': hukum['karar'], 'hukum_sha256': h_sha, 'denetim_sha256': den_sha, 'kosu_ozeti_sha256': oz_sha,
            'rapor_sha256': A.sha_bayt((kapi / 'KAPI_RAPORU.md').read_bytes())}


def kuru_kaniti(kuru: Path, mimari: str, guncel: dict) -> dict:
    """Kuru koşu: denetim özeti temiz (T1 kuru, T2/T3 yok, T4 muhasebe kapısı bütün birimlerde, T5 yok); damga kökü
    satırlardan yeniden hesaplanır ve özetle aynı; iş listesi özetin bağladığı kimlik, kuru kipte, kapının
    mimarisinde, bugünkü kod kimlikleriyle koşulmuş ve taban birimleri eksiksiz."""
    kuru = Path(kuru)
    den, den_sha = _oku(kuru / 'denetim' / 'DENETIM_OZETI.json')
    damga, damga_sha = _oku(kuru / 'SONUC_DAMGA.json')
    il, il_sha = _oku(kuru / K.IS_LISTESI)
    t4 = (den.get('T4') or {}).get('muhasebe_kapisi_gecen_birim')
    if (not str(den.get('T1', '')).startswith('kuru') or den.get('T2') != 'yok' or den.get('T3') != 'yok'
            or (den.get('T5') or {}).get('durum') != 'yok' or t4 is None or t4 != den.get('birim_sayisi')):
        raise DondurmaHatasi("kuru kosu denetim ozeti temiz degil")
    satirlar = damga.get('birimler') or []
    if (A.sha_bayt(kanonik(satirlar)) != damga.get('kok_sha256') or damga.get('birim_sayisi') != len(satirlar)
            or den.get('damga_kok_sha256') != damga['kok_sha256'] or den.get('birim_sayisi') != len(satirlar)):
        raise DondurmaHatasi("kuru kosu damgasi kendi kokuyle ya da ozetle tutarsiz")
    kim = il.get('kimlikler') or {}
    if A.sha_bayt(kanonik(kim)) != den.get('is_listesi_kimlik_sha256'):
        raise DondurmaHatasi("kuru kosu is listesi denetim ozetinin bagladigi kimlik degil")
    if kim.get('mod') != 'kuru' or kim.get('mimari') != mimari:
        raise DondurmaHatasi("kuru kosu kipi ya da mimarisi kapi kararindan farkli")
    if kim.get('kimlikler') != guncel:
        raise DondurmaHatasi("kuru kosu bugunku kod kimlikleriyle kosulmamis (yeniden kos)")
    taban = ayar.birimler(mimari)
    if kanonik(il.get('birimler')) != kanonik(taban):
        raise DondurmaHatasi("kuru kosu is listesi taban birimlerden farkli")
    adlar = {s[0] for s in satirlar}
    if any(K.birim_adi(b) not in adlar for b in taban):
        raise DondurmaHatasi("kuru kosu damgasinda taban birim eksik")
    return {'denetim_ozeti_sha256': den_sha, 'sonuc_damga_sha256': damga_sha, 'damga_kok_sha256': damga['kok_sha256'],
            'is_listesi_sha256': il_sha, 'birim_sayisi': len(satirlar)}


def icerik(kilit_yolu, kilit_commit: str, ek_commitler, kapi: Path, kuru: Path, alici: str, git: bool = True) -> dict:
    import kilit
    from banka.olcutler import sr0
    kilit_yolu = Path(kilit_yolu)
    ek_commitler = list(ek_commitler or ())
    try:
        kt = A.kilit_tam(kilit_yolu, kilit_commit, ek_commitler, ('kapi', 'banka_oncesi'), git=git)   # dondurma bankadan önce
    except kilit.KilitHatasi as e:
        raise DondurmaHatasi(f"kilit zinciri dogrulanmadi: {e}") from None
    if len(ek_commitler) != len(kt['teknik_ekler']):
        raise DondurmaHatasi("her teknik ek icin commit bildirilmeli")
    ekler = [dict(e, commit=c) for e, c in zip(kt['teknik_ekler'], ek_commitler)]
    k = A.kimlikler()
    kc = kapi_kaniti(kapi, kt['zincir'], kilit_commit)
    kd = kuru_kaniti(kuru, kc['karar'], k)
    toplama, t_sha = _oku(KAL / 'TOPLAMA.json')
    r = toplama['duzey1']['rapor']
    kur = r['kurallar']
    defter = defter_ozeti()
    if kur['N'] != defter['N_defter'] - len(ekler):
        raise DondurmaHatasi("defter N'si kalibrasyon N'siyle ve teknik eklerle tutarsiz")
    defter = dict(defter, d_dogrulama_sayimi=D_DOGRULAMA_SAYIMI, N_dondurma=defter['N_defter'] + D_DOGRULAMA_SAYIMI)
    if not alici.startswith('age1'):
        raise DondurmaHatasi("alici age acik anahtari degil")
    from banka_kos.age import alici_coz
    alici_coz(alici)
    har, har_sha = _oku(HAR / 'sonuc.json')
    return {
        'mimari': kc['karar'], 'kilit_yolu': _goreli(kilit_yolu), 'kilit_sha256': A.sha_bayt(kilit_yolu.read_bytes()),
        'kilit_commit': kilit_commit, 'teknik_ekler': ekler, **k, 'v1_guncel': kt['v1_guncel'],
        'v1_kilit': (kt['zincir'].get('onkosul') or {}).get('v1'),
        'git_commit_ust': kilit._git()['head'] if git else None,
        'tahminci': {'secim': 'HAR', 'sonuc_sha256': har_sha, 'rapor_sha256': A.sha_bayt((HAR / 'RAPOR.md').read_bytes()),
                     'dondurulan': har['dondurulan']},
        'carry_kapisi': kc,
        'd_dogrulama': kd,
        'kalibrasyon': {'toplama_sha256': t_sha, 'kod_sha256': kt['zincir']['kod']['kalibrasyon'], 'kurallar': kur,
                        'b7_kuantil': B7_KUANTIL},
        'dsr': {'sigma_sr_bag': r['sigma_sr']['sigma_sr_bag'], 'kaynak': r['sigma_sr']['kaynak'],
                'b2_turu': 'B' if kur['b2_bagli'] else 'R', 'd': kur['d'], 'N_kilit': kur['N'],
                'SR0_kilit': sr0(kur['N'], kur['sigma_sr'])},
        'deneme_defteri': defter, 'onkayit_sha256': A.sha_bayt(ONKAYIT.read_bytes()),
        'uygulama_ek_sha256': A.sha_bayt(UYGULAMA_EK.read_bytes()),
        'sifreleme_acik_anahtar': alici, 'stres_secenegi': 'i', 'kullanici_onayi': 'dondur',
        'utc': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())}


def main(argv) -> int:
    def al(ad, coklu=False):
        if coklu:
            return [argv[i + 1] for i, x in enumerate(argv) if x == ad]
        return argv[argv.index(ad) + 1] if ad in argv else None
    if len(argv) < 1 or al('--onay') != 'dondur':
        raise SystemExit(__doc__ + "\n(--onay dondur zorunlu: kullanicinin 'dondur' onayi)")
    cikti = Path(argv[0])
    yol = cikti / 'DONDURMA.json'
    if yol.exists():
        raise SystemExit("DONDURMA.json zaten var; dondurma bir kez yapilir")
    d = icerik(al('--kilit'), al('--kilit_commit'), al('--ek_commit', True), Path(al('--kapi')), Path(al('--kuru')),
               al('--alici'))
    cikti.mkdir(parents=True, exist_ok=True)
    yol.write_bytes(json.dumps(d, indent=1, sort_keys=True, ensure_ascii=True).encode('ascii'))   # CRLF yok
    print(json.dumps({'DONDURMA_sha256': A.sha_bayt(yol.read_bytes()), 'mimari': d['mimari'],
                      'tohum_banka': d['tohum_banka']}), flush=True)
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
