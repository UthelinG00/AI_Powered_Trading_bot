# Doğrulama kılavuzu

Aşağıdaki komutlar **depo kökünden** (README.md'nin bulunduğu klasör) başlar; Linux/macOS sözdizimi (Windows'ta
`venv/bin/python` yerine `venv\Scripts\python.exe`).

## Ortam

Python **3.12.14**, numpy **2.5.1**, pandas **3.0.5**, cryptography **50.0.0** (kilitteki ortam; farklı sürümler kimlik
denetimini bozar ve son haneye kadar aynı sayıları vermeyebilir).

```bash
python3.12 -m venv venv
venv/bin/pip install numpy==2.5.1 pandas==3.0.5 python-dateutil==2.9.0.post0 six==1.17.0 tzdata==2026.3 cryptography==50.0.0
```

## 1. Hash zinciri — veri ve git gerektirmez (önce bunu yapın)

```bash
venv/bin/python dogrula.py
```

Kilitteki 29 belge (defter yalnız sona ekleme kuralıyla), teknik ek, kod/parametre kimlikleri, dondurma, kapı, kuru koşu,
banka açık grubu, banka veri manifesti, DENETIM_TAMAM ve hüküm girdileri/çıktıları. Beklenen son satır:
`… denetim geçti` ve çıkış kodu 0.

## 2. Testler

```bash
cd AKTIF_MODEL/v8 && ../../venv/bin/python v8_calistir.py test; cd ../..
```

59 test dosyası, çoğu sentetik fikstürle. Koşu `AKTIF_MODEL/v8/ciktilar/test_*/sonuc.json` raporu yazar.
Beklenen sonuçlar (yayım öncesi temiz klonda denendi):

- **D verisi olmadan: 57/59.** `test_v8_kilit` ve `test_v8_banka_hukum_dondur` gerçek kilidi doğrular ve ham D
  paketini ister (`ham veri bulunamadi`).
- **D verisi diskteyken: 58/59.** `test_v8_banka_hukum_dondur.KilitTamTest.test_gercek_kilit` bilerek kalır: defterde
  hükümden sonra (karar B) 24. satır eklendi; teknik ek 23 satırlık defteri bağlar.
- **Defter teknik ekteki hâline (ilk 23 kayıt) indirilip daha yeni test raporu yokken: 59/59** (bu test de geçer).

Projenin kendi zincir doğrulaması (3) en yeni test raporuna bakar; testleri koştuktan sonra yeni rapor ekin V1'inden
farklıdır ve o doğrulama bilerek durur. `dogrula.py` bunların hiçbirinden etkilenmez.

## 3. Projenin kendi kilit doğrulaması (isteğe bağlı)

D paketinin diskte olmasını (`AKTIF_MODEL/ciktilar/v8_veri_20260924_01/ham/`, bkz. 4) ve defterin teknik ekteki hâlini
(ilk 23 satır; hükümden sonra karar B gereği 24. satır eklendi) ister:

```bash
cd AKTIF_MODEL/v8 && ../../venv/bin/python -c "
from banka_kos import acilis as A
A.kilit_tam(A.AKTIF / 'ciktilar/v8_kilit_20261001/KILIT.json', '71cf576f50722a7ef7580ba03f757780014df40a',
            ['4666db25cce22e1545639442fdbf33166cb936a1'], ('kapi', 'banka_oncesi'), git=False); print('tamam')"; cd ../..
```

`git=True` doğrulaması özgün özel depodaki uzak commit'leri ister; bu depoda yapılamaz (`ZAMAN_CIZELGESI.md`).

## 4. Veri

Kaynak: Binance kamu veri arşivi (https://data.binance.vision). Her dosya manifestteki sha256 ile doğrulanmalı.

- D paketi: `AKTIF_MODEL/ciktilar/v8_veri_20260924_01/MANIFEST.jsonl` (yol, sha256) ve `indir.py`.
- Banka: `AKTIF_MODEL/ciktilar/v8_banka_acilis_20261002/BANKA_MANIFEST.jsonl` (her dosya için URL, bayt, sha256,
  checksum; 19.766 dosya) ve `liste.jsonl`; betikler `indirme_listesi.py`, `banka_indir.py`. Arşiv sonradan değişirse
  yeniden indirilen dosya manifestteki sha256'yla tutmaz; bu, bilerek böyle tasarlandı.

## 5. Bankanın yeniden üretimi

`AKTIF_MODEL/ciktilar/v8_banka_20260924_01/`: `DAMGA.json` hedef drand turunu (6492331, zincir `8990e7a9…`) verir.
Turun BLS imzası drand'dan (https://api.drand.sh) alınıp zincir anahtarıyla doğrulanır; randomness = sha256(imza).
`banka_sec.py` (sha256 `757ef3c9…`) Python 3.12'de çalıştırılır; çıktıların hash'leri `SECIM.json` ile aynı olmalı
(BANKA ön-kaydı §2.2).

## 6. Hüküm

`AKTIF_MODEL/ciktilar/v8_banka_kosu_20261002/hukum/HUKUM_KIMLIK.json` girdilerin (DONDURMA, ACILIS, DENETIM_TAMAM,
VERI_DENETIM, TOPLAMA, damga kökü) ve çıktıların sha256'larını taşır. Çözülmüş sonuç `banka_sonuc.json` ve rapor
`BANKA_RAPORU.md` yayımlandı; şifreli birim dosyaları yayımlanmadı. ACILIS kanonik biçimde (`ACILIS_kanonik.json`)
yayımlandı; hüküm bu dosyayla açıldı (bkz. `SONUC.md`, teknik notlar).
