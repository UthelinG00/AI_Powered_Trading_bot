# v8 kilit adım 2: HAR/EWMA risk tahmincisi seçimi — ön-kayıt

Tarih: 2026-09-29 (koşudan ÖNCE yazıldı). **Revizyon 2 (koşudan ÖNCE):** Codex ön-kayıt incelemesinden
(`v8/codex_cagrilari/20260929T7_har_onkayit_inceleme_{istem,yanit}.md`) sonra madde 1, 4, 6, 8, 9, 10 netleştirildi,
11–13 eklendi; D'de HAR/EWMA sonucu hiç hesaplanmadı. Revizyon 1 metni `_arsiv/V8_HAR_ONKAYIT_20260929_01/`.
**Revizyon 3 (koşudan ÖNCE):** Codex doğrulamasından (`20260929T8_har_onkayit_dogrulama_*`) sonra madde 9, 11 ve 12
değişti (banka/canlı ŝ² MIMARI'deki yürüyen tanıma döndü; boş bootstrap çekişi teknik hata). Revizyon 2 metni aynı
arşivde (`ONKAYIT_v2.md`). Bağlayıcı prosedür: MIMARI §1b "Seçim prosedürü" (madde 1–9). Bu belge o
prosedürü tekrar etmez; belgenin açık bıraktığı uygulama ayrıntılarını koşudan önce sabitler. **P&L'siz:** strateji
koşulmaz, getiri/NAV hesaplanmaz. Sonuç kilit adım 4'te (ön-kayıt kilidi) hash'lenir.

## Girdi
- Veri: D (2023-07-01 → 2026-07-01), `adaptor/veri_yukleyici.py` ile hash doğrulamalı; veri kimliği
  5907a89bbe56adc0c65a80ad06c9e852b4e7bb58c40b000cab7615e7ddfd23f7 (D kesit denetimiyle aynı yükleme).
- Motor: v8/motor (evren, maske, hijyen, günlük getiri ve σ̂_EWMA tanımları) + v8/motor/har.py.
- Parametreler: `Parametreler()` varsayılanları (MIMARI §7); HAR alanları `har_*`.

## Uygulama ayrıntıları (belgenin açık bıraktığı yerler; sabit)
1. **PIT trend evreni (§1b.1).** Motorun kendi kuralıyla, işlem yapılmadan kurulur: T0 = 2023-10-01 00:00'dan her gün
   `maske_ilerlet` (ilk gün verinin başından), her ayın 1'i ve ilk gün `evren_sec` (histerezis önceki üyelerle).
   Pazartesi t'nin değerlendirme coinleri: evren üyeleri ∩ maskesiz ∩ işlem dışı değil (MIMARI §3.3'teki A_t).
   Maske geçmişi son hedef haftasının sonuna (2026-06-29) kadar ilerletilir; Pazartesi evreni 2026-06-22'ye kadar.
2. **Hedef (§1b.2).** t'den sonraki 7 günün günlük log getirileri r_{t+1..t+7}; getiri motorun tanımıyla
   (`hedef.coin_gunluk`: iki ardışık geçerli günlük kapanış; maskeli ve işlem dışı gün eksik). Yedisi de tanımlı
   olmalı. Y = Σr² × 365/7; Y = 0 olan coin-hafta dışarıda.
