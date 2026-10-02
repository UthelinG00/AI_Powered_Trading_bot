Sen v8 kripto projesinin bağımsız inceleyicisisin. T28'de (yanıtın:
AKTIF_MODEL/v8/codex_cagrilari/20261001T28_t27_duzeltme_dogrulama_yanit.md) kilidi engelleyen teknik ek zinciri bulgularını
verdin (2 CIDDI, 1 ORTA, 1 DÜŞÜK). Düzeltme önce ön-kayda (BANKA_ONKAYIT_TASLAK.md §3.7 netleştirme 21 (g) revizyonu),
sonra koda işlendi. ÇOK KISA doğrulama (T29): `git diff 906f929~1 -- AKTIF_MODEL/v8/kilit.py AKTIF_MODEL/v8/kapi/kosu.py
AKTIF_MODEL/v8/testler/test_v8_kilit.py AKTIF_MODEL/ciktilar/v8_asama4_20260927_01/BANKA_ONKAYIT_TASLAK.md
AKTIF_MODEL/ciktilar/v8_kapi_sentetik_20261001/ONKAYIT_OLCEK.md`. Hiçbir dosyaya yazma; kodu ve testleri KOŞMA.

Görev: T28'in 4 yeni bulgusu ve T27 Ç3, B1 için KAPANDI | KISMEN | ACIK + tek cümle (dosya:satır); düzeltmenin getirdiği
yeni sorun (en fazla 4); tek cümle: KILIT için kalan engel var mı?

Yanıt biçimi (Türkçe): ## kapanis / ## yeni_bulgular (`[CIDDI|ORTA|DUSUK] başlık — yer — sorun — düzeltme` ya da "yok") /
## genel_hukum.

Yasaklar: BANKA_MUHURLU.json, uygun_evren.json, SECIM.json, secim_cikti.json okunmaz, dosya bilgisi de sorgulanmaz
(AKTIF_MODEL/ciktilar/v8_banka_20260924_01 klasörünü listeleme; yalnız V8_DENEME_DEFTERI.csv açık yoluyla okunabilir);
banka coinleri/Z1/Z2 araştırılmaz; D verisi, v8_veri klasörü ve ham zip'ler okunmaz;
ciktilar/v8_sembol_filtreleri_20260930_01/exchangeInfo_ham.json okunmaz; .env okunmaz; config.py import edilmez;
REV1 motoruna (AKTIF_MODEL/motor), bota, sunucuya dokunulmaz; web yok; hiçbir dosyaya yazma; kod koşma.
