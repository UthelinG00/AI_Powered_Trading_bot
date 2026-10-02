"""v8 yayım doğrulayıcısı: veri ve git gerektirmeden hash zincirini denetler.

Kullanım (depo kökünden, kilitteki ortamla — DOGRULAMA.md): python dogrula.py
Denetimler:
  1. KILIT.json'daki 29 belge: defter dışındakiler bayt bayt aynı; defter (V8_DENEME_DEFTERI.csv) yalnız sona satır
     eklenerek büyümüş (kilitteki ve teknik ekteki defter bugünkünün satır sınırında biten baş kısmı).
  2. KILIT_TEKNIK_1: ilk kilide zincirli (ilk kilit sha256'sı), kod kimlikleri bugünkü kodla aynı; parametre, ortam ve
     sabitler ilk kilitle aynı.
  3. DONDURMA: kilit ve ek sha256'ları, kod kimlikleri (acilis.kimlikler) bugünkü kodla aynı.
  4. Kapı: HUKUM ve DENETIM, KOSU_OZETI'ndeki hash'lerle aynı.
  5. Kuru koşu ve banka: DENETIM_OZETI ↔ SONUC_DAMGA kökü (satırlardan yeniden hesap) ↔ IS_LISTESI; DENETIM_TAMAM.
  6. Hüküm: HUKUM_KIMLIK'teki girdi ve çıktı sha256'ları dosyalarla aynı.
Ortam sürümleri farklıysa 2–3'teki ortam alanı farklı çıkar (uyarı olarak basılır).
"""
import hashlib
import json
import sys
from pathlib import Path

KOK = Path(__file__).resolve().parent
AKTIF = KOK / 'AKTIF_MODEL'
V8 = AKTIF / 'v8'
sys.path.insert(0, str(V8))
C = AKTIF / 'ciktilar'

sonuc = []


def sha(p) -> str:
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def j(p):
    return json.loads(Path(p).read_bytes().decode('utf-8'))


def kontrol(ad: str, kosul: bool, ayrinti: str = ''):
    sonuc.append((ad, bool(kosul), ayrinti))


