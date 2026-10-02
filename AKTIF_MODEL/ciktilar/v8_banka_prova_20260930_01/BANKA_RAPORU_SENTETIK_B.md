> SENTETİK PROVA — performans anlamı yoktur; eşikler yer tutucudur.

# v8 Banka Raporu

## 1. Hüküm

**RET** — mimari **B**

| belge | sha256 |
|---|---|
| SONUC_DAMGA kok | 54670125a9b218cf7a95d6aa5e41653bd32def0daa676225d7561acfeb969207 |

- Hayatta kalan yanlılığı giderilmedi.
- B2 (DSR) ve birincil Sharpe hayatta kalan yanlılığına göre düzeltilmedi.
- D90, SQ ve DM tek kanallı stres bindirmeleridir; hayatta kalan yanlılığının üst sınırı değildir.

## 2. Bağlayıcı tablo (B2–B11)

| ölçüt | değer | eşik | sonuç | %90 GA |
|---|---|---|---|---|
| B2 | 0.789 | 0.750 | geçti | — |
| B3 | 3.980 | 0.300 | geçti | [0.585, 7.755] |
| B4 | 2.412 | 0.300 | geçti | [-0.470, 6.462] |
| B5 | 1.436 | 0.600 | kaldı | — |
| B6 | 3 | 2 | geçti | — |
| B7 | 4.150 | 4.150 | kaldı | [0.910, 8.160] |
| B8 | 3.797 | 0.000 | geçti | [0.155, 7.735] |
| B9 | -0.315 | 0.000 | kaldı | [-4.057, 4.031] |
| B10 | 2.526 | 0.800 | kaldı | — |
| B11 | 0.019 | 0.300 | geçti | — |

B3 ×3 SR 3.810 (%90 GA [0.647, 7.540]); eşik > 0.

B6 dilimleri:

| dilim | SR | %90 GA |
|---|---|---|
| Z1 dilim 1 | 16.655 | [13.140, 24.812] |
| Z1 dilim 2 | 7.547 | [4.906, 13.590] |
| Z1 dilim 3 | -1.883 | [-4.999, 3.795] |
| Z1 dilim 4 | 2.265 | [-1.697, 6.811] |

Karar: **RET**

## 3. Birincil sonuç

| SR (R11) | %90 GA | CAGR | vol | MDD | gerçekleşen vol / birim (R7) |
|---|---|---|---|---|---|
| 4.150 | [0.910, 8.160] | 0.164 | 0.037 | 0.005 | 0.244 |

SR ≥ 0,50: evet (bilgi; eski B1).

Tahminci tanıları (R7):

| satır | değer |
|---|---|
| gerceklesen_vol_orani | 0.244 |

## 4. DSR

B2 türü: **B**; d* = 0.750; N_hüküm = 330; SR₀ = 0.04594; γ₃ = -0.736; γ₄ = 3.094; η = 1.000; T = 27.

**σ_SR = 0,30 varsayımdır, doğrulanmadı.**

DSR bir performans çıtasıdır; birleşik yanlış kabul §3.7'de ölçüldü (B7 dahil olanı için üst sınırın nokta tahmini ve Wilson aralığı).

R16 duyarlılık tablosu:

