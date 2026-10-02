# v8 banka koşusu (Adım 6–8) — uygulama planı ve ilerleme

Başlangıç: 2026-09-30 01:45 UTC. Kaynak: BANKA_ONKAYIT_TASLAK.md §1.3–§1.4, §2, §3, §4, §5.4, §8 (3. revizyon + netleştirmeler).
Kod YAN DALDA yazılır (`claude/v8-kapi-motor-502e`, `.claude/worktrees/codex-kirmizi-502e`): `v8/banka` kalibrasyonun
dondurulmuş kod kimliğine dahildir, Düzey 2 + 3.09 bitene kadar ana dizinde değişmez. Yeni paket: `v8/banka_kos/`.

## Tasarım kararları (kilitten önce BANKA "Uygulama netleştirmeleri"ne yazılacak; D ve banka verisi görülmeden)

- **BK-1 Birim düzeni ve devam.** Banka koşusu `banka_kos.py`'nin tek çağrısıdır (§2.4) ama içeride kalibrasyon koşucusunun
  birim/devam/çok süreç düzenini kullanır: her tam motor koşusu bir birimdir (kimlik kanonik JSON). Kesilirse aynı komut
  yeniden verilir; biten birimler atlanır; sonuç sıradan ve işçi sayısından bağımsızdır (§3.7 kalibrasyon kuralıyla aynı).
  Bu "ikinci çağrı" değildir: aynı dondurulmuş iş listesinin tamamlanmasıdır; iş listesi ve kimlikler hash'lidir.
- **BK-2 Şifreli birim sonuçları.** Kapalı grup düz metni diske yazılmaz (§2.4). Her birimin performans içeriği
  (NAV, getiri, metrik) üretildiği anda kullanıcının açık anahtarına age v1 (X25519) biçiminde şifrelenir: `sonuc/birim/<ad>.age`.
  Açık gruba (`denetim/`) birim başına yalnız düz metnin sha256'sı, şifreli dosyanın sha256'sı ve performans içermeyen
  denetimler (T4 değişmezleri, özdeşlik farkı, N1–N6) yazılır. Devam için içerik gerekmez (dosya + hash yeter).
- **BK-3 Hüküm hesabı.** `SONUC_DAMGA.json` bütün birimlerin düz metin sha256'larını ve bunların kök hash'ini taşır
  (şifrelemeden önce, §2.4 "önce düz metnin sha256'sı"). Denetim listesi (T1–T5) tamamlanıp `DENETIM_TAMAM.json` itildikten
  sonra kullanıcı şifreyi çözer; dondurulmuş `banka_hukum.py` çözülmüş birimlerin sha256'larını damgayla doğrular ve
  `banka_sonuc.json`'u (B2–B11, R1–R17, Kelly, 𝓛*) mekanik olarak üretir. Hesap deterministiktir; Codex aynı girdilerle
  yeniden üretebilir. Birim içeriği değişirse damga tutmaz → T1.
- **BK-4 Stres bindirmeleri (§5.4) ek motor koşusu değildir;** gerçekleşen kitap (gün sonu pozisyonları) ve NAV'dan hüküm
  aşamasında hesaplanır; bu yüzden birimler gün sonu ağırlık özetini (şifreli) taşır.

- **BK-5 Görülmüş 7 gün.** BTC/ETH'nin görülmüş 7 günü mühür belgesinin §4'ündedir (mühürlü; şimdi okunmaz). Kod listeyi
  açılışta girdi olarak alır ve yalnız uygular (bütün metriklerden ve null istatistiğinden aynı takvim günleri düşülür).
