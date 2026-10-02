"""Banka tam motorlu uçtan uca provası (6.12; 30 Eylül dizüstü). Sentetik carry senaryosunda (testler/fikstur) BÜTÜN banka
birimleri gerçek yürütücüyle (şablonsuz) koşar: koşucu (age şifreleme, B10 türetmesi, devam), SONUC_DAMGA, birimleri_coz
(T1), hüküm, rapor satırları ve BANKA_RAPORU.md. Teknik provadır: kabul = zincir hatasız biter ve rapor üretilir.
Sentetik sayıların performans anlamı yoktur; eşikler (Kurallar) yer tutucudur.
Kullanım (v8 dışından): python prova.py A|B [--isci N] -> kosu_<M>/ (git dışı), ozet_<M>.json, BANKA_RAPORU_SENTETIK_<M>.md"""
import os

for _k in ('OMP_NUM_THREADS', 'MKL_NUM_THREADS', 'OPENBLAS_NUM_THREADS', 'NUMEXPR_NUM_THREADS'):
    os.environ[_k] = '1'

import json  # noqa: E402
import sys  # noqa: E402
import time  # noqa: E402
from pathlib import Path  # noqa: E402

BURASI = Path(__file__).resolve().parent
V8 = BURASI.parents[1] / 'v8'
for _d in (V8, V8 / 'testler'):
    sys.path.insert(0, str(_d))

from banka_kos import age, ayar, rapor, rapor_md  # noqa: E402
from banka_kos import hukum as H  # noqa: E402
from banka_kos import kosucu as K  # noqa: E402
from banka_kos import yurutucu as Y  # noqa: E402
from fikstur.saatlik_veri import gun_ms  # noqa: E402
from kalibrasyon.duzey1_esik import Kurallar  # noqa: E402


def bag_kur():
    from test_v8_banka_yurutucu import _bag
    return _bag()


def main(argv):
    M = argv[0]
    isci = int(argv[argv.index('--isci') + 1]) if '--isci' in argv else 12
    cikti = BURASI / f'kosu_{M}'
    kimlik, alici = age.anahtar_uret()
    birimler = ayar.birimler(M)
    t0 = time.perf_counter()
    kosu = K.calistir(cikti, birimler, {'prova': 'sentetik'}, alici, Y.birim_yurut, bag_kur, isci=isci, sessiz=True)
    t_kosu = time.perf_counter() - t0
    damga = K.damga_yaz(cikti, birimler)
    cozulen = H.birimleri_coz(cikti, kimlik, beklenen_kok=damga['kok_sha256'])
    bag = bag_kur()
    hb = H.HukumBaglami(mimari=M, t0_z1_ms=bag.t0_z1_ms, gorulmus_gunler=bag.gorulmus_gunler, tohum_banka=bag.tohum_banka,
                        kurallar=Kurallar(N=327, sigma_sr=0.30, b2_bagli=True, d=0.75, e_b5=0.6, e_b10=0.8),
                        N_hukum=330, birincil_son_ms=bag.birincil_son_ms, z2_bas_ms=gun_ms(125), z2_son_ms=bag.z2_son_ms,
                        z1_dilim_sinir=bag.z1_dilim_sinir, d_bas_ms=gun_ms(94), d_bit_ms=gun_ms(112))
    t1 = time.perf_counter()
    h = H.hukum(cozulen, hb)
    sat = rapor.rapor_satirlari(cozulen, hb)
    md = rapor_md.banka_raporu(h, sat, rapor_md.birincil_metrikler(cozulen, hb), {
        'hukum_turu': h['karar'], 'mimari': M, 'b2_turu': 'B', 'sigma_kaynak': 'varsayim', 'N_hukum': hb.N_hukum,
        'hashler': {'SONUC_DAMGA kok': damga['kok_sha256']}, 'stres_secenegi': {'secenek': 'i', 'hash': '—'},
        'kalibrasyon': {'not': 'sentetik prova; kalibrasyon toplanmadi'}, 'teknik': {'prova': 'sentetik'}})
    t_hukum = time.perf_counter() - t1
    (BURASI / f'BANKA_RAPORU_SENTETIK_{M}.md').write_text(
        '> SENTETİK PROVA — performans anlamı yoktur; eşikler yer tutucudur.\n\n' + md, encoding='utf-8')
    ozet = {'mimari': M, 'birim': len(birimler), 'damga_birim': damga['birim_sayisi'], 'cozulen': len(cozulen),
            'kosu': {k: v for k, v in kosu.items() if isinstance(v, (int, float, str))}, 'isci': isci,
            'sure_kosu_sn': round(t_kosu, 1), 'sure_hukum_rapor_sn': round(t_hukum, 1), 'karar': h['karar'],
            'rapor_bolum': sum(1 for i in range(1, 14) if f'## {i}. ' in md), 'gecti': True}
    (BURASI / f'ozet_{M}.json').write_text(json.dumps(ozet, indent=1, ensure_ascii=False), encoding='utf-8')
    print(json.dumps(ozet, ensure_ascii=False), flush=True)
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
