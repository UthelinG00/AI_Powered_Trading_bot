## netlestirmeler

İnceleme: `b908b74..78b7c56` ve çalışma kopyasındaki ilgili dosyalar; yalnız statik okuma, kod/test çalıştırılmadı. Aşağıdaki yollar `AKTIF_MODEL/v8/` altındadır.

13 UYUMLU — `banka_kos/long_beta.py:56` — Karar sırası, kayıt biçimi, aylık/ara gün ayrımı, bütçe, devreden emir ve reduce-only kuralları korunuyor; saat döngüsü motorla aynı ve yürütücü A/B için aynı A kitabını kuruyor.

14 SAPMA — `banka_kos/tanilar.py:140` — R6 iptal edilen niyetlerin gecikmesini dışlıyor ve sonraki karara yetişmeme oranını niyetin nihai kapanış sınıfıyla karıştırıyor; B’nin R5 güvenlik ölçeklemesi sayacı da eksik kayıt nedeniyle sıfırlanıyor.

15 SAPMA — `banka_kos/tanilar.py:280`, `banka_kos/rapor.py:195` — R2 gün başı ağırlığı gece yarısı uzlaşmasından sonraki pozisyonu alabiliyor; R4 takvim blokları yerine sıkıştırılmış ortak gözlemleri kullanıyor.

16 UYUMLU — `banka_kos/tanilar.py:355`, `banka_kos/yurutucu.py:197`, `banka_kos/rapor.py:243` — Günlük ayrıştırma gün başı NAV’a bölünüyor, Kelly carry serisi yalnız 1× maliyette üretiliyor ve bu birimlerin ölçümü BK-13 gereği B5’siz kalıyor.

Ek doğrulamalar: `durum_izi` motorun indirgeme fonksiyonunu kayıt sırasıyla uyguluyor. R7’nin `σ̂ = k·s/wᵘ` çıkarımı T4-a günleri dışlandığında doğru; yedi günlük hedef HAR tanımıyla aynı. Koşu sonu maske geçmişi burada gerçekleşmiş hedefi ölçüyor, karar girdisini değiştirmediğinden tek başına PIT ihlali değil. R2 katkı toplamı özdeşliği korunuyor; ancak bu, katkının doğru dağıtıldığını kanıtlamıyor.

## bulgular

1. **[CIDDI] CHECKSUM kapısı bağlayıcı veri kimliğini korumuyor** — `banka_kos/veri_denetim.py:32` — Son satır önceki kimliği tamamen eziyor; ilk doğrulanmış hash sonradan başka eşleşen hash/checksum çiftiyle değiştirilebilir (§2.3). Ayrıca `TAMAM` satırında iki hash de eksikse `None == None` ile geçiliyor; her `TAMAM` dışı durum ise CHECKSUM hatası sayılıyor — İlk bağlayıcı kimliği koru, hash alanlarını doğrula ve bulunamayan dosya/indirme hatası/onarılamayan doğrulama hatasını ayrı sınıflandır.

2. **[CIDDI] Betimsel R3 hesabı hüküm üretimini durdurabilir** — `banka_kos/long_beta.py:244`, `banka_kos/hukum.py:198` — Birincil getiri serisinin volatilitesi sıfırken R3 ölçeği sıfır, regresyon matrisi tekil olur ve `inv` istisnası bütün `hukum()` çağrısını keser — Yetersiz gözlem ve sıfır volatiliteyi açık “tanımsız” sonuçla ele al; betimsel satır bağlayıcı hükmü engellemesin.

3. **[ORTA] R6 gecikmesi ve tamamlanmama oranı yanlış örneklemden** — `banka_kos/tanilar.py:145` — İptalle kapanan niyetler gecikme dağılımına girmiyor; sonraki kararı aşarak korunup daha sonra dolan niyet ise zamanında tamamlanmış gibi sayılıyor — Gecikmeye bütün kapanmış niyetleri kat; sonraki karar anındaki kalan miktarı nihai kapanıştan ayrı izle.

4. **[ORTA] R2 önceki gün sonu pozisyonunu kaybedebiliyor** — `banka_kos/tanilar.py:280`, `banka_kos/yurutucu.py:130` — `searchsorted(..., side='right')`, gün sınırındaki uzlaşmayı da uygulayıp pozisyonu sıfırlar; NAV ise bu uzlaşmadan öncedir, dolayısıyla BTC katkısı yanlışlıkla artığa aktarılır — Gün başı ağırlığı `nav` kaydı anındaki durumdan veya kesinlikle sınır öncesi pozisyondan al.

5. **[ORTA] R4 takvim ve stres örneklemi kayıyor** — `banka_kos/rapor.py:188` — Eksik/görülmüş günleri çıkardıktan sonra her 30 gözlemi birleştirmek, D başlangıcına bağlı ardışık 30 takvim günü tanımını bozuyor; BTC q5 eşiği de bütün D yerine REV1 ile ortak günlerden hesaplanıyor — Önce D’ye bağlı takvim bloklarını ve D içi BTC eşiğini kur, ardından ortaklık/dışlama kurallarını uygula.

