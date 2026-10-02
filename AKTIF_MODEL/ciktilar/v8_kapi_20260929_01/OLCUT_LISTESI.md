# Carry kapısı ölçüt listesi (koda aktarım için mekanik çıkarım)

Kaynak: `AKTIF_MODEL/ciktilar/v8_asama4_20260927_01/CARRY_KAPISI_ONKAYIT_TASLAK.md` (2. tur, 2026-09-27, durum "TASLAK, koşulmadı").
Yardımcı kaynaklar: `AKTIF_MODEL/v8/motor/ayristirma.py` (yalnız dönen yapı), `MIMARI.md` §4.4–§4.7 ve §6.1–§6.2 (yalnız atıf ve satır tanımı için).
Bu liste mekanik bir çıkarımdır: yorum, karar ve belirsizlik çözümü yoktur; belirsizlikler "Belirsizlikler" bölümünde (U-xx) işaretlidir. Formüller belgedeki biçimiyle alınmıştır; "§" belgenin kendi bölümüdür (aksi belirtilmedikçe CARRY_KAPISI).

**Özet**
- Geçerlilik koşulu: **7 satır** (V1, V2, V3, V4a, V4b, V5, V6; belge "V1–V6" der, V4 ikiye bölünmüştür; V1 içinde 11 alt madde vardır). Biri sağlanmazsa sonuç A.
- Karar ölçütü: **11** (K1–K11); bağlayıcı **9** (K1, K2, K5–K11), yalnız rapor **2** (K3, K4). Çift seri kuralı K1, K6, K8, K9, K10 için geçerlidir.
- Betimsel rapor: §6.6'da **28 kalem** (BR-01…BR-28; belgedeki virgül ve noktalı virgülle ayrılmış kalemler tek tek sayıldı) + §6.6 dışında "raporlanır" denen **8 ek kalem** (BX-01…BX-08). İstatistik tanımı: 12 satır (S1…S12). Belirsizlik: 40 madde (U-01…U-40).

---

## Tablo 1. Geçerlilik koşulları (§6.1)

Genel kural (§6.1 başlık): "biri sağlanmazsa sonuç A". §6.1 son cümle: "V4a veya V4b aşılırsa sanal bacak gerçek pozisyonu temsil etmiyor sayılır ve sonuç A olur." Karar kuralında (§7.1) B için "V1–V6 sağlanır" şarttır.

| Kimlik | Ad | Tam tanım / formül (belgeye sadık) | Girdi | Eşik | Sağlanmazsa | Ref |
|---|---|---|---|---|---|---|
| V1 | MIMARI parite ve bakış-ileri testleri, fikstürler, carry birimi denetimi | "MIMARI §5.6 parite ve bakış-ileri testleri Adım 0'da geçmiş, kritik hata 0." Fikstürler "en az şunları" içerir (alt maddeler V1-a…V1-k aşağıda). "Carry birimi denetimi (KC-09 carry tarafı): her Pazartesi carry birim kitabının ex-ante vol'ü ölçekleme sonrası ve isim tavanları öncesi τ = %15'e eşit (1e-9), isim tavanları sonrası ≤ τ; ω_C·L uygulanmış carry katkısının ex-ante vol'ü ≤ ω_C·L·τ." Bu denetim "carry birimi nesnesine aittir; trend birimi, kaldıraçlı net hedef ve gerçekleşen defter için T4 tanımları BANKA/MIMARI'dedir." | Adım 0 test sonuçları; sentetik fikstürler; her Pazartesi carry birim kitabı ve Σ̂ (ex-ante vol V(w^C), "V §3.5'teki gibi", MIMARI §4.4 adım 1) | kritik hata = 0; \|vol_ölçek_sonrası − τ\| ≤ 1e-9 (τ = 0,15); vol_isim_tavanı_sonrası ≤ τ; vol(ω_C·L·w^C) ≤ ω_C·L·τ | A | §6.1 V1; §3.3; §5.1; §4.2 |
| V2 | Uzlaşma özdeşliği | "Her gün: ΔNAV = trend satırları + (F + P − C) + netleme kazancı + icra artığı. Özdeşlik 1e-8 NAV içinde tutmalıdır." "§5.5 uzlaşma özdeşliği her gün tutuyor." | `ayristirma.py`: `gunluk['dnav']` ile günlük satır toplamı; `AyristirmaSonucu.ozdeslik_max_hata` | her gün fark ≤ 1e-8 NAV (birim/taban için U-16) | A | §6.1 V2; §5.5 |
| V3 | Carry kitabı aktifliği | "Carry kitabının sıfır olduğu (n_C < 10) hafta payı ≤ %25; aktif hafta ≥ 108/143." | haftalık n_C (aday sayısı; MIMARI §4.1) ya da haftalık carry kitabı sıfır göstergesi | sıfır hafta payı ≤ %25; aktif hafta ≥ 108 (143 üzerinden) | A | §6.1 V3; §4.1 |
| V4a | Mutlak artık toplamı | "Σ_w \|a^C_w\| ≤ 0,10 · Σ_w \|r^N_w\|. Mutlak değerlerin toplamıdır; zıt işaretli artıklar birbirini silmez (KC-05)." a^C_w = A^C_w/(ω_C·L·NAV_{w başı}); A^C_w = Σ_{t∈w} A^C_t | `artik_carry` (haftalık toplam, ölçekli); r^N_w (Tablo 2b) | Σ\|a^C_w\| ≤ 0,10·Σ\|r^N_w\| (eşitlik geçer); 143 hafta | A | §6.1 V4a; §5.6 |
| V4b | Haftalık yol sapması | "her hafta ayrı ayrı \|a^C_w\| ≤ 1,0 · sd(r^N_w). Tek bir haftadaki büyük sapma (ör. maske çıkışında geç kapanan pozisyon) sanal defterin o haftayı temsil etmediğini gösterir." | `artik_carry` haftalık; r^N_w serisi ve sd'si | her w için \|a^C_w\| ≤ 1,0·sd(r^N); 143 hafta | A | §6.1 V4b |
| V5 | Tek defter | "kapının kullandığı q^C,v, κ^C_t ve s^C serileri motorun MIMARI §4.7 çıktısıyla her gün birebir aynı (mutlak fark ≤ 1e-12). Kapı betiği bu serileri yeniden hesaplamaz; denetim, aynı serinin motor günlüğünden bağımsız okunmasıyla yapılır." | motor günlüğü karar kayıtları (`hedef.carry.sanal_carry`, `sc`, κ^C_t) ile kapının kullandığı seriler | her gün mutlak fark ≤ 1e-12 (birim için U-28) | A | §6.1 V5; §5.1 |
| V6 | Tavan etkileşimi | "B'nin trend bacağının net hedefi (w^T*) A'nın aynı gündeki trend hedefinden farklı olan gün oranı ≤ %10. A'nın hedefi yalnız `hedef_agirlik` ile, P&L üretmeden hesaplanır. Aşılırsa 'B = A + carry' varsayımı ve §8.4 seyreltme formülü geçersizdir." | B çözücüsünün günlük w^T*; A için `hedef_agirlik` çıktısı | farklı gün oranı ≤ %10 (paydanın gün sayısı ve "farklı" toleransı için U-13) | A | §6.1 V6; §8.4 |

### V1 alt maddeleri ("Fikstürler en az şunları içerir", §6.1 V1)
- V1-a: MIMARI §5.6 parite testleri geçmiş, kritik hata 0 (Adım 0).
- V1-b: MIMARI §5.6 bakış-ileri testleri geçmiş (Adım 0).
- V1-c: 1h→8h ve 4h→8h funding aralık dönüşü fikstürü (K1-01).
- V1-d: delist ve uzun funding boşluğu fikstürü (K1-02).
- V1-e: S1/S2 bağlarken carry bloğunun tek katsayıyla küçülmesi fikstürü (§3.3).
- V1-f: günlük κ^C'nin sanal carry miktarına aynı gün yansıması (κ 1 → 0,8 örneği, KC-03).
- V1-g: iki sanal bacak sıfırken taşınan gerçek pozisyonun artığının MIMARI §4.7 kuralıyla dağılması (KC-03).
- V1-h: zıt işaretli haftalık artıklar (+100/−100, KC-05); "V4a ve V4b'nin reddettiği gösterilir".
- V1-i: her Pazartesi carry birim kitabının ex-ante vol'ü, ölçekleme sonrası ve isim tavanları öncesi τ = %15'e eşit (1e-9).
- V1-j: isim tavanları sonrası ex-ante vol ≤ τ.
- V1-k: ω_C·L uygulanmış carry katkısının ex-ante vol'ü ≤ ω_C·L·τ.

---

## Tablo 2. İstatistik tanımları (§6.2)

Örneklem (hepsi için, aksi belirtilmedikçe): D = [2023-07-01, 2026-07-01) UTC; T0 = 2023-10-01 00:00 UTC; hafta = Pazartesi 00:00 → sonraki Pazartesi 00:00; 2023-10-02 → 2026-06-29 arası **n_w = 143** tam hafta ("Kalan iki gün toplam P&L'e girer, haftalık istatistiğe girmez"); ay = UTC takvim ayı 2023-10 → 2026-06, **n_m = 33**; çeyrek 11 adet ("n < 30 olduğu için yalnız betimsel") (§4.1).

