"""BANKA_RAPORU.md üreteci (BANKA §8.2 şablonu; 6.09; Codex T21 → netleştirme 17 h, i). Girdi: hüküm sözlüğü
(`hukum.hukum`), rapor satırları (`rapor.rapor_satirlari`; %90 GA tablosu 'GA' dahil), birincil metrikler ve açılışta
toplanan bağlam (hash'ler, hüküm türü, veri denetimi, kalibrasyon ve teknik özetleri). Hesap yapmaz; sayıları biçimler ve
zorunlu cümleleri (§3.3, §4, §5.5, K2-02) aynen yazar.

Coin adı (§8.1): rapor BTC/ETH dışında sembol yazmaz. Serbest metin taşıyabilen bağlam alanları (dosya adları, teknik,
kalibrasyon, düzeltme ve veri denetimi sözlükleri) ve son metin `[A-Z0-9]{2,}USDT` biçimli dizge için denetlenir;
BTCUSDT/ETHUSDT dışında bulunursa hata (netleştirme 17 i).
"""
import json
import math
import re

import numpy as np

from . import kelly
from .hukum import _birim, gunluk_getiri

CUMLE_SIGMA_VARSAYIM = "σ_SR = 0,30 varsayımdır, doğrulanmadı"
CUMLE_DSR = ("DSR bir performans çıtasıdır; birleşik yanlış kabul §3.7'de ölçüldü (B7 dahil olanı için üst sınırın "
             "nokta tahmini ve Wilson aralığı)")
CUMLE_KELLY_BOS = kelly.BOS_CUMLE
CUMLE_ORNEKLEM_ICI = ("Seçilen L'nin DD değerleri banka örnekleminin içindedir; 𝓛*'ı banka örnekleminden seçmek seçim "
                      "yanlılığı taşır. Demo ön-kaydı DD beklentisini bootstrap q95 ile yazar; bu iyimser olabilir.")
CUMLE_YENIDEN_ORNEKLEME = ("Blok bootstrap geçmiş getirileri yeniden örnekler. Marjin çağrısı, otomatik kaldıraç azaltma "
                           "(ADL), tasfiye ve bankada gerçekleşmemiş kuyruk olaylarını üretmez. %30 DD sınırı hiçbir L "
                           "için garanti edilemez.")
CUMLELER_HAYATTA_KALAN = ("Hayatta kalan yanlılığı giderilmedi.",
                          "B2 (DSR) ve birincil Sharpe hayatta kalan yanlılığına göre düzeltilmedi.",
                          "D90, SQ ve DM tek kanallı stres bindirmeleridir; hayatta kalan yanlılığının üst sınırı değildir.")
CUMLE_B_FIYAT = "B, fiyattan gelmediği gösterildi demek değildir."
SINIRLAR = ("asimetrik güç", "korelasyonlu kesit", "hayatta kalan yanlılığı",
            "mark vekili (uzlaşma damgası T için [T−1h, T) barının kapanışı; MIMARI §2.1)", "ADL/marjin modellenmedi",
            "tarihsel sembol filtresi yok", "B'nin funding/fiyat ayrımının gücü düşük")
HUKUM_TURLERI = ('KABUL', 'RET', 'TEKNİK GEÇERSİZ', 'NOT_EVALUATED')
SEMBOL = re.compile(r'[A-Z0-9]{2,}USDT')
IZINLI_SEMBOL = {'BTCUSDT', 'ETHUSDT'}
STRES_SUTUNLARI = ('D90-1', 'D90-2', 'D90-4', 'SQ-1', 'SQ-2', 'SQ-4', 'DM-1')


class RaporHatasi(ValueError):
    """Hüküm türü geçersiz ya da rapora coin adı sızacak."""


def sembol_denetimi(metin: str, yer: str):
    bulunan = sorted(set(SEMBOL.findall(metin)) - IZINLI_SEMBOL)
    if bulunan:
        raise RaporHatasi(f"{yer}: rapora coin adi sizacak ({len(bulunan)} sembol)")


def _f(x, n: int = 3) -> str:
    if x is None:
        return '—'
    if isinstance(x, bool):
        return 'evet' if x else 'hayır'
    if isinstance(x, (int, np.integer)):
        return str(int(x))
    try:
        v = float(x)
    except (TypeError, ValueError):
        return str(x)
    if math.isnan(v):
        return '—'
    if math.isinf(v):
        return '∞' if v > 0 else '−∞'
    return f'{v:.{n}f}'


def _ga(g) -> str:
    return '—' if not g else f"[{_f(g.get('q05'))}, {_f(g.get('q95'))}]"


