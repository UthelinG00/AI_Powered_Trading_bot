# v8 Banka Raporu

## 1. Hüküm

**RET** — mimari **A**

| belge | sha256 |
|---|---|
| KILIT | bea874f342e4f182e00573b6a76645ee21620e35e7350bf9c0074f5185c2c700 |
| DONDURMA | 60559c75ba00414e1b87804f5f7d6f167148efb93206268b099e4b29b3e4f841 |
| DENETIM_TAMAM | ce6b3cd9a56ef6d503facbaabdd15a139da6b016165d09f1e172cc32404b6af6 |
| SONUC_DAMGA kok | 2b8e5e1ac237d112f5a3b3b4c7c4bbb6c30db5b3d8556f80c0d9d829729becbc |
| VERI_DENETIM | ea9c0cf8fd1e7a086a63a28e007b2be50de4e8094715b99213811620c92e0fce |

- Hayatta kalan yanlılığı giderilmedi.
- B2 (DSR) ve birincil Sharpe hayatta kalan yanlılığına göre düzeltilmedi.
- D90, SQ ve DM tek kanallı stres bindirmeleridir; hayatta kalan yanlılığının üst sınırı değildir.

## 2. Bağlayıcı tablo (B2–B11)

| ölçüt | değer | eşik | sonuç | %90 GA |
|---|---|---|---|---|
| B2 | 0.139 | 0.900 | kaldı | — |
| B3 | 0.233 | 0.300 | kaldı | [-0.682, 1.115] |
| B4 | -0.071 | 0.300 | kaldı | [-1.113, 0.893] |
| B5 | 1.544 | — | rapor | — |
| B6 | 3 | 2 | geçti | — |
| B7 | 0.262 | 0.868 | kaldı | [-0.682, 1.135] |
| B8 | 0.495 | 0.000 | geçti | [-0.423, 1.368] |
| B9 | 0.081 | 0.000 | geçti | [-0.818, 0.884] |
| B10 | 0.108 | — | rapor | — |
| B11 | 0.204 | 0.300 | geçti | — |

B3 ×3 SR 0.202 (%90 GA [-0.716, 1.033]); eşik > 0.

B6 dilimleri:

| dilim | SR | %90 GA |
|---|---|---|
| Z1 dilim 1 | 0.760 | [-0.972, 2.378] |
| Z1 dilim 2 | 0.867 | [-0.726, 2.477] |
| Z1 dilim 3 | 0.132 | [-1.599, 1.497] |
| Z1 dilim 4 | -1.878 | [-3.910, 0.167] |

Karar: **RET**

## 3. Birincil sonuç

| SR (R11) | %90 GA | CAGR | vol | MDD | gerçekleşen vol / birim (R7) |
|---|---|---|---|---|---|
| 0.262 | [-0.682, 1.135] | 0.012 | 0.051 | 0.072 | 0.341 |

SR ≥ 0,50: hayır (bilgi; eski B1).

Tahminci tanıları (R7):

| satır | değer |
|---|---|
| gerceklesen_vol_orani | 0.341 |
| gozlem | 16444 |
| karar_gunu | 1149 |
| rv_sigma2_q50 | 0.508 |
| rv_sigma2_q95 | 2.621 |
| rv_sigma2_q99 | 6.364 |
| t4a_disarida_orani | 0.000 |

## 4. DSR

B2 türü: **B**; d* = 0.900; N_hüküm = 331; SR₀ = 0.04595; γ₃ = 0.154; γ₄ = 9.902; η = 1.011; T = 1149.

**σ_SR = 0,30 varsayımdır, doğrulanmadı.**

DSR bir performans çıtasıdır; birleşik yanlış kabul §3.7'de ölçüldü (B7 dahil olanı için üst sınırın nokta tahmini ve Wilson aralığı).

R16 duyarlılık tablosu:

