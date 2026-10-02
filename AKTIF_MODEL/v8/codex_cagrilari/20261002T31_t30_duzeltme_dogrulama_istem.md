Sen v8 kripto projesinin bağımsız inceleyicisisin. T30'da (yanıtın: AKTIF_MODEL/v8/codex_cagrilari/
20261001T30_dondurma_hukum_betikleri_yanit.md) 5 CIDDI + 3 ORTA bulgu verdin. Düzeltmeler commit 0dacfcd'de:
`git diff 7fbf091 0dacfcd -- AKTIF_MODEL/v8 AKTIF_MODEL/ciktilar/v8_dondurma_hazirlik_20261001/UYGULAMA_EK.md`.
UYGULAMA_EK "Revizyon 2" bölümü gerekçeleri yazar. T30-2'nin D doğrulama defter satırı kısmı bilerek açık bırakıldı
(kilitli iki metnin yorumu; kullanıcı kararı). ÇOK KISA doğrulama; hiçbir dosyaya yazma; kod ve test KOŞMA.

Görev: T30 bulguları 1–8 için KAPANDI | KISMEN | ACIK + tek cümle (dosya:satır); düzeltmenin getirdiği yeni sorun (en
fazla 4); R1'deki "onkosul=False + ayrı ön koşul/V1 denetimi" yaklaşımı kilitli 21 g metniyle (T29 eki) uyumlu mu ve
kilidin güvencesini zayıflatıyor mu (tek paragraf); tek cümle: kuru koşuyu (6.15, banka_kos.py kuru A) başlatmaya
engel var mı?

Yanıt biçimi (Türkçe): ## kapanis / ## yeni_bulgular (`[CIDDI|ORTA|DUSUK] başlık — yer — sorun — düzeltme` ya da "yok")
/ ## r1_uyum / ## genel_hukum.

Yasaklar: BANKA_MUHURLU.json, uygun_evren.json, SECIM.json, secim_cikti.json okunmaz, dosya bilgisi de sorgulanmaz
(AKTIF_MODEL/ciktilar/v8_banka_20260924_01 klasörünü listeleme; yalnız V8_DENEME_DEFTERI.csv açık yoluyla okunabilir);
AKTIF_MODEL/ciktilar/v8_kapi_kosu_20261001/muhur okunmaz ve listelenmez; banka coinleri/Z1/Z2 araştırılmaz; D verisi,
v8_veri klasörü ve ham zip'ler okunmaz; ciktilar/v8_sembol_filtreleri_20260930_01/exchangeInfo_ham.json okunmaz; .env
okunmaz; config.py import edilmez; REV1 motoruna (AKTIF_MODEL/motor), bota, sunucuya dokunulmaz; web yok; hiçbir
dosyaya yazma; kod koşma.
