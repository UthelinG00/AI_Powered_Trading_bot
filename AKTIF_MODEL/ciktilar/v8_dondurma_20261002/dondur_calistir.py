"""7.01 dondurma çalıştırıcısı (UYGULAMA_EK rev 4). v8/dondur.py olduğu gibi kullanılır; tek fark: kapı kanıtı
(`kapi_kaniti`) kapı koşusunun kimliklerini **ilk kilitle** (KILIT.json, 71cf576) karşılaştırır. dondur.py bunları
zincirin son haliyle (teknik ek KILIT_TEKNIK_1 sonrası kod) karşılaştırıyordu; kapı ekten önce, ilk kilitle koştu ve ek
kalibrasyon kodunu değiştirdi, bu yüzden karşılaştırma yanlış hedefe yapılıyordu. dondur.py değiştirilmez: değişirse
banka_kos kimliği değişir (kuru koşu bağı bozulur) ve ekli zincirin V1 bağı yeni test raporu kabul etmez.
Kullanım (AKTIF_MODEL/v8 içinden): python ../ciktilar/v8_dondurma_20261002/dondur_calistir.py <dondur.py argümanları>
"""
import json
import sys
from pathlib import Path

V8 = Path(__file__).resolve().parents[2] / 'v8'
sys.path.insert(0, str(V8))
import dondur  # noqa: E402

ilk = json.loads((V8.parent / 'ciktilar' / 'v8_kilit_20261001' / 'KILIT.json').read_text(encoding='ascii'))
_asil = dondur.kapi_kaniti
dondur.kapi_kaniti = lambda kapi, kilit_icerik, kilit_commit: _asil(kapi, ilk, kilit_commit)

if __name__ == '__main__':
    sys.exit(dondur.main(sys.argv[1:]))
