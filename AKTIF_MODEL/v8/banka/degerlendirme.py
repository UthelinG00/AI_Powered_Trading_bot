"""Bir motor kosusundan degerlendirme penceresinin olcut girdileri (BANKA_ONKAYIT_TASLAK Ss3.1, Ss3.4; kalibrasyon
Duzey 2 ve banka ortak). Esik uygulanmaz: esikler (d*, e_B5, k_B6, e_B10) Duzey 1'de sabitlenir, kabul toplama
adiminda hesaplanir.

Gun d = [d, d + 24h); gunluk basit getiri r_d = NAV(d + 24h) / NAV(d) - 1 (Ss3.1). NAV(pencere basi) kosunun o andaki
NAV'idir (kosu pencere basinda basladiysa nav0).
- B8 serisi: (dNAV_d - funding_d) / NAV(d); funding_d kosunun gercek funding nakdi (funding, dolgu, ters kayit). B'de
  bu, butun fiyat satirlari - maliyet + netleme + icra artiginin fiyat kismidir (MIMARI Ss4.7 satirlarinin toplami).
- B5: M = A coin basi net pozisyon epizotlari (banka/pnl.py); M = B trend sanal bacagi (ayristirma.trend_coin,
  trend_q). Yalniz pencere saatleri; pencere basinda suren epizot pencere basinda baslamis sayilir. Payda: A'da
  pencerenin toplam net P&L'i, B'de trend sanal bacaginin net P&L'i. Funding'in epizot atfi (Codex T18): pencere
  icinde kayda gecen funding parcasi (coin_pnl.fon_ozgun, ayristirma.trend_fon_ozgun) OZGUN saatin basindaki
  pozisyonun epizotuna gider; ozgun saat pencereden onceyse ve o epizot pencere basina kadar kesintisiz suruyorsa pencere
  basinda suren epizota, surmuyorsa hicbir pencere epizotuna. Payda ve katkilar kayit saatiyle kalir.
- B10 secimi icin net katki: pencerede coinin toplam P&L'i (coin_pnl).
- Haric gunler (BANKA Ss3.1, BK-5: BTC/ETH'nin gorulmus gunleri): gunluk getiri tabanli butun olcutlerden (SR, DSR
  anlari, dilimler, B4, B8, B11) o gunlerin getirisi dusulur; saatlik girdilerde (B5 epizotlari, B10 katkisi, B5
  paydasi) o gunlerin saatlerinin P&L'i sifirlanir (pozisyon surekliligi korunur). Bos iken sonuc degismez."""
from dataclasses import dataclass

import numpy as np

from motor.gorunum import GUN_MS, SAAT_MS

from . import olcutler as o
from .pnl import coin_pnl, epizot_pnl, gunluk_topla


class DegerlendirmeHatasi(ValueError):
    """Kosu pencereyi kapsamiyor ya da ozdeslik bozuk."""


