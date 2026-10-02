## dogrulama

- KAPANDI — Bulgu 1: Maske geçmişi son hedefin tamamlandığı 2026-06-29’a kadar ilerletiliyor.
- KAPANDI — Bulgu 2: Günlük kapanışı olmayan günlerin RV değerleri artık dışlanıyor.
- KAPANDI — Bulgu 3: Aradaki boş haftalar korunuyor; bloklar dört takvim haftasından oluşuyor.
- KAPANDI — Bulgu 4: BTC getirisi iki uç kapanıştan hesaplanıyor; eksik kapanışlı haftalar sıralamaya alınmıyor.
- KAPANDI — Bulgu 5: Seçim betiğinin OLS çağrılarında en az 30 gözlem ve tam rank zorunlu; yetersizlikte katsayı tanımsız.
- KAPANDI — Bulgu 6: Değerlendirmeye girecek HAR varyansı ve kayıplar sonluluk kontrolünden geçiyor; taşma teknik duruş üretiyor.
- KAPANDI — Bulgu 7: Veri kimliği ön-kayıttaki sabitle hesaplamadan önce karşılaştırılıyor.
- KISMEN — Eksik karar 1: Takvim, eksik BTC kapanışı ve eşitlik sırası belirlenmiş; tamamen boş bootstrap çekişinin karar politikası eksik.
- KAPANDI — Eksik karar 2: Yetersiz/rank eksik eğitimde tanımsız HAR, geçersiz değerlendirme tahmininde teknik duruş belirlenmiş.
- KAPANDI — Eksik karar 3: Isınma ve tanımsızlıkta EWMA dönüşü; D içindeki günlük özellik ve olgunlaşmış artık güncellemesi tanımlanmış.
- KISMEN — Eksik karar 4: Eğitim kesiti ve kayıt eklenmiş; dondurulan ŝ² mimariyle çelişiyor, yetersiz eğitimde kayıt tamamen atlanıyor.

Bellekte çalıştırılan 10 sentetik test geçti. Dosya yazılmadı; D hesabı yapılmadı.

## yeni_bulgular

**[CIDDI] ONKAYIT.md:65 — Dondurulan ŝ² bağlayıcı HAR tanımını değiştiriyor**  
Yeni kural, banka/canlı için tam eğitim kümesinin örneklem içi artık varyansını donduruyor; MIMARI.md:108 ise son 52 haftanın yürüyen tahmin artıklarını şart koşuyor. `har_secimi.py:241` yeni kuralı uyguluyor; böylece seçimde sınanan varyans düzeltmesiyle sonraki kullanım ayrışıyor ve bağlayıcı belgeler çelişiyor.

**[ORTA] har_secimi.py:210 — Boş bootstrap çekişi sessizce EWMA kararına dönüşüyor**  
`dairesel_blok_bootstrap`, tamamen boş çekişte `NaN` döndürüyor; `np.quantile` bunu üst sınıra taşıyor ve `ust < 0` yanlış oluyor. W=30, W_takvim=130 ve kayıtlı tohumla kurduğum sentetik örnekte 2.000 çekişin biri boş kaldı; tüm mevcut farklar −0,1 olmasına rağmen koşul (iv) başarısız oldu. Bu durumun teknik duruş veya başka açık bir kuralla önceden tanımlanması gerekiyor.

**[DUSUK] har_secimi.py:232 — Stres haftası sayısı gerçek seçilen kümeyi göstermiyor**  
Rapor `len(stres)` yerine hedeflenen `ceil(0,10·W)` değerini yazıyor. Sentetik W=30 örneğinde yalnız bir geçerli BTC haftası seçildiği halde sayı 3 raporlandı; hiç geçerli hafta yoksa ortalama da `NaN` oluyor.

**[DUSUK] har_secimi.py:240 — Yetersiz son eğitimde dondurma kaydı kayboluyor**  
`beta_tam is None` olduğunda `dondurulan` alanı hiç yazılmıyor; boş eğitimle bunu doğruladım. Ön-kayıt madde 12’nin karardan bağımsız kayıt şartı için tanımsızlık durumu ve eğitim sayısı da kaydedilmeli.

## genel_hukum

Bağlayıcı koşuya henüz hazır değil; özellikle ŝ² tanımı belgeler arasında uzlaştırılmalı ve boş bootstrap çekişinin karar davranışı kilitlenmeli.