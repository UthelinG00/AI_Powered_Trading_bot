# v8 sentetik kalibrasyon raporu (Adım 3, 3.12)

TOPLAMA.json sha256: `cd65c3cde9f163712b3666726fc6aeef07edfc4245c81422580717caa4b2a0ca`; durum: **TAMAM** (Düzey 1: TAMAM; Düzey 2: TAMAM).

## Kanıt zinciri

| alan | değer |
|---|---|
| KOD_DONDURMA sha256 | 0a6ab6b4b5802b5a8d8b9b6bc2e380b195c2ec09b3fbe47e29de5e446bcf521b |
| HAR sonuç sha256 | c5602b2b3350fdb7e07a7105b58a4e08ef9c6b484e9effdf0307cb3a9b8d666a |
| betik sha256 | 926e05465d8238dd2c2439146e9b32bd813ca6006564d679f64ef43f18e85011 |
| kimlik kod | c442f5ba779c36411317662dc8422a1a296a5a1d1b6b71369eee6f15356c69e0 |
| kimlik motor | 7e2320f4073164c15d298be40a713caaf234130c6cd94f6d45e10a650b7b597f |
| kimlik parametre | 80c67909654742210e318b1b4e37da77edf9f007a35f26c61faf600100700a6f |
| kimlik ortam | python 3.12.14; numpy 2.5.1 |
| kaynak bitis_sonuc_sha256 | 326c1df79625a33ae9b67a6818972ef97fb975ae905346a2c153722033c5ee07 |
| kaynak duzey1_is_listesi_sha256 | 9d0d5823e17ff979e5fe8da647c2ffb88746118e71b86f2cc7cb0f9a08dc0a4f |
| kaynak duzey2_is_listesi_sha256 | ae68a5eb3051a52af814bce0da06a57da47f49a1e4cac066172b48e3992e6e8f |
| kaynak defter_sha256 | 54301c1504142dc7f626979aa3bc7b1b216e550bec6ab6fc7cc38dc5a434ee95 |
| kaynak defter_dondurma_sha256 | 3aab2d2caf54f3bcff996049b564ec35993266f70751c40b34c8e46e2c1b5d10 |
| kaynak duzey2_tuketilen | {"is_listesi_sha256": "ae68a5eb3051a52af814bce0da06a57da47f49a1e4cac066172b48e3992e6e8f", "ek_liste_sha256": "7385b3b41c2874b4d486e366d9e2161f293f8e8bb712c3cfdb2ccdb2b2d72569", "birim_dosyalari": {"dosya": 5140, "birlesik_sha256": "43e421d31064f055de2cf4d389294acdc0df9772169841be7a31dd6b24450318"}} |
| kaynak duzey1_tuketilen | {"ozet_sha256": "c415e5fdc7f3e7bbe1131a28cc6acdb3843d80d4438d80fb62869e39dde3a875", "is_listesi_sha256": "9d0d5823e17ff979e5fe8da647c2ffb88746118e71b86f2cc7cb0f9a08dc0a4f", "dosya": 256, "birlesik_sha256": "b818310cd9000fd289b738ce3b956da6d5f487ecec60043f28757d0e33647d00"} |

## 1. Düzey 1 kararları (§3.3 kuralları; BANKA §3.7)

| alan | değer |
|---|---|
| σ_SR_bağ | 0.300 |
| σ kaynağı | varsayim |
| N | 329 |
| sigma_sr | 0.300 |
| b2_bagli | evet |
| d | 0.900 |
| b3_esik | 0.300 |
| b4_esik | 0.300 |
| e_b5 | — |
| k_b6 | 2 |
| e_b10 | — |

**σ_SR = 0,30 varsayımdır, doğrulanmadı**

Karar kaydı (ayar başı kabul oranları TOPLAMA.json içinde; ortalaması aşağıda):

| alan | değer |
|---|---|
| e_b5_ham | inf |
| e_b10_ham | 0.800 |
| k_b6 | 2 |
| N | 329 |
| sigma_sr_bag | 0.300 |
| b2_guc_d050_sr1 | 0.574 |
| durum | TAMAM |
| denemeler | [{"ayarli": false, "d": 0.5, "en_kotu_far_sr0": 0.111, "tamam": false}, {"ayarli": false, "d": 0.75, "en_kotu_far_sr0": 0.0595, "tamam": false}, {"ayarli": false, "d": 0.9, "en_kotu_far_sr0": 0.021, "tamam": true}] |

