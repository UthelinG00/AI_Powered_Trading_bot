"""MIMARI Ss3.7 katilim/lot ve Ss6 maliyet modeli. Sentetik veri, gercek islem yok."""
import sys as _sys
import unittest
from pathlib import Path as _Path

V8_DIR = _Path(__file__).resolve().parents[1]
if str(V8_DIR) not in _sys.path:
    _sys.path.insert(1, str(V8_DIR))

from motor.katilim import (  # noqa: E402
    KatilimGirdiHatasi,
    katilim_siniri,
    lot_delta,
    tek_saat_dolum,
)
from motor.maliyet import (  # noqa: E402
    MaliyetGirdiHatasi,
    dilim_bps,
    etki_bps,
    m_carpani,
    maliyet_hesapla,
)
from motor.tipler import Parametreler  # noqa: E402

P = Parametreler()


class KatilimSiniriTest(unittest.TestCase):
    def test_en_kucuk_terim_secilir(self):
        # 0.001*30M=30000; 0.001*10M=10000 (en kucuk); 0.10*500000=50000
        q = katilim_siniri(v1h30=30_000_000, v1h7=10_000_000, onceki_saat_hacmi=500_000, p=P)
        self.assertAlmostEqual(q, 10_000.0, places=6)

    def test_onceki_saat_hacmi_en_kucukse_o_secilir(self):
        q = katilim_siniri(v1h30=100_000_000, v1h7=100_000_000, onceki_saat_hacmi=1_000, p=P)
        self.assertAlmostEqual(q, 0.10 * 1_000, places=6)

    def test_negatif_hacim_hata(self):
        with self.assertRaises(KatilimGirdiHatasi):
            katilim_siniri(-1, 1, 1, P)


class LotDeltaTest(unittest.TestCase):
    def test_normal_yuvarlama_sifira_dogru(self):
        # hedef miktar = 0.10*100000/50 = 200; mevcut=150; delta_ham=50; adim=1 -> delta=50
        d = lot_delta(w_hedef=0.10, q_mevcut=150.0, nav=100_000.0, fiyat_ref=50.0, adim=1.0, min_notional=5.0)
        self.assertAlmostEqual(d, 50.0, places=9)

    def test_adim_altinda_sifira_yuvarlanir(self):
        # hedef=200.3 -> delta_ham=50.3, adim=1 -> trunc(50.3)=50
        d = lot_delta(w_hedef=0.1003, q_mevcut=150.0, nav=100_000.0, fiyat_ref=50.0, adim=1.0, min_notional=5.0)
        self.assertAlmostEqual(d, 50.0, places=9)

    def test_min_notional_altinda_emir_yok(self):
        # hedef_miktar=0.0015*1000/1000=0.0015; mevcut=0 -> delta_ham=0.0015; adim=0.001 -> delta=0.001;
        # nominal=0.001*1000=1 USDT < min_notional=5 -> emir yok.
        d = lot_delta(w_hedef=0.0015, q_mevcut=0.0, nav=1000.0, fiyat_ref=1000.0, adim=0.001, min_notional=5.0)
        self.assertEqual(d, 0.0)

    def test_hedef_sifir_tam_kapanis_min_notional_istisnasi(self):
        # w_hedef=0 -> tam kapanis, minNotional denetlenmez, delta = -q_mevcut.
        d = lot_delta(w_hedef=0.0, q_mevcut=0.0007, nav=100_000.0, fiyat_ref=50_000.0, adim=0.001,
                      min_notional=5.0)
        self.assertAlmostEqual(d, -0.0007, places=9)

    def test_gecersiz_adim_hata(self):
        with self.assertRaises(KatilimGirdiHatasi):
            lot_delta(0.1, 0.0, 1000.0, 50.0, adim=0.0, min_notional=5.0)


