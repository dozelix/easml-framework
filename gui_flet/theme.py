"""Paleta y constantes visuales de la GUI Flet.

Tema único `red_neon` (oscuro): grilla + neón sobre negro, inspirado en
estética de red cyberpunk genérica. Sin variantes claro/oscuro ni assets
externos: todo el contraste se valida sobre fondo oscuro.

Nombres de constantes estables para no romper vistas ni tests.
"""

BG = "#0D0F14"
BG_CARD = "#232839"
BG_PANEL = "#1A1D27"
BG_HOVER = "#2B3245"
BG_CONSOLA = "#0A0C10"
TEXTO = "#E6EDF3"
TEXTO_DIM = "#8B949E"
TEXTO_CONSOLA = "#9ECE6A"
ACCENT = "#00E5FF"
BORDE = "#3A4156"

ROJO = "#FF2A6D"
AZUL = "#00E5FF"
VERDE = "#9ECE6A"
AMARILLO = "#FFB454"
CYAN = "#00E5FF"
MORADO = "#BB9AF7"
NARANJA = "#FF9E64"

TEXTO_SOBRE_NEON = "#0D0F14"

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
