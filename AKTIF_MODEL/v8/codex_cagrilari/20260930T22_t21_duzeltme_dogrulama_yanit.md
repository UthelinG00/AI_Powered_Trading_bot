## kapanis

Yollar `AKTIF_MODEL/v8/` altındadır. İnceleme statiktir; dosya yazılmadı, kod/test çalıştırılmadı.

1 KAPANDI — İlk bağlayıcı hash korunuyor; geçersiz TAMAM, kimlik değişimi ve indirme/yok durumları ayrılıyor (`banka_kos/veri_denetim.py:36`).

2 KAPANDI — Yetersiz gözlem, sonlu olmayan getiri ve sıfır volatilite regresyondan önce “tanımsız” döndürüyor (`banka_kos/long_beta.py:266`).

3 KAPANDI — Bütün kapanışlar gecikmeye katılıyor; sonraki karar anında açıklık, nihai kapanış türünden ayrı izleniyor (`banka_kos/tanilar.py:43`, `banka_kos/tanilar.py:150`).

4 KAPANDI — R2 ağırlıkları NAV kaydındaki pozisyondan, stres ağırlıkları sınırdan kesin önceki olaydan alınıyor (`banka_kos/tanilar.py:288`, `banka_kos/yurutucu.py:130`).

5 KAPANDI — R4 blokları D başlangıcına bağlı; ≥25 ortak gün koşulu ve ortaklıktan önce hesaplanan BTC eşiği uygulanıyor (`banka_kos/rapor.py:194`, `banka_kos/rapor.py:204`).

6 KAPANDI — Netleştirme 17(f) doğrultusunda eksik T4-a kaydı sıfır yerine `None` oluyor (`banka_kos/tanilar.py:93`, `banka_kos/tanilar.py:114`).

7 KISMEN — Veri taraması düzeldi; R17 bütün kararları topluyor fakat null koşusunda son günü taşıyacak sonraki karar bulunmuyor (`banka_kos/veri_denetim.py:89`, `banka_kos/tanilar.py:360`, `banka_kos/yurutucu.py:185`).

8 KISMEN — GA kapsamı genişletildi fakat R1’in birincil hücresi atlanıyor ve R9’un hesaplanan GA’sı Markdown’a taşınmıyor (`banka_kos/rapor.py:305`, `banka_kos/rapor_md.py:194`).

9 KAPANDI — B2 alanları, R7 tanıları, Kelly sütunları, carry epizot payı ve funding sayacı zincire bağlanmış (`banka_kos/hukum.py:106`, `banka_kos/rapor_md.py:136`, `banka_kos/rapor_md.py:177`, `banka_kos/tanilar.py:413`, `banka_kos/veri_denetim.py:139`).

10 KAPANDI — Netleştirme 17(i)’deki sembol deseni hem serbest alanlarda hem nihai metinde denetleniyor (`banka_kos/rapor_md.py:45`, `banka_kos/rapor_md.py:102`, `banka_kos/rapor_md.py:226`).

## b8

Düzeltme, kullanılan ardışık günlük takvim için doğru: son gün +24h ve sonrası dışlanıyor (`banka/pnl.py:201`). Düzey 2 **birincil A/B** aynı son-saat sınırında bittiğinden etkilenmez; **x2, x3, null ve çıkarma** da bu sınırı paylaşır, ayrıca yalnız `sadece_sharpe` çağırır (`kalibrasyon/yurutucu.py:138`, `kalibrasyon/yurutucu.py:143`). **Düzey 1** için sonuç aynı, gerekçe farklıdır: motor/funding yolu kullanılmaz (`kalibrasyon/yurutucu.py:91`). v8 üretim kodunda `gunluk_topla`nın tek tüketicisi B8 funding hesabıdır (`banka/degerlendirme.py:136`). B5 A/B epizotları, özgün funding atfı, katkılar ve paydalar pencereye süzülüyor; `sadece_sharpe` sınır NAV’larından hesaplanıyor, bu yollarda başka pencere dışı yığılma saptamadım (`banka/degerlendirme.py:104`, `banka/degerlendirme.py:141`, `banka/degerlendirme.py:161`, `banka/degerlendirme.py:85`). `side='left'` stres için de doğru: gece yarısı dolum yok, NAV önceki saatin sonunda kaydediliyor; değişiklik sınırdaki uzlaşmanın pozisyonu erken silmesini önlüyor (`motor/geri_test.py:161`, `motor/geri_test.py:170`, `banka_kos/yurutucu.py:217`).

## yeni_bulgular

- [ORTA] R17 null son günü hâlâ eksik — `banka_kos/yurutucu.py:185`, `banka_kos/tanilar.py:360` — Null pencere sonunda durduğu için son günün boşluklarını taşıyan sonraki karar oluşmuyor; gerçek/null karşılaştırması farklı kapsam kullanıyor — Motor koşusunu uzatmadan son günü aynı boşluk taramasıyla tamamla.

- [ORTA] GA’nın rapora aktarımı tamamlanmamış — `banka_kos/rapor.py:305`, `banka_kos/rapor_md.py:200`, `banka_kos/rapor_md.py:84`, `banka_kos/rapor_md.py:194` — R1 birincil hücresinin GA anahtarı yok; R9’un iç içe `ga` sözlüğü genel tablo üreticisince atılıyor — Birincil GA’yı R1’e bağla ve R9’a açık GA sütunu ekle.

- [DUSUK] Yeni R4 testi standart koşucuda çalışmıyor — `testler/test_v8_banka_rapor.py:58`, `testler/test_v8_banka_rapor.py:62`, `v8_calistir.py:78` — `unittest.main()` yeni sınıf tanımlanmadan çıkıyor; 55/55 dosya başarısı bu testi kapsamıyor — Ana çağrıyı dosyanın sonuna taşı.

## genel_hukum

6.01b ve 6.12 dışında da **henüz tam hazır değil**: R17 null kapsamı ve zorunlu GA aktarımı tamamlanmalı, R4 testi koşucuya gerçekten dahil edilmeli. B8 düzeltmesi ve stres ağırlıklarının sınır değişimi statik incelemede doğru görünüyor.