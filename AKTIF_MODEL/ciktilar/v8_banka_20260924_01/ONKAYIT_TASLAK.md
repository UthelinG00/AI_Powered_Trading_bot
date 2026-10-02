# v8 mühürlü test bankası — ön-kayıt TASLAĞI

Durum: **TASLAK, damgalanmadı, seçim yapılmadı.** Kullanıcı onayından sonra `ONKAYIT.md` adıyla damgalanır.
Tohum ve seçim ancak damgadan sonra hesaplanır.

## 1. Bağlam ve kararlar (kullanıcı, 2026-09-24)

| Konu | Karar |
|---|---|
| Amaç | REV1'den bağımsız yeni model adayı (v8) |
| Hedef | Mutlak getiri. Zirveden düşüş en fazla %30. Tasarım hedefi: geri test DD'si yaklaşık %15–20 |
| Kapsam | Sınırsız: coinler, zaman dilimleri, strateji tipleri, fiyat dışı veri |
| Kapalı aileler | REV1'de kapanan aileler yeni gerekçeyle yeniden açılabilir; ret geçmişi yanında gösterilir |
| Doğrulama | Mühürlü test bankası, tek atış; ardından ileri demo |
| Banka payı | Uygun coinlerin %40'ı |
| Uygunluk | En az 3 yıl (≥36 ay) 1h geçmiş |

Gerçek para ve mainnet işlem yasağı değişmez. REV1 DEMO ve E3 arşiv ikizi süreci bu işten bağımsızdır.

## 2. Denetim bulguları (0a)

- **Geçmiş veri kullanımı:** Projedeki bütün veri cache'leri 2023-06-13 ile 2023-06-24 arasında başlıyor ve yalnız BTC/ETH içeriyor. 2023-06 öncesi dönem projede kullanılmamış.
- **Altcoinler:** Hiçbir altcoin verisi projeye girmemiş. D6 XRP/LINK/DOGE'yi aday olarak adlandırmıştı, fakat "VERİ BEKLİYOR" durumunda kaldı ve hiç koşulmadı.
- **Bilinen sızıntı:** 2026-09-23 beyin fırtınası ajanları bazı sembollerin (XAU, XAG, PAXG, demo BTC/ETH) güncel ticker/premium değerlerine baktı. Bunlar anlık değerlerdi, tarihsel seri değildi. XAU, XAG ve PAXG zaten uygun evrende değil.

## 3. Uygun evren

- **Kaynak:** data.binance.vision `futures/um/monthly/klines/<SYM>/1h/` klasör listesi (2026-09-24). Ham liste `um_1h_aylar_ham.json` (sha256 5ad6f895…).
- **Kural:** Aşağıdaki koşulların hepsi.
  - USDT ile kote edilen USDⓈ-M perp; vadeli kontrat (alt çizgili) değil.
  - İlk aylık 1h dosyası ≤ 2023-09.
  - En az 36 aylık dosya.
  - Hariç tutulanlar: stablecoinler, `BTCDOMUSDT`, `DEFIUSDT`, BVOL endeksleri, BTC ve ETH.
- **Listeden çıkmış coinler:** 36 ay koşulunu sağlıyorsa evrende kalır. Bu, hayatta kalma yanlılığını azaltır. 8 coin: BTCST, BTS, EOS, HNT, MATIC, SRM, SXP, TOMO.
- **Sonuç:** **200 coin**. Liste `uygun_evren.json` (sha256 9148fb8e…).
- **Listeleme yılı kohortları:** 2020: 75 · 2021: 49 · 2022: 21 · 2023: 55.
- **Sınır:** 36 aydan kısa sürüp listeden çıkan 20 eski coin (LUNA, BZRX, KEEP vb.) evren dışında. Hayatta kalma yanlılığı tamamen giderilmiş değildir.

## 4. Banka (mühürlenecek)

**K — kesitsel banka:** 200 coinin 80'i, bütün dönemleriyle. Kohort içinde tabakalı basit rastgele seçim yapılır;
kohort payları en büyük kalan yöntemiyle 80'e tamamlanır: 2020: 30 · 2021: 20 · 2022: 8 · 2023: 22.

