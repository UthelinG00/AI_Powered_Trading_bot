# Kuru koşu denetim raporu (6.15–6.16)

Tarih: 2 Ekim 2026. Sunucu <sunucu> (Hetzner CPX52, Ubuntu 24.04; python 3.12.14, numpy 2.5.1, pandas 3.0.5,
cryptography 50.0.0 — kilitteki ortam). Kod 4a6b3dd soyu (teknik ek KILIT_TEKNIK_1, commit 4666db2); kilit zinciri
(ilk kilit + ek, git dahil) sunucuda doğrulandı. Komut: `veri_denetim.py kuru ../ciktilar/v8_kuru_20261002c A`, ardından
systemd `v8-kuru` (`banka_kos.py kuru ../ciktilar/v8_kuru_20261002c A --isci 12`, Restart=no).

## Sonuç: temiz (performans açılmadı)

| Kalem | Sonuç |
|---|---|
| Süre | 14:50:36–15:46:09 UTC (56 dk), çıkış 0 |
| Birim | 539 / 539 (529 taban + 10 B10; 500 rejim-null) |
| T1 | kuru: DONDURMA yok, kimlikler kaydedildi |
| T2 (veri denetimi) | yok — 8.345 dosya, 122 aday, checksum temiz |
| T3 | yok |
| T4 (muhasebe kapısı) | 539 / 539 birim geçti; null değişmezleri bütün yollarda geçti |
| T5 (parite, 20 gün) | hata 0 |
| `dondur.kuru_kaniti` | GEÇTİ (bugünkü kod kimlikleri, mimari A, damga kökü, iş listesi bağı, taban birimler) |

Hash'ler: DENETIM_OZETI `dbba2fd9…1fc995d`, SONUC_DAMGA `440bb767…12cb2ae2` (kök `202ec967…3652fce8`), IS_LISTESI
`3bdf1ccc…4938d9a`, VERI_DENETIM `5b5ca6dd…ac22b922`. Şifreli birim sonuçları (tek kullanımlık alıcı; gizli yarı yok)
ve anonim eşleme sunucuda kalır, git dışı.

## Geçmiş

- `v8_kuru_20261002/`: ilk 6.14 veri denetimi (eski kod; kimlik değiştiği için yenilendi).
- `v8_kuru_20261002b/`: ilk kuru koşu, 5 dk sonra null birimlerinde durdu → `HATA_N1.md` (N1 yanlış alarmı), kullanıcı
  onayıyla `banka_oncesi` teknik ekle düzeltildi.

## Sıradaki

7.01 dondurma: `dondur.py ... --kilit_commit 71cf576… --ek_commit 4666db25… --kapi ../ciktilar/v8_kapi_kosu_20261001
--kuru ../ciktilar/v8_kuru_20261002c --alici <kullanıcının age açık anahtarı> --onay dondur` — kullanıcının "dondur"
onayıyla.
