"""Set chibi 128px completo (scripts/generar_chibis.py)."""

import os
import unittest
from importlib.util import find_spec

REQUIERE_PIL = find_spec("PIL") is None

_REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SLUGS = [
    "trojan", "keylogger", "steganography", "backdoor", "dns_tunneling",
    "fileless", "rootkit", "supply_chain", "ransomware", "wiper", "worm",
    "cryptominer", "logic_bomb", "botnet",
]


@unittest.skipIf(REQUIERE_PIL, "pillow no instalado")
class ChibisTests(unittest.TestCase):
    def test_set_completo_y_valido(self):
        from PIL import Image
        for slug in SLUGS:
            for suf in ("", "_sombra"):
                ruta = os.path.join(
                    _REPO_ROOT, "assets", "modulos", f"{slug}{suf}.png")
                self.assertTrue(os.path.isfile(ruta), f"falta {ruta}")
                with Image.open(ruta) as im:
                    self.assertEqual(im.size, (128, 128), ruta)
                    self.assertEqual(im.mode, "RGBA", ruta)
                    colores = im.getcolors(maxcolors=1 << 14)
                    self.assertGreater(len(colores or []), 5, ruta)


if __name__ == "__main__":
    unittest.main()
