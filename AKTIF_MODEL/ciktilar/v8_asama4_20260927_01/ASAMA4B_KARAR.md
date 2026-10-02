# Aşama 4b: kullanıcı kararı ve revizyon turu başlangıcı

Tarih: 2026-09-27. Bu belge revizyon turundan ÖNCE yazıldı. Dayanak: [RAPOR.md §12–§13](RAPOR.md),
[CODEX_KIRMIZI_TAKIMI.md](CODEX_KIRMIZI_TAKIMI.md), Codex'e canlı danışma
(`codex_cagrilari/20260927T_saclik_yanit.md`).

## 1. Kullanıcı kararları (27 Eylül)

1. **S-a: kapı → A/B kalır** (RAPOR §10 seçenek (a), mevcut karar). Kapısız A seçilmedi. Carry kapısı
   Codex'in KC-03/04/05/06/07 bulgularıyla düzeltilerek korunur.
2. **S-c: DSR tek sabit bağlayıcı eşik değil; kalibre edilmiş σ_SR duyarlılık tablosu.** BANKA_ONKAYIT_TASLAK
   §3.3'teki "DSR ≥ 0,50, σ_SR = 0,30 sabit" yaklaşımı yerine, banka açılmadan önce (kilit adımı 3, sentetik
   kalibrasyonla birlikte) σ_SR için birden fazla değer (öneri: {0,20; 0,30; 0,50}) ayrı SR₀/DSR ile raporlanır
   ve **hangi değerin/hangi sonucun bağlayıcı sayılacağı kilitten önce, D performansına bakılmadan yazılır.**
   Codex'in canlı yanıtındaki yaklaşım (§3.3 tablosu {1,50; 1,80; 2,38} gibi) örnek alınabilir; sayılar D'ye
   bakılmadan, yalnız istatistiksel gerekçeyle seçilir.

Bu iki karar bağlayıcıdır; §2'deki revizörler değiştiremez.

## 2. Revizyon turunun kapsamı

`CODEX_KIRMIZI_TAKIMI.md`'deki 14 bulgunun (1 OLDURUCU, 12 CIDDI, 1 DUZELTILEBILIR) hepsi kapatılır ya da
gerekçeyle reddedilir (ONKAYIT §4 kuralı, ilk turdaki gibi). Round-1 nihai taslakları
`AKTIF_MODEL/_arsiv/V8_ASAMA4_SENTEZ_20260927_01/round1_nihai/` altında saklanır.

| Bulgu | Düzey | Ana belge | Özet |
|---|---|---|---|
| KC-01 | OLDURUCU | BANKA §3.5, B7 | Rejim-null: blok zincirleme/yeniden bazlama/yaşam döngüsü tanımsız |
| KC-02 | CIDDI | BANKA §3.7, §1.2 | Sentetik kalibrasyon üretecinde serbestlik; sorular kalibrasyondan önce isteniyor |
| KC-03 | CIDDI | CARRY §5.1/5.6, MIMARI §4.7 | Kapı ile mimari farklı carry miktarını ölçüyor (κ/bant farkı, sıfır/sıfır payı) |
| KC-04 | CIDDI | MIMARI §4.3–4.5 | BTC hedge'i isim kırpmasından önce hesaplanıyor; nötrlük bozuluyor |
| KC-05 | CIDDI | CARRY V4, §5.6 | V4 zıt işaretli artıkları birbirine siliyor |
| KC-06 | CIDDI | CARRY §1, K3/K4/K11 | Anlamsızlık nötrlük kanıtı değil; eşdeğerlik testi yok |
| KC-07 | CIDDI | CARRY §8.4/12, MIMARI §1d, BANKA §9 | K1=0,10 yalnız ρ=0'da başabaş; K10'un izin verdiği ρ=0,3'te yetersiz |
| KC-08 | CIDDI | BANKA §3.3 | σ_SR=0,30 doğrulanmamış; DSR tek başına "olasılıksal kanıt" değil — **§1'deki S-c kararıyla çözülüyor** |
| KC-09 | CIDDI | BANKA T4, MIMARI §3.3–3.5 | V≤τ değişmezi hedef/kaldıraçlı/carry nesnelerinde farklı okunuyor |
| KC-10 | CIDDI | BANKA §4, §7.1 | %30 DD sınırını aşan L'nin seçilmesini önleyen kural yok |
| KC-11 | CIDDI | BANKA §5.2–5.5 | D90 yalnız long çöküşünü kapsıyor; short sıkışması/çoklu ölüm yok |
| KC-12 | CIDDI | MIMARI §3.1, §5.2/5.8 | Haftalık carry miktarı yalnız piyasa geçmişinden yeniden üretilemez; devreden emir çelişkisi |
| KC-13 | CIDDI | MIMARI §2.4, §3.2 | Çift bazlı korelasyon matrisi PSD olmayabilir |
| KC-14 | DUZELTILEBILIR | MIMARI §3.3 | "Referans kitap her gün %15" ifadesi M_max ile çelişiyor |

## 3. Roller (ikinci tur)

| Adım | Ajan | Model | Çıktı |
|---|---|---|---|
| 4b-1 | MIMARI revizörü (KC-04, KC-12, KC-13, KC-14 + KC-03/09'un mimari tarafı) | Opus | `MIMARI.md` (yerinde revize) |
| 4b-2 | CARRY revizörü (KC-03, KC-05, KC-06, KC-07 + KC-09'un carry tarafı) | Opus | `CARRY_KAPISI_ONKAYIT_TASLAK.md` (yerinde revize) |
| 4b-3 | BANKA revizörü (KC-01, KC-02, KC-08[§1 kararıyla], KC-09, KC-10, KC-11) | Opus | `BANKA_ONKAYIT_TASLAK.md` (yerinde revize) |
| 4b-4 | Codex'e canlı doğrulama (`codex exec`, aynı bağımsızlık değil — doğrulama turu) | — | `codex_cagrilari/` altına kayıt |
| 4b-5 | Sayı kontrolü (yalnız değişen bölümler) + RAPOR/DURUM/defter güncellemesi | Sonnet | `RAPOR.md` §14, DURUM, defter satırı |

Her revizör round-1 dosyasının TAMAMINI okur, yalnız kendi bulgularını değil, öteki revizörlerin dokunduğu
arayüzleri de (isim tavanı sırası, κ tanımı, T4 değişmezi) tutarlı tutmakla yükümlüdür. Bulguların işlenişi
tablosu her belgenin sonuna eklenir/güncellenir (KC-01…KC-14, karar: DUZELTILDI/KISMEN/ilgisiz).

---

## 4. Sonuç (27 Eylül, aynı gün)

Üç revizör 14/14 bulguyu kapattı (tablo yukarıda). Ana oturum tutarlılık geçişinde bir gerçek arayüz hatası buldu
(T4 harfleri, eksik toplam risk kuralı) ve düzeltti; ρ=0/0,30 sayı karışıklığını netleştirdi. İkinci bir Codex
doğrulama turu (`codex exec`, aynı gün) bir CIDDI bulgu daha buldu (rejim-null Y1/N3 kendi içi çelişkisi); bu da
düzeltildi. Ayrıntı: [RAPOR.md §14](RAPOR.md). Adım 4b-4 (Codex doğrulaması) ve 4b-5 (bu belge + RAPOR + defter)
tamamlandı. Aşama burada durur; kullanıcı değerlendirmesi bekleniyor.
