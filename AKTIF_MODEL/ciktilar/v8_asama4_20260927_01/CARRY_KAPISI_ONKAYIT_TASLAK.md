# Carry uydusu D içi kapısı: ön-kayıt taslağı

Durum: **KİLİT ADAYI (1 Ekim 2026, 4.02).** Bütün açık sorular `ACIK_SORU_YANITLARI.md`'de yanıtlı; Adım 3 (kalibrasyon) kapandı. Koşulmadı: D'de P&L üretilmedi. Kilitten (`KILIT.json`) sonra eşik, ölçüt ve parametre değişmez. İçerik: 2. tur (Aşama 4b-2) + §15 uygulama netleştirmeleri (30 Eylül). Kullanıcı kararı (ASAMA4B_KARAR §1): kapı → A/B kalır.

Tarih: 2026-09-27. Yazan: Aşama 4 carry kapısı revizörü (Opus). Girdi taslak: `calisma/CARRY_KAPISI_v1.md`.
Dayanak: `girdi/` altındaki 17 dosya, `calisma/MIMARI_v1.md`, `calisma/BANKA_ONKAYIT_v1.md`, `calisma/KIRMIZI_1.md`,
`calisma/KIRMIZI_2.md`. 2. tur dayanağı: `CODEX_KIRMIZI_TAKIMI.md` (KC-03, KC-05, KC-06, KC-07; KC-09'un carry
tarafı), `ASAMA4B_KARAR.md`, `codex_cagrilari/20260927T_saclik_yanit.md`. Round-1 nihai hali
`_arsiv/V8_ASAMA4_SENTEZ_20260927_01/round1_nihai/` altındadır.

**Kapı koşulmadı.** Geri test, veri hesabı ve performans ölçümü yapılmadı. Aşağıdaki sayılar belgelerdeki
sabitlerle yapılmış kaba aritmetiktir, ölçüm değildir. Ekonomik kabul NOT_EVALUATED. Banka içeriği ve banka
dönemine dayanan eşik yoktur. Coin adı yalnız BTC/ETH için geçer.

Bağlayıcı çerçeve (ONKAYIT §2): Kapıyı geçerse nihai mimari **B** olur (trend ve sabit bütçeli carry uydusu).
Geçemezse **A** olur (yalnız trend). A ile B bankada yarışmaz. Kapı tek atıştır; ana deneme sayısı 1'dir.

---

## 0. v1'den farklar (özet)

