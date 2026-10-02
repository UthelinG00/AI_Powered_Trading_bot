"""Carry kapisi denetimleri V1, V5, V6 (CARRY Ss6.1; U-13, U-15, U-28; U-51, U-53).

- V1 (U-15): kilit.v1_raporu ile kilitte sabitlenen test raporu (motor kimligi, basarisiz 0, butun testler; Codex T15-5).
- V5 (U-28): kapinin kullandigi seriler (ayristirmanin okudugu bellekteki gunluk kayitlari), motorun ciktisi
  (KosuSonucu.kararlar[i].hedef.carry) ve diske yazilip bagimsiz okunan gunluk (JSON satirlari; hash zinciri dosyadan
  yeniden hesaplanir) her karar gunu birebir: kappa, kappa_etkin, sc mutlak 1e-12; sanal_carry goreli 1e-12 max(1, |q|).
  Sonlu olmayan deger (NaN/inf) hicbir karsilastirmada esit sayilmaz (T17-d). Saatlik tuketim karsilastirmasindan once
  sekil/kapsam/sonluluk on denetimi: saat izgarasi bos degil, tam saatlik ve artan; karar saatleri artan ve izgaranin
  icinde; her saatlik dizi izgarayla ayni uzunlukta ve sonlu; karar kayitlarindaki miktar ve s^C sonlu.
  Gunluk dosyasi muhur klasorune yazilir (NAV kayitlari B'nin toplam getirisini, dolayisiyla trend P&L'ini tasir; U-53).
- V6 hedefleri (U-13, U-51; Codex T15-6 ile duzeltildi): her karar gunu T icin A REFERANS DURUMU = B kosusunun T'deki
  karar oncesi durumu (gunluk sirayla katlanir), pozisyonlar yerine B'nin SANAL TREND bacagi (q^T,v), devreden emir yok,
  NAV ayni kalacak bicimde nakit ayarli. Boylece carry pozisyonlari A'nin tavanlarini tuketmez. Bu durum ve gorunum
  uzerinde karar_ver'in hedef oncesi adimlari (bosluklar, maske, evren) ayni saf fonksiyonlarla tekrarlanir ve A'nin bant
  oncesi hedefi hedef_agirlik_ayrintili (mimari 'A') ile P&L uretmeden hesaplanir. B tarafi karar kaydindaki
  w_trend_yildiz'dir (w^T*). Iki tarafin islem disi (sabit) isimleri karsilastirmadan cikar.
"""
import hashlib
import json
import math

import numpy as np
from dataclasses import replace
from pathlib import Path

from kapi.betimsel_kayit import karar_oncesi_durumlar
from motor.durum import nav_hesapla
from motor.evren import evren_sec
from motor.gorunum import aylik_secim_gunu_mu, gorunum_kur
from motor.gunluk import KOK_HASH
from motor.hedef import hedef_agirlik_ayrintili, karar_bosluklari
from motor.karar import maske_ilerlet

V5_TOL = 1e-12


# ---- V5 ----------------------------------------------------------------------------------------------------------

def gunluk_yaz(gunluk, yol) -> str:
    """Her kayit bir satir: govde + hash (kanonik JSON), satir satir yazilir. Doner: dosyanin sha256'si."""
    h = hashlib.sha256()
    with open(yol, 'wb') as f:
        for k in gunluk.kayitlar():
            g = k.govde()
            g['hash'] = k.hash
            satir = (json.dumps(g, sort_keys=True, separators=(',', ':'), ensure_ascii=True, allow_nan=False)
                     + '\n').encode('ascii')
            f.write(satir)
            h.update(satir)
    return h.hexdigest()


def gunluk_oku_dogrula(yol) -> tuple:
    """Dosyadan bagimsiz okuma (satir satir): her satirin hash'i govdeden yeniden hesaplanir, zincir izlenir.
    Doner (karar kayitlari, kayit sayisi, son hash)."""
    onceki = KOK_HASH
    kararlar = []
    i = -1
    with open(yol, encoding='ascii') as f:
        satirlar = (x.rstrip('\n') for x in f)
        for i, satir in enumerate(satirlar):
            d = json.loads(satir)
            h = d.pop('hash')
            if d['sira'] != i or d['onceki_hash'] != onceki:
                raise ValueError(f"gunluk zinciri bozuk: satir {i}")
            if hashlib.sha256(json.dumps(d, sort_keys=True, separators=(',', ':'), ensure_ascii=True,
                                         allow_nan=False).encode('ascii')).hexdigest() != h:
                raise ValueError(f"gunluk kaydi hash'i tutmuyor: satir {i}")
            onceki = h
            if d['tur'] == 'karar':
                kararlar.append(d)
    return kararlar, i + 1, onceki


def _esit(a: dict, b: dict, goreli: bool) -> bool:
    for c in set(a) | set(b):
        x, y = float(a.get(c, 0.0)), float(b.get(c, 0.0))
        if not (math.isfinite(x) and math.isfinite(y)):             # T17-d: NaN/inf esit sayilmaz
            return False
        tol = V5_TOL * max(1.0, abs(x), abs(y)) if goreli else V5_TOL
        if not abs(x - y) <= tol:
            return False
    return True


