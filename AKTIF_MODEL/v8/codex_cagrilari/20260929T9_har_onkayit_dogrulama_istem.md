Sen v8 kripto motorunun bağımsız inceleyicisisin. T8 doğrulamanda (AKTIF_MODEL/v8/codex_cagrilari/
20260929T8_har_onkayit_dogrulama_yanit.md) 1 CIDDI, 1 ORTA, 2 DUSUK bulgu verdin. Yazar ön-kayıt revizyon 3 ile
işledi. Görev: YALNIZ bu dört düzeltmeyi doğrulamak ve bu değişikliğin yeni bir sorun getirip getirmediğine bakmak.
Hiçbir dosyaya yazma; yalnız metin yanıt ver. `har_secimi.py`'yi çalıştırma (ne D ne --sentetik); D'de HAR/EWMA
sonucu hesaplama.

Oku: AKTIF_MODEL/ciktilar/v8_har_secimi_20260929_01/ONKAYIT.md (revizyon 3 notu, madde 9, 11, 12),
har_secimi.py; önceki halleri AKTIF_MODEL/_arsiv/V8_HAR_ONKAYIT_20260929_01/ONKAYIT_v2.md, har_secimi_v2.py;
MIMARI §1b (AKTIF_MODEL/ciktilar/v8_asama4_20260927_01/MIMARI.md).

Yanıt biçimi (Türkçe):
## dogrulama
Dört bulgu, her biri tek satır: `KAPANDI | KISMEN | ACIK — gerekçe (≤25 kelime)`.
## yeni_bulgular
En fazla 3; yoksa "yok".
## genel_hukum
1 cümle: bağlayıcı koşuya hazır mı?

Yasaklar: BANKA_MUHURLU.json, uygun_evren.json, SECIM.json, secim_cikti.json okunmaz, dosya bilgisi de sorgulanmaz
(v8_banka_20260924_01 klasörünü listeleme); banka coinleri/Z1/Z2 araştırılmaz; .env okunmaz; config.py import
edilmez; REV1 motoruna, bota, sunucuya dokunulmaz; web yok; hiçbir dosyaya yazma.
