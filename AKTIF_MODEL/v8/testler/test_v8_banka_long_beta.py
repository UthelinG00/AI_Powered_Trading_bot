"""R3 long-beta kitabı (banka_kos/long_beta.py; BANKA §3.7 netleştirme 13, BK-14): ağırlık ve bütçe kuralı, NW
regresyonu, karşılaştırma ölçeği; sentetik carry senaryosunda gerçek R3 koşusu: yalnız long, aylık tahsis a_t'de ve
bütçe içinde, aradaki günlerde yalnız çıkış hedefi, muhasebe kapısı, A ve B'de aynı kitap. Performans ölçümü değildir."""
import json
import sys as _sys
import unittest
from dataclasses import replace
from pathlib import Path as _Path

import numpy as np

TESTLER_DIR = _Path(__file__).resolve().parent
V8_DIR = TESTLER_DIR.parent
for _dir in (V8_DIR, TESTLER_DIR):
    if str(_dir) not in _sys.path:
        _sys.path.insert(1, str(_dir))

from banka_kos import long_beta as LB  # noqa: E402
from banka_kos import yurutucu as Y  # noqa: E402
from motor.geri_test import KosuAyarlari  # noqa: E402
from motor.gorunum import GUN_MS, SAAT_MS, aylik_secim_gunu_mu  # noqa: E402
from test_v8_banka_yurutucu import _bag, _birim  # noqa: E402


class SafFonksiyonTest(unittest.TestCase):
    def test_ters_sigma_ve_butce(self):
        w = LB.ters_sigma_agirlik([0.2, 0.4, 0.8])
        self.assertAlmostEqual(float(w.sum()), 1.0, places=15)
        np.testing.assert_allclose(w * np.array([0.2, 0.4, 0.8]), np.full(3, w[0] * 0.2))
        with self.assertRaises(ValueError):
            LB.ters_sigma_agirlik([0.2, 0.0])
        self.assertEqual(LB.r3_butce({'A': 0.3, 'B': 0.1, 'C': 0.25}, {'A'}), 1.0 - 0.35)
        self.assertEqual(LB.r3_butce({'X': 1.4}, {'A'}), 0.0)                 # satılamayan pozisyon bütçeyi aşarsa 0
        self.assertEqual(LB.r3_butce({}, set()), 1.0)

    def test_nw_ols(self):
        rng = np.random.default_rng(7)
        x = rng.normal(0, 0.02, 500)
        y = 0.001 + 0.6 * x + rng.normal(0, 0.01, 500)
        r = LB.nw_ols(y, x)
        b = np.linalg.lstsq(np.column_stack([np.ones(500), x]), y, rcond=None)[0]
        self.assertAlmostEqual(r['alfa'], float(b[0]), places=12)
        self.assertAlmostEqual(r['beta'], float(b[1]), places=12)
        self.assertTrue(np.isfinite(r['t_alfa']) and r['t_beta'] > 10)

    def test_karsilastirma_olcegi(self):
        rng = np.random.default_rng(3)
        rp = rng.normal(0.0005, 0.01, 300)
        r3 = 0.5 * rp + rng.normal(0.0002, 0.02, 300)
        k = LB.r3_karsilastirma(rp, r3)
        self.assertAlmostEqual(k['olcek'] * np.std(r3, ddof=1), np.std(rp, ddof=1), places=12)
        self.assertAlmostEqual(k['sr_farki'], k['sr_birincil'] - k['sr_r3'], places=12)
        k2 = LB.r3_karsilastirma(rp, 3.0 * r3)                                 # ölçek SR ve korelasyonu değiştirmez
        for a in ('sr_r3', 'korelasyon', 't_alfa_nw', 'alfa_gunluk'):
            self.assertAlmostEqual(k[a], k2[a], places=9)
        with self.assertRaises(ValueError):
            LB.r3_karsilastirma(rp, r3[:-1])

    def test_karsilastirma_tanimsiz_dallari(self):
        # Netleştirme 17 b: betimsel R3 hükmü durdurmaz.
        rp = np.random.default_rng(5).normal(0, 0.01, 50)
        self.assertEqual(LB.r3_karsilastirma(rp, np.zeros(50))['durum'], 'tanimsiz')        # R3 hiç pozisyon almadı
        self.assertEqual(LB.r3_karsilastirma(np.zeros(50), rp)['durum'], 'tanimsiz')
        self.assertEqual(LB.r3_karsilastirma(rp[:2], rp[:2])['gun'], 2)
        self.assertEqual(LB.r3_karsilastirma(np.array([]), np.array([]))['durum'], 'tanimsiz')


def _ms(y, a, g):
    from datetime import datetime, timezone
    return int(datetime(y, a, g, tzinfo=timezone.utc).timestamp() * 1000)


