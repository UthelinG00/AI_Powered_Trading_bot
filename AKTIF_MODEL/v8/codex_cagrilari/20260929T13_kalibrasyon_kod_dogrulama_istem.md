Sen v8 kripto motorunun bağımsız kod inceleyicisisin. T12 incelemende (AKTIF_MODEL/v8/codex_cagrilari/
20260929T12_kalibrasyon_kod_inceleme_yanit.md) kalibrasyon kodunda 3 CIDDI, 7 ORTA, 1 DUSUK bulgu verdin ve yorum (c) ile
(e)'ye itiraz ettin. Yazar düzeltmeleri dört commit'te yaptı (git log: "P14a" … "P14d") ve ön-kayda uygulama
netleştirmeleri ekledi. Görev: YALNIZ bu düzeltmeleri doğrulamak ve yeni bir sorun getirip getirmediklerine bakmak.
Hiçbir dosyaya yazma; yalnız metin yanıt ver. Kod koşma.

Oku:
- Değişiklikler: `git diff d755cd7 48134fa -- AKTIF_MODEL/v8 AKTIF_MODEL/ciktilar/v8_asama4_20260927_01/BANKA_ONKAYIT_TASLAK.md`
  (git komutlarını salt okunur kullanabilirsin).
- AKTIF_MODEL/v8/ILERLEME_KALIBRASYON.md (P14a–d günlük satırları).
- BANKA_ONKAYIT_TASLAK.md §0.2 madde 7, §3.7 sonu "Uygulama netleştirmeleri", Ek C T12 satırı.

Özellikle:
- T12-1: banka/pnl.py `bolus`, eski/yeni payları, `epizot_pnl`; motor/ayristirma.py trend_eski/trend_yeni. Özdeşlik
  (eski + yeni = saatlik P&L) her durumda korunuyor mu? Uzlaşma, tam kapanış (tam_kapanis_son) ve geç funding doğru mu?
- T12-2: ayristirma sıralı dolaşım; test_v8_kalibrasyon_kapilar'daki PYTHONHASHSEED testi yeterli mi?
- T12-3: yurutucu.muhasebe_kapisi her birim türünde çağrılıyor mu; tolerans uygun mu?
- T12-4…11 ve yorum (c), (e) düzeltmeleri.
- Uygulama netleştirmeleri metni kodla tutarlı mı; bir yorumu ön-kayıtta eksik ya da farklı mı yazılmış?

Yanıt biçimi (Türkçe):
## dogrulama
T12-1 … T12-11 ve yorum-c, yorum-e: her biri tek satır `KAPANDI | KISMEN | ACIK — gerekçe (≤25 kelime)`.
## yeni_bulgular
En fazla 5, `[CIDDI|ORTA|DUSUK] başlık — dosya:satır — sorun — düzeltme`; yoksa "yok".
## genel_hukum
1 cümle: kod dondurmaya ve duman denetimine hazır mı?

Yasaklar: BANKA_MUHURLU.json, uygun_evren.json, SECIM.json, secim_cikti.json okunmaz, dosya bilgisi de sorgulanmaz
(AKTIF_MODEL/ciktilar/v8_banka_20260924_01 klasörünü listeleme); banka coinleri/Z1/Z2 araştırılmaz; D verisi ve ham
zip'ler okunmaz; .env okunmaz; config.py import edilmez; REV1 motoruna, bota, sunucuya dokunulmaz; web yok; hiçbir
dosyaya yazma; kod koşma.
