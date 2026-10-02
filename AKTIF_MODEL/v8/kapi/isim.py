"""Carry kapisi isim tabanli hesaplar (CARRY Ss6.3 K8 notu, Ss6.6, Ss5.6 sifir/sifir tanisi; U-07, U-08, U-25; U-49, U-50).
Girdi: ayristirma (carry_coin, artik_coin; 5.02e) ve kosunun Mimari B karar kayitlari (betimsel_kayit.karar_kayitlari).

- Hic tutulmus isim (U-07): donemdeki bir karar kaydinda sanal_carry[i] != 0 olan alt isim (BTC haric); sanal miktar
  karar gununun 01:00'inden itibaren en az bir saat gecerlidir.
- K8 isim katkisi (U-07): N_i = sum carry_coin[i], saat T in [T0, son hafta sonu); en iyi 3 (buyukten) ve en kotu 3
  (kucukten), esitlikte alfabetik; yalniz hic tutulmus alt isimler. < 30 isim ise K8 hesaplanamaz (None).
- Bacak serileri (U-49; Codex T15-13, T17-f ile duzeltildi): her saat, carry_yeni payi saat sonundaki sanal carry
  miktarinin isaretine gore long (> 0) ya da short (< 0) bacaga yazilir. carry_eski payinin funding kismi (gercek
  kayit, dolgu, ters kayit) ayristirmanin carry_fon_long / carry_fon_short ayrimiyla OZGUN saatin yonune; kalani
  (fiyat, kapanan kismin maliyeti; saat basinda miktar 0 iken 0) saat basindaki miktarin isaretine. Olay islendigi
  saatte kalir. Haftalik toplam / (omega_C L NAV_{w basi}). BTC hedge ayri seri. long + short + hedge = haftalik carry
  toplami. En kotu isim-hafta: alt isimlerin ayni olcekteki en kucuk haftalik katkisi.
- Sifir/sifir tanisi (U-08, U-50): karar gunu D'nin gecerlilik araliginda [D 01:00, D+1 01:00) iki sanal miktari da 0
  olan isim-gunlerin artigi: toplam, mutlak toplam ve guncel kuralla (son sifir olmayan s^C, karar kaydindaki 'sc')
  carry'ye dusen karsiligi; s^C = 0 kuralinda carry'ye 0 duserdi, fark bu karsiliktir.
"""
import numpy as np

SAAT_MS = 3_600_000
GUN_MS = 86_400_000
K8_N = 3
K8_ISIM_MIN = 30


def tutulan_isimler(kararlar: list, btc: str) -> list:
    out = set()
    for k in kararlar:
        out |= {c for c, v in k.veri['hedef']['carry']['sanal_carry'].items() if float(v) != 0.0 and c != btc}
    return sorted(out)


def _pencere(ayr, bas_ms: int, bit_ms: int):
    saat = np.asarray(ayr.saat_ms, dtype=np.int64)
    return int(np.searchsorted(saat, bas_ms)), int(np.searchsorted(saat, bit_ms))


def isim_katkilari(ayr, bas_ms: int, bit_ms: int, isimler) -> dict:
    a, b = _pencere(ayr, bas_ms, bit_ms)
    return {c: float(np.sum(ayr.carry_coin[c][a:b])) if c in ayr.carry_coin else 0.0 for c in sorted(isimler)}


def k8_cikarilacaklar(katki: dict) -> dict:
    """En iyi 3 (buyukten, esitlikte alfabetik), sonra KALANLARDAN en kotu 3 (kucukten, esitlikte alfabetik): butun
    katkilar esit olsa da 6 ayri isim (Codex T15-8, U-56). Isim < 30 ise None."""
    if len(katki) < K8_ISIM_MIN:
        return None
    iyi = sorted(katki, key=lambda c: (-katki[c], c))[:K8_N]
    kotu = sorted((c for c in katki if c not in iyi), key=lambda c: (katki[c], c))[:K8_N]
    return {'en_iyi': iyi, 'en_kotu': kotu, 'haric': tuple(sorted(set(iyi) | set(kotu)))}


