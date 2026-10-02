"""Strateji durumu ve olay gunlugunden yeniden kurulumu (saf). MIMARI Ss5.1 (durum_turet), Ss5.4, Ss5.8.

Ag, dosya, config veya durum erisimi yoktur. Durum yalniz gorunumden turetilemez (KC-12); pozisyon, nakit,
devreden emirler, evren ve maske gunlukten, katlama (fold) ile kurulur: StratejiDurumu = f(gorunum, gunluk).
Geri test orkestratoru ayni `kayit_uygula` indirgeyicisini artimsal kullanir; boylece artimsal durum ile
gunlukten yeniden kurulan durum tanim geregi aynidir ve parite testi bunu sinar.
Mimari B (carry) alanlari karar kaydinin 'carry' blogundan okunur (MIMARI Ss5.8: q^C*, beta, lambda, sanal
trend ve carry miktarlari, s^C son sifir-disi paylari).
"""
from bisect import bisect_left
from dataclasses import dataclass, field, replace

from .gorunum import PiyasaGorunumu, son_kapanis
from .hijyen import MaskeKaydi, maske_jsondan


class DurumHatasi(ValueError):
    """Gunluk bir 'baslangic' kaydiyla baslamiyor, hash zinciri bozuk ya da kayit bilinmeyen bir coine/emre
    atif yapiyor."""


@dataclass(frozen=True)
class MaliyetBaglami:
    """Karar aninda sabitlenen ve karar boyunca degismeyen dolum/maliyet girdileri (MIMARI Ss3.7, Ss6.1)."""
    v1h30: float
    v1h7: float
    v60: float
    sigma_d_bps: float        # karar anindaki gunluk sigma_EWMA / sqrt(365), bps
    sigma_1h: float           # son 30 gunun saatlik log getiri std'si (nan olabilir)
    btc_eth: bool
    btc_sigma_1h: float

    def json(self) -> dict:
        return {k: (None if (isinstance(v, float) and v != v) else v) for k, v in self.__dict__.items()}

    @classmethod
    def jsondan(cls, d: dict) -> 'MaliyetBaglami':
        return cls(**{k: (float('nan') if v is None else v) for k, v in d.items()})


@dataclass(frozen=True)
class Emir:
    """Devreden (dolmayi bekleyen) emir. kalan isaretli; + alis, - satis."""
    kalan: float
    karar_ms: int
    maske_cikisi: bool        # maliyet carpani m_i = 3 (MIMARI Ss6.1)
    tam_kapanis: bool         # hedef 0: son parca minNotional'dan muaf ve tam -q doldurur
    baglam: MaliyetBaglami

    def json(self) -> dict:
        return {'kalan': self.kalan, 'karar_ms': self.karar_ms, 'maske_cikisi': self.maske_cikisi,
                'tam_kapanis': self.tam_kapanis, 'baglam': self.baglam.json()}

    @classmethod
    def jsondan(cls, d: dict) -> 'Emir':
        return cls(kalan=float(d['kalan']), karar_ms=int(d['karar_ms']), maske_cikisi=bool(d['maske_cikisi']),
                   tam_kapanis=bool(d['tam_kapanis']), baglam=MaliyetBaglami.jsondan(d['baglam']))


