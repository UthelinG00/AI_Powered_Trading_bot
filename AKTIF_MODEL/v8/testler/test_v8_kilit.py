"""On-kayit kilidi (4.03; CARRY Ss2 Adim 4): gecici bir AKTIF_MODEL agacinda uretim, dogrulama, degisiklik yakalama,
tek atis ve defter satiri. Veri kimligi yuklenmez (yalniz manifest ve evren hash'i).
Kanit zinciri (Codex T17-a): sentetik ama ureticiyle ayni bicimde (kanit.py, duman_kanit.py) duman/bitis/toplama/esdegerlik
kanitlari; HAR, parametre, kod ya da motor degisince ve bayat/baska kanitla kilit reddedilir."""
import hashlib
import importlib.util
import json
import shutil
import sys as _sys
import tempfile
import unittest
from pathlib import Path as _Path

V8_DIR = _Path(__file__).resolve().parent.parent
if str(V8_DIR) not in _sys.path:
    _sys.path.insert(1, str(V8_DIR))

import kilit  # noqa: E402

KAL_DIR = V8_DIR.parent / 'ciktilar' / 'v8_kalibrasyon_20260929_01'


def _yukle(ad: str):
    spec = importlib.util.spec_from_file_location(f'kal_{ad}', KAL_DIR / f'{ad}.py')
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


kanit = _yukle('kanit')
duman_kanit = _yukle('duman_kanit')
topla = _yukle('topla')

BELGELER = ('ciktilar/x/A.md', 'ciktilar/x/B.json', kilit.DEFTER)


