"""Gun basina sure olcumu (SENTETIK 122 coin; D kullanilmaz). Her gunun karar + 24 saatlik adim suresini yazar.
Kullanim: python gun_suresi.py [gun_sayisi] [mimari]   -> gun_suresi_<mimari>.json
"""
import json
import sys
import time
from dataclasses import replace
from pathlib import Path

BURASI = Path(__file__).resolve().parent
sys.path.insert(0, str(BURASI))
from hiz_profil import V8, veri_uret  # noqa: E402,F401

from fikstur.saatlik_veri import gun_ms, saat_ms  # noqa: E402
from motor import geri_test  # noqa: E402
from motor.tipler import Parametreler  # noqa: E402


def main():
    gun = int(sys.argv[1]) if len(sys.argv) > 1 else 150
    mimari = sys.argv[2] if len(sys.argv) > 2 else 'A'
    veri = veri_uret(92 + gun)
    p = replace(Parametreler(), mimari=mimari)
    ayar = geri_test.KosuAyarlari(t0_ms=gun_ms(92), t_son_ms=saat_ms((92 + gun) * 24 - 1))
    damgalar = []
    asil = geri_test._Kosucu.karar_adimi

    def sarili(self, g, T):
        damgalar.append((T, time.perf_counter()))
        return asil(self, g, T)
    geri_test._Kosucu.karar_adimi = sarili
    t = time.perf_counter()
    s = geri_test.kos(veri, ayar, p)
    bitis = time.perf_counter()
    sureler = [b[1] - a[1] for a, b in zip(damgalar, damgalar[1:])] + [bitis - damgalar[-1][1]]
    sonuc = {'mimari': mimari, 'gun': gun, 'toplam_sn': round(bitis - t, 1), 'son_hash': s.gunluk.son_hash,
             'gun_sn': [round(x, 3) for x in sureler]}
    (BURASI / f'gun_suresi_{mimari}.json').write_text(json.dumps(sonuc), encoding='utf-8')
    ilk, orta, son = sureler[0], sum(sureler[1:31]) / 30, sum(sureler[-30:]) / 30
    print(f"{mimari}: toplam {bitis - t:.1f} sn; ilk gun {ilk:.2f} sn; gun 2-31 ort {orta:.2f}; son 30 gun ort {son:.2f}")


if __name__ == '__main__':
    main()
