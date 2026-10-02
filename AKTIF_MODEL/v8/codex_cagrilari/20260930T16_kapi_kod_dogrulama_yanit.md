## t15_kapanis

İncelenen HEAD: `e0403c1`, dal: `claude/v8-kapi-motor-502e`. İnceleme statiktir; kod/test çalıştırılmadı, dosya yazılmadı, web ve yasaklı içeriklere erişilmedi. Kısa yollar `AKTIF_MODEL/v8/` altındadır.

T15-1 KISMEN — U-41–U-55 ve §15.11 eklenmiş, ancak bu kopyada §15.12 ve Grup 4/U-56–U-61 hâlâ yok (`AKTIF_MODEL/ciktilar/v8_asama4_20260927_01/CARRY_KAPISI_ONKAYIT_TASLAK.md:977`; `AKTIF_MODEL/ciktilar/v8_kapi_20260929_01/BELIRSIZLIK_COZUMLERI.md:85`).

T15-2 KISMEN — Normal istisna mühürlenip zinciri bastırılıyor, fakat hata dosyasını yazma veya hata mesajını basma başarısızlığında özgün istisna yeniden dışarı sızabilir (`kapi/kosu.py:141`).

T15-3 KISMEN — Kabul bayrakları ve P&L öncesi V1 kapısı eklenmiş, ancak kalibrasyon/duman/eşdeğerlik kanıtlarının kaynak ve parametre kimlikleri doğrulanmıyor (`kilit.py:125`; `kapi/kosu.py:134`).

T15-4 KISMEN — Zorunlu belge kümesi karşılaştırılıyor, fakat Git denetimi önceden sabitlenmiş kilit kimliği yerine dosyanın en son commit’ini ve herhangi bir yerel uzak-dal referansını kabul ediyor (`kilit.py:212`; `kilit.py:228`).

T15-5 KISMEN — Rapor adı/hash’i ve test dosyası kapsamı bağlanmış, ancak raporda kapı/adaptör/test kaynak kimlikleri bulunmadığından aynı motorla eski PASS kullanılabilir (`kilit.py:111`; `v8_calistir.py:142`).

T15-6 KISMEN — Sanal trend pozisyonları, boş devreden kitap ve korunmuş NAV doğrudan carry maruziyetini temizliyor, fakat bu yeni referans tanımı mevcut bağlayıcı U-51 metnine işlenmemiş (`kapi/denetim.py:106`; `AKTIF_MODEL/ciktilar/v8_kapi_20260929_01/BELIRSIZLIK_COZUMLERI.md:81`).

T15-7 KAPANDI — İki seriye merkezlemeden önce kesin sabitlik kontrolü uygulanıyor ve tanımsız korelasyon muhafazakâr sonuç veriyor (`kapi/istatistik.py:161`).

T15-8 KAPANDI — En kötü üçlü, en iyi üçlü çıkarıldıktan sonra seçilerek eşit katkılarda da altı farklı isim sağlanıyor (`kapi/isim.py:46`).

T15-9 KISMEN — Mevcut saat dizisindeki tamamen NaN gün reddediliyor, ancak beklenen tam gün kümesi doğrulanmadığından yeniden koşularda son NAV kaydıyla birlikte kaybolan son günler kapsam dışında kalabilir (`kapi/seriler.py:149`; `motor/ayristirma.py:118`; `kapi/kosu.py:119`).

T15-10 KISMEN — Kayıt sayısı ve terminal hash kesilmeyi yakalıyor, fakat V5 hâlâ ayrıştırmanın fiilen tükettiği saatlik miktarları değil karar kayıtlarını karşılaştırıyor (`kapi/denetim.py:84`).

T15-11 KAPANDI — Ağırlık dizisi `min(ℓ,n−1)` ile sınırlanırken özgün `ℓ+1` paydası korunuyor (`kapi/istatistik.py:74`).

T15-12 KAPANDI — Coin dizileri yalnız ilk erişimde ayrılıyor ve günlük serileştirme/okuma satır bazında yapılıyor (`motor/ayristirma.py:158`; `kapi/denetim.py:33`; `kapi/denetim.py:47`).

T15-13 KISMEN — Olağan fiyat, maliyet ve funding geçişleri eski/yeni miktarla ayrılıyor, fakat kapanıştan sonra tahakkuk eden geçmiş funding tutarları bacak toplamından düşebiliyor (`motor/ayristirma.py:339`; `kapi/isim.py:73`).

T15-14 KAPANDI — S4 temas/aşım ayrılmış ve karar öncesi gerçekleşen pozisyonlara devreden emir kalanları eklenerek ikinci kitap raporlanıyor (`kapi/betimsel_kayit.py:89`; `kapi/betimsel_kayit.py:130`).

T15-15 KAPANDI — Python/NumPy yanında pandas ve cryptography sürümleri de kilit içeriğine girip doğrulamada karşılaştırılıyor (`kilit.py:97`; `kilit.py:234`).

## yeni_bulgular

- [CIDDI] Mühürleme hatası özgün istisnayı açıyor — `kapi/kosu.py:143` — `HATA.txt` yazımı disk/izin hatasıyla veya `print` kapalı çıktı kanalıyla başarısız olursa `raise … from None` satırına ulaşılamıyor; Python özgün NAV istisnasını bağlam zincirinde gösterebilir — Mühürleme ve bildirim hatalarını da yakalayıp her çıkışta sabit, bağlamı bastırılmış hata üretin.

