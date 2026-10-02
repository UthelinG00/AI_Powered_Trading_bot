"""Carry kapısı sentetik doğrulaması (CARRY_KAPISI_ONKAYIT_TASLAK §8.5; BX-08; ölçüt eşlemesi §15 madde 16 c).
D kullanmaz. Üreteç §8.5'te dondurulmuştur; eşleme 16 (c)'dedir (koşudan önce, e701040). Ölçütler kapının dondurulmuş
kodu `kapi/olcutler.py` ile hesaplanır. V1–V6 fikstürde yoktur: P(B) = bağlayıcı K1, K2, K5–K11'in hepsinin geçme oranı
("V'siz kapı geçiş oranı"). Sonuç eşikleri kendiliğinden değiştirmez; kilitten önce kullanıcıya sunulur.
Kullanım (v8 dışından): python kapi_sentetik.py [--tekrar N] [--isci N] -> sonuc.json"""
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
V8 = BURASI.parents[1] / 'v8'
sys.path.insert(0, str(V8))

from kapi import olcutler as O  # noqa: E402

TOHUM = 20260929
N_HAFTA, N_AY = 143, 33
H = 52.0
SIGMA_P, SIGMA_D, SIGMA_T = 0.15, 0.03, 0.09
PHI = 0.5
MALIYET_YIL = 0.009
K8_FUNDING_PAY, K8_ISIM = 0.8, 40
SIGMA_N = math.sqrt(SIGMA_P ** 2 + SIGMA_D ** 2)
OLCUTLER = ('K1', 'K2', 'K5', 'K6', 'K7', 'K8', 'K9', 'K10', 'K11')

# (ad, s, mu_d (yıllık; s verilmişse None), mu_P (yıllık), rho, b_A)
SENARYOLAR = (
    ('H1_s0.30_rho0', 0.30, None, 0.0, 0.0, 0.0),
    ('H1_s0.30_rho0.3', 0.30, None, 0.0, 0.3, 0.0),
    ('H1_s0.45_rho0', 0.45, None, 0.0, 0.0, 0.0),
    ('H1_s0.45_rho0.3', 0.45, None, 0.0, 0.3, 0.0),
    ('H0b', 0.40, None, -0.09, 0.0, 0.0),
    ('H0c_ortalama', None, 0.01, 0.03, 0.0, 0.0),
    ('H0c_faktor', 0.45, None, 0.0, 0.0, 0.40),
)


def uret(senaryo_no: int, tekrar_no: int) -> tuple:
    """(KapiGirdisi alanları için seriler) — 16 (c) eşlemesi."""
    _, s, mu_d, mu_p, rho, b_a = SENARYOLAR[senaryo_no - 1]
    rng = np.random.Generator(np.random.PCG64(np.random.SeedSequence((TOHUM, senaryo_no, tekrar_no))))
    hs = SIGMA_P / math.sqrt(H)
    x = rng.normal(0.0, hs, size=(4, N_HAFTA))                           # x_B, x_A, x_R, x_S
    b = np.array([0.0, b_a, 0.0, 0.0])
    e = rng.normal(0.0, hs * math.sqrt(1.0 - float(b @ b)), size=N_HAFTA)
    p = mu_p / H + b @ x + e
    md = (s * SIGMA_N) if mu_d is None else mu_d
    sd_u = SIGMA_D / math.sqrt(H)
    u = np.empty(N_HAFTA)
    u[0] = rng.normal(0.0, sd_u)
    yen = rng.normal(0.0, sd_u * math.sqrt(1.0 - PHI ** 2), size=N_HAFTA - 1)
    for w in range(1, N_HAFTA):
        u[w] = PHI * u[w - 1] + yen[w - 1]
    d = md / H + u
    c = np.full(N_HAFTA, MALIYET_YIL / H)
    f = d + c
    n = f - c + p
    z = (n - n.mean()) / n.std()
    t = (SIGMA_T / math.sqrt(H)) * (rho * z + math.sqrt(1.0 - rho ** 2) * rng.normal(0.0, 1.0, size=N_HAFTA))
    return f, c, p, n, t, x, d


def _seri(f, c, p, t) -> dict:
    n = f - c + p
    return {'F': f, 'C': c, 'P': p, 'N': n, 'N_g': n, 'a_C': np.zeros_like(n), 'T': t, 'T_g': t}


def degerlendir(senaryo_no: int, tekrar_no: int) -> dict:
    f, c, p, n, t, x, d = uret(senaryo_no, tekrar_no)
    ana = _seri(f, c, p, t)
    ay = (np.arange(N_HAFTA) * N_AY) // N_HAFTA
    aylik = {'FC': np.array([d[ay == m].sum() for m in range(N_AY)])}
    faktor = dict(zip(O.FAKTORLER, x))
    K = {'K1': O.k1(ana), 'K2': O.k2(ana), 'K5': O.k5(aylik), 'K6': O.k6(_seri(f, 2 * c, p, t)),
         'K7': O.k7(_seri(f, 3 * c, p, t)), 'K8': O.k8(_seri(K8_FUNDING_PAY * f, c, p, t), K8_ISIM),
         'K9': O.k9(ana, faktor), 'K10': O.k10(ana), 'K11': O.k11(ana, faktor)}
    return {k: bool(K[k]['gecti']) for k in OLCUTLER}


def _is(arg) -> tuple:
    sn, bas, bit = arg
    return sn, [degerlendir(sn, r) for r in range(bas, bit)]


def wilson(k: int, n: int, z: float = 1.959963984540054) -> tuple:
    p = k / n
    m = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / (1 + z * z / n)
    o = (p + z * z / (2 * n)) / (1 + z * z / n)
    return (p, max(0.0, o - m), min(1.0, o + m))


def main(argv):
    tekrar = int(argv[argv.index('--tekrar') + 1]) if '--tekrar' in argv else 10000
    isci = int(argv[argv.index('--isci') + 1]) if '--isci' in argv else 12
    parca = 250
    isler = [(sn, b, min(b + parca, tekrar)) for sn in range(1, len(SENARYOLAR) + 1) for b in range(0, tekrar, parca)]
    t0 = time.perf_counter()
    sonuc = {sn: [] for sn in range(1, len(SENARYOLAR) + 1)}
    with ProcessPoolExecutor(max_workers=isci) as h:
        for sn, r in h.map(_is, isler):
            sonuc[sn].extend(r)
    out = {'tohum': TOHUM, 'tekrar': tekrar, 'hafta': N_HAFTA, 'ay': N_AY, 'senaryolar': {}}
    for sn, (ad, s, mu_d, mu_p, rho, b_a) in enumerate(SENARYOLAR, start=1):
        r = sonuc[sn]
        b = sum(all(x.values()) for x in r)
        out['senaryolar'][ad] = {
            'parametre': {'s': s, 'mu_d': mu_d, 'mu_P': mu_p, 'rho': rho, 'b_A': b_a},
            'P_B_Vsiz': wilson(b, len(r)), 'B_sayisi': b,
            'olcut_gecme': {k: sum(x[k] for x in r) / len(r) for k in OLCUTLER}}
    out['sure_sn'] = round(time.perf_counter() - t0, 1)
    out['betik_sha256'] = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    b = json.dumps(out, indent=1, sort_keys=True).encode('ascii')
    ad = 'sonuc.json' if tekrar == 10000 else f'deneme_{tekrar}.json'
    (BURASI / ad).write_bytes(b)
    print(json.dumps({k: round(v['P_B_Vsiz'][0], 4) for k, v in out['senaryolar'].items()}), out['sure_sn'], flush=True)


if __name__ == '__main__':
    main(sys.argv[1:])
