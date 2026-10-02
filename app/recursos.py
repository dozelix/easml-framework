"""Autodiagnóstico silencioso de recursos empaquetados (dev y .bin).

Verifica que los 14×3 archivos de módulo + iconos + fondo existan en
base_recursos() (raíz en dev, _MEIPASS en ejecutable congelado).
La GUI lo corre al arrancar: si todo OK no muestra nada; si falta algo,
avis badge en portada + línea en consola. Sin jerga de archivos en fichas.
"""

import os
import sys

_DIR_RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _DIR_RAIZ not in sys.path:
    sys.path.insert(0, _DIR_RAIZ)

from app.config import MODULOS, defensa_arch  # noqa: E402
from modulos.common.paths import base_recursos  # noqa: E402


def verificar() -> list[str]:
    """Retorna la lista de recursos faltantes (vacía = todo OK)."""
    base = base_recursos()
    faltan = []
    for _num, nombre, script, _cia, _cis, _url in MODULOS:
        for rel in (os.path.join("modulos", nombre, f"{script}.py"),
                    os.path.join("modulos", nombre, defensa_arch(nombre)),
                    os.path.join("modulos", nombre, "README.md"),
                    os.path.join("assets", "modulos", f"{nombre}.png")):
            if not os.path.isfile(os.path.join(base, rel)):
                faltan.append(rel)
    for rel in (os.path.join("assets", "portada_fondo.png"),):
        if not os.path.isfile(os.path.join(base, rel)):
            faltan.append(rel)
    return faltan
