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
TEXTO_DIM = "#A7B0BC"
TEXTO_CONSOLA = "#9ECE6A"
ACCENT = "#00E5FF"
BORDE = "#3A4156"

# Tarjeta sobre arte de fondo (portada): mismo panel con 85% opacidad.
BG_TARJETA = "#D91A1D27"

ROJO = "#FF2A6D"
AZUL = "#00E5FF"
VERDE = "#9ECE6A"
AMARILLO = "#FFB454"
CYAN = "#00E5FF"
MORADO = "#BB9AF7"
NARANJA = "#FF9E64"

TEXTO_SOBRE_NEON = "#0D0F14"

# Tamaños mínimos (accesibilidad: cuerpo nunca bajo 12).
TAM_TITULO = 20
TAM_CUERPO = 13
TAM_MINIMO = 12

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


def fondo_portada() -> str:
    """Arte de la pantalla título dentro de assets/."""
    return "portada_fondo.png"


def borde_neon(color: str):
    """Borde fino luminoso para tarjetas (importa flet solo aquí)."""
    import flet as ft
    return ft.Border.all(1, color)


def brillo(color: str, activado: bool = True):
    """Glow neón (un solo BoxShadow por pantalla). Off si anim=false."""
    import flet as ft
    if not activado:
        return None
    return ft.BoxShadow(color=color, blur_radius=18, spread_radius=1)
