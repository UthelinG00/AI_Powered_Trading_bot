## bulgular

Dosya yolları `AKTIF_MODEL/v8/` köküne göredir. Bulgular statik incelemeye dayanır; kod ve test çalıştırılmadı.

1. **[CIDDI] B5 işaret değiştirme saatini yanlış epizota yüklüyor — `banka/pnl.py:111` —** `q[h]`, T’deki işlemlerden sonraki pozisyon; saatlik P&L ise yeni pozisyonun T→T+1 fiyat hareketini de içeriyor. Tamamını eski epizota yazmak yeni short’un kazancını eski long’a aktarabilir. Toplam P&L özdeşliği bu hatayı yakalamaz. **Önerilen düzeltme:** eski pozisyonun kapanışa kadarki fiyat/funding/kapanış maliyetini eski epizota; yeni pozisyonun açılış maliyeti ve sonraki fiyat hareketini yeni epizota ayırın.

2. **[CIDDI] B sonucu süreçlerin hash rastgeleliğine bağlı olabilir — `kalibrasyon/yurutucu.py:99`, `motor/ayristirma.py:259` —** Ayrıştırmada sıralanmamış küme üzerinden funding toplamı alınıyor. Toplama sırasındaki kayan nokta farkı `ozdeslik_max_hata` üzerinden sonuç gövdesine, dolayısıyla birincil SHA’ya ve B10 kimliklerine taşınabilir. Windows `spawn` süreçleri farklı küme sıraları üretebilir. **Önerilen düzeltme:** ayrıştırmadaki toplama sıralarını sabitleyin; gerçek B birimini farklı `PYTHONHASHSEED` ve işçi sayılarıyla karşılaştırın. Sahte yürütücülü mevcut test bunu sınamıyor.

3. **[CIDDI] T4-e ihlali her birimde durdurulmuyor — `kalibrasyon/yurutucu.py:99` —** B ayrıştırma özdeşlik hatası yalnız kaydediliyor; eşik aşımında istisna yok. ×2/×3, çıkarma ve null birimleri de yalnız Sharpe çıkararak bitiyor; birincil koşudaki coin-P&L kontrolünden geçmiyor. **Önerilen düzeltme:** gerekli muhasebe değişmezlerini bütün koşu türlerinde denetleyen ortak tamamlanma kapısı ekleyin; sonlu olmayan hata veya tolerans aşımı sonuç yazımını engellesin.

4. **[ORTA] Yarım ek iş günlüğü devamı engelliyor; geçici dosyalar korunmuyor — `kalibrasyon/kosucu.py:146`, `kalibrasyon/birim.py:84` —** Ek listeye yazma sırasında kesinti, yarım JSON satırı bırakabilir; sonraki başlangıç koşulsuz `json.loads` ile durur. Ayrıca `.gecici` dosyaları ve zarfsız NPZ’ler karantinaya alınmadan yeniden yazılabilir. **Önerilen düzeltme:** bozuk günlük kuyruğunu koruyup doğrulanmış birincillerden ek listeyi deterministik yeniden kurun; artık dosyaları yeniden koşmadan önce karantinaya taşıyın.

5. **[ORTA] HAR artık haftaları yetersizleşince eski ŝ² kullanılmaya devam ediyor — `banka/har_banka.py:105`, `motor/har.py:153` —** Sekizden az geçerli hafta bulunan Pazartesi takvime yazılmıyor. `artik_varyansi` önceki mevcut kaydı döndürdüğünden, daha önce HAR kullanılmışsa EWMA’ya dönüş gerçekleşmiyor. **Önerilen düzeltme:** her Pazartesiyi kaydedin; yetersiz haftalarda açık `None` üretin. “Önce yeterli, sonra yetersiz, sonra toparlanan” fikstürü ekleyin.

6. **[ORTA] N3 geçerli gap taşınmasını ihlal sayabiliyor — `banka/rejim_null.py:165` —** Her dilimin ilk/son mevcut bar saati karşılaştırılıyor. Sürekli yaşayan coinin yaşam içi boşluğu dilimin ilk veya son tam bloğuna taşınırsa bu saatler değişebilir; gerçek listelenme/ölüm ve toplam bar sayısı korunmuştur. **Önerilen düzeltme:** ilk/son bar kontrolünü gerçek yaşam sınırlarında yapın; dilimlerde bar sayısını ve ilgili yaşam kenarlarını denetleyin.

7. **[ORTA] Isınma yılı durumlu motoru ısıtmıyor — `kalibrasyon/yurutucu.py:91` —** Motor 365. günde boş defterle başlıyor. Önceki pozisyon, devreden emir, evren histerezisi ve carry durumu taşınmıyor; HAR takvimi ise önceki yılda ilerletilmiş durumda. Bu, §3.1 sürekli koşusuyla aynı başlangıç dağılımı değil. **Önerilen düzeltme:** motoru ısınma boyunca ilerletip yalnız değerlendirme P&L’ini ölçün veya bu farklı başlangıcı koşudan önce açık bir tasarım değişikliği olarak sabitleyin.

8. **[ORTA] Seyreltme raporu B’nin birleşik kabulünü ölçmüyor — `kalibrasyon/duzey1_olcut.py:98` —** B9 ve B10 A’dan kopyalanıyor; özellikle B10, `SR(X+C)−SR(X_ikame+C)` yerine A’nın düşüşünü kullanıyor. Carry maliyetinin stres altında değişmemesi de ek varsayım. **Önerilen düzeltme:** B’ye ait ikame/ikinci portföy ölçülerini hesaplayın; sadeleştirme korunacaksa çıktıyı açıkça “A filtreleri sabit tutulan kısmi seyreltme” olarak adlandırın.

