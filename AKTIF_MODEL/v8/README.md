# v8 motor — Slice 1–3: Mimari A çekirdeği ve orkestrasyonu, Mimari B carry uydusu

Bu ağaç, v8 model adayının motor kodudur. **REV1'den (`AKTIF_MODEL/motor/`) tamamen bağımsızdır**: hiçbir dosya
REV1'i import etmez, REV1'in hiçbir dosyası burayı import etmez. `AKTIF_MODEL/calistir.py` bu ağacı görmez ve
görmemelidir; kendi launcher'ı `v8_calistir.py`'dir.

Tasarım kaynağı: `AKTIF_MODEL/ciktilar/v8_asama4_20260927_01/MIMARI.md` (nihai taslak, 2. tur revizyonu dahil).
Bu belge TASLAK durumundadır (koşulmadı, ekonomik kabul NOT_EVALUATED); motor kodu spesifikasyonu birebir
uygular, spesifikasyonu değiştirmez. Belgenin açık bıraktığı yerlerdeki yorumlar aşağıda ve kod yorumlarında yazılıdır.

## Kapsam — üç dilim

- **Slice 1 (27 Eylül, tamam):** Mimari A'nın **saf hesaplama çekirdeği**. Sinyal, σ̂/Σ̂, birim risk, tavan çözücü,
  band, katılım/lot matematiği, maliyet modeli (`sinyal`, `risk`, `boyutlama`, `tavanlar`, `bant`, `katilim`,
  `maliyet`, `tipler`).
