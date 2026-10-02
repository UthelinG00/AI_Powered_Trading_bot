Sen v8 kripto motorunun bağımsız kod inceleyicisisin. T23'te (yanıtın:
AKTIF_MODEL/v8/codex_cagrilari/20260930T23_tek_atis_inceleme_yanit.md) tek atış betiğinde 5 CIDDI + 5 ORTA bulgu verdin.
Düzeltmeler önce ön-kayda yazıldı (BANKA_ONKAYIT_TASLAK.md §3.7 netleştirme 20 (f)–(k)), sonra kodlandı. KISA doğrulama
turu (T24). T23'teki HEAD 72b1386 idi: `git log --oneline 72b1386..HEAD`, `git diff 72b1386 -- AKTIF_MODEL/v8
AKTIF_MODEL/ciktilar/v8_asama4_20260927_01`. Hiçbir dosyaya yazma; yalnız metin yanıt ver. Kodu ve testleri KOŞMA.

Kod: v8/banka_kos.py, v8/veri_denetim.py (denetim_hesapla, sinirli), v8/banka_kos/acilis.py (t1_denetimi, tohum_turet,
acilis_oku boyut, baglam_kur kimlik denetimi, bagla, damga_farki, hazirla anonim_anahtar/tohum), banka_kos/parite.py
(_onek, karar_paritesi), banka_kos/veri.py (eksik_dosyalar, Eylül kaynağı), testler test_v8_banka_acilis.py,
test_v8_banka_veri.py.

Görevler:
1. T23'ün 10 bulgusu için KAPANDI | KISMEN | ACIK + tek cümle gerekçe (dosya:satır).
2. Düzeltmelerin getirdiği yeni sorun (özellikle: VERI_DENETIM.json'un kanonik birebir yeniden hesabı determinist mi —
   sözlük sırası, kayan nokta, yükleyici raporu; hata sınırının kendi hataları ve AcilisHatasi mesajlarında sızıntı;
   20 k'nın ilk_motor_sha256 tanımının T1'i zayıflatıp zayıflatmadığı).
3. Genel hüküm: banka betiği dondurmaya (Adım 7) hazır mı?

Yanıt biçimi (Türkçe):
## kapanis
`<no> KAPANDI|KISMEN|ACIK — gerekçe`
## yeni_bulgular
`[OLDURUCU|CIDDI|ORTA|DUSUK] başlık — dosya:satır — sorun — düzeltme` (en fazla 6; yoksa "yok")
## genel_hukum
1–2 cümle.

Yasaklar: BANKA_MUHURLU.json, uygun_evren.json, SECIM.json, secim_cikti.json okunmaz, dosya bilgisi de sorgulanmaz
(AKTIF_MODEL/ciktilar/v8_banka_20260924_01 klasörünü listeleme; yalnız V8_DENEME_DEFTERI.csv açık yoluyla okunabilir);
banka coinleri/Z1/Z2 araştırılmaz; D verisi, v8_veri klasörü ve ham zip'ler okunmaz;
ciktilar/v8_sembol_filtreleri_20260930_01/exchangeInfo_ham.json okunmaz; .env okunmaz; config.py import edilmez;
REV1 motoruna (AKTIF_MODEL/motor), bota, sunucuya dokunulmaz; web yok; hiçbir dosyaya yazma; kod koşma.
