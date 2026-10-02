#!/usr/bin/env bash
# v8 hesaplama sunucusu kurulumu (Ubuntu 24.04). Yalniz kalibrasyon: numpy disinda paket yok, ag gerektirmez.
# Ortam kimligi dondurmayla ayni olmali: "python 3.12.14; numpy 2.5.1".
set -euo pipefail
export DEBIAN_FRONTEND=noninteractive
apt-get update -q
apt-get install -y -q curl ca-certificates tar
if ! command -v uv >/dev/null; then
  curl -LsSf https://astral.sh/uv/install.sh | env UV_INSTALL_DIR=/usr/local/bin sh
fi
mkdir -p /opt/v8
uv python install 3.12.14 --install-dir /opt/v8/python
uv venv /opt/v8/venv --python /opt/v8/python/cpython-3.12.14-*/bin/python3.12
uv pip install --python /opt/v8/venv/bin/python numpy==2.5.1
/opt/v8/venv/bin/python -c "import sys, numpy as np; print('python', sys.version.split()[0] + '; numpy', np.__version__)"
nproc; free -g | head -2; lscpu | grep -E 'Model name|Flags' | sed 's/Flags:.*avx512f.*/Flags: avx512f VAR/;s/Flags:.*/Flags: avx512 YOK/'