3. **HAR'ın sol tarafı (yorum).** y = ln(Σ_{k=1..7} r²_{t+k}): değerlendirme hedefinin kendisi (MIMARI "iki tahminci
   aynı hedefe karşı sınanır"; K1-12). `ml` tasarımındaki saatlik RV hedefi K1-12 ile değişti; HAR'ın sol tarafı da
   buna uyar. Tahmin σ̂²_HAR = (365/7)·exp(ŷ + ½ŝ²) (MIMARI'deki 52,14 = 365/7).
4. **RV_d ve özellikler.** `har.py`: saatlik getiri yalnız ardışık iki barda; eksik getiri > 8 ise (MIMARI §2.5(d)
   eşiği) RV_d tanımsız, aksi halde 24/n ölçeklenir; RV_d = 0 tanımsız; maskeli, §2.5(d) ve günlük kapanışı olmayan
   (§2.2 işlem dışı) gün tanımsız. l7 en az
   4/7, l30 en az 15/30 tanımlı gün; m son en fazla 365 günün ln RV ortalaması, en az 90 tanımlı gün. Özellik
   tanımsızsa o coin-hafta HAR için tanımsızdır.
5. **σ̂_EWMA.** Motorun `sigma_ewma_tahmin`i (max(σ_EW(20), σ_EW(90))), t'ye kadarki günlük getirilerle; %20 taban
   UYGULANMAZ (tahminci karşılaştırılır; taban her iki durumda boyutlamada ayrıca uygulanır). F_E = σ̂²_EWMA.
6. **Yürüyen HAR katsayıları (§1b.3).** Her ayın 1'i 00:00'da (ilk 2024-01-01), eğitim gözlemleri: T0'dan sonraki
   Pazartesiler s ve madde 1'deki değerlendirme coinleri, hedefi tamamlanmış olanlar (s + 7g ≤ tahmin anı), özelliği
   ve hedefi tanımlı olanlar. Havuzlu OLS (`har_katsayi`). En az 30 gözlem ve tam rank (4) gerekir; sağlanmazsa o
   ayın katsayısı tanımsızdır ve o aya düşen Pazartesilerde HAR tanımsızdır. Pazartesi t'de kullanılan katsayı:
   t'den önceki son ay başı tahmini.
7. **ŝ² (§1b "son 52 haftalık").** Yürüyen tahmin artıkları: 2024-01-01'den itibaren her Pazartesi s ve coin için
   e = y − ŷ (ŷ s'de geçerli katsayıyla). t'deki ŝ²: hedefi t'ye kadar tamamlanmış (s + 7g ≤ t) son 52 haftanın bütün
   artıklarının varyansı (havuzlu, ddof = 0). 8 haftadan az artık haftası varsa HAR o Pazartesi tanımsızdır.
8. **Değerlendirme kümesi (§1b.1, .7).** 2024-01-01'den son hedefi 2026-07-01'e kadar biten Pazartesiye kadar
   (son Pazartesi 2026-06-22) her Pazartesi; yalnız iki tahminin ve hedefin tanımlı olduğu coin-haftalar (eşli).
   En az bir satırı olan haftalar hafta sayısını (W) verir; 30'dan azsa prosedür koşulmaz, EWMA kalır.
9. **Karar (§1b.5).** (i) havuzlu ortalama QLIKE_HAR ≤ 0,95 × havuzlu ortalama QLIKE_EWMA (satır ortalaması).
   (iv) haftalık dairesel blok bootstrap (`har.dairesel_blok_bootstrap`): blok 4 TAKVİM haftası, 2.000 çekiş, tohum
   20260927. Takvim: ilk ve son değerlendirme haftası arasındaki bütün Pazartesiler; satırı olmayan hafta boş kalır
   (blok takvim bitişikliğini korur). Her çekişte ⌈W_takvim/4⌉ blok başlangıcı eşit olasılıkla, blok dairesel devam
   eder, ilk W_takvim hafta alınır; istatistik seçilen haftaların bütün satırlarında (QLIKE_HAR − QLIKE_EWMA)
   ortalaması. Hiç satır içermeyen bir çekiş olursa (tanımsız istatistik) koşu teknik hatayla durur (madde 11). Tek taraflı %95 üst sınır = çekişlerin 0,95
   kantili; < 0 olmalı. İkisi birden sağlanırsa HAR, değilse EWMA.
10. **Betimsel (§1b.6; bağlayıcı değil).** (ii) stres haftaları: değerlendirme haftaları içinde BTC'nin hedef
    haftasındaki getirisi ln(P_{t+7}/P_t) (günlük kapanışlar; biri eksikse hafta sıralamaya girmez, eşitlikte erken
    tarih) en kötü ⌈0,10·W⌉ hafta; bu haftalarda ortalama QLIKE
    farkı. (iii) Y/F oranının q95 ve q99'u, iki tahminci için. Ayrıca: satır ve hafta sayısı, iki ortalama QLIKE,
    bootstrap kantilleri (0,05; 0,5; 0,95), katsayı yolu, ŝ² yolu, dışarıda kalan coin-hafta sayıları (nedenleriyle).

11. **Teknik hata.** Veri kimliği yukarıdaki sabitle aynı değilse, değerlendirme satırlarından birinde Y, F_H,
    F_E ya da QLIKE sonlu ve pozitif (QLIKE için sonlu) değilse, ya da bir bootstrap çekişi hiç satır içermiyorsa koşu
    karar üretmeden durur (`TeknikHata`). Düzeltme
    yalnız sentetik fikstürle gösterilen hata için yapılır; teknik yeniden koşu deftere ayrı satır olarak girer
    (MIMARI §10 / CARRY §7.3 ilkesi). Prosedür ve eşikler değişmez.
12. **HAR seçilirse motorda kullanım (koşudan önce sabit).** Boyutlama σ̂_i = σ̂_HAR,i (taban %20, §3.2); HAR tanımsız
    olduğunda (2024-01-01 öncesi, ilk 8 artık haftası, özellik ya da katsayı tanımsız) σ̂_EWMA,i. D içindeki
    koşularda: özellikler karar günü t'de, katsayı t'den önceki son ay başı tahmini (bu betiğin yürüyen katsayıları),
    ŝ² bu betikle aynı küme (t'ye kadar hedefi tamamlanmış son 52 Pazartesi haftasının yürüyen artıkları; en az 8).
    Banka ve canlı: katsayı D'nin tamamında (hedefi 2026-07-01'e kadar biten bütün eğitim satırları) aynı OLS ile bir
    kez tahmin edilir ve dondurulur (§1b.8). ŝ² dondurulmaz: MIMARI §1b tanımıyla, o verideki (banka/canlı) Pazartesi
    haftalarında dondurulmuş katsayıyla üretilen tahminlerin yürüyen artıklarından (hedefi t'ye kadar tamamlanmış son
    52 hafta, en az 8; PIT) hesaplanır; 8 haftadan az artık varken σ̂ = σ̂_EWMA. Dondurulan katsayı (ya da eğitim
    yetersizse "tanımsız" ve eğitim sayısı) karar ne olursa olsun `sonuc.json`'a yazılır; son değerlendirme
    Pazartesisindeki (2026-06-22) yürüyen ŝ² tarihiyle bilgi olarak yazılır.
13. **Hafta sayıları.** Raporda W (satırlı değerlendirme haftası) ve W_takvim ayrı yazılır.

## Hesaplanmayan
Strateji P&L'i, NAV, getiri serisi, Sharpe ya da herhangi bir performans ölçütü. Bu koşu yalnız volatilite tahmini
isabetini ölçer.

## Görülmüş bilgi
`ml` tasarımcısı D'de (farklı hedef ve EWMA tanımıyla) HAR'ın QLIKE'ını EWMA-RV'den %14 düşük buldu (MIMARI §1b).
Bu ön-kayıt o sonucu bilerek yazıldı; karar kuralı MIMARI'de önceden sabittir, burada değiştirilmedi.

## Sonuç ve kayıt
Sonuç `sonuc.json` ve `RAPOR.md`'ye yazılır; kilit adım 4'te hash'lenir. HAR seçilirse D içindeki bütün koşularda
yürüyen aylık katsayılar kullanılır (2024-01-01 öncesi σ̂ = σ̂_EWMA); banka ve canlı için D'nin tamamında aynı
OLS ile bir kez tahmin edilip dondurulur (§1b.8). Deneme defteri: `V8-HAR-secimi`, "P&L'siz tahminci seçimi",
varyant 2 (EWMA, HAR), koşudan önce.
