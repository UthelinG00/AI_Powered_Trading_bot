## kapanis

İncelenen HEAD: `4beaf6cb98005990aaa731e39c2b58e080e1f38d`, dal `claude/v8-kapi-motor-502e`. İnceleme statiktir; kod/test çalıştırılmadı, dosya yazılmadı, yasaklı kaynaklara erişilmedi. Aşağıda kod yolları `AKTIF_MODEL/v8/`, `KAL/` ise `AKTIF_MODEL/ciktilar/v8_kalibrasyon_20260929_01/` altındadır.

T15-3 KISMEN — Dondurma/HAR/parametre bağları tamamlanmış, ancak toplamanın gerçekten bitişte doğrulanan birim dosyalarını tükettiği doğrulanmıyor (`kilit.py:191`, `KAL/topla.py:62`).

T15-4 KAPANDI — Tam commit hash’i zorunlu; üretim çağrısı `fetch --prune origin` ve `ls-remote` ile doğrulanmış origin dallarında atalık ve dosya bayt eşitliği arıyor (`kilit.py:303`, `kilit.py:357`).

T15-10 KAPANDI — Sonluluk/şekil denetimi, isim-saat bazında `carry_q`/`sc_q` karşılaştırması ve ayrı artık toplamı kontrolü eklenmiş (`kapi/denetim.py:103`, `kapi/denetim.py:149`).

T15-13 KAPANDI — Eski payın funding kısmı özgün yöne, kalanı saat başındaki miktarın işaretine ayrılıyor (`motor/ayristirma.py:101`, `kapi/isim.py:76`).

T16-ORTA-funding KAPANDI — Dolgu ve ters kayıt, son pozisyon işaretinden bağımsız olarak kapsanan saatlerin özgün yönlerine dağıtılıyor (`motor/ayristirma.py:110`, `motor/ayristirma.py:294`).

T17-a-CIDDI KAPANDI — Özgün HAR/parametre açığı giderilmiş; ortak bloklar dondurmayla, eşdeğerliğin güncel kod/motor/parametre/HAR ucu kilit girdileriyle karşılaştırılıyor (`kilit.py:164`, `kilit.py:207`).

T17-b-CIDDI KAPANDI — Olağan istisnalarda birim, başlatıcı, BK-6 yeniden yürütmesi ve dış koşucu sınırı mühürlü; şifreleme/yazım başarısızlığı ve işçinin uzak izi dış bağlamı açmıyor (`banka_kos/kosucu.py:87`, `banka_kos/kosucu.py:115`, `banka_kos/kosucu.py:171`, `banka_kos/kosucu.py:219`).

T17-c-ORTA KAPANDI — Hareketli referanslar, başka uzak depolar ve silinmiş origin dallarının bayat referansları normal kilit yolunda kabul edilmiyor (`kilit.py:282`, `kilit.py:319`).

T17-d-ORTA KAPANDI — Günlük karşılaştırmalar NaN/inf’i reddediyor; saatlik miktar/pay/artık dizileri karşılaştırmadan önce sonluluk ve şekil denetiminden geçiyor (`kapi/denetim.py:75`, `kapi/denetim.py:103`).

T17-e-ORTA KAPANDI — `sc_q`, artık sıfırken de payları görünür kılıyor; toplamı koruyan yanlış paylar artık isim-saat karşılaştırmasından kaçamıyor (`motor/ayristirma.py:425`, `kapi/denetim.py:155`).

T17-f-ORTA KAPANDI — Gerçek funding `q(d−)`, dolgu `q(h−)` ile sınıflandırılıyor ve ters kayıt aynı dolguların özgün bacak atamalarını tersliyor (`motor/ayristirma.py:108`, `motor/ayristirma.py:116`).

**Ek doğrulamalar:** Ayrıştırmanın mevcut `satirlar`, `trend_*`, `carry_coin/eski/yeni`, `artik_coin`, `carry_q` ve `bacak_funding_tur` hesaplarında aritmetik değişiklik saptamadım; `artik_carry` aynı değerleri aynı sırada topluyor (`motor/ayristirma.py:429`). Yeni alanlar ek çıktıdır; banka/kalibrasyon tüketicileri belirli eski alanları okuyor (`banka/degerlendirme.py:121`, `kalibrasyon/yurutucu.py:79`). Bu, çalıştırılmış bayt eşitliği kanıtı değildir.

Aynı çağrıda birden çok gerçek kayıt için `ters_kayit → funding` sırası bekleyen kümeyi bir sonraki kayıttan önce güncelliyor; `(d−aralık,d]` sınırları aynı ve budama, tanımlı geç kayıt penceresinde gerekli dolguları koruyor (`motor/funding.py:124`, `motor/durum.py:138`, `motor/ayristirma.py:286`). Mevcut çağrı yollarının `print` ve günlüklerinde ek performans sızıntısı saptamadım.

**6.02a:** Hüküm fonksiyonundaki B2 `N_hukum`, B3 eşikleri, B6 sayımı, B7’nin 475’inci değeri ve katı `>`, B9 penceresi, B10 ve bağlı/bağsız karar uygulaması tutarlı (`banka_kos/hukum.py:102`). R1’in dokuz SR hücresi, Kelly/stres gün dışlaması ve şekil kontrolü, BK-12’nin iç kök/sayı/tekrar/dosya kontrolleri ve verilirse itilmiş kökle karşılaştırması da doğru (`banka_kos/hukum.py:50`, `banka_kos/hukum.py:136`, `banka_kos/hukum.py:154`); aşağıdaki üretici sorunları nedeniyle uçtan uca uygunluk tamamlanmış değil.

