"""Duzey 2 fiyat ureteci (kalibrasyon/duzey2_uretec.py) ve kanonik tohum (kalibrasyon/tohum.py): belgedeki
formullerle moment, OHLC, hacim ve funding denetimleri; tohum tanimi regresyon degerleriyle sabit."""
import math
import sys as _sys
import unittest
from pathlib import Path as _Path

import numpy as np

V8_DIR = _Path(__file__).resolve().parent.parent
if str(V8_DIR) not in _sys.path:
    _sys.path.insert(1, str(V8_DIR))

from kalibrasyon import duzey2_uretec as u  # noqa: E402
from kalibrasyon.tohum import TOHUM_KAL, hash_tohum, kanonik_json  # noqa: E402
from motor.geri_test import KosuAyarlari, kos  # noqa: E402
from motor.gorunum import GUN_MS, SAAT_MS  # noqa: E402
from motor.tipler import Parametreler  # noqa: E402


class TohumTest(unittest.TestCase):
    def test_tanim_sabit(self):
        self.assertEqual(TOHUM_KAL, 1157334973)                  # int(sha256("v8_asama4b_kalibrasyon")[:16],16) mod 2^32
        self.assertEqual(kanonik_json([TOHUM_KAL, 2, 0, 1]), '[1157334973,2,0,1]')
        self.assertEqual(hash_tohum(TOHUM_KAL, 2, 0, 1), 15894020429147432617)
        self.assertEqual(hash_tohum(1, 'a'), 2310509695340830360)
        self.assertNotEqual(hash_tohum(1, 2), hash_tohum(2, 1))

    def test_gecersiz_parca(self):
        for x in (True, 1.0, None, 'ç'):
            with self.assertRaises((TypeError, ValueError)):
                hash_tohum(1, x)


class UretecTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.h0 = u.ham_yol(0, 1)
        cls.h4 = u.ham_yol(4, 1)

    def test_belirlenimli(self):
        h = u.ham_yol(0, 1)
        for c in u.COINLER:
            self.assertTrue(np.array_equal(h.kapanis[c], self.h0.kapanis[c]))
            self.assertTrue(np.array_equal(h.hacim[c], self.h0.hacim[c]))
        self.assertEqual(h.yasam, self.h0.yasam)
        self.assertFalse(np.array_equal(u.ham_yol(0, 2).kapanis['BTCUSDT'], self.h0.kapanis['BTCUSDT']))

    def test_beta_ve_yasam_tarifi(self):
        self.assertEqual(self.h0.beta['BTCUSDT'], 1.0)
        alt = [self.h0.beta[c] for c in u.ALTLAR]
        self.assertTrue(all(0.6 <= b <= 1.4 for b in alt))
        y = self.h0.yasam
        secilen = [c for c, _ in y.listelenen + y.olen + y.funding_4h]
        self.assertEqual(len(secilen), len(set(secilen)))          # ayrik alt kumeler
        self.assertTrue(all(c in u.ALTLAR for c in secilen))
        self.assertTrue(all(u.ISINMA_GUN <= g < u.GUN for _, g in y.listelenen + y.olen))
        self.assertTrue(all(u.ISINMA_GUN <= g < u.GUN - u.FUNDING_4H_GUN for _, g in y.funding_4h))
        self.assertTrue(u.ISINMA_GUN * 24 <= y.bosluk_saat < u.SAAT - u.BOSLUK_SAAT)

    def test_kappa0_gunluk_vol(self):
        oran = []
        for c in u.COINLER:
            gunluk = self.h0.r[c].reshape(-1, 24).sum(axis=1)
            s_i = u.SIGMA_I_BUYUK if c in ('BTCUSDT', 'ETHUSDT') else u.SIGMA_I_ALT
            oran.append(np.std(gunluk) / u.sigma_toplam(self.h0.beta[c], s_i))
            self.assertTrue(np.all(self.h0.g[c] == 0.0))
        self.assertAlmostEqual(float(np.mean(oran)), 1.0, delta=0.05)

    def test_trend_duragan_std_ve_kalicilik(self):
        kappa, hl = u.AYARLAR[4]
        oran, rho = [], []
        for c in u.COINLER:
            s_i = u.SIGMA_I_BUYUK if c in ('BTCUSDT', 'ETHUSDT') else u.SIGMA_I_ALT
            g = self.h4.g[c]
            oran.append(np.std(g) / (kappa * u.sigma_toplam(self.h4.beta[c], s_i)))
            rho.append(np.corrcoef(g[:-1], g[1:])[0, 1])
        self.assertAlmostEqual(float(np.mean(oran)), 1.0, delta=0.25)
        self.assertAlmostEqual(float(np.mean(rho)), 2.0 ** (-1.0 / hl), delta=0.01)

    def test_ohlc(self):
        for c in u.COINLER:
            o, h, l, k = self.h0.acilis[c], self.h0.yuksek[c], self.h0.dusuk[c], self.h0.kapanis[c]
            self.assertEqual(o[0], 1.0)
            self.assertTrue(np.array_equal(o[1:], k[:-1]))
            self.assertTrue(np.all(h >= np.maximum(o, k)) and np.all(l <= np.minimum(o, k)) and np.all(l > 0))

    def test_hacim_merkezi(self):
        for c in ('BTCUSDT', 'C05USDT', 'C20USDT'):
            gunluk = self.h0.hacim[c].reshape(-1, 24).sum(axis=1)
            self.assertAlmostEqual(float(np.median(np.log(gunluk))), math.log(self.h0.hacim_merkezi[c]), delta=0.5)
        merkez = [self.h0.hacim_merkezi[c] for c in u.ALTLAR]
        self.assertTrue(all(10e6 <= v <= 400e6 for v in merkez))
        self.assertEqual(self.h0.hacim_merkezi['ETHUSDT'], 5000e6)

    def test_veri_ve_funding(self):
        v = u.veri_kur(self.h0, yasam=False)
        self.assertEqual(v.adaylar, u.COINLER)
        self.assertEqual(len(u.COINLER), 30)
        f = v.funding['C07USDT']
        saat = (f.damga_ms - u.BAS_MS) // 3_600_000
        self.assertTrue(np.all(saat % 8 == 0) and saat[0] == 8)
        self.assertAlmostEqual(float(np.mean(f.oran)), u.FUNDING_ORT, delta=5e-6)
        self.assertTrue(np.all(f.aralik_saat == 8.0))
        self.assertEqual(len(v.barlar['BTCUSDT']), u.SAAT)
        pen = u.pencere()
        self.assertEqual(pen.bas_ms, u.BAS_MS + 365 * GUN_MS)
        self.assertEqual(pen.gun_sayisi, 1168)
        self.assertEqual(pen.bit_ms, u.BAS_MS + u.GUN * GUN_MS)


class YasamTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.v, cls.h = u.yol_verisi(0, 1)
        cls.y = cls.h.yasam

    def _saat(self, ms):
        return (np.asarray(ms) - u.BAS_MS) // SAAT_MS

    def test_listelenme(self):
        for c, g in self.y.listelenen:
            b = self._saat(self.v.barlar[c].acilis_ms)
            self.assertEqual(int(b[0]), g * 24)
            self.assertTrue(np.all(self._saat(self.v.funding[c].damga_ms) > g * 24))

    def test_olum(self):
        for c, g in self.y.olen:
            s = self.v.barlar[c]
            b = self._saat(s.acilis_ms)
            self.assertEqual(int(b[-1]), g * 24 - 1)
            son10 = b >= (g - u.OLUM_HACIM_GUN) * 24
            self.assertTrue(np.allclose(s.hacim[son10], self.h.hacim[c][b[son10]] * u.OLUM_HACIM_CARPAN))
            self.assertTrue(np.allclose(s.hacim[~son10], self.h.hacim[c][b[~son10]]))
            self.assertTrue(np.all(self._saat(self.v.funding[c].damga_ms) < g * 24))

    def test_funding_4h(self):
        for c, g in self.y.funding_4h:
            f = self.v.funding[c]
            h = self._saat(f.damga_ms)
            ic = (h >= g * 24) & (h < (g + u.FUNDING_4H_GUN) * 24)
            self.assertEqual(int(ic.sum()), u.FUNDING_4H_GUN * 6)
            self.assertTrue(np.all(f.aralik_saat[ic] == 4.0) and np.all(f.aralik_saat[~ic] == 8.0))
            self.assertTrue(np.all(h[~ic] % 8 == 0) and np.all(h[ic] % 4 == 0))

    def test_borsa_capi_bosluk(self):
        g0 = self.y.bosluk_saat
        for c in u.COINLER:
            b = set(self._saat(self.v.barlar[c].acilis_ms).tolist())
            self.assertFalse(b & set(range(g0, g0 + u.BOSLUK_SAAT)), c)
        normal = [c for c in u.COINLER if c not in dict(self.y.listelenen) and c not in dict(self.y.olen)]
        for c in normal:
            b = set(self._saat(self.v.barlar[c].acilis_ms).tolist())
            self.assertIn(g0 - 1, b)
            self.assertIn(g0 + u.BOSLUK_SAAT, b)

    def test_motor_boslugu_gorur(self):
        g0 = self.y.bosluk_saat
        gun = g0 // 24
        s = kos(self.v, KosuAyarlari(t0_ms=u.BAS_MS + gun * GUN_MS,
                                     t_son_ms=u.BAS_MS + (gun + 3) * GUN_MS - SAAT_MS), Parametreler())
        gecmis = set()
        for k in s.gunluk.kayitlar():
            if k.tur == 'karar':
                gecmis |= set(k.veri.get('bosluk_gecmis', ()))
        bosluk_ms = {u.BAS_MS + h * SAAT_MS for h in range(g0, g0 + u.BOSLUK_SAAT)}
        self.assertTrue(bosluk_ms & gecmis)


if __name__ == '__main__':
    unittest.main()
