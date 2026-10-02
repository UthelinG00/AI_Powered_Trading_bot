"""Kapı sentetik doğrulaması — gerçekçi faktör ölçeği ek duyarlılığı (ONKAYIT_OLCEK.md). Dondurulmuş `kapi_sentetik.py`'yi
içe aktarır; yalnız faktör vol'lerini ve x_B–x_A korelasyonunu değiştirir. Kilit belgesi değildir.
Kullanım (v8 dışından): python kapi_sentetik_olcek.py [--tekrar N] [--isci N] -> duyarlilik_olcek.json"""
import os

for _k in ('OMP_NUM_THREADS', 'MKL_NUM_THREADS', 'OPENBLAS_NUM_THREADS', 'NUMEXPR_NUM_THREADS'):
    os.environ[_k] = '1'

import hashlib  # noqa: E402
import json  # noqa: E402
import math  # noqa: E402
import sys  # noqa: E402
import time  # noqa: E402
from concurrent.futures import ProcessPoolExecutor  # noqa: E402
from pathlib import Path  # noqa: E402

import numpy as np  # noqa: E402

BURASI = Path(__file__).resolve().parent
sys.path.insert(0, str(BURASI))
import kapi_sentetik as KS  # noqa: E402

VOL = np.array([0.60, 0.80, 0.40, 0.40])          # x_B, x_A, x_R, x_S (yıllık)
KOR_BA = 0.8
AKIS = 100


def _kovaryans() -> np.ndarray:
    k = np.eye(4)
    k[0, 1] = k[1, 0] = KOR_BA
    s = VOL / math.sqrt(KS.H)
    return k * np.outer(s, s)


KOV = _kovaryans()
LKOV = np.linalg.cholesky(KOV)


def uret(senaryo_no: int, tekrar_no: int) -> tuple:
    _, s, mu_d, mu_p, rho, b_a = KS.SENARYOLAR[senaryo_no - 1]
    rng = np.random.Generator(np.random.PCG64(np.random.SeedSequence((KS.TOHUM, AKIS + senaryo_no, tekrar_no))))
    x = LKOV @ rng.normal(0.0, 1.0, size=(4, KS.N_HAFTA))
    b = np.array([0.0, b_a * KS.SIGMA_P / VOL[1], 0.0, 0.0])
    var_e = KS.SIGMA_P ** 2 / KS.H - float(b @ KOV @ b)
    e = rng.normal(0.0, math.sqrt(var_e), size=KS.N_HAFTA)
    p = mu_p / KS.H + b @ x + e
    md = (s * KS.SIGMA_N) if mu_d is None else mu_d
    sd_u = KS.SIGMA_D / math.sqrt(KS.H)
    u = np.empty(KS.N_HAFTA)
    u[0] = rng.normal(0.0, sd_u)
    yen = rng.normal(0.0, sd_u * math.sqrt(1.0 - KS.PHI ** 2), size=KS.N_HAFTA - 1)
    for w in range(1, KS.N_HAFTA):
        u[w] = KS.PHI * u[w - 1] + yen[w - 1]
    d = md / KS.H + u
    c = np.full(KS.N_HAFTA, KS.MALIYET_YIL / KS.H)
    f = d + c
    n = f - c + p
    z = (n - n.mean()) / n.std()
    t = (KS.SIGMA_T / math.sqrt(KS.H)) * (rho * z + math.sqrt(1.0 - rho ** 2) * rng.normal(0.0, 1.0, size=KS.N_HAFTA))
    return f, c, p, n, t, x, d


def _is(arg) -> tuple:
    KS.uret = uret                                  # işçide üreteci değiştir (dondurulmuş dosya değişmez)
    sn, bas, bit = arg
    return sn, [KS.degerlendir(sn, r) for r in range(bas, bit)]


def main(argv):
    tekrar = int(argv[argv.index('--tekrar') + 1]) if '--tekrar' in argv else 2000
    isci = int(argv[argv.index('--isci') + 1]) if '--isci' in argv else 12
    parca = 250
    isler = [(sn, b, min(b + parca, tekrar)) for sn in range(1, len(KS.SENARYOLAR) + 1) for b in range(0, tekrar, parca)]
    t0 = time.perf_counter()
    sonuc = {sn: [] for sn in range(1, len(KS.SENARYOLAR) + 1)}
    with ProcessPoolExecutor(max_workers=isci) as h:
        for sn, r in h.map(_is, isler):
            sonuc[sn].extend(r)
    out = {'tohum': KS.TOHUM, 'akis': AKIS, 'tekrar': tekrar, 'vol': VOL.tolist(), 'kor_BA': KOR_BA, 'senaryolar': {}}
    for sn, (ad, s, mu_d, mu_p, rho, b_a) in enumerate(KS.SENARYOLAR, start=1):
        r = sonuc[sn]
        b = sum(all(x.values()) for x in r)
        out['senaryolar'][ad] = {'P_B_Vsiz': KS.wilson(b, len(r)), 'B_sayisi': b,
                                 'olcut_gecme': {k: sum(x[k] for x in r) / len(r) for k in KS.OLCUTLER}}
    out['sure_sn'] = round(time.perf_counter() - t0, 1)
    out['betik_sha256'] = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    ad = 'duyarlilik_olcek.json' if tekrar == 2000 else f'olcek_deneme_{tekrar}.json'
    (BURASI / ad).write_bytes(json.dumps(out, indent=1, sort_keys=True).encode('ascii'))
    print(json.dumps({k: round(v['P_B_Vsiz'][0], 4) for k, v in out['senaryolar'].items()}), out['sure_sn'], flush=True)


if __name__ == '__main__':
    main(sys.argv[1:])
