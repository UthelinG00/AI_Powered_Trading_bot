Sen v8 kripto projesinin bağımsız inceleyicisisin. Ön-kayıt kilidi vuruldu (KILIT.json, commit 71cf576); carry kapısı koştu
ve hükmü A çıktı (AKTIF_MODEL/ciktilar/v8_kapi_kosu_20261001/KAPI_RAPORU.md). Kilitten sonra kural değiştirmeyen bir uygulama
belgesi (AKTIF_MODEL/ciktilar/v8_dondurma_hazirlik_20261001/UYGULAMA_EK.md, U1–U3) ve kodu yazıldı. Bunlar dondurmadan
(DONDURMA.json) ve sunucudaki kuru koşudan önce son okumadır. Hiçbir dosyaya yazma; kodu ve testleri KOŞMA.

Okunacaklar: `git diff 71cf576 -- AKTIF_MODEL/v8/banka_hukum.py AKTIF_MODEL/v8/dondur.py AKTIF_MODEL/v8/banka_kos/acilis.py
AKTIF_MODEL/v8/testler/test_v8_banka_acilis.py AKTIF_MODEL/v8/testler/test_v8_banka_hukum_dondur.py
AKTIF_MODEL/ciktilar/v8_dondurma_hazirlik_20261001/UYGULAMA_EK.md`. Bağlam için: BANKA_ONKAYIT_TASLAK.md §1.4 (DONDURMA),
§2.4 (kör hüküm), §3.3 (N), §3.7 netleştirme 20 (b, e, k, l) ve 21 (g); banka_kos/hukum.py, banka_kos/rapor_md.py,
banka_kos.py, veri_denetim.py, kilit.py (zincir_dogrula).

Görev — şu sorulara kanıtla (dosya:satır) yanıt ver:
1. UYGULAMA_EK kilitli ön-kayıtla çelişiyor mu ya da yeni bir kural/eşik/serbestlik getiriyor mu?
2. dondur.py: §1.4 ve 20 (b, k, l) alanlarının hepsi var ve doğru kaynaktan mı? DONDURMA'nın banka girişindeki T1
   (acilis.t1_denetimi) ve U2 kilit zinciriyle tutarlılığı; N_dondurma = 159 + N_v8 ve kalibrasyon N'si denetimi; teknik ek
   sayısının hesaba girişi; kapı hükmü (karar A/B) ve kuru koşu temizlik koşulları yeterli mi?
3. banka_hukum.py: §2.4 sırası (DENETIM_TAMAM ↔ klasör, T2–T5, çözmeden önce denetim), N_hüküm = N_dondurma + teknik ek,
   bağlamın VERI_DENETIM dönemlerinden kurulması, TEKNİK GEÇERSİZ yolu, tek yazım, ekrana sızıntı (yalnız hüküm türü ve
   hash'ler basılmalı; hata yolunda coin adı ya da metrik sızabilir mi?), gizli anahtarın işlenişi.
4. acilis.kilit_zinciri (U2): banka kipinde atlanabilir mi (ek['kilit_denetimi'] yalnız testte mi kullanılıyor?), kilit
   yolu/sha'sı DONDURMA'dan doğru okunuyor mu, izinli teknik ek türleri doğru mu?
5. Testler: yamalanan adımlar (hazirla, birimleri_coz, hukum, zincir_dogrula) yüzünden sınanmadan kalan kritik yol var mı?

Yanıt biçimi (Türkçe): ## bulgular (`[CIDDI|ORTA|DUSUK] başlık — yer — sorun — düzeltme`; en fazla 8; yoksa "yok") /
## sorular (1–5, her biri tek-iki cümle) / ## genel_hukum (dondurma ve kuru koşu için engel var mı, tek cümle).

Yasaklar: BANKA_MUHURLU.json, uygun_evren.json, SECIM.json, secim_cikti.json okunmaz, dosya bilgisi de sorgulanmaz
(AKTIF_MODEL/ciktilar/v8_banka_20260924_01 klasörünü listeleme; yalnız V8_DENEME_DEFTERI.csv açık yoluyla okunabilir);
AKTIF_MODEL/ciktilar/v8_kapi_kosu_20261001/muhur klasörü (trend mühürü) okunmaz ve listelenmez;
banka coinleri/Z1/Z2 araştırılmaz; D verisi, v8_veri klasörü ve ham zip'ler okunmaz;
ciktilar/v8_sembol_filtreleri_20260930_01/exchangeInfo_ham.json okunmaz; .env okunmaz; config.py import edilmez;
REV1 motoruna (AKTIF_MODEL/motor), bota, sunucuya dokunulmaz; web yok; hiçbir dosyaya yazma; kod koşma.
