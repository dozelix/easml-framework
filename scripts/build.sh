#!/usr/bin/env bash
# Empaqueta la GUI Flet en binario local (reproducible).
# Canónico: workflow release.yml (CI). Esto es solo para probar en tu máquina.
# Requiere: Python 3.10+, pip, ~2GB libres (Flutter SDK + PyInstaller).
set -euo pipefail
cd "$(dirname "$0")/.."

pip install -r requirements.txt pyinstaller
flet pack flet_main.py -n EASML \
  --product-name EASML \
  --add-data "assets:assets" \
  --add-data "modulos:modulos" \
  --add-data "core:core" \
  --distpath dist

echo ""
echo "[OK] Salida en dist/. En Linux/macOS empaquetá a mano:"
echo "  tar -czf easml-linux.tar.gz -C dist ."
