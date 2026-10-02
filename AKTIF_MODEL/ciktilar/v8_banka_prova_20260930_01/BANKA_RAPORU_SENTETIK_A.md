> SENTETİK PROVA — performans anlamı yoktur; eşikler yer tutucudur.

# v8 Banka Raporu

## 1. Hüküm

**RET** — mimari **A**

| belge | sha256 |
|---|---|
| SONUC_DAMGA kok | 90bcfec397a2d990dd2073ebe030b3b5b00bc21e70e962faf08eb98b3697a446 |

- Hayatta kalan yanlılığı giderilmedi.
- B2 (DSR) ve birincil Sharpe hayatta kalan yanlılığına göre düzeltilmedi.
- D90, SQ ve DM tek kanallı stres bindirmeleridir; hayatta kalan yanlılığının üst sınırı değildir.

## 2. Bağlayıcı tablo (B2–B11)

| ölçüt | değer | eşik | sonuç | %90 GA |
|---|---|---|---|---|
| B2 | 0.649 | 0.750 | kaldı | — |
| B3 | 2.185 | 0.300 | geçti | [-1.160, 6.035] |
| B4 | 1.093 | 0.300 | geçti | [-2.258, 5.270] |
| B5 | 1.431 | 0.600 | kaldı | — |
| B6 | 3 | 2 | geçti | — |
| B7 | 2.356 | 2.356 | geçti | [-0.990, 6.317] |
| B8 | 2.523 | 0.000 | geçti | [-0.704, 6.364] |
| B9 | -0.278 | 0.000 | kaldı | [-3.794, 4.015] |
| B10 | 1.953 | 0.800 | kaldı | — |
| B11 | 0.027 | 0.300 | geçti | — |

B3 ×3 SR 2.020 (%90 GA [-1.084, 5.671]); eşik > 0.

B6 dilimleri:

| dilim | SR | %90 GA |
|---|---|---|
| Z1 dilim 1 | 10.465 | [6.134, 15.549] |
| Z1 dilim 2 | 5.049 | [1.377, 11.048] |
| Z1 dilim 3 | -4.065 | [-7.089, -0.115] |
| Z1 dilim 4 | 1.210 | [-2.396, 6.108] |

Karar: **RET**

## 3. Birincil sonuç

| SR (R11) | %90 GA | CAGR | vol | MDD | gerçekleşen vol / birim (R7) |
|---|---|---|---|---|---|
| 2.356 | [-0.990, 6.317] | 0.076 | 0.031 | 0.006 | 0.209 |

SR ≥ 0,50: evet (bilgi; eski B1).

Tahminci tanıları (R7):

| satır | değer |
|---|---|
| gerceklesen_vol_orani | 0.209 |
| gozlem | 405 |
| karar_gunu | 27 |
| rv_sigma2_q50 | 0.957 |
| rv_sigma2_q95 | 2.263 |
| rv_sigma2_q99 | 3.001 |
| t4a_disarida_orani | 0.000 |

## 4. DSR

B2 türü: **B**; d* = 0.750; N_hüküm = 330; SR₀ = 0.04594; γ₃ = -0.495; γ₄ = 2.908; η = 1.000; T = 27.

**σ_SR = 0,30 varsayımdır, doğrulanmadı.**

DSR bir performans çıtasıdır; birleşik yanlış kabul §3.7'de ölçüldü (B7 dahil olanı için üst sınırın nokta tahmini ve Wilson aralığı).

R16 duyarlılık tablosu:

