"""Ejecución asíncrona de scripts para la GUI."""

import os
import subprocess
import sys
import threading

from modulos.common.utils import strip_ansi

_DIR_RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class ScriptRunner:
    """Ejecuta scripts del laboratorio en un hilo separado."""

    def __init__(self, on_log=None, on_done=None, on_error=None):
        self.on_log = on_log
        self.on_done = on_done
        self.on_error = on_error
        self.ejecutando = False

    def ejecutar(self, script_path: str, etiqueta: str = ""):
        if self.ejecutando:
            return
        self.ejecutando = True

        def _hilo():
            try:
                proc = subprocess.run(
                    [sys.executable, script_path],
                    capture_output=True, text=True, cwd=_DIR_RAIZ, timeout=120
                )
                if self.on_done:
                    self.on_done(proc.stdout + proc.stderr, etiqueta)
            except subprocess.TimeoutExpired:
                if self.on_error:
                    self.on_error(f"⏱️ Timeout en {etiqueta} (120s)")
            except Exception as e:
                if self.on_error:
                    self.on_error(f"❌ Error: {e}")
            finally:
                self.ejecutando = False

        threading.Thread(target=_hilo, daemon=True).start()

    def procesar_salida(self, salida: str, etiqueta: str):
        if not self.on_log:
            return
        limpia = strip_ansi(salida)
        for linea in limpia.strip().split("\n"):
            if linea.strip():
                self.on_log(linea)
        self.on_log(f"✅ {etiqueta} completado.")