class _Baglam:
    def json(self):
        return {}


class R3KararDallariTest(unittest.TestCase):
    """r3_karar'ın sentetik koşuda oluşmayan dalları (ay içi çıkış, işlem dışı, reduce-only, bütçe): motor girdileri
    taklit edilir; karar mantığı ve devreden emir kuralı gerçek koddur."""

    def kur(self, t, a_t, sabit, w_mevcut, q, devreden, reduce_only=False, maskeli=('M',), sigma=None):
        from types import SimpleNamespace
        from unittest import mock
        from motor.durum import Emir, StratejiDurumu
        from motor.hijyen import MaskeKaydi
        from motor.tipler import Parametreler
        coinler = tuple(sorted(set(a_t) | set(sabit) | set(w_mevcut)))
        hedef = SimpleNamespace(coinler=coinler, a_t=tuple(a_t), sabit=tuple(sabit), w_mevcut=dict(w_mevcut),
                                fiyat_ref={c: 10.0 for c in coinler}, nav=1000.0, reduce_only=reduce_only,
                                json=lambda: {'a_t': list(a_t), 'w_mevcut': dict(w_mevcut)})
        girdiler = SimpleNamespace(gunluk={c: SimpleNamespace(sigma_ewma=0.5) for c in coinler})
        durum = StratejiDurumu(pozisyonlar=dict(q), evren=tuple(a_t), evren_ms=_ms(2021, 3, 1),
                               devreden={c: Emir(kalan=k, karar_ms=t - GUN_MS, maske_cikisi=False, tam_kapanis=False,
                                                 baglam=_Baglam()) for c, k in devreden.items()})
        maske = {c: MaskeKaydi(maskeli=True) for c in maskeli}
        yamalar = [mock.patch.object(LB, 'karar_bosluklari', return_value=(frozenset(), None)),
                   mock.patch.object(LB, 'maske_ilerlet', return_value=maske),
                   mock.patch.object(LB, 'evren_sec', return_value=SimpleNamespace(uyeler=tuple(a_t))),
                   mock.patch.object(LB, 'hedef_agirlik_ayrintili', return_value=(hedef, girdiler)),
                   mock.patch.object(LB, 'boyut_sigmalari',
                                     return_value=(np.array(sigma if sigma else [0.2] * len(a_t)), 0)),
                   mock.patch.object(LB, 'maliyet_baglami', return_value=_Baglam())]
        for y in yamalar:
            y.start()
            self.addCleanup(y.stop)
        return LB.r3_karar(SimpleNamespace(t_ms=t, barlar={}), durum, Parametreler(), {})

    def test_ay_ici_cikis_ve_devreden(self):
        t = _ms(2021, 3, 15)
        s = self.kur(t, a_t=('A',), sabit=('S',), w_mevcut={'A': 0.1, 'M': 0.05, 'S': 0.03, 'Z': 0.0},
                     q={'A': 10.0, 'M': 5.0, 'S': 3.0}, devreden={'A': 2.0, 'S': 1.0})
        self.assertEqual(s.bantli, {'M': 0.0})                              # yalnız a_t dışına düşen pozisyonlu isim
        self.assertEqual(set(s.niyetler), {'M'})
        e = s.niyetler['M']
        self.assertEqual((e.kalan, e.tam_kapanis, e.maske_cikisi), (-5.0, True, True))
        iptal = dict(s.iptaller)
        self.assertNotIn('A', iptal)                                        # tutulan ismin devreden emri sürer
        self.assertEqual(iptal['S']['sebep'], 'islem_disi')                 # işlem dışı: risk artıran parça iptal
        karar = s.kayitlar[0]
        self.assertEqual((karar.tur, karar.veri['r3']['aylik']), ('karar', False))

    def test_aylik_butce_ve_reduce_only(self):
        t = _ms(2021, 4, 1)
        w0 = {'A': 0.5, 'B': 0.0, 'S': 0.2}
        s = self.kur(t, a_t=('A', 'B'), sabit=('S',), w_mevcut=w0, q={'A': 50.0, 'S': 20.0}, devreden={},
                     maskeli=(), sigma=[0.2, 0.4])
        self.assertAlmostEqual(s.bantli['A'], 0.8 * 2 / 3, places=12)      # bütçe 1 − 0,2 (satılamayan S)
        self.assertAlmostEqual(s.bantli['B'], 0.8 / 3, places=12)
        self.assertNotIn('S', s.bantli)                                     # işlem dışına yeni emir yok
        self.assertTrue(s.kayitlar[0].veri['r3']['aylik'])
        s = self.kur(t, a_t=('A', 'B'), sabit=('S',), w_mevcut=w0, q={'A': 50.0, 'S': 20.0}, devreden={},
                     maskeli=(), sigma=[0.2, 0.4], reduce_only=True)
        self.assertEqual(s.bantli, {'A': 0.5, 'B': 0.0})                    # boşlukta risk artıran hedef yok
        self.assertEqual(s.niyetler, {})