*(Tarihsel özet; buradaki sayılar bağlayıcı değildir. Güncel eşikler §6.3 ve §15'tir.)*

1. Ortak **ön-kayıt kilidi** eklendi (§2). Kilit, D'de P&L üreten ilk koşudan önce vurulur. Kapının trend
   çıktısı artık bağlayıcı biçimde mühürlüdür (K2-01, K1-13).
2. Tavan çözücüsünde carry **tek blok** olarak ölçeklenir ve önce trend küçülür. Sanal bacak, çözücünün
   çıktısıyla tanımlanır (K1-09). Bu bir ARAYUZ_DEGISIKLIGI'dir (§11).
3. Fiyat bahsi için faktör testi **K11** eklendi. K4'ün en küçük saptanabilir etkisi sayıyla yazıldı (K2-02).
4. K1 eşiği 0'dan **0,10**'a çıktı. Gerekçe artık bankadaki seyreltme aritmetiğidir (K2-03).
5. Hüküm **kör** açılır. Hüküm açıldıktan sonra bulunan hata sonucu yalnız A'ya çevirebilir (K2-07).
6. Maliyet çarpanı MIMARI §6'daki tek tanıma bağlandı. 2× ve 3× tam yeniden koşudur (K1-06).
7. Newey-West gecikmesi {4, 12} olarak hesaplanır; her ölçütte B aleyhine olan kullanılır. V4 bölme formülü
   ve K8 yöntemi şimdi yazıldı (K2-11).
8. Kapı içinde HAR, tam-D katsayısıyla değil yürüyen aylık katsayılarla çalışır (K1-12).
9. "Kapısız A" seçeneği kullanıcıya sayılarla sunuldu. Kullanıcı 27 Eylül'de kapı → A/B'yi seçti (§12).

### 0.1 Round-1'den farklar (2. tur, Codex bulguları)
1. **Tek sanal defter (KC-03).** Kapı kendi sanal carry kitabını kurmaz. MIMARI §4.4–§4.7'nin günlük κ^C'li sanal
   carry miktarını ve sıfır/sıfır artık kuralını birebir okur. Kapıya özgü "%25 κ bandı" kaldırıldı; yalnız tanı
   olarak raporlanır (§5.1). Yeni geçerlilik koşulu V5: kapı defteri = motor defteri.
2. **V4 yol sınırı (KC-05).** V4 artık `|Σ Aᶜ|` değil `Σ|Aᶜ_w|`'yi sınırlar. Haftalık tekil sapmaya ayrı sınır
   (V4b) eklendi. SR tabanlı ölçütler gerçekleşen icra artığı dahil seriyle de geçmelidir (§6.3, "çift seri").
3. **Eşdeğerlik (KC-06).** K11 ve K9 eşdeğerlik (TOST / kesişim-birleşim) testine çevrildi; toleranslar ekonomik
   gerekçeyle, D'ye bakmadan konuldu. Fiyat ortalaması için ekonomik olarak anlamlı bir tolerans D'de
   sınanamaz (fizibilite aritmetiği §8.3). Bu yüzden K3/K4'ün bağlayıcı rolü **fiyat kazancı kredilenmez**
   kuralına devredildi: SR tabanlı ölçütler fiyat kazancını saymaz, fiyat kaybını sayar. K3/K4 TOST'u raporlanır.
4. **Korelasyonlu başabaş (KC-07).** K1 eşiği sabit 0,10 değil, gözlenen ρ'nun üst güven sınırına bağlı bir
   formüldür: 0,14–0,37 aralığında (§6.4, §8.4). Tavan etkileşimi için V6 eklendi.
5. **Hata olasılıkları (KC-06).** §8.2 ve §8.5'teki sayılar kaba, tek ölçütlü normal yaklaşımlardır; olasılık
   iddiası değildir. Bileşik oranlar kilitten önce sentetik fikstürle ölçülür (§8.5).
6. **Carry birimi değişmezi (KC-09 carry tarafı).** V1'e carry birimi ve carry katkısı denetimi eklendi.

---

## 1. Hipotez ve kapının amacı

**Amaç.** Carry uydusunun D'deki getirisinin kaynağını ayırmak: funding geliri mi, fiyat bileşeni mi? Uydu,
trendden bağımsız bir risk primi olarak mimariye girer. Getirisi gizli bir fiyat bahsinden geliyorsa bağımsız
kol değildir. Funding geliri fiyat kaybıyla siliniyorsa da işe yaramaz.

**H1 (B'yi destekler).** Carry bacağı maliyet sonrası pozitif getiri üretir ve bu getiri, fiyat kazancı hiç
sayılmadan, yalnız funding eksi maliyet ile (fiyat kaybı düşülerek) bankadaki başabaş eşiğini aşar. Bilinen fiyat
faktörlerine yüklemesi önceden dondurulmuş ekonomik toleransın içindedir (eşdeğerlik). Bacak BTC'ye ve alt
sepetine karşı tolerans içinde nötrdür, trend bacağıyla korelasyonu sınırlıdır.

**H0 (A'yı destekler).** Şunlardan en az biri doğrudur:
- H0a: Funding geliri maliyeti anlamlı biçimde aşmaz.
- H0b: Fiyat bileşeni funding gelirini siler.
- H0c: Net getiri fiyat bileşeninden gelir. Ortalama olarak (kredilenme kuralı, K1/K6/K8) ya da faktör
  yüklemesi olarak (K11).
- H0d: Bacak nötr değildir (K9, K10).

**Anlamsızlık kanıt değildir (KC-06).** "Fiyat bileşeni sıfırdan anlamlı ayrışmıyor" ifadesi fiyat riskinin
yokluğunu göstermez; yüksek belirsizlikte kendiliğinden sağlanır. Bu belgede hiçbir bağlayıcı ölçüt
anlamsızlıkla geçilmez. Nötrlük iddiaları eşdeğerlik (güven aralığı toleransın içinde) biçimindedir. Fiyat
ortalaması için eşdeğerlik D'de sınanamadığından (§8.3) kapı onu kanıtlamaya çalışmaz; fiyat kazancını karar
serisinden dışlar.

**Kapının niteliği.** Bu bir *yanlışlama elemesidir*, kenar kanıtı değildir. Gücü düşüktür (§8). D içindeki
kapı bir geliştirme/seçim işlemidir; bağımsız örneklem dışı kanıt değildir (Codex canlı yanıtı, S-a c).

---

## 2. Ön-kayıt kilidi ve sıra (üç belgede ortak)

Ana oturum notu (1) ile K2-01 ve K1-13'ün ortak önerisi uygulanır. Sıra ve adlar üç belgede aynıdır.

| Adım | Ad | İçerik | P&L üretir mi |
|---|---|---|---|
| 0 | Motor ve parite testleri | MIMARI §5.6 testleri. Yalnız sentetik fikstürler ve metrik hesaplamayan kısa D kesitleri | Hayır |
| 1 | Açık soruların kapanışı | Üç belgedeki bütün açık kullanıcı soruları yanıtlanır (`ACIK_SORU_YANITLARI.md`) | Hayır |
| 2 | HAR/EWMA seçimi | MIMARI §1b prosedürü koşulur. P&L'sizdir. Sonuç hash'lenir | Hayır |
| 3 | Sentetik kalibrasyon | BANKA_ONKAYIT §3.7; D ve banka verisi kullanmaz | Hayır |
| 4 | **ÖN-KAYIT KİLİDİ** | MIMARI (parametre dosyası dahil), HAR seçim sonucu, bu kapı ön-kaydı, banka ön-kaydı, açık soru yanıtları ve kalibrasyon çıktısı **birlikte** hash'lenir (`KILIT.json`). Kilit kaydı uzak depoya itilir. Deneme defterine kapı satırı girer | Hayır |
| 5 | Carry kapısı koşusu | Bu belge. **D'de P&L üreten ilk koşu.** Sonuç A ya da B | Evet (trend satırları mühürlü) |
| 6 | D doğrulama ve kuru koşu | Performans çıktıları mühürlü; yalnız hash ve denetim çıktıları | Evet (mühürlü) |
| 7 | Banka dondurması | `DONDURMA.json` (BANKA ön-kaydı) | Hayır |
| 8 | Banka açılışı | Tek atış | Evet (banka) |

**Bağlayıcı cümle.** D'de P&L görüldükten sonra hiçbir eşik, ölçüt, parametre ya da ölçüt kümesi değişmez.
D sonucu ne çıkarsa çıksın bu geçerlidir.

**Kilitten önce yasak olanlar.** D'de tam dönem strateji P&L'i üreten koşu. Kısa D kesitlerindeki motor
testleri Sharpe, getiri ya da bileşen ortalaması hesaplamaz; yalnız özdeşlik ve biçim denetler.

**Kapının trend çıktısı.** Kapı koşusu trend bacağının D P&L'ini de üretir. Kapı yalnız K10 için trend haftalık
getirisini içeride kullanır ve yalnız korelasyonu raporlar. Trend satırları ayrı dosyaya yazılır. Bu dosyanın
yalnız hash'i raporlanır ve banka hükmü açılana kadar açılmaz (BANKA_ONKAYIT §1.3). Bu kural artık açık soru değil, bağlayıcıdır.

---

## 3. Test edilen nesne

### 3.1 Nesne ve koşu biçimi
- **Nesne:** MIMARI'nin nihai halindeki mimari B'nin carry bacağı, birebir. Bütün sabitler MIMARI parametre
  tablosundaki değerlerdir. Kapı içinde hiçbir parametre değişmez.
- **Koşu biçimi:** Tam B motoru koşulur: trend ve carry, ortak net defter, ortak tavanlar. Carry bacağı ayrı
  koşulamaz, çünkü nötrleme trend sinyalini kullanır ve tavanlar net kitaba uygulanır.
- **Kaldıraç:** L = 1.
- **NAV:** Banka ön-kaydının birincil NAV'ı. Varsayılan 0,1M USDT (MIMARI §6 önerisi). Değer Adım 4'te (kilit) kilitlenir.

### 3.2 Kapının dayandığı carry kuralları (MIMARI §4'e ek açıklık)
Bunlar MIMARI v1'de açık kalan noktalardır (K1-20). Kapı bu okumaları kullanır:
1. s^trend, bütün carry adayları için §3.1 formülüyle hesaplanır. Aday trend evreninde olmasa da.
2. Long şartı F30_i ≥ −%50, her haftalık kararda bütün long'lara uygulanır, mevcut long'lar dahil. Şartı
   kaybeden long hedefi 0 olur.
3. Carry %25 bandı isim başınadır ve yalnız Pazartesi'nin haftalık miktarına (q^C*) uygulanır. Tanım MIMARI
   §4.4 madde 5'tir; bu belge tekrar tanımlamaz. Günlük κ^C bu banda tabi değildir (§5.1).
4. F30 yalnız gerçek funding kayıtlarıyla hesaplanır. Doldurulan kayıtlar skora girmez (§4.2).

### 3.3 Tavan çözücüsünde bacak önceliği (ARAYUZ_DEGISIKLIGI 1)
**Bağlayıcı tanım MIMARI §4.3–§4.5'tir** (2. turda MIMARI revizörü hedge'in kırpma sonrası yeniden hesaplanmasını
da orada düzenler, KC-04). Aşağıdaki özet yalnız okuma kolaylığı içindir; MIMARI ile çelişirse MIMARI geçerlidir ve
kapı MIMARI'nin çözücüsünü sınar. K1-09'a göre, v1'deki "tavan küçültmesi bir coinde iki bacağı aynı katsayıyla
küçültür" kuralı carry'nin dolar-nötrlüğünü ve beta hedge'ini bozar. Kapı şu çözücüyü sınar:

1. Net kitap: w_i = w^T_i + κ_C·w^C_i. Burada w^C_i, carry isim tavanlarından geçmiş, ω_C ve L uygulanmış carry
   katkısıdır. κ_C ∈ [0, 1], başlangıç 1.
2. Her tavan adımında (isim → brüt → S1 → S2 → B'de S4) küçültme önce **trend bacağına** uygulanır. Kapsam
   MIMARI'nin o adımdaki kapsamıdır: isim tavanında o ismin trend katkısı, S1'de trend long tarafı, S2'de trend
   short tarafı, brütte bütün trend.
3. Katsayı c, ihlali gideren en büyük c ∈ [0, 1] değeridir. İkiye bölme ile bulunur. Kayıp fonksiyonları
   (Σ max(0, c·w^T_i + w^C_i) ve benzerleri) c'de dışbükeydir; c = 0'da carry katkısı tavanın içindeyse çözüm
   vardır.
4. c = 0'da ihlal sürerse **carry bloğu** tek katsayı κ_C ile küçülür. Bütün carry isimleri ve BTC hedge'i aynı
   κ_C ile. Böylece dolar-nötrlük ve hedge oranı korunur.
5. Tur sınırı ve son çare MIMARI §3.5 ile aynıdır.
6. Günlük κ_C, trend katsayıları ve bağlayan tavan kaydedilir.

**Gerekçe.** (a) Carry bloğu içindeki oranlar hiç değişmez; carry nötrlüğü tavandan etkilenmez. (b) Trend
bacağını küçültmek net uzun (ya da kısa) maruziyeti tekdüze azaltır. Carry bloğunu küçültmek ise tekdüze
değildir: carry short'u küçülünce o coinde net long büyüyebilir. (c) KARARLAR §2'deki "sabit carry bütçesi"
korunur; ω_C ancak trend payı tükenince küçülür. Bedeli: tavan bağladığında B'nin trend bacağı A'nınkinden
küçük olur. Bu fark B−A ayrıştırmasında görünür ve raporlanır.

L = 1'de carry uzun brütü yaklaşık 0,1–0,14 NAV beklenir. S1 kaybı yaklaşık 0,07–0,10 eder, yani sınırın
(0,20) altındadır. κ_C < 1 beklenen durum değildir; sıklığı raporlanır.

### 3.4 σ̂ tahmincisi
- Adım 2'deki HAR/EWMA sonucu kullanılır.
- HAR seçildiyse kapı, D'nin tamamında tahmin edilmiş katsayıları **kullanmaz** (K1-12 i). Her ayın ilk günü,
  yalnız o güne kadar hedefi tamamlanmış gözlemlerle tahmin edilen yürüyen katsayılar kullanılır. Yöntem MIMARI
  §1b'deki yürüyen tahminle aynıdır.
- O ay için ≥30 tamamlanmış haftalık gözlem (hafta sayısı; coin-hafta değil) yoksa o ay σ̂_EWMA kullanılır.
- Tam-D katsayıları yalnız banka ve canlı içindir.

### 3.5 Varyant yok
Tasarımdaki ablasyonlar (nötrlemesiz, σ'suz skor, aylık karar) kapıda koşulmaz. Sonradan betimsel koşulursa her
biri ayrı defter satırıdır ve kararı değiştiremez.

### 3.6 Deneme sayacı ve sayım kuralı
- **Defter satırı:** Adım 4'te (kilit), koşudan önce: `A4-carry-kapisi`, aile "kesitsel funding taşıma", varyant 1, kapsam D
  (T0 → 2026-07-01). HAR prosedürü ayrı satırdır (adı MIMARI'de).
- **Sayım kuralı** (K2-09, üç belgede önerilen): Alternatif şartname N'ye girer. Aynı şartnamenin alt kümesi ya
  da ölçek koşusu girmez. Bu yüzden şunlar varyant değildir:
  - maliyet çarpanı 2× ve 3× koşuları,
  - K8 yeniden koşusu (6 isim çıkarılmış aday listesi),
  - delist uzlaşma senaryoları (h_L %50, %90).
- **Teknik yeniden koşu** (§7.3) sayacı 2 yapar ve deftere ayrı satır girer.
- **Maliyet çarpanı:** Tanım MIMARI §6'daki tek tanımdır (ana oturum notu 3, K1-06). Bu belge tanımı tekrar
  etmez. m_c ∈ {1, 2, 3} olarak anılır. Yöntem: MIMARI §6 yöntem belirtiyorsa o; belirtmiyorsa **tam yeniden
  koşu** (karekök terimi ve katılım NAV yoluna bağlıdır).

### 3.7 Dondurma
Motor kodu, parametre nesnesi, veri hash'leri (ilk indirme) ve Adım 2 sonucu koşudan önce hash'lenir. Karar, koşu
betiği tarafından mekanik olarak üretilir (§7).

---

## 4. Veri

### 4.1 Dönem, evren, ısınma
- **Dönem:** Yalnız D = [2023-07-01, 2026-07-01) UTC. D öncesinden veri alınmaz.
- **Evren:** `GELISTIRME_EVRENI.json` (120 alt ve BTC/ETH). Carry adayları MIMARI §4.1 kuralıyla PIT seçilir.
  ETH carry'de kullanılmaz. BTC yalnız hedge'dir.
- **Isınma:** MIMARI §2.4. Değerlendirme başlangıcı T0 = 2023-10-01 00:00 UTC. İlk carry kararı 2023-10-02
  00:00 UTC (Pazartesi). T0 öncesinde işlem ve metrik yoktur.
- **Değerlendirme birimleri:**
  - Hafta: Pazartesi 00:00 → sonraki Pazartesi 00:00. 2023-10-02 → 2026-06-29: **n_w = 143** tam hafta.
    Kalan iki gün toplam P&L'e girer, haftalık istatistiğe girmez.
  - Ay: UTC takvim ayı, 2023-10 → 2026-06: **n_m = 33**.
  - Çeyrek: 11 adet. n < 30 olduğu için yalnız betimsel.

### 4.2 Funding kuralları (kapının asgari gereksinimi)
K1-01 ve K1-02 funding muhasebesinde iki artefakt buldu. Metin MIMARI §2.5–§2.6'dadır; MIMARI revizörü
düzeltir. Kapı, MIMARI'nin nihai kuralının en az şunları sağlamasını gerektirir:
1. **Beklenen aralık:** son 30 günde gözlenen en uzun funding aralığı. Kayıt yoksa 8 saat.
2. **Eksik kayıt:** beklenen aralığın 1,5 katı sonra hâlâ kayıt yoksa eklenir.
3. **Donma ölçütü (c):** mutlak eşik, 16 saat (2 × 8 saat) funding kaydı yok.
4. **En kötü oran:** son 30 günün en kötü oranı önce saatlik orana çevrilir, sonra doldurulan damganın aralık
   saatiyle çarpılır.
5. **F30:** yalnız gerçek kayıtlarla. Doldurulan kayıtlar yalnız P&L'e girer.
6. Doldurulan kayıt sayısı ve funding tutarı bacak ve isim bazında raporlanır.

Görülmüş bilgi: aralık geçişlerinin varlığı (Aşama 1 §2.10). 8 saat eşiği borsa mekaniğinden gelir.

### 4.3 Delist, donma, çıkış
- MIMARI §1c, §2.5, §2.7 geçerlidir. Maske yeni riski keser. Pozisyon gerçekleşebilir dolumla ya da 30 gün sonra
  uzlaşmayla kapanır: long son kapanış × (1 − h_L), short son kapanış × (1 + h_S). Taban h_L = %10, h_S = %5.
  Senaryolar h_L = %50 ve %90.
- **Delist sonrası tahakkuk yok** (K1-02). Funding tahakkuku coinin son barında durur. 30 günlük bekleme
  süresinde funding yazılmaz. Kapı bunu gerektirir; metin MIMARI'dedir.
- Maske çıkışlarında katılım sınırı ve slipaj MIMARI'nin nihai tanımıyla (K1-05: Q_max'ın 7 günlük ve önceki
  saat hacmiyle sınırlanması; ×3 slipajın tek sefer uygulanması).
- `islem_disi_supheli` hiçbir kurala girmez.

### 4.4 Diğer
- **Mark vekili:** uzlaşma damgası T için [T−1h, T) barının kapanışı (MIMARI §2.1).
- **Borsa çapı boşluk:** MIMARI §2.6, reduce-only.

---

## 5. P&L ayrıştırma formülleri

### 5.1 Sanal carry bacağı: tek defter, tek güncelleme kuralı (ARAYUZ_DEGISIKLIGI 2; KC-03)
**Kural.** Kapının sınadığı carry, mimarinin uyguladığı carry ile **aynı nesnedir**. Kapı betiği sanal carry
kitabını kendisi kurmaz. Motorun MIMARI §4.7 muhasebesinin ürettiği sanal miktarları, P&L satırlarını ve icra
artığı paylarını okur. Tanımlar yalnız MIMARI'dedir; bu belge onları tekrar icat etmez:

| Öğe | Tek tanım |
|---|---|
| Haftalık carry miktarı q^C*_i ve %25 haftalık bant | MIMARI §4.4 madde 4–5 |
| Günlük carry blok katsayısı κ^C_t | MIMARI §4.5 madde 2–4 |
| Sanal carry miktarı q^C,v_i = κ_etkin,t · q^C*_i (BTC hedge dahil; κ_etkin güvenlik ölçeklemelerini içerir, bağlamadıklarında κ^C_t'dir) | MIMARI §4.7 |
| Sanal trend miktarı q^T,v_i | MIMARI §4.7 |
| Geçerlilik anı: kararın 1 saat sonrası, 01:00 barının açılışı | MIMARI §4.7, §5.2 |
| İcra artığı, carry payı s^C_i ve sıfır/sıfır durumu | MIMARI §4.7 (§5.6'ya bakınız) |

Bu belgede q^C_i yazılan her yerde q^C,v_i kastedilir.

**Sonuçlar.**
- κ^C_t her gün doğrudan uygulanır. Round-1'deki "κ_C göreli değişimi %25'i aşarsa ölçekle" kuralı kaldırıldı.
  Codex'in örneğinde (κ 1 → 0,8) sanal carry miktarı aynı gün %20 küçülür; motor ile kapı aynı miktarı taşır.
- %25 bandı yalnız Pazartesi haftalık miktarına (q^C*) uygulanır; iki belgede aynı formüldür.
- Maske ya da evren çıkışında q^C*_i = 0 (MIMARI §4.4 madde 4).
- Sanal bacak katılım sınırına tabi değildir. Gerçek pozisyonla fark icra artığına gider; V4 ve çift seri
  kuralı (§6.3) ile sınırlanır.
- **Tanı (bağlayıcı değil).** κ^C_t'nin bir önceki güne göre göreli değişiminin %25'i aştığı gün sayısı ve
  round-1'deki bantlı kuralın bu defterden izleme farkı raporlanır. Karar serilerine girmez.

**Tek fonksiyon şartı.** Sıfır durumu, zaman damgası ve artık dağıtımı motorda tek bir fonksiyonla hesaplanır
(MIMARI §4.7). Kapı betiği bu fonksiyonun çıktısını kullanır; aynı kuralın ikinci bir uygulaması yazılmaz. V5
(§6.1) bunu denetler.

### 5.2 Satırlar (her saat h, her isim i)

Funding (her damga T):

    F^alt_T = Σ_{i∈alt} −q^C_i(T−) · m_i(T) · ρ_i(T)
    F^hdg_T = −q^C_BTC(T−) · m_BTC(T) · ρ_BTC(T)

ρ oran, m mark vekili, q > 0 long. Pozitif oranda long öder, short alır.

Fiyat (h barı; güncelleme saatinde eski miktar close_{h−1} → open_h, yeni miktar open_h → close_h):

    P^alt_h = Σ_{i∈alt} [ q^C,eski_i·(open_h − close_{h−1}) + q^C,yeni_i·(close_h − open_h) ]
    P^hdg_h = aynı formül, BTC için

Maliyet (bacağın kendi sanal dolumları):

    C_h = Σ_i |Δq^C_i| · open_h · c_i / 10⁴

c_i, MIMARI §6 modelidir. Karekök teriminde Q, bacağın kendi dolum nominalidir.

Bileşenler:

    F = F^alt + F^hdg      (funding)
    P = P^alt + P^hdg      (fiyat, hedge dahil)
    N = F + P − C          (carry net)

**Netleme kazancı carry'ye yazılmaz.** MIMARI §4.7'deki "netleme kazancı" ve "icra artığı" ayrı raporlanır.
Kapı ölçütleri N'yi kullanır. Bu muhafazakâr bir seçimdir. MIMARI §4.7'nin "Carry hedge" satırı burada ikiye
bölünür: hedge funding F'ye, hedge fiyatı P'ye girer.

### 5.3 Ölçek

    r^X_w = Σ_{h∈w} X_h / (ω_C · L · NAV_{w başı}),   X ∈ {F, P, C, N}

Sharpe ölçekten bağımsızdır. Beta ve MDD bu carry birim ölçeğinde okunur.

### 5.4 Olay sırası (MIMARI §5.2 ile aynı)
Her saat sınırı T:
1. Funding: T damgalı uzlaşmalar, T'deki dolumlardan önceki miktarla (q(T−)) yazılır.
2. Karar (00:00): aylık evren (ayın 1'i) → haftalık carry (Pazartesi) → günlük trend → çözücü (§3.3) → bant →
   lot. Önceki devreden emirler iptal edilir. 00:00'da dolum yoktur.
3. Dolum (≥ 01:00): gerçek net emirler katılım sınırıyla dolar. Sanal miktarlar 01:00 açılışında güncellenir.
4. Değerleme: bar kapanışında.

Aynı damgada funding ve dolum varsa önce funding eski miktara yazılır.

### 5.5 Uzlaşma özdeşliği
Her gün:

    ΔNAV = trend satırları + (F + P − C) + netleme kazancı + icra artığı

Özdeşlik 1e-8 NAV içinde tutmalıdır (V2).

### 5.6 İcra artığının bacaklara bölünmesi (V4 ve çift seri için)
**Tek tanım MIMARI §4.7'dir** (artık miktar e_i = q_i − q^T,v_i − q^C,v_i; A_i, e_i'nin fiyat + funding P&L'i; carry
payı s^C_i günlük karar anında hesaplanır ve o gün sabittir; A^C_t = Σ_i s^C_i·A_i,t). Round-1'deki π ve "0/0 → 0,5"
kuralı kaldırıldı; kapı MIMARI'nin sıfır/sıfır kuralını birebir kullanır (bugünkü metinde s^C_i = 0). MIMARI bu kuralı
değiştirirse kapı yeni kuralı kullanır; iki belgede iki kural olamaz. *(30 Eylül: MIMARI §4.7 güncel kuralı sıfır/sıfır
isim-gününde son sıfır olmayan s^C payını taşır; kapı onu kullanır — §15 madde 4.)*

**Sıfır/sıfır tanısı (bağlayıcı değil).** İki sanal miktarın 0 olduğu isim-günlerde gerçekleşen artık P&L'in
toplamı, mutlak toplamı ve bu günlerin önceki son sıfır olmayan s^C_i ile carry'ye düşecek karşılığı ayrıca
raporlanır. Gerekçe: carry maske çıkışında sanal miktar hemen 0 olur, gerçek pozisyon katılım sınırıyla geç
kapanır; bu kayıp s^C = 0 kuralında trende yazılır ve carry'yi iyi gösterir. Kapı bu yönü MIMARI revizörüne
arayüz notu olarak iletir (§11): "son sıfır olmayan payın taşınması" daha muhafazakârdır. Karar MIMARI'nindir.

**Haftalık toplama ve carry birim ölçeği.**

    A^C_w = Σ_{t∈w} A^C_t,    a^C_w = A^C_w / (ω_C · L · NAV_{w başı})

**Gerçekleşen carry serisi (çift seri kuralı için):**

    r^{N,g}_w = r^N_w + a^C_w

r^N sanal defterin carry net getirisi, r^{N,g} icra artığının carry payı eklenmiş gerçekleşen karşılığıdır.

---

## 6. Kapı ölçütleri

### 6.1 Geçerlilik koşulları (biri sağlanmazsa sonuç A)

| Kod | Koşul |
|---|---|
| V1 | MIMARI §5.6 parite ve bakış-ileri testleri Adım 0'da geçmiş, kritik hata 0. Fikstürler en az şunları içerir: 1h→8h ve 4h→8h aralık dönüşü (K1-01), delist ve uzun funding boşluğu (K1-02), S1/S2 bağlarken carry bloğunun tek katsayıyla küçülmesi (§3.3), günlük κ^C'nin sanal carry miktarına aynı gün yansıması (κ 1 → 0,8 örneği, KC-03), iki sanal bacak sıfırken taşınan gerçek pozisyonun artığının MIMARI §4.7 kuralıyla dağılması (KC-03), zıt işaretli haftalık artıklar (+100/−100, KC-05; V4a ve V4b'nin reddettiği gösterilir). **Carry birimi denetimi (KC-09 carry tarafı):** her Pazartesi carry birim kitabının ex-ante vol'ü ölçekleme sonrası ve isim tavanları öncesi τ = %15'e eşit (1e-9), isim tavanları sonrası ≤ τ; ω_C·L uygulanmış carry katkısının ex-ante vol'ü ≤ ω_C·L·τ. Bu denetim carry birimi nesnesine aittir; trend birimi, kaldıraçlı net hedef ve gerçekleşen defter için T4 tanımları BANKA/MIMARI'dedir |
| V2 | §5.5 uzlaşma özdeşliği her gün tutuyor |
| V3 | Carry kitabının sıfır olduğu (n_C < 10) hafta payı ≤ %25; aktif hafta ≥ 108/143 |
| V4a | **Mutlak artık toplamı:** Σ_w \|a^C_w\| ≤ 0,10 · Σ_w \|r^N_w\|. Mutlak değerlerin toplamıdır; zıt işaretli artıklar birbirini silmez (KC-05) |
| V4b | **Haftalık yol sapması:** her hafta ayrı ayrı \|a^C_w\| ≤ 1,0 · sd(r^N_w). Tek bir haftadaki büyük sapma (ör. maske çıkışında geç kapanan pozisyon) sanal defterin o haftayı temsil etmediğini gösterir |
| V5 | **Tek defter (KC-03):** kapının kullandığı q^C,v, κ^C_t ve s^C serileri motorun MIMARI §4.7 çıktısıyla her gün birebir aynı (mutlak fark ≤ 1e-12). Kapı betiği bu serileri yeniden hesaplamaz; denetim, aynı serinin motor günlüğünden bağımsız okunmasıyla yapılır |
| V6 | **Tavan etkileşimi (KC-07):** B'nin trend bacağının net hedefi (w^T*) A'nın aynı gündeki trend hedefinden farklı olan gün oranı ≤ %10. A'nın hedefi yalnız `hedef_agirlik` ile, P&L üretmeden hesaplanır. Aşılırsa "B = A + carry" varsayımı ve §8.4 seyreltme formülü geçersizdir |

V4a veya V4b aşılırsa sanal bacak gerçek pozisyonu temsil etmiyor sayılır ve sonuç A olur.

### 6.2 İstatistik tanımları
- **SR** = ortalama(r_w) / std(r_w) · √52.
- **Kredilenen Sharpe (KC-06; fiyat kazancı kredilenmez):**

      SR^K(r) = [ ortalama(r^F − r^C) + min(ortalama(r^P), 0) + ortalama(a) ] / std(r) · √52

  r ∈ {r^N, r^{N,g}}; a = 0 sanal seride, a = a^C gerçekleşen seride (§5.6). Fiyat bileşeninin ortalaması pozitifse
  sıfır sayılır, negatifse düşülür. Payda tam serinin oynaklığıdır; fiyat riski riskte sayılır, getiride sayılmaz.
  Böylece B'nin geçişi fiyat ortalamasından gelen kazanca hiçbir koşulda dayanamaz. Codex'in KC-06 örneğinde
  (funding − maliyet %1, fiyat %3, vol %15, birim ölçek) SR^K ≈ 0,07'dir; K1'i geçemez.
- **NW t ve NW standart hatası:** Newey-West, Bartlett çekirdeği. Gecikme ℓ ∈ {4, 12} hafta; ikisi de hesaplanır.
  - ℓ = 4: ⌊4·(143/100)^{2/9}⌋.
  - ℓ = 12: 84 gün (~3 ay); funding sırasının 30–90 günlük kalıcılığını kapsar (görülmüş bilgi, K2-11).
  - **Seçim kuralı: her ölçütte B aleyhine olan kullanılır.** Anlamlılık isteyen ölçütte (K2, K7) ve eşdeğerlik
    isteyen ölçütte (K9, K11; betimsel K3/K4) **büyük** standart hata. Round-1'deki "anlamsızlık isteyen ölçütte
    küçük standart hata" kuralı, anlamsızlık ölçütleri kalmadığı için kalktı.
- **Eşdeğerlik testi (TOST; KC-06).** Parametre θ, tolerans δ > 0. H0: |θ| ≥ δ; H1: |θ| < δ. İki tek taraflı %5
  testi; eşdeğer: %90 güven aralığı (θ̂ ± 1,645·SE_NW) tamamen (−δ, +δ) içinde. Birden fazla parametre için
  kesişim-birleşim ilkesi: hepsi ayrı ayrı eşdeğer olmalıdır; ilke birinci tür hatayı çoklu düzeltme
  gerektirmeden %5'te tutar. Eşdeğerlik "anlamsızlık" ile karıştırılmaz: SE büyüdükçe eşdeğerlik **zorlaşır**.
- **Korelasyonun üst güven sınırı (K1 eşiği için; KC-07):** Fisher dönüşümüyle, tek taraflı %90:

      ρ_üst = tanh( atanh(ρ̂) + 1,2816 / √(n_w − 3) ),   n_w = 143  →  ek terim ≈ 0,108

  ρ̂ = ρ(r^N, r^trend,net), haftalık. Seri bağımlılık bu sınırı biraz iyimser yapar; K1 eşiği ayrıca 0,30'da
  doyuma ulaştığı için etkisi sınırlıdır.
- **Blok bootstrap:** dairesel, blok 4 ve 12 hafta, 10.000 çekiş, tohum **20260928**, yüzdelik güven sınırı.
  K2'de iki alt sınırın küçüğü kullanılır.
- **Beta (K9):** haftalık OLS, r^N_w = a + β·x_w + e. x: BTC haftalık basit getirisi; ayrıca eşit ağırlıklı alt
  sepeti (o haftanın carry aday evreni) haftalık getirisi. Ayrı regresyonlar.
- **Fiyat faktörleri (K11):** hepsi o haftanın Pazartesi carry aday evreninde, PIT:
  - x_B: BTC haftalık basit getirisi;
  - x_A: eşit ağırlıklı alt sepeti getirisi;
  - x_R: R30 sırasına göre üst %30 eşit ağırlıklı long, alt %30 short; sonraki haftanın getirisi;
  - x_S: s^trend sırasına göre aynı biçimde kurulmuş uzun-kısa getirisi.
  x_S trend bacağının P&L'ini kullanmaz; mühür (§2) bozulmaz.
  - **Standart yükleme:** b̃_k = b_k · sd(x_k) / sd(r^P). Faktörün tek başına açıkladığı fiyat varyansı payı
    yaklaşık b̃_k²'dir. SE(b̃_k) = SE_NW(b_k) · sd(x_k) / sd(r^P); sd'ler örneklem değeridir.

### 6.3 Karar ölçütleri (hepsi önceden; K3/K4 dışındakilerin hepsi sağlanmalı)

| Kod | Ölçüt | Eşik | Birim | n |
|---|---|---|---|---|
| K1 | Kredilenen net Sharpe başabaşı aşar (m_c = 1, taban delist) | SR^K ≥ **K1\*(ρ_üst)** = 0,85 · g(ρ_K1, 1/3); g(ρ, k) = (√(1 + k² + 2ρk) − 1)/k; ρ_K1 = min(0,30; max(0; ρ_üst)). Eşik 0,138 (ρ_üst ≤ 0) ile 0,370 (ρ_üst ≥ 0,30) arasındadır (§8.4) | hafta | 143 |
| K2 | Funding maliyeti anlamlı aşar | NW t(r^F − r^C) ≥ 3,0 **ve** bootstrap tek taraflı %95 alt sınır > 0 | hafta | 143 |
| K3 | *Bağlayıcı değil (2. tur).* Fiyat ortalaması eşdeğerliği, alt taraf | TOST alt kolu: μ_P'nin %95 tek taraflı alt sınırı > −δ_P; δ_P = %4/yıl birim. Yalnız rapor; gerekçe §6.4, §8.3. Bağlayıcı rolü K1/K6/K8'deki fiyat kaybı düşümüne geçti | hafta | 143 |
| K4 | *Bağlayıcı değil (2. tur).* Fiyat ortalaması eşdeğerliği, üst taraf | TOST üst kolu: μ_P'nin %95 tek taraflı üst sınırı < +δ_P. Yalnız rapor. Bağlayıcı rolü "fiyat kazancı kredilenmez" kuralına geçti | hafta | 143 |
| K5 | Taşıma tutarlılığı | (r^F − r^C) > 0 olan ay payı ≥ %75 (≥ 25/33) | ay | 33 |
| K6 | Maliyet 2× dayanıklılığı | SR^K(m_c = 2) > 0 | hafta | 143 |
| K7 | Maliyet 3× dayanıklılığı | NW t(r^F − r^C; m_c = 3) ≥ 2,0 | hafta | 143 |
| K8 | Tekil isim bağımlılığı | Yeniden koşu: toplam N katkısına göre en iyi 3 ve en kötü 3 isim carry aday listesinden bütün dönem çıkarılır. SR^K > 0 | hafta; isim | 143; ≥30 isim |
| K9 | Beta eşdeğerliği | β_BTC ve β_alt için ayrı ayrı %90 güven aralığı (NW, büyük SE) ⊂ (−0,15; +0,15) | hafta | 143 |
| K10 | Trend bağımsızlığı | \|ρ̂(r^N, r^trend,net)\| ≤ 0,30. ρ'nun ekonomik etkisi ayrıca K1\*'a ρ_üst ile girer | hafta | 143 |
| K11 | Fiyat faktörü yüklemesi eşdeğerliği | r^P_w = a + b_B·x_B + b_A·x_A + b_R·x_R + b_S·x_S + e (ortak regresyon). Dört standart yüklemenin her biri için %90 güven aralığı ⊂ (−δ_b; +δ_b), **δ_b = 0,30** (kesişim-birleşim TOST) | hafta | 143 |

**Çift seri kuralı (KC-05).** K1, K6, K8, K9 ve K10 hem sanal seriyle (r^N) hem gerçekleşen seriyle (r^{N,g} =
r^N + a^C, §5.6) hesaplanır; ölçüt ancak **ikisinde de** geçerse geçmiş sayılır. K1'de iki seri için ρ_üst ayrı
hesaplanır ve her seri kendi eşiğine karşı sınanır. K2, K5, K7 ve K11 funding/fiyat ayrıştırmasına dayanır ve
sanal satırlarla hesaplanır; gerçekleşen seriden sapmaları V4a/V4b ile sınırlıdır. Gerekçe: karar yalnız toplam
net hatayla değil, icra artığının yol boyunca dağılımıyla da doğrulanmalıdır; Sharpe ve beta artığın yoluna
duyarlıdır.

Notlar:
- K2, K6, K7'deki maliyet çarpanı MIMARI §6'daki tek tanımdır (§3.6).
- K8'de çıkarılan isimler yalnız carry adaylığından çıkar. Trend evrenindeyse trend onları tutmaya devam eder.
  İsim sıralaması ana koşunun sanal carry satırlarından yapılır; eşitlikte alfabetik. Bu yeniden koşu varyant
  değildir (§3.6). Hiç tutulmuş ayrı isim sayısı < 30 ise K8 hesaplanamaz ve sonuç A olur.
- K11'de ham katsayılar, NW t'leri ve round-1'deki ortak Wald p değeri yalnız raporlanır; karar standart yükleme
  aralıklarıyla verilir. Faktörlerin açıkladığı fiyat ortalaması Σ_k b_k·ortalama(x_k) ayrıca raporlanır; bu
  pay zaten kredilenmediği için karara ayrıca girmez.
- K1\* formülünde yalnız ρ_üst gözlemden gelir; SR_T,ref = 0,85 ve k = 1/3 sabittir. Trend P&L'i, trend Sharpe'ı
  ve trend vol'ü kapıda hesaplanmaz, açılmaz (§2 mühür). ρ̂ ve ρ_üst hüküm dosyasına yazılır.

### 6.4 Gerekçeler
- **K1, eşik K1\*(ρ_üst) (KC-07).** Eşik, B'nin bankada A'yı seyreltmediği başabaş carry Sharpe'ına konur (§8.4).
  Round-1'deki 0,10 yalnız ρ = 0 ve SR_T = 0,45–0,60 için başabaştı; K10 ise ρ = 0,30'a izin veriyordu. Yeni eşik
  korelasyonlu seyreltme formülünden **mekanik olarak** hesaplanır; D P&L'ine bakılarak seçilmez. Üç girdisi:
  (i) SR_T,ref = 0,85: seyreltmenin banka hükmünü en çok etkilediği çıta civarı (§8.4; önsel A bandı 0,45–0,60
  seçilseydi eşik daha düşük ve B lehine olurdu); (ii) k = σ_C/σ_T = 1/3: MIMARI §1d'nin σ_C = %3, σ_T = %9 önseli;
  (iii) ρ_K1: gözlenen ρ'nun tek taraflı %90 üst sınırı, [0; 0,30] aralığına kırpılmış. Alt kırpma: D'de negatif ρ
  bankada negatif ρ garantisi değildir; üst kırpma: K10 zaten |ρ̂| > 0,30'u reddeder ve eşik kapının izin verdiği
  aralığın en kötü ucunda (0,370) doyar. Kredilenen SR fiyat kazancını saymadığı için eşik, pratikte funding eksi
  maliyetin Sharpe'ına uygulanır. Anlamlılık eşiği (t ≥ 2) 33 ayda SR ≳ 1,2 ister ve kapıyı "hep A"ya çevirir;
  başabaş seçimi bu yüzden korunur.
- **Fiyat kazancı kredilenmez (K1, K6, K8; KC-06).** Kapının sorusu "getiri funding'den mi" sorusudur. Fiyat
  ortalamasının ekonomik olarak önemsiz olduğu D'de gösterilemez (§8.3: en küçük geçilebilir tolerans net
  funding gelirinin 2–3 katı). Gösterilemeyen şeye dayanmak yerine karar serisi fiyat kazancını dışlar: B'nin
  geçmesi yalnız funding eksi maliyetin, fiyat kaybı düşüldükten sonra, başabaşı aşmasıyla mümkündür. Bedeli: H1
  doğruyken bile fiyat gürültüsünün negatif yarısı düşülür, pozitif yarısı sayılmaz. Bu, kapıyı B aleyhine
  yanlılaştırır (§8.2); A varsayılanıyla uyumludur.
- **K2, t ≥ 3.** Funding geliri düşük oynaklıklı ve kalıcıdır. H1 doğruysa t yüksek beklenir. Görülmüş bilgi
  (§10) bu ölçütün büyük olasılıkla geçeceğini söyler; eşik bu yüzden 2 değil 3'tür. ℓ = 12 kalıcılığın t'yi
  şişirmesini önler.
- **K3, K4 (2. turda bağlayıcılıktan çıktı; KC-06).** Round-1'de "NW t(r^P) ∈ (−2, +2)" idi: bir anlamsızlık
  testi. Yüksek belirsizlikte kendiliğinden geçer; Codex'in örneğinde fiyat t ≈ 0,33 ile geçer ve kazancın %75'i
  fiyattandır. Eşdeğerlik biçimine (TOST) çevrildi. Tolerans δ_P = %4/yıl birim ölçekte (≈ %0,8/yıl NAV): beklenen
  net funding gelirinin (önsel %5–8/yıl birim, §8.3) kabaca yarısı ile üçte ikisi; yani "fiyat katkısı, funding
  katkısının yarısını geçmez" ekonomik tanımı. δ_P D'ye bakmadan, bu önselden seçildi (zayıf görülmüş bilgi: önsel
  jürilerden). Ancak TOST'un geçilebilmesi için δ_P > 1,645·SE ≈ %15 gerekir (§8.3); δ_P = %4 ile TOST H1 doğruyken
  bile pratikte hiç geçilemez. Geçilemez bir ölçütü bağlayıcı koymak kapıyı gizlice "kapısız A"ya çevirir ve
  kullanıcı kararıyla (ASAMA4B_KARAR §1) çatışır; δ_P'yi %15'in üstüne çekmek ise ekonomik olarak önemsiz olmayan
  bir fiyat bahsini "eşdeğer" ilan eder. Bu yüzden K3/K4 TOST'u yalnız raporlanır; bağlayıcı içerik kredilenme
  kuralına taşınır: K3'ün sorusu (fiyat funding'i silmez mi) fiyat kaybının K1/K6/K8'de düşülmesiyle, K4'ün sorusu
  (getiri fiyattan mı) fiyat kazancının hiç sayılmamasıyla bağlayıcı olarak yanıtlanır. φ yalnız betimsel.
- **K5.** Kanıt jürisi "çeyreklerin ≥%75'i" önerdi. D'de 11 çeyrek var (n < 30). Ölçüt aya indirildi (n = 33).
- **K6, K7.** KARARLAR §2 "maliyet 3×". 3×'te net Sharpe'ın pozitifliği gürültülü ikinci bir K1 olurdu. 3×'te
  istenen, funding'in maliyeti anlamlı karşılamasıdır.
- **K8.** Tek isim sıkışması ya da tek isim şansı sonucu belirlememeli. Simetrik kırpma yanlılık yaratmaz.
  Yeniden koşu, nötrleme ve hedge'in isimler olmadan yeniden kurulmasını da sınar (K2-11).
- **K9 (eşdeğerliğe çevrildi; KC-06).** Dolar nötrlüğü beta nötrlüğü değildir (Codex jürisi). 0,15, BTC kaynaklı
  varyansı carry birim ölçeğinde ~%10 ile sınırlar. Round-1'de nokta tahmini sınırdı; artık %90 aralığın tamamı
  sınırın içinde olmalıdır. β'nın standart hatası kabaca 0,03'tür (ölçülmedi); %90 yarı genişlik ~0,05, yani H1
  altında |β̂| ≲ 0,10 gerekir. Ölçüt fizibildir.
- **K10.** Carry tasarımının banka önerisi (|ρ| ≤ 0,3) D'ye taşındı. Uydu trendin kopyası olmamalı. Nokta
  tahmini sınırı korunur; korelasyonun belirsizliği K1\*'a ρ_üst ile, B aleyhine girer.
- **K11 (eşdeğerliğe çevrildi; K2-02, KC-06).** Gizli fiyat bahsi en olası biçimde bir faktöre yüklenir: piyasa,
  alt sepeti, geçmiş getiri ya da trend. Round-1'deki "ortak Wald p > 0,10" bir anlamsızlık testiydi: güç düştükçe
  kolaylaşır. Yeni ölçüt her yüklemenin **küçük olduğunu** gösterir. Tolerans δ_b = 0,30 standart yükleme: tek bir
  faktör fiyat varyansının en çok ~%9'unu açıklar. Ekonomik anlamı: faktör Sharpe'ı ≤ 0,5 (tipik faktör primleri
  için önsel; zayıf görülmüş bilgi) iken tek faktörden gelebilecek fiyat getirisi ≤ 0,30·0,5·%15 ≈ %2,3/yıl birim,
  yani net funding önselinin (%5–8) kabaca üçte biri. Fizibilite: dikey faktörlerde SE(b̃) ≈ 1/√143 ≈ 0,084; NW
  ve faktörler arası korelasyonla ~0,10. H1 altında (b̃ = 0) bir yüklemenin geçme şansı kabaca %83–95; dört
  yükleme birlikte kabaca %45–80 (bağımsızlık varsayımıyla, kaba). Kesişim-birleşim ilkesi çoklu düzeltme
  gerektirmez. Faktör dışı fiyat bahisleri K11'e görünmez; onları kredilenme kuralı karar serisinden dışlar.

### 6.5 Çıkarılan jüri ölçütleri
- "2021 kaybı ≤ 1σ", "2021'de short bacağı kaybı ≤ 0,5σ", "2021 ve 2022 ayrı yıllık kayıp ≤ %15, MDD ≤ %25":
  banka dönemine atıf. Çıkarıldı; D'ye uyarlanmadı.
- "Görülmemiş coin alt kümesinde SR > 0": D'de görülmemiş coin yok. Çıkarıldı.
- "Short bacağının ayrı fiyat bileşeni": D'deki alt düşüşünde short bacağın ham fiyatı mekanik olarak olumlu
  görünür. Ölçüt D lehine yanlı olacağından alınmadı. K11 bu kanalı faktör olarak sınar.
- DSR: betimsel. N, banka ön-kaydının sayım kuralıyla hesaplanır. Eşik konmaz; 33 ayda bu sayaçla kapı hiç
  geçilemez.
- **Rejim bilgisi:** Hiçbir kapı eşiği banka dönemine dair genel piyasa bilgisine dayanmaz (K2-06 ilkesi).
  Rejim cümleleri yalnız §8.6'daki yorumda geçer.

### 6.6 Betimsel (bağlayıcı olmayan) raporlar
- φ = (F̄ − C̄) / (F̄ − C̄ + max(P̄, 0)); çeyrek tablosu; MDD; en kötü hafta ve isim-hafta.
- Delist senaryolarında (h_L %50, %90) K1 değeri.
- K11 tekil katsayıları ve t'leri; ℓ = 4 ve 12 için bütün NW t'leri; Andrews otomatik gecikmesiyle t'ler.
- κ_C < 1 gün oranı; trend katsayılarının bağlama sıklığı; S4 bağlama sıklığı; n_C serisi.
- **Gerçekleşen kitap tavanları** (K1-04): gerçekleşen ve devreden kitapta S1, S2, S4 aşım günü oranı ve en
  büyük aşım; hedefe ulaşılamayan gün oranı.
- **Hedge yuvarlama** (K1-18): kapı NAV'ında ve 5.000 USDT demo NAV'ında BTC hedge nominalinin bir lot adımının
  altında kaldığı gün oranı. Ağırlıktan hesaplanır; yeniden koşu gerekmez.
- Doldurulan funding kayıtlarının sayısı ve F'ye katkısı.
- Long ve short bacak satırları; netleme kazancı; Σ_t |A^C_t|; bootstrap SR aralığı.
- **2. tur tanıları:** K3/K4 TOST (δ_P = %4/yıl birim) ve fiyat ortalamasının %90 aralığı; kredilenmeyen SR(r^N) ve
  SR(r^{N,g}); a^C_w serisi, en büyük üç haftalık sapma; sıfır/sıfır artık tanısı (§5.6); κ^C günlük göreli değişim
  tanısı (§5.1); ρ̂, ρ_üst ve iki serinin K1\* değerleri; K1\*'ın SR_T,ref ∈ {0,45; 0,60} ve k ∈ {0,27; 0,43}
  duyarlılığı (bağlayıcı değil); V6 fark günlerinin ortalama trend brüt farkı.

**Delist senaryoları neden bağlayıcı değil.** Carry kitabındaki delist olayı büyük olasılıkla 30'dan azdır.
Karar birkaç olaya dayanmamalı. İlke: az olaya dayanan senaryo kapıda bağlayıcı değildir. Bankada −%90 ayrıca
raporlanır (KARARLAR §1.2); R12'nin (banka; eski B12, rapora indi) bu ilkeyle uyumu banka ön-kaydında ele alınır.

---

## 7. Karar kuralı, kör hüküm ve hata yönetimi

### 7.1 Karar
- **B:** V1–V6 sağlanır **ve** bağlayıcı ölçütlerin (K1, K2, K5–K11) hepsi, çift seri kuralı gereken yerde iki
  seride de geçer. K3 ve K4 2. turda yalnız rapordur (§6.4).
- **A:** Diğer bütün durumlar. Hesaplanamayan ölçüt geçmemiş sayılır.

Yasaklar:
- "Kıl payı" yoktur. Ölçüt ikilidir. Eşitlik ölçütün yazıldığı yöndedir (K1: SR^K = K1\* geçer; K2: t = 3,0
  geçer; K9/K11: aralık ucu toleransa eşitse geçmez, çünkü aralık açık (−δ, +δ) içinde olmalıdır).
- Yeniden koşma yoktur. Eşik, dönem, evren, NAV, L, tohum ya da ölçüt kümesi değişmez.
- Alt küme seçilmez: dönem kırpılmaz, isim dışlanmaz, "şu çeyrek hariç" yorumu yapılmaz.
- Başarısız sonucu yeni eşikle ya da yeni varyantla kurtarmak yasaktır. Yeni carry sürümü ayrı hipotez, ayrı
  ön-kayıt ve ayrı denemedir ve bu bankaya gidemez.
- Sonuç ne olursa olsun bütün ölçütler, betimsel raporlar ve karar yayımlanır (trend satırları hariç, §2).

### 7.2 Kör hüküm (K2-07)
Kapı betiği üç dosya yazar ve hepsini yazıldığı anda hash'ler:
1. **Denetim dosyası:** V1–V6 geçti/kaldı, değişmez denetimleri, veri raporu, doldurulan kayıt sayıları.
   Ölçüt değeri içermez. (V4a/V4b yalnız geçti/kaldı olarak yazılır; oranları hüküm dosyasındadır.)
2. **Hüküm dosyası:** K1–K11 değerleri, eşikler, geçti/kaldı, karar, betimsel raporlar.
3. **Trend mühür dosyası:** trend satırları. Banka hükmü açılana kadar açılmaz.

Koşu sırasında hiçbir metrik ekrana basılmaz. Önceden yazılmış denetim listesi (V1–V6, değişmezler, veri
raporu; istenirse Codex'in hash ve değişmez yeniden üretimi) hüküm dosyası açılmadan tamamlanır ve kaydedilir.
Hüküm dosyası ancak bundan sonra açılır.

### 7.3 Hata yönetimi
**Hüküm açılmadan önce bulunan hata.**
1. Hata, kapı çıktısından bağımsız bir sentetik fikstürle gösterilir.
2. Düzeltme diff'i yayımlanır. Parametre, eşik ve davranış değişmez.
3. Kapı bütünüyle bir kez, yine kör olarak yeniden koşulur. Deneme sayacı 2 olur; deftere satır girer.
4. En fazla bir teknik yeniden koşu. İkinci teknik geçersizlikte sonuç A.

**Hüküm açıldıktan sonra bulunan hata.**
- Yalnız şu sınıflar kabul edilir: muhasebe özdeşliği, bakış-ileri, funding işareti, maliyet işareti. Hata
  kapı çıktısından bağımsız bir testle gösterilmelidir.
- Kabul edilen hata sonucu **A** yapar ("kapı değerlendirilemedi"). Sonuç B'ye hiçbir koşulda dönmez.
- İki çıktı da raporlanır.
- Gerekçe: B pozitif kanıt ister; kanıtı bozuk bir koşu B'yi destekleyemez. Hüküm sonrası hata avı yalnız
  B'den A'ya götürebilir; kullanıcı kararının varsayılanı zaten A'dır.

**Sonuç beğenmeme hiçbir koşulda gerekçe değildir.**

---

## 8. Güç analizi ve bankaya etkisi (hesapsız, ölçekle)

### 8.1 Sharpe'ın standart hatası

    SE(SR̂) ≈ √((1 + SR²/2) / T_yıl),   T_yıl = 33/12 = 2,75   →   SE ≈ 0,61

Negatif çarpıklık ve kalın kuyruk bunu büyütür (Mertens düzeltmesi: 1 − γ₃·SR + (γ₄−1)/4·SR²).

### 8.2 K1'in tek başına geçme oranı (kaba yaklaşım; olasılık iddiası değil)
**Uyarı (KC-06).** Bu bölümdeki ve §8.5'teki sayılar tek ölçütlü, normal ve bağımsız getiri varsayımlı kaba
hesaplardır. Ölçütlerin ortak dağılımı, NW düzeltmesi, çarpıklık ve eşdeğerlik testlerinin gücü doğrulanmadan
bunlar "olasılık" olarak sunulmaz ve RAPOR'a olasılık diye yazılmaz. Doğrulama §8.5'teki sentetik fikstürle yapılır.

Kredilenen SR'da fiyat ortalamasının pozitif yarısı sayılmaz. Funding eksi maliyetin tahmin gürültüsü fiyatınkine
göre küçük kabul edilirse (ölçülmedi), fiyat ortalaması sıfırken:

    SR^K̂ ≈ s + min(Z·0,61; 0),   s = funding eksi maliyetin gerçek Sharpe'ı (N'nin oynaklığıyla)
    geçme oranı ≈ Φ((s − K1*)/0,61)  (s ≥ K1* ise);   ≈ 0  (s < K1* ise)

| Gerçek s | 0 | 0,15 | 0,3 | 0,45 | 0,6 |
|---|---|---|---|---|---|
| K1\* = 0,138 (ρ_üst ≤ 0) | ~0 | ~0,51 | ~0,60 | ~0,70 | ~0,78 |
| K1\* = 0,370 (ρ_üst ≥ 0,30) | ~0 | ~0 | ~0 | ~0,55 | ~0,65 |

Round-1 ile fark: kredilenme kuralı gerçek funding Sharpe'ı eşiğin altındaysa geçişi pratikte kapatır; eşiğin
üstündeyse fiyat gürültüsünün yalnız kötü yarısı zarar verir. Beklenen funding Sharpe'ı (net funding önseli
%5–8/yıl birim, vol ~%15) s ≈ 0,33–0,53'tür; kapı bu yüzden ρ düşükse ve funding önselin üst ucundaysa geçer.

### 8.3 K4'ün en küçük saptanabilir etkisi (K2-02)
- Fiyat bileşeninin vol'ü yaklaşık carry birim vol'üdür: σ_P ≈ %15 (ölçülmedi).
- Yıllık ortalamanın standart hatası: %15 / √2,75 ≈ %9,0 (carry birim ölçeği).
- En küçük saptanabilir etki (|t| ≥ 2):
  - %50 güçle: 2 × %9,0 ≈ **%18/yıl** birim; NAV'da (× ω_C = 0,20) **%3,6/yıl**.
  - %80 güçle: 2,84 × %9,0 ≈ **%26/yıl** birim; NAV'da **%5,1/yıl**.
- Beklenen net funding geliri: birim ölçekte yılda ~%5–8 (brüt %6–9 eksi maliyet %0,6–1,2); NAV'da ~%1,0–1,6.
- **Sonuç:** Anlamlılık testi, net funding gelirinin 2–5 katı büyüklüğündeki bir fiyat bahsini ancak görebilir.
- **Eşdeğerlik fizibilitesi (KC-06).** Fiyat ortalaması için TOST, H1 doğruyken (μ_P = 0) ancak δ_P > 1,645·%9,0 ≈
  **%15/yıl birim** (≈ %3/yıl NAV) ise geçilebilir; geçme oranı ≈ 2Φ((δ_P − 1,645·SE)/SE) − 1:
  δ_P = %15 → ~%1; %20 → ~%43; %25 → ~%74. En küçük geçilebilir tolerans, beklenen net funding gelirinin (%5–8)
  2–3 katıdır; ekonomik olarak önemsiz değildir. Ekonomik tolerans δ_P = %4 ile TOST pratikte hiç geçilemez.
  **33 ayda fiyat ortalamasının ekonomik olarak önemsiz olduğu gösterilemez.** Bu yüzden kapı bunu iddia etmez;
  fiyat kazancını karar serisinden dışlar (§6.4). Yükleme eşdeğerliği (K11, K9) ise fizibildir: yükleme
  tahminleri ortalamadan çok daha kesindir.

### 8.4 Bankada seyreltme ve K1 eşiğinin türetilmesi (K2-03)
B bankada bütün olarak yargılanır. B seçilirse A'nın sonucu hükme girmez. Yanlış kabulün asıl bedeli, iyi bir
trendin bankada seyrelip RET yemesidir. Korelasyonla (KC-07; round-1 yalnız ρ = 0 idi):

    SR_B = (SR_T·σ_T + SR_C·σ_C) / √(σ_T² + σ_C² + 2ρ·σ_T·σ_C)

Başabaş carry Sharpe'ı (SR_B = SR_T):

    SR_C* = SR_T · g(ρ, k),   g(ρ, k) = (√(1 + k² + 2ρk) − 1) / k,   k = σ_C / σ_T

σ_C = %3 (L = 1'de ω_C = 0,20 × %15; tavanlar düşürebilir). σ_T = %7–11 (MIMARI §3.3 beklentisi, ölçülmedi).
g(ρ, k) değerleri:

| ρ | k = 0,27 (σ_T = %11) | k = 1/3 (σ_T = %9) | k = 0,43 (σ_T = %7) |
|---|---|---|---|
| −0,30 | −0,17 | −0,14 | −0,09 |
| 0 | 0,13 | 0,16 | 0,21 |
| +0,30 | 0,41 | 0,44 | 0,47 |

Başabaş SR_C* (k = 1/3):

| SR_T | ρ = 0 | ρ = 0,10 | ρ = 0,20 | ρ = 0,30 |
|---|---|---|---|---|
| 0,45 (kâr jürisi A merkezi) | 0,07 | 0,12 | 0,16 | 0,20 |
| 0,60 (A bandı üstü) | 0,10 | 0,15 | 0,21 | 0,26 |
| 0,85 (banka çıtası civarı) | 0,14 | 0,22 | 0,29 | **0,37** |

Codex'in hesabı (σC/σT = 1/3, SR_T = 0,85, ρ = 0,30 → ≈ 0,37) bu tabloyla aynıdır. Round-1'in 0,10'u yalnız ρ = 0 ve
SR_T ≈ 0,6'da başabaştı; kapının izin verdiği ρ = 0,30'da başabaşın dörtte biridir.

**K1\* kuralı.** K1\* = 0,85 · g(ρ_K1, 1/3), ρ_K1 = min(0,30; max(0; ρ_üst)) (§6.2, §6.3). Gözlenen ρ̂'ya göre:

| ρ̂ | ≈ −0,11 ve altı | 0 | 0,10 | ≈ 0,20 ve üstü |
|---|---|---|---|---|
| ρ_üst | ≤ 0 | 0,11 | 0,21 | ≥ 0,30 |
| K1\* | 0,138 | 0,224 | 0,299 | 0,370 |

Yalnız ρ̂ gözlemden gelir; formül ve öteki girdiler kilitte dondurulur. Seçim D P&L'ine bakılmadan, yalnız bu
aritmetikle yapıldı.

**Tavan etkileşimi (KC-07).** Formül B'nin trend bacağının A ile aynı olduğunu varsayar. §3.3 çözücüsü tavan
bağladığında önce trendi küçültür; o günlerde B, "A + carry" değildir ve seyreltme formülün gösterdiğinden büyük
olabilir. L = 1'de bu beklenmez (§3.3: S1 kaybı ~0,07–0,10, sınır 0,20). V6 bunu bağlayıcı yapar: B trend hedefinin
A'dan ayrıldığı gün oranı %10'u aşarsa formül geçersiz sayılır ve sonuç A olur. Kelly L > 1'de tavanlar daha sık
bağlar; bu, bankada L başına carry betası ve trend katsayısı raporuyla (BANKA R8) izlenir, kapıda sınanamaz.

Seyreltmenin banka hükmüne etkisi (SR_T = 0,85, σ_T = %9, σ_C = %3, ρ = 0; ρ > 0'da kayıplar büyür):

| Gerçek banka SR_C | −0,3 | −0,2 | 0 | 0,1 | 0,3 |
|---|---|---|---|---|---|
| SR_B | 0,71 | 0,74 | 0,81 | 0,84 | 0,90 |
| Çıta civarında P(KABUL) farkı | ~−10 puan | ~−8 puan | ~−3 puan | ~−1 puan | ~+4 puan |

P(KABUL) farkı ≈ φ(z) · ΔSR / SE_banka ile hesaplandı; SE_banka ≈ 0,56 (banka taslağı v1 §3.2), φ(z) ≤ 0,40.
Etki, trend çıtaya yakınken en büyüktür. Trend çıtanın çok üstünde ya da altındaysa B/A seçimi hükmü nadiren
değiştirir.

### 8.5 Bileşik hata oranları (kaba büyüklük sırası; olasılık iddiası değil)
§8.2'deki uyarı geçerlidir. Ölçütler bağımsız değildir: K1, K6, K8 aynı fiyat gürültüsüyle sürülür; K9 ve K11 aynı
regresyon ailesindendir. Aşağıdakiler yalnız yön ve büyüklük sırası gösterir.

- **Yanlış ret (H1 doğru, fiyat ortalaması 0).** Kredilenme ve K11 eşdeğerliği kapıyı round-1'den zorlaştırır.
  Funding Sharpe'ı s = 0,3 ve ρ düşükken K1 tek başına ~%60 geçer; K11 dört yüklemeyle kabaca %45–80. Bileşik
  yanlış ret kabaca %50–75'tir. ρ yüksekse (K1\* = 0,37) s = 0,3'te geçiş pratikte yoktur.
- **Yanlış kabul, H0a (funding zayıf):** K2 ve K7 yakalar; düşük.
- **Yanlış kabul, H0b (fiyat funding'i siliyor):** Fiyat kaybı K1'de düşülür. Örnek: s = 0,4, fiyat ortalaması
  −0,6 SR birimi (net SR ≈ −0,2): K1 geçişi kabaca %15–30 (K1\* 0,37 → 0,14). Round-1'deki ~%25 ile aynı büyüklük
  sırası; bu kanalı yine esas olarak K1'in gürültüsü belirler.
- **Yanlış kabul, H0c (gizli fiyat bahsi).** Round-1'e göre asıl iyileşme buradadır. Fiyat kazancı kredilenmediği
  için, funding eksi maliyet tek başına K1\*'ın altındaysa geçiş pratikte yoktur (Codex örneği: SR^K ≈ 0,07).
  Funding tek başına eşiği aşıyor ve yanına ayrıca bir fiyat bahsi ekleniyorsa B seçilebilir; ama o durumda B'nin
  gerekçesi fiyat bahsi değil funding'dir. Bahis bir faktöre b̃ > 0,30 yüklüyse K11 büyük olasılıkla reddeder.

**Sentetik doğrulama (kilitten önce; D kullanmaz).** Bu sayılar olasılık olarak sunulmadan önce kapı ölçüt
kümesinin bileşik davranışı sentetik fikstürle ölçülür. Adım 3'te (sentetik kalibrasyon) ayrı bir fikstür olarak
koşulur ve Adım 4 kilidine girer. Üreteç şimdi dondurulur: 143 haftalık seri; fiyat bileşeni = Σ_k b_k·x_k + e,
x_k bağımsız normal (her biri yıllık vol %15), e normal, fiyat bileşeninin toplam yıllık vol'ü %15; funding eksi
maliyet = sabit ortalama + haftalık AR(1) gürültü (φ = 0,5, yıllık vol %3); trend serisi ρ ile ilişkili normal.
Senaryolar: H1 (s ∈ {0,3; 0,45}, b = 0, ρ ∈ {0; 0,3}); H0b (s = 0,4, fiyat ortalaması −%9/yıl); H0c-ortalama (funding
eksi maliyet %1, fiyat ortalaması %3, Codex örneği); H0c-faktör (b̃_A = 0,40). 10.000 tekrar, tohum **20260929**. Çıktı:
her senaryoda P(B) ve ölçüt başına geçme oranı. **Sonuç eşikleri kendiliğinden değiştirmez.** Kilitten önce
kullanıcıya sunulur; değişiklik ancak kullanıcı kararıyla ve D P&L'i görülmeden yapılabilir. V4a/V4b, V5, V6
fikstürde yoktur (icra katmanı yok).

**Hüküm: kapının gücü düşüktür.** Kapı funding gelirinin varlığını iyi ölçer. Fiyat ortalamasının sıfır olduğunu
gösteremez; bunu iddia etmez, onun yerine fiyat kazancını karardan dışlar. 33 ayda carry'nin kenarı ile sıfır
arasında ayrım yapılamaz.

**RAPOR'a girecek cümle:** "B kararı, getirinin fiyattan gelmediğinin gösterildiği anlamına gelmez; fiyat
ortalaması için eşdeğerlik D'de sınanamaz. B'nin anlamı şudur: funding eksi maliyet, fiyat kazancı hiç
sayılmadan ve fiyat kaybı düşülerek, ölçülen korelasyona göre ayarlanmış bankadaki başabaş eşiğini aştı; bu
sonuç gerçekleşen icra artığı eklenmiş seride de tuttu; BTC ve alt sepeti betası ile dört fiyat faktörüne
yüklemeler önceden dondurulmuş toleranslar içinde eşdeğer bulundu."

### 8.6 Yorum (eşik gerekçesi değildir)
D, farkın geniş olduğu bir dönemdir; carry için elverişli olabilir. D'de geçmek başka bir rejimde geçmek
anlamına gelmez. Banka A/B seçmediği için bu risk B'nin içinde taşınır. B seçilirse bankada carry satırları
ayrıca raporlanır. Bu paragraf hiçbir eşiği etkilemedi.

---

## 9. Bütçe sabittir

- B seçilirse carry katkısı MIMARI'deki **ω_C = 0,20** ile girer. Değer kapıdan önce sabittir.
- Kapıdan bütçe çıkarılmaz. Kapı SR'ına, funding t'sine ya da "kıl payı" sonuca göre ω_C büyütülmez,
  küçültülmez, kademelendirilmez.
- κ_C < 1 yalnız tavan çözücüsünün son adımıdır (§3.3); bütçe kararı değildir. Sıklığı raporlanır.
- A seçilirse carry kodu nihai mimaride devre dışıdır (bacak yok); banka A'yı koşar.
- B seçilirse A'nın banka sonucu yalnız ayrıştırmadır (ONKAYIT §2).
- B seçilirse demo ön-kaydı, demo NAV'ında BTC hedge'inin lot adımı altında kalmasını (K1-18) açıkça ele alır.

---

## 10. Görülmüş bilgi ve kapı sabitleri

### 10.1 D'de carry hakkında zaten bilinenler
Kaynaklar: tasarım `carry` betimsel kontrolü, Aşama 1, defter `A2-carry` ve `A1-veri`. Strateji P&L'i ve fiyat
bacağı hesaplanmadı.

| Bilgi | Kaynak | Kapıya etkisi |
|---|---|---|
| F30 sırasının 30 ve 90 günlük kalıcılığı 0,47–0,56 | carry | K2, K5 büyük olasılıkla geçer; NW ℓ = 12 buradan |
| Uç beşliler ileri funding farkı yılda ~%19–22; haftaların %96–97'sinde pozitif; std %18–28 | carry | K2, K5, K7 büyük olasılıkla geçer |
| Fark yarıyıla göre: 2024H1 %10, 2025H2 %28–40 | carry | K5'te zayıf aylar beklenir; eşik bundan türetilmedi |
| Funding seviyesi IC −0,008 (t −0,58), ham sıra ve sonraki 30 gün getirisi | VERI_PAKETI C4 | K3/K4 lehine önsel; nötrlenmiş kitabın fiyat bileşeni değildir |
| Funding sırası ile 60 gün getiri korelasyonu −0,11…−0,16; işaret rejime göre değişiyor | carry | R30 nötrlemesi ve x_R faktörü |
| Beta: üst beşli 1,30, alt beşli 1,23; betayla sıra korelasyonu +0,03…+0,07 | carry | K9 lehine; β nötrlemesi |
| Medyan funding ile BTC 60 gün getirisi korelasyonu 0,72; 2026H1'de coinlerin %58'i negatif funding | carry (KAYNAKTA_YOK) | Yeniden üretilmeli; K10 ile ilişkili |
| Biten coinler: F30 yüzdelik medyanı 0,47, %20'si negatif; 4'ü −%41…−%56 | carry; sayı 35 değil **33** (KALITE_RAPORU) | −%50 long tabanı buradan etkilendi |
| Medyan alt CAGR −%42; altların %83,5'i başlangıcın altında | VERI_PAKETI | Nötrleme sızarsa fiyat bileşeni D'de olumlu çıkar; K11'in x_A faktörü |
| Kesitsel ters dönüş IC −0,040 (30g→7g) | VERI_PAKETI C3 | R30 nötrlemesi ve x_R faktörü |
| Funding aralık geçişleri (2023-10-12, 2025–26 1h dönemleri) | Aşama 1 §2.10 | §4.2 funding kuralları ve V1 fikstürleri |

**Kapıyı nasıl zayıflatıyor.**
1. K2, K5, K7'nin sonucu kısmen bilinir. Bu ölçütler bilgiden çok mekanik başarısızlığı (maliyet modeli, funding
   muhasebesi, nötrleme hatası) yakalar.
2. Kapının belirsiz kısmı K1, K6, K8 ve K11'dir.
3. R30 nötrlemesi ve −%50 long tabanı D özetlerinden sonra seçildi. Fiyat bileşeni bu yüzden D'de olduğundan iyi
   görünebilir. 2. turda fiyat kazancı karar serisinde kredilenmediği için bu yanlılık B lehine çalışamaz; K9/K11
   eşdeğerliği ise bu seçimlerden kolaylaşmış olabilir.

### 10.2 Bu belgenin sabitleri
Etiket ölçeği (K2-12): **Hayır** = D özeti görülmeden; **Zayıf evet** = D özetini görmüş bir kaynaktan, P&L
görülmeden; **Evet** = doğrudan bir D istatistiğine dayanır. Hiçbir değer D P&L'ine göre seçilmedi; D P&L'i yok.

| Sabit | Değer | Kaynak | Görülmüş |
|---|---|---|---|
| K1 eşiği | SR^K ≥ K1\* = 0,85·g(ρ_K1, 1/3); 0,138–0,370 | §8.4 korelasyonlu başabaş aritmetiği (KC-07) | Zayıf evet (SR_T,ref ve k önselleri D özetlerini görmüş jürilerden/MIMARI §1d'den) |
| SR_T,ref | 0,85 | banka çıtası civarı; seyreltmenin en etkili olduğu nokta (§8.4) | Hayır (banka mührü çıtası; D değil) |
| k = σ_C/σ_T | 1/3 | MIMARI §1d (σ_C %3, σ_T %9) | Zayıf evet (σ_T önseli jürilerden) |
| ρ_K1 | ρ_üst (Fisher, tek taraflı %90), [0; 0,30]'a kırpılmış | §6.2; K10 ile aynı üst sınır | Hayır |
| Kredilenme kuralı | fiyat ortalaması: kazanç 0, kayıp düşülür | §6.4 (KC-06) | Hayır |
| K2 eşiği | t ≥ 3,0; bootstrap %95 | yeni faktör literatürü çıtası | Evet (§10.1 bilgisine karşı 2'den 3'e çıkarıldı) |
| K3, K4 (yalnız rapor) | TOST, δ_P = %4/yıl birim | net funding önselinin ~yarısı (§6.4) | Zayıf evet (funding önseli) |
| K5 | ≥ 25/33 ay | kanıt jürisi (%75), aya taşındı | Hayır |
| K6, K7 | 2×: SR > 0; 3×: t ≥ 2 | KARARLAR §2 | Hayır |
| K8 | 3 + 3 isim; ≥ 30 isim | bu belge | Hayır |
| K9 | β'nın %90 aralığı ⊂ (−0,15; +0,15) | bu belge; 2. turda eşdeğerliğe çevrildi | Hayır |
| K10 | \|ρ\| ≤ 0,30 | carry tasarımı | Hayır |
| K11 | 4 faktör; her standart yüklemenin %90 aralığı ⊂ (−0,30; +0,30) | K2-02, KC-06; δ_b faktör Sharpe önseli ≤ 0,5'ten (§6.4) | Zayıf evet (faktör seçimi D özetleriyle bilinen kanallardan) |
| V3 | aktif hafta ≥ %75 | bu belge | Hayır |
| V4a | Σ\|a^C_w\| ≤ 0,10·Σ\|r^N_w\| | bu belge (KC-05) | Hayır |
| V4b | her hafta \|a^C_w\| ≤ 1,0·sd(r^N_w) | bu belge (KC-05) | Hayır |
| V6 | B trend ≠ A trend gün oranı ≤ %10 | bu belge (KC-07) | Hayır |
| Sentetik fikstür | §8.5 üreteci; 10.000 tekrar; tohum 20260929 | bu belge | Hayır |
| NW gecikmesi | 4 ve 12 hafta; B aleyhine | Newey-West kuralı; kalıcılık | Evet (ℓ = 12, funding kalıcılığı) |
| Bootstrap | blok 4 ve 12, 10.000, tohum 20260928 | bu belge | Hayır |
| κ_C güncelleme bandı | *kaldırıldı (2. tur)*: κ^C günlük doğrudan uygulanır (MIMARI §4.5); %25 yalnız tanı | KC-03 | Hayır |
| HAR kapı eşiği | ≥ 30 haftalık gözlem | n ≥ 30 ilkesi | Hayır |
| Funding kuralları | en uzun aralık; 1,5×; 16 saat | K1-01 | Evet (aralık geçişleri) |

---

## 11. Belgeler arası arayüz

v1 metinleri ortak referanstır. Aşağıdakiler bu belgenin arayüzü değiştirdiği ya da MIMARI'ye bağlı olduğu
yerlerdir. SAYI_KONTROLU (Adım 5) bunları üç nihai belgede karşılaştırmalıdır.

### ARAYUZ_DEGISIKLIGI
1. **Tavan çözücüsünde bacak önceliği** (MIMARI §4.5). v1: "tavan küçültmesi bir coinde iki bacağı aynı
   katsayıyla küçültür." Bu belge: önce trend bacağı; c = 0'da ihlal sürerse carry bloğu tek κ_C ile (§3.3).
   Gerekçe K1-09. MIMARI'nin nihai çözücüsü farklıysa kapı onu sınar; ancak carry bloğu içindeki oranları bozan
   bir çözücü K1-09'u yeniden açar ve kilitten önce çözülmelidir.
2. **Sanal carry bacağı: tek defter** (MIMARI §4.4, §4.5, §4.7; KC-03). Kapı, motorun sanal carry defterini
   birebir kullanır: haftalık miktar × günlük κ^C, 01:00 geçerlilik, MIMARI'nin sıfır/sıfır artık kuralı. Kapıya
   özgü güncelleme kuralı yoktur (§5.1, §5.6). V5 bunu denetler. **MIMARI'ye arayüz notu:** sıfır/sıfır durumunda
   artığı trende yazmak (s^C = 0) carry maske çıkışlarının geç kapanma kaybını trende aktarır; "son sıfır olmayan
   payı taşı" kuralı daha muhafazakârdır. Hangi kural dondurulursa iki belgede aynıdır.
3. **Kilit sırası ve adları** (§2). Adım 0–8 ve "ÖN-KAYIT KİLİDİ" adı üç belgede aynı olmalıdır. 2. tur: kapının
   sentetik fikstürü (§8.5) Adım 3'te koşulur ve kilide girer.
4. **Ölçüt kümesi.** Round-1: K1 eşiği 0 → 0,10; yeni ölçüt K11. 2. tur: K1 eşiği ρ'ya bağlı K1\* (0,138–0,370);
   K1/K6/K8 kredilenen SR ile; K3/K4 yalnız rapor; K9 ve K11 eşdeğerlik testi; V4 → V4a/V4b; yeni V5, V6; çift
   seri kuralı. Ölçüt kodları K1–K11 korunur. **BANKA ve MIMARI'ye not:** MIMARI §1d ve BANKA §9'daki "SR_C* ≈
   0,16·SR_T" hesabı ρ = 0 içindir; kapının izin verdiği ρ = 0,30'da çarpan ≈ 0,44'tür (§8.4).
5. **Deneme sayacı.** Kapı satırı `A4-carry-kapisi`, varyant 1. Sayım kuralı §3.6 (maliyet ve alt küme koşuları
   varyant değildir). Teknik yeniden koşu +1.

### MIMARI'ye bağımlılıklar (kapı MIMARI'nin nihai metnini kullanır)
1. Maliyet çarpanının tanımı ve yöntemi: MIMARI §6 (tek tanım). Yöntem yazılmamışsa tam yeniden koşu.
2. Funding aralığı ve eksik kayıt kuralları (§4.2 asgari gereksinim; K1-01).
3. Delist sonrası tahakkuk yok (K1-02).
4. Q_max ve maske slipajı (K1-05).
5. Carry ölçeklemesinde max(Σ̂, Σ₀) (K1-10). Bu belge öneriyi destekler; karar MIMARI'nindir.
6. HAR ŝ² tanımı ve hedef birimi (K1-12 ii–iii).
7. s^trend'in bütün carry adayları için hesaplanması ve F30'un yalnız gerçek kayıtlarla kurulması (§3.2).
8. Carry'nin ex-ante vol'ü isim tavanlarından sonra %3'ün altında kalabilir. Kapı tavanlı nesneyi sınar.
9. κ^C tanımı, haftalık bant, sanal miktarlar ve icra artığı bölmesi (MIMARI §4.4–§4.7; KC-03). 2. turda MIMARI
   revizörü κ tanımını ve kırpma sonrası hedge'i (KC-04) netleştirir; kapı nihai metni kullanır.
10. Carry birimi değişmezi (V1; KC-09 carry tarafı): nesne adları MIMARI §3.3–§3.5 ve BANKA T4'teki adlarla aynıdır.

### Banka ön-kaydıyla bağlar
- Kapı NAV'ı = banka birincil NAV'ı (§3.1).
- DSR sayım kuralı banka ön-kaydındadır; kapı DSR'ı betimsel raporlar.
- "Az olaya dayanan senaryo kapıda bağlayıcı değildir" ilkesi (§6.6). Banka R12 (eski B12) yalnız rapordur; ilkeyle uyumlu.
- Kör hüküm ve hüküm sonrası hata kuralı (§7.2–7.3) banka ön-kaydındaki karşılığıyla aynı ilkeye dayanır.

---

## 12. Kullanıcı kararı: kapı → A/B (27 Eylül; ASAMA4B_KARAR §1)

*(Tarihsel kayıt; round-1 sayıları bağlayıcı değildir. Güncel eşikler §6.3 ve §15'tir.)*

**Durum: kapandı, açık soru değildir.** Kullanıcı 27 Eylül'de S-a için mevcut kararı seçti: **kapı → A/B kalır**;
kapısız A seçilmedi. Kapı, Codex'in KC-03/05/06/07 bulgularıyla düzeltilerek korunur (bu belgenin 2. turu). Codex
de canlı danışmada kapısız A'da ısrar etmediğini, düzeltilmiş kapının kabul edilebilir olduğunu yazdı
(`codex_cagrilari/20260927T_saclik_yanit.md`). Aşağıdaki round-1 gerekçesi tarihsel kayıt olarak kalır; sayıları
round-1 ölçütlerine aittir.

**2. tur notu.** Düzeltmeler kapıyı B aleyhine zorlaştırdı (§8.2, §8.5): yanlış ret artar, gizli fiyat bahsi
kanalında yanlış kabul azalır. Bu, A varsayılanıyla uyumludur. Kapı gizlice "kapısız A"ya çevrilmedi: fiyat
ortalaması için geçilemez bir TOST bağlayıcı konmadı (§6.4). §8.5 sentetik fikstürü kapının pratikte geçilemez
olduğunu gösterirse bu kilitten önce kullanıcıya sunulur; karar yine kullanıcınındır.

**Kapısız A lehine:**
1. Kapının gücü düşük. Gerçek SR 0,3'te yanlış ret ~%50–55; SR −0,2'de yanlış kabul ~%25 (§8.5).
2. Kapı, kararın istediği funding/fiyat ayrıştırmasını küçük ölçekte yapamaz. K4 ancak net funding gelirinin
   2–5 katı fiyat bahsini görür; K11 yalnız faktöre yüklenen bahsi yakalar (§8.3).
3. Bankada kötü bir carry, çıtaya yakın bir trendin kabul olasılığını ~8–10 puan düşürebilir (§8.4).
4. B, 21 ek sabit, ek parite yükü ve demo NAV'ında hedge yuvarlama sorunu getirir (MIMARI §7; K1-18).

**Kapı lehine:**
1. Kullanıcı kararıdır; jürilerin tek bağımsız kol dediği carry'ye ön-kayıtlı bir şans verir.
2. İyi bir carry bankada kabul olasılığını ~+4 puan artırır. Kötü carry'nin bedeli de küçüktür; iki yönde
   etki birkaç puandır.
3. K1 eşiği başabaş noktasına kondu (§8.4); kapı seyreltme sorusunda yansızdır.
4. B seçilirse bankadaki carry satırları, ters işaretli bir rejimde carry hakkında bilgi üretir.

**Sayılarla özet.** B/A seçiminin banka hükmüne beklenen etkisi iki yönde de birkaç yüzde puandır. Asıl fark
karmaşıklık ve ayrıştırma iddiasının zayıflığıdır.

**Kullanıcı kararı (27 Eylül): kapı → A/B.** Soru kapandı.

---

## 13. Kullanıcıya açık sorular (Adım 1'de, kilitten önce yanıtlanır)

**Hepsi yanıtlandı** (`ACIK_SORU_YANITLARI.md`: 1 → #1, 2 → #8, 3 → #9, 4 → #10, 5 → #11, 6 → #23, 7 → #13, 8 → #24).

1. ~~Kapı mı, kapısız A mı?~~ **Kapandı:** kullanıcı kararı kapı → A/B (§12; ASAMA4B_KARAR §1).
2. **Ayrıştırma yeterli mi?** 2. turda kapı fiyat ortalamasının sıfır olduğunu iddia etmez; fiyat kazancını karar
   serisinden dışlar ve dört faktör yüklemesini eşdeğerlik testiyle sınar (§6.4, §8.3). Bu, kullanıcı kararındaki
   "funding/fiyat ayrıştırması" tanımını karşılıyor mu (K2-02, KC-06)? Varsayılan: evet.
3. **K1 eşiği.** 2. tur: ρ'ya bağlı K1\* (0,138–0,370; SR_T,ref = 0,85). Seçenek: SR_T,ref = 0,60 (eşik 0,097–0,261,
   B lehine). Varsayılan 0,85 (§6.4). Round-1'deki sabit 0,10 KC-07 ile geçersizdir.
4. **K2 eşiği.** 3,0 mı 2,0 mı? Varsayılan 3,0 (görülmüş bilgiye karşı).
5. **Netleme kazancı** carry'ye yazılmıyor (muhafazakâr). Kabul mü?
6. **Delist senaryoları** bağlayıcı değil (az olay). Kabul mü?
7. **Kapı NAV'ı** banka birincil NAV'ına bağlı. Kabul mü?
8. **Eşdeğerlik toleransları** (2. tur): δ_b = 0,30 (K11), β toleransı 0,15 (K9), δ_P = %4 (K3/K4, yalnız rapor).
   Kabul mü? Değişiklik yalnız ekonomik gerekçeyle ve D P&L'i görülmeden.

---

## 14. Kırmızı takım bulgularının işlenişi

| Bulgu | Düzey | Karar | Nerede / gerekçe |
|---|---|---|---|
| K1-01 | CIDDI | KISMEN | §4.2 asgari gereksinim ve V1 fikstürü. Kuralın metni MIMARI §2.5–2.6'da; MIMARI revizörü düzeltir |
| K1-02 | CIDDI | KISMEN | §4.3 "delist sonrası tahakkuk yok" ve V1 fikstürü. Metin MIMARI'de |
| K1-03 | CIDDI | ilgisiz | Canlı emir zamanı; kapı geri testtir (MIMARI) |
| K1-04 | CIDDI | KISMEN | §6.6 gerçekleşen ve devreden kitapta S1/S2/S4 aşım raporu. T4 tanımı banka ön-kaydında |
| K1-05 | CIDDI | KISMEN | §4.3: kapı MIMARI'nin nihai Q_max ve tek sefer maske slipajını kullanır. Metin MIMARI'de |
| K1-06 | CIDDI | DUZELTILDI | §3.6, §6.3: tanım MIMARI §6'ya atıf (ana oturum notu 3); yöntem tam yeniden koşu; v1'deki "ücret sabit" ve "yeniden fiyatlama" kaldırıldı |
| K1-07 | DUZELTILEBILIR | ilgisiz | m_stres tanımı MIMARI §6'da |
| K1-08 | DUZELTILEBILIR | ilgisiz | Kapasite satırı banka R1'de |
| K1-09 | CIDDI | DUZELTILDI | §3.3 carry bloğu tek katsayı, önce trend; §5.1 sanal bacak = çözücü çıktısı; §5.6 V4 bölme formülü. ARAYUZ_DEGISIKLIGI 1–2 |
| K1-10 | DUZELTILEBILIR | KISMEN | §11 MIMARI bağımlılığı 5: öneri desteklenir; carry ölçeklemesi MIMARI'nin kararı |
| K1-11 | DUZELTILEBILIR | ilgisiz | Trend risk kontrolleri (MIMARI §3.3) |
| K1-12 | DUZELTILEBILIR | KISMEN | (i) §3.4: kapı yürüyen aylık HAR katsayılarını kullanır. (ii)–(iii) MIMARI §1b'de |
| K1-13 | CIDDI | DUZELTILDI | §2 ÖN-KAYIT KİLİDİ ve Adım 0–8; kapının trend çıktısı bağlayıcı olarak mühürlü |
| K1-14 | CIDDI | ilgisiz | Banka rejim-null |
| K1-15 | DUZELTILEBILIR | ilgisiz | Banka Z2 funding kaynağı |
| K1-16 | DUZELTILEBILIR | ilgisiz | Banka anonimleştirmesi; kapı yalnız D coinleriyle çalışır |
| K1-17 | DUZELTILEBILIR | ilgisiz | Canlı durum ve kaçırılan karar (MIMARI) |
| K1-18 | CIDDI | KISMEN | §6.6 hedge yuvarlama gün oranı (kapı ve demo NAV'ında); §9 demo ön-kaydı şartı. Lot yuvarlama kuralı MIMARI'de, demo parite koşusu bankada |
| K1-19 | DUZELTILEBILIR | ilgisiz | Felaket stopu (MIMARI §3.8) |
| K1-20 | DUZELTILEBILIR | KISMEN | Madde 5, 6, 10, 13 burada (§3.2, §5.6). Madde 11–12 banka, diğerleri MIMARI |
| K2-01 | CIDDI | DUZELTILDI | §2 ortak kilit, bağlayıcı "D P&L'inden sonra değişmez" cümlesi, trend ve D doğrulama çıktılarının mühürü |
| K2-02 | CIDDI | KISMEN | K11 eklendi (§6.3); K4 MDE §8.3; RAPOR cümlesi §8.5; kullanıcı sorusu §13.2. Tekil \|t\| < 2 şartları reddedildi: ortak Wald testine bilgi eklemeden H1 altında yanlış reddi ~%15–20 artırır; tekil t'ler raporlanır |
| K2-03 | CIDDI | KISMEN | Gerekçe banka seyreltmesiyle yeniden yazıldı (§8.4); K1 eşiği başabaşa (0,10) çekildi; "kapısız A" §12'de KARAR_DEGISIKLIGI_ONERISI / kullanıcı sorusu. Ana kural kapı → A/B olarak kaldı (ana oturum notu 2) |
| K2-04 | CIDDI | ilgisiz | Banka DSR çıtası. Kapıda DSR betimsel; N banka sayım kuralıyla |
| K2-05 | CIDDI | ilgisiz | Banka ölçüt gücü. Arayüz notu: kapıdaki delist ilkesi §6.6; banka R12 (eski B12) yalnız rapor |
| K2-06 | CIDDI | ilgisiz | Banka eşik gerekçesi. Kapıda denetlendi: hiçbir eşik rejim bilgisine dayanmaz (§6.5, §8.6) |
| K2-07 | CIDDI | DUZELTILDI | §7.2 kör hüküm; §7.3 sınıf kısıtı; hüküm sonrası hata yalnız A'ya götürür |
| K2-08 | CIDDI | ilgisiz | Bankadaki betimsel varyant koşuları |
| K2-09 | DUZELTILEBILIR | KISMEN | §3.6 sayım kuralı kapıya uygulandı. B9 banka ön-kaydında |
| K2-10 | DUZELTILEBILIR | ilgisiz | HAR prosedürü koşulları (MIMARI §1b) |
| K2-11 | DUZELTILEBILIR | DUZELTILDI | V4 formülü §5.6; K8 yeniden koşu §6.3; NW ℓ ∈ {4, 12}, B aleyhine seçim §6.2; F30 yalnız gerçek kayıt §3.2, §4.2. Andrews gecikmesi yalnız rapor |
| K2-12 | DUZELTILEBILIR | KISMEN | §10.2 kapı sabitleri üç kademeli etiketle. MIMARI §7 tablosu MIMARI revizöründe |
| K2-13 | DUZELTILEBILIR | ilgisiz | Banka D90 sıklığı |
| K2-14 | DUZELTILEBILIR | ilgisiz | Banka rejim-null |
| K2-15 | YOK | ilgisiz | İşlem gerekmez; kapıda banka atfı yok |

### Codex bulgularının işlenişi (2. tur)

| Bulgu | Düzey | Karar | Nerede / gerekçe |
|---|---|---|---|
| KC-01 | OLDURUCU | ilgisiz | Öteki belgede işlendi (BANKA rejim-null) |
| KC-02 | CIDDI | ilgisiz | Öteki belgede işlendi (BANKA sentetik kalibrasyon). Kapının kendi sentetik fikstürünün üreteci §8.5'te ayrıca dondurulur |
| KC-03 | CIDDI | DUZELTILDI | §5.1 tek sanal defter: kapı motorun MIMARI §4.4–§4.7 defterini birebir okur; günlük κ^C doğrudan uygulanır, kapıya özgü %25 κ bandı kaldırıldı (yalnız tanı). §5.6 sıfır/sıfır kuralı MIMARI'nin tek tanımı (0,5 kaldırıldı). V1 fikstürleri (κ 1 → 0,8; iki sanal bacak sıfırken artık), V5 defter özdeşliği. §11 ARAYUZ 2: 0/0 kuralı için MIMARI'ye muhafazakâr öneri; karar MIMARI'nin. K1-09/K2-11 iddiaları bu tanımla kapanır |
| KC-04 | CIDDI | ilgisiz | Öteki belgede işlendi (MIMARI §4.3–4.5). Kapı §3.3'te MIMARI'nin nihai çözücüsüne bağlandı |
| KC-05 | CIDDI | DUZELTILDI | V4a: Σ\|a^C_w\| (mutlak değerlerin toplamı) ≤ 0,10·Σ\|r^N_w\|; V4b: her hafta \|a^C_w\| ≤ 1,0·sd(r^N). Çift seri kuralı (§6.3): K1, K6, K8, K9, K10 gerçekleşen r^{N,g} = r^N + a^C serisinde de geçmeli. Codex örneği (+1/+1, +100/−100) V4a'yı ihlal eder; V1 fikstürü |
| KC-06 | CIDDI | DUZELTILDI | K9 ve K11 eşdeğerlik (TOST/kesişim-birleşim; %90 aralık tolerans içinde); δ_b = 0,30, β toleransı 0,15, ekonomik gerekçe §6.4. Fiyat ortalaması için TOST fizibilite aritmetiği §8.3: ekonomik tolerans (δ_P = %4) D'de geçilemez; bu yüzden K3/K4 yalnız rapor, bağlayıcı içerik "fiyat kazancı kredilenmez" kuralına (SR^K; K1/K6/K8) taşındı; Codex örneğinde SR^K ≈ 0,07, K1 geçmez. NW seçimi eşdeğerlikte büyük SE. §8.2/§8.5 sayıları olasılık iddiası değil; bileşik davranış kilitten önce dondurulmuş sentetik fikstürle ölçülür (§8.5). H1 ve RAPOR cümlesi yeniden yazıldı |
| KC-07 | CIDDI | DUZELTILDI | §8.4 korelasyonlu seyreltme: SR_C* = SR_T·g(ρ, k); Codex'in 0,37'si yeniden üretildi. K1\* = 0,85·g(ρ_K1, 1/3), ρ_K1 = gözlenen ρ'nun Fisher %90 üst sınırı, [0; 0,30]'a kırpılmış: eşik 0,138–0,370, formülle ve D P&L'ine bakmadan. Tavan etkileşimi: V6 (B trend ≠ A trend gün oranı ≤ %10). MIMARI §1d ve BANKA §9'daki ρ = 0 hesabı için §11'de not |
| KC-08 | CIDDI | ilgisiz | Öteki belgede işlendi (BANKA DSR; ASAMA4B_KARAR §1 S-c) |
| KC-09 | CIDDI | KISMEN | Carry tarafı: V1'e carry birimi (τ, tavan öncesi/sonrası) ve ω_C·L uygulanmış carry katkısı denetimi eklendi; nesne adları §11 bağımlılık 10. T4'ün aşama/nesne adlandırması ve toplam risk kuralı BANKA/MIMARI'de |
| KC-10 | CIDDI | ilgisiz | Öteki belgede işlendi (BANKA Kelly L seçimi) |
| KC-11 | CIDDI | ilgisiz | Öteki belgede işlendi (BANKA D90) |
| KC-12 | CIDDI | ilgisiz | Öteki belgede işlendi (MIMARI durum/olay günlüğü) |
| KC-13 | CIDDI | ilgisiz | Öteki belgede işlendi (MIMARI PSD) |
| KC-14 | DUZELTILEBILIR | ilgisiz | Öteki belgede işlendi (MIMARI §3.3) |

---

## 15. Uygulama netleştirmeleri (30 Eylül; kod öncesi, kilitten önce)

Belgenin açık bıraktığı 40 nokta (`ciktilar/v8_kapi_20260929_01/OLCUT_LISTESI.md` U-01…U-40) hiçbir D performans verisi
görülmeden karara bağlandı; gerekçeli tablo `ciktilar/v8_kapi_20260929_01/BELIRSIZLIK_COZUMLERI.md` (bu belgeyle
birlikte kilitlenir). Bağlayıcı olanlar:

1. **r^trend,net** (K1 ρ̂, K10): r^T_w = Σ_{h∈w}(trend fiyat + trend funding − trend maliyet) / (L · NAV_{w başı});
   gerçekleşen karşılığı r^{T,g} = r^T + a^T (trend icra artığı payı). Trend serisi yalnız ρ̂/ρ_üst için bellekte
   hesaplanır; yazılmaz, raporlanmaz (§2). ρ̂ ve ρ_üst iki çift için ayrı: (r^N, r^T) ve (r^{N,g}, r^{T,g}); n_w = iki
   serinin tanımlı olduğu hafta sayısı. ρ̂ = ±1 → atanh girişi ±(1 − 1e-12); ρ̂ tanımsız → ρ_üst = +1.
2. **Gerçekleşen seride kredilenen Sharpe:** SR^K(r^{N,g}) = [ort(r^F − r^C) + min(ort(r^P), 0) + **min(ort(a^C), 0)**]
   / std(r^{N,g}) · √52. İcra artığı yalnız aleyhe sayılır (fiyat kazancı kredilenmez ilkesi).
3. **K8:** yalnız alt isimler sıralanır; isim katkısı N_i = F_i + P_i − C_i (sanal carry bacağı, T0 → son hafta). BTC
   hedge'i sıralamaya girmez. "Hiç tutulmuş isim" = en az bir saat q^C,v_i ≠ 0. K8 yeniden koşusu m_c = 1, taban delist.
4. **MIMARI ile eşitlik:** kapı MIMARI'nin güncel kurallarını kullanır (sıfır/sıfır → son sıfır olmayan s^C, κ_etkin,t,
   V60 < 20M çıkışı, net kitaba yalnız-azaltma istisnası). V5, κ_etkin,t'yi de denetler. İcra artığının işlevsel tanımı
   §5.5 özdeşliğini kapatan terimdir (delist uzlaşma farkı dahil). C_h BTC hedge bacağının maliyetini içerir. BR-24 tanısı: sıfır/sıfır isim-günlerinde
   güncel kuralla carry'ye düşen artık ile s^C = 0 kuralında düşecek olanın farkı.
5. **İstatistik:** std'ler ddof = 1. NW: Bartlett w_j = 1 − j/(ℓ + 1), küçük örneklem düzeltmesi yok, regresyonda HAC
   sandviç; "büyük SE" parametre başına. K2 bootstrap istatistiği ort(r^F − r^C); dairesel blok, tek
   Generator(PCG64(20260928)) önce b = 4 sonra b = 12 (10.000'er), alt sınır 0,05 kantili. K5 aylık: ay toplamı /
   (ω_C·L·NAV_{ay başı}), 2023-10 … 2026-06 (33 ay, T0 sonrası bütün günler).
6. **V koşulları:** V1, V2, V5 ihlali teknik hatadır (§7.3 hüküm öncesi dalı; en fazla bir teknik yeniden koşu);
   V3, V4a, V4b, V6 ihlali esastır (sonuç A). V2 ve V5 her koşuda (ana, m_c = 2, 3, K8, delist), V3/V4/V6 yalnız ana
   koşuda. V2: günlük |fark| / NAV_{gün başı} ≤ 1e-8. V3 sıfır hafta = Pazartesi kararında carry kitabı boş. V4b sd'si
   143 haftalık r^N'nin tek sd'si. V5 toleransı κ, s^C için mutlak 1e-12, q^C,v için göreli 1e-12. V6: gün farklı ⇔
   max_i |w^T*_B,i − w^T_A,i| > 1e-9, ikisi de bant öncesi hedef, payda T0 sonrası bütün karar günleri. V1 carry birimi
   denetiminde 1e-9 göreli.
7. **Ölçek ve NAV:** NAV_{w başı} = Pazartesi 00:00 NAV'ı. Kapı NAV'ı 100.000 USDT (açık soru yanıtları #4, #13).
8. **Faktörler:** x_B, x_A haftalık basit getiri (Pazartesi 00:00 son kapanışından bir sonraki Pazartesiye); x_A carry
   aday evrenindeki alt isimlerin (BTC hariç) eşit ağırlıklı ortalaması. x_R, x_S: Pazartesi PIT sıralaması, aynı haftanın
   getirisi; üst/alt ⌊0,30·n⌋ isim; uzun − kısa = ort(uzun) − ort(kısa); sıralama bütün carry adaylarında.
9. **Hüküm ve mühür:** V2 farkı, V3 payı, V4a/V4b ve V6 oranları hüküm dosyasına (denetimde yalnız geçti/kaldı). K3/K4
   değer + "bağlayıcı değil" etiketi. Yeniden koşuların trend satırları hiç yazılmaz. Hüküm sonrası kabul edilen hata
   sınıfları yalnız §7.3'teki dördüdür.
10. **Kavramlar:** "Yeniden koşma yoktur" (§7.1) sonucu kurtarmak için değiştirilmiş koşu yasağıdır; §3.6 tam yeniden
    koşuları tek atış prosedürünün parçasıdır; §7.3 teknik yeniden koşu bütün prosedürün bir kez tekrarıdır.

11. **Kod sırasında çıkan netleştirmeler (U-41…U-55; 30 Eylül, kilitten önce):** faktör sıralamasında tanımsız değer
    ve tamsayı ⌊0,3·n⌋; V2/V5 zorunlu koşuları; κ, bağlama, gerçekleşen kitap tavanı, hedefe ulaşılamayan gün, hedge
    yuvarlama, funding dolgu, long/short bacak, sıfır/sıfır tanılarının hesap biçimi; V6'da A hedefinin B koşusunun
    durumu üzerinde hesaplanması; K8 hesaplanamazsa k8 koşusunun yapılmaması; mühürün bütün koşuların günlüklerini ve NAV
    yollarını kapsaması; sembol filtre kuralı; kilit kapsamının kapı kodunu içermesi. Gerekçeli tablo:
    `BELIRSIZLIK_COZUMLERI.md` Grup 3.
12. **Codex T15 düzeltmeleri (U-44, U-45, U-49, U-51 düzeltmeleri; U-56…U-61):** S4 bağlama/aşım ayrımı; gerçekleşen ve
    devreden kitap tavanları; long/short bacağın saat başı/sonu miktar işaretiyle ayrılması; V6'da A referansının B'nin
    sanal trend bacağı üzerinde kurulması; K8'de eşitlikte bile 6 ayrı isim; V2'de eksik günün başarısızlık sayılması;
    hata yolunun mühürlenmesi; kilit ön koşulları, kapsamı ve uzak commit bağı; V5'te kayıt sayısı ve son hash; ρ̂ ve
    NW'de sayısal korumalar. Gerekçeli tablo: `BELIRSIZLIK_COZUMLERI.md` Grup 4.
13. **Codex T16 düzeltmeleri (U-58 ve U-59 ekleri; U-62…U-64):** hata yolunun her koşulda mühürlü kalması; kilit kanıt
    zinciri, sabit kilit commit'i ve V1 raporunun bütün kod kimlikleri; V2'de bütün takvim günleri; V5'te saatlik
    tüketim denetimi; geç funding'in bacak ataması. Gerekçeli tablo: `BELIRSIZLIK_COZUMLERI.md` Grup 5.
14. **Codex T17 düzeltmeleri (U-58 ek 2, U-59 ek 2–3, U-63 eki; U-64 düzeltmesi):** banka koşucusunun hata yolunun da
    her koşulda mühürlü kalması; kilit kanıt zincirinin (duman, bitiş, toplama, eşdeğerlik) HAR, parametre ve kalibrasyon
    kodu kimliklerini ve kaynak hash'lerini kapsaması, kilit anındaki girdilerle karşılaştırılması; tam hash'li kilit
    commit'i ve yalnız origin'in doğrulanmış dalları; V5'te şekil/kapsam/sonluluk ön denetimi ve s^C'nin isim/saat
    bazında birebirliği; geç funding'in long/short bacak payının özgün saatin yönüne göre bölünmesi (T16'nın son işaret
    kuralının yerine). Gerekçeli tablo: `BELIRSIZLIK_COZUMLERI.md` Grup 6.
15. **Codex T18 düzeltmeleri (U-59 ek 4; U-65…U-67):** kalibrasyon toplamasının bitişte doğrulanan Düzey 2 dosyalarını
    tükettiğinin kanıtlanması (ortak klasör özeti; kilit karşılaştırır); banka tarafında B7 null ve yan birimlerde
    görülmüş gün maskesi, B5'te funding'in özgün epizota atfı (BANKA §3.7 netleştirme 11–12) ve M = B'de B5'in yalnız
    birincilde hesaplanması. Kapı ölçütleri ve eşikleri değişmez. Gerekçeli tablo: `BELIRSIZLIK_COZUMLERI.md` Grup 7.

16. **Codex T27 (kilit öncesi okuma, 1 Ekim 2026; D P&L'i ve banka görülmeden).**
    (a) **HAR geçiş kuralı.** §3.4'teki "o ay için ≥ 30 tamamlanmış haftalık gözlem" ifadesi, uygulanan HAR
    ön-kaydının (`ciktilar/v8_har_secimi_20260929_01/ONKAYIT.md` madde 6, 7 ve 12) koşullarıyla okunur: yürüyen aylık
    katsayı en az 30 eğitim gözlemi (havuzlu, hedefi tamamlanmış Pazartesi × coin satırı) ve tam rank (4) ister; ŝ² en
    az 8 artık haftası ister; biri sağlanmazsa o Pazartesi σ̂_EWMA kullanılır. Kapı kodu bunu `HarTakvimi.sonuctan`
    ile zaten uygular; yeni bir tahminci seçimi değildir.
    (b) **Delist senaryolarının gerekçesi.** Kapıda delist senaryoları (h_L %50, %90) rapordur. Gerekçe risk tercihidir
    ve önceden belirlenmiş kapsamdır: kapı funding gelirinin varlığını sınar; delist kuyruğu bankada R9/R12 olarak
    raporlanır. §6'daki "olay sayısı 30'dan az olduğu için bağlayıcı olamaz" gerekçesi geri çekilir (BANKA §5.5 ile
    tutarlı).
    (c) **§8.5 sentetik doğrulamanın ölçüt eşlemesi (BX-08; koşudan önce).** Haftalık birimler; yıllık ortalamalar
    /52, yıllık vol'ler /√52. 143 hafta. Fiyat r^P_w = μ_P/52 + Σ_k b_k x_{k,w} + e_w; x_k (x_B, x_A, x_R, x_S)
    bağımsız normal, her biri yıllık vol %15; e normal, var(e) = (0,15² /52)(1 − Σ b_k²). Funding eksi maliyet
    d_w = μ_d/52 + u_w, u AR(1) (φ = 0,5, durağan yıllık vol %3, başlangıç durağan dağılımdan). Maliyet sabit
    r^C_w = 0,009/52 (birim ölçekte yıllık %0,9; §8.3 aralığının ortası); r^F = d + r^C. r^N = r^F − r^C + r^P;
    sanal ve gerçekleşen seri aynı (a^C = 0, r^{N,g} = r^N; icra katmanı yok). Trend r^T_w = ρ·z_w + √(1 − ρ²)·ε_w,
    z = standartlaştırılmış r^N, yıllık vol %9 (ölçek ρ̂'yı etkilemez); T_g = T. s, N'nin oynaklığıyla funding eksi
    maliyetin Sharpe'ıdır (§8.2): μ_d = s · σ_N, σ_N = √(0,15² + 0,03²). K5: 33 ay; hafta w'nin ayı ⌊33·w/143⌋;
    aylık F − C = o aydaki d toplamı. K6 (m_c = 2): r^C iki katı (r^F aynı); K7 (m_c = 3): üç katı. K8: varsayım —
    en büyük katkılı isimlerin çıkarılması funding'in %20'sini götürür: K8 serisinde r^F' = 0,8·r^F (maliyet ve fiyat
    aynı), isim sayısı 40. K9 ve K11 faktörleri x_B, x_A (K9) ve dördü (K11). V1–V6 fikstürde yoktur (her biri geçti
    sayılır); P(B) = bağlayıcı K1, K2, K5–K11'in hepsinin geçme oranıdır ve "V'siz kapı geçiş oranı" diye adlandırılır.
    Senaryolar (7): H1 (s ∈ {0,30; 0,45} × ρ ∈ {0; 0,30}; b = 0, μ_P = 0); H0b (s = 0,40, μ_P = −%9, ρ = 0); H0c-
    ortalama (μ_d = %1, μ_P = %3, ρ = 0); H0c-faktör (s = 0,45, b_A = 0,40, öteki b = 0, μ_P = 0, ρ = 0). Her senaryo
    10.000 tekrar; tekrar üreteci `np.random.Generator(PCG64(SeedSequence((20260929, senaryo_no, tekrar_no))))`
    (senaryo_no yukarıdaki sırayla 1–7). Ölçütler kapının dondurulmuş kodu (`kapi/olcutler.py`) ile hesaplanır (K2
    bootstrap'ı kendi sabit tohumuyla). Çıktı: senaryo başına P(B), Wilson %95 aralığı ve ölçüt başına geçme oranı;
    `ciktilar/v8_kapi_sentetik_20261001/`. Sonuç eşikleri kendiliğinden değiştirmez; kilitten önce kullanıcıya sunulur
    ve sonuç dosyası kilit belgelerine girer.
    (d) **Teknik yeniden koşu ve kilit.** §7.3'teki teknik yeniden koşu, ilk `KILIT.json`'u değiştirmez; BANKA §3.7
    netleştirme 21 (g)'deki ek kilit kaydıyla zincirlenir.

Betimsel raporların ayrıntıları (BR-02 çeyrek tablosu, BR-03 bileşik MDD, BR-09 Andrews AR(1), BR-20 %90 blok bootstrap
tohum 20260929, BR-27 2×2 duyarlılık, δ_P haftalık /52, delist senaryoları tam yeniden koşu) tablodadır. §0 ve §12'deki
round-1 sayıları tarihseldir; güncel eşik §6.3 ve bu bölümdür.
