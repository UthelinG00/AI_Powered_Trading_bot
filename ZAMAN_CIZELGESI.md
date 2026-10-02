# Zaman çizelgesi

Bu depo yeni ve tek commit'lik bir geçmişle yayımlandı. Özgün çalışma özel bir depoda yürütüldü; aşağıdaki commit
hash'leri ve zamanları o depodandır.

**Neyi bağımsız doğrulayabilirsiniz, neyi doğrulayamazsınız:**
- **Bağımsız doğrulanabilir:** (1) dosya bütünlüğü ve hash zinciri (`dogrula.py`); (2) bankanın seçimi: `DAMGA.json`
  23 Eylül 21:47 UTC'de damgalandı ve seçimi drand'ın 6492331. turuna bağladı; o tur 22:02 UTC'de, damgadan sonra
  yayımlandı ve geriye dönük değiştirilemez. Seçim betiği ve girdileri bu turla birlikte bankayı yeniden üretir.
- **Doğrulanamaz (çalışma kaydı):** özel depodaki commit zamanları, kilidin ve dondurmanın banka sonuçları görülmeden
  yapıldığı, şifreli sonuçların hüküm anına kadar açılmadığı. Bunlar tarafımızca tutulan kayıtlardır; dış okuyucu için
  kanıt değil, beyandır. Özel depo commit'leri GitHub'a o anlarda itilmiştir; istenirse inceleme için erişim verilebilir.

| Zaman (UTC) | Olay | Özel depo commit'i | Bu depodaki kanıt |
|---|---|---|---|
| 2026-09-23 21:47 | **Banka mühürü damgalandı.** Seçim drand zincirinin 6492331. turuna bağlandı; tur 22:02 UTC'de, damgadan **sonra** yayımlandı | 326d7dd (depo ilk durumu, 24 Eylül) | `ciktilar/v8_banka_20260924_01/DAMGA.json`, `SECIM.json`, `banka_sec.py` |
| 2026-09-24 → 30 | Tasarım (Aşama 1–4), motor, HAR seçimi, kalibrasyon (Düzey 1–2) | çok sayıda | `V8_DENEME_DEFTERI.csv`, `v8_kalibrasyon_20260929_01/RAPOR.md` |
| 2026-10-01 19:05 | **Ön-kayıt kilidi** (`KILIT.json`: 29 belge, kod/parametre/ortam/veri kimlikleri, defter 22 satır) | 71cf576f50722a7ef7580ba03f757780014df40a | `ciktilar/v8_kilit_20261001/KILIT.json` |
| 2026-10-01 20:30 | Carry kapısı koşusu; denetim listesi hüküm açılmadan itildi | b1bcd41e3b6816c384a32b6e174fc43ba3ac0a74 | `ciktilar/v8_kapi_kosu_20261001/DENETIM_LISTESI.md` |
| 2026-10-01 20:31 | **Kapı hükmü: A** (carry reddedildi) | af86403b63fed2eaf2d0b7b6db791e8b5c8ce160 | `ciktilar/v8_kapi_kosu_20261001/KAPI_RAPORU.md` |
| 2026-10-02 05:35 | İlk kuru koşu teknik hata ile durdu (N1 yanlış alarmı; performans açılmadı) | 485f720 | `ciktilar/v8_kuru_20261002b/HATA_N1.md` |
| 2026-10-02 14:49 | **Teknik ek** `KILIT_TEKNIK_1` (banka_oncesi; tek hak) | 4666db25cce22e1545639442fdbf33166cb936a1 | `ciktilar/v8_kilit_20261001/KILIT_TEKNIK_1.json` |
| 2026-10-02 15:46 | Kuru koşu temiz (539/539 birim) | 42a2dec4c4fb2156f581555de7f00655e8686f74 | `ciktilar/v8_kuru_20261002c/RAPOR.md` |
| 2026-10-02 15:52 | **Dondurma** (`DONDURMA.json`; kullanıcı onayı) | de596953cadbad43c1cc699d6391ed8693de821c | `ciktilar/v8_dondurma_20261002/` |
| 2026-10-02 18:08 | Banka açılışı ve tek atış koşusu (ayrı değerlendirici oturum) | 9aff1204acef70078c6a2236ff647248ba59c2a1 | `ciktilar/v8_banka_acilis_20261002/`, `ciktilar/v8_banka_kosu_20261002/` |
| 2026-10-02 18:14 | **Kör denetim listesi** (T1–T5 temiz) ve `DENETIM_TAMAM.json` | fe808dbf46e9eec0c5577c96c058acd0e959ca15 | `ciktilar/v8_banka_kosu_20261002/DENETIM_LISTESI.md` |
| 2026-10-02 18:31 | **Banka hükmü: RET** | 658794e855ceef9b775712a78d531118a502ec6c | `ciktilar/v8_banka_kosu_20261002/hukum/`, `SONUC.md` |

Saatler özel depodaki commit zamanlarıdır (UTC'ye çevrilmiş; olayın kendisi birkaç dakika önce olabilir).
