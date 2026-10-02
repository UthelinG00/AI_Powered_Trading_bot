"""Hüküm betiği (banka_hukum.py, UYGULAMA_EK U3), dondurma betiği (dondur.py, U1) ve banka girişinin kilit denetimi
(acilis.kilit_tam / kilit_zinciri, U2): yapıştırıcı katman (Codex T30 düzeltmeleri dahil).
Ağır zincir (koşucu → damga → birimleri_coz → hukum → rapor) 6.12 tam motorlu provada sınandı; burada betiklerin kendi
denetimleri sınanır. Kuru VERI_DENETIM sentetik D paketinden üretilir; gerçek D, banka verisi ya da mühürlü dosya
okunmaz. Git denetimleri (uzak commit) ayrı: kilit testleri; burada kapalı ya da yamalı."""
import json
import shutil
import sys as _sys
import tempfile
import unittest
from pathlib import Path as _Path
from unittest import mock

TESTLER_DIR = _Path(__file__).resolve().parent
V8_DIR = TESTLER_DIR.parent
for _d in (V8_DIR, TESTLER_DIR):
    if str(_d) not in _sys.path:
        _sys.path.insert(1, str(_d))

from banka_kos import acilis as A  # noqa: E402
from banka_kos import age, ayar  # noqa: E402
from banka_kos import kosucu as K  # noqa: E402
from banka_kos.veri_denetim import kanonik  # noqa: E402
from test_v8_banka_acilis import _betik, _d_paketi, _filtre_klasoru  # noqa: E402

AKTIF = V8_DIR.parent
TOPLAMA = AKTIF / 'ciktilar' / 'v8_kalibrasyon_20260929_01' / 'TOPLAMA.json'
KAPI = AKTIF / 'ciktilar' / 'v8_kapi_kosu_20261001'
KILIT = AKTIF / 'ciktilar' / 'v8_kilit_20261001' / 'KILIT.json'
KOMMIT = '71cf576f50722a7ef7580ba03f757780014df40a'


def _kurallar():
    return json.loads(TOPLAMA.read_text(encoding='utf-8'))['duzey1']['rapor']['kurallar']


def _yaz(yol: _Path, d) -> str:
    yol.parent.mkdir(parents=True, exist_ok=True)
    b = kanonik(d)
    yol.write_bytes(b)
    return A.sha_bayt(b)


