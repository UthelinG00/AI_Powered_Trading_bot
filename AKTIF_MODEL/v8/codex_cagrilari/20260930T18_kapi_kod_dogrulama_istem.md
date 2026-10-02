Sen v8 kripto motorunun bağımsız kod inceleyicisisin. T17'de carry kapısı ve banka koşucusu kodunu doğrulamıştın
(yanıtın: AKTIF_MODEL/v8/codex_cagrilari/20260930T17_kapi_kod_dogrulama_yanit.md; 5 KISMEN, yeni 2 CIDDI + 4 ORTA,
"kapı kodu henüz kilide hazır değil"). Bunlar bulut oturumunda işlendi. Şimdi DOĞRULAMA turu (T18). Çalışma kökü bu git
çalışma kopyasıdır (dal claude/v8-kapi-motor-502e). T17'deki HEAD 9623677 idi; T17 düzeltmeleri 744fcce'den sonra:
`git log --oneline 744fcce..HEAD` ve `git diff 744fcce -- AKTIF_MODEL/v8 AKTIF_MODEL/ciktilar/v8_kalibrasyon_20260929_01`.
Oturum günlüğü: AKTIF_MODEL/v8/BULUT_OTURUMU.md "Günlük" (madde 1–9; madde 6'nın tasarım notu koddan önce yazıldı).
Hiçbir dosyaya yazma; yalnız metin yanıt ver. Kodu ve testleri KOŞMA.

Bağlayıcı belgeler (bu commit'te güncel): CARRY_KAPISI_ONKAYIT_TASLAK.md §15 (madde 1–14) ve
AKTIF_MODEL/ciktilar/v8_kapi_20260929_01/BELIRSIZLIK_COZUMLERI.md Grup 1–6 (U-01…U-64; Grup 6 = T17).

Görevler:
1. T17'de KISMEN kalan 5 madde (T15-3, T15-4, T15-10, T15-13, T16-ORTA-funding) ve T17'nin 6 yeni bulgusu için:
   KAPANDI | KISMEN | ACIK + tek cümle gerekçe (dosya:satır). Özellikle:
   - banka_kos/kosucu.py: _muhurle/_sinirli ortak hata sınırı; birim_hesapla, _isci_hazirla (başlatıcı hiç istisna
     fırlatmaz), BK-6 yeniden yürütme (_yeniden_yurut), calistir'in dış sınırı (işçinin uzak izi dahil bağlam bastırma);
   - kanıt zinciri: ciktilar/v8_kalibrasyon_20260929_01/kanit.py (ortak blok), duman_kanit.py (yeni; diskteki duman
     klasörlerinden), bitis.py, topla.py, esdegerlik_502e.py ('guncel' kimlikler, girdi zarf hash'leri, guncel_sabit);
     v8/kilit.py guncel_girdiler ve onkosullar (blok = dondurma; güncel HAR = dondurma HAR; eşdeğerlik güncel ucu = kilit
     anı; kaynak zinciri TOPLAMA→bitis_sonuc, duman_kanit→duman_sonuc, eşdeğerlik girdileri→duman dosyaları);
     KILIT_BELGELERI'ne duman_kanit.json eklendi;
   - kilit.git_denetimi ve _uzak_dallar (tam hash, fetch --prune, ls-remote ile doğrulanmış yalnız origin dalları);
   - kapi/denetim.py _v5_on_denetim, _esit/_skaler_esit (NaN/inf), v5_saatlik (sc_q isim/saat, artik_farkli_saat);
   - motor/ayristirma.py sc_q (artik_carry aynı değerlerle aynı sırada) ve fon_yonu + carry_fon_long/short;
     kapi/isim.py bacak_serileri (funding kısmı özgün yön; kalan saat başındaki işaret).
2. Düzeltmelerin getirdiği yeni sorun. Özellikle: (a) motor/ayristirma.py değişikliklerinin mevcut alanları (satirlar,
   trend_*, carry_coin/eski/yeni, artik_coin, carry_q, bacak_funding_tur) ve özdeşliği DEĞİŞTİRMEDİĞİ (yeni alanlar
   yalnız ek çıktı; kalibrasyon ve banka yalnız belirli alanları okur); (b) fon_yonu'nun ters kayıt kümesinin
   funding_saati/kayit_uygula ile birebir aynı olduğu (aynı saatte birden çok gerçek kayıt, budama, geç kayıt); (c)
   kanıt zincirinin 3.09'u sunucuda koşacak bitis.py'ye yeni bağımlılığı (kanit.py de sunucuya gitmeli); (d) hata
   sınırında düz metin sızabilecek başka yol (ProcessPoolExecutor, print, günlük); (e) banka_kos/hukum.py (6.02a; bu
   oturumda testlendi, testler/test_v8_banka_hukum.py): B2 (N_hüküm), B3, B6, B7 kantili (⌈0,95·n⌉'inci, katı >), B9
   penceresi, B10, bağlı/bağsız karar, R1, Kelly/stres (görülmüş gün dışlaması, stres nesnesi şekli) ve birimleri_coz damga
   denetimi (BK-12; ILERLEME_BANKA.md) BANKA_ONKAYIT_TASLAK §2.4, §3.3–§3.5, §4, §5.4 ile tutarlı mı.
3. Grup 6 kararları (U-58 ek 2, U-59 ek 2 ve 3, U-63 ek, U-64 düzeltme): her biri tek satır KABUL | ITIRAZ.
4. Açık soru (karar değil): banka B5 epizot kuralı (banka/pnl.epizot_pnl; trend sanal bacağı ve A'nın net pozisyonu)
   geç gelen eski payı saat başındaki ya da son kapanan epizota yazıyor; yön değişimini kapsayan dolgu aynı biçimde
   yanlış epizota gidebilir. Banka kodu kalibrasyonun dondurulmuş kimliğindedir. Bu B5'te bağlayıcı bir yanlılık mı
   (düzeltilmeli mi, kalibrasyonla tutarlılık için olduğu gibi mi kalmalı)? Gerekçeli tek paragraf.
5. Genel hüküm: kapı kodu, dizüstünde kalan adımlarla (duman_kanit.py koşusu, 3.09 bitiş yeni bitis.py ile, toplama,
   eşdeğerliğin son motorla yeniden koşulması, yan dalın birleştirilmesi, tam test takımı ve V1 raporu, kilit) kilide
   hazır mı? Banka koşucusu banka yürütmesine hazır mı?

Yanıt biçimi (Türkçe):
## kapanis
`<madde> KAPANDI|KISMEN|ACIK — gerekçe`
## yeni_bulgular
`[OLDURUCU|CIDDI|ORTA|DUSUK] başlık — dosya:satır — sorun — düzeltme` (en fazla 8; yoksa "yok")
## kararlar
`U-xx KABUL|ITIRAZ — gerekçe (≤25 kelime)`
## acik_soru
Tek paragraf.
## genel_hukum
1–2 cümle.

Yasaklar: BANKA_MUHURLU.json, uygun_evren.json, SECIM.json, secim_cikti.json okunmaz, dosya bilgisi de sorgulanmaz
(AKTIF_MODEL/ciktilar/v8_banka_20260924_01 klasörünü listeleme; yalnız V8_DENEME_DEFTERI.csv açık yoluyla okunabilir);
banka coinleri/Z1/Z2 araştırılmaz; D verisi, v8_veri klasörü ve ham zip'ler okunmaz;
ciktilar/v8_sembol_filtreleri_20260930_01/exchangeInfo_ham.json okunmaz; .env okunmaz; config.py import edilmez;
REV1 motoruna (AKTIF_MODEL/motor), bota, sunucuya dokunulmaz; web yok; hiçbir dosyaya yazma; kod koşma.
