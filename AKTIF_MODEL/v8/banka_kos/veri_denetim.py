"""Banka koşu öncesi veri denetimi, T2 (BANKA §2.3, §2.5, §8.1 `veri_raporu.json`; K2-07; 6.11; netleştirme 17 a, g).

`banka_kos.py`'den önce koşar; kararı `VERI_DENETIM.json`'a yazılır ve hash'lenir. T2 yoksa koşu başlar; koşudan sonra
veri gerekçesiyle T2 ileri sürülemez. T2 koşulları (§2.5):
  (1) onarılamayan CHECKSUM hatası: son durumu CHECKSUM_HATASI, geçersiz TAMAM satırı (sha256 ya da checksum eksik ya
      da biçimsiz), sha256 ≠ checksum, ya da ilk TAMAM satırındaki bağlayıcı sha256'nın sonradan değişmesi;
  (2) birincil örneklemde [T0_Z1, 2023-06-24) BTC ya da ETH saatlerinin > %1'i eksik;
  (3) K coinlerinin > %10'unda hiç veri yok.
INDIRME_HATASI ve YOK ayrıca sayılır (T2 değil; eksik veri (2) ve (3) ile yakalanır).
Rapor ayrıca (§8.1): manifest özeti (bağlayıcı hash'lerle), coin başı eksik saat (toplam, en büyük; coin adı yazılmaz),
borsa çapı boşluk saati (`gorunum.bosluk_taramasi`, motorla aynı tanım; [bas, bit) saatlerinin tamamı), koşu öncesi
eksik funding kaydı, filtresi olmayan sembol sayısı, süreklilik sorunu sayısı, Eylül funding kaynağı. Performans
içermez (açık grup). Veri okuma (zip → TamVeri) 6.01b yükleyicisindedir; bu modül saf denetimdir.
"""
import hashlib
import json
from pathlib import Path

import numpy as np

from motor.gorunum import SAAT_MS, bosluk_taramasi, gorunum_kur

BTC_ETH_ESIK = 0.01
K_VERI_YOK_ESIK = 0.10
DURUMLAR = ('TAMAM', 'CHECKSUM_HATASI', 'INDIRME_HATASI', 'YOK')
SATIR_AYRAC = chr(10)


def kanonik(x) -> bytes:
    return json.dumps(x, sort_keys=True, separators=(',', ':'), ensure_ascii=True, allow_nan=False).encode('ascii')


def _hash_mi(x) -> bool:
    return isinstance(x, str) and len(x) == 64 and all(ch in '0123456789abcdef' for ch in x)


def checksum_denetimi(manifest: list) -> dict:
    """manifest: BANKA_MANIFEST.jsonl satırları {'yol', 'sha256', 'checksum', 'durum'} yazım sırasıyla (indirme yeniden
    denenmiş olabilir; her dosyanın son satırı son durumdur). Bir dosyanın ilk TAMAM satırındaki sha256 bağlayıcıdır."""
    son, baglayici, kimlik_degisti, gecersiz = {}, {}, set(), set()
    for r in manifest:
        y, durum = r.get('yol'), r.get('durum')
        if not isinstance(y, str) or durum not in DURUMLAR:
            raise ValueError(f"manifest satiri bicimsiz: {r}")
        son[y] = r
        if durum == 'TAMAM':
            if not (_hash_mi(r.get('sha256')) and _hash_mi(r.get('checksum'))):
                gecersiz.add(y)
                continue
            if y in baglayici and baglayici[y] != r['sha256']:
                kimlik_degisti.add(y)
            baglayici.setdefault(y, r['sha256'])
    onarilamayan = set(kimlik_degisti) | set(gecersiz)
    for y, r in son.items():
        if r['durum'] == 'CHECKSUM_HATASI' or (r['durum'] == 'TAMAM' and r.get('sha256') != r.get('checksum')):
            onarilamayan.add(y)
    ozet = hashlib.sha256(SATIR_AYRAC.join(f"{y} {baglayici.get(y)}" for y in sorted(son)).encode('utf-8')).hexdigest()
    return {'dosya': len(son), 'onarilamayan': len(onarilamayan), 'kimlik_degisti': len(kimlik_degisti),
            'gecersiz_satir': len(gecersiz),
            'indirme_hatasi': sum(1 for r in son.values() if r['durum'] == 'INDIRME_HATASI'),
            'yok': sum(1 for r in son.values() if r['durum'] == 'YOK'), 'manifest_ozeti': ozet}


def eksik_saat(seri, bas_ms: int, bit_ms: int) -> tuple:
    """[bas, bit) içindeki beklenen saatlerden barı olmayanların sayısı ve beklenen saat sayısı."""
    beklenen = (bit_ms - bas_ms) // SAAT_MS
    if seri is None or len(seri.acilis_ms) == 0:
        return beklenen, beklenen
    ms = np.asarray(seri.acilis_ms, dtype=np.int64)
    var = int(((ms >= bas_ms) & (ms < bit_ms)).sum())
    return beklenen - var, beklenen


