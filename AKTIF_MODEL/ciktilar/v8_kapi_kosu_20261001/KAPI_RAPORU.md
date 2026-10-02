# Carry kapısı hükmü (5.07)

Tarih: 1 Ekim 2026. Koşu 19:07–20:27 UTC (dizüstü), kilit 71cf576. Denetim listesi hüküm açılmadan tamamlandı ve
itildi (b1bcd41; `DENETIM_LISTESI.md`). HUKUM.json sha256 `745c6a63…a393eed`, açılmadan önce commit edilmişti.

## Karar: **A** (carry modülü bankaya girmez; banka mimarisi yalnız trend)

Karar kuralı (CARRY §7): B için K1, K2, K5–K11'in hepsi geçmeli; biri kalırsa A. Ön-kayıtta varsayılan zaten A'dır
ve sentetik doğrulama (BX-08, #27) kapının pratikte kapalı olduğunu göstermişti. Gerçek sonuç bundan da açık: carry
bacağı maliyetler düşüldükten sonra **negatif** getiri üretti; kapanan yalnız eşdeğerlik ölçütleri değil, taşıma
kazancının kendisi.

## Ölçütler (143 hafta, 33 ay)

| Ölçüt | Ne sınar | Eşik | Gerçekleşen | Sonuç |
|---|---|---|---|---|
| K1 | Kredilenen net Sharpe başabaşı aşar | SR^K ≥ 0,138 | −0,106 (sanal −0,064); ρ_üst −0,165 | kaldı |
| K2 | Funding, maliyeti anlamlı aşar | NW t ≥ 3,0 ve bootstrap alt sınır > 0 | t −1,19 (L=4: −1,51); alt sınır −0,00028 | kaldı |
| K3/K4 | Fiyat ortalaması eşdeğerliği (yalnız rapor) | δ_P = %4/yıl | alt −0,00127, üst 0,00210 | bağlayıcı değil |
| K5 | Taşıma tutarlılığı | ≥ 25/33 ay pozitif | 12/33 (%36) | kaldı |
| K6 | Maliyet 2× dayanıklılığı | SR^K(2×) > 0 | −0,344 (sanal −0,301) | kaldı |
| K7 | Maliyet 3× dayanıklılığı | NW t(3×) ≥ 2,0 | −5,75 | kaldı |
| K8 | Tekil isim bağımlılığı (en iyi 3 + en kötü 3 çıkarılır) | SR^K > 0, ≥ 30 isim | −0,271 (sanal −0,226), 97 isim | kaldı |
| K9 | Beta eşdeğerliği | %90 GA ⊂ (−0,15; +0,15) | β_alt −0,020 [−0,042; 0,003], β_BTC −0,029 [−0,079; 0,022] | geçti |
| K10 | Trend bağımsızlığı | \|ρ̂\| ≤ 0,30 | −0,268 (sanal −0,273) | geçti |
| K11 | Fiyat faktörü yüklemesi eşdeğerliği | dört yüklemenin %90 GA'sı ⊂ (−δ_b; +δ_b) | x_R GA [−0,60; −0,19], x_S [0,04; 0,64]; x_A, x_B geniş | kaldı |

K8'de çıkarılan isimler: en iyi BCH, OP, DYDX; en kötü 1000SHIB, FIL, XRP.

Teknik oranlar (V_oran): V2 muhasebe kalıntısı ≤ 2,3e−15 (altı koşu); V3 143 aktif hafta, sıfır pay 0; V4a 0,019;
V4b 0,233; V6 0,042.

## Okuma

- **Sentetik beklentiyle fark:** BX-08'de engel K9 görünmüştü; gerçekte K9 geçti. Kapıyı kapatan ekonominin kendisi:
  K2'de funding net maliyetin altında kaldı (t < 0), K5'te ayların yalnız üçte biri pozitif.
- **Yorum sınırı:** bu, D döneminde ve bu yapı/maliyet varsayımıyla carry'nin kredilenebilir olmadığını söyler. Carry
  priminin piyasada var olmadığını kanıtlamaz.
- **Hüküm sonrası hata kuralı (§7.3):** bundan sonra bulunacak bir hata sonucu ancak A'da bırakır; B'ye dönüş yoktur.
  A zaten varsayılandır, dolayısıyla hata avının sonucu değiştirme yolu yoktur.

## Sonraki adımlar

- DONDURMA `mimari` = "A" (dondur.py hükümden okur).
- Trend mühür dosyası (`muhur/`) banka hükmü açılana kadar kapalı kalır.
- Tam yayın (betimsel seriler dahil, trend satırları hariç) proje sonundaki açık yayımla birlikte (#26).