class R3KosuTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.bag = _bag()
        cls.a = Y.birim_yurut(_birim('long_beta', 'A'), cls.bag)
        cls.b = Y.birim_yurut(_birim('long_beta', 'B'), cls.bag)
        bag = cls.bag
        t_son = bag.z2_son_ms - SAAT_MS
        takvim = Y._takvim(bag.veri, bag, t_son)
        p = replace(bag.parametreler, mimari='A', sigma_tahmincisi='HAR', har_takvimi=takvim, delist_h_long=0.10)
        cls.s = LB.kos_r3(bag.veri, KosuAyarlari(t0_ms=bag.motor_bas_ms, t_son_ms=t_son, L=1.0, maliyet_k=1.0,
                                                 nav0=1e5, filtreler=bag.filtreler), p)

    def test_cikti_bicimi_ve_muhasebe(self):
        duz, acik = self.a
        gun = (self.bag.z2_son_ms - self.bag.t0_z1_ms) // GUN_MS
        self.assertEqual(len(duz['nav_gunluk']), gun + 1)
        for a in ('brut_devir', 'net_devir', 'maliyet_payi', 'funding_payi'):
            self.assertEqual(len(duz[a]), gun)
        self.assertTrue(all(x >= 0 for x in duz['brut_devir'] + duz['maliyet_payi']))
        self.assertLess(acik['muhasebe']['coin_pnl_hata'], 1e-6)
        self.assertGreaterEqual(acik['aylik_karar_sayisi'], 2)
        json.dumps(duz)

    def test_a_ve_b_ayni_kitap(self):
        da, db = dict(self.a[0]), dict(self.b[0])
        self.assertEqual(da.pop('birim')['mimari'], 'A')
        self.assertEqual(db.pop('birim')['mimari'], 'B')
        self.assertEqual(da, db)
        self.assertEqual(self.a[1]['son_hash'], self.b[1]['son_hash'])

    def test_yalniz_long_ve_karar_kurallari(self):
        q = {}
        aylik_n = 0
        for k in self.s.gunluk.kayitlar():
            if k.tur == 'dolum':
                q[k.coin] = 0.0 if k.veri.get('tam_kapanis_son') else q.get(k.coin, 0.0) + k.miktar
                self.assertGreaterEqual(q[k.coin], -1e-9, k.coin)                       # yalnız long
            elif k.tur == 'uzlasma':
                q[k.coin] = 0.0
            elif k.tur == 'karar':
                v = k.veri
                aylik = v['r3']['aylik']
                self.assertEqual(aylik, aylik_secim_gunu_mu(k.damga_ms) or aylik_n == 0)
                a_t = set(v['r3']['a_t'])
                self.assertEqual(a_t, set(v['hedef']['a_t']))
                w = v['bantli']
                if aylik:
                    aylik_n += 1
                    pozitif = {c for c, x in w.items() if x > 0}
                    self.assertTrue(pozitif <= a_t)
                    disari = sum(abs(x) for c, x in v['hedef']['w_mevcut'].items() if c not in a_t)
                    beklenen = max(0.0, 1.0 - disari)
                    if not v['hedef']['reduce_only'] and a_t:
                        self.assertAlmostEqual(sum(w.values()), beklenen, places=12)
                    self.assertLessEqual(sum(w.values()) + disari, 1.0 + 1e-12)       # karar anında brüt ≤ 1
                else:
                    self.assertTrue(all(x == 0.0 for x in w.values()))                 # yalnız çıkış hedefi
                    self.assertTrue(all(c not in a_t for c in w))
        self.assertGreaterEqual(aylik_n, 2)

    def test_aradaki_gunlerde_devreden_surer(self):
        # Aylık olmayan karar devreden emri yalnız hedefi yenilenen (çıkış) isimde iptal eder; ötekiler sürer
        # (işlem dışı / reduce-only risk artıran parça hariç).
        hedefli = {}
        for k in self.s.gunluk.kayitlar():
            if k.tur == 'karar':
                hedefli[k.damga_ms] = (k.veri['r3']['aylik'], set(k.veri['bantli']))
            elif k.tur == 'devreden_iptal' and k.veri.get('sebep') in ('yeni_karar', 'yeni_niyet'):
                aylik, kume = hedefli[k.damga_ms]
                self.assertTrue(aylik or k.coin in kume, (k.damga_ms, k.coin))


if __name__ == '__main__':
    unittest.main()
