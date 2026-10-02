Sen v8 kripto motorunun bağımsız inceleyicisisin. T10 incelemende (AKTIF_MODEL/v8/codex_cagrilari/
20260929T10_banka_duzey2_inceleme_yanit.md) BANKA ön-kaydı 3. revizyonunda 1 CIDDI, 3 ORTA, 1 DUSUK bulgu verdin.
Yazar hepsini işledi ve ayrıca Düzey 2'nin motor yapılandırmasını (HAR banka modu) açık yazdı. Görev: YALNIZ bu beş
düzeltmeyi ve yeni "Motor yapılandırması" maddesini doğrulamak, bu değişikliklerin yeni bir sorun getirip getirmediğine
bakmak. Hiçbir dosyaya yazma; yalnız metin yanıt ver. Kod koşma.

Oku: AKTIF_MODEL/ciktilar/v8_asama4_20260927_01/BANKA_ONKAYIT_TASLAK.md — §0.2, §3.7 "Tohum" paragrafı ve Düzey 2
bölümünün tamamı, §8.2 madde 4 ve 12, §10 madde 13 ve 15, Ek C (K2-14, KC-02 satırları ve sondaki "3. revizyon"
tablosu). HAR banka kuralı için: AKTIF_MODEL/ciktilar/v8_har_secimi_20260929_01/ONKAYIT.md madde 7 ve 12. Düzey 1
eşik kuralları için §3.3 kural 2–4 ve §3.7 "Eşik kuralları", "Birleşik yanlış kabul ve güç (Düzey 1)".

Yanıt biçimi (Türkçe):
## dogrulama
T10-1 … T10-5, her biri tek satır: `KAPANDI | KISMEN | ACIK — gerekçe (≤25 kelime)`.
## motor_yapilandirmasi
1–3 satır: HAR banka modu maddesi HAR ön-kaydıyla tutarlı ve Düzey 2 için uygun mu?
## yeni_bulgular
En fazla 3, `[CIDDI|ORTA|DUSUK] başlık — konum — sorun — düzeltme`; yoksa "yok".
## genel_hukum
1 cümle: §3.7 kalibrasyon koduna geçmeye uygun mu?

Yasaklar: BANKA_MUHURLU.json, uygun_evren.json, SECIM.json, secim_cikti.json okunmaz, dosya bilgisi de sorgulanmaz
(v8_banka_20260924_01 klasörünü listeleme); banka coinleri/Z1/Z2 araştırılmaz; D verisi ve ham zip'ler okunmaz; .env
okunmaz; config.py import edilmez; REV1 motoruna, bota, sunucuya dokunulmaz; web yok; hiçbir dosyaya yazma.
