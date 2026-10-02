## dogrulama

Statik inceleme; kod ve test çalıştırılmadı. Kod yolları `AKTIF_MODEL/v8/` köküne göredir.

- T12-1: KISMEN — Eski+yeni özdeşliği, uzlaşma ve tam kapanış korunuyor; pencere sınırındaki epizot kaybı ve yeniden açılışla çakışan geç funding ataması sorunlu.
- T12-2: KAPANDI — Toplama sırası sabitlendi; iki tohumlu gerçek B testi uygun regresyon kapsamı sağlıyor, çok işçi ve kesinti/devam dumanını kapsamıyor.
- T12-3: KISMEN — Kapı bütün Düzey 2 türlerinde çağrılıyor; tolerans makul, ancak ayrıştırmadaki NaN özet hata hesaplanırken gizlenebiliyor.
- T12-4: KISMEN — Yarım ek liste ve zarfsız NPZ korunuyor; başlangıç iş listesinin geçici dosyası karantinadan önce ezilebiliyor.
- T12-5: KAPANDI — Banka takvimi yetersiz Pazartesileri None kaydediyor; önceki varyans taşınmıyor, yeterli/yetersiz/toparlanma testi mevcut.
- T12-6: KAPANDI — Dilim bar sayısı korunuyor; ilk/son saat denetimi gerçek yaşam sınırlarına taşınmış, geçerli boşluk hareketi testi eklenmiş.
- T12-7: KAPANDI — Varsayılan motor başlangıcı verinin ilk günü; durum kesintisiz ilerliyor, ölçütler değerlendirme penceresinden hesaplanıyor.
- T12-8: KAPANDI — B9 ve B10 artık B serisinden hesaplanıyor; carry maliyetinin stres altında sabit tutulması ön-kayıtta açıklanmış.
- T12-9: KAPANDI — HAR özeti ve beta aynı baytlardan türetiliyor; gerçek yürütücü işçileri parametre kimliğini ve verilen betayı doğruluyor.
- T12-10: KAPANDI — Düzey 2-b kabulünde e_b10=None kullanılarak B10 açıkça dışlanmış.
- T12-11: KAPANDI — Epsilon kaldırılmış; yuvarlanmış ızgara adayı kesin x<e koşuluyla doğrulanıyor, sınır örnekleri test edilmiş.
- yorum-c: KAPANDI — A’dan B9/B10 kopyalama kaldırılmış; B’ye özgü ikame ve ikinci portföy hesapları ön-kayıtla uyumlu.
- yorum-e: KAPANDI — Fiyat geçmişinin görünmesiyle yetinilmiyor; pozisyon, histerezis ve carry durumu ısınma boyunca ilerletiliyor.

## yeni_bulgular

1. **[ORTA] Pencere başında kapanan epizot kayboluyor** — `banka/degerlendirme.py:94`, `banka/pnl.py:142` — Diziler kesildikten sonra önceki pozisyon bilinmiyor. İlk saatte kapanan pozisyonun eski payı, örneğin `q=[0], eski=[7]`, hiçbir epizota yazılmıyor; paydada kalıyor. — Pencere öncesi pozisyon/epizot kimliğini taşıyın; yalnız pencere P&L’ini toplayın.

2. **[ORTA] Yeniden açılış saatindeki geç funding yeni epizota gidiyor** — `banka/pnl.py:143` — `q=[1,0,-1]` dizisinde son saatte eski pozisyona gelen funding, `ep[h]` önceliğiyle yeni short’a yazılıyor. Toplam özdeşlik bunu yakalamıyor. — Geç funding’i kaynak pozisyonun epizot kimliğiyle ilişkilendirin; yeniden açılış senaryosunu sınayın.

3. **[CIDDI] Ayrıştırmadaki NaN muhasebe kapısından kaçabiliyor** — `kalibrasyon/yurutucu.py:75`, `motor/ayristirma.py:322` — Bileşen toplamı NaN olduğunda `max(hata, NaN)` önceki sonlu hatayı koruyabiliyor; kapının özet hata üzerindeki `isfinite` kontrolü geçiyor. — Bileşenleri ve artık dizisini özetlemeden önce sonluluk denetiminden geçirin; bozuk B ayrıştırması testi ekleyin.

4. **[ORTA] İlk iş listesi yazımının artığı korunmuyor** — `kalibrasyon/kosucu.py:132` — Karantina taramasından önce iş listesi oluşturuluyor. Önceki kesintiden kalan `IS_LISTESI.json.gecici`, asıl dosya yoksa `_atomik` tarafından yeniden açılıp eziliyor. — Geçici dosyaların karantinasını iş listesi yazımından önce yapın.

5. **[ORTA] Yorum-d’nin kaynak sınırlaması ön-kayıtta kaybolmuş** — `AKTIF_MODEL/ciktilar/v8_asama4_20260927_01/BANKA_ONKAYIT_TASLAK.md:808` — Tek kayıt dosyasında Sharpe bulunmamasından §3.3 gereği doğrudan 0,30 sonucu çıkarılıyor; T12, başka kullanılabilir kayıtların yokluğunun doğrulanmadığını belirtmişti. — Kaynak kapsamının yalnız bu dosya olduğu kararını açıkça yazın veya kullanılabilirlik hükmünü kanıtla destekleyin.

## genel_hukum

Statik incelemeye göre kalan epizot, muhasebe ve dosya koruma açıkları giderilmeden kod dondurmaya ve kabul amaçlı duman denetimine hazır değil.