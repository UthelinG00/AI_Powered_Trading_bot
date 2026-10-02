"""HAR banka modu (banka/har_banka.py): kilit Adim 2'nin baglayici betigiyle (har_secimi.py) ayni kume ve ayni s^2.
Betik ice aktarilir, tarih sabitleri fikstur takvimine cekilir; D verisi okunmaz (sentetik senaryo)."""
import importlib.util
import json
import math
import sys as _sys
import unittest
from dataclasses import replace
from pathlib import Path as _Path

TESTLER_DIR = _Path(__file__).resolve().parent
V8_DIR = TESTLER_DIR.parent
for _dir in (V8_DIR, TESTLER_DIR):
    if str(_dir) not in _sys.path:
        _sys.path.insert(1, str(_dir))

from banka.har_banka import (HAFTA, banka_takvimi, har_satirlari, pazartesi_kumesi, pazartesi_mi,  # noqa: E402
                             s2_yolu)
from fikstur.saatlik_veri import SENARYO_GUN, gun_ms, saat_ms, senaryo_verisi  # noqa: E402
from motor.geri_test import KosuAyarlari, kos  # noqa: E402
from motor.har import har_katsayi  # noqa: E402
from motor.tipler import Parametreler  # noqa: E402

CIKTILAR = V8_DIR.parent / 'ciktilar'
BETIK = CIKTILAR / 'v8_har_secimi_20260929_01' / 'har_secimi.py'
SENTETIK_SONUC = CIKTILAR / 'v8_har_secimi_20260929_01' / 'sonuc_sentetik.json'
HIZ_DIR = CIKTILAR / 'v8_hiz_20260929_01'


def betik_modulu():
    spec = importlib.util.spec_from_file_location('har_secimi_betik', BETIK)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


class PazartesiKumesiTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.veri = senaryo_verisi()
        cls.p = Parametreler()
        cls.t0 = gun_ms(92)
        son = gun_ms(SENARYO_GUN - 8)
        while not pazartesi_mi(son):
            son -= 24 * 3_600_000
        cls.son = son

    def test_betikle_ayni(self):
        m = betik_modulu()
        m.T0, m.SON_PAZARTESI = self.t0, self.son
        beklenen, maske_b = m.pit_evren(self.veri, self.p)
        kume, maske = pazartesi_kumesi(self.veri, self.t0, self.son, self.p)
        self.assertEqual(kume, beklenen)
        self.assertEqual(maske, maske_b)
        self.assertTrue(any(kume.values()))
        self.assertTrue(all(pazartesi_mi(t) for t in kume))
        self.assertEqual(max(kume), self.son)
        self.assertEqual(sorted(kume), list(range(min(kume), self.son + 1, HAFTA)))


