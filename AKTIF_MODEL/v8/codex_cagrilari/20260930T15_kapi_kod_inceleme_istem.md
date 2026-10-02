Sen v8 kripto motorunun bağımsız kod inceleyicisisin. Carry kapısının (CARRY_KAPISI_ONKAYIT) kodu yazıldı; ön-kayıt
kilidinden (Adım 4) ve D'deki ilk P&L koşusundan (Adım 5) ÖNCE incelemeni istiyorum. Çalışma kökü bu git çalışma
kopyasıdır (dal claude/v8-kapi-motor-502e). Hiçbir dosyaya yazma; yalnız metin yanıt ver. Kodu ve testleri KOŞMA.
Okumak için `git diff d5aefdf -- <yol>` ve `git show` kullanabilirsin.

Tasarım (bağlayıcı): AKTIF_MODEL/ciktilar/v8_asama4_20260927_01/CARRY_KAPISI_ONKAYIT_TASLAK.md §2, §3, §4.1, §5, §6,
§7 ve §15 (uygulama netleştirmeleri 1–11); AKTIF_MODEL/ciktilar/v8_kapi_20260929_01/BELIRSIZLIK_COZUMLERI.md
(U-01…U-55, gerekçeli karar tablosu); MIMARI.md §4.7 (sanal bacaklar, s^C), §5.1 (sembol filtreleri).
Durum ve plan: AKTIF_MODEL/v8/ILERLEME_KALIBRASYON.md "DEVAM" bölümü.

İncelenecek kod (AKTIF_MODEL/v8 altında):
- kapi/istatistik.py (SR, SR^K, Newey–West ortalama ve OLS HAC, büyük SE, ρ_üst, K1*, K2 blok bootstrap, TOST, Andrews)
- kapi/seriler.py (haftalık/aylık seriler, ölçek, NAV sınırları, V2 günlük oranı)
- kapi/olcutler.py (V3, V4a/b, K1–K11, çift seri kuralı, §7.1 karar, denetim/hüküm ayrımı, U-52)
- kapi/faktorler.py (x_B, x_A, x_R, x_S), kapi/isim.py (K8 sıralaması, bacaklar, sıfır/sıfır)
- kapi/betimsel.py, kapi/betimsel_kayit.py (betimsel raporlar), kapi/denetim.py (V1, V5, V6), kapi/kosu.py (koşu betiği)
- kilit.py (KILIT.json üret/doğrula)
- motor değişiklikleri (d5aefdf'e göre): motor/ayristirma.py (carry_coin, artik_coin, bacak_funding_tur),
  motor/hedef_b.py (Pazartesi 'r30'/'s_trend' tanısı, 'w_trend_yildiz', carry_haric), motor/tipler.py (carry_haric)
- testler: testler/test_v8_kapi_*.py, testler/test_v8_kilit.py

Özellikle sına (her biri için EVET/HAYIR/KISMEN + gerekçe):
1. Ölçüt uygunluğu: K1 (SR^K, U-09 artık terimi, ρ_üst her seri kendi trend çiftiyle, K1* kırpma), K2 (NW t büyük SE ≥ 3,0;
   bootstrap tek akış 4 sonra 12, 0,05 kantili), K5 (tamsayı karşılaştırma, 33 ay), K6/K7, K8 (sıralama penceresi,
   yalnız carry adaylığından çıkarma), K9 (ayrı regresyonlar, açık aralık), K10, K11 (standart yükleme ve SE'si),
   V3/V4a/V4b, eşitlik yönleri (§7.1), "hesaplanamayan geçmemiş sayılır".
2. Seriler: hafta/ay sınırları, saatin haftaya atanması (T damgalı funding dahil), r^X ölçeği ω_C·L·NAV_{w başı},
   r^T ölçeği, NAV_{w başı} = sınır anındaki NAV, V2'nin göreli günlük tanımı (U-16).
3. MÜHÜR: trend P&L'i ya da B'nin toplam getirisi HUKUM.json, DENETIM.json, KOSU_OZETI.json ya da ekrana herhangi bir
   yoldan sızıyor mu (ρ̂/ρ_üst dışında)? Mühür klasörü (günlükler, NAV, trend satırları) yeterli mi (U-53)?
4. Motor değişiklikleri P&L'i ve kararları değiştirmiyor mu (varsayılan carry_haric = ()); günlüğe NaN yazılabilir mi;
   carry_coin/artik_coin toplam özdeşliği ve sıralama kararlılığı; D ölçeğinde bellek (122 coin × ~24.000 saat).
5. V5'in "bağımsız okuma"sı anlamlı mı; V6'da A hedefinin B'nin durumu üzerinde kurulması (U-51) kabul edilebilir mi;
   V1 rapor seçimi.
6. Kilit: kapsam yeterli mi; kilitten sonra fark edilmeden değişebilecek bir girdi (kod, parametre, veri, filtre,
   tohum, eşik) kalıyor mu; dogrula mantığında delik var mı?
7. Hatalar: uç durumlar (NaN, boş hafta, sabit seri, n < 4, K8 < 30 isim), sayısal, Windows, ölü kod.

Yanıt biçimi (Türkçe):
## bulgular
Her bulgu: `[OLDURUCU|CIDDI|ORTA|DUSUK] başlık — dosya:satır — sorun — önerilen düzeltme` (en fazla 15; yoksa "yok").
## u41_u55
Her biri tek satır: `U-xx KABUL | ITIRAZ — gerekçe (≤30 kelime)`.
## sorular_1_7
Her biri tek satır: `EVET/HAYIR/KISMEN — gerekçe`.
## genel_hukum
1–2 cümle: kapı kodu kilide ve D koşusuna hazır mı?

Yasaklar: BANKA_MUHURLU.json, uygun_evren.json, SECIM.json, secim_cikti.json okunmaz, dosya bilgisi de sorgulanmaz
(AKTIF_MODEL/ciktilar/v8_banka_20260924_01 klasörünü listeleme; yalnız V8_DENEME_DEFTERI.csv açık yoluyla okunabilir);
banka coinleri/Z1/Z2 araştırılmaz; D verisi, v8_veri klasörü ve ham zip'ler okunmaz;
ciktilar/v8_sembol_filtreleri_20260930_01/exchangeInfo_ham.json okunmaz; .env okunmaz; config.py import edilmez;
REV1 motoruna (AKTIF_MODEL/motor), bota, sunucuya dokunulmaz; web yok; hiçbir dosyaya yazma; kod koşma.
