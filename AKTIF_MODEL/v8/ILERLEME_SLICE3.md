# v8 motor Slice 3: ilerleme kontrol noktası (2026-09-28)

Durum: **TAMAMLANDI (29 Eylül)** — 241 test PASS, Codex 6. tur doğrulaması işlendi, belgeler güncel, commit edildi. Sıradaki: kilit Adım 2 (HAR/EWMA) ve D verisi yükleyicisi. Kaynak: MIMARI §4 (carry uydusu), §4.5 net çözücü, §4.7 sanal bacaklar/ayrıştırma, §5.8 carry
durumu; CARRY_KAPISI §3.2–§3.3, §5 (kapının motordan okuduğu tek tanımlar). Kapı KOŞULMAZ (ön-kayıt kilidi yok);
bu dilim yalnız kod + sentetik test.

Öncesi: K8 kullanıcı kararı MIMARI'ye yazıldı, commit 2c7f238.

## Plan (modüller)
1. `tipler.py`: `mimari` ('A'|'B', varsayılan 'A') ve carry sabitleri (§7 carry satırları, S4).
2. `carry.py` (saf): V30, eksik funding olay sayısı, carry adayları (histerezis), F30/σ^C/c, sıra-OLS nötrleme,
   β, bacaklar (%30/medyan histerezis, long funding tabanı), haftalık kitap §4.4 adım 1–7, hafta içi çıkış +
   yeniden nötrleme, günlük blok (adım 0) + T4-c.
3. `net_cozucu.py`: §4.5 adım 1–6 (trend önce; ikiye bölme 60 adım; κ^C; son çare tek katsayı).
4. `hedef.py`: B yolu (ortak Σ̂: A_t ∪ carry adayları ∪ BTC ∪ sabit), toplam risk L(1+ω_C)τ.
5. `karar.py` / `durum.py`: carry durumu (q^C*, β, λ, hafta damgası), sanal bacaklar, s^C son sıfır-dışı payı,
   sanal bacak maliyet bağlamı karar kaydında.
6. `ayristirma.py`: §4.7 satırları (trend/carry fiyat+funding, hedge, bacak maliyeti, netleme, icra artığı, s^C
   bölüşümü), CARRY §5.5 özdeşliği.
7. Testler: KC-04 örneği, haftalık bant, λ, hafta içi çıkış, κ<1, genişlik 15/10, long tabanı, S4 %3,33, T4-b/T4-c,
   kaçırılan/yapılan Pazartesi aynı görünümde farklı q^C*, s^C sıfır/sıfır, özdeşlik, A yolu değişmedi.
8. Codex incelemesi → belgeler → commit.

## Belgenin açık bıraktığı yerlerde yorumlar (kodda da yazılacak)
- Y1 Carry adayı ayrıca **V60 ≥ 20M** ister ve V60 < 20M olunca hafta içi çıkar: <20M maliyet dilimi yalnız
  çıkışta tanımlı (§6.1; K13 ile aynı gerekçe).
- Y2 Histerezisteki "mevcut" = önceki haftanın q^C* ≠ 0 isimleri; mevcut isim V30 ≥ 10M ile kalır, yeni isim
  V30 ≥ 20M ister. Hafta içi çıkış: maske, V30 < 10M, V60 < 20M.
- Y3 Bacak büyüklüğü k = ⌊0,30·n_C⌋ (en yüksek/en düşük). Eşit z'de alfabetik.
- Y4 Sıralar ortalama sıra (eşitlik); R30 eksikse (kapanış yok) o isim sırası medyan sıra.
- Y5 β̂: son 60 günün ortak tanımlı günlük getirileri; < 2 gözlem ya da BTC varyansı 0 ise β̂ = 1.
- Y6 Genişlik ×0,5 adım 2'de (bütçe) uygulanır, tavanlardan önce.
- Y7 Pazartesi işlem dışı (§2.5(d)) ya da bugünkü kapanışı olmayan isim yeni seçilmez; mevcut miktarı korunur
  (sabit).
