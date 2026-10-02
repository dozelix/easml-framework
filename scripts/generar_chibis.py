#!/usr/bin/env python3
"""Genera los chibis de la Red Neón (v1.0.0.0-alpha).

Set cohesivo 128x128 por módulo: base chibi común + material de era punk
(oxido/cinta/neón/nube) + accesorio distintivo por bicho + rim neón.
Recién horneado: `python scripts/generar_chibis.py` (requiere pillow, uso
manual; los PNG resultantes sí se versionan).

Variante `*_sombra.png`: versión oscura para JEFES (bicho reclutado).
"""

import os
import sys

try:
    from PIL import Image, ImageDraw
except ImportError:
    sys.exit("requiere pillow: pip install pillow")

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEST = os.path.join(RAIZ, "assets", "modulos")

TAM = 128
LINEA = (13, 15, 20, 255)        # borde neobrutalista
CABEZA = (201, 209, 217, 255)    # chapa clara
CUERPO_OSCURO = (26, 29, 39, 255)

ERA = {
    # fondo del medallón, rim neón, detalle
    "oxido": ((46, 34, 22, 255), (255, 180, 84, 255), (176, 122, 59, 255)),
    "cinta": ((10, 26, 18, 255), (158, 206, 106, 255), (60, 120, 70, 255)),
    "neon": ((14, 20, 34, 255), (0, 229, 255, 255), (70, 110, 160, 255)),
    "nube": ((24, 14, 34, 255), (187, 154, 247, 255), (110, 80, 150, 255)),
}

MUNDO = {
    "Confidencialidad": (0, 229, 255, 255),
    "Integridad": (187, 154, 247, 255),
    "Disponibilidad": (255, 158, 100, 255),
}

# slug -> (mundo, era)
FICHA = {
    "trojan": ("Integridad", "oxido"),
    "keylogger": ("Confidencialidad", "cinta"),
    "steganography": ("Confidencialidad", "neon"),
    "backdoor": ("Confidencialidad", "oxido"),
    "dns_tunneling": ("Confidencialidad", "nube"),
    "fileless": ("Integridad", "nube"),
    "rootkit": ("Integridad", "cinta"),
    "supply_chain": ("Integridad", "nube"),
    "ransomware": ("Disponibilidad", "neon"),
    "wiper": ("Disponibilidad", "cinta"),
    "worm": ("Disponibilidad", "oxido"),
    "cryptominer": ("Disponibilidad", "nube"),
    "logic_bomb": ("Disponibilidad", "oxido"),
    "botnet": ("Disponibilidad", "neon"),
}