class HukumBetigiTest(unittest.TestCase):
    """Sentetik D'den kuru VERI_DENETIM (gerçek dönem yapısı); banka klasörü onun üzerine kurulur."""
    SEM = ('BTCUSDT', 'ETHUSDT', 'XUSDT')

    @classmethod
    def setUpClass(cls):
        cls.k = _Path(tempfile.mkdtemp(prefix='hukum_'))
        _d_paketi(cls.k / 'd', cls.SEM, ayar.D_BAS_MS, ayar.D_BIT_MS)
        _filtre_klasoru(cls.k / 'filtre', ('BTCUSDT', 'ETHUSDT'))
        ek = {'d_kok': str(cls.k / 'd'), 'evren': cls.SEM, 'filtre_klasoru': str(cls.k / 'filtre')}
        kod = _betik('veri_denetim').main(['kuru', str(cls.k / 'kuru'), 'A'], ek)
        assert kod == 0, kod
        cls.vd = json.loads((cls.k / 'kuru' / 'denetim' / 'VERI_DENETIM.json').read_text(encoding='ascii'))
        cls.BH, cls.DN = _betik('banka_hukum'), _betik('dondur')
        cls.guncel = A.kimlikler()
        cls.defter = cls.DN.defter_ozeti()
        cls.N = cls.defter['N_defter'] + 1                                      # + D doğrulama (karar B)
        _, cls.alici = age.anahtar_uret()

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.k, ignore_errors=True)

    def setUp(self):
        self.c = _Path(tempfile.mkdtemp(prefix='banka_', dir=self.k))
        self.dondurma = dict(self.guncel, mimari='A', kilit_sha256='k' * 64, sifreleme_acik_anahtar=self.alici,
                             kalibrasyon={'kurallar': _kurallar(), 'toplama_sha256': A.sha_bayt(TOPLAMA.read_bytes())},
                             deneme_defteri=dict(self.defter, d_dogrulama_sayimi=1, N_dondurma=self.N), teknik_ekler=[], dsr={'kaynak': 'varsayim'},
                             stres_secenegi='i')
        self.d_yol = self.c.parent / f'{self.c.name}_DONDURMA.json'
        self.acilis = {'gorulmus_gunler': [f'2021-0{i}-15' for i in range(1, 8)]}
        self.a_yol = self.c.parent / f'{self.c.name}_ACILIS.json'
        self.dt_yol = self.c.parent / f'{self.c.name}_DT.json'
        self.kimlik_yol = self.c.parent / f'{self.c.name}_kimlik.txt'
        self.kimlik_yol.write_text('# created: x\n# public key: ' + self.alici + '\nAGE-SECRET-KEY-1TEST\n',
                                   encoding='ascii')
        self._kur()

    def _kur(self, kim_boz=None, ozet_boz=None, il_alici=None):
        """DONDURMA → VERI_DENETIM → IS_LISTESI → DENETIM_OZETI → DENETIM_TAMAM zinciri (hash'leri birbirine bağlı)."""
        d_sha = _yaz(self.d_yol, self.dondurma)
        a_sha = _yaz(self.a_yol, self.acilis)
        vd_sha = _yaz(self.c / 'denetim' / 'VERI_DENETIM.json', dict(self.vd, dondurma_sha256=d_sha))
        kim = {'mod': 'banka', 'mimari': 'A', 'kimlikler': self.guncel, 'dondurma_sha256': d_sha, 'acilis_sha256': a_sha,
               'veri_denetim_json_sha256': vd_sha, 'donem': self.vd['donem'], 'veri_kimligi': self.vd['veri_kimligi'],
               'tohum_banka': self.dondurma['tohum_banka'], **(kim_boz or {})}
        (self.c / K.IS_LISTESI).write_bytes(kanonik({'birimler': ayar.birimler('A'), 'kimlikler': kim,
                                                      'alici': il_alici or self.alici}))
        _yaz(self.c / 'SONUC_DAMGA.json', {'kok_sha256': 'a' * 64, 'birim_sayisi': 2, 'birimler': []})
        self.ozet = {'T1': 'yok', 'T2': 'yok', 'T3': 'yok', 'T4': {'muhasebe_kapisi_gecen_birim': 2},
                     'T5': {'durum': 'yok'}, 'birim_sayisi': 2, 'damga_kok_sha256': 'a' * 64,
                     'is_listesi_kimlik_sha256': A.sha_bayt(kanonik(kim)), **(ozet_boz or {})}
        oz_sha = _yaz(self.c / 'denetim' / 'DENETIM_OZETI.json', self.ozet)
        self.dt = {'damga_kok_sha256': 'a' * 64, 'denetim_ozeti_sha256': oz_sha, 'commit': 'c' * 40}
        _yaz(self.dt_yol, self.dt)

    def _cagir(self, **yama):
        """Ağır adımlar (T1/kilit zinciri, çözme, hüküm, rapor) yamalanır; yapıştırıcı gerçek koşar; git kapalı."""
        kayit = {}

        def coz(cikti, kimlik, beklenen_kok=None):
            kayit['coz'] = (kimlik, beklenen_kok)
            return {'u1': {}}

        def hukum(birimler, hb):
            kayit['hb'] = hb
            return {'karar': yama.get('karar', 'RET')}

        def rapor_md(sonuc, satir, metrik, baglam):
            kayit['baglam'] = baglam
            return '# rapor\nikinci satir\n'
        with mock.patch.object(self.BH.A, 'hazirla', return_value=({}, {'motor_sha256': 'm'}, {})), \
                mock.patch.object(self.BH.H, 'birimleri_coz', side_effect=coz), \
                mock.patch.object(self.BH.H, 'hukum', side_effect=hukum), \
                mock.patch.object(self.BH.rapor, 'rapor_satirlari', return_value=[]), \
                mock.patch.object(self.BH.rapor_md, 'birincil_metrikler', return_value={}), \
                mock.patch.object(self.BH.rapor_md, 'banka_raporu', side_effect=rapor_md):
            kim = self.BH.hukum_ver(self.c, self.a_yol, self.d_yol, self.dt_yol, self.kimlik_yol,
                                    ek={'kilit_denetimi': False})
        return kim, kayit

    def test_hukum_ve_baglam(self):
        kim, kayit = self._cagir()
        self.assertEqual(kim['hukum_turu'], 'RET')
        self.assertEqual(kayit['coz'], ('AGE-SECRET-KEY-1TEST', 'a' * 64))
        hb, dm = kayit['hb'], self.vd['donem']
        self.assertEqual((hb.mimari, hb.N_hukum, hb.kurallar.N, hb.kurallar.d), ('A', self.N, 329, 0.9))
        self.assertEqual(hb.tohum_banka, self.guncel['tohum_banka'])
        self.assertEqual((hb.t0_z1_ms, hb.birincil_son_ms, hb.z2_bas_ms, hb.z2_son_ms, hb.d_bas_ms, hb.d_bit_ms),
                         (dm['t0_z1_ms'], dm['birincil_son_ms'], dm['z2_bas_ms'], dm['z2_son_ms'], dm['d_bas_ms'],
                          dm['d_bit_ms']))
        self.assertEqual(hb.z1_dilim_sinir, tuple(dm['z1_dilim_sinir']))
        self.assertEqual(hb.gorulmus_gunler, tuple(sorted(hb.gorulmus_gunler)))
        self.assertEqual(len(hb.gorulmus_gunler), 7)
        b = kayit['baglam']
        self.assertEqual((b['hukum_turu'], b['b2_turu'], b['N_hukum']), ('RET', 'B', self.N))
        self.assertEqual(b['hashler']['DONDURMA'], A.sha_bayt(self.d_yol.read_bytes()))
        k = self.c / 'hukum'
        self.assertEqual(json.loads((k / 'HUKUM_KIMLIK.json').read_bytes()), kim)
        self.assertEqual(kim['banka_sonuc_sha256'], A.sha_bayt((k / 'banka_sonuc.json').read_bytes()))
        self.assertEqual(kim['rapor_sha256'], A.sha_bayt((k / 'BANKA_RAPORU.md').read_bytes()))   # CRLF yok
        self.assertEqual((kim['girdiler']['damga_kok'], kim['girdiler']['N_hukum']), ('a' * 64, self.N))
        with self.assertRaises(A.AcilisHatasi):                                    # hüküm bir kez yazılır
            self._cagir()

    def test_n_hukum_defterden(self):
        # §3.3: N_hüküm güncel defterden bir kez; dondurmadaki defter baş kısmı olmalı, N_dondurma'dan küçük olamaz.
        self.assertEqual(self.BH.n_hukum(self.dondurma), self.N)                 # defter + 1 D doğrulama (karar B)
        with self.assertRaises(A.AcilisHatasi):
            self.BH.n_hukum(dict(self.dondurma, deneme_defteri=dict(self.dondurma['deneme_defteri'], sha256='0' * 64)))
        with self.assertRaises(A.AcilisHatasi):
            self.BH.n_hukum(dict(self.dondurma, deneme_defteri=dict(self.dondurma['deneme_defteri'], N_dondurma=400)))

    def test_teknik_gecersiz_cozmeden(self):
        for boz, beklenen in (({'T3': 'var'}, ['T3']), ({'T5': {'durum': 'VAR'}}, ['T5']),
                              ({'T4': {'muhasebe_kapisi_gecen_birim': 1}}, ['T4'])):
            with self.subTest(boz=boz):
                shutil.rmtree(self.c / 'hukum', ignore_errors=True)
                self._kur(ozet_boz=boz)
                self.assertEqual(self.BH.denetim_tamam(self.c, self.dt, git=False)['teknik'], beklenen)
                kim, kayit = self._cagir(karar='KABUL')
                self.assertEqual(kim['hukum_turu'], 'TEKNİK GEÇERSİZ')
                self.assertNotIn('coz', kayit)                                     # anahtar okunmadı, çözülmedi
                self.assertNotIn('hb', kayit)

    def test_tutarsizliklar_durdurur(self):
        bozuklar = {
            'dt_kok': lambda: _yaz(self.dt_yol, dict(self.dt, damga_kok_sha256='b' * 64)),
            'dt_ozet': lambda: _yaz(self.dt_yol, dict(self.dt, denetim_ozeti_sha256='0' * 64)),
            'vd_dondurma': lambda: _yaz(self.c / 'denetim' / 'VERI_DENETIM.json', self.vd),
            'toplama': lambda: (setattr(self, 'dondurma', dict(self.dondurma, kalibrasyon=dict(
                self.dondurma['kalibrasyon'], toplama_sha256='0' * 64))), self._kur()),
            'il_mimari': lambda: self._kur(kim_boz={'mimari': 'B'}),
            'il_acilis': lambda: self._kur(kim_boz={'acilis_sha256': '0' * 64}),
            'il_donem': lambda: self._kur(kim_boz={'donem': dict(self.vd['donem'], t0_z1_ms=0)}),
            'il_kimlik': lambda: self._kur(kim_boz={'kimlikler': dict(self.guncel, motor_sha256='0' * 64)}),
            'il_alici': lambda: self._kur(il_alici='age1baska'),
            'il_ozet_bagi': lambda: self._kur(ozet_boz={'is_listesi_kimlik_sha256': '0' * 64}),
        }
        for ad, boz in bozuklar.items():
            with self.subTest(ad=ad):
                self.setUp()
                boz()
                with self.assertRaises(A.AcilisHatasi):
                    self._cagir()
                self.assertFalse((self.c / 'hukum').exists())

    def test_main_cikislari(self):
        arg = [str(self.c), str(self.a_yol), str(self.d_yol), str(self.dt_yol), str(self.kimlik_yol)]
        self.assertEqual(self.BH.main(arg), 4)                     # gerçek hazirla: kilit_yolu yok → T1
        self.assertFalse((self.c / 'hukum').exists())
        with mock.patch.object(self.BH, 'hukum_ver', side_effect=ValueError('XUSDT 0.1234')), \
                mock.patch('builtins.print') as p:
            self.assertEqual(self.BH.main(arg), 6)
        cikti = p.call_args.args[0]
        self.assertNotIn('XUSDT', cikti)                           # ham istisna ekrana çıkmaz
        self.assertIn('iz_sha256', cikti)
        self.assertFalse((self.c / 'hukum_hata_izi.txt').exists())               # iz diske yazılmaz
        self.assertEqual(self.BH.main(arg[:3]), 2)


