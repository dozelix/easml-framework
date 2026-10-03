#!/usr/bin/env python3
"""Arenas de combate + héroe (v1.0.0.0-alpha).

4 fondos 960x540 (garaje tutorial + 1 por mundo CIA, cada uno con su neón)
y el chibi del héroe analista. Arte 100% original, mismo pipeline PIL.

Uso manual: `python scripts/generar_arena.py` (requiere pillow).
Los PNG resultantes sí se versionan.
"""

import os
import sys

try:
    from PIL import Image, ImageDraw
except ImportError:
    sys.exit("requiere pillow: pip install pillow")

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(RAIZ, "scripts"))
from generar_chibis import CABEZA, CUERPO_OSCURO, LINEA  # noqa: E402

DEST = os.path.join(RAIZ, "assets", "arenas")
W, H = 960, 540

ARENAS = {
    # nombre: (negro base, neón, suelo)
    "garaje": ((8, 9, 12), (255, 180, 84, 255)),
    "confidencialidad": ((5, 10, 16), (0, 229, 255, 255)),
    "integridad": ((12, 8, 18), (187, 154, 247, 255)),
    "disponibilidad": ((16, 9, 8), (255, 158, 100, 255)),
}


def fondo(nombre: str, negro: tuple, neon: tuple) -> None:
    img = Image.new("RGB", (W, H), negro)
    d = ImageDraw.Draw(img, "RGBA")
    hy = 330
    for i in range(40, 0, -1):
        alfa = int(70 * (1 - i / 40) ** 2)
        d.line([(0, hy - i), (W, hy - i)], fill=neon[:3] + (alfa,))
    for k in range(1, 10):
        t = (k / 10) ** 2
        y = int(hy + t * (H - hy))
        d.line([(0, y), (W, y)], fill=neon[:3] + (int(40 + 90 * t),), width=1)
    for i in range(-12, 13):
        d.line([(W // 2 + i * 52, H), (W // 2 + i * 16, hy)],
               fill=neon[:3] + (60,), width=1)
    # plataformas de combate (elipses)
    d.ellipse([90, 400, 350, 470], outline=neon[:3] + (160,), width=3)
    d.ellipse([610, 180, 870, 250], outline=neon[:3] + (160,), width=3)
    img.save(os.path.join(DEST, f"{nombre}.png"))


def heroe() -> None:
    img = Image.new("RGBA", (128, 128), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    dorado = (255, 180, 84, 255)
    d.rounded_rectangle([44, 82, 84, 112], radius=8, fill=CUERPO_OSCURO,
                        outline=LINEA, width=4)
    d.line([52, 96, 76, 96], fill=dorado, width=4)
    d.rounded_rectangle([34, 30, 94, 84], radius=16, fill=CABEZA,
                        outline=LINEA, width=4)
    d.rounded_rectangle([42, 50, 86, 70], radius=8, fill=(10, 12, 16, 255),
                        outline=LINEA, width=3)
    d.ellipse([52, 56, 60, 64], fill=dorado)
    d.ellipse([68, 56, 76, 64], fill=dorado)
    # visera de analista (banda superior)
    d.rounded_rectangle([34, 30, 94, 46], radius=8, fill=dorado,
                        outline=LINEA, width=3)
    img.save(os.path.join(RAIZ, "assets", "heroe.png"))


def main() -> None:
    os.makedirs(DEST, exist_ok=True)
    for nombre, (negro, neon) in ARENAS.items():
        fondo(nombre, negro, neon)
        print(f"  [+] arenas/{nombre}.png")
    heroe()
    print("  [+] heroe.png")


if __name__ == "__main__":
    main()
