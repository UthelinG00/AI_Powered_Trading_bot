Görev (Türkçe çalış, Türkçe yaz): v8 kripto botunun "carry kapısı" ön-kaydındaki bütün ölçütleri, koda aktarılabilecek biçimde tek bir listeye çıkar. Bu mekanik bir çıkarım işi: yorum yapma, karar verme, belirsizliği çözme — belirsizliği işaretle.

Çalışma klasörü (git worktree): <depo>\.claude\worktrees\codex-kirmizi

Oku:
1. AKTIF_MODEL/ciktilar/v8_asama4_20260927_01/CARRY_KAPISI_ONKAYIT_TASLAK.md — özellikle §3.1–3.7, §4, §5 (P&L ayrıştırma formülleri), §6 (kapı ölçütleri: 6.1 geçerlilik, 6.2 istatistik tanımları, 6.3 karar ölçütleri, 6.6 betimsel raporlar), §7 (karar kuralı, kör hüküm, hata yönetimi), §8 yalnız eşik türetimi için gerekirse.
2. AKTIF_MODEL/v8/motor/ayristirma.py — yalnız dönen yapıyı anlamak için (SATIRLAR sabiti, AyristirmaSonucu alanları: satirlar, gunluk, trend_coin, trend_q, trend_eski, trend_yeni). Mevcut satır adlarını ölçüt girdilerine eşle.
3. Gerekirse AKTIF_MODEL/ciktilar/v8_asama4_20260927_01/MIMARI.md §4.7 (sanal bacaklar ve P&L satırları).

Yaz (tek çıktı dosyası): AKTIF_MODEL/ciktilar/v8_kapi_20260929_01/OLCUT_LISTESI.md
İçerik:
- Başlık + 3 satırlık özet (kaç geçerlilik koşulu, kaç karar ölçütü, kaç betimsel rapor).
- Tablo 1 "Geçerlilik koşulları" (§6.1): kimlik, ad, tam tanım/formül (belgedeki ifadeye sadık), girdi, eşik, sağlanmazsa sonuç, belge referansı (§).
- Tablo 2 "İstatistik tanımları" (§6.2): her tanım için formül, pencere/örneklem, parametreler (ör. Newey–West gecikmesi), belge referansı.
- Tablo 3 "Karar ölçütleri" (§6.3): kimlik (K1, K2, …), ad, formül, girdi serisi (ayristirma.py'deki hangi satır(lar) ya da başka hangi veri), örneklem/pencere/dilim, eşik (sayı ve yön: >, ≥ …), bağlayıcı mı (K3/K4 istisnası dahil nasıl), uç durumlar (NaN, boş dilim, sıfır varyans), belge referansı.
- Tablo 4 "Betimsel raporlar" (§6.6): ad, tanım, girdi.
- Bölüm "Karar kuralı ve kör hüküm" (§7.1–7.3): kapının A/B kararını nasıl verdiği; hangi çıktıların açık, hangilerinin mühürlü (yalnız hash) olduğu; hata/teknik geçersizlik dalları. Madde madde.
- Bölüm "Koda aktarım notları": (a) ayristirma.py'nin şu an verdiği satırlarla doğrudan hesaplanabilen ölçütler; (b) ek veri ya da ek hesap gerektirenler (ör. faktör serileri, BTC/alt getirileri, dilim sınırları) ve belgede bunların nereden geldiği; (c) belgede tanımlı olup ayristirma.py satırlarında karşılığı bulunmayan kavramlar.
- Bölüm "Belirsizlikler": belgede açık bırakılmış ya da çelişkili görünen her nokta; her biri için belge referansı ve neden belirsiz olduğu (çözme, yalnız işaretle).

Kurallar (kesin):
- Yalnız yukarıdaki tek dosyayı oluştur. Başka hiçbir dosyayı değiştirme, silme ya da oluşturma. git commit/push yapma.
- Kod ya da test ÇALIŞTIRMA (python, pytest vb. yok). Yalnız dosya okuma.
- Şu dosyaları okuma, listeleme, dosya bilgisini sorgulama (stat/ls dahil): BANKA_MUHURLU.json, uygun_evren.json, SECIM.json, secim_cikti.json; AKTIF_MODEL/ciktilar/v8_banka_20260924_01 klasörünü listeleme. D verisini (AKTIF_MODEL/ciktilar/v8_veri_* ve .zip dosyaları) okuma. .env okuma. config.py import etme ya da okuma. AKTIF_MODEL/motor/ (REV1) klasörüne dokunma.
- Web kullanma. Alt ajan açma.
- Belgeden alıntı yaparken formülleri değiştirme; kısaltırsan anlamı koru ve § referansı ver.
- Dosyayı bir kerede yaz (gerekirse bölüm bölüm ekleyerek), gereksiz yeniden okuma yapma.

Bitince ana oturuma kısa bir yanıt ver: dosya yolu, tablo başına satır sayısı ve en önemli 3–5 belirsizlik (her biri bir satır).
