"""Rejim-null (B7) sentetik yol ureteci (BANKA_ONKAYIT_TASLAK Ss3.5; kalibrasyon Duzey 2-b ve banka ortak).

P6 (bu bolum): indeks duzeyinde blok atamasi, Ss3.5.1-3.5.2. Saatler veri tabanindan (00:00 UTC hizali) itibaren
tamsayi saat indeksidir. Dilim [bas, bit) bas'tan baslayarak 120 saatlik tam bloklara bolunur; 120 saatten kisa artik
kuyruk bloktur, yerinde kalir. Ortak permutasyon pi: sentetik konum k gercek blok pi[k]'nin icerigini alir.
Coin i (yasam [a_i, d_i); hala islem goruyorsa d_i = sonsuz):
  - Y2 kenar bloklar (a_i'yi ve d_i - 1'i iceren tam bloklar) yerinde kalir;
  - Y3 R_i = yasamin tamamen kapsadigi, kenar olmayan tam bloklar; K_i = R_i konumlari. k in K_i ve pi[k] in R_i ise
    ortak eslesme; kalan konumlar U_i (artan) kalan bloklar W_i'nin ikincil permutasyonla karistirilmis sirasiyla eslenir.
  - Yasam disi ve kuyruk saatleri kimlik eslemesidir (gercek yolda da bar yoktur ya da yerinde kalir).
Sonuc: coin basina saat eslemesi kaynak[h_sentetik] = h_gercek; her coin icin bir permutasyondur. Blok ici saat sirasi
ve yasam ici bosluklar blokla tasinir (Y1: giris, cikis ve dilimdeki bar sayisi korunur)."""
import math
from dataclasses import dataclass

import numpy as np

from motor.gorunum import SAAT_MS, TamVeri, funding_serisi, saatlik_seri

BLOK_SAAT = 120
SONSUZ = math.inf