### P(KABUL | gerçek SR) — Düzey 1, 128 ayar ortalaması

| SR | 0 | 0.3 | 0.5 | 0.8 | 1 | 1.2 |
|---|---|---|---|---|---|---|
| P(KABUL) | 0.008 | 0.023 | 0.044 | 0.102 | 0.168 | 0.257 |

### B seyreltme (carry katkısı; rapor)

| ρ; SR_C | 0 | 0.3 | 0.5 | 0.8 | 1 | 1.2 |
|---|---|---|---|---|---|---|
| rho=0.0;SR_C=-0.3 | 0.005 | 0.015 | 0.028 | 0.068 | 0.116 | 0.183 |
| rho=0.0;SR_C=0.0 | 0.008 | 0.021 | 0.038 | 0.090 | 0.147 | 0.226 |
| rho=0.0;SR_C=0.3 | 0.011 | 0.028 | 0.051 | 0.116 | 0.183 | 0.272 |
| rho=0.3;SR_C=-0.3 | 0.006 | 0.015 | 0.026 | 0.059 | 0.097 | 0.152 |
| rho=0.3;SR_C=0.0 | 0.008 | 0.019 | 0.034 | 0.076 | 0.122 | 0.186 |
| rho=0.3;SR_C=0.3 | 0.011 | 0.026 | 0.045 | 0.097 | 0.152 | 0.225 |

B9 geçme oranı (SR = 1,0; ayar ortalaması): 0.943

### R16 kalem-kâğıt tablosu (η = 1, γ₃ = 0, γ₄ = 3)

| T yıl | σ_SR | SR₀ yıllık | d=0,50 | d=0,75 | d=0,90 | d=0,95 |
|---|---|---|---|---|---|---|
| 3.000 | 0.200 | 0.585 | 0.585 | 0.974 | 1.325 | 1.535 |
| 3.000 | 0.300 | 0.877 | 0.877 | 1.267 | 1.617 | 1.827 |
| 3.000 | 0.500 | 1.462 | 1.462 | 1.852 | 2.202 | 2.412 |
| 3.500 | 0.200 | 0.585 | 0.585 | 0.945 | 1.270 | 1.464 |
| 3.500 | 0.300 | 0.877 | 0.877 | 1.238 | 1.562 | 1.757 |
| 3.500 | 0.500 | 1.462 | 1.462 | 1.823 | 2.147 | 2.341 |

## 2. Düzey 2 (§3.7 3. revizyon)

### 2-a: κ = 0, B7'siz kabul (tarama kuralı; güven kanıtı değil)

| mimari | kabul | n | üst sınırın nokta tahmini | Wilson alt | Wilson üst | tarama geçti |
|---|---|---|---|---|---|---|
| A | 0 | 100 | 0.000 | 0.000 | 0.037 | evet |
| B | 0 | 100 | 0.000 | 0.000 | 0.037 | evet |

### 2-b: B7 gücü (betimsel; yalnız M = A, ayar başına 10 temel yol × 50 null yolu)

Ayarlar: 0 = κ 0 (trendsiz kontrol); 1 = (κ 0,0262; HL 30); 2 = (0,0262; 90); 3 = (0,0523; 30); 4 = (0,0523; 90).
"taban + B7 q95": birincil koşudan hesaplanabilen ve bağlayıcı kalan ölçütler (B2, B4, B6, B8, B11) ile B7 birlikte;
B3 ve B9 bu sütunda yoktur.

| ayar | n | B7 q90 | B7 q95 | taban + B7 q95 | sıra yüzdeliği ort | ortak pay |
|---|---|---|---|---|---|---|
| 0 | 10 | 0.100 [0.018, 0.404] | 0.100 [0.018, 0.404] | 0.000 [0.000, 0.278] | 0.496 | 0.985 |
| 1 | 10 | 0.400 [0.168, 0.687] | 0.200 [0.057, 0.510] | 0.000 [0.000, 0.278] | 0.586 | 0.985 |
| 2 | 10 | 0.600 [0.313, 0.832] | 0.400 [0.168, 0.687] | 0.100 [0.018, 0.404] | 0.692 | 0.985 |
| 3 | 10 | 0.300 [0.108, 0.603] | 0.200 [0.057, 0.510] | 0.000 [0.000, 0.278] | 0.718 | 0.984 |
| 4 | 10 | 0.100 [0.018, 0.404] | 0.000 [0.000, 0.278] | 0.000 [0.000, 0.278] | 0.536 | 0.984 |

## 3. Kararlar ve gerekçe

