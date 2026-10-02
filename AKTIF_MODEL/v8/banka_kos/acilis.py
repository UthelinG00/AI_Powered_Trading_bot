"""Banka açılışı: tek atış betiğinin ortak katmanı (BANKA §2.3–§2.5, §3.7 netleştirme 20; BK-20).

- Dönemler (`Donem`): banka (ayar sabitleri, T0_Z1 veriden) ve kuru koşu (20 e: D'ye taşınmış aynı yapı).
- Kimlikler ve T1: DONDURMA.json alanlarının yeniden hesabı (motor, banka_kos, veri_denetim, parametreler, HAR, ortam,
  tohum_banka).
- ACILIS.json denetimi (20 a): değerlendirici oturumun mühürden hazırladığı girdi; betik mühürü okumaz.
- Sembol filtreleri: kilitli exchangeInfo görüntüsünden veri adayları için (sha256 ALINMA.json ile aynı olmalı).
- Veri: banka (netleştirme 19 yükleyicisi) ya da kuru (D paketi); yükleyici raporunun coin adsız toplamı.
- `baglam_kur(tanim)`: her işçide aynı yoldan BankaBaglami (veri kimliği denetimli). tanim düz sözlüktür (pickle).
Açık gruba giden hiçbir çıktı coin adı ya da performans taşımaz.
"""
import hashlib
import json
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path

from . import anonim, ayar
from .veri_denetim import kanonik

V8 = Path(__file__).resolve().parents[1]
AKTIF = V8.parent
FILTRE_KLASORU = AKTIF / 'ciktilar' / 'v8_sembol_filtreleri_20260930_01'
BTC, ETH = 'BTCUSDT', 'ETHUSDT'
GUN_MS = ayar.GUN_MS
ACILIS_ALANLARI = ('mimari', 'adaylar', 'k_coinleri', 'd_coinleri', 'gorulmus_gunler', 'banka_kok', 'anonim_anahtar',
                   'sureklilik_sorunu')
DONDURMA_ALANLARI = ('motor_sha256', 'banka_kos_sha256', 'veri_denetim_sha256', 'parametreler_sha256',
                     'har_sonuc_sha256', 'ortam')
K_N, D_N = 80, 120                                     # BANKA §2.3 (20 j); sentetik testler boyut denetimini kapatır


class AcilisHatasi(RuntimeError):
    """T1 (kimlik ya da açılış girdisi tutarsız) ya da T2 kararı / veri kimliği uyuşmazlığı: koşu başlamaz."""


