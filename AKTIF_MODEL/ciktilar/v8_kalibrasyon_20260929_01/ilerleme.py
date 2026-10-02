"""Duzey 2 kosusunun parca basina ilerlemesi (takip sayfasi 3.05-3.08). Yalniz birim dosya ADLARINI sayar; sonuc
degerlerini okumaz. Kullanim: python ilerleme.py [duzey2_klasoru] -> JSON."""
import json
import sys
from pathlib import Path

BURASI = Path(__file__).resolve().parent
TOPLAM = {'3.05': 100 * 13, '3.06': 100 * 13, '3.07': 4 * 10, '3.08': 5 * 10 * 50}


def say(d: Path) -> dict:
    ad = [p.stem for p in d.glob('d2_*.json')]
    n = {'3.05': sum(1 for x in ad if x.startswith('d2_a000_') and '_A_' in x and '_null_' not in x),
         '3.06': sum(1 for x in ad if x.startswith('d2_a000_') and '_B_' in x),
         '3.07': sum(1 for x in ad if not x.startswith('d2_a000_') and x.endswith('_A_birincil')),
         '3.08': sum(1 for x in ad if '_null_' in x)}
    return {k: {'bitti': v, 'toplam': TOPLAM[k], 'oran': round(v / TOPLAM[k], 4)} for k, v in n.items()}


if __name__ == '__main__':
    d = Path(sys.argv[1]) if len(sys.argv) > 1 else BURASI / 'duzey2'
    print(json.dumps(say(d), ensure_ascii=False))
