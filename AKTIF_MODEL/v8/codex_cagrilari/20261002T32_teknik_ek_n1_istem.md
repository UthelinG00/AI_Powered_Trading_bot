Sen v8 kripto projesinin bağımsız inceleyicisisin. Kuru koşu (6.15) null birimlerinde durdu; teşhis
AKTIF_MODEL/ciktilar/v8_kuru_20261002b/HATA_N1.md. Kilitli kalibrasyon kodunda (banka/rejim_null.py) düzeltme, BANKA
§3.7 netleştirme 21 g'nin `banka_oncesi` teknik ek yoluyla yapılıyor (ek kaydı KILIT_TEKNIK_1 henüz üretilmedi; tam takım
ve senin okumandan sonra). Okunacak: `git diff 66ea9ea HEAD -- AKTIF_MODEL/v8 AKTIF_MODEL/ciktilar/v8_banka_20260924_01/V8_DENEME_DEFTERI.csv`
(yalnız bu dosya; o klasörde başka dosyaya bakma) ve HATA_N1.md. Hiçbir dosyaya yazma; kod ve test KOŞMA.

Sorular (kanıtla, dosya:satır): (1) Düzeltme N1'in anlamını değiştiriyor mu, gerçek bir ihlali kaçırabilir mi (iki ızgara
yaklaşımı dahil)? (2) Parametre, eşik ya da davranış değişikliği var mı (21 g: yalnız teknik)? Kalibrasyon sonuçlarını
(Düzey 1/2, B7 null) geçersiz kılar mı? (3) Hata testi D'den bağımsız mı ve eski denetimin hatasını gerçekten gösteriyor
mu? (4) Defter satırı 21 g ve §3.3 ile uyumlu mu (sona ekleme, varyant 0 → +1, N_defter 330, N_dondurma 331)?
(5) test_gercek_kilit'in ara durumda atlanması kabul edilebilir mi? (6) Ek kaydını üretmeye engel var mı?

Yanıt (Türkçe): ## bulgular (`[CIDDI|ORTA|DUSUK] başlık — yer — sorun — düzeltme`; en fazla 6; yoksa "yok") /
## sorular (1–6, kısa) / ## genel_hukum (tek cümle).

Yasaklar: BANKA_MUHURLU.json, uygun_evren.json, SECIM.json, secim_cikti.json okunmaz, dosya bilgisi de sorgulanmaz
(AKTIF_MODEL/ciktilar/v8_banka_20260924_01 klasörünü listeleme; yalnız V8_DENEME_DEFTERI.csv açık yoluyla okunabilir);
AKTIF_MODEL/ciktilar/v8_kapi_kosu_20261001/muhur okunmaz ve listelenmez; banka coinleri/Z1/Z2 araştırılmaz; D verisi,
v8_veri klasörü ve ham zip'ler okunmaz; ciktilar/v8_sembol_filtreleri_20260930_01/exchangeInfo_ham.json okunmaz; .env
okunmaz; config.py import edilmez; REV1 motoruna (AKTIF_MODEL/motor), bota, sunucuya dokunulmaz; web yok; hiçbir
dosyaya yazma; kod koşma.