class TekSaatDolumTest(unittest.TestCase):
    def test_normal_kismi_dolum_asagi_yuvarlanir(self):
        # kalan=105, q_max/acilis=100.7 -> ham=100.7, floor(100.7/1)*1=100
        sonuc = tek_saat_dolum(kalan_miktar=105.0, q_max=10_070.0, acilis_fiyati=100.0, adim=1.0,
                                min_notional=5.0, bar_var_mi=True, hacim_var_mi=True, maliyet_c_i=0.001)
        self.assertAlmostEqual(sonuc.miktar, 100.0, places=9)
        self.assertAlmostEqual(sonuc.fiyat, 100.0 * 1.001, places=9)

    def test_satis_fiyati_asagi_kayar(self):
        sonuc = tek_saat_dolum(kalan_miktar=-50.0, q_max=100_000.0, acilis_fiyati=100.0, adim=1.0,
                                min_notional=5.0, bar_var_mi=True, hacim_var_mi=True, maliyet_c_i=0.002)
        self.assertLess(sonuc.miktar, 0.0)
        self.assertAlmostEqual(sonuc.fiyat, 100.0 * 0.998, places=9)

    def test_bar_yoksa_dolum_sifir(self):
        sonuc = tek_saat_dolum(kalan_miktar=50.0, q_max=100_000.0, acilis_fiyati=100.0, adim=1.0,
                                min_notional=5.0, bar_var_mi=False, hacim_var_mi=True, maliyet_c_i=0.001)
        self.assertEqual(sonuc.miktar, 0.0)

    def test_hacim_sifirsa_dolum_sifir(self):
        sonuc = tek_saat_dolum(kalan_miktar=50.0, q_max=100_000.0, acilis_fiyati=100.0, adim=1.0,
                                min_notional=5.0, bar_var_mi=True, hacim_var_mi=False, maliyet_c_i=0.001)
        self.assertEqual(sonuc.miktar, 0.0)

    def test_min_notional_altinda_normalde_sifir_ama_tam_kapanis_istisnasi(self):
        # ham kucuk (0.02 birim, nominal 2 USDT < 5 min_notional): normalde 0, tam kapanisin son
        # parcasiysa yine de dolar.
        sonuc_normal = tek_saat_dolum(kalan_miktar=0.02, q_max=1_000_000.0, acilis_fiyati=100.0, adim=0.001,
                                       min_notional=5.0, bar_var_mi=True, hacim_var_mi=True, maliyet_c_i=0.0)
        self.assertEqual(sonuc_normal.miktar, 0.0)
        sonuc_son_parca = tek_saat_dolum(kalan_miktar=0.02, q_max=1_000_000.0, acilis_fiyati=100.0, adim=0.001,
                                          min_notional=5.0, bar_var_mi=True, hacim_var_mi=True, maliyet_c_i=0.0,
                                          tam_kapanisin_son_parcasi_mi=True)
        self.assertAlmostEqual(sonuc_son_parca.miktar, 0.02, places=9)

    def test_katilim_sinirinin_uzerine_cikilmaz(self):
        # kalan cok buyuk ama q_max/acilis kucuk -> ham q_max/acilis ile sinirlanir.
        sonuc = tek_saat_dolum(kalan_miktar=10_000.0, q_max=1_000.0, acilis_fiyati=100.0, adim=1.0,
                                min_notional=5.0, bar_var_mi=True, hacim_var_mi=True, maliyet_c_i=0.0)
        self.assertAlmostEqual(sonuc.miktar, 10.0, places=9)  # 1000/100=10


