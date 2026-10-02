# v8 beyin fırtınası ve geliştirme planı

Bu çalışma planıdır; mühürlü değildir, gerektiğinde güncellenir. Mühürlü olan yalnız banka ön-kaydıdır:
[ONKAYIT.md](ONKAYIT.md) ve `DAMGA.json`.

## Kararlar (kullanıcı, 2026-09-24)

| Konu | Karar |
|---|---|
| Hedef | Yeni model adayı v8. Mutlak getiri; zirveden düşüş en fazla %30 (tasarım hedefi: geri test DD'si ~%15–20) |
| Kapsam | Sınırsız. Kapalı REV1 aileleri yeni gerekçeyle yeniden açılabilir |
| Doğrulama | Mühürlü banka: 80 coin ve Z1/Z2 zaman bölümleri. Tek atış, ardından ileri demo |
| İşleyiş | Her aşama ayrı bir iş akışı; aşama sonunda durulur ve kullanıcıyla değerlendirilir |
| Veri | Ajanlar geliştirme coinlerinin verisini kullanabilir. Her indirme listesi kullanıcı onayına sunulur |
| Roller | CTA yöneticisi, agresif prop trader, kesitsel faktör araştırmacısı, carry/nötr uzmanı, risk mimarı, mikroyapı uzmanı, makro/rejim stratejisti, ML araştırmacısı |
| Codex | Hem bağımsız tasarımcı hem jüri üyesi. Paket aktarımını kullanıcı yapar |
| Model dağılımı | Muhakeme gerektiren işler Opus 5.5'te. Kolay ve mekanik işlerde Sonnet 5 yardımcı ajanlar |

## Aşama 1 sonrası kararlar (kullanıcı, 2026-09-24)

| Konu | Karar |
|---|---|
| Tasarım hedefi | Getiri hedefi yok; **kalite hedefi**: maliyet sonrası en yüksek ve en sağlam Sharpe. Kaldıraç ve DD düzeyini banka testinden sonra kullanıcı, Kelly tablosuna göre seçer (Aşama 1 sonrası sohbet). |
| Kısa vadeli ve yapısal fikirler | Masada; yüksek Sharpe potansiyeli için araştırılır. |
| Metrics verisi (OI/LS/taker) | Şimdilik indirilmez. |
| Spot carry | Kapsam dışı; yalnız USDⓈ-M perp. |

## Aşama 3 sonrası kararlar (kullanıcı, 2026-09-27)

Ayrıntı: [v8_asama4_20260927_01/KARARLAR.md](../v8_asama4_20260927_01/KARARLAR.md).

| Konu | Karar |
|---|---|
| Bankaya giden | Tek mimari, bankadan önce dondurulur. Carry D içi ön-kayıtlı kapıyı geçerse B (trend + küçük sabit carry uydusu), geçemezse A (yalnız trend). A ile B bankada yarışmaz. |
| Hayatta kalan yanlılığı | Ön-kayda açıkça yazılır; delist kaybı −%90 senaryosuyla da raporlanır. Ek test bankası yok. |
| Zamanlama | Aşama 4 hemen, bulut oturumunda ($100 kredi). |

## Aşamalar ve ajanlar

| Aşama | Opus 5.5 | Sonnet 5 (yardımcı) |
|---|---|---|
| 0. Banka mührü | Yok; ana oturum yapar | Yok |
| 1. Araştırma ve veri paketi | 3 araştırmacı: akademik, uygulayıcı, piyasa yapısı. Kanıtı derecelendirir ve sentezler | Kaynak toplayıcılar: yapılandırılmış kaynak özetleri. Veri işleri: indirme listesi, CHECKSUM, eksik ay ve sembol sürekliliği kontrolü, betimsel veri paketinin hesap tabloları |
| 2. Tasarım | 8 rol tasarımcı, birbirini görmeden; ardından çapraz eleştiri | Tasarımları ortak şablona dönüştürme; Codex tasarım paketini hazırlama |
| 3. Jüri | Kâr, kanıt ve uygulama jürileri; kırmızı takım. Puanlar ayrı tutulur, ortalama alınmaz; kural çatışması yalnız etiket olur | Sayı kontrolü: tasarımlardaki rakamların veri paketi ve kaynaklarla tutarlılığı |
| 4. Sentez | 2–3 v8 mimarisi ve banka testi ön-kaydının taslağı | Deneme defteri kaydı, ilerleme dosyası, rapor biçimi |

**Sonnet sınırı:** Sonnet fikir elemez, puanlamaz, tasarım kararı vermez. Yargı gerektiren bir durum çıkarsa
(şüpheli veri, çelişkili kaynak) işaretler; kararı Opus ya da ana oturum verir.

## Limit ve kesinti yönetimi

- Her aşamada kontrol noktası dosyası tutulur: `kontrol_noktasi.py` deseni, `ILERLEME.md`, devam argümanları.
- Tasarımcılar sıfırdan keşfe çıkmaz. Aşama 1 kataloğunu ve ortak veri paketini alır, sınırlı sayıda dosya okur.
- Jüri tasarımları toplu değerlendirir.
- İş akışı başlamadan önce limit saati kontrol edilir.

## Erişim kuralları (ONKAYIT §6'nın özeti)

- **Ajanlara verilecekler:** yalnız `GELISTIRME_EVRENI.json` ve geliştirme dönemi (2023-07-01 → 2026-07-01).
- **Yasak olanlar:**
  - `BANKA_MUHURLU.json` okunmaz.
  - Banka coinleri ve Z1/Z2 dönemleri indirilmez.
  - Banka coinlerine özel araştırma yapılmaz.
- **Banka içeriği:** Sohbete ve raporlara yazılmaz; yalnız sayılar ve hash'ler raporlanır.

## Sonraki adım

Aşama 1'in ilk işi geliştirme verisi indirme listesidir: 122 coin, 2023-07 → 2026-06 aylık 1h klines,
fundingRate ve CHECKSUM dosyaları. Liste, dosya sayısı ve toplam boyutla kullanıcı onayına sunulur. Onaydan
sonra araştırma ve veri keşfi iş akışı başlar.