| σ|N çarpanı|η | N | dsr | eta | sigma_sr | sr0 |
|---|---|---|---|---|---|
| 0.20|0.8|eta | 264 | 0.810 | 1.000 | 0.200 | 0.030 |
| 0.20|0.8|eta1 | 264 | 0.810 | 1.000 | 0.200 | 0.030 |
| 0.20|1.0|eta | 330 | 0.809 | 1.000 | 0.200 | 0.031 |
| 0.20|1.0|eta1 | 330 | 0.809 | 1.000 | 0.200 | 0.031 |
| 0.20|1.2|eta | 396 | 0.808 | 1.000 | 0.200 | 0.031 |
| 0.20|1.2|eta1 | 396 | 0.808 | 1.000 | 0.200 | 0.031 |
| 0.30|0.8|eta | 264 | 0.790 | 1.000 | 0.300 | 0.045 |
| 0.30|0.8|eta1 | 264 | 0.790 | 1.000 | 0.300 | 0.045 |
| 0.30|1.0|eta | 330 | 0.789 | 1.000 | 0.300 | 0.046 |
| 0.30|1.0|eta1 | 330 | 0.789 | 1.000 | 0.300 | 0.046 |
| 0.30|1.2|eta | 396 | 0.788 | 1.000 | 0.300 | 0.047 |
| 0.30|1.2|eta1 | 396 | 0.788 | 1.000 | 0.300 | 0.047 |
| 0.50|0.8|eta | 264 | 0.748 | 1.000 | 0.500 | 0.075 |
| 0.50|0.8|eta1 | 264 | 0.748 | 1.000 | 0.500 | 0.075 |
| 0.50|1.0|eta | 330 | 0.745 | 1.000 | 0.500 | 0.077 |
| 0.50|1.0|eta1 | 330 | 0.745 | 1.000 | 0.500 | 0.077 |
| 0.50|1.2|eta | 396 | 0.743 | 1.000 | 0.500 | 0.078 |
| 0.50|1.2|eta1 | 396 | 0.743 | 1.000 | 0.500 | 0.078 |
| bag|0.8|eta | 264 | 0.790 | 1.000 | 0.300 | 0.045 |
| bag|0.8|eta1 | 264 | 0.790 | 1.000 | 0.300 | 0.045 |
| bag|1.0|eta | 330 | 0.789 | 1.000 | 0.300 | 0.046 |
| bag|1.0|eta1 | 330 | 0.789 | 1.000 | 0.300 | 0.046 |
| bag|1.2|eta | 396 | 0.788 | 1.000 | 0.300 | 0.047 |
| bag|1.2|eta1 | 396 | 0.788 | 1.000 | 0.300 | 0.047 |

## 5. Rejim dilimleri ve Z2 teşhisi

Z2 ve D segmenti (R10):

| segment | SR | %90 GA | CAGR | vol | MDD | gün |
|---|---|---|---|---|---|---|
| Z2 | 9.371 | [7.256, 12.066] | 0.234 | 0.022 | 0.001 | 5 |
| D | 4.784 | [1.091, 9.335] | 0.205 | 0.039 | 0.004 | 17 |

## 6. Ayrıştırmalar

Beta ayrıştırması (R2):

| pencere | alfa | artik_katki_yillik | beta_btc | beta_d | btc_katki_yillik | n | t_alfa | t_btc | t_d |
|---|---|---|---|---|---|---|---|---|---|
| birincil | 0.000 | 0.152 | 0.021 | 0.032 | 0.000 | 27 | 1.677 | 0.747 | 1.321 |
| dilim1 | 0.001 | 0.234 | 0.080 | 0.080 | 0.000 | 6 | 7.697 | 7.912 | 6.779 |
| dilim2 | 0.001 | 0.364 | -0.013 | -0.010 | 0.000 | 7 | 2.605 | -0.187 | -0.163 |
| dilim3 | -0.000 | -0.070 | 0.037 | 0.021 | 0.000 | 7 | -0.652 | 1.122 | 1.203 |
| dilim4 | 0.001 | 0.092 | 0.061 | 0.096 | 0.000 | 7 | 3.576 | 4.237 | 6.698 |

Long-beta karşılaştırması (R3):

| satır | değer |
|---|---|
| gun | 27 |
| olcek | 0.198 |
| sr_birincil | 4.150 |
| sr_r3 | -1.008 |
| sr_farki | 5.157 |
| korelasyon | 0.351 |
| beta | 0.351 |
| alfa_gunluk | 0.000 |
| alfa_yillik | 0.165 |
| t_alfa_nw | 2.339 |
| nw_gecikme | 10 |
| nan_yok | evet |

