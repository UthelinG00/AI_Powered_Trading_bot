Sen v8 kripto motorunun bağımsız kod inceleyicisisin. T15'te carry kapısı kodunu incelemiştin (yanıtın:
AKTIF_MODEL/v8/codex_cagrilari/20260930T15_kapi_kod_inceleme_yanit.md; 6 CIDDI, 9 ORTA; "kilide hazır değil").
Bulguların işlendi. Şimdi DOĞRULAMA turu. Çalışma kökü bu git çalışma kopyasıdır (dal claude/v8-kapi-motor-502e).
T15'teki HEAD c0c7cc6 idi; düzeltmeler: `git log --oneline c0c7cc6..HEAD` ve `git diff c0c7cc6 -- AKTIF_MODEL/v8`.
Hiçbir dosyaya yazma; yalnız metin yanıt ver. Kodu ve testleri KOŞMA.

Bağlayıcı belgeler (bu commit'te güncel): CARRY_KAPISI_ONKAYIT_TASLAK.md §15 (madde 1–12),
AKTIF_MODEL/ciktilar/v8_kapi_20260929_01/BELIRSIZLIK_COZUMLERI.md (Grup 1–4; U-01…U-61; Grup 4 = T15 kararları).

Görevler:
1. T15'in 15 bulgusunun her biri için: KAPANDI | KISMEN | ACIK + tek cümle gerekçe (dosya:satır).
   Özellikle: T15-2 (hata yolu mühürü: kapi/kosu.py), T15-3/4/5/15 (kilit.py ön koşullar, kapsam, git bağı, V1 raporu,
   ortam), T15-6 (kapi/denetim.py a_referans_durumu ve v6_hedefleri), T15-13 (motor/ayristirma.py carry_eski/yeni ve
   kapi/isim.py bacak_serileri), T15-14 (kapi/betimsel_kayit.py S4 ve devreden kitap).
2. Düzeltmelerin getirdiği YENİ sorun var mı (motor P&L'ini değiştiren bir değişiklik dahil)? `motor/ayristirma.py`
   değişikliklerinin P&L satırlarını ve özdeşliği değiştirmediğini statik olarak doğrula.
3. U-44, U-45, U-49, U-51 düzeltmeleri ve U-54…U-61: her biri tek satır KABUL | ITIRAZ.
4. Yeni modül `banka_kos/age.py` (age v1, X25519; BANKA §2.4 kör hüküm için): resmi age-encryption.org/v1 biçimiyle
   uyum (başlık, stanza gövdesi sarma, HKDF tuz/bilgi, header MAC kapsamı, STREAM nonce ve son parça kuralı, Bech32
   anahtar metinleri) ve güvenlik hataları. Uyumsuzluk varsa satır ve düzeltme.

Yanıt biçimi (Türkçe):
## t15_kapanis
`T15-n KAPANDI|KISMEN|ACIK — gerekçe`
## yeni_bulgular
`[OLDURUCU|CIDDI|ORTA|DUSUK] başlık — dosya:satır — sorun — düzeltme` (en fazla 10; yoksa "yok")
## kararlar
`U-xx KABUL|ITIRAZ — gerekçe (≤25 kelime)`
## age
`UYUMLU | UYUMSUZ` + maddeler
## genel_hukum
1–2 cümle: kapı kodu (kalibrasyon bitince yapılacak son testlerle) kilide hazır mı?

Yasaklar: BANKA_MUHURLU.json, uygun_evren.json, SECIM.json, secim_cikti.json okunmaz, dosya bilgisi de sorgulanmaz
(AKTIF_MODEL/ciktilar/v8_banka_20260924_01 klasörünü listeleme; yalnız V8_DENEME_DEFTERI.csv açık yoluyla okunabilir);
banka coinleri/Z1/Z2 araştırılmaz; D verisi, v8_veri klasörü ve ham zip'ler okunmaz;
ciktilar/v8_sembol_filtreleri_20260930_01/exchangeInfo_ham.json okunmaz; .env okunmaz; config.py import edilmez;
REV1 motoruna (AKTIF_MODEL/motor), bota, sunucuya dokunulmaz; web yok; hiçbir dosyaya yazma; kod koşma.
