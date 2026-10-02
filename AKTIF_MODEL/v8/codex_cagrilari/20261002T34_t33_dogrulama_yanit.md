## ikili_esle

Doğru: sonlu dört sütunlu girdilerde, pozitif sonlu toleransla ve kaynaklar yeterliyken, `en_cok` dışında yanlış kabul/ret üretmez. Her tur artıran yol arar; `onceki` ve `a_es` üzerinden geri sarma birebirliği koruyarak eşleşmeyi bir artırır. Yol bulunamaması mükemmel eşleşmenin bulunmadığını gösterir. T33 açığı kapanmış.

## yeni_bulgular

- **DÜŞÜK:** `pop()` nedeniyle arama BFS değil, LIFO; doğruluğu etkilemez.
- **DÜŞÜK:** Yeni testler geri sarmayı zorunlu kılan açık bir örneği doğrulamıyor.
- **ORTA, kaynak riski:** 5.000×5.000×4 fark tensörü float64 için tek başına yaklaşık 800 MB; `abs` geçicisiyle bellek ihtiyacı daha yüksek.

## genel_hukum

Tam takım geçince, bu incelemenin kapsamında **KILIT_TEKNIK_1 ek kaydının üretilmesine engel görmüyorum**; değerlendirme statiktir, kod/test çalıştırılmadı ve dosya yazılmadı.