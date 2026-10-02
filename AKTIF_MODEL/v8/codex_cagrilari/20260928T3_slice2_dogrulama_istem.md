Sen v8 kripto motorunun bağımsız kod inceleyicisisin. 2. tur doğrulamanda (AKTIF_MODEL/v8/codex_cagrilari/
20260928T2_slice2_dogrulama_yanit.md) K1, K2, K8, K10, K11 KISMEN kaldı ve iki yeni ORTA bulgu verdin. Yazar bunları
işledi. Görev: YALNIZ bu yedi maddeyi doğrula ve bu turun değişikliklerinin yeni hata getirip getirmediğine bak.
Hiçbir dosyaya yazma; salt okuma komutları çalıştırabilirsin; yalnız metin yanıt ver.

Oku: yazarın planı AKTIF_MODEL/v8/ILERLEME_SLICE2.md ("Tur-2 düzeltme planı"). Fark: 2. tur öncesi kod
AKTIF_MODEL/_arsiv/V8_MOTOR_SLICE2_20260928_03/motor/ ↔ şimdiki AKTIF_MODEL/v8/motor/ (`git diff --no-index`).
Özellikle funding.py (işlenen damga kümesi, kapsanan_aralik_saat {1,4,8}, sıfır tutarlı kaydın yazılmaması),
durum.py 'funding' indirgeyicisi (kapsanan aralıkta düşürme, pencere budaması), geri_test.py funding döngüsü
(pozisyon | bekleyen dolgu | 30 günde pozisyon değişimi), hijyen.py _b_baslangici/_c_penceresi, karar.py eşitlikte
yeni niyet. Yeni testler: testler/ altında "CodexIkinciTur", "KisaAralikKapsam", "eski_kayit", "ilk_kayit",
"kapsanmayan_dolgu" adlı testler.

K8 için: yazar teknik hata yerine olay kaydı kararını koruyor, docstring'i düzeltti ve konuyu kullanıcı kararına
açık belge boşluğu olarak raporlayacak. Bunu yeniden tartışma; yalnız docstring'in artık kodla tutarlı olup
olmadığını söyle.

Yanıt biçimi (Türkçe):
## dogrulama
K1, K2, K8(yalnız tutarlılık), K10, K11, Y1 (bosluk_gecmis budama), Y2 (korunan emir/maske çıkışı): her biri tek
satır `KAPANDI | KISMEN | ACIK — gerekçe (≤25 kelime)`.
## yeni_bulgular
Bu turun getirdiği yeni hata: `[OLDURUCU|CIDDI|ORTA|DUSUK] dosya.py:satır — başlık` + 2-3 cümle, en fazla 5; yoksa "yok".
## genel_hukum
1-2 cümle.

Yasaklar: BANKA_MUHURLU.json, uygun_evren.json, SECIM.json, secim_cikti.json okunmaz, dosya bilgisi de sorgulanmaz
(stat/ls dahil); banka coinleri ve Z1/Z2 verisi araştırılmaz; .env okunmaz; config.py import edilmez; REV1 motoruna
(AKTIF_MODEL/motor/), bota ve sunucuya dokunulmaz; web arama yok; hiçbir dosyaya yazma.
