"""Banka veri yükleyicisi (6.01b; BANKA §2.3, §3.1; §3.7 netleştirme 19). Adaptör katmanıdır: dosya okur, motor saf kalır.

İki paket:
  (i) banka indirmesi — kök altında `BANKA_MANIFEST.jsonl` (satır {yol, sha256, checksum, durum}; ilk TAMAM satırının
      sha256'sı bağlayıcıdır, netleştirme 17 a), `ham/klines/<sym>/*.zip` (aylık ve Eylül günlük 1h kline),
      `ham/fundingRate/<sym>/*.zip` (aylık), Eylül funding arşivi yoksa `ham/fundingRate_api/<sym>.json` tek anlık
      görüntü [{fundingTime, fundingRate, fundingIntervalHours?}, ...];
  (ii) D paketi — `adaptor.veri_yukleyici.coin_yukle` (mevcut MANIFEST ve hash'ler), yalnız D coinleri ve BTC/ETH,
      yalnız [2023-07-01, 2026-07-01).
Temizlik D yükleyicisiyle aynıdır (başlık algılama, mikrosaniye → ms, sıralama, tekrar eden damgada ilki, sayısal olmayan
satır atılır; kline saat ızgarası ve pozitif fiyat zorunlu; funding damgası en yakın saate, çakışmada ilki). Dönem: ilk
bar → bit_ms (Z2_son, hariç). D coinlerinde banka indirmesinin D penceresine düşen satırları atılır ve sayılır; iki
kaynağın birleşiminde aynı damga iki kez gelirse hata. Veri kimliği: kullanılan her dosyanın "önek/yol sha256"
satırlarının sıralı birleşiminin sha256'sı. Aday listesi dışarıdan (mühürdeki uygun evren + BTC/ETH) verilir.
Netleştirme 20 (i): adayın manifestte TAMAM olup diskte olmayan dosyası hatadır (`eksik_dosyalar`); sembolde
`*-2026-09.zip` funding arşivi varsa API görüntüsü bulunmamalıdır; API görüntüsünden yalnız [2026-09-01, Z2_son) alınır.
"""
import hashlib
import json
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np
import pandas as pd

from adaptor import veri_yukleyici as dv
from motor.gorunum import SAAT_MS, TamVeri, funding_serisi, saatlik_seri

from . import ayar

D_BAS_MS, D_BIT_MS = ayar.D_BAS_MS, ayar.D_BIT_MS
MANIFEST_ADI = 'BANKA_MANIFEST.jsonl'
EYLUL_BAS_MS = ayar._ms(2026, 9, 1)
EYLUL_ARSIV = '-2026-09.zip'


class BankaVeriHatasi(RuntimeError):
    pass


def banka_manifest(kok: Path) -> dict:
    """yol -> bağlayıcı sha256. Onarılamayan satır (T2 (1)) varsa hata: yükleyici T2 kararından sonra çağrılır."""
    from .veri_denetim import checksum_denetimi
    satirlar = [json.loads(s) for s in (Path(kok) / MANIFEST_ADI).read_text(encoding='utf-8').splitlines() if s.strip()]
    cs = checksum_denetimi(satirlar)
    if cs['onarilamayan']:
        raise BankaVeriHatasi(f"manifestte onarilamayan {cs['onarilamayan']} dosya (T2)")
    out = {}
    for r in satirlar:
        if r['durum'] == 'TAMAM':
            out.setdefault(r['yol'], r['sha256'])
    return out


def aday_yollari(sym: str) -> tuple:
    """Adayın manifestteki dosya önekleri (klines, fundingRate klasörleri ve API görüntüsü)."""
    return (f'ham/klines/{sym}/', f'ham/fundingRate/{sym}/', f'ham/fundingRate_api/{sym}.json')


def eksik_dosyalar(kok: Path, manifest: dict, adaylar) -> list:
    """Manifestte TAMAM olup diskte bulunmayan aday dosyaları (20 i; onarılamayan hata)."""
    onekler = tuple(o for c in adaylar for o in aday_yollari(c))
    return sorted(y for y in manifest if y.startswith(onekler) and not (Path(kok) / y).is_file())


