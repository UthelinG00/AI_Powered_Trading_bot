"""Tek atış betiğinin ortak katmanı ve betikler (banka_kos/acilis.py, banka_kos/parite.py, veri_denetim.py,
banka_kos.py; BANKA §3.7 netleştirme 20): dönemler (banka, kuru), T1 kimlik denetimi, ACILIS denetimi, kilitli
filtre görüntüsü, kuru zincirde VERI_DENETIM → hazırlık kapıları → işçi bağlamı, T5 paritesi. Sentetik D biçimli paket;
gerçek D ya da banka verisi okunmaz."""
import io
import json
import re
import shutil
import sys as _sys
import tempfile
import unittest
import zipfile
from dataclasses import replace
from datetime import datetime, timezone
from pathlib import Path as _Path
from types import SimpleNamespace

import numpy as np

TESTLER_DIR = _Path(__file__).resolve().parent
V8_DIR = TESTLER_DIR.parent
for _d in (V8_DIR, TESTLER_DIR):
    if str(_d) not in _sys.path:
        _sys.path.insert(1, str(_d))

import banka_kos as _paket  # noqa: E402,F401  (paket; betik dosyası değil)
from banka_kos import acilis as A  # noqa: E402
from banka_kos import ayar  # noqa: E402
from banka_kos import parite as PR  # noqa: E402
from banka_kos.veri_denetim import kanonik  # noqa: E402

H = 3_600_000


def _ms(y, a, g):
    return int(datetime(y, a, g, tzinfo=timezone.utc).timestamp() * 1000)


def _betik(ad):
    import importlib.util
    spec = importlib.util.spec_from_file_location(f'betik_{ad}', V8_DIR / f'{ad}.py')
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def _zip(yol: _Path, metin: str):
    yol.parent.mkdir(parents=True, exist_ok=True)
    b = io.BytesIO()
    with zipfile.ZipFile(b, 'w', zipfile.ZIP_DEFLATED) as z:
        z.writestr(yol.with_suffix('.csv').name, metin)
    yol.write_bytes(b.getvalue())


def _d_paketi(kok: _Path, semboller, bas_ms, bit_ms, tohum=7):
    rng = np.random.default_rng(tohum)
    t = np.arange(bas_ms, bit_ms, H, dtype=np.int64)
    satirlar = []
    for i, s in enumerate(semboller):
        p = 100.0 * (i + 1) * np.exp(np.cumsum(rng.normal(0, 0.004, len(t))))
        k = ['open_time,open,high,low,close,volume,close_time,quote_volume,count,taker_buy_volume,'
             'taker_buy_quote_volume,ignore']
        k += [f'{a},{x:.6f},{x * 1.002:.6f},{x * 0.998:.6f},{x:.6f},10,{a + H - 1},{1e6:.1f},5,1,1,0' for a, x in zip(t, p)]
        _zip(kok / f'ham/klines/{s}/{s}-1h.zip', '\n'.join(k) + '\n')
        f = ['calc_time,funding_interval_hours,last_funding_rate'] + [f'{a},8,0.0001' for a in t[::8]]
        _zip(kok / f'ham/fundingRate/{s}/{s}-fundingRate.zip', '\n'.join(f) + '\n')
    import hashlib
    for p in sorted(kok.rglob('*.zip')):
        satirlar.append({'yol': p.relative_to(kok).as_posix(), 'sha256': hashlib.sha256(p.read_bytes()).hexdigest(),
                         'durum': 'TAMAM'})
    (kok / 'MANIFEST.jsonl').write_text('\n'.join(json.dumps(r) for r in satirlar) + '\n', encoding='utf-8')


def _filtre_klasoru(kok: _Path, semboller):
    import hashlib
    ham = json.dumps({'symbols': [{'symbol': s, 'status': 'TRADING', 'contractType': 'PERPETUAL', 'filters': [
        {'filterType': 'LOT_SIZE', 'stepSize': '0.001'}, {'filterType': 'MARKET_LOT_SIZE', 'stepSize': '0.01'},
        {'filterType': 'MIN_NOTIONAL', 'notional': '5'}]} for s in semboller]}).encode('ascii')
    kok.mkdir(parents=True, exist_ok=True)
    (kok / 'exchangeInfo_ham.json').write_bytes(ham)
    (kok / 'ALINMA.json').write_text(json.dumps({'exchangeInfo_ham_sha256': hashlib.sha256(ham).hexdigest()}),
                                     encoding='ascii')


