## bulgular

1. **[CIDDI] funding.py:84 — Geç gelen gerçek funding kaydı işlenemiyor.** §2.6, düzeltmenin kaydın geldiği saatte nakde işlenmesini ister. Kod yalnız `damga_ms == t_ms` olan son kaydı işler; `FundingSerisi` uzlaşma zamanı ile geliş zamanını ayıramaz. Örneğin 08:00 uzlaşması 12:00’de gelirse gerçek ödeme işlenmez; damgayı 12:00 yapmak ise yanlış pozisyonu ve mark fiyatını kullanır.

2. **[CIDDI] funding.py:86 — Yeni gerçek kayıt, kapsamadığı dolguları da geri alıyor.** §2.6 yalnız gerçek kaydın **kapsadığı aralıktaki** dolguların ters kaydedilmesini ister. Kod son gerçek kayıttan beri bütün dolguları topluca siler; gerçek funding aralığı ve dolguların kapsadığı saatler korunmaz. Sekiz saatlik düzende 400. saat kaydı eksikken 408. saatin normal kaydı geldiğinde, 400. saate ait eksik borç da silinir; bellekteki örnekte toplam nakit yalnız 408. saatin −0,01 tutarına döndü.

3. **[CIDDI] geri_test.py:65 — Tespitten önce kapanan pozisyonun funding borcu atlanıyor.** §2.6 ilk tespitte geçmiş saatleri, o saatlerdeki `q(h−)` ile tahakkuk ettirir. Orkestrasyon yalnız hâlen pozisyonu veya önceden yazılmış dolgusu olan coinleri işler. Pozisyon 10. saatte kapanıp eksik funding 12. saatte saptanacaksa coin döngüden çıkar; doğrulamada saf funding fonksiyonu borç üretirken orkestratör hiçbir kayıt üretmedi.

4. **[CIDDI] karar.py:50 — İlk kararda ısınma döneminin maske geçmişi kayboluyor.** §2.4–§2.5, ısınma geçmişini ve maskeden dönüş için aylık seçimle birlikte 30 temiz günü gerektirir. `maske_ms is None` durumunda yalnız bugünün hijyeni işlenir; `kos()` da geçmiş sayaçları kurmadan T0’da başlar. Sentetik örnekte 90. gün donan coin 92. gün maskesiz seçildi; aynı geçmiş gün gün işlendiğinde hâlâ maskeliydi.

5. **[CIDDI] geri_test.py:139 — Gün içinde bilinen borsa boşluğunda eski girişler dolmaya devam ediyor.** §5.4, borsa çapı boşlukta devreden emrin risk artıran parçasını iptal eder. Saatlik dolum yolunda boşluk kontrolü veya bu iptal yoktur; kontrol günlük karara bırakılmıştır. Üç adaydan ikisinin barı eksikken, kesintinin bilindiği sonraki saatte üçüncü coindeki eski giriş emri yeni pozisyon açtı.

6. **[CIDDI] karar.py:143 — Reduce-only kararı mevcut azaltıcı emri silebiliyor.** §5.2 ve §5.4, borsa boşluğunda eski risk azaltan parçanın korunmasını açıkça ister. Kod yalnız `sabit` coinlerde bu ayrımı yapar; diğer coinlerin emirlerini tamamen iptal eder. Doğrulamada mevcut ağırlık %4, yeni reduce-only hedef %4 ve eski yarım kapatma emri varken emir tamamen iptal edildi, yerine hiçbir niyet yazılmadı.

7. **[CIDDI] gorunum.py:268 — Uzun kesintide referans küme unutuluyor.** §2.6, kesintinin sürdüğü her kararda reduce-only davranışı gerektirir. Referans yalnız sorgu başlangıcından 24 saat geriye taranarak bulunuyor; kesinti daha önce başlamışsa kalan çalışan coinler yeni referans oluyor. Beş adayın üçünün 72 saat kesildiği örnekte son günlük sorgu **0 boşluk saati**, kesintinin başından yapılan sorgu **72 saat** buldu.

8. **[CIDDI] hedef.py:220 — Sabit pozisyon varsa hedef tavan ihlali kabul ediliyor.** §3.5 T4-d, giderilemeyen hedef ihlalini teknik hata sayar; gerçekleşen kitap istisnası hedef kitaba taşınamaz. Kod herhangi bir sabit isim bulunduğunda kalan toplam risk ihlalini hata yapmaz; `tavanlar.py` ayrıca sabit isimlerin isim tavanını ihlal bayrağına katmaz. Sabit %25 alt-long örneğinde %6 isim tavanı aşılmasına rağmen `sabit_ihlal=False` döndü.

9. **[CIDDI] durum.py:107 — Borsa pozisyon düzeltmesi durumdan yeniden üretilemiyor.** §5.8, borsa kaydıyla uyuşmazlığın düzeltme olayıyla giderilmesini ve durumun günlükten kurulmasını ister. `duzeltme` yalnız nakdi değiştirir; miktar, pozisyon, devreden emir ve pozisyon geçmişi değişmez. Eksik bir dolum için miktarlı düzeltme yazıldığında pozisyon boş kalır; sonraki hedef ve funding yanlış pozisyon üzerinden hesaplanır.

10. **[ORTA] hijyen.py:71 — Borsa boşluğu funding donma sayacından çıkarılmıyor.** §2.6, boşluk saatlerinin donma sayaçlarına girmemesini ister. `_olcut_c` boşluk kümesini almadan son 16 takvim saatini değerlendirir. Son gerçek funding’den sonra 14 saat ortak kesinti ve ardından bir çalışan bar bulunan örnekte `(c)=True` çıktı; ortak kesinti coin maskesine dönüşebiliyor.