def _temizle(df: pd.DataFrame, kol: str, bas_ms: int, bit_ms: int, rapor: dict, haric=None) -> pd.DataFrame:
    df = df.copy()
    df[kol] = pd.to_numeric(df[kol], errors='coerce')
    rapor['gecersiz_zaman'] = rapor.get('gecersiz_zaman', 0) + int(df[kol].isna().sum())
    df = df.dropna(subset=[kol])
    mikro = df[kol] > 1e14
    rapor['mikrosaniye'] = rapor.get('mikrosaniye', 0) + int(mikro.sum())
    df.loc[mikro, kol] = (df.loc[mikro, kol] / 1000).round()
    df[kol] = df[kol].astype('int64')
    df = df.sort_values(kol, kind='mergesort')
    disi = ~df[kol].between(bas_ms, bit_ms - 1)
    rapor['donem_disi'] = rapor.get('donem_disi', 0) + int(disi.sum())
    df = df.loc[~disi]
    if haric is not None:
        h = df[kol].between(haric[0], haric[1] - 1)
        rapor['d_penceresi_atilan'] = rapor.get('d_penceresi_atilan', 0) + int(h.sum())
        df = df.loc[~h]
    tekrar = df.duplicated(kol, keep='first')
    rapor['tekrar'] = rapor.get('tekrar', 0) + int(tekrar.sum())
    return df.loc[~tekrar].reset_index(drop=True)


def _kline_df(df: pd.DataFrame, sym: str, rapor: dict) -> pd.DataFrame:
    for k in ('open', 'high', 'low', 'close', 'quote_volume'):
        df[k] = pd.to_numeric(df[k], errors='coerce')
    nan = df[['open', 'high', 'low', 'close', 'quote_volume']].isna().any(axis=1)
    rapor['sayisal_gecersiz'] = rapor.get('sayisal_gecersiz', 0) + int(nan.sum())
    df = df.loc[~nan].reset_index(drop=True)
    if (df['open_time'] % SAAT_MS != 0).any():
        raise BankaVeriHatasi(f"{sym}: saat izgarasinda olmayan kline acilisi")
    if (df['close'] <= 0).any() or (df['open'] <= 0).any():
        raise BankaVeriHatasi(f"{sym}: sifir ya da negatif fiyat")
    return df