| Kimlik | Tanım | Formül / kural | Pencere / örneklem | Parametreler | Ref |
|---|---|---|---|---|---|
| S1 | Sharpe (SR) | SR = ortalama(r_w) / std(r_w) · √52 | haftalık, n_w = 143 | yıllıklandırma √52; std tanımı (ddof) belirtilmemiş (U-04) | §6.2 |
| S2 | Kredilenen Sharpe (SR^K; "fiyat kazancı kredilenmez") | SR^K(r) = [ ortalama(r^F − r^C) + min(ortalama(r^P), 0) + ortalama(a) ] / std(r) · √52; r ∈ {r^N, r^{N,g}}; a = 0 sanal seride, a = a^C gerçekleşen seride. "Fiyat bileşeninin ortalaması pozitifse sıfır sayılır, negatifse düşülür. Payda tam serinin oynaklığıdır." | haftalık, n_w = 143 | m_c çarpanı ayrı koşudan gelir (K6 için m_c = 2) | §6.2; §5.6 |
| S3 | Newey–West t ve standart hata | Newey–West, Bartlett çekirdeği. Gecikme ℓ ∈ {4, 12} hafta, ikisi de hesaplanır. ℓ = 4: ⌊4·(143/100)^{2/9}⌋. ℓ = 12: 84 gün (~3 ay), "funding sırasının 30–90 günlük kalıcılığını kapsar". **Seçim kuralı: "her ölçütte B aleyhine olan kullanılır."** K2, K7 (anlamlılık isteyen) ve K9, K11 (eşdeğerlik isteyen; betimsel K3/K4) için **büyük** standart hata. | haftalık serilerde (K2, K7, K9, K11, K3/K4) | ℓ = 4 ve ℓ = 12; Bartlett ağırlık normalizasyonu ve küçük örneklem düzeltmesi belirtilmemiş (U-02) | §6.2 |
| S4 | Eşdeğerlik testi (TOST) | Parametre θ, tolerans δ > 0. H0: \|θ\| ≥ δ; H1: \|θ\| < δ. İki tek taraflı %5 testi; eşdeğer: %90 güven aralığı (θ̂ ± 1,645·SE_NW) tamamen (−δ, +δ) içinde. Birden fazla parametrede kesişim-birleşim: hepsi ayrı ayrı eşdeğer olmalı. K3/K4 için tek taraflı %95 alt/üst sınır: θ̂ ∓ 1,645·SE_NW; θ = μ_P, δ_P = %4/yıl birim | K9: β_BTC, β_alt; K11: dört standart yükleme; K3/K4: μ_P | z = 1,645; δ = 0,15 (K9), 0,30 (K11), %4/yıl birim (K3/K4); "yıl birim" için ×52 belgede açık değil (U-38) | §6.2; §6.3 |
| S5 | ρ̂ ve korelasyonun üst güven sınırı | ρ̂ = ρ(r^N, r^trend,net), haftalık. ρ_üst = tanh( atanh(ρ̂) + 1,2816 / √(n_w − 3) ); n_w = 143 → ek terim ≈ 0,108. Fisher dönüşümü, tek taraflı %90. K1'de iki seri için ρ_üst ayrı hesaplanır. | haftalık, n_w = 143 | z = 1,2816; n_w − 3 | §6.2; §6.3 |
| S6 | K1 eşiği K1\*(ρ_üst) | K1\* = 0,85 · g(ρ_K1, 1/3); g(ρ, k) = (√(1 + k² + 2ρk) − 1)/k; ρ_K1 = min(0,30; max(0; ρ_üst)). Aralık: 0,138 (ρ_üst ≤ 0) … 0,370 (ρ_üst ≥ 0,30). "Yalnız ρ_üst gözlemden gelir; SR_T,ref = 0,85 ve k = 1/3 sabittir." Örnek değerler: ρ_üst 0,11 → 0,224; 0,21 → 0,299. | K1'e girer | SR_T,ref = 0,85; k = σ_C/σ_T = 1/3; kırpma [0; 0,30] | §6.3; §8.4 |
| S7 | Blok bootstrap | Dairesel blok bootstrap, blok 4 ve 12 hafta, 10.000 çekiş, tohum **20260928**, yüzdelik güven sınırı. K2'de "iki alt sınırın küçüğü kullanılır." | haftalık, n_w = 143 | blok {4, 12}; 10.000; tohum 20260928; bootstrap edilen istatistik belirtilmemiş (U-03) | §6.2 |
| S8 | Beta (K9) | Haftalık OLS: r^N_w = a + β·x_w + e. x: BTC haftalık basit getirisi; ayrıca eşit ağırlıklı alt sepeti (o haftanın carry aday evreni) haftalık getirisi. "Ayrı regresyonlar." Beta ve MDD "bu carry birim ölçeğinde okunur" (§5.3). | haftalık, n_w = 143; r^N ve r^{N,g} | %90 aralık, NW büyük SE (S3, S4) | §6.2; §5.3 |
| S9 | Fiyat faktörleri (K11) | Hepsi o haftanın Pazartesi carry aday evreninde, PIT: x_B = BTC haftalık basit getirisi; x_A = eşit ağırlıklı alt sepeti getirisi; x_R = R30 sırasına göre üst %30 eşit ağırlıklı long, alt %30 short, "sonraki haftanın getirisi"; x_S = s^trend sırasına göre aynı biçimde kurulmuş uzun-kısa getirisi. "x_S trend bacağının P&L'ini kullanmaz; mühür (§2) bozulmaz." | haftalık, n_w = 143 | R30 = 30 günlük log getiri (MIMARI §4.2); s^trend = MIMARI §3.1 formülü, bütün carry adayları için (§3.2 madde 1) | §6.2; §3.2 |
| S10 | Standart yükleme (K11) | b̃_k = b_k · sd(x_k) / sd(r^P). "Faktörün tek başına açıkladığı fiyat varyansı payı yaklaşık b̃_k²'dir." SE(b̃_k) = SE_NW(b_k) · sd(x_k) / sd(r^P); "sd'ler örneklem değeridir." Regresyon: r^P_w = a + b_B·x_B + b_A·x_A + b_R·x_R + b_S·x_S + e (ortak) | haftalık, n_w = 143 | %90 aralık b̃_k ± 1,645·SE(b̃_k) | §6.2; §6.3 |
| S11 | Ölçek ve haftalık seriler | r^X_w = Σ_{h∈w} X_h / (ω_C · L · NAV_{w başı}), X ∈ {F, P, C, N}. "Sharpe ölçekten bağımsızdır. Beta ve MDD bu carry birim ölçeğinde okunur." Funding: F^alt_T = Σ_{i∈alt} −q^C_i(T−)·m_i(T)·ρ_i(T); F^hdg_T = −q^C_BTC(T−)·m_BTC(T)·ρ_BTC(T); Fiyat P^alt_h = Σ_{i∈alt}[q^C,eski_i·(open_h − close_{h−1}) + q^C,yeni_i·(close_h − open_h)]; P^hdg aynı (BTC); Maliyet C_h = Σ_i \|Δq^C_i\|·open_h·c_i/10⁴; F = F^alt + F^hdg; P = P^alt + P^hdg; N = F + P − C. | haftalık, n_w = 143 | ω_C = 0,20; L = 1; NAV_{w başı} | §5.2; §5.3 |
| S12 | Artık serisi ve gerçekleşen seri | A^C_w = Σ_{t∈w} A^C_t; a^C_w = A^C_w/(ω_C·L·NAV_{w başı}); r^{N,g}_w = r^N_w + a^C_w. A^C_t = Σ_i s^C_i·A_i,t (MIMARI §4.7). "Netleme kazancı carry'ye yazılmaz." | haftalık, n_w = 143 | s^C_i: MIMARI §4.7 tek fonksiyonu | §5.6; §5.2 |

---

## Tablo 3. Karar ölçütleri (§6.3)

Ortak notlar (§6.3, §7.1):
- "hepsi önceden; K3/K4 dışındakilerin hepsi sağlanmalı."
- **Çift seri kuralı (KC-05):** "K1, K6, K8, K9 ve K10 hem sanal seriyle (r^N) hem gerçekleşen seriyle (r^{N,g} = r^N + a^C, §5.6) hesaplanır; ölçüt ancak **ikisinde de** geçerse geçmiş sayılır. K1'de iki seri için ρ_üst ayrı hesaplanır ve her seri kendi eşiğine karşı sınanır. K2, K5, K7 ve K11 funding/fiyat ayrıştırmasına dayanır ve sanal satırlarla hesaplanır; gerçekleşen seriden sapmaları V4a/V4b ile sınırlıdır."
- Maliyet çarpanı: "K2, K6, K7'deki maliyet çarpanı MIMARI §6'daki tek tanımdır" (§6.3 notlar); m_c ∈ {1, 2, 3}; yöntem MIMARI §6.2: "Her k değeri ayrı ve tam bir koşudur."
- Uç durum (hepsi için) belgede genel kural: "Hesaplanamayan ölçüt geçmemiş sayılır" (§7.1). Sıfır varyans, NaN, boş dilim için ölçüte özgü kural yalnız K8'de yazılıdır (aşağıda).
- Eşitlik ve yön (§7.1): "Eşitlik ölçütün yazıldığı yöndedir (K1: SR^K = K1\* geçer; K2: t = 3,0 geçer; K9/K11: aralık ucu toleransa eşitse geçmez, çünkü aralık açık (−δ, +δ) içinde olmalıdır)."

