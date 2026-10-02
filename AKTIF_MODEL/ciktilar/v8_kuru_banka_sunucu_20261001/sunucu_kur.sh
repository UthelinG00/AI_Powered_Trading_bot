#!/usr/bin/env bash
# v8 kuru koşu + banka sunucusu kurulumu (Hetzner CPX52, Ubuntu 24.04; 1 Ekim 2026).
# Ortam kimliği kilitle aynı olmalı: python 3.12.14; numpy 2.5.1; pandas 3.0.5; cryptography 50.0.0.
# Bağımlılık sürümleri dizüstü venv'iyle birebir (pip freeze).
set -euo pipefail
export DEBIAN_FRONTEND=noninteractive
apt-get update -q
apt-get install -y -q curl ca-certificates tar unzip
if ! command -v uv >/dev/null; then
  curl -LsSf https://astral.sh/uv/install.sh | env UV_INSTALL_DIR=/usr/local/bin sh
fi
mkdir -p /opt/v8
uv python install 3.12.14 --install-dir /opt/v8/python
uv venv /opt/v8/venv --python /opt/v8/python/cpython-3.12.14-*/bin/python3.12
uv pip install --python /opt/v8/venv/bin/python numpy==2.5.1 pandas==3.0.5 python-dateutil==2.9.0.post0 six==1.17.0 \
  tzdata==2026.3 cryptography==50.0.0 cffi==2.0.0 pycparser==3.0
/opt/v8/venv/bin/python -c "import sys, numpy, pandas, cryptography; print('python', sys.version.split()[0] + '; numpy', numpy.__version__ + '; pandas', pandas.__version__ + '; cryptography', cryptography.__version__)"
nproc; free -g | head -2; lscpu | grep -E 'Model name'
