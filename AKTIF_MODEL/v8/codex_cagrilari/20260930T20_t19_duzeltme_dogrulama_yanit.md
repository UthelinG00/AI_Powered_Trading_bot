## kapanis

HEAD `b908b74`; yalnız statik inceleme yapıldı, dosya yazılmadı ve kod/test çalıştırılmadı. Kısaltmalar: `KAL` = `AKTIF_MODEL/ciktilar/v8_kalibrasyon_20260929_01`, `B5` = `AKTIF_MODEL/ciktilar/v8_b5_a_esdegerlik_20260930_01`, `BANKA` = `AKTIF_MODEL/ciktilar/v8_asama4_20260927_01/BANKA_ONKAYIT_TASLAK.md`.

Düzey 1 bağı KAPANDI — Gerçek özet biçimiyle uyumlu dosya/hash/küme denetimi ve hesap sonrası tekrar kontrolü mevcut; kilidin birleşik hash tanımı `kanit.birlesik` ile aynı (`KAL/DUZEY1_OZET.json:9`, `KAL/topla.py:108`, `KAL/topla.py:154`, `AKTIF_MODEL/v8/kilit.py:83`, `KAL/kanit.py:32`).

B5 A eşdeğerliği KISMEN — 140 A birincil kapsamı, `son_hash` dışındaki gövde karşılaştırması, B birincil/B5 tüketmeyen yolların dışlanması ve rette tam yeniden koşu doğru; sonuç bekleniyor ve betiğin kabul/kanıt kontrolleri eksik (`B5/ONKAYIT.md:9`, `B5/ONKAYIT.md:22`, `B5/b5_a_esdegerlik.py:54`, `B5/b5_a_esdegerlik.py:90`).

R3 (b) KAPANDI — `a_t`, güncel evren üyeliğini ve maske/işlem dışılık koşullarını sağlıyor (`BANKA:839`, `AKTIF_MODEL/v8/motor/hedef.py:213`).

R3 (d) KISMEN — Çıkış hedefi, gerçekleşene kadar değerleme/funding ve devreden emir açıklanmış; sonraki aylık seçimde satılamayan pozisyonun bütçesi hâlâ belirsiz (`BANKA:842`, `BANKA:845`).

R3 (e) KAPANDI — Saatlik devreden dolum, katılım sınırı ve aynı maliyet/lot kuralları motorla uyumlu (`BANKA:850`, `AKTIF_MODEL/v8/motor/emir.py:69`).

## yeni_bulgular

[CIDDI] Yeniden başlatma eski girdiye bağlanmıyor — `B5/b5_a_esdegerlik.py:70` — Aynı güncel kimlik süzgeci doğru, fakat kayıtlı `girdi_sha256` tekrar okunup karşılaştırılmıyor; kaynak dosya değişse bile eski “aynı” satırı kullanılıyor, karşılaştırıcı betik değişikliği de güncel kimliğe dahil değil — Devam kayıtlarını güncel kimlik, betik hash’i, dondurma/iş listesi ve mevcut girdi hash’iyle eşleyin.

[CIDDI] Kabul koşulu ön-kayıttan zayıf — `B5/b5_a_esdegerlik.py:90` — `140/140` yerine herhangi bir pozitif listenin tamamı, örneğin `1/1`, geçebiliyor; eski kimliklerin tek olması denetleniyor fakat dondurmayla eşitliği denetlenmiyor — Beklenen 140 benzersiz birimin tam kümesini, zarf bütünlüğünü, dondurulmuş kimlikleri ve aynı ortam koşulunu zorunlu doğrulayın.

[CIDDI] B5 kanıtı kilidin dışında — `AKTIF_MODEL/v8/kilit.py:222` — Kilit yalnız dört duman birimli `esdegerlik_502e.json` kontrolünü tüketiyor; B5 sonucu eksik veya başarısız olsa da diğer koşullarla geçebilir — B5 raporunu zorunlu kilit belgesi/önkoşulu yapın; kapsamını, güncel kimliklerini ve girdilerini kilitlenen kalibrasyon kanıtına bağlayın.

[ORTA] R3 aylık bütçesinde satılamayan pozisyon — `BANKA:842` — NAV’ın %20’si işlem dışı pozisyonda kalırken `a_t` üyelerine NAV’ın %100’ünü dağıtmak toplam hedefi %120’ye çıkarır; “brüt 1” ile birlikte uygulanacak kural belirtilmemiş — Satılamayan pozisyon nominalini aylık tahsis bütçesinden düşme ve kalan çıkışlar gerçekleştiğinde bütçeyi kullanma kuralını sabitleyin.

## kararlar

U-59-ek-5 KABUL — Mevcut özet korunuyor; tüketilen dosyalar toplama öncesi/sonrası ve kilitte aynı kanıta bağlanıyor.

U-66-ek KABUL — Ön-kayıttaki kapsam ve tam yeniden koşu kararı uygun; uygulamadaki kanıt açıkları kapanmadan eşdeğerlik kabulü verilemez.

R3 ITIRAZ — Evren ve icra düzeltmeleri uygun; aylık seçimde satılamayan pozisyonun brüt bütçeye etkisi açık kalıyor.

## genel_hukum

Mevcut betikten yalnız “140/140” çıkması yetmez; yukarıdaki B5 kontrolleri ve kilit bağı tamamlandıktan sonra belirtilen 3.09, toplama, birleştirme, tam takım ve V1 adımlarıyla kapı kilidine ilerlenebilir. R3, aylık bütçe kuralı netleşmeden bütünüyle kodlanmaya hazır değil.