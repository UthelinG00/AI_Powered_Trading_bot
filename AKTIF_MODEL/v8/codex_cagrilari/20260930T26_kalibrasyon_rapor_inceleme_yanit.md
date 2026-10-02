## kararlar

Değerlendirme statiktir; proje kodu çalıştırılmadı, dosya yazılmadı. Aşağıdaki `RAPOR.md` ve `TOPLAMA.json`, verilen kalibrasyon klasöründekilerdir.

1. **DOGRU — σ_SR_bağ = 0,30; kaynak varsayım.** TOPLAMA aynı değeri ve zorunlu “doğrulanmadı” cümlesini taşıyor. Kaydın bildirilen şeması deneme başına Sharpe içermediğinden §3.3’teki kullanılabilirlik koşulu sağlanmıyor. (`TOPLAMA.json:5`; `sigma_sr.py:37`; `BANKA_ONKAYIT_TASLAK.md:370`)

2. **DOGRU — B5 rapora iner.** Ham eşik `"inf"`, uygulanan `e_b5=null`; %60 üst sınırını aşıyor. Rapordaki gerekçe, eşik algoritmasıyla uyumlu. (`TOPLAMA.json/duzey1/rapor/karar/e_b5_ham`; `duzey1_esik.py:43`; ön-kayıt:663)

3. **DOGRU — B10 rapora iner.** Ham eşik 0,80 > 0,40; uygulanan `e_b10=null`. (`TOPLAMA.json/duzey1/rapor/karar/e_b10_ham`; ön-kayıt:665)

4. **DOGRU — k_B6 = 2.** TOPLAMA ve uygulanan kurallar aynı. Kod, bütün ayarlarda üç pozitif dilim koşulunun geçme oranı ≥%90 olmadığında 2 seçiyor. Ham yol sonuçlarını yeniden hesaplamadım. (`TOPLAMA.json/duzey1/rapor/karar/k_b6`; `duzey1_esik.py:58`; ön-kayıt:667)

5. **DOGRU — B2 bağlayıcı.** Karar girdisi `0.57410546875 ≥ 0.25`; rapordaki 0,574 doğru yuvarlama. Bu, **d=0,50’deki B2 gücüdür**, seçilen d=0,90’ın gücü değildir. (`TOPLAMA.json:28`; `duzey1_karar.py:39`; ön-kayıt:383)

6. **DOGRU — d*=0,90; tek ayar uygulanmaz.** Arama sırası 0,50 → 0,75 → 0,90; en kötü yanlış kabul oranları sırasıyla %11,1, %5,95, %2,1. İlk sağlayanda durulması doğru; 0,95’i denemek veya B3/B4’ü 0,40’a çıkarmak gerekmiyor. (`TOPLAMA.json:30`; `duzey1_karar.py:44`; ön-kayıt:389)

7. **DOGRU — Düzey 2-a taraması geçti.** Küme B2, B3, B4, B6, B8, B11; B5/B10 raporda, B7/B9 dışarıda. A ve B ayrı ayrı 0/100; Wilson üst uç `0.0369934982`. Kural, Wilson üst ucuna değil **p̂≤%5** koşuluna bakıyor; rapor bunu doğru anlatıyor. (`TOPLAMA.json/duzey2/duzey2a`; `toplama.py:45`; ön-kayıt:730)

8. **DOGRU — B7 q95 sabit.** Sonuçlardan seçilmemiş; 3. revizyonun kuralı. B9’un Düzey 2 dışında bırakılması da doğru; Düzey 1 ortalaması 0,942625 → 0,943. (`toplama.py:37`; `TOPLAMA.json/duzey1/rapor/b9_gecme_ref`; ön-kayıt:726)

9. **DOGRU — Güç tablolarının sayıları TOPLAMA ile tutarlı.** Düzey 1 ortalamaları `0,0081953; 0,0230430; 0,0436406; 0,1026602; 0,1678086; 0,2573438`; rapordaki yuvarlamalar doğru. Seyreltme tablosu ve 2-b’nin oranları, Wilson aralıkları, sıra yüzdelikleri ve ortak payları da örtüşüyor. **Bu sayıların yorumunda aşağıdaki eksikler var.** (`TOPLAMA.json:1298`; `TOPLAMA.json/duzey2/duzey2b`; `RAPOR.md:54`)

