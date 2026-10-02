# v8: önceden kaydedilmiş, mühürlü bir kripto trend stratejisi testi — sonuç: RET

> **Depo adı hakkında.** Ad bir yapay zekâ işlem botu ima etse de bu depo **bir araştırma kaydıdır**: test edilen strateji
> klasik bir trend kuralıdır ve kendi önceden kaydedilmiş ölçütlerine göre **reddedildi**. Yapay zekâ (Claude oturumları,
> Codex) tasarım, kodlama ve bağımsız denetim sürecinde kullanıldı; strateji bir yapay zekâ modeli değildir.
> *Despite the repository name, this is a research record, not a working AI trading bot; the tested strategy was rejected.*

> **English summary.** A fully pre-registered test of a crypto-futures trend-following strategy (v8). Rules, thresholds,
> code and data identities were hash-locked before any out-of-sample P&L was seen; the evaluation bank (coins and
> periods) was sealed on 2026-09-23 with selection randomness from a *future* drand round; results were encrypted and
> opened blind after a technical audit. **Verdict: REJECT.** Primary-sample Sharpe 0.26 (90% CI −0.68…1.14); the
> deflated Sharpe (N = 331 trials) and a regime-null benchmark were not passed. A carry module was rejected earlier by
> its own pre-registered gate (net carry negative after costs). We publish everything — including the negative
> result — because selective publication is itself a selection bias. Code: MIT. Texts: CC BY 4.0. Language: Turkish.

Bu depo bir **araştırma kaydıdır**, işlem botu değildir. Gerçek parayla kullanılmak için tasarlanmadı ve kendi
ölçütlerine göre **reddedildi**.

## Ne yapıldı

1. **Tasarım (Eylül 2026).** Geliştirme verisinde (D: 122 vadeli kontrat, 2023-07 → 2026-07) bir trend stratejisi ve isteğe
   bağlı bir carry (funding) modülü tasarlandı. Bütün denemeler bir deneme defterine yazıldı.
2. **Mühürlü banka (23 Eylül).** Değerlendirme coinleri ve dönemleri, damga anından *sonra* yayımlanacak bir drand
   turunun rastgeleliğiyle seçildi; seçim betiği ve girdileri hash'lendi.
3. **Kilit (1 Ekim).** Eşikler, ölçütler, parametreler, kod/ortam/veri kimlikleri `KILIT.json`'da hash'lendi. Kalibrasyon
   (sentetik veride ~5.000 tam motor koşusu) eşikleri kilitten önce sabitledi.
4. **Carry kapısı (1 Ekim).** Kör hüküm: **A** — carry maliyet sonrası negatif; banka yalnız trendle gitti.
5. **Kuru koşu (2 Ekim).** Tek atış betiği D üzerinde koşturuldu; bir teknik hata buldu (null değişmez denetiminde
   yanlış alarm). Ön-kayıtlı tek teknik düzeltme hakkıyla düzeltildi (`KILIT_TEKNIK_1`, deneme sayısı +1).
6. **Dondurma ve banka (2 Ekim).** `DONDURMA.json` → tasarıma katılmamış ayrı bir oturum bankayı drand'dan yeniden
   üretti, veriyi indirdi, koşuyu başlattı → sonuçlar kullanıcının açık anahtarına şifreli → kör teknik denetim (T1–T5
   temiz) → hüküm kullanıcının anahtarıyla açıldı: **RET**.

## Sonuç

| ölçüt | değer | eşik | sonuç |
|---|---|---|---|
| B2 Deflated Sharpe (N = 331) | 0,139 | 0,90 | kaldı |
| B3 2× maliyet Sharpe | 0,233 | 0,30 | kaldı |
| B4 | −0,071 | 0,30 | kaldı |
| B7 rejim-null | 0,262 | 0,868 | kaldı |
| B6, B8, B9, B11 | — | — | geçti |

Birincil örneklem: Sharpe 0,26, yıllık %1,2, vol %5,1, en büyük düşüş %7,2. Ayrıntı:
[`AKTIF_MODEL/ciktilar/v8_banka_kosu_20261002/hukum/BANKA_RAPORU.md`](AKTIF_MODEL/ciktilar/v8_banka_kosu_20261002/hukum/BANKA_RAPORU.md)
ve [`SONUC.md`](AKTIF_MODEL/ciktilar/v8_banka_kosu_20261002/SONUC.md).

## Nereden başlamalı

- [`ZAMAN_CIZELGESI.md`](ZAMAN_CIZELGESI.md) — hangi kararın ne zaman, hangi hash'le alındığı.
- [`DOGRULAMA.md`](DOGRULAMA.md) — testleri koşmak, kilidi ve zinciri doğrulamak, veriyi indirmek, bankayı yeniden üretmek.
- Ön-kayıtlar: [`MIMARI`](AKTIF_MODEL/ciktilar/v8_asama4_20260927_01/MIMARI.md),
  [`BANKA_ONKAYIT`](AKTIF_MODEL/ciktilar/v8_asama4_20260927_01/BANKA_ONKAYIT_TASLAK.md),
  [`CARRY_KAPISI_ONKAYIT`](AKTIF_MODEL/ciktilar/v8_asama4_20260927_01/CARRY_KAPISI_ONKAYIT_TASLAK.md).
- Kod: [`AKTIF_MODEL/v8/`](AKTIF_MODEL/v8) (motor, kapı, kalibrasyon, banka betikleri, 59 test dosyası).
- Bağımsız incelemeler: [`AKTIF_MODEL/v8/codex_cagrilari/`](AKTIF_MODEL/v8/codex_cagrilari) (Codex, T1–T34).

## Yayımlanmayanlar ve nedenleri

- **Ham piyasa verisi** (Binance arşivleri): yalnız manifestler (yol + sha256) ve indirme betikleri; veri Binance'ten
  indirilip hash'le doğrulanabilir.
- **Kapı trend mühürü**: carry ön-kaydı trend satırlarını yayımdan hariç tutar (kilitli kural); hash'i kayıtlıdır.
- **Şifreli banka sonuç dosyaları ve anonim anahtar**: çözülmüş sonuç (`hukum/banka_sonuc.json`) ve hash'leri yayımlandı.
- **Ham tasarım taslakları ve önceki model (REV1)**: deneme defteri ve kararlar yayımlandı; REV1'in 159 denemesi N'ye
  kayıt sayısı olarak girer.

## Bilinen sınırlar

- σ_SR = 0,30 bir varsayımdır (doğrulanmadı); hayatta kalan yanlılığı giderilmedi (raporda açıkça yazılı).
- Kilitli iki dosyada yerel bir Windows yolu kalmıştır; hash'leri bozmamak için değiştirilmedi.
- Git geçmişi bu depoda yenidir; özgün tarihli commit'ler özel depodadır ve [`ZAMAN_CIZELGESI.md`](ZAMAN_CIZELGESI.md)
  hash'leriyle listelenir. Dışarıdan bağımsız doğrulanabilen zaman kanıtı banka seçimini bağlayan drand turudur; kilit,
  dondurma ve kör açılış sırası tarafımızca tutulan bir çalışma kaydıdır (beyan).

## Lisans

Kod (`*.py` ve betikler): [MIT](LICENSE). Metinler (ön-kayıtlar, raporlar, belgeler): [CC BY 4.0](LICENSE-DOCS.md).
