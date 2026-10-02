## dogrulama

B1: KAPANDI — Δ artık boşluk başlangıcında değil, olası tespit saatinde hesaplanıyor; pencere sınırı regresyonu geçti.  
B2: KAPANDI — Çözücü ve yeniden sınama ortak mutlak TOL kullanıyor; trend ikiye bölmeleri toleranssız sınırı hedefliyor.  
B3: KAPANDI — Bant kapatma net ve trend işaretlerini kapsıyor; kalan ihlalde bütün bantlar kapatılıyor.  
B4: KISMEN — Gerçek düşük hacimli giriş engellendi; K13(ii), §4.7’deki net hedef=sanal bacaklar eşitliğine belgelenmemiş istisna getiriyor.  
B5: KAPANDI — T4-d yalnız azaltmadan sonra uygulanıyor; bağlandığı 45 bağımsız örnekte nihai risk ve yalnız azaltma koşulları korundu.  
B6: KAPANDI — Tutulan sanal trend miktarı önceki değerden doğrudan alınıyor; gereksiz kayan nokta dönüşümü kaldırılmış.  
B7: KAPANDI — Maliyet çarpanı başlangıç kaydından okunuyor; farklı dış değer reddediliyor.  
B8: KAPANDI — Bacak geçmişi, budama ve funding döngüsü bağımsız; kapanış sonrası dolgu ve ters kayıt karşı örneği de geçti.  
B9: KAPANDI — Pazartesi λ’sı ve bağlayan bacak durumdan taşınıyor; hafta içi yeniden nötrleme ayrı kaydediliyor.  
B10: KAPANDI — Tutulan işlem dışı isimlerin β’sı da Pazartesi yeniden hesaplanıyor.  
B11: KAPANDI — Kısıtlar dışbükey; uygun küme aralık. İç aralık bulunuyor; uygun κ yokken minimum ihlalden ortak küçültmeye geçiş son çareyle uyumlu.  
B12: KAPANDI — Miktarlı düzeltmenin nakit ve başlangıç pozisyon değeri icra artığına birlikte giriyor.  
B13: KAPANDI — İşlem dışı tutulan mevcut long da haftalık funding tabanından geçiriliyor.  
B14: KAPANDI — Pozisyonsuz önceki adaylar durumdaki aday listesiyle histerezisten yararlanıyor.  
B15: KAPANDI — Hafta içi ortak matris son Pazartesi adaylarını da kapsıyor.  
B16: KISMEN — `kappa_etkin` miktar özdeşliğini sağlıyor; MIMARI §4.7 ve CARRY §5.1 hâlâ eski κ sözleşmesini veriyor.  
B17: KAPANDI — Eksik sıra dolgusu tanımlı sıraların gerçek medyanı; eşitlik karşı örneği geçti.

## x9_gerekcesi

İtiraz. Günlük κ artışının düşük hacimde sanal giriş oluşturabilmesi gerçek bir maliyet tanımı boşluğudur. Ancak bu, mevcut carry’nin zorunlu kapatılmasını tek başına gerektirmez; §4.1’in V30 histerezisine ve §4.4’ün çıkış kurallarına yeni koşul eklenmiştir. Y1 korunacaksa bağlayıcı mimariye açık tasarım değişikliği olarak işlenmeli; yalnız kod yorumuyla X9 kapatılamaz.

## yeni_bulgular

[ORTA] hedef_b.py:282 — K13(ii) hedef–sanal bacak eşitliğini bozuyor

Başlangıçta dolar/beta nötr carry ve net=sanal toplam koşullarını sağlayan sentetik örnekte, V60=15M sonrası gerçek hedef miktarı 0, sanal trend +100, sanal carry 0 oldu; reduce-only kapalıydı. Fark icra artığıyla muhasebeleştirilebilir, fakat MIMARI §4.7’nin hedef eşitliği sağlanmıyor. K13(ii) sonrası sanal miktarlar uzlaştırılmalı veya bu yeni artık kaynağı bağlayıcı sözleşmede tanımlanmalı.

## genel_hukum

46 mevcut test ve bağımsız sayısal kontroller geçti; 15 bulgu kapandı, B4/B16 sözleşme düzeyinde kısmen açık. Yeni sayısal tavan veya funding hatası doğrulamadım; belge–kod ayrılıkları nedeniyle koşulsuz onay vermiyorum.