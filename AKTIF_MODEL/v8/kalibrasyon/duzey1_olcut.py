"""Duzey 1 olcut eslemesi (BANKA_ONKAYIT_TASLAK Ss3.7 "Olcut eslemesi (Duzey 1)"). Bir yol ve bir SR_hedef icin
esikten bagimsiz olcut girdileri; esikler P10'da (duzey1_esik) uygulanir.

Esleme:
- B2: X'in gunluk SR, carpiklik, basiklik, eta ve T'si (DSR toplama adiminda N_kilit ve sigma_SR_bag ile).
- B3: maliyet 2K ve 3K ile X yeniden (ayni gurultu ve epizotlar; m 1x ile kalir) -> SR.
- B4: dilimler (T - 904, 365, 365, 174); toplam log getirisi en yuksek dilim cikarilir, kalan gunlerin SR'i.
  YORUM: X birim olceklidir (gunluk std ~ sigma_P); log getiri icin X once gerceklesen yillik vol %15'e dogrusal
  olceklenir (B11 ile ayni olcek), sonra dilim basina sum ln(1 + x). SR olcekten bagimsizdir; olcek yalniz dilim
  siralamasini belirler.
- B5: butun hatlarin epizot P&L'leri (epizot icindeki gunlerin (x + F - K)/J toplami); en buyuk 3'un toplami / toplam
  net P&L (sum X); toplam <= 0 ise inf.
- B6: dort dilimde SR > 0 sayisi.
- B8: X - F serisinin SR'i.
- B9: X^K = 0,7 X_0 + sqrt(0,51) Y_0 + SR_hedef sigma_P / sqrt365; X_0 ve Y_0 SR_hedef = 0 serileri (net ortalama 0),
  Y bagimsiz 15 hatlik portfoy; sabit kaydirma populasyon net SR'ini SR_hedef yapar. SR(X^K).
- B10: mutlak net katkisi en buyuk 10 hat (esitlikte kucuk hat numarasi); r'inci siradaki hat r'inci ikame hattiyla
  degistirilir (tek tek); en buyuk SR dususu.
- B11: X %15 vol'e olceklenir; bilesik NAV'in MDD'si.

B seyreltme raporu (Ss3.7 "B seyreltmesi (rapor)"; karar girdisi degildir). Carry serisi
C = sigma_C (rho X_0 / sigma_P + sqrt(1 - rho^2) w) + SR_C sigma_C / sqrt365, sigma_C = sigma_P / 3, rho {0; 0,30},
SR_C {-0,3; 0; 0,3}; w yolun carry gurultusu. B serisi Z = X + C. SR, DSR girdileri, B3 (Z'de trend maliyeti 2K/3K;
carry maliyeti SR_C'nin icinde), B4, B6, B9 (SR(X^K + C)), B10 (Z uzerinde ikame: SR(Z) - SR(X_ikame + C)) ve B11 B'ye
ait; B5 (trend sanal bacagi; bankada da oyle) ve B8 (fiyat bileseni; modelde carry P&L'i funding sayilir) tanim geregi
A'dakiyle ayni (Codex T12-8)."""
import math

import numpy as np

from banka import olcutler as o

from .duzey1 import B9_KARISIM, J, SR_IZGARASI, hat_net, portfoy

ALANLAR = ('sr', 'sr_gunluk', 'g3', 'g4', 'eta', 'T', 'b3_2', 'b3_3', 'b4', 'b5', 'b6', 'b8', 'b9', 'b10', 'b11')


def _olcekli(x: np.ndarray, hedef_vol: float = 0.15) -> np.ndarray:
    s = float(np.std(x, ddof=1))
    return x * (hedef_vol / (s * math.sqrt(365))) if s > 0 else x


def _b10_sira(net: np.ndarray, n: int) -> list:
    katki = net.sum(axis=1) / J
    return sorted(range(J), key=lambda j: (-abs(katki[j]), j))[:n]


