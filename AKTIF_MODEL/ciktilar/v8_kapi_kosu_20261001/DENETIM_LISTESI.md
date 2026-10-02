# Kapı koşusu denetim listesi (CARRY §7.2; hüküm dosyası açılmadan önce)

Tarih: 1 Ekim 2026, 20:3x UTC. Koşu 19:07:09–20:27:32 UTC, dizüstü, çıkış kodu 0. Bu liste HUKUM.json açılmadan
tamamlandı ve commit edildi; HUKUM.json bu commit'te açılmamış hâliyle durur.

## Dosya hash'leri (koşu günlüğü ve KOSU_OZETI ile aynı)

- DENETIM.json: `d9f1124d9efe09a24b2438170025609e98e01953b4b4a3c4d42b2ff0f3c3c4df`
- HUKUM.json: `745c6a63e26061481c1b2c7967ecdc5d21368cc8ca83d789ba6199a2fa393eed`
- Trend mühür (`muhur/`): açılmadı; ana koşunun `trend_satirlari` hash'i KOSU_OZETI'nde
  (`ccbb1ef2…2eba39`). Banka hükmü açılana kadar açılmaz; git'e girmez.

## Liste

| Madde | Sonuç |
|---|---|
| V1 (kilitli test raporu test_20261001T184830Z, 58/58) | geçti |
| V2 | geçti |
| V3 | geçti |
| V4a / V4b | geçti / geçti |
| V5 (altı koşunun gün denetimi: ana, mc2, mc3, delist50, delist90, k8) | geçti (6/6) |
| V6 | geçti |
| Değişmezler: esas ihlal | yok |
| Değişmezler: teknik ihlal | yok |
| Veri raporu: veri kimliği | `5907a89b…ddfd23f7` = KILIT.json `veri.veri_kimligi` |
| Veri raporu: dosya / sembol | 8345 dosya (= KILIT) / 122 sembol |
| Doldurulan kayıtlar | C: funding 99933, funding dolgu 2, ters kayıt 1; T: funding 45808 (betimsel, eşik yok) |
| Kod kimlikleri (motor, kapi, kalibrasyon, adaptor, kilit) | KILIT.json ile aynı |
| Parametre kimlikleri (varsayılan, kapı, HAR sonucu) | KILIT.json ile aynı |
| Kilit commit'i | 71cf576, uzak dallarda (KOSU_OZETI `kilit_git`) |

## Not: kilit sonrası V1 kayması (kapıyı etkilemez)

Koşu bittikten sonra `python -m kilit dogrula` V1'de durdu ("güncel motor için en yeni test raporu geçmiyor ya da
eksik"). Neden: kilitten sonra U2/U3 için `banka_kos/` ve `testler/` değişti (84099aa, 1f28416, 7b3efe2; ~20:10 UTC).
Bu ikisi tam takım raporunun kod kimliklerindedir; kilidin kod kimliğinde (motor, kapi, kalibrasyon, adaptor, kilit)
değildir. Kapı V1'i koşu başında (19:07) kilitteki raporla geçti ve kapının kullandığı kod kilitle aynıdır. Yeni tam
takım raporu, dondurmadan önceki V1 için koşturuluyor.

Sonuç: denetim listesi temiz; teknik geçersizlik yok. HUKUM.json açılabilir.
