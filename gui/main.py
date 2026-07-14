"""Aplicación principal de la GUI del laboratorio."""

import os
import sys
import tkinter as tk
from tkinter import ttk, messagebox

_DIR_RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _DIR_RAIZ)

from gui.config import MODULOS, NOMBRES_DEFENSA
from gui.laboratorio import DESAFIOS_POR_MODULO
from gui.styles import *
from gui.views import dashboard, tutorial, modulo_info, leer_readme, md_to_html

try:
    from tkhtmlview import HTMLLabel
    HAS_HTML = True
except ImportError:
    HAS_HTML = False
from gui.runner import ScriptRunner
from gui.desafio import DesafioWindow

try:
    from PIL import Image, ImageTk as _ImageTk
    HAS_PIL = True
except ImportError:
    HAS_PIL = False

ASSETS_DIR = os.path.join(_DIR_RAIZ, 'assets', 'modulos')
ICONOS_CIA = {"Confidencialidad": "🔒", "Integridad": "🛡️", "Disponibilidad": "⚡"}


class LaboratorioGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("E.A.S.M.L — Laboratorio Educativo de Malware")
        self.geometry("1280x800")
        self.minsize(960, 600)

        self.runner = ScriptRunner(on_log=self._log, on_done=self._runner_done,
                                   on_error=lambda e: self._log(e))
        self.viendo_readme = False

        configurar_estilos()
        self._iconos = {}
        self._construir()
        self._mostrar_dashboard()

    # ── Layout ──────────────────────────────────────────────────────────────

    def _cargar_icono(self, nombre, size=28):
        if not HAS_PIL:
            return None
        import PIL.Image as _PILImage
        import PIL.ImageTk as _PILImageTk
        ruta = os.path.join(ASSETS_DIR, f"{nombre}.png")
        if not os.path.exists(ruta):
            return None
        if nombre in self._iconos:
            return self._iconos[nombre]
        filtro = getattr(_PILImage.Resampling, "LANCZOS", 1)
        img = _PILImage.open(ruta).resize((size, size), filtro)
        photo = _PILImageTk.PhotoImage(img)
        self._iconos[nombre] = photo
        return photo

    def _construir(self):
        self.configure(bg=BG)

        self.pw = tk.PanedWindow(self, orient=tk.HORIZONTAL, bg=BG,
                                 sashwidth=2, sashrelief=tk.FLAT)
        self.pw.pack(fill=tk.BOTH, expand=True, padx=4, pady=4)

        # ─── Sidebar ────────────────────────────────────────────────────────
        izq = tk.Frame(self.pw, bg=BG_PANEL, width=200)
        self.pw.add(izq, minsize=160)

        dash_btn = tk.Button(izq, text="📊  Panel", command=self._mostrar_dashboard,
                             bg=BG_PANEL, fg=CYAN, font=FUENTE_BOLD,
                             activebackground=BG_HOVER, activeforeground=CYAN,
                             relief="flat", anchor="w", padx=14, pady=8,
                             cursor="hand2")
        dash_btn.pack(fill=tk.X)
        dash_btn.bind("<Enter>", lambda e: dash_btn.configure(bg=BG_HOVER))
        dash_btn.bind("<Leave>", lambda e: dash_btn.configure(bg=BG_PANEL))

        ttk.Separator(izq, orient=tk.HORIZONTAL).pack(fill=tk.X, padx=10, pady=4)

        tk.Label(izq, text="MÓDULOS", bg=BG_PANEL, fg=TEXTO_DIM,
                 font=FUENTE_SM, anchor="w").pack(fill=tk.X, padx=14, pady=(2, 4))

        self.lista = ttk.Treeview(izq, columns=(), show="tree",
                                  selectmode="browse", height=22)
        self.lista.column("#0", width=180)

        for i, m in enumerate(MODULOS):
            _, nombre, _, _, _, _ = m
            img = self._cargar_icono(nombre)
            self.lista.insert("", tk.END, iid=str(i),
                              text=f"  {nombre}", image=img or "")

        self.lista.pack(fill=tk.BOTH, expand=True, padx=4, pady=2)
        self.lista.bind("<<TreeviewSelect>>", self._on_seleccion)

        tuto_btn = tk.Button(izq, text="📖  Tutorial", command=self._mostrar_tutorial,
                             bg=BG_PANEL, fg=MORADO, font=FUENTE_BOLD,
                             activebackground=BG_HOVER, activeforeground=MORADO,
                             relief="flat", anchor="w", padx=14, pady=8,
                             cursor="hand2")
        tuto_btn.pack(fill=tk.X, side=tk.BOTTOM)
        tuto_btn.bind("<Enter>", lambda e: tuto_btn.configure(bg=BG_HOVER))
        tuto_btn.bind("<Leave>", lambda e: tuto_btn.configure(bg=BG_PANEL))

        # ─── Panel derecho ──────────────────────────────────────────────────
        der = tk.Frame(self.pw, bg=BG)
        self.pw.add(der, minsize=500)

        # Header del módulo
        hdr = tk.Frame(der, bg=BG_PANEL, height=40)
        hdr.pack(fill=tk.X)
        hdr.pack_propagate(False)

        self.lbl_nombre = tk.Label(hdr, text="", bg=BG_PANEL, fg=ACCENT,
                                   font=FUENTE_LG, anchor="w")
        self.lbl_nombre.pack(side=tk.LEFT, padx=14)

        self.lbl_cis = tk.Label(hdr, text="", bg=BG_PANEL, fg=TEXTO_DIM,
                                font=("JetBrains Mono", 9), padx=10, pady=2)
        self.lbl_cis.pack(side=tk.RIGHT, padx=10)

        # Área de contenido
        self.content_frame = tk.Frame(der, bg=BG)
        self.content_frame.pack(fill=tk.BOTH, expand=True)

        self.contenido = tk.Text(self.content_frame, bg=BG_PANEL, fg=TEXTO, font=FUENTE,
                                 wrap=tk.WORD, relief="flat", padx=14, pady=10,
                                 insertbackground=ACCENT, state=tk.DISABLED)
        self.contenido.pack(fill=tk.BOTH, expand=True)

        self.html_readme = None
        if HAS_HTML:
            self.html_readme = HTMLLabel(self.content_frame, html="",
                                         background=BG_PANEL, font=FUENTE)
            self.html_readme.fit_height = True

        # Barra de acciones
        bacc = tk.Frame(der, bg=BG, height=48)
        bacc.pack(fill=tk.X)
        bacc.pack_propagate(False)

        for texto, color, cmd in [
            ("  Setup  ", AMARILLO, self._action_setup),
            (" Simular ", ROJO,     self._action_simular),
            (" Defensa ", AZUL,     self._action_defensa),
            ("  Clean  ", VERDE,    self._action_clean),
            (" Readme  ", MORADO,   self._action_readme),
            ("  Juego  ", NARANJA,  self._action_juego),
        ]:
            btn = tk.Button(bacc, text=texto, command=cmd,
                            bg=BG_PANEL, fg=color, font=FUENTE_BOLD,
                            activebackground=color, activeforeground=BG,
                            relief="flat", padx=12, pady=6, cursor="hand2")
            btn.pack(side=tk.LEFT, padx=3)
            btn.bind("<Enter>", lambda e, b=btn, c=color: b.configure(bg=c, fg=BG))
            btn.bind("<Leave>", lambda e, b=btn, c=color: b.configure(bg=BG_PANEL, fg=c))

        # Consola
        cf = tk.Frame(der, bg=BG, height=150)
        cf.pack(fill=tk.X, pady=(4, 0))
        cf.pack_propagate(False)

        enc = tk.Frame(cf, bg=BG)
        enc.pack(fill=tk.X)
        tk.Label(enc, text="› Consola", bg=BG, fg=TEXTO_DIM,
                 font=FUENTE_SM, anchor="w").pack(side=tk.LEFT)
        tk.Button(enc, text="×", command=self._log_clear,
                  bg=BG, fg=TEXTO_DIM, font=("JetBrains Mono", 10, "bold"),
                  relief="flat", padx=8, cursor="hand2").pack(side=tk.RIGHT)

        self.consola = tk.Text(cf, bg="#0a0c10", fg=VERDE, font=("JetBrains Mono", 9),
                               wrap=tk.WORD, relief="flat", padx=10, pady=6,
                               insertbackground=VERDE, state=tk.DISABLED, height=5)
        self.consola.pack(fill=tk.BOTH, expand=True)

    # ── Métodos de contenido ────────────────────────────────────────────────

    def _mostrar_texto(self):
        if self.html_readme:
            self.html_readme.pack_forget()
        self.contenido.pack(fill=tk.BOTH, expand=True)

    def _mostrar_html(self, html: str):
        self.contenido.pack_forget()
        if self.html_readme:
            self.html_readme.set_html(html)
            self.html_readme.pack(fill=tk.BOTH, expand=True)

    def _set_contenido(self, texto: str):
        self._mostrar_texto()
        self.contenido.configure(state=tk.NORMAL)
        self.contenido.delete("1.0", tk.END)
        self.contenido.insert("1.0", texto)
        self.contenido.configure(state=tk.DISABLED)

    def _log(self, msg: str):
        self.consola.configure(state=tk.NORMAL)
        self.consola.insert(tk.END, msg + "\n")
        self.consola.see(tk.END)
        self.consola.configure(state=tk.DISABLED)

    def _log_clear(self):
        self.consola.configure(state=tk.NORMAL)
        self.consola.delete("1.0", tk.END)
        self.consola.configure(state=tk.DISABLED)

    def _runner_done(self, salida: str, etiqueta: str):
        self.runner.procesar_salida(salida, etiqueta)

    # ── Vistas ──────────────────────────────────────────────────────────────

    def _mostrar_dashboard(self):
        self.viendo_readme = False
        self.lbl_nombre.configure(text="📊  Panel")
        self.lbl_cis.configure(text="")
        self._set_contenido(dashboard())

    def _mostrar_tutorial(self):
        self.viendo_readme = False
        self.lbl_nombre.configure(text="📖  Tutorial")
        self.lbl_cis.configure(text="")
        self._set_contenido(tutorial())

    def _mostrar_modulo(self, index: int):
        self.viendo_readme = False
        num, nombre, _, cia, cis, _ = MODULOS[index]
        self.lbl_nombre.configure(text=f"{ICONOS_CIA.get(cia, '?')}  {nombre}")
        self.lbl_cis.configure(text=cis)
        self._set_contenido(modulo_info(index))

    def _mostrar_readme(self, index: int):
        md = leer_readme(index)
        if md is None:
            self._set_contenido("⚠️ Este módulo no tiene documentación aún.")
            return
        self.viendo_readme = True
        if self.html_readme:
            self._mostrar_html(md_to_html(md))
        else:
            self._set_contenido(md)

    def _restaurar(self):
        self.viendo_readme = False
        sel = self.lista.selection()
        if sel:
            self._mostrar_modulo(int(sel[0]))
        else:
            self._mostrar_dashboard()

    # ── Acciones ────────────────────────────────────────────────────────────

    def _action_setup(self):
        self._log_clear()
        self._log("⚙️ Preparando entorno de pruebas...")
        self.runner.ejecutar(os.path.join(_DIR_RAIZ, "core", "lab_setup.py"), "Setup")

    def _action_simular(self):
        sel = self.lista.selection()
        if not sel:
            return
        idx = int(sel[0])
        _, nombre, script, _, _, _ = MODULOS[idx]
        sp = os.path.join(_DIR_RAIZ, 'modulos', nombre, f"{script}.py")
        self._log_clear()
        self._log(f"🦠 Simulando {nombre}...")
        self.runner.ejecutar(sp, f"{nombre}/simulacion")

    def _action_defensa(self):
        sel = self.lista.selection()
        if not sel:
            return
        idx = int(sel[0])
        num, nombre = MODULOS[idx][0], MODULOS[idx][1]
        nd = NOMBRES_DEFENSA.get(num, "defensa")
        sp = os.path.join(_DIR_RAIZ, 'modulos', nombre, f"{nd.lower().replace(' ', '_')}.py")
        self._log_clear()
        self._log(f"🛡️ Defendiendo {nombre}...")
        self.runner.ejecutar(sp, f"{nombre}/defensa")

    def _action_readme(self):
        sel = self.lista.selection()
        if not sel:
            return
        idx = int(sel[0])
        if self.viendo_readme:
            self._restaurar()
        else:
            self._mostrar_readme(idx)

    def _action_clean(self):
        self._log_clear()
        self._log("🧹 Consola limpiada.")
        self._restaurar()

    def _action_juego(self):
        sel = self.lista.selection()
        if not sel:
            return
        idx = int(sel[0])
        _, nombre = MODULOS[idx][0], MODULOS[idx][1]
        if nombre not in DESAFIOS_POR_MODULO:
            self._log(f"⚠️ {nombre} no tiene desafíos disponibles.")
            return
        DesafioWindow(self, nombre)

    def _on_seleccion(self, event):
        sel = self.lista.selection()
        if sel:
            self.viendo_readme = False
            self._mostrar_modulo(int(sel[0]))

    def on_closing(self):
        if messagebox.askyesno("Salir", "¿Salir del laboratorio?"):
            self.destroy()


def main():
    app = LaboratorioGUI()
    app.protocol("WM_DELETE_WINDOW", app.on_closing)
    app.mainloop()


if __name__ == "__main__":
    main()
