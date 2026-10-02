# v8: D verisi yükleyicisi ve hız — ilerleme kontrol noktası (2026-09-29)

Durum: **BAŞLADI**. Kilit sırası (MIMARI §10) adım 0'ın kalan kısmı: D verisi yalnız metrik hesaplanmayan kısa
kesitlerle biçim ve özdeşlik denetimi. **Adım 4'ten (ön-kayıt kilidi) önce D'de P&L/metrik raporlanmaz.**

Öncesi: Slice 3 commit b1954e8; kullanıcı 1. kuralı (V60 < 20M carry çıkışı) onayladı, MIMARI/DURUM'a işlendi
(arşiv `_arsiv/V8_MIMARI_KURAL1_ONAY_20260929_01/`, henüz commit edilmedi).

## Veri gerçekleri (doğrulandı)
- Ham zip'ler ANA depoda: `<kök>/AKTIF_MODEL/ciktilar/v8_veri_20260924_01/ham/{klines,fundingRate}/<SYM>/*.zip`
  (worktree'de yok; izlenmeyen veri). 122 + 122 klasör.
- MANIFEST.jsonl (8596 satır) sha256 5eabe360…, ana depo = git. Satırlar yol başına tekrar edebilir (bilinen).
- GELISTIRME_EVRENI.json sha256 343dead4… (indir.py sabitiyle aynı); 'gelistirme' 122 sembol (BTC, ETH dahil).
  Klasördeki diğer dosyalar okunmaz/listelenmez (mühür kuralı).
- Funding zip'lerinde `funding_interval_hours` sütunu var → `funding_serisi(..., aralik_saat=)` (K2 sınırı kapanır).
- isle.py kuralları: başlık algılama, µs → ms, dönem [2023-07-01, 2026-07-01), sırala, tekrar ilkini tut,
  sayısal olmayanı at.

## Plan
1. `v8/adaptor/veri_yukleyici.py` (dosya okuyan adaptör; motor/ saf kalır): hash doğrulamalı ham zip okuma,
   isle.py kuralları, SaatlikSeri/FundingSerisi, TamVeri + yükleme raporu + veri kimliği (kullanılan dosya
   hash'lerinin özeti).
2. `testler/test_v8_veri_yukleyici.py`: sentetik zip + manifest fikstürüyle (gerçek veri yok).
3. Ön-kayıtlı D kısa kesit biçim/özdeşlik denetimi (`ciktilar/v8_d_kesit_<tarih>/ONKAYIT.md` önce yazılır): yükleme
   raporu, görünüm yapısı, kısa A ve B koşusunda günlük zinciri ve ayrıştırma özdeşliği. NAV/getiri yazdırılmaz.
4. Hız: 122 coinli sentetik fikstürle profil (D'ye dokunmadan), sıcak noktaları iyileştir, sonuçların birebir aynı
   kaldığını (günlük son hash'i) doğrula.

## Durum günlüğü
- 29 Eylül: plan yazıldı.
- 29 Eylül: yükleyici + 6 birim testi (15/15 dosya PASS); ön-kayıt ciktilar/v8_d_kesit_20260929_01/ONKAYIT.md
  (sha256 f6c440d0…) ve defter V8MOTOR-dkesit; commit cf2bd21 (koşudan önce). kesit_denetim.py arka planda koşuyor
  (sonuç: ciktilar/v8_d_kesit_20260929_01/sonuc.json; NAV/getiri yazmaz). Hız profili betiği hazır:
  ciktilar/v8_hiz_20260929_01/hiz_profil.py (sentetik 122 coin; D'ye dokunmaz). SIRADAKİ: kesit sonucu → RAPOR, profil.
- D kesit denetimi PASS (RAPOR ciktilar/v8_d_kesit_20260929_01/RAPOR.md; performans ölçülmedi). Veri kimliği 5907a89b….
- Hız: hijyen/boşluk taraması vektörleştirildi (gorunum.saat_indeksleri); sonuç hash'leri birebir aynı; ~2× hızlı.
  Sentetik 122 coin gün başına: A ~0,18 s, B ~0,45–0,49 s (150 gün). Tam uzunluk (1004 gün) B ölçümü arka planda.
  Hız engel değil. Arşiv: _arsiv/V8_VERI_HIZ_20260929_01/motor (iyileştirme öncesi).
- HAR (kilit adım 2): motor/har.py + testler/test_v8_har.py (8 test); tipler har_* alanları; ön-kayıt
  ciktilar/v8_har_secimi_20260929_01/ONKAYIT.md (henüz commit/defter YOK); betik har_secimi.py (--sentetik deneme
  arka planda). SIRADAKİ: sentetik deneme → Codex ön-kayıt+betik incelemesi → defter + commit → BAĞLAYICI D koşusu.
- Commit 43a48a0 (hız + D kesit), 31e9dea (HAR ön-kaydı rev 3, pushlandı; Codex T7/T8/T9). BAĞLAYICI HAR koşusu
  başladı (ciktilar/v8_har_secimi_20260929_01/kosu_cikti.txt, sonuc.json; kosu_commit.txt). SIRADAKİ: sonuç → RAPOR,
  HAR seçildiyse motor entegrasyonu (madde 12), commit.
- HAR SONUCU: HAR seçildi (QLIKE oranı 0,927; bootstrap üst sınır −0,008); commit c1288e6 pushlandı. Betimsel uyarı:
  stres haftalarında HAR kötü (+0,085), Y/F q99 HAR 6,50 / EWMA 6,04. RAPOR'a ifade notu eklendi (M ≤ t; commit YOK).
- HAR MOTOR ENTEGRASYONU (commit YOK): har.py HarTakvimi + har_sigma; tipler sigma_tahmincisi/har_takvimi; hedef.py
  CoinGunluk.gun_gecerli + boyut_sigmalari (A ve B); hedef_b.py aynı. EWMA yolu hash'i birebir (A 1f82d9f5 doğrulandı;
  B 150 gün karşılaştırması YAPILAMADI). Arşiv _arsiv/V8_HAR_MOTOR_20260929_01/. Test dosyası
  testler/test_v8_har_motor.py yazıldı, KOŞULAMADI (komut onay denetimi yanıt vermedi). SIRADAKİ: test koş, B hash
  karşılaştırması (gun_suresi 150 B; referans son_hash gun_suresi_B.json), tam takım, commit.
- HAR ENTEGRASYONU TAMAM: test_v8_har_motor.py 5/5; B 150 gün son hash f967ac19… entegrasyon öncesiyle AYNI; tam takım
  17/17 PASS (v8/ciktilar/test_20260929T083615Z). Ara test çıktıları _arsiv/V8_HAR_MOTOR_20260929_01/ara_test_ciktilari/.
- KAPASİTE SORUNU (kullanıcıya sunuldu, 29 Eylül; karar bekliyor): BANKA §3.7 Düzey 2 = 6 ayar × 100 temel yol × (1 + ×2 + ×3 + 10 çıkarma)
  + her temel yolda 200 null → ~120.000 null koşu × A/B; 30 coinlik 4,2 yıllık koşu ~4 dk → on binlerce CPU saati.
  Bankadaki B7 null'u (500 yol × 82 coin × ~3,5 yıl) ~80–125 CPU saati (yapılabilir). Düzey 2 bu haliyle yapılamaz;
  tasarım revizyonu ya da büyük hızlanma gerekiyor — kilitten önce karar.
  Değerlendirmede: (i) B7 veto olduğu için B7'siz birleşik yanlış kabul B7'li değerin üst sınırıdır → (b) null gerektirmez;
  (ii) κ=0'da HL anlamsız (6 ayar aslında 5); (iii) mevcut q-kuralı artefakt olmadan da ~%10–15 q95'e çıkar.
  Seçenekler: 1 q95 sabit; 1+ (öneri) q95 + κ=0 null'suz motor kontrolü (100 yol × 13 koşu, A ve B, ~195 CPU sa) +
  betimsel B7 gücü (yalnız A, 5 ayar × 10 yol × 50 null, ~105 CPU sa) ≈ 300 CPU sa / 1–1,5 gün; 2 küçültülmüş Düzey 2
  (20 yol × 50 null; 300–1.100 CPU sa; q kararı ve %5 doğrulaması gürültülü); 3 motoru 10× hızlandır (haftalar,
  hash birebirliği kaybı riski). 16 mantıksal çekirdek.