3.09 için **yeni `bitis.py` ile birlikte `kanit.py` de sunucuya taşınmalı**; doğrudan import bağımlılığı var (`KAL/bitis.py:33`). Bu işlem dondurulmuş motorun değiştirilmesini gerektirmiyor.

## yeni_bulgular

[CIDDI] Bitiş kanıtı ile toplamanın tükettiği dosyalar arasında bağ eksik — `KAL/bitis.py:110`, `KAL/topla.py:62`, `KAL/topla.py:91`, `kilit.py:191` — Bitiş birim dosyalarının birleşik hash’ini yazıyor; toplama bunu kendi girdileriyle karşılaştırmadan yalnız bitiş raporunun hash’ini kaydediyor. Aynı dört kimliği taşıyan, iç hash’i geçerli başka bir birim dosyası kullanılması yakalanmıyor; belgelenmiş Windows/Linux bayt farkları bu ihtimali somutlaştırıyor — Toplama öncesinde iş listesi, ek liste ve birim dosyaları özetini bitiş kanıtıyla eşleştirin; tüketilen özeti TOPLAMA’ya taşıyıp kilitte karşılaştırın.

[CIDDI] B7 null örnekleminden görülmüş günler düşülmüyor — `banka_kos/yurutucu.py:194`, `banka/degerlendirme.py:82` — `sadece_sharpe`, `pencere.gun_maskesi()` uygulamıyor; gerçek birincil SR görülmüş günleri dışlarken 500 null SR bunları içeriyor ve BANKA §3.5.6’daki aynı takvim şartı bozuluyor — Null istatistiğine aynı maskeyi uygulayın; dışlanan güne yerleştirilen uç getirinin null SR’ı etkilemediğini sınayın.

[CIDDI] B mimarisinde birincil dışındaki normal birimler duruyor — `banka_kos/yurutucu.py:189`, `banka_kos/yurutucu.py:197`, `banka/degerlendirme.py:115` — Ayrıştırma yalnız B birincilde üretiliyor, fakat B ızgara/Kelly/çıkarma/K-evren gibi birimler de ayrıştırmayı zorunlu isteyen `birincil_olcum` çağrısına gidiyor; dolayısıyla istisna veriyor — Bu birimlerde gerekli ayrıştırmayı üretin veya ihtiyaç duyulan ölçümleri ayrı yoldan hesaplayın; gerçek B birincil dışı yürütme testi ekleyin.

Son iki bulgu `744fcce` tabanında da mevcut; T17 düzeltmelerinin getirdiği regresyonlar değil, bu turda banka entegrasyonunda saptanan açıklardır. Yeni uçtan uca test yalnız A şablonlarını kullandığından B sorununu yakalamıyor (`testler/test_v8_banka_uctan_uca.py:61`).

## kararlar

U-58-ek-2 KABUL — Olağan istisna yollarında ortak mühürleme, mühürleme hatasında bağlam bastırma ve işçi uzak izinin temizlenmesi uygulanmış.

U-59-ek-2 ITIRAZ — Kimlik bağları doğru; TOPLAMA’nın tükettiği birimler bitişte doğrulanan dosya özetiyle eşleştirilmiyor.

U-59-ek-3 KABUL — Üretim yolu tam hash, budama, origin doğrulaması ve atalık denetimini birlikte uyguluyor.

U-63-ek KABUL — Sonluluk denetimi, isim-saat pay karşılaştırması ve bağımsız artık toplamı kontrolü önceki açıkları kapatıyor.

U-64-duzeltme KABUL — Funding özgün saat yönüne ayrılıyor; olay zamanı ve mevcut toplam P&L korunuyor.

## acik_soru

B5 bağlayıcı kaldığında bu, düzeltilmesi gereken bir atıf hatasıdır: yanlış epizoda taşınan funding toplam P&L’i korusa bile en iyi üç epizodun sıralamasını ve payını değiştirerek kabul/ret sonucunu etkileyebilir; etkinin yönü önceden belli değildir (`banka/pnl.py:143`). Kalibrasyonla aynı hatayı paylaşmak, BANKA §3.4’teki epizot tanımına uygunluk sağlamaz. Funding gerçek kayıt/dolgu/ters kayıt bazında özgün **epizot kimliğine** bağlanmalı; yalnız long/short ayrımı, kapanıp aynı yönde yeniden açılmış epizotları ayıramaz. Dondurulmuş eski kimlik korunarak düzeltme ayrı sürümde belgelenmeli ve etkilenen kalibrasyon doğrulamaları yeniden yapılmalıdır; ölçüt değişikliğini P&L eşdeğerliği diye sunmak yeterli olmaz. B5 kalibrasyon kuralıyla rapora inerse bağlayıcı karar etkisi kalkar, rapor hatası kalır.

## genel_hukum

Kapı kodu yalnız sayılan dizüstü adımlarıyla henüz kilide hazır değil: önce bitiş–toplama girdi bağı tamamlanmalı ve B5 konusu kilit öncesinde çözülmeli, ardından güncel kanıtlar, eşdeğerlik, birleştirme ve tam test/V1 tamamlanmalıdır. Banka yürütmesi de hazır değil: null gün maskesi ve B birimlerinin ayrıştırma açığına ek olarak, belgelenmiş R3, veri yükleyici, T2 ve raporlama işleri açıktır.