def _funding_df(df: pd.DataFrame, rapor: dict) -> pd.DataFrame:
    df['last_funding_rate'] = pd.to_numeric(df['last_funding_rate'], errors='coerce')
    df['funding_interval_hours'] = pd.to_numeric(df['funding_interval_hours'], errors='coerce')
    nan = df['last_funding_rate'].isna()
    rapor['oran_gecersiz'] = rapor.get('oran_gecersiz', 0) + int(nan.sum())
    df = df.loc[~nan].reset_index(drop=True)
    df['calc_time'] = ((df['calc_time'] + SAAT_MS // 2) // SAAT_MS) * SAAT_MS
    cak = df.duplicated('calc_time', keep='first')
    rapor['yuvarlama_cakismasi'] = rapor.get('yuvarlama_cakismasi', 0) + int(cak.sum())
    return df.loc[~cak].reset_index(drop=True)


@dataclass
class BankaCoinRaporu:
    klines: dict = field(default_factory=dict)
    funding: dict = field(default_factory=dict)
    d_paketi: bool = False


def _banka_parcalari(kok: Path, sym: str, manifest: dict, bas_ms: int, bit_ms: int, haric, rapor: BankaCoinRaporu,
                     kullanilan: list, dogrula: bool):
    def dogrulanmis(yol: Path):
        goreli = yol.relative_to(kok).as_posix()
        beklenen = manifest.get(goreli)
        if beklenen is None:
            raise BankaVeriHatasi(f"manifestte TAMAM kaydi olmayan dosya: {goreli}")
        if dogrula and dv._sha256_dosya(yol) != beklenen:
            raise BankaVeriHatasi(f"sha256 uyusmuyor: {goreli}")
        kullanilan.append((f'banka/{goreli}', beklenen))
    kd = sorted((kok / 'ham' / 'klines' / sym).glob('*.zip')) if (kok / 'ham' / 'klines' / sym).is_dir() else []
    kl = None
    if kd:
        parca = []
        for y in kd:
            dogrulanmis(y)
            parca.append(dv._zip_csv(y, dv.KLINES_KOLONLAR))
        kl = _kline_df(_temizle(pd.concat(parca, ignore_index=True), 'open_time', bas_ms, bit_ms, rapor.klines, haric),
                       sym, rapor.klines)
    fd = sorted((kok / 'ham' / 'fundingRate' / sym).glob('*.zip')) if (kok / 'ham' / 'fundingRate' / sym).is_dir() else []
    parca = []
    for y in fd:
        dogrulanmis(y)
        parca.append(dv._zip_csv(y, dv.FUNDING_KOLONLAR))
    api = kok / 'ham' / 'fundingRate_api' / f'{sym}.json'
    if api.exists():
        if any(y.name.endswith(EYLUL_ARSIV) for y in fd):
            raise BankaVeriHatasi(f"{sym}: Eylul funding icin hem arsiv hem API goruntusu var")
        dogrulanmis(api)
        kayit = [r for r in json.loads(api.read_text(encoding='utf-8')) if int(r['fundingTime']) >= EYLUL_BAS_MS]
        parca.append(pd.DataFrame({'calc_time': [r['fundingTime'] for r in kayit],
                                   'funding_interval_hours': [r.get('fundingIntervalHours') for r in kayit],
                                   'last_funding_rate': [r['fundingRate'] for r in kayit]}))
        rapor.funding['api_goruntusu'] = True
    fn = None
    if parca:
        fn = _funding_df(_temizle(pd.concat(parca, ignore_index=True), 'calc_time', bas_ms, bit_ms, rapor.funding, haric),
                         rapor.funding)
    return kl, fn


def _birlestir(a: pd.DataFrame, b: pd.DataFrame, kol: str, sym: str) -> pd.DataFrame:
    parca = [x for x in (a, b) if x is not None and len(x)]
    if not parca:
        return None
    df = pd.concat(parca, ignore_index=True).sort_values(kol, kind='mergesort')
    if df[kol].duplicated().any():
        raise BankaVeriHatasi(f"{sym}: iki kaynakta ayni damga ({kol})")
    return df.reset_index(drop=True)


def _d_df(seri, fon):
    kl = None if seri is None else pd.DataFrame({'open_time': seri.acilis_ms, 'open': seri.acilis, 'high': seri.yuksek,
                                                'low': seri.dusuk, 'close': seri.kapanis, 'quote_volume': seri.hacim})
    fn = None if fon is None else pd.DataFrame({
        'calc_time': fon.damga_ms, 'last_funding_rate': fon.oran,
        'funding_interval_hours': fon.aralik_saat if fon.aralik_saat is not None else np.full(len(fon.damga_ms), np.nan)})
    return kl, fn


def banka_veri_yukle(banka_kok, d_kok, adaylar, d_coinleri, bit_ms: int = ayar.Z2_SON_MS, bas_ms: int = 0,
                     dogrula: bool = True) -> tuple:
    """(TamVeri, rapor). adaylar: uygun evren + BTC/ETH (açılışta mühürden); d_coinleri: D paketinden D dönemi alınan
    semboller (D coinleri ve BTC/ETH)."""
    banka_kok = Path(banka_kok)
    manifest = banka_manifest(banka_kok)
    if eksik_dosyalar(banka_kok, manifest, adaylar):
        raise BankaVeriHatasi("manifestte TAMAM olan dosya diskte yok")
    d_manifest = dv.manifest_tamam(Path(d_kok)) if d_coinleri else {}
    if d_coinleri and eksik_dosyalar(d_kok, d_manifest, sorted(d_coinleri)):              # 20 l (3)
        raise BankaVeriHatasi("D manifestinde TAMAM olan dosya diskte yok")
    barlar, funding, raporlar, kullanilan = {}, {}, {}, []
    for sym in sorted(set(adaylar)):
        r = BankaCoinRaporu(d_paketi=sym in d_coinleri)
        haric = (D_BAS_MS, D_BIT_MS) if sym in d_coinleri else None
        kl, fn = _banka_parcalari(banka_kok, sym, manifest, bas_ms, bit_ms, haric, r, kullanilan, dogrula)
        if sym in d_coinleri:
            seri, fon, _, dosyalar = dv.coin_yukle(Path(d_kok), sym, d_manifest, dogrula)
            kullanilan.extend((f'd/{y}', h) for y, h in dosyalar)
            dk, dfn = _d_df(seri, fon)
            kl, fn = _birlestir(kl, dk, 'open_time', sym), _birlestir(fn, dfn, 'calc_time', sym)
        if kl is not None and len(kl):
            barlar[sym] = saatlik_seri(kl['open_time'].to_numpy(np.int64), kl['open'].to_numpy(float),
                                       kl['high'].to_numpy(float), kl['low'].to_numpy(float), kl['close'].to_numpy(float),
                                       kl['quote_volume'].to_numpy(float))
        if fn is not None and len(fn):
            funding[sym] = funding_serisi(fn['calc_time'].to_numpy(np.int64), fn['last_funding_rate'].to_numpy(float),
                                          fn['funding_interval_hours'].to_numpy(float))
        raporlar[sym] = r.__dict__
    ozet = '\n'.join(f'{y} {h}' for y, h in sorted(kullanilan)).encode('utf-8')
    veri = TamVeri(barlar=barlar, funding=funding, adaylar=tuple(sorted(set(adaylar))))
    return veri, {'veri_kimligi': hashlib.sha256(ozet).hexdigest(), 'dosya_sayisi': len(kullanilan),
                  'sembol': len(raporlar), 'coin': raporlar}
