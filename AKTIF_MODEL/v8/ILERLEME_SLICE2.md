# v8 motor Slice 2: ilerleme kontrol noktası (2026-09-28)

Durum: **TAMAMLANDI (28 Eylül ~19:00 UTC)** — Codex 3 tur incelemesi işlendi, 195 test PASS, belgeler güncellendi, commit edildi. Sıradaki iş: Slice 3 (carry uydusu).

## Yapılan
- Yeni motor modülleri (`motor/`): `gorunum.py` (PIT veri, borsa çapı boşluk), `hijyen.py` (donma (a)-(d), maske),
  `evren.py` (aylık seçim, histerezis), `gunluk.py` (hash zincirli OlayGunlugu), `durum.py` (StratejiDurumu,
  `kayit_uygula`, `durum_turet`), `funding.py` (gerçek kayıt, eksik funding dolgusu, ters kayıt), `emir.py`
  (lot, risk azaltan/artıran ayrımı, saatlik dolum), `hedef.py` (`hedef_agirlik`, T4-a/T4-d), `karar.py`
  (`karar_ver`, `kacirilan_karar`), `geri_test.py` (§5.2 saatlik olay döngüsü, `kos`).
- Değişen Slice 1 dosyaları: `tipler.py` (Slice 2 parametreleri), `tavanlar.py` (isteğe bağlı `sabit_mi`;
  varsayılan davranış aynı). Önceki halleri `AKTIF_MODEL/_arsiv/V8_MOTOR_SLICE2_20260928_01/`.
- Testler: `fikstur/saatlik_veri.py` (sentetik 1h bar/funding + 150 günlük uçtan uca senaryo),
  `test_v8_gunluk_durum.py` (17), `test_v8_hijyen_evren.py` (24), `test_v8_funding.py` (9), `test_v8_emir.py` (17),
  `test_v8_karar.py` (8), `test_v8_geri_test.py` (16). Toplam ~165 test (Slice 1'in 74'ü dahil).
- `v8_calistir.py test`: 12/12 dosya PASS (2026-09-28 13:56 UTC).

## Belgenin açık bıraktığı yerlerde verilen yorumlar (kod yorumlarında da yazılı)
- Borsa çapı boşluk: çok saatlik kesintide referans küme kesinti öncesi son temiz saatte tutulur (yoksa yalnız
  ilk saat boşluk sayılırdı). `gorunum.bosluk_saatleri`.
- (b)/(d) penceresi son 24 saat; boşluk saatleri sayaçlara girmez. (d) = en uzun ardışık eksik > 8 saat.
- İşlem dışı coin tavan çözücüsüne sabit girer; küçültmeler yalnız serbest isimlere (dışbükeylik katsayısı).
- Borsa boşluğunda karar reduce-only verilir; eski devreden tamamen iptal edilip yeni (yalnız azaltan) niyet yazılır.
- V60 < 20M iken giriş dolumu da 25 bps dilimle fiyatlanır (muhafazakâr; belge yalnız çıkışı tanımlıyor).

## 2. oturum (2026-09-28 ~18:15 UTC)
- Adım 1 yapıldı: ara çıktı silinmedi (kural 5), `_arsiv/V8_MOTOR_SLICE2_20260928_01/ara_test_20260928T135135Z/`
  altına taşındı. Test yeniden: 12/12 PASS.
- Adım 2 yapıldı: Codex incelemesi `v8/codex_cagrilari/20260928T_slice2_inceleme_{istem,yanit}.md`.
  Sonuç: 15 bulgu (9 CIDDI, 6 ORTA), Y1/Y3 kabul, Y2/Y4/Y5 itiraz. **Şimdi: bulguları doğrulama + düzeltme.**
  Her bulgunun durumu aşağıdaki "Bulgu işleme" tablosuna yazılır.
- Düzeltme öncesi motor+test anlık görüntüsü: `_arsiv/V8_MOTOR_SLICE2_20260928_02/`.

### Bulgu işleme (Claude doğrulaması → karar; [ ] yapılacak, [k] kod yazıldı, [x] kod+test tamam)
Durum 18:45 UTC: 15 bulgunun KODU yazıldı (gorunum, hijyen, durum, funding, emir, hedef, karar, geri_test, tipler).
Testleri güncel: emir, gunluk_durum, funding (K1/K2/K3/K9/K14/K15 testli). 18:55 UTC: bütün K1-K15 kod+test tamam; 12/12 PASS; yeni testler eski motora karşı KALIYOR (ayırt edici).
19:10 UTC: Codex 2. tur yapıldı (20260928T2_slice2_dogrulama_*): 10 KAPANDI, 5 KISMEN (K1,K2,K8,K10,K11), 2 yeni ORTA.
Tur-2 düzeltme planı (hepsi doğrulandı, uygulanıyor):
- K1b: durum `funding_islenen` = coin başına işlenmiş damga kümesi (son 30 gün); pencere içindeki işlenmemiş her kayıt
  işlenir (eski kayıt yenisinden sonra gelse de; ilk kayıt da). q=0 ve kapsanan dolgu yoksa kayıt yazılmaz.
  Bekleyen dolgular yalnız kapsanan aralıkta düşer, 30 günden eskisi budanır. Döngü: pozisyon | bekleyen dolgu |
  son 30 günde pozisyon değişimi. Parametre `funding_gec_kayit_gun=30` (mekanik).
- K2b: FundingSerisi isteğe bağlı `aralik_saat` (arşivdeki funding_interval_hours); yoksa kapsam = aralıktan küçük/eşit
  en büyük borsa aralığı {1,4,8} (MIMARI §5.3).
