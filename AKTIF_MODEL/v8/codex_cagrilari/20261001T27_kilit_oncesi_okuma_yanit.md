## celiskiler

1. **[CIDDI] Kapının ayrı sentetik doğrulaması kilit paketinde yok** — CARRY:680–689 ↔ kilit.py:47–72,171–252 — CARRY §8.5, 10.000 tekrarlı ayrı fikstürün Adım 3’te koşulmasını ve çıktısının kilide girmesini istiyor. Kilit listesi ve ön koşullarında bu sonuç bulunmuyor; banka kalibrasyonu bunun karşılığı değil. — **Düzeltme:** Fikstürün üreteç/ölçüt kapsamını tamamlayıp sonucunu belgelemek, kullanıcıya sunmak ve sonuç kimliğini kilit ön koşuluna bağlamak gerekir. İncelediğim paket çalıştırılmış olduğunu kanıtlamıyor.

2. **[CIDDI] Son defter ile kalibrasyon N’si bağlanmıyor** — BANKA:813–814,1049 ↔ CARRY:172–173; kilit.py:204–218,272–278 — TOPLAMA’nın N’si 327; açık defterde `A4-carry-kapisi` henüz yok. Yalnız bu satır eklenirse N=328 olur. BANKA bu durumda toplamayı yenilemeyi emrediyor; `kilit.py` ise TOPLAMA’daki N’yi veya `kaynak.defter_sha256` değerini güncel defterle karşılaştırmıyor. Eski N’li kalibrasyonla yeni defter birlikte kilitlenebilir. — **Düzeltme:** Son defterden N hesaplanmalı, toplama yenilenmeli; N ve defter hash eşleşmesi zorunlu ön koşul olmalı. BANKA’daki sonuç özeti ve rapor da yeni toplamaya bağlanmalı.

3. **[CIDDI] İzin verilen teknik yeniden koşunun kilit yolu yok** — CARRY:545–549; MIMARI:1004–1005 ↔ kilit.py:296–301,378–392 — Belgeler hata düzeltmesi ve deftere yeni satırla bir teknik yeniden koşuya izin veriyor. Kilit doğrulaması değişen kodu, defteri ve test kanıtını reddediyor; üretim de mevcut kilidi yeniden üretmiyor. Belgelenmiş istisna mevcut doğrulama yolundan geçemiyor. — **Düzeltme:** İlk kilidi koruyan, yalnız yetkili teknik düzeltmeyi ve sayaç artışını zincirleyen bir ek kayıt/doğrulama protokolü kilitten önce tanımlanmalı; ekonomik kurallar değişmez kalmalı.

4. **[CIDDI] HAR kullanılabilirliği: 30 hafta ile 30 gözlem farklı** — CARRY:161–165,775 ↔ HAR/ONKAYIT.md:36–43,65–72 — CARRY en az **30 tamamlanmış hafta**, HAR ön-kaydı havuzlu OLS için **30 gözlem** ve ayrıca **8 artık haftası** istiyor. Bunlar D içinde farklı günlerde HAR’a geçiş üretir; §15 bu farkı kapatmıyor. — **Düzeltme:** CARRY, uygulanmış HAR ön-kaydının eğitim gözlemi, tam-rank ve artık haftası koşullarına birebir bağlanmalı; yeni bir tahminci seçimi yapılmamalı.

5. **[ORTA] #23 geri çekilmiş gerekçeyi yeniden kullanıyor** — ACIK_SORU_YANITLARI:69; CARRY:511–513 ↔ BANKA:1186–1197 — “Olay sayısı 30’dan az olabilir, dolayısıyla senaryo bağlayıcı olamaz” gerekçesi BANKA’da açıkça geri çekilmiş. Önceden konulan ekonomik stres sınırı, az gözlemle kural seçmek değildir. **Rapor kararı** tutarlı olabilir; gerekçesi tutarlı değil. — **Düzeltme:** Rapor statüsü korunacaksa gerekçe risk tercihi ve önceden belirlenmiş kapsam olarak yazılmalı; n<30 zorunluluğu iddiası çıkarılmalı.

6. **[ORTA] BANKA T4-d, sabit isim istisnasını taşımıyor** — BANKA:238–246 ↔ MIMARI:410–420 — BANKA tavan ve toplam risk koşullarını istisnasız birlikte arıyor; MIMARI işlem dışı isimlerden kalan ihlali teknik hata saymıyor ve bankanın da aynı istisnayı uygulamasını istiyor. — **Düzeltme:** BANKA T4-d’ye K8 istisnası ve raporlanacak ihlal alanları açıkça eklenmeli.

7. **[DUSUK] Ana ölçüt tablosunun tür sütunu sonuçlarla güncellenmemiş** — BANKA:409,414 ↔ BANKA:1053–1057; TOPLAMA.json:1084–1086 — B5/B10 tabloda hâlâ “B”; kesinleşmiş sonuçta ikisi de rapor. §3.7 üzerinden doğru karar bulunabiliyor, fakat hüküm tablosu tek başına yanlış okunabiliyor. — **Düzeltme:** Tür sütunları R yapılmalı; B2 bağlayıcı/d*=0,90 ve B6 k=2 aynı tabloda kesinleştirilmeli.

