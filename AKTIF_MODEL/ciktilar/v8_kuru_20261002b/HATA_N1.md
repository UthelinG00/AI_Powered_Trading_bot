# Kuru koşu teknik hatası: N1 null değişmezi yanlış alarm (2 Ekim 2026)

**Olay.** 6.15 kuru koşu (sunucu, kod 66ea9ea, `banka_kos.py kuru ../ciktilar/v8_kuru_20261002b A --isci 12`) 05:30:22
UTC'de başladı, 05:35:16 UTC'de çıkış 6 ile durdu. 29 birim bitti; `null_A_p001`–`p005` "birim hatasi" verdi (iz tek
kullanımlık alıcıya şifreli, açılamaz). Performans hiçbir aşamada açılmadı.

**Teşhis** (geçici kopya klasörde, yalnız istisna sınıfı/satır ve ihlal kodları basıldı; performans yok):
1. İstisna `banka_kos/yurutucu.py:185`: null değişmez ihlali (T4-f).
2. İhlallerin hepsi N1 (`banka/rejim_null.py:172-175`): yol 1'de 426 ihlal, 117/122 coin, dört dilim; sıralı fark
   0,001–0,26. N2–N5 ve funding temiz. 115 ihlalli coinde yaşam içi boşluk yok (boşluk hipotezi yanlış).
3. ρ dörtlüsünün her bileşeni tek başına gerçek ile sentetikte çoklu küme olarak aynı (sıralı fark ≤ 2,2e-16).
4. Gerçek D'de ρ_0 = 0 olan 1.068.731 saat var (açılış = önceki kapanış); sentetikte aynı sayı. N1, satırları ham
   kayan noktalı değerlerle `lexsort` ediyor; bağlı anahtarların arkasındaki 1e-16 düzeyindeki exp/log yuvarlaması
   sırayı değiştiriyor ve karşılaştırma farklı satırları eşliyor.
5. Aynı karşılaştırma sıralama anahtarı 1e-9 ızgarasına yuvarlanarak (`np.round(x, 9)` ile lexsort; karşılaştırma ham
   değerlerle, atol 1e-9 aynı): 122 coin × 4 dilimde ihlal 0, en büyük fark 2,2e-16.

**Sonuç.** Null üreteci doğru; N1 denetimi bağlı değerlerde yanlış alarm veriyor. Sentetik fikstürde açılış önceki
kapanışa hiç tam eşit olmadığı için görülmedi. `banka/rejim_null.py` kilitli kalibrasyon kod kimliğindedir: düzeltme
yalnız 21 g teknik ek zinciriyle (`banka_oncesi`, en fazla 1) yapılabilir. Hata testi D'den bağımsız sentetik fikstürle
(ρ_0 = 0 bağları + yuvarlama gürültüsü) gösterilmeli; parametre, eşik ve davranış değişmez; defter +1 satır (§3.3
muhafazakâr istisna), yeni V1, Codex okuması; kuru koşu baştan. Kullanıcı kararı bekleniyor.

**Düzeltme (kullanıcı onayı, 2 Ekim).** 21 g `banka_oncesi` teknik eki: kod 1b4e6e6 → ba8e7b2 (T32) → e316faa (T33) →
31aada7 (T34); defter satırı `V8-teknik-banka-oncesi` (1aa551b; N_defter 330, N_dondurma 331); V1
test_20261002T144855Z 59/59; ek kaydı `ciktilar/v8_kilit_20261001/KILIT_TEKNIK_1.json`, commit
4666db25cce22e1545639442fdbf33166cb936a1. Zincir dizüstünde ve sunucuda git ile doğrulandı. Sunucuda düzeltilmiş
denetimle D null yolları 1–5 ihlal 0. Kuru koşu yeni klasörde (`v8_kuru_20261002c`) 14:50 UTC'de yeniden başladı.
Bankadan önce başka teknik ek hakkı kalmadı (21 g: tür başına en fazla 1).
