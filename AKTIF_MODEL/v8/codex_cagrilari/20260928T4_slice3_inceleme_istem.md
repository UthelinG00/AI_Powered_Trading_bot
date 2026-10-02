Sen v8 kripto modeli motorunun bağımsız kod inceleyicisisin. Slice 2'yi daha önce üç turda incelemiştin. Bu YENİ
görev: Slice 3 (Mimari B carry uydusu) kodunu tasarım belgesine karşı DOĞRULUK açısından incelemek. Hiçbir dosyaya
yazma; salt okuma komutları çalıştırabilirsin; yalnız metin yanıt ver.

Tasarım (tek doğruluk kaynağı): AKTIF_MODEL/ciktilar/v8_asama4_20260927_01/MIMARI.md §1d, §3.2 (tek matris), §3.5
(T4 tablosu, K8 istisnası), §4.1–§4.7, §5.8 (carry durumu, kaçırılan haftalık karar), §7 carry satırları. Kapının
motordan okuduğu tanımlar: CARRY_KAPISI_ONKAYIT_TASLAK.md §3.2, §3.3, §5.1–§5.6 (aynı klasör).

Yeni kod (AKTIF_MODEL/v8/motor/): carry.py, net_cozucu.py, hedef_b.py, ayristirma.py; değişenler: tipler.py (carry
sabitleri, mimari), hedef.py (A/B yönlendirmesi, HedefKitap.carry), karar.py (B dalı, sanal_baglam), durum.py (carry
alanları). Slice 3 öncesi kod: AKTIF_MODEL/_arsiv/V8_MOTOR_SLICE3_20260928_01/ (`git diff --no-index` ile fark).
Testler: testler/test_v8_carry.py, testler/test_v8_mimari_b.py, fikstür testler/fikstur/saatlik_veri.py
(carry_senaryo_*). Yazarın yorumları (Y1–Y11): AKTIF_MODEL/v8/ILERLEME_SLICE3.md; her birini belgeye uygunluk
açısından değerlendir (kabul/itiraz).

Aradığım şeyler (öncelik sırasıyla):
1. Belgeyle çelişen davranış: §4.4 adım sırası (ölçekleme → bütçe → tavan → miktar → bant → λ), hafta içi çıkış,
   §4.5 adım 0 hedge'in günlük gerçek alt sepetinden kurulması ve T4-c, net çözücüde trend önceliği ve κ^C, S4,
   trend bandının sanal trende göre uygulanması, toplam risk kuralı L(1+ω_C)τ, sanal bacakların zamanlaması ve
   tanımı, s^C sıfır/sıfır kuralı, icra artığı ve netleme kazancının tanımı, CARRY §5.5 özdeşliği.
2. Gelecek bilgisi sızıntısı (PIT), canlı/geri test paritesini bozan yapı, günlükten durum kurulamayan yol.
3. A yolunun (p.mimari='A') davranışının değişip değişmediği.
4. Testlerin kör noktaları.
Stil ve performans önemsiz.

Yanıt biçimi (Türkçe):
## bulgular
`[OLDURUCU|CIDDI|ORTA|DUSUK] dosya.py:satır — başlık` + 2-4 cümle (belgedeki kural §'iyle, koddaki davranış, somut
başarısızlık senaryosu). En fazla 15, en ciddiden başla.
## yorumlar_Y1_Y11
Her biri tek satır: kabul/itiraz + gerekçe.
## test_kor_noktalari
En fazla 5 madde.
## genel_hukum
2-3 cümle.

Yasaklar: BANKA_MUHURLU.json, uygun_evren.json, SECIM.json, secim_cikti.json okunmaz, dosya bilgisi de sorgulanmaz
(stat/ls dahil); banka coinleri ve Z1/Z2 verisi araştırılmaz; .env okunmaz; config.py import edilmez; REV1 motoruna
(AKTIF_MODEL/motor/), bota ve sunucuya dokunulmaz; web arama yok; hiçbir dosyaya yazma. Carry kapısını koşma.
