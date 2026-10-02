"""Kosu gunlugunden coin basi saatlik P&L ve epizotlar (BANKA_ONKAYIT_TASLAK Ss3.4: B5 epizotu, B8 fiyat bileseni,
B10 net katki). Motorun indirgeyicisiyle (durum.kayit_uygula) ayni nakit kurallari:
  dolum: nakit -= miktar * fiyat;  uzlasma: nakit += q * fiyat, q = 0;  duzeltme: nakit += tutar, q += miktar;
  funding / funding_dolgu / ters_kayit: nakit += tutar.
Saat T (T'de acilan bar, T+1h'de degerleme; geri_test.kos ile ayni): coin P&L = q(T sonrasi) * sk(T+1h)
- q(T oncesi) * sk(T) + T'deki nakit akislari. Ozdeslik: sum_c P&L = NAV(T+1h) - NAV(T) (ozdeslik_max_hata).
Funding'in ozgun saati (B5 epizot atfi; Codex T18): gercek kayit, dolgu ve ters kayit parcalari motor.ayristirma.
fon_parcalari ile; ters kayit icin bekleyen dolgular gunlukten izlenir (funding_dolgu ekler, gercek kayit (kapsam_bas,
damga] kapsamini siler; durum.kayit_uygula ile ayni). Ozgun saati kayit saatinden farkli parcalar fon_ozgun'dadir; tutar
eski payda kayit satirinda kalir (nakit ve ozdeslik degismez)."""
from dataclasses import dataclass

import numpy as np

from motor.ayristirma import fon_parcalari
from motor.gorunum import SAAT_MS, bar_indeksi, son_kapanis

NAKIT_TURLERI = ('dolum', 'uzlasma', 'duzeltme', 'funding', 'funding_dolgu', 'ters_kayit')
FUNDING_TURLERI = ('funding', 'funding_dolgu', 'ters_kayit')


class PnlHatasi(ValueError):
    """Pozisyonlu coinin kapanisi yok ya da ozdeslik bozuk."""


@dataclass
class CoinPnl:
    saat_ms: np.ndarray       # T; satir n (T, T+1h] araligidir
    pnl: dict                 # coin -> saatlik toplam P&L (fiyat + funding - maliyet; uzlasma dahil) = eski + yeni
    funding: dict             # coin -> saatlik funding nakdi
    q: dict                   # coin -> T'deki olaylardan sonraki pozisyon (saat boyunca tutulan)
    dnav: np.ndarray          # saatlik NAV farki (kosunun NAV'indan)
    ozdeslik_max_hata: float
    eski: dict = None         # coin -> saat basindaki pozisyonun payi (B5 epizotu; Codex T12-1)
    yeni: dict = None         # coin -> saat sonundaki pozisyonun payi
    fon_ozgun: dict = None    # coin -> [(kayit satiri, ozgun_ms, tutar)]: ozgun saati farkli funding parcalari (T18)


def bolus(q_a: float, q_b: float) -> tuple:
    """Pozisyon q_a -> q_b degisiminin (eski, yeni) paylari: q_a = 0 ise hepsi yeni; q_b = 0 ya da ayni isarette
    azalma ise hepsi eski; ayni isarette artis yeni (ayni epizot); isaret degisimi |q_a| : |q_b| oraninda."""
    if q_a == 0.0:
        return 0.0, 1.0
    if q_b == 0.0 or (q_a > 0) == (q_b > 0):
        return (1.0, 0.0) if abs(q_b) <= abs(q_a) else (0.0, 1.0)
    t = abs(q_a) + abs(q_b)
    return abs(q_a) / t, abs(q_b) / t


