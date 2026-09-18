"""Tests de la GUI Flet (gui_flet/) y su entrypoint flet_main.py.

Los tests que importan flet se omiten si flet no está instalado
(entornos mínimos); en CI siempre corre con requirements.txt completo.
Ningún test abre ventanas: todo es headless.
"""

import asyncio
import os
import subprocess
import sys
import unittest
from importlib.util import find_spec

_REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

REQUIERE_FLET = find_spec("flet") is None


class TestFletMain(unittest.TestCase):
    """flet_main.py --help/--clean no requieren flet instalado."""

    def _run(self, *args, timeout=60):
        return subprocess.run(
            [sys.executable, os.path.join(_REPO_ROOT, "flet_main.py"), *args],
            capture_output=True, text=True, timeout=timeout, cwd=_REPO_ROOT,
        )

    def test_help(self):
        result = self._run("--help")
        self.assertEqual(result.returncode, 0, f"stderr:\n{result.stderr}")

    def test_clean(self):
        result = self._run("--clean")
        self.assertEqual(result.returncode, 0, f"stderr:\n{result.stderr}")


class TestRunnerSinFlet(unittest.TestCase):
    """runner_flet no depende de flet: corre en cualquier entorno."""

    def test_lineas_limpias(self):
        from gui_flet.runner_flet import lineas_limpias
        self.assertEqual(
            lineas_limpias("\x1b[32m hola \x1b[0m\n\n  mundo\n"),
            ["hola", "mundo"],
        )

    def test_ejecutar_script_acepta_callback_sync(self):
        from gui_flet.runner_flet import ejecutar_script
        msgs = []
        asyncio.run(ejecutar_script(
            os.path.join(_REPO_ROOT, "core", "lab_setup.py"),
            "Setup", msgs.append))
        self.assertTrue(msgs, "sin mensajes del runner")
        self.assertTrue(msgs[-1].endswith("completado."),
                        f"último mensaje inesperado: {msgs[-1]!r}")
        subprocess.run(
            [sys.executable, os.path.join(_REPO_ROOT, "core", "lab_setup.py"),
             "--clean"],
            capture_output=True, timeout=60, cwd=_REPO_ROOT,
        )


@unittest.skipIf(REQUIERE_FLET, "flet no instalado")
class TestTema(unittest.TestCase):
    def test_iconos(self):
        from gui_flet import theme as T
        self.assertEqual(T.icono_modulo("ransomware"), "modulos/ransomware.png")
        self.assertEqual(T.icono_cia("Integridad"), "cia_integridad.png")
        for color in (T.BG, T.BG_CARD, T.ROJO, T.AZUL, T.VERDE, T.AMARILLO,
                      T.MORADO, T.NARANJA, T.CYAN):
            self.assertTrue(color.startswith("#"), color)


@unittest.skipIf(REQUIERE_FLET, "flet no instalado")
class TestVistas(unittest.TestCase):
    def test_dashboard_tutorial_modulo(self):
        from gui_flet import views as V
        self.assertIsNotNone(V.vista_dashboard())
        self.assertIsNotNone(V.vista_tutorial())
        self.assertIsNotNone(V.vista_modulo(0))
        guia = V.vista_guia("# Hola")
        self.assertIsNotNone(guia)
        # Regresión: la guía debe desplazarse (Column con scroll propio).
        # Sin esto el Markdown desborda y la botonera lo pisa.
        self.assertIsNotNone(getattr(guia, "scroll", None))
        md = V.leer_readme_modulo(0)
        self.assertTrue(md and len(md) > 100)
        self.assertIsNone(V.leer_readme_modulo(999))


@unittest.skipIf(REQUIERE_FLET, "flet no instalado")
class TestLayout(unittest.TestCase):
    def test_main_construye_layout(self):
        from gui_flet.main import main

        class Ventana:
            pass

        class PaginaSimulada:
            """Stub mínimo de ft.Page SIN update_async a propósito.

            Si main() usa API inexistente en el Flet instalado
            (ej: page.update_async(), eliminado en 1.0), este test rompe
            con AttributeError en vez de llegar roto a la ventana real.
            """

            def __init__(self):
                self.window = Ventana()
                self.title = ""
                self.added = []

            def add(self, *controles):
                self.added.extend(controles)

            def update(self):
                pass

            def run_task(self, *args):
                pass

            def show_dialog(self, *args):
                pass

        async def _correr():
            pagina = PaginaSimulada()
            await main(pagina)
            return pagina

        pagina = asyncio.run(_correr())
        self.assertTrue(pagina.title)
        self.assertEqual(len(pagina.added), 1)
        fila = pagina.added[0].content
        self.assertEqual(len(fila.controls), 3)  # sidebar | div | central
        central = fila.controls[2]
        self.assertEqual(len(central.controls), 5)  # header+contenido+etc.
        tiles = fila.controls[0].content.controls[3].controls
        self.assertEqual(len(tiles), 14)


@unittest.skipIf(REQUIERE_FLET, "flet no instalado")
class TestQuiz(unittest.TestCase):
    def test_flujo_completo(self):
        from gui_flet.desafio import ControladorQuiz
        ctrl = ControladorQuiz("ransomware")
        self.assertTrue(ctrl.desafios)
        ctrl.iniciar("facil")
        primera = ctrl.pregunta_actual()
        self.assertIsNotNone(primera)
        assert primera is not None
        res = ctrl.responder(primera.respuesta_correcta)
        self.assertIsNotNone(res)
        assert res is not None
        correcto, _mensaje = res
        self.assertTrue(correcto)
        while ctrl.avanzar():
            d = ctrl.pregunta_actual()
            self.assertIsNotNone(d)
            assert d is not None
            ctrl.responder(d.respuesta_correcta)
        datos = ctrl.finalizar()
        self.assertEqual(datos["correctas"], datos["total"])
        self.assertTrue(datos["aprobado"])

    def test_modulo_sin_desafios(self):
        from gui_flet.desafio import ControladorQuiz
        ctrl = ControladorQuiz("modulo_inexistente")
        self.assertEqual(ctrl.desafios, [])
        self.assertIsNone(ctrl.pregunta_actual())
        self.assertIsNone(ctrl.responder(0))


if __name__ == "__main__":
    unittest.main()
