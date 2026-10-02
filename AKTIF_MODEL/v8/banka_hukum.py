"""Banka hüküm betiği (BANKA §2.4, BK-3; UYGULAMA_EK U3). Kör hükmün açılışı: denetim listesi tamamlanıp
DENETIM_TAMAM.json uzak depoya itildikten sonra kullanıcı kendi bilgisayarında koşar.

Kullanım (v8 içinden):
  python banka_hukum.py <banka çıktısı> <ACILIS.json> <DONDURMA.json> <DENETIM_TAMAM.json> <age kimlik dosyası>
                        --dt_commit <DENETIM_TAMAM.json'un itildiği commit, 40 hane>
                        [--rev1 <REV1 D günlük getiri JSON'u: {"seri": {gün_ms: getiri}}>]
Sıra (anahtar okunmadan önce bütün denetimler): T1 + kilit zinciri + dondurma commit'i (U2) → DENETIM_TAMAM: damga kökü
ve DENETIM_OZETI sha256'sı klasördekiyle aynı, ikisi DENETIM_TAMAM'daki commit'te bayt bayt aynı ve o commit uzakta →
iş listesi (IS_LISTESI.json) özetin bağladığı kimlik ve bu ACILIS/DONDURMA/VERI_DENETIM/dönemle aynı → TOPLAMA →
defter (N_hüküm = güncel defterden §3.3 sayımı; dondurmadaki defter baş kısmı) → T1–T5'ten biri varsa TEKNİK GEÇERSİZ
yazılır, sonuç çözülmez → yoksa çöz, hüküm, rapor → <çıktı>/hukum/{banka_sonuc.json, BANKA_RAPORU.md, HUKUM_KIMLIK.json}.
Ekrana yalnız hüküm türü ve hash'ler basılır; beklenmeyen hatada sabit mesaj ve izin sha256'sı (iz hiçbir yere
yazılmaz; hata ayıklama ayrı ve bilinçli bir adımdır). Çıkış: 0 hüküm yazıldı; 4 T1/kimlik/denetim; 6 hata.
"""
import json
import sys
import traceback
from pathlib import Path

V8 = Path(__file__).resolve().parent
if str(V8) not in sys.path:
    sys.path.insert(0, str(V8))

from banka_kos import acilis as A  # noqa: E402
from banka_kos import ayar  # noqa: E402
from banka_kos import hukum as H  # noqa: E402
from banka_kos import kosucu as K  # noqa: E402
from banka_kos import rapor, rapor_md  # noqa: E402
from banka_kos.veri_denetim import kanonik  # noqa: E402

AKTIF = V8.parent
TOPLAMA = AKTIF / 'ciktilar' / 'v8_kalibrasyon_20260929_01' / 'TOPLAMA.json'
T_YOK = ('T2', 'T3')


def _oku(yol) -> tuple:
    b = Path(yol).read_bytes()
    return json.loads(b.decode('utf-8')), A.sha_bayt(b)


def denetim_tamam(cikti: Path, dt: dict, git: bool = True) -> dict:
    """DENETIM_TAMAM.json ↔ klasör (§2.4): damga kökü ve DENETIM_OZETI sha256'sı aynı; git açıksa SONUC_DAMGA ve
    DENETIM_OZETI, DENETIM_TAMAM'daki commit'te bayt bayt aynı ve commit uzak depoda (yayımlanma kanıtı).
    teknik: T2/T3 'yok' değil, T4 muhasebe kapısını geçen birim ≠ birim sayısı, T5 'yok' değil."""
    damga_yol, oz_yol = cikti / 'SONUC_DAMGA.json', cikti / 'denetim' / 'DENETIM_OZETI.json'
    damga, _ = _oku(damga_yol)
    oz_b = oz_yol.read_bytes()
    oz = json.loads(oz_b)
    if dt.get('damga_kok_sha256') != damga['kok_sha256'] or dt.get('denetim_ozeti_sha256') != A.sha_bayt(oz_b):
        raise A.AcilisHatasi("DENETIM_TAMAM.json klasordeki damga ya da denetim ozetiyle ayni degil")
    if git:
        import kilit
        try:
            for y in (damga_yol, oz_yol):
                kilit.git_denetimi(y, dt.get('commit'))
        except kilit.KilitHatasi as e:
            raise A.AcilisHatasi(f"DENETIM_TAMAM commit'i dogrulanmadi: {e}") from None
    teknik = [t for t in T_YOK if oz.get(t) != 'yok']
    t4 = (oz.get('T4') or {}).get('muhasebe_kapisi_gecen_birim')
    if t4 is None or t4 != oz.get('birim_sayisi') or oz.get('birim_sayisi') != damga.get('birim_sayisi'):
        teknik.append('T4')
    if (oz.get('T5') or {}).get('durum') != 'yok':
        teknik.append('T5')
    return {'damga': damga, 'ozet': oz, 'teknik': teknik}


