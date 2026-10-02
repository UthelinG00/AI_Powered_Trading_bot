# Carry kapısı belirsizliklerinin çözümü (5.01b; ana oturum, Opus)

Girdi: `OLCUT_LISTESI.md` "Belirsizlikler" (U-01…U-40). Kaynak: `CARRY_KAPISI_ONKAYIT_TASLAK.md`, `MIMARI.md` §4.7,
`v8/motor/ayristirma.py`. Hiçbir D performans verisi görülmeden, kilitten önce. İlkeler: (1) ön-kaydın kendi ilkeleri
("fiyat kazancı kredilenmez", §6.2 "her ölçütte B aleyhine olan"); (2) motor koduyla tutarlılık; (3) CARRY §5.6'nın
kendi kuralı gereği MIMARI'nin güncel metni önceliklidir. Bu kararlar kilitten önce CARRY ön-kaydına "Uygulama
netleştirmeleri" eki olarak işlenir ve Codex kilit öncesi okumasında denetlenir.

## Grup 1 — bağlayıcı kararı etkileyenler (29 Eylül)

| Kod | Karar | Gerekçe |
|---|---|---|
| U-01 | **r^trend,net** = trend sanal bacağının net haftalık getirisi: r^T_w = Σ_{h∈w}(trend_fiyat + trend_funding − trend_maliyet)_h / (L · NAV_{w başı}). Gerçekleşen karşılığı r^{T,g}_w = r^T_w + a^T_w, a^T = artik_trend (aynı ölçek). "Trend P&L'i kapıda hesaplanmaz" (§6.3) = yazılmaz, raporlanmaz, açılmaz; §2 gereği yalnız ρ̂ ve ρ_üst için bellekte hesaplanır, hüküm dosyasına yalnız ρ̂/ρ_üst yazılır | "Net" = maliyet sonrası, r^N'nin (sanal carry, artıksız) simetriği; ölçek korelasyonu etkilemez ama tanım sabitlenir |
| U-10 | ρ̂ ve ρ_üst iki çift için ayrı: sanal (r^N, r^T) ve gerçekleşen (r^{N,g}, r^{T,g}). n_w = iki serinin de tanımlı olduğu hafta sayısı (normalde 143; eksik hafta çift olarak düşer). K8 yeniden koşusu K1\* kullanmaz (eşik > 0) | Çift seri kuralının trend tarafı |
| U-22 | ρ̂ = ±1 ise atanh girişi ±(1 − 1e-12)'ye kırpılır; ρ̂ tanımsızsa (sıfır varyans, n_w < 4) ρ_üst = +1 alınır (K1\* = 0,370, K10 kalır) | Belirsizlikte B aleyhine (§6.2) |
| U-07 | **K8 isim katkısı**: yalnız alt isimler sıralanır; isim i'nin katkısı N_i = F_i + P_i − C_i (sanal carry bacağının o isimdeki funding, fiyat ve maliyeti; T0'dan son haftaya). BTC hedge'i isim değildir, aday listesinden çıkarılamaz; sıralamaya girmez. "Hiç tutulmuş isim" = değerlendirme döneminde en az bir saat q^C,v_i ≠ 0. **Kod gereği:** ayristirma.py'ye isim başı carry satırı (carry_coin: fiyat + funding − maliyet) eklenir (trend_coin'in simetriği) | K8'in amacı tekil aday bağımlılığı; hedge carry'nin nötrleme aracıdır |
| U-08 | CARRY, MIMARI'nin güncel kurallarını birebir kullanır (CARRY §5.6'nın kendi hükmü): sıfır/sıfır isim-gününde **son sıfır olmayan s^C payı taşınır** (MIMARI §4.7 güncel), κ_etkin,t, V60 < 20M çıkışı ve net kitaba yalnız-azaltma istisnası. V5, κ^C_t yanında **κ_etkin,t**'yi de birebirlik için denetler. BR-24 tanısı yeniden tanımlanır: sıfır/sıfır isim-günlerinde güncel kuralla carry'ye düşen artık ile s^C = 0 kuralında düşecek olanın farkı (karşılaştırma tanısı). CARRY metni (§5.1, §5.6, V5, §11) bu yönde eşitlenir | İki belgede iki kural olamaz (CARRY §5.6) |
| U-09 | Gerçekleşen seride SR^K'nın artık terimi yalnız aleyhe sayılır: SR^K(r^{N,g}) = [ort(r^F − r^C) + min(ort(r^P), 0) + **min(ort(a^C), 0)**] / std(r^{N,g}) · √52 | a^C icra artığının fiyat P&L'ini de içerir; H1 "fiyat kazancı hiç sayılmadan" ve KC-06 niyetiyle tutarlı olan muhafazakâr okuma. Etki V4a (Σ\|a\| ≤ 0,10·Σ\|r^N\|) ile sınırlı. Codex kilit öncesi okumasında ayrıca sorulacak (bağlayıcı formül netleştirmesi) |
| U-20 | İcra artığının işlevsel tanımı §5.5 özdeşliğini kapatan terimdir: e_i miktarının fiyat + funding P&L'i, artı delist uzlaşmasının son kapanıştan farkı (ve canlıda düzeltme). Kodun tanımı (ayristirma.py) bağlayıcıdır; CARRY §5.6 ve MIMARI tablo ifadesi buna göre netleştirilir | Özdeşlik (V2) tek tanımı zorlar; delist farkı gerçek pozisyona aittir, sanal bacaklara değil |
| U-23 | C_h toplamı BTC hedge bacağının sanal dolum maliyetini de içerir (kodla aynı) | F ve P hedge'i içeriyor; N = F + P − C tutarlılığı |
| U-02 | NW: Bartlett ağırlığı w_j = 1 − j/(ℓ + 1); ortalamanın varyansı (γ₀ + 2 Σ_{j=1}^{ℓ} w_j γ_j)/n, γ_j = (1/n) Σ (x_t − x̄)(x_{t−j} − x̄); küçük örneklem düzeltmesi yok. Regresyonda HAC sandviç (X'X)⁻¹ Ŝ (X'X)⁻¹, Ŝ = Γ̂₀ + Σ w_j (Γ̂_j + Γ̂_j'), artıklarla. "Büyük SE" seçimi **parametre başına** (her katsayı için ℓ = 4 ve ℓ = 12'den büyük olan) | Standart Newey–West (1987); parametre başına seçim her ölçütte B aleyhine kuralının en katı hali |
| U-03 | K2 bootstrap istatistiği: ort(r^F − r^C). Dairesel blok: başlangıçlar {0…n−1} üzerinde tekdüze, blok sarar, çekiş başına ⌈n/b⌉ blok, ilk n alınır. Tek Generator(PCG64(20260928)): önce b = 4'ün 10.000 çekişi, sonra b = 12'nin 10.000 çekişi. Alt sınır = çekiş ortalamalarının 0,05 kantili (numpy varsayılan doğrusal). İkisinin küçüğü > 0 olmalı | HAR seçimindeki bootstrap biçimiyle aynı aile; tohum sırası sabitlenir |
| U-04 | Bütün std/sd'ler örneklem (ddof = 1) | Banka ölçüt kütüphanesiyle aynı (banka/olcutler.py) |
| U-05 | Aksi yazılmadıkça bütün ölçütler ve V koşulları ana koşudan (m_c = 1, taban delist h_L %10 / h_S %5); K8 yeniden koşusu da m_c = 1, taban delist | "m_c = 1, taban delist" K1'de açık, diğerleri için örtük olanın yazılması |
| U-06 | K5 aylık seri: ay m için (r^F − r^C)_m = Σ_{h∈m}(F − C)_h / (ω_C · L · NAV_{ay başı}); NAV_{ay başı} = ayın ilk günü 00:00 NAV'ı (T0 ayında T0 NAV'ı). Aylar 2023-10 … 2026-06 (33); T0 sonrası bütün günler dahil (2023-10-01 ve 2026-06-29/30 dahil) | n_m = 33 takvim ayı; haftalık serinin kısmi hafta dışlaması aylık seriye taşınmaz |

