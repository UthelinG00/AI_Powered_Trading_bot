# v8 Aşama 4: başlangıç kararları

Tarih: 2026-09-27. Girdi: [Aşama 3 jüri raporu](../v8_asama3_20260926_01/JURI_RAPORU.md),
[Codex jürisi](../v8_asama3_20260926_01/CODEX_JURISI.md),
[ana oturum özeti](../v8_asama3_20260926_01/ANA_OTURUM_OZETI.md).

Bu belge Aşama 4 iş akışından ÖNCE yazıldı. Aşama 4'ün kendi ön-kaydı (`ONKAYIT.md`)
bu kararlara dayanır ve iş akışı başlamadan yazılır.

## 1. Kullanıcı kararları (27 Eylül)

Kullanıcı, ana oturumun üç önerisini aynen kabul etti.

1. **Bankaya tek mimari gider.** Mimari bankadan önce dondurulur. A ile B bankada yarışmaz.
   - Carry, D içinde ön-kayıtlı bir kapıyı geçerse nihai mimari **B** olur: trend ve küçük, sabit bütçeli carry uydusu.
   - Kapı, carry getirisinin funding'den mi yoksa fiyat bileşeninden mi geldiğini ayrıştırır.
   - Kapıyı geçemezse nihai mimari **A** olur: yalnız trend.
   - Nihai mimari B olursa, bankada A'nın sonucu yalnız ayrıştırma olarak raporlanır; seçim için kullanılmaz.
   - Kapının tanımı ve eşikleri, kapı koşusundan önce ön-kayda yazılır.
2. **Hayatta kalan yanlılığı ön-kayda açıkça yazılır.**
   - Banka ≥36 ay geçmişli coinlerden seçildi. Z1'de listelenip ölen coinler bankada yok.
   - Mühür değişmez. Delist kaybı, tasarımların küçük cezalarına ek olarak −%90 senaryosuyla da raporlanır.
   - Ek bir test bankası kurulmaz.
3. **Aşama 4 hemen başlar, bulut oturumunda.** $100 bulut kredisi kullanılır. Yerel haftalık kota %92'deydi.

## 2. Ana oturumun teknik kararları

Bunlar 26–27 Eylül'de kullanıcıya bildirildi; kullanıcı itiraz etmedi. Sentez bunları
uygular. Değiştirecekse gerekçesini yazar.

- **Trend çekirdeği:** CTA ile Codex çekirdekleri neredeyse aynı. Biri gerekçesiyle dondurulur, öteki yalnız betimsel kalır. Codex'in ilkeleri korunur: zayıf sinyali büyütmemek, bant kenarına işlem, kısmi dolumun açık taşınması, PIT delist.
- **Risk tahmincisi:** Başlangıç standardı basit bir tahmincidir (EWMA). HAR ancak bankadan önce, P&L'e bakmadan, QLIKE ile seçilip dondurulursa girer. Bankada tahminci seçimi yapılmaz.
- **Birim risk:** %15 iki yönlü bir hedeftir, tavan değil. Yukarı çarpan ön-kayıtlı bir sınırla kısıtlanır.
- **Şok tavanları:** Kaldıraç sonrası NAV'da tanımlanır. Tek altta +%100 sıkışma senaryosu ve asimetrik isim tavanları olur.
- **Kelly:** Banka sonuçları, tavanlar aktifken her Kelly adayı için ayrı raporlanır; her aday için DD tablosu çıkar.
- **ML'nin çıkış kuralı alınmaz.** Eksik ya da donmuş günde önceki kapanıştan kapatmak bakış-ileridir (Codex jürisi: `OLDURUCU`).
- **Carry bütçesi:** Ön-kayıtta tek, sabit ve küçük bir değerdir. Otomatik %30–35 tahsis yapılmaz.
- **Isınma:** Ortak ve ön-kayıtlı bir ısınma kuralı olur. D öncesinden veri alınmaz.
- **Veri boşlukları:**
  - Borsa çapındaki boşlukta yalnız yeni risk durur; tasfiye yapılmaz.
  - Coine özgü boşlukta mevcut kural geçerlidir.
  - Eksik funding en kötü oranla doldurulur.
- **Deflated Sharpe:** Deneme sayısına REV1'in 159 denemesi ve v8 defterinin bütün satırları girer.
- **Muhasebe ve maliyet:** Funding ile dolum için olay sırası tanımlanır. Mark fiyatının yerine 1h kapanış kullanılır; bu vekil ön-kayda yazılır. Maliyet modelinde şunlar olur:
  - karekök etki terimi,
  - stres günü çarpanı,
  - NAV ızgarası (0,1 / 1 / 5M),
  - REV1 ile korelasyon raporu.
- **Kabul ölçütleri** şunları içerir:
  - rejim dilimleri (2020, 2021, 2022, 2023H1, Z2),
  - "en iyi yıl hariç" Sharpe,
  - en iyi 3 epizodun payı,
  - rejim-null karşılaştırması,
  - maliyet 3×,
  - görülmemiş coinler ayrı.

## 3. Aşama 4'ün çıktıları

V8_PLAN'daki Aşama 4 satırı bu kararlarla şöyle daraltıldı:

1. `ONKAYIT.md`: Aşama 4 iş akışının ön-kaydı. İş akışından önce yazılır.
2. `MIMARI.md`: nihai v8 mimarisinin formül düzeyinde tarifi. İçinde mimari A, B'nin uydu kolu ve ortak motor sözleşmesi olur. Ortak motor sözleşmesi şunları kapsar: hedef ağırlık → bant → lot yuvarlama → emir zinciri, canlı ve geri testte aynı fonksiyon.
3. `CARRY_KAPISI_ONKAYIT_TASLAK.md`: carry'nin D içi kapısının ön-kayıt taslağı. Kapı henüz koşulmaz.
4. `BANKA_ONKAYIT_TASLAK.md`: banka testi ön-kaydının taslağı. Hayatta kalan yanlılığı bölümü de burada.
5. `RAPOR.md` ve deneme defteri satırı.

Aşama sonunda durulur ve kullanıcıyla değerlendirilir. Motor yazımı, D içi doğrulama ve banka koşusu Aşama 4'e dahil değildir.
