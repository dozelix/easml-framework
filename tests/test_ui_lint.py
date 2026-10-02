"""Lint de UI: sin colores por defecto (contraste garantizado)."""

import unittest
from importlib.util import find_spec

REQUIERE_FLET = find_spec("flet") is None

_CLAROS = ()


def _lum(hex_color: str) -> float:
    h = str(hex_color).lstrip("#")
    if len(h) != 6:
        return 0.0
    rgb = [int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)]

    def _c(v: float) -> float:
        return v / 12.92 if v <= 0.03928 else ((v + 0.055) / 1.055) ** 2.4

    r, g, b = (_c(v) for v in rgb)
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def _hijos(ctrl):
    import flet as ft
    vistos = []
    for attr in ("controls", "actions"):
        seq = getattr(ctrl, attr, None)
        if isinstance(seq, (list, tuple)):
            vistos.extend([c for c in seq if isinstance(c, ft.Control)])
    for attr in ("content", "title", "leading", "subtitle", "error_content"):
        uno = getattr(ctrl, attr, None)
        if isinstance(uno, ft.Control):
            vistos.append(uno)
    return vistos


def _caminar(raiz):
    pila, vistos = [raiz], []
    while pila:
        ctrl = pila.pop()
        vistos.append(ctrl)
        pila.extend(_hijos(ctrl))
    return vistos


@unittest.skipIf(REQUIERE_FLET, "flet no instalado")
class UiLintTests(unittest.TestCase):
    def _revisar(self, raiz, donde: str):
        import flet as ft
        textos = mds = 0
        for ctrl in _caminar(raiz):
            if isinstance(ctrl, ft.Text):
                textos += 1
                self.assertIsNotNone(
                    ctrl.color, f"{donde}: Text sin color: {ctrl.value!r}")
            if isinstance(ctrl, ft.Markdown):
                mds += 1
                self.assertIsNotNone(
                    ctrl.md_style_sheet, f"{donde}: Markdown sin stylesheet")
            if isinstance(ctrl, ft.Image):
                self.assertIsNotNone(
                    ctrl.error_content, f"{donde}: Image sin error_content")
            if isinstance(ctrl, (ft.AlertDialog,)):
                if ctrl.bgcolor is not None:
                    self.assertLess(
                        _lum(ctrl.bgcolor), 0.35, f"{donde}: diálogo claro")
            if isinstance(ctrl, ft.Container) and ctrl.bgcolor is not None:
                self.assertLess(
                    _lum(ctrl.bgcolor), 0.4,
                    f"{donde}: superficie clara {ctrl.bgcolor}")
        self.assertGreater(textos + mds, 0, f"{donde}: sin textos")

    def test_vistas_con_colores_explicitos(self):
        import gui_flet.views as V
        prog = {"minijefe": {"trojan": {"ok": True, "cien": True}},
                "megajefe": {}, "sombra": ["trojan"], "dlc": True,
                "panteon": {}, "anim": True}
        mundos = {"Confidencialidad": ["keylogger"],
                  "Integridad": ["trojan"],
                  "Disponibilidad": ["wiper"]}
        self._revisar(V.vista_dashboard(), "dashboard")
        self._revisar(V.vista_tutorial(), "tutorial")
        self._revisar(V.vista_modulo(0), "modulo")
        self._revisar(V.vista_guia("# Hola\n\n| a | b |\n|---|---|\n| 1 | 2 |"),
                      "guia")
        self._revisar(V.vista_menu(prog, mundos, "trojan"), "menu")
        self._revisar(V.vista_mapa("Integridad", ["trojan"], prog), "mapa")
        self._revisar(V.vista_jefes(prog, mundos), "jefes")
        self._revisar(V.vista_ajustes(
            prog, {"lab_dir": "x", "logs_dir": "y"}), "ajustes")
        self._revisar(V.vista_portada("trojan", prog), "portada")
        self._revisar(V.vista_combate("trojan", 100, 80, ["hola"], None),
                      "combate")

    def test_dialogo_quiz_oscuro(self):
        import flet as ft

        class Pagina:
            def update(self):
                pass

            def show_dialog(self, *a):
                pass

            def run_task(self, *a):
                pass

        from gui_flet.desafio import construir_dialogo
        dlg = construir_dialogo(Pagina(), "trojan")
        self._revisar(dlg, "quiz")


if __name__ == "__main__":
    unittest.main()
