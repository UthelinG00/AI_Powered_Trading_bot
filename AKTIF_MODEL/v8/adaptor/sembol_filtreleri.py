"""Sembol filtreleri: kamu exchangeInfo tek anlik goruntusu (MIMARI Ss5.1, Ss9 soru 4; BANKA Ss2.3; ACIK_SORU_YANITLARI
#5: salt okuma, anahtarsiz kamu uc noktasi, emir yok).

Alma (bir kez): python -m adaptor.sembol_filtreleri <cikti_dizini>
  -> exchangeInfo_ham.json (yanitin baytlari aynen), SEMBOL_FILTRELERI.json (gelistirme evreni sembolleri icin tablo),
     alinma anı ve iki dosyanin sha256'si (ALINMA.json).
Tablo kurali: adim = max(LOT_SIZE.stepSize, MARKET_LOT_SIZE.stepSize) (motorun dolumlari piyasa emri gibidir; iki adimdan
buyugu her iki kisiti saglar), minNotional = MIN_NOTIONAL.notional. Goruntude olmayan sembol tabloya girmez; motor onlara
varsayilan (adim 0, minNotional 5 USDT) uygular ve sayilari raporlanir.
Kullanim (kosu): filtreler_yukle(yol) -> {sembol: (adim, minNotional)} (KosuAyarlari.filtreler bicimi)."""
import hashlib
import json
import sys
import time
import urllib.request
from pathlib import Path

UC = 'https://fapi.binance.com/fapi/v1/exchangeInfo'


def tablo(ham: dict, semboller) -> dict:
    istenen = set(semboller)
    out = {}
    for s in ham.get('symbols', []):
        ad = s.get('symbol')
        if ad not in istenen:
            continue
        f = {x['filterType']: x for x in s.get('filters', [])}
        adim = max(float(f.get('LOT_SIZE', {}).get('stepSize', 0.0)), float(f.get('MARKET_LOT_SIZE', {}).get('stepSize', 0.0)))
        mn = float(f.get('MIN_NOTIONAL', {}).get('notional', 5.0))
        out[ad] = {'adim': adim, 'min_notional': mn, 'durum': s.get('status'), 'kontrat': s.get('contractType')}
    return out


def filtreler_yukle(yol) -> dict:
    d = json.loads(Path(yol).read_text(encoding='utf-8'))
    return {c: (float(v['adim']), float(v['min_notional'])) for c, v in sorted(d['tablo'].items())}


def al(cikti: Path, semboller) -> dict:
    cikti.mkdir(parents=True, exist_ok=False)                 # tek goruntu: var olan klasorun ustune yazilmaz
    an = time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())
    with urllib.request.urlopen(urllib.request.Request(UC, headers={'User-Agent': 'v8-sembol-filtreleri'}), timeout=60) as r:
        bayt = r.read()
    (cikti / 'exchangeInfo_ham.json').write_bytes(bayt)
    t = tablo(json.loads(bayt), semboller)
    icerik = {'kaynak': UC, 'alinma_utc': an, 'kural': 'adim = max(LOT_SIZE, MARKET_LOT_SIZE stepSize); MIN_NOTIONAL.notional',
              'istenen': len(set(semboller)), 'bulunan': len(t), 'eksik': sorted(set(semboller) - set(t)), 'tablo': t}
    metin = json.dumps(icerik, indent=1, sort_keys=True, ensure_ascii=True)
    (cikti / 'SEMBOL_FILTRELERI.json').write_text(metin, encoding='ascii')
    alinma = {'alinma_utc': an, 'exchangeInfo_ham_sha256': hashlib.sha256(bayt).hexdigest(),
              'SEMBOL_FILTRELERI_sha256': hashlib.sha256(metin.encode('ascii')).hexdigest(),
              'bulunan': len(t), 'eksik_sayisi': len(icerik['eksik'])}
    (cikti / 'ALINMA.json').write_text(json.dumps(alinma, indent=1), encoding='ascii')
    return alinma


if __name__ == '__main__':
    V8 = Path(__file__).resolve().parents[1]
    sys.path.insert(0, str(V8))
    from adaptor.veri_yukleyici import gelistirme_evreni
    print(json.dumps(al(Path(sys.argv[1]), gelistirme_evreni())))