| σ|N çarpanı|η | N | dsr | eta | sigma_sr | sr0 |
|---|---|---|---|---|---|
| 0.20|0.8|eta | 265 | 0.293 | 1.011 | 0.200 | 0.030 |
| 0.20|0.8|eta1 | 265 | 0.292 | 1.000 | 0.200 | 0.030 |
| 0.20|1.0|eta | 331 | 0.284 | 1.011 | 0.200 | 0.031 |
| 0.20|1.0|eta1 | 331 | 0.283 | 1.000 | 0.200 | 0.031 |
| 0.20|1.2|eta | 397 | 0.278 | 1.011 | 0.200 | 0.031 |
| 0.20|1.2|eta1 | 397 | 0.276 | 1.000 | 0.200 | 0.031 |
| 0.30|0.8|eta | 265 | 0.147 | 1.011 | 0.300 | 0.045 |
| 0.30|0.8|eta1 | 265 | 0.146 | 1.000 | 0.300 | 0.045 |
| 0.30|1.0|eta | 331 | 0.139 | 1.011 | 0.300 | 0.046 |
| 0.30|1.0|eta1 | 331 | 0.137 | 1.000 | 0.300 | 0.046 |
| 0.30|1.2|eta | 397 | 0.132 | 1.011 | 0.300 | 0.047 |
| 0.30|1.2|eta1 | 397 | 0.131 | 1.000 | 0.300 | 0.047 |
| 0.50|0.8|eta | 265 | 0.020 | 1.011 | 0.500 | 0.075 |
| 0.50|0.8|eta1 | 265 | 0.019 | 1.000 | 0.500 | 0.075 |
| 0.50|1.0|eta | 331 | 0.017 | 1.011 | 0.500 | 0.077 |
| 0.50|1.0|eta1 | 331 | 0.017 | 1.000 | 0.500 | 0.077 |
| 0.50|1.2|eta | 397 | 0.015 | 1.011 | 0.500 | 0.078 |
| 0.50|1.2|eta1 | 397 | 0.015 | 1.000 | 0.500 | 0.078 |
| bag|0.8|eta | 265 | 0.147 | 1.011 | 0.300 | 0.045 |
| bag|0.8|eta1 | 265 | 0.146 | 1.000 | 0.300 | 0.045 |
| bag|1.0|eta | 331 | 0.139 | 1.011 | 0.300 | 0.046 |
| bag|1.0|eta1 | 331 | 0.137 | 1.000 | 0.300 | 0.046 |
| bag|1.2|eta | 397 | 0.132 | 1.011 | 0.300 | 0.047 |
| bag|1.2|eta1 | 397 | 0.131 | 1.000 | 0.300 | 0.047 |

## 5. Rejim dilimleri ve Z2 teşhisi

Z2 ve D segmenti (R10):

| segment | SR | %90 GA | CAGR | vol | MDD | gün |
|---|---|---|---|---|---|---|
| Z2 | 0.676 | [-2.008, 2.629] | 0.038 | 0.058 | 0.022 | 85 |
| D | 0.553 | [-0.298, 1.328] | 0.031 | 0.058 | 0.058 | 1096 |

## 6. Ayrıştırmalar

Beta ayrıştırması (R2):

| pencere | alfa | artik_katki_yillik | beta_btc | beta_d | btc_katki_yillik | n | t_alfa | t_btc | t_d |
|---|---|---|---|---|---|---|---|---|---|
| birincil | 0.000 | 0.014 | 0.004 | 0.002 | -0.001 | 1149 | 0.392 | 0.518 | 0.201 |
| dilim1 | -0.000 | -0.019 | 0.044 | 0.030 | 0.048 | 245 | -1.063 | 6.528 | 4.311 |
| dilim2 | 0.000 | 0.047 | 0.028 | 0.023 | 0.002 | 365 | 0.007 | 3.371 | 2.468 |
| dilim3 | -0.000 | 0.010 | -0.050 | -0.049 | -0.002 | 365 | -2.065 | -5.627 | -5.066 |
| dilim4 | -0.000 | 0.002 | 0.012 | -0.000 | -0.074 | 174 | -1.646 | 0.774 | -0.002 |

Long-beta karşılaştırması (R3):

| satır | değer |
|---|---|
| gun | 1149 |
| olcek | 0.060 |
| sr_birincil | 0.262 |
| sr_r3 | 0.539 |
| sr_farki | -0.276 |
| korelasyon | 0.108 |
| beta | 0.108 |
| alfa_gunluk | 0.000 |
| alfa_yillik | 0.010 |
| t_alfa_nw | 0.359 |
| nw_gecikme | 10 |
| nan_yok | evet |

R3 kitabının SR %90 GA: [-0.316, 1.449]

REV1 korelasyonu (R4):

| satır | değer |
|---|---|
| durum | REV1 serisi yok |

## 7. Görülmemiş coinler (B9, R15)

