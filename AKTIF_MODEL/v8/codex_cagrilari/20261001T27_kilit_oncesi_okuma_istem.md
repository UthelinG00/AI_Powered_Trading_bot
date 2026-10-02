Sen v8 kripto projesinin bağımsız inceleyicisisin. Ön-kayıt KİLİDİNDEN (kilit adımı 4; `KILIT.json`) önceki son okuma
(T27; 4.04). Kilitten sonra hiçbir eşik, ölçüt, parametre ya da kural değişmez; ardından D'de ilk P&L (carry kapısı)
üretilir. Çalışma kökü bu git çalışma kopyasıdır. Hiçbir dosyaya yazma; yalnız metin yanıt ver. Kod KOŞMA.

Kilitlenecek belgeler `AKTIF_MODEL/v8/kilit.py` içindeki KILIT_BELGELERI listesidir (exchangeInfo_ham.json HARİÇ hepsini
okuyabilirsin; o dosyayı açma). Ana belgeler: `AKTIF_MODEL/ciktilar/v8_asama4_20260927_01/` altında MIMARI.md,
CARRY_KAPISI_ONKAYIT_TASLAK.md, BANKA_ONKAYIT_TASLAK.md, ACIK_SORU_YANITLARI.md, ASAMA4B_KARAR.md, KARARLAR.md;
`ciktilar/v8_kapi_20260929_01/` OLCUT_LISTESI.md, BELIRSIZLIK_COZUMLERI.md; HAR seçimi; kalibrasyon RAPOR.md ve TOPLAMA.json.
Son değişiklikler: `git log --oneline -15`, özellikle f0bf370 (4.02) ve b695292 (4.01).

Görevler:
1. Üç belge (MIMARI, CARRY, BANKA) ve açık soru yanıtları arasında ÇELİŞKİ: aynı nesnenin farklı tanımı, farklı sayı,
   eşik ya da sıra; kalibrasyon sonuçlarının (BANKA §3.7 "Kalibrasyon sonuçları") TOPLAMA ve kalibrasyon RAPOR'uyla
   birebirliği; kapı ölçütlerinin (CARRY §6, OLCUT_LISTESI, BELIRSIZLIK_COZUMLERI, CARRY §15) birbirine uyumu.
2. Kilitten sonra "yorum gerektirecek" belirsiz kural: hüküm anında iki makul okumaya izin veren her yer (özellikle
   BANKA §2.4–§2.5, §3.4 ölçüt tablosu, §4 Kelly/𝓛*, §5.5, §8; CARRY §7 karar kuralı).
3. ACIK_SORU_YANITLARI #23 ve #24 (1 Ekim; ana oturum kararı, D görülmeden): gerekçeleri belgeyle uyumlu mu?
4. Kilit sırasında yapılacaklar (`kilit.py`): deneme defterine A4-carry-kapisi satırı (N etkisi: BANKA §3.3), belge ve
   kod hash'leri, ön koşullar. Kilitten önce yapılması gereken başka adım var mı?
5. Genel hüküm: KILIT için hazır mı; değilse kilidi engelleyen maddeler.

Yanıt biçimi (Türkçe):
## celiskiler
`[OLDURUCU|CIDDI|ORTA|DUSUK] başlık — belge:satır ↔ belge:satır — sorun — düzeltme` (en fazla 12; yoksa "yok")
## belirsizlikler
aynı biçim (en fazla 8)
## kilit_adimlari
madde listesi
## genel_hukum
1–3 cümle.

Yasaklar: BANKA_MUHURLU.json, uygun_evren.json, SECIM.json, secim_cikti.json okunmaz, dosya bilgisi de sorgulanmaz
(AKTIF_MODEL/ciktilar/v8_banka_20260924_01 klasörünü listeleme; yalnız V8_DENEME_DEFTERI.csv açık yoluyla okunabilir);
banka coinleri/Z1/Z2 araştırılmaz; D verisi, v8_veri klasörü ve ham zip'ler okunmaz;
ciktilar/v8_sembol_filtreleri_20260930_01/exchangeInfo_ham.json okunmaz; .env okunmaz; config.py import edilmez;
REV1 motoruna (AKTIF_MODEL/motor), bota, sunucuya dokunulmaz; web yok; hiçbir dosyaya yazma; kod koşma.
