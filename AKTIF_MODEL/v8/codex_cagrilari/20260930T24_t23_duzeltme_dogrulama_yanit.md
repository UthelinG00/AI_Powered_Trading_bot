## kapanis

1 KISMEN — Hazırlık/yükleme sınırı eklenmiş ve `_muhurle` kendi hatalarını bastırıyor; mevcut `AcilisHatasi` mesajlarında banka adı sızıntısı saptamadım, ancak denetim raporu yazımı sınır dışında (`v8/veri_denetim.py:106`, `v8/banka_kos/kosucu.py:87`).

2 KAPANDI — Filtre raporu yeniden karşılaştırılıyor; dönem, filtre tablosu, HAR ve anonim anahtar kimlikleri her işçide doğrulanıyor (`v8/banka_kos.py:48`, `v8/banka_kos/acilis.py:246`).

3 KAPANDI — Önek ilk karar kaydında kesilerek uzlaşmayı içeriyor ve test uzlaşmalı kararları zorunlu seçiyor (`v8/banka_kos/parite.py:38`, `v8/testler/test_v8_banka_acilis.py:313`).

4 KAPANDI — T2 dahil rapor yeniden hesaplanıp bayt düzeyinde karşılaştırılıyor; sabit girdiler/ortam altında sıralı JSON, tamsayı yükleyici sayaçları ve sabit bölmeler nedeniyle sözlük sırası veya kayan nokta kaynaklı bir deterministiklik kusuru saptamadım (`v8/banka_kos.py:47`, `v8/banka_kos/veri_denetim.py:30`, `v8/banka_kos/veri_denetim.py:132`).

5 KISMEN — Banka manifestindeki kayıp dosyalar yakalanıyor, fakat birleşimde kullanılan D paketinin TAMAM dosyaları aynı varlık kontrolünden geçmiyor (`v8/banka_kos/veri.py:186`, `v8/banka_kos/veri.py:195`).

6 KAPANDI — T5 artık ayrı durum ve çıkış kodu 7 üretiyor (`v8/banka_kos.py:86`, `v8/banka_kos.py:103`).

7 KAPANDI — Kuru koşuda eski anonim anahtar/tohum açıkça verilebiliyor ve karşılaştırma yalnız birim adı/düz hash üzerinden yapılıyor (`v8/banka_kos/acilis.py:290`, `v8/banka_kos/acilis.py:314`).

8 KISMEN — Şema netleştirilmiş ve 80/120 denetleniyor; aday evreninin K∪D dışında ek coin taşımaması hâlâ doğrulanmıyor (`v8/banka_kos/acilis.py:139`).

9 KAPANDI — Eylül arşivi/API birlikteliği reddediliyor; API alt sınırı ve ortak dönem üst sınırı uygulanıyor (`v8/banka_kos/veri.py:145`, `v8/banka_kos/veri.py:156`).

10 KISMEN — Ham bayt ve ortam tanımları netleştirilmiş, ancak 20(k)’daki genel yol sıralaması birleşik betik kimliğinde uygulanmıyor (`v8/banka_kos/acilis.py:105`, `v8/kalibrasyon/birim.py:33`).

## yeni_bulgular

[CIDDI] İlk motor kimliği doğrulanmadan tohum seçilebiliyor — `v8/banka_kos/acilis.py:120` — `ilk_motor_sha256` ilk dondurma kaydına bağlanmıyor; bu alanla uyumlu herhangi bir tohum T1’i geçiyor ve mevcut test bunu kabul ediyor (`v8/testler/test_v8_banka_acilis.py:125`); güncel motor hash kontrolü korunuyor fakat tohumun kökeni doğrulanmıyor — İlk dondurmanın bağımsız sabitlenmiş hash’ini doğrulayın ve eski motor/tohumu o kayıttan alın.

[ORTA] Denetim raporu yazımı hata sınırının dışında — `v8/veri_denetim.py:107` — `mkdir` veya `VD.yaz` sırasında oluşan OSError genel sınırdan geçmeyerek ham traceback ve çıktı yolunu stderr’e çıkarır; argüman dönüşümleri de sınır dışındadır (`:103`) — Yazım/sonlandırmayı sınır içine taşıyın; argüman hatalarını sabit mesajlarla karşılayın ve başarısız yazım testini ekleyin.

[CIDDI] Eksik dosya kontrolü D paketini kapsamıyor — `v8/banka_kos/veri.py:195` — D yükleyicisi yalnız diskte bulunan zip’leri dolaştığından manifestte TAMAM olan kayıp D ayı/funding dosyası ilk denetimde sessizce atlanabilir (`v8/adaptor/veri_yukleyici.py:139`) — Kullanılan D adayları için de manifest–disk tamlık kontrolünü yüklemeden önce uygulayın.

[ORTA] Aday evreni fazlalıkları kabul ediliyor — `v8/banka_kos/acilis.py:139` — Ayrık 80/120 kümeleri sağlanırken `adaylar` içine ek isimler konulabilir; bunlar yükleyiciye ve motor evrenine ulaşır — `adaylar = K∪D` eşitliğini ve BTC/ETH referanslarının tanımlı konumunu doğrulayın.

[ORTA] Kanonik kimlikte sıralama sözleşmesi hâlâ farklı — `v8/banka_kos/acilis.py:105` — Paket içleri sıralı olsa da birleştirilmiş liste genel olarak sıralı değil; `_birlesik_sha256` gelen sırayı kullanıyor ve 20(k)’yi uygulayan başka üretici farklı hash hesaplar — Mevcut kimliği koruyarak paket sırasını açıkça belgeleyin veya sürümlü bir kimlik geçişiyle ortak genel sıralamaya geçin.

## genel_hukum

Banka betiği Adım 7 dondurmasına henüz hazır değil; özellikle tohum kökeni ve D paketi tamlık kontrolü kapatılmalı. İnceleme yalnız statiktir; kod/test çalıştırmadım, dosya yazmadım ve yasaklı kaynaklara erişmedim.