"""Kilit Adim 3, 3.12: kalibrasyon raporu taslagi (RAPOR_TASLAK.md) TOPLAMA.json'dan. Yalniz tablolari ve kaniti
mekanik yazar; yorum, kararlarin gerekcesi ve sinirlar bolumu raporu yazan oturumca doldurulur (TASLAK isaretli
bolumler). Hesap yapmaz; TOPLAMA'nin kanit blogunu ve sha256'sini basa yazar.
Kullanim (v8 disindan): python rapor_uret.py -> RAPOR_TASLAK.md"""
import hashlib
import json
import math
import sys
from pathlib import Path

BURASI = Path(__file__).resolve().parent
sys.path.insert(0, str(BURASI.parents[1] / 'v8'))

from kalibrasyon.duzey1 import SR_IZGARASI  # noqa: E402
from kalibrasyon.duzey1_olcut import SEYRELTME  # noqa: E402

TASLAK = '> **TASLAK — raporu yazan oturum doldurur.**'


def _f(x, n=3) -> str:
    if x is None:
        return '—'
    if isinstance(x, bool):
        return 'evet' if x else 'hayır'
    if isinstance(x, int):
        return str(x)
    try:
        v = float(x)
    except (TypeError, ValueError):
        return str(x)
    return '—' if math.isnan(v) else f'{v:.{n}f}'


def _tablo(bas, satirlar) -> list:
    return (['| ' + ' | '.join(bas) + ' |', '|' + '---|' * len(bas)]
            + ['| ' + ' | '.join(s if isinstance(s, str) else _f(s) for s in r) + ' |' for r in satirlar])


def _wilson(t) -> str:
    return '—' if not t else f"{_f(t[0])} [{_f(t[1])}, {_f(t[2])}]"


def uret(toplama: dict, toplama_sha: str) -> str:
    d1 = toplama['duzey1']
    r = d1['rapor']
    L = ['# v8 sentetik kalibrasyon raporu (Adım 3) — TASLAK', '',
         f"TOPLAMA.json sha256: `{toplama_sha}`; durum: **{toplama['durum']}** (Düzey 1: {d1['durum']}; Düzey 2: "
         f"{toplama.get('duzey2', {}).get('durum', '—')}).", '']
    k = toplama.get('kanit', {})
    L += ['## Kanıt zinciri', ''] + _tablo(['alan', 'değer'], [
        ['KOD_DONDURMA sha256', k.get('kod_dondurma_sha256', '—')], ['HAR sonuç sha256', k.get('har_sonuc_sha256', '—')],
        ['betik sha256', k.get('betik_sha256', '—')]] + [[f'kimlik {a}', v] for a, v in (k.get('kimlikler') or {}).items()]
        + [[f'kaynak {a}', json.dumps(v, ensure_ascii=False) if isinstance(v, dict) else v]
           for a, v in (k.get('kaynak') or {}).items()]) + ['']

    L += ['## 1. Düzey 1 kararları (§3.3 kuralları; BANKA §3.7)', '']
    sig = r.get('sigma_sr', {})
    L += _tablo(['alan', 'değer'], [['σ_SR_bağ', sig.get('sigma_sr_bag')], ['σ kaynağı', str(sig.get('kaynak', '—'))],
                                    ['N', r.get('N')]]
                + [[a, v] for a, v in (r.get('kurallar') or {}).items() if a != 'N']) + ['']
    if sig.get('cumle'):
        L += [f"**{sig['cumle']}**", '']
    karar = r.get('karar', {})
    L += ['Karar kaydı (ayar başı kabul oranları TOPLAMA.json içinde; ortalaması aşağıda):', ''] + _tablo(
        ['alan', 'değer'], [[a, json.dumps(v, ensure_ascii=False) if isinstance(v, (dict, list)) else v]
                            for a, v in karar.items() if a != 'kabul_oranlari']) + ['']

    if r.get('p_kabul_A_ort'):
        L += ['### P(KABUL | gerçek SR) — Düzey 1, 128 ayar ortalaması', '']
        L += _tablo(['SR'] + [f'{s:g}' for s in SR_IZGARASI], [['P(KABUL)'] + list(r['p_kabul_A_ort'])]) + ['']
    if r.get('seyreltme'):
        L += ['### B seyreltme (carry katkısı; rapor)', '']
        L += _tablo(['ρ; SR_C'] + [f'{s:g}' for s in SR_IZGARASI],
                    [[a] + list(v) for a, v in r['seyreltme'].items()]) + ['']
    if r.get('b9_gecme_ref'):
        v = list(r['b9_gecme_ref'].values())
        L += [f"B9 geçme oranı (SR = 1,0; ayar ortalaması): {_f(sum(v) / len(v))}", '']
    L += ['### R16 kalem-kâğıt tablosu (η = 1, γ₃ = 0, γ₄ = 3)', '']
    L += _tablo(['T yıl', 'σ_SR', 'SR₀ yıllık', 'd=0,50', 'd=0,75', 'd=0,90', 'd=0,95'],
                [[x['T_yil'], x['sigma_sr'], x['sr0_yillik']] + [x['gereken_sr'][dd] for dd in ('0.5', '0.75', '0.9', '0.95')]
                 for x in r.get('r16', [])]) + ['']

    d2 = toplama.get('duzey2')
    L += ['## 2. Düzey 2 (§3.7 3. revizyon)', '']
    if d2:
        L += ['### 2-a: κ = 0, B7\'siz kabul (tarama kuralı; güven kanıtı değil)', '']
        L += _tablo(['mimari', 'kabul', 'n', 'üst sınırın nokta tahmini', 'Wilson alt', 'Wilson üst', 'tarama geçti'],
                    [[m, v['kabul'], v['n'], v['ust_sinirin_nokta_tahmini'], v['wilson_alt'], v['wilson_ust'],
                      v['tarama_gecti']] for m, v in d2['duzey2a'].items()]) + ['']
        L += ['### 2-b: trendli yollarda B7 gücü (betimsel)', '']
        L += _tablo(['ayar', 'n', 'B7 q90', 'B7 q95', 'taban + B7 q95', 'sıra yüzdeliği ort', 'ortak pay'],
                    [[a, v['n'], _wilson(v['b7_q90']), _wilson(v['b7_q95']), _wilson(v['taban_ve_b7_q95']),
                      v['sira_yuzdeligi_ort'], v['ortak_pay']] for a, v in d2['duzey2b'].items()]) + ['']
    else:
        L += ['Düzey 2 toplanmadı (Düzey 1 kuralları yok: KILIT_BEKLER).', '']

    L += ['## 3. Kararlar ve gerekçe', '', TASLAK, '', '## 4. Sınırlar', '', TASLAK, '',
          '## 5. Görülmüş bilgi', '', TASLAK, '']
    return '\n'.join(L)


def main():
    b = (BURASI / 'TOPLAMA.json').read_bytes()
    metin = uret(json.loads(b.decode('utf-8')), hashlib.sha256(b).hexdigest())
    (BURASI / 'RAPOR_TASLAK.md').write_text(metin, encoding='utf-8')
    print('RAPOR_TASLAK.md yazildi')


if __name__ == '__main__':
    main()
