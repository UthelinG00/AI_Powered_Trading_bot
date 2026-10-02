## kapanis

İncelenen son HEAD: `9623677`, dal `claude/v8-kapi-motor-502e`. İnceleme statiktir; kod/test çalıştırılmadı, dosya yazılmadı, yasaklı içeriklere erişilmedi. Kısa kod yolları `AKTIF_MODEL/v8/` altındadır. T16 metninde özetin aksine **dokuz KISMEN** bulunduğundan dokuzu da değerlendirildi.

T15-1 KAPANDI — Grup 4–5 ve §15.12–13 artık mevcut; eksik bağlayıcı kararlar bu kopyaya taşınmış (`AKTIF_MODEL/ciktilar/v8_asama4_20260927_01/CARRY_KAPISI_ONKAYIT_TASLAK.md:983`).

T15-2 KAPANDI — Mühür yazımı ve bildirim hataları ayrı yakalanıyor, son istisna özgün bağlamı bastırıyor (`kapi/kosu.py:142`).

T15-3 KISMEN — Dondurulmuş→güncel motor bağı eklenmiş, ancak duman kanıtının kimliği ve güncel HAR/parametrelerin kalibrasyonla bağı hâlâ doğrulanmıyor (`kilit.py:139`, `kilit.py:146`, `kilit.py:151`).

T15-4 KISMEN — Bildirilen commit ile bayt eşitliği sağlanmış, fakat hareketli referanslar kabul ediliyor ve yalnız `origin` tazelenirken bütün yerel uzak-dal referanslarına güveniliyor (`kilit.py:237`).

T15-5 KAPANDI — V1 raporu bütün belirtilen kod kümelerini içeriyor; test öncesi/sonrası kimlikler ve raporun güncel kaynaklarla eşitliği denetleniyor (`v8_calistir.py:84`, `v8_calistir.py:145`, `kilit.py:125`).

T15-6 KAPANDI — Sanal trend pozisyonları, boş devreden/carry durumu ve korunmuş NAV artık bağlayıcı U-51 düzeltmesiyle uyumlu (`kapi/denetim.py:145`; `AKTIF_MODEL/ciktilar/v8_kapi_20260929_01/BELIRSIZLIK_COZUMLERI.md:97`).

T15-9 KAPANDI — V2, beklenen bütün takvim günlerini dolaşıyor ve tamamen kaybolmuş son günleri de `inf` yapıyor (`kapi/kosu.py:116`, `kapi/kosu.py:122`).

T15-10 KISMEN — Saatlik miktar karşılaştırması eklenmiş, ancak sonlu olmayan değerler geçebiliyor ve ağırlıklı artık toplamı tüketilen `s^C` değerlerinin birebirliğini kanıtlamıyor (`kapi/denetim.py:107`, `kapi/denetim.py:115`).

T15-13 KISMEN — Kapanış sonrası katkının kaybolması giderilmiş, fakat arada yön değişmişse geçmiş funding hâlâ yanlış bacağa atanabiliyor (`kapi/isim.py:75`, `motor/ayristirma.py:349`).

T16-CIDDI KAPANDI — `HATA.txt` veya çıktı kanalı başarısız olduğunda da dışarı sabit mesaj ve bastırılmış istisna bağlamı çıkıyor (`kapi/kosu.py:145`).

T16-ORTA-funding KISMEN — Son sıfır olmayan işaret, basit kapanış örneğini çözüyor; özgün funding saatinin yönünü ve ters kaydın önceki sınıflandırmasını korumuyor (`kapi/isim.py:78`).

T16-ORTA-age KAPANDI — T16’da belirtilen kanonik Base64, gövde satırı, X25519/sarılı anahtar, açılan anahtar ve MAC uzunluğu kontrolleri eklenmiş (`banka_kos/age.py:142`, `banka_kos/age.py:218`, `banka_kos/age.py:230`, `banka_kos/age.py:239`).

## yeni_bulgular

[CIDDI] Kanıt zinciri HAR/parametre değişikliğini kapsamıyor — `kilit.py:146`, `kilit.py:151` — Kalibrasyon sonrasında HAR sonuç dosyası değişirse motor kimliği aynı kalabilir; eski eşdeğerlik/duman PASS’i yeni parametre kimliğiyle kilitlenebilir. Eşdeğerlik üreticisi de kaynak zarfından yalnız motor kimliğini alıyor — Duman, bitiş ve eşdeğerlik kanıtlarına kaynak hash’leri ile kod/parametre/HAR kimliklerini bağlayın; güncel kalibrasyon girdileriyle karşılaştırın.

[ORTA] Uzak commit denetimi eski referanslarla geçebiliyor — `kilit.py:237` — `fetch origin` budama yapmıyor; silinmiş `origin` dalları veya tazelenmemiş başka remote referansları `branch -r --contains` sonucunu doldurabilir; `HEAD` gibi hareketli girdiler de kabul ediliyor — Tam commit hash’i zorunlu tutun, ilgili remote’u budayarak tazeleyin ve yalnız onun doğrulanmış referanslarını kullanın.

