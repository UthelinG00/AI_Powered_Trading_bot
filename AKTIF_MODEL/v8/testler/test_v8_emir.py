"""MIMARI Ss5.1 lot_yuvarlama/emir_zinciri, Ss5.4 risk artiran/azaltan ayrimi, Ss3.7 katilim, Ss6.1 maliyet.
Sentetik degerler, gercek islem yok."""
import math
import sys as _sys
import unittest
from pathlib import Path as _Path

TESTLER_DIR = _Path(__file__).resolve().parent
V8_DIR = TESTLER_DIR.parent
for _dir in (V8_DIR, TESTLER_DIR):
    if str(_dir) not in _sys.path:
        _sys.path.insert(1, str(_dir))

from motor.durum import Emir, MaliyetBaglami  # noqa: E402
from motor.maliyet import MaliyetGirdiHatasi  # noqa: E402
from motor.emir import filtre_al, lot_niyeti, risk_parcalari, saat_dolumu  # noqa: E402
from motor.tipler import Parametreler  # noqa: E402

P = Parametreler()
# Q_max = min(0.001*1e6, 0.001*1e6, 0.10*onceki) = 1000 USDT (onceki >= 10.000)
BAGLAM = MaliyetBaglami(v1h30=1e6, v1h7=1e6, v60=1e8, sigma_d_bps=10.0, sigma_1h=0.01, btc_eth=False,
                        btc_sigma_1h=0.01)
BAR = (10.0, 10.01, 9.99, 1e6)   # acilis, yuksek, dusuk, hacim; |ln(H/L)| = 0.002 < 5*0.01 (stres yok)


def _emir(kalan, tam=False, maske=False, baglam=BAGLAM):
    return Emir(kalan=kalan, karar_ms=0, maske_cikisi=maske, tam_kapanis=tam, baglam=baglam)


def _bps(dilim, nominal, m=1.0, k=1.0):
    return P.ucret_bps + k * m * (dilim + 10.0 * math.sqrt(nominal / 1e8))


class RiskParcalariTest(unittest.TestCase):
    def test_siniflama(self):
        self.assertEqual(risk_parcalari(-3.0, 2.0), (-2.0, -1.0))   # isaret degistiren: 0'a kadar azaltan
        self.assertEqual(risk_parcalari(-1.0, 2.0), (-1.0, 0.0))
        self.assertEqual(risk_parcalari(1.0, 2.0), (0.0, 1.0))      # ayni yon: artiran
        self.assertEqual(risk_parcalari(1.0, 0.0), (0.0, 1.0))      # sifirdan acilis: artiran
        self.assertEqual(risk_parcalari(3.0, -2.0), (2.0, 1.0))


