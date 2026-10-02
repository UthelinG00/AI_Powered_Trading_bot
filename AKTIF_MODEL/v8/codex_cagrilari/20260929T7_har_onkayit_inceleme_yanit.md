## bulgular

**[CIDDI] har_secimi.py:51 — Maske geçmişi son hedef haftasını kapsamıyor**  
`pit_evren`, 2026-06-22’de duruyor; buna karşılık son değerlendirme hedefi 2026-06-29’a kadar günlük getirileri kullanıyor. Bu aralıkta yeni tetiklenen maske veya §2.5(d) günleri kaydedilmediğinden, ön-kayıt madde 2 gereği dışlanması gereken hedefler değerlendirmeye girebilir. Evren gözlemleri son Pazartesi’de bitebilir; hijyen geçmişi son hedef tamamlanana kadar ilerletilmelidir.

**[ORTA] har_secimi.py:105 — Günlük kapanışı olmayan geçmiş günler RV’den çıkarılmıyor**  
Ön-kayıt madde 4, işlem dışı günlerin RV’sini tanımsız sayıyor; MIMARI §2.2’ye göre son saat barının bulunmaması da işlem dışı olma nedenidir. Buradaki filtre yalnız maske dönemlerini ve `(d)` kayıtlarını kullanıyor; kapanış eksikliğini denetlemiyor. Sentetik örnekte son saat barı bulunmayan günün RV’si tanımlı kaldı: sonraki geçerli Pazartesilerin l7/l30/m özelliklerine ön-kaydın dışladığı günler girebilir.

**[ORTA] har_secimi.py:183 — Boş haftalar bootstrap’ın takvimini sıkıştırıyor**  
Kod, hiç eşli gözlemi kalmayan haftaları kaldırdıktan sonra ardışık dört liste elemanını blok sayıyor. Arada boş hafta varsa bu blok dört takvim haftasından uzun olur; MIMARI’nin “4 haftalık blok” tanımıyla eşdeğerliği kaybolur. Ön-kayıt ve kod bu durumu açıkça çözmeli; bağımlılık yapısı ve güven sınırı etkilenebilir.

**[ORTA] har_secimi.py:199 — Eksik BTC getirileri stres sıralamasında sıfır katkı alıyor**  
`np.nansum`, eksik günlük getirileri atlıyor; yedi günün tamamı eksikse haftalık getiriyi sıfır yapıyor. Bu, ön-kayıttaki yedi günlük BTC getirisini hesaplamakla aynı değildir ve en kötü %10 haftayı değiştirebilir. Etki betimsel raporladır; doğrudan (i)/(iv) kararına girmez.

**[ORTA] motor/har.py:87 — Boş eğitim kümesi geçerli katsayı gibi kabul ediliyor**  
`lstsq` için eğitim yeterliliği denetlenmiyor; sentetik boş girdide dört sıfır katsayı döndüğünü doğruladım. Böylece eğitim bulunmayan ayda `ŷ=m` üretilip tahmin tanımlı kabul edilebilir; rank eksikliğinde de çözüm politikası örtük olarak NumPy’ye bırakılır. Eğitim yetersizliğinin teknik duruş mu, tanımsız HAR mı olduğu koşudan önce belirlenmeli.

**[ORTA] har_secimi.py:179 — Eşli değerlendirmede sonlu HAR tahmini koşulu eksik**  
Ön-kayıt madde 8 iki tahminin de tanımlı olmasını istiyor; kod `y_hat` için yalnız `None` denetliyor, üretilen `F_H` ve kayıpların sonluluğunu denetlemiyor. Sentetik `ŷ=1000` girdisi sonsuz varyans ve kayıp üretti; bu tür değerler bootstrap’a taşınıp teknik geçersizliği EWMA kararı gibi gösterebilir. Sonlu olmayan değerler için önceden belirlenmiş davranış gerekir.

**[ORTA] har_secimi.py:89 — Ön-kayıttaki veri kimliği zorunlu doğrulanmıyor**  
Yükleyici mevcut dosyaların manifest hash’lerini denetliyor; betik ise dönen toplam veri kimliğini yalnız yazdırıyor, ön-kayıttaki sabitle karşılaştırmıyor. Yükleyici dosyaları mevcut ZIP’lerden topladığı için eksilmiş bir dosya kümesi farklı kimlikle hesaplamaya devam edebilir. Kimlik eşitliği sonuç hesaplanmadan zorunlu tutulmalıdır.

## yorumlar_3_5_6_7

- **3 — kabul:** Günlük getirilerin yedi günlük kareler toplamını öğrenmek §1b.2’nin hedefiyle tutarlı; günlük RV çapasıyla haftalık hedef arasındaki sabit ölçek farkını serbest sabit terim karşılayabilir.
- **5 — kabul:** §1b tabansız tahminciyi, §3.2 boyutlamadaki tabanı tanımlıyor; iki tahminciye de taban uygulamamak simetrik.
- **6 — kabul:** Tarihsel PIT evreninden tamamlanmış Pazartesi hedefleriyle eğitim savunulabilir bir netleştirme; MIMARI bütün aday coinlerle veya günlük gözlemlerle eğitim zorunluluğu koymuyor.
- **7 — kabul:** Havuzlu artık varyansı ve `ddof=0`, belirtilen varyans düzeltmesinin makul uygulaması; tek başına HAR lehine sistematik avantaj kanıtı değildir.

## eksik_kararlar

- Boş değerlendirme haftalarının bootstrap takvimindeki yeri; eksik BTC haftalarının stres sıralamasındaki işlemi ve eşit getirilerde tarih önceliği.
- Boş/yetersiz/rank eksik eğitim ile sonlu olmayan tahminlerde uygulanacak kesin duruş veya geri dönüş kuralı.
- HAR seçilirse ilk sekiz artık haftası dolmadan ve sonraki tanımsız günlerde kullanılacak tahminci; günlük motor kullanımında ŝ²’nin güncellenme takvimi.
- Banka/canlı için son katsayı dondurmasının kesin eğitim kesiti ve üretilecek kayıt; betik şu anda yalnız yürüyen aylık katsayıları çıkarıyor.

## genel_hukum

Bağlayıcı koşuya henüz hazır değil; özellikle son hedef haftasının hijyen geçmişi ve RV geçerlilik filtresi düzeltilmeli, eksik kararlar kilitlenmeli. İncelenen kodda katsayı/artık olgunlaşma sınırları, geçmişe dayalı özellikler ve EWMA, OLS çapası, eşli kayıp hesabı ve üst %95 kantil yönü doğru; D sonucu hesaplamadım ve dosyalara yazmadım.