[ORTA] Yeni V5 karşılaştırması NaN/sonsuzluğu reddetmiyor — `kapi/denetim.py:107`, `kapi/denetim.py:115` — `carry_q` içinde NaN fark sayılmaz; sonsuz miktarda tolerans da sonsuz olur ve karşılaştırma yine başarısızlığı yakalamaz — Saat, miktar, artık ve beklenen dizilerde şekil/kapsam ile sonluluk kontrollerini karşılaştırmadan önce zorunlu kılın.

[ORTA] Artık toplamı eşitliği `s^C` birebirliği değildir — `kapi/denetim.py:110` — Artık sıfırken yanlış `s^C` görünmez; iki isimde `A=(1,−1)` için payların birlikte `0,5→0,7` değişmesi de toplamı değiştirmez — Ayrıştırmanın fiilen tükettiği isim/saat bazlı `s^C` değerlerini ayrıca çıkarıp diskten türetilenlerle mutlak `1e-12` toleransla karşılaştırın.

[ORTA] Son işaret geçmiş funding’i başka epizoda taşıyor — `kapi/isim.py:75`, `motor/ayristirma.py:233` — Long döneminin dolgusu short açıldıktan sonra gelirse tamamı short’a yazılır; farklı yönlerdeki saatler tek tutarda toplandığından toplam özdeşliği bu hatayı yakalayamaz — Dolguyu özgün saat/yön üzerinden bölün ve ters kayıtta özgün bacak atamasını tersine çevirin.

[CIDDI] Yeni banka koşucusunda aynı mühür açığı bulunuyor — `banka_kos/kosucu.py:100`, `banka_kos/kosucu.py:168` — Hata şifreleme/yazımı başarısızsa özgün istisna zinciri açılır; devam sırasında birincilin yeniden yürütülmesi ise mühürlü hata sarmalayıcısını tamamen atlar — İlk ve yeniden yürütmeyi ortak hata sınırına alın; mühürleme başarısızlığında da özgün bağlamı bastırın.

**P&L doğrulaması:** `e0403c1` farkında `carry_q` yalnız ayrı bir diziye yazılıyor (`motor/ayristirma.py:277`); mevcut miktar, fiyat, funding, maliyet, netleme, artık, `dnav` ve özdeşlik hesapları değişmemiş (`motor/ayristirma.py:288`, `motor/ayristirma.py:340`, `motor/ayristirma.py:356`, `motor/ayristirma.py:369`). Statik olarak P&L değişikliği saptamadım; çalıştırılmış eşdeğerlik sonucu vermiyorum.

## kararlar

U-44 KABUL — S4 teması ve aşımı ayrı ölçülüyor.

U-45 KABUL — Gerçekleşen ve devreden emirlerle oluşacak kitap ayrı değerlendiriliyor.

U-49 ITIRAZ — Olağan geçişler doğru; geçmiş funding ve ters kayıtlar özgün yönlerine bağlanmıyor.

U-51 KABUL — Sanal trend referansı carry maruziyetini temizliyor; NAV korunması açıkça belgelenmiş.

U-56 KABUL — Kalan isimlerden ikinci seçim, eşit katkılarda da altı ayrık isim sağlıyor.

U-57 KABUL — Gün sonu NAV kaydı bulunmayan gün başarısız sayılıyor.

U-58 KABUL — Kapıdaki olağan istisnalar mühürlü ayrıntı ve sabit dış mesajla yönetiliyor.

U-58-ek KABUL — Mühürleme ve bildirim başarısızlığında özgün bağlam bastırılıyor.

U-59 ITIRAZ — Kabul kapıları mevcut; kanıtların parametre/HAR bağı ve uzak commit doğrulaması eksik.

U-59-ek ITIRAZ — Motor ve V1 kaynak bağları düzelmiş; bütün kanıt zinciri ve sabit uzak kimlik garantisi tamamlanmamış.

U-60 KABUL — Kayıt sayısı ve terminal hash karşılaştırması geçerli günlük önekinin kabulünü engelliyor.

U-61 KABUL — Kesin sabitlik kontrolü ve sınırlanmış Bartlett dizisi önceki sayısal sorunları gideriyor.

U-62 KABUL — Beklenen takvim günlerinin tamamı denetleniyor; görünmeyen günler de başarısız.

U-63 ITIRAZ — Ağırlıklı artık eşitliği tüketilen payların birebirliğini kanıtlamıyor; sonluluk kontrolleri de eksik.

U-64 ITIRAZ — Son işaret, geçmiş funding’in özgün yönünü garanti etmiyor; yön değişiminde yanlış bacak ataması sürüyor.

## genel_hukum

Kapı kodu henüz kilide hazır değil; birleştirme, tam test/V1, son motorla eşdeğerlik ve toplama adımları kalan kimlik zinciri, Git, V5 ve funding açıklarını kendiliğinden kapatmaz. Önce bu açıklar düzeltilmeli, ardından belirtilen doğrulama sırası tamamlanmalıdır; yeni banka koşucusunun mühür açığı da banka yürütmesinden önce kapatılmalıdır.