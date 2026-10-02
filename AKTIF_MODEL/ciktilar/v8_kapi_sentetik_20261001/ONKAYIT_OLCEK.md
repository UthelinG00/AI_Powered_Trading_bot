# Kapı sentetik doğrulaması — gerçekçi faktör ölçeği ek duyarlılığı (koşudan önce; 1 Ekim 2026)

**Amaç.** CARRY §8.5'in dondurulmuş üreteci fiyat faktörlerine (x_B, x_A, x_R, x_S) yıllık %15 vol verir. K9 ham beta
eşdeğerliğidir (±0,15) ve betanın standart hatası sd(r^N)/sd(x) ile ölçeklenir; faktör vol'ü gerçekte (BTC ~%60) çok daha
büyük olduğundan dondurulmuş fikstür K9'u gerçekte olacağından katı ölçebilir. Bu ek koşu, kapı eşikleri hakkında
kullanıcı kararı (CARRY §8.5: "değişiklik ancak kullanıcı kararıyla ve D P&L'i görülmeden") için bilgi üretir.
**Dondurulmuş BX-08 sonucunun (`sonuc.json`) yerine geçmez; hiçbir eşiği kendiliğinden değiştirmez.** (Not, 1 Ekim:
kullanıcı kararı #27'nin girdisi olduğu için bu ön-kayıt ve sonucu sonradan arşivsel olarak kilit kapsamına alındı; ana
sonucu ikame etmez.)

**Tek fark (öteki her şey `kapi_sentetik.py` ve CARRY §15 madde 16 c ile aynı).** Faktör yıllık vol'leri: x_B %60,
x_A %80, x_R %40, x_S %40 (kripto için genel bilgi; D verisinden okunmadı); corr(x_B, x_A) = 0,8, öteki çiftler 0. Fiyat
bileşeni r^P = μ_P/52 + Σ b_k x_k + e, toplam yıllık vol %15 korunur: var(e) = (0,15²/52) − var(Σ b_k x_k). H0c-faktör'de
standart yükleme b̃_A = 0,40 → b_A = 0,40 · 0,15 / 0,80.

**Düzen.** 7 senaryo (aynı), senaryo başına 2.000 tekrar; üreteç `SeedSequence((20260929, 100 + senaryo_no, tekrar_no))`
(dondurulmuş akıştan ayrı). Çıktı `duyarlilik_olcek.json`: P(B) (V'siz), Wilson %95, ölçüt başına geçme oranı. Betik
`kapi_sentetik_olcek.py` (dondurulmuş betiği içe aktarır, yalnız üreteci değiştirir).