def main() -> int:
    import kilit
    from banka_kos import acilis as A
    from banka_kos.veri_denetim import kanonik

    ilk_yol = C / 'v8_kilit_20261001' / 'KILIT.json'
    ek_yol = C / 'v8_kilit_20261001' / 'KILIT_TEKNIK_1.json'
    ilk, ek = j(ilk_yol), j(ek_yol)

    # 1. belgeler
    for b, h in ilk['belgeler'].items():
        if b == kilit.DEFTER:
            continue
        kontrol(f'belge {b}', sha(AKTIF / b) == h)
    defter = (AKTIF / kilit.DEFTER).read_bytes()
    kontrol('defter: kilitteki defter baş kısım', kilit._bas_kismi(defter, ilk['belgeler'][kilit.DEFTER]))
    kontrol('defter: teknik ekteki defter baş kısım', kilit._bas_kismi(defter, ek['icerik']['belgeler'][kilit.DEFTER]))

    # 2. teknik ek
    kontrol('ek: ilk kilit sha256', ek['ilk_kilit_sha256'] == sha(ilk_yol))
    kontrol('ek: tür banka_oncesi, sıra 1', ek['tur'] == 'banka_oncesi' and ek['sira'] == 1)
    kontrol('ek: kod kimlikleri = bugünkü kod', ek['icerik']['kod'] == kilit.kod_kimlikleri())
    kontrol('ilk kilit: parametre kimlikleri', ilk['parametre'] == kilit.parametre_kimlikleri())
    kontrol('ilk kilit: sabitler', ilk['sabitler'] == kilit.sabitler())
    ortam = kilit.ortam()
    if ortam != ilk['ortam']:
        print(f"UYARI ortam farklı: kilit {ilk['ortam']} / bugün {ortam}")
    kontrol('ek: değişmezler ilk kilitle aynı', all(ek['icerik'][a] == ilk[a] for a in ('parametre', 'ortam', 'sabitler')))

    # 3. dondurma
    d_yol = C / 'v8_dondurma_20261002' / 'DONDURMA.json'
    d = j(d_yol)
    kontrol('dondurma: kilit sha256', d['kilit_sha256'] == sha(ilk_yol))
    kontrol('dondurma: teknik ek sha256', [e['sha256'] for e in d['teknik_ekler']] == [sha(ek_yol)])
    g = A.kimlikler()
    fark = [k for k in ('motor_sha256', 'banka_kos_sha256', 'veri_denetim_sha256', 'parametreler_sha256',
                        'har_sonuc_sha256', 'tohum_banka') if d[k] != g[k]]
    kontrol('dondurma: kod kimlikleri = bugünkü kod', not fark, str(fark))
    kontrol('dondurma: kapı hükmü sha256', d['carry_kapisi']['hukum_sha256'] == sha(C / 'v8_kapi_kosu_20261001/HUKUM.json'))
    kontrol('dondurma: kuru koşu özet sha256',
            d['d_dogrulama']['denetim_ozeti_sha256'] == sha(C / 'v8_kuru_20261002c/denetim/DENETIM_OZETI.json'))

    # 4. kapı
    oz = j(C / 'v8_kapi_kosu_20261001/KOSU_OZETI.json')
    kontrol('kapı: HUKUM/DENETIM = KOSU_OZETI hash', oz['hash'] == {
        'DENETIM.json': sha(C / 'v8_kapi_kosu_20261001/DENETIM.json'),
        'HUKUM.json': sha(C / 'v8_kapi_kosu_20261001/HUKUM.json')})

    # 5. kuru ve banka
    for ad in ('v8_kuru_20261002c', 'v8_banka_kosu_20261002'):
        k = C / ad
        den, dm, il = j(k / 'denetim/DENETIM_OZETI.json'), j(k / 'SONUC_DAMGA.json'), j(k / 'IS_LISTESI.json')
        kontrol(f'{ad}: damga kökü satırlardan', hashlib.sha256(kanonik(dm['birimler'])).hexdigest() == dm['kok_sha256'])
        kontrol(f'{ad}: özet ↔ damga ↔ iş listesi', den['damga_kok_sha256'] == dm['kok_sha256']
                and den['is_listesi_kimlik_sha256'] == hashlib.sha256(kanonik(il['kimlikler'])).hexdigest())
        kontrol(f'{ad}: T2/T3 yok, T4 tam, T5 yok', den['T2'] == 'yok' and den['T3'] == 'yok'
                and den['T4']['muhasebe_kapisi_gecen_birim'] == den['birim_sayisi'] and den['T5']['durum'] == 'yok')
    bk = C / 'v8_banka_kosu_20261002'
    dt = j(bk / 'DENETIM_TAMAM.json')
    kontrol('banka: DENETIM_TAMAM', dt['damga_kok_sha256'] == j(bk / 'SONUC_DAMGA.json')['kok_sha256']
            and dt['denetim_ozeti_sha256'] == sha(bk / 'denetim/DENETIM_OZETI.json'))
    il = j(bk / 'IS_LISTESI.json')['kimlikler']
    kontrol('banka: iş listesi → DONDURMA, VERI_DENETIM', il['dondurma_sha256'] == sha(d_yol)
            and il['veri_denetim_json_sha256'] == sha(bk / 'denetim/VERI_DENETIM.json'))

    # 6. hüküm
    hk = j(bk / 'hukum/HUKUM_KIMLIK.json')
    gr = hk['girdiler']
    kontrol('hüküm: çıktı sha256', hk['banka_sonuc_sha256'] == sha(bk / 'hukum/banka_sonuc.json')
            and hk['rapor_sha256'] == sha(bk / 'hukum/BANKA_RAPORU.md'))
    kontrol('hüküm: girdi sha256', gr['DONDURMA'] == sha(d_yol) and gr['DENETIM_TAMAM'] == sha(bk / 'DENETIM_TAMAM.json')
            and gr['VERI_DENETIM'] == sha(bk / 'denetim/VERI_DENETIM.json')
            and gr['TOPLAMA'] == sha(C / 'v8_kalibrasyon_20260929_01/TOPLAMA.json')
            and gr['damga_kok'] == dt['damga_kok_sha256'])
    acilis = bk / 'ACILIS_kanonik.json'
    kontrol('hüküm: ACILIS (kanonik) var ve sha256 bağlı', acilis.exists()
            and gr['ACILIS'] == sha(acilis) == il['acilis_sha256'])
    bs = j(bk / 'hukum/banka_sonuc.json')
    kontrol('hüküm türü: kimlik = sonuç dosyası = karar', hk['hukum_turu'] == bs['hukum_turu'] == bs['sonuc']['karar'],
            hk['hukum_turu'])
    ba = C / 'v8_banka_acilis_20261002'
    oz_i = j(ba / 'INDIRME_OZETI.json')
    kontrol('banka verisi: manifest ve liste sha256 = indirme özeti', (ba / 'BANKA_MANIFEST.jsonl').exists()
            and sha(ba / 'BANKA_MANIFEST.jsonl') == oz_i['manifest_sha256'] and sha(ba / 'liste.jsonl') == oz_i['liste_sha256'])

    for ad, ok, ayr in sonuc:
        print(f"{'GEÇTİ ' if ok else 'KALDI '} {ad}{(' — ' + ayr) if ayr else ''}")
    kalan = [s for s in sonuc if not s[1]]
    print(f"\n{len(sonuc) - len(kalan)}/{len(sonuc)} denetim geçti")
    return 1 if kalan else 0


if __name__ == '__main__':
    sys.exit(main())