class SaatDolumuTest(unittest.TestCase):
    def test_katilim_siniri_kismi_dolum(self):
        d = saat_dolumu(_emir(250.0), 0.0, BAR, 1e6, 0.0, 1.0, 0.1, 5.0, P)
        self.assertEqual(d.sebep, 'kismi')
        self.assertAlmostEqual(d.miktar, 100.0, places=9)       # 1000 USDT / 10
        self.assertAlmostEqual(d.q_max, 1000.0, places=9)
        self.assertAlmostEqual(d.maliyet_bps, _bps(8.0, 1000.0), places=9)   # 50-200M dilimi 8 bps
        self.assertAlmostEqual(d.fiyat, 10.0 * (1 + d.maliyet_bps / 1e4), places=12)

    def test_onceki_saat_hacmi_siniri(self):
        d = saat_dolumu(_emir(250.0), 0.0, BAR, 2000.0, 0.0, 1.0, 0.0, 5.0, P)
        self.assertAlmostEqual(d.q_max, 200.0, places=9)        # 0.10 * 2000
        self.assertAlmostEqual(d.miktar, 20.0, places=9)

    def test_adim_alti_kismi_dolum_sifir(self):
        d = saat_dolumu(_emir(5.0), 0.0, BAR, 5.0, 0.0, 1.0, 0.1, 0.0, P)   # Q_max 0.5 USDT -> 0.05 adet
        self.assertEqual((d.miktar, d.sebep), (0.0, 'adim_alti'))

    def test_min_notional_alti_dolum_sifir(self):
        d = saat_dolumu(_emir(5.0), 0.0, BAR, 40.0, 0.0, 1.0, 0.001, 5.0, P)  # 4 USDT < 5
        self.assertEqual((d.miktar, d.sebep), (0.0, 'min_notional'))

    def test_tam_kapanis_son_parcasi_min_notionaldan_muaf(self):
        q = 0.1 + 0.2
        d = saat_dolumu(_emir(-q, tam=True), q, BAR, 1e6, 0.0, 1.0, 0.1, 5.0, P)   # 3 USDT
        self.assertEqual(d.miktar, -q)
        self.assertTrue(d.tam_kapanis_son)
        self.assertLess(d.fiyat, 10.0)                          # satis: acilis * (1 - c)

    def test_tam_kapanisin_ara_parcasi_normal(self):
        d = saat_dolumu(_emir(-300.0, tam=True), 300.0, BAR, 1e6, 0.0, 1.0, 0.1, 5.0, P)
        self.assertAlmostEqual(d.miktar, -100.0, places=9)
        self.assertFalse(d.tam_kapanis_son)
        self.assertAlmostEqual(d.maliyet_bps, _bps(8.0, 1000.0), places=9)

    def test_bar_yok_ya_da_hacim_sifir(self):
        self.assertEqual(saat_dolumu(_emir(1.0), 0.0, None, 1e6, 0.0, 1.0, 0.1, 5.0, P).sebep, 'bar_yok')
        self.assertEqual(saat_dolumu(_emir(1.0), 0.0, (10.0, 10.0, 10.0, 0.0), 1e6, 0.0, 1.0, 0.1, 5.0, P).sebep,
                         'hacim_0')

    def test_katilimsiz_golge_yol_tamamini_doldurur(self):
        d = saat_dolumu(_emir(250.0), 0.0, BAR, 0.0, 0.0, 1.0, 0.1, 5.0, P, katilimsiz=True)
        self.assertAlmostEqual(d.miktar, 250.0, places=9)
        self.assertEqual(d.sebep, 'doldu')

    def test_maske_cikisi_ve_stres_carpani(self):
        maske = saat_dolumu(_emir(-50.0, maske=True), 50.0, BAR, 1e6, 0.0, 1.0, 0.1, 5.0, P)
        self.assertAlmostEqual(maske.maliyet_bps, _bps(8.0, 500.0, m=3.0), places=9)
        stres_bar = (10.0, 10.4, 9.8, 1e6)                      # |ln(H/L)| = 0.0594 > 0.05
        stres = saat_dolumu(_emir(50.0), 0.0, stres_bar, 1e6, 0.0, 1.0, 0.1, 5.0, P)
        self.assertAlmostEqual(stres.maliyet_bps, _bps(8.0, 500.0, m=3.0), places=9)
        btc_stres = saat_dolumu(_emir(50.0), 0.0, BAR, 1e6, 0.05, 1.0, 0.1, 5.0, P)   # 0.05 > 4*0.01
        self.assertAlmostEqual(btc_stres.maliyet_bps, _bps(8.0, 500.0, m=3.0), places=9)

    def test_maliyet_carpani_ucrete_uygulanmaz(self):
        d = saat_dolumu(_emir(50.0), 0.0, BAR, 1e6, 0.0, 3.0, 0.1, 5.0, P)
        self.assertAlmostEqual(d.maliyet_bps, _bps(8.0, 500.0, k=3.0), places=9)

    def test_yirmi_milyon_alti_giris_reddedilir_cikis_25_bps(self):
        # MIMARI Ss6.1: <20M dilimi yalniz cikista tanimli (Codex K13). Karar boyle bir giris uretmez; uretirse hata.
        dusuk = MaliyetBaglami(1e6, 1e6, 1e7, 10.0, 0.01, False, 0.01)
        with self.assertRaises(MaliyetGirdiHatasi):
            saat_dolumu(_emir(50.0, baglam=dusuk), 0.0, BAR, 1e6, 0.0, 1.0, 0.1, 5.0, P)
        d = saat_dolumu(_emir(-50.0, baglam=dusuk), 100.0, BAR, 1e6, 0.0, 1.0, 0.1, 5.0, P)
        self.assertAlmostEqual(d.maliyet_bps, P.ucret_bps + 25.0 + 10.0 * math.sqrt(500.0 / 1e7), places=9)

    def test_sigma_1h_eksikse_stres_yok(self):
        b = MaliyetBaglami(1e6, 1e6, 1e8, 10.0, float('nan'), False, float('nan'))
        d = saat_dolumu(_emir(50.0, baglam=b), 0.0, (10.0, 11.0, 9.0, 1e6), 1e6, 0.5, 1.0, 0.1, 5.0, P)
        self.assertAlmostEqual(d.maliyet_bps, _bps(8.0, 500.0), places=9)


class LotNiyetiTest(unittest.TestCase):
    def test_adim_sifir_yuvarlama_yok(self):
        self.assertAlmostEqual(lot_niyeti(0.1, 0.0, 1000.0, 3.0, 0.0, 5.0), 100.0 / 3.0, places=12)

    def test_adimli_sifira_dogru(self):
        self.assertAlmostEqual(lot_niyeti(0.1, 0.0, 1000.0, 3.0, 1.0, 5.0), 33.0, places=12)

    def test_min_notional_ve_tam_kapanis(self):
        self.assertEqual(lot_niyeti(0.1, 33.0, 1000.0, 3.0, 0.0, 5.0), 0.0)    # 0.33 adet * 3 = 1 USDT
        self.assertEqual(lot_niyeti(0.0, 0.25, 1000.0, 3.0, 0.0, 5.0), -0.25)  # hedef 0: tam kapanis

    def test_filtre_varsayilani(self):
        self.assertEqual(filtre_al({}, 'YOK', P), (0.0, 5.0))
        self.assertEqual(filtre_al({'X': (0.001, 10.0)}, 'X', P), (0.001, 10.0))


if __name__ == '__main__':
    unittest.main()