- Y8 İlk Pazartesi'den önce carry kitabı 0.
- Y9 B'de işlem dışı coin net ağırlığında sabittir; trend bileşeni = w0 − κ·w^C (çözücüde değişmez), sanal trend
  miktarı değişmez.
- Y10 B'de reduce-only (§2.6) net kitaba uygulanır; K13 (V60 < 20M) trend bileşenine, önceki sanal trend değerine
  göre uygulanır. Sanal bacaklar reduce-only'den etkilenmez (fark icra artığına).
- Y11 S1/S2 aşamasında κ^C ikiye bölmeyle (her iki şok birlikte sağlanana kadar) bulunur; κ = 0 yetmezse bütün
  serbest net kitap tek katsayıyla küçülür (A §3.5 son çare).

## Durum günlüğü
- 19:10 UTC: plan yazıldı.
- 19:40 UTC: yazıldı: tipler (carry sabitleri, mimari), carry.py, net_cozucu.py, hedef_b.py, durum (carry alanları,
  karar kaydının hedef.carry bloğundan), karar (B dalı, sanal_baglam). Duman testi: 14 alt, 130 gün B koşusu çalışıyor.
  A testleri 12/12 PASS. SIRADAKİ: ayristirma.py, sonra B testleri.
- 20:00 UTC: ayristirma.py yazıldı (özdeşlik duman koşusunda 9e-11 USD). Testler: test_v8_carry.py (19 birim),
  test_v8_mimari_b.py (9 bütünleşik; fikstür carry_senaryo_verisi). Tam takım PASS. SIRADAKİ: Codex incelemesi
  (codex_cagrilari/20260928T4_slice3_inceleme_*), sonra belgeler + commit.
- 20:20 UTC: Codex 4. tur limit nedeniyle kesildi; günlükteki 4 karşı örnekten 3'ü düzeltildi (κ isim tavanı, bant
  tavanı, duzeltme nakdi; testli, eski koda karşı kalıyor; eski dosyalar _arsiv/V8_MOTOR_SLICE3_20260928_02/), 1'i
  belgelenmiş sınır (geç funding zamanlaması). Kayıt: codex_cagrilari/20260928T4_slice3_inceleme_KESIK_gunluk.md.
- Limit sıfırlandı (kullanıcı). Ultracode: iş akışı wf_94f2a3aa-9a3 = Codex 5. tur (20260928T5_slice3_inceleme_*)
  + 4 Claude inceleyici (carry, cozucu, ayristirma, durum_parite) + bulgu başına 2 şüpheci. SIRADAKİ: onaylı
  bulguları düzelt, test, belgeler (README, v8_calistir, defter V8MOTOR-slice3, DURUM), commit.
- 29 Eylül: wf_94f2a3aa-9a3 bitti. Claude: 9 onaylı (2/2 şüpheci), 2 tartışmalı. Codex 5. tur 12 bulgu (yanıt
  codex_cagrilari/20260928T5_slice3_inceleme_yanit.md); doğrulayıcıları oturum limitine takıldı, Claude elle
  değerlendirdi. Düzeltme öncesi kod: _arsiv/V8_MOTOR_SLICE3_20260929_03/. (Not: _02 arşivine yanlışlıkla güncel
  dosyalar kopyalandı; eski üç dosya tmp/eski_s3'ten geri yüklendi, fazlalar silinmeden tmp'ye taşındı.)

### Tur-5 bulgu işleme ([ ] yapılacak, [x] kod+test)
- [x] B1 (C onaylı, ORTA) eksik olay sayımı: Δ tespit saatinde (her h) — funding.py ile aynı kural.
- [x] B2 (C+X, OLDURUCU) çözücü/yeniden sınama toleransı: ikiye bölme sınırı toleranssız hedefler; denetimler
      ortak mutlak tolerans (net_cozucu.TOL).