- **BK-6 B10 türetmesi ve devam.** B10 çıkarma birimleri birincil sonucun (şifreli) alt katkı sırasından türetilir. Kesintiden
  sonra içerik çözülemeyeceği için, B10 birimleri bitmeden kesinti olursa birincil birim bellekte yeniden yürütülür
  (deterministik) ve liste yeniden türetilir; hiçbir şey diske düz yazılmaz. Türetilen birimlerin adları coin kimliği
  taşımaz (opak sıra numarası + birincil düz metin sha'sı).
- **BK-7 T0_Z1 yuvarlaması.** "İzleyen ayın 1'i": tarih zaten ay başı 00:00 ise kendisi, değilse bir sonraki ayın 1'i.

- **BK-8 Stres bindirmesi ayrıntıları.** Blok uzunluğu ⌊365/k⌋ gün; şok çarpanı olay gününden sonraki ilk ölçüte dahil
  günün getirisine uygulanır (görülmüş gün dışlaması şoku silmesin); öyle gün yoksa olay gününe.
- **BK-9 Kelly bootstrap'ı.** §4'ün "blok bootstrap (20 gün, 2.000 çekiş)"ı §3.1'deki gibi durağan blok bootstrap'tır
  (geometrik blok, ortalama 20, dairesel); her çekiş 1.095 günlük yol; tohum uretec(tohum_banka, 'kelly', 10·L, maliyet_k).
- **BK-10 Lot kapalı koşu (R13).** Bütün sembollerde miktar adımı 0, minNotional aynı (yürütücüde uygulanıyordu; burada
  kayda geçti, 30 Eylül bulut).
- **BK-11 Hata sınırı (Codex T17-b; BELIRSIZLIK_COZUMLERI Grup 6, U-58 ek 2).** Birim yürütme + serileştirme + şifreleme +
  yazım, işçi başlatma, BK-6 yeniden yürütmesi ve koşucunun kendisi ortak sınırdan geçer; iz alıcıya şifreli
  (`sonuc/hata/<etiket>.age`), dışarı sabit mesaj + düz izin sha256'sı; özgün bağlam (işçinin uzak izi dahil) bastırılır.
- **BK-12 Hükümde damga denetimi (T1).** `birimleri_coz` damganın kök hash'ini ve birim sayısını kendi satırlarıyla, verilirse
  denetim sırasında itilmiş damganın kök hash'iyle karşılaştırır; tekrarlanan birim ve eksik şifreli dosya hatadır; her
  birimin şifreli ve düz sha256'sı damgayla aynı olmalı. Stres nesneleri birincil örneklem günleriyle aynı şekilde olmalı.
- **BK-13 B5 yalnız birincilde (Codex T18-CIDDI-3; 30 Eylül, bulut 2. tur).** BANKA §3.4 "aksi yazılmadıkça birincil ayar":
  B5 epizotları (ve M = B'de ayrıştırma) yalnız birincil birimde ve R8'in bağımsız A biriminde hesaplanır; ızgara, Kelly,
  çıkarma, K-evren ve rapor birimleri SR, NAV, katkı, stres nesneleri ve B9 serisini taşır (b5 alanları None). R8'in
  "her Kelly L'si için carry bacağının betası" 6.08'de B Kelly birimleri için ayrıştırma ister (açık).
- **BK-20 Tek atış betiği (30 Eylül dizüstü).** Tanım BANKA §3.7 netleştirme 20 (koddan önce 6bdab51). `v8/veri_denetim.py` (T2, VERI_DENETIM.json) → `v8/banka_kos.py` (T1 DONDURMA, VERI_DENETIM kapısı, kosucu, SONUC_DAMGA, DENETIM_OZETI); ortak katman `banka_kos/acilis.py` (Donem: banka/kuru, kimlikler, ACILIS denetimi, kilitli exchangeInfo'dan filtreler, veri, işçi bağlamı); T5 `banka_kos/parite.py` (birincil birimde 20 gün, açık grupta yalnız sayı). Kuru kip D paketinde, tek kullanımlık alıcı.
- **BK-17 R8 (30 Eylül dizüstü).** Tanım BANKA §3.7 netleştirme 16 (koddan önce 83b6299). B birincil `r8_satirlar`; B'nin 1× Kelly birimleri `r8_carry` (ayrıştırma yalnız bu seri için; ölçüm B5'siz, BK-13'teki açık nokta kapandı); rapor `rapor.r8_b`.
- **BK-16 R2, R4, R13 (b), R15, R17 (30 Eylül dizüstü).** Tanımlar BANKA §3.7 netleştirme 15 (koddan önce ac5bfe7). Birincil birim `piyasa`, `r13b`, `r17`; null birimleri `r17` (ortak pay dahil); rapor `banka_kos/rapor.py`. R4 için REV1 süreci D dönemi günlük getirisini tek yönlü verir (açık soru 6); dosya ve sha256 satırda.
- **BK-15 Koşu tanıları R5, R6, R7, R14 (30 Eylül dizüstü).** Tanımlar BANKA §3.7 netleştirme 14'te (koddan önce commit e3fa0f1). Kod `banka_kos/tanilar.py`; birincil birimin düz çıktısında `tanilar`, demo NAV biriminde `r14`; rapor `banka_kos/rapor.kosu_tanilari`. R7 tahminci yalnız M = A.
- **BK-14 R3 long-beta kitabı — KARAR VERİLDİ (30 Eylül dizüstü, kullanıcı önerileri kabul etti): (4) AYLIK yeniden
  dengeleme (b); BTC/ETH evrendeyse dahil; M = A/B aynı; R3 kendi motor koşusu. Bağlayıcı metin BANKA §3.7
  netleştirme 13; kod 6.08'de. Aşağısı bulut taslağıdır (tarihsel).** Taslak (30 Eylül, bulut 2. tur; kod yazılmadı). BANKA §3.4 R3: "aynı PIT
  evrende 1/σ̂ ağırlıklı pasif long kitap, aynı maliyetle, aynı gerçekleşen vol'e ölçekli; SR farkı, korelasyon, α ve t".
  Belge ayrıntıyı bırakmış; kilitten önce BANKA §3.7 netleştirmesine girmesi gereken öneriler:
  (1) Evren: aynı birim birincil ayarla motoru koşar (bir ek motor koşusu) ve her karar gününde karar kaydının
      `hedef.coinler` − `maskeli` − `sabit` kümesini kullanır (motorun PIT evreni, maske ve işlem dışı kuralı birebir).
  (2) σ̂: aynı gün, aynı kümede `motor.hedef.boyut_sigmalari` (HAR banka takvimi, taban %20; boyutlamayla aynı).
  (3) Ağırlık: w_i = (1/σ̂_i) / Σ_j (1/σ̂_j), yalnız long, brüt 1 (L = 1); BTC/ETH dahil (evrenin parçası).
  (4) Yeniden dengeleme: SORU — (a) motorla aynı günlük karar saati, bantsız; (b) aylık evren seçimi gününde ("pasif");
      öneri (b) + evrenden çıkan/maskelenen isim o gün satılır.
  (5) İcra ve maliyet: karar 00:00, dolum 01:00 açılışı, `motor.maliyet.maliyet_hesapla` aynı bağlam girdileriyle
      (V60, σ, BTC/ETH sınıfı, karekök terimi kitabın kendi nominaliyle); lot/minNotional aynı filtre.
  (6) Funding: long pozisyon gerçek funding kayıtlarını öder/alır (motorun funding_saati kuralı, dolgu ve ters kayıt dahil).
  (7) Vol ölçekleme hükümde/raporda: R3 günlük getirisi birincilin gerçekleşen vol'üne doğrusal ölçeklenir (B11 gibi;
      görülmüş günler hariç); SR farkı, korelasyon, α ve t (birincil r_t = α + β r3_t + ε; t NW, gecikme 10).
  (8) Çıktı (şifreli): gün sınırı NAV'ı, günlük brüt/net devir, maliyet ve funding payı; açık grupta performanssız sayılar.
  Açık sorular: (4); BTC/ETH dahil mi; M = B'de aynı mı (evet önerisi: R3 mimariden bağımsız pasif kitap, evren A/B
  aynı); R3 kendi motor koşusu yerine birincil birimin karar kayıtlarını mı kullanmalı (birimler bağımsız olduğu için
  öneri: kendi koşusu).

## Birim listesi (M = kapı sonucu; B ise ayrıca A ayrıştırması)

| Grup | Birimler | Sayı |
|---|---|---|
| Birincil | L=1, 1×, 0,1M, h_L %10 | 1 |
| R1 + B3 | NAV {0,1M; 1M; 5M} × maliyet {1×, 2×, 3×} (birincil hariç) | 8 |
| Kelly | L {0,5; 1,5; 2; 2,5; 3; 4} × maliyet {1×, 2×} + L=1 2× (R1'de) | 12 |
| B10 | ana koşunun mutlak net katkısı en büyük 10 alt, tek tek çıkarma (türetilen) + BTC, ETH çıkarma (R) | 12 |
| B9 | K-evren koşusu (80 K + BTC/ETH) | 1 |
| B7 | rejim-null yolları p = 1…500 | 500 |
| R9 | h_L %50, %90 | 2 |
| R13, R14 | lot kapalı; demo NAV 5.000 | 2 |
| R8 | M = B ise bağımsız A koşusu (birincil ayar) | 0/1 |
| R3 | 1/σ̂ pasif long kitap (motor dışı; ayrı basit simülatör, aynı maliyet modeli) | 1 |

## Parçalar (her biri ≤ 45 dk; test → commit → push → takip)

| Kod | İş | Durum |
|---|---|---|
| 6.01a | `banka_kos/ayar.py`: dönemler (T0_Z1 kuralı, Z1 dilimleri, birincil örneklem, Z2, D segmenti, görülmüş 7 gün), birim listesi, birim kimliği | TAMAM (yan dal; 5 test) |
| 6.01b | `banka_kos/veri.py`: banka verisi yükleyici | TAMAM (30 Eylül dizüstü; netleştirme 19, BK-19: banka indirmesi + D paketi, bağlayıcı ilk hash, D penceresi dışlaması, Z2_son, Eylül API funding görüntüsü, çift damga hatası, veri kimliği; test_v8_banka_veri 3 test; anonim kimlik bbeddc5) |
| 6.01c | `banka_kos/yurutucu.py`: birim yürütücü (motor koşusu → ayrıştırma → gün sonu ağırlıklar → düz metin sonuç sözlüğü) | TAMAM (yan dal 9623677; 5 test; R3 long_beta ayrı) |
| 6.10a | `banka_kos/age.py`: age v1 X25519 şifreleme (cryptography ile) + çözme (test ve hüküm için) + test vektörleri | TAMAM (yan dal 9ebe248; 8 test; resmi age ile gidiş-dönüş kullanıcı anahtarıyla 6.10b'de) |
| 6.10b | Kullanıcı anahtar çifti + resmi age ile uyumluluk | TAMAM (1 Ekim): kullanıcı age-keygen ile üretti (gizli anahtar yalnız kullanıcıda, proje dışında); açık anahtar `age1n4ad…5ac4jl` (DONDURMA `sifreleme_acik_anahtar`); `ciktilar/v8_age_sinama_20261001`: banka_kos/age ile şifreli dosya resmi `age -d` ile çözüldü, düz sha256 eşleşti |
| 6.01d | `banka_kos/kosucu.py`: iş listesi, şifreli sonuç yazımı, devam, damga (BK-1, BK-2) | TAMAM (yan dal 33bec64; 5 test); BK-11 hata sınırı a6c0ba3 (10 test) |
| 6.05 | B7 null birimleri (banka.rejim_null ile; bankanın dilimleri; N1–N6 açık grupta) | TAMAM yürütücüde (6.01c: null_yolu, veri_kes, N1–N6 açık grupta; test_k_evren_null_lot) |
| 6.02 | `banka_kos/hukum.py`: B2–B11 (banka.olcutler, degerlendirme), karar | 6.02a TAMAM (bulut a093e28, madde 7; 13 test); bootstrap %90 aralıkları (§3.1 betimsel) AÇIK |
| 6.03–6.04 | R1/B3 ızgarası, B10/B9 hesapları (hukum.py'de) | TAMAM (6.02a ile; R1 9 hücre, B9 penceresi, B10 türetilen 10 birim) |
| 6.06 | Kelly tablosu, bootstrap MDD, 𝓛* | 6.06a TAMAM (banka_kos/kelly.py, 5 test); hüküme bağlandı (6.02a; `kelly_cekis` bağlam alanı) |
| 6.07 | Stres bindirmeleri D90/SQ/DM (BK-4), R9 | 6.07a TAMAM (banka_kos/stres.py, 5 test); gün sonu ağırlıkları yürütücüde; hüküme bağlandı (6.02a, şekil denetimi) |
| 6.08 | R2–R17 rapor satırları | KISMEN: R3 TAMAM (30 Eylül dizüstü; `banka_kos/long_beta.py`, yürütücü + hüküm `R3`; test_v8_banka_long_beta 9 test, uçtan uca R3 dahil). 1. parça TAMAM: `banka_kos/rapor.py` R9, R10 (Z2 + D), R11 (SR %90 GA: durağan blok bootstrap, §3.1), R12 (L = 1 kanal stresleri SR + MDD), R13 (a), R16 (24 hücre); test_v8_banka_rapor 3 + uçtan uca A/B. 2. parça TAMAM: `banka_kos/tanilar.py` R5, R6, R7, R14 (BANKA §3.7 netleştirme 14, BK-15; yürütücü birincil ve demo NAV biriminde şifreli çıktıya yazar; durum izi pozisyon geçmişiyle çapraz denetlendi). 3. parça TAMAM: R2 (piyasa serileri + NW regresyon + pozisyon bazında BTC/artık katkı; katkı özdeşliği testte 1e-9), R4 (REV1 serisi dışarıdan; yoksa 'REV1 serisi yok'), R13 (b), R15, R17 (null birimleri r17 taşır) — netleştirme 15, BK-16. R8 TAMAM (netleştirme 16, BK-17: B birincil ayrıştırma satırları, trend/carry bacağı SR + GA, bağımsız A, her Kelly L için carry bacağı BTC/alt betası; ayrıştırma özdeşliği testte 1e-9). 6.08 TAMAM; B tablosunun %90 GA’ları 6.09 şablonunda |
| 6.09 | BANKA_RAPORU.md şablonu | TAMAM (30 Eylül dizüstü; `banka_kos/rapor_md.py`: §8.2'nin 13 bölümü, zorunlu cümleler aynen, B tablosunda %90 GA (B3, B7, B9; serisi olmayanlar —), coin adı yok; uçtan uca A/B testi) |
| 6.11 | `veri_denetim.py` (T2) | TAMAM (30 Eylül dizüstü): saf denetim `banka_kos/veri_denetim.py` + betik `v8/veri_denetim.py` (netleştirme 20 c: T1, yükleme, dönem, kilitli exchangeInfo'dan filtreler, onarılamayan satır yükleyiciden önce T2, coin adsız VERI_DENETIM.json; çıkış 3 = T2); test_v8_banka_acilis kuru zinciri |
| 6.12 | Uçtan uca sentetik banka koşusu testi | TAMAM: 6.12a (bulut) + tam motorlu prova (30 Eylül dizüstü; `ciktilar/v8_banka_prova_20260930_01`: A 539 birim 885 sn, B 540 birim 1.226 sn, 12 işçi; zincir hatasız, 13 bölüm rapor; NOT.md B7/R17 fikstür notu). Tek atış betiği `v8/banka_kos.py` (netleştirme 20; T5 parite birincilde, test A/B hata 0) |
| 6.13 | Codex 2 tur | AÇIK |

## Günlük
- 2026-09-30 01:45 UTC: plan yazıldı; BK-1…BK-4 kararları.
- 2026-09-30 01:50 UTC: 6.10a age (9ebe248), 6.01a ayar (yan dal); BK-5…BK-7.
- 2026-09-30 02:06 UTC: anonim kimlik (HMAC), Pencere.haric_gunler (BK-5), stres (BK-8), Kelly (BK-9) — yan dal.
- 2026-09-30 07:04 UTC: anonim kimlik, stres, Kelly, yürütücü (null veri kesimi dahil), koşucu yan dalda; age katı biçim (F9).
  SIRADAKİ: 6.01b veri yükleyici (banka + D + Z2 birleşik kökler; banka verisi 8.01'de iner, şimdi sentetik testle),
  R3 long-beta, 6.02 hüküm (banka_hukum.py: çözülmüş birimlerden B2–B11, R1–R17, Kelly, stres; damga doğrulaması).

## Gece planı (2 Ekim, kullanıcı yok; limit: 5 sa %49, haftalık %67 — haftalık ≥%75'te yeni parça yok)
1. Codex T30 (U1–U3 okuması) → düzeltme (kilitli kurala dokunan bulgu varsa DUR, kuru koşu başlamaz)
2. Tam takım venv ile (V1 raporu) → commit
3. Sunucu <sunucu>: 6.14 veri_denetim.py kuru (yalnız T2 geçti/kaldı açık)
4. 6.15 banka_kos.py kuru A --isci 12 (systemd, Restart=no) → ilk birimlerden hız ve bitiş tahmini
5. Bitti ise 6.16 denetim raporu. Dondurma (7.02 onay) ve banka (8) YAPILMAZ; sunucu silinmez.
Gece durumu (2 Ekim ~21:35 UTC): 1 Codex T30 → düzeltme 0dacfcd, T31 → 808bc39 (kuru koşuya engel yok) TAMAM; 2 tam takım
59/59 test_20261001T212829Z (1803f49) TAMAM; 3 6.14 sunucuda T2 yok (b7dda04) TAMAM; 4 kuru koşu servisi hazır
(`systemctl start v8-kuru`), kullanıcı onayı bekleniyor (açık karar: D doğrulama defter satırı — UYGULAMA_EK rev 2).
