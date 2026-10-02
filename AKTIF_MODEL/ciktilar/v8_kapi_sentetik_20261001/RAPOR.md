# Carry kapısı sentetik doğrulaması (BX-08; CARRY §8.5, §15 madde 16 c) — rapor

Tarih: 1 Ekim 2026. D ve banka verisi kullanılmadı. Ölçütler kapının dondurulmuş kodu (`v8/kapi/olcutler.py`) ile
hesaplandı. V1–V6 fikstürde yok; P(B) = bağlayıcı K1, K2, K5–K11'in hepsini geçme oranı ("V'siz kapı geçiş oranı").

## 1. Dondurulmuş üreteç (kilit belgesi: `sonuc.json`, 7 senaryo × 10.000 tekrar, tohum 20260929)

| Senaryo | P(B) | Wilson %95 | K1 | K2 | K5 | K9 | K11 |
|---|---|---|---|---|---|---|---|
| H1 s=0,30 ρ=0 | 0,0011 | [0,0006; 0,0020] | 0,40 | 0,13 | 0,09 | 0,03 | 0,78 |
| H1 s=0,30 ρ=0,3 | 0,0006 | [0,0003; 0,0013] | 0,22 | 0,13 | 0,09 | 0,02 | 0,79 |
| H1 s=0,45 ρ=0 | 0,0037 | [0,0027; 0,0051] | 0,58 | 0,32 | 0,23 | 0,03 | 0,78 |
| H1 s=0,45 ρ=0,3 | 0,0017 | [0,0011; 0,0027] | 0,41 | 0,33 | 0,24 | 0,02 | 0,79 |
| H0b | 0,0007 | [0,0003; 0,0014] | 0,23 | 0,25 | 0,18 | 0,02 | 0,79 |
| H0c-ortalama | 0,0001 | [0,0000; 0,0006] | 0,16 | 0,02 | 0,01 | 0,02 | 0,78 |
| H0c-faktör | 0,0000 | [0,0000; 0,0004] | 0,58 | 0,33 | 0,24 | 0,00 | 0,00 |

K6, K7, K8, K10 bağlayıcı ama tıkayıcı değildir (geçme oranları `sonuc.json`'da).

## 2. Gerçekçi faktör ölçeği duyarlılığı (kilit kararı için bilgi; `duyarlilik_olcek.json`, 7 × 2.000; ONKAYIT_OLCEK.md)

Faktör vol'leri BTC %60, alt %80, x_R ve x_S %40; corr(x_B, x_A) = 0,8. Öteki her şey aynı.

| Senaryo | P(B) | Wilson %95 | K9 | K11 |
|---|---|---|---|---|
| H1 s=0,30 ρ=0 | 0,0085 | [0,0053; 0,0136] | 1,00 | 0,20 |
| H1 s=0,30 ρ=0,3 | 0,0065 | [0,0038; 0,0111] | 1,00 | 0,21 |
| H1 s=0,45 ρ=0 | 0,0280 | [0,0216; 0,0362] | 1,00 | 0,21 |
| H1 s=0,45 ρ=0,3 | 0,0140 | [0,0097; 0,0202] | 1,00 | 0,19 |
| H0b | 0,0130 | [0,0089; 0,0190] | 1,00 | 0,19 |
| H0c-ortalama | 0,0020 | [0,0008; 0,0051] | 1,00 | 0,22 |
| H0c-faktör | 0,0000 | [0,0000; 0,0019] | 0,96 | 0,00 |

## 3. Yorum

- Kapı her iki ölçekte de fiilen kapalıdır: iyi bir funding kenarında (H1, s = 0,45) bile B'yi seçme olasılığı ≤ %2,8.
- Dondurulmuş fikstürde asıl tıkayan K9'dur ve bu, faktörlere verilen %15 vol'den kaynaklanır (gerçekçi ölçekte K9 ~%100
  geçer). Gerçekçi ölçekte bu kez K11 (BTC–alt korelasyonu yüklemeleri belirsizleştirir) ~%20'ye iner. K2 (NW t ≥ 3;
  AR(1) gürültü SE'yi büyütür) ve K5 (ayların %75'i pozitif) her iki ölçekte sıkıdır.
- Sahte B seçimi düşüktür (H0 senaryolarında ≤ %0,07 dondurulmuş, ≤ %1,3 gerçekçi ölçek); gizli fiyat bahsini (H0c-faktör)
  K11 her iki ölçekte yakalar.
- §8.2'deki kaba K1 hesapları K1'in tek başına geçişini doğru büyüklükte verir; bileşik kapı ise K1'den çok daha katıdır.

## 4. Kullanıcı kararı (1 Ekim 2026; kilitten ve kapı koşusundan önce, D P&L'i görülmeden)

**Seçenek 1: kapı eşikleri değiştirilmez.** Kapı tasarımı gereği "carry ancak çok güçlü kanıtla" eklenir; bu ölçümle kapının
büyük olasılıkla A seçeceği ve bankanın trend sistemini sınayacağı önceden bilinerek kabul edildi. Eşik gevşetmek yeni bir
tasarım (yeni seçim, yeni sentetik doğrulama, yeni inceleme) olurdu ve sahte B oranını artırırdı. Kayıt:
`ACIK_SORU_YANITLARI.md` #27.
