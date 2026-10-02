Sen v8 kripto motorunun bağımsız kod inceleyicisisin. T16'da carry kapısı kodunun düzeltmelerini doğrulamıştın
(yanıtın: AKTIF_MODEL/v8/codex_cagrilari/20260930T16_kapi_kod_dogrulama_yanit.md; 7 KISMEN, yeni 1 CIDDI + 2 ORTA,
"henüz kilide hazır değil"). Bunlar işlendi. Şimdi son DOĞRULAMA turu. Çalışma kökü bu git çalışma kopyasıdır (dal
claude/v8-kapi-motor-502e). T16'daki HEAD e0403c1 idi; değişiklikler: `git log --oneline e0403c1..HEAD` ve
`git diff e0403c1 -- AKTIF_MODEL/v8 AKTIF_MODEL/ciktilar/v8_kalibrasyon_20260929_01/esdegerlik_502e.py`.
Hiçbir dosyaya yazma; yalnız metin yanıt ver. Kodu ve testleri KOŞMA.

Bağlayıcı belgeler (bu commit'te güncel): CARRY_KAPISI_ONKAYIT_TASLAK.md §15 (madde 1–13) ve
AKTIF_MODEL/ciktilar/v8_kapi_20260929_01/BELIRSIZLIK_COZUMLERI.md Grup 1–5 (U-01…U-64; Grup 4 = T15, Grup 5 = T16).

Görevler:
1. T16'da KISMEN kalan 7 madde (T15-1, 2, 3, 4, 5, 6, 9, 10, 13 içinden KISMEN olanlar) ve T16'nın 3 yeni bulgusu için:
   KAPANDI | KISMEN | ACIK + tek cümle gerekçe (dosya:satır). Özellikle: kapi/kosu.py hata yolu; kilit.py
   onkosullar (kanıt kimlik zinciri), git_denetimi (sabit commit, fetch, git show eşitliği), v1_raporu +
   v8_calistir.py kod_kimlikleri_hepsi; kapi/denetim.py v5_saatlik; motor/ayristirma.py carry_q; kapi/kosu.py V2 gün
   kümesi; kapi/isim.py geç funding işareti; banka_kos/age.py katı biçim.
2. Düzeltmelerin getirdiği yeni sorun (özellikle motor/ayristirma.py carry_q'nun P&L'i ve özdeşliği değiştirmediği).
3. Grup 4 ve Grup 5 kararları (U-44, U-45, U-49, U-51 düzeltmeleri; U-56…U-64; U-58/U-59 ekleri): her biri tek satır
   KABUL | ITIRAZ.
4. Genel hüküm: kapı kodu, kalibrasyon bitince yapılacak adımlarla (yan dalın birleştirilmesi, tam test takımı ve V1
   raporu, eşdeğerliğin son motorla yeniden koşulması, toplama, kilit) kilide hazır mı?

Yanıt biçimi (Türkçe):
## kapanis
`<madde> KAPANDI|KISMEN|ACIK — gerekçe`
## yeni_bulgular
`[OLDURUCU|CIDDI|ORTA|DUSUK] başlık — dosya:satır — sorun — düzeltme` (en fazla 8; yoksa "yok")
## kararlar
`U-xx KABUL|ITIRAZ — gerekçe (≤25 kelime)`
## genel_hukum
1–2 cümle.

Yasaklar: BANKA_MUHURLU.json, uygun_evren.json, SECIM.json, secim_cikti.json okunmaz, dosya bilgisi de sorgulanmaz
(AKTIF_MODEL/ciktilar/v8_banka_20260924_01 klasörünü listeleme; yalnız V8_DENEME_DEFTERI.csv açık yoluyla okunabilir);
banka coinleri/Z1/Z2 araştırılmaz; D verisi, v8_veri klasörü ve ham zip'ler okunmaz;
ciktilar/v8_sembol_filtreleri_20260930_01/exchangeInfo_ham.json okunmaz; .env okunmaz; config.py import edilmez;
REV1 motoruna (AKTIF_MODEL/motor), bota, sunucuya dokunulmaz; web yok; hiçbir dosyaya yazma; kod koşma.
