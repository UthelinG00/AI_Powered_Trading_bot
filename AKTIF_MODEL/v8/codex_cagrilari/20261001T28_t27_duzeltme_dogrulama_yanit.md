## kapanis

Aşağıda CARRY ve BANKA, ilgili `*_ONKAYIT_TASLAK.md` dosyalarını belirtir.

| T27 maddesi | Durum | Gerekçe ve yer |
|---|---|---|
| Ç1 — Ayrı sentetik doğrulama | **KAPANDI** | Sonuç üretilmiş, betik hash’i eşleşiyor ve kilit belgeleri/ön koşullarına bağlanmış (`kilit.py:72`, `kilit.py:219`). |
| Ç2 — Son defter–N bağı | **KAPANDI** | İlk kilit için güncel N ve defter hash’i TOPLAMA ile zorunlu eşleştiriliyor (`kilit.py:216`, `TOPLAMA.json:21`, `TOPLAMA.json:1496`). |
| Ç3 — Teknik yeniden koşunun kilit yolu | **KISMEN** | Ek kayıt tanımlanmış fakat varsayılan ön koşullarla çalışamıyor ve kapı girişine bağlanmamış (`kilit.py:432`, `kilit.py:433`, `v8/kapi/kosu.py:254`). |
| Ç4 — HAR kullanılabilirliği | **KAPANDI** | Havuzlu 30 eğitim gözlemi, rank=4 ve sekiz artık haftası uygulanmış HAR ön-kaydına bağlanmış (`CARRY:1004`). |
| Ç5 — #23 gerekçesi | **KAPANDI** | n<30 gerekçesi açıkça geri çekilip risk tercihi/kapsam gerekçesi konmuş (`CARRY:1009`, `ACIK_SORU_YANITLARI.md:69`). |
| Ç6 — T4-d/K8 istisnası | **KAPANDI** | İşlem dışı isim istisnası ve R5’te raporlanacak ihlaller açıkça eklenmiş (`BANKA:1060`). |
| Ç7 — Ana ölçüt tablosu | **KAPANDI** | B2=bağlayıcı/d*=0,90, B5/B10=R ve B6=2 tabloya işlenmiş (`BANKA:406`). |
| Ç8 — L=1 çıkarımı | **KAPANDI** | Monotonluk varsayımı kaldırılıp öneri hesaplanan uygun kümeye ve CAGR sıralamasına bağlanmış (`BANKA:1123`). |
| B1 — Hüküm sonrası düzeltme sınırı | **KISMEN** | Öncesinden bağımsız hüküm sonrası hak tanımlanmış; ancak 21(g) ve kod bankaya toplam yalnız bir ek tanıyor (`BANKA:1068`, `BANKA:1083`, `kilit.py:430`). |
| B2 — Tanımsız ölçüt | **KAPANDI** | Sonlu NAV’dan hesaplanamayan bağlayıcı ölçüt, tanımsız null SR ve rapor satırlarının davranışı yazılmış (`BANKA:1072`). |
| B3 — Sentetik karar girdileri | **KAPANDI** | K5–K8 eşlemeleri ve V1–V6’nın dışlanması koşudan önce tanımlanmış (`CARRY:1013`, `kapi_sentetik.py:79`). |

## sentetik

**§8.5’in §15/16(c) ile tamamlanmış eşlemesine betik uyuyor:**

- Yedi senaryo ve sıraları doğru; `s`, funding eksi maliyet ortalamasının **σ_N** ile ölçeklenmesi olarak uygulanıyor (`kapi_sentetik.py:34`, `:38`, `:58`).
- AR(1) φ=0,5; başlangıç durağan dağılımdan, yenilik standart sapması √(1−φ²) ile düzeltilmiş; maliyet yıllık 0,009 (`:59`).
- K5 ayı `⌊33w/143⌋`; K6/K7 maliyeti 2×/3×; K8 funding’i 0,8 ile çarpıyor ve isim sayısını 40 alıyor (`:82`).
- Üreteç tohumu `(20260929, senaryo_no, tekrar_no)`; K2 kendi sabit **20260928** tohumunu kullanıyor (`:52`; `v8/kapi/istatistik.py:22`, `:200`).
- Sonuç **V’siz geçiş oranı** olarak doğru adlandırılmış; gerçek icra/isim çıkarma doğrulaması olduğu ileri sürülmüyor.

Ölçek duyarlılığı da ön-kayıtla uyumlu: vol’ler %60/%80/%40/%40, korelasyon 0,8, standart faktör yüklemesini koruyan dönüşüm, ayrı `100+senaryo_no` akışı ve 2.000 tekrar (`kapi_sentetik_olcek.py:23`, `:41`, `:70`). Her iki betiğin dosya hash’i sonuç kayıtlarıyla eşleşiyor.

