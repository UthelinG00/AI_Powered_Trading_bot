## bulgular

1. **[CIDDI] Üst sınırın ölçüt seti yanlış sabitlenmiş — §3.7 Düzey 2-a; §3.3 kural 2–4; Düzey 1 eşik kuralları —** “Sekizinin hepsi geçer” tanımı, B2/B5/B10’un rapora indirilebilmesini kapsamıyor. Rapora indirilmiş bir ölçütü kalibrasyonda veto olarak tutmak kabul oranını küçültür; bulunan oran gerçek bağlayıcı set için üst sınır olmayabilir. B2 raporsa d* da tanımsız kalabilir. **Düzeltme:** KABUL_B7siz, Düzey 1 sonunda **bağlayıcı kalan** ölçütlerin kesişimi olsun; B3/B4’ün olası 0,40 eşikleri de aktarılsın. Tam banka kabulü B9’u ayrıca içerir: `KABUL_tam ⊆ KABUL_B7siz ∩ B7`. B7’nin d*, e_B5 veya diğer eşikleri değiştirdiği başka bir mekanik yol bulmadım.

2. **[ORTA] Üst sınırın tahmini, üst sınırın kendisi gibi etiketleniyor — §3.7 Düzey 2-a; §8.2/4 ve 12 —** Olasılıklar arasındaki eşitsizlik geçerlidir; örneklem oranı p̂ ise bilinmeyen olasılığın kesin üst sınırı değildir. 0/100 için iki taraflı %95 Wilson üst ucu `1,96²/(100+1,96²) ≈ %3,70` doğrudur. Ancak 5/100 kapıyı geçer ve Wilson üst ucu yaklaşık **%11,18** olur. **Düzeltme:** p̂’yi “üst sınırın nokta tahmini”, Wilson üst ucunu ayrı raporlayın. “>%5 → bekle” anlamlı bir tarama kuralıdır; %95 güvenle yanlış kabul ≤%5 kanıtı olarak sunulmasın. Sonuç yalnız tanımlı sentetik üreteç için geçerlidir.

3. **[ORTA] Tohumlar tek başına sıra bağımsızlığını tanımlamıyor — §3.5.1; §3.7 tohumlar ve tekrarlanabilirlik —** `hash(...)` algoritması, girdilerin bayt gösterimi, RNG türü/sürümü ve “coin sırası” tanımlanmamış. Tek iş parçacığı; dosya/küme dolaşımı, sözlük kuruluş sırası, eşitlik bozma, duvar saati veya süreçler arası ortak RNG sorunlarını çözmez. **Düzeltme:** SHA-256 tabanlı kanonik tohum türetimini, RNG’yi, sıralamaları, zaman kaynağını ve sonuç serileştirmesini sabitleyin. Tekrar denetimi A/B ve koşu türlerini kapsasın; farklı işçi sayısı, ters sıra ve kesinti/devam altında karşılaştırma içersin.

4. **[ORTA] Tamamlanmış birimi atlama sözleşmesi eksik — §3.7 “Kesinti ve devam” —** Atomik yeniden adlandırma yarım dosyanın görünmesini azaltır; fakat atlamadan önce içerik hash’inin, beklenen kimliğin ve girdilerin doğrulanması zorunlu yazılmamış. Kod hash’lerinin birbirine eşit olması, beklenen sürüm olduklarını kanıtlamaz. B10 çıkarma kimliği de ilgili mimarinin birincil koşusundaki ilk 10 alta bağlıdır. **Düzeltme:** Beklenen birim listesini ve parametre/HAR/ortam kimliklerini sabitleyin; yalnız bütünlüğü doğrulanmış dosyaları atlayın. B10’a birincil sonuç ve çıkarılan coin kimliği bağlansın; geçici/bozuk dosyalar yeniden koşulsun. On rastgele tekrar bu bütünlük denetiminin yerine geçmez.

5. **[DUSUK] Eski ifadelerin geçersizliği yerinde işaretlenmemiş — §10/13; Ek C eski K2-14 ve KC-02 satırları —** “Adım 3 … B7 kuantilini … sabitler”, “q95 ayar kuralı” ve doğrudan “B7 dahil … ölçülür” ifadeleri duruyor. Bunlar tarihsel bölümlerde; §10/15 ve Ek C sonu yeni kuralı açıklıyor, dolayısıyla yürürlükte ikinci bir q90 kuralı bulmadım. **Düzeltme:** Eski satırlara §0.2/3. revizyon tarafından değiştirildiklerini belirten kısa atıf ekleyin. Düzey 2-b’deki q90 karşılaştırması betimsel olarak kalabilir.

## sorular_1_6

1. **KISMEN —** B7 bağımsız vetodur; eşiklere geri besleme yok. Ancak rapora indirilen B2/B5/B10’u zorunlu tutan sekizli kesişim üst sınırı bozabilir.
2. **EVET —** Belgelenen kronolojiye göre meşru, sonuç öncesi revizyondur; §1.2 ihlali değildir. 475’inci değer doğru ampirik kuantildir; tek başına tam %5 test garantisi değildir.
3. **KISMEN —** Tek κ=0, A/B ve 1+2+10=13 koşu doğru. 100 yol kaba kontrol sağlar; Wilson %3,70 doğru, nokta eşiği güven garantisi değildir.
4. **EVET —** Ekonomik karar girdisi açıkça dışlanmış; mekanik geri besleme yok. Yalnız A ve 50-null sonuçları, 500-null banka testinin gücü için kaba vekildir.
5. **HAYIR —** Tek iş parçacığı ve atomik yazma yeterli değil; kanonik tohum/sıra, girdi doğrulaması ve kesinti-paralellik karşılaştırması eksik.
6. **KISMEN —** 2.600+2.540=5.140 ve eski 255.600 doğru; on doğrulama tekrarı ayrıca. Eski ifadeler tarihsel bölümlerde duruyor; hız ölçümünü bağımsız doğrulamadım.

## genel_hukum

**Mevcut metin Adım 4 kilidine hazır değil:** özellikle bağlayıcı ölçüt seti düzeltilmeli, tekrarlanabilirlik ve devam sözleşmesi tamamlanmalıdır. q95’e sonuç görülmeden sabitleme ve B7’siz kabul üzerinden üst sınır yaklaşımı istatistiksel olarak savunulabilir; eski 255.600 koşuluk plana dönmek gerekmiyor.