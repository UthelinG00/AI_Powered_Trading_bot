## kapanis

- **1 KAPANDI** — Raporun `mkdir` ve `VD.yaz` işlemleri hata sınırına alınmış (`v8/veri_denetim.py:104`).
- **5 KAPANDI** — Kullanılan D sembollerinin TAMAM dosyaları yüklemeden önce denetleniyor (`v8/banka_kos/veri.py:189`).
- **8 KAPANDI** — Referanslar hariç aday kümesinin K∪D eşitliği zorunlu (`v8/banka_kos/acilis.py:150`).
- **10 KAPANDI** — Mevcut paket sırası ön-kayıtta açıkça tanımlanarak kodla eşleştirilmiş (`BANKA_ONKAYIT_TASLAK.md:1036`, `v8/banka_kos/acilis.py:105`).
- **Yeni 1 — KISMEN** — İlk kayıt okunup hash’i doğrulanıyor, ancak beklenen hash aynı değiştirilebilir DONDURMA’dan geliyor ve bağlantı isteğe bağlı olduğundan bağımsız köken sabitlemesi eksik (`v8/banka_kos/acilis.py:122`).
- **Yeni 2 — KISMEN** — Yazım korunmuş, fakat argüman dönüşümleri hâlâ sınır dışında olduğundan geçersiz `--tohum` ham traceback üretebilir (`v8/veri_denetim.py:38`, `v8/veri_denetim.py:111`).
- **Yeni 3 — KAPANDI** — D manifestindeki kayıp dosya yüklemeden önce T2 üretiyor; işçi yükleyicisi de reddediyor (`v8/veri_denetim.py:51`, `v8/banka_kos/veri.py:189`).
- **Yeni 4 — KAPANDI** — Ek adaylar ve BTC/ETH’nin K veya D’ye konulması reddediliyor (`v8/banka_kos/acilis.py:150`).
- **Yeni 5 — KAPANDI** — Birleşik kimliğin paket sırası mevcut hesaplama korunarak belgelenmiş (`BANKA_ONKAYIT_TASLAK.md:1037`).

## yeni_bulgular

yok

## genel_hukum

Yalnız statik incelemeye göre banka betiği dondurmaya henüz hazır değil: bağımsız ilk-dondurma sabitlemesi ve argüman hata sınırı tamamlanmalı; kod/test çalıştırmadım, dosya yazmadım.