- [x] B3 (C, CIDDI) adım 6 bant kapatma tarafı net işaretinden (+trend işareti); sürerse bütün bantlar kapanır.
- [x] B4 (C+X, CIDDI) K13: trend bileşenine ÇÖZÜCÜDEN ÖNCE (sanal trend değerine göre; bacak maliyeti için) VE net
      kitaba gerçek w0'a göre "yalnız azaltma" (A ile aynı; gerçek düşük hacimli giriş yok).
- [x] B5 (C+X, ORTA) sıra: bant/yeniden sınama → yalnız azaltma (reduce-only, K13 net) → T4-d → son denetim (A ile aynı).
- [x] B6 (C, CIDDI) bantta/K13'te tutulan sanal trend miktarı birebir önceki miktar (float gidiş-dönüşü yok).
- [x] B7 (C, ORTA) ayristir maliyet_k'yı günlükten okur; verilen değer farklıysa hata.
- [x] B8 (C+X, ORTA) bacak funding'i (gerçek + dolgu + ters kayıt) her bacağın kendi miktar geçmişiyle funding_saati
      üzerinden; gerçek net pozisyondan bağımsız.
- [x] B9 (C+X, DUSUK) λ ve bağlayan bacak durumda; hafta içinde son Pazartesi değeri taşınır, hafta içi λ ayrı kayıt.
- [x] B10 (tartışmalı, DUSUK) Pazartesi tutulan işlem dışı ismin β'sı da o Pazartesi hesaplanır.
- [x] B11 (tartışmalı + X, ORTA) κ: dışbükey kısıtlar → uygun κ kümesi aralık; önce en küçük ihlal noktası (üçe bölme),
      sonra en büyük uygun κ. Uygun κ yoksa son çare.
- [x] B12 (X, CIDDI) miktarlı düzeltmede özdeşlik: artık += tutar + miktar·açılış.
- [x] B13 (X, CIDDI) Y7 isimlerine de long funding tabanı (F30 ≥ −%50).
- [x] B14 (X, CIDDI) carry evreni histerezisi aday üyeliğine göre (durumda önceki Pazartesi aday listesi).
- [x] B15 (X, ORTA) ortak matris hafta içinde de son Pazartesi adaylarını kapsar.
- [x] B16 (X, ORTA) kayıtta 'kappa_etkin' (q^C,v = kappa_etkin·q^C*) yayımlanır; belge metni.
- [x] B17 (X Y4) eksik R30 sırası = tanımlı sıraların gerçek medyanı.
- Reddedilen: X9 / Y1 itirazı (V60 < 20M'de carry çıkışı kalır: yoksa κ'nın günlük artışı <20M'de sanal bacak
  girişi yaratır ve §6.1 maliyeti tanımsız olur). Y5, Y9 korunur (belge boşluğu; gerekçe README).
- 29 Eylül: B1-B17 kod + regresyon testleri tamam (test_v8_carry.TurBesTest, test_v8_mimari_b.TurBes*); 15 yeni
  test düzeltme öncesi koda (_03) karşı kalıyor. Tam takım PASS. SIRADAKİ: Codex 6. tur doğrulama
  (codex_cagrilari/20260929T6_slice3_dogrulama_*), sonra belgeler + commit.
- 29 Eylül 10:15: Codex 6. tur (20260929T6_slice3_dogrulama_*): 15 KAPANDI; B4, B16 KISMEN (belge–kod sözleşmesi);
  yeni ORTA (K13(ii) net = sanal toplam eşitliğini bozuyor; B4 ile aynı konu); X9: Y1'in MIMARI'ye yazılmasını istedi.
  İşlendi: MIMARI §4.1 (V60 tabanı, histerezis "mevcut" tanımı), §4.4 (evren çıkışı), §4.5 κ aralığı ve sıra özeti,
  §4.7 (κ_etkin, yalnız-azaltma istisnası); CARRY §5.1 κ satırı. Önceki metinler _arsiv/V8_MIMARI_SLICE3_20260929_01/.
  hedef_b tanılara 'yalniz_azaltma' isimlerini yazar. 241 test PASS. SIRADAKİ: README, v8_calistir, defter, DURUM, commit.