def is_listesi_bagi(cikti: Path, ozet: dict, dondurma: dict, d_sha: str, a_sha: str, vd: dict, vd_sha: str) -> dict:
    """IS_LISTESI.json'un kimlikleri DENETIM_OZETI'nin bağladığı kimlik; banka kipi, bu DONDURMA/ACILIS/VERI_DENETIM,
    VERI_DENETIM dönemi, DONDURMA mimarisi/tohumu/alıcısı, T1 kimlikleri ve taban birimler (Codex T30-4)."""
    il, _ = _oku(cikti / K.IS_LISTESI)
    kim = il.get('kimlikler') or {}
    if A.sha_bayt(kanonik(kim)) != ozet.get('is_listesi_kimlik_sha256'):
        raise A.AcilisHatasi("IS_LISTESI denetim ozetinin bagladigi kimlik degil")
    beklenen = {'mod': 'banka', 'mimari': dondurma['mimari'], 'dondurma_sha256': d_sha, 'acilis_sha256': a_sha,
                'veri_denetim_json_sha256': vd_sha, 'donem': vd['donem'], 'tohum_banka': dondurma['tohum_banka'],
                'veri_kimligi': vd.get('veri_kimligi')}
    fark = [k for k, v in beklenen.items() if kim.get(k) != v]
    if il.get('alici') != dondurma['sifreleme_acik_anahtar']:
        fark.append('alici')
    if A.t1_denetimi(dondurma, kim.get('kimlikler') or {}):
        fark.append('kimlikler')
    if kanonik(il.get('birimler')) != kanonik(ayar.birimler(dondurma['mimari'])):
        fark.append('birimler')
    if fark:
        raise A.AcilisHatasi(f"IS_LISTESI bu hukmun girdileriyle ayni degil: {fark}")
    return kim


def n_hukum(dondurma: dict) -> int:
    """§3.3: N_hüküm = güncel defter N'si (her deneme bir kez; teknik ek satırları dahil) + dondurmada sayılan, defterde
    olmayan D doğrulama (UYGULAMA_EK rev 3, karar B). Dondurmadaki defter bugünkünün satır sınırında biten baş kısmı
    olmalı (21 f); N_hüküm ≥ N_dondurma."""
    import kilit
    from dondur import defter_ozeti
    b = (AKTIF / kilit.DEFTER).read_bytes()
    if not kilit._bas_kismi(b, dondurma['deneme_defteri']['sha256']):
        raise A.AcilisHatasi("dondurmadaki deneme defteri bugunkunun bas kismi degil")
    n = defter_ozeti()['N_defter'] + int(dondurma['deneme_defteri'].get('d_dogrulama_sayimi', 0))
    if n < dondurma['deneme_defteri']['N_dondurma']:
        raise A.AcilisHatasi("N_hukum N_dondurma'dan kucuk")
    return n


