"""v8 motor hiz profili: SENTETIK 122 coinli veri (D verisi kullanilmaz). Yalniz sure ve sicak nokta raporlar.

Kullanim: python hiz_profil.py [gun_sayisi] [mimari] [t0_gunu]   (varsayilan 8 gun, A, t0 = gun 92)
t0_gunu buyudukce gecmis uzar: gecmis uzunlugunun gunluk maliyete etkisini olcmek icin.
Ayrica gunlugun son hash'ini yazar: hiz iyilestirmelerinden sonra ayni kosu ayni hash'i uretmelidir (birebir sonuc).
"""
import cProfile
import io
import pstats
import sys
import time
from dataclasses import replace
from pathlib import Path

BURASI = Path(__file__).resolve().parent
V8 = BURASI.parents[1] / 'v8'
sys.path.insert(0, str(V8))
sys.path.insert(0, str(V8 / 'testler'))

from fikstur.saatlik_veri import CoinTarifi, gun_ms, saat_ms, tam_veri_uret  # noqa: E402
from motor.geri_test import KosuAyarlari, kos  # noqa: E402
from motor.tipler import Parametreler  # noqa: E402


def veri_uret(toplam_gun: int):
    t = {'BTCUSDT': CoinTarifi(p0=30000, gunluk_suruklenme=0.002, saatlik_vol=0.005, saatlik_hacim=50e6),
         'ETHUSDT': CoinTarifi(p0=2000, gunluk_suruklenme=0.001, saatlik_vol=0.006, saatlik_hacim=30e6)}
    for i in range(120):
        t[f'A{i:03d}'] = CoinTarifi(p0=1 + i % 17, gunluk_suruklenme=0.001 * (i % 7 - 3), saatlik_vol=0.008,
                                    saatlik_hacim=(0.5 + (i % 11)) * 1e6, funding_orani=0.00005 * (i % 13 - 6),
                                    baslangic_saat=(i % 5) * 24 * 20)
    return tam_veri_uret(t, toplam_gun)


def main():
    gun = int(sys.argv[1]) if len(sys.argv) > 1 else 8
    mimari = sys.argv[2] if len(sys.argv) > 2 else 'A'
    t0g = int(sys.argv[3]) if len(sys.argv) > 3 else 92
    t = time.perf_counter()
    veri = veri_uret(t0g + gun)
    print(f"veri uretimi {time.perf_counter() - t:.1f} sn")
    p = replace(Parametreler(), mimari=mimari)
    ayar = KosuAyarlari(t0_ms=gun_ms(t0g), t_son_ms=saat_ms((t0g + gun) * 24 - 1))
    pr = cProfile.Profile()
    t = time.perf_counter()
    pr.enable()
    s = kos(veri, ayar, p)
    pr.disable()
    print(f"kos {mimari} t0=gun {t0g}, {gun} gun: {time.perf_counter() - t:.1f} sn; son hash {s.gunluk.son_hash}")
    out = io.StringIO()
    pstats.Stats(pr, stream=out).sort_stats('cumulative').print_stats(35)
    print(out.getvalue()[:9000])
    out = io.StringIO()
    pstats.Stats(pr, stream=out).sort_stats('tottime').print_stats(25)
    print(out.getvalue()[:6000])


if __name__ == '__main__':
    main()