def sr_olculeri(yol, sr_hedef: float) -> dict:
    ay = yol.ayar
    net = np.array([hat_net(h, ay, sr_hedef, 1) for h in yol.hatlar])            # (J, T)
    X = net.mean(axis=0)
    d = o.dsr(X, 2, 0.30)
    etiket = np.repeat(np.arange(4), ay.dilim_gun())
    b4, _ = o.en_iyi_dilim_haric(_olcekli(X), etiket)
    epizot = []
    for j, h in enumerate(yol.hatlar):
        epizot.extend((np.bincount(h.epizot, weights=net[j] / J)).tolist())
    sira = _b10_sira(net, len(yol.ikame))
    sr_ana = o.sharpe(X)
    sr_cik = []
    for r, j in enumerate(sira):
        yeni = X + (hat_net(yol.ikame[r], ay, sr_hedef, 1) - net[j]) / J
        sr_cik.append(o.sharpe(yeni))
    X0 = portfoy(yol.hatlar, ay, 0.0, 1)
    Y0 = portfoy(yol.y_hatlar, ay, 0.0, 1)
    XK = B9_KARISIM * X0 + math.sqrt(1.0 - B9_KARISIM ** 2) * Y0 + sr_hedef * ay.sigma_P / math.sqrt(365)
    return {
        'sr': sr_ana, 'sr_gunluk': d['sr_gunluk'], 'g3': d['g3'], 'g4': d['g4'], 'eta': d['eta'], 'T': float(d['T']),
        'b3_2': o.sharpe(portfoy(yol.hatlar, ay, sr_hedef, 2)), 'b3_3': o.sharpe(portfoy(yol.hatlar, ay, sr_hedef, 3)),
        'b4': b4,
        'b5': o.epizot_payi(epizot, float(X.sum())),
        'b6': float(sum(1 for x in o.dilim_sharpeleri(X, etiket) if x > 0)),
        'b8': o.sharpe(X - ay.F()),
        'b9': o.sharpe(XK),
        'b10': o.en_buyuk_dusus(sr_ana, sr_cik),
        'b11': o.vol_olcekli_mdd(X),
    }


def yol_olculeri(yol, sr_izgarasi=SR_IZGARASI) -> np.ndarray:
    """(len(sr_izgarasi), len(ALANLAR)) dizi."""
    return np.array([[sr_olculeri(yol, s)[a] for a in ALANLAR] for s in sr_izgarasi])


SEYRELTME = tuple((rho, src) for rho in (0.0, 0.30) for src in (-0.3, 0.0, 0.3))
CARRY_ORAN = 1.0 / 3.0


def seyreltme_olculeri(yol, sr_hedef: float, a: dict = None) -> np.ndarray:
    """(len(SEYRELTME), len(ALANLAR)): B serisinin olcut girdileri; B5, B8, B9, B10 A'dakinden (a; verilmezse
    hesaplanir) kopyalanir."""
    ay = yol.ayar
    a = sr_olculeri(yol, sr_hedef) if a is None else a
    net = np.array([hat_net(h, ay, sr_hedef, 1) for h in yol.hatlar])
    X = net.mean(axis=0)
    X0 = portfoy(yol.hatlar, ay, 0.0, 1)
    Y0 = portfoy(yol.y_hatlar, ay, 0.0, 1)
    XK = B9_KARISIM * X0 + math.sqrt(1.0 - B9_KARISIM ** 2) * Y0 + sr_hedef * ay.sigma_P / math.sqrt(365)
    sira = _b10_sira(net, len(yol.ikame))
    ikameli = [X + (hat_net(yol.ikame[r], ay, sr_hedef, 1) - net[j]) / J for r, j in enumerate(sira)]
    etiket = np.repeat(np.arange(4), ay.dilim_gun())
    s_c = CARRY_ORAN * ay.sigma_P
    out = []
    for rho, src in SEYRELTME:
        C = s_c * (rho * X0 / ay.sigma_P + math.sqrt(1.0 - rho * rho) * yol.carry_w) + src * s_c / math.sqrt(365)
        Z = X + C
        d = o.dsr(Z, 2, 0.30)
        b = dict(a)
        b.update({'sr': o.sharpe(Z), 'sr_gunluk': d['sr_gunluk'], 'g3': d['g3'], 'g4': d['g4'], 'eta': d['eta'],
                  'b3_2': o.sharpe(portfoy(yol.hatlar, ay, sr_hedef, 2) + C),
                  'b3_3': o.sharpe(portfoy(yol.hatlar, ay, sr_hedef, 3) + C),
                  'b4': o.en_iyi_dilim_haric(_olcekli(Z), etiket)[0],
                  'b6': float(sum(1 for x in o.dilim_sharpeleri(Z, etiket) if x > 0)),
                  'b9': o.sharpe(XK + C),
                  'b10': o.en_buyuk_dusus(o.sharpe(Z), [o.sharpe(xi + C) for xi in ikameli]),
                  'b11': o.vol_olcekli_mdd(Z)})
        out.append([b[k] for k in ALANLAR])
    return np.array(out)