9. **[ORTA] İşçi parametre/HAR kimliğini doğrulamıyor — `kalibrasyon/kosucu.py:73` —** İşçi yalnız kod, motor ve ortamı doğruluyor; verilen `beta` ile beklenen parametre kimliği arasında kontrol yok. Aynı kimlikle farklı beta çalıştırılabilir veya eski sonuçlar atlanabilir. **Önerilen düzeltme:** HAR kaynağını bir kez okuyup hem hash’i hem beta’yı aynı baytlardan üretin; işçinin kullandığı parametre/beta paketini de doğrulayın.

10. **[ORTA] Düzey 2-b’de sıfır düşüş B10’u koşulsuz etkisizleştirmiyor — `kalibrasyon/toplama.py:80` —** `e_b10 ≤ 0` çıkmasını eşik kodu yasaklamıyor. Böyle bir bağlayıcı eşikte `0 < e_b10` yanlış olur; 2-b’de bulunmaması gereken B10 veto uygular. **Önerilen düzeltme:** 2-b kabulünü açık ölçüt kümesiyle hesaplayın; en azından bu çağrıda `e_b10=None` kullanın.

11. **[DUSUK] Izgara yuvarlaması “en küçük eşik” kuralını sınır yakınında bozuyor — `kalibrasyon/duzey1_esik.py:34` —** Eklenen `1e-9`, ızgaranın hemen altındaki değeri üst hücreye itiyor. Örneğin sıra istatistiği `0.60−1e-12` ise yeterli eşik `0.60` olmasına rağmen `0.61` seçilip B5 rapora indirilebilir. **Önerilen düzeltme:** epsilon kullanmadan aday ızgara eşiğinin kesin `x < e` koşulunu doğrudan doğrulayın.

## yorumlar_2a_2g

a) **KABUL —** Ortak faktörü paylaşmak hatlar arası korelasyonu korur; bağımsızlık özgül gürültü ve epizot çekişleri için tanımlanmalı. Belgedeki “bağımsız yeni hat” ifadesi buna göre netleştirilmeli.

b) **KABUL —** Birim ölçekli X doğrudan loglanamaz; %15 ölçek makul bir tamamlamadır. Dilim sıralaması ölçeğe bağlı olduğundan bu seçim ön-kayda açıkça eklenmeli.

c) **ITIRAZ —** B9/B10’u A’dan kopyalamak B’nin birleşik kabul eğrisini vermez. Ancak açıkça adlandırılmış kısmi seyreltme teşhisi olarak kullanılabilir.

d) **KABUL —** Yalnız başlık doğrulandı: belirtilen kayıt deneme başına Sharpe taşımıyor. Bu kaynak için 0,30 varsayım dalı doğru; başka kullanılabilir REV1 kayıtlarının bulunmadığı başlıktan çıkarılamaz.

e) **ITIRAZ —** Geçmiş fiyatların görünmesi, pozisyon ve histerezis durumunu ısıtmaz. Sürekli banka koşusuyla eşdeğerlik kurulmadan bu fark sessiz uygulama yorumu olarak kabul edilemez.

f) **ITIRAZ —** B8’in gerçek funding nakdini çıkarması ve B10 aday/HAR takviminin yeniden kurulması doğru. B5’te dönüş saatinin bütün P&L’ini eski epizota atamak yanlış.

g) **KABUL —** Null yolunun kendi verisiyle, sabit β ve tamamlanmış hedef haftaları üzerinden ŝ² yeniden kurulmalı. Eski ŝ²’nin taşınması sorunu ayrıca düzeltilmeli.

## sorular_1_3_4_5

1) **KISMEN —** Üreteç formülleri, ana ölçüt eşlemeleri, k_B6 ve §3.3 karar sırası uyumlu; kesin eşitsizlik yönleri doğru. Izgara sınırı, başlangıç durumu ve seyreltme raporunda sorunlar var.

3) **KISMEN —** Kanonik tohum, birincil gövde SHA bağı, zarf kontrolü ve CLI’de erken thread ayarı doğru. Sırasız toplamlar, yarım günlük ve eksik parametre doğrulaması garantiyi bozuyor; `fsync` ve `os.replace` bunları çözmüyor.

4) **KISMEN —** HAR hedef kesimi PIT; null getiri zinciri ve düz-bar işlemi uygun. Epizot ataması, N3, eksik ŝ² ve T4 kontrolleri sorunlu; boş/sonlu olmayan girdilerin doğrulanması da tutarlı değil.

5) **KISMEN —** 2-a’da B9=+1 doğru; 2-b’de B3=+∞ mevcut sonlu eşiklerde etkisiz. B10=0 yalnız `e_b10>0` iken etkisiz; ölçüt açıkça dışlanmalı.

## genel_hukum

Kod dondurmaya ve esas kalibrasyon koşusuna hazır değil. Bulgular giderilip yorumlar ön-kayda işlendiğinde, gerçek motorla süreçler arası ve kesinti/devam duman denetimi tamamlanmalı; mevcut testlerin geçtiğini bu incelemede doğrulamadım.