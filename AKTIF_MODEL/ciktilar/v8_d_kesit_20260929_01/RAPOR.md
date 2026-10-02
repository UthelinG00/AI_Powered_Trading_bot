# v8 D kısa kesit biçim ve özdeşlik denetimi — rapor

Ön-kayıt: `ONKAYIT.md` (sha256 f6c440d038dc76c5dec179d2ee82e0ae0f6c73a7e3d5ad2deb642703c7f07a5a; commit cf2bd21,
koşudan önce). Betik: `kesit_denetim.py`. Çıktılar: `sonuc.json`, `yukleme_raporu.json`. Deneme defteri:
`V8MOTOR-dkesit` (varyant 0). **Sonuç: PASS** (ön-kayıttaki bütün denetimler sağlandı).

Bu denetim performans ölçmez. NAV, getiri, P&L satır toplamları ve hiçbir performans ölçütü hesaplanıp
raporlanmadı (kilit sırası adım 0; MIMARI §10).

## Yükleme (tam D, 122 coin)

| Kalem | Değer |
|---|---|
| Doğrulanan zip (MANIFEST sha256) | 8.345 |
| Veri kimliği | 5907a89bbe56adc0c65a80ad06c9e852b4e7bb58c40b000cab7615e7ddfd23f7 |
| Bar serisi / funding serisi | 122 / 122 |
| Kline satırı / funding satırı | 3.135.362 / 410.950 |
| Atılan satır (tekrar, dönem dışı, µs, sayısal geçersiz, zaman) | 0 |
| Geçersiz OHLC, funding yuvarlama çakışması, aralığı bilinmeyen funding | 0, 0, 0 |
| Süre | 101 s (hash doğrulama + zip okuma) |

Bütün funding kayıtları `funding_interval_hours` taşıyor; ters kayıt kapsamı arşiv aralığıyla belirleniyor (Slice 2'de
belgelenen K2 sınırı D'de oluşmuyor).

## Kısa kesit koşuları (2023-10-01 → 2023-10-07, L = 1, k = 1, NAV0 0,1M)

| Denetim | A | B |
|---|---|---|
| İstisna | yok | yok |
| Günlük zinciri | doğru | doğru |
| Kayıt sayısı (karar / emir niyeti / dolum / funding) | 7 / 53 / 53 / 300 | 7 / 68 / 69 / 521 |
| Günlükten durum paritesi (gün 0, 1 = ilk Pazartesi, 6) | 3/3 | 3/3 |
| Tavan ve T4-d değişmez ihlali olan gün | 0 | 0 |
| Trend evreni boyutu (her gün) | 15 | 15 |
| Carry aday sayısı n_C (ilk Pazartesi) / carry isim sayısı | — | 36 / 17 |
| Ayrıştırma özdeşliği en büyük hata (eşik 1e-8·NAV0 = 1e-3) | — | 1,2e-10 |
| Koşu süresi | 6,0 s | 7,1 s (+ ayrıştırma 2,9 s) |
| Günlüğün son hash'i | a9a13e35… | 1a00f0ae… |

## Gözlem ve sonraki adım
- Kısa kesitte günlük karar + 24 saatlik adım yaklaşık 1 s sürüyor. Ancak birçok hesap (günlük kapanışlar, σ̂,
  korelasyon, maske geçmişi) bütün geçmiş üzerinden yapıldığı için günlük maliyet geçmiş uzadıkça büyüyebilir;
  tam D (1.004 karar günü) süresi bu kesitten doğrusal kestirilemez. Hız, sentetik 122 coinli fikstürle iki geçmiş
  uzunluğunda profillenecek (`ciktilar/v8_hiz_20260929_01/`; D'ye dokunmaz).
- Yükleme 101 s; tam D koşularında bir kez yapılır. Gerekirse veri kimliğine bağlı yerel önbellek eklenebilir.