@dataclass(frozen=True)
class DilimBloklari:
    bas: int                    # dilim basi (saat indeksi; 00:00 hizali)
    bit: int                    # dilim sonu (haric)

    @property
    def n_tam(self) -> int:
        return (self.bit - self.bas) // BLOK_SAAT

    def blok_bas(self, b: int) -> int:
        return self.bas + b * BLOK_SAAT

    def blok(self, h) -> int:
        """h'yi iceren tam blok; kuyrukta ya da dilim disinda -1."""
        if self.bas <= h < self.bas + self.n_tam * BLOK_SAAT:
            return int((h - self.bas) // BLOK_SAAT)
        return -1


def dilim_bloklari(bas: int, bit: int) -> DilimBloklari:
    if bas % 24 != 0 or bit <= bas:
        raise ValueError("dilim 00:00 hizali ve bos olmayan olmali")
    return DilimBloklari(bas=int(bas), bit=int(bit))


def coin_blok_atamasi(a, d, db: DilimBloklari, pi: np.ndarray, ikincil_uretec) -> tuple:
    """Ss3.5.2 Y2-Y3. a: ilk bar saati; d: son bardan sonraki saat (SONSUZ olabilir). pi: ortak permutasyon.
    ikincil_uretec: argumansiz cagrilinca bu coin-dilimin ikincil Generator'unu veren fonksiyon (yalniz gerekirse
    cagrilir). Doner: ({konum: gercek blok} yalniz R_i icin, ortak eslesme sayisi |K_i \\ U_i|, |K_i|)."""
    kenar = {b for b in (db.blok(a), db.blok(d - 1) if d != SONSUZ else -1) if b >= 0}
    R = [b for b in range(db.n_tam)
         if db.blok_bas(b) >= a and db.blok_bas(b) + BLOK_SAAT <= d and b not in kenar]
    R_kume = set(R)
    atama = {k: int(pi[k]) for k in R if int(pi[k]) in R_kume}
    U = [k for k in R if k not in atama]
    if U:
        kullanilan = set(atama.values())
        W = sorted(b for b in R if b not in kullanilan)
        sira = ikincil_uretec().permutation(len(W))
        for k, i in zip(U, sira):
            atama[k] = W[int(i)]
    return atama, len(R) - len(U), len(R)


def saat_eslemesi(yasamlar: dict, coin_no: dict, dilimler, perm_uretec, ikincil_uretec, H: int) -> tuple:
    """yasamlar: coin -> (a, d). coin_no: coin -> numara (ikincil tohum icin). dilimler: [(bas, bit), ...] takvim
    sirasiyla; j = 1, 2, ... perm_uretec(j) ve ikincil_uretec(j, i) Generator dondurur. H: toplam saat sayisi.
    Doner: ({coin: kaynak dizisi (uzunluk H)}, {'ortak': sum |K \\ U|, 'toplam': sum |K|})."""
    kaynak = {c: np.arange(H, dtype=np.int64) for c in yasamlar}
    ortak = toplam = 0
    for j, (bas, bit) in enumerate(dilimler, start=1):
        db = dilim_bloklari(bas, bit)
        pi = perm_uretec(j).permutation(db.n_tam)
        for c in sorted(yasamlar):
            a, d = yasamlar[c]
            if a >= db.bit or d <= db.bas:
                continue
            atama, o, t = coin_blok_atamasi(a, d, db, pi, lambda j=j, c=c: ikincil_uretec(j, coin_no[c]))
            ortak, toplam = ortak + o, toplam + t
            k_ = kaynak[c]
            for k, b in atama.items():
                k_[db.blok_bas(k):db.blok_bas(k) + BLOK_SAAT] = np.arange(db.blok_bas(b), db.blok_bas(b) + BLOK_SAAT)
    return kaynak, {'ortak': ortak, 'toplam': toplam}


# --- P7: getiri uzayinda yeniden kurma (Ss3.5.3-3.5.4) ve null degismezleri N1-N6 (Ss3.5.7) ---

def yasamlar(veri, taban_ms: int, H: int) -> dict:
    """Coin -> (a, d): a ilk bar saati; d son bardan sonraki saat; son bar verinin son saatindeyse d = SONSUZ."""
    out = {}
    for c, s in veri.barlar.items():
        if len(s) == 0:
            continue
        h = (np.asarray(s.acilis_ms, dtype=np.int64) - taban_ms) // SAAT_MS
        out[c] = (int(h[0]), SONSUZ if int(h[-1]) == H - 1 else int(h[-1]) + 1)
    return out


def ro_getirileri(s) -> tuple:
    """Gercek barlarin (rhoO, rhoH, rhoL, rhoC) dizileri ve C^- (ilk barda O). Ss3.5.3."""
    o, hi, lo, k = (np.asarray(x, dtype=float) for x in (s.acilis, s.yuksek, s.dusuk, s.kapanis))
    onceki = np.concatenate(([o[0]], k[:-1])) if len(k) else k
    return np.log(o / onceki), np.log(hi / onceki), np.log(lo / onceki), np.log(k / onceki), onceki


def _coin_sentetik(s, kaynak: np.ndarray, taban_ms: int):
    h_gercek = (np.asarray(s.acilis_ms, dtype=np.int64) - taban_ms) // SAAT_MS
    ro, rh, rl, rc, onceki = ro_getirileri(s)
    bar_no = np.full(len(kaynak), -1, dtype=np.int64)
    bar_no[h_gercek] = np.arange(len(h_gercek))
    esli = bar_no[kaynak]                        # sentetik saat k -> gercek bar numarasi (yoksa -1)
    k_saat = np.nonzero(esli >= 0)[0]
    j = esli[k_saat]
    taban = onceki[j[0]]                         # ilk sentetik bar coinin ilk gercek bari (Y2): C^- = O
    # Sirali carpim: kap[k] = kap[k-1] * exp(rhoC) (cumprod siralidir); once * exp(rhoO) ayni islem olduğundan
    # O = H = L = C barlari bit duzeyinde duz kalir (donma olcutu (b)).
    kap = np.cumprod(np.concatenate(([taban], np.exp(rc[j]))))[1:]
    once = np.concatenate(([taban], kap[:-1]))
    return saatlik_seri(taban_ms + k_saat * SAAT_MS, once * np.exp(ro[j]), once * np.exp(rh[j]), once * np.exp(rl[j]),
                        kap, np.asarray(s.hacim, dtype=float)[j])


def _funding_sentetik(f, kaynak: np.ndarray, taban_ms: int):
    ters = np.empty(len(kaynak), dtype=np.int64)
    ters[kaynak] = np.arange(len(kaynak))
    h = (np.asarray(f.damga_ms, dtype=np.int64) - taban_ms) // SAAT_MS
    yeni = ters[h]
    sira = np.argsort(yeni, kind='stable')
    aralik = None if f.aralik_saat is None else np.asarray(f.aralik_saat, dtype=float)[sira]
    return funding_serisi(taban_ms + yeni[sira] * SAAT_MS, np.asarray(f.oran, dtype=float)[sira], aralik_saat=aralik)


def sentetik_veri(veri, kaynak: dict, taban_ms: int):
    """Ss3.5.3-3.5.4: her sentetik bar, esli gercek barin onceki kapanisa gore getirilerini tasir ve sentetik onceki
    kapanistan zincirlenir; hacim barla, funding kaydi blok ici goreli saatiyle tasinir (oran degismez). Eslemesi olmayan
    coin (kaynak'ta yok) aynen kalir."""
    barlar, funding = {}, {}
    for c, s in veri.barlar.items():
        barlar[c] = _coin_sentetik(s, kaynak[c], taban_ms) if c in kaynak and len(s) else s
    for c, f in veri.funding.items():
        funding[c] = _funding_sentetik(f, kaynak[c], taban_ms) if c in kaynak and len(f) else f
    return TamVeri(barlar=barlar, funding=funding, adaylar=veri.adaylar)


def n1_farki(a: np.ndarray, b: np.ndarray, tol: float):
    """N1: iki rho dörtlüsü kümesi (satır = bar) çoklu küme olarak tol içinde aynı mı. None: aynı; değilse en büyük
    sıralı fark. Satırlar tol ızgarasındaki anahtarla sıralanır (teknik ek banka_oncesi, 2 Ekim; HATA_N1.md): gerçek
    veride fiyat tikleri ve açılış = önceki kapanış çok sayıda tam bağ üretir, sentetikte exp/log yuvarlaması (~1e-16)
    bağları bozar; ham değerle lexsort bağlı grupların sırasını değiştirip farklı satırları eşliyordu. Izgara sınırına
    düşen değer için yarım hücre kaydırılmış ikinci ızgara denenir; ikisi de kaçırırsa kesin zincir eşleştirmesi
    (_zincir_esle). Karşılaştırma ham değerlerle, atol = tol."""
    fark = 0.0
    for kayma in (0.0, 0.5):
        ka, kb = np.floor(a / tol + kayma), np.floor(b / tol + kayma)
        a_s, b_s = a[np.lexsort(ka.T[::-1])], b[np.lexsort(kb.T[::-1])]
        if np.allclose(a_s, b_s, rtol=0.0, atol=tol):
            return None
        fark = float(np.max(np.abs(a_s - b_s)))
    return None if _zincir_esle(a, b, tol, 0) else fark      # Codex T32-1: iki ızgara da kaçırırsa kesin eşleştirme


def _zincir_esle(a: np.ndarray, b: np.ndarray, tol: float, k: int) -> bool:
    """Kesin yedek: k. sütunda değerler tol zinciriyle kümelenir (aralarında tol'den büyük boşluk olmayan ardışık
    değerler bir küme); her kümede a ve b satır sayısı eşit olmalı ve sonraki sütunla özyinelenir. Son sütundan sonra
    kümedeki satırlar sıralanıp tol içinde birebir karşılaştırılır. True yalnız tol içinde birebir eşleştirme bulunursa
    döner (yanlış kabul yok). Yaprakta sıralı karşılaştırma tutmazsa kesin ikili eşleştirme (Codex T33)."""
    if len(a) != len(b):
        return False
    if len(a) == 0:
        return True
    if k == a.shape[1]:
        a_s, b_s = a[np.lexsort(a.T[::-1])], b[np.lexsort(b.T[::-1])]
        return bool(np.allclose(a_s, b_s, rtol=0.0, atol=tol)) or _ikili_esle(a, b, tol)
    v = np.concatenate([a[:, k], b[:, k]])
    kaynak = np.concatenate([np.zeros(len(a), dtype=bool), np.ones(len(b), dtype=bool)])
    sira = np.argsort(v, kind='stable')
    kesim = np.flatnonzero(np.diff(v[sira]) > tol) + 1
    for grup in np.split(sira, kesim):
        ia, ib = grup[~kaynak[grup]], grup[kaynak[grup]] - len(a)
        if not _zincir_esle(a[ia], b[ib], tol, k + 1):
            return False
    return True


def _ikili_esle(a: np.ndarray, b: np.ndarray, tol: float, en_cok: int = 5000) -> bool:
    """Yaprak kümede kesin eşleştirme: uyumluluk grafiğinde (bütün sütunlar tol içinde) mükemmel eşleşme var mı
    (Kuhn, artıran yol derinlik öncelikli arama). en_cok satırdan büyük yaprakta False (yanlış ret; yanlış kabul
    değil). Uyumluluk satırı gerektikçe hesaplanır (bellek O(n), Codex T34)."""
    n = len(a)
    if n != len(b) or n > en_cok:
        return False
    a_es, b_es = [-1] * n, [-1] * n
    for i in range(n):
        onceki, kuyruk, gorulen, son = {}, [i], set(), -1
        while kuyruk and son < 0:
            x = kuyruk.pop()
            for j in np.flatnonzero(np.all(np.abs(b - a[x]) <= tol, axis=1)):
                j = int(j)
                if j in gorulen:
                    continue
                gorulen.add(j)
                onceki[j] = x
                if b_es[j] < 0:
                    son = j
                    break
                kuyruk.append(b_es[j])
        if son < 0:
            return False
        j = son
        while True:
            x = onceki[j]
            j_eski = a_es[x]
            a_es[x], b_es[j] = j, x
            if x == i:
                break
            j = j_eski
    return True


def degismezler(veri, sent, dilimler, taban_ms: int, tol: float = 1e-9) -> dict:
    """N1-N6 (Ss3.5.7), her coin ve her dilim. N1: sentetik rho dortlulerinin coklu kumesi gerceginkine esit (sirali
    listeler, mutlak tolerans tol; exp/log gidis-donus yuvarlamasi). Doner: {'gecti': bool, 'ihlaller': [...]}."""
    ihlal = []
    for c in sorted(veri.barlar):
        s, z = veri.barlar[c], sent.barlar[c]
        hs = (np.asarray(s.acilis_ms, dtype=np.int64) - taban_ms) // SAAT_MS
        hz = (np.asarray(z.acilis_ms, dtype=np.int64) - taban_ms) // SAAT_MS
        rs, rz = np.column_stack(ro_getirileri(s)[:4]), np.column_stack(ro_getirileri(z)[:4]) if len(z) else None
        fz, fs = sent.funding.get(c), veri.funding.get(c)
        for j, (bas, bit) in enumerate(dilimler, start=1):
            ms_, mz = (hs >= bas) & (hs < bit), (hz >= bas) & (hz < bit)
            if ms_.sum() != mz.sum():
                ihlal.append(('N3', c, j, 'bar sayisi'))
                continue
            if not ms_.any():
                continue
            # Y1/N3: giris ve cikis saatleri yalniz gercek yasam sinirlarinda denetlenir; yasam ici bosluk dilimin
            # kenar blogundan tasinabilir (Codex T12-6).
            a_i, d_son = int(hs[0]), int(hs[-1])
            if bas <= a_i < bit and hz[mz][0] != a_i:
                ihlal.append(('N3', c, j, 'listelenme bari'))
            if bas <= d_son < bit and hz[mz][-1] != d_son:
                ihlal.append(('N3', c, j, 'son bar'))
            a, b = rs[ms_], rz[mz]
            n1 = n1_farki(a, b, tol)
            if n1 is not None:
                ihlal.append(('N1', c, j, n1))
            if abs(a[:, 3].sum() - b[:, 3].sum()) > tol * max(1.0, abs(a[:, 3].sum())):
                ihlal.append(('N2', c, j, 'sum rhoC'))
            ks, kz = float(s.kapanis[ms_][-1]), float(z.kapanis[mz][-1])
            if abs(ks - kz) > tol * abs(ks):
                ihlal.append(('N2', c, j, 'dilim sonu kapanis'))
            if not np.array_equal(np.sort(s.hacim[ms_]), np.sort(z.hacim[mz])):
                ihlal.append(('N4', c, j, 'hacim'))
            if abs(np.max(np.abs(a[:, 3])) - np.max(np.abs(b[:, 3]))) > tol:
                ihlal.append(('N5', c, j, 'max |rhoC|'))
            if fs is not None and len(fs):
                t_s = (np.asarray(fs.damga_ms, dtype=np.int64) - taban_ms) // SAAT_MS
                t_z = (np.asarray(fz.damga_ms, dtype=np.int64) - taban_ms) // SAAT_MS
                o_s = np.sort(np.asarray(fs.oran)[(t_s >= bas) & (t_s < bit)])
                o_z = np.sort(np.asarray(fz.oran)[(t_z >= bas) & (t_z < bit)])
                if len(o_s) != len(o_z) or not np.array_equal(o_s, o_z):
                    ihlal.append(('N4', c, j, 'funding'))
        fiyat = np.concatenate([z.acilis, z.yuksek, z.dusuk, z.kapanis]) if len(z) else np.array([1.0])
        if not (np.all(np.isfinite(fiyat)) and np.all(fiyat > 0)):
            ihlal.append(('N6', c, 0, 'fiyat'))
    return {'gecti': not ihlal, 'ihlaller': ihlal}


def null_yolu(veri, taban_ms: int, H: int, dilimler, coin_no: dict, perm_uretec, ikincil_uretec) -> tuple:
    """Tek null yolu: saat eslemesi (P6) + yeniden kurma + N1-N6. Doner: (sentetik TamVeri, ortak pay sozlugu,
    degismez sonucu). Degismez ihlali T4'tur (Ss2.5); cagiran durur."""
    kaynak, pay = saat_eslemesi(yasamlar(veri, taban_ms, H), coin_no, dilimler, perm_uretec, ikincil_uretec, H)
    sent = sentetik_veri(veri, kaynak, taban_ms)
    return sent, pay, degismezler(veri, sent, dilimler, taban_ms)
