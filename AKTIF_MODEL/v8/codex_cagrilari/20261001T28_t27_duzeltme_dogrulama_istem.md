Sen v8 kripto projesinin bağımsız inceleyicisisin. T27'de (yanıtın:
AKTIF_MODEL/v8/codex_cagrilari/20261001T27_kilit_oncesi_okuma_yanit.md) kilidi engelleyen 4 CIDDI çelişki, 4 ORTA/DÜŞÜK
çelişki ve 3 belirsizlik verdin. Düzeltmeler önce ön-kayda yazıldı, sonra kodlandı; kapı sentetik doğrulaması koşuldu ve
kullanıcı iki karar verdi (#26 yayım, #27 kapı eşikleri değişmez). KISA doğrulama turu (T28; kilit öncesi son okuma).
`git log --oneline 2d5f0a0..HEAD` yerine şunu kullan: `git log --oneline -20`; değişiklikler `git diff f0bf370 --
AKTIF_MODEL/ciktilar AKTIF_MODEL/v8/kilit.py AKTIF_MODEL/v8/testler/test_v8_kilit.py` (exchangeInfo_ham.json HARİÇ).
Hiçbir dosyaya yazma; yalnız metin yanıt ver. Kod KOŞMA.

Kaynaklar: CARRY_KAPISI_ONKAYIT_TASLAK.md §15 madde 16; BANKA_ONKAYIT_TASLAK.md §3.7 netleştirme 21, §3.4 tablo, §4 madde
5, §7.2; ACIK_SORU_YANITLARI.md #23–#27; `ciktilar/v8_kapi_sentetik_20261001/` (kapi_sentetik.py, sonuc.json, RAPOR.md,
ONKAYIT_OLCEK.md, kapi_sentetik_olcek.py, duyarlilik_olcek.json); `ciktilar/v8_kalibrasyon_20260929_01/` (topla.py,
TOPLAMA.json, RAPOR.md); `v8/kilit.py` (n_kilit, onkosullar, teknik_ek, zincir_dogrula, KILIT_BELGELERI); deneme defteri
(açık yoluyla).

Görevler:
1. T27'nin her maddesi için KAPANDI | KISMEN | ACIK + tek cümle (dosya:satır).
2. Kapı sentetik betiği CARRY §8.5 ve §15 madde 16 (c) eşlemesiyle birebir mi (senaryolar, s tanımı, AR(1), maliyet,
   K5 ay ataması, K6/K7/K8, tohum)? Ölçek duyarlılığı ön-kaydıyla uyumlu mu ve dondurulmuş sonucun yerine geçmediği açık mı?
3. N = 329: defterin yeni iki satırı (V8-kapi-sentetik varyant 0, A4-carry-kapisi varyant 1) sayım kuralına uygun mu;
   topla.py'nin "baş kısım" kuralı ve N ≥ dondurma koşulu madde 8 ve 21 (f) ile tutarlı mı; TOPLAMA'nın kararları
   N = 327'dekiyle aynı mı?
4. Yeni sorun ve kilit hazırlığı: KILIT için kalan engel var mı?

Yanıt biçimi (Türkçe): ## kapanis / ## sentetik / ## n_defter / ## yeni_bulgular (`[CIDDI|ORTA|DUSUK] başlık — yer — sorun
— düzeltme` ya da "yok") / ## genel_hukum (1–2 cümle: KILIT için hazır mı).

Yasaklar: BANKA_MUHURLU.json, uygun_evren.json, SECIM.json, secim_cikti.json okunmaz, dosya bilgisi de sorgulanmaz
(AKTIF_MODEL/ciktilar/v8_banka_20260924_01 klasörünü listeleme; yalnız V8_DENEME_DEFTERI.csv açık yoluyla okunabilir);
banka coinleri/Z1/Z2 araştırılmaz; D verisi, v8_veri klasörü ve ham zip'ler okunmaz;
ciktilar/v8_sembol_filtreleri_20260930_01/exchangeInfo_ham.json okunmaz; .env okunmaz; config.py import edilmez;
REV1 motoruna (AKTIF_MODEL/motor), bota, sunucuya dokunulmaz; web yok; hiçbir dosyaya yazma; kod koşma.
