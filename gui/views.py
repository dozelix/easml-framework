import os
import re
import tkinter as tk
import webbrowser
from collections import Counter
from gui.config import MODULOS, NOMBRES_DEFENSA
from gui.styles import *


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _card(parent, **kwargs):
    card = tk.Frame(parent, bg=BG_PANEL, highlightbackground=BORDE,
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
        tk.Label(c, text=tit, bg=BG_PANEL, fg=TEXTO_DIM,
                 font=FUENTE_SM).pack(anchor="w")
        tk.Label(c, text=val, bg=BG_PANEL, fg=color,
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
        tk.Label(c, text=cia_name, bg=BG_PANEL, fg=TEXTO_DIM,
                 font=FUENTE_SM).pack(anchor="w")
        tk.Label(c, text=str(cia_counter.get(cia_name, 0)),
                 bg=BG_PANEL, fg=TEXTO, font=FUENTE_STAT).pack(anchor="w", pady=(4, 0))


def build_tutorial(parent):
    _limpiar(parent)

    _titulo(parent, "TUTORIAL RAPIDO")

    intro = _card(parent, padx=18, pady=14)
    intro.pack(fill=tk.X, pady=(0, 20))
    tk.Label(intro, text="Bienvenido! Este laboratorio te permite ejecutar 14 tipos\nde amenazas de forma segura en un entorno aislado.",
             bg=BG_PANEL, fg=TEXTO, font=FUENTE, justify="left").pack(anchor="w")

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
        tk.Label(c, text=paso, bg=BG_PANEL, fg=color,
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
    md_existe = os.path.exists(os.path.join(dir_modulo, "README.md"))

    _titulo(parent, "INFORMACION DEL MODULO")

    cia_card = _card(parent, padx=16, pady=12)
    cia_card.pack(fill=tk.X, pady=(0, 16))

    color_cia = {"Confidencialidad": CYAN, "Integridad": MORADO, "Disponibilidad": NARANJA}.get(cia, TEXTO)
    tk.Label(cia_card, text="PILAR CIA", bg=BG_PANEL, fg=TEXTO_DIM,
             font=FUENTE_SM).pack(anchor="w")
    tk.Label(cia_card, text=cia, bg=BG_PANEL, fg=color_cia,
             font=FUENTE_H2).pack(anchor="w", pady=(4, 0))

    _separador(parent)
    tk.Label(parent, text="ARCHIVOS DEL MODULO", bg=BG, fg=TEXTO,
             font=FUENTE_BOLD, anchor="w").pack(anchor="w", pady=(0, 12))

    for label, existe in [
        (f"Simulacion: {script}.py", sim_existe),
        (f"Defensa:    {arch_defensa}.py", def_existe),
        ("Documentacion (README.md)", md_existe),
    ]:
        c = _card(parent, padx=16, pady=8)
        c.pack(fill=tk.X, pady=2)
        fg_color = VERDE if existe else ROJO
        status = "[OK]" if existe else "[--]"
        lbl = tk.Label(c, text=f"{status}  {label}", bg=BG_PANEL, fg=fg_color,
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


def leer_readme(index: int) -> str | None:
    if index < 0 or index >= len(MODULOS):
        return None
    num, nombre = MODULOS[index][0], MODULOS[index][1]
    readme_path = os.path.join(ROOT, 'modulos', nombre, "README.md")
    if os.path.exists(readme_path):
        with open(readme_path, "r", encoding="utf-8") as f:
            return f.read()
    return None


def _insert_md_text(text: tk.Text, md: str):
    text.tag_configure("h1", font=FUENTE_H1, foreground=ACCENT, spacing1=10, spacing3=6)
    text.tag_configure("h2", font=FUENTE_H2, foreground=ACCENT, spacing1=8, spacing3=4)
    text.tag_configure("h3", font=("JetBrains Mono", 11, "bold"), foreground=ACCENT, spacing1=6, spacing3=3)
    text.tag_configure("bold", font=FUENTE_BOLD)
    text.tag_configure("code", background=BG_HOVER, foreground=ROJO, font=FUENTE)
    text.tag_configure("code_block", background="#1A1A1A", foreground="#9ECE6A",
                       font=("JetBrains Mono", 9), spacing1=4, spacing3=4,
                       lmargin1=14, lmargin2=14, rmargin=14)
    text.tag_configure("bullet", lmargin1=14, lmargin2=28)
    text.tag_configure("link", foreground=ACCENT, underline=True)

    lines = md.split("\n")
    in_code = False
    code_buffer = []

    for line in lines:
        if line.startswith("```"):
            if in_code:
                code_buffer.append(line)
                text.insert(tk.END, "\n".join(code_buffer) + "\n", "code_block")
                code_buffer.clear()
                in_code = False
            else:
                in_code = True
                code_buffer = []
            continue

        if in_code:
            code_buffer.append(line)
            continue

        if line.startswith("# "):
            text.insert(tk.END, line[2:].strip() + "\n", "h1")
        elif line.startswith("## "):
            text.insert(tk.END, line[3:].strip() + "\n", "h2")
        elif line.startswith("### "):
            text.insert(tk.END, line[4:].strip() + "\n", "h3")
        elif line.startswith("- ") or line.startswith("* "):
            text.insert(tk.END, line[2:].strip() + "\n", "bullet")
        elif "**" in line:
            parts = re.split(r"(\*\*.*?\*\*)", line)
            for p in parts:
                if p.startswith("**") and p.endswith("**"):
                    text.insert(tk.END, p[2:-2], "bold")
                else:
                    text.insert(tk.END, p)
            text.insert(tk.END, "\n")
        elif "`" in line:
            parts = re.split(r"(`[^`]+`)", line)
            for p in parts:
                if p.startswith("`") and p.endswith("`"):
                    text.insert(tk.END, p[1:-1], "code")
                else:
                    text.insert(tk.END, p)
            text.insert(tk.END, "\n")
        elif line.strip():
            text.insert(tk.END, line + "\n")
        else:
            text.insert(tk.END, "\n")

    text.configure(state=tk.DISABLED)


def build_readme(parent, md_text: str):
    _limpiar(parent)

    frame = tk.Frame(parent, bg=BG, highlightbackground=BORDE, highlightthickness=1)
    frame.pack(fill=tk.BOTH, expand=True)

    text = tk.Text(frame, bg="#FAF7F2", fg=TEXTO, font=FUENTE,
                   wrap=tk.WORD, relief="flat", padx=14, pady=10,
                   highlightthickness=0, borderwidth=0)
    text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    scroll = tk.Scrollbar(frame, command=text.yview, bg=BG_HOVER,
                          troughcolor=BG, relief="flat", borderwidth=0)
    scroll.pack(side=tk.RIGHT, fill=tk.Y)
    text.configure(yscrollcommand=scroll.set)

    _insert_md_text(text, md_text)
