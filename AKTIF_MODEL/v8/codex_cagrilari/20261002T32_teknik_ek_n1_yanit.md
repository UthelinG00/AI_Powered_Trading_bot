## bulgular

1. **[ORTA] İki ızgara yanlış alarmı tamamen çözmüyor — `AKTIF_MODEL/v8/banka/rejim_null.py:155–161` —** Her ızgara bütün satırlara birlikte uygulanıyor; farklı satır grupları farklı ızgaraların sınırlarına düşerse ikisi de geçerli eşleştirmeyi kaçırabilir. Çalıştırmadan kurulabilen karşı örnek: `t=1e-9`, `ε=1e-16`; dörtlülerin son iki bileşeni `(-0.01, 0)` olsun:
   
   ```text
   a'nın ilk iki bileşeni:
   (0,     0.01), (0,     0.02), (t/2,     0.03), (t/2,     0.04)
   b'nin ilk iki bileşeni:
   (ε,     0.01), (-ε,    0.02), (t/2+ε,   0.03), (t/2-ε,   0.04)
   ```
   
   Satır satır gerçek fark yalnız ε. Sıfır kaymalı ızgara ilk çifti, yarım kaymalı ızgara ikinci çifti yanlış eşler; ham karşılaştırmada `0.01` fark çıkar. **Düzeltme:** İki hızlı denetim başarısız olduğunda tolerans içinde birebir dörtlü eşleştirmesini tamamlayan yöntem kullanın; bu örneği sentetik regresyon testine ekleyin. Toleransı büyütmeyin.

2. **[DUSUK] N uyuşmazlığı testi artık N denetimine ulaşmıyor — `AKTIF_MODEL/v8/testler/test_v8_banka_hukum_dondur.py:306–307` —** Bir ek ve iki commit verildiğinden hata `dondur.py:122–123` üzerinde oluşuyor; yorumda belirtilen N kontrolü (`:132–133`) sınanmıyor. Üstelik yardımcı fonksiyon N’yi daima ek sayısıyla uyumlu kuruyor (`test_v8_banka_hukum_dondur.py:241`). **Düzeltme:** Commit sayısını doğru bırakıp defter N’sini bağımsız bozun; beklenen N hata mesajını doğrulayın.

## sorular

1. **N1’in amaçlanan anlamı korunuyor; fakat denetim eksik.** Eşit satır sayısı önceden denetleniyor (`rejim_null.py:176–180`). Her başarılı sonuç, dörtlüleri bölmeden kurulmuş birebir eşleştirme ve ham değerlerde `atol=tol, rtol=0` demek (`:157–159`). Sonlu girdilerde tolerans içinde hiçbir eşleştirmesi bulunmayan gerçek ihlal böylece geçemez. İki ızgara yanlış kabul yaratmıyor; yukarıdaki yanlış ret riski kalıyor.

2. **Ekonomik parametre/eşik veya null üretimi değişmiyor.** Değişen davranış teknik geçer/kalır kararı ve dondurmanın `banka_oncesi` türünü kabul etmesi (`dondur.py:119`). Null üretimi denetimden önce tamamlanıyor (`rejim_null.py:217–219`); kalibrasyonda denetim yalnız durduruyor (`kalibrasyon/yurutucu.py:125–138`). Dolayısıyla bu yama, mevcut Düzey 1/2 ve B7 null sayısal sonuçlarını kendiliğinden geçersiz kılmaz. Sonuçları yeniden çalıştırarak doğrulamadım. N artışının SR₀ etkisi ise §3.3’ün önceden tanımlı sayım sonucudur.

3. **Test D verisinden bağımsız ve eski hatayı göstermeye uygun.** Sabit tohumlu sentetik üretici kullanılıyor (`testler/fikstur/saatlik_veri.py:32–45,74–81`); eski lexsort denetimi açıkça yeniden kurulmuş ve başarısız olması istenmiş (`test_v8_rejim_null.py:230–252`). Ancak testi çalıştırmadığım için PASS iddiasında bulunmuyorum; iki ızgaranın ortak başarısızlık durumu kapsamda yok.

4. **Evet, incelenen diff bakımından uyumlu.** Deftere yalnız son satır eklenmiş (`V8_DENEME_DEFTERI.csv:24`). Toplam 23 kayıt için `N_v8=20+144+5+2=171`; dolayısıyla `N_defter=330`. Varyant 0, `max(1,varyant)` nedeniyle +1’dir (`kalibrasyon/duzey1_karar.py:24`). Ayrı D doğrulamasıyla `N_dondurma=331` (`dondur.py:32,134`). İlk kilide göre bayt düzeyinde baş-kısım uygunluğunu bu incelemede doğrulamadım; zincir bunu zorunlu denetliyor (`kilit.py:445–448`).

5. **Yalnız ara durum için kabul edilebilir.** Ekten önce V1 üretimindeki döngüyü kırıyor; ek mevcut olduğunda atlama kalkıyor (`test_v8_banka_hukum_dondur.py:330–342`). Bu SKIP, gerçek zincirin geçtiği şeklinde raporlanmamalı. Ek sonrasında test atlanmadan geçmeli ve uzak commit doğrulaması ayrıca tamamlanmalı (`kilit.py:535–537`).

6. **İnceleme onayı bakımından ilk bulgu kapanmalı.** Ardından yeni V1 ve hata testiyle ek üretilebilir; bunlar BANKA §3.7/21(g)’nin açık koşullarıdır (`BANKA_ONKAYIT_TASLAK.md:1089–1095`). İkinci bulgunun da aynı test güncellemesinde giderilmesi gerekir. Henüz üretilmemiş ekin bütünlüğüne onay vermiyorum.

## genel_hukum

Düzeltme ekonomik tasarımı ve N1 toleransını koruyor, ancak iki ızgaranın kanıtlanabilir yanlış alarmı giderilmeden teknik eki inceleme açısından hazır bulmuyorum.