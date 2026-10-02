# v8 sentetik kalibrasyon raporu (Adım 3) — TASLAK

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

### 2-b: trendli yollarda B7 gücü (betimsel)

| ayar | n | B7 q90 | B7 q95 | taban + B7 q95 | sıra yüzdeliği ort | ortak pay |
|---|---|---|---|---|---|---|
| 0 | 10 | 0.100 [0.018, 0.404] | 0.100 [0.018, 0.404] | 0.000 [0.000, 0.278] | 0.496 | 0.985 |
| 1 | 10 | 0.400 [0.168, 0.687] | 0.200 [0.057, 0.510] | 0.000 [0.000, 0.278] | 0.586 | 0.985 |
| 2 | 10 | 0.600 [0.313, 0.832] | 0.400 [0.168, 0.687] | 0.100 [0.018, 0.404] | 0.692 | 0.985 |
| 3 | 10 | 0.300 [0.108, 0.603] | 0.200 [0.057, 0.510] | 0.000 [0.000, 0.278] | 0.718 | 0.984 |
| 4 | 10 | 0.100 [0.018, 0.404] | 0.000 [0.000, 0.278] | 0.000 [0.000, 0.278] | 0.536 | 0.984 |

## 3. Kararlar ve gerekçe

> **TASLAK — raporu yazan oturum doldurur.**

## 4. Sınırlar

> **TASLAK — raporu yazan oturum doldurur.**

## 5. Görülmüş bilgi

> **TASLAK — raporu yazan oturum doldurur.**
