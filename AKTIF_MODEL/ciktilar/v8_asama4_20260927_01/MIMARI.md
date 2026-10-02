# v8 nihai mimari — MIMARI (revizyon taslağı)

Durum: **KİLİT ADAYI (1 Ekim 2026, 4.02).** Bütün açık sorular `ACIK_SORU_YANITLARI.md`'de yanıtlı; Adım 3 (kalibrasyon) kapandı. Koşulmadı: D'de P&L üretilmedi. Kilitten (`KILIT.json`) sonra eşik, ölçüt ve parametre değişmez. Önceki durum: TASLAK (27 Eylül); Slice 1–3 ve kilit adımı 2 netleştirmeleri işlendi.

Tarih: 2026-09-27. Yazan: Aşama 4 mimari revizörü (Opus). Girdi taslak: `calisma/MIMARI_v1.md`. Revizyon
dayanağı: `calisma/KIRMIZI_1.md`, `calisma/KIRMIZI_2.md`, `calisma/CARRY_KAPISI_v1.md`,
`calisma/BANKA_ONKAYIT_v1.md` ve `girdi/` altındaki 17 dosya.

**2. tur revizyonu (Aşama 4b, 2026-09-27).** Dayanak: `CODEX_KIRMIZI_TAKIMI.md` (KC-01…KC-14) ve
`ASAMA4B_KARAR.md`. Değişen bölümler: §0, §2.4, §2.5(d), §3.1, §3.2, §3.3, §3.5, §4.3–§4.7, §5.1, §5.2, §5.4,
§5.6, §5.8, §7, §9, §11, §12, §13. Round-1 metni `_arsiv/V8_ASAMA4_SENTEZ_20260927_01/round1_nihai/` altındadır.

**Kullanıcı kararı K8 (2026-09-28, motor Slice 2 Codex incelemesi).** §3.1 ile §3.5 T4-d arasındaki boşluk
kapatıldı: işlem dışı (sabit) isimlerin yol açtığı tavan ihlali teknik hata değildir, kayıtlı olaydır. Değişen
yerler: §3.1 "işlem dışı coin" maddesi, §3.5 değişmez tablosu (T4-d satırı ve altındaki not). Önceki metin
`_arsiv/V8_MIMARI_K8_20260928_01/` altındadır.

**Motor yazımı netleştirmeleri (2026-09-29, Slice 3 Codex 5.–6. tur; B4, B16, X9).** Kodla belge arasındaki üç
ayrılık belgeye yazıldı; hiçbiri D verisine bakılarak seçilmedi: (1) §4.1 carry adayı V60 ≥ 20M ister, V60 < 20M
olan tutulan isim evrenden çıkar; (2) §4.5 sıra özeti ve §4.7: net kitaba uygulanan yalnız-azaltma kuralları sanal
bacakları değiştirmez (fark icra artığı), V60 < 20M'de trend bileşeni çözücüden önce kırpılır, T4-d nihai kitapta
denetlenir; (3) §4.7 sanal carry miktarı güvenlik ölçeklemelerini içeren κ_etkin ile tanımlanır. Önceki metin
`_arsiv/V8_MIMARI_SLICE3_20260929_01/` altındadır.

Bu belge tasarım tarifidir. Geri test, veri hesabı ve performans ölçümü yapılmadı. Ekonomik kabul
**NOT_EVALUATED**. Banka içeriği yoktur. Coin adı yalnız BTC/ETH için geçer. Sayılar belgelerdeki sabitlerden
yapılmış kalem-kâğıt aritmetiğidir; ölçüm değildir.

Bağlayıcı çerçeve (ONKAYIT §2): bankaya tek mimari gider ve bankadan önce dondurulur. Carry D içi kapıyı
geçerse **B** (trend + küçük, sabit bütçeli carry uydusu), geçemezse **A** (yalnız trend). A ile B bankada
yarışmaz. B seçilirse A'nın banka sonucu yalnız ayrıştırmadır. Bu belge ikisini de formül düzeyinde tarif eder.
Hangisinin gideceğini kapı belirler (`CARRY_KAPISI`). Kullanıcı 27 Eylül'de "kapısız A"yı seçmedi; kapı → A/B
kesinleşti (`ASAMA4B_KARAR.md` §1; §11).

---

## 0. Özet ve karar tablosu

v8, Binance USDⓈ-M perp'te günlük karar veren, çok coinli, simetrik bir zaman serisi trend kitabıdır. B seçilirse
aynı motora haftalık, beta-nötr bir funding taşıma uydusu eklenir. Bütün hesaplar tek bir saf fonksiyon
zincirinden geçer: `hedef_agirlik → bant → lot_yuvarlama → emir_zinciri`. Geri test ve canlı aynı fonksiyonları
çağırır. Bütün eşik ve ölçütler, D'de P&L üreten ilk koşudan önce kilitlenir (§10).

| Bileşen | Kaynak tasarım | Neden |
|---|---|---|
| Trend sinyali (14/42/84, tanh, simetrik) | `codex` | En az serbestlik; 7 günlük pencere ve funding çarpanı yok |
| Sinyal normalizasyonu σ̂ = max(EWMA20, EWMA90), taban %20 | `risk` + `codex` tabanı | KARARLAR §2 "EWMA standart"; 365 günlük pencere ısınmayı yemez |
| Evren: sıra tabanlı, BTC/ETH sabit, N=15, histerezis 15/20, taban 20M | `cta` | Nominal eşikten sağlam; öncelik kuralı var |
| PIT donma/delist ölçütleri; funding ölçütü mutlak 16 saat | `cta` + K1-01 | Aralık değişiminde sahte donma olmaz |
| Birim risk: tam sinyal referans kitabı ex-ante %15 (çarpan ve tavanlar izin verdiğinde), yukarı çarpan ≤1,5 | `ml` k tanımı + `cta` M çarpanı | İki yönlü hedef; zayıf sinyal büyütülmez (§1a) |
| Σ̂ = 0,5·örnek + 0,5·(ρ=0,7); örnek matris PSD'ye projekte | `risk` / `ml` + KC-13 | Stres harmanı; vol her zaman tanımlı |
| Şok tavanları kaldıraç sonrası NAV'da, hedge kredisiz; hedef kitapta değişmez | `risk` + `codex` + K1-04 | KARARLAR §2 |
| Asimetrik isim tavanları (alt long %6, alt short %4) | `risk` | Yukarı sıçrama kuyruğu |
| İşlem bandı, sınıra işlem | `codex` | Devri düşürür |
| Katılım sınırı: 30g, 7g ve önceki saat hacminin en küçüğü; kısmi dolum adım katına | `codex` + `mikroyapi` + K1-05, K1-18 | Ölen coinde iyimser dolum olmaz |
| Maliyet: dilim + karekök etki, stres ×3; **çarpan yalnız dilim + etkiye, ücret sabit** | `cta` + KARARLAR §2 + K1-06 | Üç belgede tek tanım (§6.2) |
| Funding/dolum olay sırası; mark vekili = 1h kapanış; delistte tahakkuk durur | KARARLAR §2 + K1-02 | Hayali funding yazılmaz |
| Carry uydusu (FTN), sabit bütçe ω_C = 0,20; tavan çözücüsünde tek blok; BTC hedge kırpma/bant/maske sonrası günlük yeniden kurulur | `carry` + K1-09 + KC-04 | Tek bağımsız kol; nötrlük tavanlarla bozulmaz |
| σ̂ tahmincisi: EWMA; HAR yalnız QLIKE prosedürüyle, kilitten önce | `ml` çerçevesi | KARARLAR §2; §1b |
| Felaket stopu (4 ATR, reduce-only) | `prop` | Yalnız canlı, operasyonel |

Dışarıda kalanlar §8'de. Açık sorular §9'da. Kilit sırası §10'da.

---

## 1. Açık noktaların çözümü

### 1a. Trend çekirdeği: Codex iskeleti dondurulur, CTA çekirdeği yalnız betimsel

**Karar.** Dondurulan sinyal `codex` iskeletidir: h ∈ {14, 42, 84}, tanh, eşit ağırlık, simetrik. CTA çekirdeği
(L ∈ {7,14,28,56,84}, clip ±1, funding çarpanı m, σ = 0,7·EWMA20 + 0,3·σ_1y) **yalnız betimsel** ilan edilir.

**Gerekçe.**
1. İki çekirdek aynı hipotezi taşır. Jüri tahmini getiri korelasyonu 0,85–0,95. Seçim Sharpe'ı belirlemez;
   serbestlik derecesini ve uygulanabilirliği belirler.
2. Codex iskeletinde getiriye dokunan sabit 3 ufuktur. CTA'da 5 pencere, 3 funding sabiti (B, 2B, 0,5) ve 2 σ
   harmanı katsayısı vardır.
3. CTA'nın 7 günlük penceresi kendi gerekçesiyle (VR(5) < 1) çelişir. Bu gerekçe D istatistiğine dayanır;
   **görülmüş bilgi** olarak işaretlenir (K2-12). Karar yalnız bu gerekçeye dayanmaz: 1, 2, 4 ve 5 D'den bağımsızdır.
4. CTA'nın σ_1y terimi 180 gün veri ister. D öncesi veri olmadığından D'nin ilk ~6 ayı kaybolur.
5. Funding çarpanı REV1'de kapanan funding ailesini yeni kanıtsız yeniden açar. Funding yalnız P&L'e girer.
6. Codex jürisinin asıl istekleri (bant, kısmi dolum, delist muhasebesi) Codex ilkeleriyle karşılanır.

**CTA'dan alınanlar:** evren kuralı, donma/delist ölçütleri, dilimli maliyet tablosu. **Codex'ten değiştirilen:**
60 günlük eşit ağırlıklı σ yerine EWMA σ̂ (KARARLAR §2). Bu değişiklik D'ye bakılarak yapılmadı.

**Betimsel statü (K2-08 ile değişti).** CTA çekirdeği bankada seçim için kullanılmaz. MIMARI onu bankaya
betimsel satır olarak **önermez**: bankada koşulan alternatif şartname, ek banka olmadığı için gelecekteki
tasarımları banka verisine bağlar. Banka ön-kaydı yine de koşacaksa çıktısı ileri demo kararına kadar yalnız
hash olarak tutulur ve DSR deneme sayacına +1 girer.

**Codex ilkeleri korunur:**
- *Zayıf sinyal büyütülmez:* portföy çarpanı sinyal gücüne bağlı değildir (§3.3). g > 1 yoktur.
- *Bant kenarına işlem:* §3.6.
- *Kısmi dolumun açık taşınması:* §5.4.
- *PIT delist:* sonradan türetilmiş `islem_disi_supheli` bayrağı hiçbir kuralda kullanılmaz (§2.5).

### 1b. Risk tahmincisi: EWMA standart; HAR için QLIKE seçim prosedürü

**Standart.** σ̂_EWMA,i = max(σ_EW(20), σ_EW(90)), σ_EW(H) = √(365·EWMA_H(r²)). r günlük log getiri, ortalama sıfır
varsayılır, H yarı ömür (gün). Yukarı hızlı, aşağı yavaş tepki verir.

**HAR adayı (tek aday).** Havuzlu, çapalı log-HAR (`ml`):
- l1 = ln RV_d, l7 = ln(7 günlük ort. RV), l30 = ln(30 günlük ort. RV). RV_d günün 24 saatlik log getiri kareleri
  toplamıdır.
- m = ln RV_d'nin geçmiş ortalaması; pencere en fazla 365, en az 90 gün.
- ŷ = c + b1·l1 + b7·l7 + b30·l30 + (1−b1−b7−b30)·m (7 günlük log varyans).
- σ̂_HAR = √(52,14·exp(ŷ + ½·ŝ²)). ŝ², yürüyen tahmin artıklarının **son 52 haftalık** varyansıdır; yalnız hedefi
  tamamlanmış haftalar girer (PIT; K1-12). 52 haftadan az artık varsa mevcut artıkların hepsi kullanılır, en az 8.
- `ml`'deki 24 saatlik RV tabanı ve düz HAR alternatifi alınmaz. Aday tektir.