def _tablo(basliklar, satirlar) -> list:
    out = ['| ' + ' | '.join(basliklar) + ' |', '|' + '---|' * len(basliklar)]
    out += ['| ' + ' | '.join(_f(h) if not isinstance(h, str) else h for h in s) + ' |' for s in satirlar]
    return out


def _sozluk_tablosu(d: dict, anahtar='satır') -> list:
    """{ad: {alan: değer}} ya da {ad: değer} sözlüğünü tabloya çevirir (iç içe sözlük/liste alanları atlanır)."""
    if not d:
        return ['—']
    if all(isinstance(v, dict) for v in d.values()):
        alanlar = sorted({a for v in d.values() for a in v if not isinstance(v[a], (dict, list))})
        return _tablo([anahtar] + alanlar, [[str(k)] + [v.get(a) for a in alanlar] for k, v in d.items()])
    return _tablo([anahtar, 'değer'], [[str(k), v] for k, v in d.items() if not isinstance(v, (dict, list))])


def birincil_metrikler(birimler: dict, hb) -> dict:
    b = _birim(birimler, grup='birincil', mimari=hb.mimari)
    r, g = gunluk_getiri(b, hb.t0_z1_ms, hb.birincil_son_ms, hb.gorulmus_gunler)
    return kelly.metrikler(r, g)


