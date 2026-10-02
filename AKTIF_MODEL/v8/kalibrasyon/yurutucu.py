"""Kalibrasyon is birimlerinin hesabi (BANKA_ONKAYIT_TASLAK Ss3.7, 3. revizyon). Her birim yalniz kimliginden ve
dondurulmus koddan hesaplanir; duvar saati okunmaz, sonuc yalniz birim.sonuc_yaz ile yazilir (P12b kosucusu).

Duzey 1 birimi (ayar): 2.000 yol x SR izgarasi; olcut (n_yol, 6, 15) ve seyreltme (n_yol, 6, 6, 15) dizileri.
Duzey 2 birimleri (Ss3.7 "Motor yapilandirmasi"): birincil ayar (L = 1, 0,1M), mimari A/B, HAR banka modu
(dondurulmus katsayi = HAR secim sonucunun `dondurulan.beta`si; s^2 kosulan verinin kendi yuruyen artiklarindan).
Motor bankadaki gibi (Ss3.1 surekli kosu) verinin ilk gununden kesintisiz kosar; olcutler yalniz degerlendirme
penceresinden (Codex T12-7).
  birincil: tam olcum (banka/degerlendirme.birincil_olcum; B'de ayristirma ile B5) + B10 icin alt katki sirasi
  x2, x3:   maliyet carpani 2 / 3 ile tam kosu -> pencere SR'i
  cikarma:  aday listeden tek coin cikarilir (veri ayni), HAR takvimi o aday listesiyle yeniden kurulur -> SR
  null:     Ss3.5 null yolu (tohum hash(tohum_kal, 2, ayar, yol, p, j) ve (..., j, i)); N1-N6 ihlali T4 (durur) ->
            null yolunda A kosusu -> SR"""
import hashlib
import json
import math
from dataclasses import replace
from pathlib import Path

import numpy as np

from banka.degerlendirme import Pencere, birincil_olcum, sadece_sharpe
from banka.har_banka import banka_takvimi
from banka.pnl import coin_pnl
from banka.rejim_null import null_yolu
from motor.ayristirma import ayristir
from motor.geri_test import KosuAyarlari, kos
from motor.gorunum import GUN_MS, SAAT_MS
from motor.tipler import Parametreler

from . import duzey2_uretec as u
from .duzey1 import SR_IZGARASI, yol_uret
from .duzey1_olcut import ALANLAR, SEYRELTME, seyreltme_olculeri, sr_olculeri
from .tohum import TOHUM_KAL, uretec

V8 = Path(__file__).resolve().parents[1]
HAR_SONUC = V8.parent / 'ciktilar' / 'v8_har_secimi_20260929_01' / 'sonuc.json'
N_YOL_DUZEY1 = 2000
COIN_NO = {c: i + 1 for i, c in enumerate(u.COINLER)}
MALIYET = {'birincil': 1.0, 'x2': 2.0, 'x3': 3.0, 'cikarma': 1.0, 'null': 1.0}
MUHASEBE_TOL = 1e-8                 # ozdeslik hatasi / max(1, max |NAV|)


class NullDegismezHatasi(RuntimeError):
    """Ss3.5.7 N1-N6 ihlali: T4 (Ss2.5); kalibrasyon durur."""


class MuhasebeHatasi(RuntimeError):
    """T4-e (Ss2.5): NAV sonlu/pozitif degil, gunluk zinciri bozuk ya da muhasebe ozdesligi tolerans disi; sonuc
    yazilmaz, kalibrasyon durur (Codex T12-3)."""


def har_paketi() -> tuple:
    """(HAR sonuc dosyasinin sha256'si, dondurulmus beta): ikisi de ayni bayt okumasindan (Codex T12-9)."""
    veri = HAR_SONUC.read_bytes()
    beta = tuple(float(x) for x in json.loads(veri.decode('utf-8'))['dondurulan']['beta'])
    return hashlib.sha256(veri).hexdigest(), beta


def har_beta() -> tuple:
    return har_paketi()[1]


