"""Carry kapisi betimsel raporlari, karar kaydi ve ayristirma tabanli kisim (baglayici degil; CARRY Ss5.1 tanisi,
Ss6.6; U-43...U-47). Girdi: kosunun olay gunlugu (motor.gunluk), ayristirma sonucu ve donem [bas_ms, bit_ms).

Tanimlar (Ss6.6'nin acik biraktigi ayrintilar; D'ye bakilmadan):
- kappa (U-43): kappa^C_t = carry['kappa'] (cozucu), kappa_etkin_t = carry['kappa_etkin']; oranlar donemdeki karar
  gunleri uzerinden. Goreli degisim tanisi (Ss5.1): |kappa_t / kappa_{t-1} - 1| > 0,25 olan gun sayisi (kappa_{t-1} = 0
  ise kappa_t != 0 gunu sayilir); round-1 bantli kural: kappa_bant_t = kappa_bant_{t-1}, goreli fark <= 0,25 ise; aksi
  kappa_t. Izleme farki |kappa_bant - kappa| (ortalama, en buyuk, farkli gun sayisi).
- Baglama sikliklari (U-44, Codex T15-14 ile duzeltildi): hedef['baglayan'] etiketlerinin (isim, brut, kappa_brut, S1,
  S2, kappa, global, bant_kapandi, T4d) karar gunu orani. S4 BAGLAMA: nihai hedefte (w_yildiz) en az bir alt ismin kisa
  tarafta -s4_sinir / s4_artis sinirina 1e-9 icinde temas ettigi gun orani; S4 ASIMI (sinirin 1e-9'dan fazla otesi)
  ayri raporlanir.
- Kitap tavanlari (U-45, T15-14 ile duzeltildi; K1-04): karar anindaki GERCEKLESEN kitap (hedef['w_mevcut']) ve
  DEVREDEN kitap ((q + devreden emirlerin kalani) fiyat_ref / NAV; karar oncesi durum gunlukten katlanir) uzerinde
  net_cozucu.asimlar (butun isimler serbest) ile S1, S2 ve S4 (alt isim kisa tarafi) asimi; asim gunu orani
  (asim > 1e-12) ve en buyuk asim. Hedefe ulasilamayan gun: o karar gunu emir niyetlerinden en az biri ayni karar
  damgali dolumlarla tam karsilanmadi (|dolan| < |niyet| (1 - 1e-12)).
- Hedge yuvarlama (U-46; K1-18): BTC sanal carry miktari (carry['sanal_carry'][BTC]) sifirdan farkliyken kapi NAV'inda
  |q| ve demo NAV'inda |q| * 5000 / NAV_karar bir lot adiminin altinda kalan gun orani (agirliktan; yeniden kosu yok).
- Netleme ve icra artigi (U-47): donemdeki netleme toplami ve sum_d |A^C_d| (gunluk artik_carry toplamlarinin mutlak
  degerleri; s^C gunluk sabit oldugu icin gun birimi).
"""
import math

import numpy as np

from dataclasses import replace

from motor.durum import StratejiDurumu, kayit_uygula
from motor.net_cozucu import asimlar

GUN_MS = 86_400_000
KAPPA_BANT = 0.25
ASIM_TOL = 1e-12
S4_TOL = 1e-9
DEMO_NAV = 5000.0


def karar_kayitlari(gunluk, bas_ms: int, bit_ms: int) -> list:
    """Donemdeki Mimari B karar kayitlari (damga sirasiyla)."""
    out = [k for k in gunluk.kayitlar() if k.tur == 'karar' and bas_ms <= k.damga_ms < bit_ms]
    if any('carry' not in k.veri['hedef'] for k in out):
        raise ValueError("Mimari B karar kaydi bekleniyor")
    return sorted(out, key=lambda k: k.damga_ms)


