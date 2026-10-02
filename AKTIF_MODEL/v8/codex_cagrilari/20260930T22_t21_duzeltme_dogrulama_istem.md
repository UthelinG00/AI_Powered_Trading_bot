Sen v8 kripto motorunun bağımsız kod inceleyicisisin. T21'de (yanıtın:
AKTIF_MODEL/v8/codex_cagrilari/20260930T21_banka_rapor_inceleme_yanit.md) banka kodunda 3 CIDDI + 7 ORTA bulgu verdin.
Bunlar işlendi ve bir yeni hata bulundu: B8'in günlük funding toplamı son güne yığılıyordu (banka/pnl.gunluk_topla).
Şimdi KISA doğrulama turu (T22). Çalışma kökü bu git çalışma kopyasıdır; T21'deki HEAD 78b7c56 idi:
`git log --oneline 78b7c56..HEAD`, `git diff 78b7c56 -- AKTIF_MODEL/v8 AKTIF_MODEL/ciktilar/v8_asama4_20260927_01`.
Hiçbir dosyaya yazma; yalnız metin yanıt ver. Kodu ve testleri KOŞMA.

Bağlayıcı kararlar: BANKA_ONKAYIT_TASLAK.md §3.7 netleştirme 16 (d) carry epizot payı, 17 (a)–(i) T21 düzeltmeleri,
18 B8 penceresi. Kod: banka_kos/veri_denetim.py, tanilar.py (durum_izi, r5, r6, piyasa_serileri, r17_sayimlar, b8_serisi,
carry_epizot_payi), rapor.py (r4_rev1, r12, sharpe_ga_tablosu, r8_b), rapor_md.py, long_beta.py (r3_karsilastirma),
yurutucu.py (gun_sonu_agirliklari side='left', b8_r, r8_carry_epizot), hukum.py (B2 alanları), banka/pnl.py
(gunluk_topla). Eşdeğerlik (ciktilar/v8_kalibrasyon_20260929_01/esdegerlik_502e.json) yeni kodla 4/4 aynı.

Görevler:
1. T21'in 10 bulgusu için KAPANDI | KISMEN | ACIK + tek cümle gerekçe (dosya:satır).
2. Netleştirme 18: gunluk_topla düzeltmesi doğru mu; kalibrasyonun etkilenmediği gerekçesi (kalibrasyon/yurutucu.py
   t_son = pencere sonu − 1 saat) her birim türü için (birincil, x2, x3, null, çıkarma; Düzey 1 dahil) geçerli mi;
   gunluk_topla'nın başka tüketicisi var mı; banka yürütücüsünde başka "pencere dışı saat" yığılması (B5 epizotları,
   birincil_olcum'un başka toplamları, sadece_sharpe) kalmış mı?
3. Düzeltmelerin getirdiği yeni sorun (gun_sonu_agirliklari side değişiminin stres nesnelerine etkisi dahil).
4. Genel hüküm: banka betiği 6.01b veri yükleyicisi ve 6.12 tam motorlu uçtan uca dışında kuru koşuya hazır mı?

Yanıt biçimi (Türkçe):
## kapanis
`<no> KAPANDI|KISMEN|ACIK — gerekçe`
## b8
kısa paragraf, her iddiaya dosya:satır
## yeni_bulgular
`[OLDURUCU|CIDDI|ORTA|DUSUK] başlık — dosya:satır — sorun — düzeltme` (en fazla 6; yoksa "yok")
## genel_hukum
1–2 cümle.

Yasaklar: BANKA_MUHURLU.json, uygun_evren.json, SECIM.json, secim_cikti.json okunmaz, dosya bilgisi de sorgulanmaz
(AKTIF_MODEL/ciktilar/v8_banka_20260924_01 klasörünü listeleme; yalnız V8_DENEME_DEFTERI.csv açık yoluyla okunabilir);
banka coinleri/Z1/Z2 araştırılmaz; D verisi, v8_veri klasörü ve ham zip'ler okunmaz;
ciktilar/v8_sembol_filtreleri_20260930_01/exchangeInfo_ham.json okunmaz; .env okunmaz; config.py import edilmez;
REV1 motoruna (AKTIF_MODEL/motor), bota, sunucuya dokunulmaz; web yok; hiçbir dosyaya yazma; kod koşma.