class DonemTest(unittest.TestCase):
    def test_ay_ekle(self):
        self.assertEqual(A.ay_ekle(_ms(2023, 10, 1), 6), _ms(2024, 4, 1))
        self.assertEqual(A.ay_ekle(_ms(2026, 7, 1), -3), _ms(2026, 4, 1))
        self.assertEqual(A.ay_ekle(_ms(2023, 11, 1), 14), _ms(2025, 1, 1))
        with self.assertRaises(ValueError):
            A.ay_ekle(_ms(2023, 10, 2), 1)

    def test_kuru_ve_banka_donemi(self):
        seri = SimpleNamespace(acilis_ms=np.array([_ms(2023, 7, 1)], dtype=np.int64))
        alt = SimpleNamespace(acilis_ms=np.array([_ms(2023, 8, 1) + 5 * H], dtype=np.int64))
        veri = SimpleNamespace(barlar={'BTCUSDT': seri, 'ETHUSDT': seri, 'XUSDT': alt})
        d = A.kuru_donemi(veri)
        self.assertEqual((d.motor_bas_ms, d.t0_z1_ms), (_ms(2023, 7, 1), _ms(2023, 10, 1)))
        self.assertEqual(d.z1_dilim_sinir, (_ms(2024, 4, 1), _ms(2024, 10, 1), _ms(2025, 4, 1)))
        self.assertEqual((d.birincil_son_ms, d.d_bas_ms, d.d_bit_ms), (_ms(2025, 10, 1), _ms(2025, 10, 1), _ms(2026, 4, 1)))
        self.assertEqual((d.z2_bas_ms, d.z2_son_ms), (_ms(2026, 4, 1), _ms(2026, 7, 1)))
        b = A.banka_donemi(veri)
        self.assertEqual((b.t0_z1_ms, b.birincil_son_ms, b.z2_son_ms), (_ms(2023, 10, 1), ayar.BIRINCIL_SON_MS,
                                                                        ayar.Z2_SON_MS))
        with self.assertRaises(A.AcilisHatasi):
            A.kuru_donemi(SimpleNamespace(barlar={'BTCUSDT': seri}))


class KimlikVeAcilisTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.guncel = A.kimlikler()
        cls.k = _Path(tempfile.mkdtemp(prefix='acilis_'))

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.k, ignore_errors=True)

    def test_t1(self):
        d = dict(self.guncel, mimari='A')
        self.assertEqual(A.t1_denetimi(d, self.guncel), [])
        self.assertIn('motor_sha256', A.t1_denetimi(dict(d, motor_sha256='0' * 64), self.guncel))
        self.assertIn('tohum_banka_turetimi', A.t1_denetimi(dict(d, tohum_banka=d['tohum_banka'] + 1), self.guncel))
        # 20 l: teknik düzeltme sonrası kayıt ilk dondurmayı (yol + sha256) gösterir; tohum ilk kayıttan.
        ilk = dict(d, motor_sha256='ab' * 32, tohum_banka=A.tohum_turet('ab' * 32))
        b = json.dumps(ilk).encode('utf-8')
        (self.k / 'ilk.json').write_bytes(b)
        gos = {'yol': 'ilk.json', 'sha256': A.sha_bayt(b)}
        yeni = dict(d, tohum_banka=ilk['tohum_banka'], ilk_dondurma=gos)
        self.assertEqual(A.t1_denetimi(yeni, self.guncel, self.k), [])
        for bozuk in (dict(yeni, ilk_dondurma=dict(gos, sha256='0' * 64)), dict(yeni, tohum_banka=1),
                      dict(yeni, ilk_dondurma=dict(gos, yol='yok.json'))):
            self.assertIn('ilk_dondurma', A.t1_denetimi(bozuk, self.guncel, self.k))
        self.assertIn('tohum_banka_turetimi', A.t1_denetimi(dict(d, ilk_motor_sha256='ab' * 32,
                                                                   tohum_banka=A.tohum_turet('ab' * 32)), self.guncel))
        self.assertEqual(self.guncel['tohum_banka'], int(self.guncel['motor_sha256'][:16], 16) % 2 ** 32)

    def _acilis(self, **k):
        a = {'mimari': 'A', 'adaylar': ['A1USDT', 'A2USDT', 'A3USDT', 'BTCUSDT'], 'k_coinleri': ['A1USDT'],
             'd_coinleri': ['A2USDT', 'A3USDT'], 'gorulmus_gunler': [f'2021-0{i}-15' for i in range(1, 8)],
             'banka_kok': 'x', 'anonim_anahtar': 'y', 'sureklilik_sorunu': 0}
        a.update(k)
        y = self.k / 'ACILIS.json'
        y.write_text(json.dumps(a), encoding='utf-8')
        return y

    def test_acilis(self):
        with self.assertRaises(A.AcilisHatasi):                                     # |K| = 80, |D| = 120 (20 j)
            A.acilis_oku(self._acilis(), {'mimari': 'A'})
        a, h = A.acilis_oku(self._acilis(), {'mimari': 'A'}, boyut=False)
        self.assertEqual(len(h), 64)
        self.assertEqual(A.veri_adaylari(a), ('A1USDT', 'A2USDT', 'A3USDT', 'BTCUSDT', 'ETHUSDT'))
        for bozuk in ({'k_coinleri': ['A2USDT']}, {'k_coinleri': ['ZZUSDT']}, {'gorulmus_gunler': ['2021-01-01'] * 7},
                      {'mimari': 'C'}, {'sureklilik_sorunu': -1}, {'adaylar': ['A1USDT', 'A1USDT', 'A2USDT', 'A3USDT']},
                      {'k_coinleri': []}, {'adaylar': ['A1USDT', 'A2USDT', 'A3USDT', 'A4USDT']},
                      {'k_coinleri': ['A1USDT', 'BTCUSDT']}):
            with self.assertRaises(A.AcilisHatasi, msg=str(bozuk)):
                A.acilis_oku(self._acilis(**bozuk), boyut=False)
        with self.assertRaises(A.AcilisHatasi):
            A.acilis_oku(self._acilis(), {'mimari': 'B'}, boyut=False)

    def test_damga_farki(self):
        a = {'birimler': [['x', '1', 'e1'], ['y', '2', 'e2'], ['z', '3', 'e3']]}
        b = {'birimler': [['x', '1', 'f1'], ['y', '9', 'f2'], ['w', '4', 'f4']]}
        self.assertEqual(A.damga_farki(a, b), {'ayni': ['x'], 'farkli': ['y'], 'yalniz_a': ['z'], 'yalniz_b': ['w']})

    def test_filtreler(self):
        f = self.k / 'filtre'
        _filtre_klasoru(f, ['BTCUSDT', 'XUSDT'])
        t, r = A.filtreler_kur(['BTCUSDT', 'XUSDT', 'YUSDT'], f)
        self.assertEqual(t, {'BTCUSDT': (0.01, 5.0), 'XUSDT': (0.01, 5.0)})
        self.assertEqual((r['filtreli'], r['filtresiz_sembol']), (2, 1))
        (f / 'exchangeInfo_ham.json').write_bytes(b'{"symbols": []}')
        with self.assertRaises(A.AcilisHatasi):
            A.filtreler_kur(['BTCUSDT'], f)