|  | SR | %90 GA | gün |
|---|---|---|---|
| B9 | 0.081 | [-0.818, 0.884] | 1234 |
| R15 (D, görülmüş zaman) | 0.407 | [-0.444, 1.194] | 1096 |

## 8. Kelly tablosu

Maliyet 1×:

| L | CAGR | vol | SR | SR %90 GA | MDD | boot q50 | boot q95 | P(MDD>%30) | Kelly kesri | %30 DD | MDD D90-1 | MDD D90-2 | MDD D90-4 | MDD SQ-1 | MDD SQ-2 | MDD SQ-4 | MDD DM-1 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 0.5 | 0.008 | 0.023 | 0.365 | [-0.563, 1.261] | 0.035 | 0.034 | 0.063 | 0.000 | 0.087 | uygun | 0.042 | 0.048 | 0.063 | 0.068 | 0.090 | 0.147 | 0.068 |
| 1 | 0.012 | 0.051 | 0.262 | [-0.577, 1.087] | 0.072 | 0.075 | 0.140 | 0.000 | 0.195 | uygun | 0.088 | 0.102 | 0.132 | 0.140 | 0.190 | 0.305 | 0.115 |
| 1.5 | 0.015 | 0.079 | 0.227 | [-0.650, 1.050] | 0.108 | 0.114 | 0.207 | 0.001 | 0.300 | uygun | 0.132 | 0.154 | 0.196 | 0.207 | 0.277 | 0.427 | 0.171 |
| 2 | 0.017 | 0.105 | 0.209 | [-0.656, 1.023] | 0.143 | 0.154 | 0.269 | 0.018 | 0.400 | uygun | 0.175 | 0.204 | 0.256 | 0.270 | 0.356 | 0.528 | 0.224 |
| 2.5 | 0.017 | 0.131 | 0.197 | [-0.644, 1.077] | 0.180 | 0.188 | 0.321 | 0.087 | 0.500 | kullanıcı hedefini (%30 DD) KARŞILAMIYOR | 0.218 | 0.252 | 0.313 | 0.331 | 0.429 | 0.604 | 0.276 |
| 3 | 0.019 | 0.156 | 0.196 | [-0.648, 1.052] | 0.212 | 0.222 | 0.382 | 0.193 | 0.597 | kullanıcı hedefini (%30 DD) KARŞILAMIYOR | 0.254 | 0.293 | 0.362 | 0.381 | 0.481 | 0.660 | 0.317 |
| 4 | 0.028 | 0.194 | 0.240 | [-0.634, 1.058] | 0.252 | 0.262 | 0.442 | 0.345 | 0.739 | kullanıcı hedefini (%30 DD) KARŞILAMIYOR | 0.301 | 0.343 | 0.421 | 0.410 | 0.522 | 0.712 | 0.370 |

𝓛* = [0.5, 1.0, 1.5, 2.0]; varsayılan öneri: 2.000.

Maliyet 2×:

| L | CAGR | vol | SR | SR %90 GA | MDD | boot q50 | boot q95 | P(MDD>%30) | Kelly kesri | %30 DD | MDD D90-1 | MDD D90-2 | MDD D90-4 | MDD SQ-1 | MDD SQ-2 | MDD SQ-4 | MDD DM-1 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 0.5 | 0.008 | 0.023 | 0.342 | [-0.578, 1.270] | 0.036 | 0.034 | 0.063 | 0.000 | 0.098 | uygun | 0.043 | 0.049 | 0.064 | 0.069 | 0.091 | 0.148 | 0.069 |
| 1 | 0.011 | 0.051 | 0.233 | [-0.681, 1.082] | 0.074 | 0.078 | 0.141 | 0.000 | 0.219 | uygun | 0.090 | 0.104 | 0.135 | 0.142 | 0.192 | 0.307 | 0.118 |
| 1.5 | 0.012 | 0.079 | 0.192 | [-0.676, 0.996] | 0.112 | 0.117 | 0.205 | 0.003 | 0.338 | uygun | 0.137 | 0.158 | 0.200 | 0.211 | 0.281 | 0.430 | 0.175 |
| 2 | 0.012 | 0.105 | 0.170 | [-0.671, 1.000] | 0.150 | 0.155 | 0.277 | 0.019 | 0.451 | uygun | 0.181 | 0.210 | 0.262 | 0.276 | 0.361 | 0.531 | 0.230 |
| 2.5 | 0.012 | 0.131 | 0.155 | [-0.745, 0.983] | 0.188 | 0.193 | 0.331 | 0.095 | 0.563 | kullanıcı hedefini (%30 DD) KARŞILAMIYOR | 0.226 | 0.260 | 0.320 | 0.338 | 0.435 | 0.608 | 0.283 |
| 3 | 0.012 | 0.156 | 0.153 | [-0.741, 0.989] | 0.222 | 0.229 | 0.386 | 0.207 | 0.672 | kullanıcı hedefini (%30 DD) KARŞILAMIYOR | 0.263 | 0.302 | 0.370 | 0.389 | 0.488 | 0.664 | 0.325 |
| 4 | 0.019 | 0.194 | 0.193 | [-0.699, 1.032] | 0.264 | 0.274 | 0.460 | 0.400 | 0.831 | kullanıcı hedefini (%30 DD) KARŞILAMIYOR | 0.313 | 0.354 | 0.431 | 0.420 | 0.529 | 0.716 | 0.381 |

