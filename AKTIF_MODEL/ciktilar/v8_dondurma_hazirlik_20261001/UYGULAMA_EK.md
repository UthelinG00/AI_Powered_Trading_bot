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

## Revizyon 2 (Codex T30, 2 Ekim; dondurma ve kuru koşudan önce)

Codex T30 (`v8/codex_cagrilari/20261001T30_dondurma_hukum_betikleri_yanit.md`) 5 CIDDI ve 3 ORTA bulgu verdi. Bu
bölüm U1–U3'ün ilgili kısımlarının yerine geçer; kural, eşik ve parametre değişmez.

**R1. Kilit denetimi (U2; T30-1, T30-7).** Kilitli `kilit.dogrula`, kilitteki V1 raporunu bugünkü en yeni test raporuyla
birebir karşılaştırır. Tam takım raporu `banka_kos/` ve `testler/` kimliklerini de bağladığı için, kilitten sonra
yazılması ön-kayıtlı banka kodu (21 g T29 eki: "banka_kos kilit kimliğine değil DONDURMA'ya girer") bu karşılaştırmayı
kalıcı olarak bozar. Kilitli kodu değiştirmeden çözüm (`acilis.kilit_tam`):
1. `kilit.zincir_dogrula(..., onkosul=False)`: belgeler, kod, parametre, ortam, veri, sabitler, defter ve git.
2. Kalibrasyon ön koşulları (`kilit.onkosullar(v1=False)`) yeniden hesaplanır ve kilittekiyle aynı olmalı.
3. Kilitteki V1 raporu tarihsel kanıttır: dosyası durmalı ve sha256'sı aynı olmalı.
4. Güncel V1 (`kilit.v1_raporu`): bugünkü bütün kod kimliklerini kapsayan, geçen en yeni rapor. DONDURMA'ya
   `v1_guncel` olarak yazılır; banka girişi yeniden hesaplar ve aynı olmalı.
5. DONDURMA `teknik_ekler` ({sıra, tür, sha256, commit}) zincirdeki eklerle birebir aynı olmalı.