| σ|N çarpanı|η | N | dsr | eta | sigma_sr | sr0 |
|---|---|---|---|---|---|
| 0.20|0.8|eta | 264 | 0.678 | 1.000 | 0.200 | 0.030 |
| 0.20|0.8|eta1 | 264 | 0.678 | 1.000 | 0.200 | 0.030 |
| 0.20|1.0|eta | 330 | 0.676 | 1.000 | 0.200 | 0.031 |
| 0.20|1.0|eta1 | 330 | 0.676 | 1.000 | 0.200 | 0.031 |
| 0.20|1.2|eta | 396 | 0.675 | 1.000 | 0.200 | 0.031 |
| 0.20|1.2|eta1 | 396 | 0.675 | 1.000 | 0.200 | 0.031 |
| 0.30|0.8|eta | 264 | 0.651 | 1.000 | 0.300 | 0.045 |
| 0.30|0.8|eta1 | 264 | 0.651 | 1.000 | 0.300 | 0.045 |
| 0.30|1.0|eta | 330 | 0.649 | 1.000 | 0.300 | 0.046 |
| 0.30|1.0|eta1 | 330 | 0.649 | 1.000 | 0.300 | 0.046 |
| 0.30|1.2|eta | 396 | 0.647 | 1.000 | 0.300 | 0.047 |
| 0.30|1.2|eta1 | 396 | 0.647 | 1.000 | 0.300 | 0.047 |
| 0.50|0.8|eta | 264 | 0.595 | 1.000 | 0.500 | 0.075 |
| 0.50|0.8|eta1 | 264 | 0.595 | 1.000 | 0.500 | 0.075 |
| 0.50|1.0|eta | 330 | 0.591 | 1.000 | 0.500 | 0.077 |
| 0.50|1.0|eta1 | 330 | 0.591 | 1.000 | 0.500 | 0.077 |
| 0.50|1.2|eta | 396 | 0.588 | 1.000 | 0.500 | 0.078 |
| 0.50|1.2|eta1 | 396 | 0.588 | 1.000 | 0.500 | 0.078 |
| bag|0.8|eta | 264 | 0.651 | 1.000 | 0.300 | 0.045 |
| bag|0.8|eta1 | 264 | 0.651 | 1.000 | 0.300 | 0.045 |
| bag|1.0|eta | 330 | 0.649 | 1.000 | 0.300 | 0.046 |
| bag|1.0|eta1 | 330 | 0.649 | 1.000 | 0.300 | 0.046 |
| bag|1.2|eta | 396 | 0.647 | 1.000 | 0.300 | 0.047 |
| bag|1.2|eta1 | 396 | 0.647 | 1.000 | 0.300 | 0.047 |

## 5. Rejim dilimleri ve Z2 teşhisi

Z2 ve D segmenti (R10):

| segment | SR | %90 GA | CAGR | vol | MDD | gün |
|---|---|---|---|---|---|---|
| Z2 | 9.121 | [6.045, 13.038] | 0.116 | 0.012 | 0.001 | 5 |
| D | 3.056 | [-0.592, 7.307] | 0.105 | 0.033 | 0.005 | 17 |

## 6. Ayrıştırmalar

Beta ayrıştırması (R2):

| pencere | alfa | artik_katki_yillik | beta_btc | beta_d | btc_katki_yillik | n | t_alfa | t_btc | t_d |
|---|---|---|---|---|---|---|---|---|---|
| birincil | 0.000 | 0.074 | 0.034 | 0.040 | 0.000 | 27 | 0.862 | 1.228 | 2.590 |
| dilim1 | 0.001 | 0.201 | 0.068 | 0.074 | 0.000 | 6 | 4.742 | 4.090 | 3.687 |
| dilim2 | 0.001 | 0.193 | 0.070 | 0.032 | 0.000 | 7 | 1.699 | 1.302 | 0.690 |
| dilim3 | -0.000 | -0.124 | 0.061 | 0.043 | 0.000 | 7 | -1.633 | 3.215 | 3.812 |
| dilim4 | 0.000 | 0.044 | 0.017 | 0.065 | 0.000 | 7 | 2.533 | 1.360 | 5.255 |

Long-beta karşılaştırması (R3):

