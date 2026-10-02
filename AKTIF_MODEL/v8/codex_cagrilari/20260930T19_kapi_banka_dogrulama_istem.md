Sen v8 kripto motorunun bağımsız kod inceleyicisisin. T18'de carry kapısı ve banka kodunu doğrulamıştın (yanıtın:
AKTIF_MODEL/v8/codex_cagrilari/20260930T18_kapi_kod_dogrulama_yanit.md; T17 6/6 KAPANDI; yeni 3 CIDDI, U-59-ek-2 İTİRAZ,
B5 açık sorusu; "kilide hazır değil"). Bunlar bulut oturumunda işlendi (2. tur). Şimdi DOĞRULAMA turu (T19). Çalışma kökü
bu git çalışma kopyasıdır (dal claude/v8-kapi-motor-502e). T18'deki HEAD 4beaf6c idi; aradaki dizüstü commit'leri
(02dffa1 duman kanıtı + eşdeğerlik + tam takım; 351ddbe; d5015ea birleştirme; 5ac4f85 oturum notu) ve 2. tur düzeltmeleri:
`git log --oneline 4beaf6c..HEAD`, `git diff 5ac4f85 -- AKTIF_MODEL/v8 AKTIF_MODEL/ciktilar/v8_kalibrasyon_20260929_01
AKTIF_MODEL/ciktilar/v8_b5_desen_20260930_01`. Oturum günlüğü: AKTIF_MODEL/v8/BULUT_OTURUMU.md "Günlük" (2. TUR madde
1–6; madde 3'ün tasarım notu ve üreteç incelemesi koddan önce yazıldı). Hiçbir dosyaya yazma; yalnız metin yanıt ver.
Kodu ve testleri KOŞMA.

Bağlayıcı belgeler (bu commit'te güncel): CARRY_KAPISI_ONKAYIT_TASLAK.md §15 (madde 1–15);
AKTIF_MODEL/ciktilar/v8_kapi_20260929_01/BELIRSIZLIK_COZUMLERI.md Grup 1–7 (U-01…U-67; Grup 7 = T18);
BANKA_ONKAYIT_TASLAK.md §3.4, §3.5.6 ve §3.7 "Uygulama netleştirmeleri" 1–13 (13 = R3, dizüstünde eklendi, kod yok);
AKTIF_MODEL/v8/ILERLEME_BANKA.md BK-1…BK-14.

Görevler:
1. T18'in açık kalemleri için KAPANDI | KISMEN | ACIK + tek cümle gerekçe (dosya:satır):
   - T15-3 / T18-CIDDI-1 bitiş–toplama bağı ve U-59-ek-2: KAL/kanit.py klasor_ozeti (bitiş ve toplamanın ortak tanımı),
     KAL/bitis.py kanıt bloğu, KAL/topla.py on_kosullar (hesaptan önce bitiş kanıtıyla eşleşme, kimlik ve KOD_DONDURMA
     denetimi) ve main (hesaptan sonra yeniden özet; değiştiyse TOPLAMA yazılmaz; duzey2_tuketilen), v8/kilit.py
     onkosullar (D2_OZET karşılaştırması). Düzey 1 girdileri yalnız kaydediliyor (duzey1_tuketilen): DUZEY1_OZET.json'un
     üretici betiği depoda yok; Düzey 1 için de zorunlu bağ gerekli mi, gerekiyorsa nasıl (json_sha256/npz_sha256 kuralı)?
   - T18-CIDDI-2 B7 null gün maskesi: banka/degerlendirme.py sadece_sharpe; kalibrasyon pencerelerinin hariç gün taşımadığı
     iddiası (kalibrasyon/duzey2_uretec.py pencere, kalibrasyon/yurutucu.py:120) ve bit eşitliği.
   - T18-CIDDI-3 B'de birincil dışı birimler: banka/degerlendirme.py birincil_olcum(b5=...), banka_kos/yurutucu.py
     B5_GRUPLARI; BANKA §3.4 okuması (B5 yalnız birincil ayar) doğru mu; R8 bağımsız A birimi; testler
     test_v8_banka_yurutucu (gerçek B yürütme) ve test_v8_banka_uctan_uca (A ve B sınıfları).
2. B5 epizot atfı (T18 açık sorusu → düzeltme):
   (a) Tasarım: motor/ayristirma.py fon_parcalari (fon_yonu bunun üstüne), trend_fon_ozgun; banka/pnl.py coin_pnl dolgu
       defteri ve fon_ozgun; epizot_pnl(ozgun=) (şimdiki epizot, hedef epizot, özgün satır) üçlüsüne netleme;
       banka/degerlendirme.py _ozgun_dilim (yalnız pencere içinde kayda geçen, saat maskeli; pencere öncesi özgün saat:
       epizot kesintisizse pencere başı, değilse hiçbiri). Özgün epizot kimliği doğru mu (kapanıp aynı yönde açılış)? Netleme
       bir hatayı gizleyebilir mi (farklı saatlerin karşılıklı götürmesi)? Pencere öncesi ve hariç gün kuralları BANKA §3.4
       ile tutarlı mı? coin_pnl'in dolgu defteri durum.kayit_uygula'daki bekleyen dolgularla her durumda (budama, aynı
       saatte birden çok gerçek kayıt) aynı kümeyi mi verir?
   (b) Üreteç incelemesi ve kalibrasyonun etkilenmediği iddiası: testler/test_v8_duzey2_funding_desen.py (veri düzeyi:
       dolgu yalnız 4h→8h dönüşünün S+6/S+7'sinde, S+8 kaydıyla tam ters kayıt; boşlukta ve ölümde dolgu yok; geri testte geç
       kayıt yok), ciktilar/v8_b5_desen_20260930_01 (motor düzeyi: 2 dolgu + 1 ters kayıt; C29 dönüşünde 2 parça epizot
       sınırını aşıyor; netleme sonrası epizot listesi değişmiyor; dört kısaltılmış birim gövdesi eski/yeni kodla aynı).
       Gerekçe zinciri (her Düzey 2 dolgusu tam ters kaydedilir; pozisyon yalnız 01:00'de değişir → fill ve tersi aynı
       üçlü anahtarda tam götürür) sağlam mı; gözden kaçan Düzey 2 dolgu kaynağı var mı (listelenme, 4h başlangıcı, ölüm
       öncesi düşük hacim, sıfır hacimli bar, maske/uzlaşma saatleri)? Düzey 2'nin yeniden koşulması gerekir mi?
3. Düzeltmelerin getirdiği yeni sorun: özellikle ayrıştırmanın 18 mevcut alanının değişmediği, fon_yonu'nun yeniden
   yazımından sonra carry_fon_long/short'un aynı kaldığı; banka/pnl.py'nin motor.ayristirma'yı içe aktarmasının döngü ya da
   kimlik etkisi; topla.py main'in test için eklenen parametreleri; kilit zincirine eklenen yeni alanlar.
4. Grup 7 kararları (U-59 ek 4, U-65, U-66, U-67): her biri tek satır KABUL | ITIRAZ.
4b. R3 long-beta tasarımı (BANKA §3.7 netleştirme 13; kullanıcı onayı; kod henüz yok): aylık yeniden dengeleme (arada
   çıkan/maskelenen isim satılır, nakitte kalır), 1/σ̂ ağırlık boyut_sigmalari ile, BTC/ETH evrendeyse dahil, A/B aynı,
   ayrı motor koşusu, icra/maliyet/funding motorla aynı, raporda birincilin gerçekleşen vol'üne ölçekleme ve NW t.
   Tek satır KABUL | ITIRAZ; ITIRAZ ise hangi alt madde (a–g) ve neden. Kilitten önce eksik kalan bir tanım var mı?
5. Genel hüküm: kapı kodu, dizüstünde kalan adımlarla (eşdeğerlik son kodla; 3.09 bitiş yan daldaki bitis.py + kanit.py ile;
   toplama yan daldaki topla.py ile; yan dalın birleştirilmesi; tam takım + V1; kilit) kilide hazır mı? Banka koşucusu ve
   hükmü (R3 long_beta hâlâ yürütücüde yok — biliniyor) banka yürütmesine R3 dışında hazır mı?

Yanıt biçimi (Türkçe):
## kapanis
`<madde> KAPANDI|KISMEN|ACIK — gerekçe`
## b5
(a) ve (b) için ayrı paragraflar; her iddiaya dosya:satır.
## yeni_bulgular
`[OLDURUCU|CIDDI|ORTA|DUSUK] başlık — dosya:satır — sorun — düzeltme` (en fazla 8; yoksa "yok")
## kararlar
`U-xx KABUL|ITIRAZ — gerekçe (≤25 kelime)`; ayrıca `R3 KABUL|ITIRAZ — gerekçe`
## genel_hukum
1–2 cümle.

Yasaklar: BANKA_MUHURLU.json, uygun_evren.json, SECIM.json, secim_cikti.json okunmaz, dosya bilgisi de sorgulanmaz
(AKTIF_MODEL/ciktilar/v8_banka_20260924_01 klasörünü listeleme; yalnız V8_DENEME_DEFTERI.csv açık yoluyla okunabilir);
banka coinleri/Z1/Z2 araştırılmaz; D verisi, v8_veri klasörü ve ham zip'ler okunmaz;
ciktilar/v8_sembol_filtreleri_20260930_01/exchangeInfo_ham.json okunmaz; .env okunmaz; config.py import edilmez;
REV1 motoruna (AKTIF_MODEL/motor), bota, sunucuya dokunulmaz; web yok; hiçbir dosyaya yazma; kod koşma.