Seçilen L'nin DD değerleri banka örnekleminin içindedir; 𝓛*'ı banka örnekleminden seçmek seçim yanlılığı taşır. Demo ön-kaydı DD beklentisini bootstrap q95 ile yazar; bu iyimser olabilir.

"Blok bootstrap geçmiş getirileri yeniden örnekler. Marjin çağrısı, otomatik kaldıraç azaltma (ADL), tasfiye ve bankada gerçekleşmemiş kuyruk olaylarını üretmez. %30 DD sınırı hiçbir L için garanti edilemez."

## 9. Hayatta kalan yanlılığı

Kanal stresleri (R12, L = 1):

| senaryo | SR | %90 GA | MDD | olay | boş olay |
|---|---|---|---|---|---|
| stressiz | 0.262 | [-0.642, 1.100] | 0.072 | — | — |
| D90-1 | 0.047 | [-0.851, 0.924] | 0.088 | 3 | 0 |
| D90-2 | -0.136 | [-1.043, 0.720] | 0.102 | 6 | 0 |
| D90-4 | -0.472 | [-1.348, 0.356] | 0.132 | 13 | 0 |
| SQ-1 | -0.325 | [-1.190, 0.637] | 0.140 | 3 | 0 |
| SQ-2 | -0.678 | [-1.534, 0.275] | 0.190 | 6 | 0 |
| SQ-4 | -1.301 | [-2.074, -0.400] | 0.305 | 13 | 0 |
| DM-1 | -0.214 | [-1.062, 0.666] | 0.115 | 3 | 0 |

Delist uzlaşma senaryoları (R9):

| h_L | SR | %90 GA | MDD | CAGR | SR farkı | gün |
|---|---|---|---|---|---|---|
| 0.50 | 0.262 | [-0.649, 1.123] | 0.072 | 0.012 | 0.000 | 1149 |
| 0.90 | 0.262 | [-0.678, 1.076] | 0.072 | 0.012 | 0.000 | 1149 |

Kilitlenen stres bağlayıcılığı: (i) — hash 60559c75ba00414e1b87804f5f7d6f167148efb93206268b099e4b29b3e4f841.

- Hayatta kalan yanlılığı giderilmedi.
- B2 (DSR) ve birincil Sharpe hayatta kalan yanlılığına göre düzeltilmedi.
- D90, SQ ve DM tek kanallı stres bindirmeleridir; hayatta kalan yanlılığının üst sınırı değildir.

## 10. Maliyet ve kapasite

NAV × maliyet ızgarası (R1):

| NAV|maliyet | SR | %90 GA |
|---|---|---|
| 100000|1 | 0.262 | [-0.682, 1.135] |
| 100000|2 | 0.233 | [-0.682, 1.115] |
| 100000|3 | 0.202 | [-0.716, 1.033] |
| 1000000|1 | 0.257 | [-0.617, 1.132] |
| 1000000|2 | 0.221 | [-0.697, 1.084] |
| 1000000|3 | 0.186 | [-0.767, 1.014] |
| 5000000|1 | 0.263 | [-0.646, 1.097] |
| 5000000|2 | 0.224 | [-0.710, 1.052] |
| 5000000|3 | 0.184 | [-0.746, 1.043] |

Devir ve maliyet (R6):