Dondurulmuş sonuç yerine geçmediği açık. H1 s=0,45, ρ=0 için kayıtlı nokta tahminleri **37/10.000=%0,37** ve **56/2.000=%2,8**; bunlar olasılık üst sınırı değildir. #27 eşikleri koruyor; #26 sonuçtan bağımsız yayımı BANKA §7.2’ye bağlıyor. Yalnız duyarlılığın “kilit belgesi değildir” ifadesi güncel listeyle çelişiyor.

## n_defter

**N=329 doğru:** 22 veri satırında `Σ max(1,varyant)=22+143+4+1=170`; REV1’in 159’u eklenince 329 olur. Yeni varyant=0 sentetik satırı **+1**, varyant=1 kapı satırı **+1** sayılır (`V8_DENEME_DEFTERI.csv:22`, `:23`; `v8/kalibrasyon/duzey1_karar.py:22`).

Baş kısım hash denetimi, yalnız sona eklemeyi; `N ≥ N_dondurma` koşulu sayacın azalmamasını sağlıyor; iki defter hash’i de TOPLAMA’ya yazılıyor ve bunlar madde 8/21(f) ile tutarlı (`topla.py:78`, `:101`, `:152`, `:171`). Güncel defter ve TOPLAMA hash’lerini kayıtlarla eşleştirdim.

**Kararlar N=327’dekiyle aynı:** σ=0,30 varsayım; B2 bağlayıcı; d*=0,90; B3/B4=0,30; B5/B10 rapor; B6=2; Düzey 2-a A ve B’de 0/100 (`TOPLAMA.json:1077`, `:1358`). Sayısal oranlar tamamen aynı değil: örneğin B2 güç değeri **0,57410546875 → 0,57378515625** olmuş; karar eşiği değişmemiş (`TOPLAMA.json:28`, `git diff f0bf370`).

## yeni_bulgular

- **[CIDDI] Teknik ek varsayılan koşullarla üretilemiyor — `kilit.py:217`, `:248`, `:259`, `:432`; `test_v8_kilit.py:91` —** Deftere zorunlu +1 satır TOPLAMA’yı bayatlatıyor; yenilenen TOPLAMA ise `:433` tarafından değişmiş ekonomik belge diye reddediliyor; motor değişikliğinde yenilenmesi gereken eşdeğerlik kanıtları da aynı çatışmayı taşıyor ve test bunu `onkosul=False` ile atlıyor. **Düzeltme:** İlk kalibrasyonu koruyan, kilit sonrası N ve yenilenen teknik kanıtları ayrı ek içinde doğrulayan protokol kurulsun; ön koşullar açıkken sınansın ve `kapi/kosu.py:254` zincire bağlansın.

- **[CIDDI] Teknik ek izin verilen değişiklikleri sınırlamıyor — `kilit.py:433`, `:461`, `:466` —** Yalnız belge hash’leri ilk kilitle karşılaştırılıyor; veri, parametre, ortam ve sabitler için değişmezlik denetimi, defter için zorunlu sona +1 denetimi yok; son ekin bugünkü durumla eşleşmesi bunların ilk kilitten sapmasını engellemiyor. **Düzeltme:** İzin verilen değişiklikler açıkça sınırlansın, diğer alanlar ilk kilitle karşılaştırılsın ve ek kayıtlar da uzak commit doğrulamasına bağlansın.

- **[ORTA] Düzeltme hakkı ile ek sayacı farklı — `BANKA:1068`, `BANKA:1083`; `kilit.py:430` —** Hüküm öncesi hak kullanıldıktan sonra bağımsız hüküm sonrası düzeltme hakkına ikinci banka eki açılamıyor. **Düzeltme:** Öncesi/sonrası hakları ve toplam sınır belge ile kodda aynı durum tablosuyla tanımlansın.

- **[DUSUK] Duyarlılığın kilit statüsü tutarsız — `ONKAYIT_OLCEK.md:7`; `kilit.py:75` —** Ön-kayıt “kilit belgesi değildir” diyor, güncel liste ön-kaydı ve sonucu kilitliyor. **Düzeltme:** Sonradan arşivsel kilit kapsamına alındığı, ana sonucu ikame etmediği belirtilsin.

## genel_hukum

**KILIT için henüz hazır değil:** sentetik doğrulama ve N=329 bağı kapanmış olsa da teknik yeniden koşu zincirinin çalışabilirliği ve değişmezlik denetimleri engel olarak kalıyor. İnceleme statik okuma ve dosya hash karşılaştırmasıyla sınırlıydı; proje kodu/test çalıştırmadım, dosya yazmadım ve yasaklanan kaynaklara erişmedim.