def muhasebe_kapisi(s, veri, ayristirma=None) -> dict:
    """Her birimin tamamlanma kapisi (Codex T12-3): NAV sonlu ve pozitif, gunluk hash zinciri saglam, coin basi P&L
    ozdesligi (ve B birincilinde ayristirma ozdesligi) tolerans icinde. Ihlal -> MuhasebeHatasi."""
    nav = np.asarray(s.nav, dtype=float)
    if len(nav) == 0 or not np.all(np.isfinite(nav)) or not np.all(nav > 0):
        raise MuhasebeHatasi("NAV sonlu ve pozitif degil")
    if not s.gunluk.dogrula():
        raise MuhasebeHatasi("gunluk hash zinciri bozuk")
    olcek = max(1.0, float(np.max(np.abs(nav))))
    cp = coin_pnl(s, veri)
    if not all(np.all(np.isfinite(v)) for d in (cp.pnl, cp.eski, cp.yeni) for v in d.values()):
        raise MuhasebeHatasi("coin P&L dizisinde sonlu olmayan deger")
    out = {'coin_pnl_hata': cp.ozdeslik_max_hata}
    if ayristirma is not None:
        # dnav yalniz gun sonu saatlerinde tanimlidir (digerleri NaN); oteki satirlar ve coin dizileri sonlu olmali
        diziler = [v for k, v in ayristirma.satirlar.items() if k != 'dnav']
        for d in (ayristirma.trend_coin, ayristirma.trend_eski, ayristirma.trend_yeni):
            diziler += list(d.values())
        if not all(np.all(np.isfinite(v)) for v in diziler):
            raise MuhasebeHatasi("ayristirma satirinda sonlu olmayan deger")
        out['ayristirma_hata'] = ayristirma.ozdeslik_max_hata
    for ad, x in out.items():
        if not math.isfinite(x) or x > MUHASEBE_TOL * olcek:
            raise MuhasebeHatasi(f"{ad} = {x} tolerans disi")
    return out


def duzey1_birimi(ayar_no: int, n_yol: int = N_YOL_DUZEY1) -> tuple:
    olcut = np.empty((n_yol, len(SR_IZGARASI), len(ALANLAR)))
    seyr = np.empty((n_yol, len(SR_IZGARASI), len(SEYRELTME), len(ALANLAR)))
    for i in range(n_yol):
        yol = yol_uret(ayar_no, i + 1)
        for j, sr in enumerate(SR_IZGARASI):
            a = sr_olculeri(yol, sr)
            olcut[i, j] = [a[k] for k in ALANLAR]
            seyr[i, j] = seyreltme_olculeri(yol, sr, a)
    govde = {'n_yol': n_yol, 'alanlar': list(ALANLAR), 'sr': list(SR_IZGARASI),
             'seyreltme': [list(x) for x in SEYRELTME]}
    return govde, {'olcut': olcut, 'seyreltme': seyr}


def duzey2_dilimleri() -> list:
    bas, out = u.ISINMA_GUN * 24, []
    for g in u.DILIM_GUN:
        out.append((bas, bas + g * 24))
        bas += g * 24
    return out


def _takvim(veri, beta):
    return banka_takvimi(veri, u.BAS_MS, u.BAS_MS + u.GUN * GUN_MS, beta, Parametreler())


def duzey2_birimi(k: dict, beta, pencere: Pencere = None, motor_bas_ms: int = None) -> dict:
    """k: birim kimligi (duzey 2). pencere ve motor_bas_ms yalniz testlerde (kisa kosu); varsayilan Duzey 2 penceresi
    ve verinin ilk gunu (u.BAS_MS)."""
    pen = pencere or u.pencere()
    motor_bas = u.BAS_MS if motor_bas_ms is None else motor_bas_ms
    tur = k['tur']
    veri, _ = u.yol_verisi(k['ayar_no'], k['yol_no'])
    govde = {}
    if tur == 'null':
        a_, y_, p_ = k['ayar_no'], k['yol_no'], k['null_no']
        veri, pay, deg = null_yolu(veri, u.BAS_MS, u.SAAT, duzey2_dilimleri(), COIN_NO,
                                   lambda j: uretec(TOHUM_KAL, 2, a_, y_, p_, j),
                                   lambda j, i: uretec(TOHUM_KAL, 2, a_, y_, p_, j, i))
        if not deg['gecti']:
            raise NullDegismezHatasi(str(deg['ihlaller'][:10]))
        govde.update({'ortak': pay['ortak'], 'toplam': pay['toplam']})
    elif tur == 'cikarma':
        coin = u.COINLER[k['cikan'] - 1]
        veri = replace(veri, adaylar=tuple(c for c in veri.adaylar if c != coin))
    takvim = _takvim(veri, beta)
    p = replace(Parametreler(), mimari=k['mimari'], sigma_tahmincisi='HAR', har_takvimi=takvim)
    s = kos(veri, KosuAyarlari(t0_ms=motor_bas, t_son_ms=pen.bit_ms - SAAT_MS, maliyet_k=MALIYET[tur]), p)
    govde.update({'son_hash': s.gunluk.son_hash, 's2_pazartesi': len(takvim.s2), 'karar_sayisi': len(s.kararlar),
                  'har_karar': sum(1 for x in s.kararlar if x.hedef.tanilar.get('har_sigma_sayisi', 0) > 0)})
    a = ayristir(s.gunluk, veri, p) if (tur == 'birincil' and k['mimari'] == 'B') else None
    govde['muhasebe'] = muhasebe_kapisi(s, veri, a)
    if tur == 'birincil':
        govde.update(birincil_olcum(s, veri, pen, k['mimari'], a))
        govde['alt_katki_no'] = [COIN_NO[c] for c in govde['alt_katki_sirasi']]
    else:
        govde['sr'] = sadece_sharpe(s, pen)
    return govde
