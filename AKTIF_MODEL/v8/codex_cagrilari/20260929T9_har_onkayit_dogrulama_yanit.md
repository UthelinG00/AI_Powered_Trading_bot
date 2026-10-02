## dogrulama

- KAPANDI — CIDDI: Madde 12, ŝ²’yi PIT yürüyen artıklara döndürüyor; kod örneklem içi varyansı artık dondurmuyor; MIMARI §1b çelişkisi giderilmiş.
- KAPANDI — ORTA: Boş bootstrap çekişinin NaN değeri, kantil ve karar hesaplanmadan `TeknikHata` üretiyor; madde 9 ve 11 uyumlu.
- KAPANDI — DUSUK: Stres haftası sayısı `len(stres)`; hedef sayı ayrı kaydediliyor, boş kümenin ortalaması `null`.
- KAPANDI — DUSUK: `dondurulan` kaydı koşulsuz oluşturuluyor; yetersiz eğitimde `beta=null` ve eğitim sayısı korunuyor.

## yeni_bulgular

- **DUSUK — `har_secimi.py:243–245`:** `d_sonu_yuruyen_s2_bilgi`, D sonundaki varyansı değil, en geç 2026-06-22’deki mevcut değeri alıyor; 2026-06-29’da olgunlaşan son haftanın artıklarını kapsamıyor. Bilgi alanı doğru tarihle adlandırılmalı veya D sonunda hesaplanmalı; seçim kararını etkilemiyor.

## genel_hukum

Yalnız bu dört düzeltme ve değişikliklerin statik incelemesi kapsamında bağlayıcı koşuya hazır; yeni düşük bulgu bilgi alanıyla sınırlı, kod çalıştırılmadı.