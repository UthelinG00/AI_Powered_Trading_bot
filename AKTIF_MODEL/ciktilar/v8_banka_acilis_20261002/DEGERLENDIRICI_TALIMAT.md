# Değerlendirici oturum talimatı (v8 banka açılışı; BANKA_ONKAYIT §2)

Sen v8 kripto projesinin **değerlendirici oturumusun**: tasarıma katılmadın; görevin mühürlü bankayı ön-kayıttaki
protokolle açmak, veriyi indirmek ve tek atış banka koşusunu başlatmaktır. Performans sonucunu hüküm açılışına kadar
görmezsin; kimse göremez (sonuçlar kullanıcının age açık anahtarına şifreli). Tasarım oturumu (DONDURMA'yı üreten oturum)
banka coinlerini ve mühürlü dosyaları görmemelidir: ona ve sohbete **coin adı, tarih listesi ya da performans
yazma; yalnız sayılar ve hash'ler**.

## Bağlayıcı belgeler (oku)

- `AKTIF_MODEL/ciktilar/v8_asama4_20260927_01/BANKA_ONKAYIT_TASLAK.md`: §2 (açılış protokolü, tamamı), §3.7 netleştirme
  19 (banka veri yükleyicisi ve paket düzeni), 20 (a, b, c, f, g, j, k, l, m: ACILIS, T1, sıra, hata sınırı), 21 (g).
- `AKTIF_MODEL/ciktilar/v8_dondurma_hazirlik_20261001/UYGULAMA_EK.md` (U2: banka girişi; rev 2: `dondurma_commit`).
- Dondurma: `AKTIF_MODEL/ciktilar/v8_dondurma_20261002/DONDURMA.json`, commit
  `de596953cadbad43c1cc699d6391ed8693de821c` (dal `claude/v8-502e-dizustu`, uzakta). Mimari **A**.
- Kod: `AKTIF_MODEL/v8/` (dondurulmuş; **hiçbir dosyasını değiştirme** — değişiklik T1 verir). Okuyabileceğin kod:
  `veri_denetim.py`, `banka_kos.py`, `banka_kos/` (özellikle `acilis.py`, `veri.py`, `anonim.py`), `adaptor/`.

Tasarım belgelerini (MIMARI, CARRY, kalibrasyon raporları, kapı ve kuru koşu çıktıları, eğitim notları) ve hafıza
notlarını kullanma; görevin için gerekmezler.

## Ortam

- Dizüstü: Windows; Python yorumlayıcısı **`<depo>/venv/Scripts/python.exe`** (3.12.14, numpy 2.5.1). Çıplak `python`
  yanlıştır.
- Hesap sunucusu: `ssh -i ~/.ssh/v8_hesap_ed25519 -o IdentitiesOnly=yes root@<sunucu>` (Hetzner CPX52, 12 çekirdek).
  Depo `/opt/v8/repo` (sparse; aynı dal, GitHub salt-okunur anahtarı kurulu, `git pull` çalışır), yorumlayıcı
  `/opt/v8/venv/bin/python` (kilitteki ortam). D paketi `AKTIF_MODEL/ciktilar/v8_veri_20260924_01` altında yerinde.
  Banka koşusu **sunucuda** yapılır (kuru koşu da orada yapıldı; ikisi aynı makinede olmalı).
- Sunucudaki sparse checkout mühürlü klasörden (`ciktilar/v8_banka_20260924_01`) yalnız iki dosya içerir; açılış için
  gereken dosyaları sunucuya sen taşırsın (aşağıda).

## Adımlar

**A. Bankanın yeniden üretimi (§2.2).** Girdiler `AKTIF_MODEL/ciktilar/v8_banka_20260924_01/` içinde: `banka_sec.py`,
`DAMGA.json`, `SECIM.json`, `uygun_evren.json`, mühür belgesi. sha256 denetimleri §2.2'deki değerlerle; drand turu
DAMGA'dan, BLS imzası zincir anahtarıyla doğrulanır; Python 3.12'de `banka_sec.py`; çıktıların hash'leri SECIM ile
birebir. Herhangi bir eşleşmezlik → **dur**, veri indirme; kullanıcıya "T1" bildir.

**B. İndirme listesi (§2.3).** Bir betikle üret (ör. `ciktilar/v8_banka_acilis_20261002/indirme_listesi.py`; bu betik
dondurulmuş kodun parçası değildir, çıktısı manifestle bağlanır). Kapsam §2.3: K (80) ve D (120) + BTC/ETH dosyaları,
CHECKSUM dosyaları, Eylül funding kaynağı (2026-09 aylık arşiv yayımlandıysa o; yoksa API tek görüntüsü — ayrı satır),
süreklilik denetimi sayısı. Paket düzeni ve `BANKA_MANIFEST.jsonl` biçimi netleştirme 19 (i) ve `banka_kos/veri.py`
ile aynı olmalı (yükleyicinin beklediği alanlar: kodu oku). Sohbete yalnız: dosya sayısı, toplam boyut, coin sayısı
(K/D/BTC-ETH), Eylül funding kaynağı, süreklilik sorunu sayısı. **Kullanıcı onayını bekle.**

**C. İndirme (onaydan sonra, sunucuda).** Banka kökü öneri: `/opt/v8/banka_veri/` (git dışı). CHECKSUM doğrulaması; ilk
indirmenin hash'leri `BANKA_MANIFEST.jsonl`'a (bağlayıcı). Sohbete: indirilen/eksik/checksum hatalı sayıları.

**D. ACILIS.json (20 a, j; UYGULAMA_EK rev 2).** Sunucuda, git dışı (coin adları içerir), ör.
`/opt/v8/banka_acilis/ACILIS.json`: {`mimari`: "A", `adaylar`, `k_coinleri` (80), `d_coinleri` (120),
`gorulmus_gunler` (7, YYYY-MM-DD), `banka_kok`, `anonim_anahtar` (yol; `banka_kos.anonim.anahtar_uret` ile önceden
üret), `sureklilik_sorunu`, `dondurma_commit`: "de596953cadbad43c1cc699d6391ed8693de821c"}; `d_kok` verilmezse mevcut D
paketi. Denetimler `acilis.acilis_oku`'da (K ⊆ adaylar, D ⊆ adaylar, K∩D = ∅, adaylar − {BTC, ETH} = K ∪ D, |K| = 80,
|D| = 120).