class KuruZincirTest(unittest.TestCase):
    """Kuru kip: veri_denetim.py → banka_kos.hazirla kapıları → işçi bağlamı (motor koşusu yok)."""
    SEM = ('BTCUSDT', 'ETHUSDT', 'XUSDT')

    @classmethod
    def setUpClass(cls):
        cls.k = _Path(tempfile.mkdtemp(prefix='kuru_'))
        _d_paketi(cls.k / 'd', cls.SEM, ayar.D_BAS_MS, ayar.D_BIT_MS)
        _filtre_klasoru(cls.k / 'filtre', ('BTCUSDT', 'ETHUSDT'))
        cls.ek = {'d_kok': str(cls.k / 'd'), 'evren': cls.SEM, 'filtre_klasoru': str(cls.k / 'filtre')}
        cls.cikti = cls.k / 'kosu'
        cls.VD, cls.BK = _betik('veri_denetim'), _betik('banka_kos')
        cls.kod = cls.VD.main(['kuru', str(cls.cikti), 'A'], cls.ek)
        cls.vd_yol = cls.cikti / 'denetim' / 'VERI_DENETIM.json'
        cls.vd_bayt = cls.vd_yol.read_bytes()

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.k, ignore_errors=True)

    def setUp(self):
        self.vd_yol.write_bytes(self.vd_bayt)

    def test_veri_denetimi(self):
        self.assertEqual(self.kod, 0)
        vd = json.loads(self.vd_bayt)
        self.assertFalse(vd['denetim']['karar']['T2'])
        self.assertEqual(vd['donem']['t0_z1_ms'], _ms(2023, 10, 1))
        self.assertEqual((vd['aday'], vd['dosya_sayisi'], vd['filtre']['filtresiz_sembol']), (3, 6, 1))
        self.assertEqual(vd['denetim']['checksum']['onarilamayan'], 0)
        self.assertEqual(vd['denetim']['k_coin'], 1)
        self.assertIsNone(re.search(r'XUSDT', self.vd_bayt.decode('ascii')))          # coin adı yok (açık grup)
        self.assertTrue((self.cikti / 'KURU_ALICI.txt').exists() and (self.cikti / 'ANONIM_ANAHTAR.bin').exists())

    def test_hazirlik_ve_baglam(self):
        arg = self.BK.argumanlar(['kuru', str(self.cikti), 'A', '--isci', '2'])
        self.assertEqual(arg['isci'], 2)
        tanim, kimlik = self.BK.hazirla(arg, self.ek)
        self.assertIsNone(re.search(r'XUSDT', kanonik(kimlik).decode('ascii')))
        self.assertEqual(kimlik['veri_denetim_json_sha256'], A.sha_bayt(self.vd_bayt))
        bag = A.baglam_kur(tanim)
        self.assertEqual((bag.t0_z1_ms, bag.birincil_son_ms, bag.z2_son_ms),
                         (_ms(2023, 10, 1), _ms(2025, 10, 1), ayar.D_BIT_MS))
        self.assertEqual(bag.k_adaylar, self.SEM)
        self.assertEqual(bag.gorulmus_gunler, ())
        self.assertEqual(bag.filtreler['BTCUSDT'], (0.01, 5.0))
        self.assertEqual(set(bag.anonim), set(self.SEM))
        for alan in ('veri_kimligi', 'filtre_tablo_sha256', 'har_sonuc_sha256', 'anonim_anahtar_sha256'):
            with self.assertRaises(A.AcilisHatasi, msg=alan):                        # 20 g: her işçi denetler
                A.baglam_kur(dict(tanim, **{alan: '0' * 64}))
        self.assertEqual(kimlik['tohum_banka'], A.kimlikler()['tohum_banka'])
        # Karşılaştırma koşusu (20 k): başka tohum → VERI_DENETIM meta'sı tutmaz (aynı argümanlarla yeniden üretilmeli).
        arg_t = self.BK.argumanlar(['kuru', str(self.cikti), 'A', '--tohum', '7', '--anonim-anahtar',
                                    str(self.cikti / 'ANONIM_ANAHTAR.bin')])
        self.assertEqual((arg_t['tohum'], arg_t['anonim_anahtar'][-18:]), (7, 'ANONIM_ANAHTAR.bin'))
        with self.assertRaises(A.AcilisHatasi):
            self.BK.hazirla(arg_t, self.ek)

    def test_d_paketi_tamligi(self):
        # 20 l (3): D MANIFEST'inde TAMAM olup diskte olmayan dosya → T2 (yükleyiciden önce), çıkış 3.
        import hashlib
        d2 = self.k / 'd2'
        shutil.copytree(self.k / 'd', d2)
        with (d2 / 'MANIFEST.jsonl').open('a', encoding='utf-8') as f:
            f.write(json.dumps({'yol': 'ham/klines/XUSDT/XUSDT-1h-2026-01.zip', 'durum': 'TAMAM',
                                'sha256': hashlib.sha256(b'x').hexdigest()}) + '\n')
        c = self.k / 'kosu_d2'
        self.assertEqual(self.VD.main(['kuru', str(c), 'A'], dict(self.ek, d_kok=str(d2))), 3)
        vd = json.loads((c / 'denetim' / 'VERI_DENETIM.json').read_text(encoding='ascii'))
        self.assertEqual(vd['denetim']['d_eksik_dosya'], 1)

    def test_hata_siniri(self):
        # 20 f: beklenmeyen hata (yol içeren yükleyici istisnası) mühürlenir; ekrana sabit mesaj, çıkış 6.
        c = self.k / 'kosu_hata'
        self.assertEqual(self.VD.main(['kuru', str(c), 'A'], dict(self.ek, d_kok=str(self.k / 'yok'))), 6)
        self.assertEqual(len(list((c / 'sonuc' / 'hata').glob('veri_denetim.age'))), 1)

    def test_kapilar(self):
        arg = self.BK.argumanlar(['kuru', str(self.cikti), 'A'])
        vd = json.loads(self.vd_bayt)
        for bozuk in (dict(vd, denetim=dict(vd['denetim'], karar={'T2': True, 'nedenler': ['x']})),
                      dict(vd, veri_kimligi='0' * 64), dict(vd, mimari='B'),
                      dict(vd, kimlikler=dict(vd['kimlikler'], motor_sha256='0' * 64))):
            self.vd_yol.write_bytes(kanonik(bozuk))
            with self.assertRaises(A.AcilisHatasi):
                self.BK.hazirla(arg, self.ek)
        self.assertEqual(self.BK.main(['kuru', str(self.cikti), 'A'], self.ek), 4)   # 20 g: dosya ≠ yeniden hesap