8. **[ORTA] L=1’in elenmesi, önerinin mutlaka 1’in altına ineceğini göstermez** — BANKA:1094 ↔ BANKA:1068–1070,1083–1093 — Her L ayrı, tavanlı koşu olduğundan MDD’nin L ile monotonluğu garanti değil. L=1 uygun değilken daha yüksek bir L uygun olabilir; uygun küme tamamen boş da olabilir. — **Düzeltme:** “Önerilen kaldıraç 1’in altına iner” yerine, önerinin yalnız hesaplanan 𝓛* ve CAGR sıralamasından çıktığı yazılmalı.

## belirsizlikler

1. **[CIDDI] Hüküm sonrası düzeltmelerin sayısal sınırı açık değil** — BANKA:258–270 ↔ BANKA:216,1243–1245 — Hüküm öncesinde bir teknik yeniden koşu sınırı açık; hüküm sonrasında “düzeltilmiş koşu yapılır” deniyor. Daha önce teknik hak kullanılmışsa veya ikinci hata bulunursa yeniden koşunun mümkün olup olmadığı belirsiz. — **Düzeltme:** Hüküm öncesi/sonrası toplam hak sayısı, izin verilen düzeltme kapsamı ve hakkın tükenmesindeki sonuç tek karar tablosuyla sabitlenmeli.

2. **[ORTA] Tanımsız banka ölçütünün statüsü belgede eksik** — BANKA:223,400–415 ↔ CARRY:522 — BANKA T3, NAV’ın NaN/sonsuz olmasını kapsıyor; sonlu NAV’dan çıkan tanımsız Sharpe/DSR, sıfır varyans veya tanımsız null istatistiği için RET–TEKNİK GEÇERSİZ ayrımı yazılmamış. CARRY’de bunun karşılığı açık. — **Düzeltme:** Bağlayıcı ölçütün hesaplanamaması ile hesaplama/altyapı hatası ayrılmalı; B7’de geçerli null sayısı ve rapor satırlarının tanımsızlık davranışı belirtilmeli.

3. **[ORTA] Kapı sentetik fikstürünün bazı karar girdileri tanımsız** — CARRY:682–689 ↔ CARRY:406–409 — Üreteç haftalık fiyat, funding-eksi-maliyet ve trend serileri tarif ediyor; K5’in 33 aylık serisi, K6/K7’nin ayrı maliyet koşulları ve K8’in isim çıkarma karşılığı tanımlanmıyor. Yalnız V4/V5/V6 açıkça dışlanmış. Bu haliyle “P(B)” tam kapının mı, bir ölçüt alt kümesinin mi oranı olacak belli değil. — **Düzeltme:** Koşudan önce ölçüt–sentetik girdi eşlemesi tamamlanmalı; temsil edilmeyen ölçütler varsa sonuç tam kapı geçiş olasılığı diye adlandırılmamalı.

## kilit_adimlari

- Önce yukarıdaki **CIDDI** maddeler kapatılmalı; son kilit adayında uygulama metinleri ve ölçüt tabloları eşitlenmeli.
- `A4-carry-kapisi`, varyant=1, kapsam T0→2026-07-01 olarak eklenmeli. Diğer yeni satırlarla birlikte nihai N yeniden hesaplanmalı; yalnız bu ekleme N’yi **327→328** yapar. BANKA §3.7 gereği sentetik yollar değil, **toplama adımı** yenilenmeli.
- **Mevcut N=327 çıktısının aktarımı doğru:** BANKA:1049–1057; kalibrasyon RAPOR:27–52,90–91; TOPLAMA:21–46,1078–1086,1360–1374 birbiriyle gösterilen yuvarlama hassasiyetinde uyuşuyor. σ=0,30 varsayım; B2 bağlayıcı; d*=0,90; B5/B10 rapor; k_B6=2; B3/B4=0,30; Düzey 2-a A ve B’de 0/100.
- **#24’ün kararı metinle uyumlu:** δ_b=0,30, β toleransı=0,15, δ_P=%4/yıl; sonuncusu yalnız rapor. Bunlar CARRY:454–482,599–605 ile örtüşüyor. #23 için karar ile hatalı gerekçe ayrılmalı.
- Kapının ayrı sentetik doğrulaması tamamlanıp kilide alınmalı. Banka kalibrasyonunun `TAMAM` olması bu yükümlülüğü karşılamıyor.
- Nihai kodla V1 raporu; duman, bitiş, Düzey 1/2 kaynak bağları, güncel eşdeğerlik ve B5 A 140/140 kanıtları doğrulanmalı. Dosyalardaki başarı alanlarını okudum; bu oturumda doğrulamaları çalıştırmadım.
- Belge, kod, parametre/HAR, ortam, filtre, veri kimlikleri ve defterin son hali birlikte hash’lenmeli. `KILIT.json` üretildikten sonra commit/push yapılmalı; kapı ilk P&L’den önce tam 40 haneli uzak commit üzerinden kilidi doğrulamalı.

## genel_hukum

**Mevcut haliyle KİLİT için hazır değil.** Başlıca engeller kapı sentetik doğrulamasının eksik kapsamı, son defter–N bağının denetlenmemesi, teknik yeniden koşunun kilitle çatışması ve HAR kullanılabilirlik kuralındaki farktır. Bu hüküm yalnız statik okumaya dayanır; kod çalıştırmadım, dosya yazmadım ve yasaklanan kaynaklara erişmedim.