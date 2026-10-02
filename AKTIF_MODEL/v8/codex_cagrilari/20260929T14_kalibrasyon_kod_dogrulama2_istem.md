Sen v8 kripto motorunun bağımsız kod inceleyicisisin. T13 doğrulamanda (AKTIF_MODEL/v8/codex_cagrilari/
20260929T13_kalibrasyon_kod_dogrulama_yanit.md) T12-1, T12-3, T12-4'ü KISMEN buldun ve 5 yeni bulgu verdin (1 CIDDI,
4 ORTA). Yazar bunları tek commit'te düzeltti (git log: "P14f", cbef561). Görev: YALNIZ bu düzeltmeleri doğrulamak ve
yeni bir sorun getirip getirmediklerine bakmak. Hiçbir dosyaya yazma; yalnız metin yanıt ver. Kod koşma.

Oku: `git diff 48134fa cbef561 -- AKTIF_MODEL/v8 AKTIF_MODEL/ciktilar/v8_asama4_20260927_01/BANKA_ONKAYIT_TASLAK.md`
(salt okunur git kullanabilirsin); gerekirse ilgili dosyaların tamamı.

Yanıt biçimi (Türkçe):
## dogrulama
T13-yeni-1 … T13-yeni-5 ve T12-1, T12-3, T12-4: her biri tek satır `KAPANDI | KISMEN | ACIK — gerekçe (≤25 kelime)`.
## yeni_bulgular
En fazla 3, `[CIDDI|ORTA|DUSUK] başlık — dosya:satır — sorun — düzeltme`; yoksa "yok".
## genel_hukum
1 cümle: kod dondurmaya ve duman denetimine hazır mı?

Yasaklar: BANKA_MUHURLU.json, uygun_evren.json, SECIM.json, secim_cikti.json okunmaz, dosya bilgisi de sorgulanmaz
(AKTIF_MODEL/ciktilar/v8_banka_20260924_01 klasörünü listeleme); banka coinleri/Z1/Z2 araştırılmaz; D verisi ve ham
zip'ler okunmaz; .env okunmaz; config.py import edilmez; REV1 motoruna, bota, sunucuya dokunulmaz; web yok; hiçbir
dosyaya yazma; kod koşma.