class KilitTest(unittest.TestCase):
    def setUp(self):
        self.aktif = _Path(tempfile.mkdtemp(prefix='kilit_'))
        for b, icerik in zip(BELGELER, ('# A\n', '{"b": 1}\n', None)):
            (self.aktif / b).parent.mkdir(parents=True, exist_ok=True)
            if icerik is not None:
                (self.aktif / b).write_text(icerik, encoding='utf-8')
        (self.aktif / kilit.DEFTER).write_text(
            'kayit_id,asama,tarih_utc,tur,kapsam,aile,varyant_sayisi,aciklama\n'
            'A4-carry-kapisi,Adim 4,2026-10-02,kapi,D,kesitsel funding tasima,1,test\n', encoding='utf-8')
        self.cikti = self.aktif / 'kilit'

    def tearDown(self):
        shutil.rmtree(self.aktif, ignore_errors=True)

    def test_uret_ve_dogrula(self):
        k = kilit.uret(self.cikti, self.aktif, BELGELER, veri_yukle=False, git=False, onkosul=False)
        self.assertEqual(set(k['belgeler']), set(BELGELER))
        self.assertIn('pandas', k['ortam'])
        self.assertEqual(set(k['kod']), {'motor', 'kapi', 'kalibrasyon', 'adaptor', 'kilit'})
        self.assertIn('kapi', k['parametre'])
        self.assertEqual(k['sabitler']['kapi_nav0'], 100_000.0)
        d = kilit.dogrula(self.cikti / 'KILIT.json', self.aktif, BELGELER, onkosul=False)
        self.assertEqual(d['belgeler'], k['belgeler'])

    def test_degisiklik_yakalanir(self):
        kilit.uret(self.cikti, self.aktif, BELGELER, veri_yukle=False, git=False, onkosul=False)
        (self.aktif / BELGELER[0]).write_text('# A degisti\n', encoding='utf-8')
        with self.assertRaises(kilit.KilitHatasi) as h:
            kilit.dogrula(self.cikti / 'KILIT.json', self.aktif, BELGELER, onkosul=False)
        self.assertIn(BELGELER[0], str(h.exception))

    def test_tek_atis_ve_eksik_belge(self):
        kilit.uret(self.cikti, self.aktif, BELGELER, veri_yukle=False, git=False, onkosul=False)
        with self.assertRaises(kilit.KilitHatasi):
            kilit.uret(self.cikti, self.aktif, BELGELER, veri_yukle=False, git=False, onkosul=False)
        with self.assertRaises(kilit.KilitHatasi):
            kilit.uret(self.aktif / 'baska', self.aktif, BELGELER + ('yok.md',), veri_yukle=False, git=False,
                       onkosul=False)

    def test_defter_satiri_sart(self):
        (self.aktif / kilit.DEFTER).write_text('kayit_id,varyant_sayisi\nA1-veri,0\n', encoding='utf-8')
        with self.assertRaises(kilit.KilitHatasi):
            kilit.uret(self.cikti, self.aktif, BELGELER, veri_yukle=False, git=False, onkosul=False)

    def test_teknik_ek_zinciri(self):
        # BANKA 21 g revizyonu: ilk kilit degismez; degismezler korunur; defter yalniz sona; tur basina 1; zincir.
        eski_v1 = kilit.v1_raporu
        kilit.v1_raporu = lambda motor: {'rapor': 'test_x', 'sha256': 's', 'motor': motor}
        try:
            kilit.uret(self.cikti, self.aktif, BELGELER, veri_yukle=False, git=False, onkosul=False)
            ilk = self.cikti / 'KILIT.json'
            ilk_bayt = ilk.read_bytes()
            ek = dict(aktif=self.aktif, belgeler=BELGELER)
            defter = self.aktif / kilit.DEFTER
            with open(defter, 'a', encoding='utf-8') as f:
                f.write('A6-banka-teknik,Adim 8,2026-10-09,teknik,banka,-,1,yeniden kosu\n')
            with self.assertRaises(kilit.KilitHatasi):                                # ek yokken defter degisti
                kilit.zincir_dogrula(ilk, self.cikti, self.aktif, BELGELER, onkosul=False)
            with self.assertRaises(kilit.KilitHatasi):                                # gerekce/test zorunlu
                kilit.teknik_ek(ilk, self.cikti, 'banka_oncesi', '', '', **ek)
            e = kilit.teknik_ek(ilk, self.cikti, 'banka_oncesi', 'hata', 'test_x', **ek)
            self.assertEqual(e['sira'], 1)
            self.assertEqual(ilk.read_bytes(), ilk_bayt)
            z = kilit.zincir_dogrula(ilk, self.cikti, **ek)
            self.assertEqual((z['ek']['tur'], z['onkosul']['v1']['rapor']), ('banka_oncesi', 'test_x'))
            with self.assertRaises(kilit.KilitHatasi):                                # ayni tur ikinci kez
                kilit.teknik_ek(ilk, self.cikti, 'banka_oncesi', 'h', 't', **ek)
            with self.assertRaises(kilit.KilitHatasi):                                # defter satiri artmadi
                kilit.teknik_ek(ilk, self.cikti, 'banka_sonrasi', 'h', 't', **ek)
            with open(defter, 'a', encoding='utf-8') as f:
                f.write('A7-banka-sonrasi,Adim 8,2026-10-10,teknik,banka,-,1,duzeltilmis kosu\n')
            kilit.teknik_ek(ilk, self.cikti, 'banka_sonrasi', 'h2', 't2', **ek)
            kilit.zincir_dogrula(ilk, self.cikti, **ek)
            with self.assertRaises(kilit.KilitHatasi):                                # asama yalniz kendi turunu
                kilit.zincir_dogrula(ilk, self.cikti, izinli_turler=('kapi',), **ek)
            metin0 = defter.read_text(encoding='utf-8')
            defter.write_text(metin0.replace('A6-banka-teknik', 'A6-banka-teknX'), encoding='utf-8')
            with self.assertRaises(kilit.KilitHatasi):                                # onceki ekin satiri degisemez
                kilit.zincir_dogrula(ilk, self.cikti, **ek)
            defter.write_text(metin0, encoding='utf-8')
            metin = defter.read_text(encoding='utf-8')
            defter.write_text(metin.replace('A4-carry-kapisi', 'A4-carry-kapisX'), encoding='utf-8')
            with self.assertRaises(kilit.KilitHatasi):                                # defter yalniz sona
                kilit.zincir_dogrula(ilk, self.cikti, **ek)
            defter.write_text(metin, encoding='utf-8')
            (self.aktif / BELGELER[0]).write_text('# A degisti\n', encoding='utf-8')
            with self.assertRaises(kilit.KilitHatasi):                                # ekonomik belge degisemez
                kilit.zincir_dogrula(ilk, self.cikti, **ek)
            (self.aktif / BELGELER[0]).write_text('# A\n', encoding='utf-8')
            kilit.zincir_dogrula(ilk, self.cikti, **ek)
            y = self.cikti / 'KILIT_TEKNIK_1.json'
            y.write_text(y.read_text(encoding='ascii').replace('"hata"', '"baska"'), encoding='ascii')
            with self.assertRaises(kilit.KilitHatasi):                                # zincir bozuk
                kilit.zincir_dogrula(ilk, self.cikti, **ek)
            with self.assertRaises(kilit.KilitHatasi):                                # git: ek commit'i eksik
                kilit.zincir_dogrula(ilk, self.cikti, git=True, kilit_commit='0' * 40, **ek)
        finally:
            kilit.v1_raporu = eski_v1

    def test_kapsam_daraltilamaz(self):
        # T15-4: kilitten bir belge cikarilirsa dogrulama beklenen kumeyle karsilastirir ve reddeder.
        kilit.uret(self.cikti, self.aktif, BELGELER[1:], veri_yukle=False, git=False, onkosul=False)
        with self.assertRaises(kilit.KilitHatasi):
            kilit.dogrula(self.cikti / 'KILIT.json', self.aktif, BELGELER, onkosul=False)

    def test_v1_raporu(self):
        testler = self.aktif / 'testler'
        ciktilar = self.aktif / 'rapor'
        testler.mkdir()
        for ad in ('test_v8_a.py', 'test_v8_b.py'):
            (testler / ad).write_text('', encoding='utf-8')

        kk = {'kapi': 'k1'}

        def rapor(ad, motor, basarisiz, dosyalar, kod=kk):
            (ciktilar / ad).mkdir(parents=True)
            (ciktilar / ad / 'sonuc.json').write_text(json.dumps(
                {'motor_kimligi': motor, 'kod_kimlikleri': kod, 'toplam': len(dosyalar), 'basarisiz': basarisiz,
                 'sonuclar': {f: {} for f in dosyalar}}), encoding='utf-8')
        rapor('test_20260101T000000Z', 'm1', 0, ['test_v8_a.py', 'test_v8_b.py'])
        rapor('test_20260102T000000Z', 'm2', 0, ['test_v8_a.py', 'test_v8_b.py'])
        self.assertEqual(kilit.v1_raporu('m1', testler, ciktilar, kk)['rapor'], 'test_20260101T000000Z')
        with self.assertRaises(kilit.KilitHatasi):                             # T16: kapı kodu değişti, eski PASS
            kilit.v1_raporu('m1', testler, ciktilar, {'kapi': 'k2'})
        rapor('test_20260103T000000Z', 'm1', 0, ['test_v8_a.py'])            # eksik kapsam: en yenisi gecmiyor
        with self.assertRaises(kilit.KilitHatasi):
            kilit.v1_raporu('m1', testler, ciktilar, kk)
        with self.assertRaises(kilit.KilitHatasi):
            kilit.v1_raporu('m3', testler, ciktilar, kk)