@dataclass(frozen=True)
class StratejiDurumu:
    t_ms: int = 0
    pozisyonlar: dict = field(default_factory=dict)     # coin -> q (isaretli miktar)
    nakit: float = 0.0
    devreden: dict = field(default_factory=dict)        # coin -> Emir
    evren: tuple = ()
    evren_ms: object = None                             # son aylik secimin damgasi
    maske: dict = field(default_factory=dict)           # coin -> MaskeKaydi
    maske_ms: object = None                             # maske durumunun islendigi son gun
    son_karar_ms: object = None
    son_kacirilan_ms: object = None
    funding_dolgu: dict = field(default_factory=dict)   # coin -> ((saat_ms, tutar), ...) ters kaydi bekleyen dolgular
    funding_dolgu_kadar: dict = field(default_factory=dict)  # coin -> son dolgu kaydinin damgasi (dahil)
    funding_islenen: dict = field(default_factory=dict)  # coin -> islenmis gercek kayit damgalari (gec kayit penceresi)
    bosluk_ref: object = None                           # maske_ms'te suren borsa kesintisinin referans saati
    bosluk_gecmis: tuple = ()                           # son karardan geriye BOSLUK_GECMIS_GUN gunun bosluk saatleri
    uzlasilan: tuple = ()
    son_nav: object = None
    nav0: object = None
    # Mimari B (MIMARI Ss4.4, Ss4.7, Ss5.8)
    carry_q: dict = field(default_factory=dict)         # alt -> q^C* (haftalik miktar, hafta ici cikislar sonrasi)
    carry_beta: dict = field(default_factory=dict)      # alt -> beta (Pazartesi karari)
    carry_hafta_ms: object = None                       # son yapilan Pazartesi carry kararinin damgasi
    carry_lam: float = 1.0                              # son Pazartesi yeniden notrleme lambda'si (Ss4.4 adim 6)
    carry_bagli: str = ''                               # lambda'nin bagladigi bacak
    carry_adaylar: tuple = ()                           # son Pazartesi carry aday listesi (Ss4.1 histerezisi, Ss3.2)
    sanal_trend: dict = field(default_factory=dict)     # coin -> q^T,v (son kararin; 01:00'da gecerli)
    sanal_carry: dict = field(default_factory=dict)     # coin -> q^C,v (BTC hedge dahil)
    sc_son: dict = field(default_factory=dict)          # coin -> son sifir-disi s^C (Ss4.7 sifir/sifir kurali)


def _sifir_mi(x: float) -> bool:
    return x == 0.0


