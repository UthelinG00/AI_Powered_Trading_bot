## dogrulama

K1: KISMEN — Sıralı gecikmeler işleniyor; ilk gerçek kayıt gecikirse veya daha yeni kayıttan sonra gelirse hâlâ atlanıyor.  
K2: KISMEN — Sekiz saatlik örnek düzeldi; kısa aralıklarda eksik uzlaşmaların dolguları sonraki gerçek kayıtla hâlâ siliniyor.  
K3: KAPANDI — Kapanmış pozisyon geçmişi taranıyor; tespitten önceki saatlerin funding borcu tahakkuk ediyor.  
K4: KAPANDI — İlk kararda veri başlangıcından günlük maske geçmişi kuruluyor; ısınmadaki donma korunuyor.  
K5: KAPANDI — Saatlik dolum öncesinde bilinen borsa boşluğu kontrol ediliyor; devreden risk artıran parçalar iptal ediliyor.  
K6: KAPANDI — Eski azaltıcı miktar korunuyor; yeni niyet yalnız daha fazla azaltıyorsa yerine geçiyor.  
K7: KAPANDI — Karar ve saatlik orkestrasyon yolları kesinti referansını taşıyor; uzun kesintide referans küme unutulmuyor.  
K8: KISMEN — İhlal bayrakları eklendi; teknik hata kaldırılmış durumda ve yalnız isim tavanı aşımında serbest ağırlıklar sıfırlanmıyor.  
K9: KAPANDI — Miktarlı düzeltme pozisyona ve pozisyon geçmişine işleniyor; devreden düzeltmesi ayrı iptal olayı gerektiriyor.  
K10: KISMEN — Kısa kesintiler dışlanıyor; üç günlük geçmiş sınırı uzun kesintide yanlış funding maskesi ve yeniden kurulum farkı üretiyor.  
K11: KISMEN — Toplam eksik saat ve normal gece geçişi düzeldi; araya borsa boşluğu girince 29 saatlik tarama altı donmuş barı kaçırabiliyor.  
K12: KAPANDI — İşlem dışı günler kaydediliyor; bu kapanışları kullanan getiriler risk tahmininden dışlanıyor.  
K13: KAPANDI — Hacim tabanı altında hedef yalnız azaltılıyor; girişin çıkış gibi fiyatlanmasını sağlayan istisna kaldırıldı.  
K14: KAPANDI — İşaret değiştiren emrin korunan kapanış parçası tam kapanış niteliği kazanıyor; minNotional muafiyeti uygulanıyor.  
K15: KAPANDI — Durum türetilmeden önce hash zinciri doğrulanıyor; değiştirilmiş kayıt reddediliyor.

## tartismali_kararlar

**K1 — İtiraz.** Arşivde geliş=damga varsayımı ve canlı adaptörün yalnız ulaşmış kayıtları sunması kabul edilebilir; ayrı alan tek zorunlu çözüm değildir. Ancak son işlenen damga yeterli değildir: 408 işlendikten sonra gelen 400 kaydı atlanıyor. Ayrıca `son_islenen=None` iken 8 damgalı ilk kayıt 9’da gelirse işlenmiyor. İki karşı örnek de boş olay listesi üretti.

**K8 — İtiraz.** §3.1 işlem yasağı, §3.5’in hedef değişmezi ve teknik hata hükmünü kendiliğinden kaldırmaz; önerilen davranış açık bir tasarım değişikliğidir. Üstelik uygulama kendi gerekçesini sağlamıyor: sabit alt-long %7, serbest alt-long %3 örneğinde `sabit_ihlal=True`, fakat serbest ağırlık %3 kalıyor. “İhlalde serbestler sıfırlanır” iddiası doğru değil.

K2’ye itiraz: 1h düzende 400 ve 401 eksikken 402 kaydı üç saat kapsamlı sayılıyor; eksik iki uzlaşmanın toplam −0,02 dolgusu yanlışlıkla geri alınıyor.

K10’a itiraz: Son 16 boşluk dışı saat yaklaşımı uygun; üç günlük geçmiş sınırı bu pencereyi garanti etmiyor.

## yeni_bulgular

**[ORTA] karar.py:188 — Kesinti geçmişinin budanması maske sonucunu değiştiriyor**

Üç günlük `bosluk_gecmis`, `_c_penceresi` için gereken eski boşluk saatlerini kaybediyor. Beş adaydan üçünün 120 saat kesildiği, funding’in durduğu sentetik örnekte çalışan coin için tam geçmişle `(c)=False`, taşınan geçmişle `(c)=True` çıktı. Böylece aynı piyasa geçmişinin ilk kurulum ve günlük ilerleme yolları farklı maske üretiyor.

**[ORTA] karar.py:166 — Korunan emir yeni maske çıkışının maliyetini taşımıyor**

Borsa boşluğu kararında coin ayrıca maskelenirse, eski tam kapanış emri yeni niyetle eşit olduğunda yeni niyet siliniyor; korunan emrin `maske_cikisi=False` alanı değişmiyor. Önceki sürüm aynı durumda maske çıkışı üretiyordu; bağımsız örnekte aynı dolum bağlamında maliyet gerekli **29,1732 bps** yerine **13,0577 bps** oldu. Azaltıcı miktar korunurken maske çıkışı niteliği de güncellenmeli.

## genel_hukum

Dosya yazmadan çalıştırılan **185 mevcut test geçti**, ancak bağımsız karşı örnekler beş bulgunun tam kapanmadığını ve düzeltmelerde ek sorunlar bulunduğunu doğruladı. Slice 2 henüz doğruluk açısından kabul edilebilir durumda değil.