11. **[ORTA] hijyen.py:55 — Y2, hem ardışık donmayı hem günlük boşluğu daraltıyor.** §2.5(b) altı ardışık bar, §2.5(d) son gündeki sekiz saati aşan bar boşluğu der; yalnız `(b)` ardışıklık şartı taşır. Kod `(b)` serisini günlük pencere başında sıfırlar, `(d)` içinse toplam yerine en uzun ardışık boşluğu ölçer. Gece yarısını bölen 3+3 donmuş bar iki kararda da yakalanmadı; son gündeki dokuz ayrı eksik saat de `(d)` üretmedi.

12. **[ORTA] hedef.py:51 — İşlem dışı günün getirisi risk tahminine giriyor.** §3.2, işlem dışı günlerde getirinin eksik olmasını ister. `coin_gunluk` yalnız kapanışın varlığına ve maskeye bakar; `(d)` ile işlem dışı kalan günleri dışlamaz. Gün içinde dokuz saat boşluğu olup son saat kapanışı bulunan örnekte `(d)=True` iken getiri sonlu ve geçerli kaldı; σ̂ ve Σ̂ yanlış gözlem kümesiyle hesaplanır.

13. **[ORTA] emir.py:99 — Hacim tabanı altındaki giriş, çıkış gibi fiyatlanarak geçiriliyor.** §2.3 giriş/kalış tabanını 20M, §6.1 bunun altındaki dilimi yalnız çıkış için tanımlar. Günlük hedef üretimi hacim tabanını yeniden denetlemiyor; bu satır gerçek girişte de `cikis=True` geçirerek maliyet modülünün reddini kaldırıyor. Aylık seçimde V60=48M olup sonradan 12M’ye düşen, donma tetiklemeyen sentetik üyede yeni long giriş üretildi.

14. **[ORTA] durum.py:131 — İşaret değiştiren emrin korunan kapanış parçası kapanış niteliği kazanmıyor.** §5.4 işaret değiştiren emrin sıfıra kadarki kısmını korur; §5.1 tam kapanışın son parçasını minNotional’dan muaf tutar. Kısmi iptal yalnız `kalan` alanını değiştirir, `tam_kapanis=False` kalır. `q=0,3`, eski emir `−0,8`, fiyat 10 ve minNotional 5 örneğinde korunan yaklaşık `−0,3` parça `min_notional` nedeniyle dolmadı.

15. **[ORTA] durum.py:155 — Bozulmuş hash zinciriyle durum türetilebiliyor.** §5.8’in yetkili günlüğü değişikliklerin tespit edilmesine dayanır. `kayitlar()` değiştirilebilir `veri` sözlüklerini dışarı verir; `durum_turet` zinciri doğrulamadan bunları uygular. Başlangıç NAV’ı 100’den 999’a değiştirilince `dogrula()` yanlış döndüğü hâlde durum türetme 999 nakdi kabul etti; artımsal durumla yeniden kurulan durum ayrışabilir.

## yorumlar_Y1_Y5

- **Y1 — Kabul:** Kesinti boyunca son temiz referansı korumak §2.6’nın süreklilik şartıyla uyumlu; mevcut 24 saatlik geri tarama bunu garanti etmiyor.
- **Y2 — İtiraz:** Boşluk saatlerinin dışlanması doğru; `(d)` için ardışıklık eklemek ve `(b)` serisini gece yarısında kesmek belgeyi daraltıyor.
- **Y3 — Kabul:** §3.1 mevcut ağırlığın sabit tutulmasını destekliyor; ancak çözümsüz tavan ihlalini başarılı hedef olarak döndürmek §3.5’e aykırı.
- **Y4 — İtiraz:** §5.4 borsa boşluğunda azaltıcı parçayı açıkça korur; yeni niyet eski azaltmayı karşılamayabilir.
- **Y5 — İtiraz:** “Muhafazakâr fiyatlama”, §6.1’de tanımlanmayan girişe izin vermez; §2.3 hacim tabanıyla birlikte çözülmelidir.

## test_kor_noktalari

- Funding testleri kalıcı eksik kayıtla aralık uzamasını ayırmıyor; geliş zamanı, değişen pozisyon ve tespitten önce kapanış senaryoları yok. Bütün dolguların silinmesini doğru sonuç kabul eden test mevcut.
- İlk karar öncesindeki donma ve maskenin T0’a taşınması sınanmıyor; maske geçişlerinin tek başına doğru olması orkestrasyonu doğrulamıyor.
- Boşluk testleri kısa kesintilere ve ardışık eksik saatlere odaklı; uzun kesinti, gece yarısını aşan donma ve gün içindeki giriş iptali eksik.
- “Parite” testi aynı karar fonksiyonunu aynı geri test günlüğünden tekrar çağırıyor; gerçek geliş zamanları, borsa düzeltmeleri ve bozuk zincirin tüketilmesi sınanmıyor.
- Uçtan uca fikstür long ağırlıklı; short delist, işaret değişiminden kalan küçük kapanış, hacim tabanı geçişi ve sabit isimli hedef ihlalleri yeterince sınanmıyor.

## genel_hukum

Slice 2, tasarım belgesine doğruluk açısından kabul edilebilir durumda değil; özellikle funding borcunun kaybolması, maske geçmişi ve boşlukta emir yönetimi düzeltilmeli. Dosyaya yazmadan çalıştırılan **169 mevcut test geçti**, fakat yukarıdaki sentetik karşı örnekler testlerin önemli sözleşme ihlallerini kaçırdığını gösterdi. Hiçbir dosya değiştirilmedi.