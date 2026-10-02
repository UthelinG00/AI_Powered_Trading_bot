# v8 banka testi — ön-kayıt taslağı (BANKA_ONKAYIT_TASLAK)

Durum: **KİLİT ADAYI (1 Ekim 2026, 4.02).** Bütün açık sorular `ACIK_SORU_YANITLARI.md`'de yanıtlı; Adım 3 (kalibrasyon) kapandı. Koşulmadı: D'de P&L üretilmedi. Kilitten (`KILIT.json`) sonra eşik, ölçüt ve parametre değişmez. İçerik: 2. tur (Aşama 4b-3), 3. revizyon (29 Eylül; §3.7 Düzey 2, §0.2), §3.7 uygulama netleştirmeleri 1–20 ve kalibrasyon sonuçları (4.01).

Tarih: 2026-09-27. Yazan: Aşama 4 banka ön-kaydı revizörü (Opus). Girdi taslak: `calisma/BANKA_ONKAYIT_v1.md`.
2. tur dayanağı: `CODEX_KIRMIZI_TAKIMI.md` (KC-01, KC-02, KC-08, KC-09, KC-10, KC-11), `ASAMA4B_KARAR.md` §1 (bağlayıcı
kullanıcı kararları) ve `codex_cagrilari/20260927T_saclik_yanit.md`. Round-1 nihai hali
`_arsiv/V8_ASAMA4_SENTEZ_20260927_01/round1_nihai/` altındadır.
Dayanak: `girdi/` altındaki 17 dosya, `calisma/MIMARI_v1.md`, `calisma/CARRY_KAPISI_v1.md`, `calisma/KIRMIZI_1.md`,
`calisma/KIRMIZI_2.md`. Belgeler arası arayüzde v1 metinleri ortak referanstır; değişiklikler §10'da.

Bu belge banka mührünün (`03_BANKA_MUHUR_ONKAYIT`, sha256 07220d0e…473a5af8) §7'sinin açtığı "kabul/ret kriterleri
ayrı ön-kayıt" belgesidir. Mührü değiştirmez. Banka içeriği (coin adı, coin listesi) yazılmaz; yalnız sayılar ve kurallar.
Coin adı yalnız BTC/ETH için geçer. Ekonomik kabul **NOT_EVALUATED**. Hiçbir eşik D P&L'ine bakılarak seçilmedi; D P&L'i
henüz hesaplanmadı. Geri test, veri hesabı ve indirme yapılmadı. Aşağıdaki sayılar kalem-kâğıt aritmetiğidir.

---

## 0. v1'e göre ne değişti (özet)

1. **ÖN-KAYIT KİLİDİ** tanımlandı (§1.2). Açık sorular, HAR seçimi, kapı ve banka ön-kayıtları D'deki ilk P&L üreten
   koşudan önce birlikte hash'lenir. Kapı ve D doğrulama performans çıktıları banka hükmüne kadar mühürlüdür (K2-01, K1-13).
2. **Kör hüküm** (§2.4). Performans çıktıları şifreli yazılır. Denetim listesi hüküm açılmadan biter. Hüküm açıldıktan sonra
   bulunan ve hükmü değiştiren hata sonucu NOT_EVALUATED yapar (K2-07).
3. **σ_SR = 0,30 sabit.** REV1'den türetilen std yalnız duyarlılık. Deneme sayacı düzeltildi: N ≈ 320–325 (K2-04).
4. **Bağlayıcı ölçüt seti yeniden kuruldu.** Eski B1 (birincil Sharpe ≥ 0,50) ve eski B12 (−%90 delist) rapora indi.
   B5, B6 ve B10'un eşiği kilitten önce **sentetik kalibrasyonla** (§3.7) sabitlenir (K2-05, K2-13).
5. **CTA çekirdeği ve DD çarpanı ablasyonu bankada koşulmaz** (K2-08).
6. B9 (görülmemiş coinler) yalnız görülmemiş zamanda bağlayıcı (K2-09).
7. Rejim-null yollarında veri hijyeni bayrakları blokla taşınır; üyelik karıştırılmış hacimden yeniden hesaplanır (K1-14,
   K2-14).
8. T4 yalnız hedef kitapta tanımlı; gerçekleşen kitabın aşımları rapor satırı (K1-04).
9. Eşik gerekçelerinden banka rejimine dair cümleler çıkarıldı (K2-06).
10. "Kapısız A" seçeneği KARAR_DEGISIKLIGI_ONERISI / kullanıcıya soru olarak sayılarla yazıldı (§9). Ana kural değişmedi:
    kapı → A/B.

### 0.1 2. turda (Aşama 4b) ne değişti

Yukarıdaki listenin 3., 7. ve 8. maddeleri bu turda aşağıdaki gibi değişti; gerisi geçerlidir.

1. **Rejim-null yeniden yazıldı (KC-01, §3.5).** Karıştırma artık ham OHLC'de değil, getiri uzayında yapılır. Fiyat
   düzeyi her blokta yeniden bazlanır; hacim ve funding blokla taşınır. Coin yaşam döngüsü korunur. Hijyen bayrakları ve
   evren üyeliği sentetik yoldan günlük yeniden hesaplanır. Round-1'in "bayrak blokla taşınır, tetik = 0" kuralı
   kaldırıldı; yerine ekonomik null değişmezleri (N1–N6) T4'e girdi.
2. **Sentetik üreteç donduruldu (KC-02, §3.7).** Epizot genliği, gürültü, maliyet, funding, Düzey 2 fiyat/hacim/funding
   üretimi ve ölçüt eşlemesi tek biçimde yazıldı. Kalibrasyon mekaniktir: kullanıcıya kalibrasyon çıktısına bağlı soru
   sorulmaz. Birleşik yanlış kabul, B7 dahil, Düzey 2'de ölçülür (3. revizyonda üst sınırla; §0.2).
3. **DSR kalibre edilmiş duyarlılık oldu (KC-08, ASAMA4B_KARAR §1 madde 2; §3.3).** "σ_SR = 0,30 sabit, DSR ≥ 0,50"
   tek sayısı kaldırıldı. σ_SR'nin seçim kuralı, B2'nin bağlayıcı mı rapor mu olacağı kuralı ve DSR eşiği d*'ın seçim kuralı
   yazıldı. Sayılar Adım 3'te, D verisine bakılmadan sabitlenir. Seri bağımlılık düzeltmesi eklendi. HAR seçimi sayaçta +2.
4. **T4 nesnelere ayrıldı (KC-09, §2.5).** Birim trend, kaldıraçlı net hedef, carry birimi ve gerçekleşen defter ayrı
   değişmezlerdir. Kaldıraçlı kitapta V ≤ τ aranmaz.
5. **Kelly kaldıraç kümesi bağlayıcı (KC-10, §4).** %30 DD koşulunu sağlamayan L önerilemez ve demoya seçilemez.
6. **Stres senaryoları kanala göre ayrıldı (KC-11, §5).** D90 yalnız long çöküş bindirmesidir. Short sıkışma (SQ) ve
   eşzamanlı çoklu ölüm (DM) senaryoları eklendi. Bağlayıcılık kullanıcının risk tercihidir; Adım 1'de yazılır.
7. §9 ve §11'deki "DSR eşiği" ve "kapısız A" soruları kullanıcı kararıyla kapandı (ASAMA4B_KARAR §1).

### 0.2 3. revizyon (29 Eylül): Düzey 2 hesap kapasitesi

2. turun Düzey 2 koşu planı mimari başına ~127.800, toplam ~255.600 tam motor koşusu ister. Ölçülen motor hızıyla bu
~15.000–30.000 CPU saatidir (bu makinede 2–3 ay kesintisiz). Plan uygulanamaz olduğu için kullanıcı kararıyla (29 Eylül,
`ACIK_SORU_YANITLARI.md` #22) değişti. Karar Adım 3'ün hiçbir koşusundan, D P&L'inden ve banka verisinden önce, yalnız
hesap maliyetine bakılarak verildi. Kalibrasyon çıktısına bağlı bir seçim değildir (§1.2).

1. **B7 eşiği q95'e sabitlendi.** 2. turun "P(B7 geçer | κ = 0) > 0,15 ise q95" kuralı kaldırıldı. Kuralın iki olası
   sonucundan muhafazakâr olanı doğrudan seçildi (§3.4, §3.5.6). Kuantil tanımı yazıldı: ⌈0,95·n⌉'inci sıralı null değeri.
2. **B7 dahil birleşik yanlış kabul üst sınırla ölçülür (Düzey 2-a).** B7 bir vetodur: P(KABUL_birleşik) ≤ P(KABUL_B7siz).
   KABUL_B7siz, Düzey 1 sonunda bağlayıcı kalan ölçütlerin kesişimidir. κ = 0'da 100 yolda A ve B için oran motorla
   ölçülür; null yolu gerekmez. Kural aynıdır: nokta kestirimi %5'i aşarsa kilit bekler (tarama kuralı; güven kanıtı
   değil).
3. **B7'nin gücü betimsel (Düzey 2-b).** Yalnız A; 5 ayar × 10 yol × 50 null. Karar girdisi değildir.
4. **Kesinti ve devam** kuralı eklendi: koşu iş birimlerine bölünür, yarıda kalan iş devam eder, sonuç sıradan bağımsızdır
   (§3.7). Tohum türetimi kanonik yazıldı (SHA-256); tamamlanmış birim yalnız bütünlüğü doğrulanırsa atlanır.
5. **Düzey 2'nin motor yapılandırması** açık yazıldı: dondurulacak banka yapılandırması (HAR, dondurulmuş katsayı, yolun
   kendi yürüyen ŝ²'si).
6. Codex T10 incelemesi (`v8/codex_cagrilari/20260929T10_*`): 1 CIDDI, 3 ORTA, 1 DUSUK bulgu; hepsi işlendi (Ek C sonu).
7. **Uygulama netleştirmeleri (kod incelemesi Codex T12; koşudan önce).** Belgenin açık bıraktığı uygulama yerleri §3.7
   sonunda sabitlendi: Düzey 2 motoru verinin ilk gününden kesintisiz koşar; B5 işaret değiştirme saati bölünür; B10
   ikame hattı ortak faktörü paylaşır; Düzey 1 B4 ölçeği; seyreltme raporunun B'ye ait B9/B10'u; muhasebe kapısı.

Toplam ~5.140 tam motor koşusu (kaba tahmin ~300 CPU saati). Öteki bütün kurallar, üreteç parametreleri ve Düzey 1 aynen
geçerlidir.

---

## 1. Test edilen tek mimari, kilit ve dondurma

### 1.1 Tek mimari
- Bankaya **tek mimari** gider: `M ∈ {A, B}`.
- M, carry D içi kapısının (`CARRY_KAPISI`) hash'li sonucuyla belirlenir. Kapı geçildiyse M = B (trend + ω_C = 0,20 sabit
  carry uydusu). Geçilmediyse M = A (yalnız trend).
- M dondurma kaydına yazılır. Sonradan değişmez.
- **B ise A yalnız ayrıştırmadır.** A'nın banka sonucu hükme girmez. B kalırsa A'ya geçilmez; A'nın banka sonucu iyi olsa
  bile.
- Mühür §7 "en fazla 3 aday ve Holm" der. Aday sayısı m = 1. Holm düzeltmesi m = 1'de etkisizdir. Çoklu test cezası §3.3'teki
  DSR ile uygulanır.

### 1.2 ÖN-KAYIT KİLİDİ ve sıra (üç belgede aynı sıra ve adlar)

