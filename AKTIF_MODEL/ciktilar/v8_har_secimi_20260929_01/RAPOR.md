# v8 kilit adım 2: HAR/EWMA risk tahmincisi seçimi — rapor

**Karar: HAR** (MIMARI §1b bağlayıcı kuralının iki koşulu da sağlandı). P&L'siz koşu: strateji koşulmadı, getiri ya da
performans ölçütü hesaplanmadı. Sonuç kilit adım 4'te (ön-kayıt kilidi) hash'lenecek.

- Ön-kayıt: `ONKAYIT.md` revizyon 3 (sha256 6a10d8f5…), koşudan önce commit ve push edildi (`31e9dea`). Codex üç
  turda inceledi (T7, T8, T9; `v8/codex_cagrilari/`). Önceki revizyonlar `_arsiv/V8_HAR_ONKAYIT_20260929_01/`.
- Koşu: tek kez, `har_secimi.py` (commit `kosu_commit.txt` = 31e9dea…), veri kimliği 5907a89b… (ön-kayıtla aynı).
  Çıktılar: `sonuc.json` (sha256 bu raporun altında), `kosu_cikti.txt`. Deneme defteri: `V8-HAR-secimi`, varyant 2.
- Sentetik tesisat denemesi: `sonuc_sentetik.json` (anlamsız sayılar; yalnız betiğin çalıştığını gösterir).

## Bağlayıcı sonuç

| | Değer | Eşik / koşul |
|---|---|---|
| Değerlendirme kümesi | 1.825 coin-hafta, 122 hafta (takvim 122) | ≥ 30 hafta |
| Havuzlu ortalama QLIKE | HAR 0,4506; EWMA 0,4862 | |
| (i) QLIKE_HAR / QLIKE_EWMA | **0,927** | ≤ 0,95 → sağlandı |
| (iv) ortalama fark (HAR − EWMA), bootstrap kantilleri 0,05 / 0,5 / 0,95 | −0,064 / −0,037 / **−0,008** | %95 üst sınır < 0 → sağlandı |

Dışarıda kalan coin-hafta: 120 (ilk 8 hafta; en az 8 artık haftası kuralı, ŝ² tanımsız), 1 (hedef tanımsız).
Aylık katsayı tahminlerinin hiçbiri tanımsız kalmadı (30 ay; ilk ay 195, son ay 2.080 eğitim gözlemi).
ŝ² yolu 0,58–1,00 aralığında.

## Betimsel (bağlayıcı değil; §1b.6)

| | HAR | EWMA |
|---|---|---|
| Stres haftaları (BTC hedef haftası getirisi en kötü 13 hafta): ortalama QLIKE farkı (HAR − EWMA) | **+0,085** | |
| Gerçekleşen / tahmin varyansı oranı Y/F, q95 | 2,72 | 2,75 |
| Y/F, q99 | **6,50** | 6,04 |

**Uyarı.** HAR ortalamada daha isabetli, ama sert düşüş haftalarında EWMA'dan kötü ve kuyrukta (q99) riski biraz daha
fazla küçümsüyor. n < 30 olduğu için bu bir kural değildir (ön-kayıt); banka ve demo izlemesinde (MIMARI §9, `ml`
tasarımının "HAR katsayılarının kayması" riski) takip edilmesi gereken bir zaaftır. Önceden görülmüş `ml` bulgusu
(%14 düşük QLIKE, farklı hedef ve EWMA tanımıyla) bu koşuda %7,3 çıktı.

## Katsayılar

- Yürüyen aylık katsayılar (c, b1, b7, b30): ilk ay (2024-01-01) 2,00 / 0,105 / 0,248 / 0,343; son ay (2026-06-01)
  1,87 / 0,230 / −0,045 / 0,454. Bütün yol `sonuc.json` → `katsayi_yolu`.
- Banka/canlı için dondurulan katsayı (D'nin tamamı, 2.140 gözlem): 1,872 / 0,223 / −0,051 / 0,442. ŝ² dondurulmaz
  (ön-kayıt madde 12: banka/canlıda yürüyen artıklardan). Son değerlendirme Pazartesisindeki (2026-06-22) yürüyen ŝ²
  0,880 (yalnız bilgi).
- Sabit terim c ≈ 1,9, özelliklerin saatlik RV (günlük birim) ile hedefin haftalık günlük-getiri toplamı arasındaki
  ölçek farkını taşır (ön-kayıt madde 3; Codex T7 kabulü).

## Ön-kayıt ifadesiyle uygulama arasındaki not
Ön-kayıt madde 6 Pazartesi t'de "t'den önceki son ay başı tahmini"nin kullanılacağını yazıyor. Betik (Codex T7–T9'un
incelediği ve koşudan önce commit edilen) ayın ilk günü Pazartesiye denk geldiğinde o günün 00:00 tahminini kullandı
(M ≤ t). Bu tahmin yalnız hedefi M'ye kadar tamamlanmış gözlemlerle yapıldığı için gelecek bilgisi içermez (PIT). Etkilenen
Pazartesiler: 2024-01-01, 2024-04-01, 2024-07-01, 2025-09-01, 2025-12-01, 2026-06-01. Koşu yeniden yapılmadı; kural motorda da
aynıdır (karar günü dahil, t'ye kadarki son ay başı).

## Sonraki adım (ön-kayıt madde 12)
Motor entegrasyonu: D içindeki bütün koşularda boyutlama σ̂_i = max(σ̂_HAR,i, %20); HAR tanımsızken σ̂_EWMA,i.
Katsayı: karar günü dahil t'ye kadarki son ay başı tahmini (`katsayi_yolu`); ŝ²: son Pazartesinin yürüyen değeri (`s2_yolu`;
t'ye kadar hedefi tamamlanmış son 52 hafta). Sinyal normalizasyonu, carry σ^C ve maliyet σ_d σ̂_EWMA'da kalır (§1b
"Kapsam", §4.2, §6.1).

sha256: sonuc.json c5602b2b3350fdb7e07a7105b58a4e08ef9c6b484e9effdf0307cb3a9b8d666a; kosu_cikti.txt bfae9629be0c500265af7f4d1be193d74597d707d539bbf1c43c7e9087f4830e.