def _skaler_esit(x, y) -> bool:
    x, y = float(x), float(y)
    return math.isfinite(x) and math.isfinite(y) and abs(x - y) <= V5_TOL


def _carry_esit(c1: dict, c2: dict) -> bool:
    return (_skaler_esit(c1['kappa'], c2['kappa']) and _skaler_esit(c1['kappa_etkin'], c2['kappa_etkin'])
            and _esit(c1['sc'], c2['sc'], goreli=False) and _esit(c1['sanal_carry'], c2['sanal_carry'], goreli=True))


def _saatlik_gecerli(saat_ms, etkin_ms, degerler: list, c: str) -> np.ndarray:
    """Her saat T icin etkin <= T olan son kararin degeri (ayristirmanin bacak(T) kurali); oncesinde 0."""
    q = np.array([float(d.get(c, 0.0)) for d in degerler])
    i = np.searchsorted(etkin_ms, saat_ms, side='right') - 1
    return np.where(i >= 0, q[np.maximum(i, 0)], 0.0)


def _v5_on_denetim(saat, etkin, diziler: dict, kayitlar: dict):
    """T17-d: karsilastirmadan once sekil, kapsam ve sonluluk. Doner: None (gecti) ya da neden metni.
    diziler: {ad: saatlik dizi}; kayitlar: {ad: karar basina {coin: deger} listesi}."""
    if saat.ndim != 1 or len(saat) == 0:
        return 'saat izgarasi bos ya da tek boyutlu degil'
    if len(saat) > 1 and not np.all(np.diff(saat) == 3_600_000):
        return 'saat izgarasi tam saatlik ve artan degil'
    if len(etkin) == 0:
        return 'karar kaydi yok'
    if len(etkin) > 1 and not np.all(np.diff(etkin) > 0):
        return 'karar saatleri artan degil'
    if etkin[0] - 3_600_000 < saat[0] or etkin[-1] > saat[-1]:
        return 'karar saatleri saat izgarasinin disinda'
    for ad, x in diziler.items():
        if x.shape != saat.shape:
            return f'{ad}: sekil saat izgarasiyla ayni degil'
        if not np.all(np.isfinite(x)):
            return f'{ad}: sonlu olmayan deger'
    for ad, liste in kayitlar.items():
        if not all(math.isfinite(float(v)) for d in liste for v in d.values()):
            return f'karar kayitlari ({ad}): sonlu olmayan deger'
    return None


def v5_saatlik(ayr, dosya_kararlari: list) -> dict:
    """T16, T17-e: ayristirmanin fiilen tukettigi saatlik degerler diskten bagimsiz okunan karar kayitlarindan
    turetilenlerle ayni mi:
    - sanal carry miktari carry_q: isim/saat bazinda goreli 1e-12 max(1, |q|);
    - s^C (sc_q; artik_carry'de icra artigiyla carpilan vektor): isim/saat bazinda mutlak 1e-12 (artik sifir olsa da);
    - artik_carry = sum_c sc_q A_i (tuketilen vektorun gercekten kullanildigi): toplama sirasi farki icin
      1e-9 max(1, sum |sc_q A|).
    Once _v5_on_denetim (T17-d); gecmezse karsilastirma yapilmaz."""
    saat = np.asarray(ayr.saat_ms, dtype=np.int64)
    etkin = np.array([k['damga_ms'] + 3_600_000 for k in dosya_kararlari], dtype=np.int64)
    qd = [k['veri']['hedef']['carry']['sanal_carry'] for k in dosya_kararlari]
    scd = [k['veri']['hedef']['carry']['sc'] for k in dosya_kararlari]
    diziler = {f'carry_q[{c}]': np.asarray(x, dtype=float) for c, x in ayr.carry_q.items()}
    diziler.update({f'sc_q[{c}]': np.asarray(x, dtype=float) for c, x in ayr.sc_q.items()})
    diziler.update({f'artik_coin[{c}]': np.asarray(x, dtype=float) for c, x in ayr.artik_coin.items()})
    diziler['artik_carry'] = np.asarray(ayr.satirlar['artik_carry'], dtype=float)
    neden = _v5_on_denetim(saat, etkin, diziler, {'sanal_carry': qd, 'sc': scd})
    if neden is not None:
        return {'q_farkli_saat': None, 'sc_farkli_saat': None, 'artik_farkli_saat': None, 'gecti': False,
                'neden': neden}
    sifir = np.zeros(len(saat))
    q_farkli = 0
    for c in sorted(set(ayr.carry_q) | {c for d in qd for c in d}):
        beklenen = _saatlik_gecerli(saat, etkin, qd, c)
        gercek = diziler.get(f'carry_q[{c}]', sifir)
        tol = V5_TOL * np.maximum(1.0, np.maximum(np.abs(beklenen), np.abs(gercek)))
        q_farkli += int(np.sum(~(np.abs(beklenen - gercek) <= tol)))
    sc_farkli = 0
    for c in sorted(set(ayr.sc_q) | {c for d in scd for c in d}):
        beklenen = _saatlik_gecerli(saat, etkin, scd, c)
        gercek = diziler.get(f'sc_q[{c}]', sifir)
        sc_farkli += int(np.sum(~(np.abs(beklenen - gercek) <= V5_TOL)))
    toplam = np.zeros(len(saat))
    olcek = np.zeros(len(saat))
    for c in ayr.artik_coin:
        x = diziler.get(f'sc_q[{c}]', sifir) * diziler[f'artik_coin[{c}]']
        toplam += x
        olcek += np.abs(x)
    artik_farkli = int(np.sum(~(np.abs(diziler['artik_carry'] - toplam) <= 1e-9 * np.maximum(1.0, olcek))))
    return {'q_farkli_saat': q_farkli, 'sc_farkli_saat': sc_farkli, 'artik_farkli_saat': artik_farkli,
            'gecti': q_farkli == 0 and sc_farkli == 0 and artik_farkli == 0}


