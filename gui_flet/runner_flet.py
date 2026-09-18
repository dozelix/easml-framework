"""Ejecución asíncrona de scripts para la GUI Flet.

Equivalente asyncio de app/runner.py: el trabajo bloqueante (subprocess)
corre en un hilo vía asyncio.to_thread para no congelar la UI.
Sin dependencia de flet: el callback on_log lo inyecta la vista.
"""

import asyncio
import inspect
import os
import subprocess
import sys

_DIR_RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _DIR_RAIZ not in sys.path:
    sys.path.insert(0, _DIR_RAIZ)

from modulos.common.utils import strip_ansi  # noqa: E402

TIMEOUT_SEGUNDOS = 120


def lineas_limpias(salida: str) -> list[str]:
    """Normaliza la salida de un script: sin ANSI, sin líneas vacías."""
    limpia = strip_ansi(salida)
    return [linea for linea in (l.strip() for l in limpia.strip().split("\n")) if linea]


async def ejecutar_script(script_path: str, etiqueta: str, on_log) -> None:
    """Ejecuta un script y reporta cada línea vía on_log (callable sync o async).

    on_log también recibe los mensajes de cierre/timeout/error, con el mismo
    formato que app/runner.py para mantener paridad con la GUI tkinter.
    """
    async def _emit(msg: str):
        res = on_log(msg)
        if inspect.isawaitable(res):
            await res

    def _correr():
        return subprocess.run(
            [sys.executable, script_path],
            capture_output=True, text=True, cwd=_DIR_RAIZ, timeout=TIMEOUT_SEGUNDOS,
        )

    try:
        proc = await asyncio.to_thread(_correr)
    except subprocess.TimeoutExpired:
        await _emit(f"[TIMEOUT] {etiqueta} superó {TIMEOUT_SEGUNDOS}s")
        return
    except Exception as e:  # noqa: BLE001 - cualquier fallo debe llegar a la consola
        await _emit(f"[ERROR] {etiqueta}: {e}")
        return
    for linea in lineas_limpias(proc.stdout + proc.stderr):
        await _emit(linea)
    await _emit(f"[OK] {etiqueta} completado.")