R3 kitabının SR %90 GA: [-4.609, 3.148]

REV1 korelasyonu (R4):

| satır | değer |
|---|---|
| durum | REV1 serisi yok |

B ayrıştırması (R8):

| satır (yıllık) | değer |
|---|---|
| trend_fiyat | 0.087 |
| trend_funding | -0.005 |
| trend_maliyet | 0.008 |
| carry_fiyat | 0.067 |
| carry_funding | 0.018 |
| carry_maliyet | 0.002 |
| hedge_fiyat | -0.005 |
| hedge_funding | -0.000 |
| netleme | 0.000 |
| icra_artigi | -0.000 |
| artik_carry | -0.000 |
| artik_trend | -0.000 |

| bacak | SR | %90 GA |
|---|---|---|
| trend | 2.351 | [-0.935, 6.215] |
| carry | 5.862 | [3.641, 8.111] |

Carry bacağı epizot payı (§3.4 B5 notu):

| satır | değer |
|---|---|
| epizot | 9 |
| pay | 1.091 |
| payda | 583.904 |

Bağımsız A koşusu:

| satır | değer |
|---|---|
| sr | 2.356 |
| q05 | -0.883 |
| q95 | 6.199 |
| cekis | 2000 |
| b5_pay | 1.431 |
| sr_farki_B_eksi_A | 1.794 |

L başına carry betası (K1-09):

| L | beta_btc | beta_d | n | t_btc | t_d |
|---|---|---|---|---|---|
| 0.5 | -0.007 | -0.004 | 27 | -0.587 | -0.568 |
| 1 | -0.013 | -0.008 | 27 | -0.586 | -0.568 |
| 1.5 | -0.013 | -0.008 | 27 | -0.451 | -0.424 |
| 2 | -0.010 | -0.006 | 27 | -0.321 | -0.293 |
| 2.5 | -0.010 | -0.006 | 27 | -0.313 | -0.288 |
| 3 | -0.010 | -0.006 | 27 | -0.314 | -0.289 |
| 4 | -0.010 | -0.006 | 27 | -0.315 | -0.291 |

B, fiyattan gelmediği gösterildi demek değildir.

## 7. Görülmemiş coinler (B9, R15)

|  | SR | %90 GA | gün |
|---|---|---|---|
| B9 | -0.315 | [-4.057, 4.031] | 32 |
| R15 (D, görülmüş zaman) | 0.665 | [-3.756, 8.085] | 17 |

## 8. Kelly tablosu

Maliyet 1×:

| L | CAGR | vol | SR | SR %90 GA | MDD | boot q50 | boot q95 | P(MDD>%30) | Kelly kesri | %30 DD | MDD D90-1 | MDD D90-2 | MDD D90-4 | MDD SQ-1 | MDD SQ-2 | MDD SQ-4 | MDD DM-1 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 0.5 | 0.082 | 0.018 | 4.310 | [0.935, 8.187] | 0.002 | 0.004 | 0.006 | 0.000 | 0.004 | uygun | 0.002 | 0.002 | 0.002 | 0.002 | 0.002 | 0.002 | 0.002 |
| 1 | 0.164 | 0.037 | 4.150 | [0.963, 7.951] | 0.005 | 0.009 | 0.012 | 0.000 | 0.009 | uygun | 0.005 | 0.005 | 0.005 | 0.005 | 0.005 | 0.005 | 0.005 |
| 1.5 | 0.230 | 0.053 | 3.895 | [0.377, 8.017] | 0.007 | 0.014 | 0.019 | 0.000 | 0.013 | uygun | 0.007 | 0.007 | 0.007 | 0.007 | 0.007 | 0.007 | 0.007 |
| 2 | 0.281 | 0.068 | 3.686 | [0.382, 7.481] | 0.009 | 0.017 | 0.024 | 0.000 | 0.016 | uygun | 0.009 | 0.009 | 0.009 | 0.009 | 0.009 | 0.009 | 0.009 |
| 2.5 | 0.312 | 0.083 | 3.311 | [0.275, 6.946] | 0.012 | 0.022 | 0.030 | 0.000 | 0.020 | uygun | 0.012 | 0.012 | 0.012 | 0.012 | 0.012 | 0.012 | 0.012 |
| 3 | 0.325 | 0.090 | 3.174 | [0.334, 6.953] | 0.015 | 0.025 | 0.034 | 0.000 | 0.022 | uygun | 0.015 | 0.015 | 0.015 | 0.015 | 0.015 | 0.015 | 0.015 |
| 4 | 0.390 | 0.093 | 3.583 | [0.584, 7.309] | 0.017 | 0.026 | 0.035 | 0.000 | 0.022 | uygun | 0.017 | 0.017 | 0.017 | 0.017 | 0.017 | 0.017 | 0.017 |

