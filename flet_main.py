#!/usr/bin/env python3
"""Punto de entrada para la GUI del laboratorio (Flet).

Uso:
    python flet_main.py                 # abre la ventana Flet (desktop)
    python flet_main.py --web           # sirve en navegador local (demo/aula)
    python flet_main.py --web --port 8888
    python flet_main.py --help          # ayuda (sin abrir ventana)
    python flet_main.py --clean         # limpia artefactos del laboratorio
"""

PUERTO_WEB_DEFECTO = 8550

import os
import subprocess
import sys

_DIR_RAIZ = os.path.dirname(os.path.abspath(__file__))
if _DIR_RAIZ not in sys.path:
    sys.path.insert(0, _DIR_RAIZ)


def ayuda() -> None:
    print(__doc__)


def main(argv: list[str]) -> int:
    if "--help" in argv or "-h" in argv:
        ayuda()
        return 0
    if "--clean" in argv:
        proc = subprocess.run(
            [sys.executable, os.path.join(_DIR_RAIZ, "core", "lab_setup.py"),
             "--clean"],
            cwd=_DIR_RAIZ,
        )
        return proc.returncode
    web = "--web" in argv
    puerto = PUERTO_WEB_DEFECTO
    if "--port" in argv:
        try:
            puerto = int(argv[argv.index("--port") + 1])
        except (IndexError, ValueError):
            print("[ERROR] --port requiere un número (ej: --port 8888)")
            return 2
    from gui_flet.main import lanzar
    lanzar(web=web, puerto=puerto)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
