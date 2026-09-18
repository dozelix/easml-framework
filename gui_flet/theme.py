"""Paleta y constantes visuales de la GUI Flet.

Paridad intencional con gui/styles.py (mismos hex) para que la migración
tkinter → Flet no cambie la identidad neobrutalista. Sin dependencias.
"""

BG = "#FFF8F0"
BG_CARD = "#F2ECE4"
BG_PANEL = "#FFFFFF"
BG_HOVER = "#E8E0D6"
BG_CONSOLA = "#1A1A1A"
TEXTO = "#1A1A1A"
TEXTO_DIM = "#5C5C5C"
TEXTO_CONSOLA = "#9ECE6A"
ACCENT = "#2563EB"
BORDE = "#1A1A1A"

ROJO = "#D6394A"
AZUL = "#2563EB"
VERDE = "#16A34A"
AMARILLO = "#D97706"
CYAN = "#0891B2"
MORADO = "#7C3AED"
NARANJA = "#EA580C"

FUENTE = "JetBrains Mono"

COLOR_CIA = {
    "Confidencialidad": CYAN,
    "Integridad": MORADO,
    "Disponibilidad": NARANJA,
}


def icono_modulo(nombre: str) -> str:
    """Ruta del icono dentro de assets/ (ft.run usa assets_dir='assets')."""
    return f"modulos/{nombre}.png"


def icono_cia(cia: str) -> str:
    return f"cia_{cia.lower()}.png"