| Kimlik | Ad | Formül | Girdi serisi | Örneklem / pencere / dilim | Eşik (sayı, yön) | Bağlayıcı mı | Uç durumlar | Ref |
|---|---|---|---|---|---|---|---|---|
| K1 | Kredilenen net Sharpe başabaşı aşar | SR^K(r) ≥ K1\*(ρ_üst) (S2, S5, S6). r ∈ {r^N (a = 0), r^{N,g} (a = a^C)}; ρ_üst her seri için ayrı, her seri kendi eşiğine karşı sınanır | r^F = (carry_funding + hedge_funding), r^C = carry_maliyet, r^P = (carry_fiyat + hedge_fiyat), a^C = artik_carry, hepsi haftalık ve ω_C·L·NAV_{w başı} ile ölçekli; r^N = r^F + r^P − r^C; r^{N,g} = r^N + a^C_w; ρ̂ için r^trend,net (tanımı U-01; olası satırlar trend_fiyat, trend_funding, trend_maliyet) | haftalık, n = 143; m_c = 1; "taban delist" (h_L %10, h_S %5; §4.3); tam D | SR^K ≥ K1\*; K1\* = 0,85·g(ρ_K1, 1/3) ∈ [0,138; 0,370]; eşitlik geçer | Evet; çift seri: iki seride de | Belgede yok; genel §7.1 (hesaplanamaz → geçmemiş). Tanımsız kalanlar: std(r) = 0; ρ̂ = ±1 iken atanh; ρ̂ NaN | §6.3 K1; §6.2; §8.4 |
| K2 | Funding maliyeti anlamlı aşar | NW t(r^F − r^C) ≥ 3,0 **ve** bootstrap tek taraflı %95 alt sınır > 0 | r^F − r^C (sanal satırlar) | haftalık, n = 143; NW ℓ ∈ {4, 12} büyük SE (S3); bootstrap blok 4 ve 12, 10.000, tohum 20260928, iki alt sınırın küçüğü (S7); m_c = 1 (yalnız örtük, U-05) | t ≥ 3,0 (eşitlik geçer) **ve** alt sınır > 0 (katı) | Evet; sanal seri (çift seri değil) | Belgede yok; genel §7.1 | §6.3 K2; §6.2; §6.4 |
| K3 | Fiyat ortalaması eşdeğerliği, alt taraf | TOST alt kolu: μ_P'nin %95 tek taraflı alt sınırı > −δ_P; δ_P = %4/yıl birim | r^P (carry_fiyat + hedge_fiyat, ölçekli) | haftalık, n = 143; NW büyük SE (betimsel K3/K4 için de "büyük", §6.2) | alt sınır > −δ_P (δ_P = %4/yıl birim) | **Hayır (2. tur).** "Yalnız rapor." Bağlayıcı rolü K1/K6/K8'deki fiyat kaybı düşümüne geçti: K3'ün sorusu (fiyat funding'i silmez mi) fiyat kaybının K1/K6/K8'de düşülmesiyle yanıtlanır. Kararda (§7.1) yer almaz; K1–K11 değerleri hüküm dosyasına yazılır (§7.2) | Belgede yok | §6.3 K3; §6.4 |
| K4 | Fiyat ortalaması eşdeğerliği, üst taraf | TOST üst kolu: μ_P'nin %95 tek taraflı üst sınırı < +δ_P | r^P | K3 ile aynı | üst sınır < +δ_P | **Hayır (2. tur).** "Yalnız rapor." Bağlayıcı rolü "fiyat kazancı kredilenmez" kuralına (S2) geçti: K4'ün sorusu (getiri fiyattan mı) fiyat kazancının hiç sayılmamasıyla yanıtlanır | Belgede yok | §6.3 K4; §6.4 |
| K5 | Taşıma tutarlılığı | (r^F − r^C) > 0 olan ay payı ≥ %75 (≥ 25/33) | r^F − r^C, aylık (sanal satırlar; aylık ölçek tanımı U-06) | ay, n = 33 (UTC takvim ayı 2023-10 → 2026-06) | pay ≥ %75, yani ≥ 25/33 ay; her ay için (r^F − r^C) > 0 (katı) | Evet; sanal seri | Belgede yok; genel §7.1 | §6.3 K5; §6.4 |
| K6 | Maliyet 2× dayanıklılığı | SR^K(m_c = 2) > 0 (S2) | m_c = 2 tam yeniden koşunun r^N ve r^{N,g} serileri (r^F, r^C, r^P, a^C) | haftalık, n = 143; tam yeniden koşu (MIMARI §6.2) | SR^K > 0 (katı) | Evet; çift seri | Belgede yok; genel §7.1 | §6.3 K6; §3.6 |
| K7 | Maliyet 3× dayanıklılığı | NW t(r^F − r^C; m_c = 3) ≥ 2,0 | m_c = 3 tam yeniden koşunun r^F − r^C serisi (sanal) | haftalık, n = 143; NW büyük SE (S3); tam yeniden koşu | t ≥ 2,0 (eşitlik geçer) | Evet; sanal seri | Belgede yok; genel §7.1 | §6.3 K7; §6.4 |
| K8 | Tekil isim bağımlılığı | Yeniden koşu: toplam N katkısına göre en iyi 3 ve en kötü 3 isim carry aday listesinden bütün dönem çıkarılır; sonra SR^K > 0. "İsim sıralaması ana koşunun sanal carry satırlarından yapılır; eşitlikte alfabetik." Çıkarılanlar yalnız carry adaylığından çıkar; trend evrenindeyse trend onları tutar | ana koşunun isim bazlı sanal carry N katkısı (isim bazlı satır `ayristirma.py`'de yok, U-07); çıkarma sonrası yeniden koşunun r^N ve r^{N,g} serileri | haftalık n = 143; isim ≥ 30 ("Hiç tutulmuş ayrı isim sayısı"); m_c = 1 (örtük) | SR^K > 0 (katı) | Evet; çift seri | **Belgede yazılı:** hiç tutulmuş ayrı isim sayısı < 30 ise K8 hesaplanamaz ve sonuç A. Eşitlikte alfabetik sıra. Diğer uç durumlar yok | §6.3 K8 ve notlar; §3.6 |
| K9 | Beta eşdeğerliği | β_BTC ve β_alt için ayrı ayrı %90 güven aralığı (NW, büyük SE) ⊂ (−0,15; +0,15) (S4, S8) | r^N ve r^{N,g}; x_B (BTC haftalık basit getirisi), x_A (eşit ağırlıklı alt sepeti, o haftanın carry aday evreni) | haftalık n = 143; iki ayrı regresyon × iki seri = 4 aralık | aralığın iki ucu da (−0,15; +0,15) içinde (açık aralık; uç eşitse geçmez) | Evet; çift seri | Belgede yok; genel §7.1 | §6.3 K9; §6.2; §6.4 |
| K10 | Trend bağımsızlığı | \|ρ̂(r^N, r^trend,net)\| ≤ 0,30. "ρ'nun ekonomik etkisi ayrıca K1\*'a ρ_üst ile girer." | r^N ve r^{N,g}; trend haftalık serisi (r^trend,net; tanımı U-01) | haftalık n = 143 | \|ρ̂\| ≤ 0,30 (eşitlik geçer) | Evet; çift seri | Belgede yok; genel §7.1 | §6.3 K10; §2 |
| K11 | Fiyat faktörü yüklemesi eşdeğerliği | r^P_w = a + b_B·x_B + b_A·x_A + b_R·x_R + b_S·x_S + e (ortak regresyon). Dört standart yüklemenin her biri için %90 aralık ⊂ (−δ_b; +δ_b), δ_b = 0,30 (kesişim-birleşim TOST; S9, S10). "Ham katsayılar, NW t'leri ve round-1'deki ortak Wald p değeri yalnız raporlanır; karar standart yükleme aralıklarıyla verilir." | r^P (carry_fiyat + hedge_fiyat, ölçekli); x_B, x_A, x_R, x_S (ek veri) | haftalık n = 143 | dört aralığın her biri (−0,30; +0,30) içinde (açık aralık; uç eşitse geçmez) | Evet; sanal seri (çift seri değil) | Belgede yok; genel §7.1 | §6.3 K11; §6.2; §6.4 |

---

## Tablo 4. Betimsel raporlar (§6.6)

"Betimsel (bağlayıcı olmayan) raporlar." Hiçbiri karara girmez; §7.1: "Sonuç ne olursa olsun bütün ölçütler, betimsel raporlar ve karar yayımlanır (trend satırları hariç, §2)." Hüküm dosyasına yazılırlar (§7.2). Sayım biçimi (kalem = virgül/noktalı virgülle ayrılmış öğe) bu listenin tercihidir.

| Kimlik | Ad | Tanım | Girdi | Ref |
|---|---|---|---|---|
| BR-01 | φ | φ = (F̄ − C̄) / (F̄ − C̄ + max(P̄, 0)) | r^F, r^C, r^P ortalamaları (carry_funding + hedge_funding; carry_maliyet; carry_fiyat + hedge_fiyat) | §6.6 |
| BR-02 | Çeyrek tablosu | 11 çeyrek, betimsel ("n < 30"); sütunları belirtilmemiş (U-33) | satır toplamları çeyreklik | §6.6; §4.1 |
| BR-03 | MDD | en büyük düşüş; "carry birim ölçeğinde okunur" (§5.3); seri ve bileşik/toplamsal biçim belirtilmemiş (U-34) | r^N (ve/veya r^{N,g}) kümülatifi | §6.6; §5.3 |
| BR-04 | En kötü hafta | en kötü haftalık getiri | r^N haftalık | §6.6 |
| BR-05 | En kötü isim-hafta | isim × hafta bazında en kötü değer | isim bazlı haftalık carry satırları (`ayristirma.py`'de yok) | §6.6 |
| BR-06 | Delist senaryolarında K1 değeri | h_L = %50 ve %90 senaryolarında K1 (SR^K ve K1\*) değeri | h_L %50 ve %90 yeniden koşuları (§4.3); baz h_L = %10, h_S = %5 | §6.6; §4.3; §3.6 |
| BR-07 | K11 tekil katsayıları ve t'leri | ham b_k ve standart b̃_k katsayıları, NW t'leri | K11 regresyonu | §6.6; §6.3 notlar |
| BR-08 | ℓ = 4 ve ℓ = 12 için bütün NW t'leri | her ölçütteki NW t değerleri, iki gecikme için ayrı | K2, K7, K9, K11 ve K3/K4 serileri | §6.6; §6.2 |
| BR-09 | Andrews otomatik gecikmesiyle t'ler | Andrews (otomatik gecikme) ile NW t'leri; kernel/yöntem belirtilmemiş (U-35) | aynı seriler | §6.6; §14 K2-11 |
| BR-10 | κ_C < 1 gün oranı | κ_C < 1 olan gün sıklığı ("κ_C < 1 beklenen durum değildir; sıklığı raporlanır", §3.3, §9) | günlük κ^C_t | §6.6; §3.3; §9 |
| BR-11 | Trend katsayılarının bağlama sıklığı | c_g, c₁, c₂ (trend bacağı küçültme katsayıları) bağlama sıklığı | çözücü günlüğü ("günlük κ_C, trend katsayıları ve bağlayan tavan kaydedilir", §3.3 madde 6) | §6.6; §3.3 |
| BR-12 | S4 bağlama sıklığı | S4 (net kitaptaki en büyük tek alt short, sınır %10 NAV) tavanının bağlama sıklığı | çözücü günlüğü | §6.6 |
| BR-13 | n_C serisi | haftalık carry aday sayısı serisi | MIMARI §4.1 aday listesi | §6.6; §6.1 V3 |
| BR-14 | Gerçekleşen kitap tavanları (K1-04) | gerçekleşen ve devreden kitapta S1, S2, S4 aşım günü oranı ve en büyük aşım; hedefe ulaşılamayan gün oranı | gerçekleşen ve devreden kitap (T4 tanımı banka ön-kaydında, §14 K1-04) | §6.6; §14 |
| BR-15 | Hedge yuvarlama (K1-18) | kapı NAV'ında ve 5.000 USDT demo NAV'ında BTC hedge nominalinin bir lot adımının altında kaldığı gün oranı; "Ağırlıktan hesaplanır; yeniden koşu gerekmez." | günlük w^C_BTC,t, NAV, lot adımı | §6.6; §9 |
| BR-16 | Doldurulan funding kayıtları | sayısı ve F'ye katkısı (§4.2 madde 6: "bacak ve isim bazında") | funding doldurma olayları | §6.6; §4.2 |
| BR-17 | Long ve short bacak satırları | carry bacaklarının ayrı satırları | bacak bazlı carry satırları (`ayristirma.py`'de yok) | §6.6 |
| BR-18 | Netleme kazancı | Σ bacak maliyetleri − gerçek net maliyet; carry'ye yazılmaz | `netleme` | §6.6; §5.2 |
| BR-19 | Σ_t \|A^C_t\| | günlük carry artığının mutlak toplamı | `artik_carry` (günlük) | §6.6 |
| BR-20 | Bootstrap SR aralığı | SR için bootstrap aralığı; güven düzeyi belirtilmemiş (U-36) | r^N (ve/veya r^{N,g}) | §6.6; §6.2 |
| BR-21 | K3/K4 TOST ve fiyat ortalamasının %90 aralığı | K3/K4 TOST (δ_P = %4/yıl birim) ve μ_P'nin %90 aralığı | r^P | §6.6 (2. tur tanıları) |
| BR-22 | Kredilenmeyen SR | SR(r^N) ve SR(r^{N,g}) (S1) | r^N, r^{N,g} | §6.6 |
| BR-23 | a^C_w serisi ve en büyük üç haftalık sapma | a^C_w serisi; \|a^C_w\| en büyük üç hafta | `artik_carry` haftalık | §6.6 |
| BR-24 | Sıfır/sıfır artık tanısı | "İki sanal miktarın 0 olduğu isim-günlerde gerçekleşen artık P&L'in toplamı, mutlak toplamı ve bu günlerin önceki son sıfır olmayan s^C_i ile carry'ye düşecek karşılığı" | isim-gün bazlı artık ve sanal miktarlar (`ayristirma.py`'de isim bazlı artık yok; U-25) | §6.6; §5.6 |
| BR-25 | κ^C günlük göreli değişim tanısı | κ^C_t'nin önceki güne göre göreli değişiminin %25'i aştığı gün sayısı ve round-1'deki bantlı kuralın bu defterden izleme farkı | günlük κ^C_t | §6.6; §5.1 |
| BR-26 | ρ̂, ρ_üst ve iki serinin K1\* değerleri | ρ̂, ρ_üst (S5) ve K1\* (S6), r^N ve r^{N,g} için ayrı; "ρ̂ ve ρ_üst hüküm dosyasına yazılır" (§6.3 notu) | r^N, r^{N,g}, r^trend,net | §6.6; §6.3 |
| BR-27 | K1\* duyarlılığı | K1\*'ın SR_T,ref ∈ {0,45; 0,60} ve k ∈ {0,27; 0,43} duyarlılığı (bağlayıcı değil); kombinasyon biçimi belirtilmemiş (U-37) | S6 formülü | §6.6 |
| BR-28 | V6 fark günlerinin ortalama trend brüt farkı | V6'da B ile A trend hedefinin farklı olduğu günlerde ortalama trend brüt farkı | B w^T* ve A `hedef_agirlik` | §6.6; §6.1 V6 |

### Tablo 4b. §6.6 dışında "raporlanır" / "betimsel" denen kalemler

| Kimlik | Ad | Tanım | Girdi | Ref |
|---|---|---|---|---|
| BX-01 | B−A trend bacağı farkı | tavan bağladığında B'nin trend bacağının A'nınkinden küçük olması: "Bu fark B−A ayrıştırmasında görünür ve raporlanır." | B ve A trend hedefleri | §3.3 gerekçe |
| BX-02 | Doldurulan funding: bacak ve isim bazlı ayrıntı | "Doldurulan kayıt sayısı ve funding tutarı bacak ve isim bazında raporlanır." (BR-16'nın ayrıntısı) | funding doldurma olayları | §4.2 madde 6 |
| BX-03 | Netleme kazancı ve icra artığı ayrı rapor | "MIMARI §4.7'deki 'netleme kazancı' ve 'icra artığı' ayrı raporlanır." (icra artığının mutlak değeri ve işareti dahil, MIMARI §4.7) | `netleme`, `icra_artigi` | §5.2; MIMARI §4.7 |
| BX-04 | K11 ortak Wald p ve faktörlerin açıkladığı fiyat ortalaması | "Round-1'deki ortak Wald p değeri yalnız raporlanır"; Σ_k b_k·ortalama(x_k) "ayrıca raporlanır; bu pay zaten kredilenmediği için karara ayrıca girmez" | K11 regresyonu | §6.3 notlar |
| BX-05 | DSR | "DSR: betimsel. N, banka ön-kaydının sayım kuralıyla hesaplanır. Eşik konmaz." | deneme sayacı N (defter) | §6.5; §11 |
| BX-06 | Sonradan koşulan ablasyon varyantları | nötrlemesiz, σ'suz skor, aylık karar: "kapıda koşulmaz"; sonradan koşulursa ayrı defter satırı ve karar değişmez | (koşu dışı) | §3.5 |
| BX-07 | Denetim dosyası raporları | veri raporu; değişmez denetimleri; doldurulan kayıt sayıları (ölçüt değeri içermez) | motor günlüğü | §7.2 |
| BX-08 | Sentetik fikstür doğrulaması | her senaryoda P(B) ve ölçüt başına geçme oranı (Adım 3; "D kullanmaz"; kapı koşusundan ayrı; tohum 20260929; 10.000 tekrar) | sentetik üreteç (§8.5) | §8.5; §2 |

---

## Karar kuralı ve kör hüküm (§7.1–§7.3)

### §7.1 Karar
- **B** ⇔ V1–V6 sağlanır (V4a ve V4b dahil) **ve** bağlayıcı ölçütlerin (K1, K2, K5, K6, K7, K8, K9, K10, K11) hepsi, çift seri kuralı gereken yerde (K1, K6, K8, K9, K10) iki seride de geçer. "K3 ve K4 2. turda yalnız rapordur."
- **A** ⇔ "Diğer bütün durumlar." "Hesaplanamayan ölçüt geçmemiş sayılır."
- Kapı geçerse nihai mimari B (trend ve sabit bütçeli carry uydusu; ω_C = 0,20); geçemezse A (yalnız trend; carry kodu nihai mimaride devre dışı). "Kapı tek atıştır; ana deneme sayısı 1'dir." (belge girişi, "Bağlayıcı çerçeve" paragrafı; §9).
- Karar, koşu betiği tarafından mekanik olarak üretilir (§3.7).
- Yasaklar: "Kıl payı" yoktur, ölçüt ikilidir; eşitlik ölçütün yazıldığı yöndedir (K1: SR^K = K1\* geçer; K2: t = 3,0 geçer; K9/K11: aralık ucu toleransa eşitse geçmez). Yeniden koşma yoktur (eşik, dönem, evren, NAV, L, tohum, ölçüt kümesi değişmez). Alt küme seçilmez (dönem kırpılmaz, isim dışlanmaz, "şu çeyrek hariç" yoktur). Başarısız sonucu yeni eşikle ya da yeni varyantla kurtarmak yasaktır (yeni carry sürümü ayrı hipotez, ayrı ön-kayıt, ayrı deneme; bu bankaya gidemez). "Sonuç ne olursa olsun bütün ölçütler, betimsel raporlar ve karar yayımlanır (trend satırları hariç, §2)."
- Bağlayıcı cümle (§2): "D'de P&L görüldükten sonra hiçbir eşik, ölçüt, parametre ya da ölçüt kümesi değişmez."

### §7.2 Kör hüküm (K2-07): üç çıktı dosyası ve açıklık durumu
Kapı betiği üç dosya yazar ve "hepsini yazıldığı anda hash'ler":
1. **Denetim dosyası** (açık, yayımlanır; ölçüt değeri içermez): V1–V6 geçti/kaldı, değişmez denetimleri, veri raporu, doldurulan kayıt sayıları. "V4a/V4b yalnız geçti/kaldı olarak yazılır; oranları hüküm dosyasındadır."
2. **Hüküm dosyası** (açık, yayımlanır; kör açılır): K1–K11 değerleri, eşikler, geçti/kaldı, karar, betimsel raporlar; ρ̂ ve ρ_üst de buraya yazılır (§6.3 notu).
3. **Trend mühür dosyası** (mühürlü; yalnız hash raporlanır): trend satırları. "Banka hükmü açılana kadar açılmaz" (§2; BANKA_ONKAYIT §1.3). Bu kural bağlayıcıdır (§2). Trend satırları ayrı dosyaya yazılır; kapı yalnız K10 için trend haftalık getirisini içeride kullanır ve yalnız korelasyonu raporlar.
- Koşu sırasında hiçbir metrik ekrana basılmaz.
- Önceden yazılmış denetim listesi (V1–V6, değişmezler, veri raporu; istenirse Codex'in hash ve değişmez yeniden üretimi) hüküm dosyası açılmadan tamamlanır ve kaydedilir. Hüküm dosyası ancak bundan sonra açılır.
- Kilit öncesi/sonrası bağlam (§2, §3.7): motor kodu, parametre nesnesi, veri hash'leri ve Adım 2 sonucu koşudan önce hash'lenir; MIMARI, HAR seçim sonucu, bu kapı ön-kaydı, banka ön-kaydı, açık soru yanıtları ve kalibrasyon çıktısı `KILIT.json` içinde birlikte hash'lenir (Adım 4). Adım 6 (D doğrulama ve kuru koşu): "Performans çıktıları mühürlü; yalnız hash ve denetim çıktıları."

### §7.3 Hata yönetimi ve teknik geçersizlik dalları
**Hüküm açılmadan önce bulunan hata:**
1. Hata, kapı çıktısından bağımsız bir sentetik fikstürle gösterilir.
2. Düzeltme diff'i yayımlanır. Parametre, eşik ve davranış değişmez.
3. Kapı bütünüyle bir kez, yine kör olarak yeniden koşulur. Deneme sayacı 2 olur; deftere ayrı satır girer (§3.6: "Teknik yeniden koşu sayacı 2 yapar ve deftere ayrı satır girer").
4. En fazla bir teknik yeniden koşu. "İkinci teknik geçersizlikte sonuç A."

**Hüküm açıldıktan sonra bulunan hata:**
- Yalnız şu sınıflar kabul edilir: muhasebe özdeşliği, bakış-ileri, funding işareti, maliyet işareti. Hata kapı çıktısından bağımsız bir testle gösterilmelidir.
- Kabul edilen hata sonucu **A** yapar ("kapı değerlendirilemedi"). "Sonuç B'ye hiçbir koşulda dönmez." İki çıktı da raporlanır.
- Gerekçe (belgede): B pozitif kanıt ister; hüküm sonrası hata avı yalnız B'den A'ya götürebilir.
- "Sonuç beğenmeme hiçbir koşulda gerekçe değildir."

**Ölçüt kaynaklı A dalları (özet):** herhangi bir V-koşulu başarısız (§6.1); K8 hesaplanamaz (< 30 isim; §6.3); hesaplanamayan herhangi bir ölçüt (§7.1); V6 aşımı ("B = A + carry" varsayımı ve §8.4 formülü geçersiz; §6.1); herhangi bir bağlayıcı K ölçütünün (çift seri gereken yerde iki seriden birinde) başarısızlığı.

---

## Koda aktarım notları

### (a) `ayristirma.py`'nin şu an verdiği satırlarla doğrudan hesaplanabilen ölçütler

`AyristirmaSonucu` alanları: `saat_ms` (int64 dizisi), `satirlar` (13 saatlik dizi: `SATIRLAR`), `gunluk` (satır → {gün_ms: toplam}, UTC gün anahtarı), `ozdeslik_max_hata`, `toplam` (satır toplamları), `trend_coin`, `trend_q`, `trend_eski`, `trend_yeni` (coin bazında yalnız trend bacağı). `SATIRLAR = ('trend_fiyat', 'trend_funding', 'trend_maliyet', 'carry_fiyat', 'carry_funding', 'carry_maliyet', 'hedge_fiyat', 'hedge_funding', 'netleme', 'icra_artigi', 'artik_carry', 'artik_trend', 'dnav')`.

**Tablo 2b. Belge serisi ↔ `ayristirma.py` satırı eşlemesi**

| Belge sembolü | Belge tanımı | `ayristirma.py` karşılığı | Not |
|---|---|---|---|
| F^alt | Σ_{i∈alt} −q^C_i(T−)·m_i(T)·ρ_i(T) | `satirlar['carry_funding']` | kod: BTC olmayan coinler |
| F^hdg | −q^C_BTC(T−)·m_BTC(T)·ρ_BTC(T) | `satirlar['hedge_funding']` | BTC (`p.btc`) |
| F | F^alt + F^hdg | `carry_funding + hedge_funding` | |
| P^alt | Σ q^C,eski·(open − close_{h−1}) + q^C,yeni·(close − open) | `satirlar['carry_fiyat']` | |
| P^hdg | aynı, BTC | `satirlar['hedge_fiyat']` | |
| P | P^alt + P^hdg | `carry_fiyat + hedge_fiyat` | |
| C | Σ_i \|Δq^C_i\|·open_h·c_i/10⁴ | `satirlar['carry_maliyet']` | alt ve BTC hedge bacak maliyeti tek satırda toplanır (CARRY §5.2 de tek C) |
| N | F + P − C | türetilir (satır yok) | |
| netleme kazancı | Σ bacak maliyetleri − gerçek net maliyet | `satirlar['netleme']` | carry'ye yazılmaz |
| A^C_t | Σ_i s^C_i·A_i,t | `satirlar['artik_carry']` (saatlik), `gunluk['artik_carry']` (günlük) | s^C karar kaydından, [D 01:00, D+1 01:00) aralığına uygulanır |
| icra artığı | e_i = q_i − q^T,v_i − q^C,v_i artığının P&L'i | `satirlar['icra_artigi']`; `artik_trend = icra_artigi − artik_carry` | kod A_i'ye uzlaşma farkı ve canlı düzeltme de katar (U-20) |
| trend satırları | (belgede r^trend,net tanımı yok) | `trend_fiyat`, `trend_funding`, `trend_maliyet`; coin bazında `trend_coin[c]` (Σ_c = fiyat + funding − maliyet) | K10 ve K1 ρ̂ girdisi için olası satırlar; tanım U-01 |
| ΔNAV | trend + (F+P−C) + netleme + icra artığı | `satirlar['dnav']` (yalnız gün sonu NAV kaydı olan saatlerde, aksi NaN); `ozdeslik_max_hata` (günlük toplamda, mutlak) | V2 |
| r^X_w | Σ_{h∈w} X_h/(ω_C·L·NAV_{w başı}) | saatlik/günlük satırların hafta toplamı | NAV_{w başı}, ω_C, L `AyristirmaSonucu`'nda yok |
| a^C_w | A^C_w/(ω_C·L·NAV_{w başı}) | `artik_carry` hafta toplamı / aynı ölçek | |
| r^{N,g}_w | r^N_w + a^C_w | türetilir | |

Saat indeksi: `satirlar[s][n]` ↔ `saat_ms[n] = T`; T'de açılan bar için değerleme T+1h'dedir; T damgalı funding n. satıra yazılır. Hafta sınırları UTC gün sınırlarıyla hizalı olduğundan `gunluk` ile de haftalık toplam kurulabilir (Pazartesi hizası kodda yok).

**Bu satırlarla (haftalık toplama, NAV_{w başı}, ω_C ve L ölçeği eklenerek) doğrudan hesaplanabilenler:**
- V2 (`ozdeslik_max_hata` / `dnav`), V4a, V4b (r^N_w, a^C_w).
- K1 (ana koşu, m_c = 1; SR^K bileşenleri r^F, r^C, r^P, a^C), K2, K3, K4 (r^P), K5 (aylık toplama), K10 (trend satırları; tanım U-01).
- BR-01, BR-02, BR-03, BR-04, BR-08 (ana koşu serileri için), BR-18, BR-19, BR-20, BR-21, BR-22, BR-23, BR-26 (ρ̂ ve ρ_üst; trend serisi tanımına bağlı), BR-27 (S6 formülü).

### (b) Ek veri ya da ek hesap gerektirenler ve belgede nereden geldikleri

- **K6, K7 (m_c = 2, 3):** MIMARI §6.2'ye göre "Her k değeri ayrı ve tam bir koşudur"; `ayristir(..., maliyet_k)` günlükteki `maliyet_k` ile aynı olmak zorundadır, yani her k için ayrı günlük gerekir (§3.6, §6.3 notları).
- **K8:** ana koşunun isim bazlı sanal carry N katkısı; ardından aday listesinden 6 ismin çıkarıldığı tam yeniden koşu (§6.3 K8 ve notları, §3.6). `ayristirma.py` isim bazlı carry satırı vermez.
- **BR-06:** h_L = %50 ve %90 delist senaryosu yeniden koşuları (§4.3, §6.6).
- **Toplam koşu sayısı (belgeden türetilen):** ana koşu + m_c = 2 + m_c = 3 + K8 yeniden koşusu + iki delist senaryosu = 6 tam koşu; A için yalnız `hedef_agirlik` (P&L'siz; V6). Belgede toplam sayı yazılı değildir.
- **NAV_{w başı}, ω_C, L:** ω_C = 0,20 ve L = 1 (§3.1, §9; MIMARI §7); NAV birincil banka NAV'ı (varsayılan 0,1M USDT; Adım 4'te kilitlenir, §3.1). NAV serisi `AyristirmaSonucu`'nda yok; `dnav` kümülatifi ve günlüğün başlangıç kaydındaki `nav0` ya da günlüğün NAV kayıtları gerekir.
- **K9 (x_B, x_A):** BTC ve carry aday evreni alt sepetinin haftalık basit getirileri; fiyat verisi (`TamVeri.barlar`) ve "o haftanın Pazartesi carry aday evreni, PIT" (MIMARI §4.1) (§6.2).
- **K11 (x_B, x_A, x_R, x_S):** x_R için R30 (30 günlük log getiri; MIMARI §4.2) sırası; x_S için s^trend (MIMARI §3.1; "bütün carry adayları için", §3.2 madde 1); her ikisi de Pazartesi aday evreninde üst %30 long / alt %30 short (§6.2).
- **V1:** Adım 0 test sonuçları ve sentetik fikstürler (MIMARI §5.6, §5.6 içeriği bu listeye alınmadı); carry birim kitabının ex-ante vol'ü (Σ̂ ve τ = %15; MIMARI §4.4 adım 1, §4.5 adım 0).
- **V3, BR-13:** haftalık n_C (aday sayısı) ve carry kitabı sıfır göstergesi (MIMARI §4.1, §4.4 adım 6).
- **V5, BR-10, BR-25:** motor günlüğünden q^C,v, κ^C_t (ve κ_etkin,t), s^C serileri. `ayristirma.py` q^C,v ve s^C'yi karar kaydından okur ama döndürmez; κ^C_t'yi hiç okumaz.
- **V6, BR-28:** B çözücüsünün günlük w^T* hedefi ve A'nın `hedef_agirlik` hedefi.
- **BR-11, BR-12, BR-14:** çözücü günlüğü (c_g, c₁, c₂, κ^C, λ, hedge ağırlığı, bağlayan tavan; MIMARI §4.5 adım 6); gerçekleşen ve devreden kitap S1/S2/S4 aşım ölçümü.
- **BR-15:** günlük hedge ağırlığı, NAV ve lot adımı (kapı NAV'ı ve 5.000 USDT).
- **BR-16, BX-02:** funding doldurma olayları (`ayristirma.py` içinde bacak durumlarında işlenir ama sayılıp döndürülmez).
- **BR-09:** Andrews otomatik gecikme yöntemi.
- **BX-05:** deneme sayacı N (banka ön-kaydı sayım kuralı, defter).
- **Bootstrap:** S7 parametreleri (blok 4 ve 12, 10.000, tohum 20260928).

### (c) Belgede tanımlı olup `ayristirma.py` satırlarında karşılığı bulunmayan kavramlar
1. İsim bazlı carry satırları (funding, fiyat, maliyet, N katkısı): yalnız trend için `trend_coin` vardır. K8 sıralaması, BR-05, BR-16 (isim bazı), BR-24 bunlara bağlıdır.
2. Long ve short bacak satırları (BR-17).
3. r^trend,net: belgede tanımsız (U-01); satırlarda `trend_fiyat + trend_funding − trend_maliyet` ile ayrıca `artik_trend` bulunur.
4. κ^C_t, κ_etkin,t, q^C,v_i, s^C_i, n_C, λ, c_g, c₁, c₂ serileri (karar kaydında var, dönüş yapısında yok).
5. Faktör serileri x_B, x_A, x_R, x_S ve R30, s^trend kesitleri.
6. NAV_{w başı} serisi.
7. Haftalık, aylık ve çeyreklik toplama ve UTC Pazartesi hizası (`gunluk` yalnız UTC gün toplamıdır).
8. İsim bazlı artık A_i (kodda yerel `artik` sözlüğü; yalnız `icra_artigi`, `artik_carry`, `artik_trend` toplamları döner): sıfır/sıfır tanısı (BR-24) ve Σ_i s^C_i·A_i'nin isim dökümü için gerekir.
9. Gerçekleşen kitap ve devreden kitap tavan ölçümleri (S1, S2, S4 aşımı), hedefe ulaşılamayan gün.
10. A koşusunun trend hedefi (`hedef_agirlik`) ve B−A trend farkı.
11. Sentetik fikstür (§8.5) ve V1 fikstürleri (motor test paketi).
12. Not: `ayristirma.py` modül açıklaması özdeşliği "her saat" der; kod özdeşliği günlük toplamda sınar. Belge (§5.5, V2) "her gün" der.

---

## Belirsizlikler (yalnız işaretlenmiştir; çözülmemiştir)

Sıra kabaca ölçütün bağlayıcılığına ve etkisine göredir.

| Kod | Nokta | Ref | Neden belirsiz |
|---|---|---|---|
| U-01 | r^trend,net'in tanımı | §6.2 (ρ̂), §6.3 K10, §2 | "trend,net" için formül yok: maliyet düşülmüş ("net") mü, "net kitap" mı; trend icra artığı payı (artik_trend) ve netleme dahil mi; ölçek tabanı (NAV_{w başı}, ω_C·L bölünmesi) ne; K10 ve K1 için çift seri kuralında trend serisinin gerçekleşen karşılığı ne. K1 eşiği ve K10 buna bağlıdır. "Trend P&L'i, trend Sharpe'ı ve trend vol'ü kapıda hesaplanmaz" (§6.3) ile "trend haftalık getirisini içeride kullanır" (§2) arasında gerilim var: "hesaplanmaz" raporlanmaz/açılmaz anlamında mı belirtilmemiş |
| U-02 | Newey–West ayrıntıları | §6.2 | Bartlett ağırlık biçimi (1 − j/(ℓ+1) mi 1 − j/ℓ mi), küçük örneklem düzeltmesi, ortalama için SE ile regresyon katsayısı için HAC sandviçinin ayrıntısı yazılı değil. "Büyük SE" seçimi parametre başına mı (K11'de her b̃_k için ayrı ℓ), yoksa tüm parametreler için tek ℓ mi belirtilmemiş |
| U-03 | Bootstrap istatistiği ve ayrıntıları | §6.2; K2 (§6.3) | K2'de bootstrap edilen istatistik (ortalama(r^F − r^C) mi, t mi) yazılı değil; iki blok uzunluğu için tohumun nasıl kullanıldığı (tek akış / ayrı akış), yüzdelik yöntemi ve dairesel blok başlangıç dağılımı yazılı değil |
| U-04 | Standart sapma tanımı | §6.2, §6.3, §6.1 V4b | SR, SR^K, sd(x_k), sd(r^P), sd(r^N_w) için ddof (n mi n−1 mi) yazılı değil ("sd'ler örneklem değeridir" ddof'u belirtmez) |
| U-05 | m_c ve delist senaryosu örtük | §6.3 | "m_c = 1, taban delist" yalnız K1'de yazılı; K2, K5, K8–K11 ve V koşulları için ana koşunun m_c = 1 ve taban delist (h_L %10, h_S %5; §4.3) olduğu örtük. K8 yeniden koşusunun m_c'si de yazılı değil |
| U-06 | K5 aylık ölçek ve toplama | §6.3 K5, §5.3, §4.1 | r^X_w yalnız hafta için tanımlı; ay için ölçek (NAV_{ay başı}?) ve haftaların ay sınırında bölünmesi yazılı değil. Haftalık istatistik son iki günü (2026-06-29/30) dışarıda tutar ama n_m = 33 Haziran 2026'nın tamamını içerir görünür; bu iki günün aylık seriye girip girmediği açık değil. 2023-10'un ilk günü (10-01, T0) için de aynı |
| U-07 | K8 isim bazlı "toplam N katkısı" | §6.3 K8 ve notlar | isim bazlı N = F + P − C tanımı ve BTC hedge'in (funding, fiyat, maliyet) isimlere dağıtılıp dağıtılmayacağı yazılı değil; `ayristirma.py` isim bazlı carry satırı vermiyor. "Hiç tutulmuş ayrı isim" tanımı (q^C,v ≠ 0 en az bir gün?) yazılı değil |
| U-08 | CARRY metni MIMARI'nin 29 Eylül güncellemelerinden geride | §5.6, §6.1 V1 (KC-03 fikstürü), §11 ARAYUZ 2; MIMARI §4.1, §4.7 | CARRY §5.6: "bugünkü metinde s^C_i = 0" ve "son sıfır olmayan payın taşınması" MIMARI'ye öneri olarak yazılı; MIMARI §4.7 şimdi sıfır/sıfır durumunda son sıfır olmayan payı taşıyor. CARRY "MIMARI bu kuralı değiştirirse kapı yeni kuralı kullanır" der. Bu durumda BR-24'ün ("önceki son sıfır olmayan s^C ile düşecek karşılık") anlamı değişmiş olabilir. Ayrıca MIMARI'nin 2026-09-29 eklemeleri (κ_etkin,t, V60 tabanı, net kitaba yalnız-azaltma istisnası) CARRY'de yalnız κ_etkin ifadesiyle yer alır; V5 yalnız κ^C_t, q^C,v ve s^C'yi sayar, κ_etkin,t'yi saymaz |
| U-09 | a^C ortalamasının SR^K'ya işaretiyle tam eklenmesi | §6.2 (SR^K), §5.6, §8.5 RAPOR cümlesi | Formülde min(ortalama(r^P), 0) yalnız fiyat için kırpar; ortalama(a) kırpılmadan eklenir. a^C icra artığının fiyat + funding P&L'ini içerir. "Fiyat kazancı hiç sayılmadan" ilkesiyle gerçekleşen seride bu terimin ilişkisi belgede açıklanmamış |
| U-10 | K1 çift seri ρ_üst | §6.2, §6.3 çift seri | "iki seri için ρ_üst ayrı hesaplanır": gerçekleşen seri için trend serisinin aynı olup olmadığı (bkz. U-01) ve n_w'nin sabit 143 mü gözlenen hafta sayısı mı olduğu yazılı değil (K8 yeniden koşusu ve NaN haftalar için) |
| U-11 | V-koşullarında teknik yeniden koşu ilişkisi | §6.1 (V başlığı), §7.3 | §6.1 "biri sağlanmazsa sonuç A" der; §7.3 kör hüküm öncesi bulunan hata için bir teknik yeniden koşuya izin verir. V-başarısızlığının (örn. V2 hatası) "teknik hata" sayılıp sayılmayacağı, hangi V-başarısızlığının yeniden koşu tetiklediği yazılı değil. "Teknik geçersizlik" tanımı yok |
| U-12 | Yeniden koşuların (m_c = 2, 3, K8, delist) V-denetimine tabi olup olmadığı | §6.1, §3.6, §6.3 | V1–V6'nın yalnız ana koşuya mı yoksa tüm yeniden koşulara mı uygulandığı yazılı değil |
| U-13 | V6 "farklı" tanımı ve payda | §6.1 V6 | B'nin w^T*'ı ile A'nın hedefinin "farklı" sayılması için sayısal tolerans yazılı değil; payda gün sayısı (T0 sonrası bütün günler mi, yalnız carry aktif günler mi) yazılı değil; B'nin bant öncesi w^T* ile A'nın (bant sonrası olabilecek) hedefinin karşılaştırılıp karşılaştırılmadığı açık değil (MIMARI §4.5 adım 5: w^T* ve w^T,b ayrı) |
| U-14 | V3 sıfır hafta tanımı | §6.1 V3; MIMARI §4.1, §4.4 adım 6 | Parantez "(n_C < 10)" yalnız bir nedeni verir; "bir bacak boşsa carry kitabı o hafta 0" (MIMARI) ve κ^C = 0 durumları V3'ün sıfır sayımına girer mi belirtilmemiş; "hafta sıfır" Pazartesi kararına mı yoksa haftanın tüm günlerine mi bağlı belirtilmemiş |
| U-15 | V1'in kapı koşusunda nasıl denetlendiği | §6.1 V1, §7.2 | "Adım 0'da geçmiş" ifadesi kapı koşusundan önceki testleri anlatır; denetim dosyasında V1'in geçti/kaldı sonucunun nasıl üretileceği (kayıtlı sonucun okunması mı, kapı betiğinin yeniden çalıştırması mı) yazılı değil. "1e-9" mutlak mı göreli mi belirtilmemiş. MIMARI §5.6 içeriği (kritik hata sınıfı) bu belgede yok |
| U-16 | V2 "1e-8 NAV içinde" | §6.1 V2, §5.5 | tolerans mutlak USDT mi NAV'ın oranı mı; hangi NAV (nav0, gün başı NAV) yazılı değil. `ozdeslik_max_hata` mutlak USDT'dir |
| U-17 | Hüküm dosyası ve denetim dosyasında V3, V6, V2 değerlerinin yeri | §7.2 | Denetim dosyası "ölçüt değeri içermez; V4a/V4b yalnız geçti/kaldı" der; V3 payı, V6 oranı ve V2 fark değerlerinin hangi dosyaya yazılacağı yazılı değil |
| U-18 | K3/K4 sonuçlarının hükümdeki yeri | §6.3 başlık, §7.1, §7.2 | §7.2 "K1–K11 değerleri, eşikler, geçti/kaldı" der; K3/K4 için "geçti/kaldı" yazılıp yazılmayacağı (yalnız değer mi) açık değil |
| U-19 | K9 x_A ve x_B getiri tanımı | §6.2 (Beta), S8 | haftalık basit getirinin fiyat referansı (hangi bar kapanışı/açılışı; `ayristirma.py` sk(T) kullanır), sepet ağırlıklarının hafta boyu sabit olup olmadığı, hafta içinde maske/delist olan isimlerin getirisi, sepete BTC/ETH'nin girip girmediği (yalnız "carry aday evreni") yazılı değil |
| U-20 | A_i tanımı: belge ↔ MIMARI ↔ kod | §5.6, §5.5; MIMARI §4.7; `ayristirma.py` | CARRY §5.6/MIMARI: A_i = "e_i'nin fiyat + funding P&L'i". MIMARI tablosu: "İcra artığı = gerçek NAV değişimi − yukarıdakilerin toplamı". Kod: A_i'ye ayrıca delist uzlaşma farkı ve canlı düzeltme (nakit + miktar × açılış) girer. Üç tanım aynı mı belgede söylenmemiş |
| U-21 | Delist senaryoları tam yeniden koşu mu | §3.6, §6.6 | "Delist uzlaşma senaryoları (h_L %50, %90)" için yöntem (tam yeniden koşu mu, yeniden fiyatlama mı) yazılı değil (m_c için açıkça tam yeniden koşu) |
| U-22 | K1 ρ_üst alt/üst kırpma uç durumları | §6.3 K1 | ρ̂ = ±1 (atanh sonsuz), ρ̂ NaN, sıfır varyans durumları yazılı değil |
| U-23 | C_h toplamının kapsamı | §5.2 | F için F^alt ve F^hdg ayrı yazılıdır; C_h = Σ_i \|Δq^C_i\|·open_h·c_i/10⁴ toplamında i'nin alt isimlerle sınırlı mı yoksa BTC hedge'i de içerip içermediği belgede açıkça yazılı değil (`ayristirma.py` `carry_maliyet` satırı BTC hedge bacağını da toplar) |
| U-24 | K11 x_R, x_S kurulumu | §6.2 (Fiyat faktörleri) | "sonraki haftanın getirisi" hangi hafta (sıralamanın yapıldığı Pazartesi'yi izleyen hafta mı); üst/alt %30 kesitinin yuvarlaması (floor/ceil); uzun−kısa getirisi ölçeği (ort(long) − ort(short) mı yarısı mı; standart yükleme ölçekten bağımsızdır ama tanım yazılı değil); kesitte q^C* = 0 olan adayların bulunup bulunmayacağı |
| U-25 | Sıfır/sıfır tanısında isim bazlı artık | §5.6, §6.6 | tanı isim-gün bazlı artığı gerektirir; kodda isim bazlı artık döndürülmüyor; "carry'ye düşecek karşılık" MIMARI'nin güncel kuralına göre yeniden anlamlandırılabilir (U-08) |
| U-26 | Hüküm dosyası sonrası hata sınıfları | §7.3 | "muhasebe özdeşliği, bakış-ileri, funding işareti, maliyet işareti" sınıflarının sınırı (ör. tavan çözücüsü hatası bu sınıflara girer mi) yazılı değil |
| U-27 | V4b gösterimi | §6.1 V4b | "sd(r^N_w)" gösterimi hafta indeksli yazılmış; anlam tüm 143 haftalık serinin sd'si olarak okunuyor, belgede açık değil |
| U-28 | V5 birimi | §6.1 V5 | "mutlak fark ≤ 1e-12": q^C,v için birim (coin adedi mi NAV oranı mı) yazılı değil; κ^C_t ve s^C boyutsuz |
| U-29 | NAV_{w başı} anı | §5.3 | NAV'ın 00:00 (karar anı) mı 01:00 (geçerlilik) mı ölçüldüğü ve gün sonu NAV kayıtlarından nasıl alınacağı yazılı değil |
| U-30 | Kapı NAV'ı kilidi | §3.1 | "Varsayılan 0,1M USDT ... Değer Adım 4'te (kilit) kilitlenir": kilit değeri belgede yok; K ölçütleri bu değere bağlı |
| U-31 | Yeniden koşuların trend satırlarının mühür kapsamı | §2, §7.2 | m_c = 2, m_c = 3, K8 yeniden koşusu ve delist senaryo koşuları da trend P&L'i üretir; bu koşuların trend satırlarının "trend mühür dosyası"na girip girmediği (ayrı mühür mü, hiç yazılmaz mı) yazılı değil |
| U-32 | BR-14 ve BR-11/BR-12 tanımlarının kaynağı | §6.6, §14 K1-04 | S1, S2, S4 tavanları, "gerçekleşen kitap", "devreden kitap" ve "hedefe ulaşılamayan gün" tanımları bu belgede yok; "T4 tanımı banka ön-kaydında" (§14) ve MIMARI §3.5/§5.7'ye havale edilmiş |
| U-33 | BR-02 çeyrek tablosu içeriği | §6.6 | tablo sütunları (hangi seri, hangi istatistik) yazılı değil |
| U-34 | BR-03 MDD tanımı | §6.6, §5.3 | hangi seri (r^N, r^{N,g}, NAV), toplamsal mı bileşik mi kümülatif, haftalık mı günlük çözünürlük yazılı değil |
| U-35 | BR-09 Andrews yöntemi | §6.6, §14 K2-11 | kernel, otomatik gecikme yöntemi (AR(1) vb.) yazılı değil |
| U-36 | BR-20 bootstrap SR aralığı | §6.6 | güven düzeyi ve blok uzunluğu yazılı değil |
| U-37 | BR-27 duyarlılık kombinasyonları | §6.6 | SR_T,ref ∈ {0,45; 0,60} ve k ∈ {0,27; 0,43}: tek tek mi, 2×2 kombinasyon mu belirtilmemiş; ρ_K1 kırpması korunur mu belirtilmemiş |
| U-38 | K3/K4 "%4/yıl birim" yıllıklandırma | §6.3 K3/K4, §6.4 | haftalık ortalamadan yıla geçiş (×52) belgede yazılı değil; §6.4'te "%4/yıl birim ölçekte (≈ %0,8/yıl NAV)" |
| U-39 | Tarihsel ifadeler | §0 madde 4, §12 | §0: "K1 eşiği 0'dan 0,10'a çıktı"; §12: "sayıları round-1 ölçütlerine aittir"; güncel eşik K1\*(ρ_üst) (§6.3). §0 ve §12 tarihsel kayıt olarak durur; güncel olmadığı yalnız §0.1 ve §12 notlarından anlaşılır |
| U-40 | Kilit sonrası "yeniden koşma yoktur" ↔ tam yeniden koşular | §7.1, §3.6, §7.3 | §7.1 "Yeniden koşma yoktur" der; §3.6 maliyet çarpanı, K8 ve delist yeniden koşularını "varyant değildir" sayar; §7.3 bir teknik yeniden koşuya izin verir. Üç kavramın sınırı §3.6'da anlatılır ama V-koşullarıyla ilişkisi (U-11, U-12) belirsizdir |

---

## Ek A. Sabit ve parametre dökümü (kod için; belgeden)

| Sabit | Değer | Ref |
|---|---|---|
| D | [2023-07-01, 2026-07-01) UTC | §4.1 |
| T0 | 2023-10-01 00:00 UTC; ilk carry kararı 2023-10-02 00:00 (Pazartesi) | §4.1 |
| n_w, n_m, çeyrek | 143 hafta (2023-10-02 → 2026-06-29); 33 ay (2023-10 → 2026-06); 11 çeyrek | §4.1 |
| L, ω_C, τ | L = 1; ω_C = 0,20; τ = %15 | §3.1, §9; §6.1 V1 |
| NAV | banka birincil NAV'ı; varsayılan 0,1M USDT; demo NAV'ı 5.000 USDT (yalnız BR-15) | §3.1, §6.6 |
| Maliyet çarpanı m_c | {1, 2, 3}; ücret sabit (5 bps), dilim + etki çarpılır (MIMARI §6.2) | §3.6; MIMARI §6.1–§6.2 |
| Delist | taban h_L = %10, h_S = %5; senaryolar h_L = %50, %90 | §4.3 |
| Yıllıklandırma | √52 | §6.2 |
| NW gecikmeleri | ℓ = 4, ℓ = 12 (84 gün) | §6.2 |
| Bootstrap | dairesel; blok 4 ve 12; 10.000; tohum 20260928 | §6.2 |
| Kritik değerler | 1,645 (%90 çift taraflı / %95 tek taraflı TOST ve alt/üst sınır); 1,2816 (Fisher, tek taraflı %90) | §6.2 |
| K1\* sabitleri | SR_T,ref = 0,85; k = 1/3; ρ_K1 ∈ [0; 0,30] | §6.3; §8.4 |
| K2 | t ≥ 3,0 ve bootstrap alt sınır > 0 | §6.3 |
| K5 | ≥ %75 (≥ 25/33) | §6.3 |
| K6, K7 | SR^K(m_c = 2) > 0; NW t(m_c = 3) ≥ 2,0 | §6.3 |
| K8 | 3 + 3 isim çıkarılır; ≥ 30 isim | §6.3 |
| K9 | (−0,15; +0,15), %90 aralık | §6.3 |
| K10 | \|ρ̂\| ≤ 0,30 | §6.3 |
| K11 | δ_b = 0,30, %90 aralık, dört faktör | §6.3 |
| K3/K4 (rapor) | δ_P = %4/yıl birim | §6.3 |
| V3 | sıfır hafta payı ≤ %25; aktif ≥ 108/143; n_C < 10 | §6.1 |
| V4a, V4b | 0,10; 1,0 | §6.1 |
| V5 | 1e-12 | §6.1 |
| V2 | 1e-8 NAV | §5.5, §6.1 |
| V6 | ≤ %10 | §6.1 |
| V1 vol denetimi | 1e-9; τ = %15 | §6.1 |
| Sentetik fikstür (kapı koşusundan ayrı) | 10.000 tekrar, tohum 20260929 | §8.5 |