@dataclass(frozen=True)
class Pencere:
    bas_ms: int                   # ilk degerlendirme gunu 00:00 UTC
    dilim_gun: tuple              # dilim uzunluklari (gun), takvim sirasiyla
    haric_gunler: tuple = ()      # olcutlerden dusulen gunler (00:00 UTC ms; BK-5)

    @property
    def gun_sayisi(self) -> int:
        return int(sum(self.dilim_gun))

    @property
    def bit_ms(self) -> int:
        return self.bas_ms + self.gun_sayisi * GUN_MS

    def gunler(self) -> np.ndarray:
        return self.bas_ms + np.arange(self.gun_sayisi, dtype=np.int64) * GUN_MS

    def etiket(self) -> np.ndarray:
        return np.repeat(np.arange(len(self.dilim_gun)), self.dilim_gun)

    def gun_maskesi(self) -> np.ndarray:
        """Olcute giren gunler (haric gunler False)."""
        return ~np.isin(self.gunler(), np.asarray(self.haric_gunler, dtype=np.int64))

    def saat_maskesi(self, saat_ms) -> np.ndarray:
        """Saatlik dizide haric gunlerin saatleri 0, digerleri 1 (carpan)."""
        gun = (np.asarray(saat_ms, dtype=np.int64) // GUN_MS) * GUN_MS
        return (~np.isin(gun, np.asarray(self.haric_gunler, dtype=np.int64))).astype(float)


def _nav_sinirlari(sonuc, pencere: Pencere, nav0: float) -> np.ndarray:
    nav_ms = np.asarray(sonuc.nav_ms, dtype=np.int64)
    nav = np.asarray(sonuc.nav, dtype=float)
    sinirlar = pencere.bas_ms + np.arange(pencere.gun_sayisi + 1, dtype=np.int64) * GUN_MS
    ix = np.searchsorted(nav_ms, sinirlar)
    out = np.empty(len(sinirlar))
    for n, (t, i) in enumerate(zip(sinirlar.tolist(), ix.tolist())):
        if i < len(nav_ms) and nav_ms[i] == t:
            out[n] = nav[i]
        elif n == 0 and (len(nav_ms) == 0 or t == nav_ms[0] - SAAT_MS):
            out[n] = nav0                      # kosu pencere basinda basladi
        else:
            raise DegerlendirmeHatasi(f"kosu {t} anindaki NAV'i icermiyor")
    return out


def gunluk_getiri(sonuc, pencere: Pencere) -> np.ndarray:
    nav0 = float(next(k for k in sonuc.gunluk.kayitlar() if k.tur == 'baslangic').veri['nav0'])
    s = _nav_sinirlari(sonuc, pencere, nav0)
    return s[1:] / s[:-1] - 1.0


def sadece_sharpe(sonuc, pencere: Pencere) -> float:
    """x2/x3, cikarma ve null birimleri: pencerenin Sharpe'i. Haric gunler birincil olcumdeki gibi dusulur (BK-5; B7
    null istatistigi gercek yolla ayni takvim gunlerinden, BANKA Ss3.5.6; Codex T18). Haric gun yoksa maske butunuyle
    dogrudur ve sonuc eskisiyle bit duzeyinde aynidir (kalibrasyon pencereleri haric gun tasimaz)."""
    return o.sharpe(gunluk_getiri(sonuc, pencere)[pencere.gun_maskesi()])


def _ozgun_dilim(parcalar, saat_ms, q_tam, icinde, sm_tam) -> list:
    """(kayit satiri, ozgun_ms, tutar) -> epizot_pnl'in (i, j, x) girdisi (pencere dilimi indeksleri; Codex T18).
    Yalniz pencere icinde kayda gecen parcalar, saat maskesiyle carpilarak. j: ozgun satir pencere icindeyse onun
    dilim indeksi; oncesindeyse ve ozgun pozisyonun epizotu pencere basina kadar kesintisiz suruyorsa 0 (pencere basinda
    suren epizot), degilse None."""
    saat_ms = np.asarray(saat_ms, dtype=np.int64)
    w = np.flatnonzero(icinde)
    if not len(w) or not parcalar:
        return []
    w0, w1 = int(w[0]), int(w[-1]) + 1
    out = []
    for i, h, t in parcalar:
        if not (w0 <= i < w1):
            continue
        x = float(t) * float(sm_tam[i])
        if x == 0.0:
            continue
        j = int(np.searchsorted(saat_ms, h))
        if j >= len(saat_ms) or saat_ms[j] != h:
            raise DegerlendirmeHatasi(f"funding parcasinin ozgun saati saat izgarasinda yok: {h}")
        if j >= w0:
            out.append((i - w0, j - w0, x))
            continue
        s0 = np.sign(q_tam[j - 1]) if j > 0 else 0.0
        suruyor = s0 != 0 and bool(np.all(np.sign(q_tam[j - 1:w0]) == s0))
        out.append((i - w0, 0 if suruyor else None, x))
    return out


def birincil_olcum(sonuc, veri, pencere: Pencere, mimari: str, ayristirma=None, btc_eth=('BTCUSDT', 'ETHUSDT'),
                   tolerans: float = 1e-6, b5: bool = True) -> dict:
    """Birincil kosunun olcut girdileri. mimari 'B' ve b5 ise ayristirma (motor.ayristirma.ayristir sonucu) verilmelidir.
    b5 False: B5 epizotlari hesaplanmaz (b5_pay, b5_epizot_sayisi, b5_payda None); B'de ayristirma gerekmez. B5 yalniz
    birincil birimin olcutudur (BANKA Ss3.4 "aksi yazilmadikca birincil ayar"); izgara, Kelly, cikarma, K-evren ve rapor
    birimleri SR, NAV, katki ve stres girdilerini kullanir (Codex T18)."""
    nav0 = float(next(k for k in sonuc.gunluk.kayitlar() if k.tur == 'baslangic').veri['nav0'])
    sinir = _nav_sinirlari(sonuc, pencere, nav0)
    r = sinir[1:] / sinir[:-1] - 1.0
    cp = coin_pnl(sonuc, veri)
    if cp.ozdeslik_max_hata > tolerans * max(1.0, float(np.max(np.abs(sonuc.nav)))):
        raise DegerlendirmeHatasi(f"coin P&L ozdesligi bozuk: {cp.ozdeslik_max_hata}")
    gunler = pencere.gunler()
    fund = np.zeros(len(gunler))
    for v in cp.funding.values():
        fund += gunluk_topla(cp.saat_ms, v, gunler)
    dnav = np.diff(sinir)
    r_b8 = (dnav - fund) / sinir[:-1]
    gm = pencere.gun_maskesi()
    r, r_b8, dnav = r[gm], r_b8[gm], dnav[gm]
    icinde = (cp.saat_ms >= pencere.bas_ms) & (cp.saat_ms < pencere.bit_ms)
    sm_tam = pencere.saat_maskesi(cp.saat_ms)
    sm = sm_tam[icinde]
    katki = {c: float((v[icinde] * sm).sum()) for c, v in sorted(cp.pnl.items())}
    ilk = int(np.argmax(icinde)) if icinde.any() else 0
    if mimari not in ('A', 'B'):
        raise DegerlendirmeHatasi(f"bilinmeyen mimari: {mimari}")
    if not b5:
        epizotlar, payda = None, None
    elif mimari == 'A':
        epizotlar = []
        for c in sorted(cp.pnl):
            q_once = float(cp.q[c][ilk - 1]) if ilk > 0 else 0.0     # pencere basinda suren pozisyon (T13-1)
            oz = _ozgun_dilim((cp.fon_ozgun or {}).get(c, ()), cp.saat_ms, cp.q[c], icinde, sm_tam)
            epizotlar += epizot_pnl(cp.q[c][icinde], cp.eski[c][icinde] * sm, cp.yeni[c][icinde] * sm, q_once,
                                    ozgun=oz)
        payda = float(dnav.sum())
    elif mimari == 'B':
        if ayristirma is None:
            raise DegerlendirmeHatasi("mimari B icin ayristirma gerekli")
        a_ic = (ayristirma.saat_ms >= pencere.bas_ms) & (ayristirma.saat_ms < pencere.bit_ms)
        a_sm_tam = pencere.saat_maskesi(ayristirma.saat_ms)
        a_sm = a_sm_tam[a_ic]
        fon_oz = getattr(ayristirma, 'trend_fon_ozgun', None) or {}
        a_ilk = int(np.argmax(a_ic)) if a_ic.any() else 0
        epizotlar, payda = [], 0.0
        for c in sorted(ayristirma.trend_coin):
            x = ayristirma.trend_coin[c][a_ic] * a_sm
            q_tam = ayristirma.trend_q.get(c, np.zeros(len(ayristirma.saat_ms)))
            q_once = float(q_tam[a_ilk - 1]) if a_ilk > 0 else 0.0
            oz = _ozgun_dilim(fon_oz.get(c, ()), ayristirma.saat_ms, q_tam, a_ic, a_sm_tam)
            epizotlar += epizot_pnl(q_tam[a_ic], ayristirma.trend_eski[c][a_ic] * a_sm,
                                    ayristirma.trend_yeni[c][a_ic] * a_sm, q_once, ozgun=oz)
            payda += float(x.sum())
    etiket = pencere.etiket()[gm]
    b4_sr, b4_cikan = o.en_iyi_dilim_haric(r, etiket, tuple(range(len(pencere.dilim_gun))))
    d = o.dsr(r, 2, 0.30)                    # yalniz an girdileri; DSR toplama adiminda N ve sigma_SR ile
    return {
        'r': [float(x) for x in r],
        'sr': o.sharpe(r),
        'sr_gunluk': d['sr_gunluk'], 'g3': d['g3'], 'g4': d['g4'], 'eta': d['eta'], 'T': d['T'],
        'b4_sr': b4_sr, 'b4_cikan': int(b4_cikan),
        'dilim_sr': o.dilim_sharpeleri(r, etiket, tuple(range(len(pencere.dilim_gun)))),
        'b5_pay': None if epizotlar is None else o.epizot_payi(epizotlar, payda),
        'b5_epizot_sayisi': None if epizotlar is None else len(epizotlar), 'b5_payda': payda,
        'b8_sr': o.sharpe(r_b8),
        'b11_mdd': o.vol_olcekli_mdd(r),
        'katki': katki,
        'alt_katki_sirasi': [c for c, _ in sorted(((c, x) for c, x in katki.items() if c not in btc_eth),
                                                  key=lambda cx: (-abs(cx[1]), cx[0]))],
        'ozdeslik_hata': cp.ozdeslik_max_hata,
    }
