# v8 kilit Adım 3: sentetik kalibrasyon koşusu

Tasarım: `ciktilar/v8_asama4_20260927_01/BANKA_ONKAYIT_TASLAK.md` §3.3, §3.7 (3. revizyon ve uygulama netleştirmeleri).
Kod dondurma kaydı: `KOD_DONDURMA.json` (dört kimlik, N = 327, ön-kayıt ve defter sha256). Kod `v8/kalibrasyon/`,
`v8/banka/`, `v8/motor/`. D verisi, D P&L'i ve banka verisi kullanılmaz. Koşu sırasında yalnız birim sayıları izlenir.

## Adımlar (v8 klasöründen; Python: `<kök>/venv/Scripts/python.exe`)

1. **Duman denetimi (P15):** `python ../ciktilar/v8_kalibrasyon_20260929_01/duman.py`
   → `duman_4isci/`, `duman_1isci_ters/`, `duman_sonuc.json` (`gecti: true` olmalı). ~2 saat.
2. **Düzey 1 (P16):** `python -m kalibrasyon.kosucu ../ciktilar/v8_kalibrasyon_20260929_01/duzey1 duzey1 --isci 14`
   → 128 ayar dosyası (npz + zarf). ~30 dk.
3. **Düzey 2 (P17):** `python -m kalibrasyon.kosucu ../ciktilar/v8_kalibrasyon_20260929_01/duzey2 duzey2 --isci 14`
   → ~5.140 birim. ~1 gün makine zamanı.
4. **Toplama (P18):** `kalibrasyon/toplama.py` (duzey1_topla → kurallar; duzey2_topla) → `kalibrasyon.json`, RAPOR.

## Duraklatma ve devam

- Duraklat: ilgili çıktı klasörüne `DUR` adlı boş dosya koy (yeni birim başlamaz, sürenler biter) ya da süreci kapat /
  makineyi kapat (yalnız o anda yarım kalan birimler kaybolur).
- Devam: `DUR`'u sil ve aynı komutu yeniden çalıştır. Biten ve bütünlüğü doğrulanan birimler atlanır; bozuk ya da yarım
  dosyalar `_karantina/`'ya taşınır (silinmez) ve yeniden koşulur. Sıra ve işçi sayısı sonucu değiştirmez.
- Durum: `python -m kalibrasyon.kosucu <klasör> durum`.
- Kod koşu sırasında değişirse işçiler başlamaz (kimlik denetimi); iş listesi değişirse koşucu reddeder.

## Düzey 2 hesap sunucusunda (30 Eylül 2026; kullanıcı kararı)

**Neden:** Dizüstündeki Düzey 2 koşusu iki kez öldü (dilim 1: Bash arka plan süreci; dilim 2: WMI süreci — Windows olay
günlüğü 07:10 UTC oturum kapanışı + uyku). 232 birim bitmişti. Koşu makineden ve internetten bağımsız olsun diye
Hetzner Cloud CPX52'ye (12 vCPU AMD EPYC Genoa, 22 GB, Ubuntu 26.04) taşındı.

**Ortam:** `sunucu_kur.sh` (uv ile python 3.12.14 + numpy 2.5.1 → ortam kimliği dondurmayla aynı). Sunucuya yalnız
`v8/kalibrasyon`, `v8/banka`, `v8/motor`, `v8/v8_calistir.py`, HAR `sonuc.json` ve bu klasörün betikleri gitti;
D verisi, banka dosyaları ve `.env` gitmedi. Sunucuda dört kimlik (kod, motor, parametre, ortam) ve HAR sha256
KOD_DONDURMA ile aynı; iş listesi sha256 `ae68a5eb…` iki platformda aynı.

**Platform eşitliği (`platform_esitlik.py` → `platform_esitlik_sonuc.json`):** Ortam kimliği işletim sistemini ve
işlemciyi taşımadığı için karışık platformlu Düzey 2 ancak bayt eşitliğiyle kabul edilecekti (karar kuralı betikte,
koşudan önce yazıldı). Sonuç: 3/3 birim (A birincil, B birincil, B x2) **FARKLI** → kural gereği Düzey 2 sunucuda
**baştan**. Farkın türü (değer yazdırılmadan): yalnız kayan nokta düzeyi — göreli fark medyanı ~2e-13, en büyük 3e-10
(özdeşlik hata alanları hariç); alan kümesi, birim ve kimlikler aynı; `son_hash` farklı. Dizüstünün 232 birimi
silinmedi: `duzey2_dizustu_20260930/` (dizüstünde ve sunucuda). Düzey 1 dizüstünde kalır (3.09 yalnız Düzey 2'yi
kapsar). 3.09 bitiş denetimi de sunucuda koşulur; böylece bütün Düzey 2 tek platformda üretilir.

**Koşu:** systemd servisi `sunucu_v8-duzey2.service` (`--isci 12`, dilimsiz; Restart=on-failure, 6 saatte en fazla 3
yeniden başlatma; sunucu yeniden açılınca kendiliğinden başlar). Çıktı sunucuda
`/opt/v8/AKTIF_MODEL/ciktilar/v8_kalibrasyon_20260929_01/duzey2/`, günlük `duzey2_sunucu.txt`. Başlangıç
2026-09-30 09:43:58 UTC. Denetim: `systemctl status v8-duzey2`; `cd /opt/v8/AKTIF_MODEL/v8 && /opt/v8/venv/bin/python -m
kalibrasyon.kosucu ../ciktilar/v8_kalibrasyon_20260929_01/duzey2 durum`.
**Bitince:** sunucuda `python bitis.py` → `bitis_sonuc.json` (gecti true), sonra `duzey2/` + çıktılar dizüstüne çekilir
(`duzey2/` git dışı), 3.10–3.11 `topla.py` dizüstünde. Ardından kullanıcı sunucuyu Hetzner'de **siler**.
