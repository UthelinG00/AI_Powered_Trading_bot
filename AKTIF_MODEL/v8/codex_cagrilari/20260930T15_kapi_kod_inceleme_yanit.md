## bulgular

İncelenen HEAD: `c0c7cc6`. İnceleme statiktir; kod/test çalıştırılmadı, dosya yazılmadı, yasaklanan içerikler okunmadı. Aksi belirtilmedikçe yollar `AKTIF_MODEL/v8/` altındadır.

1. **[CIDDI] Bağlayıcı belge sürümü eksik — `AKTIF_MODEL/ciktilar/v8_asama4_20260927_01/CARRY_KAPISI_ONKAYIT_TASLAK.md:939` —** Bu kopyada §15 yalnız 1–10 maddelerini içeriyor; `BELIRSIZLIK_COZUMLERI.md` U-40’ta bitiyor. U-41–U-53’ün bazı tanımları kod yorumlarında bulunuyor, U-54/U-55 bulunmuyor. İstenen tasarımın tamamına uygunluk doğrulanamıyor. **Düzeltme:** Eksik gerekçeli kararları ve §15.11’i aynı inceleme commit’ine getirip kilitleyin.

2. **[CIDDI] Hata yolunda mühür sızıntısı — `kapi/kosu.py:111`, `motor/hedef_b.py:79` —** Motor `NAV <= 0: {nav}` istisnasıyla sayısal B NAV’ını bildiriyor; koşucu bunu yakalamadığı için traceback ekrana çıkar. Bilinen başlangıç NAV’ıyla toplam getiri de açığa çıkar. **Düzeltme:** Koşu sınırında hataları yakalayın; ayrıntıyı mühürleyip dışarı yalnız sabit hata kodu ve hash verin.

3. **[CIDDI] Kilit, önkoşulların başarısını denetlemiyor — `kilit.py:129`, `kapi/kosu.py:229` —** Kalibrasyon, duman ve eşdeğerlik belgelerinin varlığı/hash’i denetleniyor; `KILIT_BEKLER` veya başarısız sonuç kilit üretimini engellemiyor. V1 geçmese de D motor koşuları başlıyor. **Düzeltme:** Adım 0–3 kabul durumlarını ve kimlik bağlarını kilit üretiminde, V1’i ilk P&L çağrısından önce zorunlu kılın.

4. **[CIDDI] Kilit kendi kapsamını daraltabiliyor — `kilit.py:161` —** Doğrulama zorunlu belge kümesini kilit dosyasından alıyor. `belgeler` içinden bir giriş çıkarılırsa o dosya artık doğrulanmıyor; eksiklik de fark sayılmıyor. **Düzeltme:** Üretim doğrulamasında belge kümesini `KILIT_BELGELERI` ile birebir karşılaştırın ve kullanılan kilidi uzak depodaki sabit kimliğe bağlayın.

5. **[CIDDI] V1 kanıtı kilitli uygulamaya yeterince bağlanmamış — `kapi/denetim.py:32`, `kilit.py:77` —** Motor hash’i, `basarisiz=0` ve `toplam>0` yeterli. Gerekli test kümesi, kapı/adaptör kodu, test kaynakları ve seçilen rapor hash’i doğrulanmıyor. Motor değişmeden kapı kodu değiştiğinde eski PASS kullanılabilir; kilitten sonra yeni rapor seçilebilir. **Düzeltme:** Test manifestini, kapsamlı kaynak kimliklerini ve seçilen raporu kilitleyin.

6. **[CIDDI] V6, carry durumuyla etkilenmiş A karşılaştırması yapıyor — `kapi/denetim.py:118` —** A hedefi B’nin gerçek pozisyonları, devreden emirleri ve nakdi üzerinden kuruluyor. Örneğin işlem dışı kalmış carry pozisyonu A çözücüsünde sabit maruziyet olur ve diğer trend hedeflerini küçültebilir. Sabit ismi sonuçtan çıkarmak bu dolaylı etkiyi kaldırmaz. **Düzeltme:** P&L üretmeden kullanılacak A referans durumunu açıkça tanımlayın; carry pozisyonunun A tavanlarını tüketmesini engelleyin. Mevcut hesap yalnız “B durumu üzerinde A hedefi”ni sınar.

7. **[ORTA] Sabit trend serisi K10’u yanlış geçebilir — `kapi/istatistik.py:166` —** `rho_ust`, Sharpe fonksiyonlarındaki kesin sabitlik kontrolünü kullanmıyor. Tekrarlanan ondalık değerlerde ortalama yuvarlaması küçük pozitif varyans üretebilir; tanımsız korelasyon yerine yaklaşık sıfır bulunup K10 geçebilir. **Düzeltme:** Merkezlemeden önce iki seriye de `_sabit` uygulayın; ondalık sabit trendle regresyon testi ekleyin.

