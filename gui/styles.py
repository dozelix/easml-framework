"""Colores, fuentes y configuración de estilos ttk para la GUI."""

import tkinter as tk
from tkinter import ttk

# ── Paleta Zen+Brutalista ──────────────────────────────────────────────────
BG = "#0d0f14"
BG_PANEL = "#1a1d27"
BG_HOVER = "#2a2e3e"
BG_ACTIVO = "#7aa2f7"
TEXTO = "#c0caf5"
TEXTO_DIM = "#565f89"
TEXTO_MUTED = "#3b4261"
ACCENT = "#7aa2f7"

# Colores semánticos para acciones
ROJO = "#f7768e"      # Simular / amenaza
AZUL = "#7aa2f7"      # Defensa
VERDE = "#9ece6a"     # Clean
AMARILLO = "#e0af68"  # Setup
CYAN = "#7dcfff"
MORADO = "#bb9af7"
NARANJA = "#ff9e64"

FUENTE = ("JetBrains Mono", 10)
FUENTE_BOLD = ("JetBrains Mono", 10, "bold")
FUENTE_SM = ("JetBrains Mono", 9)
FUENTE_LG = ("JetBrains Mono", 12, "bold")


def configurar_estilos():
    estilo = ttk.Style()
    estilo.theme_use("clam")

    estilo.configure("TFrame", background=BG)
    estilo.configure("Panel.TFrame", background=BG_PANEL)
    estilo.configure("TLabel", background=BG, foreground=TEXTO, font=FUENTE)
    estilo.configure("Titulo.TLabel", background=BG_PANEL, foreground=ACCENT,
                     font=FUENTE_BOLD)
    estilo.configure("Dim.TLabel", background=BG, foreground=TEXTO_DIM, font=FUENTE_SM)

    estilo.configure("Treeview", background=BG_PANEL, foreground=TEXTO,
                     font=FUENTE, rowheight=30, fieldbackground=BG_PANEL)
    estilo.configure("Treeview.Heading", background=BG_HOVER, foreground=ACCENT,
                     font=FUENTE_BOLD)
    estilo.map("Treeview", background=[("selected", BG_ACTIVO)],
               foreground=[("selected", "#0d0f14")])

    estilo.configure("Accion.TButton", background=BG_HOVER, foreground=TEXTO,
                     font=FUENTE_BOLD, padding=(14, 10), relief="flat", borderwidth=0)
    estilo.map("Accion.TButton",
               background=[("active", ACCENT), ("disabled", BG_HOVER)],
               foreground=[("active", BG), ("disabled", TEXTO_MUTED)])
