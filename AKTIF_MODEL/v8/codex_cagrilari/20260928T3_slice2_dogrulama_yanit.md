## dogrulama

K1: KAPANDI — 30 günlük pencerede ilk ve sıra dışı geciken kayıtlar işleniyor; kapanmış pozisyon ve günlükten yeniden kurulum doğrulandı.  
K2: KISMEN — Aralık sütunuyla düzeldi; sütunsuz 4h düzende tek eksik kayıt hâlâ 8h geçişi sanılarak dolgusu siliniyor.  
K8: KAPANDI — Yalnız tutarlılık açısından: docstring, isim tavanı ihlalinin diğer isimleri küçültmediğini artık kodla uyumlu açıklıyor.  
K10: KAPANDI — Funding maskesinin penceresiyle taşınan boşluk geçmişinin sınırı eşleşiyor; 120 saatlik kesinti örneği düzeldi.  
K11: KISMEN — 702 saatlik boşlukta 30 günlük tarama sınırı, son güne değen altı donmuş barı hâlâ kaçırıyor.  
Y1: KAPANDI — Boşluk geçmişinin budama sınırı tüketici pencereyle eşleşiyor; tam geçmiş ve günlük ilerleme önceki karşı örnekte aynı sonucu veriyor.  
Y2: KAPANDI — Eşit azaltmada yeni niyet seçiliyor; maske çıkışı niteliği ve güncel maliyet bağlamı korunuyor.

## yeni_bulgular

**[ORTA] durum.py:134 — Budama, geç kaydın kapsadığı dolguları erken kesinleştiriyor**

Dolgu saatleri 30 günlük sınırla budanırken, kabul edilen funding damgası bu sınırın öncesindeki saatleri kapsayabiliyor. Sentetik X long örneğinde 400 damgalı 8h kayıt 1119’da geldiğinde, sonraki saatlik uzlaşmalar 393–397 dolgularını budamıştı: gerekli 0,01000 yerine 0,00375 iade edildi; nakit 0,00625 eksik kaldı.

**[DUSUK] funding.py:132 — Sıfır tutarlı kayıtların atlanması budamayı durduruyor**

398. saatte kapanan sentetik X pozisyonunun 393–398 dolguları ve işlenmiş 392 damgası, 1160. saatte hâlâ durumda kalıyor. Budama yalnız `funding` olayında çalıştığından, atlanan sıfır tutarlı kayıtlar temizliği engelliyor; bekleyen dolgu anahtarı coini döngüde süresiz tutuyor.

## genel_hukum

Dosya yazmadan çalıştırılan 81 ilgili test geçti; bağımsız karşı örnekler K2/K11’in tam kapanmadığını ve iki yeni sorunu doğruladı. Bu turun düzeltmeleri henüz bütünüyle kabul edilebilir değil.