def kappa_tanisi(kararlar: list) -> dict:
    kap = np.array([float(k.veri['hedef']['carry']['kappa']) for k in kararlar])
    ket = np.array([float(k.veri['hedef']['carry']['kappa_etkin']) for k in kararlar])
    n = len(kap)
    if n == 0:
        return {'gun': 0}
    buyuk = 0
    for a, b in zip(kap[:-1], kap[1:]):
        if (a == 0.0 and b != 0.0) or (a != 0.0 and abs(b / a - 1.0) > KAPPA_BANT):
            buyuk += 1
    bant = np.empty(n)
    bant[0] = kap[0]
    for i in range(1, n):
        o = bant[i - 1]
        degis = (o == 0.0 and kap[i] != 0.0) or (o != 0.0 and abs(kap[i] / o - 1.0) > KAPPA_BANT)
        bant[i] = kap[i] if degis else o
    fark = np.abs(bant - kap)
    return {'gun': n, 'kappa_lt1_oran': float(np.mean(kap < 1.0)), 'kappa_etkin_lt1_oran': float(np.mean(ket < 1.0)),
            'goreli_degisim_gun': buyuk, 'bant_izleme': {'ortalama': float(fark.mean()), 'en_buyuk': float(fark.max()),
                                                           'farkli_gun': int(np.sum(fark > 0))}}


def karar_oncesi_durumlar(gunluk, bas_ms: int, bit_ms: int):
    """Donemdeki her karar kaydi icin (kayit, karar oncesi durum): gunluk sirayla katlanir; karar anindaki durum
    (funding ve uzlasma uygulanmis) karar kaydindan hemen onceki haldir (geri_test karar_adimi ile ayni)."""
    d = StratejiDurumu()
    for k in gunluk.kayitlar():
        if k.tur == 'karar' and bas_ms <= k.damga_ms < bit_ms:
            yield k, replace(d, t_ms=k.damga_ms)
        d = kayit_uygula(d, k)


def baglama_sikliklari(kararlar: list, p) -> dict:
    n = len(kararlar)
    say = {}
    s4_temas = s4_asim = 0
    s4_sinir = p.s4_sinir / p.s4_artis
    for k in kararlar:
        h = k.veri['hedef']
        for e in set(h['baglayan']):
            say[e] = say.get(e, 0) + 1
        alt = [w for c, w in h['w_yildiz'].items() if c not in (p.btc, p.eth)]
        s4_temas += any(abs(w + s4_sinir) <= S4_TOL for w in alt)
        s4_asim += any(w < -s4_sinir - S4_TOL for w in alt)
    return {'gun': n, 'etiket': {e: v / n for e, v in sorted(say.items())} if n else {},
            'S4_baglama': s4_temas / n if n else float('nan'), 'S4_asim': s4_asim / n if n else float('nan')}


def n_c_serisi(kararlar: list, hafta_ms) -> list:
    """Pazartesi carry kararlarindaki n_C (haftalik kitap kuruldugu gunler)."""
    ix = {k.damga_ms: k for k in kararlar}
    out = []
    for t in np.asarray(hafta_ms, dtype=np.int64).tolist():
        k = ix.get(int(t))
        tan = k.veri['hedef']['carry'].get('tanilar', {}) if k is not None else {}
        out.append({'hafta_ms': int(t), 'n_c': tan.get('n_c')})
    return out


def _kitap_asimlari(kitaplar, p) -> dict:
    s = {'S1': [], 'S2': [], 'S4': []}
    s4_sinir = p.s4_sinir / p.s4_artis
    for w in kitaplar:
        adlar = sorted(w)
        if not adlar:
            for v in s.values():
                v.append(-math.inf)
            continue
        vek = np.array([float(w[c]) for c in adlar])
        be = np.array([c in (p.btc, p.eth) for c in adlar], dtype=bool)
        a = asimlar(vek, np.ones(len(adlar), dtype=bool), be, p)
        s['S1'].append(a['S1'])
        s['S2'].append(a['S2'])
        alt = vek[~be]
        s['S4'].append(float(np.max(-alt - s4_sinir)) if len(alt) else -math.inf)
    out = {}
    for ad, v in s.items():
        v = np.array(v)
        out[ad] = {'gun_orani': float(np.mean(v > ASIM_TOL)) if len(v) else float('nan'),
                   'en_buyuk': float(np.max(v)) if len(v) and np.max(v) > ASIM_TOL else 0.0}
    return out