**Seçim prosedürü (P&L'siz, ön-kayıtlı; kilit adımı 2, §10).**
1. **Değerlendirme kümesi:** D içinde 2024-01-01'den itibaren her Pazartesi 00:00 UTC; o anki PIT trend evrenindeki
   coinler. Hedefin son günü 2026-07-01'den önce biter.
2. **Hedef (K1-12 ile değişti):** sonraki 7 günün **günlük** log getiri kareleri toplamı × 365/7. İki tahminci aynı
   hedefe karşı sınanır. Gerekçe: günlük karar kitabının riski günlük getirilerle ölçülür. Saatlik RV hedefi,
   saatlik ters dönüş varken EWMA'yı yapısal olarak eksik tahminci gösterir (görülmüş bilgi: VR(5) < 1).
3. **Yürüyen tahmin:** HAR katsayıları her ayın ilk günü, yalnız o güne kadar hedefi tamamlanmış gözlemlerle
   havuzlu OLS ile yeniden tahmin edilir. İlk tahmin 2024-01-01'dedir. Gelecek veri kullanılmaz.
4. **Kayıp:** QLIKE(Y, F) = Y/F − ln(Y/F) − 1; Y hedef, F = σ̂².
5. **Bağlayıcı karar kuralı.** HAR ancak ikisi birden sağlanırsa girer; yoksa EWMA:
   - (i) havuzlu ortalama QLIKE_HAR ≤ 0,95 × QLIKE_EWMA;
   - (iv) hafta düzeyinde, 4 haftalık bloklarla dairesel blok bootstrap (2.000 çekiş, tohum 20260927): ortalama
     (QLIKE_HAR − QLIKE_EWMA) için tek taraflı %95 üst sınır < 0. Bloklar kesitsel bütün olarak çekilir.
6. **Betimsel (bağlayıcı değil; K2-10):** (ii) stres haftalarında (BTC haftalık getirisinin en kötü %10'u, ~13
   hafta) ortalama QLIKE farkı; (iii) Y/F oranının q95 ve q99'u. n < 30 olduğu için kural olamazlar; raporlanırlar.
7. Değerlendirme kümesi 30 haftadan kısaysa prosedür koşulmaz; EWMA kalır.
8. **Katsayı kullanımı (K1-12):**
   - D içindeki bütün koşularda (carry kapısı, D doğrulaması) yürüyen aylık katsayılar kullanılır. 2024-01-01
     öncesinde HAR katsayısı yoktur; bu dönemde σ̂ = σ̂_EWMA.
   - Banka ve canlı için katsayılar D'nin tamamında aynı OLS ile bir kez tahmin edilip dondurulur.
9. Sonuç ön-kayıt kilidinde (kilit adımı 4) hash'lenir. Deneme defterine "P&L'siz tahminci seçimi" satırı girer,
   varyant sayısı 2 (EWMA, HAR). Bankada HAR/EWMA seçimi yapılmaz.

**Kapsam.** σ̂ tahmincisi yalnız boyutlamaya (Σ̂) girer. Sinyal normalizasyonu her durumda σ̂_EWMA'dır. HAR kararı
getiri sinyalini değiştirmez.

**Görülmüş bilgi.** `ml` tasarımcısı D'de HAR'ın QLIKE'ını EWMA-RV'den %14 düşük buldu. Hedef ve EWMA tanımı
farklıydı; yine de sonuç kısmen bilinmektedir ve görülmüş bilgi olarak işaretlenir.

### 1c. ML çıkış kuralının yerine gerçekleşebilir ileri çıkış

`ml`'nin "donmuş günde önceki geçerli kapanıştan kapat" kuralı alınmaz (Codex jürisi: `OLDURUCU`). Yerine:
1. Karar anı t'de, yalnız t'ye kadar kapanmış barlarla bir donma ölçütü (§2.5) tetiklenirse coinin hedef ağırlığı 0
   olur. Coin maskelenir.
2. Çıkış emri, sonraki saatlerde **işlem gören** (hacmi > 0) ilk bardan itibaren verilir. Bar yoksa ya da hacmi
   sıfırsa o saatte dolum olmaz.
3. Dolum fiyatı: o barın açılışı × (1 ± c_i), c_i maske çıkışı maliyetidir (§6.1). Katılım sınırı (§3.7) geçerlidir.
4. Dolmayan kalan açık pozisyon olarak taşınır ve son geçerli kapanışla değerlenir. Funding §2.6'ya göre işler:
   gerçek kayıt varsa uygulanır; eksik kayıt dolgusu **yalnız coinin bar akışı sürerken** yazılır. Bar akışı durunca
   funding tahakkuku durur (K1-02).
5. Coin 30 ardışık gün işlem görmezse (hacmi > 0 bar yoksa) pozisyon uzlaşmaya gider: long, son kapanış × (1 − h_L);
   short, son kapanış × (1 + h_S). Taban h_L = %10, h_S = %5. Bu 30 gün boyunca funding yazılmaz.
6. Senaryolar ayrıca raporlanır: h_L = %50 ve h_L = %90 (KARARLAR §1.2). Her senaryo ayrı tam koşudur (§6.2).

Hiçbir adım karar sonrasında geçmiş fiyata işlem yazmaz. Maske ≠ tasfiye.

### 1d. Carry bütçesi: ω_C = 0,20 (sabit)

**Tanım.** Carry birim kitabı kendi ex-ante vol'ü τ = %15 olacak biçimde ölçeklenir (§4.4). Ardından ω_C = 0,20
ile çarpılıp trend kitabına **eklenir**. İsim tavanları ölçeklemeden sonra kırptığı için L = 1'de carry ex-ante
vol'ü **≤ %3**'tür. Trend kitabı değişmez.

**Gerekçe (K2-03 ile yeniden yazıldı).**
1. *Ekleme biçimi ayrıştırmayı temiz tutar.* B'nin trend bacağı A ile aynıdır. B seçilirse A'nın banka sonucu
   doğrudan ayrıştırma olur.
2. *Doğru bedel metriği portföy Sharpe'ıdır.* B bankada bütün olarak yargılanır. Carry'nin yıllık sürüklemesi
   (v1'deki "−%0,6") yanlış metrikti. ρ = 0, σ_T = %9 (trend gerçekleşen vol önseli; `cta`/`ml` tahmini %7–11'in
   ortası, ölçülmedi), σ_C = %3 için:

       SR_B = (SR_T·σ_T + SR_C·σ_C) / √(σ_T² + σ_C²)
       Başa baş: SR_C* = SR_T·(√(1 + r²) − 1)/r,  r = σ_C/σ_T = 1/3  →  SR_C* ≈ 0,16·SR_T

   | SR_T | SR_C = −0,3 | SR_C = 0 | SR_C = +0,3 |
   |---|---|---|---|
   | 0,50 | 0,38 (−%24) | 0,47 (−%5) | 0,57 (+%14) |
   | 0,85 | 0,71 (−%16) | 0,81 (−%5) | 0,90 (+%6) |

   Sıfır Sharpe'lı, korelasyonsuz bir carry bile portföy Sharpe'ını ~%5 seyreltir. B, carry'nin bankada SR_C*'ı
   aşacağına dair bir bahistir. Bu bedel §11'de kullanıcıya sayıyla sunulur.

   **Bu sayı ρ = 0 içindir ve CARRY kapısının K1 eşiğiyle KARIŞTIRILMAMALIDIR.** SR_C* ≈ 0,16·SR_T burada yalnız
   ω_C'nin portföy düzeyinde bütçe gerekçesi için kullanılır. Kapının kendi geçme eşiği (K1*, CARRY §6.4) ölçülen
   ρ'ya bağlıdır ve K10'un izin verdiği ρ = 0,30 üst sınırında ≈ 0,37'ye çıkar (Codex KC-07). Kapı, ω_C = 0,20'yi
   değiştirmez; yalnız B'nin bankaya gidip gitmeyeceğine karar verir.
3. *Uydu kalır.* %3 carry, σ_T = %9 iken toplam varyansın ~%10'udur.
4. *Kuyruk sınırlıdır.* §4.3 isim tavanıyla tek carry short'unun +%300 şoku NAV'ın ≤ %3'üdür.
5. *Önsel aralığın içindedir.* ρ = 0'da optimum risk oranı σ_C/σ_T = SR_C/SR_T'dir. Codex carry bandının merkezi
   (SR_C ≈ 0,1) ve SR_T = 0,45 ile optimum ω ≈ 0,13; kâr jürisi merkezi (SR_C ≈ 0,3) ile ω ≈ 0,40. 0,20 bu iki
   önselin arasındadır ve %30–35 otomatik tahsis yapılmaz. Önseller D özetlerini görmüş jürilerden gelir: **zayıf
   görülmüş bilgi** (K2-12).
6. Değer D P&L'ine bakılarak seçilmedi; D'de carry P&L'i hesaplanmadı. Kapı sonucu ω'yı değiştirmez.

**Duyarlılık (yalnız bilgi).** ω_C = 0,10 (σ_C = %1,5), SR_T = 0,85'te: SR_C = −0,3 → 0,79 (−%7); 0 → 0,84 (−%1);
+0,3 → 0,89 (+%4). Küçük ω aşağı yönü yukarı yönden hızlı küçültür. ω değişikliği bir arayüz değişikliği olurdu;
bu revizyon ω'yı değiştirmez, kullanıcı §11'de isterse kilitten önce değiştirebilir.

---

## 2. Veri ve evren sözleşmesi

### 2.1 Veri
- Kaynak: data.binance.vision mainnet arşivi. `futures/um` aylık **1h klines** ve **fundingRate**. İlk indirmenin
  hash'i bağlayıcıdır.
- Kullanılmayan: metrics, mark/premium kline, bookTicker, 1m veri, demo hacmi.
- Hacim: 1h kline `quote_volume`. Canlıda aynı büyüklük mainnet kamu verisinden okunur.
- Mark vekili: uzlaşma damgası T için [T−1h, T) barının kapanışı. Bu vekil banka ön-kaydına yazılır.
- Funding damgası en yakın tam saate yuvarlanır (milisaniye sapmaları için; K1-20.8).

### 2.2 Takvim ve günlük kapanış
- Günlük karar: her gün 00:00 UTC, [t−1g, t) günlük barıyla. Günlük bar 1h barlardan kurulur.
- **Günlük kapanış** P_i,t = [t−1h, t) barının kapanışı. Bu bar yoksa coin o gün "işlem dışı"dır (§3.1; K1-20.1).
- Aylık evren: her ayın 1'i 00:00 UTC; günlük karardan önce çalışır.
- Carry haftalık karar: Pazartesi 00:00 UTC; evren güncellemesinden sonra, trend kararından önce.
- İlk dolum: kararın 1 saat sonrası, 01:00 barının açılışı. Canlı zamanlama §5.5.

### 2.3 PIT trend evreni
- Adaylar: o ana kadar kline'ı olan USDT perp'ler. Stablecoin, endeks ve alt çizgili vadeli hariç. Geliştirmede aday
  listesi `GELISTIRME_EVRENI.json`; bankada banka ön-kaydının listesi.
- Uygunluk: coinin kendi ilk barından 90 gün geçmiş olması (ısınma, §2.4) ve maskeli olmaması. Maskeden dönüş §2.5.
- Sıralama ölçütü: son 60 günün medyan günlük quote hacmi (V60).
- Mutlak taban: V60 ≥ 20M USDT (giriş ve kalış).
- BTC ve ETH taban ve ısınma koşuluyla her zaman evrende.
- Alt yuvaları: N − 2 = 13.
- **Öncelik kuralı (histerezis çatışması):**
  1. Mevcut alt üyelerden alt-sırası ≤ 20 olanlar sıra düzeninde tutulur.
  2. Bunlar 13'ü aşarsa en kötü sıradakiler çıkar.
  3. Boş yuvalar, alt-sırası ≤ 15 olan yeni adaylarla sıra düzeninde dolar.
  4. Eşitlikte alfabetik sıra.
  5. Yetersiz aday varsa yuva boş kalır.
- Evrenden çıkan coinin hedefi 0 olur; çıkış normal emir zinciriyle yapılır.

(v1'de bu listede yer alan S4 satırı yanlış yerdeydi; §4.5'e taşındı.)

### 2.4 Ortak ısınma kuralı
- D öncesinden veri alınmaz.
- Isınma **coin başınadır ve koşu başınadır**: bir coin, koşunun verisindeki kendi ilk barından 90 gün sonra sinyal
  ve boyutlama için uygun olur. Değerlendirme penceresi başına yeniden ısınma yapılmaz (BANKA Ek A.1 ile uyum:
  banka tek, sürekli koşudur; Z2 pencereyi boşaltmaz).
- D koşularında değerlendirme başlangıcı T0 = **2023-10-01 00:00 UTC** (D başı + 92 gün). Bütün D metrikleri T0'dan
  başlar. T0 öncesi yalnız ısınmadır; işlem yoktur.
- Bankada değerlendirme başlangıcı banka ön-kaydında tanımlıdır (T0_Z1).
- EWMA tahmincileri ilk gözlemden başlatılır; ağırlıklar kullanılabilir gözlemlere göre normalize edilir.
- Korelasyon: bir çift için ≥ 60 ortak gün yoksa o çiftte ρ = 0,7 kullanılır. Ortak gün, eksik getiri, merkezleme
  ve PSD düzeltmesi §3.2'dedir (KC-13).

### 2.5 Donma, delist ve coine özgü boşluk
Günlük, yalnız t'ye kadar kapanmış verilerle:
- (a) son 7 günün medyan hacmi < 90 günlük medyanın %10'u;
- (b) ≥ 6 ardışık 1h barda hacim 0 ya da O=H=L=C;
- (c) coinin bar akışı sürerken **son 16 saat** boyunca gerçek funding kaydı yok (mutlak eşik = 2 × 8h; K1-01);
- (d) son günde > 8 saat bar boşluğu.

(a)–(c) tetiklenirse hedef 0 ve maske. Maskeden dönüş: bir sonraki aylık seçim **ve** ≥ 30 ardışık temiz gün.
(d) tetiklenirse o gün o coinde yeni emir verilmez; mevcut pozisyon korunur; devreden emirlerden yalnız risk azaltan
parçalar reduce-only olarak korunur, risk artıran parçalar iptal edilir (§5.4 öncelik kuralı; KC-12). Sembol değişimi
birleştirilmez: eski sembol biter, yenisi yeni listelenmiş sayılır. `islem_disi_supheli` hiçbir kurala girmez.

Gerekçe (c): v1'deki "son aralığın 2 katı" eşiği, kısa aralıktan uzun aralığa dönüşte (1h→8h, 4h→8h) coini yanlış
maskeliyordu. Borsa aralığı en fazla 8 saattir; 16 saat, iki kaçırılmış 8 saatlik uzlaşmadır. Aralık geçişlerinin
varlığı görülmüş bilgidir (RAPOR §2.10); eşik borsa mekaniğinden gelir.

### 2.6 Borsa çapı boşluk ve eksik funding
**Borsa çapı boşluk.** Saat h'de, h−1'de barı olan **aday listenin tamamının** (geliştirmede 122, bankada banka
listesi; trend evreni değil; K1-20.7) ≥ %50'sinde bar yoksa h borsa çapı boşluktur. O saatten sonraki ilk günlük
karar ve boşluğun sürdüğü her karar **reduce-only**'dir: |w_yeni,i| ≤ |w_eski,i| ve işaret korunur ya da 0. Devreden
emirlerin risk artıran parçaları iptal edilir (§5.4). Tasfiye yapılmaz. Donma sayaçları boşluk saatlerini saymaz.

**Coine özgü boşluk:** §2.5.

**Eksik funding (K1-01, K1-02 ile yeniden yazıldı).**
- Δ_i(t): son 30 günde ardışık gerçek kayıtlar arasındaki en uzun aralık. 30 günde iki gerçek kayıt yoksa Δ_i = 8h.
- **Eksik olay:** son gerçek kayıttan bu yana 1,5·Δ_i geçti ve coinin bar akışı sürüyor (o saatte hacmi > 0 bar var).
- **Saatlik en kötü oran:** gerçek kayıtlar saatlik orana çevrilir (oran / aralık saati).
  - long için r*_i = max(son 30 günün en yüksek saatlik oranı, +r_taban);
  - short için r*_i = min(son 30 günün en düşük saatlik oranı, −r_taban);
  - r_taban = %0,01 / 8 = %0,00125 saatlik.
- **Dolgu:** eksik olay tespit edildiğinde, son gerçek kayıttan tespit anına kadar birikmiş saatler tek kalemde,
  sonra her saat sınırında yazılır: nakit_h = −q_i(h−)·mark_i(h)·r*_i. Yalnız bar akışının sürdüğü saatler dolgu alır.
- **Ters kayıt:** gerçek kayıt sonradan gelirse kaydın kapsadığı aralıktaki dolgular ters kaydedilir ve gerçek tutar
  yazılır. Düzeltme, kaydın geldiği saatte nakde işlenir. Karar girdilerine yalnız NAV yoluyla etki eder; geçmiş
  kararlar değişmez. Böylece aralık değişiminde çift sayım olmaz.
- **Delist:** bar akışı durunca dolgu yazılmaz. §1c.5'teki 30 günlük bekleme boyunca funding yoktur.
- **Skor:** carry skorundaki F30 yalnız gerçek kayıtlarla hesaplanır; dolgu F30'a girmez (K2-11, CARRY §10.2).
- Sonuç "doğrulanmamış" sayılmaz. Eksik olay sayısı, dolgu saatleri ve ters kayıtlar coin ve bacak bazında raporlanır.

### 2.7 Delist ve donma muhasebesi
§1c geçerlidir. Maske yalnız yeni riski ve hedefi keser. Pozisyon ancak gerçekleşebilir dolumla ya da 30 gün sonraki
uzlaşmayla kapanır. Çıkılamayan pozisyon açık yükümlülük olarak taşınır ve değerlenir. Funding yalnız gerçek kayıt
ya da bar akışı sürerken yazılan dolgu ile işler.

---

## 3. Mimari A (trend)

### 3.1 Sinyal
P_i,t: t anındaki günlük kapanış (§2.2). σ^sig_i = max(σ̂_EWMA,i, 0,20).

    s_i,t = (1/3) · Σ_{h∈{14,42,84}} τ_h,  τ_h = tanh( ln(P_i,t / P_i,t−h) / (σ^sig_i · √(h/365)) )

- s_i ∈ (−1, 1). Long ve short aynı formül. Ölü bölge yok.
- Girdiler yalnız tamamlanmış barlardan.
- P_i,t−h yoksa ya da coinin maskeli olduğu bir güne düşüyorsa o ufkun terimi τ_h = 0; payda 3 kalır (K1-20.2).
  Donmuş fiyat sinyale girmez.
- **"İşlem dışı" coin** (günlük kapanışı yok ya da §2.5(d)): hedef ağırlık mevcut ağırlığa eşitlenir; yeni emir
  yoktur; devreden emirlerin yalnız risk azaltan parçaları korunur (§5.4). Coin tavan hesaplarına mevcut ağırlığıyla
  girer (K1-20.3).
  Tavan çözücüsünde sabit girer; bütün küçültmeler serbest isimlere uygulanır. Sabit isimler tek başına bir
  tavanı ya da toplam risk kuralını aşıyorsa bu teknik hata değildir (K8, §3.5 tablo notu).
- Funding sinyali, ML, rejim filtresi yok.

### 3.2 σ̂ ve Σ̂
- Boyutlama σ̂_i: §1b sonucuna göre σ̂_EWMA,i ya da σ̂_HAR,i; her durumda taban %20.
- **Matris kapsamı.** Her kararda tek bir matris kurulur: o gün hedefe giren bütün coinler (trend evreni A_t, B'de
  carry adayları ve BTC). Trend ve carry aynı R̂'nin alt bloklarını kullanır.
- **Günlük getiri (KC-13).** r_i,t = ln(P_i,t / P_i,t−1g) yalnız iki ardışık günlük kapanış varsa tanımlıdır; aksi
  halde (işlem dışı gün, maske, listeleme öncesi) **eksiktir**, 0 yazılmaz. Ortalama sıfır varsayılır (merkezleme
  yok), σ̂_EWMA ile aynı.
- **Çift-bazlı ham korelasyon.** Her (i, j) çifti için O_ij = ikisinin de getirisinin tanımlı olduğu günler. Ağırlık
  a_t = 2^(−yaş_t/90), yalnız O_ij üzerinde. c_ij = Σ a·r_i·r_j, v_i^(ij) = Σ a·r_i², v_j^(ij) = Σ a·r_j² (üçü aynı
  gün kümesinde); ρ_ij = c_ij / √(v_i^(ij)·v_j^(ij)). Aynı gün kümesi kullanıldığı için |ρ_ij| ≤ 1 (Cauchy–Schwarz).
  |O_ij| < 60 ise ρ_ij = 0,7. Köşegen 1. Sonuç R_çift simetriktir ama **PSD olmayabilir** (farklı ortak geçmişler,
  dolgu).
- **PSD düzeltmesi (özdeğer kırpma; dondurulur).** R_çift = QΛQᵀ özayrışımı; Λ⁺ = max(Λ, ε), ε = 10⁻⁸;
  B = QΛ⁺Qᵀ; **R_EW = D^(−1/2)·B·D^(−1/2)**, D = diag(B). R_EW simetrik, köşegeni 1 ve PSD'dir. Kırpılan özdeğer
  sayısı ve Frobenius düzeltme büyüklüğü ‖R_EW − R_çift‖_F her gün kaydedilir. Higham en yakın korelasyon yöntemi
  alınmadı: yinelemeli, tolerans parametresi ister; kırpma tek adımlı ve deterministiktir.
- R_S: köşegen 1, diğer bütün öğeler 0,7. PSD'dir (özdeğerler 0,3 ve 1 + 0,7·(N−1)).
- **R̂ = 0,5·R_EW + 0,5·R_S**; Σ̂ = diag(σ̂)·R̂·diag(σ̂). PSD matrislerin dışbükey birleşimi olduğundan R̂ PSD'dir;
  en küçük özdeğeri ≥ 0,5·0,3 = 0,15 olduğundan pozitif tanımlıdır. √(wᵀΣ̂w) her w için tanımlıdır.
- R_0: birim matris (hedge çöküşü senaryosu); Σ₀ = diag(σ̂)·R_0·diag(σ̂).
- **Codex karşı örneği (KC-13).** R_çift dış köşegenleri (0,9; 0,9; −0,9) iken PSD değildir; harmanı (0,8; 0,8; −0,1)
  v = (−1; 0,5; 0,5) için −0,15 verir. Kırpmadan sonra R_EW PSD olduğundan harman da PSD'dir; bu durum oluşamaz.
- **Boyut dalları.** Matris boyu 0 ise (boş evren) Σ̂ kurulmaz; trend ve carry kitapları 0'dır (§3.3 N_t = 0 dalı,
  §4.1 genişlik kuralı). Boyu 1 ise R̂ = [1].