Grup 2 (U-11…U-19, U-21, U-24…U-40: V koşullarının ayrıntıları, hüküm dosyası yerleşimi, betimsel raporlar,
tarihsel ifadeler) ayrı commit'te.

## Grup 2 — V koşulları, hüküm dosyası, betimsel raporlar, metin (30 Eylül)

| Kod | Karar | Gerekçe |
|---|---|---|
| U-11 | V1, V2, V5 ihlali **teknik hatadır** (motor/muhasebe/tek defter): §7.3 hüküm öncesi dalı uygulanır (bağımsız sentetik fikstürle gösterilir, en fazla bir teknik yeniden koşu). V3, V4a, V4b, V6 ihlali **esastır**: sonuç A, yeniden koşu yok. "Teknik geçersizlik" = kapı çıktısından bağımsız bir testle gösterilen muhasebe, bakış-ileri, funding işareti, maliyet işareti, parite ya da tek defter hatası | V1/V2/V5 hesaplamanın doğruluğunu, V3/V4/V6 carry nesnesinin temsil gücünü denetler |
| U-12 | V1 bir kez (dondurulmuş motorun test raporu). V2 ve V5 **her koşuda** (ana, m_c = 2, m_c = 3, K8, delist senaryoları); ihlal U-11'deki teknik dala gider. V3, V4a, V4b, V6 yalnız ana koşuda | Muhasebe her koşuda tutmalı; temsil koşulları ana koşunun özelliğidir |
| U-13 | V6: gün "farklı" ⇔ max_i \|w^T\*_B,i − w^T_A,i\| > 1e-9 (NAV ağırlığı). Karşılaştırılan ikisi de **bant öncesi** hedeftir (B: MIMARI §4.5 adım 5'teki w^T\*; A: `hedef_agirlik` çıktısı). Payda: T0 sonrası bütün karar günleri | Tavan etkileşimi bant öncesi hedefte görünür; 1e-9 kayan nokta gürültüsünün üstü |
| U-14 | V3 "sıfır hafta": Pazartesi kararında carry kitabı boş (bütün q^C\* = 0) — nedeni ne olursa olsun (n_C < 10, bir bacak boş, κ = 0). Karar Pazartesiye göre | Parantez bir örnektir; haftalık kitap Pazartesi kurulur |
| U-15 | V1 kapı koşusunda dondurulmuş motor kimliğini taşıyan son `v8_calistir.py test` raporundan okunur (motor kimliği eşleşmeli, başarısız 0). Carry birimi denetiminde "1e-9" göreli: \|vol − τ\| ≤ 1e-9·τ | Adım 0 testleri kodla hash'e bağlanır |
| U-16 | V2: her gün \|özdeşlik farkı_d\| / NAV_{d başı} ≤ 1e-8 (göreli) | "1e-8 NAV içinde" ifadesinin oran okuması |
| U-17 | V2 fark, V3 payı, V4a/V4b oranları ve V6 oranı hüküm dosyasına; denetim dosyasında yalnız geçti/kaldı | §7.2'nin V4 notunun genellemesi |
| U-18 | K3/K4 hüküm dosyasında değer + "geçti/kaldı (bağlayıcı değil)" etiketiyle | §6.3 "yalnız rapor" |
| U-19 | x_B, x_A haftalık basit getiri: Pazartesi 00:00'daki son kapanıştan bir sonraki Pazartesi 00:00'daki son kapanışa (motorun sk değerlemesi). x_A: o Pazartesinin carry aday evrenindeki alt isimlerin (BTC hariç) eşit ağırlıklı ortalaması, ağırlık hafta boyu sabit; hafta içinde barı biten isim son kapanışıyla kalır | P&L değerlemesiyle aynı fiyat kaynağı |
| U-21 | Delist senaryoları (h_L %50, %90) tam yeniden koşudur (m_c gibi); betimsel | Yeniden fiyatlama pozisyon yolunu yansıtmaz |
| U-24 | x_R, x_S: sıralama Pazartesi t'de motorun PIT R30 ve s^trend değerleriyle; getiri **aynı haftanın** (t → t + 7g, r^P_w ile hizalı) getirisi. Üst/alt %30 = ⌊0,30·n⌋ isim (en az 1); uzun−kısa = ort(uzun) − ort(kısa). Sıralama bütün carry adaylarında (q^C\* = 0 olanlar dahil) | Faktör ve r^P aynı haftada ölçülmeli; "sonraki hafta" sıralama kararından sonraki hafta demektir |
| U-25 | Sıfır/sıfır tanısı isim başı artık ister. **Kod gereği:** ayristirma.py'ye isim başı artık (artik_coin) çıktısı eklenir | U-07'deki carry_coin ile birlikte |
| U-26 | Hüküm sonrası kabul edilen sınıflar yalnız dört sınıftır; tavan çözücüsü hatası ancak bunlardan birinde (ör. özdeşlik) görünürse kabul edilir | §7.3 listesi kapalıdır |
| U-27 | V4b: sd, 143 haftalık r^N serisinin tamamı üzerinden (ddof 1), tek sayı; her hafta \|a^C_w\| bununla karşılaştırılır | Gösterim hatası |
| U-28 | V5 toleransı: κ^C_t, κ_etkin,t, s^C için mutlak 1e-12; q^C,v (coin adedi) için göreli 1e-12·max(1, \|q\|) | Boyutlar farklı |
| U-29 | NAV_{w başı} = Pazartesi 00:00 NAV'ı (önceki günün gün sonu 'nav' kaydı) | Karar anı; banka ölçüt kütüphanesindeki gün sınırıyla aynı |
| U-30 | Kapı NAV'ı = **100.000 USDT** (açık soru yanıtları #4 ve #13: birincil NAV 0,1M, kapı NAV'ı ona bağlı); KILIT.json'a yazılır | Değer zaten kararla belli |
| U-31 | Yeniden koşuların (m_c = 2, 3, K8, delist) trend satırları hiç yazılmaz; trend mühür dosyası yalnız ana koşunun trend satırlarını taşır | Mühür kapsamı en dar hali |
| U-32 | BR-11/12/14 tanımları banka R5 ile aynı (MIMARI §3.5, §5.7; BANKA §2.5 T4) | Tek tanım |
| U-33 | BR-02 çeyrek tablosu: her takvim çeyreği için hafta sayısı, ort r^F, r^C, r^P, r^N, SR^K(r^N) | Tanımın yazılması |
| U-34 | BR-03 MDD: r^N ve r^{N,g} için haftalık, bileşik (Π(1 + r)) yol, carry birim ölçeği | Banka B11 ile aynı biçim |
| U-35 | BR-09: Andrews (1991) Bartlett, AR(1) takılı otomatik gecikme ℓ = ⌈1,1447·(α̂·n)^{1/3}⌉ | Standart yöntem |
| U-36 | BR-20: SR(r^N) için %90 yüzdelik aralık, dairesel blok 4 hafta, 10.000 çekiş, tohum 20260929 (K2'den ayrı akış) | Tanımın yazılması |
| U-37 | BR-27: 2×2 = 4 birleşim (SR_T,ref × k); ρ_K1 kırpması [0; 0,30] korunur | Izgaranın tam hali |
| U-38 | δ_P = %4/yıl birim ⇒ haftalık δ_P/52; TOST haftalık ortalama üzerinde | Doğrusal yıllıklandırma |
| U-39 | §0 ve §12'ye "tarihsel; güncel eşik §6.3" notu eklenir (metin düzeltmesi) | Okur yanılgısını önler |
| U-40 | "Yeniden koşma yoktur" (§7.1) = sonucu kurtarmak için eşik/parametre değiştirerek koşu yasağı. §3.6'daki tam yeniden koşular (m_c, K8, delist) kapı prosedürünün ana koşuyla birlikte tek atış parçasıdır. §7.3 teknik yeniden koşu bütün prosedürün bir kez tekrarıdır. V koşullarıyla ilişki U-11/U-12 | Üç kavramın sınırı |

**Kod gerekleri (5.02'ye):** ayristirma.py'ye isim başı carry satırı (`carry_coin`: fiyat + funding − maliyet) ve isim
başı artık (`artik_coin`) çıktıları; birer özdeşlik testiyle (toplamları satır toplamlarına eşit).

Sonraki adım: bu iki grubun kararları, CARRY ön-kaydına "Uygulama netleştirmeleri" eki olarak işlenir (önce arşiv).

## Grup 3 — kod sırasında çıkan netleştirmeler (30 Eylül; 5.02–5.04, kilitten önce, D görülmeden)

| Kod | Karar | Gerekçe |
|---|---|---|
| U-41 | Faktör sıralamasında (x_R, x_S) değeri tanımsız (R30 eksik, s^trend yok) isim o faktörün sıralamasına girmez; n < 2 ya da aday yoksa o haftanın faktörü tanımsız → K9/K11 hesaplanamaz → kaldı. Üst/alt küme ⌊0,30·n⌋ tamsayı aritmetiğiyle ((3n) div 10), en az 1. Faktör girdisi motorun o Pazartesi carry sıralamasında kullandığı R30 ve s^trend'dir (karar kaydına yazılır; tek kaynak) | U-24'ün tanımsız değer hali; B aleyhine |
| U-42 | V2 ve V5'in zorunlu koşuları: ana, mc2, mc3, delist50, delist90 ve (K8 hesaplanabiliyorsa) k8 | U-12'nin kod hali |
| U-43 | κ tanısı: κ^C_t = karar kaydındaki 'kappa', κ_etkin ayrı; oranlar T0 sonrası karar günleri üzerinden. §5.1 göreli değişim tanısı |κ_t/κ_{t−1} − 1| > 0,25 gün sayısı; round-1 bantlı kural κ_bant_t = κ_bant_{t−1} (göreli fark ≤ 0,25), aksi κ_t; izleme farkı |κ_bant − κ| (ortalama, en büyük, farklı gün) | §5.1 tanısının hesap biçimi |
| U-44 | Bağlama sıklıkları: karar kaydındaki bağlayan etiketlerinin (isim, brüt, kappa_brut, S1, S2, kappa, global, bant_kapandi, T4d) gün oranı; S4 bağlaması = nihai hedefte en az bir alt ismin −s4_sinir/s4_artis sınırına 1e-9 içinde olduğu gün oranı | §6.6 "bağlama sıklığı" |
| U-45 | Gerçekleşen kitap tavanları (K1-04): karar anındaki mevcut kitapta (w_mevcut) S1, S2 ve S4 aşımı (motorun asimlar fonksiyonu, bütün isimler serbest); aşım günü oranı (> 1e-12) ve en büyük aşım. Hedefe ulaşılamayan gün: o günün emir niyetlerinden biri aynı karar damgalı dolumlarla tam karşılanmadı | §6.6 tanımı |
| U-46 | Hedge yuvarlama (K1-18): BTC sanal carry miktarı sıfırdan farklı günlerde |q| (kapı NAV'ı) ve |q|·5.000/NAV_karar (demo NAV'ı) BTC lot adımının altında kalan gün oranı | Ağırlıktan hesap (§6.6) |
| U-47 | Funding dolgu raporu: ayrıştırma bacak funding'ini kayıt türüne göre döker (funding, funding_dolgu, ters_kayit; bacak ve isim başı sayı ve tutar); denetim dosyasına yalnız sayılar, hüküm dosyasına carry bacağının tutarları | §4.2 madde 6 |
| U-48 | Σ_t |A^C_t|'de t = gün (s^C gün boyu sabit) | §6.6 |
| U-49 | Long/short bacak satırları: hafta w'nin Pazartesi kararında q^C* > 0 olan isimler long, < 0 short; haftalık Σ carry_coin / (ω_C·L·NAV_{w başı}); BTC hedge ayrı. En kötü isim-hafta: alt isimlerin aynı ölçekteki en küçük haftalık katkısı | §6.6 |
| U-50 | Sıfır/sıfır tanısı: karar günü D'nin geçerlilik aralığında [D 01:00, D+1 01:00) iki sanal miktarı da 0 olan isim-günlerin artığı: toplam, mutlak toplam ve güncel kuralla (karar kaydındaki s^C) carry'ye düşen karşılık (s^C = 0 kuralına göre fark budur) | U-08/BR-24'ün hesap biçimi |
| U-51 | V6'da A'nın bant öncesi hedefi, B koşusunun o günkü karar öncesi durumu ve görünümü üzerinde karar_ver'in hedef öncesi adımları (boşluklar, maske, evren) aynı fonksiyonlarla tekrarlanarak hedef_agirlik (mimari A) ile hesaplanır; B tarafı karar kaydındaki bant öncesi trend hedefi w^T*'dir. İki tarafın işlem dışı (sabit) isimleri karşılaştırmadan çıkar | "Aynı gün" ve "P&L üretmeden" (V6) tanımının uygulanabilir hali |
| U-52 | K8 hesaplanamazsa (hiç tutulmuş alt isim < 30) K8 yeniden koşusu yapılmaz, K8 kaldı sayılır; V2/V5 k8 koşusunu istemez | §6.3 K8 notu |
| U-53 | Mühür kapsamı: ana koşunun trend satırları ve BÜTÜN koşuların olay günlükleri ile NAV yolları mühür klasörüne yazılır (NAV ve günlük B'nin toplam getirisini, dolayısıyla trend P&L'ini türetmeye yeter); yalnız hash'leri açıktır. V5'in bağımsız okuması betik içinde bu mühürlü dosyadan yapılır | §2 mührünün sızıntısız hali |
| U-54 | Sembol filtreleri: adım = max(LOT_SIZE, MARKET_LOT_SIZE stepSize), minNotional = MIN_NOTIONAL.notional; anlık görüntü 2026-09-30T01:09:20Z (`ciktilar/v8_sembol_filtreleri_20260930_01/`); kapı, D doğrulaması ve banka aynı tabloyu kullanır | MIMARI §5.1 tek anlık görüntü kuralı; motor dolumları piyasa emri gibidir |
| U-55 | Kilit kapsamı genişletildi: kapı kodu (v8/kapi) ve Codex incelemesi kilitten önce biter; KILIT.json kapı, motor, kalibrasyon, adaptör kod kimliklerini, parametre kimliklerini, sembol filtre tablosunu, D manifest ve veri kimliğini, deneme defterini ve `A4-carry-kapisi` satırını taşır. Motorun kalibrasyon sonrası çıktı eklemeleri (carry_coin, artik_coin, funding türü, R30/s^trend ve w^T* tanıları, carry_haric) P&L'i değiştirmez; eşdeğerlik `esdegerlik_502e.json` ile kanıtlanır | Ölçüt kodu D'deki ilk P&L'den önce donar |

## Grup 4 — Codex T15 kod incelemesinin kararları (30 Eylül; kilitten önce, D görülmeden)

Codex T15 (`v8/codex_cagrilari/20260930T15_kapi_kod_inceleme_yanit.md`): 6 CIDDI, 9 ORTA; hepsi işlendi. Aşağıdaki
satırlar önceki kararların yerini alır ya da onlara eklenir.

| Kod | Karar | Gerekçe |
|---|---|---|
| U-44 (düzeltme) | S4 BAĞLAMA = nihai hedefte bir alt ismin kısa sınıra (−s4_sinir/s4_artis) 1e-9 içinde teması; sınırın 1e-9'dan fazla ötesi S4 AŞIMI olarak ayrı raporlanır | T15-14: tek yönlü eşitsizlik aşımı da bağlama sayıyordu |
| U-45 (düzeltme) | Tavan raporu iki kitapta: gerçekleşen (w_mevcut) ve devreden ((q + devreden emir kalanı)·fiyat_ref/NAV; karar öncesi durum günlükten katlanır) | T15-14: §6.6 devreden kitabı da ister |
| U-49 (düzeltme) | Long/short: her saatin carry_eski payı saat başındaki, carry_yeni payı saat sonundaki sanal carry miktarının işaretine yazılır (ayrıştırma carry_eski/carry_yeni; trend_eski/yeni ile aynı kural); long + short + hedge = haftalık carry toplamı (testli) | T15-13: Pazartesi yeni hedef işareti eski miktarın payını yanlış bacağa yazıyordu |
| U-51 (düzeltme) | V6'da A referans durumu: B'nin karar öncesi durumu, pozisyonlar yerine B'nin SANAL TREND bacağı, devreden emir ve carry durumu yok, NAV korunacak biçimde nakit ayarlı. Carry pozisyonları A'nın tavanlarını tüketmez | T15-6: B'nin gerçek (carry içeren) pozisyonları A çözücüsünü etkiliyordu |
| U-56 | K8: en iyi 3 (büyükten, eşitlikte alfabetik), sonra KALAN isimlerden en kötü 3 (küçükten, eşitlikte alfabetik); bütün katkılar eşit olsa da 6 ayrı isim | T15-8 |
| U-57 | V2 her gün denetlenir: gün sonu NAV kaydı (dnav) olmayan gün inf sayılır (atlanmaz) | T15-9 |
| U-58 | Hata yolu mühürlüdür: kapı koşusunda her istisnanın ayrıntısı mühür klasörüne (HATA.txt) yazılır; dışarı yalnız sabit mesaj ve dosyanın sha256'sı çıkar (motor istisnaları NAV değeri taşıyabilir) | T15-2 |
| U-59 | Kilit ön koşulları: bitiş denetimi geçti, toplama TAMAM, duman geçti, motor eşdeğerliği geçti, V1 test raporu (güncel motor kimliği, başarısız 0, bütün test_v8_*.py dosyaları) — adı ve sha256'sı kilide girer; kapı koşusu yalnız bu raporu V1 sayar ve V1 geçmeden hiçbir D koşusu başlamaz. Doğrulama belge kümesini sabit listeyle birebir karşılaştırır (kilit kapsamını daraltamaz); kapı koşusu KILIT.json'un commit'li, değişmemiş ve uzak depoda olduğunu denetler. Ortam kimliğine pandas ve cryptography sürümleri girer | T15-3, T15-4, T15-5, T15-15 |
| U-60 | V5 kesilmeye karşı: diske yazılıp bağımsız okunan günlüğün kayıt sayısı ve son hash'i bellekteki günlükle aynı olmalı | T15-10 |
| U-61 | Sayısal: ρ̂ tanımında iki serinin kesin sabitliği denetlenir (ondalık sabit seride ρ̂ tanımsız → ρ_üst = +1); NW Bartlett ağırlıkları j = 1…min(ℓ, n−1) ile üretilir (payda ℓ + 1 korunur) | T15-7, T15-11 |

## Grup 5 — Codex T16 doğrulama turunun kararları (30 Eylül; kilitten önce, D görülmeden)

Codex T16 (`v8/codex_cagrilari/20260930T16_kapi_kod_dogrulama_yanit.md`): T15'in 7 bulgusu kapandı, 7'si kısmen; yeni
1 CIDDI + 2 ORTA. Kısmen kalanların bir kısmı yan dalın belge kopyasında Grup 4'ün henüz olmamasındandı (birleştirildi).
Kod düzeltmeleri yan dalda F6–F9.

| Kod | Karar | Gerekçe |
|---|---|---|
| U-58 (ek) | Hata yolunda mühürleme (HATA.txt) ya da bildirim de başarısız olursa özgün istisna bağlamı yine bastırılır; mesaj yalnız sabit metin ve (yazılabildiyse) hash taşır | T16 CIDDI |
| U-59 (ek) | Kilit kanıt zinciri: bitiş denetiminde birim dosyalarının kimliği tek ve dondurmayla aynı; motor eşdeğerliği kanıtı dondurulmuş motordan (eski) GÜNCEL motora (yeni) — motor değişirse eşdeğerlik yeniden koşulur. V1 test raporu motor dışında adaptör, kapı, kalibrasyon, banka, banka_kos, testler, kilit.py ve v8_calistir.py kimliklerini taşır; kilit hepsini güncel koda karşı denetler. Kapı koşusu kilidi önceden bildirilen commit'e bağlar (`--kilit_commit`): uzak referanslar tazelenir, commit bir uzak dalda olmalı, o commit'teki KILIT.json yereldekiyle bayt bayt aynı olmalı | T15-3/4/5 kısmen kapanmıştı |
| U-62 | V2 beklenen gün kümesi: [T0, D sonu) aralığının her takvim günü denetlenir; oranı hesaplanamayan (gün sonu NAV kaydı olmayan ya da hiç görünmeyen) gün inf sayılır | T15-9 kısmen |
| U-63 | V5 saatlik tüketim: ayrıştırmanın her saat fiilen kullandığı sanal carry miktarı (carry_q) ve s^C (artik_carry = Σ s^C_i·A_i), diske yazılıp bağımsız okunan karar kayıtlarından aynı "etkin ≤ T olan son karar" kuralıyla türetilen değerlerle aynı olmalı (miktar göreli 1e-12; artık, toplama sırası için 1e-9·max(1, Σ|s^C·A|)) | T15-10 kısmen |
| U-64 (U-49 eki) | Long/short bacakta saat başı miktarı 0 iken gelen eski pay (kapanmış pozisyonun geç funding dolgusu, ters kayıt) coinin son sıfır olmayan sanal carry miktarının işaretine yazılır (B5 epizot kuralıyla aynı) | T16 ORTA |

## Grup 6 — Codex T17 doğrulama turunun kararları (30 Eylül; kilitten önce, D görülmeden)

Codex T17 (`v8/codex_cagrilari/20260930T17_kapi_kod_dogrulama_yanit.md`): T15/T16'nın kısmen kalanlarından 5'i hâlâ
kısmen; yeni 2 CIDDI + 4 ORTA; U-49, U-59, U-59-ek, U-63, U-64 İTİRAZ. Hepsi yan dalda (`claude/v8-kapi-motor-502e`)
bulut oturumunda işlendi (madde 1–6; günlük `v8/BULUT_OTURUMU.md`). Aşağıdaki satırlar önceki kararlara eklenir ya da
yerlerini alır.

| Kod | Karar | Gerekçe |
|---|---|---|
| U-58 (ek 2) | Banka koşucusu da (`banka_kos/kosucu.py`; BANKA BK-2) aynı hata sınırı kuralına tabidir: birim yürütme + serileştirme + şifreleme + yazım, işçi başlatma, BK-6 birincil yeniden yürütmesi ve koşucunun kendisi ortak sınırdan geçer. İz alıcıya şifreli yazılır (`sonuc/hata/<etiket>.age`); dışarı yalnız sabit mesaj ve düz izin sha256'sı çıkar; özgün bağlam (işçinin uzak izi dahil) bastırılır; mühürleme de düşerse mesaj "hata dosyasi yazilamadi" der | T17 CIDDI (banka koşucusu) |
| U-59 (ek 2) | Kanıt zinciri: duman (`duman_kanit.json`; diskteki iki duman klasöründen, motor koşmadan), bitiş, toplama ve eşdeğerlik kanıtları ortak bir blok taşır (üreten betiğin, KOD_DONDURMA.json'un ve HAR sonuç dosyasının sha256'sı; dayandığı birimlerin dört kimliği; kaynak dosyaların hash'leri). Kilit: her blok bugünkü KOD_DONDURMA.json'la (dosya sha256'sı, dört kimlik, HAR) aynı; güncel HAR = dondurmadaki HAR; eşdeğerliğin güncel ucu (kalibrasyon kodu, motor, varsayılan parametre kimliği + HAR) kilit anındaki girdilerle aynı; kaynak zinciri tutar (TOPLAMA → bitis_sonuc; duman_kanit → duman_sonuc; eşdeğerlik girdileri → duman_kanit dosyaları). Biri değişirse ilgili kanıt yeniden üretilir (motor, kalibrasyon/banka kodu ya da Parametreler değişince eşdeğerlik yeniden koşulur) | T17 CIDDI (T15-3 kısmen) |
| U-59 (ek 3) | Uzak commit denetimi: kilit commit'i tam 40 haneli küçük harf hash (HEAD, dal adı, kısa hash reddedilir); `git fetch --prune origin`; yalnız origin'in `ls-remote` ile doğrulanmış dalları sayılır (başka remote'lar ve silinmiş dalların bayat referansları sayılmaz); commit bu dallardan birinin atası olmalı | T17 ORTA (T15-4 kısmen) |
| U-63 (ek) | V5: saatlik karşılaştırmadan önce şekil/kapsam/sonluluk denetimi (saat ızgarası boş değil, tam saatlik ve artan; karar saatleri artan ve ızgaranın içinde; her saatlik dizi ızgarayla aynı uzunlukta ve sonlu; karar kayıtlarındaki miktar ve s^C sonlu); NaN/inf hiçbir V5 karşılaştırmasında (günlük dahil) eşit sayılmaz. s^C birebirliği: ayrıştırma saat T'de icra artığıyla çarptığı s^C vektörünü isim/saat bazında çıkarır (`sc_q`; artığı sıfır isimler dahil); V5 bunu diskten türetilenle mutlak 1e-12 karşılaştırır ve artik_carry = Σ sc_q·A_i'yi (1e-9·max(1, Σ\|sc_q·A\|)) ayrıca denetler | T17 ORTA ×2 (T15-10 kısmen) |
| U-64 (düzeltme; U-49 eki) | Carry bacağı funding olaylarının long/short payı ÖZGÜN saatin bacak miktarı işaretinden gelir: gerçek kayıt q(d−), dolgu her dolgu saatinin q(h−), ters kayıt kapsadığı her dolgunun kendi saatinin yönü (eksi işaretle). Olay işlendiği saatte kalır (nakit özdeşliği ve haftalık toplam korunur); eski payın geri kalanı (fiyat, kapanan kısmın maliyeti) saat başındaki miktarın işaretine. T16'nın "son sıfır olmayan işaret" kuralının yerini alır | T17 ORTA (T15-13 kısmen) |

Açık (T18'e soru, karar değil): banka B5 epizot kuralı (`banka/pnl.epizot_pnl`; trend sanal bacağı ve A'nın net
pozisyonu) geç gelen eski payı saat başındaki ya da son kapanan epizota yazar; yön değişimini kapsayan dolgu aynı biçimde
yanlış epizota gidebilir. Banka kodu kalibrasyonun dondurulmuş kimliğindedir; değişiklik kalibrasyon eşdeğerliğini ve
kod kimliğini etkiler.

## Grup 7 — Codex T18 doğrulama turunun kararları (30 Eylül; kilitten önce, D ve banka görülmeden)

Codex T18 (`v8/codex_cagrilari/20260930T18_kapi_kod_dogrulama_yanit.md`): T17'nin 6 bulgusu ve T15/T16 kısmenleri
kapandı; yeni 3 CIDDI; U-59-ek-2 İTİRAZ; B5 açık sorusu. B5 için düzeltme kararı dizüstü oturumunda verildi (30 Eylül).
Hepsi yan dalda bulut oturumunda işlendi (2. tur madde 1–4; günlük `v8/BULUT_OTURUMU.md`).

| Kod | Karar | Gerekçe |
|---|---|---|
| U-59 (ek 4) | Bitiş–toplama girdi bağı: Düzey 2 klasörünün girdi özeti (iş listesi ve ek liste sha256'sı, birim dosyalarının sayısı ve birleşik özeti; `kanit.klasor_ozeti`, bitiş ve toplamanın ortak tanımı) bitiş kanıtında yazılır; toplama hesaplamadan ÖNCE kendi okuduğu klasörün özetini bununla karşılaştırır (farklıysa hiçbir şey hesaplanmaz), hesaptan SONRA özeti yeniden alır (değiştiyse TOPLAMA yazılmaz) ve tükettiği özeti TOPLAMA kanıtına yazar; kilit bunu bitiş kanıtıyla karşılaştırır. Düzey 1 girdilerinin özeti yalnız kaydedilir (DUZEY1_OZET.json'un üretici betiği depoda yok; bağ T19'a soru) | T18 CIDDI (U-59-ek-2 itirazı) |
| U-65 | Banka B7 null yolları ile ×2/×3 ve B10 çıkarma birimlerinin Sharpe'ı, birincil ölçümle aynı görülmüş gün maskesini uygular (BK-5, BANKA §3.5.6 aynı takvim). Kalibrasyon pencereleri hariç gün taşımaz; kalibrasyon sonucu bit düzeyinde aynıdır | T18 CIDDI |
| U-66 | B5 epizot atfı: funding (gerçek kayıt q(d−), dolgu her saatin q(h−)'si, ters kayıt kapsadığı dolguların kendi saati) ÖZGÜN saatin başındaki pozisyonun EPİZOTUNA yazılır (kimlik epizottan: kapanıp aynı yönde açılan pozisyon ayrı epizot); nakit kayıt saatinde kalır (NAV, B5 paydası, B8, B10 değişmez). Özgün saat pencereden önceyse: epizot pencere başına kadar kesintisiz sürüyorsa pencere başı epizotu, sürmüyorsa hiçbiri; yalnız pencere içinde kayda geçen parçalar yeniden atanır. Yeniden atama (şimdiki, özgün epizot, özgün saat) üçlüsüne göre netlenir. Düzey 2'de desen yalnız 4h→8h funding dönüşünde oluşur ve tam ters kaydedilir; netlemeyle kalibrasyon birim çıktıları değişmez (kanıt `ciktilar/v8_b5_desen_20260930_01/`); Düzey 2'nin yeniden koşulması kararı dizüstünde. BANKA §3.7 netleştirme 11 | T18 açık soru → düzeltme (dizüstü kararı) |
| U-67 | M = B'de B5 (ve ayrıştırma) yalnız birincil birimde ve R8'in bağımsız A biriminde; ızgara, Kelly, çıkarma, K-evren ve rapor birimleri B5'siz ölçülür (b5 alanları boş), ayrıştırma gerektirmez (BANKA §3.4 "aksi yazılmadıkça birincil ayar"; ILERLEME_BANKA BK-13). R8'in B Kelly birimleri için carry betası 6.08'de ayrıştırma ister | T18 CIDDI |

## Grup 8 — Codex T19 doğrulama turunun kararları (30 Eylül dizüstü; kilitten önce, D ve banka görülmeden)

Codex T19 (`v8/codex_cagrilari/20260930T19_kapi_banka_dogrulama_yanit.md`): T18-CIDDI-1/2/3 KAPANDI; U-65, U-67 KABUL;
yeni 2 CIDDI (Düzey 1 bağı; A'da gün içi dolumla B5 eşdeğerliği) ve R3 için 2 ORTA; U-59-ek-4, U-66, R3 İTİRAZ.

| Kod | Karar | Gerekçe |
|---|---|---|
| U-59 (ek 5) | Düzey 1 bağı zorunlu: toplama hesaplamadan önce `duzey1/` girdilerini önceden kaydedilmiş `DUZEY1_OZET.json`'a bağlar (kimlikler dondurmayla, iş listesi sha256'sı, birim kümesi = iş listesi = özet = klasördeki d1_* dosyaları, her birimin JSON dosya baytlarının sha256'sı = json_sha256, NPZ dosya baytlarının sha256'sı = npz_sha256 = zarfın govde.npz_sha256'sı; özet geçersiz birim bildirmez); hesaptan sonra yeniden doğrular; tükettiği özeti (özet dosyasının sha256'sı dahil) TOPLAMA'ya yazar; kilit bunu DUZEY1_OZET.json'dan türettiği değerle karşılaştırır. Özet sessizce yeniden üretilmez. Kod `topla.duzey1_bagi`, `kilit.duzey1_ozet_bagi` | T19 CIDDI (U-59-ek-4 itirazı) |
| U-66 (ek) | "Kalibrasyon birim çıktıları değişmez" iddiası A için genel değildir: devreden emirler 00:00 dışındaki her saatte kısmen dolar, dolgu ile ters kaydı arasında epizot değişebilir. Karar ön-kayda bağlandı (`ciktilar/v8_b5_a_esdegerlik_20260930_01/ONKAYIT.md`): Düzey 2'nin 140 A birincil birimi sunucuda güncel kodla yeniden hesaplanır, gövdeler (son_hash hariç) bayt bayt karşılaştırılır; 140/140 aynıysa Düzey 2 geçerli, bir fark bile varsa kalibrasyon kodu yeniden dondurulur ve Düzey 2 baştan koşulur (yamalı birim yok). B birincil (sanal bacak yalnız 01:00) ve B5 tüketmeyen birimler kapsam dışı | T19 CIDDI (U-66 itirazı) |
| R3 (düzeltme) | R3 evreni aylık seçim günündeki karar kaydının `a_t` kümesidir (`coinler` değil: evren dışı pozisyonlu/devreden isimleri içerir). Aradaki günlerde `a_t` dışına düşen isim satılmış sayılmaz: hedef 0 emri motorun icra kurallarıyla (katılım sınırı, kısmi dolum, bar yoksa devretme, delist beklemesi ve uzlaşma) gerçekleşir, o zamana kadar değerlenir ve funding öder/alır; işlem dışı isimde yeni emir yok; serbest nakit dağıtılmaz; aylık seçimde devreden emir yeni hedefle değiştirilir. BANKA §3.7 netleştirme 13 (b), (d), (e) | T19 ORTA ×2 (R3 itirazı) |