def kayit_uygula(d: StratejiDurumu, k) -> StratejiDurumu:
    """Tek bir gunluk kaydini duruma uygulayan saf indirgeyici."""
    tur = k.tur
    if tur == 'baslangic':
        return replace(d, t_ms=k.damga_ms, nakit=float(k.veri['nav0']), nav0=float(k.veri['nav0']))
    if d.nav0 is None:
        raise DurumHatasi("gunluk 'baslangic' kaydiyla baslamali")
    d = replace(d, t_ms=k.damga_ms)
    c = k.coin
    if tur == 'dolum':
        poz = dict(d.pozisyonlar)
        q = poz.get(c, 0.0) + k.miktar
        if k.veri.get('tam_kapanis_son'):
            q = 0.0
        if _sifir_mi(q):
            poz.pop(c, None)
        else:
            poz[c] = q
        dev = dict(d.devreden)
        e = dev.get(c)
        if e is None:
            raise DurumHatasi(f"devreden emri olmayan coinde dolum: {c}")
        kalan = e.kalan - k.miktar
        if k.veri.get('tam_kapanis_son') or _sifir_mi(kalan) or (kalan > 0) != (e.kalan > 0):
            dev.pop(c)
        else:
            dev[c] = replace(e, kalan=kalan)
        return replace(d, pozisyonlar=poz, nakit=d.nakit - k.miktar * k.fiyat, devreden=dev)
    if tur == 'duzeltme':
        # Canli: borsa kaydiyla uyusmazlik (MIMARI Ss5.8). tutar nakde; miktar (varsa) pozisyona eklenir.
        # Devreden emir farki ayrica 'devreden_iptal' kaydiyla duzeltilir.
        poz = dict(d.pozisyonlar)
        if k.miktar is not None and k.miktar != 0.0:
            q = poz.get(c, 0.0) + k.miktar
            if _sifir_mi(q):
                poz.pop(c, None)
            else:
                poz[c] = q
        return replace(d, pozisyonlar=poz, nakit=d.nakit + float(k.veri.get('tutar', 0.0)))
    if tur in ('funding', 'funding_dolgu', 'ters_kayit'):
        nakit = d.nakit + float(k.veri.get('tutar', 0.0))
        fd = dict(d.funding_dolgu)
        if tur == 'funding':
            # Gercek kayit (damgasi veri['damga_ms']; gec gelebilir): kapsadigi (kapsam_bas, damga] saatlerinin
            # dolgulari ayni adimda 'ters_kayit' ile geri alinmistir ve beklemeden duser. Kapsanmayan dolgular
            # (gercekten eksik uzlasmalar) gec kayit penceresi boyunca bekler, sonra budanir (kesinlesir).
            damga = int(k.veri['damga_ms'])
            kapsam_bas = int(k.veri.get('kapsam_bas_ms', damga))
            budama = int(k.veri.get('budama_ms', damga))
            kalan = tuple(x for x in fd.get(c, ()) if not (kapsam_bas < x[0] <= damga) and x[0] >= budama)
            if kalan:
                fd[c] = kalan
            else:
                fd.pop(c, None)
            fi = dict(d.funding_islenen)
            fi[c] = tuple(sorted(x for x in set(fi.get(c, ())) | {damga} if x >= budama))
            return replace(d, nakit=nakit, funding_dolgu=fd, funding_islenen=fi)
        if tur == 'funding_dolgu':
            fd[c] = fd.get(c, ()) + tuple((int(h), float(t)) for h, t in k.veri['saatler'])
            fk = dict(d.funding_dolgu_kadar)
            fk[c] = k.damga_ms
            return replace(d, nakit=nakit, funding_dolgu=fd, funding_dolgu_kadar=fk)
        return replace(d, nakit=nakit)
    if tur == 'karar':
        v = k.veri
        maske = {coin: maske_jsondan(m) for coin, m in v['maske'].items()}
        # Gunluk budama: sifir tutarli kayitlar yazilmadigi icin funding olayi gelmeyen coinde de eski dolgu ve
        # islenen damgalar temizlenir (Codex 3. tur).
        budama = v.get('funding_budama_ms')
        fd, fi = d.funding_dolgu, d.funding_islenen
        if budama is not None:
            fd = {c2: t for c2, t in ((c2, tuple(x for x in xs if x[0] >= budama)) for c2, xs in fd.items()) if t}
            fi = {c2: t for c2, t in ((c2, tuple(x for x in xs if x >= budama)) for c2, xs in fi.items()) if t}
        d = replace(d, funding_dolgu=fd, funding_islenen=fi)
        cr = v.get('hedef', {}).get('carry')
        if cr is not None:
            d = replace(d, carry_q={c2: float(x) for c2, x in cr['q_yildiz'].items()},
                        carry_beta={c2: float(x) for c2, x in cr['beta'].items()},
                        carry_hafta_ms=cr.get('hafta_ms'), carry_lam=float(cr.get('lam', 1.0)),
                        carry_bagli=cr.get('bagli_bacak', ''), carry_adaylar=tuple(cr.get('adaylar', ())),
                        sanal_trend={c2: float(x) for c2, x in cr['sanal_trend'].items()},
                        sanal_carry={c2: float(x) for c2, x in cr['sanal_carry'].items()},
                        sc_son={c2: float(x) for c2, x in cr['sc_son'].items()})
        return replace(d, evren=tuple(v['evren']), evren_ms=v.get('evren_ms'), maske=maske,
                       maske_ms=k.damga_ms, son_karar_ms=k.damga_ms, bosluk_ref=v.get('bosluk_ref'),
                       bosluk_gecmis=tuple(v.get('bosluk_gecmis', ())))
    if tur == 'kacirilan_karar':
        return replace(d, son_kacirilan_ms=k.damga_ms)
    if tur == 'devreden_iptal':
        dev = dict(d.devreden)
        e = dev.get(c)
        if e is None:
            raise DurumHatasi(f"devreden emri olmayan coinde iptal: {c}")
        kalan = e.kalan - float(k.veri['iptal'])
        if k.veri.get('tamami') or _sifir_mi(kalan):
            dev.pop(c)
        else:
            # Korunan parca pozisyonu tam kapatiyorsa (isaret degistiren emrin 0'a kadarki kismi) tam kapanis
            # niteligi kazanir: son parca minNotional'dan muaf (MIMARI Ss5.1, Ss5.4; Codex K14).
            dev[c] = replace(e, kalan=kalan, tam_kapanis=e.tam_kapanis or bool(k.veri.get('tam_kapanis')))
        return replace(d, devreden=dev)
    if tur == 'emir_niyeti':
        dev = dict(d.devreden)
        if c in dev:
            raise DurumHatasi(f"eski emir iptal edilmeden yeni niyet yazilamaz: {c}")
        dev[c] = Emir.jsondan(k.veri['emir'])
        return replace(d, devreden=dev)
    if tur == 'uzlasma':
        poz = dict(d.pozisyonlar)
        q = poz.pop(c, 0.0)
        dev = dict(d.devreden)
        dev.pop(c, None)
        return replace(d, pozisyonlar=poz, devreden=dev, nakit=d.nakit + q * k.fiyat,
                       uzlasilan=tuple(sorted(set(d.uzlasilan) | {c})))
    if tur == 'nav':
        return replace(d, son_nav=float(k.veri['nav']))
    raise DurumHatasi(f"indirgeyicide tanimsiz tur: {tur}")


