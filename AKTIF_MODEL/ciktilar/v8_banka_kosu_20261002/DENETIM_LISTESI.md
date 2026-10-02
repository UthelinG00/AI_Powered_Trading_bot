# Banka kör denetim listesi (8.04; hüküm açılmadan önce, tasarım oturumu)

Tarih: 2 Ekim 2026. Girdi: değerlendirici oturumun commit'i 9aff120 (açık grup). Şifreli sonuçlar, ACILIS ve banka
verisi görülmedi. Denetimler `banka_hukum.py`'nin anahtar gerektirmeyen kısımlarıyla ve elle yapıldı.

| Madde | Sonuç |
|---|---|
| T1 (DENETIM_OZETI) / güncel kod ↔ DONDURMA | yok / fark yok |
| Kilit zinciri (ilk kilit + KILIT_TEKNIK_1, git, uzak commit'ler, güncel V1 = DONDURMA) | geçti |
| T2 (VERI_DENETIM) | yok; 19.766 dosya, checksum/indirme/geçersiz satır 0; K 80, K veri yok 0 |
| VERI_DENETIM ↔ DONDURMA sha256 | aynı |
| T3 | yok |
| T4 muhasebe kapısı | 539 / 539 |
| T5 parite | 20 gün, hata 0 |
| SONUC_DAMGA kökü satırlardan yeniden hesap; birim sayısı | aynı; 539 (taban birimler eksiksiz) |
| DENETIM_OZETI ↔ damga kökü; ↔ IS_LISTESI kimlik sha256 | aynı; aynı |
| IS_LISTESI: kip/mimari, DONDURMA, VERI_DENETIM, dönem, veri kimliği, tohum, alıcı, T1 kimlikleri, taban birimler | banka/A; hepsi aynı (ACILIS kanonik sha256 5940011b… değerlendirici kaydıyla aynı) |
| Rapor kalemleri (hüküm değil) | Eylül funding: arşiv 148, API görüntüsü 48, yok 6; süreklilik sorunu 8; filtresiz sembol 8; eksik funding kaydı 58 |

Sonuç: teknik geçersizlik yok. `DENETIM_TAMAM.json` = {damga kökü, DENETIM_OZETI sha256, commit 9aff120}; bu dosyanın
itildiği commit hüküm betiğine `--dt_commit` olarak verilir. Hüküm (8.05) kullanıcının bilgisayarında, kullanıcının
gizli anahtarıyla açılır.
