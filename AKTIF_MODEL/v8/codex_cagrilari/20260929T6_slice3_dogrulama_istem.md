Sen v8 kripto motorunun bağımsız kod inceleyicisisin. 5. turda Slice 3'ü (Mimari B carry uydusu) inceleyip 12 bulgu
verdin (AKTIF_MODEL/v8/codex_cagrilari/20260928T5_slice3_inceleme_yanit.md). Aynı anda 4 Claude inceleyici de 9
onaylı bulgu verdi. Yazar hepsini B1–B17 olarak işledi. Görev: düzeltmeleri DOĞRULAMAK ve yeni hata getirip
getirmediklerine bakmak. Hiçbir dosyaya yazma; salt okuma komutları ve karşı örnek betikleri (yalnız stdin/-c ile,
diske yazmadan) çalıştırabilirsin; yalnız metin yanıt ver. Python: "<ev>/Desktop/KRİPTO
PROJECT(CODEX-CLAUDE)/venv/Scripts/python.exe"; sys.path'e AKTIF_MODEL/v8 ekle.

Oku:
- Yazarın bulgu tablosu ve kararları: AKTIF_MODEL/v8/ILERLEME_SLICE3.md ("Tur-5 bulgu işleme" ve "Reddedilen").
- Düzeltme öncesi kod: AKTIF_MODEL/_arsiv/V8_MOTOR_SLICE3_20260929_03/motor/ ; sonrası: AKTIF_MODEL/v8/motor/
  (`git diff --no-index`). Değişen dosyalar: net_cozucu.py, hedef_b.py, carry.py, ayristirma.py, durum.py.
- Yeni testler: testler/test_v8_carry.py (TurBesTest), testler/test_v8_mimari_b.py (TurBesBTest, TurBesAyristirmaTest).
- Tasarım: AKTIF_MODEL/ciktilar/v8_asama4_20260927_01/MIMARI.md §2.6, §3.5, §4.1–§4.7, §5.8; CARRY_KAPISI_ONKAYIT_TASLAK.md §3.2, §3.3, §5.

Özellikle değerlendir:
- B2/B11 net_cozucu: ortak TOL, ikiye bölmenin sınırı toleranssız hedeflemesi, κ için dışbükey aralık araması
  (üçe bölme + ikiye bölme). Dışbükeylik iddiası (S1, S2 = 0,5·Σshort + 0,5·max short, brüt, isim κ'da dışbükey)
  doğru mu? Uygun κ yokken κ'nın en küçük ihlal noktasında bırakılıp son çareye geçilmesi belgeye uygun mu?
- B4/B5 hedef_b sırası: K13(i) trend bileşenine çözücüden önce; yeniden sınama; yalnız azaltma (reduce-only ve
  K13(ii)) net kitaba gerçek w0'a göre; sonra T4-d nihai kitapta. Bu sıra yeni bir tavan/özdeşlik sorunu yaratıyor mu?
- B8 ayristirma: bacak funding'inin funding_saati + kayit_uygula ile bacak miktar geçmişinden hesaplanması; bacak
  durumu budaması; döngü üyeliği.
- Reddedilen X9 (Y1 korunur: V60 < 20M'de carry hafta içi çıkışı) gerekçesi: "çıkış olmasa κ'nın günlük artışı
  <20M'de sanal bacak girişi yaratır, §6.1 bacak maliyeti tanımsız kalır". Kabul/itiraz.

Yanıt biçimi (Türkçe):
## dogrulama
B1..B17 her biri tek satır: `B<n>: KAPANDI | KISMEN | ACIK — gerekçe (≤25 kelime)`.
## x9_gerekcesi
Kabul/itiraz, ≤80 kelime.
## yeni_bulgular
Bu turun getirdiği yeni hata: `[OLDURUCU|CIDDI|ORTA|DUSUK] dosya.py:satır — başlık` + 2-3 cümle, en fazla 8; yoksa "yok".
## genel_hukum
1-2 cümle.

Yasaklar: BANKA_MUHURLU.json, uygun_evren.json, SECIM.json, secim_cikti.json okunmaz, dosya bilgisi de sorgulanmaz
(stat/ls dahil); banka coinleri ve Z1/Z2 verisi araştırılmaz; .env okunmaz; config.py import edilmez; REV1 motoruna
(AKTIF_MODEL/motor/), bota ve sunucuya dokunulmaz; web arama yok; hiçbir dosyaya yazma; carry kapısını koşma.