def baglam_kur(dondurma: dict, acilis: dict, vd: dict, N: int) -> H.HukumBaglami:
    from kalibrasyon.duzey1_esik import Kurallar
    k = dict(dondurma['kalibrasyon']['kurallar'])
    dm = vd['donem']
    return H.HukumBaglami(
        mimari=dondurma['mimari'], t0_z1_ms=dm['t0_z1_ms'],
        gorulmus_gunler=tuple(sorted(A.gun_ms(g) for g in acilis['gorulmus_gunler'])),
        tohum_banka=dondurma['tohum_banka'], kurallar=Kurallar(**k), N_hukum=N,
        birincil_son_ms=dm['birincil_son_ms'], z2_bas_ms=dm['z2_bas_ms'], z2_son_ms=dm['z2_son_ms'],
        d_bas_ms=dm['d_bas_ms'], z1_dilim_sinir=tuple(dm['z1_dilim_sinir']), d_bit_ms=dm['d_bit_ms'])


def hukum_ver(cikti, acilis_yolu, dondurma_yolu, dt_yolu, kimlik_yolu, rev1_yolu=None, ek: dict = None,
              dt_commit: str = None) -> dict:
    cikti = Path(cikti)
    git = (ek or {}).get('kilit_denetimi', True)
    k = cikti / 'hukum'
    if k.exists():
        raise A.AcilisHatasi("hukum klasoru zaten var; hukum bir kez yazilir")
    tanim, guncel, meta = A.hazirla('banka', cikti, acilis_yolu, dondurma_yolu, ek=ek)     # T1 + ACILIS + U2
    dondurma, d_sha = _oku(dondurma_yolu)
    acilis, a_sha = _oku(acilis_yolu)
    dt, dt_sha = _oku(dt_yolu)
    vd, vd_sha = _oku(cikti / 'denetim' / 'VERI_DENETIM.json')
    if vd.get('dondurma_sha256') != d_sha or vd['denetim']['karar']['T2']:
        raise A.AcilisHatasi("VERI_DENETIM bu dondurmayla uretilmedi ya da T2")
    den = denetim_tamam(cikti, dt, git=git)
    if git:                                             # DENETIM_TAMAM.json'un kendisi de uzakta (Codex T31-3)
        import kilit
        try:
            kilit.git_denetimi(dt_yolu, dt_commit)
        except kilit.KilitHatasi as e:
            raise A.AcilisHatasi(f"DENETIM_TAMAM.json commit'i dogrulanmadi (--dt_commit): {e}") from None
    is_listesi_bagi(cikti, den['ozet'], dondurma, d_sha, a_sha, vd, vd_sha)
    toplama, t_sha = _oku(TOPLAMA)
    if t_sha != dondurma['kalibrasyon']['toplama_sha256']:
        raise A.AcilisHatasi("TOPLAMA.json dondurmadakinden farkli")
    N = n_hukum(dondurma)
    hb = baglam_kur(dondurma, acilis, vd, N)
    hashler = {'KILIT': dondurma['kilit_sha256'], 'DONDURMA': d_sha, 'DENETIM_TAMAM': dt_sha,
               'SONUC_DAMGA kok': den['damga']['kok_sha256'], 'VERI_DENETIM': vd_sha}
    girdiler = {'DONDURMA': d_sha, 'ACILIS': a_sha, 'DENETIM_TAMAM': dt_sha, 'VERI_DENETIM': vd_sha, 'TOPLAMA': t_sha,
                'damga_kok': den['damga']['kok_sha256'], 'N_hukum': N}
    rev1 = None
    if den['teknik']:                                   # §2.4: teknik geçersizlikte sonuç çözülmez, hüküm hesaplanmaz
        tur = 'TEKNİK GEÇERSİZ'
        sb = kanonik({'hukum_turu': tur, 'teknik': den['teknik']})
        md = (f"# Banka hükmü: {tur}\n\nDENETIM_OZETI'nde teknik geçersizlik: {', '.join(den['teknik'])}. Sonuçlar "
              f"çözülmedi; ekonomik hüküm hesaplanmadı (§2.4; teknik yeniden koşu §3.7 21 g).\n\n"
              + ''.join(f"- {a}: `{h}`\n" for a, h in hashler.items()))
    else:
        kimlik = Path(kimlik_yolu).read_text(encoding='ascii').strip().splitlines()
        kimlik = next(s for s in kimlik if s.startswith('AGE-SECRET-KEY-'))
        birimler = H.birimleri_coz(cikti, kimlik, beklenen_kok=dt['damga_kok_sha256'])
        if rev1_yolu:
            rv, rv_sha = _oku(rev1_yolu)
            rev1 = {'seri': rv['seri'], 'dosya': Path(rev1_yolu).name, 'sha256': rv_sha}
        sonuc = H.hukum(birimler, hb)
        satir = rapor.rapor_satirlari(birimler, hb, rev1=rev1)
        tur = sonuc['karar']
        r1 = toplama['duzey1']['rapor']
        md = rapor_md.banka_raporu(sonuc, satir, rapor_md.birincil_metrikler(birimler, hb), {
            'hukum_turu': tur, 'mimari': hb.mimari, 'b2_turu': 'B' if hb.kurallar.b2_bagli else 'R',
            'sigma_kaynak': dondurma['dsr']['kaynak'], 'N_hukum': hb.N_hukum, 'hashler': hashler,
            'stres_secenegi': {'secenek': dondurma['stres_secenegi'], 'hash': d_sha},
            'veri_denetimi': vd['denetim'],
            'kalibrasyon': {'P(KABUL|SR) B7siz': r1.get('p_kabul_A_ort'), 'duzey2a': toplama['duzey2']['duzey2a']},
            'teknik': {'T': {t: den['ozet'].get(t) for t in ('T1', 'T2', 'T3', 'T4')}, 'T5': den['ozet'].get('T5'),
                       'teknik_ek': len(dondurma.get('teknik_ekler') or [])}})
        sb = kanonik({'hukum_turu': tur, 'sonuc': sonuc, 'satirlar': satir})
    k.mkdir(parents=True, exist_ok=False)                       # hüküm bir kez yazılır
    (k / 'banka_sonuc.json').write_bytes(sb)
    (k / 'BANKA_RAPORU.md').write_bytes(md.encode('utf-8'))   # bayt: hash platformdan bağımsız (CRLF yok)
    kim = {'hukum_turu': tur, 'banka_sonuc_sha256': A.sha_bayt(sb), 'rapor_sha256': A.sha_bayt(md.encode('utf-8')),
           'girdiler': dict(girdiler, rev1=rev1 and rev1['sha256']), 'kimlikler': guncel}
    (k / 'HUKUM_KIMLIK.json').write_bytes(kanonik(kim))
    return kim


