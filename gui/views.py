import os
import re
import tkinter as tk
import webbrowser
from collections import Counter
from tkhtmlview import HTMLLabel
from app.config import MODULOS, NOMBRES_DEFENSA
from gui.styles import *


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _card(parent, **kwargs):
    card = tk.Frame(parent, bg=BG_CARD, highlightbackground=BORDE_CARD,
                    highlightthickness=1, **kwargs)
    return card


def _limpiar(parent):
    for w in parent.winfo_children():
        w.destroy()


def _titulo(parent, texto):
    lbl = tk.Label(parent, text=texto, bg=BG, fg=TEXTO, font=FUENTE_H1, anchor="w")
    lbl.pack(anchor="w", pady=(0, 20))
    return lbl


def _separador(parent):
    ttk.Separator(parent, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=8)


def build_dashboard(parent):
    _limpiar(parent)

    dir_lab = os.path.join(ROOT, 'directorio_pruebas')
    dir_logs = os.path.join(ROOT, 'lab_data', 'logs')

    archivos_lab = len([f for f in os.listdir(dir_lab)
                        if os.path.isfile(os.path.join(dir_lab, f))]) if os.path.isdir(dir_lab) else 0
    logs_lab = len([f for f in os.listdir(dir_logs) if f.endswith('.log')]) if os.path.isdir(dir_logs) else 0
    cia_counter = Counter(m[3] for m in MODULOS)
    activo = archivos_lab > 0

    _titulo(parent, "DASHBOARD")

    stats_row = tk.Frame(parent, bg=BG)
    stats_row.pack(fill=tk.X, pady=(0, 20))

    for i, (tit, val, color) in enumerate([
        ("ESTADO", "ACTIVO" if activo else "VACIO", VERDE if activo else ROJO),
        ("ARCHIVOS", str(archivos_lab), TEXTO),
        ("LOGS", str(logs_lab), TEXTO),
    ]):
        stats_row.grid_columnconfigure(i, weight=1, uniform="stats")
        c = _card(stats_row, padx=18, pady=14)
        c.grid(row=0, column=i, sticky="nsew", padx=(0 if i == 0 else 4, 0 if i == 2 else 4))
        tk.Label(c, text=tit, bg=BG_CARD, fg=TEXTO_DIM,
                 font=FUENTE_SM).pack(anchor="w")
        tk.Label(c, text=val, bg=BG_CARD, fg=color,
                 font=FUENTE_STAT).pack(anchor="w", pady=(4, 0))

    _separador(parent)

    tk.Label(parent, text="MODULOS POR PILAR CIA", bg=BG, fg=TEXTO,
             font=FUENTE_BOLD, anchor="w").pack(anchor="w", pady=(0, 12))

    cia_row = tk.Frame(parent, bg=BG)
    cia_row.pack(fill=tk.X)

    for i, (cia_name, icon_key) in enumerate([
        ("Confidencialidad", "confidencialidad"),
        ("Integridad", "integridad"),
        ("Disponibilidad", "disponibilidad"),
    ]):
        cia_row.grid_columnconfigure(i, weight=1, uniform="cia")
        c = _card(cia_row, padx=16, pady=14)
        c.grid(row=0, column=i, sticky="nsew", padx=(0 if i == 0 else 4, 0 if i == 2 else 4))
        tk.Label(c, text=cia_name, bg=BG_CARD, fg=TEXTO_DIM,
                 font=FUENTE_SM).pack(anchor="w")
        tk.Label(c, text=str(cia_counter.get(cia_name, 0)),
                 bg=BG_CARD, fg=TEXTO, font=FUENTE_STAT).pack(anchor="w", pady=(4, 0))


def build_tutorial(parent):
    _limpiar(parent)

    _titulo(parent, "TUTORIAL RAPIDO")

    intro = _card(parent, padx=18, pady=14)
    intro.pack(fill=tk.X, pady=(0, 20))
    tk.Label(intro, text="Bienvenido! Este laboratorio te permite ejecutar 14 tipos\nde amenazas de forma segura en un entorno aislado.",
             bg=BG_CARD, fg=TEXTO, font=FUENTE, justify="left").pack(anchor="w")

    _separador(parent)
    tk.Label(parent, text="FLUJO DE TRABAJO", bg=BG, fg=TEXTO,
             font=FUENTE_BOLD, anchor="w").pack(anchor="w", pady=(0, 12))

    for paso, color in [
        ("[1] Setup   — Genera archivos de prueba", AMARILLO),
        ("[2] Simular — Ejecuta la simulacion del modulo", ROJO),
        ("[3] Defensa — Mitiga la amenaza y restaura archivos", AZUL),
        ("[4] Clean   — Limpia consola y entorno", VERDE),
    ]:
        c = _card(parent, padx=16, pady=10)
        c.pack(fill=tk.X, pady=3)
        tk.Label(c, text=paso, bg=BG_CARD, fg=color,
                 font=FUENTE_BOLD).pack(anchor="w")

    _separador(parent)
    tk.Label(parent, text="Los modulos estan ordenados por control CIS (2 -> 15) para\nfacilitar el aprendizaje progresivo de los estandares.",
             bg=BG, fg=TEXTO_DIM, font=FUENTE_SM, justify="left").pack(anchor="w")