8. **[ORTA] K8 altı farklı isim çıkarmayı garanti etmiyor — `kapi/isim.py:44` —** En iyi ve en kötü listeler bağımsız sıralanıyor. Otuz katkı eşitse iki liste de aynı alfabetik üçlü olur; birleşim yalnız üç isim çıkarır. **Düzeltme:** Eşitliklerde de ayrık altı isim sağlayan sıralama kuralını dondurun ve bu örneği test edin.

9. **[ORTA] Eksik günlük özdeşlik denetimi atlanıyor — `kapi/seriler.py:152` —** Bir günün bütün `dnav` değerleri NaN ise gün sessizce çıkarılıyor. Koşucu yalnız kalan oranların maksimumunu alıyor; “her gün V2” şartının kapsamı doğrulanmıyor. **Düzeltme:** Beklenen tam gün kümesini denetleyin; eksik gün sonu NAV kaydını teknik başarısızlık sayın.

10. **[ORTA] V5 günlük sonunun kesilmesini yakalamıyor — `kapi/denetim.py:61`, `kapi/denetim.py:95` —** Disk okuması geçerli hash zinciri önekini kabul ediyor; yalnız karar kayıtlarını karşılaştırıyor. Son karardan sonraki dolum/funding/NAV kayıtları kesilmiş dosya V5’i geçebilir. Ayrıca bu kontrol ayrıştırmanın doğru saatte doğru miktarı tükettiğini sınamıyor. **Düzeltme:** Toplam kayıt sayısını ve terminal hash’i bellek kaynağıyla karşılaştırın; tüketilen miktar/zaman eşleşmesini ayrıca denetleyin.

11. **[ORTA] Betimsel Andrews hesabı aşırı bellek ayırabilir — `kapi/istatistik.py:75`, `kapi/istatistik.py:237` —** AR katsayısı ±1’e kırpılınca gecikme yüz milyonlara çıkabilir. `_bartlett` bu büyüklükte dizi oluşturuyor; `j >= n` kontrolü sonradan geliyor. Örneğin merkezlenmiş `[-1, 2, -3, 2]` için AR oranı −1’dir. **Düzeltme:** Yalnız `min(ℓ,n−1)` ağırlık üretin; ağırlık paydasında özgün `ℓ+1` değerini koruyun.

12. **[ORTA] Ayrıştırmada her erişimde gereksiz tam dizi tahsisi — `motor/ayristirma.py:155` —** `setdefault(c, np.zeros(...))`, anahtar mevcutken de sıfır dizisini oluşturur. Yeni `_cc/_ac` yardımcıları bunu saat/coin döngüsünde tekrarlar. Ayrıca günlük yazma/okuma bütün dosyanın birden fazla bellek kopyasını oluşturuyor. **Düzeltme:** Dizileri yalnız ilk erişimde ayırın; günlükleri satır satır yazıp doğrulayın. 122×24.000 ölçeğinde iki yeni kalıcı dizi grubu yaklaşık 47 MB’dir; geçici tahsisler buna eklenir.

13. **[ORTA] Long/short raporu hafta başındaki eski bacağı yanlış sınıflandırıyor — `kapi/isim.py:57` —** Bütün haftanın katkısı yeni Pazartesi `q_yildiz` işaretine yazılıyor. Oysa Pazartesi 00:00–01:00 eski miktar geçerli; funding ve değişim saatindeki kapanış payı da eski bacağa ait olabilir. Yeni hedef sıfırsa katkı iki bacaktan da düşebilir. **Düzeltme:** Katkıları etkin eski/yeni miktar işaretleriyle ayırın; long+short+hedge toplamını haftalık carry toplamına karşı sınayın.

14. **[ORTA] Betimsel tavan raporu eksik ve S4 etiketi fazla geniş — `kapi/betimsel_kayit.py:73`, `kapi/betimsel_kayit.py:95` —** §6.6’nın istediği devreden kitap değerlendirilmeden yalnız `w_mevcut` ölçülüyor. S4 “bağlama” kontrolü sınırdan çok ilerideki ihlalleri de bağlama sayıyor. **Düzeltme:** Devreden emirlerle oluşabilecek kitabı ayrıca raporlayın; sınıra temas ile sınır aşımını ayrı ölçün.

15. **[ORTA] Veri ayrıştırma ortamı tamamen kilitlenmiyor — `kilit.py:93` —** Ortam yalnız Python/NumPy sürümlerini içeriyor; D yükleyicisinin kullandığı pandas sürümü dışarıda. Aynı zip hash’leriyle farklı ayrıştırma davranışı kilit tarafından fark edilmeyebilir. **Düzeltme:** En az pandas’ı ve kullanılan bağımlılık kilidini ortam kimliğine dahil edin.

## u41_u55

U-41–U-53 değerlendirmeleri mevcut kod açıklamalarına dayanıyor; eksik bağlayıcı belge metninin kabulü anlamına gelmiyor.