DORT = {'kod': 'k0', 'motor': 'm0', 'parametre': 'p0', 'ortam': 'python 3.12.14; numpy 2.5.1'}
D2 = {'is_listesi_sha256': 'x', 'ek_liste_sha256': None, 'birim_dosyalari': {'dosya': 3, 'birlesik_sha256': 'y'}}
HAR = 'h' * 64
GUNCEL = {'kod': 'k1', 'motor': 'm1', 'parametre': 'p1', 'har_sonuc_sha256': HAR}
N_DUMAN = duman_kanit.BEKLENEN_BIRIM


def _sha(yol) -> str:
    return hashlib.sha256(_Path(yol).read_bytes()).hexdigest()


def _jyaz(yol, d):
    _Path(yol).parent.mkdir(parents=True, exist_ok=True)
    _Path(yol).write_text(json.dumps(d, sort_keys=True), encoding='utf-8')


def duman_klasorleri(kal: _Path, kimlik=DORT, ters_bozuk: bool = False):
    """duman.py'nin iki klasörü: 28 zarf + iş listesi + ek liste (1 işçide ters sırada)."""
    _jyaz(kal / 'duman_sonuc.json', {'gecti': True, 'birim_sayisi_4isci': N_DUMAN, 'birim_sayisi_1isci': N_DUMAN})
    for ad in duman_kanit.KLASORLER:
        d = kal / ad
        _jyaz(d / duman_kanit.IS_LISTESI, {'birimler': [], 'kimlikler': DORT})
        ek = [json.dumps({'cikan': i}) for i in range(3)]
        (d / duman_kanit.EK_LISTE).write_text('\n'.join(ek if ad == 'duman_4isci' else ek[::-1]) + '\n', encoding='ascii')
        for i in range(N_DUMAN):
            govde = {'sr': i + (1 if ters_bozuk and ad != 'duman_4isci' and i == 0 else 0)}
            (d / f'd2_a000_y001_{i:02d}.json').write_text(json.dumps(
                {'birim': {'i': i}, 'kimlikler': kimlik, 'govde': govde}, sort_keys=True), encoding='ascii')


def duzey1_klasoru(kal: _Path, n: int = 4, kimlik=DORT) -> dict:
    """Gercek bicimli Duzey 1 girdileri (zarf + npz, is listesi) ve onlardan DUZEY1_OZET.json; ozeti doner."""
    d = kal / 'duzey1'
    d.mkdir(parents=True, exist_ok=True)
    for eski in list(d.glob('d1_*')):
        eski.unlink()
    liste = [{'duzey': 1, 'ayar_no': a, 'tur': 'ayar', 'n_yol': 10} for a in range(n)]
    (d / 'IS_LISTESI.json').write_text(json.dumps({'birimler': liste, 'kimlikler': kimlik}), encoding='ascii')
    birimler = []
    for k in liste:
        ad = f"d1_a{k['ayar_no']:03d}_ayar"
        npz = f'npz-{ad}'.encode('ascii')
        (d / f'{ad}.npz').write_bytes(npz)
        (d / f'{ad}.json').write_text(json.dumps({'birim': k, 'kimlikler': kimlik, 'govde': {
            'npz_sha256': hashlib.sha256(npz).hexdigest(), 'ek': {'i': k['ayar_no']}}}, sort_keys=True), encoding='ascii')
        birimler.append({'birim': ad, 'json_sha256': _sha(d / f'{ad}.json'), 'npz_sha256': _sha(d / f'{ad}.npz')})
    oz = {'is_listesi_sha256': _sha(d / 'IS_LISTESI.json'), 'kimlikler': kimlik, 'birim_sayisi': n, 'gecersiz': 0,
          'birimler': birimler}
    _jyaz(kal / 'DUZEY1_OZET.json', oz)
    return oz