| Adım | Ad | İçerik | P&L üretir mi |
|---|---|---|---|
| 0 | Motor testleri | Motor yazılır. Parite, bakış-ileri ve muhasebe özdeşliği yalnız sentetik fikstürlerle ve metrik hesaplanmayan kısa D kesitleriyle sınanır | Hayır |
| 1 | Açık sorular | MIMARI §9, CARRY §10 ve bu belgenin §11'indeki bütün kullanıcı soruları yanıtlanır. Yanıtlar `ACIK_SORU_YANITLARI.md` | Hayır |
| 2 | HAR seçimi | MIMARI §1b prosedürü koşulur; sonuç hash'lenir | Hayır (QLIKE) |
| 3 | Sentetik kalibrasyon | §3.7 ve §3.3. D ve banka verisi kullanmaz. σ_SR'yi, B2'nin türünü ve d*'ı, e_B5, k_B6 ve e_B10'u önceden yazılı kurallarla sabitler (B7 kuantili 3. revizyonla q95'e sabit); birleşik yanlış kabulü (B7 dahil olanı üst sınırla) ve güç eğrilerini üretir | Hayır (yalnız sentetik) |
| 4 | **ÖN-KAYIT KİLİDİ** | MIMARI nihai hali, HAR seçim sonucu, carry kapısı ön-kaydı, bu belge, açık soru yanıtları, kalibrasyon çıktısı ve üreteç kodu **birlikte** hash'lenir (`KILIT.json`). Git commit uzak depoya itilir | — |
| 5 | Kapı koşusu | D'deki **ilk P&L üreten koşu**. Karar A/B. Trend performans satırları mühürlü | Evet (mühürlü) |
| 6 | D doğrulaması ve kuru koşu | Motorun D'de tam koşusu ve `banka_kos.py` kuru koşusu. Denetim çıktıları açık; performans çıktıları mühürlü | Evet (mühürlü) |
| 7 | DONDURMA | §1.4. Kullanıcı onayı "dondur" | — |
| 8 | Banka | Veri denetimi (T2), tek atış, kör denetim, hüküm açılışı (§2) | Evet |

**Bağlayıcı cümle.** Adım 4'ten sonra hiçbir eşik, ölçüt, parametre, örneklem tanımı ya da açık soru yanıtı değişmez. D sonucu
ne çıkarsa çıksın değişmez. Adım 5 ve 6 yalnız kilitli nesneyi koşar.

Kilitten önce tam dönem D strateji P&L'i üreten koşu yapılmaz. Yapılırsa kilit geçersizdir; olay deneme defterine yazılır ve
kullanıcıya bildirilir.

**Adım 1 ile Adım 3 arasındaki sıra (KC-02).** Kullanıcı soruları Adım 1'de biter. Hiçbir soru kalibrasyon çıktısına bağlı
değildir. Adım 3 mekaniktir: üreteç (§3.7), tohumlar ve eşleme kuralları bu belgede dondurulmuştur. Kalibrasyon yalnız bu
kuralları uygular; çıktısı kullanıcı seçimine açılmaz. Adım 3'e kadar hiçbir D performans verisi, D P&L'i ya da banka verisi
kullanılmaz. Adım 3'ün kullandığı tek gerçek kayıt §3.3'teki REV1 deneme kayıtlarıdır; bunlardan yalnız Sharpe dağılımının
std'si alınır. Tek istisna yazılı başarısızlık dalıdır: bir kural "kilit bekler" sonucu verirse durum kullanıcıya sunulur. O
durumda verilen karar yeni bir açık soru yanıtı olarak `ACIK_SORU_YANITLARI.md`'ye eklenir ve Adım 3 baştan koşulur.

### 1.3 Mühürlü D performans çıktıları
- Adım 5 ve 6'nın performans çıktıları (NAV, getiri, Sharpe, DD, epizot, coin katkısı) dosyaya yazılır. Yalnız sha256'ları
  raporlanır.
- Açık kalanlar yalnız denetim çıktılarıdır: parite, özdeşlik farkı, bakış-ileri bekçisi, veri raporu, tavan çözücüsü
  değişmezleri, doldurulan funding sayısı. Bunlar performans sayısı içermez.
- Kapının kendi kararı (A/B) ve kapı ölçütleri açıktır. Bu kapının tasarımıdır. Kapının trend satırları mühürlüdür.
- Mühür, banka hükmü açıldıktan sonra kalkar. DONDURMA'dan sonra açılmaz; aksi halde "D kötü göründü, bankayı açma" seçimi
  doğar.
- T3–T5 düzeltmelerinde "D satırları birebir aynı" karşılaştırması hash düzeyinde yapılır (K1-13).

### 1.4 Dondurma kaydı (`DONDURMA.json`)

| Alan | İçerik |
|---|---|
| `mimari` | A ya da B |
| `kilit_sha256` | `KILIT.json`'un sha256'sı |
| `motor_sha256` | `v8/` motor klasöründeki dosyaların sıralı listesinin (yol + sha256) sha256'sı |
| `git_commit` | Dondurma commit'i; uzak depoya itilir (zaman kanıtı) |
| `parametreler_sha256` | Tek parametre dosyası (MIMARI parametre tablosunun makine hali) |
| `banka_kos_sha256` | Tek atış betiği |
| `veri_denetim_sha256` | Koşu öncesi veri denetim betiği (§2.3) |
| `ortam` | Python sürümü, paket kilit dosyasının sha256'sı |
| `tahminci` | EWMA ya da HAR; seçim raporunun sha256'sı; HAR ise dondurulmuş katsayılar |
| `carry_kapisi` | Sonuç ve rapor sha256'sı |
| `d_dogrulama` | Denetim raporu sha256'sı; mühürlü performans dosyasının sha256'sı |
| `kalibrasyon` | Üreteç kodu ve çıktısının sha256'sı; sabitlenen e_B5, k_B6, e_B10; B7 kuantili q95 (3. revizyonla sabit) |
| `dsr` | σ_SR_bağ ve kaynağı (REV1 kaydı ya da varsayım 0,30); B2 türü (B/R); d*; kalibrasyondaki N_kilit ve SR₀ (§3.3) |
| `deneme_defteri` | sha256, satır sayısı, N_v8 ve N_dondurma (§3.3) |
| `onkayit_sha256` | Bu belgenin nihai halinin sha256'sı |
| `sifreleme_acik_anahtar` | Kullanıcının açık anahtarı (§2.4) |
| `tohum_banka` | int(motor_sha256[:16], 16) mod 2³² |
| `utc` ve `kullanici_onayi` | Onay metni ("dondur") ve zaman |

Dondurmadan sonra motor, parametre, betik, ölçüt ve eşik değişmez. Tek istisna §2.5'teki teknik düzeltmedir.

---

## 2. Açılış protokolü

### 2.1 Roller
- **Kullanıcı:** dondurma onayı, indirme listesi onayı, şifre çözme ve hüküm açılışı.
- **Değerlendirici oturum:** tasarıma katılmamış yeni bir Claude oturumu. Yalnız şunları alır: dondurulmuş depo, bu ön-kayıt,
  `banka_sec.py`, `DAMGA.json`, drand tur JSON'u, `SECIM.json`, `uygun_evren.json`. Tasarım belgelerini ve D sonuçlarını
  almaz. Performans sonucunu hüküm açılışına kadar görmez.
- **Bağımsız yeniden üretici (isteğe bağlı):** Codex. Aynı girdilerle hash'leri, değişmezleri ve şifrelenmemiş sonuç
  dosyasının sha256'sını yeniden üretir; içeriği görmez (§2.4). Paket aktarımını kullanıcı yapar.

### 2.2 Bankanın yeniden üretimi
1. `banka_sec.py`'nin sha256'sı `757ef3c92f64e51e91a3e79acaf46d0f7b4b91dda153ca37fc4c49112c739ee6` ile eşleşmeli.
2. Mühür belgesinin sha256'sı `07220d0e…473a5af8`, `uygun_evren.json`'unki `9148fb8e…` ile eşleşmeli.
3. `DAMGA.json`'daki hedef drand turu alınır. BLS imzası zincir anahtarıyla doğrulanır. Randomness = sha256(imza).
4. Python 3.12'de `banka_sec.py` çalıştırılır. Çıkan `BANKA_MUHURLU.json` ve `GELISTIRME_EVRENI.json` hash'leri `SECIM.json`'daki
   kayıtla birebir eşleşmeli.
5. Herhangi bir eşleşmezlik → **dur**. Veri indirilmez. Sonuç TEKNİK GEÇERSİZ (T1). Kullanıcıya bildirilir.

### 2.3 Veri indirme, onay ve koşu öncesi veri denetimi
Liste bir betikle üretilir. Sohbete yalnız sayılar yazılır (dosya sayısı, toplam boyut, coin sayısı).
- **K coinleri (80):** ilk aylık dosyadan 2026-08'e kadar aylık 1h klines ve fundingRate; 2026-09-01 → 2026-09-23 günlük
  kline dosyaları; hepsinin CHECKSUM dosyaları.
- **D coinleri (120) ve BTC/ETH:** Z1 ayları (ilk dosya → 2023-06) ve Z2 (2026-07, 2026-08, Eylül). D dönemi verisi mevcut
  paketten, mevcut hash'lerle kullanılır.
- **Eylül funding kaynağı (K1-15):** birincil kaynak 2026-09 aylık fundingRate arşiv dosyasıdır. Banka açılışı bu dosya
  yayımlandıktan sonra yapılır. Yalnız Z2_son'dan önceki kayıtlar kullanılır. Açılış tarihinde dosya yoksa kamu fundingRate
  geçmiş uç noktası tek anlık görüntüyle okunur ve hash'lenir. Seçilen kaynak indirme onayında ayrı satırda gösterilir.
- **Sembol filtreleri:** kamu `exchangeInfo` tek anlık görüntüsü (MIMARI §9 soru 4). Görüntüde olmayan (listeden çıkmış)
  semboller için lot yuvarlama kapalı, minNotional 5 USDT. Bu sembollerin sayısı raporlanır.
- Kullanıcı listeyi onaylar. İndirme sonrası CHECKSUM doğrulanır. İlk indirmenin hash'leri `BANKA_MANIFEST.jsonl`'a yazılır ve
  bağlayıcıdır.
- Süreklilik denetimi (yeniden adlandırma, taşınma) yapılır. Sorunlu semboller çıkarılmaz; sayısı raporlanır (mühür §8).
- **T2 koşudan önce karara bağlanır (K2-07).** `veri_denetim.py` `banka_kos.py`'den önce çalışır. T2 kararı
  `VERI_DENETIM.json`'a yazılır ve hash'lenir. T2 yoksa koşu başlar. Koşudan sonra veri gerekçesiyle T2 ileri sürülemez.

### 2.4 Tek atış ve kör hüküm (K2-07)
- `banka_kos.py` **bir kez** çağrılır. Bütün koşuları (§3–§5) tek çağrıda üretir.
- Çıktılar iki gruptur:
  - **Açık grup (`denetim/`):** T3–T5 değişmezleri, parite tekrarları, veri raporu, null hijyen sayaçları, çalışma günlüğü,
    hash'ler. Performans sayısı içermez.
  - **Kapalı grup (`sonuc/`):** NAV serileri, metrikler, geçti/kaldı, hüküm. Düz metin diske yazılmaz. Önce düz metnin
    sha256'sı `SONUC_DAMGA.json`'a yazılır. Ardından içerik kullanıcının açık anahtarına şifrelenir (age biçimi, X25519).
    Çözme anahtarı yalnız kullanıcıdadır.
- Koşu sırasında ekrana hiçbir metrik basılmaz.
- **Denetim listesi (önceden yazılı; hüküm açılmadan tamamlanır):**
  1. T1: dondurma kaydı ile çalışan kodun hash eşleşmesi.
  2. T2: `VERI_DENETIM.json` (koşu öncesi).
  3. T3: çalışma hatası yok.
  4. T4: değişmezler (§2.5).
  5. T5: parite tekrarı.
  6. İsteğe bağlı: Codex, aynı girdilerle düz metin sonuç dosyasının sha256'sını ve açık grubu yeniden üretir. Eşleşme,
     içerik görülmeden yeniden üretim kanıtıdır.
- Liste tamamlanınca `DENETIM_TAMAM.json` hash'lenir ve depoya itilir. Ancak bundan sonra kullanıcı şifreyi çözer; hüküm
  açılır ve rapor üretilir.
- Açılıştan sonra motor, parametre, ölçüt, eşik, örneklem ya da evren değiştirilmez. Ek koşu yapılmaz.

### 2.5 Hata yönetimi
**Teknik geçersizlik koşulları:**
- **T1:** §2.2 hash eşleşmezliği ya da dondurma kaydıyla çalışan kod arasında hash farkı.
- **T2:** Veri (koşu öncesi). Onarılamayan CHECKSUM hatası; ya da birincil örneklemde BTC veya ETH saatlerinin >%1'i eksik; ya
  da K coinlerinin >%10'unda hiç veri yok.
- **T3:** Çalışma hatası. İstisna, NAV'da NaN/sonsuz, ya da koşunun tamamlanmaması.
- **T4:** Yerleşik değişmez ihlali. Her değişmez **tek bir nesneye** aittir (KC-09, K1-04, K1-11). Bir nesnenin
  değişmezi başka nesnede aranmaz. Sayısal tolerans: 1e-9 (göreli).
  - **T4-a, birim trend kitabı w^u** (MIMARI §3.3 adım 6–7). Kaldıraç, tavan, bant ve carry uygulanmadan önceki nesnedir.
    Değişmez: V(w^u) = max(√(w^uᵀΣ̂w^u), √(w^uᵀΣ₀w^u)) ≤ τ ve M̃_t ≤ M_max. Her koşuda (her L, A ve B) w^u üzerinde denetlenir.
    Bu nesne L'ye bağlı değildir. L = 1'de kaldıraçsız ve carry'siz temel koşunun ölçeğidir. MIMARI §3.3'teki güvenlik
    ölçeklemesi (V > τ ise w^u ← w^u·τ/V) çalışırsa bu ihlal değildir. Olay sayısı R5'te raporlanır. İhlal, ölçekleme
    sonrasında V > τ kalmasıdır.
  - **T4-b, carry birim kitabı w^C** (yalnız B; MIMARI §4.4 adım 1). Ölçekleme sonrası, ω_C ve L öncesi değişmez:
    max(√(w^Cᵀ Σ̂ w^C), √(w^Cᵀ Σ₀ w^C)) ≤ τ. MIMARI T4-b ile birebir aynı nesne ve eşiktir.
  - **T4-c, carry bloğu** (yalnız B; MIMARI §4.4 adım 3–6, §4.5 adım 0). ω_C·L uygulanmış, carry isim tavanı
    (short ≤ %1,0, long ≤ %1,5; V30 < 50M'de yarısı), yeniden nötrleme ve BTC hedge yeniden kurulumu sonrası
    (günlük, κ^C öncesi) nesne. Değişmez: V ≤ ω_C·L·τ. MIMARI'nin nihai hali carry nesnesine ek değişmez
    tanımlarsa (ör. kırpma sonrası hedge nötrlüğü, KC-04) o değişmez T4-c'ye aynen girer; bu belge onu yeniden
    tanımlamaz. MIMARI T4-c ile birebir aynı nesne ve eşiktir.
  - **T4-d, kaldıraçlı net hedef kitap w*** (MIMARI §3.4–3.6 ve B'de §4.5 sonu). Çözücü ve bant sonrası
    HedefKitap'tır. Değişmez ikilidir: (i) **tavan uyumu** — isim tavanları (B'de alt short %3,33, yani S4),
    brüt ≤ 2,0, S1 ≤ %20 NAV, S2 ≤ %20 NAV; çözücü katsayıları c_g, c₁, c₂, κ^C ∈ [0, 1]; (ii) **toplam risk
    kuralı** — V(w*) ≤ L·(1 + ω_C·𝟙_B)·τ (A'da sınır L·τ, B'de L·1,2·τ; L=1'de B'de %18). Bu nesnede tek başına
    V ≤ τ aranmaz: örnek, V(w^u) = %12, L = 2 ve tavanlar bağlamıyorsa V(w*) ≈ %24'tür; bu geçerli bir Kelly
    koşusudur ve toplam risk kuralını (ii) ihlal etmediği sürece T4 değildir. B'de trend %15'e ek carry toplamı
    %15'in üstüne taşıyabilir; bu da (ii)'yi ihlal etmediği sürece T4 değildir. **(i) ve (ii) BİRLİKTE aranır**
    (Codex doğrulama turu): (ii)'nin sağlanması (i)'den, ya da (i)'nin sağlanması (ii)'den muafiyet vermez; ikisi de
    ayrı, eş zamanlı denetlenen koşullardır. MIMARI T4-d ile birebir aynıdır.
  - **T4-e, muhasebe ve veri akışı** (gerçekleşen defter, tavan değil): NAV = nakit + Σ q_i·kapanış_i özdeşliği; P&L
    satırları toplamının (MIMARI §4.7, icra artığı dahil) NAV değişimine eşitliği, fark ≤ 1e-6 NAV; bakış-ileri bekçisinin
    tetiklenmemesi; funding işaret denetimi.
  - **T4-f, rejim-null yolları:** §3.5'teki N1–N6 null değişmezleri.
  - **T4 değil, R5:** gerçekleşen ve devreden defterin tavan aşımları ve hedefe ulaşılamayan günler. Gerçekleşen defter
    katılım sınırı yüzünden hedefin gerisinde kalabilir; bu hata değildir (MIMARI §3.5, §5.7).
  - **Toplam risk kuralı T4-d'nin (ii) koludur, ayrı bir madde değildir** (2. tur düzeltmesi: v1'de "ayrı bir tavan
    yoktur" deniyordu; MIMARI'nin 2. tur eklediği bağlayıcı toplam risk kuralı burada yansıtılmıştır). Gerçekleşen
    vol R7'de, kaldıraçlı vol Kelly tablosunda raporlanır.
- **T5:** Banka anlık görüntüleriyle rastgele 20 günlük parite tekrarında kritik hata.

**Hüküm açılmadan önce T3–T5 olursa:**
1. Hata, banka sonucu kullanılmadan, sentetik fikstür ya da D verisiyle başarısız olan bir testle gösterilir.
2. Düzeltme diff'i yayımlanır. D kuru koşu çıktıları, hatadan etkilenmeyen her satırda hash düzeyinde aynı kalmalı.
3. Parametre, eşik ve davranış değişmez; yalnız hata giderilir. Yeni motor hash'i kaydedilir.
4. Banka bütünüyle bir kez yeniden koşulur; yine kör. Deneme defterine "banka teknik yeniden koşu" satırı girer; N +1.
5. En fazla **1** teknik yeniden koşu. İkinci teknik geçersizlik → banka NOT_EVALUATED; bu mimari için kapanır.

**Hüküm açıldıktan sonra bulunan hata (her yönde aynı kural):**
- Hata banka dışı bir testle gösterilmeli. Düzeltilmiş koşu yapılır; iki sonuç da raporlanır.
- Düzeltme hükmü değiştirmiyorsa hüküm geçerlidir; düzeltme notu eklenir.
- Düzeltme hükmü değiştiriyorsa (RET→KABUL ya da KABUL→RET) sonuç **NOT_EVALUATED** olur. Mimari kapanır; ileri demoya
  gidilmez.
- "Düzeltme sonrası KABUL" yolu yoktur. Böylece hata avı sonucu yalnız bir yöne çeviremez.

**Sonuç beğenmeme hiçbir koşulda gerekçe değildir.** Eşik, parametre, örneklem ya da evren değişikliği yeni bir modeldir ve bu
bankada sınanamaz.

---

## 3. Hipotez, ölçütler ve eşikler

### 3.1 Koşu düzeni ve örneklem
- **Aday evren (banka):** mühürdeki uygun evren (200 coin) + BTC/ETH. PIT sıra kuralı MIMARI §2.3. Dönem içinde listelenen ve
  uygun evrende olmayan coinler yoktur (§5).
- **Sürekli koşu:** motor, ilk arşiv barından Z2 sonuna kadar tek ve kesintisiz koşar. Isınma MIMARI §2.4 kuralıyla: coin kendi
  ilk barından 90 gün sonra uygun olur. Pencere başına yeniden başlatma yapılmaz (Z2 ~85 gündür; 90 günlük ısınma onu boşaltır).
  Bkz. §10 madde 8.
- **T0_Z1** = max(BTC ilk barı, ETH ilk barı) + 92 gün, izleyen ayın 1'ine yuvarlanır. Kesin değer açılışta hesaplanır.
  Z1 değerlendirmesinin ~3,2 yıl olması beklenir.
- **Birincil örneklem:** **[T0_Z1, 2023-06-24 00:00 UTC)**. BTC/ETH'nin görülmüş 7 günü (mühür §4) bütün metriklerden düşülür.
- **Z2:** [2026-07-01, Z2_son). Z2_son = 2026-09-24 00:00 UTC (mühür damgasının UTC günü). Hüküm dışı teşhis; yalnız B9'da
  birincil örneklemle birlikte kullanılır.
- **D segmenti** [2023-07-01, 2026-07-01): görülmüş dönem; yalnız rapor.
- **Birincil ayar:** L = 1 (birim kitap), başlangıç NAV = **0,1M USDT**, maliyet 1×, delist uzlaşması h_L = %10 / h_S = %5,
  tahminci dondurulmuş olan. NAV bileşik işler.
- **Sharpe tanımı:** günlük basit NAV getirisinin ortalaması / std × √365. Risksiz oran 0.
- **Belirsizlik:** her Sharpe için durağan blok bootstrap (ortalama blok 20 gün, 2.000 çekiş, `tohum_banka`) %90 güven aralığı.
- **Maliyet çarpanı:** tanımı MIMARI §6'nın nihai halindeki tek tanımdır (ana oturum notu 3, K1-06). Bu belge tanımı
  tekrarlamaz. Her çarpan (1×, 2×, 3×) **tam yeniden koşudur**; karekök terimi ve katılım NAV'a bağlı olduğundan yeniden
  fiyatlama kullanılmaz.

### 3.2 Hipotez
H1: Dondurulmuş mimari M, birim riskte, maliyet ve funding sonrası, görülmemiş zaman diliminde, deneme sayısına göre
düzeltilmiş olarak pozitif Sharpe üretir.

**Birincil istatistik:** birincil örneklemde SR̂_net (L = 1, 1×, 0,1M). Çoklu test çıtası DSR'dir (B2, §3.3). B2'nin türü
(bağlayıcı ya da rapor) ve eşiği Adım 3'te §3.3 kuralıyla sabitlenir. Eski B1 eşiği (SR̂ ≥ 0,50) tablodaki her σ_SR'de SR₀'ın
altında kalır (en küçüğü 0,58). B2 bağlayıcıysa B1 bilgi taşımaz. Değeri R11'de raporlanır (K2-05).

**Eşik gerekçesi yalnız istatistiktir (K2-06).** Çıta, N, σ_SR ve kalibrasyondan gelir. Banka döneminin rejimine dair hiçbir
bilgi eşik gerekçesi değildir. Rejim yorumu yalnız §6'dadır.

### 3.3 Deflated Sharpe (B2)

**Deneme sayısı (K2-04, K2-09).**

    N = 159 (REV1) + N_v8,   N_v8 = Σ_satır max(1, varyant_sayisi)

- v8 defterinin bütün satırları girer (KARARLAR §2).
- **Defter düzeltmesi:** `A2-mikroyapi` ~144 hücrelik bir taramadan seçim yaptı; `A2-ml` 5 tahmin modeli sınadı. İkisi de
  varyant 0 kayıtlı. Ana oturum kilitten önce bu iki satırı 144 ve 5 olarak düzeltir. Düzeltilmezse bu belge N hesabında onları
  144 ve 5 sayar. Bu bir karar değişikliği değildir; KARARLAR "bütün satırlar" der.
- **Sayım kuralı:** alternatif şartname N'ye girer. Aynı şartnamenin alt kümesi, ölçeği ya da yeniden fiyatlanması girmez.
  Girmeyenler: maliyet ve NAV ızgarası, Kelly ızgarası, tek coin çıkarma, K-evren koşusu, rejim-null yolları, D90 bindirmeleri,
  demo NAV koşusu, lot filtresi koşusu. Giren: B ise bağımsız A koşusu (+1). Muhafazakâr istisna: banka teknik yeniden koşusu
  (+1).
- **HAR seçimi +2 (KC-08, Codex S-b).** MIMARI §1b iki varyantı (EWMA, HAR) karşılaştırır. Sayım kuralı max(1, varyant)
  olduğundan satır +2 sayılır; round-1'deki +1 hatalıydı.
- **Bugünkü değer:** 12 defter satırı; düzeltmeyle N_v8 = 10 + 144 + 5 = 159. `A4-sentez` ile 160. Kilide kadar eklenen her
  defter satırı sayılır (ör. Aşama 4b revizyon satırı, varyant 0 ise +1). Kilide kadar HAR seçimi +2. Dondurmaya kadar kapı
  +1 ve D doğrulama +1. B ise A ayrıştırması +1. Beklenen N_dondurma = 159 + 164…166 ≈ **323–325**. Kesin değer
  `DONDURMA.json`'a yazılır. Hüküm anındaki N, teknik yeniden koşu olursa +1'dir.
- **Ham N kullanılır; etkin N'ye indirilmez.** Denemeler korelasyonludur. Bu yüzden etkin bağımsız deneme sayısı ham N'den
  küçüktür ve ham N SR₀'ı büyütür, yani muhafazakârdır. Etkin N kestirimi bütün denemelerin getiri serilerini ister. REV1'in
  159 denemesi için bu seriler yoktur. Kestirim ayrıca serbest bir parametre açar. Denemeler arası heterojenlik σ_SR ile
  temsil edilir.

**Formül** (Bailey–López de Prado; seri bağımlılık düzeltmesi eklendi). SR̂: günlük Sharpe; T: birincil örneklem gün sayısı;
γ₃ çarpıklık, γ₄ basıklık (normal = 3); γ = 0,5772; σ_g = σ_SR / √365.

    SR₀ = σ_g · [ (1−γ)·Φ⁻¹(1 − 1/N) + γ·Φ⁻¹(1 − 1/(N·e)) ]
    η   = 1 + 2·Σ_{k=1}^{10} (1 − k/11)·ρ̂_k          (ρ̂_k: günlük net getirinin k gecikmeli otokorelasyonu; η < 1 ise η = 1)
    DSR = Φ( (SR̂ − SR₀)·√(T−1) / √( η·(1 − γ₃·SR̂ + ((γ₄−1)/4)·SR̂²) ) )

η, Sharpe tahmininin varyansına Bartlett ağırlıklı seri bağımlılık düzeltmesidir (Lo 2002 türü). Gecikme 10 gün sabittir.
Aşağı düzeltme (η < 1) yapılmaz. DSR = 0,50'de moment ve η terimleri etkisizdir; eşik 0,50'nin üstündeyse örneklem uzunluğu,
çarpıklık, basıklık ve bağımlılık kabul sınırına girer.

**Ne ölçtüğü (KC-08).** σ_SR, denemeler arasındaki yıllık Sharpe dağılımının std'sidir; örneklem Sharpe'ının standart hatası
(≈ 1/√3,2 ≈ 0,559) değildir. DSR = 0,50 yalnız SR̂ ≥ SR₀ demektir. Bu bir **performans çıtasıdır**, olasılıksal kanıt değildir.
DSR tek başına bütün seçimin ya da ölçüt setinin yanlış kabul oranını kontrol etmez. Birleşik yanlış kabul §3.7'de ayrıca
ölçülür.

**Duyarlılık tablosu (kalem-kâğıt).** Varsayımlar: N ≈ 323, T ≈ 3,2 yıl, SE ≈ 0,559, bağımsız ve yaklaşık normal getiri (η = 1,
γ₃ = 0, γ₄ = 3).

    Φ⁻¹(1 − 1/323) ≈ 2,74;  Φ⁻¹(1 − 1/(323·e)) ≈ 3,05;  SR₀ ≈ σ_SR·(0,423·2,74 + 0,577·3,05) ≈ 2,92·σ_SR
    DSR = d için gereken SR̂ ≈ SR₀ + Φ⁻¹(d)·0,559;   Φ⁻¹(0,75) = 0,674;  Φ⁻¹(0,90) = 1,282;  Φ⁻¹(0,95) = 1,645

| σ_SR | SR₀ (= DSR 0,50 çıtası) | DSR 0,75 için SR̂ | DSR 0,90 için SR̂ | DSR 0,95 için SR̂ | P(B2 geçer, d = 0,50 \| SR = 0) | P(B2 geçer, d = 0,50 \| SR = 1,0) |
|---|---|---|---|---|---|---|
| 0,20 | 0,58 | 0,96 | 1,30 | 1,50 | ≈ %15 | ≈ %77 |
| 0,30 | 0,88 | 1,25 | 1,59 | 1,80 | ≈ %6 | ≈ %59 |
| 0,50 | 1,46 | 1,84 | 2,18 | 2,38 | ≈ %0,5 | ≈ %21 |

Son iki sütun tek ölçüt olasılığıdır: Φ(−SR₀/0,559) ve Φ((1,0 − SR₀)/0,559). DSR 0,95 sütunu Codex'in canlı hesabıyla aynıdır
({1,50; 1,80; 2,38}). Tablo her N ve T için Adım 3'te N_kilit ve T_yıl ∈ {3,0; 3,5} ile yeniden hesaplanır ve R16'ya girer.

**Bağlayıcı sayının seçim kuralı (Adım 3; D'ye bakılmadan; ASAMA4B_KARAR §1 madde 2).** Bu belge önsel tek bir σ_SR ya da
tek bir DSR eşiği yazmaz. Kural ve prosedür aşağıdadır. Hangi sayının bağlayıcı olduğu Adım 3'te bu kuralla belirlenir ve
`KILIT.json`'a ve `DONDURMA.json` `dsr` alanına yazılır.

1. **σ_SR_bağ.** Adım 3'te bir betik REV1 deneme kayıtlarını okur. Betiğin kodu bu kural yazıldıktan sonra ve REV1 kayıtlarına
   bakılmadan yazılır.
   - Kullanılabilirlik koşulu: teknik hata olarak işaretlenmemiş, en az 1 yıllık günlük (ya da daha sık) getiri
     serisinden hesaplanmış yıllık net Sharpe'ı olan **en az 30** deneme. Farklı sıklıktaki Sharpe'lar √(yıllık dönem
     sayısı) ile yıllıklanır. Aynı denemenin birden çok satırı varsa son satır alınır.
   - Koşul sağlanırsa σ̂_REV1 bu Sharpe'ların örneklem std'sidir (n − 1). **σ_SR_bağ = min(max(σ̂_REV1; 0,20); 0,50).**
     Kırpma sınırı tablonun uçlarıdır. Tek bir aykırı kayıt çıtayı tablonun dışına taşıyamaz.
   - Koşul sağlanmazsa **σ_SR_bağ = 0,30** (tablonun ortası). Bu durumda raporda "σ_SR = 0,30 varsayımdır, doğrulanmadı"
     cümlesi zorunludur.
   - v8 defter satırlarının D Sharpe'ları σ_SR kestirimine girmez. Bunlar D performansıdır ve çoğu hücre düzeyinde kayıtlı
     değildir.
   - Görülmüş bilgi: REV1 kayıtları v8 bankasıyla ya da v8'in D P&L'iyle ilgili değildir. Ancak REV1 sonuçları ekipçe
     kabaca bilinmektedir (Ek B: "Zayıf evet"). Kırpma, bu bilginin etkisini tablonun aralığıyla sınırlar.
2. **SR₀ ve güç koşulu.** SR₀, σ_SR_bağ ve N_kilit ile hesaplanır. Düzey 1'de (§3.7) bütün ayarların ortalaması olarak
   P(B2 geçer, d = 0,50 | SR = 1,0) bulunur.
   - Bu değer **≥ 0,25** ise **B2 bağlayıcıdır.**
   - **< 0,25** ise B2 **rapora iner (R16)**. Gerekçe: çıta önsel Sharpe bandının tamamen üstündedir; test fiilen
     geçilemez. Round-1'deki "0,90 eşiği fiilen geçilemez" gerekçesinin aynısıdır. Tablodaki kaba değerlerle σ_SR_bağ = 0,50
     bu dala düşer; 0,20 ve 0,30 düşmez.
3. **d\* (B2 bağlayıcıysa).** d ∈ {0,50; 0,75; 0,90; 0,95} içinden, Düzey 1'in **bütün** ayarlarında birleşik
   P(KABUL | SR = 0) ≤ %5 sağlayan **en küçük** d seçilir. Birleşik ölçüt seti burada B2 = d ile kurulur. Hiçbir d
   sağlamazsa önce §3.7'nin tek önceden yazılı ayarı (B3 ×2 ve B4 eşiği 0,40) uygulanır ve arama tekrarlanır. Yine
   sağlanmazsa kilit bekler.
4. **B2 raporsa:** birleşik P(KABUL | SR = 0) ≤ %5 B2 olmadan sağlanmalıdır. Sağlanmazsa aynı tek ayar uygulanır; yine
   sağlanmazsa kilit bekler.
5. **Hüküm anında** SR₀, N_hüküm ile yeniden hesaplanır. σ_SR_bağ, B2 türü ve d* değişmez.

Bu kurallar bankayı açmadan ve D'ye bakmadan uygulanır. Böylece "açık bırakma" değildir: kural, prosedür ve duyarlılık tablosu
bugün yazılıdır; kilitte yalnız kuralın mekanik çıktısı sabitlenir.

### 3.4 Ölçüt tablosu
"B": bağlayıcı; hepsi geçilirse KABUL, biri kalırsa RET. "R": yalnız rapor. Aksi yazılmadıkça birincil ayar ve birincil örneklem.
v1 kimlikleri korundu; tür değişenler işaretli.

| # | Ölçüt | Tanım | Eşik | Tür |
|---|---|---|---|---|
| B2 | DSR | §3.3 (σ_SR_bağ, η düzeltmeli) | ≥ d* = **0,90** (Adım 3; §3.7 Kalibrasyon sonuçları) | B (Adım 3'te bağlayıcı çıktı) |
| B3 | Maliyet stresi | MIMARI §6 çarpanı, ×2 ve ×3 tam koşu | ×2'de SR ≥ 0,30; ×3'te SR > 0 | B |
| B4 | En iyi yıl hariç | Z1 dilimlerinden {2020, 2021, 2022, 2023H1} toplam log getirisi en yüksek olanı çıkarılır; kalan günlerin SR'ı | ≥ 0,30 | B |
| B5 | En iyi 3 epizot payı | Tanım aşağıda | e_B5 > %60 çıktı (Adım 3) | **R** (Adım 3'te rapora indi) |
| B6 | Rejim dilimleri | SR, getiri, vol, MDD: 2020 [T0_Z1, 2021-01-01), 2021, 2022, 2023H1 [2023-01-01, 2023-06-24), Z2 | Z1'in 4 diliminden en az k_B6 = **2**'sinde SR > 0 (Adım 3) | B (Z2: R) |
| B7 | Rejim-null | §3.5 (getiri uzayında blok karıştırma) | SR̂ > null dağılımının q95'i (§3.5.6 kuantil tanımı; 3. revizyon) | B |
| B8 | Fiyat bileşeni | Funding hariç, maliyet dahil P&L serisinin SR'ı (MIMARI §4.7 "trend fiyat" − maliyet; B'de bütün fiyat satırları) | > 0 | B |
| B9 | Görülmemiş coinler | §3.6; yalnız [T0_Z1, 2023-06-24) ∪ Z2 | K alt katkısının SR'ı > 0 | B |
| B10 | Tek coin çıkarma | Ana koşuda mutlak net katkısı en büyük 10 alt, aday listeden tek tek çıkarılıp yeniden koşulur | e_B10 = 0,80 > 0,40 çıktı (Adım 3) | **R** (Adım 3'te rapora indi; BTC/ETH çıkarma: R) |
| B11 | DD biçimi | Birincil seri gerçekleşen vol %15'e doğrusal ölçeklenir (tavanlar yok sayılır; biçim ölçüsü) | MDD ≤ %30 | B |
| R1 | NAV × maliyet ızgarası | 0,1M / 1M / 5M × 1×/2×/3× (9 tam koşu); kapasite eğrisi. 1M ve 5M satırları "kapasite" etiketlidir. **Gecikme maliyeti:** gerçek yol ile anlık tam dolum yolunun NAV farkı. Karekök teriminin ima ettiği ortalama bps (K1-08) | — | R |
| R2 | Beta ayrıştırması | r = α + β_BTC·r_BTC + β_D·r_D + ε; r_D = evren altlarının eşit ağırlıklı getirisi − r_BTC. Pozisyon bazında β_i·r_BTC ve artık katkı. Dilim bazında | — | R |
| R3 | Long-beta karşılaştırması | Aynı PIT evrende 1/σ̂ ağırlıklı pasif long kitap, aynı maliyetle, aynı gerçekleşen vol'e ölçekli. SR farkı, korelasyon, α ve t | — | R |
| R4 | REV1 ile korelasyon | Günlük ve 30 günlük getirilerde; stres günlerinde ayrıca. REV1 serisi olan dönemlerde (§11 soru 6) | — | R |
| R5 | Tavan bağlama ve gerçekleşen aşım | Hedef kitapta: isim, brüt, S1, S2, (B'de S4) bağlama gün oranı. Birim kitapta (w^u): M_max bağlama ve V > τ güvenlik ölçeklemesi gün oranı (T4-a). **Gerçekleşen + devreden kitapta** S1/S2 değeri: aşım günü oranı, en büyük aşım. Hedefe ulaşılamayan gün oranı (K1-04) | — | R |
| R6 | Devir ve maliyet | Yıllık tek yön devir, maliyet payı, funding payı, doldurulan funding kaydı, katılım gecikmesi, icra artığı | — | R |
| R7 | Gerçekleşen vol / birim | Gerçekleşen vol'ün τ'ya oranı; tahminci için RV/σ̂² q50/q95/q99 | — | R |
| R8 | B ayrıştırması | Yalnız M = B: bağımsız A koşusu; sanal bacak satırları; carry funding/fiyat/hedge satırları; her Kelly L'si için carry bacağının gerçekleşen BTC ve alt betası (K1-09) | — | R |
| R9 | Delist uzlaşma senaryoları | Gerçekten 30 gün işlem görmeyen pozisyonlarda h_L = %50 ve %90 | — | R |
| R10 | Z2 ve D segmenti | Tam metrik seti; hüküm dışı | — | R |
| R11 | Birincil Sharpe (eski B1) | SR̂, %90 GA; 0,50'yi geçip geçmediği bilgi olarak | — | R |
| R12 | Kanal stresleri (eski B12) | D90-1/2/4 (long çöküş), SQ-1/2/4 (short sıkışma), DM-1 (eşzamanlı çoklu ölüm) altında SR ve MDD (§5.4) | — | R; kullanıcı Adım 1'de bağlayıcı seçerse B12 (§5.5) |
| R13 | Lot filtresi etkisi | Lot yuvarlama kapalı tek koşu ile birincil koşunun farkı; bugünkü adımın erken fiyat düzeyindeki nominali (K1-20.14) | — | R |
| R14 | Demo NAV koşusu | NAV 5.000 USDT, L = 1, tek koşu: lot/minNotional altında kalan emir oranı; B'de BTC hedge'inin sıfıra yuvarlandığı gün oranı (K1-18) | — | R |
| R15 | B9'un D kısmı | K-evren koşusunun D segmenti; görülmüş zaman | — | R |
| R16 | DSR duyarlılığı | σ_SR ∈ {0,20; 0,30; 0,50}, σ̂_REV1 (varsa, kırpılmamış) ve σ_SR_bağ için SR₀ ve DSR; η = 1 ve η kestirimli iki hali; N_hüküm ±%20. B2 rapora indiyse DSR burada raporlanır | — | R |
| R17 | Rejim-null tanıları | §3.5: ortak eşleşme payı; sentetik ve gerçek yolda maske günü, dolgu saati, borsa çapı boşluk ve evren üyeliği sayıları (ortalama, q5, q95) | — | R |

Teknik kabul (hükümden önce): §2.5'teki T1–T5 koşullarının hiçbiri yok.

**B5 epizot tanımı (K1-20.11).**
- M = A: epizot, bir coinde net pozisyonun işaretinin kesintisiz sabit kaldığı dönemdir; 0'a inme ya da işaret değişimi bitirir.
  Epizot P&L = fiyat + funding − maliyet. Pay = en iyi 3 epizot P&L'i / toplam net P&L.
- M = B: epizot ve pay, trend sanal bacağında (MIMARI §4.7 sanal pozisyonları) hesaplanır; payda trend sanal bacağının net
  P&L'idir. Oran tutarlı kalır. Carry bacağı için aynı ölçü R8'de raporlanır.
- Toplam net P&L ≤ 0 ise B5 kalmış sayılır.

### 3.5 Rejim-null (B7) — 2. turda yeniden yazıldı (KC-01)

**Soru.** SR, rejimde bulunmanın kendisinden mi, yoksa zamanlamadan mı geliyor? B7 zamanlamayı ister. Null, her dilimin
coin bazında sürüklenmesini, oynaklığını, saatlik getiri dağılımını, funding düzeyini ve (büyük ölçüde) kesitsel eş
hareketini korur. 5 günden uzun zaman sıralamasını bozar.

**Bağlayıcı ilke.** Karıştırma **getiri uzayında** yapılır. Ham OHLC fiyat düzeyleri hiçbir yerde taşınmaz. Sentetik fiyat,
taşınan log-getirilerden bir çapadan zincirlenerek yeniden kurulur. Bu kural Codex'in örneğini kapatır. Biri 100, öteki 200
düzeyinde, kendi içinde sabit iki blok ham fiyatla yan yana konursa sınırda %100 ya da −%50 yapay getiri doğar. Getiri
uzayında sınır getirisi, o blok ilk barının **gerçek** önceki kapanışa göre getirisidir. Gerçekte bu iki blok arasında bir
sıçrama olmuşsa o sıçrama tek bir gerçek getiri olarak bir kez taşınır. Olmamışsa sınır getirisi 0'dır. Yapay getiri doğmaz.

**3.5.1 Dilimler ve bloklar.**
- Dilimler: j ∈ {2020 = [T0_Z1, 2021-01-01), 2021, 2022, 2023H1 = [2023-01-01, 2023-06-24)}; dilim j = [S_j, E_j).
- Her dilim S_j'den başlayarak ardışık 120 saatlik (5 × 24 h, 00:00 UTC hizalı) bloklara bölünür: b = 1…B_j. Dilim sonundaki
  120 saatten kısa artık blok **kuyruk bloğudur**; yerinde kalır, karıştırılmaz.
- Yol p ∈ {1…500} için ortak permütasyon π_{p,j}, B_j tam blok üzerinde tekdüze rastgele seçilir. Tohum
  hash(tohum_banka, p, j). Sentetik konum k, gerçek blok π_{p,j}(k)'nın içeriğini alır. Blok içi saat sırası ve göreli saatler
  korunur: konum k'nın r'inci saati, gerçek bloğun r'inci saatidir.

**3.5.2 Yaşam döngüsü (listelenme ve ölüm).** Coin i için a_i gerçek ilk barının saati, d_i gerçek son barından sonraki saattir.
Coin hâlâ işlem görüyorsa d_i = ∞.
- **Y1, varlık ekseni korunur (2. tur: kesinlik düzeltildi, Codex doğrulama turu).** Coin i'nin giriş (listelenme), 90 günlük
  ısınmanın bitişi (MIMARI §2.4) ve çıkış (son bar) saatleri, ve dilim içindeki **toplam bar sayısı** (yaşam içi boşluklar
  dahil toplam saat − boşluk saati), gerçek yoldakiyle birebir aynıdır; bunlar mutlak takvim saatiyle çakışır (dilimler
  takvim sırasıyla eklendiği ve sınırları sabit olduğu için). Sentetik zamanın her anında coinin **kendi ilk barından bu
  yana geçen gün sayısı** gerçek yoldakiyle aynıdır. **Bu, yaşam içi tekil boşlukların TAM saatinin de aynı kalacağı
  anlamına gelmez:** bir boşluk, ait olduğu blokla birlikte taşınır (aşağıdaki madde); blok farklı bir sentetik konuma
  giderse boşluk da o konumun göreli saatinde görünür. Sayı ve giriş/çıkış korunur; ince tanecikli gap konumu korunmaz. Bu
  kasıtlıdır (N3, §3.5.7, bu ayrıma göre yeniden yazıldı).
- **Y2, kenar blokları sabit.** Coin i için a_i'yi içeren blok ve d_i − 1'i içeren blok o coin için **kenar bloktur**. Kenar
  bloklar coin i için gerçek konumlarında kalır. Böylece listelenme barı her zaman coinin ilk sentetik barıdır. Ölüm barı her
  zaman son sentetik barıdır. Blok içi kısmi yaşam korunur.
- **Y3, tam bloklar ortak permütasyonla.** Coin i'nin dilim j'deki tam blokları R_i: coinin yaşamının tamamen kapsadığı ve
  kenar olmayan tam bloklardır. Y1 gereği coin i bu konumlarda (K_i = R_i kümesi) barlıdır. Atama şöyledir:
  - k ∈ K_i ve π(k) ∈ R_i ise coin i konum k'da gerçek blok π(k)'yı alır (**ortak eşleşme**; kesitsel eş hareket korunur).
  - Kalan konumlar U_i = {k ∈ K_i : π(k) ∉ R_i} ve kalan bloklar W_i = R_i \ {π(k) : k ∈ K_i, π(k) ∈ R_i} eşit sayıdadır
    (π birebir olduğundan). U_i artan sırayla, W_i ikincil permütasyonla karıştırılmış sırayla eşlenir. İkincil
    permütasyonun tohumu hash(tohum_banka, p, j, anonim kimlik_i).
  - Dilim boyunca yaşayan coinlerde (BTC ve ETH dahil) U_i boştur; bu coinler tamamen ortak permütasyondadır.
  - Sonuç: her coin, dilimdeki tam bloklarının **tamamını, her birini bir kez** alır. Coinin dilim sürüklenmesi korunur.
    Ortak eşleşme payı (Σ_i |K_i \ U_i| / Σ_i |K_i|) R17'de raporlanır.
- **Yaşam içi boşluklar** (eksik bar, donma, 30 günlük delist beklemesi) bloğun içinde göreli saatiyle taşınır. Boşluğun yeri
  blokla birlikte değişir, uzunluğu değişmez.

**3.5.3 Fiyatın yeniden kurulması (yeniden bazlama).** Gerçek yolda coin i'nin var olan her barı h için C⁻_h, coinin h'den
önceki son var olan barının gerçek kapanışıdır. Coinin ilk barında (h = a_i) C⁻_h := O_h alınır.

    ρᴼ_h = ln(O_h / C⁻_h),  ρᴴ_h = ln(H_h / C⁻_h),  ρᴸ_h = ln(L_h / C⁻_h),  ρᶜ_h = ln(C_h / C⁻_h)

Sentetik saat k, gerçek saat h(k)'ye eşlenir (3.5.1–3.5.2). Ĉ⁻_k, coinin k'dan önceki son var olan **sentetik** barının
kapanışıdır:

    Ô_k = Ĉ⁻_k · exp(ρᴼ_h(k)),  Ĥ_k = Ĉ⁻_k · exp(ρᴴ_h(k)),  L̂_k = Ĉ⁻_k · exp(ρᴸ_h(k)),  Ĉ_k = Ĉ⁻_k · exp(ρᶜ_h(k))

- **Çapa.** Dilim j'nin başındaki Ĉ⁻, coinin önceki sentetik dilimdeki son sentetik kapanışıdır. İlk dilimde (2020) çapa,
  T0_Z1 öncesindeki gerçek ısınma geçmişinin son gerçek kapanışıdır. Dilim içinde listelenen coinde ilk bar Y2 gereği
  gerçek listelenme barıdır; çapası Ĉ⁻ := O_{a_i} (gerçek açılış).
- **Sonuç.** Sentetik yolun her barı, gerçek bir barın önceki kapanışa göre açılış, yüksek, düşük ve kapanış getirisini
  taşır. H ≥ max(O, C), L ≤ min(O, C) ve O = H = L = C eşitlikleri korunur (donma ölçütü (b) aynı çalışır). Dilim içi toplam
  log getiri korunduğundan ve ilk çapa gerçek olduğundan, **her dilim sonunda sentetik kapanış gerçek kapanışa eşittir**
  (tümevarım). Fiyat düzeyi yalnız dilim içinde gerçekten sapar.
- Günlük barlar, günlük kapanış ve bütün sinyal girdileri sentetik saatlik barlardan MIMARI §2.2 ile kurulur.

**3.5.4 Hacim ve funding.**
- **Hacim** (1h `quote_volume`, USDT) barla birlikte değişmeden taşınır. Birim USDT olduğundan fiyat düzeyinden
  bağımsızdır ve yeniden bazlanmaz. Motorun kullandığı bütün hacim büyüklükleri (V60, V30, V1h30, V1h7, Q_max, donma (a))
  USDT hacimdir (MIMARI §2.1, §3.7).
- **Funding kaydı** (damga t_f, oran r) damganın düştüğü bloğa aittir. Blok başına (00:00) düşen kayıt o bloğundur. Kayıt,
  blok içi göreli saatiyle taşınır: t̂_f = t_f − başlangıç(gerçek blok) + başlangıç(sentetik konum). Oran boyutsuzdur ve
  değişmez. Nakit, motor tarafından **sentetik** pozisyon ve sentetik mark vekiliyle hesaplanır: −q̂_i·mark̂_i·r (MIMARI
  §5.1, §5.3). Bloklar 00:00'da başladığı ve borsa aralıkları (1h, 4h, 8h) 24 saati böldüğü için uzlaşma saatlerinin fazı
  korunur. Bitişik iki blok farklı aralık rejimindeyse bu, gerçek bir aralık geçişi gibi işlenir (MIMARI §2.5(c), §2.6).
- **Eksik funding dolgusu** gerçek yoldan taşınmaz. Motor dolguyu sentetik kayıtlardan kendisi üretir (Δ_i ve r*_i sentetik
  son 30 günden). Dolgu nakdi sentetik pozisyonla yazılır.

**3.5.5 Evren üyeliği, maske ve hijyen: sentetik yoldan günlük yeniden hesap.** Motor sentetik yolda **üretim modunda**
koşar: gorunum sentetik barlardan, hacimden ve funding kayıtlarından kurulur. Bütün türetilmiş durum, gerçek koşudakiyle
aynı takvimle sentetik yoldan yeniden hesaplanır. Bu durum aylık evren (V60 sırası, taban, histerezis; MIMARI §2.3), günlük
uygunluk, donma/delist maskesi (a)–(d), maskeden dönüş, borsa çapı boşluk, eksik funding olayı ve carry evrenidir. **Gerçek
koşudan hiçbir maske, bayrak ya da üyelik taşınmaz.** Round-1'deki "bayraklar blokla taşınır, yeniden tetiklenmez" kuralı ve
"yeniden tetik = 0" değişmezi kaldırıldı. Codex'in belirttiği gibi taşınan maske önceki sentetik günlerle çelişebilir. "Tetik
= 0" da yeniden hesabı kapatmanın sonucudur, geçerlilik kanıtı değildir. Hijyen kuralları stratejinin parçasıdır; null'da
kapatılırsa başka bir strateji sınanır. Blok sınırında sentetik geçmişin kendisinden doğan tetikler geçerlidir. Sentetik ve
gerçek yoldaki tetik sayıları R17'de karşılaştırılır.
- **MIMARI ile ilişki.** MIMARI §5.1 "dış bayrak modu" kancasını banka null'u için isteğe bağlı bırakır ("kullanabilir").
  Banka bu modu **kullanmaz**. Null, motorun üretim modundaki aynı `hedef_agirlik → bant → lot_yuvarlama → emir_zinciri`
  zinciriyle koşar (§10 madde 12).
- Lot yuvarlama ve minNotional birincil koşudaki aynı sembol filtresi tablosuyla uygulanır. Sentetik fiyat düzeyi dilim içinde
  gerçekten sapabildiği için lot etkisi yol başına biraz değişir. Ölçeği R13'tür.

**3.5.6 Koşu ve istatistik.**
- Sentetik yol, T0_Z1 öncesinin gerçek (karıştırılmamış) ısınma geçmişiyle başlar. Karıştırılmış dilimler takvim sırasıyla
  art arda eklenir. Dilim sınırında 84 günlük sinyal geçmişi ve bütün EWMA durumları önceki sentetik dilimden gelir. Yol
  2023-06-24'te biter.
- Dondurulmuş motor her yolda baştan koşar: birincil ayar (L = 1, 1×, 0,1M), aynı M. 500 yol.
- Null istatistiği SR̂^null_p, birincil istatistikle aynı tanımla ve aynı takvim günlerinde hesaplanır. BTC/ETH'nin görülmüş 7
  günü aynı takvim konumlarında düşülür.
- B7: SR̂ > q95. n null değerinde q_α, sıralı değerlerin ⌈α·n⌉'inci elemanıdır (n = 500, α = 0,95 → 475'inci). 2. turun q90
  eşiği ve Düzey 2 ayar kuralı 3. revizyonda kaldırıldı (§0.2, §3.7).

**3.5.7 Null değişmezleri (T4-f; her yol, her coin, her dilim).** Açık grupta (`denetim/`) yazılır; performans içermez.
- **N1, getiri permütasyonu:** sentetik (ρᴼ, ρᴴ, ρᴸ, ρᶜ) dörtlülerinin çoklu kümesi gerçek dörtlülerin çoklu kümesine eşittir.
  Sıralı listelerin hash'i karşılaştırılır.
- **N2, dilim sürüklenmesi ve çapa:** Σρᶜ sentetik = Σρᶜ gerçek (göreli tolerans 1e-9). Her dilim sonunda sentetik kapanış =
  gerçek kapanış.
- **N3, yaşam döngüsü (Codex doğrulama turunda kesinleştirildi):** coin başına, dilim içi **toplam bar sayısı** gerçek
  yoldakiyle aynıdır. İlk ve son bar saatleri (mutlak takvim) aynıdır. Kenar bloklar yerindedir. **Bu, yaşam içi tekil
  boşlukların hangi tam saatte göründüğünü denetlemez** — boşluk bloğuyla birlikte taşınabilir (§3.5.2 Y1); denetlenen
  yalnız sayıdır (toplam bar sayısı ve dolayısıyla toplam boşluk sayısı). Bir gap'in taşınması N3 ihlali değildir.
- **N4, hacim ve funding:** quote_volume çoklu kümesi, funding oranı çoklu kümesi ve funding kaydı sayısı gerçek yoldakiyle
  aynıdır.
- **N5, yapay sıçrama yok:** sentetik max |ρᶜ| = gerçek max |ρᶜ|. N1'den çıkar; ucuz ayrı denetimdir.
- **N6, sayısal:** bütün sentetik fiyatlar pozitif ve sonludur.
Biri ihlal edilirse T4'tür (§2.5).

**Bilinen sınırlar.**
- Dilim içi sürüklenme korunduğundan 42–84 günlük ufukların değerinin bir kısmı null'da da kalır. B7 gerçek bir trendi
  reddetmeye yatkın olabilir. q95 eşiği (3. revizyon) bu eğilimi artırır. Gücü §3.7 Düzey 2-b'de kabaca ölçülür
  (betimsel).
- Y3'ün ikincil eşlemesiyle yerleşen bloklarda (dilim içinde listelenen ya da ölen coinler) kesitsel eş hareket bozulur.
  Ortak eşleşme payı R17'dedir.
- 5 günlük blok içindeki kısa vadeli ters dönüş ve momentum korunur. Blok uzunluğu dondurulmuştur.

### 3.6 Görülmemiş coinler (B9)
- **K-evren koşusu:** aynı dondurulmuş sistem; aday liste = 80 K coini + BTC/ETH (kural gereği sabit). Motor sürekli koşar
  (ısınma §3.1).
- **B9 ölçüsü (K2-09):** K alt katkısı serisi = K altlarının günlük fiyat + funding − maliyet katkısı / NAV. Bağlayıcı pencere
  yalnız görülmemiş zamandır: [T0_Z1, 2023-06-24) ∪ Z2. Eşik SR > 0. D segmenti R15'tir; D zamanında K coinleri tasarımı
  biçimlendiren D coinleriyle aynı piyasa faktörünü paylaşır.
- **Güç (kaba):** ~3,4 yılda SE ≈ 0,54. Gerçek SR 0,5 ise geçme olasılığı ≈ Φ(0,93) ≈ %82; gerçek SR 0,3 ise ≈ %71.
- Ana koşuda K coinlerinin katkısı ve coin-ay sayısı ayrıca raporlanır. 15 isimli evrende bu katkı birkaç coin-aya inebilir.

### 3.7 Sentetik kalibrasyon (Adım 3; kilitten önce) — 2. turda donduruldu (KC-02)
Amaç: σ_SR_bağ, B2 türü ve d* (§3.3), e_B5, k_B6 ve e_B10'u P&L'e ve banka verisine bakmadan sabitlemek. Ayrıca ölçüt
setinin birleşik yanlış kabul oranını ve gücünü ölçmek (K2-05, KC-02). 3. revizyondan (§0.2) beri B7 kuantili q95'e sabittir;
B7 dahil birleşik yanlış kabul üst sınırla (Düzey 2-a), B7'nin gücü betimsel olarak (Düzey 2-b) ölçülür.

**Sıra ve körlük.** Adım 3, Adım 1'den (bütün kullanıcı soruları yanıtlandı) ve Adım 2'den (HAR seçimi hash'lendi) **sonra**,
Adım 4 kilidinden **önce** koşar. Girdi yalnız aşağıdaki parametrik üreteçler, dondurulmuş motor kodu ve §3.3'ün REV1 Sharpe
std'sidir. D verisi, D P&L'i, D performans çıktısı ve banka verisi kullanılmaz. Bu noktaya kadar da hiçbiri üretilmemiştir
(§1.2). Aşağıdaki her üreteç parametresi, ızgara değeri, tohum ve eşleme bu belgede dondurulmuştur. Kalibrasyon kodu bunları
okur, değiştirmez. Kullanıcıya kalibrasyon çıktısına bağlı seçim sorulmaz. Tek istisna §1.2'deki "kilit bekler" dalıdır.
Üreteç kodu, parametre dosyası ve çıktı kilit paketine girer.

**Tohum.** tohum_kal = int(sha256("v8_asama4b_kalibrasyon")[:16], 16) mod 2³². Her ayar ve yol için alt tohum
hash(tohum_kal, düzey, ayar_no, yol_no). tohum_banka kullanılmaz; dondurmadan önce bilinmez. **hash tanımı (3. revizyon,
Codex T10):** hash(x₁, …, x_k) = SHA-256 özetinin ilk 8 baytı, büyük uçlu tamsayı olarak; özetlenen bayt dizisi
`json.dumps([x₁, …, x_k], separators=(',', ':'), ensure_ascii=True)`'nin UTF-8 halidir; x'ler tamsayı ya da ASCII
dizedir. Her alt tohum `numpy.random.Generator(PCG64(tohum))` başlatır; numpy sürümü ortam kimliğine girer. Bir
üreteç çağrısının çekiş sırası kodda sabittir (coinler numara sırasıyla, günler ve saatler takvim sırasıyla).

**Düzey 1 — P&L üreteci (B2–B6, B8–B11).** Birim ölçekli bir getiri modeli. Sharpe ölçekten bağımsızdır; B11 için ölçek
ayrıca verilir.

- **Izgara (7 boyut, 2⁷ = 128 ayar, ayar başına 2.000 yol):**

| Boyut | Değerler | Gerekçe |
|---|---|---|
| T_yıl (yol uzunluğu) | 3,0; 3,5 yıl | T0_Z1 kesin bilinmediği için iki uç |
| ℓ_e (ortalama epizot) | 30; 60 gün | 14/42/84 ufuklu sinyalin yön değişim ölçeği |
| s (epizot çarpıklığı) | 0,75; 1,25 | Orta ve güçlü trend konveksitesi |
| ρ_f (hatlar arası ortak faktör) | 0,3; 0,6 | Düşük ve yüksek kesitsel eş hareket |
| δ (1× maliyet sürüklemesi) | 0,05; 0,10 Sharpe | Düşük ve yüksek devir |
| φ (epizot genliği, aşağıda) | 0,5; 1,5 | Yaygın küçük kazanç ve az epizotta yoğun kazanç uçları |
| g (funding bileşeninin işareti) | −1; +1 | B8'in iki yönü: fiyat payı funding kadar büyük ya da küçük |

- **Hatlar.** J = 15 hat, eşit risk katkısı (ters-vol ağırlık). Hat j'nin t günündeki fiyat P&L'i:

      x_{j,t} = μ_{j,e(j,t)} + ε_{j,t}
      ε_{j,t} = √ρ_f · u_t + √(1−ρ_f) · v_{j,t},   u_t, v_{j,t} ~ i.i.d. √(1/2)·t₄   (birim varyans; ν = 4)

- **Epizotlar.** Her hattın günleri ardışık epizotlara bölünür. Uzunluk i.i.d. geometriktir: P(ℓ) = p(1−p)^{ℓ−1}, p = 1/ℓ_e.
  İlk epizot da aynı dağılımdan gelir. Epizot e'nin sabit günlük sürüklemesi:

      μ_{j,e} = m + a · (exp(s·Z_{j,e}) − exp(s²/2)),   Z_{j,e} ~ i.i.d. N(0,1)

  Parantez içi terimin ortalaması 0'dır ve sağa çarpıktır. Çok sayıda küçük negatif, az sayıda büyük pozitif epizot üretir.
  std'si sd_s = √(exp(s²)·(exp(s²) − 1)) olur: s = 0,75'te ≈ 1,151; s = 1,25'te ≈ 4,240.
- **Genlik a (dondurulmuş formül).** Ortalama uzunluktaki bir epizotta birikmiş sürüklemenin std'si, aynı sürede birikmiş
  gürültünün std'sinin φ katıdır:

      a · sd_s · ℓ_e = φ · √ℓ_e   ⇒   a = φ / (sd_s · √ℓ_e)

  Gerekçe: epizot yoğunlaşmasını (B5) ve tek hat bağımlılığını (B10) belirleyen boyutsuz büyüklük bu orandır. φ = 0,5'te
  kazanç yaygındır; φ = 1,5'te birkaç epizot baskındır. Codex'in "küçük a / büyük a" senaryosunun iki ucu ızgaradadır. Eşik
  kuralları iki ucu da sağlamak zorundadır.
- **Maliyet ve funding (deterministik, hat başına eşit).** Fiyat bileşeninin portföy günlük std'si:

      σ_P = √( ρ_f + (1−ρ_f)/J + a²·sd_s²/J )

  1× maliyet her hatta günlük K = δ·σ_P/√365; ×2 ve ×3'te 2K ve 3K. Funding her hatta günlük F = g·0,05·σ_P/√365.
- **Portföy ve hedef Sharpe.** X_t = (1/J)·Σ_j (x_{j,t} + F − K). m, net yıllık Sharpe hedef değere eşit olacak biçimde kapalı
  formülle bulunur:

      m = SR_hedef · σ_P/√365 − F + K

  Sharpe tanımı §3.1'dekiyle aynıdır (günlük ortalama/std × √365). Böylece fiyat − maliyet bileşeninin Sharpe'ı
  SR_hedef − g·0,05'tir.
- **Epizot ve işaret.** Üreteçte hat getirisi pozisyonun P&L'idir. Pozisyon işareti ayrıca modellenmez. B5'in epizotları
  üreteçteki epizotlardır; sınırları bilinir. Epizot P&L'i = Σ (x + F − K) / J.

**Ölçüt eşlemesi (Düzey 1).**

| Ölçüt | Sentetik karşılık |
|---|---|
| B2 | X_t'nin SR̂'ı; §3.3 formülü; N = N_kilit, σ_SR = σ_SR_bağ; γ₃, γ₄, η yoldan kestirilir; T = yol gün sayısı |
| B3 | Maliyet 2K ve 3K ile X_t yeniden kurulur (aynı gürültü ve epizotlar) |
| B4 | Dilim uzunlukları: son üçü 365, 365, 174 gün; ilki 365·T_yıl − 904 (T = 3,0'da 191; T = 3,5'te 373 gün). Toplam log getirisi en yüksek dilim çıkarılır |
| B5 | Bütün hatların epizot P&L'lerinden en büyük 3'ünün toplamı / toplam net P&L; toplam ≤ 0 ise kalır |
| B6 | Aynı dört dilimde SR > 0 sayısı ≥ k_B6 |
| B8 | X_t − F serisinin SR'ı > 0 |
| B9 | K portföyü: aynı ayarla bağımsız üretilmiş Y_t; X^K_t = 0,7·X_t + √(1 − 0,49)·Y_t, sonra sabit kaydırmayla net SR = SR_hedef. SR > 0 |
| B10 | Mutlak net katkısı en büyük 10 hattın her biri tek tek, aynı ayarla bağımsız üretilmiş yeni bir hatla değiştirilir (sıra ikamesi). En büyük SR düşüşü < e_B10 |
| B11 | X_t yıllık vol %15'e ölçeklenir; bileşik NAV'ın MDD'si ≤ %30 |
| B7 | Düzey 1'de yok; Düzey 2-b (betimsel) |

**Eşik kuralları (her biri önceden yazılı; önce Düzey 1).** Referans sistem: gerçek SR_ref = 1,0 (net, yıllık). Gerekçe: trend
önsel bandının üst ucunun biraz üstündedir. σ_SR = 0,30'da B2 çıtasını (~0,88) aşar. Yardımcı ölçütler ana ölçütü geçebilecek
gerçek sistemleri kesmemelidir. SR_ref, σ_SR_bağ'dan bağımsız olarak 1,0'da sabittir.
- **e_B5:** 128 ayarın her birinde P(B5 geçer | SR_ref) ≥ 0,95 sağlayan en küçük eşik (yüzde puanına yukarı yuvarlanır).
  e_B5 > %60 çıkarsa ölçüt ayrım yapmıyor sayılır ve B5 rapora iner.
- **e_B10:** her ayarda P(B10 geçer | SR_ref) ≥ 0,95 sağlayan en küçük eşik (0,01'e yuvarlanır). e_B10 > 0,40 çıkarsa B10
  rapora iner.
- **k_B6:** her ayarda P(B6 geçer | SR_ref) ≥ 0,90 ise k_B6 = 3; değilse 2. (Kaba ön hesap: bağımsız dilimlerle SR_ref = 1,0'da
  P(≥ 3/4) ≈ 0,85. Kural büyük olasılıkla k_B6 = 2 verir. Bu durumda B6 zayıf bir filtredir; tek rejim bağımlılığını asıl B4
  ve B7 sınar.)
- **B2 türü ve d\*:** §3.3 kural 2–4. Bu adım e_B5, e_B10 ve k_B6 sabitlendikten sonra koşar.

**Birleşik yanlış kabul ve güç (Düzey 1).**
- Her ayarda P(KABUL | SR) hesaplanır: SR ∈ {0; 0,3; 0,5; 0,8; 1,0; 1,2}. Bağlayıcı ölçütlerin hepsi sabitlenmiş eşiklerle
  kullanılır; B7 hariç.
- Hedef: bütün ayarlarda P(KABUL | SR = 0) ≤ %5.
- Aşılırsa tek önceden yazılı ayar: B3'ün ×2 eşiği ve B4 eşiği 0,30'dan 0,40'a çıkar (§3.3 kural 3–4 ile aynı ayar). Yine
  aşılırsa kilit bekler ve durum kullanıcıya sunulur (§1.2 istisna dalı).
- **B seyreltmesi (rapor):** aynı üreteçte trend + carry: σ_C/σ_T = 1/3, ρ ∈ {0; 0,30}, SR_C ∈ {−0,3; 0; 0,3}. A ve B için
  P(KABUL | SR_T) eğrileri rapora girer. Kapı → A/B kullanıcı kararıyla sabittir (ASAMA4B_KARAR §1 madde 1). Eğriler karar
  girdisi değildir. ρ = 0,30'un kapı eşiğine etkisi CARRY belgesinin konusudur (KC-07).

**Düzey 2 — fiyat üreteci ve dondurulmuş motor (3. revizyon: B7 dahil birleşik yanlış kabulün üst sınırı ve B7'nin
betimsel gücü).** Kapı sonucu (M) Adım 5'te belli olur. Bu yüzden Düzey 2-a hem A hem B yapılandırmasıyla koşar; kural
iki sonucun muhafazakâr olanıyla uygulanır. Üreteç (aşağıdaki ilk yedi madde) 2. turdakiyle aynıdır.

- **Süre ve takvim.** 365 günlük ısınma + 3,2 yıllık değerlendirme. Değerlendirme dilimleri banka dilimlerinin uzunluklarıyla
  264, 365, 365 ve 174 gündür. Saatlik barlar.
- **Coinler.** 30 coin. c1 ve c2 BTC/ETH karşılığıdır: β = 1, σ_I = 0,010 günlük, her zaman evrende (MIMARI §2.3). c3–c30
  altlardır: β_i ~ U[0,6; 1,4], σ_I = 0,035 günlük. β_i coin başına bir kez çekilir ve yol boyunca sabittir.
- **Saatlik log getiri:**

      r_{i,h} = β_i · m_h + g_{i,d(h)}/24 + (σ_I/√24) · √(1/2)·t₄,     m_h = (σ_M/√24) · √(1/2)·t₄,   σ_M = 0,030 günlük

  Toplam yıllık vol altlarda kabaca %70–%100, c1/c2'de ~%60'tır. Gerekçe (mekanik): motorun σ tabanları (%20 sinyal, %20
  boyutlama, %30 carry) bu düzeyde her gün bağlamaz. Böylece ters-vol boyutlaması ve korelasyon matrisi gerçekten çalışır.
- **Trend bileşeni.** Günlük AR(1), gün içinde sabit:

      g_{i,d} = φ_H · g_{i,d−1} + √(1 − φ_H²) · κ · σ_tot,i · ζ_{i,d},   ζ ~ N(0,1),   φ_H = 2^(−1/HL),   HL ∈ {30; 90} gün

  σ_tot,i coinin günlük toplam vol'üdür. Durağan std(g) = κ·σ_tot,i. κ, g'yi bilen kâhin stratejinin coin başına günlük bilgi
  oranıdır. **κ ∈ {0; 0,0262; 0,0523}** ("yok", "orta", "güçlü") coin başına kâhin yıllık Sharpe'ı {0; 0,5; 1,0}'a karşılık gelir
  (κ·√365). Trend izleyici bunun bir kesrini yakalar.
- **OHLC.** O_h = C_{h−1}; C_h = O_h·exp(r_{i,h}); H_h = max(O_h, C_h)·exp(0,5·σ_h·|n₁|); L_h = min(O_h, C_h)·exp(−0,5·σ_h·|n₂|).
  σ_h saatlik toplam vol'dür, n ~ N(0,1). Başlangıç fiyatı 1,0. Lot yuvarlama kapalıdır (adım 0), minNotional 5 USDT.
- **Hacim (quote, USDT).** Coin başına günlük düzey log V̄_{i,d}, yarı ömrü 60 gün ve durağan std'si 0,5 olan AR(1)'dir.
  Merkez altlarda log-tekdüze [10M; 400M] USDT/gün, c1/c2'de 5.000M. Saatlik:

      V_{i,h} = (V̄_{i,d}/24) · exp(0,5·n_{i,h} − 0,125 + 0,3·(|r_{i,h}|/σ_h − 0,8))

  Gerekçe (mekanik): 20M tabanı ve 13 alt yuvası altlar arasında gerçek evren giriş-çıkışı üretir.
- **Yaşam döngüsü ve hijyen fikstürleri.** 6 alt değerlendirme içinde tekdüze rastgele bir günde listelenir. 3 alt tekdüze
  rastgele bir günde ölür (son 10 gününde hacim ×0,05; sonra bar yok). 2 alt 60 günlük bir aralıkta 4h funding aralığına geçip
  döner. Yol başına bir kez 12 saatlik borsa çapı boşluk vardır. Böylece §3.5.2–3.5.5 kuralları kalibrasyonda da çalışır.
- **Funding.** 8h damgalar (00/08/16 UTC). Oran r = 0,0001 + 0,00005·n, n ~ N(0,1) i.i.d. B'nin carry bacağı bu yüzden
  beklentide sıfır kenarlıdır.
- **Motor yapılandırması (3. revizyon).** Düzey 2'deki her koşu dondurulacak banka yapılandırmasıdır: birincil ayar
  (L = 1, 1×, 0,1M), mimari A ya da B; σ tahmincisi kilit Adım 2'nin sonucu (HAR). HAR katsayısı Adım 2'nin dondurulmuş
  banka/canlı katsayısıdır (`ciktilar/v8_har_secimi_20260929_01/sonuc.json`). ŝ² dondurulmaz: HAR ön-kaydı madde 12'nin
  banka kuralıyla sentetik yolun kendi Pazartesi haftalarından, dondurulmuş katsayıyla yürüyen artıklardan (PIT; hedefi
  t'ye kadar tamamlanmış son 52 hafta, en az 8; yoksa σ̂_EWMA). Null yolları aynı kuralı kendi sentetik verilerinde
  uygular.
- **3. revizyon gerekçesi (§0.2).** 2. turun planı (6 ayar × 100 temel yol; her yolda ×2, ×3, 10 çıkarma ve 200 null; A ve
  B) ~255.600 tam motor koşusu, ~15.000–30.000 CPU saati ister. Plan kullanıcı kararıyla (29 Eylül) aşağıdaki gibi
  değişti; karar hiçbir kalibrasyon, D ya da banka çıktısı görülmeden verildi. 2. turun metni
  `_arsiv/V8_BANKA_DUZEY2_20260929_01/`'dedir.
- **B7 eşiği q95 (sabit).** 2. turun q90/q95 ayar kuralı kaldırıldı. Gerekçe: (i) B7 bir vetodur; eşiği sıkılaştırmak
  birleşik yanlış kabulü yalnız düşürebilir. (ii) O kural 100 yol ve dört karşılaştırmayla, yapısal artefakt olmadan da
  ~%10–15 olasılıkla q95 verirdi. Bedel: B7'nin gerçek bir trendi reddetme olasılığı artar (normal yaklaşımla orta güçte bir
  sistemde ~10–15 puan). Büyüklüğü Düzey 2-b'de görülür.
- **Düzey 2-a — κ = 0'da B7'siz birleşik yanlış kabul (bağlayıcı).** κ = 0'da g ≡ 0'dır ve HL tanımsızdır; tek ayar koşulur.
  100 temel yol. Her yolda A ve B için ayrı ayrı: birincil koşu, ×2 ve ×3 maliyet koşuları (B3) ve 10 tek coin çıkarma
  koşusu (B10). Yol ve mimari başına 13 tam koşu; null yolu yoktur.
  - **Ölçüt kümesi (Codex T10 CIDDI).** B2, B3, B4, B5, B6, B8, B10 ve B11'den **Düzey 1 sonunda bağlayıcı kalanlar**,
    Düzey 1'in son eşikleriyle: B2 bağlayıcıysa d*; e_B5; k_B6; e_B10; tek önceden yazılı ayar uygulandıysa B3 ×2 ve B4
    için 0,40. Rapora inen ölçüt (B2 → R16; e_B5 > %60; e_B10 > 0,40) kesişime girmez. KABUL_B7siz = bu kümenin hepsi
    geçer. Düzey 1 "kilit bekler" verirse Düzey 2-a hesaplanmaz.
  - **Üst sınır.** Bankanın tam kabulü KABUL_tam ⊆ KABUL_B7siz ∩ B7 ∩ B9 (B12 bağlayıcı seçildiyse o da ek vetodur)
    olduğundan P(KABUL_tam | κ = 0) ≤ P(KABUL_B7siz | κ = 0). Raporlanan, A ve B için ayrı ayrı: p̂ = k/100, **"üst sınırın nokta tahmini"** etiketiyle, ve
    Wilson %95 aralığı ayrı sütunda (0/100 → üst uç %3,70; 5/100 → %11,18). Sonuç yalnız bu sentetik üreteç için
    geçerlidir.
  - **Kural.** A ya da B'de p̂ > %5 ise kilit bekler ve durum kullanıcıya sunulur (§1.2 istisna dalı). Otomatik ek ayar
    yapılmaz. Bu bir tarama kuralıdır; "yanlış kabul %95 güvenle ≤ %5" kanıtı değildir ve öyle raporlanmaz. Kilit
    beklerse B7'nin katkısı ölçülmemiştir; κ = 0 null koşuları ancak kullanıcı kararıyla eklenir.
  - B9 ikinci bir evren ister; Düzey 2'de yoktur. B9'un geçme olasılığı Düzey 1'den raporlanır.
- **Düzey 2-b — B7'nin gücü (betimsel; karar girdisi değil).** Yalnız M = A yapılandırması. 5 ayar: κ = 0 ve κ ∈ {0,0262;
  0,0523} × HL ∈ {30; 90}. Ayar başına 10 temel yol. κ = 0 ayarı Düzey 2-a'nın 1–10 numaralı yollarını ve onların birincil A
  koşusunu kullanır. Her temel yolda §3.5 yöntemiyle 50 null yolu. Dilimler Düzey 2'nin dört değerlendirme dilimidir; ısınma
  karıştırılmaz. Her ayar için raporlanan: B7'nin q90 ve q95 ile geçme oranı; gerçek SR̂'ın null değerleri içindeki sıra
  yüzdeliğinin ortalaması; birincil koşudan hesaplanabilen ve Düzey 1 sonunda bağlayıcı kalan ölçütlerle (B2, B4, B5, B6,
  B8, B11'in bağlayıcı olanları) birlikte B7'yi (q95) geçme oranı. Wilson %95 aralıkları yazılır (10 yolda ± ~25–30
  puan; kaba). Bu sayılar hiçbir eşiği değiştirmez; §3.5 "Bilinen sınırlar"daki "B7 gerçek trendi kesebilir" riskinin
  kaba büyüklüğünü gösterir.
- **Ayar ve tohum numaraları.** ayar_no 0: κ = 0. ayar_no 1–4: (κ, HL) = (0,0262; 30), (0,0262; 90), (0,0523; 30),
  (0,0523; 90). Temel yol tohumu hash(tohum_kal, 2, ayar_no, yol_no); Düzey 2-a yol_no 1–100, Düzey 2-b yol_no 1–10.
  Null yolunda §3.5.1'in hash(tohum_banka, p, j) tohumu yerine hash(tohum_kal, 2, ayar_no, yol_no, p, j), ikincil
  permütasyonda hash(tohum_kal, 2, ayar_no, yol_no, p, j, i) kullanılır; i üreteçteki coin numarasıdır (c1 = 1 … c30 = 30),
  j dilim numarasıdır (değerlendirme sırasıyla 1–4), p null numarasıdır (1–50). Maliyet ve çıkarma koşuları temel yolun
  kendisini kullanır; ek rastgelelik yoktur.
- **Kesinti ve devam (Codex T10 ORTA ile tamamlandı).**
  - **İş listesi.** Koşudan önce `IS_LISTESI.json` üretilir, hash'lenir ve kayda girer: her iş biriminin kimliği (düzey,
    ayar_no, yol_no, mimari, koşu türü ∈ {birincil, x2, x3, cikarma, null}, null no ya da çıkarılan coin numarası) ve
    dört beklenen kimlik: kalibrasyon kodunun sha256'sı, motorun sha256'sı (`DONDURMA.json` tanımıyla), Parametreler ve
    HAR katsayı kaynağının kimliği, ortam kimliği (Python ve numpy sürümü).
  - **B10 birimleri** ilgili mimarinin birincil birimi bitince deterministik olarak eklenir: birincil sonuçtan mutlak net
    katkısı en büyük 10 alt (eşitlikte küçük coin numarası). Birim kimliği birincil sonucun sha256'sını ve çıkarılan coin
    numarasını taşır; ekleme iş listesine ayrı satır olarak yazılır.
  - **Birim.** Girdisi yalnız tohumu ve dondurulmuş koddur. Birim içinde duvar saati okunmaz (süre yalnız ilerleme
    günlüğüne yazılır, sonuca girmez); küme ve sözlük dolaşımı sıralıdır; süreçler RNG paylaşmaz. Her süreç sayısal
    kütüphanelerde tek iş parçacığıyla koşar (OpenMP/MKL/OpenBLAS = 1).
  - **Sonuç dosyası.** Kanonik JSON (anahtarlar sıralı, sabit ayırıcılar, float'lar Python repr): birim kimliği, dört
    kimlik, sonuç gövdesi ve gövdenin sha256'sı. Geçici dosyaya yazılıp yeniden adlandırılır (atomik).
  - **Atlama kuralı.** Bir birim yalnız dosyası ayrıştırılabiliyor, gövde sha256'sı tutuyor, birim kimliği iş listesindekiyle
    ve dört kimlik beklenenle aynıysa atlanır. Aksi halde (bozuk, geçici, eski sürüm) dosya karantina klasörüne taşınır
    (silinmez) ve birim yeniden koşar. Makine kapanır ya da iş durdurulursa yalnız o anda yarım kalan birimler yeniden
    koşar. Koşu sırasında yalnız tamamlanan birim sayısı izlenir. Ölçütler ve oranlar bütün birimler bitince bir kez
    hesaplanır.
- **Tekrarlanabilirlik denetimi.** İki parça; biri sağlanmazsa kalibrasyon geçersizdir: neden bulunur, düzeltilir ve
  Düzey 2 baştan koşulur.
  1. **Koşudan önce (duman).** Düzey 2-a'nın 1. yolunun bütün birimleri (A ve B, 26) ve Düzey 2-b'nin iki null birimi 4
     işçiyle koşulur, yarıda durdurulup devam ettirilir. Aynı birimler ayrı klasörde 1 işçiyle ters sırada koşulur.
     Bütün sonuç hash'leri aynı olmalıdır.
  2. **Bitişte.** Sabit tohumla (hash(tohum_kal, 2, "tekrar")) seçilen 10 birim (her koşu türünden ve her iki mimariden
     en az biri) ayrı klasörde 1 işçiyle yeniden koşulur; sonuç hash'leri birebir aynı olmalıdır. Birim dosyalarındaki
     dört kimlik tek değer olmalıdır.
- **Sıra.** Motor koşuları Düzey 1'den bağımsızdır ve önce başlayabilir. Düzey 2-a'nın ölçütleri Düzey 1'in eşikleri
  sabitlendikten sonra hesaplanır.
- **Maliyet.** Düzey 2-a 100 × 13 × 2 = 2.600, Düzey 2-b 4 × 10 × 51 + 10 × 50 = 2.540 tam koşu; toplam ~5.140. Ayrıca
  tekrarlanabilirlik denetimlerinin ~66 koşusu.

**Uygulama netleştirmeleri (Codex T12 kod incelemesi, 29 Eylül; hiçbir kalibrasyon koşusundan önce).** Belgenin açık
bıraktığı uygulama yerleri şöyle sabitlendi; kod `v8/kalibrasyon/`, `v8/banka/`:
1. **Düzey 2 motor başlangıcı.** Motor bankadaki gibi (§3.1 sürekli koşu) verinin ilk gününden kesintisiz koşar; ısınma
   yılında evren, maske, pozisyon ve carry durumu oluşur. Ölçütler yalnız değerlendirme penceresinden hesaplanır. Null
   yollarında ısınma karıştırılmaz; motor aynı biçimde ilk günden koşar.
2. **B5 epizot ataması (A: net pozisyon; B: trend sanal bacağı).** Saatlik P&L iki paya ayrılır. Eski pay: saat başındaki
   pozisyonun önceki kapanıştan açılışa fiyat hareketi, funding ve kapanan kısmın işlem maliyeti; saat başındaki
   pozisyonun epizotuna yazılır. Yeni pay: saat sonundaki pozisyonun açılıştan kapanışa fiyat hareketi ve açılan kısmın
   maliyeti; saat sonundakinin epizotuna. İşaret değiştiren işlemde maliyet |q_eski| : |q_yeni| oranında bölünür.
   Kapanmış pozisyonun geç funding'i coinin son epizotuna yazılır.
3. **B8** = (ΔNAV − gerçek funding nakdi) / NAV günlük serisinin SR'ı (A ve B). **B10** çıkarması coini aday listeden
   çıkarır (veri aynı kalır); HAR banka takvimi o aday listesiyle yeniden kurulur. Null yolunda ŝ² null verisinden kurulur.
4. **Düzey 1 B10 ikame hattı** ana portföyün ortak faktörünü (u_t) paylaşır; kendi v, epizot ve Z çekişleri bağımsızdır.
5. **Düzey 1 B4 dilim seçimi.** X birim ölçekli olduğundan dilim sıralaması için X gerçekleşen yıllık vol %15'e doğrusal
   ölçeklenir ve dilim başına Σ ln(1 + x) alınır; SR ölçekten bağımsızdır.
6. **B seyreltme raporu.** C = σ_C (ρ X₀/σ_P + √(1 − ρ²) w) + SR_C σ_C/√365, σ_C = σ_P/3, w yolun ayrı çekişi; Z = X + C.
   SR, DSR, B3 (trend maliyeti 2K/3K; carry maliyeti SR_C içinde), B4, B6, B9 (SR(X^K + C)), B10 (Z üzerinde ikame) ve
   B11 Z'den; B5 (trend sanal bacağı) ve B8 (carry P&L'i funding sayılır) tanım gereği A ile aynı. Rapordur.
7. **σ_SR_bağ kaynağı.** Kural 1'in "REV1 deneme kayıtları" kapsamı, N_REV1 = 159'un kaynağı olan REV1 deneme kaydı
   `GECMIS/2026_09_19_oncesi/DENEY_TRIAL_REGISTRY.csv` ile sınırlandı (karar, Codex T13-5). Başka REV1 dosyalarında deneme
   sonucu aranmaz: aramak REV1 performans değerlerini görmeyi gerektirir ve kural betiğin kayıtlara bakılmadan yazılmasını
   ister. Bu kayıt aile başına yalnız deneme sayısı taşır, deneme başına Sharpe yoktur; kullanılabilir deneme 0 < 30 →
   σ_SR_bağ = 0,30 ve "varsayım, doğrulanmadı" cümlesi. Betik yalnız başlığı görerek yazıldı.
8. **N_kilit** = 159 + Σ max(1, varyant) deneme defterinden kalibrasyon anında (kalibrasyonun kendi satırı dahil);
   kilitte N değişmişse yalnız toplama adımı yeniden koşulur (yollar N'ye bağlı değildir).
9. **Muhasebe kapısı (T4-e).** Her Düzey 2 biriminde NAV sonlu ve pozitif, günlük zinciri sağlam, coin başı P&L
   özdeşliği (B birincilinde ayrıştırma özdeşliği de) ≤ 10⁻⁸ · max NAV; ihlal kalibrasyonu durdurur. HAR banka takviminde
   artık haftası yetersiz Pazartesi açıkça tanımsızdır (σ̂_EWMA); önceki ŝ² taşınmaz.
10. **Eşik ızgarası.** e_B5 ve e_B10, kesin "değer < e" koşulunu sağlayan en küçük ızgara değeridir (yuvarlama epsilonu yok).
11. **B5'te funding'in özgün epizotu (Codex T18; 30 Eylül, kilitten önce, D ve banka görülmeden; 2. maddenin geç funding
    cümlesinin yerini alır).** Funding nakdi kayda geçtiği saatte kalır (NAV, özdeşlik, B5 paydası, B8 ve B10 değişmez);
    B5 epizot atfı için her funding parçası ÖZGÜN saatinin başındaki pozisyonun EPİZOTUNA yazılır: gerçek kayıt q(d−)
    (damga d), eksik funding dolgusu her dolgu saatinin q(h−)'si, ters kayıt kapsadığı her dolgunun kendi saati (eksi
    işaretle). Kimlik epizottan gelir, yalnız yönden değil: kapanıp aynı yönde yeniden açılan pozisyon ayrı epizottur.
    Özgün saat pencereden önceyse ve o epizot pencere başına kadar kesintisiz sürüyorsa pencere başında süren epizota,
    sürmüyorsa hiçbir pencere epizotuna; yalnız pencere içinde kayda geçen parçalar yeniden atanır (hariç gün saatleri
    sıfır). Yeniden atama (şimdiki epizot, özgün epizot, özgün saat) üçlüsüne göre netlenir; aynı saati tam tersine
    döndüren dolgu + ters kayıt sonucu değiştirmez. Düzey 2'de desen yalnız 4h funding penceresinin 8h'e dönüşünde oluşur
    (ilk 8h aralığında 06:00/07:00 dolgusu, 08:00 kaydıyla (00:00, 08:00] tam ters kayıt; 01:00 icrasını kapsayınca epizot
    sınırı aşılabilir) ve net etkisi sıfırdır; kalibrasyon birim çıktıları değişmez (kanıt:
    `ciktilar/v8_b5_desen_20260930_01/`, testler `test_v8_duzey2_funding_desen.py`, `test_v8_banka_pnl.py`). Kod:
    `motor/ayristirma.fon_parcalari`, `banka/pnl.coin_pnl` (fon_ozgun), ayrıştırma `trend_fon_ozgun`,
    `banka/degerlendirme._ozgun_dilim`, `banka/pnl.epizot_pnl(ozgun=)`.
12. **Null ve yan birimlerde görülmüş gün maskesi (Codex T18).** B7 null yolları, ×2/×3 ve B10 çıkarma birimlerinin Sharpe'ı
    birincil ölçümle aynı görülmüş günleri düşer (BK-5; §3.5.6 aynı takvim). Kalibrasyon pencereleri hariç gün taşımaz;
    kalibrasyon sonucu bit düzeyinde aynıdır.
13. **R3 long-beta kitabı (§3.4 R3; kullanıcı onayı 30 Eylül, kilitten önce, D ve banka görülmeden; ILERLEME_BANKA
    BK-14).** R3 betimsel satırdır, kapıya ve hükme girmez. (a) Kendi birimi: birincil ayarla ayrı bir motor koşusu; R3
    birincil birimin çıktısını okumaz. M = A ve M = B'de aynıdır (mimariden bağımsız pasif kitap). (b) Evren (Codex T19
    düzeltmesi): her aylık evren seçimi gününde (`gorunum.aylik_secim_gunu_mu`) karar kaydının `a_t` kümesi (güncel
    evren üyesi, işlem dışı değil, maskeli değil; `hedef.hedef_agirlik_ayrintili`). `coinler` kullanılmaz: evren dışı
    pozisyonlu/devreden isimleri de içerir. BTC ve ETH o gün `a_t`'deyse dahildir. (c) Ağırlık: aynı gün, aynı kümede
    `hedef.boyut_sigmalari` (HAR banka takvimi, taban %20); w_i = Bütçe · (1/σ̂_i) / Σ_j (1/σ̂_j), yalnız long, o
    günün NAV'ına göre. Bütçe (Codex T20) = max(0, 1 − Σ_{c ∉ a_t} w_c): `a_t` dışında hâlâ tutulan (işlem dışı,
    çıkışı sürmekte olan) pozisyonların o günkü ağırlığı düşülür; böylece karar anında toplam brüt 1'i aşmaz. Bu
    pozisyonlar sonradan satılınca serbest kalan nakit sonraki aylık seçime kadar dağıtılmaz. (d) Yeniden dengeleme AYLIK: yalnız aylık seçim gününde hedef ağırlığa dönülür, aradaki günlerde
    hedef miktar sabittir (ağırlık fiyatla kayar). Aradaki bir günün kararında `a_t` dışına düşen (evrenden çıkan,
    maskelenen) isme hedef 0 verilir; işlem dışı isimde yeni emir verilmez (motorun `sabit` kuralı), işlem dışılık bitip
    isim `a_t` dışındaysa hedef 0 o günkü kararda verilir. Çıkış satılmış sayılmaz: emir motorun icra kurallarıyla
    (katılım sınırı, kısmi dolum, bar yoksa devretme, delist beklemesi ve uzlaşma) gerçekleşir; gerçekleşene kadar
    kalan pozisyon değerlenir ve funding öder/alır. Serbest kalan nakit yeniden dağıtılmaz; yeni ya da maskeden dönen
    isim ancak sonraki aylık seçimde girer. Aylık seçim gününde devreden emir motordaki gibi yeni hedefle değiştirilir.
    (e) İcra ve maliyet motorla aynı: karar 00:00, dolum 01:00'den itibaren saat saat (devreden emir),
    `maliyet.maliyet_hesapla` aynı bağlam girdileriyle (V60, σ, BTC/ETH sınıfı, karekök terimi kitabın kendi nominaliyle),
    aynı lot/minNotional filtresi ve katılım sınırı. (f) Funding: long pozisyon gerçek funding kayıtlarını öder ya da alır (`funding_saati`,
    dolgu ve ters kayıt dahil). (g) Rapor: R3 günlük getirisi birincilin gerçekleşen vol'üne doğrusal ölçeklenir (B11 gibi;
    görülmüş günler hariç); SR farkı, korelasyon, α ve t (r_birincil = α + β r_R3 + ε; t Newey-West, gecikme 10). Çıktı
    şifreli: gün sınırı NAV'ı, günlük brüt/net devir, maliyet ve funding payı.
14. **Koşu tanıları: R5, R6, R7, R14 (30 Eylül dizüstü, kilitten önce, D ve banka görülmeden; ILERLEME_BANKA BK-15).**
    Birincil birimde (ve R14 için demo NAV biriminde) koşunun kendi kayıtlarından, birincil örneklem günlerinde
    (görülmüş günler hariç) hesaplanır ve şifreli çıktıya yazılır; hüküm dışıdır. Durum, günlük olayları
    `motor.durum.kayit_uygula` ile baştan uygulayarak her gün sınırında (karar öncesi) alınır.
    (a) **R5.** Hedef kitap: karar kaydının `baglayan` listesindeki her tavan adı (isim, brüt, S1, S2, global, T4d; B'de
    kaydın taşıdığı adlar) için bağladığı gün oranı. Birim kitap: M_max bağlama (m > m_max, yani m̃ < m) ve T4-a
    güvenlik ölçeklemesi gün oranı (A_t boş günler paydada değil). Gerçekleşen + devreden kitap: her gün sınırında
    w = (q + devreden kalan)·kapanış / NAV; S1 ve S2 kayıp değeri (`tavanlar._kayip_s1/_s2`, aynı parametreler)
    sınırını aştığı gün oranı ve en büyük aşım (değer − sınır). Hedefe ulaşılamayan gün: gün sınırında devreden emri
    kalan gün oranı.
    (b) **R6.** Yıllık tek yön devir = 365 · ort_gün(Σ|dolum nominali| / NAV_gün başı) / 2; maliyet payı ve funding
    payı = 365 · ort_gün(tutar / NAV_gün başı) (maliyet = |Δq|·açılış·c; funding gelir > 0); doldurulan funding
    kaydı ve ters kayıt sayıları; katılım gecikmesi = her emir niyetinin karar saatinden tamamlanana (son dolum ya da
    iptal) kadar geçen saat: ortalama, q50, q95 ve bir sonraki karara kadar tamamlanmayan niyet oranı; icra artığı =
    gün sınırında Σ|devreden kalan|·kapanış / NAV: ortalama ve q95.
    (c) **R7.** Gerçekleşen vol / birim: birincil günlük getirinin yıllık std'si / (L·τ). Tahminci: her karar gününde
    A_t coinleri için boyutlamada kullanılan σ̂ (taban dahil), birim kitaptan σ̂_i = k·s_i / w^u_i (s_i ≠ 0; T4-a
    güvenlik ölçeklemesinin uygulandığı günler dışarıda, oranı ayrıca yazılır); hedef HAR seçimiyle aynı: sonraki 7
    günün günlük log getirileri (`hedef.coin_gunluk` tanımı; yedisi tanımlı) Y = Σr²·365/7; RV/σ̂² = Y/σ̂²: q50, q95,
    q99 ve gözlem sayısı. Yalnız M = A'da hesaplanır (B'de w^u trend sanal bacağıdır; aynı formül, aynı tanım).
    (d) **R14.** Demo NAV birimi: karar anında |bantlı hedef − mevcut| > 0 olan serbest isimlerden emir niyeti
    üretilmeyenlerin (lot adımı / minNotional altında) oranı; M = B'de ayrıca bantlı hedefte BTC ağırlığı ≠ 0 iken
    gün sonu BTC pozisyonu 0 olan gün oranı.
15. **R2, R4, R13 (b), R15, R17 (30 Eylül dizüstü, kilitten önce, D ve banka görülmeden; ILERLEME_BANKA BK-16).**
    (a) **Piyasa serileri (birincil birim, şifreli):** her gün g ∈ [T0_Z1, Z2_son) için r_BTC,g = P(g+1)/P(g) − 1 (gün
    damgası kapanışı, `gorunum.gunluk_kapanislar`); r_alt,g = g günündeki karar kaydının evreninden (BTC/ETH hariç) iki
    kapanışı da tanımlı üyelerin eşit ağırlıklı basit getirisi (üye yoksa tanımsız); r_D = r_alt − r_BTC.
    (b) **R2.** Birincil örneklemde (görülmüş günler ve r_D tanımsız günler hariç) r = α + β_BTC r_BTC + β_D r_D + ε;
    OLS, t Newey-West (gecikme 10); ayrıca her Z1 diliminde. Pozisyon bazında: coin başına β_i = coinin günlük basit
    getirisinin r_BTC'ye OLS eğimi (birincil örneklem, en az 30 ortak gün; yoksa β_i = 0 ve sayılır); günlük BTC katkısı
    Σ_i w_i,g · β_i · r_BTC,g (w_i,g: gün başı gerçekleşen ağırlık, önceki gün sonu); artık katkı = kitabın günlük coin
    P&L'i / NAV_gün başı − BTC katkısı. β_i örneklem içi tahmindir (betimsel; ileriye bakar). Rapor: iki katkının yıllık
    toplamı ve dilim bazında aynısı.
    (c) **R4.** REV1 serisi (açık soru 6: REV1 sürecinin tek yönlü aktardığı D dönemi günlük getirisi; dosya ve sha256
    raporda) D segmentindeki ortak günlerde (görülmüş günler hariç): günlük korelasyon; D başından ardışık, örtüşmeyen 30
    günlük bileşik getirilerin korelasyonu; stres günleri (D'de r_BTC ≤ r_BTC'nin D içindeki %5 yüzdeliği) korelasyonu.
    Seri verilmezse satır "REV1 serisi yok" yazar.
    (d) **R13 (b).** Adım > 0 filtreli her aday coin için adım × T0_Z1'de ya da sonraki ilk tanımlı gün kapanışı
    (USDT): q50, q95, en büyük; birincil NAV'ın %1'ini aşan coin sayısı. Coin adı yazılmaz.
    (e) **R15.** K-evren biriminin B9 serisi D segmentinde (görülmüş günler hariç): SR ve %90 GA; "görülmüş zaman" etiketi.
    (f) **R17.** Birincil ve her null biriminde, birincil örneklemde: maske günü (Σ_coin maskeli gün; koşu sonu maske
    dönemlerinden), dolgu saati (funding dolgu kayıtlarının saat sayısı toplamı), borsa çapı boşluk saati (karar
    kayıtlarının `bosluk_gecmis` listelerinin birleşiminden pencereye düşen saatler), ortalama evren üyeliği (karar başına
    evren uzunluğu). Rapor: gerçek yol değeri; null değerlerinin ortalaması, q5, q95; ortak eşleşme payı (null birimlerinin
    ortak / toplam payı) ortalaması, q5, q95.
16. **R8, B ayrıştırması (30 Eylül dizüstü, kilitten önce, D ve banka görülmeden; ILERLEME_BANKA BK-17).** Yalnız M = B.
    (a) Birincil B biriminde `motor.ayristirma` satırları (trend/carry/hedge × fiyat/funding/maliyet, netleme, icra
    artığı, artık carry/trend) günlük toplam / NAV_gün başı olarak [T0_Z1, Z2_son) için şifreli çıktıya yazılır. Rapor:
    birincil örneklemde (görülmüş günler hariç) her satırın yıllık katkısı (365 · günlük ortalama); trend bacağı
    (trend fiyat + funding − maliyet) ve carry bacağı (carry fiyat + funding − maliyet + hedge fiyat + funding) günlük
    serilerinin SR'ı ve %90 GA'sı. (b) Bağımsız A koşusu (`a_ayristirma`): SR, %90 GA, B5 payı; birincil B ile SR farkı.
    (c) K1-09: Kelly tablosunun 1× maliyet satırlarında her L için (L = 1 birincil B) carry bacağının günlük serisi
    (b'deki tanım) r_c = α + β_BTC r_BTC + β_D r_D + ε ile (R2'deki piyasa serileri; NW gecikme 10) β_BTC, β_D ve t'leri.
    Bunun için B'nin 1× maliyetli Kelly birimleri de ayrıştırılır (yalnız R8 serisi; ölçüm B5'siz kalır, BK-13).
    (d) §3.4 B5 notu gereği carry bacağının epizot payı: carry sanal bacağında (`carry_q`, `carry_eski/yeni`; B5 ile
    aynı `banka.pnl.epizot_pnl` kuralı), en iyi 3 epizot / carry bacağı net P&L'i; özgün saat funding atfı carry bacağında
    uygulanmaz (carry funding yönü `carry_fon_long/short` ile ayrıca verilir). Betimseldir.
17. **Codex T21 düzeltmeleri (30 Eylül dizüstü, kilitten önce, D ve banka görülmeden; BK-18).**
    (a) **Veri kimliği (T2).** `BANKA_MANIFEST.jsonl` satırı {yol, sha256, checksum, durum ∈ TAMAM | CHECKSUM_HATASI |
    INDIRME_HATASI | YOK}. Bir dosyanın ilk TAMAM satırındaki sha256 bağlayıcıdır; sonraki bir TAMAM satırı başka sha256
    taşırsa "kimlik değişti" sayılır. TAMAM satırında sha256 ya da checksum eksikse satır geçersizdir. T2 (1) =
    onarılamayan CHECKSUM hatası: son durumu CHECKSUM_HATASI, geçersiz TAMAM satırı, sha256 ≠ checksum ya da kimlik
    değişimi. INDIRME_HATASI ve YOK ayrıca sayılır (T2 değil; eksik veri (2) ve (3) ile yakalanır). Veri raporu ayrıca
    koşu öncesi eksik funding kaydı sayısını yazar: ardışık iki kaydın aralığı kaydın kendi `funding_interval_hours`'unun
    1,5 katını aşan boşluk sayısı (motor dolgusunun tetik koşuluyla aynı ölçek).
    (b) **R3 sayısal dal.** Gözlem < 3 ya da birincil veya R3 serisinin std'si 0 ise R3 satırı "tanımsız" yazar ve
    nedeni verir; hüküm hesabı durmaz.
    (c) **R6.** Katılım gecikmesi = kapanan (dolum, uzlaşma ya da iptal) bütün niyetlerin karardan kapanışa saatleri;
    kapanış türü ayrıca sayılır. "Sonraki karara yetişmeyen niyet oranı" = sonraki karar kaydı anında emri hâlâ açık olan
    niyetlerin oranı (nihai kapanış türünden bağımsız).
    (d) **Gün başı ağırlık (R2, stres nesneleri).** Gün sınırındaki durum, o sınırdaki 'nav' kaydı anındaki durumdur
    (aynı damgadaki uzlaşma ve karar olaylarından önce). Gün sonu ağırlıkları `pozisyon_gecmisleri` ile sınırdan kesin
    önceki son olaydan alınır.
    (e) **R4.** D başından ardışık, örtüşmeyen 30 takvim günlük bloklar; blokta REV1 ile ortak ve görülmemiş en az 25 gün
    varsa blok iki serinin o günlerdeki bileşik getirisiyle girer, yoksa blok dışarıda. Stres günü eşiği, D'nin bütün
    görülmemiş günlerindeki r_BTC'nin %5 yüzdeliğidir (REV1 ortaklığından önce).
    (f) **R5 B'de T4-a.** B karar kaydı T4-a bayrağı taşımaz (motor değişmez); B'de oran "kayıt yok" (None) yazılır.
    (g) **R17 boşluk saati** (Codex T22 düzeltmesi): birimin kendi verisinde motorun tarama fonksiyonuyla
    (`gorunum.bosluk_taramasi`, pencere başından pencere sonuna, [bas, bit) saatlerinin tamamı) sayılır; gerçek ve null
    yolda aynı kapsam (null koşusu pencere sonunda durduğu için karar kayıtları son günü taşımaz). Veri denetimi taraması
    da [bas, bit) saatlerinin tamamını kapsar.
    (h) **%90 GA (§3.1 "her Sharpe").** B3 (×2, ×3), B4 (en iyi dilim hariç günler), B6 (dört dilim), B7, B8 (funding
    hariç seri; birincil birimde saklanır), B9, R1 (9 hücre), R3 (birincil ve ölçekli R3), R11, R12 (her senaryo), R13
    (lot kapalı), Kelly (her L ve maliyet), R8 bacakları, R15; hepsi aynı durağan bootstrap, etiket = birim/satır adı.
    (i) **Rapor zorunlu alanları:** B2 satırında γ₃, γ₄, η, T; R7 tanıları; Kelly tablosunda bootstrap q50, q95, P(MDD >
    %30), gerçekleşen MDD ve stres sütunları (D90-1/2/4, SQ-1/2/4, DM-1 MDD); R8'de carry epizot payı; veri raporunda
    eksik funding kaydı. Rapor üreteci serbest metin alanlarında (dosya adı, teknik ve kalibrasyon sözlükleri) ve son
    metinde BTC/ETH dışında sembol biçimli dizge (`[A-Z0-9]{2,}USDT`) bulursa hata verir.
18. **B8 günlük funding toplamı penceresi (30 Eylül dizüstü; kilitten önce, D ve banka görülmeden; BK-18).** B8'in
    gerçek funding nakdi günlük toplamı (`banka.pnl.gunluk_topla`) yalnız [ilk gün, son gün + 24 saat) içindeki saatleri
    toplar. Önceki kod son günden sonraki bütün saatleri son güne yığıyordu: bankada motor Z2 sonuna kadar koştuğu için
    2023-06-24 → Z2 sonu arasındaki funding nakdi birincil örneklemin son gününe yazılırdı (B8 bozulurdu). Kalibrasyonda
    motor pencere sonunda durduğundan (`kalibrasyon/yurutucu.py`: t_son = pencere sonu − 1 saat) pencere dışı saat yoktur ve
    kalibrasyon sonuçları değişmez; bu, eşdeğerlik ve B5 A kabul koşusuyla (güncel kodla) doğrulanır. Bulgu: banka_kos
    B8 serisinin birincil ölçümle birebirlik testi (Codex T21 17 h).
19. **Banka veri yükleyicisi (6.01b; 30 Eylül dizüstü, kilitten önce, banka verisi görülmeden; BK-19).** Kaynaklar
    §2.3'teki gibi iki pakettir: (i) banka indirmesi (`BANKA_MANIFEST.jsonl`; klasör `ham/klines/<sym>/`,
    `ham/fundingRate/<sym>/`; aylık ve Eylül günlük kline zip'leri, aylık fundingRate zip'leri; Eylül funding'i arşiv
    zip'i yoksa `ham/fundingRate_api/<sym>.json` tek anlık görüntüsü {fundingTime, fundingRate, fundingIntervalHours?}),
    (ii) D paketi (`adaptor.veri_yukleyici`, mevcut MANIFEST ve hash'ler; yalnız D coinleri ve BTC/ETH, yalnız
    [2023-07-01, 2026-07-01)). Her dosya manifestteki bağlayıcı (ilk TAMAM) sha256 ile doğrulanır; manifestte olmayan ya
    da eşleşmeyen dosya hatadır. Temizlik D yükleyicisiyle aynı kurallar (başlık algılama, mikrosaniye → ms, sıralama,
    tekrar eden damgada ilki, sayısal olmayan satır atılır, kline saat ızgarası ve pozitif fiyat zorunlu, funding
    damgası en yakın saate yuvarlanır ve çakışmada ilki). Dönem: ilk bar → Z2_son (hariç). D coinlerinde banka
    indirmesinin D penceresine düşen satırları atılır ve sayılır (D dönemi yalnız D paketinden); iki kaynağın
    birleşiminde aynı damga iki kez gelirse hata. Veri kimliği = kullanılan her dosyanın "yol sha256" satırlarının sıralı
    birleşiminin sha256'sı (iki paket ayrı önekle). Aday listesi (uygun evren + BTC/ETH) açılışta mühürden girdi olarak
    verilir; yükleyici listeyi yalnız uygular.
20. **Tek atış betiği, veri denetim betiği, T5 paritesi ve kuru koşu (6.14–6.15; 30 Eylül dizüstü, kilitten önce, D
    ve banka görülmeden; BK-20).**
    (a) **Açılış girdisi `ACILIS.json`.** Değerlendirici oturum mühürden hazırlar (betik mühür belgesini okumaz):
    {mimari, adaylar (uygun evren), k_coinleri (80), d_coinleri (120), gorulmus_gunler (7 tarih, YYYY-MM-DD),
    banka_kok, d_kok, anonim_anahtar (yol)}. Denetim: K ⊆ adaylar, D ⊆ adaylar, K ∩ D = ∅, 7 farklı gün, mimari
    DONDURMA'dakiyle aynı; aksi T1 (dur). Veri adayları = adaylar ∪ {BTC, ETH}; D paketinden D dönemi alınanlar
    D ∪ {BTC, ETH}. ACILIS'in kanonik sha256'sı iş listesi kimliklerine girer.
    (b) **T1 kimlik denetimi.** `banka_kos.py` ve `veri_denetim.py` ilk iş olarak `DONDURMA.json`'daki şu alanları
    yeniden hesaplayıp karşılaştırır: `motor_sha256` (v8/motor), `banka_kos_sha256` (v8/banka_kos.py + v8/banka_kos,
    v8/banka, v8/kalibrasyon, v8/adaptor paketleri; birleşik yol + bayt sha256'sı), `veri_denetim_sha256`
    (v8/veri_denetim.py), `parametreler_sha256` (varsayılan Parametreler + HAR sonuç sha'sı; kilitteki tanım), ortam
    (Python, numpy, pandas, cryptography sürümleri) ve `tohum_banka = int(motor_sha256[:16], 16) mod 2³²`. Tek fark →
    T1, hiçbir koşu başlamaz. Alıcı açık anahtar `sifreleme_acik_anahtar`'dır.
    (c) **Sıra.** `veri_denetim.py` veriyi yükler (netleştirme 19), T0_Z1'i veriden hesaplar, sembol filtrelerini
    kilitli `exchangeInfo_ham.json`'dan (sha256'sı ALINMA.json'dakiyle aynı olmalı) veri adayları için
    `adaptor.sembol_filtreleri.tablo` ile kurar, T2'yi (§2.5; netleştirme 17 a, g) hesaplar ve
    `denetim/VERI_DENETIM.json`'u (kanonik; veri kimliği, yükleyici raporu, filtresiz sembol sayısı dahil) yazar; T2
    varsa çıkış kodu 3. `banka_kos.py` VERI_DENETIM.json'u okur: T2 yok ve veri kimliği kendi yüklemesiyle aynı
    olmalı; aksi dur. Bağlam: veri, K-evren adayları (K ∪ {BTC, ETH}), motor başı (bütün adayların ilk barının günü
    00:00), T0_Z1, görülmüş günler (00:00 UTC ms), filtreler, dondurulmuş HAR β, tohum_banka, anonim kimlikler (anahtar
    dosyası önceden `anonim.anahtar_uret` ile üretilmiş olmalı; eşleme dosyası yerel, sha256'sı açık grupta). Her işçi
    bağlamı aynı yolla kurar ve veri kimliğini denetler. Koşucu (`kosucu.calistir`) bütün birimleri yürütür, ardından
    `SONUC_DAMGA.json` ve `denetim/DENETIM_OZETI.json` (T1–T5 durumları, birim sayısı, kimlikler; performanssız)
    yazılır. Ekrana yalnız sayılar basılır.
    (d) **T5 parite (MIMARI §5.6 senaryo 1).** Birincil birimde karar günlerinden 20'si
    `uretec(tohum_banka, 'parite')` ile yerine koymadan seçilir (20'den azsa hepsi). Her T'de durum, günlüğün T'deki ilk
    uzlaşma/karar kaydından önceki öneğinden `durum_turet` ile kurulur; `karar_ver(gorunum_kur(veri, T), durum, L, p,
    filtreler)` geri test kararıyla karşılaştırılır: hedef ağırlıklar (w*, w^u, bantlı) mutlak fark ≤ 1e-12; niyet
    miktarları, iptaller, evren ve maske birebir. Kritik parite hatası = uyuşmayan gün sayısı; açık grupta yalnız sayı
    ve seçilen günlerin sha256'sı. > 0 → T5.
    (e) **Kuru koşu (6.15).** Aynı betik `--kuru` ile D paketinde koşar: veri `adaptor.veri_yukleyici.tam_veri_yukle`
    (geliştirme evreni, mevcut MANIFEST; checksum alanı yerine paket sha256'sı), DONDURMA yerine kimlikler o an
    hesaplanıp kaydedilir. Dönemler (D'ye taşınmış, banka yapısıyla aynı): T0 = T0_Z1 kuralı D'nin BTC/ETH ilk barına
    uygulanır; dilim sınırları T0 + 6, 12, 18 ay; birincil son T0 + 24 ay; "D" penceresi (R4, R10) [birincil son,
    birincil son + 6 ay); Z2 = [D sonu − 3 ay, D sonu); görülmüş gün yok; K = geliştirme evreni (B9 ayrımı yok). Alıcı:
    kullanıcının açık anahtarı verilmişse o; değilse bellekte üretilen tek kullanımlık anahtar (gizli yarısı diske
    yazılmaz; performans yeniden koşulmadan açılamaz). Kuru koşunun damgası (birim başına düz sha256) §2.5'teki "D kuru
    koşu çıktıları hash düzeyinde aynı" karşılaştırmasının tabanıdır. Hüküm kuru koşuda çalıştırılmaz.
    **Codex T23 düzeltmeleri (30 Eylül dizüstü, kod öncesi):**
    (f) **Hata sınırı.** İki betikte hazırlık, yükleme, denetim ve sonlandırma BK-11 sınırındadır: kendi hatalarımız
    (AcilisHatasi, sabit metin) dışında her istisnanın izi alıcıya şifreli `sonuc/hata/<etiket>.age` yazılır; dışarı
    yalnız sabit mesaj + düz izin sha256'sı çıkar. Alıcı henüz bilinmiyorsa (DONDURMA okunamadı) iz yazılmaz, yalnız
    sha256 basılır.
    (g) **Bağlam kimlikleri.** Tanım filtre tablosunun sha256'sını, HAR sonuç sha256'sını, anonim anahtar sha256'sını ve
    dönemi taşır; ana süreç ve her işçi bunları yeniden hesaplayıp karşılaştırır (VERI_DENETIM.json'daki filtre kaydı
    dahil). T2 kararına güvenilmez: `banka_kos.py` veri denetimini aynı kodla yeniden hesaplar ve VERI_DENETIM.json ile
    kanonik birebir aynı olmalıdır.
    (h) **T5 öneği (d'nin düzeltmesi).** Durum, T'deki ilk **karar** kaydından önceki önekten kurulur (T'deki funding ve
    delist uzlaşması kayıtları dahil; geri testin karar_ver'e verdiği durumla aynı nesne). Test uzlaşma gününü zorunlu
    seçer.
    (i) **Eksik dosya ve Eylül funding kaynağı.** Bir adayın manifestte TAMAM olup diskte bulunmayan dosyası
    onarılamayan hatadır (T2 (1)); yükleyici de hata verir. Eylül funding'i için sembolde `*-2026-09.zip` arşivi
    varsa API görüntüsü bulunmamalıdır (ikisi birden → hata); API görüntüsünden yalnız [2026-09-01, Z2_son) kayıtları
    alınır.
    (j) **ACILIS şeması.** (a)'ya `sureklilik_sorunu` (indirme listesi betiğinin saydığı süreklilik sorunu sayısı;
    negatif olmayan tamsayı) eklenir; `d_kok` isteğe bağlıdır (yoksa mevcut D paketi). Bankada |K| = 80, |D| = 120
    zorunludur (sentetik testler bu denetimi açıkça kapatır). T5 hatası ayrı çıkış kodudur (7); özet "T5 VAR" yazar.
    (k) **Kimlik tanımları ve kuru karşılaştırma.** §1.4'teki `motor_sha256` ve `banka_kos_sha256`, kalibrasyon
    kimliğiyle aynı işlevle hesaplanır: dosyalar yola göre sıralı, her dosya için göreli yol + ham baytlar tek sha256'ya
    beslenir (`kalibrasyon.birim._birlesik_sha256`; KOD_DONDURMA ile aynı tanım). `ortam` = {python, numpy, pandas,
    cryptography} sürüm sözlüğü (depoda paket kilit dosyası yoktur). Teknik düzeltmeden sonra `tohum_banka` ilk
    DONDURMA'daki değer kalır (yeni motor hash'inden yeniden türetilmez; T1 türetme denetimi ilk motor hash'iyle yapılır).
    Kuru karşılaştırma koşusu aynı anonim anahtar ve aynı tohumla yapılır (`--anonim-anahtar`, `--tohum`); karşılaştırma
    (birim adı, düz sha256) çiftleri üzerindendir; şifreli sha ve damga zamanı kullanılmaz.
    (l) **Codex T24 düzeltmeleri (kod öncesi).** (1) Teknik düzeltme sonrası DONDURMA, ilk dondurma kaydını
    `ilk_dondurma` = {yol (depo köküne göre), sha256} ile gösterir; betik o dosyayı okur, sha256'sını doğrular ve
    tohumu oradan alır (`tohum_banka` ilk kayıttakiyle aynı, ilk kayıttaki `motor_sha256`'dan türetilmiş olmalı);
    ilk kaydın kendisinde `ilk_dondurma` bulunmaz. (k)'daki serbest `ilk_motor_sha256` alanı kaldırılır. (2) Denetim
    dosyasının yazımı da hata sınırındadır. (3) Manifest–disk tamlık denetimi (i) D paketinden alınan semboller (D ∪
    {BTC, ETH}; kuruda geliştirme evreni) için D MANIFEST'inin TAMAM satırlarına da uygulanır. (4) ACILIS'te
    adaylar − {BTC, ETH} = K ∪ D olmalı; BTC ve ETH K ya da D'de bulunmaz. (5) `banka_kos_sha256` dosya listesi sabit
    paket sırasıyla kurulur: v8/banka_kos.py, v8/banka_kos/, v8/banka/, v8/kalibrasyon/, v8/adaptor/ (her paket içinde
    yola göre sıralı); `motor_sha256` = v8/motor/ yola göre sıralı. Tanım `acilis.kimlikler` işlevidir; DONDURMA
    üreticisi aynı işlevi çağırır.
    (m) **Codex T25 (kod öncesi).** Argüman dönüşüm hataları sabit mesajla çıkış 2 verir. `ilk_dondurma`'nın bağımsız
    sabitlemesi işlem kuralıdır: teknik yeniden koşuda §2.4 denetim listesinin T1 maddesi, `ilk_dondurma.yol` +
    `sha256`'nın uzak depoya itilmiş ilk dondurma commit'indeki dosyayla (`git show <dondurma commit>:<yol>`) aynı
    olduğunun değerlendirici ve Codex tarafından doğrulanmasını içerir; betik bu karşılaştırmayı yapmaz (git geçmişi
    betiğin girdisi değildir).

**Kalibrasyon sonuçları (Adım 3 kapanışı, 30 Eylül 2026; 4.01).** Yukarıdaki kuralların mekanik çıktısıdır
(`ciktilar/v8_kalibrasyon_20260929_01/RAPOR.md`, TOPLAMA.json (N = 329 ile yeniden toplanmış; sha256 kalibrasyon RAPOR.md başında);
bitiş `bitis_sonuc.json` geçti; B5 A eşdeğerliği 140/140; Codex T26 kararları doğruladı). Kilitte sabitlenir:
- σ_SR_bağ = 0,30, kaynak **varsayım** ("σ_SR = 0,30 varsayımdır, doğrulanmadı"); N_kilit = 329 (159 + 170; kilitte deftere kapı sentetik doğrulaması ve kapı satırı eklendi, toplama N = 329 ile yeniden koşuldu — netleştirme 21 f; kararlar değişmedi).
- **B2 bağlayıcı** (P(B2 geçer, d = 0,50 | SR = 1) = 0,574 ≥ 0,25); **d\* = 0,90** (d = 0,50 ve 0,75 birleşik
  P(KABUL | SR = 0) ≤ %5'i sağlamadı; 0,90'da en kötü ayar %2,1). Tek önceden yazılı ayar uygulanmadı: B3 ×2 ve B4
  eşikleri 0,30.
- **e_B5 = rapor** (ham ∞ > %60): B5 bankada bağlayıcı değildir, R olarak raporlanır.
- **e_B10 = rapor** (ham 0,80 > 0,40): B10 bankada bağlayıcı değildir, R olarak raporlanır.
- **k_B6 = 2.** B7 kuantili q95 (3. revizyon).
- Düzey 2-a taraması geçti (κ = 0, B7'siz: A 0/100, B 0/100; Wilson %95 üst uç %3,7).
- Bankanın bağlayıcı ölçüt seti: B2 (d\* = 0,90), B3, B4, B6 (k = 2), B7 (q95), B8, B9, B11.

21. **Codex T27 (kilit öncesi okuma, 1 Ekim 2026; D P&L'i ve banka görülmeden).**
    (a) **T4-d ve K8 istisnası.** §2.5 T4-d, MIMARI §3'ün işlem dışı isim istisnasını (K8, kullanıcı kararı
    2026-09-28) aynen uygular: işlem dışı isimden kalan tavan ya da toplam risk ihlali teknik hata değildir; olay olarak
    kaydedilir (`sabit_tavan_ihlali`, `sabit_t4d_ihlali`) ve R5'te gün sayısı ile en büyük aşım raporlanır.
    (b) **Ölçüt tablosu (§3.4) kalibrasyon sonrasıyla okunur:** B2 bağlayıcı, d* = 0,90; B5 ve B10 R; B6 k_B6 = 2;
    B7 q95. Tablo bu satırlarda güncellendi.
    (c) **§4 madde 5.** "L = 1 ∉ 𝓛* ise önerilen kaldıraç 1'in altına iner" cümlesi geri çekilir: her L ayrı, tavanlı
    koşudur ve MDD'nin L ile monotonluğu garanti değildir. Öneri yalnız hesaplanan 𝓛* ve onun içindeki CAGR
    sıralamasından çıkar; 𝓛* boşsa madde 4 uygulanır.
    (d) **Düzeltme hakları (tek tablo).** Hüküm öncesi: en fazla 1 teknik yeniden koşu (§2.5); ikinci teknik
    geçersizlik → NOT_EVALUATED. Hüküm sonrası: bulunan her hata için en fazla 1 düzeltilmiş koşu; bu, hüküm öncesi
    hakkın kullanılıp kullanılmadığından bağımsızdır ve hükmü yalnız NOT_EVALUATED'a çevirebilir (§2.5); hüküm sonrası
    ikinci bir hata bulunursa sonuç NOT_EVALUATED'dır. Her düzeltilmiş ya da teknik koşu deftere satır ekler (N +1).
    (e) **Hesaplanamayan ölçüt.** NAV sonlu iken bağlayıcı bir ölçüt hesaplanamazsa (sıfır varyans, yetersiz gözlem,
    tanımsız DSR) ölçüt **kaldı** sayılır (RET yönü); bu TEKNİK GEÇERSİZ değildir. B7'de null SR'larından biri tanımsızsa
    B7 kaldı sayılır. Rapor satırları tanımsızlığı "tanımsız" ve nedeniyle yazar (netleştirme 17 b ile aynı ilke).
    (f) **N ve deneme defteri bağı.** Kilit anında N_kilit, defterin son halinden §3.3 sayım kuralıyla yeniden
    hesaplanır (kapı satırı `A4-carry-kapisi` dahil). TOPLAMA.json'daki N ve defter sha256'sı bununla aynı olmalıdır;
    değilse toplama (`topla.py`, sentetik yollar yeniden üretilmez) yeni N ile yeniden koşulur ve kalibrasyon
    raporu ile 4.01 sonuç özeti güncellenir. `kilit.py` bu eşitliği zorunlu ön koşul olarak denetler. `topla.py`'nin
    defter koşulu buna göre okunur (madde 8 ile aynı): dondurmadaki defter (KOD_DONDURMA `deneme_defteri_sha256`) bugünkü
    defterin bir satır sınırında biten baş kısmı olmalıdır (defter yalnız sona satır eklenerek değişir); TOPLAMA kaynağına
    hem dondurmadaki hem güncel defterin sha256'sı yazılır.
    (g) **Teknik yeniden koşunun kilit zinciri.** İlk `KILIT.json` değişmez ve yeniden üretilmez. Kapı ya da banka
    için izin verilen teknik düzeltme (her biri için en fazla 1) bir ek kayıtla zincirlenir: `KILIT_TEKNIK_<n>.json` =
    {ilk_kilit_sha256, önceki kayıt sha256, gerekçe, hatayı gösteren test, değişen kod/motor kimlikleri, yeni test
    raporu, defter satırı}. Ekonomik belgelerin (MIMARI, CARRY, BANKA, açık sorular, kalibrasyon) hash'leri ilk kilitteki
    ile aynı kalmalıdır; yalnız kod, motor, test ve defter kimlikleri değişebilir. `kilit.py` zinciri doğrular.
    **(g) revizyonu (Codex T28, 1 Ekim; kilitten önce).** Ek türleri ve hakları: `kapi` (hüküm öncesi, en fazla 1),
    `banka_oncesi` (en fazla 1), `banka_sonrasi` (en fazla 1; yalnız (d)'deki hüküm sonrası düzeltilmiş koşu). Ek kaydın
    içeriği kilit içeriğidir, şu farkla: kalibrasyon ön koşulları (bitiş, toplama, duman, eşdeğerlik, B5 A) ilk kilitte
    doğrulandı ve ekte yeniden doğrulanmaz (teknik düzeltme parametre, eşik ve davranışı değiştirmez, §2.5); onların
    yerine düzeltilmiş motorla yeni V1 test raporu ve hatayı gösteren test zorunludur. **Değişmezler** (ilk kilitle bayt
    düzeyinde aynı): defter dışındaki bütün belgeler, parametre kimlikleri, ortam, veri (manifest, evren), sabitler.
    **Değişebilir:** kod kimlikleri; defter yalnız sona satır eklenerek (ilk kilitteki defter bugünkünün baş kısmı) ve
    satır sayısı ilk kilit + ek sıra numarası olacak biçimde. Her ek kayıt commit edilip uzak depoya itilir; doğrulama
    (`kilit.zincir_dogrula`) ilk kilidin ve her ekin uzak commit'ini (`git_denetimi`) ve zinciri (ilk kilit sha256'sı,
    önceki kayıt sha256'sı, sıra) denetler; kapı ve banka koşuları ek varsa zinciri doğrular. **Codex T29 ekleri (kod öncesi):**
    her ekin defter sha256'sı sonraki eklerin ve bugünkü defterin satır sınırında biten baş kısmı olmalıdır (önceki ekin
    satırı değiştirilemez); doğrulayan aşama yalnız kendi türlerini kabul eder (kapı koşusu yalnız `kapi`; banka
    koşusu `kapi`, `banka_oncesi`, `banka_sonrasi`). Banka girişinin zincir doğrulaması dondurmayla (7.01) bağlanır:
    `banka_kos` kodu kilit kimliğine değil DONDURMA'ya (banka_kos_sha256) girer; DONDURMA `kilit_sha256`'yı ve varsa son
    teknik ekin sha256'sını taşır ve `banka_kos.py` T1'de bunları `kilit.zincir_dogrula` ile denetler.

**Görülmüş bilgi.** ρ_f = 0,6, D'deki medyan korelasyona (0,64) yakındır; bu yüzden 0,3 de koşulur. ℓ_e ve δ, D özetlerini
görmüş tasarımların yön değişimi ve devir tahminlerinden gelir. φ, s, ν, κ, HL, SR_ref ve Düzey 2 ölçekleri istatistiksel ya
da motor mekaniği gerekçelidir. σ_M, σ_I ve hacim aralığı motor tabanlarından türetildi, D istatistiğinden değil. Eşik
kuralları hiçbir D P&L'ine dayanmaz.

---

## 4. Kelly tablosu

- **Kaldıraç ızgarası (dondurulur):** L ∈ {0,5; 1; 1,5; 2; 2,5; 3; 4}. Her L **ayrı tam koşudur**. Bütün tavanlar (isim, brüt, S1,
  S2, B'de S4) w^L üzerinde, kaldıraç sonrası NAV'da ve L'den bağımsız değerlerle aktiftir (MIMARI §3.4–3.5). 2L sonucu L
  sonucundan türetilmez.
- **Kelly karşılığı:** L = 1 koşusundan tam Kelly f* = μ/σ² (günlük basit getiri, yıllık). Her L için "Kelly kesri" = gerçekleşen
  vol_L / (f*·vol_1). 0,25 / 0,5 / 0,75 / 1 kesirlerine en yakın L satırları işaretlenir. Kesir satırı ayrıca koşulmaz.
- **Her L için sütunlar** (birincil örneklem; ayrıca Z1 dilimlerinin en kötüsü): CAGR, gerçekleşen vol, SR, MDD, en uzun DD süresi,
  Calmar, en kötü gün, en kötü ay, S1/S2/brüt/isim bağlama sıklığı, gerçekleşen kitapta S1/S2 aşım günü oranı, D90-1 / D90-2 /
  D90-4, SQ-1 / SQ-2 / SQ-4 ve DM-1 altında MDD (§5.4), blok bootstrap (20 gün, 2.000 çekiş) 3 yıllık MDD'nin q50 ve q95'i,
  P(MDD > %30). B'de carry bacağının gerçekleşen betası (R8).
- **%30 DD sınırı:** her satırda "gerçekleşen MDD ≤ %30" ve "bootstrap q95 ≤ %30" evet/hayır olarak işaretlenir.
- Şok tavanı gerçekleşmiş DD sınırı değildir; %30 sınırının sağlandığı tavandan iddia edilemez.
- Tablo birincil NAV ve 1× maliyette; ayrıca 2× maliyette tekrar edilir.

**Uygun kaldıraç kümesi (bağlayıcı; KC-10).** Kilitten önce yazılır ve bankadan sonra mekanik olarak uygulanır.

    𝓛* = { L ∈ ızgara : MDD_gerçekleşen(L) ≤ %30  VE  q95_bootstrap MDD(L) ≤ %30 }     (birincil örneklem, 1× maliyet, birincil NAV)

1. İki koşulu birden sağlamayan hiçbir L, KABUL sonrası önerilen kaldıraç kümesine giremez. Demo ön-kaydında seçilemez.
   Tabloda bu satırlar **"kullanıcı hedefini (%30 DD) KARŞILAMIYOR"** diye açıkça işaretlenir.
2. **Varsayılan öneri:** 𝓛* içinde birincil örneklem CAGR'ı en yüksek L. Eşitlikte küçük L. CAGR ile Sharpe arasında kaldıraç
   yüzünden fark varsa CAGR kullanılır. Sharpe L'den neredeyse bağımsızdır; büyüme kaldıraç seçiminin hedefidir.
3. Kullanıcı 𝓛* içinden varsayılandan **küçük** bir L'yi serbestçe seçebilir. 𝓛* dışından seçim yoktur. 𝓛* dışında bir L
   kullanmak yeni bir kaldıraç kararıdır: yeni ön-kayıt ve banka dışı yeni kanıt ister, bu bankada sınanamaz.
4. **𝓛* boşsa** (her L'de koşullardan biri sağlanmıyorsa, L = 0,5 dahil) rapora şu cümle zorunlu olarak yazılır: "**Kullanıcı
   hedefine (%30 DD) uygun kaldıraç yok.**" Hüküm yine L = 1'e dayanır; KABUL ise KABUL kalır. Ancak ileri demo ön-kaydı bu
   bankadan bir L öneremez. Izgaranın altında bir L için bankada ek koşu yapılmaz. Konu kullanıcıya sunulur.
5. L = 1 ∉ 𝓛* olabilir. Hüküm L = 1'dedir; bu durum KABUL'ü değiştirmez. Öneri yalnız hesaplanan 𝓛* ve CAGR sıralamasından çıkar (netleştirme 21 c).
6. 2× maliyet tablosu ve stres sütunları (D90, SQ, DM) 𝓛*'ı daraltmaz; rapordur. Kullanıcı Adım 1'de §5.5'teki stres
   bağlayıcılığını seçerse (§11 soru 4) aynı stres koşulu 𝓛*'ın tanımına da eklenir. Bu seçim kilitten önce yazılır.

- **Kaldıraç seçimi bankadan sonra, yalnız 𝓛* içinden yapılır.** Seçim hükmü değiştirmez. Hüküm L = 1'e dayanır. Ek L koşusu
  yapılmaz.
- **Örneklem içi uyarı (K2-08):** seçilen L'nin DD değerleri banka örnekleminin içindedir. 𝓛*'ı banka örnekleminden seçmek
  seçim yanlılığı taşır. Demo ön-kaydı, seçilen L için DD beklentisini gerçekleşen MDD ile değil, bootstrap q95 ile yazar ve
  bunun iyimser olabileceğini belirtir.
- **Yeniden örnekleme uyarısı (KC-10, zorunlu rapor cümlesi):** "Blok bootstrap geçmiş getirileri yeniden örnekler. Marjin
  çağrısı, otomatik kaldıraç azaltma (ADL), tasfiye ve bankada gerçekleşmemiş kuyruk olaylarını üretmez. %30 DD sınırı hiçbir
  L için garanti edilemez." Motor ADL ve marjini modellemez (§8.2 madde 13). Yüksek L'de gerçek DD, tablodakinden büyük olabilir.

---

## 5. Hayatta kalan yanlılığı

### 5.1 Kaynak
- Banka, uygun evrenden seçildi: ≥36 aylık 1h geçmiş, ilk dosya ≤ 2023-09.
- Z1'de listelenip 36 aydan kısa sürede ölen coinler evrende yoktur. Mühür bunu açıkça yazar: 20 eski coin evren dışında kaldı.
  Karar gereği mühür değişmez ve ek banka kurulmaz; bu coinler eklenmez.
- ≥36 ay yaşayıp sonra listeden çıkan 8 coin evrendedir. Bu yanlılığı azaltır, gidermez.
- Z2'de, 2023-09'dan sonra listelenen coinler aday değildir. Z2 evreni eksiktir.
- D evreni de aynı biçimde yanlıdır (MIMARI §9 zaaf 8).

### 5.2 Yön (kanal kanal)
Simetrik trend için yön belirsizdir.
1. **Yavaş ölüm** (uzun süreli düşüş): trend short'u kazanır. Eksik coin kaçan short kârıdır. Yanlılık stratejinin **aleyhine**.
2. **Ani çöküş** (günler içinde −%90 ve üstü): trend o sırada long ise büyük kayıp. Eksik coin kaçan kayıptır. **Lehine**.
3. **Ölüm öncesi sıkışma:** short'lar zarar eder. **Lehine**.
4. **Sıra ikamesi:** hacimce yüksek bir ölü coin, sıra evreninde yaşayan bir coinin yerini alırdı. Net etki iki coinin P&L farkıdır;
   işareti belirsiz.
5. **Carry (B):** negatif funding'li long bacak distresli coinleri tutar. Eksik ölümler long zararını gizler. Açıkça **lehine**.

Kanal 1 ve 4 ölçülemez (veri yok). Kanal 2 (ve B'de kanal 5'in long bacağı) için D90, kanal 3 için SQ, eşzamanlı ölümler için
DM stres bindirmeleri §5.4'tedir. **Hiçbiri üst sınır değildir** (KC-11). Her biri önceden belirlenmiş tek bir kanalın
kötümser bir bindirmesidir. Ardışık ve eşzamanlı olayların bütün birleşimlerini, sıra ikamesini (kanal 4) ve kanal 1'i
kapsamaz.

### 5.3 Büyüklük (kaba)
L = 1'de tek alt long ağırlığı tipik olarak NAV'ın %1–3'üdür (birim kitabın brütü tam sinyalde ~%20–25, 15 isim). Tek ani çöküş:
−%0,9 ile −%2,7 NAV. L = 3'te isim tavanı %6 ile −%5,4 NAV. L = 1'de beklenen yıllık getiri kabaca %4–6'dır (SR 0,5 × vol %7–11; MIMARI §3.3).
Yılda bir olay kenarın dörtte birinden yarısına kadarını silebilir. Bu hesap banka verisi kullanmaz.

### 5.4 Kanal stres bindirmeleri (deterministik; R12)
Üç aile vardır. Hepsi tasarımların küçük delist cezalarına (h_L %10, h_S %5) **ek** olarak uygulanır. Hepsi aynı blok ve gün
seçim kuralını kullanır.

| Aile | Kanal | Nesne | Şok | Ertesi gün NAV çarpanı |
|---|---|---|---|---|
| **D90-k** | 2 (ani çöküş; B'de 5'in long bacağı) | En büyük tek alt **long** ağırlığı w_max | −%90 | 1 − 0,90·w_max |
| **SQ-k** | 3 (ölüm öncesi short sıkışması) | En büyük tek alt **short** ağırlığının mutlak değeri \|w_min\| | +%300 (S4 ile aynı büyüklük; MIMARI §4.5) | 1 − 3,00·\|w_min\| |
| **DM-1** | 2, eşzamanlı çoklu ölüm | O gün en büyük **üç** alt long ağırlığı w₍₁₎, w₍₂₎, w₍₃₎ | Üçüne aynı anda −%90 | 1 − 0,90·(w₍₁₎ + w₍₂₎ + w₍₃₎) |

**D90: yalnız long çöküş bindirmesi (KC-11).** D90 yalnız kanal 2'yi temsil eder. Short sıkışmasını (kanal 3), eşzamanlı çoklu
ölümü ve sıra ikamesini göstermez. Örneğin kitap yalnız %4 alt short taşıyorsa D90 zarar eklemez. Aynı gün SQ'nun +%300
sıkışması NAV'ın %12'sini götürür. B'de alt short tavanı %3,33 olduğundan SQ olayı başına en fazla ~%10 NAV götürür (S4
sınırı). A'da tavan %4 olduğundan en fazla %12 götürür.

**Ortak kurallar (üç aile).**

**Sıklık olay/yıl olarak tanımlanır (K2-13).**
- D90-k ve SQ-k: yılda k olay, k ∈ {1; 2; 4}. DM-1: yılda 1 olay. Aileler ayrı ayrı uygulanır; birbirine eklenmez.
- Birincil örneklem baştan itibaren 365/k günlük ardışık bloklara bölünür. Son blok kısmiyse, uzunluğu blok uzunluğunun en az
  yarısıysa olay uygulanır; değilse uygulanmaz.
- Her blokta, **gerçekleşen** net kitapta (gün sonu pozisyonları, koşunun L'si ile) ailenin nesnesinin en yüksek olduğu gün
  seçilir (K1-20.12). Nesneler şunlardır: D90'da en büyük tek alt long ağırlığı; SQ'da en büyük tek alt short ağırlığının
  mutlak değeri; DM'de en büyük üç alt long ağırlığının toplamı. Eşitlikte önceki gün seçilir. O blokta nesne 0 ise
  (ör. hiç alt short yoksa) olay NAV'ı değiştirmez ve "boş olay" olarak sayılır.
- Ertesi gün NAV çarpanı tablodaki gibidir. Karşı tarafa kredi yazılmaz: D90 ve DM'de short kazancı, SQ'da long kazancı
  sayılmaz.
- Bindirmedir: sonraki günlerin getirileri değişmez (ağırlıklar NAV oranıdır). Coin yoldan çıkarılmaz.
- B'de carry long'u ve carry short'u net kitaba dahil olduğu için kapsanır.
- Delist sonrası funding: bindirme funding yazmaz. Motor içindeki çıkılamayan pozisyonlarda funding tahakkuku MIMARI'nin nihai
  kuralına göre işler (bkz. §10 madde 9, K1-02).
- Şok büyüklükleri dondurulmuştur: −%90 (KARARLAR §1.2), +%300 (MIMARI S4). S2'nin +%100'ü tavan senaryosudur, stres değil.
  Bu değerler bankadan kalibre edilmez.

**Beklenen olay sayısının kaba sınırları (yalnız mühür sayıları).**
- Mühür: 36 aydan kısa sürüp ölen 20 coin; arşivin ~3,5 yılına oranla yılda ~6.
- Üst uç: hepsi ölüm anında kitapta ve long → yılda ~6.
- Kitap payı ölçeği: 13 alt yuvası / ~200 aday alt → yılda ~0,4. Hacim seçimi ölümden önce yüksek hacimli coinleri kayırıyorsa
  gerçek oran bu payın üstündedir; bilinmiyor.
- D90-1 bu iki değerin arasındadır. D90-2 ve D90-4 stres senaryosudur. SQ-k'nın sıklığı için mühürde sayı yoktur; D90 ile aynı
  ızgara simetri gereği kullanılır.

**Gerekçe.** Deterministiktir; tohum ve olasılık yoktur. En yüksek maruziyet günü seçildiği için her aile kendi kanalında
kötümser bir bindirmedir, **üst sınır değildir** (KC-11). Aynı gün birden çok kanalın birlikte gerçekleşmesi, bir blokta k'dan
fazla olay ve sıra ikamesi kapsanmaz. Sıklık önseldir, banka verisinden kalibre edilmedi. Rastgele p olasılıklı tanım
reddedildi: sonucu tohuma bağlar ve p'nin kalibrasyonu banka verisi ister.

### 5.5 Kabule etkisi
- **Varsayılan: stres senaryoları rapordur** (R12, Kelly sütunları). Gerekçe:
  1. KARARLAR §1.2 delist kaybının −%90 senaryosuyla "raporlanmasını" ister.
  2. Sıklık önseldir (K2-13). Bağlayıcı yapmak hükmü önsel bir sabite bağlar. Bu bir **risk tercihi** sorusudur, istatistik
     sorusu değildir.
  3. Round-1'deki "olay sayısı 30'un altında olan senaryoya bağlayıcı eşik konmaz" gerekçesi **geri çekildi** (KC-11). n < 30
     kuralı örnekten kural seçmeyi yasaklar. Önceden belirlenmiş ekonomik bir stres sınırı koymayı yasaklamaz.
- **Bağlayıcılık kullanıcının risk tercihidir; Adım 1'de yazılır (§11 soru 4).** Seçenekler:
  - (i) Rapor (varsayılan).
  - (ii) **B12, bağlayıcı:** D90-1 altında SR ≥ 0,30 **ve** SQ-1 altında SR ≥ 0,30. Seçilirse aynı iki koşul L başına
    uygun kaldıraç kümesi 𝓛*'ın tanımına da girer (§4 madde 6).
  Seçim `ACIK_SORU_YANITLARI.md`'ye yazılır ve kilitle hash'lenir. **Raporlama kararı sessizce değiştirilmez.** Kilitten
  sonra (i) ile (ii) arasında geçiş yoktur. Rapor hangi seçeneğin kilitlendiğini ve hash'ini yazar. (ii) seçilirse §3.7
  kalibrasyonu B12'yi içermez, çünkü sentetik üreteç kitap ağırlığı üretmez. Bu, ölçülmemiş ek katılık olarak raporda belirtilir.
- Rapor, yanlılığın yönünü kanal kanal yazar. Hükmün yanına şu iki cümle zorunludur:
  "Hayatta kalan yanlılığı giderilmedi." ve "B2 (DSR) ve birincil Sharpe hayatta kalan yanlılığına göre düzeltilmedi."
  Ayrıca: "D90, SQ ve DM tek kanallı stres bindirmeleridir; hayatta kalan yanlılığının üst sınırı değildir."

---

## 6. Bankanın asimetrik gücü ve yorum

Bu bölüm yorumdur. Buradaki hiçbir cümle eşik ya da parametre gerekçesi değildir (K2-06).

- Kanıt jürisi ve kırmızı takıma göre Z1 trend için elverişli, carry için ters rejimdir. Trend önselini veren literatürün
  örneklemi Z1'i kapsar.
- **A geçerse:** Trend önseli görülmemiş zamanda ve maliyetler dahil yeniden ölçülmüş olur. Bu önselin bağımsız kanıtı değildir;
  zayıf bir doğrulamadır. İleri demo gerçek hakemdir.
- **A kalırsa:** v8 trend çekirdeği bu haliyle kapanır.
- **B geçerse:** B'nin toplamı geçmiştir. Carry bacağı Z1'de negatif olsa bile hüküm değişmez; carry satırları yalnız rapordur.
  B'nin seçilmiş olması "carry getirisi fiyattan gelmiyor" demek değildir; kapının bu ayrımı yapma gücü düşüktür (K2-02). Bu cümle
  rapora girer.
- **B kalırsa:** RET. A'nın banka sonucu iyi olsa bile A'ya geçilmez.
- **Birlikte katılık:** bağlayıcı ölçütler birbiriyle yüksek korelasyonludur (B2, B3, B4, B8 aynı getiri serisine dayanır).
  Birleşik güç §3.7'de ölçülür; P(KABUL | SR) eğrisi rapora girer.
- Rejim dilimleri (B6), en iyi yıl hariç (B4) ve rejim-null (B7), sonucun tek bir rejimden gelip gelmediğini sınar.

---

## 7. Sonrası

### 7.1 KABUL
- İleri demo **ayrı bir kapıdır** ve ayrı ön-kayıt ister. Gerçek para ve mainnet işlemi yoktur.
- Kullanıcı L'yi demodan önce, yalnız uygun kaldıraç kümesi 𝓛* içinden seçer ve yazar (§4). 𝓛* boşsa demo ön-kaydı bu
  bankadan L öneremez. DD beklentisi bootstrap q95 ile yazılır (§4).
- Sinyal ve hacim mainnet kamu verisinden, emirler yalnız yetkili demodan. Ekonomik hakem arşiv ikizi, demo yalnız icra hakemi.
  Süre ≥ 3 ay. Parametre değişmez.
- Demo hesabında listelenmeyen sembollerin hedefi 0'dır ve yeniden dağıtılmaz; bu semboller demo ön-kaydında listelenir (K1-18).
- Demo kabul ölçütleri (kayma oranı, funding farkı, parite) demo ön-kaydında, demo başlamadan yazılır.
- Mühür §7'ye göre ayrı demo hesabı gerekebilir; bu kullanıcı kararıdır.

### 7.2 RET
- v8 bu mimariyle kapanır. Aynı bankada kurtarma **yasaktır**: parametre değişikliği, carry'yi çıkarma ya da ekleme, coin
  çıkarma, eşik değişikliği, B'den A'ya geçiş, farklı L ya da NAV ile hüküm.
- Yeni bir model yeni hipotez, yeni ön-kayıt ve yeni doğrulama verisi ister. Ek banka kurulmayacağı için tek temiz kaynak mühür
  tarihinden sonraki ileri dönemdir.
- Sonuç deneme defterine ve DURUM.md'ye yazılır. REV1 süreci etkilenmez.
- **Kullanıcı kararı (1 Ekim 2026; kilitten ve kapı koşusundan önce, D P&L'i ve banka görülmeden; ACIK_SORU_YANITLARI
  #26):** RET, TEKNİK GEÇERSİZ sonrası NOT_EVALUATED ya da ikinci teknik geçersizlik hâlinde v8'i ilerletmek için ek
  çaba yapılmaz (yeni varyant, yeni ön-kayıt ya da ileri dönem denemesi bu kararla başlatılmaz). Bulgular temize
  çekilir ve **sonuç ne olursa olsun** (KABUL dahil) GitHub'da açık olarak yayımlanır: ön-kayıt belgeleri, kilit ve
  dondurma kayıtları, kalibrasyon ve kapı sentetik doğrulaması, banka raporu, deneme defteri ve kod. Yayımdan önce
  gizli bilgi taraması yapılır (anahtarlar, .env, sunucu bilgileri, kişisel bilgiler, lisanslı ham veri; git
  geçmişi dahil); depoyu açık yapmak kullanıcının eylemidir.

### 7.3 TEKNİK GEÇERSİZ ve NOT_EVALUATED
§2.5. En fazla bir teknik yeniden koşu; ikincisinde NOT_EVALUATED. Hüküm açıldıktan sonra hükmü değiştiren hata da
NOT_EVALUATED'dır. NOT_EVALUATED mimariyi kapatır; ileri demoya gidilmez.

---

## 8. Kaydedilecek çıktılar ve rapor şablonu

### 8.1 Çıktılar (hepsi `SONUC_DAMGA.json`'da hash'li)
Açık grup (`denetim/`):
- `veri_raporu.json`: manifest hash'leri, eksik saatler, doldurulan funding kayıtları, borsa çapı boşluklar, filtresi olmayan
  sembol sayısı, süreklilik sorunları, Eylül funding kaynağı.
- `degismezler.json`: T4 denetimleri; null hijyen sayaçları.
- `parite.json`: T5 tekrarları.
- `gunluk.log`: ilerleme günlüğü (metriksiz).

Kapalı grup (`sonuc/`, şifreli; düz metin sha256'sı damgada):
- `banka_sonuc.json`: bütün ölçütler, eşikler, geçti/kaldı, güven aralıkları.
- `nav_<koşu>.csv`: her koşunun günlük NAV'ı ve getirisi (ana, maliyet × NAV ızgarası, Kelly ızgarası, K-evren, tek coin
  çıkarma, lot kapalı, demo NAV, B ise A).
- `pnl_ayristirma.csv`: MIMARI §4.7 satırları, günlük.
- `epizotlar.csv`, `tavan_baglama.csv`, `kelly_tablosu.csv` (𝓛* işaretli), `rejim_null.csv`, `stres.csv` (D90, SQ, DM).
- Açık gruba ek: `null_degismezler.json` (N1–N6 sonuçları ve hash'ler; performans içermez).

**Anonim kimlik (K1-16).** Coin düzeyindeki bütün tablolar `C001…` kimliği kullanır. Sıra, yerel ve gizli bir anahtarla
HMAC-SHA256(anahtar, sembol) değerine göredir. Anahtar ve eşleme dosyası yerel kalır; yalnız hash'leri raporlanır. Coin
tablolarında listeleme tarihi ve mutlak hacim yazılmaz; yalnız hacim dilimi etiketi (MIMARI §6 dilimleri) yazılır. Raporda coin
adı geçmez (BTC/ETH hariç).

### 8.2 Rapor şablonu (`BANKA_RAPORU.md`)
1. **Hüküm:** KABUL / RET / TEKNİK GEÇERSİZ / NOT_EVALUATED. Mimari. Kilit, dondurma, denetim ve sonuç hash'leri.
2. **Bağlayıcı tablo:** B2–B11; değer, eşik, geçti/kaldı, %90 güven aralığı. Kalibrasyonla sabitlenen eşikler ve rapora inenler.
3. **Birincil sonuç:** SR (R11), CAGR, vol, MDD; birim ve gerçekleşen vol.
4. **DSR:** B2 türü (B/R) ve d*; σ_SR_bağ ve kaynağı (REV1 ya da "varsayım" cümlesi); N_hüküm, SR₀, γ₃, γ₄, η; R16
   duyarlılık tablosu. "DSR bir performans çıtasıdır; birleşik yanlış kabul §3.7'de ölçüldü (B7 dahil olanı için üst sınırın nokta tahmini ve Wilson aralığı)"
   cümlesi.
5. **Rejim dilimleri** ve Z2 teşhisi.
6. **Ayrıştırmalar:** fiyat/funding/maliyet; BTC-beta/dominans/artık; long-beta; REV1 korelasyonu. B ise: A ayrıştırması, bacak
   satırları, netleme kazancı, icra artığı, L başına carry betası.
7. **Görülmemiş coinler** ve güç notu (B9, R15).
8. **Kelly tablosu**, %30 işaretleri, uygun kaldıraç kümesi 𝓛* ve varsayılan öneri (ya da "uygun kaldıraç yok" cümlesi),
   örneklem içi uyarısı ve yeniden örnekleme uyarısı (§4).
9. **Hayatta kalan yanlılığı:** kanallar, D90-1/2/4, SQ-1/2/4, DM-1, h_L senaryoları, kilitlenen bağlayıcılık seçeneği
   (§5.5), üç zorunlu cümle.
10. **Maliyet ve kapasite:** NAV × maliyet ızgarası, gecikme maliyeti, devir, katılım gecikmesi, gerçekleşen tavan aşımları, lot
    ve demo NAV etkisi.
11. **Veri ve teknik:** T1–T5, denetim listesi, teknik yeniden koşu ya da açılış sonrası düzeltme varsa iki sonucun
    karşılaştırması.
12. **Güç:** §3.7 Düzey 1'in P(KABUL | SR) eğrileri; Düzey 2-a'nın κ = 0'daki B7'siz P(KABUL) değeri (B7 dahil yanlış
    kabulün üst sınırının nokta tahmini, Wilson aralığı ayrı; A ve B; "tarama kuralı, güven kanıtı değil" notu); Düzey
    2-b'nin betimsel B7 güç tablosu; R17 null tanıları.
13. **Sınırlar:** asimetrik güç, korelasyonlu kesit, hayatta kalan yanlılığı, mark vekili (uzlaşma damgası T için [T−1h, T) barının
    kapanışı; MIMARI §2.1), ADL/marjin modellenmedi, tarihsel sembol filtresi yok, B'nin funding/fiyat ayrımının gücü düşük.

---

## 9. "Kapısız A" sorusu (K2-03) — KAPANDI

**Kullanıcı kararı (27 Eylül, ASAMA4B_KARAR §1 madde 1): (a) kapı → A/B kalır.** Kapısız A seçilmedi. Carry kapısı Codex'in
KC-03/04/05/06/07 bulgularıyla düzeltilerek korunur (CARRY ve MIMARI belgelerinin konusu). Aşağıdaki gerekçe ve seçenekler
tarihsel kayıttır. Sayılar ρ = 0 içindir. ρ = 0,30'da başabaş carry Sharpe'ı çok daha yüksektir (Codex KC-07: ≈ 0,37). Bu
etkinin kapı eşiğine yansıtılması CARRY belgesindedir.

**Gerekçe (sayılı).**
1. B bankada bütün olarak yargılanır. B seçilirse A'nın sonucu hükme girmez. Yanlış kabulün asıl bedeli, carry'nin yılda
   ~−%0,6'lık sürüklemesi değil, iyi bir trendin B içinde RET yemesidir.
2. **Seyreltme aritmetiği** (ρ = 0; σ_T = %9, σ_C = %3; kaba):
   SR_B = (SR_T·σ_T + SR_C·σ_C) / √(σ_T² + σ_C²).
   - SR_T = 0,85, SR_C = 0 → SR_B ≈ 0,81.
   - SR_T = 0,85, SR_C = −0,3 → SR_B ≈ 0,71.
   - σ_T = %7 alınırsa SR_C = 0'da SR_B ≈ 0,78.
3. **Başabaş.** B, A'yı seyreltmemek için bankada SR_C ≥ SR_T·(√(σ_T² + σ_C²) − σ_T)/σ_C gerektirir. SR_T = 0,85'te bu σ_T = %9 için
   ≈ 0,14, σ_T = %7 için ≈ 0,17'dir. Sıfır Sharpe'lı, korelasyonsuz bir carry bile SR'ı %5–8 düşürür.
4. B2 çıtası σ_SR = 0,30'da SR₀ ≈ 0,88'dir (§3.3 tablosu). SR_T bu çıtanın hemen üstündeyse seyreltme onu altına iter.
5. Kapının gücü düşüktür (CARRY §7): 33 ayda carry'nin kenarı ile sıfır ayrılamaz. Kapıyı geçmek, carry'nin bankada başabaşı
   aşacağını göstermez.

**Seçenekler (tarihsel; kullanıcı (a)'yı seçti).**
- (a) Mevcut karar: kapı → A/B. **Seçildi.**
- (b) Kapısız A: carry bu bankaya hiç gitmez; ayrı bir ön-kayıtla ileri dönemde sınanabilir. Kullanıcı kararının değişmesini
  gerektirir.
- (c) Kapı kalır; kapının net ölçütü, bankadaki seyreltmeyi karşılayacak düzeyde gerekçelendirilir (kapı belgesinin konusu).

**Sayısal sunum.** §3.7'deki B seyreltme koşusu, A ve B için P(KABUL | SR_T) eğrilerini SR_C ∈ {−0,3; 0; 0,3} ve ρ ∈ {0; 0,30}
için verir. Bu eğriler artık karar girdisi değildir; rapordur.

---

## 10. ARAYUZ_DEGISIKLIGI

Belgeler arası arayüzde v1 metinleri ortak referanstır. Bu belgenin v1'e göre değiştirdiği ya da yeni tanımladığı arayüz öğeleri:

1. **ÖN-KAYIT KİLİDİ (yeni ortak arayüz, ana oturum notu 1).** Sıra ve adlar §1.2'dedir: Adım 0 motor testleri → 1 açık sorular →
   2 HAR seçimi → 3 sentetik kalibrasyon → 4 ÖN-KAYIT KİLİDİ (`KILIT.json`) → 5 kapı koşusu (D'deki ilk P&L) → 6 D doğrulaması ve
   kuru koşu → 7 DONDURMA → 8 banka. Adım 3 bu belgeye özgüdür; öteki iki belge onu "banka ön-kaydının parçası" olarak okuyabilir.
   Üç belgede adlar farklı çıkarsa sayı kontrolünde bu tabloya bağlanması önerilir.
2. **Maliyet çarpanı (ana oturum notu 3, K1-06).** v1 B3'teki "(ücret dahil)" ifadesi kaldırıldı. Tanım MIMARI §6'nın nihai halidir;
   bu belge atıf yapar. Bankada her çarpan tam yeniden koşudur. Kapının yöntemi kapı belgesinindir; K1-06 iki belgede aynı yöntemi
   önerir.
3. **Deneme sayacı.** N_v8 = Σ max(1, varyant_sayisi); `A2-mikroyapi` 144, `A2-ml` 5 olarak düzeltilir. Sayım kuralı: alternatif
   şartname girer; alt küme, ölçek ve yeniden fiyatlama girmez (§3.3). Kapı belgesinin DSR raporu aynı sayacı kullanmalıdır.
4. **Ölçüt adları.** Eski B1 → R11, eski B12 → R12. B2–B11 kimlikleri korundu. B5, B6, B10 eşikleri kalibrasyon değişkenleridir
   (e_B5, k_B6, e_B10).
5. **B5 epizotu B'de trend sanal bacağında** (MIMARI §4.7 sanal pozisyonları).
6. **D90 w_max gerçekleşen kitaptan** (gün sonu pozisyonları).
7. **CTA çekirdeği ve DD çarpanı ablasyonu bankada koşulmaz (K2-08).** MIMARI §1a ve §3.5'teki "banka taslağında betimsel satır
   olabilir" atfı artık geçersizdir; MIMARI revizörünün bu atfı kaldırması önerilir. Uydu tanımı ve ω_C = 0,20 değişmedi.
8. **Isınma: sürekli koşu (v1'den).** MIMARI §2.4 "her değerlendirme penceresine ısınma" der. Banka tek sürekli koşu kullanır;
   pencereler metrik pencereleridir.
9. **Delist sonrası funding (K1-02).** Bu belge, çıkılamayan pozisyonda funding tahakkukunun coinin son barında durduğunu ve 30 gün
   beklemede funding yazılmadığını varsayar (K1-02 önerisi). MIMARI nihai hali farklı bir kural koyarsa R9 ve D90 o kurala göre
   okunur; bu belge değişmez.
10. **T4 nesnelere ayrıldı (K1-04; 2. turda KC-09 ile değişti; ana oturum bu belgeyi MIMARI'nin nihai lettering'iyle
    hizaladı).** T4-a birim trend kitabı w^u: V ≤ τ, M̃ ≤ M_max (MIMARI §3.3). T4-b carry birim kitabı w^C, ω_C/L
    öncesi: V ≤ τ (MIMARI §4.4 adım 1). T4-c carry bloğu, ω_C·L ve tavan uygulanmış: V ≤ ω_C·L·τ, artı MIMARI'nin
    nihai halinde tanımlanan carry değişmezleri (KC-04 hedge nötrlüğü dahil; MIMARI §4.4–4.5). T4-d kaldıraçlı net
    hedef kitap w*: tavan uyumu + toplam risk kuralı V(w*) ≤ L·(1+ω_C·𝟙_B)·τ (MIMARI §3.4–3.6, §4.5). T4-e
    muhasebe. T4-f null değişmezleri. Gerçekleşen/devreden defter T4 değildir, R5'tir (MIMARI §5.7). MIMARI §3.5'teki
    "banka T4 bu tabloyu kullanır" atfı T4-a/b/c/d'nin dördüne birden karşılık gelir.

**2. tur (Aşama 4b) arayüz öğeleri:**

11. **DSR (KC-08).** Sayaç kuralında HAR seçimi +2 (iki varyant). CARRY'nin betimsel DSR raporu aynı N'yi ve §3.3'ün η
    düzeltmeli formülünü σ_SR_bağ ile kullanmalıdır. σ_SR_bağ, B2 türü ve d* Adım 3'te sabitlenir.
12. **Rejim-null üretim modunda (KC-01).** Banka null'u MIMARI §5.1'deki "dış bayrak modunu" kullanmaz. Motor sentetik
    gorunum'dan bütün bayrakları, maskeyi ve evreni kendisi türetir. MIMARI'nin bu kancayı tutması zararsızdır; bankanın
    ihtiyacı yoktur. Motorun sentetik yol için tek gereksinimi, gorunum'un dışarıdan verilmiş (yeniden bazlanmış) bar,
    hacim ve funding kayıtlarından kurulabilmesidir.
13. **Kilit sırası (KC-02).** §1.2 tablosunun adları ve sırası değişmedi. Adım 3 artık σ_SR/B2/d* ve B7 kuantilini de
    sabitler. Adım 1'deki hiçbir soru kalibrasyon çıktısına bağlı değildir. *(3. revizyonla değişti: B7 kuantili
    sabitlenmez, q95'tir; §0.2, madde 15.)*
14. **Stres aileleri (KC-11).** D90 yalnız long; SQ ve DM eklendi. SQ şoku +%300 bu belgede dondurulmuştur. Bugünkü MIMARI
    §4.5 S4 büyüklüğüyle aynıdır, ancak ona bağlı değildir: MIMARI S4'ü değiştirse de SQ +%300 kalır.

**3. revizyon (29 Eylül) arayüz öğesi:**

15. **Kalibrasyon Düzey 2 (§0.2, §3.7).** B7 q95'e sabit; B7 dahil birleşik yanlış kabul üst sınırla; B7 gücü betimsel. Kilit
    sırası (§1.2) ve öteki iki belge değişmez. HAR seçimi (Adım 2) bu revizyondan önce tamamlandı; sonuç bu belgenin hiçbir
    sayısına girmez.

---

## 11. Açık sorular (Adım 1'de, kilitten önce yanıtlanır)

**Hepsi yanıtlandı** (`ACIK_SORU_YANITLARI.md`: 1 → #14, 2 → #15, 3 → #16, 4 → #12 (seçenek (i): rapor), 5 → #1, 6 → #6, 7 → #17, 8 → #5, 9 → #18, 10 → #4, 11 → #19 ve #25, 12 → #20).

1. **DSR eşiği — KAPANDI. Kullanıcı kararı (27 Eylül, ASAMA4B_KARAR §1 madde 2):** DSR tek sabit bağlayıcı eşik değildir.
   σ_SR için {0,20; 0,30; 0,50} duyarlılık tablosu raporlanır. σ_SR_bağ, B2'nin bağlayıcı mı rapor mu olduğu ve d*, §3.3'ün
   yazılı kurallarıyla Adım 3'te, D performansına bakılmadan sabitlenir.
2. **Birincil örneklem yalnız Z1.** Z2 (~85 gün) yalnız teşhis; B9'da Z1 ile birlikte. Onaylanıyor mu?
3. **Z2_son.** 2026-09-24 00:00 UTC olarak okundu. Doğru mu?
4. **Stres bağlayıcılığı (risk tercihi; §5.5).** (i) Rapor (varsayılan) ya da (ii) B12: D90-1 ve SQ-1 altında SR ≥ 0,30.
   (ii) seçilirse aynı koşullar 𝓛*'a da girer (§4). Seçim kilitle hash'lenir; sonradan değişmez.
5. **Kapısız A (§9) — KAPANDI. Kullanıcı kararı (27 Eylül, ASAMA4B_KARAR §1 madde 1):** (a) kapı → A/B kalır.
6. **REV1 korelasyonu.** REV1'in D dönemi günlük getirisi v8 değerlendiricisine verilebilir mi? Z1 için REV1 serisi ancak REV1
   sürecinin kendisi üretirse kullanılabilir; v8 REV1 motoruna dokunmaz. E3 Z2 verisi yasak kalır.
7. **Değerlendirici.** Tasarıma katılmamış yeni oturum mu? Codex'in içerik görmeden hash yeniden üretimi istenir mi?
8. **Sembol filtreleri.** `exchangeInfo` okumasına onay; listeden çıkmış semboller için §2.3 varsayılanı.
9. **Kelly ızgarası.** {0,5; 1; 1,5; 2; 2,5; 3; 4} yeterli mi?
10. **Birincil NAV.** 0,1M dondurulur (MIMARI §9 soru 3 ile aynı soru). Değişirse kapı da aynı değerle koşulur.
11. **Şifreleme.** Kullanıcı bir age anahtar çifti üretip açık anahtarı DONDURMA'ya verir. Kabul mü?
12. **Kısa ömürlü 20 coin.** Karar gereği eklenmedi. Konu yeniden açılırsa ayrı ön-kayıt gerekir.

---

## Ek A. MIMARI_v1 ile çelişki ve notlar (v1 okuması; nihai MIMARI.md bunları işledi)
1. **Isınma:** §10 madde 8.
2. **Sapmış satır:** MIMARI_v1 §2.3'teki S4 satırı nihai MIMARI.md'de §4.5'e taşındı.
3. **Banka aday listesi:** MIMARI §2.3 bunu banka taslağına bırakır. Burada: uygun evren (200) + BTC/ETH.
4. **Betimsel satırlar:** MIMARI §1a ve §3.5'teki CTA ve DD satırları bankada koşulmaz (§10 madde 7).
5. **Birincil NAV:** MIMARI §6 0,1M önerir; burada dondurulur.
6. **D segmenti farkı:** sürekli banka koşusundaki D segmenti 202 adaylı evrende çalışır. D içi doğrulama koşusuyla (122 aday) aynı
   sonucu vermez. Yalnız rapordur.
7. **HAR katsayıları:** bankada HAR seçildiyse D'nin tamamında kestirilmiş dondurulmuş katsayılar kullanılır. Bu, K1-12'nin "tam-D
   katsayısı yalnız banka ve canlı için" önerisiyle uyumludur.

## Ek B. Bu belgenin sabitleri ve görülmüş bilgi (üç kademe, K2-12)
Kademeler: **Hayır**; **Zayıf evet** (D özetlerini görmüş kaynaktan geliyor, P&L değil); **Evet** (D istatistiğine doğrudan
dayanıyor). Hiçbiri D P&L'ine bakılarak seçilmedi (D P&L'i yok).

| Sabit | Değer | Kaynak | Görülmüş |
|---|---|---|---|
| B2 | Tür (B/R) ve d* ∈ {0,50; 0,75; 0,90; 0,95}: §3.3 kuralı, Adım 3'te | bu belge, ASAMA4B_KARAR §1 | Hayır |
| σ_SR | σ_SR_bağ = kırp(σ̂_REV1; 0,20; 0,50), kayıt yoksa 0,30 (varsayım); tablo {0,20; 0,30; 0,50} | bu belge, ASAMA4B_KARAR §1 | Zayıf evet (REV1 sonuçları ekipçe kabaca biliniyor; D değil) |
| η gecikmesi | 10 gün, Bartlett; η ≥ 1 | bu belge | Hayır |
| B2 güç koşulu | P(B2 \| SR = 1,0; d = 0,50) ≥ 0,25 | bu belge | Hayır |
| N | 159 + N_v8; sayım kuralı; HAR +2 | KARARLAR, bu belge, Codex S-b | Hayır |
| B3 | ×2 ≥ 0,30; ×3 > 0 | mühür, carry, risk | Zayıf evet |
| B4 | 0,30 | kanıt jürisi | Zayıf evet |
| B5 yöntemi | e_B5 kalibrasyon kuralı; üst sınır %60 | bu belge (§3.7) | Hayır |
| B6 yöntemi | k_B6 ∈ {2, 3} kalibrasyon kuralı | bu belge | Hayır |
| B7 | q95 (3. revizyonla sabit; ⌈0,95·n⌉'inci sıralı değer); 120 saatlik blok; getiri uzayı; yaşam döngüsü kuralı Y1–Y3; 500 yol | bu belge | Hayır |
| B8 | > 0 | kanıt jürisi | Zayıf evet |
| B9 | > 0; görülmemiş zaman | cta, bu belge | Zayıf evet |
| B10 yöntemi | e_B10 kalibrasyon kuralı; üst sınır 0,40; ilk 10 alt | cta, bu belge | Zayıf evet |
| B11 | %15 vol'de MDD ≤ %30 | cta, kullanıcı hedefi | Hayır |
| SR_ref | 1,0 | bu belge (B2 çıtasının üstü) | Hayır |
| Kalibrasyon hedefi | P(KABUL \| SR = 0) ≤ %5; tek ayar 0,30→0,40 | bu belge | Hayır |
| Üreteç ρ_f | 0,3 ve 0,6 | bu belge | Zayıf evet (0,6 ≈ D'deki 0,64) |
| Üreteç ℓ_e | 30 ve 60 gün | tasarım yön değişimi tahminleri | Zayıf evet |
| Üreteç δ | 0,05 ve 0,10 Sharpe | cta devir/maliyet tahmini | Zayıf evet |
| Üreteç ν, s | 4; 0,75 ve 1,25 | genel kalın kuyruk ve çarpıklık | Hayır |
| Üreteç φ (genlik) | 0,5 ve 1,5; a = φ/(sd_s·√ℓ_e) | bu belge (§3.7) | Hayır |
| Üreteç g, funding | ±0,05 Sharpe | bu belge | Hayır |
| tohum_kal | sha256("v8_asama4b_kalibrasyon") | bu belge | Hayır |
| Düzey 2 σ_M, σ_I, β | 0,030; 0,035 (c1/c2 0,010); U[0,6; 1,4] | motor σ tabanları | Hayır |
| Düzey 2 κ, HL | {0; 0,0262; 0,0523}; {30; 90} gün (κ = 0'da HL yok) | kâhin Sharpe {0; 0,5; 1,0} | Hayır |
| Düzey 2 yol sayıları | 2-a: κ = 0, 100 yol × 13 koşu, A ve B, null yok; 2-b: 5 ayar × 10 yol × 50 null, yalnız A | hesap kapasitesi (3. revizyon) | Hayır |
| Düzey 2 hacim | log-tekdüze 10M–400M; AR(1) yarı ömür 60 gün | 20M tabanı ve 13 yuva | Hayır |
| D90 | −%90; yılda 1/2/4 olay; yalnız long | KARARLAR, mühür sayıları | Hayır |
| SQ | +%300; yılda 1/2/4 olay; en büyük alt short | MIMARI S4 büyüklüğü | Hayır |
| DM | 3 alt long aynı anda −%90; yılda 1 | bu belge | Hayır |
| 𝓛* | MDD ≤ %30 ve bootstrap q95 ≤ %30; varsayılan en yüksek CAGR | kullanıcı hedefi, bu belge | Hayır |
| Bootstrap | 20 gün blok, 2.000 çekiş | cta | Zayıf evet |
| Kelly ızgarası | 0,5…4 | bu belge | Hayır |
| NAV / maliyet ızgarası | 0,1/1/5M; 1×/2×/3× | KARARLAR | Hayır |
| Demo NAV koşusu | 5.000 USDT | uygulama jürisi | Hayır |
| R11 eşik bilgisi | 0,50 | kanıt jürisi, ml, risk | Zayıf evet |

**KARAR_DEGISIKLIGI_ONERISI:** Yalnız §9 (kapısız A, kullanıcıya soru). KARARLAR §2'deki teknik kararlar uygulandı. D90'ın rapora
inmesi KARARLAR §1.2'nin "raporlanır" ifadesine uyar; bir karar değişikliği değildir. DSR eşiği 2. turda kullanıcı kararıyla
(ASAMA4B_KARAR §1 madde 2) kalibre edilmiş duyarlılık kuralına bağlandı (§3.3); §9 ve §11'deki iki soru kapandı.

---

## Ek C. Kırmızı takım bulgularının işlenişi

| Bulgu | Düzey | Karar | Nerede / gerekçe |
|---|---|---|---|
| K1-01 | CIDDI | ilgisiz | MIMARI §2.5(c)/§2.6 funding aralığı kuralı. Banka MIMARI nihai tanımını kullanır; doldurulan kayıtlar R6'da raporlanır |
| K1-02 | CIDDI | KISMEN | Ana düzeltme MIMARI'nin. Banka tarafı: D90 bindirmesi funding yazmaz; R9/D90 okuması K1-02 kuralını varsayar (§5.4, §10 madde 9) |
| K1-03 | CIDDI | ilgisiz | MIMARI §5.5 canlı emir zamanı; demo ön-kaydının konusu |
| K1-04 | CIDDI | DUZELTILDI | T4 yalnız hedef kitapta (§2.5); gerçekleşen/devreden aşımlar ve hedefe ulaşılamayan gün oranı R5'te; 1M/5M "kapasite" etiketli (R1) |
| K1-05 | CIDDI | ilgisiz | MIMARI §3.7/§6 Q_max ve maske çıkış maliyeti |
| K1-06 | CIDDI | DUZELTILDI | Tanım MIMARI §6'ya atıf; v1'deki "(ücret dahil)" kaldırıldı; bankada her çarpan tam koşu (§3.1, B3, §10 madde 2) |
| K1-07 | DUZELTILEBILIR | ilgisiz | MIMARI §6 m_stres |
| K1-08 | DUZELTILEBILIR | DUZELTILDI | R1'e gecikme maliyeti ve karekök ortalama bps satırı |
| K1-09 | CIDDI | KISMEN | Tavan çözücüsü MIMARI/CARRY'nin. Banka: her Kelly L'si için carry bacağının gerçekleşen betası R8'de ve Kelly tablosunda |
| K1-10 | DUZELTILEBILIR | ilgisiz | MIMARI §4.4 carry ölçeklemesi |
| K1-11 | DUZELTILEBILIR | KISMEN | V ≤ τ ve M̃ ≤ M_max T4 değişmezi; bağlama sıklığı R5. Serbestlik sayımı MIMARI'nin |
| K1-12 | DUZELTILEBILIR | ilgisiz | MIMARI §1b. Bankada tam-D katsayısı kullanımı öneriyle uyumlu (Ek A.7) |
| K1-13 | CIDDI | DUZELTILDI | ÖN-KAYIT KİLİDİ (§1.2); kuru koşu ve D doğrulama performans çıktıları mühürlü, yalnız hash (§1.3); T3–T5 karşılaştırması hash düzeyinde |
| K1-14 | CIDDI | DUZELTILDI | Null'da hijyen bayrakları blokla taşınır, yeniden tetiklenmez; funding blok içi saatle; T4 değişmezi "tetik = 0" (§3.5, §2.5) |
| K1-15 | DUZELTILEBILIR | DUZELTILDI | Eylül funding kaynağı önceden yazıldı; onayda ayrı satır (§2.3) |
| K1-16 | DUZELTILEBILIR | DUZELTILDI | Gizli anahtarlı HMAC sırası; listeleme tarihi ve mutlak hacim yerine dilim etiketi (§8.1) |
| K1-17 | DUZELTILEBILIR | ilgisiz | MIMARI §5.1 durum ve kaçırılan karar |
| K1-18 | CIDDI | KISMEN | Banka tarafı: demo NAV koşusu R14 (hedge sıfırlanan gün oranı); demoda olmayan sembol kuralı §7.1. Kısmi dolumun adım katına yuvarlanması MIMARI'nin |
| K1-19 | DUZELTILEBILIR | ilgisiz | MIMARI §3.8 felaket stopu |
| K1-20 | DUZELTILEBILIR | KISMEN | Madde 11 (B5 paydası, §3.4), 12 (D90 w_max gerçekleşen, §5.4), 14 (lot filtresi, R13) düzeltildi; diğer maddeler MIMARI/CARRY'nin |
| K2-01 | CIDDI | DUZELTILDI | ÖN-KAYIT KİLİDİ, ana oturum notu 1 sırasıyla (§1.2); bağlayıcı "D sonucu ne çıkarsa çıksın değişmez" cümlesi; mühürlü D çıktıları (§1.3) |
| K2-02 | CIDDI | KISMEN | Kapının gücü CARRY'nin konusu. Banka: §6 ve rapor sınırlarına "B, fiyattan gelmediği gösterildi demek değildir" cümlesi |
| K2-03 | CIDDI | KISMEN | Ana oturum notu 2: karar değiştirilmedi; §9 KARAR_DEGISIKLIGI_ONERISI / kullanıcıya soru; seyreltme sayıları ve §3.7'de A/B P(KABUL) eğrileri |
| K2-04 | CIDDI | DUZELTILDI | σ_SR = 0,30 sabit; REV1 std'si yalnız R16; defter düzeltmesi (144, 5) ve sayım kuralı; N ≈ 322–323, SR₀ ≈ 0,88 (§3.3) |
| K2-05 | CIDDI | KISMEN | B1 → R11; B12 → R12; B5 ve B10 eşikleri, B6'nın k'si sentetik kalibrasyonla (§3.7); P(KABUL \| SR = 0) ≤ %5 hedefi. B6 otomatik ≥3/4 yapılmadı: KARARLAR rejim dilimlerini kabul ölçütüne koyar; k kuralla seçilir |
| K2-06 | CIDDI | DUZELTILDI | Eşik gerekçeleri yalnız istatistik (§3.2); rejim cümleleri yalnız §6 yorumunda, "eşik gerekçesi değildir" notuyla |
| K2-07 | CIDDI | DUZELTILDI | Kör hüküm ve şifreli sonuç (§2.4); T2 koşu öncesi (§2.3); açılış sonrası hükmü değiştiren hata → NOT_EVALUATED, her iki yönde (§2.5) |
| K2-08 | CIDDI | DUZELTILDI | CTA çekirdeği ve DD ablasyonu bankadan çıkarıldı (R8, §10 madde 7); Kelly L'si için örneklem içi uyarı ve bootstrap q95 (§4, §7.1) |
| K2-09 | DUZELTILEBILIR | DUZELTILDI | B9 bağlayıcı yalnız [T0_Z1, 2023-06-24) ∪ Z2; D kısmı R15; güç yazıldı; sayım kuralı yazıldı (§3.6, §3.3) |
| K2-10 | DUZELTILEBILIR | ilgisiz | MIMARI §1b HAR koşulları |
| K2-11 | DUZELTILEBILIR | ilgisiz | CARRY V4/K8/NW ve MIMARI §2.6 |
| K2-12 | DUZELTILEBILIR | KISMEN | Bu belgenin sabit tablosu üç kademeli (Ek B). MIMARI §7 etiketleri MIMARI'nin |
| K2-13 | DUZELTILEBILIR | DUZELTILDI | Sıklık olay/yıl (D90-1/2/4); mühür sayılarından kaba sınırlar; D90-2/4 Kelly tablosunda; zorunlu "B1/DSR düzeltilmedi" cümlesi (§5.4–5.5) |
| K2-14 | DUZELTILEBILIR | DUZELTILDI | Üyelik karıştırılmış hacimden; dilim sınırı geçmişi tanımlı; B7 gücü §3.7 Düzey 2'de; q95 ayar kuralı (§3.5). *(3. revizyonla değişti; Ek C sonu.)* |
| K2-15 | YOK | — | İşlem gerekmedi; coin adı ve dönem ayarı yok |

Not: K1-04, K1-11 (T4), K1-14, K2-14 (rejim-null) ve K2-04 (DSR) satırları round-1 kararlarıdır. Bu satırların içeriği 2. turda
aşağıdaki KC-09, KC-01 ve KC-08 satırlarıyla değişti. Çelişki halinde 2. tur geçerlidir.

### Codex bulgularının işlenişi (2. tur)

| Bulgu | Düzey | Karar | Nerede / gerekçe |
|---|---|---|---|
| KC-01 | OLDURUCU | DUZELTILDI | §3.5 tamamen yeniden yazıldı. Karıştırma getiri uzayında yapılır: ρᴼ/ρᴴ/ρᴸ/ρᶜ gerçek önceki kapanışa göre alınır, sentetik fiyat çapadan zincirlenir, sınırda yapay getiri yoktur ve dilim sonunda sentetik kapanış gerçek kapanışa eşittir (3.5.3). Hacim (USDT) ve funding oranı blokla taşınır; funding nakdi sentetik pozisyonla hesaplanır (3.5.4). Yaşam döngüsü Y1–Y3: varlık saatleri ve coinin kendi yaşı korunur, kenar bloklar sabittir, tam bloklar ortak permütasyonla ve kalanlar ikincil eşlemeyle yerleşir (3.5.2). Maske, hijyen ve evren sentetik yoldan günlük yeniden hesaplanır; taşınan maske ve "tetik = 0" kaldırıldı; MIMARI §5.1 dış bayrak modu kullanılmaz (3.5.5, §10 madde 12). Ekonomik null değişmezleri N1–N6 T4-f oldu (3.5.7); tanılar R17'de. **Codex doğrulama turu (2. verify):** Y1/N3'ün
"gap'in tam saati de aynı kalır" biçimindeki fazla iddiası düzeltildi — korunan sayı ve giriş/çıkıştır, gap'in blokla
taşınması artık N3 ihlali sayılmıyor (§3.5.2, §3.5.7). Kalan zayıf nokta (ikincil eşlemenin kesitsel bağımlılığı hafif
değiştirmesi) R17'nin ortak eşleşme payı raporuyla izlenir; ek bir düzeltme gerektirmiyor. |
| KC-02 | CIDDI | DUZELTILDI | §3.7: bütün üreteç parametreleri donduruldu. Genlik a = φ/(sd_s·√ℓ_e), φ ∈ {0,5; 1,5}; gürültü √(1/2)·t₄ ve ortak faktör; σ_P, maliyet K, funding F ve m kapalı formülle; ölçüt eşleme tablosu; tohum_kal. Düzey 2'de σ_M, σ_I, β, κ ∈ {0; 0,0262; 0,0523} (kâhin SR 0/0,5/1,0), HL, saatlik OHLC, hacim ve funding formülleri, yaşam ve hijyen fikstürleri. B7 dahil birleşik yanlış kabul Düzey 2'de ölçülür (B9 hariç, Düzey 1'den). *(3. revizyonla değişti: üst sınırla; Ek C sonu.)* Sıra: Adım 1 → 2 → 3 (mekanik) → 4 kilit; kalibrasyon çıktısına bağlı kullanıcı sorusu yoktur (§1.2 notu, §3.7 başı) |
| KC-08 | CIDDI | DUZELTILDI | Kullanıcı kararı (ASAMA4B_KARAR §1 madde 2). §3.3 yeniden yazıldı: σ_SR ∈ {0,20; 0,30; 0,50} × DSR {0,50; 0,75; 0,90; 0,95} duyarlılık tablosu (Codex'in {1,50; 1,80; 2,38} değerleriyle aynı). σ_SR_bağ kuralı: REV1 kayıtlarından kırpılmış std, yoksa 0,30 "varsayım". B2 türü kuralı: güç koşulu ≥ 0,25. d* kuralı: birleşik P(KABUL \| SR = 0) ≤ %5 veren en küçük d. Hepsi Adım 3'te, D'ye bakılmadan. η seri bağımlılık düzeltmesi eklendi. Ham N gerekçesi yazıldı. HAR +2. "Olasılıksal kanıt" yerine "performans çıtası" denildi |
| KC-09 | CIDDI | DUZELTILDI | §2.5 T4 nesnelere ayrıldı, MIMARI ile aynı lettering (ana oturum hizaladı). T4-a birim trend w^u: V ≤ τ, M̃ ≤ M_max (MIMARI §3.3). T4-b carry birim kitabı w^C, ω_C/L öncesi: V ≤ τ (MIMARI §4.4). T4-c carry bloğu, ω_C·L ve tavan uygulanmış: V ≤ ω_C·L·τ (MIMARI §4.4–4.5). T4-d kaldıraçlı net hedef: tavan uyumu + toplam risk kuralı V(w*) ≤ L·(1+ω_C·𝟙_B)·τ; L = 2 ve V = %24 örneği toplam risk kuralını ihlal etmediği sürece geçerli (MIMARI §3.4–3.6, §4.5). T4-e muhasebe, T4-f null. Gerçekleşen defter R5'tir (MIMARI §5.7). §10 madde 10 |
| KC-10 | CIDDI | DUZELTILDI | §4: bağlayıcı uygun kaldıraç kümesi 𝓛* (gerçekleşen MDD ≤ %30 ve bootstrap q95 ≤ %30). Dışındaki L'ler "KARŞILAMIYOR" diye işaretlenir, önerilemez ve demoya seçilemez. Varsayılan öneri 𝓛* içinde en yüksek CAGR. 𝓛* boşsa "uygun kaldıraç yok" cümlesi zorunludur. Yeniden örneklemenin marjin, ADL ve gerçekleşmemiş kuyrukları üretmediği uyarısı eklendi; §7.1 ve §8.2 güncellendi |
| KC-11 | CIDDI | DUZELTILDI | §5.2 ve §5.4: D90 "yalnız long çöküş bindirmesi (kanal 2)" diye sınırlandı; "üst sınır" iddiası geri çekildi. SQ-k (en büyük alt short +%300, S4 büyüklüğü) ve DM-1 (üç alt long aynı anda −%90) eklendi; R12 ve Kelly sütunlarına girdi. §5.5: n < 30 gerekçesi geri çekildi. Bağlayıcılık kullanıcının risk tercihidir: Adım 1'de (i) rapor ya da (ii) B12 (D90-1 ve SQ-1 altında SR ≥ 0,30) seçilir ve kilitle hash'lenir. Raporlama kararı sessizce değiştirilmez (§11 soru 4) |
| KC-03 | CIDDI | ilgisiz | Öteki belgede işlendi (CARRY/MIMARI) |
| KC-04 | CIDDI | ilgisiz | Öteki belgede işlendi (MIMARI). Nötrlük değişmezi tanımlanırsa T4-c'ye girer (§2.5) |
| KC-05 | CIDDI | ilgisiz | Öteki belgede işlendi (CARRY) |
| KC-06 | CIDDI | ilgisiz | Öteki belgede işlendi (CARRY) |
| KC-07 | CIDDI | ilgisiz | Öteki belgede işlendi (CARRY/MIMARI). §9'a ρ = 0,30 notu ve §3.7 seyreltme ızgarasına ρ = 0,30 eklendi (rapor) |
| KC-12 | CIDDI | ilgisiz | Öteki belgede işlendi (MIMARI) |
| KC-13 | CIDDI | ilgisiz | Öteki belgede işlendi (MIMARI) |
| KC-14 | DUZELTILEBILIR | ilgisiz | Öteki belgede işlendi (MIMARI) |

### 3. revizyon (29 Eylül; kullanıcı kararı, hesap kapasitesi)

| Bulgu | Düzey | Karar | Nerede / gerekçe |
|---|---|---|---|
| KC-02 | CIDDI | DEGISTI | "B7 dahil birleşik yanlış kabul Düzey 2'de ölçülür" artık üst sınırla karşılanır: B7 veto olduğundan P(KABUL_birleşik) ≤ P(KABUL_B7siz); κ = 0'da 100 yolda A ve B motorla ölçülür (Düzey 2-a). Kural (> %5 → kilit bekler) aynı. §0.2, §3.7 |
| K2-14 | DUZELTILEBILIR | DEGISTI | B7 gücü Düzey 2-b'de betimsel ve kaba (10 yol); q95 ayar kuralı yerine sabit q95 (§3.4, §3.5.6) |
| T10-1 | CIDDI | DUZELTILDI | KABUL_B7siz artık Düzey 1 sonunda bağlayıcı kalan ölçütlerin kesişimi, Düzey 1'in son eşikleriyle (0,40 ayarı dahil); rapora inen ölçüt girmez; KABUL_tam ⊆ KABUL_B7siz ∩ B7 ∩ B9 (§3.7 Düzey 2-a) |
| T10-2 | ORTA | DUZELTILDI | p̂ "üst sınırın nokta tahmini", Wilson aralığı ayrı; "> %5 → bekle" tarama kuralı, güven kanıtı değil; sonuç yalnız bu üreteç için (§3.7, §8.2 madde 4 ve 12) |
| T10-3 | ORTA | DUZELTILDI | hash tanımı (SHA-256, kanonik JSON, ilk 8 bayt), RNG PCG64, coin/dilim/null numaraları, sabit çekiş sırası; duman denetimi farklı işçi sayısı, ters sıra ve kesinti/devam altında (§3.7 Tohum, Kesinti ve devam, Tekrarlanabilirlik) |
| T10-4 | ORTA | DUZELTILDI | İş listesi ve dört beklenen kimlik hash'lenir; atlama yalnız bütünlük doğrulanırsa; bozuk dosya karantinaya; B10 birimi birincil sonucun sha256'sına ve coin numarasına bağlı (§3.7) |
| T10-5 | DUSUK | DUZELTILDI | §10 madde 13, Ek C K2-14 ve KC-02 satırlarına 3. revizyon atfı |
| T11 | doğrulama | KAPANDI | Codex T11: T10-1…5 KAPANDI; HAR banka modu maddesi ön-kayıtla tutarlı. Tek DUSUK not (eşitlik yerine kapsama, B12) işlendi. Hüküm: kalibrasyon koduna geçmeye uygun |
| T12 | kod incelemesi | DUZELTILDI | 3 CIDDI (B5 işaret değiştirme saati, süreç hash tohumuna bağlı toplam, muhasebe kapısı), 7 ORTA, 1 DUSUK; yorum (c) ve (e) itirazları kabul edildi. Kod düzeltmeleri P14a–d; uygulama netleştirmeleri §3.7 sonu |
