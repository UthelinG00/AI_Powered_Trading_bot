# B5 özgün epizot atfı — Düzey 2 A birincil eşdeğerliği (ön-kayıt)

Tarih: 2026-09-30 (dizüstü oturumu), koşudan ÖNCE yazıldı. Tetikleyen: Codex T19 CIDDI-2
(`v8/codex_cagrilari/20260930T19_kapi_banka_dogrulama_yanit.md`): "Düzey 2'de pozisyon yalnız 01:00'de değişir" gerekçesi
A için geçersiz — devreden emirler 00:00 dışındaki her saatte katılım sınırıyla kısmen dolar (`motor/geri_test.py`
dolum_adimi, `motor/emir.py` saat_dolumu). Bir dolgu saati ile onu tersine çeviren kayıt arasında gün içi dolumla epizot
değişirse, özgün epizot atfı (BANKA §3.7 netleştirme 11) eski kuraldan farklı sonuç verebilir.

**Hipotez.** Düzey 2'nin 140 A birincil biriminin gövdesi (son_hash hariç bütün alanlar, B5 dahil) dondurulmuş kodla
(sunucu, `KOD_DONDURMA.json`) ve güncel yan dal koduyla (claude/v8-502e-dizustu, commit kanıt bloğunda) bayt düzeyinde
aynıdır. B birincil (trend sanal bacağı yalnız 01:00'de değişir; Codex T19 kabul etti) ve B5 tüketmeyen birimler
(null, x2, x3, çıkarma) kapsam dışıdır.

**Koşu.** Sunucuda (dondurma ile aynı platform ve ortam; dizüstü–sunucu platform eşitliği FARKLI olduğu için dizüstünde
değil), güncel kod `/opt/v8_yeni/AKTIF_MODEL` altında, Düzey 2 koşusuna dokunmadan, 6 işçi. Eski gövdeler sunucunun
`duzey2/` klasöründeki `d2_*_A_birincil.json` zarflarıdır (girdi dosyası sha256'ları kanıta yazılır). Betik
`ciktilar/v8_b5_a_esdegerlik_20260930_01/b5_a_esdegerlik.py`; sonuç değeri yazılmaz, yalnız alan adı ve eşitlik.

**Kabul.** 140/140 birim "aynı" ve güncel kimlikler koşu boyunca sabit → Düzey 2 dondurulmuş kodla geçerli; U-66'nın
"kalibrasyon çıktıları değişmez" cümlesi bu kanıta bağlanır.

**Ret (≥ 1 birim farklı).** Tek kimlik ilkesi (kilit tüm birimlerin tek kod kimliği taşımasını ister) nedeniyle
yamalı birim değişimi yapılmaz: kalibrasyon kodu güncel kodla yeniden dondurulur (yeni KOD_DONDURMA, deneme defteri
notu) ve Düzey 2 tamamı sunucuda baştan koşulur; o sırada süren koşu durdurulur. Farkların sayısı ve alan adları
raporlanır, değerleri raporlanmaz.

**Yan kontrol.** Dizüstü eşdeğerliği (`esdegerlik_502e.py`, 4 duman birimi, dizüstü platformu) aynı oturumda ayrıca koşar;
bu kontrolün yerine geçmez.

## Ek (Codex T20, 30 Eylül; hiçbir sonuç görülmeden önce değil — erken koşunun ilk 42 birimi "aynı" görülmüştü; kabul
kuralı yalnız SIKILAŞTI, gevşemedi)

Codex T20 üç CIDDI buldu: yeniden başlatma girdi/betik hash'ine bağlı değil; kabul "tam 140 ve dondurulmuş kimlik"
olarak zorunlu değil; sonuç kilide bağlı değil. Kararlar:
1. İlk sürümle sunucuda başlamış koşu (v8-b5a, 6 işçi, Düzey 2 sürerken) **erken uyarıdır**: bir FARKLI birim görülürse
   ret kuralı hemen uygulanır (Düzey 2 durdurulur). Kabul kanıtı değildir.
2. **Kabul koşusu:** düzeltilmiş betik (bu commit) Düzey 2 bittikten sonra, tamamlanmış `duzey2/` klasörü üzerinde,
   boş jsonl ile baştan koşar. Kabul: iş listesindeki A birincil kümesi tam 140 benzersiz birim; her birimin satırı var
   ve "aynı"; her zarf bütün (birim kimliği, govde_sha256); eski dört kimlik KOD_DONDURMA'dakiyle aynı; güncel ortam ve
   HAR dondurmayla aynı; güncel kimlikler ve betik koşu boyunca sabit. Devam satırı yalnız aynı güncel kimlik, aynı betik
   sha256'sı ve bugünkü girdi dosyasının sha256'sıyla kullanılır.
3. Kanıt bloğu `duzey2/` klasör özetini (`kanit.klasor_ozeti`) taşır; kilit (`v8/kilit.py`) sonucu zorunlu ön koşul
   olarak okur: gecti, 140/140, kanıt bloğu KOD_DONDURMA'yla, güncel kimlikler kilit anındaki girdilerle ve klasör özeti
   bitiş kanıtıyla aynı olmalı.