class KanitZinciriTest(unittest.TestCase):
    """kilit.onkosullar: kanıt blokları KOD_DONDURMA'yla, eşdeğerliğin güncel ucu kilit anındaki girdilerle karşılaştırılır."""

    def setUp(self):
        self.aktif = _Path(tempfile.mkdtemp(prefix='kilit_kanit_'))
        self.kal = self.aktif / 'ciktilar' / 'v8_kalibrasyon_20260929_01'
        self.betik = self.aktif / 'betik.py'
        self.betik.write_text('# uretici\n', encoding='utf-8')
        self.zincir()

    def tearDown(self):
        shutil.rmtree(self.aktif, ignore_errors=True)

    def blok(self, kaynak, kimlik=DORT, har=HAR):
        return kanit.blok(self.betik, kimlik, har, kaynak, burasi=self.kal)

    def zincir(self, dondurma_ek=None, es_kimlik=DORT, es_girdi=None, es_guncel=None, tuketilen=None, d1_tuketilen=None,
               b5=None, n_toplama=None, ks_betik=None):
        _jyaz(self.kal / 'KOD_DONDURMA.json', {'kimlikler': DORT, 'har_sonuc_sha256': HAR, **(dondurma_ek or {})})
        duman_klasorleri(self.kal)
        dk = duman_kanit.olustur(self.kal, har_sha=HAR)
        self.assertTrue(dk['gecti'], dk['denetim'])
        _jyaz(self.kal / 'duman_kanit.json', dk)
        _jyaz(self.kal / 'bitis_sonuc.json', {'gecti': True, 'kimlik': {'farkli_kimlik': 1, 'dondurmayla_ayni': True},
                                               'kanit': self.blok(dict(D2))})
        oz = duzey1_klasoru(self.kal)
        d1 = dict(kilit.duzey1_ozet_bagi(oz), ozet_sha256=_sha(self.kal / 'DUZEY1_OZET.json'))
        (self.aktif / kilit.DEFTER).parent.mkdir(parents=True, exist_ok=True)
        (self.aktif / kilit.DEFTER).write_text(
            'kayit_id,asama,tarih_utc,tur,kapsam,aile,varyant_sayisi,aciklama\n'
            'A1-veri,Adim 1,2026-09-24,veri,-,-,0,x\n'
            'A4-carry-kapisi,Adim 4,2026-10-02,kapi,D,kesitsel funding tasima,1,test\n', encoding='utf-8')
        n = kilit.n_kilit(self.aktif) if n_toplama is None else n_toplama
        _jyaz(self.kal / 'TOPLAMA.json', {'durum': 'TAMAM', 'duzey1': {'rapor': {'N': n}}, 'kanit': self.blok({
            'bitis_sonuc_sha256': _sha(self.kal / 'bitis_sonuc.json'), 'duzey2_tuketilen': dict(D2, **(tuketilen or {})),
            'duzey1_tuketilen': dict(d1, **(d1_tuketilen or {})), 'defter_sha256': _sha(self.aktif / kilit.DEFTER)})})
        ks = self.aktif / kilit.KAPI_SENTETIK
        ks.mkdir(parents=True, exist_ok=True)
        (ks / 'kapi_sentetik.py').write_text('# sentetik\n', encoding='utf-8')
        _jyaz(ks / 'sonuc.json', {'tekrar': kilit.KAPI_SENTETIK_TEKRAR, 'senaryolar': {str(i): {} for i in range(7)},
                                  'betik_sha256': _sha(ks / 'kapi_sentetik.py') if ks_betik is None else ks_betik})
        ilk = sorted(dk['dosya_sha256'])[:4]
        girdi = es_girdi if es_girdi is not None else {a: dk['dosya_sha256'][a] for a in ilk}
        _jyaz(self.kal / 'esdegerlik_502e.json', {
            'gecti': True, 'guncel': dict(GUNCEL, ortam='python 3.12.14; numpy 2.5.1', **(es_guncel or {})),
            'kanit': self.blok({'klasor': 'duman_4isci', 'dosya_sha256': girdi}, kimlik=es_kimlik)})
        b5 = b5 or {}
        _jyaz(self.aktif / kilit.B5_A_ESDEGERLIK, {
            'gecti': b5.get('gecti', True), 'birim_sayisi': b5.get('birim_sayisi', 140),
            'ayni_sayisi': b5.get('ayni_sayisi', 140), 'denetim': {'gecti': b5.get('denetim', True)},
            'guncel': dict(GUNCEL, ortam='python 3.12.14; numpy 2.5.1', **b5.get('guncel', {})),
            'kanit': self.blok({'klasor': 'duzey2', 'duzey2_ozet': dict(D2, **b5.get('ozet', {})), 'dosya_sha256': {}},
                               kimlik=b5.get('kimlik', DORT))})

    def onk(self, **guncel):
        return kilit.onkosullar(self.aktif, v1=False, guncel=dict(GUNCEL, **guncel))

    def red(self, parca: str, **guncel):
        with self.assertRaises(kilit.KilitHatasi) as h:
            self.onk(**guncel)
        self.assertIn(parca, str(h.exception))

    def test_n_ve_defter_bagi(self):
        # BANKA 21 f: TOPLAMA'nin N'si ve defter sha'si guncel defterle ayni olmali (N = 159 + 1 + 1 = 161).
        self.assertEqual(kilit.n_kilit(self.aktif), 161)
        self.zincir(n_toplama=160)
        self.red('guncel N 161')
        self.zincir()
        with open(self.aktif / kilit.DEFTER, 'a', encoding='utf-8') as f:
            f.write('A5-yeni,Adim 5,2026-10-03,x,D,y,1,z\n')
        self.red('guncel N 162')

    def test_kapi_sentetik_zorunlu(self):
        # CARRY 16 c (BX-08): sonuc.json tam ve betik degismemis olmali.
        self.zincir(ks_betik='0' * 64)
        self.red('kapi sentetik')

    def test_tutarli_zincir_gecer(self):
        o = self.onk()
        self.assertEqual((o['motor_dondurulmus'], o['motor_guncel']), ('m0', 'm1'))
        self.assertEqual(o['kanit']['kod_dondurma_sha256'], _sha(self.kal / 'KOD_DONDURMA.json'))
        self.assertEqual(o['kanit']['guncel'], GUNCEL)

    def test_har_parametre_kod_motor_degisirse_ret(self):
        self.red('HAR', har_sonuc_sha256='9' * 64)                   # HAR sonuç dosyası kalibrasyondan sonra değişti
        self.red('parametre', parametre='p2')                        # PASS eski parametreyle, kilit yenisiyle
        self.red('kod', kod='k2')                                    # kalibrasyon/banka kodu değişti
        self.red('motor', motor='m2')

    def test_esdegerlik_baska_kimlikten_ret(self):
        self.zincir(es_kimlik=dict(DORT, parametre='p_baska'))
        self.red('esdegerlik: kanitin dayandigi')

    def test_esdegerlik_girdisi_duman_dosyasi_degil(self):
        self.zincir(es_girdi={'d2_a000_y001_00.json': '0' * 64})
        self.red('esdegerlik girdileri')
        self.zincir(es_girdi={})
        self.red('esdegerlik girdileri')

    def test_kod_dondurma_sonradan_degisirse_ret(self):
        self.zincir()
        _jyaz(self.kal / 'KOD_DONDURMA.json', {'kimlikler': DORT, 'har_sonuc_sha256': HAR, 'not': 'sonradan'})
        self.red('baska bir KOD_DONDURMA')

    def test_eski_bicimli_kanit_ret(self):
        _jyaz(self.kal / 'bitis_sonuc.json', {'gecti': True, 'kimlik': {'farkli_kimlik': 1, 'dondurmayla_ayni': True}})
        self.red('bitis_sonuc: kanit blogu yok')

    def test_bayat_bitis_ve_duman_ret(self):
        _jyaz(self.kal / 'bitis_sonuc.json', {'gecti': True, 'kimlik': {'farkli_kimlik': 1, 'dondurmayla_ayni': True},
                                               'kanit': self.blok({'is_listesi_sha256': 'y'})})
        self.red("TOPLAMA bugunku bitis_sonuc")                     # bitiş TOPLAMA'dan sonra yeniden üretildi
        self.zincir()
        _jyaz(self.kal / 'duman_sonuc.json', {'gecti': True, 'birim_sayisi_4isci': N_DUMAN, 'yeniden': 1})
        self.red("duman kaniti bugunku duman_sonuc")

    def test_toplamanin_tukettigi_duzey2_bitisle_ayni_olmali(self):
        # Codex T18-CIDDI-1: aynı kimlikli, iç hash'i geçerli başka birim dosyaları, ek liste ya da iş listesi.
        for deg in ({'birim_dosyalari': {'dosya': 3, 'birlesik_sha256': 'baska'}}, {'ek_liste_sha256': 'e2'},
                    {'is_listesi_sha256': 'x2'}, {'birim_dosyalari': {'dosya': 4, 'birlesik_sha256': 'y'}}):
            self.zincir(tuketilen=deg)
            self.red('Duzey 2 girdileri')
        self.zincir()
        tp = json.loads((self.kal / 'TOPLAMA.json').read_text(encoding='utf-8'))
        del tp['kanit']['kaynak']['duzey2_tuketilen']                          # eski biçimli TOPLAMA
        _jyaz(self.kal / 'TOPLAMA.json', tp)
        self.red('Duzey 2 girdileri')

    def test_toplamanin_tukettigi_duzey1_ozetle_ayni_olmali(self):
        # Codex T19 CIDDI-1: Duzey 1 tuketimi onceden kaydedilmis DUZEY1_OZET.json'a bagli.
        for deg in ({'birlesik_sha256': 'baska'}, {'dosya': 7}, {'is_listesi_sha256': 'x2'}, {'ozet_sha256': 'o2'}):
            self.zincir(d1_tuketilen=deg)
            self.red('Duzey 1 girdileri')
        self.zincir()
        oz = json.loads((self.kal / 'DUZEY1_OZET.json').read_text(encoding='utf-8'))
        _jyaz(self.kal / 'DUZEY1_OZET.json', dict(oz, not_='sonradan'))            # ozet TOPLAMA'dan sonra degisti
        self.red('Duzey 1 girdileri')
        _jyaz(self.kal / 'DUZEY1_OZET.json', dict(oz, kimlikler=dict(DORT, kod='k_baska')))
        self.red('DUZEY1_OZET.json kimlikleri')
        self.zincir()
        tp = json.loads((self.kal / 'TOPLAMA.json').read_text(encoding='utf-8'))
        del tp['kanit']['kaynak']['duzey1_tuketilen']                          # eski bicimli TOPLAMA
        _jyaz(self.kal / 'TOPLAMA.json', tp)
        self.red('Duzey 1 girdileri')
        self.zincir()
        (self.kal / 'DUZEY1_OZET.json').unlink()
        self.red('DUZEY1_OZET.json')

    def test_b5_a_esdegerligi_zorunlu(self):
        # Codex T20: B5 A birincil eşdeğerliği kilidin ön koşulu; tam 140/140, dondurulmuş kimlik, bitişteki klasör.
        self.assertTrue(self.onk()['b5_a_esdegerlik'])
        for b5, parca in (({'gecti': False}, 'B5 A birincil'), ({'ayni_sayisi': 139}, 'B5 A birincil'),
                          ({'birim_sayisi': 1, 'ayni_sayisi': 1}, 'B5 A birincil'), ({'denetim': False}, 'B5 A birincil'),
                          ({'ozet': {'birim_dosyalari': {'dosya': 2, 'birlesik_sha256': 'eksik'}}}, 'Duzey 2 klasorunde'),
                          ({'guncel': {'motor': 'm_baska'}}, 'B5 A esdegerligi guncel'),
                          ({'kimlik': dict(DORT, kod='k_baska')}, 'b5_a_esdegerlik: kanitin dayandigi')):
            self.zincir(b5=b5)
            self.red(parca)
        self.zincir()
        (self.aktif / kilit.B5_A_ESDEGERLIK).unlink()
        self.red('b5_a_esdegerlik.json')

    def test_durumlar(self):
        _jyaz(self.kal / 'TOPLAMA.json', {'durum': 'KILIT_BEKLER'})
        self.red('TAMAM degil')
        self.zincir()
        dk = json.loads((self.kal / 'duman_kanit.json').read_text(encoding='utf-8'))
        _jyaz(self.kal / 'duman_kanit.json', dict(dk, gecti=False))
        self.red('duman kanit denetimi')
        self.zincir()
        (self.kal / 'duman_kanit.json').unlink()
        self.red('duman_kanit.json')


