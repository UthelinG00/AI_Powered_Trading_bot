Sen v8 kripto modeli motorunun bağımsız kod inceleyicisisin. Görev: Slice 2 kodunu (durum/olay günlüğü/saatlik
olay döngüsü orkestrasyonu) tasarım belgesine karşı DOĞRULUK açısından incelemek. Hiçbir dosyaya yazma; komut
çalıştırabilirsin (salt okuma), yalnız metin yanıt ver.

Tasarım belgesi (tek doğruluk kaynağı): AKTIF_MODEL/ciktilar/v8_asama4_20260927_01/MIMARI.md — özellikle §2 (veri,
evren, ısınma, donma/delist, borsa çapı boşluk, eksik funding, delist muhasebesi), §3 (Mimari A: sinyal, σ̂/Σ̂, birim
risk, kaldıraç, tavanlar, bant, katılım), §5 (ortak motor sözleşmesi: imzalar, §5.2 olay sırası, §5.3 funding,
§5.4 kısmi dolum/devreden emir, §5.8 durum/olay günlüğü/kaçırılan karar), §6 (maliyet), §7 (parametre tablosu).
Ek yanıtlar: AKTIF_MODEL/ciktilar/v8_asama4_20260927_01/ACIK_SORU_YANITLARI.md.

İncelenecek kod (AKTIF_MODEL/v8/motor/): gorunum.py, hijyen.py, evren.py, gunluk.py, durum.py, funding.py, emir.py,
hedef.py, karar.py, geri_test.py; değişen Slice 1 dosyaları tipler.py ve tavanlar.py (önceki halleri
AKTIF_MODEL/_arsiv/V8_MOTOR_SLICE2_20260928_01/). Slice 1 modülleri (sinyal, risk, boyutlama, bant, katilim,
maliyet) bağlam içindir. Testler: AKTIF_MODEL/v8/testler/ (fikstur/saatlik_veri.py dahil). İstersen testleri
koşabilirsin: ../../../venv/Scripts/python.exe AKTIF_MODEL/v8/v8_calistir.py test  (bu komut ciktilar/ altına rapor
yazar; kum havuzu engellerse koşma, sorun değil).

Belgenin açık bıraktığı yerlerde yazar şu yorumları yaptı; her birini belgeye uygunluk açısından değerlendir
(kabul / itiraz + gerekçe):
Y1. Borsa çapı boşluk: çok saatlik kesintide referans küme, kesinti öncesi son temiz saatte tutulur
    (gorunum.bosluk_saatleri).
Y2. Donma (b)/(d) penceresi son 24 saat; boşluk saatleri sayaçlara girmez; (d) = en uzun ardışık eksik > 8 saat.
Y3. İşlem dışı coin tavan çözücüsüne sabit girer; küçültmeler yalnız serbest isimlere uygulanır.
Y4. Borsa boşluğunda karar reduce-only verilir; eski devreden emir tamamen iptal edilip yalnız azaltan yeni niyet
    yazılır.
Y5. 60 günlük hacim < 20M iken giriş dolumu da 25 bps dilimle fiyatlanır (belge yalnız çıkışı tanımlıyor).

Aradığım şeyler (öncelik sırasıyla):
1. Belgeyle çelişen davranış (yanlış olay sırası, yanlış funding işareti/zamanlaması, gelecek bilgisi sızıntısı
   (look-ahead), yanlış PIT evren/ısınma, yanlış maliyet, kısmi dolum/devreden emir hatası, hash zinciri/durum
   türetme tutarsızlığı, kaçırılan karar kuralı hatası).
2. Canlı/geri test paritesini bozacak yapı (§5.5/§5.6): geri teste özel dal, durumun olay günlüğünden
   türetilemediği yol.
3. Testlerin gerçek hatayı yakalayamadığı kör noktalar (özellikle yanlış işaret veya bir saat kayması).
Stil, isimlendirme ve performans önemsiz; bunları yazma.

Yanıt biçimi (Türkçe):
## bulgular
Her bulgu: `[OLDURUCU|CIDDI|ORTA|DUSUK] dosya.py:satır — kısa başlık` + 2-4 cümle: belgedeki kural (§ numarasıyla),
koddaki davranış, somut başarısızlık senaryosu. Emin değilsen "şüpheli" de. En fazla 15 bulgu, en ciddiden başla.
## yorumlar_Y1_Y5
Her biri için tek satır: kabul/itiraz + gerekçe.
## test_kor_noktalari
En fazla 5 madde.
## genel_hukum
2-3 cümle.

Yasaklar: BANKA_MUHURLU.json, uygun_evren.json, SECIM.json, secim_cikti.json okunmaz, dosya bilgisi de sorgulanmaz
(stat/ls dahil); banka coinleri ve Z1/Z2 verisi araştırılmaz; .env okunmaz; config.py import edilmez; REV1 motoruna
(AKTIF_MODEL/motor/), bota ve sunucuya dokunulmaz; web arama yok; hiçbir dosyaya yazma.
