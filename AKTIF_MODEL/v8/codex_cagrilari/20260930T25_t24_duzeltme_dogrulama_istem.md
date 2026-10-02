Sen v8 kripto motorunun bağımsız kod inceleyicisisin. T24'te (yanıtın:
AKTIF_MODEL/v8/codex_cagrilari/20260930T24_t23_duzeltme_dogrulama_yanit.md) 4 KISMEN ve 5 yeni bulgu verdin. Düzeltmeler
önce ön-kayda (BANKA_ONKAYIT_TASLAK.md §3.7 netleştirme 20 (l)) yazıldı, sonra kodlandı. ÇOK KISA doğrulama (T25):
`git diff bb6ebdc -- AKTIF_MODEL/v8 AKTIF_MODEL/ciktilar/v8_asama4_20260927_01`. Hiçbir dosyaya yazma; kodu ve testleri KOŞMA.

Görev: T24'ün KISMEN (1, 5, 8, 10) ve yeni 5 bulgusu için KAPANDI | KISMEN | ACIK + tek cümle (dosya:satır); düzeltmenin
getirdiği yeni sorun varsa en fazla 4 madde; son olarak tek cümle: banka betiği dondurmaya hazır mı.

Yanıt biçimi (Türkçe): ## kapanis / ## yeni_bulgular (`[CIDDI|ORTA|DUSUK] başlık — dosya:satır — sorun — düzeltme` ya da
"yok") / ## genel_hukum.

Yasaklar: BANKA_MUHURLU.json, uygun_evren.json, SECIM.json, secim_cikti.json okunmaz, dosya bilgisi de sorgulanmaz
(AKTIF_MODEL/ciktilar/v8_banka_20260924_01 klasörünü listeleme; yalnız V8_DENEME_DEFTERI.csv açık yoluyla okunabilir);
banka coinleri/Z1/Z2 araştırılmaz; D verisi, v8_veri klasörü ve ham zip'ler okunmaz;
ciktilar/v8_sembol_filtreleri_20260930_01/exchangeInfo_ham.json okunmaz; .env okunmaz; config.py import edilmez;
REV1 motoruna (AKTIF_MODEL/motor), bota, sunucuya dokunulmaz; web yok; hiçbir dosyaya yazma; kod koşma.