class DefterBasKismiTest(unittest.TestCase):
    def test_yalniz_sona_ekleme(self):
        # BANKA 21 f / madde 8: dondurmadaki defter bugunkunun satir sinirinda biten bas kismi olmali.
        eski = b'kayit_id,varyant_sayisi\nA1,0\n'
        h = hashlib.sha256(eski).hexdigest()
        self.assertTrue(topla.defter_bas_kismi(eski, h))
        self.assertTrue(topla.defter_bas_kismi(eski + b'A4-carry-kapisi,1\n', h))
        self.assertFalse(topla.defter_bas_kismi(b'kayit_id,varyant_sayisi\nA1,1\n', h))      # satir degisti
        self.assertFalse(topla.defter_bas_kismi(b'X\n' + eski, h))                            # basa ekleme


class DumanKanitTest(unittest.TestCase):
    """duman_kanit.py: diskteki iki duman klasöründen kimlik ve hash kanıtı (motor koşulmaz)."""

    def setUp(self):
        self.kal = _Path(tempfile.mkdtemp(prefix='duman_kanit_'))
        _jyaz(self.kal / 'KOD_DONDURMA.json', {'kimlikler': DORT, 'har_sonuc_sha256': HAR})

    def tearDown(self):
        shutil.rmtree(self.kal, ignore_errors=True)

    def test_gecer_ve_blok(self):
        duman_klasorleri(self.kal)
        d = duman_kanit.olustur(self.kal, har_sha=HAR)
        self.assertTrue(d['gecti'], d['denetim'])
        self.assertEqual(d['kanit']['kimlikler'], DORT)
        self.assertEqual(d['kanit']['kod_dondurma_sha256'], _sha(self.kal / 'KOD_DONDURMA.json'))
        self.assertEqual(d['kanit']['betik_sha256'], _sha(KAL_DIR / 'duman_kanit.py'))
        self.assertEqual(d['kanit']['kaynak']['duman_sonuc_sha256'], _sha(self.kal / 'duman_sonuc.json'))
        self.assertEqual(len(d['dosya_sha256']), N_DUMAN)

    def test_red_durumlari(self):
        duman_klasorleri(self.kal, ters_bozuk=True)
        self.assertFalse(duman_kanit.olustur(self.kal, har_sha=HAR)['denetim']['dosyalar_ayni'])
        duman_klasorleri(self.kal, kimlik=dict(DORT, parametre='p_baska'))
        d = duman_kanit.olustur(self.kal, har_sha=HAR)
        self.assertFalse(d['gecti'])
        self.assertFalse(d['denetim']['dondurmayla_ayni'])
        duman_klasorleri(self.kal)
        self.assertFalse(duman_kanit.olustur(self.kal, har_sha='9' * 64)['denetim']['har_dondurmayla_ayni'])
        (self.kal / 'duman_4isci' / 'd2_a000_y001_00.json').unlink()
        self.assertFalse(duman_kanit.olustur(self.kal, har_sha=HAR)['denetim']['birim_sayisi'])