𝓛* = [0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 4.0]; varsayılan öneri: 4.000.

Maliyet 2×:

| L | CAGR | vol | SR | SR %90 GA | MDD | boot q50 | boot q95 | P(MDD>%30) | Kelly kesri | %30 DD | MDD D90-1 | MDD D90-2 | MDD D90-4 | MDD SQ-1 | MDD SQ-2 | MDD SQ-4 | MDD DM-1 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 0.5 | 0.079 | 0.018 | 4.171 | [0.895, 8.151] | 0.002 | 0.004 | 0.006 | 0.000 | 0.005 | uygun | 0.002 | 0.002 | 0.002 | 0.002 | 0.002 | 0.002 | 0.002 |
| 1 | 0.156 | 0.037 | 3.980 | [0.816, 7.804] | 0.005 | 0.009 | 0.012 | 0.000 | 0.009 | uygun | 0.005 | 0.005 | 0.005 | 0.005 | 0.005 | 0.005 | 0.005 |
| 1.5 | 0.218 | 0.053 | 3.715 | [0.583, 7.252] | 0.007 | 0.014 | 0.019 | 0.000 | 0.013 | uygun | 0.007 | 0.007 | 0.007 | 0.007 | 0.007 | 0.007 | 0.007 |
| 2 | 0.265 | 0.068 | 3.499 | [0.389, 7.565] | 0.010 | 0.018 | 0.025 | 0.000 | 0.017 | uygun | 0.010 | 0.010 | 0.010 | 0.010 | 0.010 | 0.010 | 0.010 |
| 2.5 | 0.292 | 0.083 | 3.127 | [0.198, 6.942] | 0.012 | 0.023 | 0.031 | 0.000 | 0.021 | uygun | 0.012 | 0.012 | 0.012 | 0.012 | 0.012 | 0.012 | 0.012 |
| 3 | 0.302 | 0.090 | 2.984 | [0.140, 6.681] | 0.015 | 0.025 | 0.034 | 0.000 | 0.023 | uygun | 0.015 | 0.015 | 0.015 | 0.015 | 0.015 | 0.015 | 0.015 |
| 4 | 0.365 | 0.093 | 3.386 | [0.429, 7.240] | 0.017 | 0.026 | 0.035 | 0.000 | 0.023 | uygun | 0.017 | 0.017 | 0.017 | 0.017 | 0.017 | 0.017 | 0.017 |

Seçilen L'nin DD değerleri banka örnekleminin içindedir; 𝓛*'ı banka örnekleminden seçmek seçim yanlılığı taşır. Demo ön-kaydı DD beklentisini bootstrap q95 ile yazar; bu iyimser olabilir.

"Blok bootstrap geçmiş getirileri yeniden örnekler. Marjin çağrısı, otomatik kaldıraç azaltma (ADL), tasfiye ve bankada gerçekleşmemiş kuyruk olaylarını üretmez. %30 DD sınırı hiçbir L için garanti edilemez."

## 9. Hayatta kalan yanlılığı

Kanal stresleri (R12, L = 1):