class DondurTest(unittest.TestCase):
    """Gerçek kapı çıktısı (karar A), TOPLAMA ve defter; kuru koşu klasörü sentetik ama tutarlı (iş listesi, damga,
    özet). Kilit denetimi (acilis.kilit_tam) yamalanır; KilitTamTest gerçek kilitle sınar."""

    @classmethod
    def setUpClass(cls):
        cls.DN = _betik('dondur')
        _, cls.alici = age.anahtar_uret()
        cls.kilit = json.loads(KILIT.read_text(encoding='ascii'))
        cls.guncel = A.kimlikler()

    def setUp(self):
        self.k = _Path(tempfile.mkdtemp(prefix='dondur_'))
        self.kuru = self.k / 'kuru'
        self._kuru_kur()

    def tearDown(self):
        shutil.rmtree(self.k, ignore_errors=True)

    def _kuru_kur(self, kim_boz=None, ozet_boz=None, eksik=0, kok_boz=False):
        taban = ayar.birimler('A')
        satirlar = [[K.birim_adi(b), 'd' * 64, 'e' * 64] for b in taban][eksik:]
        kim = {'mod': 'kuru', 'mimari': 'A', 'kimlikler': self.guncel, **(kim_boz or {})}
        (self.kuru).mkdir(parents=True, exist_ok=True)
        (self.kuru / K.IS_LISTESI).write_bytes(kanonik({'birimler': taban, 'kimlikler': kim, 'alici': 'age1x'}))
        kok = 'f' * 64 if kok_boz else A.sha_bayt(kanonik(satirlar))
        self.damga_sha = _yaz(self.kuru / 'SONUC_DAMGA.json', {'kok_sha256': kok, 'birim_sayisi': len(satirlar),
                                                               'birimler': satirlar})
        self.ozet = {'T1': 'kuru: DONDURMA yok, kimlikler kaydedildi', 'T2': 'yok', 'T3': 'yok',
                     'T4': {'muhasebe_kapisi_gecen_birim': len(satirlar)}, 'T5': {'durum': 'yok'},
                     'birim_sayisi': len(satirlar), 'damga_kok_sha256': kok,
                     'is_listesi_kimlik_sha256': A.sha_bayt(kanonik(kim)), **(ozet_boz or {})}
        _yaz(self.kuru / 'denetim' / 'DENETIM_OZETI.json', self.ozet)

    def _icerik(self, kapi=KAPI, alici=None, ekler=(), ek_commitler=(), n_defter=None):
        kt = {'zincir': self.kilit, 'v1_guncel': {'rapor': 'test_x', 'sha256': 'v' * 64}, 'teknik_ekler': list(ekler)}
        defter = {'sha256': 'd' * 64, 'satir': 22, 'N_v8': 170, 'N_defter': n_defter or 329 + len(ekler)}   # gerçek defterden bağımsız
        with mock.patch.object(self.DN.A, 'kilit_tam', return_value=kt) as z,                 mock.patch.object(self.DN, 'defter_ozeti', return_value=defter):
            d = self.DN.icerik(KILIT, KOMMIT, list(ek_commitler), kapi, self.kuru, alici or self.alici, git=False)
        self.assertEqual(z.call_args.args[3], ('kapi', 'banka_oncesi'))
        return d

    def test_alanlar(self):
        d = self._icerik()
        self.assertEqual((d['mimari'], d['carry_kapisi']['karar']), ('A', 'A'))
        self.assertEqual(d['carry_kapisi']['hukum_sha256'], A.sha_bayt((KAPI / 'HUKUM.json').read_bytes()))
        self.assertEqual(d['carry_kapisi']['rapor_sha256'], A.sha_bayt((KAPI / 'KAPI_RAPORU.md').read_bytes()))
        self.assertEqual(d['kilit_sha256'], A.sha_bayt(KILIT.read_bytes()))
        self.assertEqual((d['kilit_yolu'], d['kilit_commit'], d['teknik_ekler']),
                         ('ciktilar/v8_kilit_20261001/KILIT.json', KOMMIT, []))
        self.assertEqual(d['v1_guncel'], {'rapor': 'test_x', 'sha256': 'v' * 64})
        self.assertEqual(d['v1_kilit'], self.kilit['onkosul']['v1'])
        self.assertEqual((d['deneme_defteri']['N_defter'], d['deneme_defteri']['d_dogrulama_sayimi'],
                          d['deneme_defteri']['N_dondurma'], d['kalibrasyon']['kurallar']['N'], d['dsr']['N_kilit']),
                         (329, 1, 330, 329, 329))
        self.assertEqual((d['dsr']['b2_turu'], d['dsr']['d'], d['kalibrasyon']['b7_kuantil']), ('B', 0.9, 0.95))
        self.assertGreater(d['dsr']['SR0_kilit'], 0)
        self.assertEqual(d['kalibrasyon']['kod_sha256'], self.kilit['kod']['kalibrasyon'])
        self.assertEqual(len(d['tahminci']['dondurulan']['beta']), 4)
        self.assertEqual(d['d_dogrulama']['sonuc_damga_sha256'], self.damga_sha)
        self.assertEqual(d['d_dogrulama']['birim_sayisi'], len(ayar.birimler('A')))
        for alan in ('motor_sha256', 'banka_kos_sha256', 'veri_denetim_sha256', 'parametreler_sha256',
                     'har_sonuc_sha256', 'ortam', 'tohum_banka'):
            self.assertEqual(d[alan], self.guncel[alan], alan)
        self.assertEqual(A.t1_denetimi(d, self.guncel), [])                        # banka girişi T1'i geçer
        self.assertEqual((d['sifreleme_acik_anahtar'], d['stres_secenegi'], d['kullanici_onayi']),
                         (self.alici, 'i', 'dondur'))
        self.assertIsNone(d['git_commit_ust'])

    def test_kapi_kaniti(self):
        sahte = self.k / 'kapi'
        shutil.copytree(KAPI, sahte, ignore=shutil.ignore_patterns('muhur'))
        self.DN.kapi_kaniti(sahte, self.kilit, KOMMIT)
        with self.assertRaises(self.DN.DondurmaHatasi):
            self.DN.kapi_kaniti(sahte, self.kilit, 'f' * 40)                       # başka kilit commit'i
        den = json.loads((sahte / 'DENETIM.json').read_text(encoding='utf-8'))
        (sahte / 'DENETIM.json').write_text(json.dumps(dict(den, teknik_ihlal=['x'])), encoding='utf-8')
        with self.assertRaises(self.DN.DondurmaHatasi):                             # hash KOSU_OZETI'yle tutmaz
            self.DN.kapi_kaniti(sahte, self.kilit, KOMMIT)

    def test_kuru_kaniti_durdurur(self):
        bozuklar = {'T4': dict(ozet_boz={'T4': {'muhasebe_kapisi_gecen_birim': 1}}),
                    'T5': dict(ozet_boz={'T5': {'durum': 'VAR'}}), 'T2': dict(ozet_boz={'T2': 'var'}),
                    'kok': dict(kok_boz=True), 'eksik_birim': dict(eksik=1),
                    'kimlik': dict(kim_boz={'kimlikler': dict(self.guncel, motor_sha256='0' * 64)}),
                    'mimari': dict(kim_boz={'mimari': 'B'}), 'kip': dict(kim_boz={'mod': 'banka'}),
                    'ozet_bagi': dict(ozet_boz={'is_listesi_kimlik_sha256': '0' * 64})}
        for ad, kw in bozuklar.items():
            with self.subTest(ad=ad):
                shutil.rmtree(self.kuru, ignore_errors=True)
                self._kuru_kur(**kw)
                with self.assertRaises(self.DN.DondurmaHatasi):
                    self._icerik()

    def test_digerleri_durdurur(self):
        with self.assertRaises(self.DN.DondurmaHatasi):
            self._icerik(alici='ssh-ed25519 AAAA')
        with self.assertRaises(Exception):
            self._icerik(alici='age1bozuk')
        with self.assertRaises(self.DN.DondurmaHatasi):                            # ek var, commit yok
            self._icerik(ekler=[{'sira': 1, 'tur': 'kapi', 'sha256': 's' * 64}])
        ek1 = [{'sira': 1, 'tur': 'banka_oncesi', 'sha256': 's' * 64}]
        with self.assertRaisesRegex(self.DN.DondurmaHatasi, 'commit'):             # ek sayısı ≠ commit sayısı
            self._icerik(ekler=ek1, ek_commitler=['c' * 40, 'e' * 40])
        with self.assertRaisesRegex(self.DN.DondurmaHatasi, "defter N"):           # §3.3: N, ek sayısıyla tutmaz
            self._icerik(ekler=ek1, ek_commitler=['c' * 40], n_defter=331)
        d = self._icerik(ekler=[{'sira': 1, 'tur': 'banka_oncesi', 'sha256': 's' * 64}], ek_commitler=['c' * 40])
        self.assertEqual((d['deneme_defteri']['N_dondurma'], d['teknik_ekler'][0]['commit']), (331, 'c' * 40))

    def test_main_onay_ve_bir_kez(self):
        with self.assertRaises(SystemExit):
            self.DN.main([str(self.k / 'c')])
        (self.k / 'c').mkdir()
        (self.k / 'c' / 'DONDURMA.json').write_text('{}', encoding='ascii')
        with self.assertRaises(SystemExit) as e:
            self.DN.main([str(self.k / 'c'), '--onay', 'dondur'])
        self.assertIn('zaten var', str(e.exception))