def build_modulo_info(parent, index: int):
    _limpiar(parent)

    if index < 0 or index >= len(MODULOS):
        tk.Label(parent, text="Selecciona un modulo de la lista.",
                 bg=BG, fg=TEXTO_DIM, font=FUENTE).pack()
        return

    num, nombre, script, cia, cis, url_ref = MODULOS[index]
    nombre_defensa = NOMBRES_DEFENSA.get(num, "defensa")
    dir_modulo = os.path.join(ROOT, 'modulos', nombre)
    arch_defensa = nombre_defensa.lower().replace(' ', '_')

    sim_existe = os.path.exists(os.path.join(dir_modulo, f"{script}.py"))
    def_existe = os.path.exists(os.path.join(dir_modulo, f"{arch_defensa}.py"))
    md_existe = os.path.exists(os.path.join(dir_modulo, "guia.html"))

    _titulo(parent, "INFORMACION DEL MODULO")

    cia_card = _card(parent, padx=16, pady=12)
    cia_card.pack(fill=tk.X, pady=(0, 16))

    color_cia = {"Confidencialidad": CYAN, "Integridad": MORADO, "Disponibilidad": NARANJA}.get(cia, TEXTO)
    tk.Label(cia_card, text="PILAR CIA", bg=BG_CARD, fg=TEXTO_DIM,
             font=FUENTE_SM).pack(anchor="w")
    tk.Label(cia_card, text=cia, bg=BG_CARD, fg=color_cia,
             font=FUENTE_H2).pack(anchor="w", pady=(4, 0))

    _separador(parent)
    tk.Label(parent, text="ARCHIVOS DEL MODULO", bg=BG, fg=TEXTO,
             font=FUENTE_BOLD, anchor="w").pack(anchor="w", pady=(0, 12))

    for label, existe in [
        (f"Simulacion: {script}.py", sim_existe),
        (f"Defensa:    {arch_defensa}.py", def_existe),
        ("Guia (guia.html)", md_existe),
    ]:
        c = _card(parent, padx=16, pady=8)
        c.pack(fill=tk.X, pady=2)
        fg_color = VERDE if existe else ROJO
        status = "[OK]" if existe else "[--]"
        lbl = tk.Label(c, text=f"{status}  {label}", bg=BG_CARD, fg=fg_color,
                       font=FUENTE_BOLD, anchor="w")
        lbl.pack(fill=tk.X)

    if url_ref:
        _separador(parent)
        tk.Label(parent, text="REFERENCIA", bg=BG, fg=TEXTO,
                 font=FUENTE_BOLD, anchor="w").pack(anchor="w", pady=(0, 8))
        link = tk.Label(parent, text=url_ref, bg=BG, fg=ACCENT,
                        font=FUENTE, cursor="hand2")
        link.pack(anchor="w")
        link.bind("<Button-1>", lambda e: webbrowser.open(url_ref))
        link.bind("<Enter>", lambda e: link.configure(fg=MORADO))
        link.bind("<Leave>", lambda e: link.configure(fg=ACCENT))


def leer_guia(index: int) -> str | None:
    if index < 0 or index >= len(MODULOS):
        return None
    num, nombre = MODULOS[index][0], MODULOS[index][1]
    path = os.path.join(ROOT, 'modulos', nombre, "guia.html")
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    return None


def _extraer_body(html: str) -> str:
    m = re.search(r'<body[^>]*>(.*?)</body>', html, re.DOTALL)
    return m.group(1) if m else html


def build_guia(parent, html_content: str):
    _limpiar(parent)
    body = _extraer_body(html_content)

    frame = tk.Frame(parent, bg=BG, highlightbackground=BORDE_CARD,
                     highlightthickness=1)
    frame.pack(fill=tk.BOTH, expand=True)

    lbl = HTMLLabel(frame, html=body, background=BG_CARD,
                    font=FUENTE, padx=10, pady=10)
    lbl.pack(fill=tk.BOTH, expand=True)