| satır | değer |
|---|---|
| gun | 27 |
| olcek | 0.170 |
| sr_birincil | 2.356 |
| sr_r3 | -1.008 |
| sr_farki | 3.363 |
| korelasyon | 0.436 |
| beta | 0.436 |
| alfa_gunluk | 0.000 |
| alfa_yillik | 0.088 |
| t_alfa_nw | 1.515 |
| nw_gecikme | 10 |
| nan_yok | evet |

R3 kitabının SR %90 GA: [-4.899, 3.044]

REV1 korelasyonu (R4):

| satır | değer |
|---|---|
| durum | REV1 serisi yok |

## 7. Görülmemiş coinler (B9, R15)

|  | SR | %90 GA | gün |
|---|---|---|---|
| B9 | -0.278 | [-3.794, 4.015] | 32 |
| R15 (D, görülmüş zaman) | 0.633 | [-4.164, 8.510] | 17 |

## 8. Kelly tablosu

Maliyet 1×:

| L | CAGR | vol | SR | SR %90 GA | MDD | boot q50 | boot q95 | P(MDD>%30) | Kelly kesri | %30 DD | MDD D90-1 | MDD D90-2 | MDD D90-4 | MDD SQ-1 | MDD SQ-2 | MDD SQ-4 | MDD DM-1 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 0.5 | 0.040 | 0.016 | 2.524 | [-0.791, 6.342] | 0.003 | 0.006 | 0.008 | 0.000 | 0.007 | uygun | 0.003 | 0.003 | 0.003 | 0.003 | 0.003 | 0.003 | 0.003 |
| 1 | 0.076 | 0.031 | 2.356 | [-0.968, 5.933] | 0.006 | 0.011 | 0.015 | 0.000 | 0.013 | uygun | 0.006 | 0.006 | 0.006 | 0.006 | 0.006 | 0.006 | 0.006 |
| 1.5 | 0.113 | 0.047 | 2.297 | [-1.052, 6.029] | 0.009 | 0.017 | 0.024 | 0.000 | 0.020 | uygun | 0.009 | 0.009 | 0.009 | 0.009 | 0.009 | 0.009 | 0.009 |
| 2 | 0.151 | 0.063 | 2.281 | [-0.944, 5.947] | 0.011 | 0.022 | 0.031 | 0.000 | 0.027 | uygun | 0.011 | 0.011 | 0.011 | 0.011 | 0.011 | 0.011 | 0.011 |
| 2.5 | 0.201 | 0.077 | 2.409 | [-0.940, 6.456] | 0.014 | 0.027 | 0.037 | 0.000 | 0.033 | uygun | 0.014 | 0.014 | 0.014 | 0.014 | 0.014 | 0.014 | 0.014 |
| 3 | 0.267 | 0.089 | 2.708 | [-0.402, 6.544] | 0.016 | 0.029 | 0.040 | 0.000 | 0.038 | uygun | 0.016 | 0.016 | 0.016 | 0.016 | 0.016 | 0.016 | 0.016 |
| 4 | 0.335 | 0.094 | 3.124 | [0.017, 7.073] | 0.016 | 0.028 | 0.038 | 0.000 | 0.040 | uygun | 0.016 | 0.016 | 0.016 | 0.016 | 0.016 | 0.016 | 0.016 |

𝓛* = [0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 4.0]; varsayılan öneri: 4.000.

Maliyet 2×:

| L | CAGR | vol | SR | SR %90 GA | MDD | boot q50 | boot q95 | P(MDD>%30) | Kelly kesri | %30 DD | MDD D90-1 | MDD D90-2 | MDD D90-4 | MDD SQ-1 | MDD SQ-2 | MDD SQ-4 | MDD DM-1 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 0.5 | 0.038 | 0.016 | 2.397 | [-0.744, 6.278] | 0.003 | 0.006 | 0.008 | 0.000 | 0.007 | uygun | 0.003 | 0.003 | 0.003 | 0.003 | 0.003 | 0.003 | 0.003 |
| 1 | 0.070 | 0.031 | 2.185 | [-1.124, 5.890] | 0.006 | 0.011 | 0.016 | 0.000 | 0.014 | uygun | 0.006 | 0.006 | 0.006 | 0.006 | 0.006 | 0.006 | 0.006 |
| 1.5 | 0.103 | 0.047 | 2.120 | [-1.188, 5.951] | 0.009 | 0.017 | 0.024 | 0.000 | 0.021 | uygun | 0.009 | 0.009 | 0.009 | 0.009 | 0.009 | 0.009 | 0.009 |
| 2 | 0.138 | 0.063 | 2.096 | [-1.298, 5.989] | 0.012 | 0.023 | 0.033 | 0.000 | 0.029 | uygun | 0.012 | 0.012 | 0.012 | 0.012 | 0.012 | 0.012 | 0.012 |
| 2.5 | 0.184 | 0.077 | 2.218 | [-1.073, 6.021] | 0.014 | 0.028 | 0.040 | 0.000 | 0.035 | uygun | 0.014 | 0.014 | 0.014 | 0.014 | 0.014 | 0.014 | 0.014 |
| 3 | 0.246 | 0.089 | 2.517 | [-0.619, 6.448] | 0.016 | 0.030 | 0.041 | 0.000 | 0.041 | uygun | 0.016 | 0.016 | 0.016 | 0.016 | 0.016 | 0.016 | 0.016 |
| 4 | 0.310 | 0.094 | 2.923 | [-0.070, 6.822] | 0.016 | 0.028 | 0.038 | 0.000 | 0.043 | uygun | 0.016 | 0.016 | 0.016 | 0.016 | 0.016 | 0.016 | 0.016 |

Seçilen L'nin DD değerleri banka örnekleminin içindedir; 𝓛*'ı banka örnekleminden seçmek seçim yanlılığı taşır. Demo ön-kaydı DD beklentisini bootstrap q95 ile yazar; bu iyimser olabilir.

"Blok bootstrap geçmiş getirileri yeniden örnekler. Marjin çağrısı, otomatik kaldıraç azaltma (ADL), tasfiye ve bankada gerçekleşmemiş kuyruk olaylarını üretmez. %30 DD sınırı hiçbir L için garanti edilemez."

## 9. Hayatta kalan yanlılığı

Kanal stresleri (R12, L = 1):

| senaryo | SR | %90 GA | MDD | olay | boş olay |
|---|---|---|---|---|---|
| stressiz | 2.356 | [-0.863, 6.297] | 0.006 | — | — |
| D90-1 | 2.356 | [-0.913, 6.004] | 0.006 | 0 | 0 |
| D90-2 | 2.356 | [-0.955, 6.282] | 0.006 | 0 | 0 |
| D90-4 | 2.356 | [-0.840, 6.129] | 0.006 | 0 | 0 |
| SQ-1 | 2.356 | [-1.070, 6.291] | 0.006 | 0 | 0 |
| SQ-2 | 2.356 | [-0.938, 6.190] | 0.006 | 0 | 0 |
| SQ-4 | 2.356 | [-1.017, 6.372] | 0.006 | 0 | 0 |
| DM-1 | 2.356 | [-0.838, 6.101] | 0.006 | 0 | 0 |

Delist uzlaşma senaryoları (R9):

| h_L | SR | %90 GA | MDD | CAGR | SR farkı | gün |
|---|---|---|---|---|---|---|
| 0.50 | 2.356 | [-0.630, 6.283] | 0.006 | 0.076 | 0.000 | 27 |
| 0.90 | 2.356 | [-1.208, 6.109] | 0.006 | 0.076 | 0.000 | 27 |

Kilitlenen stres bağlayıcılığı: (i) — hash —.

- Hayatta kalan yanlılığı giderilmedi.
- B2 (DSR) ve birincil Sharpe hayatta kalan yanlılığına göre düzeltilmedi.
- D90, SQ ve DM tek kanallı stres bindirmeleridir; hayatta kalan yanlılığının üst sınırı değildir.

## 10. Maliyet ve kapasite

NAV × maliyet ızgarası (R1):

