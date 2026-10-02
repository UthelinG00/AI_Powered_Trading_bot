# v8 banka hükmü: RET (8.05–8.06)

Tarih: 2 Ekim 2026. Hüküm kullanıcının bilgisayarında, kullanıcının gizli anahtarıyla `banka_hukum.py` ile açıldı
(`--dt_commit fe808db`). `hukum/HUKUM_KIMLIK.json`: banka_sonuc `85661542…`, rapor `93777075…`. Mimari A (yalnız trend;
carry kapısı A), N_hüküm 331, B2 türü B (d* = 0,90, σ_SR = 0,30 varsayım).

## Bağlayıcı ölçütler

| ölçüt | değer | eşik | sonuç |
|---|---|---|---|
| B2 DSR | 0,139 | 0,90 | kaldı |
| B3 (×2 maliyet SR) | 0,233 | 0,30 | kaldı |
| B4 | −0,071 | 0,30 | kaldı |
| B6 (dilimler) | 3 | 2 | geçti |
| B7 rejim-null | 0,262 | 0,868 (q95) | kaldı |
| B8 | 0,495 | > 0 | geçti |
| B9 görülmemiş coinler | 0,081 | > 0 | geçti |
| B11 | 0,204 | ≤ 0,30 | geçti |

Birincil örneklem: SR 0,262 (%90 GA [−0,68; 1,14]), CAGR %1,2, vol %5,1, MDD %7,2. Z1 dilimleri SR 0,76 / 0,87 /
0,13 / −1,88. D segmenti SR 0,55, Z2 0,68 (hüküm dışı teşhis). Ayrıntı `hukum/BANKA_RAPORU.md` (13 bölüm).

## Okuma

Strateji bankada pozitif ama küçük ve istatistiksel olarak sıfırdan ayırt edilemeyen bir getiri üretti; son dilimde
belirgin kayıp var. Çoklu deneme düzeltmesi (DSR) ve rejim-null karşılaştırması (B7) açık farkla geçilemedi: bu getiri,
rastgele rejim yeniden düzenlemesinin ürettiği dağılımdan ayırt edilemiyor. Karar #26 gereği v8 bu haliyle
ilerletilmez; bulgular temizlenip açık yayımlanır.

## Teknik notlar (hükmü değiştirmez)

- **ACILIS biçimi:** iş listesi ACILIS'in kanonik sha256'sını (`5940011b…`) bağlar; `banka_hukum.py` ise dosyanın ham
  bayt sha256'sını hesaplıyordu. Değerlendiricinin ACILIS dosyası kanonik biçimde yazılmadığı için ilk çağrı
  "acilis_sha256" ile durdu (hüküm yazılmadı). Kod dondurulduğu için değiştirilmedi; aynı içerik kanonik biçimde
  `ACILIS_kanonik.json` olarak yazıldı (sha256 = bağlı kimlik 5940011b…) ve hüküm onunla açıldı. İçerik ve kimlik aynı.
- **Gizli anahtar:** kullanıcı bir denemede gizli anahtarı sohbete yapıştırdı; anahtar ifşa olmuş sayılır ve yalnız bu
  bankanın (yayımlanacak) sonuçlarını açar; başka yerde kullanılmaz.
- Kör denetim listesi `DENETIM_LISTESI.md` (T1–T5 yok); değerlendirici kaydı 9aff120.
- Karar B: D doğrulama satırı deftere hüküm açıldıktan sonra eklendi (`V8-D-dogrulama`).