U-41 KABUL — Tanımsız sıralama girdisini dışlamak ve yetersiz adayda faktörü hesaplanamaz saymak muhafazakâr; uygulama bunu yapıyor.  
U-42 KABUL — Altı koşuda V2/V5 gerekliliği doğru; U-52’deki gerçekten yapılmayan K8 koşusu istisnası korunmalı.  
U-43 KABUL — Betimsel κ ve katsayı bandı tanımı tutarlı; izleme farkı P&L farkı olarak sunulmamalı.  
U-44 ITIRAZ — S4 bağlama kontrolü sınıra yakınlığı değil, aşımı da kapsayan tek yönlü eşitsizliği kullanıyor.  
U-45 ITIRAZ — Gerçekleşen kitap ölçülüyor; §6.6’nın istediği devreden kitap tavan denetimi eksik.  
U-46 KABUL — Sabit ağırlık varsayımıyla 5.000 USDT ölçeklemesi uygun bir betimsel hesap; bağımsız demo koşusu değildir.  
U-47 KABUL — Netleme toplamı ve günlük carry artığının mutlak toplamı ayrı tutuluyor.  
U-48 KABUL — Gün birimi deterministik; günlük mutlak toplam ile haftalık V4a birbirine karıştırılmıyor.  
U-49 ITIRAZ — Pazartesi yeni hedef işareti, eski miktarın funding ve geçiş saati katkısını doğru bacaklara ayırmıyor.  
U-50 KABUL — 01:00 geçerlilik aralığı ve taşınan s^C ile sıfır-kuralı karşılaştırması mimariyle uyumlu.  
U-51 ITIRAZ — B’nin carry pozisyonları A hedefinin tavanlarını etkileyebilir; bu hesap bağımsız A referansını temsil etmiyor.  
U-52 KABUL — İsim sayısı <30 iken K8’in kalması ve yapılmayan koşunun V2/V5 teknik ihlali üretmemesi uygun.  
U-53 KABUL — Günlükler, NAV yolları ve ana trend satırlarının mühür kapsamına alınması doğru; istisna çıktısı ayrıca kapatılmalı.  
U-54 ITIRAZ — İstenen bağlayıcı tanım bu commit’te bulunmuyor; içeriğini varsayarak kabul veremem.  
U-55 ITIRAZ — İstenen bağlayıcı tanım bu commit’te bulunmuyor; içeriğini varsayarak kabul veremem.

## sorular_1_7

1. KISMEN — K1/SR^K/U-09, seri başına ρ_üst, K1* kırpması, K2 büyük SE/tek bootstrap akışı/0,05 kantili, K5 tamsayı karşılaştırması, K6/K7, K9 ayrı regresyonları/açık aralıkları, K11 yükleme ve SE ölçeği, çift seri ve eşitlik yönleri uygun; K8 eşitlikleri ve sabit seride K10 sorunlu.
2. KISMEN — 143 tam hafta, 33 ay, T damgalı funding’in saat penceresi, carry/trend ölçekleri ve sınır NAV’ı doğru; V2’nin göreli formülü doğru fakat eksik günleri atlıyor.
3. KISMEN — Normal HUKUM/DENETIM/KOSU_OZETI yolunda doğrudan trend P&L’i görmedim; mühür dosya kapsamı uygun, ancak yakalanmayan NAV istisnası ekrana sızıyor.
4. KISMEN — Varsayılan `carry_haric=()` ve ek çıktı hesapları mevcut P&L aritmetiğini statik olarak koruyor; toplam özdeşliklerinin yapısı uygun, günlük NaN’ı reddediyor; çalıştırılmış eşdeğerlik kanıtı vermiyorum, bellek tahsisleri sorunlu.
5. KISMEN — V5 bağımsız serileştirme okuması olarak anlamlı fakat tam günlük/tüketim doğrulaması değil; V6 karşılaştırması carry durumundan etkileniyor, V1 kanıt bağı yetersiz.
6. HAYIR — Kod, parametre, veri, filtre, tohum ve eşik kapsamı büyük ölçüde mevcut; belge kümesi daraltılabiliyor, kabul önkoşulları denetlenmiyor, V1 kanıtı ve pandas ortamı kilitsiz.
7. KISMEN — NaN ve n<4 yollarının çoğu muhafazakâr; sabit korelasyon, K8 eşitliği, eksik V2 günü, günlük kesilmesi ve Andrews tahsisi açık. Belirgin Windows yol hatası veya kritik ölü kod görmedim.

## genel_hukum

Kapı kodu bu haliyle ön-kayıt kilidine ve D’de ilk P&L koşusuna hazır değil. Önce bağlayıcı belge eksikleri, mühür hata yolu, kilit/V1 önkoşulları ve V6 referans tanımı kapatılmalı; ardından düzeltmeler sentetik testlerle doğrulanmalı.