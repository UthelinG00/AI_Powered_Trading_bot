## bulgular

Salt okunur incelemede RET, ölçütler, kapı A ve teknik ek tarihleri tutarlı; kontrol edilen kilit, teknik ek, dondurma, sonuç, rapor ve seçim betiği hash’leri kayıtlarla eşleşiyor. Gerçek kimlik bilgisi, şifreli sonuç, ham piyasa verisi, `muhur/`, REV1/bot veya kapsam dışı ham tasarım taslağı saptamadım. Araştırma/sınır uyarıları mevcut; yatırım tavsiyesi olmadığı `LICENSE-DOCS.md:14` içinde belirtilmiş. Kod ve test çalıştırılmadı.

- **[ORTA] Temizleme betiğinde sunucu IP’leri kalmış** — `AKTIF_MODEL/ciktilar/v8_yayim_20261002/yayim_hazirla.py:49–50,58` — İki sunucu IP adresi regex içinde yayımlanıyor; kaçışlı yazım nedeniyle `tarama` bunları yakalamamış. Bilinen yerel yol istisnasından farklı bir kalıntı — Betiğin yayımlanan kopyasından adresleri kaldırın veya betiği kapsam dışına alın; yayım kaydını güncelleyin.

- **[ORTA] Banka veri manifesti eksik** — `DOGRULAMA.md:49–52`; `AKTIF_MODEL/ciktilar/v8_banka_acilis_20261002/INDIRME_OZETI.json:6–7` — Hash’leri verilen `liste.jsonl` ve `BANKA_MANIFEST.jsonl` depoda yok. Özet hash, dosya bazındaki özgün veri kimliklerini okuyucuya sağlamıyor; güncel arşivden yeniden liste üretmek aynı kaydı garanti etmez — Ham veriyi eklemeden özgün listeyi ve manifesti yayımlayın.

- **[ORTA] Zaman damgası kanıtı iddiası fazla güçlü** — `ZAMAN_CIZELGESI.md:3–5,9`; `README.md:3–5` — Özel depo commit hash’leri ve dosyalardaki tarihler, tek başına GitHub’a itilme zamanını veya kilidin sonuç görülmeden oluşturulduğunu dış okuyucuya kanıtlamaz — Dosya bütünlüğü ile tarihsel öncelik doğrulamasını ayırın; bağımsız zaman kanıtı ekleyin veya iddiayı doğrulanamayan çalışma kaydı olarak niteleyin.

- **[ORTA] Doğrulayıcı eksik girdiyi başarıyla geçiştirebilir** — `dogrula.py:115–118`; `DOGRULAMA.md:26–27` — ACILIS dosyası yoksa kontrol atlanıyor ve betik kalan kontrollerle başarılı çıkabiliyor; “hüküm türü” kontrolü ise koşulsuz `True`. Mevcut dosya bulunuyor, fakat doğrulayıcı bu eksilmeyi/tutarsızlığı güvenilir biçimde yakalamıyor — ACILIS’i zorunlu yapın; hüküm türünü sonuç içeriğiyle karşılaştırın.

- **[DUSUK] Komutların çalışma dizini ve yorumlayıcısı belirsiz** — `DOGRULAMA.md:9,15,23,49` — Test komutu okuyucuyu `AKTIF_MODEL/v8` içinde bırakıyor; sonraki `python dogrula.py` kökteki dosyayı bulamaz. Sanal ortam oluşturuluyor fakat sonraki `python` komutları onu kullanmıyor; `ciktilar/` yollarının tabanı da belirtilmemiş — Her blokta başlangıç dizinini ve sanal ortam yorumlayıcısını açıkça yazın.

## genel_hukum

Evet; sunucu IP kalıntıları temizlenmeden, eksik banka manifesti tamamlanmadan ve doğrulama iddiaları düzeltilmeden mevcut kopyanın yayımlanmasını önermiyorum.