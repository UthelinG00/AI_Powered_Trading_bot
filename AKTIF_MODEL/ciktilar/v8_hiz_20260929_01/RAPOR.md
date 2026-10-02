# v8 motor hız ölçümü ve iyileştirmesi — rapor (2026-09-29)

Bütün ölçümler **sentetik** 122 coinli veriyle yapıldı (`hiz_profil.veri_uret`; D verisi kullanılmadı). Yalnız süre
ve günlüğün son hash'i raporlanır. Betikler: `hiz_profil.py` (cProfile), `gun_suresi.py` (gün başına süre).

## Sıcak noktalar ve iyileştirme
- Profil: süre `bar_indeksi` tek saatlik aramalarında (8,6 milyon çağrı) ve bunları çağıran hijyen ölçütleri (b),
  (c), (d) ile borsa çapı boşluk taramasında toplanıyordu (ilk karardaki geçmiş taraması dahil).
- İyileştirme (`motor/gorunum.py` `saat_indeksleri`, `bosluk_taramasi`; `motor/hijyen.py` `_olcut_b/_c/_d`): saat
  dizisi için tek vektör araması; boşluk taramasında adaylar × saatler varlık matrisi. Mantık birebir aynı.
- Doğrulama: aynı koşuların günlük son hash'leri iyileştirme öncesi ve sonrası aynı
  (`1f82d9f5…`, `dca802e0…`; 150 günlük A ve B koşuları da aynı); 15/15 test dosyası PASS. Önceki kod
  `_arsiv/V8_VERI_HIZ_20260929_01/motor/`.

| Koşu (sentetik) | Önce | Sonra |
|---|---|---|
| A, 6 gün, geçmiş 92 gün | 6,3 s | 3,3 s |
| A, 6 gün, geçmiş 700 gün (ilk karar bütün geçmişi tarar) | 58,6 s | 26,9 s |
| İlk gün (A / B) | 1,7 / 2,0 s | 0,63 / 0,63 s |

## Gün başına süre (T0 = 92. gün, sonrası)

| Koşu | Gün başına ortalama |
|---|---|
| A, 150 gün | 0,17–0,18 s (sabit) |
| B, 150 gün | 0,45–0,49 s |
| B, 1.004 gün (tam D uzunluğu) | gün 1–100: 0,48; 100–300: 0,51; 300–600: 0,59; 600–900: 0,65; 900–1004: 0,56 s |

Tam D uzunluğunda B koşusu **580 s (~10 dk)**; bu ölçüm eşzamanlı başka işlerle yapıldı, yalın koşu biraz daha
kısa olur. A koşusu ~3–4 dk. Ayrıştırma B'ye yaklaşık 0,4 s/gün ekler (~7 dk). Veri yüklemesi (hash doğrulama +
zip okuma) koşu başına bir kez ~100 s.

## Sonuç
Hız, kilit sırasındaki koşular (carry kapısı: k ∈ {1, 2, 3}, NAV ızgarası, delist senaryoları; banka kuru koşusu)
için engel değil. Ek iyileştirme şimdilik gerekmiyor.
