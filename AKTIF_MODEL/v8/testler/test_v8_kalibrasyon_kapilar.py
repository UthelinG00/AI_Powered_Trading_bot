"""Codex T12 duzeltmeleri (P14a): izgara esigi epsilonsuz, muhasebe kapisi (T4-e), isci parametre/beta denetimi,
B birincil biriminin surec hash tohumundan bagimsizligi (ayri surecler, farkli PYTHONHASHSEED)."""
import hashlib
import os
import subprocess
import sys as _sys
import unittest
from pathlib import Path as _Path
from types import SimpleNamespace

import numpy as np

TESTLER_DIR = _Path(__file__).resolve().parent
V8_DIR = TESTLER_DIR.parent
for _dir in (V8_DIR, TESTLER_DIR):
    if str(_dir) not in _sys.path:
        _sys.path.insert(1, str(_dir))

from fikstur.saatlik_veri import SENARYO_GUN, gun_ms, saat_ms, senaryo_verisi  # noqa: E402
from kalibrasyon import birim as B  # noqa: E402
from kalibrasyon import kosucu as K  # noqa: E402
from kalibrasyon import yurutucu as Y  # noqa: E402
from kalibrasyon.duzey1_esik import ayar_esigi  # noqa: E402
from motor.geri_test import KosuAyarlari, kos  # noqa: E402
from motor.tipler import Parametreler  # noqa: E402

ALT_BETIK = r'''
import sys, hashlib
sys.path.insert(0, {v8!r})
from banka.degerlendirme import Pencere
from kalibrasyon import birim as B, duzey2_uretec as u, yurutucu as Y
k = {{'duzey': 2, 'ayar_no': 0, 'yol_no': 1, 'mimari': 'B', 'tur': 'birincil'}}
g = Y.duzey2_birimi(k, Y.har_beta(), Pencere(bas_ms=u.pencere().bas_ms, dilim_gun=(2, 2, 2, 1)), u.pencere().bas_ms)
print(hashlib.sha256(B.kanonik(g).encode()).hexdigest())
'''


class IzgaraTest(unittest.TestCase):
    def test_sinir_alti_deger(self):
        x = np.full(20, 0.60 - 1e-12)
        self.assertEqual(ayar_esigi(x, 0.95, 0.01), 0.60)            # eski epsilon 0,61 verirdi
        self.assertEqual(ayar_esigi(np.full(20, 0.60), 0.95, 0.01), 0.61)
        self.assertEqual(ayar_esigi(np.full(20, 0.3), 0.95, 0.01), 0.31)


class MuhasebeKapisiTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.veri = senaryo_verisi()
        cls.s = kos(cls.veri, KosuAyarlari(t0_ms=gun_ms(92), t_son_ms=saat_ms(SENARYO_GUN * 24 - 1)), Parametreler())

    def test_saglam_kosu_gecer(self):
        m = Y.muhasebe_kapisi(self.s, self.veri)
        self.assertLess(m['coin_pnl_hata'], 1e-6)

    def test_bozuk_nav_ve_zincir(self):
        bozuk = SimpleNamespace(nav=np.r_[self.s.nav[:-1], np.nan], gunluk=self.s.gunluk)
        with self.assertRaises(Y.MuhasebeHatasi):
            Y.muhasebe_kapisi(bozuk, self.veri)
        zincir = SimpleNamespace(nav=self.s.nav, gunluk=SimpleNamespace(dogrula=lambda: False))
        with self.assertRaises(Y.MuhasebeHatasi):
            Y.muhasebe_kapisi(zincir, self.veri)
        kayik = SimpleNamespace(nav=self.s.nav * 1.001, gunluk=self.s.gunluk, nav_ms=self.s.nav_ms)
        with self.assertRaises(Y.MuhasebeHatasi):
            Y.muhasebe_kapisi(kayik, self.veri)                       # ozdeslik NAV'la tutmaz


class AyristirmaKapisiTest(unittest.TestCase):
    """Codex T13-3: ayristirmadaki sonlu olmayan deger ozet hatanin arkasinda gizlenmez."""

    @classmethod
    def setUpClass(cls):
        cls.veri = senaryo_verisi()
        cls.s = kos(cls.veri, KosuAyarlari(t0_ms=gun_ms(92), t_son_ms=saat_ms(SENARYO_GUN * 24 - 1)), Parametreler())

    def _a(self, **kw):
        a = dict(satirlar={'trend_fiyat': np.zeros(3), 'dnav': np.array([np.nan, np.nan, 1.0])}, trend_coin={},
                 trend_eski={}, trend_yeni={}, ozdeslik_max_hata=0.0)
        a.update(kw)
        return SimpleNamespace(**a)

    def test_nan_ve_inf(self):
        self.assertIn('ayristirma_hata', Y.muhasebe_kapisi(self.s, self.veri, self._a()))
        with self.assertRaises(Y.MuhasebeHatasi):
            Y.muhasebe_kapisi(self.s, self.veri, self._a(satirlar={'trend_fiyat': np.array([0.0, np.nan]),
                                                                   'dnav': np.zeros(2)}))
        with self.assertRaises(Y.MuhasebeHatasi):
            Y.muhasebe_kapisi(self.s, self.veri, self._a(trend_eski={'X': np.array([np.inf])}))
        with self.assertRaises(Y.MuhasebeHatasi):
            Y.muhasebe_kapisi(self.s, self.veri, self._a(ozdeslik_max_hata=float('inf')))

class IsciDenetimiTest(unittest.TestCase):
    def test_beta_ve_parametre(self):
        sha, beta = Y.har_paketi()
        kim = B.beklenen_kimlikler(Parametreler(), sha)
        K._isci_hazirla(kim, beta, True)
        with self.assertRaises(K.KosucuHatasi):
            K._isci_hazirla(kim, tuple(b + 1e-9 for b in beta), True)
        with self.assertRaises(K.KosucuHatasi):
            K._isci_hazirla({**kim, 'parametre': 'eski'}, beta, True)
        self.assertEqual(sha, hashlib.sha256(Y.HAR_SONUC.read_bytes()).hexdigest())


class HashTohumuTest(unittest.TestCase):
    def test_b_birincil_surecler_arasi_ayni(self):
        betik = ALT_BETIK.format(v8=str(V8_DIR))
        cikti = []
        for tohum in ('1', '12345'):
            env = {**os.environ, 'PYTHONHASHSEED': tohum, 'OMP_NUM_THREADS': '1', 'OPENBLAS_NUM_THREADS': '1',
                   'MKL_NUM_THREADS': '1'}
            r = subprocess.run([_sys.executable, '-c', betik], env=env, capture_output=True, text=True, timeout=900)
            self.assertEqual(r.returncode, 0, r.stderr[-2000:])
            cikti.append(r.stdout.strip().splitlines()[-1])
        self.assertEqual(cikti[0], cikti[1])


if __name__ == '__main__':
    unittest.main()
