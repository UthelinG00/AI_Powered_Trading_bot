# Aşama 4 açık sorularının yanıtları

Tarih: 2026-09-27. Bu belge, kilit sırasının Adım 1'idir (ASAMA4B_KARAR.md §2 / BANKA_ONKAYIT_TASLAK.md §1.2): üç
belgedeki (MIMARI, CARRY_KAPISI_ONKAYIT_TASLAK, BANKA_ONKAYIT_TASLAK) bütün açık kullanıcı soruları burada
yanıtlanır. Yanıtlar D'ye ve banka içeriğine bakılmadan verildi. Bu belge Adım 2'de (HAR seçimi) ve Adım 4'te
(ön-kayıt kilidi) diğer belgelerle birlikte hash'lenir.

Soru numaraları RAPOR.md §9'daki birleştirilmiş tabloyla aynıdır.

## Kullanıcı kararları (doğrudan sorulan 4 soru)

| # | Soru | Karar | Not |
|---|---|---|---|
| 5 | exchangeInfo tek anlık görüntüsüne onay | **Evet.** | Salt okuma, herkese açık uç nokta, emir verilmez. Görüntü alınınca hash'lenir ve `SEMBOL_FILTRELERI.json` olarak kaydedilir; alınma anı (D'ye bakılmadan, banka açılışından önce) raporlanır. |
| 6 | REV1'in D dönemi günlük getirisi v8'e verilebilir mi | **Evet.** | REV1 süreci kendi D dönemi (2023-07-01→2026-07-01) günlük getiri serisini üretip tek yönlü aktarır. v8 REV1 motoruna dokunmaz, REV1 süreci de v8'e dokunmaz. E3/Z2 verisi bu kapsamda değildir, yasak kalır. Aktarılan seri ve hash'i R4 raporunda belgelenir. |
| 17 | Banka değerlendiricisi ve Codex'in rolü | **Yeni, tasarıma katılmamış oturum + Codex bağımsız hash doğrulaması.** | BANKA_ONKAYIT_TASLAK §2.1'deki rol tanımı aynen uygulanır: değerlendirici oturum yalnız dondurulmuş depo, ön-kayıt, `banka_sec.py`, `DAMGA.json`, drand turu, `SECIM.json`, `uygun_evren.json` alır; tasarım belgelerini almaz. Codex aynı girdilerle hash'leri ve birincil sayıları içerik görmeden yeniden üretir. |
| 19 | Kör hüküm anahtar çifti | **Kabul; kullanıcı üretir.** | Motor yazımı (Adım 0) sırasında üretim adımları (age/X25519, tek komut) ayrıca anlatılır. Açık anahtar `DONDURMA.json`'a girer. |

## Ana oturum kararı (teknik/istatistiksel; D'ye bakılmadan, belgedeki gerekçeli varsayılan kabul edildi)

Aşağıdakiler düşük riskli, tersine çevrilebilir, saf mühendislik/istatistik seçimleridir; hiçbiri D performansına
bakılarak verilmedi. Her biri ilgili belgede zaten gerekçeliydi.