def sha_bayt(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


# --------------------------------------------------------------------------------------------------- dönemler
@dataclass(frozen=True)
class Donem:
    motor_bas_ms: int
    t0_z1_ms: int
    z1_dilim_sinir: tuple
    birincil_son_ms: int
    d_bas_ms: int
    d_bit_ms: int
    z2_bas_ms: int
    z2_son_ms: int

    def json(self) -> dict:
        return {k: list(v) if isinstance(v, tuple) else v for k, v in asdict(self).items()}


def ay_ekle(t_ms: int, ay: int) -> int:
    d = datetime.fromtimestamp(t_ms / 1000, timezone.utc)
    if d.day != 1 or t_ms % GUN_MS:
        raise ValueError("ay basi 00:00 olmali")
    n = d.year * 12 + (d.month - 1) + ay
    return int(datetime(n // 12, n % 12 + 1, 1, tzinfo=timezone.utc).timestamp() * 1000)


def _ilkler(veri) -> tuple:
    for c in (BTC, ETH):
        if c not in veri.barlar or not len(veri.barlar[c].acilis_ms):
            raise AcilisHatasi(f"{c} verisi yok (T0_Z1 hesaplanamaz)")
    ilk = min(int(s.acilis_ms[0]) for s in veri.barlar.values() if len(s.acilis_ms))
    return ilk - ilk % GUN_MS, ayar.t0_z1(int(veri.barlar[BTC].acilis_ms[0]), int(veri.barlar[ETH].acilis_ms[0]))


def banka_donemi(veri) -> Donem:
    motor_bas, t0 = _ilkler(veri)
    return Donem(motor_bas_ms=motor_bas, t0_z1_ms=t0, z1_dilim_sinir=tuple(ayar.Z1_DILIM_SINIR),
                 birincil_son_ms=ayar.BIRINCIL_SON_MS, d_bas_ms=ayar.D_BAS_MS, d_bit_ms=ayar.D_BIT_MS,
                 z2_bas_ms=ayar.Z2_BAS_MS, z2_son_ms=ayar.Z2_SON_MS)


def kuru_donemi(veri, d_bit_ms: int = ayar.D_BIT_MS) -> Donem:
    """20 e: T0 = T0_Z1 kuralı D'nin BTC/ETH ilk barına; dilimler T0 + 6/12/18 ay; birincil son T0 + 24 ay; 'D'
    penceresi [birincil son, + 6 ay); Z2 = [D sonu − 3 ay, D sonu)."""
    motor_bas, t0 = _ilkler(veri)
    son = ay_ekle(t0, 24)
    z2_bas = ay_ekle(d_bit_ms, -3)
    if not (son < ay_ekle(son, 6) <= z2_bas):
        raise AcilisHatasi("kuru donemler D'ye sigmiyor")
    return Donem(motor_bas_ms=motor_bas, t0_z1_ms=t0, z1_dilim_sinir=tuple(ay_ekle(t0, a) for a in (6, 12, 18)),
                 birincil_son_ms=son, d_bas_ms=son, d_bit_ms=ay_ekle(son, 6), z2_bas_ms=z2_bas, z2_son_ms=d_bit_ms)


# --------------------------------------------------------------------------------------------------- kimlikler, T1
def _py(kok: Path) -> list:
    return sorted(p for p in kok.rglob('*.py') if '__pycache__' not in p.parts)


def kimlikler() -> dict:
    """DONDURMA.json'un yeniden hesaplanan alanları (20 b)."""
    from kalibrasyon import birim as B
    from kalibrasyon.yurutucu import har_paketi
    from kilit import ortam
    from motor.tipler import Parametreler
    har_sha, _ = har_paketi()
    motor = B.motor_kimligi()
    betik = ([V8 / 'banka_kos.py', V8 / 'banka_hukum.py', V8 / 'dondur.py'] + _py(V8 / 'banka_kos') + _py(V8 / 'banka')
             + _py(V8 / 'kalibrasyon') + _py(V8 / 'adaptor'))                          # UYGULAMA_EK U2
    return {'motor_sha256': motor, 'banka_kos_sha256': B._birlesik_sha256([p for p in betik if p.exists()]),
            'veri_denetim_sha256': sha_bayt((V8 / 'veri_denetim.py').read_bytes()),
            'parametreler_sha256': B.parametre_kimligi(Parametreler(), har_sha), 'har_sonuc_sha256': har_sha,
            'ortam': ortam(), 'tohum_banka': tohum_turet(motor)}


def tohum_turet(motor_sha256: str) -> int:
    return int(motor_sha256[:16], 16) % (2 ** 32)


def t1_denetimi(dondurma: dict, guncel: dict, depo: Path = AKTIF.parent) -> list:
    """Uyuşmayan alanlar (boşsa T1 yok). tohum_banka ilk dondurmanın motor hash'inden türetilmiş olmalı (20 k, l):
    teknik düzeltme sonrası kayıt `ilk_dondurma` = {yol, sha256} ile ilk kaydı gösterir; ilk kayıt okunur, sha256'sı
    doğrulanır, tohum ondan alınır. İlk kaydın kendisi `ilk_dondurma` taşımaz."""
    fark = [a for a in DONDURMA_ALANLARI if dondurma.get(a) != guncel[a]]
    kok = dondurma
    if 'ilk_dondurma' in dondurma:
        g = dondurma['ilk_dondurma']
        y = Path(depo) / str(g.get('yol', ''))
        b = y.read_bytes() if y.is_file() else b''
        kok = json.loads(b.decode('utf-8')) if b and sha_bayt(b) == g.get('sha256') else None
        if kok is None or 'ilk_dondurma' in kok or kok.get('tohum_banka') != dondurma.get('tohum_banka'):
            return fark + ['ilk_dondurma']
    ms = kok.get('motor_sha256')
    if not isinstance(ms, str) or kok.get('tohum_banka') != tohum_turet(ms):
        fark.append('tohum_banka_turetimi')
    return fark


# --------------------------------------------------------------------------------------------------- ACILIS
def acilis_oku(yol, dondurma: dict = None, boyut: bool = True) -> tuple:
    """(ACILIS sözlüğü, kanonik sha256). 20 a, j denetimleri; aykırılık AcilisHatasi (T1). boyut: |K| = 80, |D| = 120."""
    a = json.loads(Path(yol).read_text(encoding='utf-8'))
    eksik = [k for k in ACILIS_ALANLARI if k not in a]
    if eksik:
        raise AcilisHatasi(f"ACILIS alanlari eksik: {eksik}")
    ad, k, d = set(a['adaylar']), set(a['k_coinleri']), set(a['d_coinleri'])
    gun = [str(x) for x in a['gorulmus_gunler']]
    if a['mimari'] not in ('A', 'B'):
        raise AcilisHatasi("mimari A ya da B")
    if dondurma is not None and dondurma.get('mimari') != a['mimari']:
        raise AcilisHatasi("ACILIS mimarisi DONDURMA ile ayni degil")
    if not (k <= ad and d <= ad) or (k & d):
        raise AcilisHatasi("K ve D adaylarin ayrik alt kumeleri olmali")
    if (ad - {BTC, ETH}) != (k | d) or ({BTC, ETH} & (k | d)):
        raise AcilisHatasi("adaylar - {BTC, ETH} = K birlesim D olmali; BTC/ETH K ya da D'de olmaz (20 l)")
    if len(k) != len(a['k_coinleri']) or len(d) != len(a['d_coinleri']) or len(ad) != len(a['adaylar']):
        raise AcilisHatasi("listelerde tekrar var")
    if not k or not d or (boyut and (len(k) != K_N or len(d) != D_N)):
        raise AcilisHatasi("K ve D buyuklukleri (80, 120) tutmuyor")
    if len(set(gun)) != 7:
        raise AcilisHatasi("gorulmus gun sayisi 7 olmali")
    for g in gun:
        datetime.strptime(g, '%Y-%m-%d')
    if not isinstance(a['sureklilik_sorunu'], int) or a['sureklilik_sorunu'] < 0:
        raise AcilisHatasi("sureklilik_sorunu negatif olmayan tamsayi olmali")
    return a, sha_bayt(kanonik(a))


def gun_ms(g: str) -> int:
    return int(datetime.strptime(g, '%Y-%m-%d').replace(tzinfo=timezone.utc).timestamp() * 1000)


# --------------------------------------------------------------------------------------------------- filtreler
def filtreler_kur(adaylar, klasor: Path = FILTRE_KLASORU) -> tuple:
    """({sembol: (adım, minNotional)}, rapor). Kilitli ham görüntünün sha256'sı ALINMA.json'dakiyle aynı olmalı."""
    from adaptor.sembol_filtreleri import tablo
    alinma = json.loads((klasor / 'ALINMA.json').read_text(encoding='utf-8'))
    ham = (klasor / 'exchangeInfo_ham.json').read_bytes()
    if sha_bayt(ham) != alinma['exchangeInfo_ham_sha256']:
        raise AcilisHatasi("exchangeInfo goruntusu kilitteki hash ile ayni degil")
    t = tablo(json.loads(ham), adaylar)
    f = {c: (float(v['adim']), float(v['min_notional'])) for c, v in sorted(t.items())}
    return f, {'exchangeInfo_ham_sha256': alinma['exchangeInfo_ham_sha256'], 'aday': len(set(adaylar)),
               'filtreli': len(f), 'filtresiz_sembol': len(set(adaylar) - set(f)),
               'tablo_sha256': sha_bayt(kanonik({c: list(v) for c, v in f.items()}))}


# --------------------------------------------------------------------------------------------------- veri
def _topla(hedef: dict, kaynak: dict):
    for k, v in kaynak.items():
        if isinstance(v, bool):
            hedef[k] = hedef.get(k, 0) + int(v)
        elif isinstance(v, (int, float)):
            hedef[k] = hedef.get(k, 0) + v
        elif isinstance(v, dict):
            _topla(hedef.setdefault(k, {}), v)


def rapor_ozeti(coin_rapor: dict) -> dict:
    """Yükleyici raporunun coin adsız toplamı (açık grup)."""
    out = {}
    for r in coin_rapor.values():
        _topla(out, r)
    return out


def veri_adaylari(acilis: dict) -> tuple:
    return tuple(sorted(set(acilis['adaylar']) | {BTC, ETH}))


def veri_yukle(tanim: dict, dogrula: bool = True) -> tuple:
    """(TamVeri, {'veri_kimligi', 'dosya_sayisi', 'ozet', 'manifest', 'eylul_funding'}). tanim['mod']: banka | kuru."""
    if tanim['mod'] == 'kuru':
        from adaptor import veri_yukleyici as dv
        from .veri import BankaVeriHatasi, eksik_dosyalar
        kok = Path(tanim['d_kok']) if tanim.get('d_kok') else dv.veri_koku_bul()
        evren = tuple(tanim['evren']) if tanim.get('evren') else dv.gelistirme_evreni()        # evren: yalnız testler
        if eksik_dosyalar(kok, dv.manifest_tamam(kok), evren):                                  # 20 l (3)
            raise BankaVeriHatasi("D manifestinde TAMAM olan dosya diskte yok")
        veri, r = dv.tam_veri_yukle(kok, dogrula=dogrula, evren=evren)
        manifest = [{'yol': y, 'sha256': h, 'checksum': h, 'durum': 'TAMAM'} for y, h in sorted(dv.manifest_tamam(kok).items())]
        return veri, {'veri_kimligi': r.veri_kimligi, 'dosya_sayisi': r.dosya_sayisi, 'ozet': rapor_ozeti(r.coin),
                      'manifest': manifest, 'eylul_funding': 'yok (kuru: D paketi)'}
    from .veri import MANIFEST_ADI, banka_veri_yukle
    a = tanim['acilis']
    d_kok = a.get('d_kok')
    if d_kok is None:
        from adaptor.veri_yukleyici import veri_koku_bul
        d_kok = veri_koku_bul()
    veri, r = banka_veri_yukle(a['banka_kok'], d_kok, veri_adaylari(a), set(a['d_coinleri']) | {BTC, ETH},
                               dogrula=dogrula)
    manifest = [json.loads(s) for s in (Path(a['banka_kok']) / MANIFEST_ADI).read_text(encoding='utf-8').splitlines()
                if s.strip()]
    api = sum(1 for c in r['coin'].values() if c['funding'].get('api_goruntusu'))
    return veri, {'veri_kimligi': r['veri_kimligi'], 'dosya_sayisi': r['dosya_sayisi'], 'ozet': rapor_ozeti(r['coin']),
                  'manifest': manifest, 'eylul_funding': f"api_goruntusu ({api} sembol)" if api else 'arsiv'}


def d_eksik(tanim: dict) -> int:
    """D paketinden alınan sembollerin manifestte TAMAM olup diskte olmayan dosya sayısı (20 l (3); T2 (1))."""
    from adaptor import veri_yukleyici as dv
    from .veri import eksik_dosyalar
    if tanim['mod'] == 'kuru':
        kok = Path(tanim['d_kok']) if tanim.get('d_kok') else dv.veri_koku_bul()
        semboller = tuple(tanim['evren']) if tanim.get('evren') else dv.gelistirme_evreni()
    else:
        a = tanim['acilis']
        kok = Path(a['d_kok']) if a.get('d_kok') else dv.veri_koku_bul()
        semboller = tuple(sorted(set(a['d_coinleri']) | {BTC, ETH}))
    return len(eksik_dosyalar(kok, dv.manifest_tamam(kok), semboller))


def donem_kur(tanim: dict, veri) -> Donem:
    return kuru_donemi(veri) if tanim['mod'] == 'kuru' else banka_donemi(veri)


def k_coinleri(tanim: dict, veri) -> tuple:
    """K (B9): bankada ACILIS'teki 80 coin; kuruda geliştirme evreni (BTC/ETH hariç; ayrım yok, 20 e)."""
    if tanim['mod'] == 'kuru':
        return tuple(sorted(c for c in veri.adaylar if c not in (BTC, ETH)))
    return tuple(sorted(tanim['acilis']['k_coinleri']))


def gorulmus(tanim: dict) -> tuple:
    return () if tanim['mod'] == 'kuru' else tuple(sorted(gun_ms(g) for g in tanim['acilis']['gorulmus_gunler']))


def baglam_kur(tanim: dict):
    """İşçi bağlamı (BK-1). Veri her işçide doğrulamalı yüklenir; kimliği tanımdakiyle aynı olmalı."""
    from kalibrasyon.yurutucu import har_paketi
    from .yurutucu import BankaBaglami
    veri, r = veri_yukle(tanim)
    if r['veri_kimligi'] != tanim['veri_kimligi']:
        raise AcilisHatasi("iscide veri kimligi farkli")
    dm = donem_kur(tanim, veri)
    filtreler, frapor = filtreler_kur(veri.adaylar, Path(tanim.get('filtre_klasoru') or FILTRE_KLASORU))
    har_sha, beta = har_paketi()
    anahtar = Path(tanim['anonim_anahtar']).read_bytes()
    if (dm.json() != tanim['donem'] or frapor['tablo_sha256'] != tanim['filtre_tablo_sha256']
            or har_sha != tanim['har_sonuc_sha256'] or sha_bayt(anahtar) != tanim['anonim_anahtar_sha256']):
        raise AcilisHatasi("iscide baglam kimlikleri farkli (donem, filtre, HAR ya da anonim anahtar)")
    k = k_coinleri(tanim, veri)
    return BankaBaglami(
        veri=veri, k_adaylar=tuple(sorted(set(k) | {BTC, ETH})), motor_bas_ms=dm.motor_bas_ms, t0_z1_ms=dm.t0_z1_ms,
        gorulmus_gunler=gorulmus(tanim), filtreler=filtreler, beta=beta, tohum_banka=tanim['tohum_banka'],
        anonim=anonim.kimlikler(anahtar, veri.adaylar),
        birincil_son_ms=dm.birincil_son_ms, z1_dilim_sinir=dm.z1_dilim_sinir, z2_son_ms=dm.z2_son_ms)


# --------------------------------------------------------------------------------------------------- hazırlık
def _kuru_alici(cikti: Path) -> str:
    """Kuru koşu alıcısı (20 e): tek kullanımlık anahtar; gizli yarısı diske yazılmaz. Devam için açık yarı saklanır."""
    from . import age
    yol = cikti / 'KURU_ALICI.txt'
    if yol.exists():
        return yol.read_text(encoding='ascii').strip()
    _, alici = age.anahtar_uret()
    cikti.mkdir(parents=True, exist_ok=True)
    yol.write_text(alici + '\n', encoding='ascii')
    return alici


def kilit_tam(yol, kilit_commit: str, ek_commitler=(), izinli_turler=('kapi',), git: bool = True) -> dict:
    """UYGULAMA_EK U2 (21 g; Codex T30-1/7). `banka_kos` kilit kimliğinde değildir (21 g T29 eki), ama kilidin V1
    ön koşulu bugünkü en yeni test raporunu ister; bu yüzden ilk kilit ön koşulsuz doğrulanır ve ön koşullar ayrıca
    denetlenir (teknik ek varsa (2) atlanır: 21 g, ekte kalibrasyon ön koşulları yeniden doğrulanmaz): (1) zincir: belgeler, kod, parametre, ortam, veri, sabitler, defter ve git (uzak commit'ler);
    (2) kalibrasyon ön koşulları yeniden hesaplanır ve kilittekiyle aynı olmalı (V1 hariç); (3) kilitteki V1 raporu
    tarihsel kanıttır: dosyası duruyor ve sha256'sı aynı; (4) güncel V1: bugünkü bütün kod kimliklerini (banka_kos dahil)
    kapsayan, geçen en yeni test raporu (kilit.v1_raporu). Teknik ekler sıra, tür ve sha256'larıyla döner.
    Doner {'zincir', 'v1_guncel', 'teknik_ekler'}; aykırılık kilit.KilitHatasi."""
    import kilit
    from kalibrasyon import birim as B
    yol = Path(yol)
    z = kilit.zincir_dogrula(yol, git=git, kilit_commit=kilit_commit, ek_commitler=tuple(ek_commitler),
                             izinli_turler=tuple(izinli_turler), onkosul=False)
    ilk = json.loads(yol.read_text(encoding='ascii'))
    ek_yollari = kilit._ekler(yol.parent)
    on = kilit.onkosullar(kilit.AKTIF, v1=False) if not ek_yollari else None   # 21 g: ekte yeniden doğrulanmaz
    beklenen = {k: v for k, v in (ilk.get('onkosul') or {}).items() if k != 'v1'}
    if on is not None and on != beklenen:
        raise kilit.KilitHatasi(f"kalibrasyon on kosullari kilittekinden farkli: {sorted(set(on) ^ set(beklenen))}"
                                if set(on) != set(beklenen) else "kalibrasyon on kosullari kilittekinden farkli")
    v1 = ilk['onkosul']['v1']
    tarihsel = V8 / 'ciktilar' / v1['rapor'] / 'sonuc.json'
    if not tarihsel.is_file() or sha_bayt(tarihsel.read_bytes()) != v1['sha256']:
        raise kilit.KilitHatasi("kilitteki V1 raporu yok ya da sha256'si farkli")
    ekler = [{'sira': e['sira'], 'tur': e['tur'], 'sha256': sha_bayt(y.read_bytes())}
             for y in ek_yollari for e in [json.loads(y.read_text(encoding='ascii'))]]
    return {'zincir': z, 'v1_guncel': kilit.v1_raporu(B.motor_kimligi()), 'teknik_ekler': ekler}


def kilit_zinciri(dondurma: dict) -> dict:
    """U2: DONDURMA'daki kilit dosyası (yol + sha256), zincir ve uzak commit'ler (banka türleri dahil), teknik eklerin
    DONDURMA'daki {sıra, tür, sha256} kaydıyla birebir eşleşmesi ve güncel V1 raporunun DONDURMA'dakiyle aynı olması."""
    import kilit
    yol = AKTIF / str(dondurma.get('kilit_yolu', ''))
    if not yol.is_file() or sha_bayt(yol.read_bytes()) != dondurma.get('kilit_sha256'):
        raise AcilisHatasi("T1: DONDURMA'daki kilit dosyasi yok ya da sha256'si farkli")
    d_ekler = list(dondurma.get('teknik_ekler') or ())
    try:
        k = kilit_tam(yol, dondurma.get('kilit_commit'), tuple(e['commit'] for e in d_ekler),
                      ('kapi', 'banka_oncesi', 'banka_sonrasi'))
    except kilit.KilitHatasi as e:
        raise AcilisHatasi(f"T1: kilit zinciri dogrulanmadi: {e}") from None
    if k['teknik_ekler'] != [{x: e.get(x) for x in ('sira', 'tur', 'sha256')} for e in d_ekler]:
        raise AcilisHatasi("T1: DONDURMA'daki teknik ek kaydi zincirdeki eklerle ayni degil")
    if k['v1_guncel'] != dondurma.get('v1_guncel'):
        raise AcilisHatasi("T1: guncel V1 test raporu DONDURMA'dakiyle ayni degil")
    return k


def hazirla(mod: str, cikti, acilis_yolu=None, dondurma_yolu=None, mimari: str = None, alici: str = None,
            ek: dict = None, anonim_anahtar=None, tohum: int = None) -> tuple:
    """(tanim, güncel kimlikler, meta). Banka: T1 (DONDURMA) ve ACILIS denetimi; kuru: kimlikler o an hesaplanır,
    anonim anahtar ve alıcı kuru klasöründe (karşılaştırma koşusunda anonim_anahtar ve tohum verilir, 20 k).
    ek: yalnız testler (d_kok, evren, filtre_klasoru, boyut_denetimi)."""
    cikti = Path(cikti)
    guncel = kimlikler()
    if mod == 'banka':
        d_bayt = Path(dondurma_yolu).read_bytes()
        dondurma = json.loads(d_bayt.decode('utf-8'))
        fark = t1_denetimi(dondurma, guncel)
        if fark:
            raise AcilisHatasi(f"T1: DONDURMA ile calisan kod farkli: {fark}")
        if (ek or {}).get('kilit_denetimi', True):                                   # UYGULAMA_EK U2 (21 g)
            kilit_zinciri(dondurma)
        a, a_sha = acilis_oku(acilis_yolu, dondurma, boyut=(ek or {}).get('boyut_denetimi', True))
        if (ek or {}).get('kilit_denetimi', True):                   # §1.4 git_commit: dondurma commit'i uzakta
            import kilit
            try:
                kilit.git_denetimi(dondurma_yolu, a.get('dondurma_commit'))
            except kilit.KilitHatasi as e:
                raise AcilisHatasi(f"T1: DONDURMA commit'i dogrulanmadi (ACILIS dondurma_commit): {e}") from None
        tanim = {'mod': 'banka', 'acilis': a, 'mimari': a['mimari'], 'tohum_banka': dondurma['tohum_banka'],
                 'anonim_anahtar': str(a['anonim_anahtar']), 'alici': dondurma['sifreleme_acik_anahtar']}
        meta = {'dondurma_sha256': sha_bayt(d_bayt), 'acilis_sha256': a_sha}
    elif mod == 'kuru':
        if mimari not in ('A', 'B'):
            raise AcilisHatasi("kuru: mimari A ya da B")
        anahtar = Path(anonim_anahtar) if anonim_anahtar else cikti / 'ANONIM_ANAHTAR.bin'
        if not anahtar.exists():
            if anonim_anahtar:
                raise AcilisHatasi("verilen anonim anahtar dosyasi yok")
            cikti.mkdir(parents=True, exist_ok=True)
            anonim.anahtar_uret(anahtar)
        t = guncel['tohum_banka'] if tohum is None else int(tohum)
        tanim = {'mod': 'kuru', 'mimari': mimari, 'tohum_banka': t, 'anonim_anahtar': str(anahtar),
                 'alici': alici or _kuru_alici(cikti)}
        meta = {'kuru_tohum': t}
    else:
        raise AcilisHatasi("mod banka ya da kuru")
    tanim.update({k: v for k, v in (ek or {}).items() if k not in ('boyut_denetimi', 'kilit_denetimi')})
    return tanim, guncel, meta


def bagla(tanim: dict, veri, r: dict, filtre_rapor: dict) -> dict:
    """Tanıma bağlam kimliklerini yazar (20 g): işçiler bunları yeniden hesaplayıp karşılaştırır."""
    from kalibrasyon.yurutucu import har_paketi
    return dict(tanim, veri_kimligi=r['veri_kimligi'], donem=donem_kur(tanim, veri).json(),
                filtre_tablo_sha256=filtre_rapor['tablo_sha256'], har_sonuc_sha256=har_paketi()[0],
                anonim_anahtar_sha256=sha_bayt(Path(tanim['anonim_anahtar']).read_bytes()))


def damga_farki(a: dict, b: dict) -> dict:
    """İki SONUC_DAMGA'nın (birim adı, düz sha256) karşılaştırması (20 k); şifreli sha ve zaman kullanılmaz."""
    x, y = {r[0]: r[1] for r in a['birimler']}, {r[0]: r[1] for r in b['birimler']}
    return {'ayni': sorted(k for k in x.keys() & y.keys() if x[k] == y[k]),
            'farkli': sorted(k for k in x.keys() & y.keys() if x[k] != y[k]),
            'yalniz_a': sorted(x.keys() - y.keys()), 'yalniz_b': sorted(y.keys() - x.keys())}
