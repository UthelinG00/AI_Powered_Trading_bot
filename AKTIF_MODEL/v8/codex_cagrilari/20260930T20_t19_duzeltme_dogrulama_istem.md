Sen v8 kripto motorunun bağımsız kod inceleyicisisin. T19'da (yanıtın:
AKTIF_MODEL/v8/codex_cagrilari/20260930T19_kapi_banka_dogrulama_yanit.md) 2 CIDDI ve R3 için 2 ORTA bulgu verdin;
U-59-ek-4, U-66 ve R3'e İTİRAZ ettin. Bunlar dizüstü oturumunda işlendi. Şimdi KISA doğrulama turu (T20). Çalışma kökü bu
git çalışma kopyasıdır; T19'daki HEAD 9ad4c3b idi: `git log --oneline 9ad4c3b..HEAD`, `git diff 9ad4c3b -- AKTIF_MODEL`.
Hiçbir dosyaya yazma; yalnız metin yanıt ver. Kodu ve testleri KOŞMA.

Değişenler:
- CIDDI-1 Düzey 1 bağı: AKTIF_MODEL/ciktilar/v8_kalibrasyon_20260929_01/topla.py (`duzey1_bagi`, on_kosullar dördüncü dönüş
  değeri, main'de hesap sonrası yeniden doğrulama), AKTIF_MODEL/v8/kilit.py (`duzey1_ozet_bagi`, onkosullar'daki
  karşılaştırma), testler AKTIF_MODEL/v8/testler/test_v8_kilit.py (duzey1_klasoru, ToplaBagiTest.test_duzey1_ozete_bagli,
  test_main_hesap_sirasinda_degisen_duzey1, KanitZinciriTest.test_toplamanin_tukettigi_duzey1_ozetle_ayni_olmali).
  Dizüstünde gerçek Düzey 1 klasörüne (128 birim) salt okuma ile uygulandı: 256 dosya bağlandı.
- CIDDI-2 B5 A eşdeğerliği: ön-kayıt AKTIF_MODEL/ciktilar/v8_b5_a_esdegerlik_20260930_01/ONKAYIT.md ve betik
  b5_a_esdegerlik.py (sunucuda dondurulmuş platformda koşuyor; sonuç henüz yok). Kabul/ret kuralı ön-kayıtta.
- R3: BANKA_ONKAYIT_TASLAK.md §3.7 netleştirme 13 (b), (d), (e) yeniden yazıldı (evren `a_t`; çıkış motor icra kurallarıyla).
- Kararlar: AKTIF_MODEL/ciktilar/v8_kapi_20260929_01/BELIRSIZLIK_COZUMLERI.md Grup 8 (U-59 ek 5, U-66 eki, R3).

Görevler:
1. T19 yeni bulguları ve itirazları için KAPANDI | KISMEN | ACIK + tek cümle gerekçe (dosya:satır): Düzey 1 bağı;
   B5 A eşdeğerliği (ön-kayıt ve betik tasarımı yeterli mi: kapsam 140 A birincil, karşılaştırma son_hash hariç bütün
   gövde, kimlik sabitliği, girdi hash'leri, ret halinde tam yeniden koşu; kapsam dışı bıraktıklarımız doğru mu); R3 (b),
   (d), (e).
2. Düzeltmelerin getirdiği yeni sorun (özellikle duzey1_bagi'nin gerçek DUZEY1_OZET.json biçimiyle uyumu, kilit
   karşılaştırmasının kanit.birlesik ile aynı tanımı kullanması, b5_a_esdegerlik.py'nin yeniden başlatmada jsonl'dan
   yalnız aynı güncel kimlikli satırları alması).
3. Grup 8: her satır tek satır KABUL | ITIRAZ.
4. Genel hüküm: B5 A eşdeğerliği 140/140 çıkarsa kapı kilide kalan adımlarla (3.09 bitiş yan daldaki bitis.py + kanit.py;
   toplama yan daldaki topla.py; birleştirme; tam takım + V1) hazır mı? R3 tanımı kodlanmaya hazır mı?

Yanıt biçimi (Türkçe):
## kapanis
`<madde> KAPANDI|KISMEN|ACIK — gerekçe`
## yeni_bulgular
`[OLDURUCU|CIDDI|ORTA|DUSUK] başlık — dosya:satır — sorun — düzeltme` (en fazla 6; yoksa "yok")
## kararlar
`<kod> KABUL|ITIRAZ — gerekçe (≤25 kelime)`
## genel_hukum
1–2 cümle.

Yasaklar: BANKA_MUHURLU.json, uygun_evren.json, SECIM.json, secim_cikti.json okunmaz, dosya bilgisi de sorgulanmaz
(AKTIF_MODEL/ciktilar/v8_banka_20260924_01 klasörünü listeleme; yalnız V8_DENEME_DEFTERI.csv açık yoluyla okunabilir);
banka coinleri/Z1/Z2 araştırılmaz; D verisi, v8_veri klasörü ve ham zip'ler okunmaz;
ciktilar/v8_sembol_filtreleri_20260930_01/exchangeInfo_ham.json okunmaz; .env okunmaz; config.py import edilmez;
REV1 motoruna (AKTIF_MODEL/motor), bota, sunucuya dokunulmaz; web yok; hiçbir dosyaya yazma; kod koşma.