### 3.3 Birim risk: iki yönlü hedef ve yukarı çarpan sınırı
A_t: o gün sinyali tanımlı, maskesiz evren üyeleri; N_t = |A_t|.

1. Ham kitap: u_i = s_i / σ̂_i.
2. Referans kitap (hepsi tam sinyalde, aynı yönde): f_i = 1/σ̂_i. Ex-ante vol'ü √(fᵀΣ̂f) = √(1ᵀR̂1).
3. Çeşitlendirme çarpanı: M_t = N_t / √(1ᵀR̂1). M_t ≥ 1'dir.
4. Yukarı çarpan sınırı: M̃_t = min(M_t, M_max), **M_max = 1,5** (KARARLAR §2 gereği).
5. Ölçek: k_t = τ·M̃_t / N_t, **τ = %15**.
6. Birim kitap: w^u_i = k_t·u_i.
7. **Değişmez (K1-11; nesnesi: birim trend kitabı w^u, kaldıraç ve tavan öncesi; §3.5 T4-a):**
   V = max(√(w^uᵀΣ̂w^u), √(w^uᵀΣ₀w^u)) ≤ τ.
8. **Boş evren dalı (KC-13):** N_t = 0 ise M_t, k_t ve w^u tanımlanmaz; birim trend kitabı sıfır vektördür ve bütün
   trend hedefleri 0 olur (çıkışlar normal emir zinciriyle). N_t = 1 ise R̂ = [1], M_t = 1.

**Adım 7 neden değişmezdir.** R̂'nin bütün öğeleri ≥ 0 iken, |s_i| ≤ 1 için sᵀR̂s ≤ 1ᵀR̂1 ve sᵀs ≤ N ≤ 1ᵀR̂1'dir.
Bu yüzden V ≤ τ matematiksel olarak sağlanır. R̂ yalnız R_EW < −0,7 olan çiftlerde negatif öğe taşır. Motor V'yi
yine hesaplar: V > τ ise w^u ← w^u·τ/V uygulanır ve olay kaydedilir. Bu bir parametre değil, güvenlik denetimidir.

**M_max ne zaman bağlar.** M > 1,5 ancak 1ᵀR̂1 < N²/2,25 iken olur. N = 15'te bu, R̂'nin ortalama dış köşegen öğesinin
0,405'in altına, yani ortalama R_EW'nin ~0,11'in altına inmesi demektir. Tipik korelasyonlarda (R_EW ortalaması
0,3–0,6) M 1,2–1,4 aralığındadır; bu aralık D'nin korelasyon özetinden gelen aritmetiktir (görülmüş bilgi). Sınır
seyrek bağlar ama KARARLAR §2 gereği tutulur. Korelasyon sıçramasına motorun gerçek tepkisi M'nin bu aralıkta
düşmesidir.