Kurallar BANKA_ONKAYIT_TASLAK §3.3 ve §3.7'dedir; aşağıdakiler bu kuralların mekanik çıktısıdır (hiçbiri yorumla
seçilmedi).

1. **σ_SR_bağ = 0,30, kaynak varsayım.** REV1 deneme kaydı deneme başına Sharpe taşımıyor (yalnız aile başına sayı); kullanılabilir deneme 0 < 30, kural varsayımı verir (`kalibrasyon/sigma_sr.py`). **σ_SR = 0,30 varsayımdır,
   doğrulanmadı.** Duyarlılık R16'da (σ ∈ {0,20; 0,30; 0,50}).
2. **e_B5 = rapor.** Ham eşik ∞: hiçbir ızgara değeri 128 ayarın hepsinde P(B5 geçer | SR_ref) ≥ 0,95 sağlamadı.
   §3.7 kuralı gereği (e_B5 > %60) **B5 rapora iner**; bankada bağlayıcı değildir.
3. **e_B10 = rapor.** Ham eşik 0,80 > 0,40 üst sınırı → **B10 rapora iner** (tek coin çıkarma tablosu R olarak yazılır).
4. **k_B6 = 2.** "Her ayarda, SR_ref'te yolların en az %90'ında dört dilimin en az üçü pozitif" koşulu sağlanmadı;
   kural 2'yi verir.
5. **B2 bağlayıcı.** P(B2 geçer, d = 0,50 | SR = 1,0) = 0,574 ≥ 0,25 (§3.3 kural 2).
6. **d\* = 0,90.** Birleşik P(KABUL | SR = 0)'ın ayarlar arası en kötü değeri: d = 0,50 → %11,1; d = 0,75 → %5,95;
   d = 0,90 → %2,1 ≤ %5. En küçük sağlayan d seçildi. Tek önceden yazılı ayara (B3 ×2 ve B4 → 0,40) gerek kalmadı; B3 ×2
   ve B4 eşikleri 0,30'dur.
7. **Düzey 2-a (bağlayıcı tarama) geçti.** Bağlayıcı kalan küme (B2 d = 0,90; B3; B4; B6 k = 2; B8; B11) κ = 0'da A'da
   0/100, B'de 0/100 kabul verdi: üst sınırın nokta tahmini 0, Wilson %95 üst ucu %3,7. Kural p̂ ≤ %5 → kilit beklemez.
   Bu tarama kuralıdır; "yanlış kabul %95 güvenle ≤ %5" kanıtı değildir.
8. **B7 kuantili q95** (3. revizyonla sabit). B9 Düzey 2'de yoktur; SR = 1,0'da ayar ortalaması geçme oranı 0,943.

**Bankaya giden bağlayıcı ölçüt seti:** B2 (d\* = 0,90; SR₀ hükümde N_hüküm ile yeniden), B3 (×2 ≥ 0,30, ×3 > 0),
B4 (≥ 0,30), B6 (k = 2), B7 (q95), B8, B9, B11. Rapora inenler: B5, B10 (ve eski B1, B12; §0).

**Güç (asimetrik; §6).** Düzey 1'in P(KABUL | SR) eğrisi **B7'sizdir** (Düzey 1 yol modelinde null yolu yoktur;
ölçüt kümesi B2 d = 0,90, B3, B4, B6, B8, B9, B11); 128 ayar ortalaması: %0,8 (SR 0), %2,3 (0,3), %4,4 (0,5), %10,2
(0,8), %16,8 (1,0), %25,7 (1,2). Tam banka kabulü B7'yi de ister, bu yüzden tam kabul gücü bu eğrinin altındadır ve
doğrudan ölçülmedi. Düzey 2-b'de (yalnız A, 10 yol) trendli ayarlarda B7'nin q95 geçme oranı %0–40, taban ölçütlerle
birlikte %0–10'dur. Sonuç: gerçek SR'ı 1,0 olan bir sistem bile bu sentetik modelde B7'siz kümeyi yaklaşık altıda bir
geçer; B7 ile oran daha da düşer. Bankanın RET'i "sistem kötü" kanıtı değildir. KABUL'ün yanlış olma olasılığı κ = 0
taramasında düşük çıktı (2-a), ama bu yalnız bu sentetik üreteç için geçerlidir. B mimarisinde carry'nin katkısı
seyreltme tablosunda: SR_C < 0 ve ρ > 0 kabul olasılığını düşürür.

## 4. Sınırlar