6. **[ORTA] B’de R5 T4-a sıklığı sessizce sıfır** — `banka_kos/tanilar.py:87`, `motor/hedef_b.py:165` — B karar kaydı `t4a_olcekleme` taşımıyor; tanı kodu eksik alanı `False` kabul ederek gerçekleşen güvenlik ölçeklemelerini gizliyor — B kaydına gerçek bayrağı ekle; eksik kayıt ile “uygulanmadı” durumunu ayır.

7. **[ORTA] Boşluk sayımlarında pencere sonu kaybı** — `banka_kos/tanilar.py:341`, `banka_kos/veri_denetim.py:63` — R17 yalnız pencere içindeki kararların geçmişini okuyarak son değerlendirme günündeki boşlukları kaçırıyor; veri denetimi de `[bas, bit)` taramasına `bit−1h` vererek son saati dışlıyor — R17’de geçmiş kayıtlarını topladıktan sonra saatleri pencereye süz ve son gün kapsamını tamamla; veri taramasını gerçek `bit_ms` sınırına kadar yap.

8. **[ORTA] “Her Sharpe için %90 GA” uygulanmamış** — `banka_kos/rapor_md.py:74`, `banka_kos/rapor.py:98` — Durağan bootstrap ve mevcut tohum etiketleri doğru/deterministik; fakat B4, B6 dilimleri, B8, R1, R3, R12, R13 ve Kelly Sharpe’ları için aralık üretilmiyor — §3.1 kapsamındaki her seri için aynı bootstrap’ı bağla; gereken serileri şifreli çıktıda sakla.

9. **[CIDDI] Zorunlu rapor içeriği eksik** — `banka_kos/rapor_md.py:135`, `banka_kos/rapor_md.py:167`, `banka_kos/veri_denetim.py:92` — DSR’nin γ₃/γ₄ alanları, R7 tahminci tanıları ve Kelly’nin stres MDD’leri, q50, aşım olasılığı ve diğer zorunlu sütunları rapora taşınmıyor; §3.4’ün carry epizot payı hesaplanmıyor, §8.1’in doldurulan funding kayıtları veri raporunda yok — Zorunlu alanları hesaplama→şifreli çıktı→rapor zincirinde tamamla; yalnız 13 bölüm başlığının bulunmasını yeterlilik sayma.

10. **[ORTA] Rapor üreteci coin adı içeren metni aynen geçirebilir** — `banka_kos/rapor_md.py:64`, `banka_kos/rapor_md.py:149`, `banka_kos/rapor_md.py:192` — R4 dosya adı ve teknik/düzeltme sözlüklerinin serbest anahtar/değerleri anonimleştirilmeden yazılıyor; bu alanlarda sembol bulunursa rapora çıkar — Girdi şemasını sınırla ve sembol taşıyabilen alanları anonimleştir. Yeni `tanilar/piyasa/r13b/r17/r8_*` üretim yollarında doğrudan coin adı veya açık gruba performans aktarımı saptamadım; bunlar şifrelenen `duz` içinde kalıyor.

T2 eşik yönleri doğru: tam **%1** ve **%10** geçiyor, yalnız üstü tetikliyor. BTC/ETH paydaları ayrı ayrı bütün `[T0_Z1, birincil_son)` takvim saatleri; görülmüş gün dışlaması uygulanmıyor.

## testler

- R3’te aylık bütçe, ay içi çıkış, işlem dışı ve reduce-only için **mock tabanlı dal testleri mevcut**; bu yollar tamamen testsiz değil.
- Gerçek kısmi dolum→devretme→risk azaltan parçayı koruma, işlem dışından dönüş ve uzlaşma zincirlerinin uçtan uca doğrulaması eksik.
- Durum izi testi pozisyon/NAV’ı karşılaştırıyor; devreden miktarları ve niyet kapanış sınıflarını doğrulamıyor.
- R2 fikstürünün birincil örneklemi **27 gün**: `β_i` için gereken **≥30 ortak gün dalı çalışmıyor**. Katkı toplamı testi sıfır betayla da geçebilir.
- R4 testi **17 ortak gün** içeriyor; 30 günlük blok yolu sınanmıyor. R7’de σ̂/RV değerlerine bağımsız sayısal karşılaştırma yok.
- R8 günlük özdeşlik ve 1×/2× ayrımı sınanıyor; uçtan uca test diğer Kelly L’lerine aynı şablonu taşıyor.
- CHECKSUM eksik alan, bağlayıcı hash değişimi, BTC/ETH tam %1 sınırı, pencere sonu boşluğu ve raporun zorunlu alanları için regresyon testleri gerekli.

## genel_hukum

Banka betiği, 6.01b ve 6.12 dışarıda tutulsa bile **kilide/banka kuru koşusuna hazır değil**: veri kimliği kapısı, R3’ün hükmü kesebilen sayısal dalı ve zorunlu çıktı eksikleri önce kapanmalı. Bu hüküm statik incelemeye dayanıyor; test başarısı iddiası yok.