class S2YoluEslikTest(unittest.TestCase):
    """Baglayici betigin sentetik kosusu (sonuc_sentetik.json, commit 31e9dea): ayni sentetik veri ve betigin yuruyen
    katsayilariyla s^2 yolu birebir; satirlardan yeniden hesaplanan aylik katsayilar da birebir."""

    def test_betigin_sentetik_kosusuyla_ayni(self):
        m = betik_modulu()
        if str(HIZ_DIR) not in _sys.path:
            _sys.path.insert(1, str(HIZ_DIR))
        from hiz_profil import veri_uret
        p = Parametreler()
        veri = veri_uret((m.D_SON - m.ms(2023, 7, 1)) // (24 * 3_600_000))
        beklenen = json.loads(SENTETIK_SONUC.read_text(encoding='utf-8'))
        kume, maske = pazartesi_kumesi(veri, m.T0, m.SON_PAZARTESI, p)
        satirlar = har_satirlari(veri, kume, maske, m.D_SON, p)
        aylar = sorted((int(k), v['beta']) for k, v in beklenen['katsayi_yolu'].items())
        for M, beta in aylar:
            egitim = [r for r in satirlar if r['t'] + HAFTA <= M and r['oz'] is not None and r['toplam'] is not None]
            b = har_katsayi([r['oz'] for r in egitim], [math.log(r['toplam']) for r in egitim], p)
            self.assertEqual(None if b is None else b.tolist(), beta, M)

        def katsayi(t):
            onceki = [b for M, b in aylar if M <= t]
            return onceki[-1] if onceki else None
        yol = s2_yolu(satirlar, katsayi, sorted(kume), p, bas_ms=m.DEGERLENDIRME_BAS)
        self.assertEqual(yol, {int(k): v for k, v in beklenen['s2_yolu'].items()})
        self.assertGreater(len(yol), 100)


class BankaTakvimiTest(unittest.TestCase):
    def test_ilk_s2_oncesi_ewma_sonrasi_har(self):
        veri = senaryo_verisi()
        p = Parametreler()
        beta = (1.9, 0.2, 0.0, 0.45)
        tk = banka_takvimi(veri, gun_ms(0), gun_ms(SENARYO_GUN), beta, p)
        self.assertEqual(tk.katsayi(gun_ms(1)), beta)
        # BTC/ETH hep evrende; m ozelligi >= 90 gun ve >= 8 artik haftasi -> ilk s^2 ancak ~149. gun Pazartesisi.
        self.assertTrue(tk.s2)
        ilk = next(t for t, v in tk.s2 if v is not None)
        self.assertTrue(all(pazartesi_mi(t) for t, _ in tk.s2))
        self.assertTrue(all(v is None for t, v in tk.s2 if t < ilk))      # tanimsiz haftalar acikca None
        self.assertGreaterEqual(ilk, gun_ms(90) + 8 * HAFTA - HAFTA)
        s = kos(veri, KosuAyarlari(t0_ms=gun_ms(140), t_son_ms=saat_ms(SENARYO_GUN * 24 - 1)),
                replace(p, sigma_tahmincisi='HAR', har_takvimi=tk))
        for k in s.kararlar:
            n = k.hedef.tanilar.get('har_sigma_sayisi', 0)
            if k.hedef.t_ms < ilk:
                self.assertEqual(n, 0)
            else:
                self.assertGreater(n, 0)


class S2YetersizTest(unittest.TestCase):
    """Codex T12-5: artik haftalari yetersizlesince takvim eski s^2'yi tasimaz (None -> EWMA)."""

    def test_yeterli_yetersiz_toparlanan(self):
        from motor.har import HarTakvimi
        p = Parametreler()
        t0 = gun_ms(2)
        while not pazartesi_mi(t0):
            t0 += 24 * 3_600_000
        satir = [{'t': t0 + w * HAFTA, 'c': c, 'oz': (0.0, 0.0, 0.0, 0.0),
                  'toplam': math.exp(0.01 * w + (0.3 if c == 'X' else -0.3))}
                 for w in list(range(0, 10)) + list(range(70, 80)) for c in ('X', 'Y')]
        pzt = [t0 + w * HAFTA for w in range(90)]
        yol = s2_yolu(satir, lambda t: (0.0, 0.0, 0.0, 0.0), pzt, p, hepsi=True)
        self.assertIsNone(yol[t0 + 5 * HAFTA])                  # 5 hafta < 8
        self.assertIsNotNone(yol[t0 + 10 * HAFTA])              # hafta 0..9
        self.assertIsNone(yol[t0 + 62 * HAFTA])                 # pencere hafta 10..61: artik yok
        self.assertIsNotNone(yol[t0 + 79 * HAFTA])              # hafta 70..78
        self.assertNotIn(t0 + 62 * HAFTA, s2_yolu(satir, lambda t: (0.0, 0.0, 0.0, 0.0), pzt, p))
        tk = HarTakvimi(aylar=((0, (0.0, 0.0, 0.0, 0.0)),), s2=tuple(sorted(yol.items())))
        self.assertIsNone(tk.artik_varyansi(t0 + 62 * HAFTA + 3 * 24 * 3_600_000))
        self.assertIsNotNone(tk.artik_varyansi(t0 + 20 * HAFTA))

if __name__ == '__main__':
    unittest.main()