**E. Veri denetimi (T2; §2.3, 8.02).** Sunucuda, `AKTIF_MODEL/v8` içinden:
`/opt/v8/venv/bin/python veri_denetim.py banka <çıktı> /opt/v8/banka_acilis/ACILIS.json ../ciktilar/v8_dondurma_20261002/DONDURMA.json`
(argümanlar için betik başlığını oku). Çıktı klasörü öneri: `AKTIF_MODEL/ciktilar/v8_banka_kosu_20261002`. Bu adım
DONDURMA T1'ini ve kilit zincirini (git, uzak commit'ler) de denetler. Çıkış 0 ve `T2: false` olmalı.
`denetim/VERI_DENETIM.json` coin adı içermez; özetini (sayılar) kullanıcıya sun. **Koşu için kullanıcı onayını bekle.**

**F. Tek atış koşusu (8.03; onaydan sonra).** Sunucuda systemd ile (kuru koşudaki `/etc/systemd/system/v8-kuru.service`
örneğine bak; yeni servis `v8-banka`, `Restart=no`, ortam değişkenleri OMP/MKL/OPENBLAS/NUMEXPR_NUM_THREADS=1):
`banka_kos.py banka <aynı çıktı> <ACILIS> <DONDURMA> --isci 12`. `banka_kos.py` **bir kez** çağrılır (§2.4); kesilirse
aynı komut devam eder (iş listesi aynı olmalı). Beklenen süre ~1–1,5 saat (kuru koşu 56 dk). Bitince yalnız
`denetim/DENETIM_OZETI.json` (T1–T5, birim sayısı, damga kökü) ve `SONUC_DAMGA.json` kökünü bildir. `sonuc/` altındaki
şifreli dosyalara dokunma.

**G. Teslim.** Açık grup dosyalarını (`denetim/VERI_DENETIM.json`, `denetim/DENETIM_OZETI.json`, `SONUC_DAMGA.json`,
`IS_LISTESI.json`) depoya commit edip it; ACILIS.json, anonim anahtar ve eşleme, banka verisi git dışında kalır. Kör
denetim listesi (8.04) ve hüküm açılışı (8.05, kullanıcının gizli anahtarıyla `banka_hukum.py`) sonraki adımlardır.

## Yasaklar

- `v8/` altında hiçbir dosyayı değiştirme; DONDURMA, KILIT ve teknik ek dosyalarına dokunma.
- Şifreli sonuçları açmaya, gizli anahtar istemeye ya da performans hesaplamaya çalışma.
- Sohbete ve commit mesajlarına coin adı, görülmüş günler, Z1/Z2 içeriği yazma.
- `.env` okuma; `config.py` import etme; REV1 motoruna (`AKTIF_MODEL/motor`) ve bota dokunma; gerçek para yok.
- Her eşleşmezlik ya da beklenmeyen durumda dur ve kullanıcıya sabit, coin adsız bir özetle bildir.
