# v8 kilit Adım 3: sentetik kalibrasyon — ilerleme kontrol noktası (2026-09-29)

Durum: **BAŞLADI**. Tasarım: `ciktilar/v8_asama4_20260927_01/BANKA_ONKAYIT_TASLAK.md` §3.3 ve §3.7 (3. revizyon, §0.2).
Kullanıcı kararı 29 Eylül "1+" (`ACIK_SORU_YANITLARI.md` #22). D verisi, D P&L'i ve banka verisi KULLANILMAZ. Kalibrasyon
çıktısına bağlı kullanıcı sorusu yok (tek istisna "kilit bekler" dalı).

## DEVAM — limit ya da oturum kesintisinden sonra buradan başla (son güncelleme 2026-09-30 07:08 UTC)

**>>> 30 EYLÜL ~22:00 UTC — GECE PLANI SONUCU: G1–G5 TAMAM, ADIM 3 KAPANDI <<<**
- G1: B provası (0eb0eee), tek atış betiği + T5 parite (72b1386); Codex T23→T25 düzeltmeleri (bb6ebdc, 3c07184, 945dd97).
- G2: Düzey 2 20:57 UTC bitti (5.140/5.140); B5 A kabul GEÇTİ 140/140 (c5f2a5a); 3.09 bitiş GEÇTİ (caeb3b6); duzey2
  dizüstünde (sha listesi sunucuyla aynı).
- G3: TOPLAMA TAMAM (8700d05); RAPOR.md (ed38944 → 53836d7): σ 0,30 varsayım, N 327, B2 bağlayıcı d* = 0,90,
  B5/B10 rapor, k_B6 = 2, Düzey 2-a 0/100; güç (B7'siz) P(KABUL|SR=1) ≈ %17.
- G4: Codex T26 10 karar DOĞRU; `kilit.onkosullar()` dizüstünde GEÇTİ. 4.01 (b695292) ön-kayda işlendi.
- G5: ana dal uzakta fast-forward (origin/claude/codex-tasarimi-8f1481-rgo4yj = 53836d7+); yerel codex-kirmizi
  çalışma kopyası 0ae923a'da kaldı (başka worktree; hook yazmayı engelliyor) — sabah `git pull --ff-only` orada.
- SIRADAKİ (kullanıcı onayıyla): 4.02 belgelerin nihai hali, 4.04 Codex kilit öncesi okuma, 4.06 KILIT. Kullanıcıya
  bırakılan: Hetzner sunucusunu SİLMEK (iş kalmadı; bütün çıktılar dizüstünde), age anahtar çifti, kilit onayı.

**>>> 30 EYLÜL ~20:15 UTC — GECE PLANI (kullanıcı uyuyor; kilit ÖNCESİNDE durulur) <<<**
Kural: her parça tek başına tamamlanır → test → commit; parçaya başlamadan önce bu listede "BAŞLADI" işaretlenir.
Limit (5 saatlik pencere ≥ %85 ya da haftalık ≥ %75) dolmak üzereyse yeni parça başlatılmaz; yarım parça commit edilmez
(çalışma kopyasında kalır, bu listede not düşülür). Sunucu işleri systemd'dedir, oturumdan bağımsız sürer.
- G1 B provası sonucu + commit; yürütücüye T5 parite (acik['parite']) + testler + commit (tek atış betiği dosyalarıyla).
- G2 Düzey 2 bitince aşağıdaki sıranın 1–4'ü (B5 kabul, 3.09 bitiş, sonuçları çekme) + commit.
- G3 Toplama (topla.py) + rapor_uret → RAPOR_TASLAK + 3.12 yorum bölümleri + commit.
- G4 Codex T23 (tek atış) ve 3.12 incelemesi; bulgular işlenir + commit.
- G5 Yan dal → ana dal fast-forward + push; yol haritası; sabah özeti. KILIT (4.06) yapılmaz — kullanıcı onayı.
Kullanıcıya bırakılan: Hetzner sunucusunu silmek, age anahtar çifti, kilit onayı.

**>>> 30 EYLÜL ~19:35 UTC — DÜZEY 2 BİTİNCE UYGULANACAK SIRA (en güncel; aşağıdaki 14:15 notunun yerine geçer) <<<**
Durum: Düzey 2 5.140 birimin 4.498'i (19:27 UTC), bitiş ~21:00 UTC. Kalibrasyon kod kimliği artık 5cee577f (B8 penceresi,
netleştirme 18); eşdeğerlik yeni kodla 4/4 (1d5769b). Banka tarafı: R2–R17, 6.09, 6.11 (saf), Codex T21/T22; tam takım 55/55.
1. `systemctl is-active v8-duzey2` inactive ve `kosucu ... durum` kalan 0 olunca:
2. **B5 A kabul koşusu** (ön-kayıt eki madde 2): `/opt/v8_kabul/AKTIF_MODEL/ciktilar/v8_b5_a_esdegerlik_20260930_01`
   (kod 5cee577f, jsonl boş) içinde `systemd-run --unit=v8-b5a-kabul --working-directory=$(pwd) /bin/sh -c "exec
   /opt/v8/venv/bin/python b5_a_esdegerlik.py /opt/v8/AKTIF_MODEL/ciktilar/v8_kalibrasyon_20260929_01/duzey2 --isci 12
   >> b5_a_cikti.txt 2>&1"`; bitince b5_a_esdegerlik.json(+jsonl, cikti) → dizüstü `ciktilar/v8_b5_a_esdegerlik_20260930_01/`.
3. **3.09 bitiş** (aynı anda koşabilir; farklı dizin): sunucuda `/opt/v8/AKTIF_MODEL/ciktilar/v8_kalibrasyon_20260929_01/`
   içindeki bitis.py, kanit.py, topla.py → `_arsiv_sunucu_20260930/`'a kopyala; yan daldaki sürümleri koy (deneme:
   `/opt/v8_bitis_deneme`'de --kuru dondurulmuş kodla sorunsuz, 19:30 UTC); `systemd-run --unit=v8-bitis ...
   /opt/v8/venv/bin/python bitis.py` → bitis_sonuc.json gecti=true olmalı.
4. `duzey2/` + bitis_sonuc.json (+bitis_tekrar/) dizüstüne (bu kopya: `ciktilar/v8_kalibrasyon_20260929_01/`, .gitignore'da).
   duzey1/ bu kopyaya alındı ve DUZEY1_OZET'e bağlandı (256 dosya).
5. **Toplama** dizüstünde: `python topla.py` (Düzey 1 ve 2 bağları zorunlu) → TOPLAMA.json; sonra 3.12 RAPOR, Codex, commit.
6. Yan dal → ana dal (claude/codex-tasarimi-8f1481-rgo4yj fast-forward), kullanıcıya sunucuyu SİLMESİNİ hatırlat.

**>>> 30 EYLÜL ~14:15 UTC DİZÜSTÜ GÜNCELLEMESİ (yan dal; bu oturumun çalışma dalı `claude/v8-502e-dizustu`, her commit
`claude/v8-kapi-motor-502e`'ye fast-forward push) — EN GÜNCEL DURUM BUDUR <<<**
- Eşdeğerlik son kodla GEÇTİ (4/4; motor db13ddad, kod cc6e9f02). Codex T19 + T20 işlendi (Düzey 1 bağı zorunlu; B5 A
  eşdeğerliği ön-kaydı `ciktilar/v8_b5_a_esdegerlik_20260930_01/ONKAYIT.md`; kilit B5 sonucunu zorunlu okur; R3 kararları
  BANKA §3.7 netleştirme 13).
- **B5 A erken koşusu (sunucu, eski betik sürümü) GEÇTİ 140/140, fark 0** (`erken_kosu/`). Ön-kayda göre erken uyarıdır;
  KABUL KOŞUSU Düzey 2 bitince: sunucuda `/opt/v8_kabul/AKTIF_MODEL/ciktilar/v8_b5_a_esdegerlik_20260930_01` altında
  (güncel kod hazır, jsonl boş) `systemd-run --unit=v8-b5a-kabul --working-directory=<o klasör> /bin/sh -c "exec
  /opt/v8/venv/bin/python b5_a_esdegerlik.py /opt/v8/AKTIF_MODEL/ciktilar/v8_kalibrasyon_20260929_01/duzey2 --isci 12
  >> b5_a_cikti.txt 2>&1"`; çıktıyı `ciktilar/v8_b5_a_esdegerlik_20260930_01/`'e çek, commit.
- 3.09: Düzey 2 bitince sunucudaki `/opt/v8/AKTIF_MODEL/ciktilar/v8_kalibrasyon_20260929_01/` bitis.py, kanit.py (ve
  topla.py) yan daldaki sürümle değiştirilir (eskiler arşive), `python bitis.py`; sonra `duzey2/` + bitis_sonuc.json
  dizüstüne; toplama dizüstünde (topla.py Düzey 1 bağını ister: duzey1/ + DUZEY1_OZET.json ana kopyada,
  `.claude/worktrees/codex-kirmizi`). Sonra yan dal ana dala (claude/codex-tasarimi-8f1481-rgo4yj; fast-forward).
- Banka: R3 (long_beta.py), rapor 1. parça (rapor.py: R9–R13a, R16), 2. parça (tanilar.py: R5, R6, R7, R14) TAMAM.
  Açık: R2, R4, R8, R13b, R15, R17, 6.09, 6.01b, 6.11.
- Düzey 2 (14:11 UTC) 1.849/5.129; tahmini bitiş ~21:30–22:00 UTC.

**>>> 30 EYLÜL ~10:00 UTC GÜNCELLEMESİ — AŞAĞIDAKİ KAPANIŞ NOTUNUN 1. MADDESİNİN YERİNE GEÇER <<<**
- **Düzey 2 artık Hetzner hesap sunucusunda** (CPX52, `ssh -i ~/.ssh/v8_hesap_ed25519 -o IdentitiesOnly=yes
  root@<sunucu>`; ayrıntı `ciktilar/v8_kalibrasyon_20260929_01/README.md` "Düzey 2 hesap sunucusunda").
  Dizüstünde Düzey 2 KOŞULMAZ, WMI/dilim tarifleri (madde 3 ve 5) tarihsel. Platform eşitliği testi FARKLI (kayan nokta
  düzeyi) → Düzey 2 sunucuda baştan, 12 işçi, dilimsiz systemd servisi `v8-duzey2`; dizüstünün 232 birimi
  `duzey2_dizustu_20260930/`. Kontrol: `systemctl status v8-duzey2` + `kosucu ... durum`. Bitince sunucuda `bitis.py`,
  sonuçları çek, kullanıcıya sunucuyu SİLMESİNİ hatırlat.
- **Bot sunucusu kullanıcı kararıyla silindi (30 Eylül); REV1 DEMO ileri dönemi bitti.** Aynı IP şimdi hesap sunucusu.
- **Kod işi bulut oturumunda sürebilir** (kullanıcı kararı): başlangıç notu `AKTIF_MODEL/v8/BULUT_OTURUMU.md`. Bulut
  oturumu yan dalda (`claude/v8-kapi-motor-502e`) çalışır; Codex ve eşdeğerlik koşusu dizüstüne kalır.

**>>> OTURUM KAPANIŞ NOTU (2026-09-30 07:08 UTC; kullanıcı oturumu kapattı) — YENİ OTURUM ÖNCE BUNU UYGULAR <<<**
1. [TARİHSEL — yukarıdaki güncellemeye bak] Düzey 2 dilim 2 WMI ile ÇALIŞIYOR olmalı (oturumdan bağımsız; 07:07'de 232 birim, `duzey2_dilim02.txt`).
   `(Get-Process python).Count` 0 ve kalan > 0 ise madde 3'teki WMI komutuyla dilim 03 olarak yeniden başlat.
2. Yan dal (`.claude/worktrees/codex-kirmizi-502e`, `claude/v8-kapi-motor-502e`, son commit bu notla birlikte):
   - Motor eşdeğerliği son motorla (carry_q eklendi, c4aa2bd) YENİDEN KOŞULMALI — arka plan koşusu oturumla öldü
     (yalnız A birincil "ayni" çıkmıştı). Komut (yan kopyada, `AKTIF_MODEL/ciktilar/v8_kalibrasyon_20260929_01`):
     `python esdegerlik_502e.py <ana kopya>/AKTIF_MODEL/ciktilar/v8_kalibrasyon_20260929_01/duman_4isci`
     (~45 dk; WMI ile başlatmak daha güvenli). Sonuç `esdegerlik_502e.json` (gecti + motor_kimligi_eski/yeni) → commit.
     Aynı koşuda motor regresyonu (mimari_b, geri_test, karar, carry, kapi_kosu, kapi_betimsel_kayit) da bitmedi.
   - Codex T17 (codex_cagrilari/20260930T17_kapi_kod_dogrulama_yanit.md) okundu, İŞLENMEDİ: 2 CIDDI + 4 ORTA:
     (a) CIDDI kanıt zinciri HAR/parametre değişikliğini kapsamıyor: duman/bitiş/eşdeğerlik kanıtlarına kod/parametre/
         HAR kimlikleri + kaynak hash'leri bağlanmalı, güncel girdilerle karşılaştırılmalı (kilit.onkosullar,
         esdegerlik_502e.py yalnız motor kimliği alıyor).
     (b) CIDDI banka_kos/kosucu.py'de aynı mühür açığı: hata şifreleme/yazımı başarısızsa bağlam açılıyor; devamda
         birincilin yeniden yürütülmesi hata sarmalayıcısını atlıyor → ortak hata sınırı, bağlam bastırma.
     (c) ORTA git_denetimi: tam 40 haneli commit zorunlu, `git fetch --prune origin`, yalnız origin referansları.
     (d) ORTA V5 saatlik: NaN/inf ve şekil/kapsam denetimi karşılaştırmadan önce.
     (e) ORTA s^C birebirliği artık toplamıyla gösterilemez → ayrıştırmaya isim/saat bazlı tüketilen s^C (sc_q gibi)
         çıktısı + diskten türetilenle mutlak 1e-12 karşılaştırma (motor değişir → eşdeğerlik tekrar).
     (f) ORTA geç funding'in bacağı "son işaret" ile değil özgün saat/yön ile bölünmeli; ters kayıt özgün bacağı tersler
         (ayrıştırma funding kaydının kapsadığı saatleri bilmeli; tasarım gerekli).
     Sonra belgeler Grup 6 (T17 kararları; arşiv önce) ve Codex T18.
   - `banka_kos/hukum.py` TASLAK, TESTSİZ (6.02a): HukumBaglami'na `kelly_cekis: int = kelly.CEKIS` ekle ve
     kelly_tablosu(..., cekis=hb.kelly_cekis) ver; sentetik birim sözlükleriyle test yaz (B2–B11 mekaniği, B7 kantili,
     B9 penceresi, B10, karar, R1, Kelly/stres şekli, birimleri_coz damga denetimi).
3. Kalan banka parçaları: ILERLEME_BANKA.md (6.01b veri yükleyici, R3 long-beta, 6.08 rapor satırları, 6.09, 6.11, 6.12).
4. Takip sayfası ve hafıza güncel (2026-09-30 07:08 UTC).

Kullanıcı isteği: limit dolup sıfırlandığında kaldığın yerden devam et. Oturumda saatlik bir "devam" hatırlatıcısı
kurulu (CronCreate, dakika 17; 7 günde kendiliğinden biter; oturum kapanırsa silinir). Kontrol listesi — her madde
tekrar koşulabilir (idempotent); zaten süren bir süreç ya da ajan varsa yenisini BAŞLATMA:
1. `git status` / `git log -3`; takip sayfasını oku (ArtifactData list `parcalar`, get `ozet/genel`).
2. **5.01 TAMAM** (Sonnet ajanı; OLCUT_LISTESI.md, 40 belirsizlik U-01…U-40; ana oturum yapıyı ve K1/K8/K11'i kaynağa
   karşı doğruladı). **5.01b TAMAM (grup 1 2a6421c, grup 2 24bd57a; CARRY ön-kaydı §15 "Uygulama netleştirmeleri" + §0/§12/§5.6 notları; arşiv _arsiv/V8_CARRY_NETLESTIRME_20260930_01/). Aşağıdaki 5.01b tarifi tarihseldir. Kod gereği 5.02'ye: ayristirma carry_coin + artik_coin.** **5.01b (Opus, ana oturum; boşta kalınca):** U-01…U-40'ı CARRY ön-kaydına göre değerlendir; çözümleri
   `CARRY_KAPISI_ONKAYIT_TASLAK.md` sonuna "Uygulama netleştirmeleri" eki olarak yaz (arşiv önce; kilitten önce; Codex
   kilit öncesi okumasında denetler). Öncelik: U-01 (r^trend,net), U-07 (K8 hedge dağıtımı), U-08 (CARRY metni MIMARI'nin
   29 Eylül güncellemelerinin gerisinde), U-09/U-20 (a^C ve icra artığı tanımı), U-02…U-13 (NW normalizasyonu, ddof, K5).
3. **KOŞU BAŞLATMA YÖNTEMİ (30 Eylül 06:48 UTC dersi):** nohup/arka plan Bash süreci oturum ya da limit kapanınca
   ÖLDÜRÜLÜYOR (dilim 1, 222 birimde 04:31 UTC'de kapanış günlüğü olmadan öldü; ~2 sa kayıp). Uzun koşuları yalnız
   PowerShell `Invoke-CimMethod -ClassName Win32_Process -MethodName Create -Arguments @{CommandLine="cmd.exe /c cd /d
   <v8> && <venv python> -m kalibrasyon.kosucu ..\ciktilar\v8_kalibrasyon_20260929_01\duzey2 duzey2 --isci 14
   --max_birim 500 > ..\ciktilar\v8_kalibrasyon_20260929_01\duzey2_dilimNN.txt 2>&1"; CurrentDirectory=<v8>}` ile
   başlat (WMI süreci oturumdan bağımsızdır). Denetim: `(Get-Process python).Count` 16 ise sürüyor; 0 ise ve kalan > 0
   ise aynı komutla sonraki dilim numarasıyla yeniden başlat. Dilim 2 başladı: 2026-09-30 06:48 UTC, `duzey2_dilim02.txt`.
3. **[TAMAM: duman geçti a064d57; Düzey 1 bitti 6dc6a1e; Düzey 2 dilim 1 başladı 2026-09-30 00:31 UTC, çıktı `duzey2_dilim01.txt`; dilim bitince (kalan > 0) sonraki dilimi `run_in_background` ile başlat, çıktı `duzey2_dilimNN.txt`]** 3.01 duman: `ciktilar/v8_kalibrasyon_20260929_01/duman_sonuc.json` varsa `gecti` alanına bak → true ise 3.01–3.02
   tamam, dosyaları (duman_*/ klasörleri dahil değil; yalnız duman_sonuc.json, duman_cikti.txt, duman.py, ilerleme.py)
   commit; false ise DUR, nedeni bul (koşuya geçme). Dosya yoksa ve `tasklist | grep python` duman süreçlerini
   göstermiyorsa → `duman.py`'yi yeniden koş (biten birimleri atlar).
4. **3.03 Düzey 1** (duman geçtiyse): v8 klasöründen
   `python -m kalibrasyon.kosucu ../ciktilar/v8_kalibrasyon_20260929_01/duzey1 duzey1 --isci 14` (arka planda; devam
   eder). Bitince 3.04: 128 zarf + npz doğrulaması, özet listesi commit.
5. **3.05–3.08 Düzey 2** (Düzey 1 bittiyse): dilimler halinde
   `python -m kalibrasyon.kosucu ../ciktilar/v8_kalibrasyon_20260929_01/duzey2 duzey2 --isci 14 --max_birim 500`
   (arka planda). Her dilim sonunda `python ../ciktilar/v8_kalibrasyon_20260929_01/ilerleme.py` → takipte 3.05–3.08
   `ilerleme`; sonra sonraki dilim. `kalan` 0 olunca 3.09 bitiş denetimi: `ciktilar/v8_kalibrasyon_20260929_01/`
   klasöründen `python bitis.py` (arka planda; 10 birim 1 işçiyle, ~1–2 sa) → `bitis_sonuc.json` `gecti` true olmalı
   (bütünlük, dört kimlik tek ve dondurmayla aynı, 10 birim bayt bayt aynı). Betik kuru modda duman klasöründe denendi.
   Sonra 3.10–3.11: aynı klasörden `python topla.py` (bir kez; ön koşul bitis gecti, kimlikler ve defter sha
   dondurmayla aynı) → TOPLAMA.json. Düzey 1 ya da 2-a KILIT_BEKLER ise DUR ve kullanıcıya sor (ön-kayıtta kullanıcıya
   ayrılmış tek dal). TAMAM ise 3.12 RAPOR.md (Opus + Sonnet), 3.13 Codex.
6. Her adımda takip sayfasını gerçek saatle güncelle (`date -u`). Mesaj yalnız adım sonunda / sorunda / onayda.
7. **SIRA KARARI (30 Eylül):** kapı kodu (5.02–5.04) ve Codex incelemesi (5.05) KİLİTTEN ÖNCE biter; KILIT.json kapı
   kodu kimliğini ve SEMBOL_FILTRELERI sha'sını da taşır (ölçüt kodu D'deki ilk P&L'den önce donar). Motor değişiklikleri
   (5.02e) ve 5.04 YAN ÇALIŞMA KOPYASINDA: `.claude/worktrees/codex-kirmizi-502e`, dal `claude/v8-kapi-motor-502e`
   (d5aefdf'ten). Bu dizindeki v8/motor'a Düzey 2 VE 3.09 bitene kadar dokunulmaz; 3.09 geçince dal buraya birleştirilir
   (motor kimliği o zaman değişir; kalibrasyon eşdeğerliği testle belgelenir). Sembol filtreleri alındı: d5aefdf.
8. **5.02 kapı kütüphanesi (Düzey 2 koşarken, ana oturum Opus)** — yeni paket `v8/kapi/` (dondurulmuş kalibrasyon
   kimlikleri yalnız v8/motor, v8/kalibrasyon, v8/banka'yı kapsar; `v8/kapi` koşuyu etkilemez). `v8/motor/`'a
   DÜZEY 2 BİTENE KADAR DOKUNMA (motor kimliği 7e2320f4 değişir). Parçalar (her biri test + commit + push):
   - 5.02a `kapi/istatistik.py` (Sharpe, SR^K, NW ortalama/OLS HAC, büyük SE, ρ_üst, K1*, K2 bootstrap, TOST, Andrews,
     standart yükleme) + `test_v8_kapi_istatistik.py` — TAMAM (bu commit).
   - 5.02b `kapi/seriler.py`: AyristirmaSonucu + günlük NAV → haftalık r^F, r^C, r^P, r^N, a^C, r^T, a^T (U-01, U-29,
     §5.3 ölçek ω_C·L; r^T ölçeği L) ve aylık (F − C) (U-06); hafta = Pazartesi 00:00 → sonraki Pazartesi, T0 sonrası
     tam haftalar (143). — TAMAM (NavOkuyucu, haftalik, aylik_fc, gunluk_ozdeslik_orani; 9 test, gerçek B koşusu dahil).
   - 5.02c `kapi/olcutler.py`: V3, V4a, V4b, K1–K11 değerlendirmesi + karar (§7.1), çift seri kuralı; hüküm/denetim
     sözlükleri (U-17, U-18). — TAMAM (degerlendir, v3, v4, k1…k11, pazartesi_bos_haftalar; 17 test). Betimsel
     raporlar (§6.6, BR-xx) ayrı parça 5.02f.
   - 5.02d faktörler x_B, x_A, x_R, x_S (U-19, U-24) — TAMAM (kapi/faktorler.py, girdiler sözlük; 8 test). Motor
     R30/s^trend'i karar kaydına YAZMIYOR → 5.02e'de hedef_b carry tanılarına 'r30', 's_trend' eklenecek.
   - 5.02e (Düzey 2 bittikten sonra) ayristirma.py'ye carry_coin + artik_coin (U-07, U-25) + özdeşlik testleri; motor
     kimliği değişir → kilitte yeni motor kimliği (kalibrasyonun kullandığı P&L yolu bayt bayt aynı kalmalı: test).
     Aynı parçada hedef_b.py Pazartesi carry_tan'a 'r30' ve 's_trend' (uygun isimler; tek kaynak, U-24).
   - 5.02f betimsel raporlar (§6.6 BR-xx; U-32…U-38). f1 seri tabanlı TAMAM (kapi/betimsel.py: φ, çeyrek, bileşik
     MDD, NW/Andrews t'leri, K11 ayrıntı + Wald, K1* duyarlılığı, a^C tanısı, delist K1; 8 test). f2 TAMAM
     (kapi/betimsel_kayit.py: κ tanısı + round-1 bant izleme, bağlama sıklıkları + S4, n_C, gerçekleşen kitap S1/S2/S4,
     hedefe ulaşılamayan gün, hedge yuvarlama, netleme + Σ|A^C_d|, V6 fark tanısı; 8 test, gerçek B koşusu dahil).
     Funding dolgu sayısı/katkısı (carry bacağı) motorda ayrıştırılmıyor → 5.02e. f3 isim tabanlı (long/short bacak,
     en kötü isim-hafta, sıfır/sıfır) 5.02e'den sonra.
   - Kod kararları U-41…U-55 CARRY §15 madde 11 + BELIRSIZLIK_COZUMLERI Grup 3 + MIMARI §5.1 notu olarak YAZILDI
     (arşiv _arsiv/V8_KILIT_ONCESI_NETLESTIRME_20260930_01/). Codex 5.05/4.04'ten yeni karar çıkarsa aynı yere eklenir.
   - YAN DAL DURUMU (claude/v8-kapi-motor-502e; ana dizinde bu dosyalara DOKUNMA, çakışma olur: v8/motor, v8/kapi,
     v8/kilit.py, testler/test_v8_kapi_*, test_v8_kilit): 5d9467a 5.02e motor çıktıları + 5.02f3 kapi/isim.py
     (regresyon 91/91); 01420e9 5.04 kapi/kosu.py + kapi/denetim.py (sentetik uçtan uca 3/3); c0c7cc6 4.03 kilit.py
     (4/4) + esdegerlik_502e.py. Eşdeğerlik koşusu yan kopyada arka planda: `ciktilar/v8_kalibrasyon_20260929_01/
     esdegerlik_502e.json` (gecti true olmalı; son_hash dışı bütün alanlar aynı) → yan dalda commit.
   - 5.05: Codex T15 (6 CIDDI + 9 ORTA) işlendi F1–F5 (yan dal 6b4e505…fce2a1a; belgeler Grup 4, d6bdfbb); kapı +
     yeni testler 115/115. Codex T16 doğrulaması ve son motorla eşdeğerlik koşusu arka planda (codex_cagrilari/
     20260930T16_*; esdegerlik_502e.json). Banka parçaları yan dalda sürüyor: ILERLEME_BANKA.md.
   - T16 (06:47 UTC okundu; codex_cagrilari/20260930T16_*_yanit.md): 7 KAPANDI, 7 KISMEN; yeni 1 CIDDI + 2 ORTA. Motor
     eşdeğerliği GEÇTİ (57236e6). YAPILACAK (yan dalda, sırayla; her biri test + commit):
     DURUM 07:03 UTC: F6 892e613, F7 849e495, F8 c4aa2bd (motor carry_q eklendi → eşdeğerlik YENİDEN koşuyor, sonuç
        yan kopyada esdegerlik_502e.json; gecti true + motor_kimligi_eski/yeni alanları olmalı → yan dalda commit),
        F9 25a1e91; belgeler Grup 5 ba95765 (yan dala birleştirildi 75c7027). Codex T17 arka planda
        (codex_cagrilari/20260930T17_*_yanit.md). Arka plan Bash işleri oturumla ölebilir: yanıt/sonuç dosyası yoksa
        yeniden başlat.
     F6 TAMAM (yan dal, birleştirme b180b5b + hata yolu). ESKİ TARİF: önce `git merge claude/codex-tasarimi-8f1481-rgo4yj` (Grup 4 belgeleri yan dala gelsin; T15-1/U-56…61 itirazları
        belge eksikliğinden). kapi/kosu.py hata yolu: HATA.txt yazımı ve print de try/except içinde, her çıkışta
        `raise KapiKosuHatasi(...) from None` (T16 CIDDI).
     F7 kilit: onkosul'da kanıt kimlik zinciri (bitis_sonuc kimlik.dondurmayla_ayni; esdegerlik motor_kimligi_yeni ==
        güncel motor ve eski == KOD_DONDURMA motor; esdegerlik_502e.py'ye motor_kimligi_eski ekle); git_denetimi
        beklenen commit parametresi (kosu.main --kilit_commit) + `git fetch` + `git show commit:yol` bayt eşitliği;
        V1 raporu bütün kod kimliklerini taşısın (v8_calistir.py test raporuna kapi/adaptor/banka/kalibrasyon/banka_kos/
        testler/kilit kimlikleri; kilit.v1_raporu bunları güncelle karşılaştırsın).
     F8 V2 beklenen gün kümesi (kosu.tek_kosu: [t0, bit) her gün; eksik = inf); V5 saatlik tüketim: ayristirma'ya
        carry_q (trend_q gibi) + V5'te disk kararlarından türetilen saatlik q ile karşılaştırma ve artik_carry = Σ sc·
        artik_coin denetimi; isim.bacak_serileri: q_eski = 0 iken eski pay (geç funding/ters kayıt) coinin SON sıfır
        olmayan miktar işaretine (epizot kuralıyla aynı).
     F9 age.coz katılığı: gövde satırı ≤ 64, kanonik b64 (yeniden kodla-karşılaştır), stanza gövdesi 32 bayt, dosya
        anahtarı 16 bayt; bozuk vektör testleri. Belgeler: Grup 5 (T16 kararları) + CARRY §15 madde 13. Sonra T17.
     Banka: banka_kos/yurutucu.py null birimi için veriyi birincil_son'da kesen yardımcı (veri_kes) eksik
        (test_v8_banka_yurutucu null testi IndexError); sonra 6.01b veri, R3 long-beta, 6.02 hüküm.
   - (eski) SIRADAKİ (yan dalda): 5.05 Codex kod incelemesi (kapi/, motor değişiklikleri, kilit.py, kosu.py) → bulgular →
     düzeltme. Sonra, Düzey 2 + 3.09 bitince: yan dalı birleştir, tam test takımı (v8_calistir test; yeni motor kimliği
     raporu V1 için), 3.10–3.13, 4.01 (kalibrasyon sonuçları BANKA'ya), 4.04 Codex kilit öncesi okuma, defter satırı
     A4-carry-kapisi (arşiv önce), `python -m kilit uret ../ciktilar/v8_kilit_<tarih>_01`, commit + push (4.06).

## Yüzdelik takip (kullanıcı isteği, 29 Eylül)
Sayfa: https://claude.ai/artifact/KjNLjD6ShUvYLdknDEmPqT ("v8 Yol Haritası"; db: `parcalar/<adım-no>` satırları
{sira, adim, kod, ad, ayrinti, saat, durum: tamam|suruyor|bekliyor|kullanici, ilerleme 0–1}, `ozet/genel`
{gecmis_saat 136, guncelleme, son_not}). Yüzde = tamamlanan tahmini saat / toplam (makine süresi dahil); genel yüzde
Adım 3 öncesi işleri 136 sa tek kalem sayar. KURAL: her parça bitince ya da başlayınca ilgili satır ve `ozet/genel`
güncellenir (ArtifactData, if_version ile); tahmin değişirse `son_not`'ta yazılır. Başlangıç: Adım 3 %32,8, genel %55,4.

## Çalışma biçimi (kullanıcı kararı, 29 Eylül)
Tam güç (`--isci 14`); uzun koşular ~500 birimlik dilimlerle (`--max_birim 500`), her dilimden sonra doğrulama ve
takip sayfası güncellemesi; mesaj yalnız adım sonlarında, sorunlarda ve onay gerektiğinde; Codex kapı noktalarında
(kalibrasyon raporu, kilit öncesi, kapı kodu, banka kodu 2 tur, dondurma öncesi).

## Ajan kullanımı (kullanıcı kararı, 29 Eylül)
Ana oturum ve yargı gerektiren işler Opus 5.5; mekanik işler Sonnet 5.5 ajanları (gerekirse tek kademe alt ajan).
Limit: ≤ ~20 dk'lık işe ajan açılmaz, aynı anda en fazla 2 ajan, ajan commit/push yapmaz ve D'ye/bankaya dokunmaz;
çıktıyı ana oturum inceler, test eder, commit eder. Takip sayfasında her parçanın `ajan` alanı var. Düzey 2 koşarken
Adım 5–6 kodu ajanlarla paralel yazılır (kod yazımı performans koşusu değildir; D'de ilk P&L yine kilitten sonra).

## Plan — küçük parçalar (kullanıcı isteği, 29 Eylül)
Kural: her parça ≤ ~45 dk aktif iş; "testler PASS → commit → push → aşağıdaki tabloda durum + günlüğe tek satır" ile
biter. Yarım kalan parça yalnız kendisini etkiler; yeni oturum ilk AÇIK parçadan başlar (önce `git status`).

| # | Parça | Durum |
|---|---|---|
| — | §3.7 3. revizyon + #22 + Codex T10/T11 | TAMAM (8fda91b) |
| P0 | Ölçüt kütüphanesi (`banka/olcutler, pnl, degerlendirme`; `ayristirma` coin başı trend çıktısı) | TAMAM |
| P1 | HAR banka modu: Pazartesi değerlendirme kümesi (`banka/har_banka.py`) | TAMAM |
| P2 | HAR banka modu: dondurulmuş β ile yürüyen ŝ² yolu + har_secimi eşlik testi | TAMAM |
| P3 | Düzey 2 üreteci: fiyat, OHLC, hacim, funding (`kalibrasyon/duzey2_uretec.py`) | TAMAM |
| P4 | Düzey 2 üreteci: yaşam döngüsü, 4h funding, borsa çapı boşluk | TAMAM |
| P5 | Bir Düzey 2 yolunda A ve B süre ölçümü → makine süresi tahmini | TAMAM |
| P6 | Rejim-null: blok permütasyonu, Y1–Y3 ataması (`banka/rejim_null.py`) | TAMAM |
| P7 | Rejim-null: getiri uzayında yeniden kurma, hacim/funding, N1–N6 | TAMAM |
| P8 | Düzey 1 P&L üreteci (`kalibrasyon/duzey1.py`) | TAMAM |
| P9 | Düzey 1 ölçüt eşlemesi B2–B11 | TAMAM |
| P10a | Düzey 1: e_B5, e_B10, k_B6 kuralları + birleşik kabul fonksiyonu | TAMAM |
| P10b | σ_SR_bağ betiği (REV1 kayıtlarına bakmadan), B2 türü, d*, tek ayar / kilit bekler dalları | TAMAM |
| P10c | B seyreltme raporu (trend + carry, ρ, SR_C) | TAMAM |
| P11 | Koşucu çekirdeği: kanonik tohum, birim kimliği, sonuç dosyası, bütünlük | TAMAM |
| P12a | Yürütücüler: Düzey 1 ayar birimi; Düzey 2 birincil / x2 / x3 / çıkarma / null birimleri | TAMAM |
| P12b | Koşucu: iş listesi, çok süreç, devam, B10 birimlerinin türetilmesi, ilerleme | TAMAM |
| P13 | Toplama betiği | TAMAM |
| P14 | Codex T12 kod incelemesi (yanıt geldi: 3 CIDDI, 7 ORTA, 1 DUSUK; yorum c ve e'ye itiraz) | TAMAM |
| P14a | Küçük düzeltmeler: ayristirma sıralı toplam (T12-2), muhasebe kapısı her birimde (T12-3), işçi parametre/beta denetimi (T12-9), 2-b B10 açıkça dışarıda (T12-10), ızgara eşiği epsilonsuz (T12-11) | TAMAM |
| P14b | B5 işaret değiştirme saatinin bölünmesi: pnl + ayristirma + degerlendirme (T12-1, yorum f) | TAMAM |
| P14c | Ek liste dayanıklılığı + artık dosya karantinası (T12-4), N3 yaşam sınırlarında (T12-6), HAR yetersiz haftada None (T12-5) | TAMAM |
| P14d | Motor verinin ilk gününden kesintisiz (T12-7, yorum e); seyreltmede B'ye ait B10 + "kısmi" etiketi (T12-8, yorum c); §3.7 uygulama netleştirmeleri eki (yorum a, b, e, f) | TAMAM |
| P14e | Codex T13 doğrulaması (yanıt: 10 KAPANDI, 3 KISMEN; yeni 1 CIDDI + 4 ORTA) | TAMAM |
| P14f | T13 düzeltmeleri: ayrıştırma NaN kapısı, pencere öncesi pozisyon, geç funding epizotu, iş listesi geçici dosyası, σ_SR kaynak kapsamı metni | TAMAM |
| P14g | Codex T14 doğrulaması; kod dondurma (defter satırı, tam takım, V8_KIMLIK) | TAMAM |
| P15 | Duman denetimi (4 işçi + durdur/devam vs 1 işçi ters sıra) | AÇIK |
| P16 | Düzey 1 koşusu (128 ayar, ayar başına dosya) | AÇIK |
| P17 | Düzey 2-a ve 2-b koşusu (~5.140 birim, parçalı) | AÇIK |
| P18 | Bitiş tekrarlanabilirlik denetimi, toplama, RAPOR, Adım 4 hazırlığı | AÇIK |

## Kesinti ve devam (kullanıcı sorusu, 29 Eylül)
Makinenin kesintisiz açık kalması gerekmez. Her tam motor koşusu bağımsız birimdir; bitince tek dosyaya atomik yazılır;
koşucu biten birimleri atlar. Kapanışta yalnız yarım kalan birimler (her biri birkaç dakika) yeniden koşar. Sonuç sıradan
ve paralellikten bağımsızdır (§3.7 "Kesinti ve devam").

## Durum günlüğü
- 29 Eylül: 3. revizyon yazıldı (arşiv `_arsiv/V8_BANKA_DUZEY2_20260929_01/`). Codex T10: 1 CIDDI (üst sınırda ölçüt
  kümesi = Düzey 1'de bağlayıcı kalanlar), 3 ORTA (etiket/tarama kuralı, kanonik tohum, atlama sözleşmesi), 1 DUSUK
  (eski ifadelere atıf) → hepsi işlendi; ayrıca Düzey 2 motor yapılandırması (HAR banka modu: dondurulmuş katsayı + yolun
  kendi yürüyen ŝ²'si) yazıldı. Codex T11: hepsi KAPANDI; DUSUK not (⊆, B12) işlendi. Plan madde 1 TAMAM (commit).
- P0 TAMAM: `banka/olcutler.py` (SR, DSR/η/SR₀, B4, B5 payı, B10 düşüşü, B11, Wilson), `banka/pnl.py` (coin başı
  saatlik P&L, NAV özdeşliği, epizot ataması), `banka/degerlendirme.py` (pencere, birincil ölçüm, B8 serisi, B10 sırası);
  `motor/ayristirma.py` coin başı trend bacağı (`trend_coin`, `trend_q`; önceki hali `_arsiv/V8_BANKA_KALIBRASYON_20260929_01/`).
  Testler: olcutler 11, pnl 9, degerlendirme 5; tam takım 20/20 PASS. Plan küçük parçalara bölündü (kullanıcı isteği).
- P1 TAMAM: `banka/har_banka.pazartesi_kumesi` (har_secimi.pit_evren'in tarih parametreli hali); test_v8_har_banka:
  betik içe aktarılıp sabitleri fikstüre çekilerek küme ve maske birebir aynı.
- P2 TAMAM: `har_satirlari`, `s2_yolu`, `banka_takvimi` (dondurulmuş β, verinin kendi yürüyen ŝ²'si, bütün takvim
  Pazartesileri). Eşlik: betiğin sentetik verisi + yürüyen katsayılarla 30 aylık katsayı ve ŝ² yolu sonuc_sentetik.json
  ile BİREBİR. Kısa fikstürde ilk ŝ² öncesi EWMA, sonrası HAR doğrulandı.
- P3 TAMAM: `kalibrasyon/tohum.py` (TOHUM_KAL = 1157334973; SHA-256 kanonik hash; PCG64) ve
  `kalibrasyon/duzey2_uretec.py` (ham_yol: sabit çekiş sırası, yaşam döngüsü çekişleri dahil; veri_kur: bütün barlar +
  8h funding). Yol başına ~0,2 sn. 9 test PASS (tohum regresyonu, vol, trend std/kalıcılık, OHLC, hacim, funding).
- P4 TAMAM: `veri_kur(ham, yasam=True)` listelenme / ölüm (son 10 gün hacim ×0,05) / 60 gün 4h funding / 12 saatlik borsa
  çapı boşluk; `yol_verisi(ayar_no, yol_no)`. 5 yeni test (motor boşluğu `bosluk_gecmis`'te görüyor); dosyada 14 test PASS.
- P6 TAMAM: `banka/rejim_null.py` blok ataması (120h tam bloklar, kuyruk yerinde, Y2 kenar bloklar, Y3 ortak + ikincil
  eşleme; coin başı saat eşlemesi permütasyon ve dilim içi). 8 test PASS. (P5 A süresi: 96 sn/koşu; B ölçülüyor.)
- P7 TAMAM: `sentetik_veri` (ρ getirileri, sıralı cumprod zinciri: düz bar bit düzeyinde korunur; hacim barla, funding
  blok içi göreli saatle), `degismezler` (N1–N6; N1 sıralı dörtlüler atol 1e-9), `null_yolu`. Düzey 2 yolunda N1–N6 geçti,
  motor null yolunda koşuyor. Dosyada 14 test PASS.
- P8 TAMAM: `kalibrasyon/duzey1.py` (128 ayar bit eşlemesi, 15 hat, geometrik epizotlar, a/σ_P/K/F/m, ortak rastgele
  sayılar SR'lar arasında; B9 portföyü ve B10 ikame hatları sabit çekiş sırasında). YORUM (Codex'e sorulacak): B10 ikame
  hattı ana ortak faktörü paylaşır. Yol başına ~5 ms. 7 test PASS.
- P9 TAMAM: `kalibrasyon/duzey1_olcut.py` (15 alan × 6 SR; B9 sabit kaydırma, B10 sıra ikamesi). YORUM (Codex'e
  sorulacak): B4 dilim seçimi için X %15 vol'e ölçeklenip Σln(1+x). Yol başına ~214 ms (256k yol ≈ 15 CPU saati). 5 test PASS.
- P5 TAMAM (`ciktilar/v8_kalibrasyon_sure_20260929_01/RAPOR.md`): A 96 sn/koşu, B 258 sn + ayrıştırma 207 sn. Toplam
  ≈ 230 CPU saati (2-a 140, 2-b 75, Düzey 1 15) ≈ 20–24 saat makine zamanı. B10 koşularında HAR takvimi yeni aday
  listesiyle kurulmalı (P12 notu).
- P10a TAMAM: `kalibrasyon/duzey1_esik.py` (ayar eşiği: frac(x < e) ≥ olasılık, ızgara katı, kesin büyük; e_B5/e_B10 = 128
  ayarın en büyüğü; k_B6; vektörel DSR; `Kurallar` + `kabul` (her ölçüt veto, nan kalır)). 4 test PASS.
  P10b için REV1 kayıt dosyası adayı: `GECMIS/2026_09_19_oncesi/DENEY_TRIAL_REGISTRY.csv` (içeriğe BAKILMADI).
- P10b TAMAM: `kalibrasyon/sigma_sr.py` (REV1 kaydı `DENEY_TRIAL_REGISTRY.csv` yalnız aile başına sayı taşıyor —
  yalnız başlık görüldü; deneme başına Sharpe yok → kural 1 gereği σ_SR_bağ = 0,30 "varsayım" cümlesiyle; Sharpe
  sütunlu kayıt incelemesiz okunmaz), `kalibrasyon/duzey1_karar.py` (N = 159 + Σ max(1, varyant); B2 türü, d* arama,
  tek ayar, KILIT_BEKLER). Güncel N_v8 = 167 (kalibrasyon satırıyla 168 → N = 327). 7 test PASS. Codex'e sorulacak:
  REV1 kaynak dosyası tanımı.
- P10c TAMAM: `duzey1_olcut.seyreltme_olculeri` (σ_C = σ_P/3, ρ {0; 0,30}, SR_C {−0,3; 0; 0,3}; Z = X + C üzerinde SR, DSR,
  B3, B4, B6, B11; B5/B8/B9/B10 A'dan). Carry gürültüsü Düzey 1 çekiş sırasının SONUNA eklendi (önceki çekişler aynı).
  YORUM (Codex'e): sadeleştirme. Düzey 1 testleri 7 + 7 + 4 + 7 PASS.
- P11 TAMAM: `kalibrasyon/birim.py` (birim adı, dört kimlik: kod = kalibrasyon + banka, motor = v8_calistir tanımı,
  parametre = Parametreler + HAR sonuc sha, ortam; kanonik JSON zarf, npz eki, geçici + os.replace, doğrulama ve
  `_karantina/`). 5 test PASS.
- P12a TAMAM: `kalibrasyon/yurutucu.py` (duzey1_birimi: 2.000 yol × 6 SR, ölçüt + seyreltme dizileri; duzey2_birimi:
  birincil (tam ölçüm + B10 sırası), x2/x3, çıkarma (aday listeden; HAR takvimi yeni aday listesiyle), null (N1–N6
  ihlali → NullDegismezHatasi)). Kısa pencereli 4 test PASS (~65 sn).
- P12b TAMAM: `kalibrasyon/kosucu.py` (`python -m kalibrasyon.kosucu <çıktı> duzey1|duzey2|durum [--isci N]`;
  IS_LISTESI.json hash'li ve değişirse ret; IS_LISTESI_EK.jsonl türetilen B10 birimleri; işçi başlangıcında kod/motor/
  ortam kimliği denetimi; `DUR` dosyasıyla duraklatma; ilerleme.log yalnız sayı). 5 test PASS: kesinti + devam (2–3 işçi)
  ile 1 işçi ters sıra bayt bayt aynı.
- P13 TAMAM: `kalibrasyon/toplama.py` (b7_gecer ⌈α·n⌉; duzey2_satiri; 2-a özeti: p̂ + Wilson + tarama; 2-b özeti: q90/q95,
  sıra yüzdeliği, taban (B3/B10 satırda etkisiz) + B7; R16 tablosu; duzey1_topla / duzey2_topla dosyalardan). 7 test PASS
  (sahte 128 + ~5.100 birim dosyasıyla uçtan uca). SIRADAKİ: P14 Codex kod incelemesi.
- Düzey 1 süresi tek iş parçacığıyla yeniden ölçüldü: 0,052 sn/yol → 128 ayar ≈ 3,7 CPU saati (P9'daki 214 ms arka planda
  koşan B ölçümüyle çakışmıştı). Toplam ≈ 220 CPU saati. Tam takım 30/30 PASS (P13 öncesi).
- P14 BAŞLADI: Codex T12 istemi `codex_cagrilari/20260929T12_kalibrasyon_kod_inceleme_istem.md` (yorumlar 2a–2g dahil).
  Dondurma commit'inde: deneme defterine `V8-kalibrasyon` satırı (varyant 0 → +1; N = 327), tam takım, V8_KIMLIK.
- P14a TAMAM: ayristirma sıralı dolaşım; `yurutucu.muhasebe_kapisi` (NAV sonlu/pozitif, zincir, coin P&L ve ayrıştırma
  özdeşliği ≤ 1e-8·max NAV; her birimde; ihlal → MuhasebeHatasi); `har_paketi` (sha + beta aynı baytlardan), işçi
  parametre/beta denetimi; 2-b `e_b10=None`; `_yukari` epsilonsuz. test_v8_kalibrasyon_kapilar 5 PASS (B birincil
  PYTHONHASHSEED 1 ve 12345 ile ayrı süreçlerde bayt bayt aynı); etkilenen 7 test dosyası PASS. Önceki kod
  `_arsiv/V8_BANKA_KALIBRASYON_20260929_01/P14_oncesi/`.
- P14b TAMAM: `banka/pnl` eski/yeni payları (eski: q0·(açılış − sk(T)) + funding + kapanan kısmın maliyeti; yeni:
  q1·(sk(T+1h) − açılış) + açılan kısmın maliyeti; işaret değişiminde maliyet |q0| : |q1|), `epizot_pnl(q, eski, yeni)`;
  `motor/ayristirma` trend_eski/trend_yeni (aynı kural); degerlendirme ikisini kullanır. Elle kurulmuş işaret değişimi
  testi + pnl 11, degerlendirme 5, mimari_b 21 PASS.
- P14c TAMAM: koşucu başlangıçta `*.gecici` karantinaya; yarım ek-liste satırında dosya karantina + doğrulanmış
  birincillerden yeniden kurma; `sonuc_oku` zarfsız npz'yi karantinaya alır; N3 giriş/çıkış yalnız gerçek yaşam
  sınırlarında; `s2_yolu(hepsi=True)` ve `banka_takvimi` tanımsız Pazartesileri None yazar (eski ŝ² taşınmaz). Testler:
  har_banka 4, rejim_null 15, kosucu 6, birim 6 PASS.
- P14d TAMAM: Düzey 2 motoru verinin ilk gününden (varsayılan `motor_bas_ms = BAS_MS`; testler kısa başlangıç verir;
  gövdede `karar_sayisi`); seyreltmede B9 = SR(X^K + C), B10 Z üzerinde ikame; BANKA §0.2 madde 7 + §3.7 sonu "Uygulama
  netleştirmeleri" (10 madde) + Ek C T12 satırı (önceki metin `_arsiv/V8_BANKA_NETLESTIRME_20260929_01/`). Süre etkisi:
  Düzey 2 koşuları ~%25 uzar (tahmin ≈ 270 CPU saati; duman denetiminde yeniden ölçülecek). yurutucu 5, kapilar 5,
  duzey1_olcut 8 test PASS.
- P14f TAMAM (Codex T13 yanıtı `codex_cagrilari/20260929T13_*`): ayristirma sonlu olmayan fark → inf; muhasebe kapısı
  coin/ayrıştırma dizilerini sonluluk için tarar; `epizot_pnl(..., q_onceki)` pencere başında süren epizot; eski pay
  yeniden açılan epizota gitmez; `.gecici` karantinası iş listesinden önce; BANKA §3.7 netleştirme 7 kaynak kapsamı kararı.
  Testler pnl 12, degerlendirme 5, kapilar 6, kosucu 7, mimari_b 21 PASS. (Tam takım bu düzenlemeyle çakıştığı için
  dondurmada yeniden koşulacak.)
- P14g TAMAM — KOD DONDURULDU: Codex T14 8/8 KAPANDI, yeni bulgu yok; temiz tam takım 32/32 PASS
  (v8/ciktilar/test_20260929T195741Z); deneme defterine `V8-kalibrasyon` satırı (N_v8 168, N 327; önceki defter
  `_arsiv/V8_KALIBRASYON_DONDURMA_20260929_01/`); `ciktilar/v8_kalibrasyon_20260929_01/KOD_DONDURMA.json` (kod c442f5ba…,
  motor 7e2320f4…, parametre 80c67909…, ortam python 3.12.14 / numpy 2.5.1) ve README (koşu, duraklatma, devam).
  SIRADAKİ: P15 duman denetimi (`duman.py`).
- 5.01 TAMAM (Sonnet ajanı, ~10 dk, 195k token): `ciktilar/v8_kapi_20260929_01/OLCUT_LISTESI.md` (V1–V6, S1–S12,
  K1–K11, BR-01…28, BX-01…08, U-01…U-40). Ana oturum doğruladı. Yeni parça 5.01b (belirsizliklerin çözümü, Opus).
