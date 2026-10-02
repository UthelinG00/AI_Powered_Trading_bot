# Sembol filtreleri anlık görüntüsü (30 Eylül 2026)

- Kaynak: kamu `https://fapi.binance.com/fapi/v1/exchangeInfo` (anahtarsız, salt okuma; ACIK_SORU_YANITLARI #5 onayı).
- Alınma: 2026-09-30T01:09:20Z — D'ye bakılmadan, kilitten ve banka açılışından önce. Betik: `v8/adaptor/sembol_filtreleri.py`.
- `exchangeInfo_ham.json`: yanıtın baytları aynen (sha256 `73c845e0…`). `SEMBOL_FILTRELERI.json`: geliştirme evreni (122)
  için tablo (sha256 `b9e5849b…`); `ALINMA.json` iki hash'i taşır.
- Kural: adım = max(LOT_SIZE, MARKET_LOT_SIZE stepSize); minNotional = MIN_NOTIONAL.notional. Görüntüde olmayan 5 sembol
  (BTCSTUSDT, EOSUSDT, HNTUSDT, MATICUSDT, SRMUSDT) tabloya girmez; motor varsayılanı uygular (adım 0, minNotional 5 USDT;
  MIMARI §5.1, BANKA §2.3). 117 sembolün 32'si `SETTLING` durumunda (filtreleri geçerli).
- Kapı, D doğrulaması ve banka koşuları aynı tabloyu kullanır; hash KILIT.json'a girer. Ham dosyadaki öteki semboller
  incelenmez.