def banka_raporu(hukum_sonuc: dict, satirlar: dict, birincil: dict, baglam: dict) -> str:
    """baglam: hukum_turu, mimari, hashler {belge: sha256}, b2_turu ('B'|'R'), sigma_kaynak ('REV1'|'varsayim'),
    N_hukum, stres_secenegi {'secenek', 'hash'}, veri_denetimi (VERI_DENETIM.json sözlüğü), kalibrasyon (Düzey 1/2 güç
    özetleri), teknik (T1–T5 ve denetim listesi), duzeltme (teknik yeniden koşu karşılaştırması ya da None)."""
    tur = baglam['hukum_turu']
    if tur not in HUKUM_TURLERI:
        raise RaporHatasi(f"hüküm türü {tur}")
    for yer in ('hashler', 'veri_denetimi', 'kalibrasyon', 'teknik', 'duzeltme', 'stres_secenegi'):
        sembol_denetimi(json.dumps(baglam.get(yer), ensure_ascii=False, default=str), yer)
    sembol_denetimi(json.dumps(satirlar.get('R4', {}), ensure_ascii=False, default=str), 'R4')
    ol = hukum_sonuc['olcutler']
    GA = satirlar.get('GA', {})
    L = []
    L += ['# v8 Banka Raporu', '', '## 1. Hüküm', '', f"**{tur}** — mimari **{baglam['mimari']}**", '']
    L += _tablo(['belge', 'sha256'], [[k, v] for k, v in baglam['hashler'].items()]) + ['']
    L += [f'- {c}' for c in CUMLELER_HAYATTA_KALAN] + ['']

    L += ['## 2. Bağlayıcı tablo (B2–B11)', '']
    ga_b = {'B3': GA.get('B3_x2'), 'B4': GA.get('B4'), 'B7': GA.get('B7_birincil'), 'B8': GA.get('B8'), 'B9': GA.get('B9')}
    sat = []
    for k in [f'B{i}' for i in range(2, 12)]:
        x = ol[k]
        deger = {'B2': x.get('dsr'), 'B3': x.get('sr_x2'), 'B4': x.get('sr'), 'B5': x.get('pay'), 'B6': x.get('pozitif'),
                 'B7': x.get('sr'), 'B8': x.get('sr'), 'B9': x.get('sr'), 'B10': x.get('en_buyuk_dusus'),
                 'B11': x.get('mdd')}[k]
        esik = {'B2': x.get('d'), 'B3': 0.30, 'B4': x.get('esik'), 'B5': x.get('esik'), 'B6': x.get('k'),
                'B7': x.get('q95'), 'B8': 0.0, 'B9': 0.0, 'B10': x.get('esik'), 'B11': 0.30}[k]
        gecti = x.get('gecti')
        sat.append([k, deger, esik, 'rapor' if gecti is None else ('geçti' if gecti else 'kaldı'), _ga(ga_b.get(k))])
    L += _tablo(['ölçüt', 'değer', 'eşik', 'sonuç', '%90 GA'], sat)
    L += ['', f"B3 ×3 SR {_f(ol['B3'].get('sr_x3'))} (%90 GA {_ga(GA.get('B3_x3'))}); eşik > 0.", '']
    L += ['B6 dilimleri:', ''] + _tablo(['dilim', 'SR', '%90 GA'], [
        [f'Z1 dilim {i + 1}', v, _ga(GA.get(f'B6_dilim{i + 1}'))] for i, v in enumerate(ol['B6']['dilim_sr'])])
    L += ['', f"Karar: **{hukum_sonuc['karar']}**", '']

    r11, r7 = satirlar['R11'], satirlar['R7']
    L += ['## 3. Birincil sonuç', '']
    L += _tablo(['SR (R11)', '%90 GA', 'CAGR', 'vol', 'MDD', 'gerçekleşen vol / birim (R7)'],
                [[r11['sr'], _ga(r11), birincil.get('cagr'), birincil.get('vol'), birincil.get('mdd'),
                  r7.get('gerceklesen_vol_orani')]])
    L += ['', f"SR ≥ 0,50: {_f(r11['esik_ustu'])} (bilgi; eski B1).", '', 'Tahminci tanıları (R7):', '']
    L += _sozluk_tablosu(r7) + ['']

    b2 = ol['B2']
    L += ['## 4. DSR', '', f"B2 türü: **{baglam['b2_turu']}**; d* = {_f(b2.get('d'))}; N_hüküm = {baglam['N_hukum']}; "
          f"SR₀ = {_f(b2.get('sr0'), 5)}; γ₃ = {_f(b2.get('g3'))}; γ₄ = {_f(b2.get('g4'))}; η = {_f(b2.get('eta'))}; "
          f"T = {_f(b2.get('T'))}.", '']
    if baglam.get('sigma_kaynak') == 'varsayim':
        L += [f'**{CUMLE_SIGMA_VARSAYIM}.**', '']
    L += [CUMLE_DSR + '.', '', 'R16 duyarlılık tablosu:', ''] + _sozluk_tablosu(satirlar['R16'], 'σ|N çarpanı|η') + ['']

    L += ['## 5. Rejim dilimleri ve Z2 teşhisi', '', 'Z2 ve D segmenti (R10):', '']
    L += _tablo(['segment', 'SR', '%90 GA', 'CAGR', 'vol', 'MDD', 'gün'],
                [[k, v.get('sr'), _ga(v.get('ga')), v.get('cagr'), v.get('vol'), v.get('mdd'), v.get('gun')]
                 for k, v in satirlar['R10'].items()]) + ['']

    L += ['## 6. Ayrıştırmalar', '', 'Beta ayrıştırması (R2):', ''] + _sozluk_tablosu(
        {k: v for k, v in satirlar['R2'].items() if isinstance(v, dict)}, 'pencere') + ['']
    L += ['Long-beta karşılaştırması (R3):', ''] + _sozluk_tablosu(hukum_sonuc.get('R3', {}))
    L += ['', f"R3 kitabının SR %90 GA: {_ga(GA.get('R3_long_beta'))}", '']
    L += ['REV1 korelasyonu (R4):', ''] + _sozluk_tablosu(satirlar['R4']) + ['']
    if baglam['mimari'] == 'B':
        r8 = satirlar['R8']
        L += ['B ayrıştırması (R8):', ''] + _sozluk_tablosu(r8['satir_yillik'], 'satır (yıllık)') + ['']
        L += _tablo(['bacak', 'SR', '%90 GA'], [['trend', r8['trend_bacagi']['sr'], _ga(r8['trend_bacagi'])],
                                                ['carry', r8['carry_bacagi']['sr'], _ga(r8['carry_bacagi'])]]) + ['']
        L += ['Carry bacağı epizot payı (§3.4 B5 notu):', ''] + _sozluk_tablosu(r8.get('carry_epizot') or {}) + ['']
        L += ['Bağımsız A koşusu:', ''] + _sozluk_tablosu(r8['bagimsiz_A']) + ['']
        L += ['L başına carry betası (K1-09):', ''] + _sozluk_tablosu(r8['kelly_carry_beta'], 'L') + ['']
        L += [CUMLE_B_FIYAT, '']

    L += ['## 7. Görülmemiş coinler (B9, R15)', '']
    L += _tablo(['', 'SR', '%90 GA', 'gün'], [['B9', ol['B9']['sr'], _ga(GA.get('B9')), ol['B9']['gun']],
                                             ['R15 (D, görülmüş zaman)', satirlar['R15']['sr'], _ga(satirlar['R15']),
                                              satirlar['R15']['gun']]]) + ['']

    L += ['## 8. Kelly tablosu', '']
    for m, ks in hukum_sonuc['kelly_stres'].items():
        kt = ks['kelly']
        sat = []
        for Lk, v in sorted(kt['satirlar'].items()):
            st = ks['stres'].get(Lk, {})
            sat.append([f'{Lk:g}', v.get('cagr'), v.get('vol'), v.get('sr'), _ga(GA.get(f'Kelly_{Lk:g}|{int(m)}')),
                        v.get('mdd'), v['bootstrap']['q50'], v['bootstrap']['q95'], v['bootstrap']['p_asim'],
                        v.get('kelly_kesri'), v.get('etiket') or 'uygun'] + [st.get(a, {}).get('mdd')
                                                                             for a in STRES_SUTUNLARI])
        L += [f'Maliyet {m}×:', ''] + _tablo(
            ['L', 'CAGR', 'vol', 'SR', 'SR %90 GA', 'MDD', 'boot q50', 'boot q95', 'P(MDD>%30)', 'Kelly kesri', '%30 DD']
            + [f'MDD {a}' for a in STRES_SUTUNLARI], sat) + ['']
        if int(m) == 1:
            L += [f"𝓛* = {kt['uygun_L']}; varsayılan öneri: {_f(kt['varsayilan_oneri'])}.", '']
            if kt.get('cumle'):
                L += [f"**{CUMLE_KELLY_BOS}**", '']
    L += [CUMLE_ORNEKLEM_ICI, '', f'"{CUMLE_YENIDEN_ORNEKLEME}"', '']

    L += ['## 9. Hayatta kalan yanlılığı', '', 'Kanal stresleri (R12, L = 1):', '']
    L += _tablo(['senaryo', 'SR', '%90 GA', 'MDD', 'olay', 'boş olay'],
                [[k, v.get('sr'), _ga(v.get('ga')), v.get('mdd'), v.get('olay'), v.get('bos_olay')]
                 for k, v in satirlar['R12'].items()]) + ['', 'Delist uzlaşma senaryoları (R9):', '']
    L += _tablo(['h_L', 'SR', '%90 GA', 'MDD', 'CAGR', 'SR farkı', 'gün'],
                [[k, v.get('sr'), _ga(v.get('ga')), v.get('mdd'), v.get('cagr'), v.get('sr_farki'), v.get('gun')]
                 for k, v in satirlar['R9'].items()]) + ['']
    st = baglam['stres_secenegi']
    L += [f"Kilitlenen stres bağlayıcılığı: ({st['secenek']}) — hash {st['hash']}.", '']
    L += [f'- {c}' for c in CUMLELER_HAYATTA_KALAN] + ['']

    L += ['## 10. Maliyet ve kapasite', '', 'NAV × maliyet ızgarası (R1):', '']
    L += _tablo(['NAV|maliyet', 'SR', '%90 GA'], [[k, v, _ga(GA.get(f'R1_{k}'))] for k, v in hukum_sonuc['R1'].items()])
    L += ['', 'Devir ve maliyet (R6):', ''] + _sozluk_tablosu(satirlar['R6']) + ['']
    L += _sozluk_tablosu(satirlar['R6'].get('kapanis_turleri', {}), 'niyet kapanışı') + ['', 'Tavan bağlama ve aşım (R5):', '']
    L += _sozluk_tablosu({k: v for k, v in satirlar['R5'].items() if not isinstance(v, dict)})
    L += [''] + _sozluk_tablosu(satirlar['R5'].get('hedef_baglama_orani', {}), 'tavan') + ['']
    L += ['Lot (R13) ve demo NAV (R14):', ''] + _sozluk_tablosu(
        {'R13': satirlar['R13'], 'R13b': satirlar['R13b'], 'R14': satirlar['R14']})
    L += ['', f"Lot kapalı SR %90 GA: {_ga(GA.get('R13_lot_kapali'))}", '']

    L += ['## 11. Veri ve teknik', '', 'Veri denetimi (T2; VERI_DENETIM.json):', '']
    vd = baglam.get('veri_denetimi') or {}
    duz_vd = {k: v for k, v in vd.items() if not isinstance(v, (dict, list))}
    for alt in ('checksum', 'oranlar', 'coin_eksik_saat'):
        duz_vd.update({f'{alt}.{a}': b for a, b in (vd.get(alt) or {}).items() if not isinstance(b, (dict, list))})
    L += _sozluk_tablosu(duz_vd) + ['', f"T2: {_f((vd.get('karar') or {}).get('T2'))}", '']
    L += _sozluk_tablosu(baglam.get('teknik', {})) + ['']
    if baglam.get('duzeltme'):
        L += ['Teknik yeniden koşu / açılış sonrası düzeltme karşılaştırması:', ''] + _sozluk_tablosu(
            baglam['duzeltme']) + ['']

    L += ['## 12. Güç', '', 'Kalibrasyon (§3.7; "tarama kuralı, güven kanıtı değil"):', '']
    L += _sozluk_tablosu(baglam.get('kalibrasyon', {})) + ['', 'Rejim-null tanıları (R17):', '']
    L += _sozluk_tablosu(satirlar['R17'], 'sayım') + ['']

    L += ['## 13. Sınırlar', ''] + [f'- {s}' for s in SINIRLAR] + [f'- {CUMLE_B_FIYAT}', '']
    metin = '\n'.join(L)
    sembol_denetimi(metin, 'rapor metni')
    return metin
