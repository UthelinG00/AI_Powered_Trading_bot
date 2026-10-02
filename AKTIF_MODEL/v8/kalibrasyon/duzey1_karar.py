"""Duzey 1 kararlari (BANKA_ONKAYIT_TASLAK Ss3.3 kural 2-4; Ss3.7 "Esik kurallari", "Birlesik yanlis kabul"):
e_B5, e_B10, k_B6 sabitlenir; sonra B2 turu ve d*; P(KABUL | SR = 0) <= %5 butun ayarlarda saglanmazsa tek onceden
yazili ayar (B3 x2 ve B4 esigi 0,30 -> 0,40), yine saglanmazsa "kilit bekler". Mekaniktir; kullaniciya soru yoktur.

N: deneme sayisi = N_REV1 (159) + N_v8; N_v8 = sum_satir max(1, varyant_sayisi) (Ss3.3), kalibrasyon aninda defterden."""
import csv
from dataclasses import replace

import numpy as np

from .duzey1 import SR_IZGARASI
from .duzey1_esik import (AYAR_ESIK, E_B10_UST, E_B5_UST, IX, REF, Kurallar, dsr_vek, e_b10, e_b5, k_b6,
                          kabul_oranlari)
from .sigma_sr import N_REV1

D_ADAYLARI = (0.50, 0.75, 0.90, 0.95)
B2_GUC_ESIGI = 0.25
FAR_HEDEF = 0.05
SR0_IX = SR_IZGARASI.index(0.0)


def n_v8(defter_yolu) -> int:
    with open(defter_yolu, encoding='utf-8', newline='') as f:
        return sum(max(1, int(r['varyant_sayisi'] or 0)) for r in csv.DictReader(f))


def _far_tamam(sonuclar: dict, k: Kurallar) -> tuple:
    oran = kabul_oranlari(sonuclar, k)
    en_kotu = max(float(v[SR0_IX]) for v in oran.values())
    return en_kotu <= FAR_HEDEF, en_kotu, oran


def duzey1_karari(sonuclar: dict, N: int, sigma_sr: float) -> dict:
    """sonuclar: ayar_no -> (n_yol, len(SR), ALANLAR). Doner: kurallar, durum ('TAMAM' | 'KILIT_BEKLER'), ara degerler."""
    e5, e10, k6 = e_b5(sonuclar), e_b10(sonuclar), k_b6(sonuclar)
    kayit = {'e_b5_ham': e5, 'e_b10_ham': e10, 'k_b6': k6, 'N': N, 'sigma_sr_bag': sigma_sr}
    taban = Kurallar(N=N, sigma_sr=sigma_sr, b2_bagli=False, d=0.50,
                     e_b5=e5 if e5 <= E_B5_UST else None, k_b6=k6, e_b10=e10 if e10 <= E_B10_UST else None)
    # Kural 2: B2 turu (butun ayarlarin ortalamasi, d = 0,50, SR = 1,0).
    guc = float(np.mean([np.mean(dsr_vek(a[:, REF, :], N, sigma_sr) >= 0.50) for a in sonuclar.values()]))
    kayit['b2_guc_d050_sr1'] = guc
    b2_bagli = guc >= B2_GUC_ESIGI
    denemeler = []
    for ayarli in (False, True):
        k0 = replace(taban, b3_esik=AYAR_ESIK, b4_esik=AYAR_ESIK) if ayarli else taban
        adaylar = D_ADAYLARI if b2_bagli else (None,)
        for d in adaylar:
            k = replace(k0, b2_bagli=b2_bagli, d=d if d is not None else 0.50)
            tamam, en_kotu, oran = _far_tamam(sonuclar, k)
            denemeler.append({'ayarli': ayarli, 'd': d, 'en_kotu_far_sr0': en_kotu, 'tamam': tamam})
            if tamam:
                kayit.update({'durum': 'TAMAM', 'kurallar': k, 'denemeler': denemeler,
                              'kabul_oranlari': {no: v.tolist() for no, v in oran.items()}})
                return kayit
    kayit.update({'durum': 'KILIT_BEKLER', 'kurallar': None, 'denemeler': denemeler})
    return kayit