class KilitTamTest(unittest.TestCase):
    """U2 (Codex T30-1/7): gerçek kilit, git kapalı. İlk kilit ön koşulsuz doğrulanır (banka_kos kilit kimliğinde
    değil), kalibrasyon ön koşulları ayrıca yeniden hesaplanır, kilitteki V1 tarihsel kanıt olarak denetlenir; güncel
    V1 (en yeni rapor) yamalanır (takım koşarken rapor henüz yazılmadı)."""

    def test_gercek_kilit(self):
        import kilit
        ekler = kilit._ekler(KILIT.parent)
        ilk = json.loads(KILIT.read_text(encoding='ascii'))
        if not ekler and kilit.kod_kimlikleri() != ilk['kod']:
            # Teknik düzeltme kodu yazıldı, ek kaydı (21 g) henüz yok: ek, bu takımın V1 raporuyla üretilir.
            self.skipTest("kilitli kod degisti, teknik ek kaydi bekleniyor")
        import contextlib
        # Eksiz yolda güncel V1 yamalanır (takım koşarken rapor yazılmadı); ekli yolda zincir ekin V1'ini bugünkü
        # en yeni raporla karşılaştırır, yama o karşılaştırmayı bozar.
        yama = contextlib.nullcontext() if ekler else mock.patch('kilit.v1_raporu', return_value={'rapor': 'test_x'})
        with yama:
            k = A.kilit_tam(KILIT, KOMMIT, (), ('kapi', 'banka_oncesi'), git=False)
        if not ekler:
            self.assertEqual(k['v1_guncel'], {'rapor': 'test_x'})
        self.assertEqual([e['sira'] for e in k['teknik_ekler']], list(range(1, len(ekler) + 1)))
        self.assertEqual(k['zincir']['kod'], kilit.kod_kimlikleri())

    def test_kilit_zinciri_dondurmayla(self):
        kt = {'zincir': {}, 'v1_guncel': {'rapor': 'r'}, 'teknik_ekler': [{'sira': 1, 'tur': 'kapi', 'sha256': 's'}]}
        d = {'kilit_yolu': 'ciktilar/v8_kilit_20261001/KILIT.json', 'kilit_sha256': A.sha_bayt(KILIT.read_bytes()),
             'kilit_commit': KOMMIT, 'v1_guncel': {'rapor': 'r'},
             'teknik_ekler': [{'sira': 1, 'tur': 'kapi', 'sha256': 's', 'commit': 'c' * 40}]}
        with mock.patch.object(A, 'kilit_tam', return_value=kt) as z:
            self.assertIs(A.kilit_zinciri(d), kt)
            self.assertEqual(z.call_args.args[2], ('c' * 40,))
            for bozuk in (dict(d, v1_guncel={'rapor': 'baska'}), dict(d, teknik_ekler=[]),
                          dict(d, teknik_ekler=[dict(d['teknik_ekler'][0], sha256='t')]),
                          dict(d, kilit_sha256='0' * 64)):
                with self.assertRaises(A.AcilisHatasi):
                    A.kilit_zinciri(bozuk)


if __name__ == '__main__':
    unittest.main()