- K8b: belge metni düzeltilir (isim tavanı aşımında serbestler küçülmez); teknik hata yerine olay kararı korunur,
  README'de belge boşluğu + kullanıcı kararına açık not.
- K10b/Y1: bosluk_gecmis 30 gün; _c_penceresi aynı sınırı kullanır.
- K11b: (b) penceresi t−24h öncesinden 5 boşluk-dışı saat geriye uzar.
- Y2: reduce-only'de yeni niyet eski azaltanı en az onun kadar azaltıyorsa yerine geçer (eşitlikte yeni; maske çıkışı taşınır).
19:00 UTC: tur-2 düzeltmeleri + testleri tamam (12/12 PASS; yeni testler tur-1 koduna karşı kalıyor).
Codex 3. tur (20260928T3_slice2_dogrulama_*): K1,K8,K10,Y1,Y2 KAPANDI; K2,K11 KISMEN (belgelenen sınırlar:
arşiv aralık sütunu yoksa 4h tek eksik ↔ 4h→8h ayrılamaz; 29+ günlük kesintide (b) tarama sınırı); 2 yeni
(ORTA budama payı, DUSUK sıfır kayıtta budama) düzeltildi: funding_budama_ms = pencere − 8h, karar kaydı da budar.
19:05 UTC: 12/12 PASS. Codex döngüsü kapandı. SIRADAKİ: Adım 3 (arşiv → README, v8_calistir, deneme defteri, DURUM).
Sıradaki (eski): Codex 2. tur doğrulama (codex_cagrilari/20260928T2_slice2_dogrulama_*), sonra Adım 3.
- [x] K1 funding geç gelen kayıt — KISMEN (geri testte geliş=damga; canlıda kayıp). Düzeltme: (son işlenen, T]
      aralığındaki bütün gerçek kayıtlar işlenir; durum coin başına son işlenen gerçek damgayı tutar.
- [x] K2 ters kayıt kapsamı — DOGRU. Dolgu saat saat kaydedilir; kayıt yalnız kapsadığı (T−aralık, T] saatlerini
      ters çevirir; aralık = min(T − önceki gerçek, 8h) (MIMARI §2.5 gerekçesi: borsa aralığı ≤ 8h).
- [x] K3 kapanmış pozisyon dolgusu — DOGRU. Funding döngüsü pozisyon geçmişi olan bütün coinleri tarar.
- [x] K4 ilk kararda maske geçmişi — DOGRU. maske_ms None ise veri başından gün gün işlenir.
- [x] K5 gün içi borsa boşluğunda giriş dolumu — DOGRU. Her dolum saatinde T−1h boşluksa risk artıran parçalar iptal.
- [x] K6 reduce-only azaltan emri siliyor — DOGRU (Y4 geri çekildi). Eski azaltan korunur; yeni niyet yalnız daha
      fazla azaltıyorsa onun yerine geçer.
- [x] K7 uzun kesintide referans — DOGRU. Boşluk referans durumu karar kaydında taşınır (bosluk_ref); ilk kararda
      veri başından taranır.
- [x] K8 sabit isim tavan ihlali — KISMEN. Teknik hata yerine (piyasa kaynaklı, işlem yasak) olay kaydı; ama sabit
      isim tavanı ve T4-d artığı bayrağa eklenir.
- [x] K9 duzeltme miktarı — DOGRU. duzeltme kaydı miktar taşıyabilir; pozisyon değişir.
- [x] K10 (c) boşluk saatleri — DOGRU. 16 saat penceresi boşluk dışı saatlerle sayılır.
- [x] K11 (b)/(d) — DOGRU. (b) gece yarısını aşan seri; (d) toplam eksik saat > 8 (Y2 değişti).
- [x] K12 işlem dışı gün getirisi — DOGRU. (d) günleri maske kaydında tutulur; getiri eksik yazılır.
- [x] K13 V60<20M giriş — DOGRU (Y5 geri çekildi). Karar anında V60<20M coinde hedef |w|≤|w0| (yalnız azaltma).
- [x] K14 korunan kapanış parçası — DOGRU. Korunan parça = −q ise tam_kapanis işaretlenir.
- [x] K15 bozuk zincir — DOGRU. durum_turet önce dogrula().

## Kalan adımlar (sırayla)
1. Ara test çıktı klasörü `ciktilar/test_20260928T135135Z/` sil (bu oturumun ara çıktısı), son test koşusunu tekrarla.
2. Codex ile bağımsız kod incelemesi (`CODEX_YEREL_AJAN.md`, `codex exec -s read-only`): Slice 2 kodu ↔ MIMARI §2, §3, §5.
   İstem/yanıt `AKTIF_MODEL/v8/codex_cagrilari/` altına, sha256 rapora. Bulguları işle, testleri yeniden koş.
3. Arşivle, sonra güncelle: `AKTIF_MODEL/v8/README.md` (Slice 2 bölümü), `v8_calistir.py` durum metni ("Slice 1"),
   `V8_DENEME_DEFTERI.csv` (`V8MOTOR-slice2` satırı, varyant 0), `DURUM.md` (kısa not; başlık tarihi de eski).
4. Commit (Co-Authored-By: Claude Opus 5.5) ve push. Bu dosya o commit'te silinmez; "tamamlandı" diye işaretlenir.
5. Sonraki iş: Slice 3 (Mimari B carry uydusu), sonra kilit Adım 2 (HAR/EWMA seçimi).
