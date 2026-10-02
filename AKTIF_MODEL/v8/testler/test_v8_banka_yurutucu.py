"""Banka birim yürütücüsü (banka_kos/yurutucu.py; BANKA §3–§5, BK-1…BK-10): sentetik carry senaryosunda kısa dönemlerle.
Performans ölçümü değildir; çıktı biçimi, pencere uzunlukları, görülmüş gün dışlaması, null değişmezleri, lot kapalı."""
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

from banka_kos import anonim, ayar  # noqa: E402
from banka_kos import yurutucu as Y  # noqa: E402
from fikstur.saatlik_veri import CARRY_GUN, carry_senaryo_verisi, gun_ms  # noqa: E402
from kalibrasyon.yurutucu import har_paketi  # noqa: E402

G = 86_400_000


def _bag():
    veri = carry_senaryo_verisi()
    return Y.BankaBaglami(
        veri=veri, k_adaylar=('A10', 'A11', 'A12', 'A13', 'BTCUSDT', 'ETHUSDT'), motor_bas_ms=gun_ms(0),
        t0_z1_ms=gun_ms(92), gorulmus_gunler=(gun_ms(95),), filtreler={'BTCUSDT': (0.001, 5.0), 'A00': (1.0, 5.0)},
        beta=har_paketi()[1], tohum_banka=12345, anonim=anonim.kimlikler(bytes(range(32)), veri.barlar),
        birincil_son_ms=gun_ms(120), z1_dilim_sinir=(gun_ms(99), gun_ms(106), gun_ms(113)), z2_son_ms=gun_ms(CARRY_GUN))


def _birim(grup, mimari='A', **k):
    return ayar._birim(grup, mimari, **k)


class YurutucuTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.bag = _bag()
        cls.a = Y.birim_yurut(_birim('birincil'), cls.bag)
        cls.b = Y.birim_yurut(_birim('birincil', 'B'), cls.bag)

    def test_bicim_ve_pencere(self):
        duz, acik = self.a
        self.assertEqual(len(duz['nav_gunluk']), (gun_ms(CARRY_GUN) - gun_ms(92)) // G + 1)
        self.assertEqual(duz['olcum']['T'], 27)                                  # 28 gün − 1 görülmüş gün
        self.assertEqual(len(duz['stres_nesneleri']['D90']), 28)
        self.assertTrue(all(x >= 0 for x in duz['stres_nesneleri']['SQ']))
        self.assertLess(acik['muhasebe']['coin_pnl_hata'], 1e-6)
        self.assertEqual((acik['parite']['secilen'], acik['parite']['hata']), (20, 0))       # T5 (20 d)
        self.assertTrue(set(duz['olcum']['alt_katki_anonim']) <= set(self.bag.anonim.values()))
        json.dumps(duz)                                                          # JSON'a çevrilebilir

    def test_b_ayristirma(self):
        duz, acik = self.b
        self.assertIn('ayristirma_hata', acik['muhasebe'])
        self.assertEqual(acik['parite']['hata'], 0)                                        # B: carry durumu dahil
        self.assertEqual(duz['olcum']['T'], 27)

    def test_b_birincil_disi_birimler(self):
        # Codex T18-CIDDI-3: B'nin ızgara, Kelly, BTC/ETH çıkarma ve K-evren birimleri ayrıştırmasız yürür (B5 yalnız
        # birincilde); Kelly/ızgara stres nesnelerini, K-evren B9 serisini taşır.
        self.assertIsNotNone(self.b[0]['olcum']['b5_pay'])
        for b in (_birim('izgara', 'B', nav0=1e6, maliyet_k=2.0), _birim('kelly', 'B', L=2.0, maliyet_k=1.0),
                  _birim('cikarma_btc_eth', 'B', cikan='BTCUSDT'), _birim('k_evren', 'B', evren='K')):
            duz, acik = Y.birim_yurut(b, self.bag)
            self.assertIsNone(duz['olcum']['b5_pay'], b['grup'])
            self.assertNotIn('ayristirma_hata', acik['muhasebe'])
            self.assertEqual(len(duz['nav_gunluk']), len(self.b[0]['nav_gunluk']))
            if b['grup'] in ('izgara', 'kelly'):
                self.assertEqual(len(duz['stres_nesneleri']['DM']), 28)
            if b['grup'] == 'k_evren':
                self.assertEqual(len(duz['b9_seri']), (gun_ms(CARRY_GUN) - gun_ms(92)) // G)
            json.dumps(duz)

    def test_nav_zinciri_getiriyle_tutarli(self):
        duz, _ = self.a
        nav = np.array(duz['nav_gunluk'])
        r = nav[1:29] / nav[:28] - 1
        np.testing.assert_allclose(np.delete(r, 3), np.array(duz['olcum']['r']), rtol=0, atol=1e-12)

    def test_k_evren_null_lot(self):
        k, _ = Y.birim_yurut(_birim('k_evren', evren='K'), self.bag)
        self.assertEqual(len(k['b9_seri']), (gun_ms(CARRY_GUN) - gun_ms(92)) // G)
        n, acik = Y.birim_yurut(_birim('null', null_no=1), self.bag)
        self.assertTrue(acik['null_degismez']['gecti'])
        self.assertEqual(set(n), {'birim', 'sr', 'r17'})
        lot, _ = Y.birim_yurut(_birim('lot_kapali', lot=False), self.bag)
        self.assertEqual(len(lot['nav_gunluk']), len(self.a[0]['nav_gunluk']))

    def test_kosu_tanilari(self):
        # BANKA §3.7 netleştirme 14: R5, R6, R7 birincilde; R14 demo NAV biriminde.
        t = self.a[0]['tanilar']
        self.assertEqual(set(t), {'R5', 'R6', 'R7'})
        r5, r6, r7 = t['R5'], t['R6'], t['R7']
        self.assertEqual(r5['karar_gunu'], 27)
        self.assertEqual(r5['gun_sonu'], 27)
        for a in ('t4a_orani', 's1_asim_orani', 's2_asim_orani', 'hedefe_ulasilamayan_orani'):
            self.assertTrue(r5[a] != r5[a] or 0.0 <= r5[a] <= 1.0, a)
        self.assertTrue(all(0.0 <= v <= 1.0 for v in r5['hedef_baglama_orani'].values()))
        self.assertEqual(r6['gun'], 27)
        self.assertGreaterEqual(r6['tek_yon_devir_yillik'], 0.0)
        self.assertGreaterEqual(r6['maliyet_payi_yillik'], 0.0)
        self.assertGreater(r6['niyet'], 0)
        self.assertGreaterEqual(r6['gecikme_saat_q50'], 1.0)                      # dolum en erken 01:00
        self.assertGreater(r7['gerceklesen_vol_orani'], 0.0)
        self.assertIn('rv_sigma2_q50', r7)
        self.assertNotIn('rv_sigma2_q50', self.b[0]['tanilar']['R7'])            # R7 tahminci yalnız A
        json.dumps(t)
        demo, _ = Y.birim_yurut(_birim('demo_nav', nav0=ayar.DEMO_NAV), self.bag)
        self.assertIn('lot_minnotional_alti_orani', demo['r14'])
        self.assertNotIn('tanilar', demo)

    def test_piyasa_serileri_r13b_r17(self):
        # Netleştirme 15: piyasa serileri Z1 başından Z2 sonuna; BTC katkısı + artık katkı = kitabın günlük getirisi.
        duz = self.a[0]
        pz = duz['piyasa']
        gun = (self.bag.z2_son_ms - self.bag.t0_z1_ms) // G
        for a in ('r_btc', 'r_alt', 'btc_katki', 'artik_katki'):
            self.assertEqual(len(pz[a]), gun, a)
        self.assertTrue(all(x is not None for x in pz['r_btc']))
        nav = np.array(duz['nav_gunluk'])
        r = nav[1:] / nav[:-1] - 1
        toplam = np.array(pz['btc_katki']) + np.array(pz['artik_katki'])
        np.testing.assert_allclose(toplam, r, rtol=0, atol=1e-9)
        self.assertGreater(pz['beta_coin'], 0)
        self.assertGreaterEqual(duz['r13b']['coin'], 1)                          # A00 adım 1,0; BTC 0,001
        self.assertEqual(set(duz['r17']), {'maske_gunu', 'dolgu_saati', 'bosluk_saati', 'evren_ort'})
        self.assertGreater(duz['r17']['evren_ort'], 0)
        # B8 serisi (17 h) birincil ölçümün B8 SR'ını birebir yeniden üretir.
        from banka import olcutler as o
        b8 = np.array(duz['b8_r'])[:28]
        b8 = np.delete(b8, 3)                                                    # görülmüş gün (95) düşülür
        self.assertAlmostEqual(o.sharpe(b8), duz['olcum']['b8_sr'], places=10)
        n, _ = Y.birim_yurut(_birim('null', null_no=2), self.bag)
        self.assertEqual(set(n['r17']), {'maske_gunu', 'dolgu_saati', 'bosluk_saati', 'evren_ort', 'ortak_pay'})
        self.assertTrue(0.0 <= n['r17']['ortak_pay'] <= 1.0)

    def test_r8_ayristirma_serileri(self):
        # Netleştirme 16: B birincilde ayrıştırma satırları; trend + carry bacağı + netleme + icra artığı = günlük getiri.
        from banka_kos import tanilar
        duz = self.b[0]
        sat = duz['r8_satirlar']
        gun = (self.bag.z2_son_ms - self.bag.t0_z1_ms) // G
        self.assertEqual(set(sat), set(tanilar.R8_SATIRLARI))
        self.assertTrue(all(len(v) == gun for v in sat.values()))
        nav = np.array(duz['nav_gunluk'])
        r = nav[1:] / nav[:-1] - 1
        toplam = (np.array(tanilar.trend_bacagi(sat)) + np.array(tanilar.carry_bacagi(sat)) + np.array(sat['netleme'])
                  + np.array(sat['icra_artigi']))
        np.testing.assert_allclose(toplam, r, rtol=0, atol=1e-9)
        self.assertNotIn('r8_satirlar', self.a[0])                                # yalnız M = B
        k, _ = Y.birim_yurut(_birim('kelly', 'B', L=2.0, maliyet_k=1.0), self.bag)
        self.assertEqual(len(k['r8_carry']), gun)
        self.assertIsNone(k['olcum']['b5_pay'])                                  # ölçüm B5'siz kalır (BK-13)
        k2, _ = Y.birim_yurut(_birim('kelly', 'B', L=2.0, maliyet_k=2.0), self.bag)
        self.assertNotIn('r8_carry', k2)                                         # yalnız 1× maliyet

    def test_durum_izi_pozisyon_gecmisiyle_ayni(self):
        # Tanıların durum izi (kayit_uygula ile yeniden oynatma) yürütücünün bağımsız pozisyon geçmişiyle aynı.
        from banka_kos import tanilar
        from motor.geri_test import KosuAyarlari, kos
        bag = self.bag
        p = replace(bag.parametreler, mimari='A', sigma_tahmincisi='HAR',
                    har_takvimi=Y._takvim(bag.veri, bag, bag.z2_son_ms - 3_600_000))
        s = kos(bag.veri, KosuAyarlari(t0_ms=bag.motor_bas_ms, t_son_ms=bag.z2_son_ms - 3_600_000, L=1.0,
                                       maliyet_k=1.0, nav0=1e5, filtreler=bag.filtreler), p)
        gun_sonu, niyetler = tanilar.durum_izi(s.gunluk)
        gecmis = Y.pozisyon_gecmisleri(s.gunluk)
        for t, (q, kalan, nav) in list(gun_sonu.items())[::7]:
            for c, (ms, qq) in gecmis.items():
                i = int(np.searchsorted(ms, t, side='right')) - 1
                self.assertAlmostEqual(q.get(c, 0.0), qq[i] if i >= 0 else 0.0, places=9, msg=(t, c))
            self.assertAlmostEqual(nav, float(s.nav[int(np.searchsorted(s.nav_ms, t))]), places=6)
        self.assertTrue(all(k is None or k >= t for t, _, k, _, _ in niyetler))
        # Kapanış türü ve "sonraki karara yetişmedi" bayrağı kararlarla tutarlı (netleştirme 17 c).
        kararlar = sorted(k.damga_ms for k in s.gunluk.kayitlar() if k.tur == 'karar')
        for t, _, kap, tur, yet in niyetler:
            self.assertTrue(tur is None or tur in ('dolum', 'uzlasma') or tur.startswith('iptal:'), tur)
            sonraki = next((x for x in kararlar if x > t), None)
            if kap is not None and sonraki is not None:
                self.assertEqual(yet, kap > sonraki, (t, kap, sonraki))
        # R2'nin β ≥ 30 gün dalı: 65 günlük pencereyle β tahmin edilir, BTC katkısı sıfırdan farklı; özdeşlik korunur.
        from banka.degerlendirme import Pencere
        pen = Pencere(bas_ms=gun_ms(60), dilim_gun=(65,), haric_gunler=())
        pz = tanilar.piyasa_serileri(s, bag.veri, p, pen, gun_ms(60), gun_ms(125))
        self.assertEqual(pz['beta_yok'], 0)
        bk = np.array([x or 0.0 for x in pz['btc_katki']])
        self.assertGreater(np.abs(bk).sum(), 0.0)
        nav = np.array([float(s.nav[int(np.searchsorted(s.nav_ms, t))]) for t in range(gun_ms(60), gun_ms(126), G)])
        np.testing.assert_allclose(bk + np.array(pz['artik_katki']), nav[1:] / nav[:-1] - 1, atol=1e-9)

    def test_pozisyon_gecmisi_esdeger(self):
        from motor.durum import pozisyon_gecmisi
        from motor.geri_test import KosuAyarlari, kos
        from motor.tipler import Parametreler
        s = kos(self.bag.veri, KosuAyarlari(t0_ms=gun_ms(92), t_son_ms=gun_ms(100) - 3_600_000), Parametreler())
        g = Y.pozisyon_gecmisleri(s.gunluk)
        for c in ('A00', 'BTCUSDT'):
            eski = pozisyon_gecmisi(s.gunluk, c)
            if c in g:
                self.assertEqual(list(zip(g[c][0].tolist(), g[c][1].tolist())), list(eski))
            else:
                self.assertEqual(eski, ())


if __name__ == '__main__':
    unittest.main()
