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


async def _emitir(on_log, msg: str) -> None:
    res = on_log(msg)
    if inspect.isawaitable(res):
        await res


def _es_congelado() -> bool:
    return getattr(sys, "frozen", False)


def _correr_interno(script_path: str) -> tuple[str, int]:
    """Ejecuta un script en-proceso (modo congelado): captura stdout/stderr.

    Retorna (salida, código). Los sys.exit() de los scripts se capturan para
    no matar la GUI: 0/None es éxito, otro código es error.
    """
    import contextlib
    import io
    import runpy

    buf = io.StringIO()
    codigo = 0
    try:
        with contextlib.redirect_stdout(buf), contextlib.redirect_stderr(buf):
            runpy.run_path(script_path, run_name="__main__")
    except SystemExit as e:
        codigo = 0 if e.code in (None, 0) else 1
    except Exception as e:  # noqa: BLE001 - el fallo se reporta como línea
        buf.write(f"[ERROR] interno: {e}\n")
        codigo = 1
    return buf.getvalue(), codigo


async def ejecutar_script(script_path: str, etiqueta: str, on_log) -> None:
    """Ejecuta un script y reporta cada línea vía on_log (callable sync o async).

    on_log también recibe los mensajes de cierre/timeout/error, con el mismo
    formato que app/runner.py para mantener paridad con la GUI tkinter.

    En ejecutable congelado (flet pack) no hay intérprete para relanzar:
    sys.executable es el propio .exe, así que el script corre en-proceso
    vía runpy con salida capturada.
    """
    if _es_congelado():
        try:
            salida, codigo = await asyncio.to_thread(
                _correr_interno, script_path)
        except Exception as e:  # noqa: BLE001 - cualquier fallo a la consola
            await _emitir(on_log, f"[ERROR] {etiqueta}: {e}")
            return
        for linea in lineas_limpias(salida):
            await _emitir(on_log, linea)
        if codigo == 0:
            await _emitir(on_log, f"[OK] {etiqueta} completado.")
        else:
            await _emitir(on_log, f"[ERROR] {etiqueta} terminó con código {codigo}")
        return

    async def _emit(msg: str):
        await _emitir(on_log, msg)

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
