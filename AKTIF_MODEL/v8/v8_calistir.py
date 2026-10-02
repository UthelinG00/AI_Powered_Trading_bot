"""v8 motor icin bagimsiz launcher. REV1'in AKTIF_MODEL/calistir.py'sine dokunmaz, onu import etmez.

Komutlar:
  durum                 -- kimlik ve dosya sayisini yazdirir (salt okuma)
  test                   -- py_compile + her test_v8_*.py'yi izole alt surecte calistirir
  test _child <dosya>    -- (ic kullanim) tek test dosyasini izole ortamda calistirir

Izolasyon: alt surec ag erisimini (socket.connect) engeller. Bu asamada (Slice 1-3) v8 motoru .env/API
anahtari kullanmaz; bu izolasyon REV1'in disiplinini tekrarlayan bir guvenlik marjidir, zorunluluktan degil.
"""
import hashlib
import json
import py_compile
import socket
import subprocess
import sys
import time
from pathlib import Path

KOK = Path(__file__).resolve().parent          # AKTIF_MODEL/v8
MOTOR_DIR = KOK / 'motor'
ADAPTOR_DIR = KOK / 'adaptor'           # dosya okuyan katman (veri yukleyici); motor/ saf kalir
TESTLER_DIR = KOK / 'testler'
BELGELER_DIR = KOK / 'belgeler'
CIKTILAR_DIR = KOK / 'ciktilar'


class AgErisimiEngellendi(RuntimeError):
    pass


def _agi_kapat():
    def engelle(*_a, **_k):
        raise AgErisimiEngellendi("v8 test izolasyonunda ag erisimi yasak")
    socket.socket.connect = engelle  # type: ignore[method-assign]


def _tum_py_dosyalari(kok: Path) -> list[Path]:
    return sorted(p for p in kok.rglob('*.py') if '__pycache__' not in p.parts)


def _birlesik_sha256(dosyalar: list[Path]) -> str:
    h = hashlib.sha256()
    for p in dosyalar:
        h.update(str(p.relative_to(KOK)).replace('\\', '/').encode('utf-8'))
        h.update(p.read_bytes())
    return h.hexdigest()


def _py_compile_hepsi(dosyalar: list[Path]) -> list[str]:
    hatalar = []
    for p in dosyalar:
        try:
            py_compile.compile(str(p), doraise=True)
        except py_compile.PyCompileError as exc:
            hatalar.append(f"{p}: {exc}")
    return hatalar


def durum():
    dosyalar = _tum_py_dosyalari(MOTOR_DIR)
    kimlik = _birlesik_sha256(dosyalar) if dosyalar else '(motor dosyasi yok)'
    print("v8 motor -- Slice 1 (hesaplama cekirdegi) + Slice 2 (durumlu orkestrasyon, Mimari A) + Slice 3 (Mimari B carry uydusu)")
    print(f"motor/ dosya sayisi: {len(dosyalar)}")
    print(f"motor kimligi (sha256): {kimlik}")
    adaptor = _tum_py_dosyalari(ADAPTOR_DIR) if ADAPTOR_DIR.is_dir() else []
    print(f"adaptor kimligi (sha256): {_birlesik_sha256(adaptor) if adaptor else '(yok)'}")
    testler = sorted(TESTLER_DIR.glob('test_v8_*.py'))
    print(f"test dosyasi sayisi: {len(testler)}")


def _child(test_dosyasi: str) -> int:
    _agi_kapat()
    import runpy
    yol = Path(test_dosyasi).resolve()
    sys.argv = [str(yol)]
    try:
        runpy.run_path(str(yol), run_name='__main__')
    except SystemExit as exc:
        return int(exc.code or 0)
    return 0


KIMLIK_KLASORLERI = ('motor', 'adaptor', 'kapi', 'kalibrasyon', 'banka', 'banka_kos', 'testler')
KIMLIK_DOSYALARI = ('kilit.py', 'v8_calistir.py')


def kod_kimlikleri_hepsi() -> dict:
    """Test raporunun ve kilidin karşılaştırdığı kod kimlikleri (klasör başına birleşik sha256; iki kök dosya)."""
    kok = Path(__file__).resolve().parent
    out = {}
    for k in KIMLIK_KLASORLERI:
        d = _tum_py_dosyalari(kok / k) if (kok / k).is_dir() else []
        out[k] = _birlesik_sha256(d) if d else None
    for f in KIMLIK_DOSYALARI:
        out[f] = _birlesik_sha256([kok / f])
    return out