| NAV|maliyet | SR | %90 GA |
|---|---|---|
| 100000|1 | 2.356 | [-0.990, 6.317] |
| 100000|2 | 2.185 | [-1.160, 6.035] |
| 100000|3 | 2.020 | [-1.084, 5.671] |
| 1000000|1 | 2.296 | [-0.940, 6.263] |
| 1000000|2 | 2.108 | [-1.163, 6.174] |
| 1000000|3 | 1.919 | [-1.300, 5.575] |
| 5000000|1 | 2.314 | [-1.117, 5.998] |
| 5000000|2 | 2.125 | [-1.152, 5.829] |
| 5000000|3 | 1.936 | [-1.254, 6.057] |

Devir ve maliyet (R6):

| satır | değer |
|---|---|
| funding_dolgu_sayisi | 0 |
| funding_payi_yillik | -0.005 |
| gecikme_saat_ort | 1.000 |
| gecikme_saat_q50 | 1.000 |
| gecikme_saat_q95 | 1.000 |
| gun | 27 |
| icra_artigi_ort | 0.000 |
| icra_artigi_q95 | 0.000 |
| maliyet_payi_yillik | 0.008 |
| niyet | 168 |
| sonraki_karara_yetismeyen_orani | 0.000 |
| tek_yon_devir_yillik | 3.213 |
| ters_kayit_sayisi | 0 |

| niyet kapanışı | değer |
|---|---|
| dolum | 168 |

Tavan bağlama ve aşım (R5):

| satır | değer |
|---|---|
| birim_gunu | 27 |
| gun_sonu | 27 |
| hedefe_ulasilamayan_orani | 0.000 |
| karar_gunu | 27 |
| mmax_baglama_orani | 1.000 |
| s1_asim_orani | 0.000 |
| s1_en_buyuk_asim | 0.000 |
| s2_asim_orani | 0.000 |
| s2_en_buyuk_asim | 0.000 |
| t4a_orani | 0.000 |

—

Lot (R13) ve demo NAV (R14):

| satır | coin | en_buyuk | fark_olan | lot_minnotional_alti_orani | nav_yuzde1_ustu | q50 | q95 | sr_birincil | sr_farki | sr_lot_kapali |
|---|---|---|---|---|---|---|---|---|---|---|
| R13 | — | — | — | — | — | — | — | 2.356 | 0.007 | 2.349 |
| R13b | 2 | 45.292 | — | — | 0 | 23.015 | 43.064 | — | — | — |
| R14 | — | — | 190 | 0.411 | — | — | — | — | — | — |

Lot kapalı SR %90 GA: [-0.925, 6.193]

## 11. Veri ve teknik

Veri denetimi (T2; VERI_DENETIM.json):

—

T2: —

| satır | değer |
|---|---|
| prova | sentetik |

## 12. Güç

Kalibrasyon (§3.7; "tarama kuralı, güven kanıtı değil"):

| satır | değer |
|---|---|
| not | sentetik prova; kalibrasyon toplanmadi |

Rejim-null tanıları (R17):

| sayım | gercek | null_ort | null_q5 | null_q95 |
|---|---|---|---|---|
| maske_gunu | 24 | 24.000 | 24.000 | 24.000 |
| dolgu_saati | 0 | 0.000 | 0.000 | 0.000 |
| bosluk_saati | 0 | 0.000 | 0.000 | 0.000 |
| evren_ort | 15.000 | 15.000 | 15.000 | 15.000 |
| ortak_pay | — | 1.000 | 1.000 | 1.000 |

## 13. Sınırlar

- asimetrik güç
- korelasyonlu kesit
- hayatta kalan yanlılığı
- mark vekili (uzlaşma damgası T için [T−1h, T) barının kapanışı; MIMARI §2.1)
- ADL/marjin modellenmedi
- tarihsel sembol filtresi yok
- B'nin funding/fiyat ayrımının gücü düşük
- B, fiyattan gelmediği gösterildi demek değildir.