class ToplaBagiTest(unittest.TestCase):
    """topla.py (T18-CIDDI-1): hesaplamadan önce duzey2/ girdi özeti bitiş kanıtıyla aynı olmalı; hesap sırasında girdi
    değişirse TOPLAMA yazılmaz; tükettiği özet TOPLAMA kanıtında ve kilit onu bitişle eşleştirir. Toplama fonksiyonları
    sahtedir (performans yok); deneme defteri geçici dosyadır (banka klasörüne dokunulmaz)."""

    def setUp(self):
        self.d = _Path(tempfile.mkdtemp(prefix='topla_bag_'))
        self.defter = self.d / 'defter.csv'
        self.defter.write_text('kayit_id\nA\n', encoding='utf-8')
        _jyaz(self.d / 'KOD_DONDURMA.json', {'kimlikler': DORT, 'har_sonuc_sha256': HAR, 'N': 327,
                                             'deneme_defteri_sha256': _sha(self.defter)})
        duzey1_klasoru(self.d)
        (self.d / 'duzey2').mkdir()
        (self.d / 'duzey2' / 'IS_LISTESI.json').write_text(json.dumps({'birimler': [], 'kimlikler': DORT}), encoding='ascii')
        for i in range(4):
            (self.d / 'duzey2' / f'd2_a000_{i:02d}.json').write_text(json.dumps({'i': i}), encoding='ascii')
        (self.d / 'duzey2' / 'IS_LISTESI_EK.jsonl').write_text('{"c":1}\n', encoding='ascii')
        self.bitis_yaz()
        self.eski_T = topla.T

    def tearDown(self):
        topla.T = self.eski_T
        shutil.rmtree(self.d, ignore_errors=True)

    def bitis_yaz(self, kaynak=None):
        kaynak = topla.girdi_ozeti(self.d / 'duzey2') if kaynak is None else kaynak
        _jyaz(self.d / 'bitis_sonuc.json', {'gecti': True, 'kanit': kanit.blok(
            self.d / 'KOD_DONDURMA.json', DORT, HAR, kaynak, burasi=self.d)})

    def ret(self, parca):
        with self.assertRaises(topla.OnKosulHatasi) as h:
            topla.on_kosullar(self.d, self.defter)
        self.assertIn(parca, str(h.exception))

    def test_ayni_girdiler_gecer(self):
        _, _, ozet, d1 = topla.on_kosullar(self.d, self.defter)
        self.assertEqual(ozet['birim_dosyalari']['dosya'], 4)
        self.assertEqual(d1['dosya'], 8)

    def test_duzey1_ozete_bagli(self):
        # Codex T19 CIDDI-1: ayni kimlikli, ic hash'i gecerli baska JSON/NPZ, eksik/fazla birim, ozet yok ya da baska.
        d1 = self.d / 'duzey1'
        (d1 / 'd1_a001_ayar.npz').write_bytes(b'baska npz')
        self.ret("d1_a001_ayar dosyalari")
        duzey1_klasoru(self.d)
        z = json.loads((d1 / 'd1_a002_ayar.json').read_text(encoding='ascii'))
        z['govde']['ek'] = {'i': 99}
        (d1 / 'd1_a002_ayar.json').write_text(json.dumps(z, sort_keys=True), encoding='ascii')
        self.ret("d1_a002_ayar dosyalari")
        duzey1_klasoru(self.d)                                     # zarfin npz_sha256'si npz'yle uyusmaz, ozet tutarli
        z = json.loads((d1 / 'd1_a003_ayar.json').read_text(encoding='ascii'))
        z['govde']['npz_sha256'] = '0' * 64
        (d1 / 'd1_a003_ayar.json').write_text(json.dumps(z, sort_keys=True), encoding='ascii')
        oz = json.loads((self.d / 'DUZEY1_OZET.json').read_text(encoding='utf-8'))
        oz['birimler'][3]['json_sha256'] = _sha(d1 / 'd1_a003_ayar.json')
        _jyaz(self.d / 'DUZEY1_OZET.json', oz)
        self.ret("npz dosyasiyla ayni degil")
        duzey1_klasoru(self.d)
        (d1 / 'd1_a009_ayar.json').write_text('{}', encoding='ascii')                  # fazladan birim
        self.ret('birim kumesi')
        (d1 / 'd1_a009_ayar.json').unlink()
        (d1 / 'd1_a000_ayar.npz').unlink()                                               # eksik npz
        self.ret('birim kumesi')
        duzey1_klasoru(self.d)
        oz = json.loads((self.d / 'DUZEY1_OZET.json').read_text(encoding='utf-8'))
        _jyaz(self.d / 'DUZEY1_OZET.json', dict(oz, kimlikler=dict(DORT, motor='baska')))
        self.ret('DUZEY1_OZET kimlikleri')
        _jyaz(self.d / 'DUZEY1_OZET.json', dict(oz, gecersiz=1))
        self.ret('gecersiz birim')
        _jyaz(self.d / 'DUZEY1_OZET.json', dict(oz, is_listesi_sha256='x'))
        self.ret('is listesi')
        (self.d / 'DUZEY1_OZET.json').unlink()
        self.ret('DUZEY1_OZET.json yok')

    def test_baska_dosya_ek_liste_is_listesi_ret(self):
        (self.d / 'duzey2' / 'd2_a000_01.json').write_text(json.dumps({'i': 1, 'baska': True}), encoding='ascii')
        self.ret('birim_dosyalari')
        self.bitis_yaz()
        (self.d / 'duzey2' / 'IS_LISTESI_EK.jsonl').write_text('{"c":1}\n{"c":2}\n', encoding='ascii')
        self.ret('ek_liste_sha256')
        self.bitis_yaz()
        (self.d / 'duzey2' / 'IS_LISTESI.json').write_text(json.dumps({'kimlikler': DORT, 'birimler': []}),
                                                            encoding='ascii')           # aynı kimlik, başka bayt
        self.ret('is_listesi_sha256')
        self.bitis_yaz()
        (self.d / 'duzey2' / 'd2_a000_09.json').write_text('{}', encoding='ascii')     # fazladan birim
        self.ret('birim_dosyalari')

    def test_bitis_kaniti_eksik_ya_da_baska_kimlik(self):
        _jyaz(self.d / 'bitis_sonuc.json', {'gecti': True})
        self.ret('bitis kaniti yok')
        _jyaz(self.d / 'bitis_sonuc.json', {'gecti': True, 'kanit': kanit.blok(
            self.d / 'KOD_DONDURMA.json', dict(DORT, motor='baska'), HAR, topla.girdi_ozeti(self.d / 'duzey2'),
            burasi=self.d)})
        self.ret('baska kimliklerle')

    def _sahte_T(self, bozan=None):
        from types import SimpleNamespace

        def d1(*a):
            return {'durum': 'TAMAM', 'rapor': {'N': 327}, 'kurallar': SimpleNamespace(e=1)}

        def d2(*a):
            if bozan:
                bozan()
            return {'durum': 'TAMAM'}
        return SimpleNamespace(duzey1_topla=d1, duzey2_topla=d2)

    def test_main_tuketilen_ozeti_yazar_ve_kilit_eslestirir(self):
        topla.T = self._sahte_T()
        topla.main(self.d, self.defter, self.d / 'kayit.csv')
        tp = json.loads((self.d / 'TOPLAMA.json').read_text(encoding='utf-8'))
        kaynak = tp['kanit']['kaynak']
        self.assertEqual(kaynak['duzey2_tuketilen'], topla.girdi_ozeti(self.d / 'duzey2'))
        self.assertEqual(kaynak['duzey1_tuketilen']['dosya'], 8)
        oz = json.loads((self.d / 'DUZEY1_OZET.json').read_text(encoding='utf-8'))
        self.assertEqual(kaynak['duzey1_tuketilen'],
                         dict(kilit.duzey1_ozet_bagi(oz), ozet_sha256=_sha(self.d / 'DUZEY1_OZET.json')))
        bitis = json.loads((self.d / 'bitis_sonuc.json').read_text(encoding='utf-8'))
        self.assertEqual(kaynak['duzey2_tuketilen'], {k: bitis['kanit']['kaynak'][k] for k in kilit.D2_OZET})

    def test_main_hesap_sirasinda_degisen_girdi(self):
        def boz():
            (self.d / 'duzey2' / 'd2_a000_02.json').write_text('{"i": 99}', encoding='ascii')
        topla.T = self._sahte_T(boz)
        with self.assertRaises(topla.OnKosulHatasi):
            topla.main(self.d, self.defter, self.d / 'kayit.csv')
        self.assertFalse((self.d / 'TOPLAMA.json').exists())

    def test_main_hesap_sirasinda_degisen_duzey1(self):
        def boz():
            (self.d / 'duzey1' / 'd1_a001_ayar.npz').write_bytes(b'hesap sirasinda')
        topla.T = self._sahte_T(boz)
        with self.assertRaises(topla.OnKosulHatasi):
            topla.main(self.d, self.defter, self.d / 'kayit.csv')
        self.assertFalse((self.d / 'TOPLAMA.json').exists())