def test() -> int:
    motor_dosyalari = _tum_py_dosyalari(MOTOR_DIR)
    testler_dosyalari = _tum_py_dosyalari(TESTLER_DIR)
    adaptor_dosyalari = _tum_py_dosyalari(ADAPTOR_DIR) if ADAPTOR_DIR.is_dir() else []
    hatalar = _py_compile_hepsi(motor_dosyalari + adaptor_dosyalari + testler_dosyalari + [Path(__file__)])
    if hatalar:
        print("py_compile HATA:")
        for h in hatalar:
            print(f"  {h}")
        return 1

    motor_kimligi_once = _birlesik_sha256(motor_dosyalari)
    kod_once = kod_kimlikleri_hepsi()

    test_dosyalari = sorted(TESTLER_DIR.glob('test_v8_*.py'))
    if not test_dosyalari:
        print("test_v8_*.py bulunamadi")
        return 1

    sonuclar: dict[str, dict] = {}
    basarisiz = 0
    for tp in test_dosyalari:
        ad = tp.name
        cikti = subprocess.run(
            [sys.executable, str(Path(__file__).resolve()), 'test', '_child', str(tp)],
            capture_output=True, text=True,
        )
        gecti = cikti.returncode == 0
        if not gecti:
            basarisiz += 1
        sonuclar[ad] = {
            'exit_code': cikti.returncode,
            'gecti': gecti,
            'stdout_son_satirlar': cikti.stdout.strip().splitlines()[-5:],
            'stderr_son_satirlar': cikti.stderr.strip().splitlines()[-15:] if not gecti else [],
        }
        etiket = 'PASS' if gecti else 'FAIL'
        print(f"[{etiket}] {ad}")
        if not gecti:
            print('\n'.join(cikti.stderr.strip().splitlines()[-15:]))

    motor_kimligi_sonra = _birlesik_sha256(motor_dosyalari)
    if motor_kimligi_once != motor_kimligi_sonra:
        print("HATA: testler sirasinda motor/ dosyalari degisti (beklenmedik)")
        return 1
    if kod_kimlikleri_hepsi() != kod_once:
        print("HATA: testler sirasinda kod dosyalari degisti (beklenmedik)")
        return 1

    BELGELER_DIR.mkdir(parents=True, exist_ok=True)
    (BELGELER_DIR / 'V8_KIMLIK.json').write_text(
        json.dumps({'motor_kimligi_sha256': motor_kimligi_once,
                    'dosya_sayisi': len(motor_dosyalari),
                    'adaptor_kimligi_sha256': _birlesik_sha256(adaptor_dosyalari) if adaptor_dosyalari else None,
                    'guncelleme_utc': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())},
                   ensure_ascii=False, indent=1),
        encoding='utf-8')

    damga = time.strftime('%Y%m%dT%H%M%SZ', time.gmtime())
    cikti_dizin = CIKTILAR_DIR / f'test_{damga}'
    cikti_dizin.mkdir(parents=True, exist_ok=True)
    (cikti_dizin / 'sonuc.json').write_text(
        json.dumps({'motor_kimligi': motor_kimligi_once, 'kod_kimlikleri': kod_once, 'toplam': len(test_dosyalari),
                    'basarisiz': basarisiz, 'sonuclar': sonuclar}, ensure_ascii=False, indent=1),
        encoding='utf-8')

    print(f"\nToplam {len(test_dosyalari)} dosya, {basarisiz} basarisiz.")
    print(f"Rapor: {cikti_dizin / 'sonuc.json'}")
    return 1 if basarisiz else 0


def main() -> int:
    argv = sys.argv[1:]
    if not argv or argv[0] == 'durum':
        durum()
        return 0
    if argv[0] == 'test':
        if len(argv) >= 3 and argv[1] == '_child':
            return _child(argv[2])
        return test()
    print(f"Bilinmeyen komut: {argv[0]} (durum|test)")
    return 2


if __name__ == '__main__':
    sys.exit(main())