class DilimBpsTest(unittest.TestCase):
    def test_btc_eth_sabit(self):
        self.assertEqual(dilim_bps(1_000_000, True, False, P), P.dilim_btc_eth_bps)
        self.assertEqual(dilim_bps(1_000_000_000, True, False, P), P.dilim_btc_eth_bps)

    def test_esikler(self):
        self.assertEqual(dilim_bps(300_000_000, False, False, P), P.dilim_200m_ustu_bps)
        self.assertEqual(dilim_bps(100_000_000, False, False, P), P.dilim_50_200m_bps)
        self.assertEqual(dilim_bps(30_000_000, False, False, P), P.dilim_20_50m_bps)

    def test_20m_alti_yalniz_cikis(self):
        self.assertEqual(dilim_bps(10_000_000, False, True, P), P.dilim_20m_alti_bps)
        with self.assertRaises(MaliyetGirdiHatasi):
            dilim_bps(10_000_000, False, False, P)


class EtkiBpsTest(unittest.TestCase):
    def test_formul(self):
        e = etki_bps(sigma_d_bps=10.0, q_nominal=1000.0, v60=1_000_000.0, p=P)
        self.assertAlmostEqual(e, 10.0 * (1000.0 / 1_000_000.0) ** 0.5, places=9)

    def test_v60_sifir_hata(self):
        with self.assertRaises(MaliyetGirdiHatasi):
            etki_bps(10.0, 1.0, 0.0, P)


class MCarpaniTest(unittest.TestCase):
    def test_normal_bir(self):
        self.assertEqual(m_carpani(False, 0.01, 0.02, 0.01, 0.02, P), 1.0)

    def test_maske_cikisi_uc(self):
        self.assertEqual(m_carpani(True, 0.0, 0.02, 0.0, 0.02, P), P.m_stres)

    def test_coin_stres_uc(self):
        self.assertEqual(m_carpani(False, 0.11, 0.02, 0.0, 0.02, P), P.m_stres)  # 0.11 > 5*0.02=0.10

    def test_btc_stres_uc(self):
        self.assertEqual(m_carpani(False, 0.0, 0.02, 0.09, 0.02, P), P.m_stres)  # 0.09 > 4*0.02=0.08

    def test_ikisi_birden_hala_uc(self):
        self.assertEqual(m_carpani(True, 0.11, 0.02, 0.09, 0.02, P), P.m_stres)


class MaliyetHesaplaTest(unittest.TestCase):
    def test_btc_k3_ornegi_etkisiz(self):
        # Spesifikasyon ornegi: BTC k=3'te 5 + 3*2 = 11 bps (etki haric).
        sonuc = maliyet_hesapla(k=3.0, v60=1_000_000_000.0, btc_eth_mi=True, cikis_mi=False,
                                 maske_cikisi_mi=False, ln_hl_coin=0.0, sigma_1h_coin=0.02,
                                 ln_hl_btc=0.0, sigma_1h_btc=0.02, sigma_d_bps=10.0, q_nominal=0.0, p=P)
        self.assertAlmostEqual(sonuc.toplam_bps, 11.0, places=9)
        self.assertEqual(sonuc.etki_bps, 0.0)

    def test_50_200m_k3_ornegi_etkisiz(self):
        # Spesifikasyon ornegi: 50-200M altta k=3'te 5 + 3*8 = 29 bps (etki haric).
        sonuc = maliyet_hesapla(k=3.0, v60=100_000_000.0, btc_eth_mi=False, cikis_mi=False,
                                 maske_cikisi_mi=False, ln_hl_coin=0.0, sigma_1h_coin=0.02,
                                 ln_hl_btc=0.0, sigma_1h_btc=0.02, sigma_d_bps=10.0, q_nominal=0.0, p=P)
        self.assertAlmostEqual(sonuc.toplam_bps, 29.0, places=9)

    def test_k_sifir_hata(self):
        with self.assertRaises(MaliyetGirdiHatasi):
            maliyet_hesapla(k=0.0, v60=1_000_000.0, btc_eth_mi=True, cikis_mi=False, maske_cikisi_mi=False,
                             ln_hl_coin=0.0, sigma_1h_coin=0.02, ln_hl_btc=0.0, sigma_1h_btc=0.02,
                             sigma_d_bps=1.0, q_nominal=1.0, p=P)


if __name__ == '__main__':
    unittest.main()
