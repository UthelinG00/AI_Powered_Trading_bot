# v8 açık yayım planı (Karar #26; 2 Ekim 2026)

Banka hükmü RET (`ciktilar/v8_banka_kosu_20261002/SONUC.md`). Karar #26: sonuç ne olursa olsun bulgular temizlenip
GitHub'da açık yayımlanır. Bu belge kullanıcı kararlarını, kapsamı ve adımları kaydeder.

## Kullanıcı kararları (2 Ekim)

| Konu | Karar |
|---|---|
| Yol | **Yeni temiz depo**; mevcut özel depo özel kalır, eski geçmiş dışarı çıkmaz |
| Ham piyasa verisi | Yayımlanmaz; **manifest (yol + sha256) ve indirme betikleri** yayımlanır |
| Ham tasarım belgeleri (Aşama 1–4 ajan/jüri/sentez taslakları) | **Girmez**; yalnız deneme defteri ve kısa özet |
| Trend mühürü (kapı `muhur/`) | **Girmez** (CARRY ön-kaydı: "trend satırları hariç", kilitli kural); hash'i yayımlanır |
| REV1 ve bot geçmişi | **Girmez**; N'deki 159 REV1 denemesi için kaynak notu |
| Commit yazarı | GitHub **noreply** adresi |
| Lisans | Kod **MIT**; yazılar (ön-kayıtlar, raporlar, eğitim serisi) **CC BY 4.0** |

## İlke: kilitli dosyalar bayt bayt aynı

KILIT.json'un hash'lediği 29 belge, KILIT_TEKNIK_1, DONDURMA ve hüküm zincirindeki dosyalar **değiştirilmeden**
yayımlanır; herkes hash'leri ve kilit zincirini (git hariç) yeniden doğrulayabilmeli. Bu dosyalardan ikisi yerel bir
Windows yolu içerir (`V8_DENEME_DEFTERI.csv`, `kalibrasyon/TOPLAMA.json`: `C:/Users/<kullanıcı>/...`); hash'i bozmamak
için olduğu gibi kalır (yalnız bir kullanıcı adı; gizli bilgi değil). Kilitli olmayan metinlerde yerel yollar ve sunucu
IP'leri temizlenir.

## Kapsam

**Girer:**
- `AKTIF_MODEL/v8/` — kod, testler, `belgeler/`, test raporları (`ciktilar/test_*`), Codex inceleme kayıtları
  (`codex_cagrilari/`, temizlenmiş), ilerleme dosyaları (temizlenmiş). Hariç: `__pycache__`, `ciktilar/_arsiv`.
- Kilit belgeleri ve bağımlılıkları: `v8_asama4_20260927_01` (yalnız 6 kilitli belge + RAPOR özeti), `v8_kapi_20260929_01`
  (kilitli 2 belge + kapı ön-kayıt eki), `v8_har_secimi_20260929_01`, `v8_kalibrasyon_20260929_01` (Düzey 1 ham klasörü
  `duzey1/` hariç, 1,3 GB), `v8_b5_a_esdegerlik_20260930_01`, `v8_sembol_filtreleri_20260930_01`,
  `v8_kapi_sentetik_20261001`, `v8_hiz_20260929_01` (testlerin fikstürü), `v8_d_kesit_20260929_01`.
- Kilit, kapı, kuru, dondurma, banka: `v8_kilit_20261001`, `v8_kapi_kosu_20261001` (muhur hariç),
  `v8_kuru_20261002`, `v8_kuru_20261002b`, `v8_kuru_20261002c`, `v8_teknik_ek_banka_oncesi_20261002`,
  `v8_dondurma_hazirlik_20261001`, `v8_dondurma_20261002`, `v8_banka_acilis_20261002`, `v8_banka_kosu_20261002`
  (ACILIS dahil — hüküm açıldı; şifreli `sonuc/` ve `denetim/birim/` hariç), `v8_banka_prova_20260930_01` (özetler).
- Banka mühürü: `v8_banka_20260924_01` (mühür, seçim betiği, DAMGA, SECIM, evrenler, deneme defteri) — hüküm açıldı;
  drand turundan yeniden üretilebilirlik için.
- Veri: `v8_veri_20260924_01` manifesti ve indirme betikleri; banka `BANKA_MANIFEST.jsonl` ve `banka_indir.py`.

**Girmez:** ham zip'ler, `v8_asama1–3` ve `v8_asama4` taslak/girdi klasörleri, kapı `muhur/`, şifreli banka sonuçları,
anonim anahtar/eşleme, kullanıcı age anahtarı (ifşa olmuş sayılır; zaten depoda yok), `.env`, REV1 (`AKTIF_MODEL/motor`
ve kök klasörler), `GECMIS/`, sunucu kurulum ayrıntıları dışındaki bot belgeleri, `v8_egitim_notlari` (eğitim serisi
ayrı iş).

## Tarama sonucu (2 Ekim, aday kapsam)

Gerçek anahtar, parola, API anahtarı, token: **yok**. `AGE-SECRET-KEY` geçen yerler kodun biçim öneki ve testteki
sahte değer. Sunucu IP'leri (silinen sunucular) 5 kilitli olmayan dosyada → temizlenecek. Yerel kullanıcı yolu 2 kilitli
dosyada (kalır) ve Codex istemlerinde (temizlenecek).

## Adımlar

1. Dışa aktarma betiği (`yayim_hazirla.py`): kapsamı depo dışındaki bir klasöre kopyalar; kilitli olmayan metinlerde
   yol/IP temizler; kilitli dosyaların hash'lerinin kopyada aynı kaldığını doğrular; ikinci bir gizli bilgi taraması yapar.
2. Yeni depoda: README (ne, nasıl doğrulanır, hüküm RET, sınırlar), `LICENSE` (MIT), yazılar için CC BY 4.0 notu,
   `ZAMAN_CIZELGESI.md` (özel depodaki kilit/dondurma/hüküm commit'leri ve tarihleri; hash'ler), `DOGRULAMA.md`
   (kilit ve zincir nasıl yeniden doğrulanır, veri nasıl indirilir).
3. Yeni depoda tam test takımı (59 dosya) ve kilit doğrulaması (git hariç) koşturulur.
4. Codex bağımsız yayım okuması (gizli bilgi, tutarlılık, eksik dosya).
5. Kullanıcı GitHub'da depoyu açar (ad, açıklama); ilk commit noreply ile; kullanıcı onayıyla push.