| senaryo | SR | %90 GA | MDD | olay | boş olay |
|---|---|---|---|---|---|
| stressiz | 4.150 | [0.804, 8.005] | 0.005 | — | — |
| D90-1 | 4.150 | [0.791, 7.951] | 0.005 | 0 | 0 |
| D90-2 | 4.150 | [0.921, 8.028] | 0.005 | 0 | 0 |
| D90-4 | 4.150 | [1.073, 8.053] | 0.005 | 0 | 0 |
| SQ-1 | 4.150 | [0.943, 7.969] | 0.005 | 0 | 0 |
| SQ-2 | 4.150 | [0.922, 7.959] | 0.005 | 0 | 0 |
| SQ-4 | 4.150 | [0.977, 8.105] | 0.005 | 0 | 0 |
| DM-1 | 4.150 | [0.676, 7.811] | 0.005 | 0 | 0 |

Delist uzlaşma senaryoları (R9):

| h_L | SR | %90 GA | MDD | CAGR | SR farkı | gün |
|---|---|---|---|---|---|---|
| 0.50 | 4.150 | [0.915, 8.435] | 0.005 | 0.164 | 0.000 | 27 |
| 0.90 | 4.150 | [0.903, 8.126] | 0.005 | 0.164 | 0.000 | 27 |

Kilitlenen stres bağlayıcılığı: (i) — hash —.

- Hayatta kalan yanlılığı giderilmedi.
- B2 (DSR) ve birincil Sharpe hayatta kalan yanlılığına göre düzeltilmedi.
- D90, SQ ve DM tek kanallı stres bindirmeleridir; hayatta kalan yanlılığının üst sınırı değildir.

## 10. Maliyet ve kapasite

NAV × maliyet ızgarası (R1):

| NAV|maliyet | SR | %90 GA |
|---|---|---|
| 100000|1 | 4.150 | [0.910, 8.160] |
| 100000|2 | 3.980 | [0.585, 7.755] |
| 100000|3 | 3.810 | [0.647, 7.540] |
| 1000000|1 | 4.138 | [0.767, 8.039] |
| 1000000|2 | 3.942 | [0.803, 7.824] |
| 1000000|3 | 3.747 | [0.625, 7.653] |
| 5000000|1 | 4.089 | [0.633, 8.038] |
| 5000000|2 | 3.892 | [0.657, 8.036] |
| 5000000|3 | 3.693 | [0.535, 7.580] |

Devir ve maliyet (R6):

| satır | değer |
|---|---|
| funding_dolgu_sayisi | 0 |
| funding_payi_yillik | 0.013 |
| gecikme_saat_ort | 1.000 |
| gecikme_saat_q50 | 1.000 |
| gecikme_saat_q95 | 1.000 |
| gun | 27 |
| icra_artigi_ort | 0.000 |
| icra_artigi_q95 | 0.000 |
| maliyet_payi_yillik | 0.010 |
| niyet | 191 |
| sonraki_karara_yetismeyen_orani | 0.000 |
| tek_yon_devir_yillik | 3.804 |
| ters_kayit_sayisi | 0 |

| niyet kapanışı | değer |
|---|---|
| dolum | 191 |

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
| t4a_orani | — |

—

Lot (R13) ve demo NAV (R14):

| satır | btc_hedefli_gun | btc_sifir_orani | coin | en_buyuk | fark_olan | lot_minnotional_alti_orani | nav_yuzde1_ustu | q50 | q95 | sr_birincil | sr_farki | sr_lot_kapali |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| R13 | — | — | — | — | — | — | — | — | — | 4.150 | -0.010 | 4.159 |
| R13b | — | — | 2 | 45.292 | — | — | 0 | 23.015 | 43.064 | — | — | — |
| R14 | 27 | 0.074 | — | — | 322 | 0.606 | — | — | — | — | — | — |

Lot kapalı SR %90 GA: [0.935, 8.028]

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