def base(mundo: str, era: str) -> tuple[Image.Image, ImageDraw.ImageDraw]:
    fondo, rim, _det = ERA[era]
    img = Image.new("RGBA", (TAM, TAM), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.rounded_rectangle([6, 6, TAM - 7, TAM - 7], radius=26, fill=fondo,
                        outline=rim, width=4)
    return img, d


def chibi(d: ImageDraw.ImageDraw, mundo: str, era: str) -> None:
    """Cuerpo chibi común: cabezón + visor + ojos neón + torso."""
    _fondo, rim, _det = ERA[era]
    mundo_c = MUNDO[mundo]
    # torso
    d.rounded_rectangle([44, 82, 84, 112], radius=8, fill=CUERPO_OSCURO,
                        outline=LINEA, width=4)
    d.line([52, 96, 76, 96], fill=mundo_c, width=4)  # núcleo mundo
    # cabeza
    d.rounded_rectangle([34, 30, 94, 84], radius=16, fill=CABEZA,
                        outline=LINEA, width=4)
    # visor
    d.rounded_rectangle([42, 50, 86, 70], radius=8, fill=(10, 12, 16, 255),
                        outline=LINEA, width=3)
    d.ellipse([52, 56, 60, 64], fill=rim)
    d.ellipse([68, 56, 76, 64], fill=rim)
    # antena
    d.line([64, 30, 64, 20], fill=LINEA, width=4)
    d.ellipse([59, 15, 69, 25], fill=mundo_c, outline=LINEA, width=2)


def acc_trojan(d, rim, det):
    d.polygon([(34, 44), (20, 26), (30, 48)], fill=det, outline=LINEA)  # casco
    d.polygon([(94, 44), (108, 26), (98, 48)], fill=det, outline=LINEA)
    d.rectangle([58, 82, 70, 96], fill=rim)  # morro


def acc_keylogger(d, rim, det):
    for x in (30, 98):
        d.ellipse([x - 8, 46, x + 8, 62], fill=CABEZA, outline=LINEA, width=3)
        d.ellipse([x - 3, 51, x + 3, 57], fill=rim)  # ojos extra
    for i in range(3):  # dedos largos
        d.line([50 + i * 14, 112, 50 + i * 14, 120], fill=det, width=4)


def acc_steganography(d, rim, det):
    d.polygon([(64, 84), (40, 114), (88, 114)], fill=det, outline=LINEA)  # capa ninja
    d.line([64, 92, 64, 106], fill=rim, width=3)


def acc_backdoor(d, rim, det):
    d.rounded_rectangle([88, 60, 110, 100], radius=6, fill=det, outline=LINEA, width=3)
    d.ellipse([94, 68, 104, 78], fill=LINEA)  # ojo cerradura
    d.polygon([(99, 78), (95, 92), (103, 92)], fill=rim)


def acc_dns_tunneling(d, rim, det):
    for i, y in enumerate((92, 100, 108)):
        d.arc([30, y - 14, 98, y + 14], start=200, end=340, fill=rim, width=3)
        d.ellipse([92, y - 3, 98, y + 3], fill=det, outline=LINEA)


def acc_fileless(d, rim, det):
    for y in (88, 96, 104):  # estelas de humo
        d.ellipse([44, y - 5, 84, y + 5], outline=rim, width=2)
    d.ellipse([58, 52, 70, 64], fill=rim)  # tercer ojo


def acc_rootkit(d, rim, det):
    d.ellipse([36, 82, 92, 118], outline=det, width=5)  # anillo RING0
    d.ellipse([58, 96, 70, 108], fill=rim, outline=LINEA)


def acc_supply_chain(d, rim, det):
    for x in (36, 56, 76):
        d.rounded_rectangle([x, 88, x + 16, 104], radius=6, fill=det,
                            outline=LINEA, width=3)
    d.line([52, 96, 56, 96], fill=rim, width=3)
    d.line([72, 96, 76, 96], fill=(255, 42, 109, 255), width=3)  # eslabón podrido


def acc_ransomware(d, rim, det):
    d.rounded_rectangle([86, 66, 110, 98], radius=4, fill=det, outline=LINEA, width=3)
    d.arc([88, 54, 108, 74], start=180, end=0, fill=rim, width=4)  # candado
    d.ellipse([95, 78, 101, 84], fill=LINEA)


def acc_wiper(d, rim, det):
    d.line([36, 88, 60, 112], fill=(255, 42, 109, 255), width=6)  # tachón
    d.line([60, 88, 36, 112], fill=(255, 42, 109, 255), width=6)
    d.rectangle([70, 90, 92, 110], fill=det, outline=LINEA, width=3)  # disco roto


def acc_worm(d, rim, det):
    for i, (x0, x1) in enumerate(((24, 44), (40, 60))):
        d.ellipse([x0, 88 - i * 6, x1, 106 - i * 6], fill=det, outline=LINEA, width=3)
    d.ellipse([58, 74, 70, 86], fill=rim, outline=LINEA)  # cabeza gusano


def acc_cryptominer(d, rim, det):
    d.line([30, 110, 52, 88], fill=det, width=5)  # pico
    d.line([52, 88, 66, 94], fill=rim, width=4)
    d.polygon([(84, 88), (92, 100), (76, 100)], fill=rim, outline=LINEA)  # gema


def acc_logic_bomb(d, rim, det):
    d.ellipse([84, 26, 112, 54], fill=CABEZA, outline=LINEA, width=3)  # reloj
    d.line([98, 40, 98, 48], fill=rim, width=3)
    d.line([98, 40, 104, 44], fill=rim, width=3)
    d.line([64, 20, 84, 30], fill=det, width=4)  # mecha


def acc_botnet(d, rim, det):
    for x, y in ((28, 30), (100, 30), (28, 100), (100, 100)):
        d.ellipse([x - 6, y - 6, x + 6, y + 6], fill=det, outline=LINEA, width=2)
        d.line([x, y, 64, 64], fill=rim, width=2)  # hilos al C2
    d.ellipse([58, 58, 70, 70], fill=rim, outline=LINEA)  # C2


ACCESORIOS = {
    "trojan": acc_trojan, "keylogger": acc_keylogger,
    "steganography": acc_steganography, "backdoor": acc_backdoor,
    "dns_tunneling": acc_dns_tunneling, "fileless": acc_fileless,
    "rootkit": acc_rootkit, "supply_chain": acc_supply_chain,
    "ransomware": acc_ransomware, "wiper": acc_wiper, "worm": acc_worm,
    "cryptominer": acc_cryptominer, "logic_bomb": acc_logic_bomb,
    "botnet": acc_botnet,
}


def sombra(img: Image.Image) -> Image.Image:
    """Variante oscura (sombra reclutada): conserva alfa, tiñe violeta."""
    r, g, b, a = img.split()
    gris = Image.merge("RGB", (r, g, b)).convert("L")
    tinte = Image.new("RGB", img.size, (187, 154, 247))
    negro = Image.new("RGB", img.size, (13, 15, 20))
    mezclado = Image.composite(tinte, negro, gris)
    mezclado.putalpha(a)
    return mezclado


def main() -> None:
    os.makedirs(DEST, exist_ok=True)
    for slug, (mundo, era) in FICHA.items():
        img, d = base(mundo, era)
        chibi(d, mundo, era)
        _fondo, rim, det = ERA[era]
        ACCESORIOS[slug](d, rim, det)
        img.save(os.path.join(DEST, f"{slug}.png"))
        sombra(img).save(os.path.join(DEST, f"{slug}_sombra.png"))
        print(f"  [+] {slug}.png + {slug}_sombra.png")
    print(f"\n[OK] 14 chibis en {DEST}")


if __name__ == "__main__":
    main()