def _saatlik_miktar(ayr, kararlar: list, c: str) -> tuple:
    """(q_eski, q_yeni) saatlik: karar D'nin sanal carry miktari D + 1h'den itibaren gecerlidir (ayristirma ile ayni)."""
    saat = np.asarray(ayr.saat_ms, dtype=np.int64)
    etkin = np.array([k.damga_ms + SAAT_MS for k in kararlar], dtype=np.int64)
    q = np.array([float(k.veri['hedef']['carry']['sanal_carry'].get(c, 0.0)) for k in kararlar])

    def gecerli(t):
        i = np.searchsorted(etkin, t, side='right') - 1
        return np.where(i >= 0, q[np.maximum(i, 0)], 0.0)
    return gecerli(saat - 1), gecerli(saat)


def bacak_serileri(ayr, kararlar: list, hafta_ms, nav, L: float, omega_c: float, btc: str) -> dict:
    hafta_ms = np.asarray(hafta_ms, dtype=np.int64)
    kararlar = sorted(kararlar, key=lambda k: k.damga_ms)
    n = len(ayr.saat_ms)
    long_h, short_h = np.zeros(n), np.zeros(n)
    sifir = np.zeros(n)
    for c in ayr.carry_coin:
        if c == btc:
            continue
        q0, q1 = _saatlik_miktar(ayr, kararlar, c)
        e, y = ayr.carry_eski[c], ayr.carry_yeni[c]
        # T17-f: funding kismi ozgun saatin yonuyle (ayristirma); kalan saat basindaki miktarin isaretine. Kalan q0 = 0
        # iken yalniz toplama sirasi artigidir; kaybolmasin diye buyuk funding payinin bacagina yazilir.
        fl = getattr(ayr, 'carry_fon_long', {}).get(c, sifir)
        fs = getattr(ayr, 'carry_fon_short', {}).get(c, sifir)
        kalan = e - fl - fs
        isaret = np.where(q0 != 0, np.sign(q0), np.where(np.abs(fs) > np.abs(fl), -1.0, 1.0))
        long_h += np.where(isaret > 0, kalan, 0.0) + fl + np.where(q1 > 0, y, 0.0)
        short_h += np.where(isaret < 0, kalan, 0.0) + fs + np.where(q1 < 0, y, 0.0)
    hedge_h = ayr.carry_coin.get(btc, np.zeros(n))
    long_, short, hedge, isim_hafta = [], [], [], []
    for t in hafta_ms.tolist():
        a, b = _pencere(ayr, t, t + 7 * GUN_MS)
        payda = omega_c * L * nav(t)
        long_.append(float(np.sum(long_h[a:b])) / payda)
        short.append(float(np.sum(short_h[a:b])) / payda)
        hedge.append(float(np.sum(hedge_h[a:b])) / payda)
        katki = {c: float(np.sum(v[a:b])) / payda for c, v in ayr.carry_coin.items()}
        isim_hafta.extend((x, c, int(t)) for c, x in katki.items() if c != btc and x != 0.0)
    enk = min(isim_hafta) if isim_hafta else None
    return {'long': np.array(long_), 'short': np.array(short), 'hedge': np.array(hedge),
            'en_kotu_isim_hafta': None if enk is None else {'katki': enk[0], 'isim': enk[1], 'hafta_ms': enk[2]}}


def sifir_sifir_tanisi(ayr, kararlar: list) -> dict:
    saat = np.asarray(ayr.saat_ms, dtype=np.int64)
    toplam = mutlak = carryye = 0.0
    isim_gun = 0
    for k in kararlar:
        cr = k.veri['hedef']['carry']
        a = int(np.searchsorted(saat, k.damga_ms + SAAT_MS))
        b = int(np.searchsorted(saat, k.damga_ms + GUN_MS + SAAT_MS))
        for c, dizi in ayr.artik_coin.items():
            if float(cr['sanal_trend'].get(c, 0.0)) != 0.0 or float(cr['sanal_carry'].get(c, 0.0)) != 0.0:
                continue
            x = float(np.sum(dizi[a:b]))
            if x == 0.0:
                continue
            isim_gun += 1
            toplam += x
            mutlak += abs(x)
            carryye += float(cr['sc'].get(c, 0.0)) * x
    return {'isim_gun': isim_gun, 'toplam': toplam, 'mutlak': mutlak, 'guncel_kuralla_carry': carryye,
            'sifir_kuralina_gore_fark': carryye}
