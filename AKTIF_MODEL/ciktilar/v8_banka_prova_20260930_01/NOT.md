# Tam motorlu sentetik prova (6.12) — notlar

- A: 539 birim (529 + 10 B10), 885 sn / 12 işçi; B: 540 birim (530 + 10 B10), 1.226 sn / 12 işçi. İkisinde de koşucu →
  SONUC_DAMGA → çözme (T1) → hüküm → rapor satırları → 13 bölümlü rapor hatasız. Karar değerleri anlamsızdır (sentetik).
- B7 satırında null q95 birincil SR'a eşit görünür: sentetik birincil pencere 28 gün, dilimler ~7 gün; rejim-null
  eşleşmesi kimlik permütasyonuna düşer (R17 ortak pay = 1,000). Null yolları gerçek yolla aynıdır; fark yalnız yeniden
  bazlamanın kayan nokta gürültüsüdür (A'da ">" geçti, B'de kaldı). Kod hatası değildir; R17 tanısı bunu doğru gösterir.
  Gerçek bankada pencere yıllardır.
- kosu_A/, kosu_B/ git dışıdır (şifreli sonuçlar tek kullanımlık anahtarla; anahtar bellekteydi).
