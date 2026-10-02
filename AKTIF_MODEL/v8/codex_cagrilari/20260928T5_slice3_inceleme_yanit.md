## bulgular

`[CIDDI] hedef_b.py:287 — Reduce-only sonrasında toplam risk yeniden aşılabiliyor`

MIMARI §3.5 T4-d ve §4.5.6, **nihai hedefte** V ≤ L(1+ω_C)τ ister; kod reduce-only kırpmasını son risk denetiminden sonra yapıyor. Karşı yönlü pozisyonun kaldırılması portföy riskini artırabiliyor: sentetik karşı örnekte L=0,001 için sınır 0,00018, dönen hedefin V’si **0,000197750**; kaydedilen `v_net` ise hâlâ 0,00018.

`[CIDDI] net_cozucu.py:150 — İç aralıkta geçerli κ bulunmasına rağmen carry sıfırlanıyor`

MIMARI §4.5 ve CARRY §3.3, uygun küçültme katsayısının çözülmesini ister; `hepsi_ok(0)` başarısızsa kod ara değerleri araştırmadan κ=0’a gidiyor. Sabit BTC=%35, ETH=%29,8; alt trend=−%4 ve carry=(+%1,+%1,−%1,−%1) örneğinde **κ=0,8** bütün tavanları sağlıyor: S1=%20, S2=%4, S4=%9,6. Kod bunun yerine carry’yi tamamen kapatıp trendi ayrıca 5/6 ile küçültüyor; önceki S4 aşımı düzelmiş, fakat çözüm seçimi hâlâ yanlış.

`[CIDDI] hedef_b.py:217 — K13 sanal trende uygulanınca düşük hacimde gerçek giriş oluşuyor`

§6.1’in V60<20M için yalnız çıkış tanımlayan kuralı gerçek net emirde korunmuyor. Sanal trend +q, carry −q ve gerçek pozisyon sıfırken, V60 düşüşü carry’yi kapatıyor; K13 önceki sanal trendi tuttuğu için gerçek kitapta yeni long açılıyor. V60=15M karşı örneğinde motor alış niyeti üretti ve dolum hesabı `MaliyetGirdiHatasi` ile durdu.

`[CIDDI] hedef_b.py:235 — Çözücü ve son denetim toleransları geçerli kararı durduruyor`

§4.5’in çözücü çıktısı, aynı tavanın son denetiminde kabul edilmelidir. `net_cozucu` S1 için 0,20+10⁻¹² kabul ederken burası 0,20×(1+10⁻¹²) kullanıyor. Mevcut carry fikstürünün 93. gününde L=5 ile çözücü **0,20000000000100002** üretiyor; son denetim bunu teknik hata sayıp kararı durduruyor.

`[CIDDI] ayristirma.py:134 — Sanal funding dolgusu gerçek net pozisyona bağımlı`

MIMARI §4.6–§4.7 ve CARRY §5.1–§5.2 uyarınca funding, sanal bacakların kendi miktarlarıyla hesaplanmalıdır. Kod eksik funding dolgusunu yalnız gerçek günlükte `funding_dolgu` olayı varsa bacaklara uyguluyor; net pozisyon sıfırken bu olay üretilmiyor. Sanal trend +1/carry −1 örneğinde eksik uzlaşma için carry dolgusu **−0,015** olması gerekirken sıfır çıktı; NAV özdeşliği yine geçtiği için mevcut kontrol hatayı gizliyor.

`[CIDDI] ayristirma.py:167 — Miktar içeren düzeltmede NAV özdeşliği hâlâ bozuluyor`

Önceki turun yalnız nakit düzeltmesi kapanmış; ancak §5.8’in izin verdiği miktar düzeltmesinde eklenen pozisyonun başlangıç değeri hesaba katılmıyor. Fiyat sürekli 100 iken `miktar=+1, tutar=−100` düzeltmesi gerçek NAV’ı değiştirmiyor, fakat ayrıştırma −100 icra artığı üretiyor. CARRY §5.5 özdeşlik hatası bu örnekte **100 USD**.

`[CIDDI] carry.py:284 — İşlem dışı mevcut long, haftalık funding tabanını atlıyor`

CARRY §3.2.2 ve MIMARI §4.3, F30≥−%50 şartını her haftalık kararda mevcut long’lara da uygular. `sabit_mevcut` isimleri F30 denetiminden geçmeden kitaba ekleniyor; yeniden nötrleme onları mutlaka sıfırlamıyor. Pazartesi kapanış barı eksik, F30’u −%60 olan mevcut long böylece korunabilir ve hafta içinde bu koşul tekrar sınanmadığından sonraki Pazartesi’ye taşınabilir; K8 gerçek pozisyonun işlem yasağını düzenler, bu seçim istisnasını tanımlamaz.

`[CIDDI] hedef_b.py:106 — Evren histerezisi pozisyon sahipliğine indirgenmiş`

§4.1’deki giriş/çıkış histerezisi carry evrenine aittir; kod “mevcut” olmayı `q_eski` içinde bulunmakla tanımlıyor. Önceki hafta aday olup orta dilimde kaldığı için pozisyon taşımayan isim, V30=15M olduğunda yeniden giriş şartına takılıyor; aynı isim pozisyon taşısaydı kalıyor. Bu durum n_C’yi yapay olarak düşürüp §4.1’in yarım bütçe veya tamamen kapanma kuralını yanlış tetikleyebilir.

`[ORTA] carry.py:110 — V60 düşüşü belge dışı zorunlu carry çıkışı getiriyor`