def coin_eksikleri(veri, coinler, bas_ms: int, bit_ms: int) -> dict:
    """Coin başı (kendi ilk barından sonra) eksik saat: toplam ve en büyük; coin adı yazılmaz."""
    eksik = []
    for c in coinler:
        s = veri.barlar.get(c)
        if s is None or not len(s.acilis_ms):
            continue
        ilk = max(bas_ms, int(s.acilis_ms[0]))
        if ilk < bit_ms:
            eksik.append(eksik_saat(s, ilk, bit_ms)[0])
    return {'coin': len(eksik), 'toplam': int(sum(eksik)), 'en_buyuk': int(max(eksik)) if eksik else 0}


def bosluk_saati(veri, bas_ms: int, bit_ms: int, p) -> int:
    """[bas, bit) saatlerinin tamamı taranır (tarama t'ye kadar kapanmış barları görür; netleştirme 17 g)."""
    g = gorunum_kur(veri, bit_ms)
    kume, _ = bosluk_taramasi(g, bas_ms, bit_ms, p.borsa_bosluk_oran, None)
    return int(sum(1 for h in kume if bas_ms <= h < bit_ms))


def eksik_funding(veri, bas_ms: int, bit_ms: int) -> int:
    """Koşu öncesi eksik funding kaydı (17 a): pencere içindeki ardışık iki kaydın aralığı, sonraki kaydın kendi aralık
    saatinin 1,5 katını aşan boşluk sayısı. Aralığı bilinmeyen (nan) kayıt sayılmaz."""
    n = 0
    for f in veri.funding.values():
        d = np.asarray(f.damga_ms, dtype=np.int64)
        m = (d >= bas_ms) & (d < bit_ms)
        if m.sum() < 2 or f.aralik_saat is None:
            continue
        dd = d[m]
        ara = np.asarray(f.aralik_saat, dtype=float)[m][1:]
        fark = np.diff(dd).astype(float)
        ok = np.isfinite(ara)
        n += int(np.sum(fark[ok] > 1.5 * ara[ok] * SAAT_MS))
    return n


def t2_karari(checksum: dict, btc_eksik_oran: float, eth_eksik_oran: float, k_veri_yok_oran: float) -> dict:
    nedenler = []
    if checksum['onarilamayan'] > 0:
        nedenler.append('onarilamayan CHECKSUM hatasi')
    if btc_eksik_oran > BTC_ETH_ESIK:
        nedenler.append('BTC saatlerinin >%1i eksik')
    if eth_eksik_oran > BTC_ETH_ESIK:
        nedenler.append('ETH saatlerinin >%1i eksik')
    if k_veri_yok_oran > K_VERI_YOK_ESIK:
        nedenler.append('K coinlerinin >%10unda veri yok')
    return {'T2': bool(nedenler), 'nedenler': nedenler}


def denetle(veri, manifest: list, k_coinler, t0_z1_ms: int, birincil_son_ms: int, bit_ms: int, p,
            filtresiz_sembol: int, sureklilik_sorunu: int, eylul_funding_kaynagi: str,
            btc: str = 'BTCUSDT', eth: str = 'ETHUSDT') -> dict:
    cs = checksum_denetimi(manifest)
    b_eks, b_bek = eksik_saat(veri.barlar.get(btc), t0_z1_ms, birincil_son_ms)
    e_eks, e_bek = eksik_saat(veri.barlar.get(eth), t0_z1_ms, birincil_son_ms)
    k = list(k_coinler)
    k_yok = sum(1 for c in k if c not in veri.barlar or not len(veri.barlar[c].acilis_ms))
    oran = {'btc_eksik': b_eks / b_bek if b_bek else 1.0, 'eth_eksik': e_eks / e_bek if e_bek else 1.0,
            'k_veri_yok': k_yok / len(k) if k else 0.0}
    karar = t2_karari(cs, oran['btc_eksik'], oran['eth_eksik'], oran['k_veri_yok'])
    return {'karar': karar, 'checksum': cs, 'oranlar': oran, 'k_coin': len(k), 'k_veri_yok': k_yok,
            'btc_eksik_saat': b_eks, 'eth_eksik_saat': e_eks,
            'coin_eksik_saat': coin_eksikleri(veri, sorted(veri.barlar), t0_z1_ms, bit_ms),
            'borsa_capi_bosluk_saati': bosluk_saati(veri, t0_z1_ms, bit_ms, p),
            'eksik_funding_kaydi': eksik_funding(veri, t0_z1_ms, bit_ms),
            'filtresiz_sembol': int(filtresiz_sembol), 'sureklilik_sorunu': int(sureklilik_sorunu),
            'eylul_funding_kaynagi': eylul_funding_kaynagi}


def yaz(sonuc: dict, yol) -> str:
    """VERI_DENETIM.json'u kanonik yazar; sha256'sını döner (damga ve hükümde kullanılır)."""
    b = kanonik(sonuc)
    Path(yol).write_bytes(b)
    return hashlib.sha256(b).hexdigest()