**R2. Dondurma commit'i (§1.4 `git_commit`; T30-6).** Bir dosya kendi commit'ini taşıyamaz. DONDURMA `git_commit_ust`
(üretim anındaki HEAD) taşır; dondurma commit'i itildikten sonra ACILIS'e `dondurma_commit` yazılır ve banka girişi
`kilit.git_denetimi(DONDURMA.json, dondurma_commit)` ile doğrular (dosya o commit'te bayt bayt aynı, commit uzakta).

**R3. Dondurma kanıtları (U1; T30-5, T30-6).**
- Kapı: HUKUM ve DENETIM, KOSU_OZETI'ndeki hash'lerle aynı; V1–V6 geçti, ihlal yok; koşunun kod/parametre kimlikleri ve
  kilit commit'i kilitle aynı. Kaydedilen: karar, HUKUM/DENETIM/KOSU_OZETI/KAPI_RAPORU sha256'ları.
- Kuru koşu: T1 kuru, T2/T3 yok, T4 (muhasebe kapısını geçen birim = birim sayısı), T5 yok; damga kökü satırlardan
  yeniden hesaplanır; IS_LISTESI kimliği özetin bağladığı kimlik, kuru kipte, kapının mimarisinde ve **bugünkü kod
  kimlikleriyle** (kuru koşu son kodla koşulur); taban birimler eksiksiz.
- Ek alanlar: `tahminci.dondurulan` (HAR katsayıları), `kalibrasyon.kod_sha256` (kilitteki kalibrasyon kod kimliği),
  `dsr.SR0_kilit`, `v1_kilit`, `v1_guncel`.

**R4. Hüküm betiği (U3; T30-3, T30-4, T30-8).**
- DENETIM_TAMAM: SONUC_DAMGA ve DENETIM_OZETI, `commit` alanındaki commit'te bayt bayt aynı ve commit uzakta.
- T4 denetlenir (muhasebe kapısını geçen birim = birim sayısı = damga birim sayısı).
- T1–T5'ten biri varsa TEKNİK GEÇERSİZ yazılır; **anahtar okunmaz, sonuç çözülmez, hüküm hesaplanmaz**.
- IS_LISTESI, DENETIM_OZETI'nin bağladığı kimlik olmalı ve bu DONDURMA, ACILIS, VERI_DENETIM, dönem, mimari, tohum, alıcı,
  T1 kimlikleri ve taban birimlerle aynı olmalı; bütün bunlar anahtar okunmadan önce.
- Beklenmeyen hata: ekrana yalnız sabit durum ve iz sha256'sı; iz yerel `hukum_hata_izi.txt`'ye.

**R5. N_hüküm (T30-2, kısmi).** N_hüküm güncel defterden §3.3 sayımıyla bir kez hesaplanır (teknik ek satırları dahil;
önceki "N_dondurma + ek sayısı" teknik eki çift sayıyordu). Dondurmadaki defter bugünkünün baş kısmı olmalı; N_hüküm ≥
N_dondurma.

**Açık karar (kullanıcı; dondurmadan önce).** §3.3 "Dondurmaya kadar kapı +1 ve D doğrulama +1" der. Kapı satırı
(`A4-carry-kapisi`) kilitten önce deftere girdi; D doğrulama satırı yok. Kilitli 21 g ise defterin kilitten sonra
yalnız teknik ekle büyüyebileceğini söyler ve kilitli `kilit.dogrula` defteri birebir karşılaştırır. Bu iki kilitli
metnin birlikte nasıl uygulanacağı bir yorum kararıdır; dondurma bu karar verilmeden yapılmaz. Kuru koşunun hesabını
etkilemez.

**Revizyon 2 eki (Codex T31, 2 Ekim).** (a) Teknik ek varsa R1 (2) atlanır: 21 g'ye göre ekte kalibrasyon ön koşulları
yeniden doğrulanmaz; ekin kendi V1'i zincirde denetlenir. (b) Hüküm betiği `--dt_commit` ister: DENETIM_TAMAM.json'un
kendisi o commit'te bayt bayt aynı ve commit uzakta olmalı. (c) Beklenmeyen hata izi hiçbir yere yazılmaz; ekrana yalnız
iz sha256'sı. Açık kalanlar: teknik yeniden dondurma (`ilk_dondurma`, ilk tohumun korunması) üreticide yok; gerekirse
o anda eklenir. `AcilisHatasi` metinleri kendi sabit metinlerimizdir (alan adları; coin adı ya da metrik yok).

## Revizyon 3 (kullanıcı kararı B, 2 Ekim; kuru koşudan ve dondurmadan önce)

Açık karar kapandı. §3.3'teki "D doğrulama +1" **defterde değil, dondurmada sayılır**: DONDURMA `deneme_defteri` =
{sha256, satir, N_v8, N_defter = 159 + N_v8, d_dogrulama_sayimi = 1, N_dondurma = N_defter + 1}. Defter ve kilit
değişmez; bankadan önceki teknik ek hakkı (`banka_oncesi`) kullanılmaz. N_hüküm = güncel defter N'si (teknik ek
satırları dahil) + d_dogrulama_sayimi. Kalibrasyon kuralları (N = 329 ile hesaplanan eşikler) değişmez; DSR (B2) N_hüküm
ile hesaplanır, yani +1 sonucu yalnız muhafazakâr yönde etkiler. D doğrulama satırı deftere hüküm açıldıktan sonra,
yayımdan önce eklenir. Reddedilen seçenekler: teknik ekle satır (tek teknik düzeltme hakkını harcar), hiç saymamak
(§3.3'e aykırı, daha az muhafazakâr).

## Revizyon 4 (dondurma anı, 2 Ekim; kullanıcı "dondur" onayından sonra)

İlk `dondur.py` çağrısı "kapi kosusunun kimlikleri kilitle ayni degil" ile durdu (dosya yazılmadı). Neden: `kapi_kaniti`
kapı koşusunun kod/parametre kimliklerini zincirin son hâliyle (KILIT_TEKNIK_1 sonrası; kalibrasyon kodu değişti)
karşılaştırıyordu; kapı ise ekten önce ilk kilitle (71cf576) koştu. Doğru hedef ilk kilittir (R3: "kilit commit'i ve
kimlikleri kilitle aynı" — kapının koştuğu kilit). `dondur.py` değiştirilmedi (banka_kos kimliği ve ekli zincirin V1
bağı); dondurma `ciktilar/v8_dondurma_20261002/dondur_calistir.py` ile yapıldı: dondur.py'yi olduğu gibi çağırır, yalnız
kapı kanıtına ilk kilit içeriğini verir. Diğer bütün denetimler (zincir ve git, kuru koşu, N, alıcı) değişmeden koşar.
