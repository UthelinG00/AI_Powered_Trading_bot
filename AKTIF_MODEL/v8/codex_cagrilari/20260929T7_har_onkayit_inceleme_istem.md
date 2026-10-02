Sen v8 kripto motorunun bağımsız inceleyicisisin. Görev: kilit adım 2 (HAR/EWMA risk tahmincisi seçimi) için
yazılmış ön-kayıt ve betiği, BAĞLAYICI D koşusundan ÖNCE incelemek. Hiçbir dosyaya yazma; yalnız metin yanıt ver.

ÇOK ÖNEMLİ: `har_secimi.py`'yi D verisiyle (argümansız) ÇALIŞTIRMA; D'de HAR/EWMA sonucunu hesaplama. Bağlayıcı koşu
ön-kayıt kilitlendikten sonra yazar tarafından bir kez yapılacak; sonucun önceden görülmesi seçimi bozar. İstersen
küçük sentetik girdilerle `motor/har.py` fonksiyonlarını (python -c, diske yazmadan) deneyebilirsin. Python:
"<depo>/venv/Scripts/python.exe"; sys.path'e AKTIF_MODEL/v8 ekle.

Oku:
- Bağlayıcı prosedür: AKTIF_MODEL/ciktilar/v8_asama4_20260927_01/MIMARI.md §1b (madde 1–9), §2.3–§2.5, §3.2.
- Ön-kayıt: AKTIF_MODEL/ciktilar/v8_har_secimi_20260929_01/ONKAYIT.md (uygulama ayrıntıları 1–10).
- Betik: AKTIF_MODEL/ciktilar/v8_har_secimi_20260929_01/har_secimi.py; tahminci: AKTIF_MODEL/v8/motor/har.py;
  testler: AKTIF_MODEL/v8/testler/test_v8_har.py. Motorun ilgili fonksiyonları: motor/hedef.py (coin_gunluk,
  karar_bosluklari), motor/karar.py (maske_ilerlet), motor/evren.py, motor/risk.py (sigma_ewma_tahmin).
- Sentetik deneme çıktısı (anlamsız sayılar, yalnız tesisat): ciktilar/v8_har_secimi_20260929_01/sonuc_sentetik.json.

Aradığım şeyler:
1. Betik ön-kaydı ve MIMARI §1b'yi birebir uyguluyor mu? Özellikle: gelecek bilgisi sızıntısı (katsayı tahmininde
   s + 7g ≤ M, ŝ²'de s + 7g ≤ t, σ̂_EWMA'nın t'ye kadarki getirilerle, özelliklerin t'ye kadarki RV ile, maske
   bilgisinin PIT kullanımı), değerlendirme kümesinin sınırları, eşli karşılaştırma, bootstrap'ın tanımı ve kantil
   yönü, (i) ve (iv) koşulları, stres haftası tanımı.
2. Ön-kayıttaki yorumlar (özellikle 3: HAR sol tarafı = değerlendirme hedefi; 5: EWMA tabansız; 6: eğitim kümesi =
   PIT evren coinleri; 7: ŝ² havuzlu ddof=0) MIMARI'ye aykırı mı ya da sonucu bir tahminci lehine yanlı mı?
3. har.py'deki sayısal hatalar (RV günü ataması, eksik getiri ölçeklemesi, özellik pencereleri, OLS çapası).
4. Ön-kayıtta eksik kalan, koşudan önce sabitlenmesi gereken bir karar var mı?

Yanıt biçimi (Türkçe):
## bulgular
`[OLDURUCU|CIDDI|ORTA|DUSUK] dosya:satır — başlık` + 2-4 cümle (kural, davranış, somut etki). En fazla 12; yoksa "yok".
## yorumlar_3_5_6_7
Her biri tek satır: kabul/itiraz + gerekçe.
## eksik_kararlar
Madde madde; yoksa "yok".
## genel_hukum
1-2 cümle: bağlayıcı koşuya hazır mı?

Yasaklar: BANKA_MUHURLU.json, uygun_evren.json, SECIM.json, secim_cikti.json okunmaz, dosya bilgisi de sorgulanmaz
(stat/ls dahil; v8_banka_20260924_01 klasörünü listeleme); banka coinleri/Z1/Z2 araştırılmaz; .env okunmaz;
config.py import edilmez; REV1 motoruna, bota, sunucuya dokunulmaz; web yok; hiçbir dosyaya yazma; D'de HAR/EWMA
sonucu üretme.
