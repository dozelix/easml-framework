import tkinter as tk
from tkinter import ttk

BG = "#FFF8F0"
BG_PANEL = "#FFFFFF"
BG_HOVER = "#F0EBE3"
BG_ACTIVO = "#2563EB"
TEXTO = "#1A1A1A"
TEXTO_DIM = "#5C5C5C"
TEXTO_MUTED = "#9C9C9C"
ACCENT = "#2563EB"
BORDE = "#1A1A1A"

ROJO = "#D6394A"
AZUL = "#2563EB"
VERDE = "#16A34A"
AMARILLO = "#D97706"
CYAN = "#0891B2"
MORADO = "#7C3AED"
NARANJA = "#EA580C"

FUENTE = ("JetBrains Mono", 10)
FUENTE_BOLD = ("JetBrains Mono", 10, "bold")
FUENTE_SM = ("JetBrains Mono", 9)
FUENTE_LG = ("JetBrains Mono", 12, "bold")
FUENTE_H1 = ("JetBrains Mono", 16, "bold")
FUENTE_H2 = ("JetBrains Mono", 13, "bold")
FUENTE_STAT = ("JetBrains Mono", 28, "bold")


def configurar_estilos():
    estilo = ttk.Style()
    estilo.theme_use("clam")

    estilo.configure("TFrame", background=BG)
    estilo.configure("Panel.TFrame", background=BG_PANEL, relief="solid", borderwidth=2)
    estilo.configure("TLabel", background=BG, foreground=TEXTO, font=FUENTE)
    estilo.configure("Titulo.TLabel", background=BG_PANEL, foreground=ACCENT,
                     font=FUENTE_BOLD)
    estilo.configure("Dim.TLabel", background=BG, foreground=TEXTO_DIM, font=FUENTE_SM)

    estilo.configure("Treeview", background=BG_PANEL, foreground=TEXTO,
                     font=FUENTE, rowheight=30, fieldbackground=BG_PANEL)
    estilo.configure("Treeview.Heading", background=BG_HOVER, foreground=ACCENT,
                     font=FUENTE_BOLD)
    estilo.map("Treeview", background=[("selected", BG_ACTIVO)],
               foreground=[("selected", "#FFFFFF")])

    estilo.configure("Accion.TButton", background=BG_PANEL, foreground=TEXTO,
                     font=FUENTE_BOLD, padding=(14, 10), relief="solid", borderwidth=2)
    estilo.map("Accion.TButton",
               background=[("active", ACCENT), ("disabled", BG_HOVER)],
               foreground=[("active", "#FFFFFF"), ("disabled", TEXTO_MUTED)])
