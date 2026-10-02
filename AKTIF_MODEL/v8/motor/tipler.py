"""Ortak parametre demeti (saf veri, hesap yok).

Ağ, dosya, config ya da durum erişimi yoktur. Her alan MIMARI.md'nin bir bölümüne karşılık gelir; yorum
satırları o bölümü işaretler. Değerler MIMARI'nin dondurulmuş sabitleridir; D verisine bakılarak seçilmedi.
"""
from dataclasses import dataclass, field


@dataclass(frozen=True)
class Parametreler:
    # MIMARI §3.1 — sinyal
    ufuklar: tuple[int, ...] = (14, 42, 84)

    # MIMARI §3.2/§3.3 — ortak sigma tabanı (sinyal normalizasyonu ve boyutlama, ikisi de aynı taban)
    sigma_taban: float = 0.20
    ewma_yariomurleri: tuple[int, ...] = (20, 90)  # gün; sigma_EW(H) = sqrt(365 * EWMA_H(r^2))

    # MIMARI §3.2 — korelasyon
    eps_psd: float = 1e-8          # ozdeger kirpma tabani (KC-13)
    r_sabit: float = 0.7           # R_S'nin kosegen disi degeri; eksik cift ro de bu
    harman_agirligi: float = 0.5  # R_EW ve R_S'nin harman agirligi (R_hat = 0.5*R_EW + 0.5*R_S)
    korelasyon_yariomur: float = 90.0  # gun; agirlik a_t = 2^(-yas_t/90)
    min_ortak_gun: int = 60       # bundan az ortak gozlemli cift icin ro = r_sabit

    # MIMARI §3.3 — birim risk
    tau: float = 0.15
    m_max: float = 1.5

    # MIMARI §3.5 — Mimari A tavanlari (kaldirac sonrasi NAV)
    isim_tavan_btc_eth: float = 0.35
    isim_tavan_alt_long: float = 0.06
    isim_tavan_alt_short: float = 0.04
    brut_tavan: float = 2.0
    s1_alt_dusus: float = 0.70
    s1_btc_eth_dusus: float = 0.30
    s1_sinir: float = 0.20         # NAV
    s2_en_buyuk_short_artis: float = 1.00
    s2_diger_short_artis: float = 0.50
    s2_btc_eth_artis: float = 0.25
    s2_sinir: float = 0.20         # NAV
    tavan_max_tur: int = 5

    # MIMARI §3.6 — bant
    bant_oran: float = 0.20
    bant_taban: float = 0.002      # NAV

    # MIMARI §3.7 — katilim
    katilim_oran_30g: float = 0.001
    katilim_oran_7g: float = 0.001
    katilim_oran_onceki_saat: float = 0.10

    # MIMARI §6.1 — maliyet
    ucret_bps: float = 5.0
    karekok_y: float = 1.0
    dilim_btc_eth_bps: float = 2.0
    dilim_200m_ustu_bps: float = 5.0
    dilim_50_200m_bps: float = 8.0
    dilim_20_50m_bps: float = 15.0
    dilim_20m_alti_bps: float = 25.0  # yalniz cikis
    dilim_200m_esik: float = 200_000_000.0
    dilim_50m_esik: float = 50_000_000.0
    dilim_20m_esik: float = 20_000_000.0
    m_stres: float = 3.0
    stres_esik_coin_sigma: float = 5.0   # |ln(H/L)| > 5*sigma_1h ise stres
    stres_esik_btc_sigma: float = 4.0    # BTC icin |ln(H/L)| > 4*sigma_1h_BTC

    # ---- Slice 2 (durumlu orkestrasyon) ----
    # MIMARI §2.3 — PIT trend evreni
    btc: str = 'BTCUSDT'
    eth: str = 'ETHUSDT'
    evren_n: int = 15              # BTC/ETH + 13 alt yuvasi
    alt_giris_sira: int = 15
    alt_kalis_sira: int = 20
    v60_gun: int = 60
    hacim_taban_v60: float = 20_000_000.0
    isinma_gun: int = 90           # MIMARI §2.4: coin ve kosu basina

    # MIMARI §2.5 — donma, delist, coine ozgu bosluk
    donma_a_kisa_gun: int = 7
    donma_a_uzun_gun: int = 90
    donma_a_oran: float = 0.10
    donma_b_ardisik_bar: int = 6
    donma_c_saat: int = 16
    donma_d_saat: int = 8
    maske_temiz_gun: int = 30

    # MIMARI §2.6 — borsa capi bosluk ve eksik funding
    borsa_bosluk_oran: float = 0.50
    bosluk_gecmis_gun: int = 30    # karar kaydinda tasinan bosluk saatleri ve (c) penceresinin en uzun geri bakisi
    funding_pencere_gun: int = 30
    funding_varsayilan_aralik_saat: float = 8.0
    funding_eksik_carpan: float = 1.5
    funding_r_taban_saatlik: float = 0.0001 / 8.0
    funding_borsa_araliklari: tuple = (1, 4, 8)   # saat; MIMARI Ss5.3 "8h/4h/1h" (ters kayit kapsami icin)
    funding_gec_kayit_gun: int = 30   # mekanik: gec gelen gercek kaydin islenebildigi ve dolgunun beklendigi pencere

    # MIMARI §1c — gerceklesebilir ileri cikis ve delist uzlasmasi (h_L %50/%90 senaryolari ayri kosudur)
    delist_bekleme_gun: int = 30
    delist_h_long: float = 0.10
    delist_h_short: float = 0.05

    # MIMARI §3.7 / §6.1 — karar aninda sabitlenen pencereler
    katilim_30g_gun: int = 30
    katilim_7g_gun: int = 7
    sigma_1h_gun: int = 30

    # MIMARI §5.1 — goruntude olmayan sembol icin filtre varsayilani (adim 0 = yuvarlama yok)
    varsayilan_adim: float = 0.0
    varsayilan_min_notional: float = 5.0

    # ---- Slice 3 (Mimari B carry uydusu) ----
    # MIMARI §0 / ONKAYIT §2 — bankaya tek mimari gider; 'A' yalniz trend, 'B' trend + carry uydusu
    mimari: str = 'A'

    # MIMARI §1d, §4.4 — sabit carry butcesi
    carry_omega: float = 0.20
    # CARRY Ss6.3 K8 yeniden kosusu: bu isimler butun donem carry aday listesinden cikar (trend evrenini etkilemez).
    # Ana kosuda bos; kapi disinda kullanilmaz.
    carry_haric: tuple = ()
    # MIMARI §4.1 — carry evreni
    carry_v30_gun: int = 30
    carry_giris_v30: float = 20_000_000.0
    carry_cikis_v30: float = 10_000_000.0
    carry_yarim_tavan_v30: float = 50_000_000.0
    carry_eksik_olay_max: int = 1          # son 30 gunde en fazla bu kadar eksik funding olayi
    carry_genislik_yarim: int = 15         # n_C < 15: carry brutu x0,5
    carry_genislik_sifir: int = 10         # n_C < 10: carry kitabi 0
    # MIMARI §4.2 — skor ve notrleme
    carry_f30_gun: int = 30
    carry_sigma_taban: float = 0.30
    carry_r30_gun: int = 30
    # MIMARI §4.3 — bacaklar, agirlik, hedge
    carry_bacak_oran: float = 0.30
    carry_long_funding_taban: float = -0.50  # yillik F30; mevcut long'a da
    carry_beta_buzulme: float = 0.5
    carry_beta_gun: int = 60
    # MIMARI §4.4 — carry isim tavanlari (NAV; omega ve L uygulanmis) ve haftalik bant
    carry_tavan_short: float = 0.010
    carry_tavan_long: float = 0.015
    carry_bant: float = 0.25
    # MIMARI §4.5 — B net kitap: S4 (en buyuk tek alt short +%300, sinir %10 NAV) => alt short isim tavani %3,33
    s4_artis: float = 3.0
    s4_sinir: float = 0.10
    cozucu_ikiye_bolme_adim: int = 60

    # ---- Kilit adim 2: HAR/EWMA secimi (MIMARI §1b) ----
    har_m_gun: int = 365            # capa m penceresi (en fazla)
    har_m_min_gun: int = 90         # capa icin en az tanimli gun
    har_l7_min: int = 4             # l7 icin en az tanimli gun (7 gunde cogunluk; uygulama sabiti)
    har_l30_min: int = 15           # l30 icin en az tanimli gun (30 gunde cogunluk; uygulama sabiti)
    har_artik_hafta: int = 52       # s^2: son 52 haftanin yuruyen tahmin artiklari
    har_artik_min_hafta: int = 8    # s^2 icin en az hafta
    har_qlike_oran: float = 0.95    # (i) havuzlu QLIKE_HAR <= 0,95 * QLIKE_EWMA
    har_boot_blok: int = 4          # (iv) blok uzunlugu (hafta)
    har_boot_cekis: int = 2000
    har_boot_tohum: int = 20260927
    har_min_hafta: int = 30         # degerlendirme kumesi bundan kisaysa EWMA kalir
    har_egitim_min: int = 30        # aylik OLS icin en az gozlem (uygulama sabiti; yoksa o ay HAR tanimsiz)
    # Kilit adim 2 sonucu (ciktilar/v8_har_secimi_20260929_01: HAR). 'EWMA' varsayilani eski davranistir; 'HAR' icin
    # har_takvimi (har.HarTakvimi) verilmelidir. Yalniz boyutlamadaki sigma degisir (MIMARI Ss1b "Kapsam", Ss3.2).
    sigma_tahmincisi: str = 'EWMA'
    har_takvimi: object = None
