Sen v8 kripto motorunun bağımsız kod inceleyicisisin. Kilit Adım 3 (sentetik kalibrasyon) kodu yazıldı; koşudan ve
kod dondurmadan önce incelemeni istiyorum. Tasarım: AKTIF_MODEL/ciktilar/v8_asama4_20260927_01/BANKA_ONKAYIT_TASLAK.md
§3.3, §3.4, §3.5, §3.7 (3. revizyon; T10/T11'de sen incelemiştin). Plan ve durum: AKTIF_MODEL/v8/ILERLEME_KALIBRASYON.md.
Hiçbir dosyaya yazma; yalnız metin yanıt ver. Kodu KOŞMA (testler dahil; D verisi yok ama gerek de yok).

İncelenecek kod (hepsi AKTIF_MODEL/v8 altında):
- banka/olcutler.py, banka/pnl.py, banka/degerlendirme.py (ölçüt kütüphanesi; banka da kullanacak)
- banka/har_banka.py (HAR banka modu; ciktilar/v8_har_secimi_20260929_01/har_secimi.py ve ONKAYIT.md madde 1, 2, 4, 7, 12)
- banka/rejim_null.py (§3.5 null: blok ataması Y1–Y3, getiri uzayında yeniden kurma, N1–N6)
- motor/ayristirma.py yalnız `trend_coin` / `trend_q` eklentisi (önceki hali _arsiv/V8_BANKA_KALIBRASYON_20260929_01/motor/)
- kalibrasyon/tohum.py, duzey2_uretec.py, duzey1.py, duzey1_olcut.py, duzey1_esik.py, sigma_sr.py, duzey1_karar.py,
  birim.py, yurutucu.py, kosucu.py, toplama.py
- ilgili testler: testler/test_v8_banka_*.py, test_v8_har_banka.py, test_v8_rejim_null.py, test_v8_duzey*.py,
  test_v8_kalibrasyon_*.py

Özellikle sına (her biri için EVET/HAYIR/KISMEN + gerekçe):
1. Belgeye uygunluk: Düzey 1 üreteci ve ölçüt eşlemesi (§3.7 tablo), eşik kuralları (e_B5, e_B10, k_B6: ızgara ve "kesin
   küçük" yönleri), §3.3 kural 2–4 sırası (B2 türü, d* araması, tek ayar, kilit bekler), Düzey 2 üreteci formülleri,
   Düzey 2-a ölçüt kümesi (Düzey 1'de bağlayıcı kalanlar) ve 2-b.
2. YORUMLAR (belgenin açık bıraktığı yerler; kabul ya da itiraz et):
   a) B10 ikame hattı ana portföyün ortak faktörünü (u_t) paylaşır (duzey1.py belge dizesi).
   b) Düzey 1 B4: X birim ölçekli; dilim seçimi için X %15 vol'e ölçeklenip Σln(1+x) (duzey1_olcut.py).
   c) B seyreltme raporu sadeleştirmesi (duzey1_olcut.seyreltme_olculeri).
   d) σ_SR_bağ: REV1 kaydı `GECMIS/2026_09_19_oncesi/DENEY_TRIAL_REGISTRY.csv` yalnız aile başına deneme SAYISI
      taşıyor (başlık: registry_id, phase, family, trial_count, included_primary_dsr, note); deneme başına Sharpe yok →
      kural 1 gereği 0,30 "varsayım". Yazar yalnız başlığı gördü. Kaynak tanımı ve bu dal doğru mu? (Dosyanın yalnız
      başlığını okuyabilirsin; değer satırlarına bakmana gerek yok.)
   e) Düzey 2 motor penceresi: motor değerlendirme başında (365. gün) boş defterle başlar; ısınma yılı yalnız geçmiş
      veri olarak görünür (yurutucu.py, sure_olcum.py). Banka §3.1 sürekli koşudan farkı kabul edilebilir mi?
   f) B5 epizot ataması (banka/pnl.epizot_pnl: saatin P&L'i saat başındaki pozisyonun epizotuna; işaret değiştirme saati
      eski epizota), B8 (NAV − gerçek funding nakdi), B10 çıkarma (TamVeri.adaylar'dan çıkar; HAR takvimi yeni aday
      listesiyle yeniden kurulur).
   g) Null yolunda ŝ²'nin null verisinden yeniden kurulması (yurutucu.py).
3. Kesinti/devam ve tekrarlanabilirlik (§3.7): kanonik tohum, birim kimliği (B10'da birincil sha'sı), atomik yazma,
   atlama kuralı, karantina, işçi kimlik denetimi, tek iş parçacığı. Sonucu sıraya, işçi sayısına ya da kesintiye
   bağlayan bir yol var mı? Windows'ta os.replace/fsync ve ProcessPoolExecutor ile bilinen tuzak var mı?
4. Hatalar: indeks/uç durumlar (NaN, inf, boş dilim, T4 değişmez ihlali), PIT/bakış-ileri (HAR banka takvimi, null
   yeniden kurma), sayısal (düz barın bit düzeyinde korunması), ölü kod.
5. Toplama (toplama.py): 2-a satırında B9 etkisiz (+1), 2-b tabanında B3/B10 etkisiz (+inf / 0 düşüş) — doğru mu?

Yanıt biçimi (Türkçe):
## bulgular
Her bulgu: `[OLDURUCU|CIDDI|ORTA|DUSUK] başlık — dosya:satır — sorun — önerilen düzeltme` (en fazla 12; yoksa "yok").
## yorumlar_2a_2g
Her biri tek satır: `KABUL | ITIRAZ — gerekçe (≤35 kelime)`.
## sorular_1_3_4_5
Her biri tek satır: `EVET/HAYIR/KISMEN — gerekçe`.
## genel_hukum
1–2 cümle: kod dondurmaya ve koşuya hazır mı?

Yasaklar: BANKA_MUHURLU.json, uygun_evren.json, SECIM.json, secim_cikti.json okunmaz, dosya bilgisi de sorgulanmaz
(AKTIF_MODEL/ciktilar/v8_banka_20260924_01 klasörünü listeleme); banka coinleri/Z1/Z2 araştırılmaz; D verisi ve ham
zip'ler okunmaz; .env okunmaz; config.py import edilmez; REV1 motoruna, bota, sunucuya dokunulmaz; web yok; hiçbir
dosyaya yazma; kod koşma.