| satır | değer |
|---|---|
| funding_dolgu_sayisi | 0 |
| funding_payi_yillik | -0.012 |
| gecikme_saat_ort | 1.040 |
| gecikme_saat_q50 | 1.000 |
| gecikme_saat_q95 | 1.000 |
| gun | 1149 |
| icra_artigi_ort | 0.000 |
| icra_artigi_q95 | 0.000 |
| maliyet_payi_yillik | 0.003 |
| niyet | 4737 |
| sonraki_karara_yetismeyen_orani | 0.001 |
| tek_yon_devir_yillik | 1.082 |
| ters_kayit_sayisi | 0 |

| niyet kapanışı | değer |
|---|---|
| dolum | 4732 |
| iptal:islem_disi | 1 |
| iptal:yeni_karar | 4 |

Tavan bağlama ve aşım (R5):

| satır | değer |
|---|---|
| birim_gunu | 1149 |
| gun_sonu | 1149 |
| hedefe_ulasilamayan_orani | 0.006 |
| karar_gunu | 1149 |
| mmax_baglama_orani | 0.000 |
| s1_asim_orani | 0.000 |
| s1_en_buyuk_asim | 0.000 |
| s2_asim_orani | 0.000 |
| s2_en_buyuk_asim | 0.000 |
| t4a_orani | 0.000 |

—

Lot (R13) ve demo NAV (R14):

| satır | coin | en_buyuk | fark_olan | lot_minnotional_alti_orani | nav_yuzde1_ustu | q50 | q95 | sr_birincil | sr_farki | sr_lot_kapali |
|---|---|---|---|---|---|---|---|---|---|---|
| R13 | — | — | — | — | — | — | — | 0.262 | -0.000 | 0.262 |
| R13b | 194 | 364.800 | — | — | 0 | 0.352 | 6.375 | — | — | — |
| R14 | — | — | 7324 | 0.734 | — | — | — | — | — | — |

Lot kapalı SR %90 GA: [-0.621, 1.114]

## 11. Veri ve teknik

Veri denetimi (T2; VERI_DENETIM.json):

| satır | değer |
|---|---|
| borsa_capi_bosluk_saati | 0 |
| btc_eksik_saat | 0 |
| eksik_funding_kaydi | 58 |
| eth_eksik_saat | 0 |
| eylul_funding_kaynagi | api_goruntusu (48 sembol) |
| filtresiz_sembol | 8 |
| k_coin | 80 |
| k_veri_yok | 0 |
| sureklilik_sorunu | 8 |
| checksum.dosya | 19766 |
| checksum.gecersiz_satir | 0 |
| checksum.indirme_hatasi | 0 |
| checksum.kimlik_degisti | 0 |
| checksum.manifest_ozeti | c26b46da599b130f4f8b025b6ecac0ec40c43218dc810b50cd4254f94b30df5c |
| checksum.onarilamayan | 0 |
| checksum.yok | 0 |
| oranlar.btc_eksik | 0.000 |
| oranlar.eth_eksik | 0.000 |
| oranlar.k_veri_yok | 0.000 |
| coin_eksik_saat.coin | 202 |
| coin_eksik_saat.en_buyuk | 20368 |
| coin_eksik_saat.toplam | 123454 |

T2: hayır

| satır | değer |
|---|---|
| teknik_ek | 1 |

## 12. Güç

Kalibrasyon (§3.7; "tarama kuralı, güven kanıtı değil"):

| satır | değer |
|---|---|

Rejim-null tanıları (R17):

| sayım | gercek | null_ort | null_q5 | null_q95 |
|---|---|---|---|---|
| maske_gunu | 4030 | 6823.066 | 6318.950 | 7444.700 |
| dolgu_saati | 0 | 0.000 | 0.000 | 0.000 |
| bosluk_saati | 0 | 0.000 | 0.000 | 0.000 |
| evren_ort | 14.411 | 14.499 | 14.384 | 14.627 |
| ortak_pay | — | 0.936 | 0.931 | 0.941 |

## 13. Sınırlar

- asimetrik güç
- korelasyonlu kesit
- hayatta kalan yanlılığı
- mark vekili (uzlaşma damgası T için [T−1h, T) barının kapanışı; MIMARI §2.1)
- ADL/marjin modellenmedi
- tarihsel sembol filtresi yok
- B'nin funding/fiyat ayrımının gücü düşük
- B, fiyattan gelmediği gösterildi demek değildir.