def coin_pnl(sonuc, veri) -> CoinPnl:
    """sonuc: geri_test.KosuSonucu; veri: kosunun TamVeri'si."""
    kayitlar = sonuc.gunluk.kayitlar()
    bas = next(k for k in kayitlar if k.tur == 'baslangic')
    saatler = np.asarray(sonuc.nav_ms, dtype=np.int64) - SAAT_MS
    olaylar = {}
    for k in kayitlar:
        if k.tur in NAKIT_TURLERI:
            olaylar.setdefault(k.damga_ms, []).append(k)
    coinler = sorted({k.coin for ks in olaylar.values() for k in ks})
    n = len(saatler)
    pnl = {c: np.zeros(n) for c in coinler}
    eski = {c: np.zeros(n) for c in coinler}
    yeni = {c: np.zeros(n) for c in coinler}
    fund = {c: np.zeros(n) for c in coinler}
    qs = {c: np.zeros(n) for c in coinler}
    q = {}
    bekleyen, fon_ozgun = {}, {}

    def sk(c, t):
        s = veri.barlar.get(c)
        v = son_kapanis(s, t) if s is not None else None
        if v is None:
            raise PnlHatasi(f"pozisyonlu coinin kapanisi yok: {c} @ {t}")
        return v

    def ref(c, T):
        """T'deki islem referans fiyati: T'de acilan barin acilisi; bar yoksa T'den once son kapanis."""
        s = veri.barlar.get(c)
        k = bar_indeksi(s, T) if s is not None else None
        return float(s.acilis[k]) if k is not None else sk(c, T)

    for i, T in enumerate(saatler.tolist()):
        T = int(T)
        q_once = dict(q)
        e_, y_ = {}, {}
        for k in olaylar.get(T, ()):
            c = k.coin
            if k.tur in FUNDING_TURLERI:
                x = float(k.veri.get('tutar', 0.0))
                e_[c] = e_.get(c, 0.0) + x
                fund[c][i] += x
                for h, t in fon_parcalari(k.tur, k.veri, bekleyen.get(c, ())):
                    if h != T:
                        fon_ozgun.setdefault(c, []).append((i, h, t))
                if k.tur == 'funding_dolgu':
                    bekleyen[c] = bekleyen.get(c, []) + [(int(h), float(t)) for h, t in k.veri['saatler']]
                elif k.tur == 'funding':
                    d = int(k.veri['damga_ms'])
                    kb = int(k.veri.get('kapsam_bas_ms', d))
                    bekleyen[c] = [x_ for x_ in bekleyen.get(c, []) if not (kb < x_[0] <= d)]
                continue
            q_a = q.get(c, 0.0)
            if k.tur == 'dolum':
                q_b = 0.0 if k.veri.get('tam_kapanis_son') else q_a + k.miktar
                dnakit = -k.miktar * k.fiyat
            elif k.tur == 'uzlasma':
                q_b, dnakit = 0.0, q_a * k.fiyat
            else:                                        # duzeltme (canli): tutar nakde, miktar pozisyona
                q_b = q_a + (k.miktar or 0.0)
                dnakit = float(k.veri.get('tutar', 0.0))
            # Islemin referans fiyatina gore P&L'i (maliyet): (q_b - q_a) * ref + nakit; kapanan/acilan paya bolunur.
            x = ((q_b - q_a) * ref(c, T) if q_b != q_a else 0.0) + dnakit
            we, wy = bolus(q_a, q_b)
            e_[c] = e_.get(c, 0.0) + we * x
            y_[c] = y_.get(c, 0.0) + wy * x
            q[c] = q_b
        for c in set(q_once) | set(q) | set(e_) | set(y_):
            q0, q1 = q_once.get(c, 0.0), q.get(c, 0.0)
            r = ref(c, T) if (q0 != 0.0 or q1 != 0.0) else 0.0
            ei = e_.get(c, 0.0) + (q0 * (r - sk(c, T)) if q0 != 0.0 else 0.0)
            yi = y_.get(c, 0.0) + (q1 * (sk(c, T + SAAT_MS) - r) if q1 != 0.0 else 0.0)
            eski[c][i], yeni[c][i] = ei, yi
            pnl[c][i] = ei + yi
            qs[c][i] = q1
        q = {c: x for c, x in q.items() if x != 0.0}
    nav = np.asarray(sonuc.nav, dtype=float)
    dnav = np.diff(np.concatenate(([float(bas.veri['nav0'])], nav)))
    toplam = np.zeros(n)
    for c in coinler:
        toplam += pnl[c]
    hata = float(np.max(np.abs(toplam - dnav))) if n else 0.0
    return CoinPnl(saat_ms=saatler, pnl=pnl, funding=fund, q=qs, dnav=dnav, ozdeslik_max_hata=hata, eski=eski,
                   yeni=yeni, fon_ozgun=fon_ozgun)


