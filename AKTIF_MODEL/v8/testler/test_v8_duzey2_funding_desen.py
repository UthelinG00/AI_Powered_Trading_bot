"""Düzey 2 üreteci ve geç funding deseni (2. tur madde 3b; Codex T18 B5 açık sorusu). Pozisyondan bağımsız, veri düzeyinde:
motorun dolgu koşulu (motor/funding.py funding_saati: bar akıyor ve son gerçek kayıttan bu yana ≥ 1,5·Δ; Δ son 30 günün
en uzun kayıt aralığı) Düzey 2 yollarında hangi saatlerde sağlanır ve bu dolguları hangi gerçek kayıt ters kaydeder.

Üreteç (kalibrasyon/duzey2_uretec.py veri_kur): funding her aralık katında (8h; iki coinde 60 gün 4h) ilk bardan sonra
ve ölümden önce var; borsa çapı boşlukta bar yok, funding sürer (bar akmadığı için dolgu yok); ölen coinde ölümden sonra
bar ve funding yok. Beklenen tek desen: 4h penceresinin bitiminde (S = (bas_gun + 60)·24) Δ son 30 günde 4h kalır, ilk 8h
aralığında S+6 ve S+7'de dolgu tetiklenir (S+1…S+7 saatleri), S+8'deki gerçek kayıt (arşiv aralığı 8h → kapsam
(S, S+8]) hepsini ters kaydeder. Geri testte gerçek kayıt hep zamanında işlenir (motor/geri_test.py funding_adimi her
saat), geç kayıt yoktur."""
import sys as _sys
import unittest
from pathlib import Path as _Path

import numpy as np

V8_DIR = _Path(__file__).resolve().parent.parent
if str(V8_DIR) not in _sys.path:
    _sys.path.insert(1, str(V8_DIR))

from kalibrasyon.duzey2_uretec import BAS_MS, FUNDING_4H_GUN, yol_verisi  # noqa: E402
from motor.funding import bar_akisi_suruyor, delta_aralik_saat, kapsanan_aralik_saat  # noqa: E402
from motor.gorunum import SAAT_MS, ilk_bar_ms  # noqa: E402
from motor.tipler import Parametreler  # noqa: E402

YOLLAR = ((0, 1), (0, 2), (1, 3), (2, 5), (3, 1), (4, 7))
P = Parametreler()


def dolgu_saatleri(f, s) -> list:
    """Dolgu koşulunun sağlandığı saatler (ms). Adaylar: kayıttan en az 6 saat sonra (1,5·Δ ≥ 1,5·4)."""
    d = f.damga_ms
    aday = []
    for j in range(len(d) - 1):
        if d[j + 1] - d[j] >= 6 * SAAT_MS:
            aday += range(int(d[j]) + 6 * SAAT_MS, int(d[j + 1]), SAAT_MS)
    if len(d) and len(s.acilis_ms):
        aday += range(int(d[-1]) + 6 * SAAT_MS, int(s.acilis_ms[-1]) + 2 * SAAT_MS, SAAT_MS)
    out = []
    for T in aday:
        ust = int(np.searchsorted(d, T, side='right'))
        son = int(d[ust - 1]) if ust > 0 else ilk_bar_ms(s)
        if son == T or not bar_akisi_suruyor(s, T):
            continue
        if T - son >= P.funding_eksik_carpan * delta_aralik_saat(f, T, P) * SAAT_MS:
            out.append(T)
    return out


class Duzey2FundingDeseniTest(unittest.TestCase):
    def test_tek_desen_4h_donusu_ve_tam_ters_kayit(self):
        toplam = 0
        for ayar, yol in YOLLAR:
            veri, ham = yol_verisi(ayar, yol)
            f4 = dict(ham.yasam.funding_4h)
            olum = dict(ham.yasam.olen)
            for c, f in veri.funding.items():
                s = veri.barlar[c]
                saatler = dolgu_saatleri(f, s)
                beklenen = []
                if c in f4 and (f4[c] + FUNDING_4H_GUN) < olum.get(c, 10 ** 9):
                    S = BAS_MS + (f4[c] + FUNDING_4H_GUN) * 24 * SAAT_MS
                    beklenen = [S + 6 * SAAT_MS, S + 7 * SAAT_MS]
                self.assertEqual(saatler, beklenen, (ayar, yol, c))
                if beklenen:
                    j = int(np.searchsorted(f.damga_ms, S + 8 * SAAT_MS))
                    self.assertEqual(int(f.damga_ms[j]), S + 8 * SAAT_MS)
                    self.assertEqual(kapsanan_aralik_saat(f, j, P), 8.0)       # (S, S+8]: S+1…S+7 dolguları
                    toplam += len(saatler)
        self.assertEqual(toplam, 2 * 2 * len(YOLLAR))                          # yol başına 2 coin × 2 saat


if __name__ == '__main__':
    unittest.main()