- Sayılar yalnız bu sentetik üreteç (30 coin, §3.7 parametreleri) için geçerlidir; gerçek piyasanın dağılımını temsil
  etmez.
- σ_SR_bağ varsayımdır; gerçek deneme dağılımı daha genişse DSR çıtası düşük, darsa yüksek kalır (R16).
- Düzey 2-a 100 yol, 2-b ayar başına 10 yol: Wilson aralıkları geniştir (2-b'de ± ~25–30 puan).
- B7'nin gücü düşüktür (2-b: trendli ayarlarda q95 geçme %0–40). Bu, §3.5 "Bilinen sınırlar"daki "B7 gerçek trendi
  kesebilir" riskinin kaba büyüklüğüdür; hiçbir eşiği değiştirmez. (2-b'deki "ortak pay" ≈ 0,985, blok atamalarının
  ortak permütasyonu izleme payıdır, yani kesitsel eş hareketin korunmasını ölçer; null yolunun gerçek yola
  benzerliği değildir.)
- Platform eşitliği sınaması dizüstü ile sunucu arasında kayan nokta düzeyinde fark gösterdi; bu yüzden Düzey 2'nin
  tamamı tek platformda (sunucu) koşuldu. Belirlenimcilik platform içindedir; banka koşusu ve kuru koşu karşılaştırması
  aynı platformda yapılmalıdır.
- B5 ve B10 rapora indiği için bankada epizot yoğunlaşması ve tek coin bağımlılığı bağlayıcı değildir; rapor
  satırlarıyla okunur.
- REV1 kaydında (`GECMIS/2026_09_19_oncesi/DENEY_TRIAL_REGISTRY.csv`) 28 satırın hepsi `included_primary_dsr = True`;
  ilk 27 satırın `trial_count` toplamı 159, son satırın değeri de 159'dur (düz toplam 318 = 159 + 159; Codex T26). Son
  satır ayrıntı satırlarının toplam satırıdır; §3.3'ün sabitlediği N_REV1 = 159 doğrudur. V8 defteri kilitte 22 satır:
  19 × 1 + 144 + 5 + 2 = 170; N = 159 + 170 = 329 (kilitte deftere `V8-kapi-sentetik` ve `A4-carry-kapisi` satırları eklendi; toplama N = 329 ile yeniden koşuldu, netleştirme 21 f; kararlar değişmedi).
- B5 A eşdeğerliği (özgün saat funding atfı) kabul koşusuyla 140/140 doğrulandı; B'nin B5'i ve öteki birim türleri bu
  değişiklikten etkilenmez (ön-kayıt `ciktilar/v8_b5_a_esdegerlik_20260930_01/ONKAYIT.md`).

## 5. Görülmüş bilgi

- Kalibrasyon hiçbir D ya da banka verisi kullanmadı; yalnız sentetik üreteç. Bu raporu yazan oturum D P&L'ini ya da
  banka verisini görmedi.
- Üreteç parametrelerinden ρ_f = 0,6 D'deki medyan korelasyona (0,64) yakındır; bu yüzden 0,3 de koşuldu. ℓ_e ve δ, D
  özetlerini görmüş tasarımların yön değişimi ve devir tahminlerinden gelir. φ, s, ν, κ, HL, SR_ref ve Düzey 2 ölçekleri
  istatistiksel ya da motor mekaniği gerekçelidir; σ_M, σ_I ve hacim aralığı motor tabanlarından türetildi (§3.7
  "Görülmüş bilgi").
- Eşik kuralları hiçbir D P&L'ine dayanmaz; kurallar bugünkü sonuçlardan önce yazılıydı (§3.3, §3.7) ve burada yalnız
  mekanik çıktıları sabitlenir.

## 6. İnceleme ve kilit ön koşulları

- Codex T26 (`v8/codex_cagrilari/20260930T26_kalibrasyon_rapor_inceleme_yanit.md`): 10 karar DOĞRU; sayısal bir
  KILIT_BEKLER nedeni yok; 3 ORTA + 1 DÜŞÜK anlatım bulgusu bu sürümde düzeltildi (güç kümesi B7'siz, ortak pay
  yorumu, 2-b ayar tanımı, REV1 sayımı).
- `kilit.onkosullar()` dizüstünde çalıştırıldı (30 Eylül ~21:50 UTC): bitiş, toplama TAMAM, duman, eşdeğerlik ve B5 A
  eşdeğerliği geçti; B5 A kaydındaki güncel kimlikler (kod, motor, parametre, HAR) çalışma anındakilerle aynı.
