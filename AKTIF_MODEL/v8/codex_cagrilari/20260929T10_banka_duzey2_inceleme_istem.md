Sen v8 kripto motorunun bağımsız inceleyicisisin. 2. turda (KC-02) BANKA ön-kaydının sentetik kalibrasyonunu (§3.7)
sen sıkılaştırdın; Düzey 2'de "B7 dahil birleşik yanlış kabul" ölçümü o turun sonucudur. Şimdi o bölüm hesap kapasitesi
yüzünden revize edildi (3. revizyon, 29 Eylül; kullanıcı kararı). Görev: revizyonun istatistiksel olarak geçerli ve
belge içinde tutarlı olup olmadığını bağımsız olarak incelemek. Hiçbir dosyaya yazma; yalnız metin yanıt ver. Kod koşma.

Bağlam (doğrula, olduğu gibi kabul etme):
- 2. turun Düzey 2 planı: 6 ayar (κ ∈ {0; 0,0262; 0,0523} × HL ∈ {30; 90}) × 100 temel yol; her yolda birincil, ×2, ×3,
  10 tek coin çıkarma ve 200 null yolu; A ve B. ≈ 127.800 tam motor koşusu/mimari. Ölçülen motor hızı (122 coinlik
  sentetik fikstür): A ~0,18 s/gün, B ~0,45–0,58 s/gün; Düzey 2 yolu 30 coin, ~1.170 değerlendirme günü + 365 gün ısınma.
  Tahmin: tam koşu A ~2–4 dk, B ~5–8 dk → ~15.000–30.000 CPU saati; makine 16 mantıksal çekirdek. Kullanıcı "1+"
  seçeneğini onayladı: B7 q95'e sabit; κ = 0'da null'suz motor kontrolü (üst sınır); B7 gücü betimsel.
- Karar anında Adım 3'ün hiçbir koşusu yapılmadı; D P&L'i ve banka verisi üretilmedi (kilit Adım 2 HAR seçimi QLIKE ile,
  P&L'siz tamamlandı).

Oku:
- AKTIF_MODEL/ciktilar/v8_asama4_20260927_01/BANKA_ONKAYIT_TASLAK.md: §0.2, §1.2 (tablo satırı 3 ve "Adım 1 ile Adım 3
  arasındaki sıra"), §1.4 `kalibrasyon`, §3.3 (kural 3–4), §3.4 (B7 satırı), §3.5 (özellikle 3.5.1, 3.5.6, "Bilinen
  sınırlar"), §3.7 tamamı (Düzey 1 ve 3. revizyon Düzey 2), §8.2 madde 4 ve 12, §10 madde 15, Ek B, Ek C sonu.
- Önceki hali: AKTIF_MODEL/_arsiv/V8_BANKA_DUZEY2_20260929_01/BANKA_ONKAYIT_TASLAK.md (aynı bölümler; `git diff` gibi
  karşılaştır).
- AKTIF_MODEL/ciktilar/v8_asama4_20260927_01/ACIK_SORU_YANITLARI.md son bölüm (#22).
- Gerekirse: AKTIF_MODEL/ciktilar/v8_asama4_20260927_01/CODEX_KIRMIZI_TAKIMI.md (KC-02).

Özellikle sına:
1. Üst sınır argümanı: KABUL_birleşik = KABUL_B7siz ∧ B7 mi, yoksa belgede B7'nin başka bir ölçütü ya da eşiği etkilediği
   (ör. d*, e_B5, B2 türü, "tek önceden yazılı ayar") bir yol var mı? Düzey 1 ile Düzey 2-a arasında ölçüt seti tutarlı mı?
2. B7'yi q95'e sabitlemek meşru bir kilit öncesi revizyon mu (sonuç görülmeden, hesap kapasitesi gerekçesiyle)? §1.2'nin
   "kalibrasyon çıktısı kullanıcı seçimine açılmaz" ilkesini ihlal ediyor mu? Kuantil tanımı (⌈α·n⌉'inci sıralı değer, n = 500)
   doğru ve yeterli mi?
3. Düzey 2-a: tek κ = 0 ayarı, 100 yol, A ve B, 13 koşu/yol yeterli mi? Wilson %3,7 üst sınır hesabı doğru mu? "> %5 →
   kilit bekler" kuralı yeni tasarımda anlamlı mı? B10 ve B3'ün koşu sayıları doğru mu?
4. Düzey 2-b: betimsel güç tasarımı (5 ayar × 10 yol × 50 null, yalnız A; κ = 0 ayarı 2-a'nın 1–10. yollarını kullanıyor)
   açıkça karar girdisi dışında mı? Bir sonucun yine de bir kararı etkileyebileceği gizli bir yol var mı?
5. Tohum ve kesinti/devam kuralları: sonuç sıradan, paralellikten ve kesintiden gerçekten bağımsız mı? Eksik kalan bir
   belirlenimsizlik kaynağı (iş parçacığı sayısı, dosya sırası, sözlük sırası, zaman okuma) ya da "yarım yazılmış birim"
   riski var mı? Tekrarlanabilirlik denetimi yeterli mi?
6. Maliyet aritmetiği (2.600 + 2.540 ≈ 5.140 koşu; ~255.600 eski) ve belge içi tutarlılık: q90'dan söz eden, eski Düzey 2
   ayar kuralına ya da "B7 dahil ölçüm"e atıf yapan ve güncellenmemiş bir yer kaldı mı?

Yanıt biçimi (Türkçe):
## bulgular
Her bulgu: `[OLDURUCU|CIDDI|ORTA|DUSUK] başlık — konum — sorun — önerilen düzeltme` (en fazla 8; yoksa "yok").
## sorular_1_6
Her soru için tek satır: `EVET/HAYIR/KISMEN — gerekçe (≤30 kelime)`.
## genel_hukum
1–2 cümle: revizyon kilide (Adım 4) girmeye uygun mu?

Yasaklar: BANKA_MUHURLU.json, uygun_evren.json, SECIM.json, secim_cikti.json okunmaz, dosya bilgisi de sorgulanmaz
(v8_banka_20260924_01 klasörünü listeleme); banka coinleri/Z1/Z2 araştırılmaz; D verisi ve ham zip'ler okunmaz; .env
okunmaz; config.py import edilmez; REV1 motoruna, bota, sunucuya dokunulmaz; web yok; hiçbir dosyaya yazma.
