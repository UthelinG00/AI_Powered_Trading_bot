Sen v8 kripto projesinin bağımsız inceleyicisisin. T33'te (yanıtın: AKTIF_MODEL/v8/codex_cagrilari/
20261002T33_t32_dogrulama_yanit.md) N1 zincir yaprağındaki ham lexsort yanlış ret açığını bildirdin. Düzeltme:
`git diff ba8e7b2 HEAD -- AKTIF_MODEL/v8/banka/rejim_null.py AKTIF_MODEL/v8/testler/test_v8_rejim_null.py`. ÇOK KISA;
hiçbir dosyaya yazma; kod ve test KOŞMA. Görev: (1) _ikili_esle doğru bir mükemmel eşleşme algoritması mı (artıran
yol ve geri sarma), yanlış kabul ya da (en_cok sınırı dışında) yanlış ret üretebilir mi; (2) yeni sorun (en fazla 3);
(3) tek cümle: KILIT_TEKNIK_1 ek kaydını (tam takım geçince) üretmeye engel var mı?
Yanıt (Türkçe): ## ikili_esle / ## yeni_bulgular / ## genel_hukum.
Yasaklar: BANKA_MUHURLU.json, uygun_evren.json, SECIM.json, secim_cikti.json okunmaz, dosya bilgisi de sorgulanmaz
(AKTIF_MODEL/ciktilar/v8_banka_20260924_01 klasörünü listeleme); AKTIF_MODEL/ciktilar/v8_kapi_kosu_20261001/muhur
okunmaz; banka coinleri/Z1/Z2 araştırılmaz; D verisi, v8_veri klasörü ve ham zip'ler okunmaz; exchangeInfo_ham.json
okunmaz; .env okunmaz; config.py import edilmez; REV1 motoruna, bota, sunucuya dokunulmaz; web yok; dosya yazma; kod koşma.