- [ORTA] Geçmiş funding katkısı long/short dökümünden kayboluyor — `motor/ayristirma.py:341`, `kapi/isim.py:73` — Örneğin 01:00’de kapanan pozisyonun geçmiş saatlerine ait dolgu 12:00’de yazıldığında katkı `carry_eski`ye giriyor, fakat 12:00 miktarı sıfır olduğundan iki bacaktan da dışlanıyor; ters kayıtlar da yanlış yöne atanabilir — Funding katkısını kapsadığı özgün saatlerin miktar işaretleriyle sınıflandırın, ters kayıtta özgün sınıflandırmayı koruyun ve bu durumlarda toplam özdeşliğini sınayın.

- [ORTA] Age çözücüsü biçim dışı dosyaları kabul ediyor — `banka_kos/age.py:142`, `banka_kos/age.py:209`, `banka_kos/age.py:219` — Kanonik Base64, stanza satırının azami 64 karakteri ve açılan dosya anahtarının tam 16 bayt olması zorunlu tutulmuyor — Katı kodlama/uzunluk kontrolleri ekleyin ve geçersiz biçim vektörlerini reddedin.

**P&L statik doğrulaması:** `c0c7cc6` karşılaştırmasında `motor/ayristirma.py` mevcut fiyat, funding, maliyet, netleme, artık ve `dnav` hesaplarını değiştirmiyor; `SATIRLAR`, toplama sırası ve özdeşlik formülü korunmuş (`motor/ayristirma.py:292`, `:332`, `:348`, `:361`). Yeni diziler ek çıktı niteliğinde; yukarıdaki funding bulgusu toplam motor P&L’ini değil bacak sınıflandırmasını etkiliyor. Çalıştırılmış eşdeğerlik iddiası vermiyorum.

## kararlar

U-44 KABUL — S4 sınıra temas ve sınır aşımı artık ayrı ölçülüyor.

U-45 KABUL — Gerçekleşen ve devreden kitap tavanları ayrı hesaplanıyor; yeni tanım bağlayıcı belgeye de işlenmeli.

U-49 ITIRAZ — Geçmiş funding dolgusu ve ters kayıtlar, kayıt anındaki miktarın işaretiyle güvenilir biçimde sınıflandırılamıyor.

U-51 ITIRAZ — Kodun sanal trend referansı doğrudan carry etkisini temizliyor; mevcut bağlayıcı metin hâlâ eski B durumunu tarif ediyor.

U-54 KABUL — Kod belirtilen adım ve minNotional kuralını uyguluyor; yasaklanan ham anlık görüntü doğrulanmadı.

U-55 ITIRAZ — Kapsam genişlemiş olsa da V1 test kaynakları ve kalibrasyondan güncel motora eşdeğerlik kimlik zinciri eksik.

U-56 ITIRAZ — Bağlayıcı karar metni yok; kod yorumundaki altı ayrık isim kuralı tek başına belge kabulü sağlamaz.

U-57 ITIRAZ — Bağlayıcı karar metni yok; kod düzeltmesi beklenen tam gün kapsamını da doğrulamıyor.

U-58 ITIRAZ — Grup 4 ve karar metni bu çalışma kopyasında bulunmuyor.

U-59 ITIRAZ — Grup 4 ve karar metni bu çalışma kopyasında bulunmuyor.

U-60 ITIRAZ — Grup 4 ve karar metni bu çalışma kopyasında bulunmuyor.

U-61 ITIRAZ — Grup 4 ve karar metni bu çalışma kopyasında bulunmuyor.

## age

**UYUMSUZ — şifreleme çekirdeği uyumlu görünüyor; çözücü katı biçim doğrulamasını tamamlamıyor.**

- **Başlık ve sarma:** Üretici sürüm satırını, X25519 stanza’sını ve 64 sütun/son kısa satır kuralını doğru kuruyor (`banka_kos/age.py:152`, `:173`); çözücü 64 karakterden uzun gövde satırlarını reddetmeli (`:209`).
- **HKDF:** X25519 için `E || alıcı` tuzu ve `age-encryption.org/v1/X25519` bilgisi; başlık için boş tuz/`header`; yük için 16 bayt nonce/`payload` doğru (`:149`, `:171`, `:174`, `:176`).
- **Header MAC:** Kapsam `---` dahil, ardından gelen boşluk/MAC/satır sonu hariç; karşılaştırma `compare_digest` ile yapılıyor (`:173`, `:228`).
- **STREAM:** 11 bayt büyük uçlu sayaç ve son bayrağı, 64 KiB parçalar, boş dosyanın tek boş son parçası ve sonraki boş son parçanın reddi doğru (`:177`, `:180`, `:236`, `:244`).
- **X25519 uzunlukları:** Açılan dosya anahtarı tam 16 bayt olmalı; karşılık gelen stanza gövdesi 32 bayt olmalı, mevcut çözücü bunu zorunlu tutmuyor (`:219`).
- **Base64:** `validate=True`, kullanılmayan son bitlerin sıfır olduğunu doğrulamaz; çözümden sonra yeniden kodlayıp özgün metinle birebir karşılaştırın (`:142`).
- **Bech32 anahtarları:** HRP, sağlama toplamı, bit dönüşümü, karma harf reddi ve 32 bayt anahtar kontrolleri anahtar yollarında uygun (`:78`, `:85`, `:119`, `:126`).
- Mevcut testler aynı uygulamayla gidiş-dönüşü sınar; bağımsız resmî age dosyalarıyla birlikte çalışabilirlik kanıtı sağlamaz (`testler/test_v8_banka_age.py:56`). Bu turda test çalıştırılmadı.

## genel_hukum

Kapı kodu henüz kilide hazır değil; kalibrasyon sonrası son testler tek başına eksik bağlayıcı kararları, kanıt kimliği bağlarını ve kalan mühür/V2/V5 açıklarını kapatmaz. Bunlar ve funding bacak sınıflandırması düzeltilip hedefli sentetik doğrulamalar tamamlanınca yeniden değerlendirilmeli.