| # | Soru | Karar |
|---|---|---|
| 1 | Kapı mı, kapısız A mı | **Kapı → A/B kalır.** Kullanıcı kararı, ASAMA4B_KARAR.md §1 (bu belgeden önce verildi). |
| 2 | Birim risk yorumu | **Tam sinyal referans kitabı** (MIMARI'nin önerdiği). Codex ilkesiyle (zayıf sinyal büyütülmez) uyumlu. |
| 3 | DD çarpanı | **Kabul: çekirdeğe alınmaz.** %30 sınırı Kelly tablosuyla kaldıraç seçimine bırakılır (BANKA §4/§7.1'deki bağlayıcı 𝓛* kuralı bunu zaten operasyonelleştiriyor). |
| 4 | Birincil NAV | **0,1M USDT.** R1'de 1M/5M ayrıca raporlanır; kaldıraç/NAV seçimi bankadan sonra kullanıcıda kalır. |
| 7 | S4 yalnız B'de mi | **Yalnız B.** A'da alt short tavanı %4 kalır. |
| 8 | Kapının funding/fiyat ayrıştırması yeterli mi | **Yeterli kabul edildi, sınırıyla birlikte.** CARRY revizyonu (K1/K3/K4/K9/K11) ve Codex'in ikinci doğrulaması ("kazanç atfetme sorunu karşılanmış, risk tamamen giderilmemiş") sonrası: kapı artık gözlenen fiyat KAZANCını kredilendirmiyor (yalnız kaybı düşüyor) ve K11 dört faktöre karşı test ediyor. Kalan sınır (negatif beklenen getirili, örneklemde şans eseri pozitif görünen bir fiyat bahsinin hâlâ sızabilmesi) CARRY §6.4/§8'de açık yazılı; bu, kapının gücü düşük olduğu için kabul edilen bir kalıntı risktir, ek düzeltme istenmiyor. |
| 9 | K1 eşiği | **Korelasyona bağlı formül** (CARRY 2. tur revizyonu, K1\* = 0,85·g(ρ_K1, 1/3), Codex'in KC-07 bulgusuyla teyitli). v1'deki sabit 0,10 önerisi bu formülle değiştirildi; bu formül zaten "0,10" sorusunun yerini aldı. |
| 10 | K2 eşiği | **3,0** (görülmüş bilgiye karşı daha katı). |
| 11 | Netleme kazancı carry'ye yazılmasın | **Kabul** (muhafazakâr). |
| 12 | D90 bağlayıcı değil | **Kabul, rapor (R12).** Ayrıca short sıkışma stresi (SQ) ve çoklu ölüm (DM) senaryoları eklendi (KC-11); bunlar da rapor. |
| 13 | Kapı NAV'ı banka birincil NAV'ına bağlı | **Kabul.** |
| 14 | DSR eşiği | **Kalibre edilmiş σ_SR duyarlılık tablosu.** Kullanıcı kararı, ASAMA4B_KARAR.md §1 (bu belgeden önce verildi); sabit 0,50/0,90 önerilerinin ikisi de yerini bu tabloya bıraktı. |
| 15 | Birincil örneklem yalnız Z1 | **Onaylandı.** Z2 yalnız teşhis. |
| 16 | Z2_son = 2026-09-24 00:00 UTC | **Doğru.** |
| 18 | Kelly ızgarası {0,5;1;1,5;2;2,5;3;4} | **Yeterli.** |
| 20 | Kısa ömürlü 20 coin | **Bilgi amaçlı; karar gerekmiyor.** Mühür değişmez (kullanıcının önceki kararı); konu yeniden açılırsa ayrı ön-kayıt gerekir. |
| 21 | Deneme sayısı: `A2-mikroyapi`/`A2-ml` | **144 ve 5 olarak sayılır.** `V8_DENEME_DEFTERI.csv` bu kararla güncellendi (satırlar 144/5; önceki hâli `_arsiv/V8_ASAMA4_SENTEZ_20260927_01/defter_144_5_oncesi/`'de). Bugünkü N_v8 = 161 (13 satır + A4b-sentez); kesin N, dondurma anında hesaplanır. |

## Özet

21 sorunun tamamı yanıtlandı: 4'ü kullanıcı kararı, 17'si ana oturumun belgedeki gerekçeli varsayılanı kabul
etmesiyle. Hiçbir yanıt D performansına ya da banka içeriğine bakılarak verilmedi. Kilit sırasının Adım 1'i
tamamlandı; sıradaki adım Adım 2 (HAR/EWMA seçimi, P&L'siz) ve Adım 0 (motor yazımı, sentetik fikstür testleri) —
ikisi de bu belgenin dışında, ayrı bir başlangıç gerektirir.

## Sonradan eklenen kullanıcı kararı (29 Eylül; Adım 3'ün hiçbir koşusundan önce)

BANKA_ONKAYIT_TASLAK §1.2 kalibrasyonla ilgili kullanıcı kararlarının bu belgeye eklenmesini ister. Aşağıdaki karar bir
kalibrasyon çıktısına bağlı değildir: hiçbir kalibrasyon, D P&L'i ya da banka verisi üretilmeden, yalnız hesap maliyetine
bakılarak verildi.

| # | Soru | Karar | Not |
|---|---|---|---|
| 22 | BANKA §3.7 Düzey 2 yazıldığı haliyle ~255.600 tam motor koşusu (~15.000–30.000 CPU saati) ister; uygulanamaz. Ne yapılsın? Seçenekler: (1) B7 q95'e sabit, Düzey 2 küçük betimsel ölçüm; (1+) aynısı + κ = 0'da null'suz motor kontrolü; (2) küçültülmüş Düzey 2 (20 yol × 50 null); (3) motoru 10× hızlandırıp tasarımı koru | **(1+)** — kullanıcı: "1+ yı onaylıyorum" | B7 eşiği q95'e sabit. Düzey 2-a: κ = 0'da 100 yolda A ve B için B7'siz birleşik yanlış kabul (B7 dahil olanın üst sınırı), > %5 → kilit bekler. Düzey 2-b: B7'nin gücü betimsel (yalnız A, 5 ayar × 10 yol × 50 null). Koşu parçalar halinde yapılabilir (kesinti ve devam kuralı). Metin: BANKA_ONKAYIT_TASLAK §0.2 ve §3.7 (3. revizyon); öncesi `_arsiv/V8_BANKA_DUZEY2_20260929_01/`. |

## Kilit öncesi tutarlılık taraması (1 Ekim 2026; 4.02)

Kilit öncesi okumada CARRY_KAPISI_ONKAYIT_TASLAK §13'ün iki sorusunun bu belgede ayrı satırı olmadığı görüldü. İkisi de
belgede gerekçeli varsayılanı olan teknik/istatistiksel seçimdir; ana oturum, D P&L'i (kapı koşulmadı) ve banka
içeriği görülmeden, varsayılanı kabul etti. Kullanıcı kilitten (4.06) önce değiştirebilir; kilitten sonra değişmez.

| # | Soru | Karar | Not |
|---|---|---|---|
| 23 | CARRY §13.6: kapının delist senaryoları (h_L %50, %90) bağlayıcı değil | **Kabul: rapor.** | Gerekçe risk tercihi ve önceden belirlenmiş kapsamdır (CARRY §15 madde 16 b; "olay sayısı 30'dan az" gerekçesi Codex T27 ile geri çekildi). K1 değeri iki senaryoda raporlanır; delist kuyruğu bankada R9/R12'dir. |
| 24 | CARRY §13.8: eşdeğerlik toleransları δ_b = 0,30 (K11), β toleransı 0,15 (K9), δ_P = %4 (K3/K4, yalnız rapor) | **Kabul (varsayılan).** | Toleranslar 2. turda ekonomik gerekçeyle, D'ye bakmadan konuldu (CARRY §0 madde 3, §6.4, §8.3); K3/K4'ün bağlayıcı rolü "fiyat kazancı kredilenmez" kuralına devredildiğinden δ_P yalnız rapordur. |
| 25 | Durum notu | **#5 ve #19 uygulandı.** | #5: exchangeInfo görüntüsü 30 Eylül 01:09 UTC alındı (`ciktilar/v8_sembol_filtreleri_20260930_01`). #19: kullanıcı age anahtar çiftini 1 Ekim'de üretti; açık anahtar `age1n4ad8wszp30d6sk54c3sjfyq0pd3xq7py5dhcm8n9uxe9ne24qqq5ac4jl`; resmi age ile uyumluluk sınaması geçti (`ciktilar/v8_age_sinama_20261001`). |

Böylece üç belgedeki bütün açık sorular yanıtlıdır (MIMARI §9 → #1–#7; CARRY §13 → #1, #8–#11, #13, #23, #24; BANKA §11 →
#1, #4–#6, #12, #14–#20).

## Kullanıcı kararı (1 Ekim 2026; kilitten ve kapı koşusundan önce)

| # | Soru | Karar | Not |
|---|---|---|---|
| 26 | Banka KABUL vermezse ne yapılır? | **v8 ilerletilmez; bulgular temize çekilip GitHub'da açık yayımlanır.** | Sonuç ne olursa olsun (KABUL dahil) yayım yapılır; seçici yayım yoktur. Ayrıntı BANKA §7.2. Karar kalibrasyon sonuçları (P(KABUL \| SR = 1) ≈ %17, B7'siz) ve kapı sentetik doğrulaması (P(B) ≤ %0,4) görüldükten sonra, D P&L'i ve banka görülmeden verildi. |
| 27 | Kapı sentetik doğrulaması (BX-08) kapının fiilen kapalı olduğunu gösterdi (P(B) ≤ %0,4; gerçekçi ölçekte ≤ %2,8). Eşikler değişsin mi? | **Hayır (seçenek 1): kapı eşikleri değiştirilmez.** | Kullanıcı kararı, 1 Ekim 2026, kilitten ve kapı koşusundan önce, D P&L'i görülmeden. Kapının büyük olasılıkla A seçeceği önceden bilinerek kabul edildi. Rapor: `ciktilar/v8_kapi_sentetik_20261001/RAPOR.md`. |