def v5_tek_defter(kosu, gunluk_dosyasi, ayr=None) -> dict:
    """kosu: KosuSonucu. Uc kaynagin karar gunu bazinda birebirligi; dosya kesilmesine karsi toplam kayit sayisi ve
    son hash bellekteki gunlukle ayni olmali (Codex T15-10)."""
    bellek = [k for k in kosu.gunluk.kayitlar() if k.tur == 'karar']
    dosya, n_kayit, son = gunluk_oku_dogrula(gunluk_dosyasi)
    motor = [k.hedef for k in kosu.kararlar]
    if n_kayit != len(kosu.gunluk) or son != kosu.gunluk.son_hash:
        return {'gun': len(bellek), 'farkli_gun': None, 'gecti': False, 'neden': 'gunluk dosyasi eksik ya da farkli'}
    if not (len(bellek) == len(dosya) == len(motor)):
        return {'gun': len(bellek), 'farkli_gun': None, 'gecti': False, 'neden': 'karar sayilari farkli'}
    farkli = 0
    for kb, kd, h in zip(bellek, dosya, motor):
        if h.carry is None or not (kb.damga_ms == kd['damga_ms'] == h.t_ms):
            farkli += 1
            continue
        if not (_carry_esit(kb.veri['hedef']['carry'], h.carry) and _carry_esit(kd['veri']['hedef']['carry'], h.carry)):
            farkli += 1
    out = {'gun': len(bellek), 'farkli_gun': farkli, 'gecti': farkli == 0}
    if ayr is not None:
        out['saatlik'] = v5_saatlik(ayr, dosya)
        out['gecti'] = out['gecti'] and out['saatlik']['gecti']
    return out


# ---- V6 ----------------------------------------------------------------------------------------------------------

def a_referans_durumu(durum, g):
    """U-51: pozisyonlar = sanal trend bacagi, devreden emir yok, carry durumu bos; NAV korunur."""
    qT = {c: float(q) for c, q in durum.sanal_trend.items() if float(q) != 0.0}
    ara = replace(durum, pozisyonlar=qT, devreden={}, carry_q={}, sanal_carry={})
    return replace(ara, nakit=durum.nakit + nav_hesapla(durum, g) - nav_hesapla(ara, g))


def v6_hedefleri(veri, gunluk, p_b, L: float, bas_ms: int, bit_ms: int) -> tuple:
    """Doner (w_b listesi, w_a listesi): donemdeki her karar gunu icin sabit isimler cikarilmis bant oncesi hedefler."""
    p_a = replace(p_b, mimari='A')
    w_b, w_a = [], []
    for k, durum_b in karar_oncesi_durumlar(gunluk, bas_ms, bit_ms):
        t = k.damga_ms
        g = gorunum_kur(veri, t)
        durum = a_referans_durumu(durum_b, g)
        bosluklar, _ = karar_bosluklari(g, durum, p_a)
        maske = maske_ilerlet(g, durum, t, p_a, bosluklar)
        if aylik_secim_gunu_mu(t) or durum.evren_ms is None:
            evren, evren_ms = evren_sec(g, t, durum.evren, maske, p_a).uyeler, t
        else:
            evren, evren_ms = durum.evren, durum.evren_ms
        hedef_a, _ = hedef_agirlik_ayrintili(g, replace(durum, maske=maske, evren=evren, evren_ms=evren_ms), L, p_a,
                                             bosluklar=bosluklar)
        hb = k.veri['hedef']
        sabit = set(hb['sabit']) | set(hedef_a.sabit)
        w_b.append({c: float(v) for c, v in hb['tanilar'].get('w_trend_yildiz', {}).items() if c not in sabit})
        w_a.append({c: float(v) for c, v in hedef_a.w_yildiz.items() if c not in sabit and float(v) != 0.0})
    return w_b, w_a
