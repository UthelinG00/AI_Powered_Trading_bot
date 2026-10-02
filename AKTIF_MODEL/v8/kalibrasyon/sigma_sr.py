"""sigma_SR_bag (BANKA_ONKAYIT_TASLAK Ss3.3 kural 1). Bu betik kural yazildiktan sonra ve REV1 kayitlarinin DEGERLERINE
bakilmadan yazildi: yazar yalniz kayit dosyasinin basligini (sutun adlari) ve satir sayisini gordu.

Kaynak: REV1 deneme kaydi `GECMIS/2026_09_19_oncesi/DENEY_TRIAL_REGISTRY.csv` (N_REV1 = 159'un kaynagi). Kural:
kullanilabilir deneme = teknik hata olarak isaretlenmemis, >= 1 yillik gunluk (ya da daha sik) getiriden hesaplanmis yillik
net Sharpe'i olan deneme; >= 30 ise sigma_SR_bag = min(max(std (n - 1); 0,20); 0,50); degilse 0,30 (varsayim).
Deneme basina Sharpe tasimayan bir kayit (aile basina yalniz sayi) kullanilabilirlik kosulunu saglayamaz; betik bunu
sutun adlarindan mekanik olarak belirler ve degerleri okumaz (yalniz sayi tutarliligi icin trial_count toplanir)."""
import csv
from pathlib import Path

SIGMA_VARSAYIM = 0.30
SIGMA_ALT, SIGMA_UST = 0.20, 0.50
MIN_DENEME = 30
N_REV1 = 159
VARSAYIM_CUMLESI = 'σ_SR = 0,30 varsayımdır, doğrulanmadı'
GEREKLI = ('deneme', 'sharpe', 'getiri_gun', 'siklik', 'teknik_hata')     # kavramlar; sutun adinda aranir


def _sutun_var(basliklar, kavram: str) -> bool:
    return any(kavram in b.lower() for b in basliklar)


def sigma_sr_bag(kayit_yolu) -> dict:
    """Doner: {'sigma_sr_bag', 'kaynak': 'REV1' | 'varsayim', 'gerekce', 'basliklar', 'trial_count_toplami', 'cumle'}."""
    yol = Path(kayit_yolu)
    with yol.open(encoding='utf-8', newline='') as f:
        okuyucu = csv.reader(f)
        basliklar = next(okuyucu)
        eksik = [k for k in GEREKLI if not _sutun_var(basliklar, k)]
        sonuc = {'basliklar': basliklar, 'kayit': str(yol).replace('\\', '/')}
        toplam = None
        if 'trial_count' in basliklar:
            i = basliklar.index('trial_count')
            toplam = sum(int(r[i]) for r in okuyucu if len(r) > i and r[i].strip())
        sonuc['trial_count_toplami'] = toplam
    if eksik:
        sonuc.update({'sigma_sr_bag': SIGMA_VARSAYIM, 'kaynak': 'varsayim', 'cumle': VARSAYIM_CUMLESI,
                      'gerekce': f"kayit deneme basina gerekli alanlari tasimiyor (eksik kavramlar: {', '.join(eksik)}); "
                                 f"kullanilabilir deneme sayisi 0 < {MIN_DENEME}"})
        return sonuc
    # Deneme basina Sharpe tasiyan bir kayit bu betigin yazildigi anda bilinmiyordu; semasi incelenmeden okunmaz.
    raise NotImplementedError("deneme basina Sharpe sutunlu kayit: sema tanimi ve inceleme gerekli (Ss3.3 kural 1)")