def durum_turet(g: PiyasaGorunumu, gunluk, p=None) -> StratejiDurumu:
    """MIMARI Ss5.1/Ss5.8: StratejiDurumu = f(gorunum, gunluk). Gunlugun damgasi <= g.t_ms olan kayitlari
    sirayla katlanir. Maske sayaclarinin son karardan bugune ilerletilmesi karar adiminda yapilir (gorunumden).
    Once hash zinciri dogrulanir; bozuk gunlukten durum kurulmaz (Codex K15)."""
    if not gunluk.dogrula():
        raise DurumHatasi("gunlugun hash zinciri bozuk; durum turetilemez")
    d = StratejiDurumu()
    for k in gunluk.kayitlar(g.t_ms):
        d = kayit_uygula(d, k)
    return replace(d, t_ms=g.t_ms)


def nav_hesapla(d: StratejiDurumu, g: PiyasaGorunumu) -> float:
    """NAV = nakit + sum q_i * son gecerli kapanis (MIMARI Ss5.2 adim 4; cikilamayan pozisyon son gecerli
    kapanisla degerlenir, Ss1c.4)."""
    toplam = d.nakit
    for c, q in d.pozisyonlar.items():
        s = g.barlar.get(c)
        fiyat = son_kapanis(s, g.t_ms) if s is not None else None
        if fiyat is None:
            raise DurumHatasi(f"pozisyonlu coinin hic kapanisi yok: {c}")
        toplam += q * fiyat
    return toplam


def pozisyon_gecmisi(gunluk, coin: str) -> tuple:
    """((damga, q_sonrasi), ...) — funding dolgusunda q(h-) icin. Dolum, uzlasma ve miktarli duzeltme
    kayitlarindan."""
    q = 0.0
    gecmis = []
    for k in gunluk.kayitlar():
        if k.coin != coin:
            continue
        if k.tur == 'dolum':
            q = 0.0 if k.veri.get('tam_kapanis_son') else q + k.miktar
            gecmis.append((k.damga_ms, q))
        elif k.tur == 'uzlasma':
            q = 0.0
            gecmis.append((k.damga_ms, q))
        elif k.tur == 'duzeltme' and k.miktar is not None and k.miktar != 0.0:
            q = q + k.miktar
            gecmis.append((k.damga_ms, q))
    return tuple(gecmis)


def q_once(gecmis: tuple, h_ms: int) -> float:
    """q(h-): damgasi < h olan son degisiklikten sonraki pozisyon (h'deki dolumlar funding'den sonradir)."""
    i = bisect_left(gecmis, (h_ms, float('-inf')))
    return gecmis[i - 1][1] if i > 0 else 0.0