10. **DOGRU — TOPLAMA kanıt bloğunun biçimi kilitle uyumlu.** KOD_DONDURMA, HAR, dört kimlik ve kaynak alanları mevcut; Düzey 2 özeti bitiş kanıtıyla birebir aynı. Dosya SHA-256 denetiminde TOPLAMA’nın rapor başındaki hash’i; bitiş, KOD_DONDURMA, HAR, DUZEY1_OZET ve defter hash’leri eşleşti. Düzey 1 birleşik hash’ini birimlerden yeniden üretmedim. (`TOPLAMA.json:1482`; `bitis_sonuc.json:20`; `kilit.py:185`)

11. **BELIRSIZ — B5 A sonucunun kilidin bütün denetimlerinden kesin geçmesi.** Kayıt içindeki koşullar uygun: kök `gecti=true`, `denetim.gecti=true`, 140/140, donmuş kimlikler ve Düzey 2 kaynak özeti eşleşiyor. Ancak kilit ayrıca kayıtlı `guncel` kod/motor/parametre/HAR kimliklerini **kilit anında hesaplanan** kimliklerle karşılaştırıyor; bu çalıştırılmadı. Dolayısıyla kayıt biçimi ve kabul alanları uygun, koşulsuz çalışma zamanı PASS iddiası verilemez. (`b5_a_esdegerlik.json:2`, `:188`; `kilit.py:237`)

## n_sorusu

Yalnız izin verilen iki sütunda **28 satırın tamamı `included_primary_dsr=True`**. İlk 27 satırın `trial_count` toplamı **159**, son satırın değeri de **159**: düz toplam **318=159+159**. Dolayısıyla rapordaki “birincil DSR’a dahil olmayan satırlar olabilir” açıklaması yanlış; bayrakla süzmek farkı çözmez. **159 ayrıntı satırlarının toplamı olarak doğru görünür**, fakat son satırın gerçekten özet satırı olduğu yalnız bu iki sütunla anlamsal olarak kesinleştirilemez. V8 defterinde 20 satır var: `17×1+144+5+2=168`; dolayısıyla §3.3’ün açıkça sabitlediği REV1=159 ile **N=327 tutarlı**. 318’i doğrudan kullanıp N’yi 486’ya yükseltmek gerekçelendirilmiş değil.

## bulgular

- **[ORTA] REV1 sayım farkının açıklaması yanlış — `RAPOR.md:146` —** Bütün dahil bayrakları True; fark dışlanan satırlardan gelmiyor. **Düzeltme:** İlk 27 satır=159, son satır=159 ayrımını yaz; son satırın özet niteliğini belgeleyerek açık noktayı kapat.

- **[ORTA] Tam banka gücüyle karışabilecek anlatım — `RAPOR.md:127`; `duzey1_esik.py:88`; `toplama.py:79` —** “Yaklaşık altıda bir geçer” değeri **B7’siz Düzey 1** hesabı. 2-b’deki “taban+B7” ise mevcut kararlarda yalnız **B2, B4, B6, B8, B11+B7**; B3 ve B9’u içermiyor. **Düzeltme:** Her güç tablosunun ölçüt kümesini açıkça yaz; tam banka kabul gücünün ölçülmediğini ve “KABUL güçlü işaret” yorumunun sentetik model sınırını belirt.

- **[ORTA] Ortak eşleşme payından yanlış yakınlık çıkarımı — `RAPOR.md:139`; ön-kayıt:476 —** ≈0,985, null yolun özgün yola benzerliği değildir; blok atamalarının ortak permütasyonu izleme payıdır. Kesitsel eş hareketin korunmasını ölçer. **Düzeltme:** “Null yolları gerçek yola çok yakındır” çıkarımını kaldır; düşük B7 gücünü doğrudan 2-b sonuçlarıyla anlat.

- **[DUSUK] 2-b deney tanımı eksik — `RAPOR.md:93`; ön-kayıt:745 —** Tablo yalnız ayar numarası veriyor; ayar 0 trendsiz kontrol olmasına rağmen başlık tümünü trendli gösteriyor. Yalnız A ve yol başına 50 null kullanıldığı da görünmüyor. **Düzeltme:** κ/HL eşlemesini, kontrol satırını ve örneklem düzenini tabloya ekle.

## genel_hukum

Kalibrasyonun mekanik eşik kararları kilide geçişi destekliyor; sayısal bir `KILIT_BEKLER` nedeni bulmadım, ancak rapordaki sayım ve güç yorumları kilitten önce düzeltilmeli. Bu statik inceleme, güncel kimlikler dahil `kilit.onkosullar` için çalıştırılmış PASS veya ekonomik kabul değildir.