§4.1 carry kalışını V30≥10M üzerinden tanımlar; §4.4 hafta içi miktar değişikliklerini maske ve evren çıkışıyla sınırlar. Kod V30=15M, V60=19M olan maskesiz mevcut ismi zorunlu çıkarıp karşı bacağı da λ ile küçültüyor. §6.1’de düşük hacimde yeni giriş maliyetinin tanımsız olması, mevcut carry pozisyonunu zorunlu kapatma kuralı değildir.

`[ORTA] hedef_b.py:110 — Ortak matrisin carry aday kapsamı hafta içinde daralıyor`

§3.2 her kararda trend evreni, carry adayları ve BTC kapsamındaki ortak matrisi ister. `uygun` yalnız Pazartesi doldurulduğundan diğer günlerde pozisyon almamış carry adayları matristen düşüyor. Ham çift korelasyonları PSD olmadığında projeksiyon tüm matrise bağlıdır; bu isimlerin çıkarılması kalan trend/carry alt bloklarını da değiştirir.

`[ORTA] hedef_b.py:304 — Kaydedilen κ, belgede tanımlanan sanal miktarı üretmiyor`

§4.7 ve CARRY §5.1 sanal alt miktarını q^C,v=κ^C·q^C* olarak tanımlar. Kod miktara ayrıca T4-c, global ve T4-d katsayılarını uygularken `carry['kappa']` alanına yalnız net çözücünün κ’sını yazıyor. Örneğin κ=1 ve T4-c katsayısı=0,5 olduğunda sanal miktar q^C*/2 oluyor; güvenlik küçültmesi gerekli olsa da yayımlanan katsayı ile miktar sözleşmesi uyuşmuyor.

`[ORTA] durum.py:169 — λ günlükten carry durumuna geri kurulmuyor`

§5.8 carry miktarlarıyla birlikte λ’nın da karar kaydından kurulmasını ve kaçırılan haftalık kararda korunmasını ister. `StratejiDurumu` λ taşımıyor; `hedef_b` her gün `lam=1` ile başlıyor ve normal hafta içi kararında bunu tekrar kaydediyor. Pazartesi λ=2/3 olan kitabın Salı kaydı λ=1 oluyor; hafta içi çıkışın bağlayan bacağı da `bagli2` hesaplanmasına rağmen kayboluyor.

## yorumlar_Y1_Y11

- **Y1: itiraz** — §6.1 giriş maliyetini sınırlayabilir; V60 düşüşünden zorunlu carry çıkışı türetilemez.
- **Y2: itiraz** — Evren üyeliği ile pozisyon sahipliği farklıdır; orta dilimdeki mevcut adayların histerezisi kayboluyor.
- **Y3: kabul** — Tam sayıya aşağı yuvarlama ve deterministik eşitlik çözümü, %30 kesiminin makul tamamlamasıdır.
- **Y4: itiraz** — Eksik R30 için dolgu §4.2’de tanımlı değil; ayrıca eşitliklerde `(m+1)/2` gerçek sıra medyanı olmayabilir: `[2,2,2,4]` için medyan 2, kodun dolgusu 2,5.
- **Y5: itiraz** — Ortak tanımlı günlerde OLS uygundur; hesaplanamayan β̂ yerine 1 koymak §4.3’te tanımlanmamış ayrı bir hedge kuralıdır.
- **Y6: kabul** — Genişlik indiriminin bütçe aşamasında, isim tavanlarından önce uygulanması §4.4 sırasıyla tutarlıdır.
- **Y7: itiraz** — Gerçek pozisyonun sabit tutulması uygun; bunun haftalık long funding tabanını atlatması uygun değil.
- **Y8: kabul** — İlk haftalık karar öncesinde carry’nin sıfır olması karar takvimiyle uyumludur.
- **Y9: itiraz** — K8 net pozisyonu sabitler; sanal trendi ayrıca değişmez tutmak, carry değiştiğinde §4.7’deki hedef=sanal trend+sanal carry eşitliğini korumuyor.
- **Y10: itiraz** — K13’ün yalnız sanal trende uygulanması gerçek düşük hacimli girişe izin veriyor; reduce-only sonrasında T4-d de yeniden sınanmıyor.
- **Y11: itiraz** — κ=0’ın uygunsuz olması, uygun bir iç aralık bulunmadığını göstermez; doğrulanan κ=0,8 örneği mevcut son-çare geçişini çürütüyor.

## test_kor_noktalari

- S1/S2/S4’ün birlikte bağladığı, sabit isimler ve farklı L değerleri içeren çözücü→nihai hedef testleri eksik.
- Reduce-only sonrasındaki nihai risk ve sanal/net eşitliği sınanmıyor; mevcut eşitlik testi reduce-only günlerini ve sabit isimleri açıkça atlıyor.
- Pozisyonsuz mevcut aday, V30/V60 ayrışması ve işlem dışı mevcut long’un haftalık funding tabanı kapsam dışı.
- Net pozisyon sıfırken sanal funding dolgusu ve miktar+nakit düzeltmesi yok; yalnız toplam özdeşlik bacak muhasebesini doğrulamıyor.
- T4-c bağladığında yayımlanan κ/miktar özdeşliği, λ’nın durumdan yeniden kurulması ve hafta içi ortak matris kapsamı sınanmıyor.

## genel_hukum

Slice 3 doğruluk açısından kabul edilmeye hazır değil; nihai risk, çözücü seçimi ve carry muhasebesinde doğrulanmış hatalar var. Önceki turun (a)–(c) özgül karşı örnekleri kapanmış; (d) geç funding zamanlamasını belgelenmiş canlı sınır olarak ayrı tuttum. A yolunda davranış değişikliği saptamadım ve 43 farklı mevcut test geçti; karar PIT testleri de geçti, ancak bunlar yukarıdaki karşı örnekleri kapsamıyor.