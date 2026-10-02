## kapanis

Statik inceleme; dosya yazılmadı, kod/test çalıştırılmadı. Kısa yollar `AKTIF_MODEL/v8/` altındadır.

1. **KISMEN** — İlk V1/güncel V1 ayrımı düzelmiş; koşulsuz ön koşul hesabı teknik ekli zinciri yeniden engelliyor (`banka_kos/acilis.py:314`).
2. **KISMEN** — Teknik ekin çift sayımı kaldırılmış; D doğrulama satırı kullanıcı kararı bekliyor (`banka_hukum.py:89`; `AKTIF_MODEL/ciktilar/v8_dondurma_hazirlik_20261001/UYGULAMA_EK.md:119`).
3. **KISMEN** — T3/T4/T5 halinde çözme duruyor; yayımlanması doğrulanan dosyalar arasında DENETIM_TAMAM’ın kendisi bulunmuyor (`banka_hukum.py:54`, `:140`).
4. **KAPANDI** — Açılış, dondurma, veri denetimi, dönem ve mimari denetlenmiş iş listesine bağlanıyor (`banka_hukum.py:67`).
5. **KAPANDI** — Kapı kanıtları ve kuru koşunun kimlikleri, mimarisi, taban birimleri ve damga kökü doğrulanıyor (`dondur.py:58`, `:79`).
6. **KISMEN** — Eksik alanlar ve uzak dondurma commit’i tamamlanmış; üretici hâlâ yalnız `kapi` eki kabul ediyor ve `ilk_dondurma`/ilk tohum koruma yolu sunmuyor (`dondur.py:118`, `:124`, `:138`).
7. **KAPANDI** — Eklerin sıra/tür/hash eşleşmesi ve commit doğrulaması bağlanmış (`banka_kos/acilis.py:337`, `:341`).
8. **KISMEN** — Genel istisnalar ekrandan gizlenmiş; `AcilisHatasi` hâlâ ham basılıyor ve traceback düz dosyaya yazılıyor (`banka_hukum.py:183`, `:188`).

## yeni_bulgular

- **[CIDDI] Teknik ekli zincir yeniden tıkanıyor** — `banka_kos/acilis.py:314`; `kilit.py:216` — Ek satırı defteri büyütünce değişmeyen TOPLAMA’nın N/hash denetimi başarısız olur; motor düzeltmesi de eski eşdeğerlik kanıtına takılır — Ekli akışta 21 g’nin tarihsel kalibrasyon kanıtı ve yeni V1 ayrımını koruyun.
- **[ORTA] Hata izi açık dosyaya taşınıyor** — `banka_hukum.py:186` — Çözme/hesap hatasının içerik taşıyabilen mesajı `hukum_hata_izi.txt` içine şifresiz kaydediliyor — İzi şifreleyin veya yalnız sabit hata kodu/hash saklayın.

## r1_uyum

`onkosul=False` tek başına kilidi kaldırmıyor: zincir, değişmezler, uzak commit’ler, tarihsel V1 hash’i ve güncel V1 ayrıca denetleniyor; **eksiz akışta T29’daki banka kodu ayrımıyla uyumlu ve güvenceyi zayıflatmıyor**. Ancak ekli akışta kalibrasyon ön koşullarını bugünkü girdilerle yeniden istemek, kilitli 21 g’nin “ekte yeniden doğrulanmaz” hükmüne aykırı ve izinli teknik düzeltmeyi engelliyor (`BANKA_ONKAYIT_TASLAK.md:1089`; `banka_kos/acilis.py:314`).

## genel_hukum

Ön-kayıt, güncel V1 ve 6.14 T2 koşulları sağlandığında 6.15 `banka_kos.py kuru A` başlangıcına bu değişikliklerden kaynaklanan engel görmedim; dondurma ve hüküm için açıklar sürüyor.