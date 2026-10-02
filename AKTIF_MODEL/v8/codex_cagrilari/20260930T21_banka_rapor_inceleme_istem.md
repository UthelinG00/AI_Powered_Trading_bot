Sen v8 kripto motorunun bağımsız kod inceleyicisisin. Bu tur (T21) banka koşucusunun 30 Eylül dizüstü oturumunda yazılan
kısmını inceler: R3 long-beta kitabı, rapor satırları (R2, R4–R17), koşu tanıları, R8 B ayrıştırması, BANKA_RAPORU.md
üreteci ve veri denetimi (T2). Çalışma kökü bu git çalışma kopyasıdır; T20'deki HEAD b908b74 idi:
`git log --oneline b908b74..HEAD`, `git diff b908b74 -- AKTIF_MODEL/v8/banka_kos AKTIF_MODEL/v8/testler
AKTIF_MODEL/ciktilar/v8_asama4_20260927_01/BANKA_ONKAYIT_TASLAK.md`. Hiçbir dosyaya yazma; yalnız metin yanıt ver.
Kodu ve testleri KOŞMA.

Bağlayıcı tanımlar: BANKA_ONKAYIT_TASLAK.md §3.1, §3.4 (R satırları), §4, §5.4–5.5, §8, ve §3.7 "Uygulama
netleştirmeleri" 13–16 (13 = R3, 14 = R5/R6/R7/R14, 15 = R2/R4/R13b/R15/R17, 16 = R8); AKTIF_MODEL/v8/ILERLEME_BANKA.md
BK-14…BK-17. Kod: AKTIF_MODEL/v8/banka_kos/long_beta.py, tanilar.py, rapor.py, rapor_md.py, veri_denetim.py; yurutucu.py
ve hukum.py'deki bağlantılar. Testler: test_v8_banka_long_beta, test_v8_banka_rapor, test_v8_banka_veri_denetim,
test_v8_banka_yurutucu, test_v8_banka_uctan_uca, test_v8_banka_hukum.

Görevler:
1. Her netleştirme (13, 14, 15, 16) için kod tanıma sadık mı: UYUMLU | SAPMA — dosya:satır — tek cümle. Özellikle:
   (a) R3: r3_karar'ın motorun karar_ver sırasını, kayıt biçimini ve devreden emir kuralını koruması; aylık/ara gün
       ayrımı; bütçe kuralı; reduce-only; kos_r3'ün geri_test.kos ile birebirliği; A ve B'de aynı kitap.
   (b) tanilar.durum_izi: kayit_uygula ile yeniden oynatmanın motor durumuyla aynı olması; niyet kapanış sınıflaması.
   (c) R7: σ̂ = k·s/w^u geri çıkarımının doğruluğu (T4-a günleri dışarıda) ve RV hedefinin HAR seçimiyle aynı tanımı
       (coin_gunluk, koşu sonu maske geçmişi — bu PIT açısından sorun mu?).
   (d) R2: piyasa serileri, gün başı ağırlık, coin P&L'i ve β_i; btc_katki + artik_katki = günlük getiri özdeşliği.
   (e) R8: ayrıştırma satırlarının günlük/NAV dönüşümü; Kelly B birimlerinin yalnız 1× maliyetle ayrıştırılması;
       ölçümün B5'siz kalması (BK-13).
   (f) Sharpe %90 GA: durağan blok bootstrap, tohum etiketlerinin benzersizliği ve determinizmi.
2. Bankanın tek atış ve kör hüküm ilkesiyle çelişki: yeni düz çıktılarda (tanilar, piyasa, r13b, r17, r8_*) coin adı ya
   da açık grupta performans sızıntısı var mı; rapor_md'de coin adı çıkma yolu var mı; şifreleme dışı kalan alan var mı.
3. Hesaplamada hata: sayısal (NaN/sıfıra bölme), gün hizası (gün damgası, NAV gün başı), pencere/görülmüş gün
   dışlaması, tekrarlanabilirlik (tohum, sıralama).
4. veri_denetim: T2 koşullarının §2.5 ile birebirliği (eşiklerin > / ≥ yönü, "onarılamayan" tanımı, BTC/ETH eksik
   saatin paydası), eksik kalan §8.1 rapor alanı.
5. Testler: her yeni dalın gerçekten sınanıp sınanmadığı; sentetik veride hiç oluşmayan yollar (kısmi dolum, işlem dışı,
   reduce-only, a_t dışına düşme) için eksik test.
6. Genel hüküm: banka betiği, 6.01b veri yükleyicisi ve 6.12 tam motorlu uçtan uca dışında, kilide/banka kuru koşusuna
   hazır mı?

Yanıt biçimi (Türkçe):
## netlestirmeler
`<no> UYUMLU|SAPMA — dosya:satır — gerekçe`
## bulgular
`[OLDURUCU|CIDDI|ORTA|DUSUK] başlık — dosya:satır — sorun — düzeltme` (en fazla 10; yoksa "yok")
## testler
kısa liste
## genel_hukum
1–2 cümle.

Yasaklar: BANKA_MUHURLU.json, uygun_evren.json, SECIM.json, secim_cikti.json okunmaz, dosya bilgisi de sorgulanmaz
(AKTIF_MODEL/ciktilar/v8_banka_20260924_01 klasörünü listeleme; yalnız V8_DENEME_DEFTERI.csv açık yoluyla okunabilir);
banka coinleri/Z1/Z2 araştırılmaz; D verisi, v8_veri klasörü ve ham zip'ler okunmaz;
ciktilar/v8_sembol_filtreleri_20260930_01/exchangeInfo_ham.json okunmaz; .env okunmaz; config.py import edilmez;
REV1 motoruna (AKTIF_MODEL/motor), bota, sunucuya dokunulmaz; web yok; hiçbir dosyaya yazma; kod koşma.
