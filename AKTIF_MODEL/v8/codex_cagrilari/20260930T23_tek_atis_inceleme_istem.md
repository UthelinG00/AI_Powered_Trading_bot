Sen v8 kripto motorunun bağımsız kod inceleyicisisin. Bu, banka betiğinin (Adım 6) son inceleme turudur (T23; 6.13).
Çalışma kökü bu git çalışma kopyasıdır. T22'den sonraki değişiklikler: `git log --oneline 1bea183..HEAD`,
`git diff 1bea183 -- AKTIF_MODEL/v8 AKTIF_MODEL/ciktilar/v8_asama4_20260927_01 AKTIF_MODEL/ciktilar/v8_banka_prova_20260930_01`.
Hiçbir dosyaya yazma; yalnız metin yanıt ver. Kodu ve testleri KOŞMA.

Bağlayıcı kararlar: BANKA_ONKAYIT_TASLAK.md §2.3–§2.5, §8.1 ve §3.7 netleştirme 19 (banka veri yükleyicisi) ve 20
(tek atış betiği, veri denetim betiği, ACILIS girdisi, T1 kimlik denetimi, T5 parite, kuru koşu dönemleri).
Kod: `v8/banka_kos/veri.py`, `v8/banka_kos/acilis.py`, `v8/banka_kos/parite.py`, `v8/veri_denetim.py`, `v8/banka_kos.py`,
`v8/banka_kos/yurutucu.py` (birincil birimde `acik['parite']`), testler `test_v8_banka_veri.py`, `test_v8_banka_acilis.py`.
Tam motorlu sentetik prova (bütün birimler gerçek yürütücüyle; `ciktilar/v8_banka_prova_20260930_01/prova.py`,
`ozet_A.json`, `ozet_B.json`, `BANKA_RAPORU_SENTETIK_*.md`) geçti.

Görevler:
1. Netleştirme 19 ve 20 ile kod birebir mi? Özellikle: (a) T1 alanlarının kapsamı (`acilis.kimlikler`: banka_kos_sha256
   hangi dosyaları kapsıyor; hüküm ve rapor kodu kapsamda mı; DONDURMA §1.4 ile uyum); (b) VERI_DENETIM → banka_kos
   kapıları (T2, veri kimliği, dönem, kimlikler, ACILIS/DONDURMA sha'ları) atlatılabilir mi; (c) işçi bağlamı her
   işçide aynı mı (veri kimliği, filtreler, anonim eşleme, dönem); (d) T5 parite tanımı MIMARI §5.6 ile uyumlu mu
   (durum öneği, funding adımı, maske, B'de carry durumu; 1e-12 toleransı yalnız ağırlıklarda).
2. Açık gruba (denetim/, VERI_DENETIM.json, IS_LISTESI.json, DENETIM_OZETI.json, ekrana basılanlar) coin adı ya da
   performans sızıyor mu? (BK-2, §8.1 K1-16; mühür: banka coin adları açık grupta geçmemeli.)
3. Kuru kip (20 e): dönemler D'ye doğru taşınmış mı, tek kullanımlık alıcının devamda tutarlılığı, kuru sonuçlarının
   §2.5 "D kuru koşu çıktıları hash düzeyinde aynı" karşılaştırmasına taban olabilmesi (determinizm: sıra, işçi
   sayısı, zaman damgası içeren alanlar).
4. Banka veri yükleyicisi (19): D penceresi dışlaması, iki kaynağın birleşimi, Eylül API funding görüntüsü, dönem
   sonu, veri kimliği; T2 (1) onarılamayan satır yükleyiciden önce yakalanıyor mu (veri_denetim.py)?
5. Hata ve kesinti yolları: çıkış kodları, DUR dosyası, kesintiden sonra aynı komut (IS_LISTESI kimlikleri sabit mi),
   hata izinin şifreli kalması (BK-11).
6. Genel hüküm: banka betiği dondurmaya (Adım 7) hazır mı; kilitten önce kapatılması gereken ne kaldı?

Yanıt biçimi (Türkçe):
## bulgular
`[OLDURUCU|CIDDI|ORTA|DUSUK] başlık — dosya:satır — sorun — düzeltme` (en fazla 12; yoksa "yok")
## sizinti
kısa paragraf, her iddiaya dosya:satır
## genel_hukum
1–3 cümle.

Yasaklar: BANKA_MUHURLU.json, uygun_evren.json, SECIM.json, secim_cikti.json okunmaz, dosya bilgisi de sorgulanmaz
(AKTIF_MODEL/ciktilar/v8_banka_20260924_01 klasörünü listeleme; yalnız V8_DENEME_DEFTERI.csv açık yoluyla okunabilir);
banka coinleri/Z1/Z2 araştırılmaz; D verisi, v8_veri klasörü ve ham zip'ler okunmaz;
ciktilar/v8_sembol_filtreleri_20260930_01/exchangeInfo_ham.json okunmaz; .env okunmaz; config.py import edilmez;
REV1 motoruna (AKTIF_MODEL/motor), bota, sunucuya dokunulmaz; web yok; hiçbir dosyaya yazma; kod koşma.