- **Slice 2 (28 Eylül, tamam):** Mimari A'nın **durumlu orkestrasyonu** (MIMARI §2, §3.1–§3.5 uygulaması, §5):
  - `gorunum.py` — PIT piyasa görünümü (`gorunum_kur`: yalnız t'ye kadar kapanmış bar/funding), borsa çapı boşluk
    taraması (kesinti durumu karar kaydında taşınır).
  - `hijyen.py` — donma ölçütleri (a)–(d), maske ve maskeden dönüş, işlem dışı günler.
  - `evren.py` — aylık PIT evren, histerezis ve öncelik kuralı.
  - `gunluk.py` — hash zincirli, yalnız eklemeli `OlayGunlugu` (kanonik JSON).
  - `durum.py` — `StratejiDurumu`, `kayit_uygula` indirgeyicisi, `durum_turet` (önce zinciri doğrular).
  - `funding.py` — gerçek uzlaşma, eksik funding dolgusu, kapsamlı ters kayıt, geç gelen kayıt.
  - `emir.py` — lot niyeti, risk azaltan/artıran ayrımı (§5.4), saatlik dolum (`emir_zinciri`'nin tek coin/saat hali).
  - `hedef.py` — `hedef_agirlik` (§5.1): evren → sinyal → birim kitap → kaldıraç → tavan → reduce-only → T4-d.
  - `karar.py` — `karar_ver` (maske ilerletme, aylık evren, hedef, bant, lot, devreden emir öncelik kuralı),
    `kacirilan_karar`.
  - `geri_test.py` — §5.2 saatlik olay döngüsü (`kos`): funding → (00:00) delist uzlaşması + karar / (diğer saatler)
    gün içi boşluk iptali + dolum → değerleme. Katılımsız gölge yol ve maliyet çarpanı k ayarları.
- **Slice 3 (29 Eylül, tamam):** Mimari B'nin **carry uydusu** (MIMARI §4, §5.8). `Parametreler.mimari = 'B'` ile
  açılır; varsayılan `'A'` yolu değişmedi.
  - `carry.py` — carry evreni (V30 histerezisi, V60 tabanı, eksik funding olay sayımı, genişlik), F30/σ^C/skor,
    sıra-OLS nötrleme (R30, s^trend, β), bacaklar (%30, medyan histerezisi, long funding tabanı), β (60 gün, 0,5
    büzülme), haftalık kitap §4.4 adım 1–7 (T4-b ölçekleme, bütçe, carry isim tavanı, bant, λ ile yeniden
    nötrleme), hafta içi çıkış, günlük blok ve BTC hedge'i + T4-c.
  - `net_cozucu.py` — §4.5 adım 1–4: trend önceliği, net isim tavanı (S4 → alt short %3,33), brüt, S1/S2 ikiye
    bölme, κ^C (dışbükey aralık araması), son çare; ortak ihlal denetimi (`ihlaller`, tek tolerans).
  - `hedef_b.py` — B'nin `hedef_agirlik` yolu: ortak Σ̂ (A_t + carry adayları + BTC), trend bandı sanal trende göre,
    yeniden sınama, yalnız-azaltma, T4-d (L(1+ω_C)τ), sanal bacaklar ve s^C.
  - `ayristirma.py` — §4.7 P&L satırları (trend/carry/hedge fiyat ve funding, bacak maliyeti, netleme, icra artığı
    ve s^C bölüşümü), CARRY §5.5 özdeşliği. Carry kapısı bu fonksiyonun çıktısını okur. Bacak funding'i motorun
    kendi funding kuralıyla, her bacağın miktar geçmişinden hesaplanır.
  - `durum.py` carry durumu (q^C*, β, λ, aday listesi, sanal bacaklar, s^C son payları) karar kaydından kurulur.

Testler (241 birim/senaryo testi, 14 dosya): Slice 1'in 74'ü + Slice 2'nin 121'i + Slice 3'ün 46'sı. Uçtan uca
senaryolar (`testler/fikstur/saatlik_veri.py`): A için 150 günlük 5 coin (borsa çapı boşluk, işlem dışı coin, maske
çıkışı, delist uzlaşması, aylık+günlük aynı gün); B için 130 günlük BTC/ETH + 14 alt (ilk Pazartesi, hafta içi
çıkış, kaçırılan ve yapılan Pazartesi, L = 4). Günlükten durum yeniden kurulumu, parite ve bakış-ileri testleri
her ikisinde. Gerçek D verisi kullanılmadı; geri test ve carry kapısı koşulmadı. Sentetik senaryolardaki NAV yalnız
mekanik doğrulamadır, performans değildir.

## Belgenin açık bıraktığı yerlerde verilen yorumlar (Slice 2)

Hiçbiri D verisine bakılarak seçilmedi. Codex incelemesiyle değişenler işaretli.

1. **Borsa çapı boşluk referansı:** çok saatlik kesintide referans küme, kesinti öncesi son temiz saatte tutulur;
   kesinti durumu (`bosluk_ref`) ve son 30 günün boşluk saatleri (`bosluk_gecmis`) karar kaydında taşınır, ilk
   kararda veri başından taranır (Codex K7, K10).
2. **Donma pencereleri:** boşluk saatleri sayaçlara girmez. (b) son güne değen ≥ 6 ardışık boşluk-dışı bar (gece
   yarısını aşabilir); (c) son 16 boşluk-dışı saat; (d) son günün **toplam** eksik saati > 8 (Codex K11 ile "en uzun
   ardışık" yorumundan değişti). (d) günleri getiri hesabından dışlanır (§3.2; Codex K12).
3. **İlk karar:** maske geçmişi verinin ilk gününden kurulur; ısınmadaki donma T0'a taşınır (Codex K4).
4. **İşlem dışı coin** tavan çözücüsüne sabit girer; küçültmeler yalnız serbest isimlere.
5. **Reduce-only ve devreden emir (§5.4):** borsa boşluğunda ve işlem dışı coinde eski emrin risk azaltan parçası
   korunur, risk artıran parçası iptal edilir; yeni niyet eski azaltanın yerine yalnız en az onun kadar azaltıyorsa
   geçer (Codex K6; önceki "hepsini iptal et" yorumu geri alındı). Gün içinde bilinen boşlukta da risk artıran
   parçalar iptal edilir (Codex K5). Korunan parça pozisyonu tam kapatıyorsa tam kapanış sayılır (Codex K14).
6. **Hacim tabanı:** karar anında V60 < 20M olan coinde hedef yalnız azaltılabilir (|w| ≤ |w0|); <20M maliyet dilimi
   yalnız çıkışta kullanılır (Codex K13; önceki "girişi de 25 bps ile fiyatla" yorumu geri alındı).
7. **Funding:** (son 30 günde) işlenmemiş her gerçek kayıt işlenir, geç ya da sıra dışı gelse de; nakit geldiği saatte
   yazılır. Ters kayıt yalnız kaydın kapsadığı aralıktaki dolguları geri alır; kapanmış pozisyonun eksik funding
   borcu da yazılır (Codex K1, K2, K3).
8. **Canlı düzeltme kaydı** miktar taşıyabilir ve pozisyonu değiştirir (Codex K9).

## Belgenin açık bıraktığı yerlerde verilen yorumlar (Slice 3)

Ayrıntı ve gerekçe `ILERLEME_SLICE3.md` (Y1–Y11) ve kod yorumlarında. Codex 6. tur sonrası üçü MIMARI'ye bağlayıcı
kural olarak yazıldı (§4.1 V60 tabanı, §4.5 sıra özeti, §4.7 κ_etkin ve yalnız-azaltma istisnası; önceki metin
`_arsiv/V8_MIMARI_SLICE3_20260929_01/`). Diğerleri: bacak sayısı ⌊0,3·n_C⌋ (Y3); eşit sırada ortalama sıra, eksik
R30'a tanımlı sıraların medyanı (Y4); β̂ hesaplanamıyorsa 1 (Y5); genişlik ×0,5 bütçe adımında (Y6); Pazartesi işlem
dışı tutulan isim korunur ama long funding tabanından geçer ve β'sı yeniden hesaplanır (Y7); ilk Pazartesi'den
önce carry 0 (Y8); işlem dışı coinin sanal trendi değişmez (Y9).

## Bilinen sınırlar ve K8 kararı

- **K8 — kullanıcı kararı (28 Eylül): motor davranışı kalır, MIMARI §3.5'e istisna olarak yazıldı.** İşlem dışı
  (sabit) isimler kendi başına bir tavanı ya da T4-d'yi aşarsa motor **teknik hata vermez**: serbest isimler (toplam
  tavanlarda) sınıra ya da 0'a küçülür, ihlal `tanilar['sabit_tavan_ihlali']` / `['sabit_t4d_ihlali']` olarak
  kaydedilir. MIMARI'nin önceki metni `_arsiv/V8_MIMARI_K8_20260928_01/`.
- **K2 — funding aralık sütunu.** Arşiv kaydın aralığını (`funding_interval_hours`) taşımıyorsa, 4h düzende tek eksik
  kayıt (8 saatlik boşluk) 4h→8h geçişinden ayrılamaz ve dolgusu geri alınır. Veri yükleyici bu sütunu varsa
  `funding_serisi(..., aralik_saat=...)` ile vermelidir.
- **K11 — uzun kesinti.** Hijyen pencereleri en fazla 30 gün geriye bakar; ≥ 29 günlük borsa çapı kesintide (b)
  tarama sınırına takılabilir.
- **Geç gelen funding (yalnız canlı).** Ayrıştırmada sanal bacaklar gerçek kaydı damga saatinde, gerçek nakit geliş
  saatinde yazılır; fark iki saat arasında icra artığına düşer (özdeşlik bozulmaz). Geri testte geliş = damga.
- **Yalnız-azaltma günleri.** Reduce-only, işlem dışı coin ve V60 < 20M günlerinde net hedef sanal bacak toplamından
  ayrılabilir; fark icra artığıdır (MIMARI §4.7 istisnası), isimler `tanilar['yalniz_azaltma']`'da.
- **κ son çaresi.** Uygun κ yoksa (ör. trend bileşeni isim tavanında kırpılmış bir isimde carry küçüldükçe tavan
  aşılıyorsa) κ en küçük ihlal noktasında kalır ve bütün serbest net kitap tek katsayıyla küçülür (belge sırası).
- **Performans:** saf Python; A senaryosu (150 gün, 5 coin) ~13 s, B senaryosu (130 gün, 16 coin) ~7 s + ayrıştırma.
  D ölçeğinde (122 aday, 33 ay) hız ölçülmedi.

## Codex ve Claude bağımsız kod incelemeleri (`codex exec -s read-only`, yerel)

| Tur | İstem / yanıt (`codex_cagrilari/`) | Sonuç |
|---|---|---|
| 1 | `20260928T_slice2_inceleme_{istem,yanit}.md` | 15 bulgu (9 CIDDI, 6 ORTA); hepsi doğrulandı, 13 DOĞRU, 2 KISMEN; düzeltildi |
| 2 | `20260928T2_slice2_dogrulama_{istem,yanit}.md` | 10 KAPANDI, 5 KISMEN, 2 yeni ORTA; düzeltildi |
| 3 | `20260928T3_slice2_dogrulama_{istem,yanit}.md` | K1/K8/K10/Y1/Y2 KAPANDI; K2, K11 KISMEN (yukarıdaki sınırlar); 2 yeni (ORTA, DÜŞÜK) düzeltildi |
| 4 (Slice 3) | `20260928T4_slice3_inceleme_istem.md`, `..._KESIK_gunluk.md` | Kullanım limitiyle kesildi; günlükteki 4 karşı örnekten 3'ü düzeltildi, 1'i sınır |
| 5 (Slice 3) | `20260928T5_slice3_inceleme_{istem,yanit}.md` + `20260929_wf94f2a3aa_slice3_inceleme_sonuc.json` | Codex 12 bulgu; aynı anda 4 Claude inceleyici (bulgu başına 2 şüpheci) 9 onaylı + 2 tartışmalı; birleşik 17 madde (B1–B17) düzeltildi, X9 MIMARI'ye yazıldı |
| 6 (Slice 3) | `20260929T6_slice3_dogrulama_{istem,yanit}.md` | 15 KAPANDI; B4/B16 KISMEN ve 1 yeni ORTA (belge–kod sözleşmesi) → MIMARI §4.1/§4.5/§4.7 güncellendi |

sha256:
- `20260928T_slice2_inceleme_istem.md` 572988963a8dcda35214789301528fca91a5c3f1b2b563fc0708a3d01d82f68c
- `20260928T_slice2_inceleme_yanit.md` cf6f9aa291c07a0490d2730bc6ea8e7d4b89cf2378c27e591325072e3c7fbb60
- `20260928T2_slice2_dogrulama_istem.md` 0e853be39c4123c283a570a6e4558fdb7ffecea37a59be1696a390a6776b4483
- `20260928T2_slice2_dogrulama_yanit.md` 6a643d5f0fef853a2301167dc2cd986d9380b16672372dbb881a8523e1797513
- `20260928T3_slice2_dogrulama_istem.md` 038d8387027dfb0cea58e2151b395da7b50e4fa27969db560cef5a11e0040497
- `20260928T3_slice2_dogrulama_yanit.md` 8e19292c9ada545a5b8fc6102669180b06c014650f8ea50d1fd134124df74b76
- `20260928T4_slice3_inceleme_istem.md` 7da04f03b177b3fcff8de808c060a83403e8c87d58b89f501e0d96a5fee2a7dc
- `20260928T4_slice3_inceleme_KESIK_gunluk.md` 0f5a3458a0dea6100530235ce695d32e4aab501f7ea6e6c57b9da6425443c961
- `20260928T5_slice3_inceleme_istem.md` 6ac38c9a5f08ec7e6d47290ef82dab1054e8891428109789c472cb2b5b96286b
- `20260928T5_slice3_inceleme_yanit.md` c0dfdcaa9bbd6733bd74e7b4ee31d142f58000e90f05101e14d7ac0c9218a615
- `20260929_wf94f2a3aa_slice3_inceleme_sonuc.json` c731d09c7fab703a99b0d6cc4485f37ef6cabb958fb9f86296ca54c641756b5b
- `20260929T6_slice3_dogrulama_istem.md` 33debdd7c2c3de15b37618f3486d04dafe50c74d5c7084b3f3b70b4ed4d56493
- `20260929T6_slice3_dogrulama_yanit.md` f725593c66cd55de410a7b8dd850b4073ac4e92071da359c4df4beba3ac86c16

Her turun düzeltmelerinden önceki kod `AKTIF_MODEL/_arsiv/V8_MOTOR_SLICE2_20260928_0{2,3}/` ve
`V8_MOTOR_SLICE3_2026092{8_01,8_02,9_03}/` altında. Her turun yeni testleri bir önceki koda karşı koşuldu ve orada kaldı
(hatayı gerçekten yakalıyor).

## Kurallar

- `.env` okunmaz, gerçek para/API anahtarı yok — bu ağaç ağa ve borsaya hiç dokunmaz.
- Her fonksiyon saftır: yan etki yok, saat okumaz, ağ yok, rastgelelik yok (testte sabit tohum hariç). Durum
  yalnız olay günlüğünden türetilir; geri test orkestratörü aynı indirgeyiciyi artımsal kullanır.
- Her modül MIMARI.md'nin ilgili bölümüne yorumla atıf yapar; spesifikasyonu tekrarlamaz.
- Testler `testler/test_v8_*.py`, saf `unittest.TestCase`, REV1'in `testler/` üslubuyla aynı.
- `v8_calistir.py test` her koşuda `belgeler/V8_KIMLIK.json` motor kimliğini yeniler ve `ciktilar/test_<zaman>/`
  raporu yazar.

## Kilit Adım 2 sonucu: HAR (29 Eylül)

`ciktilar/v8_har_secimi_20260929_01/RAPOR.md`: QLIKE oranı 0,927, bootstrap üst sınır −0,008 → HAR. Motorda:
`Parametreler.sigma_tahmincisi='HAR'` ve `har_takvimi=HarTakvimi.sonuctan(sonuc)` verilince boyutlama σ̂ =
max(σ̂_HAR, %20); HAR tanımsızsa σ̂_EWMA (`hedef.boyut_sigmalari`, A ve B). Katsayı karar günü dahil son ay başı
tahmini, ŝ² son Pazartesinin yürüyen değeri. Sinyal normalizasyonu, carry σ^C ve maliyet σ_d EWMA'da kalır.
Varsayılan `'EWMA'` eski davranıştır: A ve B sentetik koşularının günlük son hash'i entegrasyon öncesiyle birebir aynı.
Testler `testler/test_v8_har_motor.py`.

D yükleyicisi `adaptor/veri_yukleyici.py` (hash doğrulamalı); D kısa kesit denetimi PASS
(`ciktilar/v8_d_kesit_20260929_01/RAPOR.md`, performans ölçülmedi).

## Sıradaki iş

Kilit Adım 3 (BANKA §3.7 sentetik kalibrasyon). Düzey 2 yazıldığı haliyle ~19.000 CPU saati; tasarım revizyonu
kararı bekliyor (`ILERLEME_VERI_HIZ.md`). Carry kapısı ve bankaya giden koşular yalnız ön-kayıt kilidinden sonra.

## Çalıştırma

```
python AKTIF_MODEL/v8/v8_calistir.py test
```
