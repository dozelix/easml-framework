#!/usr/bin/env python3
"""Fondo de la pantalla título (v1.0.0.0-alpha).

Grilla en perspectiva sobre negro puro + horizonte con glow + viñeta central
(la viñeta deja el centro oscuro para que el menú mantenga contraste).
Arte 100% original, sin referencias externas.

Uso manual: `python scripts/generar_fondo.py` (requiere pillow).
El PNG resultante sí se versiona.
"""

import math
import os
import sys

try:
    from PIL import Image, ImageDraw
except ImportError:
    sys.exit("requiere pillow: pip install pillow")

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEST = os.path.join(RAIZ, "assets", "portada_fondo.png")

W, H = 1280, 800
NEGRO = (5, 7, 12)
CIAN = (0, 229, 255)
HORIZONTE_Y = 300


def main() -> None:
    img = Image.new("RGB", (W, H), NEGRO)
    d = ImageDraw.Draw(img, "RGBA")

    # resplandor del horizonte (bandas decrecientes)
    for i in range(60, 0, -1):
        alfa = int(90 * (1 - i / 60) ** 2)
        d.line([(0, HORIZONTE_Y - i), (W, HORIZONTE_Y - i)],
               fill=CIAN + (alfa,))
        d.line([(0, HORIZONTE_Y + i), (W, HORIZONTE_Y + i)],
               fill=CIAN + (alfa // 3,))

    # líneas horizontales con fuga hacia el horizonte
    for k in range(1, 14):
        t = (k / 14) ** 2.2
        y = int(HORIZONTE_Y + t * (H - HORIZONTE_Y))
        alfa = int(40 + 120 * t)
        d.line([(0, y), (W, y)], fill=CIAN + (alfa,), width=1)

    # verticales en fuga desde un punto central
    for i in range(-16, 17):
        x_base = W // 2 + i * 46
        d.line([(x_base, H), (W // 2 + i * 14, HORIZONTE_Y)],
               fill=CIAN + (70,), width=1)

    # nodos (intersecciones encendidas, pocas para no saturar)
    for i in range(-8, 9, 2):
        for k in (3, 6, 9, 12):
            t = (k / 14) ** 2.2
            y = int(HORIZONTE_Y + t * (H - HORIZONTE_Y))
            x = int(W // 2 + i * (14 + t * 90))
            r = 2 if k < 9 else 3
            d.ellipse([x - r, y - r, x + r, y + r], fill=CIAN + (200,))

    # viñeta: oscurece bordes y aclara el centro del menú
    vineta = Image.new("L", (W, H), 0)
    vd = ImageDraw.Draw(vineta)
    for r in range(620, 0, -4):
        sombra = int(150 * (1 - r / 620) ** 1.6)
        vd.ellipse([W // 2 - r, H // 2 - r * 0.62,
                    W // 2 + r, H // 2 + r * 0.62], fill=sombra)
    negro = Image.new("RGB", (W, H), NEGRO)
    img = Image.composite(img, negro, vineta)

    # sol partido en el horizonte (marca de la red, original)
    for r in range(70, 0, -2):
        alfa = int(60 * (1 - r / 70))
        d = ImageDraw.Draw(img, "RGBA")
        d.ellipse([W // 2 - r, HORIZONTE_Y - r, W // 2 + r, HORIZONTE_Y + r],
                  outline=CIAN + (alfa,), width=2)
    img.save(DEST)
    print(f"[OK] {DEST} ({os.path.getsize(DEST) // 1024} KB)")


if __name__ == "__main__":
    main()