**Yorum (KC-14 ile düzeltildi).** Birim risk, "tam sinyal referans kitabının ex-ante vol'ü %15" olarak tanımlıdır.
Bu bir tavan değildir, ama her gün tam tutturulan bir sabit de değildir: referans kitabın ex-ante vol'ü
τ·M̃_t·√(1ᵀR̂1)/N_t = τ·min(1, M_max/M_t)'dir. **Referans kitap, çarpan ve tavanlar izin verdiğinde %15'tir:**
M_t ≤ M_max iken tam %15, M_t > M_max iken %15'in altındadır; kaldıraç sonrası isim/brüt/şok tavanları gerçek kitabı
ayrıca düşürebilir. Sayısal örnek (Codex): N = 15, R_EW = I iken R̂'nin dış köşegeni 0,35, 1ᵀR̂1 = 15 + 210·0,35 =
88,5, M ≈ 15/9,41 ≈ 1,59 > 1,5; referans vol = %15·1,5·√88,5/15 ≈ **%14,1**. Korelasyon düşünce k yükselir (en fazla
1,5 kat), yükselince düşer. Vol düşünce u_i büyür (σ̂ tabanıyla sınırlı), yükselince küçülür. Hedef iki yönlüdür.
Gerçek kitabın vol'ü sinyal gücüyle orantılıdır ve genellikle %15'in altında kalır. Zayıf ya da karışık sinyal
büyütülmez. **%7–11 gerçekleşen vol yalnız bir önseldir** (`cta` tahmini); ölçülmedi, bu belgedeki hiçbir hesap onu
ölçülmüş kabul etmez (§1d ve CARRY §8.4'teki σ_T = %9 da önseldir). Banka raporu hem birim ölçeği hem gerçekleşen
vol'ü verir; Kelly tablosu gerçekleşen vol'e dayanır; Kelly artışı düşük gerçekleşen vol'ün otomatik telafisi
sayılmaz. Yorum §9 soru 1'de kullanıcıya sunulur ve kilitten önce yanıtlanır.

### 3.4 Kaldıraç
Kullanıcının Kelly adayı L, birim kitaba uygulanır: w^L = L·w^u. L listesi banka ön-kaydındadır. Motor L'yi girdi
olarak alır. Bütün tavanlar **w^L üzerinde**, NAV cinsinden ve L'den bağımsız değerlerle uygulanır. 2L sistemi L
sisteminin iki katı değildir; her aday ayrı koşulur.

### 3.5 Tavanlar (kaldıraç sonrası NAV)
Uygulama sırası: isim tavanları → brüt → şok senaryoları. Her adım yalnız küçültür.

**İsim tavanları:** BTC ve ETH için |w| ≤ %35; alt long w ≤ %6; alt short |w| ≤ %4 (B'de net kitapta %3,33; §4.5).
Aşan ağırlık tavana kırpılır.

**Brüt:** Σ|w| ≤ 2,0. Aşılırsa bütün ağırlıklar aynı katsayıyla küçülür.

**Şok senaryoları (hedge kredisiz: karşı taraftaki kazanç sayılmaz):**
- S1 aşağı: bütün long'larda alt −%70, BTC/ETH −%30. Kayıp_S1 = 0,70·Σ(alt long) + 0,30·Σ(BTC/ETH long).
  Sınır **%20 NAV**.
- S2 yukarı: en büyük tek alt short +%100, diğer alt short'lar +%50, BTC/ETH short'ları +%25.
  Kayıp_S2 = 1,00·max(alt short) + 0,50·Σ(diğer alt short) + 0,25·Σ(BTC/ETH short). Sınır **%20 NAV**.

**Çözücü (A; deterministik):**
1. S1 ihlalde long tarafın bütün ağırlıkları c₁ = 0,20/Kayıp_S1 ile küçülür (BTC/ETH dahil).
2. S2 ihlalde short tarafın bütün ağırlıkları c₂ = 0,20/Kayıp_S2 ile küçülür.
3. Nihai kitap bütün tavanlarla yeniden sınanır. İhlal sürerse 1–2 tekrarlanır; en fazla 5 tur. Sonra hâlâ ihlal
   varsa bütün kitap tek katsayıyla küçülür.
4. Her gün hangi tavanın bağladığı kaydedilir (bağlama sıklığı raporu).

B'nin net kitap çözücüsü §4.5'tedir; A'da iki çözücü aynı sonucu verir.

**Değişmezler, nesne ve aşama bazında (K1-04, KC-09).** Her değişmez tek bir nesnede ve tek bir aşamada denetlenir.
V(x) = max(√(xᵀΣ̂x), √(xᵀΣ₀x)); V bir normdur (Σ̂ ve Σ₀ PSD; §3.2).

| Kod | Nesne | Aşama | Değişmez | İhlal |
|---|---|---|---|---|
| T4-a | Birim trend kitabı w^u | §3.3 adım 7; kaldıraç ve tavan öncesi | V(w^u) ≤ τ; M̃ ≤ M_max | Güvenlik ölçeklemesi + olay kaydı; ölçekleme sonrası ihlal teknik hata |
| T4-b | Carry birim kitabı w^C (altlar + geçici BTC hedge) | §4.4 adım 1 ölçekleme sonrası, ω_C ve L öncesi | V(w^C) ≤ τ | Teknik hata (ölçekleme tanım gereği eşitlik verir) |
| T4-c | Carry bloğu: ω_C·L uygulanmış, carry isim tavanı, yeniden nötrleme ve BTC hedge yeniden kurulumu sonrası (günlük, κ^C öncesi) | §4.4 adım 3–6, §4.5 adım 0 | V ≤ ω_C·L·τ | Güvenlik ölçeklemesi (bloğun tek katsayısı) + olay kaydı; sonrası ihlal teknik hata |
| T4-d | Kaldıraçlı net hedef kitap (HedefKitap; çözücü ve bant sonrası) | §3.5 / §4.5 sonu | İsim, brüt, S1, S2 (B'de S4) tavanları; **toplam risk kuralı** V(w*) ≤ L·(1 + ω_C·𝟙_B)·τ | Tavanlar: teknik hata. Toplam risk: güvenlik ölçeklemesi + olay kaydı; sonrası ihlal teknik hata. İstisna (K8): ihlal işlem dışı (sabit) isimlerden geliyorsa olay kaydı, teknik hata değil |
| — | Gerçekleşen + devreden defter | Her saat | Değişmez yok | Rapor (§5.7; banka R5) |

- **İşlem dışı isim istisnası (K8, kullanıcı kararı 2026-09-28).** İşlem dışı coinde emir yasak olduğundan
  (§3.1) o isim hedefte mevcut ağırlığında sabit kalır ve piyasa hareketiyle bir tavanı aşabilir. Bu durumda:
  toplam tavanlarda (brüt, S1, S2, B'de S4) ve toplam risk kuralında serbest isimler sınıra, gerekirse 0'a kadar
  küçültülür; kalan ihlal **teknik hata sayılmaz**, olay olarak kaydedilir (`sabit_tavan_ihlali`,
  `sabit_t4d_ihlali`) ve raporlanır. Sabit ismin kendi isim tavanını aşması öteki isimleri küçültmez. Gerekçe:
  ihlal karardan değil piyasadan gelir; teknik hata koşuyu piyasa verisi yüzünden durdururdu. Coin ertesi gün
  işlem dışı değilse normal kurallarla tavana indirilir (bant geçersiz: isim tavanı aşımı, §3.6). Banka T4
  denetimi bu istisnayı aynı biçimde uygular; istisna gün sayısı ve en büyük aşım raporlanır.
- **V ≤ τ yalnız T4-a ve T4-b'dir.** Kaldıraçlı net hedefte V ≤ τ aranmaz: L = 2'de birim V = %12 ise hedefte V = %24
  geçerlidir (Codex KC-09 örneği). Kaldıraçlı nesnedeki sınır toplam risk kuralıdır.
- **Toplam risk kuralı.** V norm olduğundan V(L·w^u + blok) ≤ L·τ + ω_C·L·τ üçgen eşitsizliğinden gelir; tavan
  küçültmeleri tekdüze olmadığından (negatif korelasyonlu isimlerde küçültme V'yi artırabilir) motor bunu yine
  hesaplar. İhlalde bütün net kitap tek katsayıyla sınıra küçültülür ve olay kaydedilir. A'da sınır L·τ, B'de
  L·1,2·τ (L = 1'de %18). Bu yeni parametre değildir; τ, ω_C ve L'den türetilir.
- Gerçekleşen kitap katılım sınırı yüzünden hedefin gerisinde kalabilir; bu hata değildir, §5.7'de raporlanır.
- Banka T4 bu tabloyu kullanır (KC-09'un banka tarafı BANKA'dadır).

Şok tavanı gerçekleşmiş DD sınırı değildir. %30 DD sınırının sağlandığı buradan iddia edilemez.

**DD çarpanı yoktur.** Codex ilkesi (DD tetikli çıkış yok) ve Kelly tablosunun yola bağımlı olmaması için çekirdeğe
alınmaz. MIMARI, `risk` tasarımının DD çarpanını bankaya betimsel ablasyon olarak **önermez** (K2-08). Banka ön-kaydı
yine de koşacaksa çıktısı ileri demo kararına kadar yalnız hash olarak tutulur ve DSR sayacına girer.

### 3.6 İşlem bandı
Her coin için, tavanlardan geçmiş hedef w*_i ve mevcut ağırlık w⁰_i (son kapanışla değerlenmiş):

    b_i = max(0,20·|w*_i|, 0,002)
    w⁰_i ∈ [w*_i − b_i, w*_i + b_i]  → işlem yok
    aksi halde → en yakın sınıra: w*_i ± b_i

Band geçersiz (doğrudan w*_i'ye işlem): w*_i = 0; sign(w*_i) ≠ sign(w⁰_i); evrenden çıkış; maske; mevcut
pozisyonun bir isim tavanını aşması. Band sonrası kitap bütün tavanlarla yeniden sınanır. İhlal varsa ihlal eden
tarafın bütün isimlerinde band kapatılır ve o isimler w*'ye gider.

### 3.7 Katılım sınırı (K1-05 ile değişti)
Bir coinde saat h'de dolabilecek en büyük nominal:

    Q_max,i,h = min( 0,001·V1h30_i , 0,001·V1h7_i , 0,10·hacim_i,h−1 )

- V1h30_i ve V1h7_i: son 30 ve 7 günün medyan saatlik quote hacmi; karar anında hesaplanır, karar boyunca sabittir.
- hacim_i,h−1: bir önceki tamamlanmış saatin quote hacmi (PIT).
- Gerekçe: donma ölçütü (a) tetiklendiğinde 30 günlük medyan hâlâ eski hacmi taşır; 7 günlük medyan ve önceki saat
  terimi ölen coinde barın tamamından fazlasını doldurmayı engeller.
- Risk azaltan emirler de aynı sınıra tabidir; gecikme gizlenmez, raporlanır.

### 3.8 Felaket stopu (yalnız canlı; K1-19)
- Borsada bekleyen reduce-only `closePosition` STOP_MARKET, MARK_PRICE tetikli.
- Referans: son kararın fiyat_ref'i. Uzaklık 4 × ATR(14 gün), ATR karar anında günlük barlardan.
- Her günlük karardan ve her dolumdan sonra yeniden kurulur.
- Tetiklenirse sonraki günlük karara kadar o coinde yeni giriş yoktur. Sonraki karar saf zincirle normal çalışır.
- Stop garantili fiyat değildir; gap ve fitilde kötü dolabilir.
- Mark geçmişi olmadığından geri teste girmez. Geri testte yalnız bir duyarlılık satırı verilir: 1h high/low ile
  tetik, sonraki barın açılışında dolum (rapor; bağlayıcı değil). Parite istisnasıdır (§5.6).

---

## 4. B'nin carry uydusu

### 4.1 Evren
- Yalnız altlar; BTC yalnız hedge aracı. ETH carry'de kullanılmaz.
- Isınma §2.4; donma/delist §2.5; maske trend ile ortaktır.
- Giriş V30 ≥ 20M, çıkış V30 < 10M (V30: 30 günlük medyan günlük hacim). V30 < 50M isimlerde carry isim
  tavanları yarıya iner. Histerezisteki "mevcut" isim: önceki Pazartesi'nin aday listesinde olan ya da q^C* ≠ 0 olan
  isimdir (pozisyon taşıması gerekmez).
- **V60 tabanı (2026-09-29; kullanıcı onayı 29 Eylül, Codex itirazına rağmen).** Aday ayrıca trend evreninin mutlak tabanını sağlar: V60 ≥ 20M. Tutulan bir ismin V60'ı
  20M'nin altına düşerse isim carry evreninden çıkar (hafta içi çıkış; §4.4). Gerekçe: §6.1'in < 20M dilimi yalnız
  çıkış için tanımlıdır. Bu çıkış olmasaydı haftalık yeniden hesap ya da κ^C_t'nin günlük artışı < 20M'de sanal carry
  bacağına giriş yaratır ve bacak maliyeti (§4.7) tanımsız kalırdı. Kural D verisine bakılarak seçilmedi.
- Son 30 günde birden fazla eksik funding olayı (§2.6) yaşayan isim aday olmaz.
- Genişlik: aday sayısı n_C < 15 ise carry brütü ×0,5; n_C < 10 ise carry kitabı 0.

### 4.2 Skor ve nötrleme
- F30_i = (son 30 günün gerçek funding oranları toplamı) × 365/30. Gerçek damgalar; tahmini oran ve dolgu yok.
- σ^C_i = max(σ̂_EWMA,i, 0,30).
- Ham skor: c_i = F30_i / σ^C_i.
- Nötrleme (kesitsel OLS, sıralar üzerinde):
  rank(c) = a + b₁·rank(R30) + b₂·rank(s^trend) + b₃·rank(β) + ε. Skor z_i = ε_i.
  R30: 30 günlük log getiri; s^trend: §3.1 sinyali; β: §4.3.
- s^trend, trend evreninde olsun olmasın **bütün carry adayları** için §3.1 formülüyle hesaplanır (CARRY §10.1;
  K1-20.10).
- Gerekçe: R30 gizli momentum/ters dönüş bahsini, s^trend trend bacağıyla örtüşmeyi, β beta sızıntısını keser.
  R7 alınmaz: 5 regresör 20–40 isimlik kesitte serbestliği şişirir.

### 4.3 Bacaklar, ağırlık ve hedge
- Short adayları: z'nin en yüksek %30'u. Long adayları: en düşük %30'u.
- Histerezis: mevcut short, z medyanın altına inene kadar; mevcut long, medyanın üstüne çıkana kadar tutulur.
- Long şartı: F30_i ≥ −%50 (yıllık). Şart **mevcut long'a da** uygulanır; sağlanmazsa isim long bacaktan çıkar
  (K1-20.5).
- Bacak içi ağırlık ∝ 1/σ^C_i. İki bacak eşit nominal (dolar-nötr).
- β_i = 0,5·β̂_i + 0,5; β̂_i: son 60 günün günlük log getirileriyle BTC'ye OLS betası. β_i Pazartesi kararında
  hesaplanır ve hafta boyunca sabittir.
- **Nötrlüklerin sahibi (KC-04).** *Dolar nötrlüğü carry alt sepetinin* özelliğidir: Σ_{i∈alt} w^C_i = 0. *Beta
  nötrlüğü carry bloğunun* (alt sepeti + BTC hedge) özelliğidir: Σ_alt β_i·w^C_i + w^C_BTC = 0. BTC hedge dahil carry
  bloğu genel olarak dolar-nötr değildir. Net kitap (trend + carry) nötr değildir; trend yönlü bir kitaptır ve hiçbir
  nötrlük ona uygulanmaz.
- BTC hedge: w^C_BTC = −Σ_{i∈alt} β_i·w^C_i, **o günkü gerçek alt sepeti** üzerinden. Bu formül iki yerde kullanılır:
  §4.4 adım 1'de yalnız ölçekleme için geçici olarak; §4.5 adım 0'da her gün, isim tavanı, bant, maske ve yeniden
  nötrleme SONRASI kalan alt ağırlıklarıyla bağlayıcı olarak. Hedge'in miktarı haftalık sabit **değildir**.

### 4.4 Sabit risk bütçesi ve haftalık alt miktarları (KC-04 ile sıra değişti)
Pazartesi kararında, bu sırayla. Her adım yalnız küçültür ya da sıfırlar (adım 5'teki bant eski miktarı tutabilir):

1. **Ölçekleme (K1-10):** altlar ve geçici BTC hedge'i (§4.3) içeren carry birim kitabı tek katsayıyla ölçeklenir:
   ölçek = τ / V(w^C), τ = %15, V §3.5'teki gibi. Trendle aynı ilke: dolar-nötr kitaba yüksek ρ hedefinden hedge
   kredisi verilmez. Geçici hedge yalnız bu ölçeği belirler; sonra atılır.
2. **Bütçe:** alt katkıları w^C,L_i = L·ω_C·w^C_i, **ω_C = 0,20**.
3. **Carry isim tavanları** (ω ve L uygulanmış, NAV cinsinden): short ≤ %1,0, long ≤ %1,5; V30 < 50M isimlerde yarısı.
   Kırpılan pay bacağın diğer isimlerine dağıtılmaz. Ölçekleme yeniden yapılmaz.
4. **Miktara çevirme:** q^C,ham_i = w^C,L_i·NAV/fiyat_ref_i (yalnız altlar).
5. **Haftalık bant (K1-20.6; isim başına):** |q^C,ham_i − q^C*_eski,i| / |q^C,ham_i| < 0,25 ise q^C,ham_i ← q^C*_eski,i.
   Yeni hedef 0, isim girişi ya da işaret değişimi her zaman işlenir.
6. **Alt sepetinin yeniden dolar-nötrlenmesi (KC-04).** Adım 3 ve 5 bacak nominallerini eşitsizleştirir.
   N_L = Σ_{long} q_i·fiyat_ref_i, N_S = Σ_{short} |q_i|·fiyat_ref_i. Ağır bacağın **bütün** isimleri (bantla tutulanlar
   dahil) λ = min(N_L, N_S)/max(N_L, N_S) ile çarpılır; hafif bacak değişmez. Yalnız küçültür; carry isim tavanları
   korunur. Bir bacak boşsa carry kitabı o hafta 0'dır. Öncelik: **nötrlük banttan önce gelir**; bantla tutulan
   isim λ yüzünden değişebilir. λ ve bağlayan bacak kaydedilir.
7. Sonuç **q^C*_i** (yalnız altlar) haftanın alt miktarıdır. BTC hedge'in haftalık miktarı yoktur (§4.5 adım 0).

**Hafta içi alt miktarları** yalnız şu olaylarla değişir; başka hiçbir anda değişmez:
- maske ya da evren çıkışı (V30 < 10M, V60 < 20M ya da bar yok; §4.1): q^C*_i ← 0; aynı gün adım 6'daki yeniden
  nötrleme günün fiyat_ref'i ile uygulanır ve
  küçülen miktarlar haftanın geri kalanı için yeni q^C*'dır (yalnız küçültür; hafta içinde hiçbir alt miktarı büyümez);
- günlük κ^C_t (§4.5) alt miktarlarını değiştirmez; yalnız net kitaba giren carry katkısını ölçekler.

**Carry miktarının güncelleme kuralı (tek tanım; KC-03'ün mimari tarafı).** Alt miktarları **haftalık** %25 bantla
(adım 5), yeniden nötrleme (adım 6 ve hafta içi çıkışlar) ve çıkışlarla güncellenir. Net kitaba giren carry katkısı
ise **her gün** κ^C_t ile doğrudan ölçeklenir: κ^C_t için bant ya da eşik **yoktur**; κ^C_t = 0,8 ise o gün carry
katkısı tam %20 küçülür. Sanal carry bacağı (§4.7) bu iki kuralın bileşimidir. CARRY'nin sanal defteri bu tanımı
birebir kullanır; κ için ayrı bir %25 bandı tanımlanmaz.

### 4.5 Net kitap çözücüsü (K1-09, KC-04 ile değişti)
**Adım 0 — günlük carry bloğunun kurulması (her günlük karar; KC-04).**
- Alt katkıları: w^C_i,t = q^C*_i·P_i,t/NAV_t (hafta içi çıkışlar ve yeniden nötrleme uygulanmış haliyle).
- BTC hedge **o günkü gerçek alt sepetinden yeniden kurulur**: w^C_BTC,t = −Σ_alt β_i·w^C_i,t. Böylece isim kırpması,
  bant, λ, maske ve hafta içi fiyat kayması sonrası blok beta-nötrdür. Hedge günlük değiştiği için lot adımı altındaki
  değişim §5.1 kuralıyla 0 sayılır ve raporlanır (K1-18).
- Blok ex-ante vol'ü T4-c ile denetlenir: V(w^C_t) > ω_C·L·τ ise blok (altlar ve hedge) tek katsayıyla küçültülür.
- Alt sepeti fiyat kaymasıyla hafta içinde tam dolar-nötr kalmaz; bu kayma düzeltilmez (beta kısmını hedge taşır),
  günlük |Σ_alt w^C_i,t| / Σ_alt |w^C_i,t| raporlanır.
- **Codex örneği (KC-04).** β = 1, +%2 long / −%2 short. İsim tavanları sonrası +%1,5 / −%1: adım 6 long bacağı
  λ = 1/1,5 ile +%1'e indirir; hedge −(1 − 1) = 0; yönlü maruziyet 0. Yeniden nötrleme olmasaydı adım 0'daki hedge
  −%0,5 olur ve beta maruziyeti yine 0 olurdu; yeniden nötrleme ayrıca dolar nötrlüğünü korur. Hafta içinde bir long
  çıkarsa aynı gün short bacağı λ ile küçülür ve hedge yeniden kurulur; long bacağı tamamen boşalırsa λ = 0, blok
  kapanır. Kalan short açıkta kalmaz.

Net aday kitap w_i = w^T_i + w^C_i,t (BTC için w^T_BTC + w^C_BTC,t). Çözücü carry bloğunu (altlar + yeniden kurulmuş
hedge) tek parça tutar; önce trend bacağını küçültür:

1. **İsim tavanları (net):** tavanı aşan coinde trend bileşeni, net ağırlık tavana inene kadar küçültülür (işaret
   değiştirmez). Alt short tavanı B'de **%3,33**'tür: S4 (net kitaptaki en büyük tek alt short +%300, sınır %10 NAV)
   bir isim tavanına denktir (3,0·|w| ≤ 0,10) ve bu adımda uygulanır (K1-20.4). Carry isim tavanları (≤ %1,5) net
   tavanların altında olduğundan carry bileşeni tek başına isim tavanını aşamaz; aşarsa değişmez ihlalidir.
2. **Brüt (net):** Σ|w| > 2,0 ise trend bacağı c_g ∈ [0, 1] ile küçültülür (koşulu sağlayan en büyük değer). c_g = 0
   yetmezse carry bloğu κ^C ile küçültülür.
3. **S1/S2 (net):** S1 ihlalinde pozitif trend bileşenleri c₁ ile, S2 ihlalinde negatif trend bileşenleri c₂ ile
   küçültülür; c₁, c₂ ∈ [0, 1] koşulu sağlayan en büyük değerlerdir. Kayıp, katsayının parça parça doğrusal ve
   azalmayan fonksiyonu olduğundan değer 60 adımlı ikiye bölmeyle bulunur (A'da kapalı biçim §3.5 ile aynıdır).
   En fazla 5 tur. İhlal sürerse carry bloğu κ^C ile küçültülür. Yine sürerse bütün net kitap tek katsayıyla küçülür.
4. **κ^C_t ∈ [0, 1]** carry bloğunun o günkü tek katsayısıdır: bütün carry alt isimleri ve adım 0'da yeniden kurulmuş
   BTC hedge aynı katsayıyla küçülür. Blok içi oranlar değişmediğinden alt sepeti dolar-nötr, blok beta-nötr kalır.
   κ^C_t her gün yeniden çözülür ve **doğrudan** uygulanır (bant yok; §4.4 tek tanım). Önceki günün κ'sı girdi değildir.
   Kısıtlar (net isim tavanları, brüt, S1, S2) κ'da dışbükey olduğundan uygun κ kümesi bir aralıktır ve 0'ı
   içermeyebilir; κ^C_t bu aralığın en büyük değeridir. Uygun κ yoksa κ en küçük ihlal noktasında kalır ve son çare
   (tek katsayı) uygulanır.
5. **Bant yalnız trend bileşenine (KC-04 ile değişti).** §3.6 bandı, çözücüden geçmiş trend hedefi w^T*_i'ye, önceki
   sanal trend miktarının fiyat_ref ile değerine göre uygulanır: w^T,b_i. Carry bloğu banttan geçmez (alt miktarlarının
   bandı haftalık §4.4 adım 5'tir). Böylece net hedefteki carry parçası tam olarak nötr bloktur; v1'deki net-ağırlık
   bandı, bloğu isim isim eski net ağırlıkta tutarak nötrlüğü bozuyordu.
6. Nihai hedef: w*_i = w^T,b_i + κ^C_t·w^C_i,t. Kitap bütün tavanlarla ve toplam risk kuralıyla (T4-d) yeniden
   sınanır; tavan ihlali varsa ihlal eden tarafın trend isimlerinde bant kapatılır (§3.6 ile aynı kural). Her gün c_g,
   c₁, c₂, κ^C, λ, hedge ağırlığı ve bağlayan tavan kaydedilir.

**Sıra özeti (B, her günlük karar):** trend birim kitabı (§3.3) → L → [V60 < 20M isimde trend bileşeni önceki sanal
trend değerine göre yalnız azaltılır] → [Pazartesi: carry §4.4 adım 1–7] → carry adım 0 (hafta içi çıkış + yeniden
nötrleme + hedge yeniden kurulumu + T4-c) → net isim tavanı → brüt → S1/S2 → κ^C → trend bandı → yeniden sınama
(tavanlar) → net kitaba yalnız-azaltma (reduce-only §2.6; V60 < 20M isimde gerçek ağırlığa göre, A ile aynı) → toplam
risk kuralı (T4-d, nihai kitapta) → lot yuvarlama.

### 4.6 Uzlaşma ve funding muhasebesi
Funding net pozisyona tek kez uygulanır (§5.3). Bacaklara uzlaşma anındaki sanal bacak miktarlarıyla (§4.7) dağıtılır.

### 4.7 Sanal bacaklar, P&L satırları ve icra artığının bölünmesi
**Sanal bacaklar (çözücünün gerçek çıktısıyla aynı; K1-09).** Her iki bacak için sanal miktar tutulur. Yeni miktar
kararın 1 saat sonrası, 01:00 barının açılışında geçerli olur; karar anında fiyat yazılmaz.
- Sanal carry altları: q^C,v_i = κ_etkin,t·q^C*_i (haftalık alt miktarı, hafta içi çıkış/yeniden nötrleme sonrası, ×
  günlük blok katsayısı). **κ_etkin,t = κ^C_t × (son çare katsayısı) × (T4-d katsayısı) × (T4-c katsayısı)**; güvenlik
  ölçeklemeleri bağlamadığında κ_etkin,t = κ^C_t. Karar kaydı κ^C_t ve κ_etkin,t'yi ayrı yazar (2026-09-29).
- Sanal carry hedge'i: q^C,v_BTC = κ^C_t × (son çare) × (T4-d)·w^C_BTC,t·NAV_t/fiyat_ref_BTC (w^C_BTC,t: §4.5 adım
  0'da günlük yeniden kurulan, T4-c sonrası hedge).
- Sanal trend: q^T,v_i = w^T,b_i·NAV/fiyat_ref_i (§4.5 adım 5'teki trend bandından geçmiş hedef). Bantta tutulan
  miktar önceki sanal miktarın kendisidir. Net hedef tanım gereği sanal trend + sanal carry'dir; icra artığı lot,
  katılım ve tavan yeniden sınamasından doğar. **İstisna (2026-09-29):** net kitaba uygulanan yalnız-azaltma kuralları
  (reduce-only §2.6, işlem dışı coin §3.1, V60 < 20M) sanal bacakları değiştirmez; o gün o isimde net hedef ile
  sanal toplam arasındaki fark icra artığıdır ve s^C ile bölünür. Bu günler ve isimler raporlanır.
- A'da sanal trend yerine gerçek pozisyon kullanılır; icra artığı tanım gereği 0'dır.

**Satırlar.**

| Satır | Tanım |
|---|---|
| Trend fiyat | q^T,v'nin fiyat P&L'i |
| Trend funding | q^T,v'nin funding'i |
| Carry funding | q^C,v alt miktarlarının funding'i |
| Carry fiyat | q^C,v alt miktarlarının fiyat P&L'i |
| Carry hedge | q^C,v BTC miktarının fiyat + funding P&L'i (CARRY bunu funding ve fiyat alt satırlarına böler) |
| Maliyet (bacak) | Her bacağın kendi |Δq^v|'sine §6.1 modeliyle ayrı hesaplanan maliyet; karekök teriminde Q = bacağın kendi dolum nominali |
| Netleme kazancı | Σ bacak maliyetleri − gerçek net maliyet |
| İcra artığı | Gerçek NAV değişimi − yukarıdakilerin toplamı (lot, katılım, bant yeniden sınaması, tavan etkileşimi) |

**İcra artığının bacaklara bölünmesi (şimdi dondurulur; K1-20.13, K2-11, CARRY V4).** Her gün ve her coin için
artık miktar e_i = q_i − q^T,v_i − q^C,v_i, artık P&L'i A_i (e_i'nin fiyat + funding P&L'i) ve gerçek maliyetin bacak
maliyetleri dışında kalan kısmı. Carry payı:

    s^C_i,t = |q^C,v_i,t| / (|q^T,v_i,t| + |q^C,v_i,t|)
    iki sanal miktar 0 ise s^C_i,t = s^C_i,t' ; t' = iki sanal miktarın birlikte 0 olmadığı son gün; böyle gün yoksa 0
    A^C = Σ_i s^C_i · A_i,   A^T = Σ_i (1 − s^C_i) · A_i

**Tek fonksiyon ve zaman damgası (KC-03'ün mimari tarafı).** s^C_i,t, t günü 01:00 açılışında geçerli olan sanal
miktarlarla (günün yeni miktarları) hesaplanır ve [t 01:00, t+1 01:00) aralığındaki bütün A_i saatlerine uygulanır.
Sıfır/sıfır durumu artığın kaynağını izler: iki sanal bacak sıfırken kalan gerçek pozisyon (ör. katılım sınırı
yüzünden çıkamayan eski carry short'u) bu pozisyonu en son hangi bacak(lar) taşıdıysa o paylarla bölünür. Round-1'deki
"0" ve CARRY v1'deki "0,5" okumalarının yerine bu kural geçer; CARRY §5.6 bu fonksiyonu birebir kullanır. Netleme
kazancı bacaklara yazılmaz. İcra artığının mutlak değeri ve işareti raporlanır.

---

## 5. Ortak motor sözleşmesi

REV1 motoru değiştirilmez. v8 ayrı bir modüldür (`v8/` altında, ayrı yapılandırma; `config.py` import edilmez).
Aşağıdaki fonksiyonlar saftır: yan etki yok, saat okumaz, ağ yok, rastgelelik yok.

### 5.1 İmzalar

    hedef_agirlik(gorunum: PiyasaGorunumu, durum: StratejiDurumu, L: float, P: Parametreler) -> HedefKitap
      gorunum: t'ye kadar kapanmış 1h barlar, funding kayıtları, evren, hacim istatistikleri,
               hijyen bayrakları (maske, eksik funding olayları, borsa çapı boşluk)
      durum: durum_turet(gorunum, gunluk) çıktısı (§5.8); yalnız gorunum'dan türetilemez (KC-12)
      HedefKitap: {w*_i, w*T_i, w*C_i, κ^C, q^C*_i, λ, w^C_BTC, bağlayan_tavanlar, tanılar}

    durum_turet(gorunum: PiyasaGorunumu, gunluk: OlayGunlugu, P) -> StratejiDurumu
      gunluk: t'ye kadar yalnız eklemeli olay günlüğü (§5.8): karar kayıtları, gerçek dolumlar, devreden
              emirler, funding nakit kayıtları, NAV yolu, kaçırılan karar kayıtları
      StratejiDurumu: {maske sayaçları, boşluk bayrağı, carry haftası, q^C*_i, β_i, λ geçmişi,
                       son sanal trend ve carry miktarları, s^C son sıfır-dışı payları, mevcut pozisyonlar,
                       nakit, devreden emirler (risk azaltan / artıran sınıfıyla), son yapılan/kaçırılan kararlar}

    bant(hedef: HedefKitap, mevcut: Pozisyonlar, nav: float, fiyat_ref: dict, P) -> BantliHedef

    lot_yuvarlama(bantli: BantliHedef, mevcut: Pozisyonlar, nav, fiyat_ref, filtre: SembolFiltreleri)
        -> EmirNiyetleri
      Δq_i = yuvarla_sifira_dogru((w^b_i·nav/fiyat_ref_i − q_i) / adım_i)·adım_i
      |Δq_i|·fiyat_ref_i < minNotional ise emir yok; istisna: hedef 0 ise tam kapanış (reduce-only)
      Carry BTC hedge bileşeni 1 adımın altındaysa 0 sayılır; sıfırlanan gün sayısı raporlanır (K1-18)

    emir_zinciri(niyetler: EmirNiyetleri, devreden: Devreden, bar_h: SaatlikBar, Q_max: dict,
                 maliyet: MaliyetModeli) -> (Dolumlar, Devreden)
      saat h için: ham_i = min(|kalan_i|, Q_max_i,h / açılış_i)
                   dolum_i = sign·⌊ham_i / adım_i⌋·adım_i       (kısmi dolum adım katına aşağı; K1-18)
                   dolum nominali < minNotional ise dolum 0 (tam kapanışın son parçası hariç)
                   fiyat = açılış_h·(1 ± c_i)
      bar yok ya da hacim 0 → dolum 0

    funding_uzlas(pozisyon_once: Pozisyonlar, kayitlar_T: list, dolgular_T: list, mark_vekili: dict) -> nakit
      nakit_i = −q_i·mark_i·oran_i (q > 0 long; pozitif oranda long öder)

- fiyat_ref_i = karar anındaki son 1h kapanış.
- SembolFiltreleri tek bir anlık görüntüden dondurulmuş tablodur (§9 soru 4; alındı 2026-09-30T01:09:20Z,
  `ciktilar/v8_sembol_filtreleri_20260930_01/`; adım = max(LOT_SIZE, MARKET_LOT_SIZE stepSize), CARRY U-54). Görüntüde olmayan sembollerde adım 0
  (yuvarlama yok) ve minNotional 5 USDT (BANKA §2.3 ile aynı). Bugünkü adımın geçmiş fiyat düzeyine uygulanmasının
  etkisi banka raporunda satır olarak verilir.
- **Hijyen bayrakları girişi (K1-14 için kanca).** Üretim modunda motor bayrakları gorunum'dan kendisi türetir.
  Dış bayrak modunda bayraklar saat damgasıyla dışarıdan verilir ve yeniden türetilmez. Banka rejim-null'u bu modu
  kullanabilir; null tanımı banka ön-kaydındadır.

### 5.2 Olay sırası (her saat sınırı T)
1. **Funding:** T damgalı gerçek uzlaşmalar ve dolgular (§2.6), T'deki hiçbir dolumdan önceki pozisyonla (q(T−)) ve
   mark vekiliyle uygulanır. Gelen gerçek kayıtlar için ters kayıtlar bu adımda işlenir.
2. **Karar (T = 00:00):** gorunum kurulur; varsa aylık evren, sonra haftalık carry, sonra
   `hedef_agirlik → bant → lot_yuvarlama`. Önceki devreden emirler §5.4 öncelik kuralıyla işlenir (yapılan normal
   kararda hepsi iptal edilip yeni niyetle değiştirilir; işlem dışı coinde ve reduce-only rejiminde yalnız risk azaltan
   parçalar korunur). T = 00:00'da dolum yoktur. Karar ve emir olayları günlüğe yazılır (§5.8).
3. **Dolum (T ≥ karar + 1h):** `emir_zinciri` T'de başlayan barın açılışında çalışır. Sanal bacak miktarları 01:00
   açılışında güncellenir.
4. **Değerleme:** barın kapanışında NAV = nakit + Σ q_i·kapanış_i.

Aynı damgada funding ve dolum varsa (1h aralıklı coinlerde 01:00) önce funding eski pozisyona yazılır, sonra dolum
olur. Uzlaşmadan sonra dolan emir o uzlaşmayı ödemez.

### 5.3 Funding muhasebesi
Her gerçek damgada (8h/4h/1h) uygulanır; sabit 8h varsayılmaz. Aralık değişimi arşivden okunur. Eksik kayıt §2.6.
Maskeli ve çıkılamayan pozisyonlar gerçek kayıt ya da bar akışı sürerken dolgu ile funding öder/alır; bar akışı
durunca funding yoktur.

### 5.4 Kısmi dolum ve devreden emir
Katılım sınırı yüzünden dolmayan kalan, sonraki saatlerde aynı kuralla dolmaya devam eder. Devreden miktar ve gecikme
günlük kaydedilir. Maske çıkışlarının maliyeti §6.1.

**Devreden emir öncelik kuralı (KC-12; tek kural, bütün durumlar için).**
- *Sınıflama.* Her devreden emir coin başına iki parçaya ayrılır: **risk azaltan** parça (|q| küçülür, işaret
  değişmez ya da 0'a iner) ve **risk artıran** parça (|q| büyür ya da 0'dan öte işaret değiştirir). İşaret değiştiren
  emir 0'a kadar risk azaltan, 0'dan sonrası risk artıran sayılır.
- *Öncelik sırası (yukarıdaki aşağıdakini geçer):*
  1. **Risk artıran parça iptal** edilir: her günlük karar anında (yapılan ya da kaçırılan), borsa çapı boşlukta
     (reduce-only), işlem dışı coinde (§2.5(d), §3.1) ve maskede. Hiçbir durumda eski bir giriş emri sürmez.
  2. **Reduce-only koruma:** risk azaltan parça, o coin için yeni bir karar üretilemediği durumlarda (kaçırılan karar,
     işlem dışı coin, borsa çapı boşluk) **korunur** ve dolmaya devam eder. Bu durumlarda yeni emir yalnız risk
     azaltıcı olabilir.
  3. **Yeni karar:** o coin için normal bir karar yapıldıysa risk azaltan parça da iptal edilir; yeni niyet gerçekleşmiş
     pozisyondan (devreden dahil değil) yeniden hesaplanır. Yeni niyet reduce-only rejimindeyse |w_yeni| ≤ |w_eski|
     sınırına tabidir.
- Böylece §2.5(d), §2.6, §3.1, §5.2 ve §5.8'deki "korunur" ve "iptal edilir" ifadeleri aynı kuralın dallarıdır:
  korunan yalnız risk azaltan parçadır, iptal edilen her zaman risk artıran parçadır.

### 5.5 Canlı ve geri test (K1-03 ile değişti)
Aynı dört fonksiyon ve aynı `Parametreler` nesnesi kullanılır. Fark yalnız adaptördedir.
- **Geri test:** `emir_zinciri` dolumu saat açılışında simüle eder.
- **Canlı karar:** yalnız `close_time < şimdi` doğrulanmış 00:00 barı ([23:00, 00:00)) ve funding kayıtlarıyla verilir.
  Veri 00:55'e kadar BTC/ETH ya da aday listenin %50'sinden fazlası için tamamlanmazsa karar kaçırılmış sayılır
  (§5.8).
- **Canlı emir zamanı:** ilk emir **01:00:30 UTC'den önce gönderilmez**. Her saat dilimi en fazla Q_max,i,h
  büyüklüğündedir ve saat başı + 30 sn'de gönderilir. Dilim önce post-only limit (10 dakika), dolmayan kısım taker.
  Böylece 1h aralıklı coinlerde 01:00 uzlaşması canlıda da eski pozisyona yazılır.
- **Veri ve emir yolu:** sinyal ve hacim mainnet kamu verisinden, emirler yalnız yetkili demodan. Kaynak kesilirse
  borsa çapı boşluk kuralı (reduce-only) uygulanır. Bu görevde bağlantı yok.
- **Demoda işlem görmeyen sembol:** hedefi 0 olur ve payı yeniden dağıtılmaz; liste demo ön-kaydına yazılır (K1-18).

### 5.6 Parite testi
- **Tanım:** Aynı (gorunum, durum, mevcut pozisyon, nav, L) girdisiyle canlı yol ve geri test yolu aynı HedefKitap'ı
  (ağırlıklarda mutlak fark ≤ 1e-12) ve aynı EmirNiyetleri'ni (miktarlar birebir) üretmelidir.
- **Senaryolar:** (1) kayıtlı canlı anlık görüntülerin tekrar oynatılması; (2) sentetik fikstürler: 8h→4h→1h→8h
  aralık değişimi ve dönüşü, eksik funding ve ters kayıt, delist + uzun funding boşluğu, coine özgü donma, 30 gün
  uzlaşma, borsa çapı boşluk, kısmi dolum ve devreden, adım altı kısmi dolum, adım altı BTC hedge, S1/S2/S4 bağlaması,
  carry blok katsayısı κ^C < 1, band istisnaları, lot altı emir, aylık + haftalık + günlük aynı gün, kaçırılan karar;
  2. tur ekleri: asimetrik carry isim kırpması sonrası yeniden nötrleme ve hedge yeniden kurulumu (Codex KC-04 örneği:
  sonuç yönlü maruziyet 0), hafta içi carry long çıkışı, bantla tutulan isim + λ, PSD olmayan R_çift (Codex KC-13
  örneği) ve kırpma sonrası V'nin tanımlı olması, N_t = 0 ve N_t = 1, devreden emirde risk artıran/azaltan ayrımı
  (işlem dışı coin, borsa çapı boşluk, kaçırılan karar), aynı gorunum'da kaçırılan ve yapılan Pazartesi kararı,
  günlükten durum yeniden kurulumu, T4-a…T4-d denetimleri;
  (3) canlı zaman damgası günlüğü ↔ geri test saat eşlemesi.
- **Bakış-ileri testi:** gorunum'daki bütün verileri t'den sonra bozup HedefKitap'ın değişmediği doğrulanır.
- **İstisnalar (yazılı):** felaket stopu; post-only → taker geçişi; canlı dolum fiyatları; API hata yönetimi.
- Kabul: kritik parite hatası 0.

### 5.7 Gerçekleşen kitap raporu (K1-04)
Hedef kitap tavan değişmezini sağlar (§3.5). Günlük ayrıca raporlanır:
- gerçekleşen + devreden kitabın S1, S2 (B'de S4) ve brüt değerleri; aşım günü oranı ve en büyük aşım;
- "hedefe ulaşılamayan gün" oranı (herhangi bir isimde devreden kalan > 0);
- risk azaltan emirlerin ortalama ve en büyük gecikmesi.

### 5.8 Durum, olay günlüğü ve kaçırılan karar (K1-17, KC-12 ile değişti)
- **Neden günlük gerekir (KC-12).** Haftalık carry miktarı, NAV_karar'a, bantla tutulan eski miktarlara, λ'ya ve
  kararın yapılıp yapılmadığına bağlıdır. Aynı piyasa geçmişinde Pazartesi kararını veren süreç yeni miktarı, kaçıran
  süreç eski miktarı tutar; gorunum bunları ayıramaz. Round-1'deki "durum gorunum geçmişinden türetilir" ifadesi
  yetersizdi ve kaldırıldı.
- **OlayGunlugu.** Yalnız eklemeli, zaman damgalı kayıt dizisi. Her kayıt: tür (karar / kaçırılan karar / emir niyeti /
  dolum / devreden iptal / funding nakdi / ters kayıt / NAV kapanışı), coin, miktar, fiyat, ilgili karar damgası.
  Karar kayıtları HedefKitap'ın tamamını (q^C*, λ, β, κ^C, sanal miktarlar, s^C) içerir. Her kayıt öncekinin
  hash'ini taşır (zincir); böylece sonradan değiştirilemez.
- **durum_turet (§5.1)** saftır: `StratejiDurumu = f(gorunum, gunluk)`. Pozisyon, nakit ve NAV dolum ve funding
  kayıtlarından; carry miktarları ve λ son karar kaydından; maske sayaçları gorunum'dan; devreden emirler niyet − dolum
  − iptal farkından yeniden kurulur.
- **Geri testte** günlük motorun kendi deterministik çıktısıdır; aynı veri + Parametreler + L aynı günlüğü üretir,
  dolayısıyla koşu yine veriden yeniden üretilebilir. **Canlıda** günlük yetkili kayıttır: borsa dolum ve funding
  kayıtlarıyla her karardan önce uzlaştırılır; uyuşmazlıkta borsa kaydı esastır ve fark günlüğe düzeltme kaydı olarak
  eklenir. Kalıcı `durum` nesnesi yalnız önbellektir; her karardan önce `durum_turet` ile yeniden kurulanla
  karşılaştırılır.
- **Kaçırılan planlı karar** (günlük ya da haftalık) yetişme koşusuyla telafi edilmez; günlüğe "kaçırılan karar" kaydı
  düşülür. Sonraki planlı karara kadar yeni risk yoktur. Devreden emirler §5.4 öncelik kuralıyla işlenir: risk artıran
  parçalar kaçırılan karar anında iptal edilir, risk azaltan parçalar korunur. Kaçırılan haftalık carry kararında
  q^C*, β ve λ son karar kaydındaki haliyle sonraki Pazartesi'ye kadar kalır; sonraki günlük kararlar §4.5 adım 0'ı
  (hafta içi çıkış, yeniden nötrleme, hedge yeniden kurulumu) bu eski miktarlarla uygular.
- Geri testte karar kaçmaz; kural sentetik fikstürle sınanır (kaçırılan Pazartesi kararı ile yapılan kararın aynı
  gorunum'da farklı q^C* ürettiği fikstür dahil).

---

## 6. Maliyet modeli (üç belgede tek tanım)

Geri testte bütün dolumlar taker'dır. Maker kazancı yazılmaz (canlı maker ücreti bilgi için: 2 bps).

### 6.1 Taraf başına maliyet

    c_i(k) = ücret + k · m_i · (dilim_i + etki_i)      [bps]
    ücret  = 5 (sabit tarife)
    etki_i = Y · σ_d,i · √(Q / V60_i),  Y = 1
    k      = maliyet çarpanı (§6.2); birincil koşuda 1

- **Dilim** (V60'a göre, karar anında): BTC/ETH 2; ≥ 200M 5; 50–200M 8; 20–50M 15; < 20M (yalnız çıkış) 25.
- **σ_d,i:** karar anındaki günlük σ̂_EWMA,i/√365, bps; karar boyunca sabit (K1-20.9). Q: o saatin dolum nominali.
  V60: günlük medyan hacim.
- **m_i (tek çarpan; K1-05, K1-07):**
  - m_i = 3, dolum maske çıkışıysa;
  - m_i = 3, dolum barında |ln(H/L)|_i > 5·σ_1h,i ya da BTC için |ln(H/L)|_BTC > 4·σ_1h,BTC ise (stres);
  - aksi halde m_i = 1.
  - Koşullar birlikte sağlansa da m_i = 3'tür; çarpılmaz.
  - σ_1h: karar anındaki son 30 günün saatlik log getiri std'si.
  - Gerekçe: v1'deki ölçüt dolum gününün gün sonunda bilinen getirisine bakıyordu. Yeni ölçüt dolum barının kendi
    hareketine bağlıdır. Yalnız maliyete girer, karara girmez. Bar aralığının ortalaması ~1,6σ olduğundan eşikler,
    v1'deki getiri eşiklerinin (4σ coin, 3σ BTC) nadirliğine yakın kalmak için bir birim yükseltildi. Bu bir Brownian
    aritmetiğidir; D'ye bakılmadı.
- Delist uzlaşması §1c (h_L %10, h_S %5; senaryolar %50, %90).

### 6.2 Maliyet çarpanı: tek tanım ve tek yöntem (K1-06; ana oturum notu 3)
- **Tanım.** Maliyet çarpanı k ∈ {1, 2, 3} yalnız **dilim + etki** terimine uygulanır. **Ücret sabit kalır** (5 bps),
  çünkü bilinen bir tarifedir. Stres/maske çarpanı m_i ayrıca uygulanır. Örnek: BTC'de normal dolum k = 3'te
  5 + 3·2 = 11 bps; 50–200M altta 5 + 3·8 = 29 bps (etki hariç).
- **Yöntem.** Her k değeri **ayrı ve tam bir koşudur**. Karar kuralları aynıdır; NAV yolu, dolayısıyla miktarlar,
  karekök terimi ve katılım sınırı koşuya göre değişir. Yeniden fiyatlama yapılmaz.
- Aynı tanım ve yöntem carry kapısında (K6/K7) ve bankada (B3, R1) kullanılır. CARRY ve BANKA bu bölüme atıf yapar.
- Maliyet çarpanı koşuları ve delist senaryo koşuları aynı şartnamenin yeniden koşusudur; deneme sayılmaz.

### 6.3 NAV ızgarası
NAV: 0,1M / 1M / 5M USDT. Katılım sınırı ve karekök terimi NAV'a bağlıdır; her NAV ayrı koşulur. Birincil NAV önerisi
0,1M; banka ön-kaydında dondurulur (§9 soru 3). 1M ve 5M satırları kapasite satırıdır.

### 6.4 Gecikme maliyeti (K1-08)
Karekök terimi katılım sınırı yüzünden yapısal olarak küçüktür: Q ≤ 0,001·V60/24 olduğundan √(Q/V60) ≤ 0,0065; alt
için etki ≲ 3–4 bps. Kapasite asıl olarak gecikmede görünür. Bu yüzden her NAV için bir **katılımsız gölge yol**
koşulur: aynı kararlar, Q_max = ∞, aynı maliyet modeli. Gecikme maliyeti = NAV(gölge yol) − NAV(gerçek yol), yıllık
bps olarak raporlanır. Karekök teriminin ima ettiği ortalama bps de raporlanır. Gölge yol betimseldir, deneme sayılmaz.

### 6.5 Funding
§5.3. Long pozitif oranda öder, short alır; BTC hedge'inin funding'i dahil.

---

## 7. Parametre tablosu

Görülmüş etiketi üç kademelidir (K2-12):
- **Hayır:** D'den ve D özetlerini görmüş kaynaklardan bağımsız (literatür, borsa mekaniği, aritmetik, kullanıcı kararı).
- **Zayıf:** D özetlerini (P&L değil) görmüş bir tasarımcı ya da jüriden geldi; D istatistiğine doğrudan dayanmıyor.
- **Evet:** değer D özetleri görüldükten sonra seçildi ya da doğrudan bir D istatistiğine dayanıyor.

Hiçbiri D P&L'ine göre ayarlanmadı; D P&L'i hesaplanmadı.

| Parametre | Değer / dondurma kuralı | Kaynak | Görülmüş |
|---|---|---|---|
| Trend ufukları | 14, 42, 84 gün | codex | Evet (RAPOR okunduktan sonra) |
| Sinyal biçimi | tanh, eşit ağırlık | codex | Hayır |
| σ̂_EWMA yarı ömürleri | 20, 90 gün; max | risk | Zayıf |
| σ tabanı (trend) | %20 | codex | Zayıf |
| σ̂ tahmincisi | EWMA; HAR yalnız §1b kuralıyla | KARARLAR, ml | Evet (HAR QLIKE üstünlüğü görüldü) |
| HAR katsayıları | D içinde yürüyen aylık; banka/canlı için tam-D OLS | ml, K1-12 | Evet |
| HAR ŝ² | yürüyen artıkların son 52 haftası, en az 8 | bu belge | Hayır |
| QLIKE bağlayıcı eşikleri | (i) 0,95; (iv) blok 4 hafta, 2.000 çekiş, tohum 20260927 | ml + bu belge | Hayır |
| QLIKE hedefi | sonraki 7 günün günlük getiri kareleri | K1-12 | Evet (VR(5) < 1 gerekçesi) |
| τ (birim) | %15 | KARARLAR | Hayır |
| M_max | 1,5 | kâr jürisi | Zayıf |
| R̂ harmanı | 0,5 örnek + 0,5·ρ0,7 | risk, ml | Evet (0,7 > D'deki 0,58/0,64) |
| R_EW yarı ömür | 90 gün | risk | Zayıf |
| Eksik çift ρ | 0,7 | bu belge | Hayır |
| R_EW PSD düzeltmesi | özdeğer kırpma, ε = 10⁻⁸, birim köşegene yeniden ölçek | KC-13 | Hayır (sayısal; sayılmaz) |
| N (trend) | 15 (BTC/ETH + 13) | cta | Evet (24 coin ≥ 50M görüldü) |
| Giriş/kalış sırası | 15 / 20 | cta | Zayıf |
| Hacim tabanı | 20M, V60 | cta | Evet (likidite dağılımı) |
| Isınma | 90 gün; coin ve koşu başına; D'de T0 2023-10-01 | codex | Hayır |
| Donma (a), (b), (d) | 7g/90g %10; 6 bar; > 8h | cta | Evet (33 bayraklı coin görüldü) |
| Donma (c) | 16 saat mutlak | K1-01 | Hayır (borsa mekaniği) |
| Maskeden dönüş | aylık seçim + 30 temiz gün | codex kırmızı takım | Zayıf |
| Borsa çapı eşik | aday listenin %50'si | bu belge | Hayır |
| Eksik funding | Δ varsayılanı 8h; tespit 1,5·Δ; r_taban %0,01/8h saatlik | K1-01, KARARLAR | Evet (aralık geçişlerinin varlığı) |
| Delist uzlaşma | long −%10, short +%5; 30 gün | carry uygulama jürisi | Zayıf |
| İsim tavanları | BTC/ETH %35; alt long %6; alt short %4 | risk | Evet (+%103 p90, eşzamanlılık 0,52/0,39) |
| Brüt | 2,0 | carry | Zayıf |
| S1 şoku | alt −%70, BTC/ETH −%30; sınır %20 | codex, risk | Evet (10/10 fitili −%67; ETH o gün −%22, en kötü tek gün −%27,5 ayrı olaydır) |
| S2 şoku | +%100 tek; +%50 diğer; +%25 BTC/ETH; sınır %20 | KARARLAR, risk | Evet (p90 +%103; medyan +%42) |
| Band | %20·|w*|, %0,2 NAV | codex | Zayıf |
| Katılım | min(%0,1·30g, %0,1·7g medyan saatlik, %10·önceki saat) | codex, mikroyapi, K1-05 | Hayır |
| Ücret | 5 bps | Aşama 1 | Hayır |
| Slipaj dilimleri | 2/5/8/15/25 bps | cta | Zayıf |
| Karekök Y | 1 | literatür | Hayır |
| Stres çarpanı | ×3; bar aralığı 5σ_1h coin, 4σ_1h BTC; σ_1h 30 gün | cta, K1-07 | Hayır |
| Maske çıkış çarpanı | ×3 (stresle çarpılmaz) | ml, K1-05 | Hayır |
| Maliyet çarpanı | k ∈ {1,2,3}, yalnız dilim + etki; tam koşu | KARARLAR, K1-06 | Hayır |
| Felaket stopu | 4 × ATR14, yalnız canlı | prop | Hayır |
| Canlı emir zamanı | ilk emir ≥ 01:00:30; dilim saat başı + 30 sn; post-only 10 dk | K1-03 | Hayır |
| **Carry (yalnız B)** | | | |
| F30 penceresi | 30 gün, yalnız gerçek kayıt | carry | Zayıf |
| σ tabanı (carry) | %30 | carry | Zayıf |
| Bacak kesimleri | %30 / medyan | carry | Hayır (Fama-French 30/40/30) |
| Nötrleme regresörleri | R30, s^trend, β | carry + jüriler | Evet (R30 D'den sonra eklendi) |
| β büzülmesi, pencere | 0,5; 60 gün | carry | Zayıf |
| Long funding tabanı | −%50, mevcut long'a da | carry | Evet (D'de biten 4 coin −%41…−%56) |
| Carry evreni | 20M giriş / 10M çıkış; 50M altı yarım tavan | carry | Zayıf |
| Genişlik | 15 / 10 | carry | Zayıf |
| Carry isim tavanları | short %1,0; long %1,5 | bu belge | Hayır |
| Haftalık band | %25, isim başına alt miktarı; κ^C için bant yok (günlük, doğrudan) | carry, KC-03 | Zayıf |
| Alt sepeti yeniden nötrleme | ağır bacak λ ile; Pazartesi ve hafta içi çıkışta | KC-04 | Hayır (sayılmaz; serbest sabit yok) |
| BTC hedge | günlük, o günkü gerçek alt sepetinden; β haftalık | KC-04 | Hayır |
| ω_C | 0,20 | bu belge (§1d) | Zayıf (jüri önselleri) |
| Carry ölçekleme | τ / max(Σ̂, Σ₀ vol) | K1-10 | Hayır |
| S4 | tek short +%300; sınır %10 ⇒ net alt short ≤ %3,33 | kâr jürisi, carry kırmızı takım | Hayır |

**Serbestlik sayımı.**
- Getiriyi doğrudan biçimlendiren (A): ufuklar 3, σ yarı ömrü 2, σ tabanı 1, N 1, sıra eşikleri 2, hacim tabanı 1 → **10**.
- Risk ve tavan (A): τ, M_max, harman 2, R_EW, S1 3, S2 4, isim tavanı 3, brüt → **16**. V ≤ τ değişmezdir, sayılmaz.
  PSD düzeltmesi (ε), toplam risk kuralı (τ, ω_C, L'den türetilir), yeniden nötrleme ve günlük hedge yeniden kurulumu
  serbest sabit getirmez; sayılmaz (2. tur).
- İcra ve maliyet (A): band 2, katılım 4, ücret 1, dilim 5, Y 1, stres 4 (çarpan, iki eşik, σ_1h penceresi), maske
  çıkışı 1 → **18**.
- Veri hijyeni (A): ısınma 1, donma 4, dönüş 1, borsa eşiği 1, delist 3, eksik çift ρ 1, eksik funding 3 → **14**.
- A toplamı **58** sabit; optimize edilen **0**. HAR seçilirse +4 öğrenilmiş katsayı ve ŝ².
- Carry (B ek): F30, σ tabanı, kesimler 2, nötrleme 3, β 2, long tabanı, evren 3, genişlik 2, isim tavanı 2, band, ω,
  S4 2 → **+21**; B toplamı **79**.
- v1'e göre artış (51 → 58) muhasebe ve icra sabitlerinin açık yazılmasındandır; getiriyi biçimlendiren çekirdek
  yine 10'dur.

---

## 8. Kapsam dışı bırakılanlar

| Öğe | Neden |
|---|---|
| RRB çarpanları (K, Π, m_L/m_S) | Yön/zamanlama tercihi; D'de sınanamaz; kapanmış aileleri açar |
| Kaskad hasadı, H2 | Sağ kuyruğu keser; eşik D sayımlarından; n < 30 |
| Mikroyapı / uzlaşma döngüsü kolu | 1h veriyle ölçülemez; `OLDURUCU`; 1m veri onayı yok |
| G ve K4 artık kolları, K2 | D'nin aynası; ayrı ön-kayıt ve deneme sayacı gerekir |
| risk K3 | FTN ile değiştirildi |
| ML çıkış kuralı | Bakış-ileri (`OLDURUCU`); §1c ile değiştirildi |
| HAR'ın otomatik girişi | Yalnız §1b prosedürüyle, kilitten önce |
| g > 1 zayıf sinyal büyütmesi | Codex ilkesi |
| 24 saatlik RV tabanı | Kırılım gününde dışbükeyliği tıraşlar |
| Funding boyut çarpanı / kalabalık kesintisi | Funding ailesini yeniden açar; funding yalnız P&L |
| 7 günlük pencere, CTA çekirdeği | Yalnız betimsel; bankaya önerilmez (§1a, K2-08) |
| Donchian ikinci sinyali | Aynı hipotez; deneme şişirir |
| DD çarpanı | Çekirdek dışı; bankaya önerilmez (§3.5, K2-08) |
| Carry %30–35 otomatik bütçe | KARARLAR §2 |
| Short Donchian vetosu (carry) | Ek serbestlik; S4 ve isim tavanı yerine konur |
| TWAP 02:00–05:00 icrası | Birincil dolum 01:00 açılışı; maliyet stresi kapsar |
| Spot bacağı, metrics verisi | Kullanıcı kararı (V8_PLAN) |
| `islem_disi_supheli` maskesi | Ex-post bayrak |

---

## 9. Bilinen zaaflar ve açık sorular

**Zaaflar.**
1. **Önsel D ile gerilimli.** D'de doğrusal momentum yok (|r| < 0,025). Trend önseli literatürden gelir; bankayı
   geçmek önseli büyük ölçüde yeniden ölçer.
2. **Gerçekleşen vol birimin altında.** §3.3 tanımıyla %7–11 önseldir (ölçülmedi); sinyal gücüyle dalgalanır.
   Referans kitabın kendisi de M > M_max ya da tavan bağladığında %15'in altındadır (KC-14). Kelly tablosu
   gerçekleşen vol'e dayanmalıdır.
3. **Şok tavanları kaldıraçla bağlar.** Birim kitabın brütü tam sinyalde ~%20–25'tir. L ≈ 1,5 üstünde S1 sık bağlar.
   B'de bu durumda önce trend bacağı küçülür (§4.5); carry bloğu ancak sonra küçülür.
4. **Korelasyon kuyrukta eksik tahmin edilir.** R̂ harmanı bunu azaltır, gidermez (`ml` bulgusu: gerçekleşen/öngörülen
   vol q99 2,36; görülmüş bilgi).
5. **Mark vekili.** 1h kapanış mark'tan sapabilir; funding hatası küçük ama ölçülemez.
6. **Tarihsel sembol filtreleri yok.** Tek anlık görüntü kullanılır.
7. **ADL ve marjin modellenmedi.** Yalnız hedge kredisiz şok bunu dolaylı karşılar.
8. **D evreni de hayatta kalan yanlıdır.** GELISTIRME_EVRENI dönem içinde listelenenleri içermez.
9. **01:00 dolumu kalabalık saattir.** Canlı emir 01:00:30'da başlar; maliyet stresi (2×, 3×) bunu kapsamak zorundadır.
10. **Carry kapısının gücü düşük.** T0'dan sonra ~33 ay; carry kitabı ~15–40 isim.
11. **B'nin bankadaki seyreltme bedeli** (§1d): SR_C < ~0,16·SR_T ise B, A'dan düşük Sharpe verir.
12. **Kapasite gecikmede görünür** (§6.4); maliyet ızgarası tek başına kapasiteyi göstermez.

**Açık sorular (hepsi kilit adımı 1'de, D'de P&L üreten ilk koşudan önce yanıtlanır; §10).** **Hepsi yanıtlandı** (`ACIK_SORU_YANITLARI.md`: 1 → #2, 2 → #3, 3 → #4, 4 → #5, 5 → #6, 6 → #7, 7 → #1).
1. **Birim risk yorumu.** §3.3 hedefi tam sinyal referans kitabına koyar (Codex ilkesiyle uyumlu). Diğer seçenek:
   gerçek kitabı %15'e getiren, yukarı çarpanı ≤ 1,5 olan portföy çarpanı; bu seçenek zayıf sinyali 1,5 kata kadar
   büyütür. Belge birinciyi önerir.
2. **DD çarpanı.** Çekirdeğe alınmadı; %30 sınırı kaldıraç seçimine bırakıldı. Kabul ediliyor mu?
3. **Birincil NAV.** 0,1M önerildi; canlı demo ~5.000 USDT. Değişsin mi?
4. **Sembol filtre anlık görüntüsü** için kamu `exchangeInfo` okumasına onay.
5. **REV1 ile korelasyon raporu** için REV1'in D dönemi günlük getiri serisi v8 değerlendiricisine verilebilir mi?
   (E3 Z2 verisi yasak kalır.)
6. **S4 yalnız B'de.** A'ya da uygulanması istenirse A'da alt short tavanı %4'ten %3,33'e iner.
7. ~~**Kapı mı, kapısız A mı?**~~ **Yanıtlandı (27 Eylül, `ASAMA4B_KARAR.md` §1):** kapı → A/B kalır. §11.

---

## 10. Ön-kayıt kilidi ve sıra (K2-01, K1-13; ana oturum notu 1)

Bu sıra üç belgede (MIMARI, CARRY_KAPISI, BANKA_ONKAYIT) aynı adlarla yazılır.

**Kural.** Bütün açık kullanıcı soruları yanıtlanır; HAR seçimi, carry kapısı ön-kaydı ve banka ön-kaydı, D'deki
**ilk P&L üreten koşudan önce** birlikte hash'lenir. **D P&L'i görüldükten sonra hiçbir eşik, ölçüt ya da parametre
değişmez; D sonucu ne çıkarsa çıksın.**

| Kilit adımı | İş | P&L görülür mü |
|---|---|---|
| 0 | Motor yazımı; sentetik fikstürlerle parite, bakış-ileri ve muhasebe testleri. D verisi yalnız metrik hesaplanmayan kısa kesitlerle (biçim ve özdeşlik denetimi) | Hayır |
| 1 | Üç belgenin bütün açık kullanıcı soruları yanıtlanır (MIMARI §9, CARRY_KAPISI §13, BANKA_ONKAYIT §11); yanıtlar `ACIK_SORU_YANITLARI.md` | Hayır |
| 2 | HAR/EWMA seçimi koşulur (§1b; P&L'siz, QLIKE); sonuç hash'lenir | Hayır |
| 3 | Sentetik kalibrasyon (BANKA_ONKAYIT §3.7; D ve banka verisi kullanmaz) | Hayır |
| 4 | **ÖN-KAYIT KİLİDİ:** MIMARI parametre dosyası, HAR seçim sonucu, CARRY_KAPISI ön-kaydı, BANKA_ONKAYIT ön-kaydı, açık soru yanıtları ve kalibrasyon çıktısı birlikte hash'lenir (`KILIT.json`); hash ve deneme defteri satırları uzak depoya itilir | Hayır |
| 5 | İlk P&L üreten koşu: carry kapısı (D). Kapı kararı ve kapı ölçütleri açık; trend performans çıktıları mühürlü (yalnız hash) | Yalnız kapı ölçütleri |
| 6 | D doğrulaması ve banka kuru koşusu: performans çıktıları mühürlü, yalnız hash ve denetim çıktıları raporlanır | Hayır (yalnız hash) |
| 7 | Dondurma (`DONDURMA.json`) | Hayır |
| 8 | Banka açılışı (BANKA_ONKAYIT §2) | Banka hükmü |

- Kilit adımı 4'ten önce D'de tam dönem strateji P&L'i üreten hiçbir koşu yapılmaz.
- Adım 5–6'nın performans çıktıları banka hükmü açılana kadar yalnız hash olarak tutulur (BANKA_ONKAYIT §1.3); dondurmada açılmaz.
- Adım 5 ya da 6'da motor hatası çıkarsa düzeltme yalnız sentetik fikstürle gösterilen hata için yapılır; eşik ve
  parametre değişmez. Düzeltme ve kararı etkileme kuralları CARRY_KAPISI ve BANKA_ONKAYIT'tadır.

---

## 11. KARAR_DEGISIKLIGI_ONERISI — "kapısız A" (KAPANDI: kapı → A/B, karar kesinleşti)

**Karar (27 Eylül, `ASAMA4B_KARAR.md` §1.1).** Kullanıcı seçenek (a)'yı seçti: **kapı → A/B kalır**; kapısız A
seçilmedi. Carry kapısı Codex'in KC-03/04/05/06/07 bulgularıyla düzeltilerek korunur (KC-04 bu belgede, §4.4–§4.5).
Bu karar bağlayıcıdır; revizörler değiştiremez. Aynı kararın ikinci maddesi (DSR tek sabit eşik değil, kilitten önce
yazılan kalibre σ_SR duyarlılık tablosu) BANKA_ONKAYIT'ın alanıdır; MIMARI'de DSR eşiği yoktur ve bu karara aykırı
bir ifade içermez. Aşağıdaki metin kararın tarihsel gerekçe kaydıdır; soru artık açık değildir (§9 soru 7).

Bu bölüm bağlayıcı kararı (ONKAYIT §2: kapı → A/B) **değiştirmedi**. Kırmızı takım 2'nin (K2-03) gösterdiği bedel
kullanıcıya sayıyla sunuldu.

**Gerekçeler.**
1. **Kapının gücü düşük.** CARRY_KAPISI v1 §7'ye göre kapı funding gelirinin varlığını iyi, fiyat bileşeninin etkisini
   kötü ölçer. K2-02'ye göre kararı fiilen D'deki net carry P&L'inin işareti verir.
2. **B bankada bütün olarak yargılanır.** B seçilirse A'nın sonucu hükme girmez (bağlayıcı karar). Yanlış kabulün asıl
   bedeli, iyi bir trendin carry yüzünden RET yemesidir.
3. **Seyreltme sayısı (§1d).** ρ = 0, σ_T = %9, σ_C = %3 iken SR_C = 0'lık carry portföy Sharpe'ını ~%5, SR_C = −0,3
   olan carry %16–24 düşürür. Başa baş SR_C* ≈ 0,16·SR_T'dir. Banka ölçütleri 0,5–0,8 aralığındaki bir Sharpe çıtasına
   yakın işlediği için bu fark hükmü değiştirebilir.
4. **Kazanç da gerçek.** SR_C = +0,3 olan carry portföy Sharpe'ını %6–14 artırır. Jüriler carry'yi tek savunulabilir
   bağımsız kol olarak gördü.
5. **Carry'nin banka dönemindeki davranışına dair hiçbir varsayım gerekçe olarak kullanılmadı** (ONKAYIT §6; K2-06).

**Seçenekler.**
- **(a) Mevcut karar:** kapı → A/B, ω_C = 0,20. **Seçildi (27 Eylül).**
- **(b) Kapısız A:** bankaya yalnız A gider. Carry kapısı koşulmaz ya da yalnız betimsel araştırma olarak koşulur ve
  kararı etkilemez. Carry ileri dönemde ayrı hipotez, ayrı ön-kayıt ve ayrı deneme olarak gelir. §4 tarif olarak kalır,
  nihai mimaride devre dışıdır.
- **(c) Kapı + daha sıkı karar:** kapı kalır; K1 eşiği seyreltmeyi karşılayacak sabit bir değere çekilir ya da ω_C
  küçültülür (§1d duyarlılığı). Eşik CARRY_KAPISI'nın alanıdır ve kilitten önce, D P&L'ine bakılmadan dondurulur.

---

## 12. ARAYUZ_DEGISIKLIGI

v1 metinleri ortak referanstır. Aşağıdaki arayüz noktaları bu revizyonda değişti. Parametre adları (τ, M_max, ω_C, L,
NAV, h_L, h_S, T0) değişmedi.

1. **Maliyet çarpanı (§6.2).** Çarpan yalnız dilim + etkiye uygulanır, ücret sabit; her çarpan ayrı tam koşudur.
   CARRY v1 §2 "yeniden fiyatlama, NAV geri beslemesi yok" ve BANKA v1 B3 "ücret dahil" okumaları bu tanıma bağlanır.
2. **Net tavan çözücüsü (§4.5).** Önce trend bacağı küçülür; carry tek blok κ^C ile küçülür. CARRY v1 §4.1'deki "net
   tavan küçültmesi (aynı katsayı)" yerine κ^C geçer.
3. **S4 (§4.5).** Sayısal olarak aynı; B'de net alt short isim tavanı %3,33 olarak isim-tavanı adımında uygulanır.
4. **Sanal bacaklar ve V4 bölmesi (§4.7).** Sanal carry = κ^C × haftalık miktar; sanal trend = trend bileşeninin kendi
   bandından geçmiş hedefi; icra artığı s^C_i payıyla bölünür. CARRY V4 bu A^C'yi kullanır.
5. **Carry haftalık sabit büyüklüğü (§4.4):** miktar (CARRY v1 §4.1 varsayımı onaylandı).
6. **Carry ölçeklemesi (§4.4):** max(Σ̂, Σ₀) ile.
7. **Eksik funding (§2.6) ve donma (c) (§2.5):** Δ_i kuralı, saatlik en kötü oran, ters kayıt, bar akışı durunca tahakkuk
   yok, (c) = 16 saat. Kural adları aynı; CARRY v1 §3 atıfları geçerli.
8. **Katılım sınırı (§3.7)** ve **stres çarpanı (§6.1)** yeni formüllerle.
9. **HAR (§1b):** D koşularında yürüyen katsayı; hedef günlük getiri kareleri; (ii)/(iii) betimsel; deneme defteri satırı
   varyant 2.
10. **Isınma (§2.4):** coin ve koşu başına; pencere başına yeniden ısınma yok (BANKA v1 §3.1 sürekli koşusuyla uyumlu).
11. **Tavan değişmezi (§3.5):** hedef kitapta; gerçekleşen kitap §5.7'de rapor (BANKA T4 ve R5 için).
12. **Betimsel banka satırları:** MIMARI, CTA çekirdeğini ve DD çarpanı ablasyonunu bankaya önermez; koşulursa çıktı
    ileri demo kararına kadar yalnız hash (BANKA R8).
13. **Kilit sırası (§10):** adım adları ve sırası üç belgede ortaktır.
14. **Hijyen bayrakları girişi (§5.1):** banka rejim-null'u için dış bayrak modu.

**2. tur (Aşama 4b) arayüz değişiklikleri.**

15. **Carry sırası ve hedge (§4.3–§4.5; KC-04).** BTC hedge Pazartesi'de sabitlenmez; her gün isim tavanı, bant,
    maske ve yeniden nötrleme sonrası o günkü gerçek alt sepetinden yeniden kurulur. Alt sepeti dolar-nötrlüğü ağır
    bacak λ ile korunur. Dolar nötrlüğü alt sepetine, beta nötrlüğü carry bloğuna aittir. CARRY §3.3, §5.1 ve V1
    fikstürleri bu sıraya bağlanır.
16. **Carry miktar güncellemesi (§4.4; KC-03 mimari tarafı).** Alt miktarları haftalık %25 bantla; carry katkısı
    günlük κ^C ile **doğrudan** (κ bandı yok). CARRY §5.1 madde 3'teki "%25 göreli κ bandı" bu tanımla değiştirilmelidir.
    Sanal carry hedge'i günlük değişir.
17. **Bant yalnız trend bileşenine (§4.5 adım 5).** Round-1'deki net-ağırlık bandı kaldırıldı; net hedef = bantlı
    trend + κ^C·carry bloğu.
18. **İcra artığı payı (§4.7).** Sıfır/sıfır durumunda son sıfır-dışı pay; pay, günün 01:00'da geçerli sanal
    miktarlarıyla hesaplanır ve [01:00, ertesi 01:00) saatlerine uygulanır. CARRY §5.6'daki "0,5" bu fonksiyonla
    değiştirilmelidir.
19. **T4 nesne tablosu (§3.5; KC-09 mimari tarafı).** T4-a birim trend (V ≤ τ), T4-b carry birimi (V ≤ τ), T4-c carry
    bloğu (V ≤ ω_C·L·τ), T4-d kaldıraçlı net hedef (tavanlar + toplam risk V ≤ L·(1 + ω_C·𝟙_B)·τ); gerçekleşen defter
    yalnız rapor. BANKA T4 bu adları kullanır.
20. **Durum ve olay günlüğü (§5.1, §5.8; KC-12).** `durum_turet(gorunum, gunluk)`; StratejiDurumu yalnız gorunum'dan
    türetilmez. Devreden emir öncelik kuralı §5.4.
21. **R_EW (§3.2; KC-13).** Çift bazlı ham korelasyon + özdeğer kırpma ile PSD düzeltmesi; boş evren dalı.

---

## 13. Kırmızı takım bulgularının işlenişi

| Bulgu | Düzey | Karar | Nerede / gerekçe |
|---|---|---|---|
| K1-01 | CIDDI | DUZELTILDI | §2.5(c) 16 saat mutlak; §2.6 Δ_i, saatlik en kötü oran, ters kayıt |
| K1-02 | CIDDI | DUZELTILDI | §1c.4–5, §2.6, §2.7, §5.3: bar akışı durunca funding yok; 30 gün beklemede tahakkuk yok; parite fikstürü §5.6 |
| K1-03 | CIDDI | DUZELTILDI | §5.5: ilk emir ≥ 01:00:30, saatlik dilim ≤ Q_max, kapanmış bar doğrulaması; §5.6 zaman eşlemesi |
| K1-04 | CIDDI | DUZELTILDI | §3.5 tavan değişmezi hedef kitapta; §5.7 gerçekleşen kitap raporu. T4 metni BANKA'da |
| K1-05 | CIDDI | DUZELTILDI | §3.7 Q_max = min(30g, 7g, %10 önceki saat); §6.1 m_i tek çarpan, maske çıkışı stresle çarpılmaz |
| K1-06 | CIDDI | DUZELTILDI | §6.2 tek tanım (ücret sabit, çarpan dilim + etki) ve tek yöntem (tam koşu); §12.1 |
| K1-07 | DUZELTILEBILIR | DUZELTILDI | §6.1: stres ölçütü dolum barının aralığına bağlandı; eşikler 5σ/4σ (aralık-getiri farkı) |
| K1-08 | DUZELTILEBILIR | DUZELTILDI | §6.4 katılımsız gölge yol ve gecikme maliyeti; banka R1'e eklenmesi BANKA'nın işi |
| K1-09 | CIDDI | DUZELTILDI | §4.4 miktar sabit; §4.5 trend-önce çözücü, carry tek blok κ^C; §4.7 sanal bacak = çözücü çıktısı, V4 bölmesi dondu |
| K1-10 | DUZELTILEBILIR | DUZELTILDI | §4.4.1 carry ölçeği max(Σ̂, Σ₀) |
| K1-11 | DUZELTILEBILIR | DUZELTILDI | §3.3: V ≤ τ değişmez (sayımdan çıktı); M_max KARARLAR gereği tutuldu, seyrek bağladığı yazıldı |
| K1-12 | DUZELTILEBILIR | DUZELTILDI | §1b: D'de yürüyen katsayı, ŝ² 52 hafta PIT, hedef günlük getiri kareleri |
| K1-13 | CIDDI | DUZELTILDI | §10 kilit sırası (açık sorular → HAR → kilit → kapı → kuru koşu; kuru koşu yalnız hash). Kuru koşu ayrıntısı BANKA'da |
| K1-14 | CIDDI | KISMEN | §5.1 dış hijyen bayrağı modu (motor kancası). Null yolunun tanımı ve değişmezleri BANKA'nın alanı |
| K1-15 | DUZELTILEBILIR | ilgisiz | BANKA §2.3 (Z2 funding kaynağı) |
| K1-16 | DUZELTILEBILIR | ilgisiz | BANKA §8.1 (anonim kimlik) |
| K1-17 | DUZELTILEBILIR | DUZELTILDI | §5.8 durum geçmişten türetilir; kaçırılan karar telafi edilmez |
| K1-18 | CIDDI | DUZELTILDI | §5.1 kısmi dolum adım katına, adım altı hedge 0 ve rapor; §5.5 demoda olmayan sembol 0. Demo NAV parite koşusu BANKA'da (R) |
| K1-19 | DUZELTILEBILIR | DUZELTILDI | §3.8 closePosition, referans, yeniden kurma, yeniden giriş, duyarlılık satırı |
| K1-20 | DUZELTILEBILIR | KISMEN | 1 §2.2; 2–3 §3.1; 4 §4.5; 5 §4.3; 6 §4.4; 7 §2.6; 8 §2.1; 9 §6.1; 10 §4.2; 13 §4.7. 11, 12, 14 BANKA'nın alanı (ilgisiz) |
| K2-01 | CIDDI | DUZELTILDI | §10 ön-kayıt kilidi; §9 açık sorulara son tarih (kilit adımı 1) |
| K2-02 | CIDDI | ilgisiz | CARRY_KAPISI ölçütleri. §11'de gerekçe 1 olarak kullanıldı |
| K2-03 | CIDDI | KISMEN | §1d gerekçe portföy Sharpe'ıyla yeniden yazıldı; kapısız A §11'de KARAR_DEGISIKLIGI_ONERISI. Ana kural (kapı → A/B) bağlayıcı karar gereği değişmedi |
| K2-04 | CIDDI | ilgisiz | BANKA DSR / σ_SR |
| K2-05 | CIDDI | ilgisiz | BANKA ölçüt kalibrasyonu |
| K2-06 | CIDDI | ilgisiz | BANKA eşik gerekçesi. MIMARI denetlendi: banka dönemine dayalı eşik ya da parametre yok (§11.5) |
| K2-07 | CIDDI | ilgisiz | BANKA/CARRY hata yönetimi |
| K2-08 | CIDDI | DUZELTILDI | §1a, §3.5: CTA çekirdeği ve DD ablasyonu bankaya önerilmez; koşulursa yalnız hash. L seçimi kırpması BANKA'da |
| K2-09 | DUZELTILEBILIR | ilgisiz | BANKA B9 |
| K2-10 | DUZELTILEBILIR | DUZELTILDI | §1b.6: (ii) ve (iii) betimsel; bağlayıcı (i) ve (iv) |
| K2-11 | DUZELTILEBILIR | KISMEN | §2.6 ve §4.2 F30 yalnız gerçek kayıt; §4.7 V4 bölme formülü. K8 yöntemi ve NW gecikmesi CARRY'de |
| K2-12 | DUZELTILEBILIR | DUZELTILDI | §7 üç kademeli etiket; §1a gerekçe 3 ve §1d.5 görülmüş diye işaretlendi |
| K2-13 | DUZELTILEBILIR | ilgisiz | BANKA −%90 sıklığı |
| K2-14 | DUZELTILEBILIR | ilgisiz | BANKA rejim-null |
| K2-15 | YOK | ilgisiz | Eylem gerekmez; MIMARI'de coin adı yalnız BTC/ETH |

**Belgeler arası notlar.** CARRY v1 §10'daki altı açıklama isteğinin hepsi yanıtlandı: s^trend bütün carry adaylarında
(§4.2); dolgu F30'a girmez (§2.6); haftalık sabit büyüklük miktar (§4.4); V4 bölmesi (§4.7); S4 satırı yerinde (§4.5);
carry ex-ante vol ≤ %3 (§1d). BANKA v1 Ek A'daki ısınma çelişkisi §2.4'te, S4 yerleşimi §2.3/§4.5'te giderildi.

**KARAR_DEGISIKLIGI_ONERISI özeti.** Tek öneri §11'dedir (kapısız A); kullanıcı 27 Eylül'de reddetti, kapı → A/B
kesinleşti. KARARLAR §2'deki teknik kararlar uygulandı; hiçbiri bu revizyonla değişmedi.

### Codex bulgularının işlenişi (2. tur)

| Bulgu | Düzey | Karar | Nerede / gerekçe |
|---|---|---|---|
| KC-01 | OLDURUCU | ilgisiz | Öteki belgede işlendi (BANKA §3.5, B7). MIMARI kancası §5.1 dış bayrak modu değişmedi |
| KC-02 | CIDDI | ilgisiz | Öteki belgede işlendi (BANKA §3.7) |
| KC-03 | CIDDI | ilgisiz | Öteki belgede işlendi (CARRY §5.1/§5.6). Mimari tarafı: §4.4 tek güncelleme kuralı (alt miktarı haftalık %25 bant, carry katkısı günlük κ doğrudan, κ bandı yok); §4.7 sıfır/sıfır payı ve zaman damgası tek fonksiyon; §12 madde 16, 18 |
| KC-04 | CIDDI | DUZELTILDI | §4.3 nötrlüklerin sahibi (dolar → alt sepeti, beta → carry bloğu, net kitap nötr değil); §4.4 sıra: ölçek → bütçe → isim tavanı → bant → λ ile yeniden dolar-nötrleme; §4.5 adım 0: BTC hedge her gün kırpma/bant/maske sonrası gerçek alt sepetinden yeniden kurulur, κ bloğun tamamına; adım 5 bant yalnız trende. Codex örneği (+%1,5/−%1) yönlü maruziyet 0 verir; hafta içi çıkışta karşı bacak λ ile küçülür |
| KC-05 | CIDDI | ilgisiz | Öteki belgede işlendi (CARRY V4). §4.5 adım 5 (bant yalnız trende) artığın bir kaynağını kaldırır |
| KC-06 | CIDDI | ilgisiz | Öteki belgede işlendi (CARRY) |
| KC-07 | CIDDI | ilgisiz | Öteki belgede işlendi (CARRY §8.4, BANKA §9). §1d tablosu ρ = 0 varsayımıyla bilgi olarak kaldı |
| KC-08 | CIDDI | ilgisiz | Öteki belgede işlendi (BANKA §3.3; ASAMA4B_KARAR §1.2). MIMARI'de DSR eşiği yok |
| KC-09 | CIDDI | DUZELTILDI (mimari tarafı) | §3.5 T4 nesne tablosu: V ≤ τ yalnız birim trend (T4-a) ve carry birimi (T4-b); carry bloğu V ≤ ω_C·L·τ (T4-c); kaldıraçlı net hedefte tavanlar + toplam risk V ≤ L·(1 + ω_C·𝟙_B)·τ (T4-d); gerçekleşen defter yalnız rapor. Banka T4 metni BANKA'da |
| KC-10 | CIDDI | ilgisiz | Öteki belgede işlendi (BANKA §4, §7.1) |
| KC-11 | CIDDI | ilgisiz | Öteki belgede işlendi (BANKA §5) |
| KC-12 | CIDDI | DUZELTILDI | §5.1 `durum_turet(gorunum, gunluk)` ve StratejiDurumu alanları; §5.8 yalnız eklemeli, hash zincirli OlayGunlugu (karar, dolum, funding, NAV, kaçırılan karar); geri testte motor çıktısı, canlıda borsa kaydıyla uzlaşan yetkili kayıt. §5.4 devreden emir önceliği: risk artıran parça her zaman iptal > risk azaltan parça karar üretilemeyen durumda reduce-only korunur > yeni kararda tümü yeniden hesaplanır. §2.5(d), §2.6, §3.1, §5.2 bu kurala bağlandı |
| KC-13 | CIDDI | DUZELTILDI | §3.2: ortak gün kümesi, eksik getiri (0 değil), sıfır merkezleme, aynı kümede varyanslar (|ρ| ≤ 1); R_çift özdeğer kırpma (ε = 10⁻⁸) + birim köşegene ölçek ⇒ R_EW PSD; harman en küçük özdeğer ≥ 0,15. Codex karşı örneği oluşamaz. N = 0 ve N = 1 dalları §3.2, §3.3 adım 8 |
| KC-14 | DUZELTILEBILIR | DUZELTILDI | §3.3 Yorum: referans vol = τ·min(1, M_max/M); "çarpan ve tavanlar izin verdiğinde %15"; Codex sayısı (%14,1) yazıldı; %7–11 yalnız önsel (§0, §9 zaaf 2 de güncellendi) |
