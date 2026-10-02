# v8 D kısa kesit biçim ve özdeşlik denetimi — ön-kayıt

Tarih: 2026-09-29 (koşudan ÖNCE yazıldı). Kilit sırası: MIMARI §10 adım 0 ("D verisi yalnız metrik hesaplanmayan
kısa kesitlerle, biçim ve özdeşlik denetimi"). Ön-kayıt kilidi (adım 4) henüz yok; bu koşu P&L/performans
ölçütü üretmez ve raporlamaz.

## Amaç
1. `adaptor/veri_yukleyici.py`'nin gerçek D arşivini (122 coin, 2023-07 → 2026-06) hash doğrulamasıyla ve motor
   sözleşmesine uygun okuduğunu göstermek.
2. Motorun gerçek veri biçiminde (funding aralık geçişleri, eksik saatler, sıfır hacim, delist) teknik hata vermeden
   çalıştığını; olay günlüğü zincirinin, günlükten durum kurulumunun ve B ayrıştırma özdeşliğinin tuttuğunu göstermek.
3. Hız: gerçek veri boyutunda bir günlük karar ve saatlik adımın süresini ölçmek (tam D koşusunun süresini kestirmek
   için). Hız ölçümü çıktısı yalnız süredir.

## Girdi ve ayarlar (sabit)
- Veri: ana depodaki `AKTIF_MODEL/ciktilar/v8_veri_20260924_01/ham/` ve MANIFEST.jsonl (sha256 5eabe360…),
  aday listesi GELISTIRME_EVRENI.json (sha256 343dead4…). Veri kimliği yükleme raporuna yazılır.
- Motor: commit b1954e8 sonrası v8/motor (kimlik 53eec265…) + adaptor/veri_yukleyici.py.
- Kesit: T0 = 2023-10-01 00:00 UTC, son saat 2023-10-07 23:00 UTC (7 gün; ilk Pazartesi 2023-10-02 dahil).
  Isınma verisi 2023-07-01'den itibaren görünümde vardır (MIMARI §2.4).
- İki koşu: Mimari A ve Mimari B; L = 1, maliyet_k = 1, NAV0 = 100.000 USDT, katılımlı, filtreler boş (MIMARI §5.1
  varsayılanı).

## Hesaplanan ve raporlanan (yalnız biçim/özdeşlik/süre)
- Yükleme raporu: coin başına satır, atılan (tekrar, dönem dışı, mikrosaniye, sayısal geçersiz), funding aralığı
  bilinmeyen kayıt, yuvarlama çakışması sayıları; veri kimliği; dosya sayısı.
- Her koşu için: istisna olmaması; `gunluk.dogrula()`; kayıt türü adetleri; evren boyutu ve (B) carry aday sayısı n_C
  günlük; üç kararda (ilk gün, ilk Pazartesi, son gün) günlükten kurulan durumla aynı karar (parite); her kararda
  nihai kitabın tavan ve T4-d değişmezleri (sağlandı/sağlanmadı); B için ayrıştırma özdeşliğinin en büyük hatası
  (eşik 1e-8·NAV0); günlüğün son hash'i; süre.

## Hesaplanmayan / raporlanmayan
NAV, getiri, P&L satır toplamları, Sharpe, MDD, isabet ya da herhangi bir performans ölçütü. Betik bunları
yazdırmaz ve diske yazmaz. Ayrıştırma sonucundan yalnız özdeşlik hatası okunur.

## Kabul
Bütün denetimler sağlanırsa PASS. Sağlanmazsa hata yükleyicide ya da motorda aranır; düzeltme yalnız sentetik
fikstürle gösterilen hata için yapılır (MIMARI §10), parametre değişmez. Sonuç RAPOR.md'ye yazılır.

## Deneme defteri
`V8MOTOR-dkesit` satırı koşudan önce eklenir (varyant 0; performans üretmez).
