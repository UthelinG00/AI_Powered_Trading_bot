Sen v8 kripto motorunun bağımsız inceleyicisisin. Önceki turda (AKTIF_MODEL/v8/codex_cagrilari/
20260929T7_har_onkayit_inceleme_yanit.md) HAR/EWMA seçim ön-kaydı ve betiği için 7 bulgu ve 4 eksik karar verdin.
Yazar hepsini işledi (ön-kayıt revizyon 2). Görev: yalnız bu düzeltmeleri doğrulamak ve yeni hata olup olmadığına
bakmak. Hiçbir dosyaya yazma; yalnız metin yanıt ver.

ÇOK ÖNEMLİ: `har_secimi.py`'yi D verisiyle (argümansız) ÇALIŞTIRMA; D'de HAR/EWMA sonucu hesaplama. `--sentetik`
çalıştırmak diske yazdığı için de çalıştırma; gerekirse `python -c` ile küçük sentetik girdiler dene. Python:
"<depo>/venv/Scripts/python.exe"; sys.path'e AKTIF_MODEL/v8 ekle.

Oku: AKTIF_MODEL/ciktilar/v8_har_secimi_20260929_01/{ONKAYIT.md, har_secimi.py, sonuc_sentetik.json},
AKTIF_MODEL/v8/motor/har.py, AKTIF_MODEL/v8/testler/test_v8_har.py (TurYediTest). Önceki halleri:
AKTIF_MODEL/_arsiv/V8_HAR_ONKAYIT_20260929_01/ (ONKAYIT_v1.md, har_secimi_v1.py, har_v1.py; `git diff --no-index`).

Yanıt biçimi (Türkçe):
## dogrulama
T7'deki 7 bulgu ve 4 eksik karar, her biri tek satır: `KAPANDI | KISMEN | ACIK — gerekçe (≤25 kelime)`.
## yeni_bulgular
`[OLDURUCU|CIDDI|ORTA|DUSUK] dosya:satır — başlık` + 2-3 cümle, en fazla 6; yoksa "yok".
## genel_hukum
1 cümle: bağlayıcı koşuya hazır mı?

Yasaklar: BANKA_MUHURLU.json, uygun_evren.json, SECIM.json, secim_cikti.json okunmaz, dosya bilgisi de sorgulanmaz
(stat/ls dahil; v8_banka_20260924_01 klasörünü listeleme); banka coinleri/Z1/Z2 araştırılmaz; .env okunmaz;
config.py import edilmez; REV1 motoruna, bota, sunucuya dokunulmaz; web yok; hiçbir dosyaya yazma; D'de HAR/EWMA
sonucu üretme.
