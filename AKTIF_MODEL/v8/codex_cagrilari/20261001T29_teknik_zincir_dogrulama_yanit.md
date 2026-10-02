## kapanis

Yollar `AKTIF_MODEL` altındadır; doğrulama statiktir, kod/test çalıştırılmadı ve dosya yazılmadı.

- **T28 CIDDI-1 — KISMEN:** Kalibrasyon çatışması ayrı V1 yoluyla giderilmiş ve kapı bağlanmış; banka girişi zinciri doğrulamıyor (`v8/kilit.py:428`, `v8/kapi/kosu.py:255`, `v8/banka_kos/acilis.py:306`).
- **T28 CIDDI-2 — KISMEN:** Değişmezler ve uzak commit denetimleri eklenmiş; ardışık ekler arasında defterin yalnız sona büyümesi korunmuyor (`v8/kilit.py:435`, `:498`, `:528`).
- **T28 ORTA — KAPANDI:** Banka öncesi/sonrası için ayrı birer hak tanımlanmış (`v8/kilit.py:82`, `:468`).
- **T28 DUSUK — KAPANDI:** Duyarlılığın arşivsel kilit statüsü ve ana sonucu ikame etmediği açıklanmış (`ciktilar/v8_kapi_sentetik_20261001/ONKAYIT_OLCEK.md:7`).
- **T27 Ç3 — KISMEN:** Kapının teknik ek yolu mevcut; bankanın teknik yeniden koşusu bu zincire bağlanmamış (`v8/kapi/kosu.py:255`, `v8/banka_kos/acilis.py:306`).
- **T27 B1 — KAPANDI:** Sayısal hak ayrımı belgeyle kodda uyumlu (`ciktilar/v8_asama4_20260927_01/BANKA_ONKAYIT_TASLAK.md:1087`, `v8/kilit.py:82`).

## yeni_bulgular

- **[CIDDI] Banka bağlantısı eksik — `v8/banka_kos/acilis.py:306` —** Banka yalnız DONDURMA/T1 denetliyor; revizyonun zorunlu kıldığı ek zinciri ve uzak commit kontrolü yok — Banka girişine zincir doğrulaması bağlanmalı.
- **[ORTA] Önceki ekin defter satırı değiştirilebilir — `v8/kilit.py:445`, `:510` —** İkinci ekte ilk kilidin baş kısmını ve toplam satır sayısını koruyarak birinci ekin satırı değiştirilebilir — Her ekin defter hash’i sonraki defterin satır sınırındaki baş kısmıyla eşleştirilmeli.
- **[ORTA] Hak türü koşu aşamasına bağlanmıyor — `v8/kilit.py:503`, `v8/kapi/kosu.py:255` —** Kapı, banka türündeki ekleri de kabul ederek farklı tür adlarıyla ek teknik koşulara izin verebilir — Çağıran aşama ve izin verilen tür geçişleri doğrulanmalı.

## genel_hukum

**Evet, KILIT için banka bağlantısı ve teknik ek zincirinin bütünlük/yetki denetimleri engel olarak kalıyor.**