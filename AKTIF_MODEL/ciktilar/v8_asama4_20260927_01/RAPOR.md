# v8 Aşama 4: sentez raporu

Tarih: 2026-09-27. Ön-kayıt: [ONKAYIT.md](ONKAYIT.md) (sha256 `b7077e34…`, iş akışından önce commit `38b3a95`).
Kararlar: [KARARLAR.md](KARARLAR.md). Çıktılar: [MIMARI.md](MIMARI.md),
[CARRY_KAPISI_ONKAYIT_TASLAK.md](CARRY_KAPISI_ONKAYIT_TASLAK.md), [BANKA_ONKAYIT_TASLAK.md](BANKA_ONKAYIT_TASLAK.md).
Geri test, veri hesabı ve performans ölçümü yapılmadı. Kapı ve banka **koşulmadı**. Ekonomik kabul **NOT_EVALUATED**.
Banka içeriği hiçbir belgede yok (sayı kontrolü #4 taraması).

**İşleyiş notu.** Bu bulut oturumunda Workflow aracı yoktu. Çok ajanlı akış, ön-kayıt §4'teki yapıyla ana oturumun
Agent aracıyla kuruldu. Toplam 10 ajan çalıştı: 8'i Opus (1 mimari, 2 sentezci, 2 kırmızı takım, 3 revizör), 2'si Sonnet
(sayı kontrolü, defter/rapor biçimi). Sonnet fikir elemedi, puanlamadı. Ajan istemleri `ajan_istemleri/` altında,
ara çıktılar `calisma/` altında. Her adım bitince commit'lendi.

---

## 1. Özet

- Aşama 4 bir **yazım ve tasarım** aşamasıdır: geri test, parametre taraması, yeni veri hesabı ya da indirme
  yapılmadı. Yeni hesap yok.
- Nihai mimari koşullu: carry uydusunun D içi ön-kayıtlı kapısı (henüz koşulmadı) geçerse **B** (trend +
  ω_C = 0,20 sabit carry uydusu), geçemezse **A** (yalnız trend). A ile B bankada yarışmaz (kullanıcı kararı,
  KARARLAR §1).
- Üç ön-kayıt taslağı hazır: `MIMARI.md`, `CARRY_KAPISI_ONKAYIT_TASLAK.md`, `BANKA_ONKAYIT_TASLAK.md`.
- İki bağımsız kırmızı takım turu tamamlandı: toplam 35 bulgu — 0 OLDURUCU, 18 CIDDI, 16 DUZELTILEBILIR,
  1 YOK. Bulguların işlenişi §7'de.
- Sayı ve iç tutarlılık kontrolü 82 iddiayı inceledi: 72 TUTARLI, 4 TUTARSIZ, 4 KAYNAKTA_YOK,
  2 HESAP_GEREKTIRIR. 4 TUTARSIZ bulgu ana oturumca düzeltildi (§8).
- Üç belgenin ön-kayıt kilit sırası (Adım 0–8, ortak adlarla) tekleştirildi; esas BANKA §1.2'dir.
- **Ön-kayıt §7'ye göre biçimsel kabul: KARŞILANDI.**
  - Üç taslak bağlayıcı kararlarla çatışmıyor. "Kapısız A" yalnız kullanıcıya soru olarak yazıldı.
  - OLDURUCU bulgu yok. Bütün CIDDI bulgular düzeltildi ya da gerekçeyle KISMEN kaldı (§7).
  - Açık TUTARSIZ yok (§8).
  - Banka içeriği yok.
- **En büyük karar yükü kullanıcıda:** 21 soru var (§9). Bunlar kilit adımı 1'de, D'de P&L üreten ilk koşudan önce yanıtlanmalı.
  En önemli üçü:
  - kapı mı, kapısız A mı (§10);
  - DSR çıtası ve deneme sayısı (soru 14 ve 21);
  - birim risk yorumu (soru 2).

---

## 2. Ne yapıldı

| Adım | Ajan | Model | Çıktı |
|---|---|---|---|
| 1 | Mimari sentezci | Opus | `calisma/MIMARI_v1.md` |
| 2a | Carry kapısı sentezci (MIMARI_v1'i okur) | Opus | `calisma/CARRY_KAPISI_v1.md` |
| 2b | Banka ön-kaydı sentezci (MIMARI_v1'i okur) | Opus | `calisma/BANKA_ONKAYIT_v1.md` |
| 3a | Kırmızı takım 1 (bakış-ileri, muhasebe, uygulanabilirlik, parite) | Opus | `calisma/KIRMIZI_1.md` (10 CIDDI, 0 OLDURUCU) |
| 3b | Kırmızı takım 2 (istatistik, ön-kayıt disiplini, banka sızıntısı, seçim serbestliği) | Opus | `calisma/KIRMIZI_2.md` (8 CIDDI, 0 OLDURUCU) |
| 4 | Üç sentezci revizyonu (her kırmızı takım bulgusu kabul/ret gerekçesiyle) | Opus | `MIMARI.md`, `CARRY_KAPISI_ONKAYIT_TASLAK.md`, `BANKA_ONKAYIT_TASLAK.md` |
| 5 | Sayı ve iç tutarlılık kontrolü | Sonnet | `calisma/SAYI_KONTROLU.md` |
| 6 | Deneme defteri satırı ve rapor biçim taslağı | Sonnet | `calisma/DEFTER_SATIRI.csv`, `calisma/RAPOR_BICIM.md` |

İki kırmızı takım birbirini görmedi. Ölçek: `OLDURUCU` / `CIDDI` / `DUZELTILEBILIR` / `YOK`.

---

## 3. Nihai mimari özeti (MIMARI.md, olgusal)

### 3.1 Bileşen tablosu (MIMARI §0)

| Bileşen | Kaynak tasarım | Neden |
|---|---|---|
| Trend sinyali (14/42/84, tanh, simetrik) | `codex` | En az serbestlik; 7 günlük pencere ve funding çarpanı yok |
| Sinyal normalizasyonu σ̂ = max(EWMA20, EWMA90), taban %20 | `risk` + `codex` tabanı | KARARLAR §2 "EWMA standart"; ısınmayı yemez |
| Evren: sıra tabanlı, BTC/ETH sabit, N=15, histerezis 15/20, taban 20M | `cta` | Nominal eşikten sağlam; öncelik kuralı var |
| PIT donma/delist ölçütleri; funding ölçütü mutlak 16 saat | `cta` + K1-01 | Aralık değişiminde sahte donma olmaz |
| Birim risk: tam sinyal referans kitabı ex-ante %15, yukarı çarpan ≤1,5 | `ml` k tanımı + `cta` M çarpanı | Zayıf sinyal büyütülmez |
| Σ̂ = 0,5·örnek + 0,5·(ρ=0,7) | `risk` / `ml` | Stres harmanı |
| Şok tavanları kaldıraç sonrası NAV'da, hedge kredisiz; hedef kitapta değişmez | `risk` + `codex` + K1-04 | KARARLAR §2 |
| Asimetrik isim tavanları (alt long %6, alt short %4) | `risk` | Yukarı sıçrama kuyruğu |
| İşlem bandı, sınıra işlem | `codex` | Devri düşürür |
| Katılım sınırı: 30g, 7g ve önceki saat hacminin en küçüğü; kısmi dolum adım katına | `codex` + `mikroyapi` + K1-05, K1-18 | Ölen coinde iyimser dolum olmaz |
| Maliyet: dilim + karekök etki, stres ×3; çarpan yalnız dilim + etkiye, ücret sabit | `cta` + KARARLAR §2 + K1-06 | Üç belgede tek tanım |
| Funding/dolum olay sırası; mark vekili = 1h kapanış; delistte tahakkuk durur | KARARLAR §2 + K1-02 | Hayali funding yazılmaz |
| Carry uydusu (FTN), sabit bütçe ω_C = 0,20; tavan çözücüsünde tek blok | `carry` + K1-09 | Tek bağımsız kol; nötrlük tavanlarla bozulmaz |
| σ̂ tahmincisi: EWMA; HAR yalnız QLIKE prosedürüyle, kilitten önce | `ml` çerçevesi | KARARLAR §2 |
| Felaket stopu (4 ATR, reduce-only) | `prop` | Yalnız canlı, operasyonel |

### 3.2 Ana sabitler

| Sabit | Değer |
|---|---|
| Trend ufukları | 14, 42, 84 gün |
| τ (birim risk) | %15 |
| M_max | 1,5 |
| N (trend evreni) | 15 (BTC/ETH + 13 alt) |
| Hacim tabanı (V60) | 20M USDT |
| Isınma | 90 gün, coin ve koşu başına |
| T0 (D değerlendirme başlangıcı) | 2023-10-01 00:00 UTC |
| İsim tavanları | BTC/ETH ≤%35; alt long ≤%6; alt short ≤%4 (B'de net %3,33) |
| Brüt tavan | Σ|w| ≤ 2,0 |
| S1 / S2 / S4 sınırı | %20 / %20 / %10 NAV |
| Band | max(%20·|w*|, %0,2 NAV) |
| Ücret | 5 bps (sabit) |
| ω_C (yalnız B) | 0,20 (sabit) |
| Carry isim tavanları | short ≤%1,0; long ≤%1,5 |
| Felaket stopu | 4 × ATR(14 gün), yalnız canlı |
| Serbestlik toplamı | A: 58; carry ek: +21; B: 79 |

---

## 4. Açık noktaların çözümü

Kaynak: `girdi/04_ANA_OTURUM_OZETI.md` (Codex jürisinin farklı gördükleri) ve `ASAMA4_ONKAYIT.md` §3. Karar ve
gerekçe MIMARI §1'den alıntıdır.

| Nokta | Ana oturum/Codex çelişkisi | Karar | Gerekçe (alıntı) |
|---|---|---|---|
| Trend çekirdeği: CTA mı Codex mi | Claude jürileri Codex sinyalini seçmişti; Codex kendi CTA benzeri çekirdeğini öneriyordu | **Codex iskeleti dondurulur** (h∈{14,42,84}, tanh, simetrik); CTA çekirdeği yalnız betimsel | MIMARI §1a: "İki çekirdek aynı hipotezi taşır... Seçim Sharpe'ı belirlemez; serbestlik derecesini ve uygulanabilirliği belirler." CTA'nın 7g penceresi kendi VR(5)<1 gerekçesiyle çelişir (görülmüş bilgi, K2-12) |
| Risk tahmincisi (HAR) | Codex basit başlangıç tahmincisi istiyor; Claude jürileri HAR'ı çekirdeğe koymuştu | **Başlangıç EWMA**; HAR yalnız bankadan önce, P&L'e bakmadan, QLIKE ile seçilip dondurulursa girer | MIMARI §1b: seçim prosedürü P&L'siz, ön-kayıtlı; bağlayıcı karar kuralı (i) ve (iv) |
| Carry bütçesi | Codex küçük/sabit uydu istiyor; otomatik %30–35 değil | **Tek, sabit, küçük ω_C = 0,20**; otomatik %30–35 yok | MIMARI §1d: "Değer D P&L'ine bakılarak seçilmedi; D'de carry P&L'i hesaplanmadı. Kapı sonucu ω'yı değiştirmez." |
| ML çıkış kuralı | Codex jürisi "öldürücü" (bakış-ileri) dedi; kırmızı takım CIDDI demişti | **Alınmaz**; yerine gerçekleşebilir ileri çıkış (donma → maskele → ilk işlem gören barda çık) | MIMARI §1c: "Hiçbir adım karar sonrasında geçmiş fiyata işlem yazmaz. Maske ≠ tasfiye." |
| A ve B bankada yarışır mı | Codex/kanıt jürisi/kırmızı takım: hayır, tek mimari dondurulmalı; kâr/uygulama jürisi: B−A ölçülsün | **Tek mimari bankaya gider** (kullanıcı kararı, KARARLAR §1); B seçilirse A'nın sonucu yalnız ayrıştırmadır | ONKAYIT §2: "Bankaya tek mimari gider... A ile B bankada yarışmaz." (Ana oturumun/kullanıcının kararı; sentez değiştirmedi) |

---

## 5. Carry kapısı özeti (CARRY_KAPISI_ONKAYIT_TASLAK.md)

**Amaç.** Carry uydusunun D'deki getirisinin funding mi fiyat mı kaynaklı olduğunu ayrıştırmak (§1). Kapı bir
**yanlışlama elemesidir**, kenar kanıtı değildir; gücü düşüktür (§8).

**Geçerlilik koşulları (biri sağlanmazsa sonuç A):** V1 (parite/bakış-ileri testleri), V2 (uzlaşma özdeşliği),
V3 (carry kitabı aktif hafta ≥108/143), V4 (icra artığının carry payı ≤%10).

### 5.1 Karar ölçütleri (§6.3; 2. tur revizyonu — K3/K4 artık bağlayıcı değil, aşağıya bkz.)

| Kod | Ölçüt | Eşik | n |
|---|---|---|---|
| K1 | Kredilenen net Sharpe (m_c=1, taban delist, fiyat kazancı kredilenmez) | SR^K ≥ **K1\*(ρ_üst) = 0,85·g(ρ_K1,1/3)**; ρ_K1 = gözlenen ρ'nun kırpılmış üst sınırı ∈[0;0,30]. Eşik 0,138–0,370 arası (sabit 0,10 değil; KC-07) | 143 hafta |
| K2 | Funding maliyeti anlamlı aşar | NW t ≥ 3,0 ve bootstrap %95 alt sınır > 0 | 143 hafta |
| K3 | *Bağlayıcı değil (KC-06).* Fiyat ortalaması eşdeğerliği (alt) | TOST, δ_P=%4/yıl; yalnız rapor — bağlayıcı rolü K1'in "fiyat kazancı kredilenmez" kuralına geçti | 143 hafta |
| K4 | *Bağlayıcı değil (KC-06).* Fiyat ortalaması eşdeğerliği (üst) | TOST, δ_P=%4/yıl; yalnız rapor | 143 hafta |
| K5 | Taşıma tutarlılığı | (r^F−r^C)>0 ay payı ≥ %75 | 33 ay |
| K6 | Maliyet 2× dayanıklılığı | SR^K(m_c=2) > 0 (kredilenmemiş fiyatla) | 143 hafta |
| K7 | Maliyet 3× dayanıklılığı | NW t ≥ 2,0 | 143 hafta |
| K8 | Tekil isim bağımlılığı | En iyi/kötü 3 isim çıkarılınca SR^K > 0 | ≥30 isim |
| K9 | Beta eşdeğerliği (KC-06) | β_BTC, β_alt için ayrı %90 GA ⊂ (−0,15;+0,15) | 143 hafta |
| K10 | Trend bağımsızlığı | |ρ̂(r^N,r^trend)| ≤ 0,30; bu ρ zaten K1\*'a girer | 143 hafta |
| K11 | Fiyat faktörü yüklemesi eşdeğerliği (KC-06) | 4 faktörün her biri için %90 GA ⊂ (−0,30;+0,30) | 143 hafta |

**Kapı tek atıştır** (ana deneme sayısı 1). Kör hüküm: denetim/hüküm/trend-mühür dosyaları ayrı yazılır ve
banka hükmüne kadar trend satırları açılmaz. Hüküm açıldıktan sonra bulunan hata sonucu yalnız **A**'ya
çevirebilir. **2. tur (KC-06) muhasebe düzeltmesi:** K3/K4'ün istatistiksel olarak bağlayıcı kılınması 33 ayda
ya imkânsız ya da anlamsızca gevşek bir tolerans gerektiriyordu; bunun yerine K1/K6/K8'in Sharpe hesabında
gözlenen fiyat KAZANCI artık kredilenmiyor (yalnız fiyat kaybı düşülüyor) — Codex'in ikinci doğrulama turu bunu
"muhafazakâr bir kabul ölçütü, fiyat nötrlüğünün kanıtı değil" diye onayladı (RAPOR §14).

Kapı koşulmadı; A/B seçimi bu koşuya bağlı. Kapı kilit adımı 5'tir, kilitten önce koşulamaz. Taslağın kendi güç analizi (§8): gerçek carry Sharpe'ı 0,3 iken yanlış ret olasılığı yüksek, K4'ün saptayabildiği en küçük fiyat bahsi net funding gelirinin 2–5 katı. Kapı zayıf bir yanlışlama elemesidir; bunu belge açıkça yazıyor.

---

## 6. Banka ön-kaydı özeti (BANKA_ONKAYIT_TASLAK.md)

**Tek mimari** M ∈ {A, B}, carry kapısının sonucuyla belirlenir; sonradan değişmez. B ise A'nın banka sonucu
hükme girmez. Aday sayısı m=1 (mühür "en fazla 3 aday"ın içinde). Hipotez: dondurulmuş M, birincil örneklemde
DSR ile düzeltilmiş pozitif Sharpe üretir.

**DSR (B2) — 2. tur revizyonu, kullanıcı kararıyla (ASAMA4B_KARAR §1 madde 2): tek sabit eşik DEĞİL.** N = 159
(REV1) + N_v8 (bugün 161, kilide kadar ≈325). σ_SR ve DSR eşiği kilit adımı 3'te, sentetik kalibrasyon ve REV1
kayıtlarıyla (D'ye bakılmadan) belirlenir; olası değerler σ_SR ∈ {0,20;0,30;0,50} için SR₀ ≈ {0,58;0,88;1,46}
(BANKA §3.3 duyarlılık tablosu, Codex'in canlı hesabıyla teyitli). Round-1'deki sabit "DSR≥0,50, σ_SR=0,30"
artık yalnız tablodaki bir satırdır, bağlayıcı varsayılan değildir.

### 6.1 Bağlayıcı ölçüt tablosu (§3.4, yalnız "B" türü)

| # | Ölçüt | Eşik |
|---|---|---|
| B2 | DSR | Kalibre edilecek (yukarı bkz.); sabit 0,50 değil |
| B3 | Maliyet stresi (×2, ×3 tam koşu) | ×2: SR ≥ 0,30; ×3: SR > 0 |
| B4 | En iyi yıl hariç | SR ≥ 0,30 |
| B5 | En iyi 3 epizot payı | < e_B5 (sentetik kalibrasyonla sabitlenir) |
| B6 | Rejim dilimleri (4 dilim) | ≥ k_B6 dilimde SR > 0, k_B6 ∈ {2,3} |
| B7 | Rejim-null | SR̂ > null q90 (ayar kuralına göre q95 olabilir) |
| B8 | Fiyat bileşeni (funding hariç, maliyet dahil) | SR > 0 |
| B9 | Görülmemiş coinler (K-evren, yalnız görülmemiş zaman) | SR > 0 |
| B10 | Tek coin çıkarma (en büyük 10, tek tek) | En büyük SR düşüşü < e_B10 |
| B11 | DD biçimi (%15 vol'e ölçekli) | MDD ≤ %30 |

Rapor-only (R) ölçütler: R1 NAV×maliyet ızgarası, R2 beta ayrıştırması, R8 (yalnız B) A ayrıştırması ve carry
bacak satırları, R11 eski B1, R12 eski −%90 delist senaryosu, R16 DSR duyarlılığı vb. — tam liste BANKA §3.4.

**Hayatta kalan yanlılığı** açıkça yazılır (§5); D90 (−%90 delist) senaryosu **rapordur**, bağlayıcı değildir
(az olay ilkesi). Kör hüküm ve hüküm-sonrası hata kuralları §2.4–2.5'te.

Banka koşulmadı; DONDURMA yapılmadı.

**Ana oturum notu (deneme sayısı) — KAPANDI (§15, Soru 21).** Banka taslağı defterdeki `A2-mikroyapi` satırını
144, `A2-ml` satırını 5 deneme sayıyor (kaynak: kanıt jürisinin "~144 hücre" notu, ML'nin 5 tahmin modeli). Ana
oturum bu sayımı kabul etti ve `V8_DENEME_DEFTERI.csv`'yi buna göre güncelledi; bugünkü N_v8 = 161. σ_SR ve DSR
çıtası artık sabit değil, yukarıdaki kalibre edilmiş tabloya göre kilit adımı 3'te belirlenecek.

---

## 7. Kırmızı takım bulgularının işlenişi

Kaynak: `MIMARI.md` §13, `CARRY_KAPISI_ONKAYIT_TASLAK.md` §14, `BANKA_ONKAYIT_TASLAK.md` Ek C. "Karar" sütunu
her belgenin kendi tablosundaki değerdir (DUZELTILDI / KISMEN / ilgisiz).

| Bulgu | Düzey | MIMARI karar | CARRY karar | BANKA karar |
|---|---|---|---|---|
| K1-01 | CIDDI | DUZELTILDI | KISMEN | ilgisiz |
| K1-02 | CIDDI | DUZELTILDI | KISMEN | KISMEN |
| K1-03 | CIDDI | DUZELTILDI | ilgisiz | ilgisiz |
| K1-04 | CIDDI | DUZELTILDI | KISMEN | DUZELTILDI |
| K1-05 | CIDDI | DUZELTILDI | KISMEN | ilgisiz |
| K1-06 | CIDDI | DUZELTILDI | DUZELTILDI | DUZELTILDI |
| K1-07 | DUZELTILEBILIR | DUZELTILDI | ilgisiz | ilgisiz |
| K1-08 | DUZELTILEBILIR | DUZELTILDI | ilgisiz | DUZELTILDI |
| K1-09 | CIDDI | DUZELTILDI | DUZELTILDI | KISMEN |
| K1-10 | DUZELTILEBILIR | DUZELTILDI | KISMEN | ilgisiz |
| K1-11 | DUZELTILEBILIR | DUZELTILDI | ilgisiz | KISMEN |
| K1-12 | DUZELTILEBILIR | DUZELTILDI | KISMEN | ilgisiz |
| K1-13 | CIDDI | DUZELTILDI | DUZELTILDI | DUZELTILDI |
| K1-14 | CIDDI | KISMEN | ilgisiz | DUZELTILDI |
| K1-15 | DUZELTILEBILIR | ilgisiz | ilgisiz | DUZELTILDI |
| K1-16 | DUZELTILEBILIR | ilgisiz | ilgisiz | DUZELTILDI |
| K1-17 | DUZELTILEBILIR | DUZELTILDI | ilgisiz | ilgisiz |
| K1-18 | CIDDI | DUZELTILDI | KISMEN | KISMEN |
| K1-19 | DUZELTILEBILIR | DUZELTILDI | ilgisiz | ilgisiz |
| K1-20 | DUZELTILEBILIR | KISMEN | KISMEN | KISMEN |
| K2-01 | CIDDI | DUZELTILDI | DUZELTILDI | DUZELTILDI |
| K2-02 | CIDDI | ilgisiz | KISMEN | KISMEN |
| K2-03 | CIDDI | KISMEN | KISMEN | KISMEN |
| K2-04 | CIDDI | ilgisiz | ilgisiz | DUZELTILDI |
| K2-05 | CIDDI | ilgisiz | ilgisiz | KISMEN |
| K2-06 | CIDDI | ilgisiz | ilgisiz | DUZELTILDI |
| K2-07 | CIDDI | ilgisiz | DUZELTILDI | DUZELTILDI |
| K2-08 | CIDDI | DUZELTILDI | ilgisiz | DUZELTILDI |
| K2-09 | DUZELTILEBILIR | ilgisiz | KISMEN | DUZELTILDI |
| K2-10 | DUZELTILEBILIR | DUZELTILDI | ilgisiz | ilgisiz |
| K2-11 | DUZELTILEBILIR | KISMEN | DUZELTILDI | ilgisiz |
| K2-12 | DUZELTILEBILIR | DUZELTILDI | KISMEN | KISMEN |
| K2-13 | DUZELTILEBILIR | ilgisiz | ilgisiz | DUZELTILDI |
| K2-14 | DUZELTILEBILIR | ilgisiz | ilgisiz | DUZELTILDI |
| K2-15 | YOK | ilgisiz | ilgisiz | — |

**Sayım:** 35 bulgu (20 K1-serisi + 15 K2-serisi). 0 OLDURUCU, 18 CIDDI, 16 DUZELTILEBILIR, 1 YOK.
Adım 4 kuralı gereği (ONKAYIT §4): "Adım 4'te `OLDURUCU` ve `CIDDI` bulguların hepsi ya düzeltilir ya
gerekçeyle reddedilir." Tabloda hiçbir CIDDI/OLDURUCU bulgu boş bırakılmamış; hepsi en az bir belgede
DUZELTILDI ya da gerekçeli KISMEN.

**Ana oturum değerlendirmesi: KISMEN kalan CIDDI bulgular.**

| Bulgu | Neden KISMEN | Yeterli mi |
|---|---|---|
| K1-14 rejim-null bayrakları | MIMARI yalnız arayüz ekledi (§5.1 dış bayrak modu). Bayrakların karıştırılan blokla taşınması BANKA §3.5'te tanımlandı. | Evet: kural BANKA'da tam; MIMARI yalnız giriş sağlıyor. |
| K2-02 kapı fiyat bileşenini ayıramıyor | K11 (4 faktörlü Wald testi) eklendi. Güç sınırı sayıyla yazıldı. Kalan boşluk verinin gücü; belgeyle kapanmaz. | Evet, kullanıcı sorusuyla (soru 8). |
| K2-03 carry'nin bankada seyreltmesi | K1 eşiği başabaşa (0,10) çekildi. "Kapısız A" sayılarla kullanıcıya soruldu. Bağlayıcı karar gereği ana kural değişmedi. | Evet; karar kullanıcıda (§10). |
| K2-05 banka ölçütleri kalibre değil | B5, B6 ve B10 eşikleri kilitten önce sentetik Monte Carlo ile sabitlenecek; hedef, gerçek SR=0 iken kabul olasılığı ≤ %5. B1 rapora indi. | Evet, koşullu: kalibrasyon kilit adımı 3'te yapılmadan kilit kurulamaz. |

**Ana oturumun ayrıca bulduğu ve düzelttiği tutarsızlık.** Sayı kontrolü bunu kaçırmıştı.
- Revizörler kilit sırasını üç belgede farklı yazmıştı:
  - HAR seçimi CARRY'de kilitten sonra geliyordu.
  - Sentetik kalibrasyon yalnız BANKA'daydı.
  - Mühürlü D performans çıktılarının açılışı MIMARI ve CARRY'de "dondurmada", BANKA'da "banka hükmünden sonra" idi.
- Üçü BANKA §1.2'deki 0–8 sırasına ve "banka hükmünden sonra açılır" kuralına getirildi. Bu, en sıkı seçenekti.
- Düzeltme öncesi kopyalar `AKTIF_MODEL/_arsiv/V8_ASAMA4_SENTEZ_20260927_01/uyumlama_oncesi/` altında.

---

## 8. Sayı kontrolü sonucu

Kaynak: `SAYI_KONTROLU.md` (Adım 5, Sonnet, mekanik). 82 iddia incelendi:

| Etiket | Sayı |
|---|---|
| TUTARLI | 72 |
| TUTARSIZ | 4 |
| KAYNAKTA_YOK | 4 |
| HESAP_GEREKTIRIR | 2 |

**4 TUTARSIZ bulgu ve ana oturumun düzeltmesi:**

1. `CARRY_KAPISI_ONKAYIT_TASLAK.md` §6.6 eski adı "B12" kullanıyordu → **R12** ile değiştirildi (BANKA §0(4),
   §3.4 ile tutarlı hale getirildi).
2. `MIMARI.md` §3.5/§7 S1 gerekçesi "10/10 fitili −%67; ETH −%27,5" iki farklı satırı (10/10/2025 alt medyanı
   ve ayrı bir "en kötü gün" ETH değeri) tek olaya atfediyordu → **ETH −%22 (10/10/2025), −%27,5 ayrı "en kötü
   gün" olarak** ayrıştırıldı.
3. `BANKA_ONKAYIT_TASLAK.md` §5.3 "vol %8–11" diyordu; `MIMARI.md`/`CARRY_KAPISI_ONKAYIT_TASLAK.md` "%7–11"
   diyordu → **%7–11**'e düzeltildi.
4. `CARRY_KAPISI_ONKAYIT_TASLAK.md` §6.2 "ℓ=12 ≈ 90 gün" diyordu (12×7=84) → **84 gün**'e düzeltildi.

**KAYNAKTA_YOK (4) ve HESAP_GEREKTIRIR (2) kalemleri** bağlayıcı bir çelişki değildir; verilen `girdi/`
kümesinde doğrudan doğrulanamayan sayılardır. Ana oturum dördünün kaynağını buldu:
- "144 hücre": `JURI_RAPORU` 2/2, kanıt jürisinin mikroyapı notu.
- "4'ü −%41…−%56": `tasarim_carry.md`.
- "20M taban": `tasarim_cta.md`, "Mutlak taban 20M USDT".
- "51 sabit": `calisma/MIMARI_v1.md` §7.

HESAP_GEREKTIRIR iki kalem N'nin bileşimidir; bu bölümdeki deneme sayısı notuna bağlanır.

**Ayrıca:** üç belgenin ön-kayıt kilit sırası (Adım 0–8, ortak
adlarla) tek sıraya getirildi; esas `BANKA_ONKAYIT_TASLAK.md` §1.2'dir. `MIMARI.md` §10 ve
`CARRY_KAPISI_ONKAYIT_TASLAK.md` §2 aynı adım adlarını kullanır.

---

## 9. Kullanıcıya sorular

Üç belgedeki açık sorular birleştirildi, tekrarlar tek satırda toplandı, kaynakları belirtildi. Ana oturum 21. soruyu ekledi. Hepsi
**Adım 1'de, D'de P&L üreten ilk koşudan önce** yanıtlanacaktır (ortak kilit sırası, §8).

| # | Soru | Varsayılan (belgedeki) | Kaynak |
|---|---|---|---|
| 1 | Kapı mı, kapısız A mı? | (a) mevcut karar: kapı → A/B | MIMARI §9.7/§11; CARRY §13.1/§12; BANKA §11.5/§9 |
| 2 | Birim risk yorumu: tam sinyal referans kitabı mı (önerilen), yoksa gerçek kitabı %15'e getiren, zayıf sinyali ≤1,5 kata büyüten çarpan mı? | Birinci (referans kitap) | MIMARI §9.1 |
| 3 | DD çarpanı çekirdeğe alınmadı, %30 sınırı kaldıraç seçimine bırakıldı — kabul mü? | Kabul (DD çarpanı yok) | MIMARI §9.2 |
| 4 | Birincil NAV 0,1M USDT olarak dondurulsun mu? (canlı demo ~5.000 USDT) | 0,1M | MIMARI §9.3; BANKA §11.10 |
| 5 | Sembol filtresi için kamu `exchangeInfo` tek anlık görüntüsüne onay | Onay bekleniyor | MIMARI §9.4; BANKA §11.8 |
| 6 | REV1'in D dönemi günlük getiri serisi v8 değerlendiricisine (R4 korelasyon raporu için) verilebilir mi? (E3 Z2 verisi yasak kalır) | Yanıt bekleniyor | MIMARI §9.5; BANKA §11.6 |
| 7 | S4 yalnız B'de mi kalsın, A'ya da uygulansın mı? (uygulanırsa A'da alt short tavanı %4→%3,33) | Yalnız B | MIMARI §9.6 |
| 8 | Kapının funding/fiyat ayrıştırması kullanıcı kararındaki tanımı karşılıyor mu? (K4 ancak net funding gelirinin 2–5 katı fiyat bahsini görür) | Yanıt bekleniyor | CARRY §13.2 (K2-02) |
| 9 | K1 eşiği: 0,10 (başabaş) mı, v1'deki 0 mı? | 0,10 | CARRY §13.3 |
| 10 | K2 eşiği: 3,0 mı 2,0 mı? | 3,0 | CARRY §13.4 |
| 11 | Netleme kazancının carry'ye yazılmaması (muhafazakâr seçim) kabul mü? | Kabul | CARRY §13.5 |
| 12 | Delist senaryolarının (D90) bağlayıcı olmaması kabul mü? | Kabul (rapor) | CARRY §13.6; BANKA §11.4 |
| 13 | Kapı NAV'ının banka birincil NAV'ına bağlı olması kabul mü? | Kabul | CARRY §13.7 |
| 14 | DSR eşiği 0,50 mi (fiilî çıta SR̂≈0,88), jüri önerisi 0,90 muydu? | 0,50 | BANKA §11.1 |
| 15 | Birincil örneklem yalnız Z1 mi (Z2 yalnız teşhis)? | Onaylanıyor (yalnız Z1) | BANKA §11.2 |
| 16 | Z2_son = 2026-09-24 00:00 UTC doğru mu? | Doğru kabul edildi | BANKA §11.3 |
| 17 | Değerlendirici: tasarıma katılmamış yeni oturum mu; Codex'in içerik görmeden hash yeniden üretimi istensin mi? | Yanıt bekleniyor | BANKA §11.7 |
| 18 | Kelly ızgarası {0,5; 1; 1,5; 2; 2,5; 3; 4} yeterli mi? | Yeterli kabul edildi | BANKA §11.9 |
| 19 | Şifreleme: kullanıcının age (X25519) anahtar çifti üretip açık anahtarı DONDURMA'ya vermesi kabul mü? | Kabul | BANKA §11.11 |
| 20 | Kısa ömürlü 20 coin konusu yeniden açılırsa ayrı ön-kayıt gerekir (bilgi amaçlı, karar gerekmez) | — | BANKA §11.12 |
| 21 | Deneme sayısı: `A2-mikroyapi` 144, `A2-ml` 5 deneme mi sayılsın (N ≈ 323, çıta ≈ 0,88), yoksa satır başına 1 mi (N ≈ 180, çıta ≈ 0,82)? | Taslak: 144 ve 5 | Ana oturum (§6 notu); BANKA §3.3 |

Yanıtlar kilit adımı 1'de `ACIK_SORU_YANITLARI.md`'ye yazılır ve kilitle birlikte hash'lenir. Yanıt verilmeyen soruda belgedeki varsayılan geçerlidir.

---

## 10. KARAR_DEGISIKLIGI_ONERISI'leri

Tek öneri, üç belgede de aynı konudadır ve **bağlayıcı kararı (ONKAYIT §2: kapı → A/B) değiştirmez**:

- **"Kapısız A" seçeneği** (K2-03 kaynaklı). Gerekçe: kapının gücü düşük (33 ayda carry'nin kenarı ile sıfır
  ayrılamaz); B bankada bütün olarak yargılanır ve kötü bir carry, çıtaya yakın bir trendin banka kabul
  olasılığını ~8–10 puan düşürebilir (MIMARI §11; CARRY §12; BANKA §9).
  - (a) Mevcut karar: kapı → A/B (varsayılan).
  - (b) Kapısız A: carry bu bankaya hiç gitmez; ayrı hipotez olarak ileri dönemde sınanır. **Kullanıcı
    kararının değişmesini gerektirir.**
  - (c) Kapı kalır; K1 eşiği ya da ω_C, bankadaki seyreltmeyi karşılayacak biçimde yeniden ayarlanır.
- Diğer tüm KARAR_DEGISIKLIGI_ONERISI alanları "Yok" ya da "ilgisiz" olarak işaretli (MIMARI §13 özet;
  CARRY §14; BANKA Ek B özet). KARARLAR §2'deki teknik kararların hiçbiri bu revizyonla değişmedi.

Seçim kullanıcınındır; varsayılan (a). Ana oturumun gözlemi: (b) yalnız bu bankada carry'yi bırakır. Carry ileri dönemde ayrı hipotez olarak sınanabilir. (a)'nın bedeli K2-03'ün seyreltme aritmetiğidir; kazancı carry'nin gerçekten pozitif olduğu durumdur. İki yol da ön-kayıt disiplinine uygun.

---

## 11. Sonraki adım

Kaynak: `ONKAYIT.md` §7–§8, `MIMARI.md` §10 (ortak kilit sırası).

> "Aşama sonunda durulur ve kullanıcıyla değerlendirilir. Codex isterse taslaklara dış kırmızı takım olabilir;
> paket kullanıcıyla aktarılır. Bu isteğe bağlıdır." (ONKAYIT §7)

Ortak ön-kayıt kilidi sırası (üç belgede aynı adlar, henüz hiçbiri koşulmadı):

| Adım | İş | P&L görülür mü |
|---|---|---|
| 0 | Motor yazımı; sentetik fikstürlerle parite/bakış-ileri/muhasebe testleri | Hayır |
| 1 | Açık soruların yanıtlanması (§9 tablosu) → `ACIK_SORU_YANITLARI.md` | Hayır |
| 2 | HAR/EWMA seçimi (MIMARI §1b, QLIKE, P&L'siz) | Hayır |
| 3 | Sentetik kalibrasyon (BANKA §3.7; D/banka verisi kullanmaz) | Hayır |
| 4 | **ÖN-KAYIT KİLİDİ** (`KILIT.json`); deneme defterine kapı satırı girer | Hayır |
| 5 | Carry kapısı koşusu — D'de ilk P&L üreten koşu; sonuç A/B | Yalnız kapı ölçütleri |
| 6 | D doğrulaması ve banka kuru koşusu — performans çıktıları mühürlü | Hayır (yalnız hash) |
| 7 | Banka dondurması (`DONDURMA.json`, kullanıcı onayı "dondur") | Hayır |
| 8 | Banka açılışı — tek atış, kör denetim, hüküm | Evet |

**Bu aşamanın hemen sonraki adımı:** kullanıcı değerlendirmesi (§9 sorularının yanıtı ve §10 seçimi), ardından
Adım 0 (motor yazımı ve sentetik fikstür testleri). Motor yazımı ve D içi doğrulama/banka koşusu bu aşamanın
kapsamı dışındadır (ONKAYIT §1).

**Bu aşamanın açık kalanları (ana oturum):**
- Deneme defterine `A4-sentez` satırı eklendi (varyant 0).
- DURUM.md kısa güncellendi.
- **Codex dış kırmızı takımı (kullanıcı istedi, 27 Eylül):** paket [CODEX_KIRMIZI_TAKIM_PAKETI.md](CODEX_KIRMIZI_TAKIM_PAKETI.md). Codex nihai üç taslağa saldırır; bağımsızlık için Claude kırmızı takım raporlarını, `calisma/` klasörünü ve bu raporu okumaz. S-a–S-d kullanıcı sorularına da görüş verir. Çıktı `CODEX_KIRMIZI_TAKIMI.md` olur. Aktarımı kullanıcı yapar. Codex çıktısı gelince ana oturum bulguları işler; gerekirse taslaklar revize edilir.

Aşama burada durur. Adım 0'a (motor yazımı) geçiş kullanıcı değerlendirmesinden sonradır.

---

## 12. Codex dış kırmızı takımı (27 Eylül, sonradan eklendi)

Kaynak: [CODEX_KIRMIZI_TAKIMI.md](CODEX_KIRMIZI_TAKIMI.md) (commit `b228152`, kullanıcı aktardı). Codex nihai üç taslağı
Claude kırmızı takım raporlarını görmeden inceledi. Körlük tam değil: DURUM.md'yi ve defteri okudu, orada önceki kırmızı
takımların toplu sayıları vardı. Codex bunu kendisi beyan etti.

**Sayım:** 14 bulgu: 1 OLDURUCU, 12 CIDDI, 1 DUZELTILEBILIR. **Codex'in hükmü: "Adım 4 kilidine hazır değil."**

| Bulgu | Düzey | Konu | "DUZELTILDI" iddiasını çürütüyor mu |
|---|---|---|---|
| KC-01 | OLDURUCU | Rejim-null (B7): blokların fiyat zincirleme, yeniden bazlama ve yaşam döngüsü kuralları tanımsız; null dağılımı tek bir nesne değil | K1-14, K2-14 |
| KC-02 | CIDDI | Sentetik kalibrasyon üretecinde serbestlik (epizot genliği, gürültü, β, κ); sorular kalibrasyondan önce isteniyor | — |
| KC-03 | CIDDI | Kapı ile mimari farklı carry miktarını ölçüyor (günlük κ ile %25 bant; sıfır/sıfır artık payı 0 ile 0,5) | K1-09, K2-11 |
| KC-04 | CIDDI | BTC hedge'i isim kırpmasından önce hesaplanıyor; tavan ve bant sonrası nötrlük bozuluyor | K1-09 |
| KC-05 | CIDDI | V4 zıt işaretli artıkları birbirine siliyor | K2-11 |
| KC-06 | CIDDI | Anlamsızlık nötrlük kanıtı değil; K3/K4/K11 eşdeğerlik testi olmalı | — |
| KC-07 | CIDDI | K1 = 0,10 başabaşı yalnız ρ = 0 için; K10'un izin verdiği ρ = 0,3'te başabaş ≈ 0,37 | K2-03 |
| KC-08 | CIDDI | σ_SR = 0,30 doğrulanmamış; DSR ≥ 0,50 "olasılıksal kanıt" değil, performans çıtası | K2-04 |
| KC-09 | CIDDI | T4'teki V ≤ τ değişmezi kaldıraçlı hedefte yanlış okunuyor; geçerli Kelly koşusu teknik geçersiz sayılabilir | K1-11 |
| KC-10 | CIDDI | %30 DD sınırını aşan L'nin seçilmesini önleyen kural yok | K2-08 |
| KC-11 | CIDDI | D90 yalnız long çöküşünü kapsıyor; short sıkışması ve çoklu ölüm stresi yok | K2-13 |
| KC-12 | CIDDI | Haftalık carry miktarı ve kaçırılan karar yalnız piyasa verisinden yeniden üretilemez; devreden emir kuralları çelişiyor | K1-17 |
| KC-13 | CIDDI | Çift bazlı korelasyon matrisi PSD olmayabilir; vol'ün karekökü tanımsız kalır | — |
| KC-14 | DUZELTILEBILIR | "Referans kitap her gün %15" ifadesi M_max ile çelişiyor (N = 15'te ≈ %14,1) | — |

**Ana oturum doğrulaması (elle aritmetik):**
- KC-07: √(1 + 1/9 + 2·0,3/3) = 1,145, dolayısıyla başabaş ≈ 0,85·0,145·3 ≈ 0,37. Doğru.
- KC-13: verilen R ve v için vᵀRv = −0,15. Doğru.
- KC-14: 1ᵀR̂1 = 88,5, M ≈ 1,59, referans vol ≈ %14,1. Doğru.

**Değerlendirme.**
- Claude kırmızı takımları ve revizyonlar 9 bulguda "DUZELTILDI" demişti; Codex bunların kapanmadığını gösterdi.
- Ön-kayıt §7'nin kabul koşulu ("OLDURUCU ve CIDDI bulgular kapatılmış") Codex bulgularıyla **artık karşılanmıyor**.
- Taslaklar kilide gitmeden bir revizyon turu gerekir.

**Kullanıcı sorularında Codex'in görüşü:**
- S-a: **(b) kapısız A.**
- S-b: 144 ve 5 sayılsın. Ham araştırma kapsamı ile etkin sayı ayrılmalı; N_A = 323, N_B = 324.
- S-c: 0,50 / 0,30 doğrulanmış bir DSR kapısı değil. Olasılıksal kanıt isteniyorsa DSR ≥ 0,95; σ_SR önceden gerekçelendirilmeli.
- S-d: Referans kitap, ama hedefin çarpan ve tavanlarla koşullu olduğu açık yazılmalı.

**Önerilen sonraki adım:** Aşama 4 revizyon turu (4b).
- Kullanıcı önce S-a'yı yanıtlar. Kapısız A seçilirse KC-03…KC-07 ile KC-12'nin carry kısmı kapsamdan çıkar.
- Opus revizörler kalan bulguları kapatır; bir kırmızı takım yeniden sınar.
- Codex isterse ikinci tur dış kontrol yapar.

---

## 13. Codex'e canlı danışma: S-a ve S-c netleşti (27 Eylül, yerel oturum, `codex exec`)

Yerel Claude Code oturumu, CODEX_YEREL_AJAN.md kuralıyla Codex'i `codex exec -s read-only --ephemeral` ile
doğrudan çağırdı ve §12'deki S-a/S-c görüşlerini netleştirmesini istedi. İstem ve yanıt
`codex_cagrilari/20260927T_saclik_{istem,yanit}.md` içinde (sha256 `f3e369ac…`, `138cfd28…`).

**Codex kendi önceki görüşünü geri çekti — ikisi de yumuşadı:**

- **S-a (kapısız A): artık ısrar etmiyor.** "Kapısız A'da ısrar etmiyorum... D'deki kapı geliştirme/seçim
  işlemidir, bağımsız OOS kanıtı değildir." Düzeltilmiş bir kapı (KC-03/04/05/06/07 kapatılmış) kabul edilebilir;
  kullanıcının 27 Eylül kararı (kapı → A/B) korunabilir. Öncelik sırasıyla üç düzeltme:
  1. Tek sanal defter + günlük κ + kırpma/bant/maske sonrası hedge (KC-03/04/05);
  2. Anlamsızlık yerine önceden dondurulmuş ekonomik eşdeğerlik toleransı (KC-06);
  3. K1 eşiğinin, kapının izin verdiği korelasyon aralığıyla (ρ=0,30'da başabaş ≈0,37) tutarlı gerekçelendirilmesi (KC-07).
- **S-c (DSR ≥ 0,95): geri çekildi.** "Kalibrasyondan bağımsız bağlayıcı 0,95 önerimi geri çekiyorum." Hesabını
  gösterdi: N≈323, süre≈3,2 yıl ile SR₀≈0,876, SE≈0,559; DSR≥0,95 ⇒ SR̂≥1,80 (A'nın 0,3–0,6 canlı bandının çok
  üstünde; gerçek SR=0,45 civarında geçme olasılığı ~%0,4–1,6, yani fiilen imkânsıza yakın). Asıl önerisi:
  σ_SR={0,20;0,30;0,50} için ayrı DSR çıtası ({1,50;1,80;2,38}) **duyarlılık olarak** verilsin; hangi sonucun
  bağlayıcı olacağı, DSR'nin yalnız raporlanıp raporlanmayacağı **banka açılmadan** kalibre edilsin. Taslağın
  σ_SR=0,30 sabit / DSR≥0,50 yaklaşımıyla aynı yönde: sabit tek eşik yerine kalibrasyon.

**Sonuç:** S-a ve S-c artık RAPOR §9/§12'deki "kullanıcı kararı gerekir, Codex'in görüşü şuydu" biçiminden
çıktı; ikisi de "düzeltilmiş/kalibre edilmiş hâliyle kabul edilebilir" yönünde birleşti. Kalan karar hâlâ
kullanıcının: (a) kapı → A/B mi kalsın (evet görünüyor), (b) DSR tek bağlayıcı sabit eşik mi yoksa kalibre
edilmiş duyarlılık tablosu mu olsun.

---

## 14. Aşama 4b: revizyon turu, tutarlılık düzeltmesi ve ikinci Codex doğrulaması (27 Eylül, yerel oturum)

**Kullanıcı kararları** (ASAMA4B_KARAR.md): (1) kapı → A/B kalır, kapısız A seçilmedi. (2) DSR tek sabit eşik (0,50)
değil; kalibre edilmiş σ_SR duyarlılık tablosu, hangi sayının bağlayıcı olacağı Adım 3'te (D'ye bakılmadan) kilitlenir.

**Üç Opus revizörü** (paralel), Codex'in 14 bulgusunu (1 OLDURUCU, 12 CIDDI, 1 DÜZELTİLEBİLİR) kapattı: 14/14 işlendi,
boşluk yok. Öne çıkanlar:
- **KC-01 (OLDURUCU, rejim-null):** BANKA §3.5 tamamen yeniden yazıldı — karıştırma artık getiri uzayında (ham fiyat
  değil), yaşam döngüsü Y1–Y3 ile listelenme/ölüm korunur, evren/maske sentetik yoldan günlük yeniden hesaplanır.
- **KC-04 (BTC hedge sırası):** Hedge artık kırpma/bant/maske SONRASI gerçek alt sepetine göre yeniden kuruluyor.
- **KC-13 (korelasyon matrisi PSD değil):** Özdeğer kırpmasıyla PSD garantisi eklendi.
- **KC-03/05/06/07 (carry kapısı):** Tek sanal defter, düzeltilmiş V4 tanımı, K3/K4 fiyat testleri için **bilinçli bir
  sapma** — bağlayıcı istatistiksel eşdeğerlik testi yerine muhafazakâr muhasebe (fiyat kazancı kredilenmez, yalnız
  kayıp düşülür); gerekçe: 33 ayda ekonomik anlamlı bir toleransla TOST ya geçilemez ya da anlamsızca gevşek olur.
  K1 eşiği artık korelasyona bağlı formül: K1\* = 0,85·g(ρ_K1, 1/3), ρ∈[0;0,30]'da 0,138–0,370 arası.
- **KC-08/DSR:** Kullanıcı kararı uygulandı; sayısal duyarlılık tablosu Codex'in canlı hesabıyla birebir eşleşiyor.
- **KC-09/10/11 (T4, Kelly-DD kuralı, D90 kapsamı):** T4 dört nesneye ayrıldı, %30 DD sınırını aşan L artık
  önerilebilir kaldıraç kümesinden otomatik dışlanıyor, D90'ın yalnız long-çöküş kanalını kapsadığı açıkça yazıldı.

**Ana oturumun tutarlılık geçişi (üç paralel revizör arası arayüz kontrolü):**
- **Gerçek hata:** MIMARI ve BANKA'nın T4-a/b/c/d harfleri ters düşüyordu (MIMARI b=carry birim/c=carry blok,
  BANKA b=net hedef/c=carry birim) ve BANKA, MIMARI'nin yeni eklediği "toplam risk kuralı"nı (V(w*)≤L·(1+ω_C·1_B)·τ)
  hiç içermiyordu — "ayrı bir tavan yoktur" diyordu. Düzeltildi: BANKA artık MIMARI'nin dört nesnesini birebir aynı
  harflerle kullanıyor (T4-a/b/c/d), muhasebe ve null kendi T4-e/f'sinde. round-1 nihai kopyalar
  `_arsiv/V8_ASAMA4_SENTEZ_20260927_01/round1_nihai/`'de.
- **Sayısal netleştirme:** MIMARI §1d ve BANKA §9'daki "sıfır Sharpe'lı carry bile trendi ~%16 seyreltir" hesabı
  ρ=0 varsayıyordu; K1*'ın izin verdiği ρ=0,30 üst sınırında gerçek seyreltme başabaşı ≈%37'dir. Her iki belgeye
  bu ayrımı netleştiren tek satır eklendi (iki farklı sayı, iki farklı amaç: portföy bütçesi vs. kapı eşiği).
- **Kontrol edilip sorun bulunmadı:** MIMARI'nin CTA/DD ablasyonu bankaya artık önerilmiyor (KC-08 ile zaten
  tutarlı); "dış bayrak modu" (MIMARI §5.1) BANKA tarafından bilinçli ve gerekçeli biçimde kullanılmıyor (opsiyonel
  bırakılmıştı); ısınma kuralı (§2.4) MIMARI'de zaten sürekli-koşu diliyle güncellenmişti.

**İkinci Codex doğrulaması (`codex exec`, canlı, aynı gün).** İstem/yanıt: `codex_cagrilari/20260927T2_dogrulama_{istem,yanit}.md`
(sha256 `839295ee…`, `a7b6e94e…`). Üç soruya yanıt:
- **KC-01 (rejim-null):** Orijinal karşı örneği artık geçerli değil onayladı. Ama **yeni bir CIDDI bulgu** verdi:
  Y1 ("bar saatleri kümesi aynı") ile "yaşam içi boşluklar bloğuyla taşınır" kuralı kendi içinde çelişiyordu — bir
  boşluk farklı bir sentetik konuma taşınırsa N3'ün "tam saat kümesi aynı" iddiası bozulurdu. **Ana oturum
  düzeltti:** Y1/N3 artık yalnız toplam bar SAYISI ve giriş/çıkış saatlerinin korunduğunu iddia ediyor; boşluğun
  hangi tam saatte göründüğü korunmuyor (bu kasıtlı ve zararsız — sayı ve kesitsel eş hareket korunuyor).
- **T4 (KC-09):** "Tutarlı, kritik belirsizlik yok" dedi; küçük bir netleştirme istedi (tavan uyumu VE toplam risk
  kuralının BİRLİKTE arandığı, biri diğerinden muafiyet vermediği) — eklendi.
- **K3/K4 muhasebe sapması (KC-06):** "Muhafazakâr bir kabul ölçütü olarak kabul ediyorum, fiyat nötrlüğünün kanıtı
  olarak değil" dedi; riskin tamamen giderilmediğini (yalnız gözlenen fiyat kazancına kredi kaldırıldığını) not
  düştü — belge zaten bu ayrımı yapıyor, ek değişiklik gerekmedi.

**Kalan iki açık, kullanıcıya bilgi amaçlı (karar gerekmiyor, revizörlerin gerekçeli seçimleri):**
1. CARRY revizörünün K3/K4 için TOST yerine muhafazakâr muhasebe seçmesi (yukarıda), Codex'in ikinci turda onayladığı.
2. BANKA revizörünün B2'nin rapora inme eşiğini (güç < 0,25) kendi önerisi olarak koyması — düşükse "DSR gevşetildi"
   diye okunabilir; sayısal tablo şeffaf, kullanıcı isterse değiştirilebilir (Adım 1, kilitten önce).

**Durum:** 14/14 Codex bulgusu kapandı; ikinci doğrulama turunda çıkan yeni bulgu da kapandı. Üç taslak artık iç
tutarlı ve MIMARI-BANKA-CARRY arayüzü hizalı. Motor yazımı, açık soruların yanıtlanması ve ön-kayıt kilidi hâlâ
kapsam dışı (bu bir yazım aşamasıdır). **Aşama burada durur; kullanıcı değerlendirmesi bekleniyor.**

---

## 15. Açık soruların yanıtlanması (kilit Adım 1, 27 Eylül aynı gün)

Ayrıntı: [ACIK_SORU_YANITLARI.md](ACIK_SORU_YANITLARI.md). Özet: 21 sorunun tamamı yanıtlandı.

**Kullanıcıya doğrudan sorulan 4 soru** (belgelerde "onay bekleniyor" diye işaretliydi):
- **Soru 5 (exchangeInfo okuma):** Evet.
- **Soru 6 (REV1 D-dönemi getirisi v8'e):** Evet; REV1 süreci üretip tek yönlü aktarır, E3/Z2 yasak kalır.
- **Soru 17 (değerlendirici):** Yeni oturum + Codex bağımsız hash doğrulaması.
- **Soru 19 (kör hüküm anahtarı):** Kabul; kullanıcı üretir (motor yazımında adımlar anlatılır).

**Kalan 17 soru:** ana oturum, D'ye bakılmadan, belgedeki gerekçeli varsayılanı kabul ederek kapattı (tam liste
ACIK_SORU_YANITLARI.md'de). Öne çıkanlar: DD çarpanı yok (Soru 3), NAV 0,1M (Soru 4), K1/K2 eşikleri (Soru 9–10,
K1 artık korelasyona bağlı formül), D90 rapor-only (Soru 12), Kelly ızgarası yeterli (Soru 18).

**Soru 21 (deneme sayısı) kapatıldı ve deftere işlendi:** `V8_DENEME_DEFTERI.csv`'de `A2-mikroyapi` 144, `A2-ml` 5
olarak düzeltildi (önceki hâli `_arsiv/V8_ASAMA4_SENTEZ_20260927_01/defter_144_5_oncesi/`'de). Bugünkü N_v8 = 161.

**Durum:** Kilit sırasının Adım 1'i tamamlandı. Adım 0 (motor yazımı, sentetik fikstür testleri) ve Adım 2 (HAR
seçimi) hâlâ başlamadı — bunlar bu aşamanın (Aşama 4 sentez) kapsamı dışındadır (ONKAYIT §1) ve ayrı bir başlangıç
gerektirir. **Aşama burada durur.**
