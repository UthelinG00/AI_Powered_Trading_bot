Sen v8 kripto motorunun bağımsız inceleyicisisin. Kilit Adım 3 (sentetik kalibrasyon) bitti; rapor yazıldı (T26; 3.12).
Çalışma kökü bu git çalışma kopyasıdır. Hiçbir dosyaya yazma; yalnız metin yanıt ver. Kod KOŞMA.

Girdiler: `AKTIF_MODEL/ciktilar/v8_kalibrasyon_20260929_01/RAPOR.md` (rapor), `TOPLAMA.json` (topla.py çıktısı; sha256
raporun başında), `bitis_sonuc.json` (3.09), `AKTIF_MODEL/ciktilar/v8_b5_a_esdegerlik_20260930_01/b5_a_esdegerlik.json`
(B5 A kabul koşusu), kurallar `AKTIF_MODEL/ciktilar/v8_asama4_20260927_01/BANKA_ONKAYIT_TASLAK.md` §3.3 ve §3.7, kod
`AKTIF_MODEL/v8/kalibrasyon/` (duzey1_esik.py, duzey1_karar.py, toplama.py, sigma_sr.py), `v8/kilit.py`.

Görevler:
1. Raporun "Kararlar ve gerekçe" bölümündeki her karar TOPLAMA.json'daki değerlerle ve §3.3/§3.7 kurallarıyla birebir mi
   (σ_SR_bağ ve kaynağı, e_B5, e_B10, k_B6, B2 türü, d* arama sırası, tek ayarın uygulanmaması, Düzey 2-a ölçüt kümesi ve
   kural, B7 q95)? Rapordaki güç sayıları (P(KABUL | SR) ortalamaları, 2-b) TOPLAMA ile tutarlı mı?
2. REV1 N sorusu: `GECMIS/2026_09_19_oncesi/DENEY_TRIAL_REGISTRY.csv` yalnız `trial_count` ve `included_primary_dsr`
   sütunlarına bakarak (Sharpe/getiri değeri yok) N_REV1 = 159'un doğru sayım olup olmadığını söyle; 318 toplamının
   nedeni ne? §3.3 "N = 159 (REV1) + N_v8" ile N = 327 tutarlı mı (N_v8 = 168; deneme defteri
   `AKTIF_MODEL/ciktilar/v8_banka_20260924_01/V8_DENEME_DEFTERI.csv` açık yoluyla okunabilir)?
3. Kanıt zinciri: TOPLAMA'nın kanıt bloğu (KOD_DONDURMA, HAR, bitiş, Düzey 1/2 kaynak hash'leri) kilit.onkosullar'ın
   beklediği biçimde mi; B5 A kabul sonucunun kilit.py denetimini geçeceği görülüyor mu?
4. Raporda eksik ya da yanıltıcı ifade (özellikle güç, "tarama kuralı" ve sınırlar).

Yanıt biçimi (Türkçe):
## kararlar
`<no> DOGRU|YANLIS|BELIRSIZ — gerekçe (dosya:satır ya da JSON yolu)`
## n_sorusu
kısa paragraf
## bulgular
`[OLDURUCU|CIDDI|ORTA|DUSUK] başlık — yer — sorun — düzeltme` (en fazla 8; yoksa "yok")
## genel_hukum
1–2 cümle: kalibrasyon kilit için hazır mı?

Yasaklar: BANKA_MUHURLU.json, uygun_evren.json, SECIM.json, secim_cikti.json okunmaz, dosya bilgisi de sorgulanmaz
(AKTIF_MODEL/ciktilar/v8_banka_20260924_01 klasörünü listeleme; yalnız V8_DENEME_DEFTERI.csv açık yoluyla okunabilir);
banka coinleri/Z1/Z2 araştırılmaz; D verisi, v8_veri klasörü ve ham zip'ler okunmaz;
ciktilar/v8_sembol_filtreleri_20260930_01/exchangeInfo_ham.json okunmaz; .env okunmaz; config.py import edilmez;
REV1 motoruna (AKTIF_MODEL/motor), bota, sunucuya dokunulmaz; REV1 kaydında Sharpe/getiri değerleri okunmaz; web yok;
hiçbir dosyaya yazma; kod koşma.