class GitDenetimiTest(unittest.TestCase):
    def test_commit_bildirilmezse_ret(self):
        with self.assertRaises(kilit.KilitHatasi):
            kilit.git_denetimi(__file__, None, fetch=False)

    def test_bu_dosya_head_ile_ayni_degilse_ret(self):
        # Bu test dosyası izleniyor; HEAD'deki hali yerelle aynıysa geçer, değilse KilitHatasi. Uzak dal koşulu
        # (push edilmiş commit) bu dalda sağlanır. Yalnız fonksiyonun çalıştığı ve tutarlı olduğu sınanır.
        import subprocess
        head = subprocess.run(['git', 'rev-parse', 'HEAD'], cwd=V8_DIR, capture_output=True, text=True).stdout.strip()
        try:
            d = kilit.git_denetimi(__file__, head, fetch=False)
            self.assertEqual(d['commit'], head)
        except kilit.KilitHatasi as e:
            self.assertTrue('farkli' in str(e) or 'uzak' in str(e) or 'izlenmiyor' in str(e))

class GitYerelUzakTest(unittest.TestCase):
    """T17-c: yerel bare 'origin' ile (ağ yok). Tam hash zorunlu; yalnız origin; silinmiş dalın bayat referansı sayılmaz."""

    def setUp(self):
        self.d = _Path(tempfile.mkdtemp(prefix='kilit_git_'))
        self.uzak, self.baska, self.c = self.d / 'uzak.git', self.d / 'baska.git', self.d / 'calisma'
        for r in (self.uzak, self.baska):
            self.git('init', '-q', '--bare', str(r), cwd=self.d)
        self.git('clone', '-q', str(self.uzak), str(self.c), cwd=self.d)
        self.kilit = self.c / 'KILIT.json'
        self.commit('{"a": 1}')
        self.git('push', '-q', 'origin', 'HEAD:refs/heads/ana')
        self.ilk = self.git('rev-parse', 'HEAD')

    def tearDown(self):
        shutil.rmtree(self.d, ignore_errors=True)

    def git(self, *a, cwd=None):
        import subprocess
        return subprocess.run(['git', '-c', 'user.name=t', '-c', 'user.email=t@t', *a], cwd=cwd or self.c,
                              capture_output=True, text=True, check=True).stdout.strip()

    def commit(self, icerik: str):
        self.kilit.write_text(icerik, encoding='ascii')
        self.git('add', 'KILIT.json')
        self.git('commit', '-q', '-m', 'k')
        return self.git('rev-parse', 'HEAD')

    def ret(self, commit, parca, fetch=True):
        with self.assertRaises(kilit.KilitHatasi) as h:
            kilit.git_denetimi(self.kilit, commit, fetch=fetch)
        self.assertIn(parca, str(h.exception))

    def test_itilmis_tam_hash_gecer(self):
        d = kilit.git_denetimi(self.kilit, self.ilk)
        self.assertEqual((d['commit'], d['uzak'], d['uzak_dallar']), (self.ilk, 'origin', ['ana']))

    def test_hareketli_ya_da_kisa_referans_ret(self):
        for ref in ('HEAD', 'ana', 'origin/ana', self.ilk[:12], self.ilk.upper(), self.ilk + ' '):
            self.ret(ref, 'tam 40')

    def test_itilmemis_ya_da_baska_remote_ret(self):
        yeni = self.commit('{"a": 2}')
        self.ret(yeni, 'uzak deposunda yok')
        self.git('remote', 'add', 'baska', str(self.baska))
        self.git('push', '-q', 'baska', 'HEAD:refs/heads/ana')
        self.git('fetch', '-q', 'baska')
        self.ret(yeni, 'uzak deposunda yok')                      # yalnız origin referansları sayılır

    def test_silinmis_dalin_bayat_referansi_ret(self):
        yeni = self.commit('{"a": 3}')
        self.git('push', '-q', 'origin', 'HEAD:refs/heads/gecici')
        self.assertEqual(kilit.git_denetimi(self.kilit, yeni)['uzak_dallar'], ['gecici'])
        self.git('update-ref', '-d', 'refs/heads/gecici', cwd=self.uzak)   # uzakta silindi; yerel origin/gecici bayat
        self.ret(yeni, 'uzak deposunda yok')                      # fetch --prune bayat referansı düşürür
        self.assertNotIn('gecici', self.git('branch', '-r'))

    def test_dosya_commitle_ayni_olmali(self):
        self.kilit.write_text('{"a": 9}', encoding='ascii')
        self.ret(self.ilk, 'farkli')


if __name__ == '__main__':
    unittest.main()
