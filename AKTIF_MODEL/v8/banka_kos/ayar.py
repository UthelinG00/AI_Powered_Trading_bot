"""Banka koşusu ayarları, dönemler ve birim listesi (BANKA §3.1, §3.4, §3.5, §3.6, §4; ILERLEME_BANKA BK-1…BK-7).

Dönemler (§3.1):
- T0_Z1 = max(BTC ilk barı, ETH ilk barı) + 92 gün, izleyen ayın 1'ine (00:00 UTC) yuvarlanır; zaten ay başı 00:00 ise
  kendisi (BK-7). Açılışta veriden hesaplanır.
- Z1 dilimleri: 2020 = [T0_Z1, 2021-01-01), 2021, 2022, 2023H1 = [2023-01-01, 2023-06-24). Birincil örneklem
  [T0_Z1, 2023-06-24). Z2 = [2026-07-01, 2026-09-24). D segmenti = [2023-07-01, 2026-07-01).
- BTC/ETH'nin görülmüş 7 günü (mühür §4) bütün metriklerden düşülür (BK-5): liste açılışta mühür belgesinden okunur ve
  koşuya girdi olarak verilir; kod listeyi yalnız uygular.
Birimler (BK-1): her tam motor koşusu bir birimdir; kimlik kanonik JSON. B10 çıkarma birimleri birincil sonuçtan
türetilir (BK-6; kosucu), bu listede yoktur.
"""
from datetime import datetime, timezone

GUN_MS = 86_400_000


def _ms(y: int, a: int, g: int) -> int:
    return int(datetime(y, a, g, tzinfo=timezone.utc).timestamp() * 1000)


BIRINCIL_SON_MS = _ms(2023, 6, 24)
Z1_DILIM_SINIR = (_ms(2021, 1, 1), _ms(2022, 1, 1), _ms(2023, 1, 1))
Z2_BAS_MS, Z2_SON_MS = _ms(2026, 7, 1), _ms(2026, 9, 24)
D_BAS_MS, D_BIT_MS = _ms(2023, 7, 1), _ms(2026, 7, 1)

NAV_BIRINCIL = 100_000.0
NAV_IZGARA = (100_000.0, 1_000_000.0, 5_000_000.0)          # R1
MALIYET = (1.0, 2.0, 3.0)                                   # R1, B3
KELLY_L = (0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 4.0)               # §4
KELLY_MALIYET = (1.0, 2.0)
N_NULL = 500                                               # B7
DELIST_H_L = (0.50, 0.90)                                  # R9
DEMO_NAV = 5_000.0                                         # R14
B10_N = 10


def t0_z1(btc_ilk_ms: int, eth_ilk_ms: int) -> int:
    t = max(int(btc_ilk_ms), int(eth_ilk_ms)) + 92 * GUN_MS
    d = datetime.fromtimestamp(t / 1000, timezone.utc)
    if d.day == 1 and t % GUN_MS == 0:
        return t
    y, a = (d.year + 1, 1) if d.month == 12 else (d.year, d.month + 1)
    return _ms(y, a, 1)


def z1_dilimleri(t0: int) -> tuple:
    """((ad, bas_ms, bit_ms), ...): 2020, 2021, 2022, 2023H1 (§3.4 B6)."""
    s = (t0,) + Z1_DILIM_SINIR + (BIRINCIL_SON_MS,)
    return tuple((ad, s[i], s[i + 1]) for i, ad in enumerate(('2020', '2021', '2022', '2023H1')))


def _birim(grup: str, mimari: str, **k) -> dict:
    b = {'grup': grup, 'mimari': mimari, 'L': 1.0, 'maliyet_k': 1.0, 'nav0': NAV_BIRINCIL, 'evren': 'banka',
         'h_L': 0.10, 'lot': True}
    b.update(k)
    return b


def birimler(mimari: str) -> list:
    """Taban birim listesi (B10 çıkarma birimleri hariç). mimari: kapı sonucu M. M = B ise R8 için bağımsız A koşusu."""
    if mimari not in ('A', 'B'):
        raise ValueError("mimari A ya da B")
    out = [_birim('birincil', mimari)]
    out += [_birim('izgara', mimari, nav0=n, maliyet_k=k) for n in NAV_IZGARA for k in MALIYET
            if not (n == NAV_BIRINCIL and k == 1.0)]
    out += [_birim('kelly', mimari, L=L, maliyet_k=k) for L in KELLY_L for k in KELLY_MALIYET
            if not (L == 1.0)]                                            # L = 1: birincil ve ızgara birimleri
    out += [_birim('cikarma_btc_eth', mimari, cikan=c) for c in ('BTCUSDT', 'ETHUSDT')]
    out.append(_birim('k_evren', mimari, evren='K'))
    out += [_birim('delist', mimari, h_L=h) for h in DELIST_H_L]
    out.append(_birim('lot_kapali', mimari, lot=False))
    out.append(_birim('demo_nav', mimari, nav0=DEMO_NAV))
    out.append(_birim('long_beta', mimari))                                # R3 (pasif long kitap; long_beta.py)
    if mimari == 'B':
        out.append(_birim('a_ayristirma', 'A'))                           # R8
    out += [_birim('null', mimari, null_no=p) for p in range(1, N_NULL + 1)]
    return out
