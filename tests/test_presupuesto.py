"""Gates de proyecto: performance, assets y contraste AA (métricas globales)."""

import os
import time
import unittest
from importlib.util import find_spec

_REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REQUIERE_FLET = find_spec("flet") is None


def _lum(hex_color: str) -> float:
    h = hex_color.lstrip("#")
    rgb = [int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)]

    def _c(v: float) -> float:
        return v / 12.92 if v <= 0.03928 else ((v + 0.055) / 1.055) ** 2.4

    r, g, b = (_c(v) for v in rgb)
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def _ratio(a: str, b: str) -> float:
    la, lb = _lum(a), _lum(b)
    return (max(la, lb) + 0.05) / (min(la, lb) + 0.05)


@unittest.skipIf(REQUIERE_FLET, "flet no instalado")
class MetricasTests(unittest.TestCase):
    def test_vistas_rapidas(self):
        import gui_flet.views as V
        prog = {"minijefe": {}, "sombra": [], "dlc": False,
                "megajefe": {}, "panteon": {}, "anim": True}
        for nombre, args in [
            ("progreso", ()),
            ("menu", (prog, {"Confidencialidad": ["keylogger"]}, "keylogger")),
            ("tutorial", ()),
            ("mapa", ("Confidencialidad", ["keylogger"], prog)),
            ("jefes", (prog, {"Confidencialidad": ["keylogger"]})),
            ("avalancha", (prog, {"Confidencialidad": ["keylogger"]})),
            ("ajustes", (prog,)),
            ("datos", ({"lab_dir": "x", "logs_dir": "y"}, "0 KB")),
            ("portada", ("trojan",)),
            ("guia", ("# Hola",)),
        ]:
            ini = time.time()
            getattr(V, f"vista_{nombre}")(*args)
            self.assertLess(time.time() - ini, 1.0, f"vista_{nombre} lenta")

    def test_contraste_aa(self):
        from gui_flet import theme as T
        pares_texto = [
            (T.TEXTO, T.BG), (T.TEXTO, T.BG_CARD), (T.TEXTO, T.BG_PANEL),
            (T.TEXTO_DIM, T.BG_CARD), (T.TEXTO_DIM, T.BG_PANEL),
            (T.TEXTO_CONSOLA, T.BG_CONSOLA),
            (T.TEXTO_SOBRE_NEON, T.ACCENT),
        ]
        for frente, fondo in pares_texto:
            self.assertGreaterEqual(
                _ratio(frente, fondo), 4.5, f"{frente} sobre {fondo}")

    def test_assets_acotados(self):
        total = 0
        for base, _dirs, fich in os.walk(os.path.join(_REPO_ROOT, "assets")):
            for f in fich:
                total += os.path.getsize(os.path.join(base, f))
        self.assertLess(total, 2 * 1024 * 1024, f"assets {total}B > 2MB")
        fondo = os.path.join(_REPO_ROOT, "assets", "portada_fondo.png")
        self.assertTrue(os.path.isfile(fondo))
        self.assertLess(os.path.getsize(fondo), 500 * 1024)


if __name__ == "__main__":
    unittest.main()