class BankaT2Test(unittest.TestCase):
    """Banka kipi: onarılamayan manifest satırı ve manifestte olup diskte olmayan dosya → T2 (çıkış 3) yükleyiciden
    önce; banka_kos aynı hesabı yeniden yapar ve T2 ile durur. DONDURMA güncel kimliklerden kurulur."""

    def setUp(self):
        from banka_kos import age
        self.k = _Path(tempfile.mkdtemp(prefix='banka_t2_'))
        g = A.kimlikler()
        _, alici = age.anahtar_uret()
        (self.k / 'DONDURMA.json').write_text(json.dumps(dict(g, mimari='A', sifreleme_acik_anahtar=alici)),
                                              encoding='utf-8')
        self.banka = self.k / 'banka'
        (self.banka / 'ham/klines/A1USDT').mkdir(parents=True)
        (self.k / 'dbos').mkdir()
        (self.k / 'dbos' / 'MANIFEST.jsonl').write_text('', encoding='utf-8')
        (self.k / 'ACILIS.json').write_text(json.dumps({
            'mimari': 'A', 'adaylar': ['A1USDT', 'A2USDT'], 'k_coinleri': ['A1USDT'], 'd_coinleri': ['A2USDT'],
            'd_kok': str(self.k / 'dbos'),
            'gorulmus_gunler': [f'2021-0{i}-15' for i in range(1, 8)], 'banka_kok': str(self.banka),
            'anonim_anahtar': str(self.k / 'anahtar.bin'), 'sureklilik_sorunu': 0}), encoding='utf-8')
        self.arg = ['banka', str(self.k / 'kosu'), str(self.k / 'ACILIS.json'), str(self.k / 'DONDURMA.json')]
        self.ek = {'boyut_denetimi': False, 'kilit_denetimi': False}
        self.VD, self.BK = _betik('veri_denetim'), _betik('banka_kos')

    def tearDown(self):
        shutil.rmtree(self.k, ignore_errors=True)

    def _manifest(self, satirlar):
        (self.banka / 'BANKA_MANIFEST.jsonl').write_text('\n'.join(json.dumps(r) for r in satirlar) + '\n',
                                                          encoding='utf-8')

    def test_checksum_hatasi(self):
        self._manifest([{'yol': 'ham/klines/A1USDT/x.zip', 'sha256': 'a' * 64, 'checksum': 'b' * 64,
                         'durum': 'CHECKSUM_HATASI'}])
        self.assertEqual(self.VD.main(self.arg, self.ek), 3)
        self.assertEqual(self.BK.main(self.arg, self.ek), 3)

    def test_eksik_dosya(self):
        self._manifest([{'yol': 'ham/klines/A1USDT/yok.zip', 'sha256': 'a' * 64, 'checksum': 'a' * 64,
                         'durum': 'TAMAM'}])
        self.assertEqual(self.VD.main(self.arg, self.ek), 3)
        vd = json.loads((self.k / 'kosu/denetim/VERI_DENETIM.json').read_text(encoding='ascii'))
        self.assertEqual(vd['denetim']['checksum']['eksik_dosya'], 1)

    def test_kilit_zinciri_zorunlu(self):
        # UYGULAMA_EK U2: DONDURMA kilit yolu/sha'sı yoksa (ya da zincir doğrulanmazsa) T1, çıkış 4.
        self._manifest([])
        self.assertEqual(self.VD.main(self.arg, {'boyut_denetimi': False}), 4)

    def test_t1(self):
        d = json.loads((self.k / 'DONDURMA.json').read_text(encoding='utf-8'))
        (self.k / 'DONDURMA.json').write_text(json.dumps(dict(d, motor_sha256='0' * 64)), encoding='utf-8')
        self.assertEqual(self.VD.main(self.arg, self.ek), 4)
        self.assertEqual(self.BK.main(self.arg, self.ek), 4)


class PariteTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from fikstur.saatlik_veri import SENARYO_GUN, SENARYO_T0_GUN, gun_ms, saat_ms, senaryo_verisi
        from motor.geri_test import KosuAyarlari, kos
        from motor.tipler import Parametreler
        cls.P = Parametreler()
        cls.veri = senaryo_verisi()
        cls.s = kos(cls.veri, KosuAyarlari(t0_ms=gun_ms(SENARYO_T0_GUN), t_son_ms=saat_ms(SENARYO_GUN * 24 - 1)), cls.P)

    def test_parite_temiz_ve_bozuk(self):
        r = PR.parite(self.s, self.veri, 1.0, self.P, {}, 12345, n=8)
        self.assertEqual((r['secilen'], r['hata']), (8, 0))
        self.assertEqual(r, PR.parite(self.s, self.veri, 1.0, self.P, {}, 12345, n=8))     # deterministik
        bozuk = replace(self.s, kararlar=[replace(k, evren=tuple(k.evren) + ('YOKUSDT',)) for k in self.s.kararlar])
        self.assertEqual(PR.parite(bozuk, self.veri, 1.0, self.P, {}, 12345, n=8)['hata'], 8)
        w = self.s.kararlar[5]
        kaydir = replace(w, hedef=replace(w.hedef, w_yildiz={c: v + 1e-13 for c, v in w.hedef.w_yildiz.items()}))
        self.assertTrue(PR.karar_esit(kaydir, w))                                     # 1e-12 toleransı
        kaydir = replace(w, hedef=replace(w.hedef, w_yildiz={c: v + 1e-9 for c, v in w.hedef.w_yildiz.items()}))
        self.assertEqual(PR.karar_esit(kaydir, w), not w.hedef.w_yildiz)

    def test_uzlasma_gunu(self):
        # 20 h: delist uzlaşması olan gün; önek T'deki uzlaşmayı içerir (geri testin karar_ver'e verdiği durum).
        kayit = self.s.gunluk.kayitlar()
        uz = {k.damga_ms for k in kayit if k.tur == 'uzlasma'}
        idx = [i for i, k in enumerate(self.s.kararlar) if int(k.hedef.t_ms) in uz]
        self.assertTrue(idx)
        for i in idx:
            self.assertTrue(PR.karar_paritesi(self.s, self.veri, i, 1.0, self.P, {}))


if __name__ == '__main__':
    unittest.main()