**Z — zaman bankası (bütün coinler, BTC/ETH dahil):**
- **Z1:** 2023-07-01 00:00 UTC öncesi. 2021 boğası ve 2022 ayısı buradadır.
- **Z2:** 2026-07-01 00:00 UTC ve sonrası. Mühür tarihine kadarki bölüm banka testinde kullanılır; sonrası ileri dönem.

İstisna: BTC/ETH'nin 2023-06-24 → 06-30 saatleri eski cache'te zaten görülmüştür; bu 7 gün Z1'den düşülür.

**Geliştirme alanı (D):** Kalan 120 coin ve BTC/ETH, **2023-07-01 → 2026-07-01** (36 tam ay).
Ajanlar ve analizler yalnız D içinde çalışır.

## 5. Tohum ve seçim (damgadan sonra)

1. Bu belge `ONKAYIT.md` olarak kaydedilir; SHA-256'sı ve UTC zamanı `DAMGA.json`'a yazılır.
2. Damga zamanından en az 15 dakika sonraki ilk drand mainnet turu (League of Entropy, herkese açık ve
   doğrulanabilir rastgelelik) belirlenir.
3. **tohum** = SHA-256(`ONKAYIT.md` sha256 hex ‖ drand turu randomness hex). İlk 16 hex tamsayıya çevrilir.
   Böylece belge yazılırken tohum bilinemez ve seçim sonradan değiştirilemez.
4. drand erişilemezse yalnız belge hash'i kullanılır ve bu durum raporlanır.
5. Seçim: Python 3.12 `random.Random(tohum)`. Kohortlar 2020 → 2023 sırasıyla, her kohortta semboller alfabetik
   sıralı; `sample(liste, kohort_payı)` ile seçilir. Kod `banka_sec.py` damgadan önce yazılır ve hash'i belgeye eklenir.
6. Banka listesi `BANKA_MUHURLU.json` dosyasına yazılır; hash'i damgaya eklenir.

## 6. Erişim kuralları

- **Veri indirme:** K coinlerinin hiçbir dönemi ve bütün coinlerin Z1/Z2 dönemleri banka testi anına kadar
  indirilmez. D verisi ay-hizalı dosyalarla (2023-07 → 2026-06) indirilir; her indirme listesi kullanıcı onayına sunulur.
- **Ajanlar:** Yalnız D coin listesini alır.
  - `BANKA_MUHURLU.json` okunmaz.
  - Banka coinlerine özel performans araştırması yapılmaz.
  - Tasarımlar belirli coin adlarına değil, kurallara dayanır (örneğin "likiditeye göre ilk N").
  - Genel piyasa bilgisi (2022 ayı piyasası gibi) sızıntı sayılmaz ama tasarım gerekçesi olarak kullanılmaz.
- **REV1 ile ayrım:** REV1 E3 arşiv ikizinin BTC/ETH Z2 verisi ve çıktıları v8 ajanlarına verilmez.

## 7. Deneme defteri ve banka testi iskeleti

- v8 geliştirme koşuları `V8_DENEME_DEFTERI.csv`'ye koşudan önce yazılır: aile, varyant sayısı, D kesiti.
  Banka testinde deneme sayısı çoklu test düzeltmesine girer.
- Banka yalnız bir kez açılır. En fazla 3 dondurulmuş aday girer ve Holm düzeltmesi uygulanır.
- Adaylar kod hash'iyle dondurulur. Kabul/red kriterleri Aşama 4 sentezinde, banka açılmadan önce, ayrı bir
  ön-kayıtla yazılır. Hedef: %30 DD sınırı, mutlak getiri ve maliyet stresi (1× ve 2×).
- Banka testini geçen aday ileri demoya gider. Bu kapsam kararıdır ve ayrı demo hesabı gerekebilir.

## 8. Sınırlar

- Kripto piyasaları yüksek korelasyonlu. Banka coinleri D ile aynı dönemde korele hareket eder; kesitsel banka
  bağımsız örneklem değildir. Z1 (farklı rejim) bu yüzden ayrı raporlanır.
- data.binance.vision dosyaları sonradan yeniden yüklenebilir. İlk indirmenin hash'i bağlayıcıdır.
- Birkaç sembolde yeniden adlandırma ya da taşınma olabilir (FTM, AGIX, OCEAN gibi). Veri indirildiğinde
  süreklilik denetlenir. Sorunlu semboller seçimden sonra çıkarılmaz; raporlanır.
