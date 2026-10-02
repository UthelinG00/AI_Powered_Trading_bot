Sen v8 kripto motorunun bağımsız kod inceleyicisisin. Önceki turda Slice 2 kodunu inceleyip 15 bulgu verdin
(AKTIF_MODEL/v8/codex_cagrilari/20260928T_slice2_inceleme_yanit.md). O rapor değişmedi. Bu YENİ bir görev: yazar
bulguları işledi. Görevin düzeltmeleri doğrulamak ve düzeltmelerin yeni bir hata getirip getirmediğine bakmak.
Hiçbir dosyaya yazma; salt okuma komutları çalıştırabilirsin; yalnız metin yanıt ver.

Oku:
- Kendi bulguların: AKTIF_MODEL/v8/codex_cagrilari/20260928T_slice2_inceleme_yanit.md
- Yazarın bulgu tablosu (her bulgu için karar ve düzeltme özeti): AKTIF_MODEL/v8/ILERLEME_SLICE2.md, "Bulgu işleme"
- Düzeltme öncesi kod: AKTIF_MODEL/_arsiv/V8_MOTOR_SLICE2_20260928_02/motor/ ; sonrası: AKTIF_MODEL/v8/motor/
  (farkı `git diff --no-index` ile görebilirsin). Testler: AKTIF_MODEL/v8/testler/ (yeni testler "Codex" / "K<n>"
  adlarıyla işaretli).
- Tasarım: AKTIF_MODEL/ciktilar/v8_asama4_20260927_01/MIMARI.md §2, §3, §5, §6.

Yazarın tartışmalı iki kararı (özellikle değerlendir):
- K1 KISMEN: geri testte kayıt geliş zamanı = damga (arşiv); canlı gecikme, (son işlenen, T] aralığındaki bütün
  kayıtların işlenmesiyle çözüldü; FundingSerisi'ne ayrı geliş zamanı alanı eklenmedi.
- K8 KISMEN: sabit (işlem dışı) isimlerin kendisi bir tavanı ya da T4-d'yi aşıyorsa teknik hata YERİNE serbest
  isimler 0'a iner ve tanılara 'sabit_tavan_ihlali' / 'sabit_t4d_ihlali' yazılır. Gerekçe: işlem dışı coinde emir
  yasak (§3.1), ihlal piyasa kaynaklı; teknik hata koşuyu piyasa verisi yüzünden durdururdu.
Ayrıca yeni yorum kararları: K2 ters kayıt kapsamı = min(önceki gerçek kayıttan geçen süre, 8h); K10 (c) penceresi
son 16 boşluk-dışı saat, karar kaydı son 3 günün boşluk saatlerini taşır (bosluk_gecmis); K11 (d) = toplam eksik
saat > 8; K13 karar anında V60 < 20M coinde yalnız azaltma (|w| ≤ |w0|).

Yanıt biçimi (Türkçe):
## dogrulama
K1..K15 her biri tek satır: `K<n>: KAPANDI | KISMEN | ACIK — gerekçe (≤25 kelime)`.
## tartismali_kararlar
K1 ve K8 için kabul/itiraz, her biri ≤80 kelime; ayrıca K2/K10/K11/K13 yorumlarına itirazın varsa tek satır.
## yeni_bulgular
Düzeltmelerin getirdiği yeni hata varsa `[OLDURUCU|CIDDI|ORTA|DUSUK] dosya.py:satır — başlık` + 2-3 cümle (en fazla 8).
Yoksa "yok".
## genel_hukum
1-2 cümle.

Yasaklar: BANKA_MUHURLU.json, uygun_evren.json, SECIM.json, secim_cikti.json okunmaz, dosya bilgisi de sorgulanmaz
(stat/ls dahil); banka coinleri ve Z1/Z2 verisi araştırılmaz; .env okunmaz; config.py import edilmez; REV1 motoruna
(AKTIF_MODEL/motor/), bota ve sunucuya dokunulmaz; web arama yok; hiçbir dosyaya yazma.