def epizot_pnl(q_saatlik, eski_saatlik, yeni_saatlik, q_onceki: float = 0.0, ozgun=()) -> list:
    """B5 epizotlari (BANKA Ss3.4): bir coinde net pozisyon isaretinin kesintisiz sabit kaldigi donem; 0'a inme ya da
    isaret degisimi bitirir. Saatin 'eski' payi (saat basindaki pozisyonun fiyat hareketi, funding, kapanan kismin
    maliyeti) saat basindaki pozisyonun epizotuna; 'yeni' payi (saat sonundaki pozisyonun fiyat hareketi, acilan kismin
    maliyeti) saat sonundaki pozisyonun epizotuna yazilir (Codex T12-1). Ilgili pozisyon yoksa (kapanmis pozisyonun gec
    funding'i) coinin son epizotuna; hic epizot yoksa hicbir epizota. Eski pay yalniz saat basindaki ya da son kapanan
    epizota gider, yeniden acilan epizota gitmez (Codex T13-2). q_onceki: dizinin ilk saatinden onceki pozisyon (pencere
    kesildiginde surmekte olan epizot; Codex T13-1).
    ozgun (Codex T18): [(i, j, x), ...] kayit satiri i'nin eski payindaki x tutarindaki funding parcasi, ozgun satir j'nin
    basindaki pozisyonun epizotuna aittir (j None: hicbir epizota). Yeniden atama (simdiki epizot, hedef epizot, j)
    uclusune gore netlenir; yalniz net != 0 uygulanir (ayni saati tam tersine donduren dolgu + ters kayit sonucu
    degistirmez). Doner: epizot P&L listesi."""
    q = np.concatenate(([float(q_onceki)], np.asarray(q_saatlik, dtype=float)))
    xe = np.concatenate(([0.0], np.asarray(eski_saatlik, dtype=float)))
    xy = np.concatenate(([0.0], np.asarray(yeni_saatlik, dtype=float)))
    isaret = np.sign(q)
    ep = np.full(len(q), -1, dtype=np.int64)
    sayac = -1
    onceki = 0.0
    for h in range(len(q)):
        if isaret[h] != 0 and isaret[h] != onceki:
            sayac += 1
        if isaret[h] != 0:
            ep[h] = sayac
        onceki = isaret[h]
    toplam = np.zeros(sayac + 1)
    he_satir = np.full(len(q), -1, dtype=np.int64)
    son = -1
    for h in range(len(q)):
        bas = ep[h - 1] if h > 0 else -1
        he = bas if bas >= 0 else son
        hy = ep[h] if ep[h] >= 0 else (bas if bas >= 0 else son)
        he_satir[h] = he
        if he >= 0:
            toplam[he] += xe[h]
        if hy >= 0:
            toplam[hy] += xy[h]
        if ep[h] >= 0:
            son = ep[h]
    net = {}
    for i, j, x in ozgun:
        simdi = int(he_satir[i + 1])
        hedef = int(ep[j]) if j is not None else -1
        if simdi != hedef:
            net[(simdi, hedef, j)] = net.get((simdi, hedef, j), 0.0) + float(x)
    for (simdi, hedef, _), x in net.items():
        if x == 0.0:
            continue
        if simdi >= 0:
            toplam[simdi] -= x
        if hedef >= 0:
            toplam[hedef] += x
    return toplam.tolist()


def gunluk_topla(saat_ms, saatlik, gun_ms) -> np.ndarray:
    """Saatlik diziyi gunlere toplar: gun d = [d, d + 24h) araligindaki T'ler (saat sonu d + 24h'ye kadar). Son gunden
    sonraki saatler toplanmaz (BANKA Ss3.7 netlestirme 18: once son gune yigiliyordu; bankada motor Z2 sonuna kadar
    kosar)."""
    saat_ms = np.asarray(saat_ms, dtype=np.int64)
    gun_ms = np.asarray(gun_ms, dtype=np.int64)
    ix = np.searchsorted(gun_ms, saat_ms, side='right') - 1
    out = np.zeros(len(gun_ms))
    if not len(gun_ms):
        return out
    ok = (ix >= 0) & (saat_ms < gun_ms[-1] + 24 * SAAT_MS)
    np.add.at(out, ix[ok], np.asarray(saatlik, dtype=float)[ok])
    return out
