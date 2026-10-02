## kapanis

- **ORTA — KISMEN:** T32 karşı örneği giderilmiş ve teste eklenmiş; ancak yedek yöntem yaprakta yine ham `lexsort` kullandığından geçerli eşleşmeleri kaçırabilir (`AKTIF_MODEL/v8/banka/rejim_null.py:175`).
- **DÜŞÜK — KAPANDI:** Test artık bir ek/bir commit ile yalnız N’yi bozuyor ve `"defter N"` hatasını arıyor (`AKTIF_MODEL/v8/testler/test_v8_banka_hukum_dondur.py:309`).

## yanlis_kabul

Sonlu, dört sütunlu girdilerde **hayır**: gruplar satır indekslerini ayrık böler, her grupta iki tarafın sayısı eşitlenir ve yaprakta bütün dörtlüler `rtol=0, atol=tol` ile birebir karşılaştırılır; başarılı yaprak eşleşmelerinin birleşimi geçerli bir birebir eşleşmedir (`AKTIF_MODEL/v8/banka/rejim_null.py:170–184`). Zincirleme kümelenme toleransı genişletmez; kalan risk yanlış rettir.

## yeni_bulgular

Yeni bağımsız sorun yok; mevcut ORTA bulgunun kalan kısmı kod açıklamasında da kabul ediliyor (`AKTIF_MODEL/v8/banka/rejim_null.py:169`).

## genel_hukum

**Evet:** tam takım geçse bile genel yanlış-ret açığı kapanmadan KILIT_TEKNIK_1 ek kaydına inceleme onayı vermiyorum; değerlendirme statiktir, kod/test çalıştırılmadı ve dosya yazılmadı.