# Kilit sonrası uygulama ayrıntıları (dondurma ve hüküm betikleri)

Tarih: 1 Ekim 2026, kilitten sonra (KILIT.json, commit 71cf576), kapı hükmü ve banka verisi görülmeden. Bu belge **kural
değiştirmez**: eşik, ölçüt, parametre, örneklem ve evren kilitteki ön-kayıtlardadır. Yalnız ön-kaydın tarif ettiği ama
kodlanmamış mekanik adımları (BANKA §1.4 DONDURMA kaydı, §2.4 kör hüküm, BK-3 hüküm betiği; §3.7 netleştirme 20 b ve
21 g'nin "7.01'de bağlanır" maddeleri) tanımlar. Kilitli belgelerle çelişirse kilitli belge geçerlidir. Bu belgenin
sha256'sı DONDURMA.json'a girer.

## U1. DONDURMA.json üretimi (`v8/dondur.py`; 7.01)

Kullanım: `python dondur.py <cikti> --kilit <KILIT.json> --kilit_commit <40 hane> [--ek_commit ...] --kapi <kapı çıktı
klasörü> --kuru <kuru koşu klasörü> --alici <age açık anahtarı> --onay dondur`. `--onay dondur` kullanıcının sohbetteki
"dondur" onayıyla verilir. Betik önce kilit zincirini uzak commit'lerle doğrular (`kilit.zincir_dogrula`, git açık).
Ardından şunları ister:

- kapı `KOSU_OZETI.json` ve `HUKUM.json`,
- kuru koşu `denetim/DENETIM_OZETI.json`: T1 kuru, T2–T4 yok, T5 yok,
- kuru koşu `SONUC_DAMGA.json`.

`DONDURMA.json` zaten varsa üretmez. Alanlar §1.4 ve 20 (b, k, l) ile aynıdır:

- **Kimlik alanları:** `mimari` (kapı hükmündeki karar), `kilit_sha256` ve `kilit_commit`, varsa `teknik_ekler`
  ({sıra, tür, sha256, commit}), `acilis.kimlikler()` alanları (`motor_sha256`, `banka_kos_sha256`, `veri_denetim_sha256`,
  `parametreler_sha256`, `har_sonuc_sha256`, `ortam`, `tohum_banka`).
- **`git_commit`:** üretim anındaki HEAD; dondurma commit'i bunun çocuğudur.
- **`tahminci`:** "HAR", HAR sonuç ve rapor sha256'ları.
- **`carry_kapisi`:** karar, HUKUM.json ve KOSU_OZETI.json sha256'ları.
- **`d_dogrulama`:** kuru koşunun DENETIM_OZETI ve SONUC_DAMGA sha256'ları ile damga kökü.
- **`kalibrasyon`:** TOPLAMA.json sha256'sı ve kilitteki kurallar (N, σ, b2_bağlı, d, b3/b4 eşikleri, e_b5, k_b6,
  e_b10, B7 q95).
- **`dsr`:** σ_SR_bağ, kaynak, B2 türü, d*, N_kilit.
- **`deneme_defteri`:** sha256, satır sayısı, N_v8, N_dondurma = 159 + N_v8.
- **Belge hash'leri:** `onkayit_sha256` (BANKA_ONKAYIT_TASLAK.md) ve `uygulama_ek_sha256` (bu belge).
- **Kullanıcıdan gelenler:** `sifreleme_acik_anahtar`, `stres_secenegi` = "i" (ACIK_SORU_YANITLARI #12; rapor),
  `kullanici_onayi` = "dondur" ve `utc`.

Teknik düzeltmeden sonra yeni DONDURMA `ilk_dondurma` = {yol, sha256} taşır (20 l).

## U2. Banka girişinin kilit zinciri (21 g; 20 b)

`banka_kos.py` ve `veri_denetim.py`, banka kipinde T1'e ek olarak şunları doğrular:

- DONDURMA'daki `kilit_sha256`'nın kilit dosyasıyla aynı olması,
- `kilit.zincir_dogrula(kilit, git=True, kilit_commit, ek_commitler, izinli_turler=('kapi', 'banka_oncesi',
  'banka_sonrasi'))`.

Kilit yolu ve commit'ler DONDURMA'dan okunur. `banka_kos_sha256` kapsamına `v8/dondur.py` ve `v8/banka_hukum.py` eklenir
(betik listesi: banka_kos.py, banka_hukum.py, dondur.py, banka_kos/, banka/, kalibrasyon/, adaptor/).

## U3. Hüküm betiği (`v8/banka_hukum.py`; BK-3, §2.4)

Kullanım: `python banka_hukum.py <banka çıktısı> <ACILIS.json> <DONDURMA.json> <DENETIM_TAMAM.json> <age kimlik
dosyası> [--rev1 <REV1 D günlük getiri dosyası>]`. Kullanıcı kendi bilgisayarında koşar; gizli anahtar başka yere
kopyalanmaz.

Sıra:

1. **T1 ve kilit zinciri:** U2'deki denetim.
2. **DENETIM_TAMAM.json:** {damga_kok_sha256, denetim_ozeti_sha256, commit}. Damga kökü ve DENETIM_OZETI sha256'sı
   klasördekiyle aynı olmalı; DENETIM_OZETI'nde T2–T5 "yok" olmalı.
3. **Çözme:** `hukum.birimleri_coz(beklenen_kok=…)`.
4. **Hüküm bağlamı:**
   - dönemler `VERI_DENETIM.json`'dan, görülmüş günler ACILIS'ten,
   - kurallar DONDURMA `kalibrasyon`dan,
   - `N_hukum` = DONDURMA N_dondurma + teknik ek sayısı (§3.3: teknik yeniden koşu +1).
5. **Hesap:** `hukum.hukum`, `rapor.rapor_satirlari` ve `rapor_md.banka_raporu`.
6. **Yazılanlar:** `hukum/banka_sonuc.json` (kanonik), `hukum/BANKA_RAPORU.md` ve `hukum/HUKUM_KIMLIK.json`. Sonuncusu
   girdilerin ve çıktıların sha256'larını taşır.

Hüküm türü:

- **TEKNİK GEÇERSİZ:** T1–T5'ten biri varsa.
- **KABUL ya da RET:** aksi hâlde, hüküm sonucundaki karar.

Rapor bağlamındaki hash'ler: KILIT, DONDURMA, DENETIM_TAMAM, SONUC_DAMGA kökü ve VERI_DENETIM. Ekrana yalnız hüküm türü ve
dosya hash'leri basılır.