def main(argv) -> int:
    if len(argv) < 5:
        print(json.dumps({'durum': 'DUR', 'neden': 'arguman hatasi (kullanim: betik basligi)'}), flush=True)
        return 2
    try:
        rev1 = argv[argv.index('--rev1') + 1] if '--rev1' in argv else None
        dtc = argv[argv.index('--dt_commit') + 1] if '--dt_commit' in argv else None
        kim = hukum_ver(*argv[:5], rev1_yolu=rev1, dt_commit=dtc)
    except A.AcilisHatasi as e:                                 # kendi sabit metinlerimiz (coin adı/metrik taşımaz)
        print(json.dumps({'durum': 'DUR', 'neden': str(e)}, ensure_ascii=False), flush=True)
        return 4
    except Exception:                                           # BK-11 sınırı: ham istisna basılmaz
        iz = traceback.format_exc().encode('utf-8')           # içerik taşıyabilir: diske ve ekrana yazılmaz
        print(json.dumps({'durum': 'HATA', 'iz_sha256': A.sha_bayt(iz)}), flush=True)
        return 6
    print(json.dumps({'hukum_turu': kim['hukum_turu'], 'banka_sonuc_sha256': kim['banka_sonuc_sha256'],
                      'rapor_sha256': kim['rapor_sha256']}, ensure_ascii=False), flush=True)
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