def tavan_asimlari(kararlar: list, p, gunluk=None, bas_ms: int = None, bit_ms: int = None) -> dict:
    """Gerceklesen (karar anindaki mevcut) kitapta ve gunluk verilirse devreden kitapta S1, S2, S4 asimi."""
    out = {'gerceklesen': _kitap_asimlari([k.veri['hedef']['w_mevcut'] for k in kararlar], p)}
    if gunluk is not None:
        kitaplar = []
        for k, d in karar_oncesi_durumlar(gunluk, bas_ms, bit_ms):
            h = k.veri['hedef']
            fr, nav = h['fiyat_ref'], float(h['nav'])
            q = dict(d.pozisyonlar)
            for c, e in d.devreden.items():
                q[c] = q.get(c, 0.0) + float(e.kalan)
            kitaplar.append({c: v * float(fr.get(c, 0.0)) / nav for c, v in q.items() if v != 0.0})
        out['devreden'] = _kitap_asimlari(kitaplar, p)
    return out


def hedefe_ulasilamayan(gunluk, kararlar: list) -> dict:
    gunler = {k.damga_ms for k in kararlar}
    niyet, dolan = {}, {}
    for k in gunluk.kayitlar():
        if k.tur == 'emir_niyeti' and k.damga_ms in gunler:
            niyet[(k.damga_ms, k.coin)] = niyet.get((k.damga_ms, k.coin), 0.0) + float(k.miktar)
        elif k.tur == 'dolum' and getattr(k, 'karar_ms', None) in gunler:
            dolan[(k.karar_ms, k.coin)] = dolan.get((k.karar_ms, k.coin), 0.0) + float(k.miktar)
    eksik = {t for (t, c), q in niyet.items() if abs(dolan.get((t, c), 0.0)) < abs(q) * (1.0 - 1e-12)}
    n = len(kararlar)
    return {'gun': n, 'oran': len(eksik) / n if n else float('nan')}


def hedge_yuvarlama(kararlar: list, btc_adim: float, btc: str = 'BTCUSDT', demo_nav: float = DEMO_NAV) -> dict:
    kapi = demo = n = 0
    for k in kararlar:
        q = float(k.veri['hedef']['carry']['sanal_carry'].get(btc, 0.0))
        if q == 0.0:
            continue
        n += 1
        nav = float(k.veri['hedef']['nav'])
        kapi += abs(q) < btc_adim
        demo += abs(q) * demo_nav / nav < btc_adim
    return {'hedge_gun': n, 'kapi_orani': kapi / n if n else float('nan'), 'demo_orani': demo / n if n else float('nan')}


def netleme_ve_artik(ayr, bas_ms: int, bit_ms: int) -> dict:
    g_net, g_art = ayr.gunluk['netleme'], ayr.gunluk['artik_carry']
    gunler = [g for g in sorted(g_art) if bas_ms <= g < bit_ms]
    return {'netleme': float(sum(g_net.get(g, 0.0) for g in gunler)),
            'abs_artik_carry_gunluk': float(sum(abs(g_art[g]) for g in gunler))}


def v6_fark_tanisi(w_b: list, w_a: list, tol: float = 1e-9) -> dict:
    """Ss6.6: V6 fark gunlerinde (max_i |w^T*_B - w^T_A| > tol) ortalama trend brut farki sum_i |w_B - w_A|.
    w_b, w_a: gun basina {isim: agirlik} (bant oncesi hedefler)."""
    farklar = []
    for b, a in zip(w_b, w_a):
        adlar = set(b) | set(a)
        d = [abs(b.get(c, 0.0) - a.get(c, 0.0)) for c in adlar]
        if d and max(d) > tol:
            farklar.append(sum(d))
    return {'gun': len(w_b), 'fark_gun': len(farklar), 'oran': len(farklar) / len(w_b) if w_b else float('nan'),
            'ort_brut_fark': float(np.mean(farklar)) if farklar else 0.0}
