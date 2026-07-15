import os
import sys
import tkinter as tk
from tkinter import ttk, messagebox

_DIR_RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _DIR_RAIZ)

from gui.config import MODULOS, NOMBRES_DEFENSA
from gui.laboratorio import DESAFIOS_POR_MODULO
from gui.styles import *
from gui.views import build_dashboard, build_tutorial, build_modulo_info, build_readme, leer_readme

from gui.runner import ScriptRunner
from gui.desafio import DesafioWindow

try:
    from PIL import Image as _PILImage, ImageTk as _PILImageTk
    HAS_PIL = True
except ImportError:
    HAS_PIL = False

ASSETS_MODULOS = os.path.join(_DIR_RAIZ, 'assets', 'modulos')
ASSETS_DIR = os.path.join(_DIR_RAIZ, 'assets')


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

    def _cargar_icono(self, nombre, size=28, directorio=ASSETS_MODULOS):
        ruta = os.path.join(directorio, f"{nombre}.png")
        if not os.path.exists(ruta):
            return None
        if nombre in self._iconos:
            return self._iconos[nombre]
        if HAS_PIL:
            filtro = getattr(_PILImage.Resampling, "LANCZOS", 1)
            img = _PILImage.open(ruta).resize((size, size), filtro)
            photo = _PILImageTk.PhotoImage(img)
        else:
            photo = tk.PhotoImage(file=ruta)
            w, h = photo.width(), photo.height()
            if w != size or h != size:
                photo = photo.zoom(size, size).subsample(w, h)
        self._iconos[nombre] = photo
        return photo

    def _construir(self):
        self.configure(bg=BG)

        main_frame = tk.Frame(self, bg=BG)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=4, pady=4)

        # ─── Sidebar ────────────────────────────────────────────────────────
        izq = tk.Frame(main_frame, bg=BG_PANEL, width=200, highlightbackground=BORDE,
                       highlightthickness=1)
        izq.pack(side=tk.LEFT, fill=tk.Y)
        izq.pack_propagate(False)

        self._btn_sidebar(izq, "PANEL", CYAN, self._mostrar_dashboard).pack(fill=tk.X)

        ttk.Separator(izq, orient=tk.HORIZONTAL).pack(fill=tk.X, padx=10, pady=4)

        tk.Label(izq, text="MODULOS", bg=BG_PANEL, fg=TEXTO_DIM,
                 font=FUENTE_SM, anchor="w").pack(fill=tk.X, padx=14, pady=(2, 4))

        self.lista = ttk.Treeview(izq, columns=(), show="tree",
                                  selectmode="browse")
        self.lista.column("#0", width=180)

        for i, m in enumerate(MODULOS):
            _, nombre, _, _, _, _ = m
            img = self._cargar_icono(nombre, directorio=ASSETS_MODULOS)
            self.lista.insert("", tk.END, iid=str(i),
                              text=f"  {nombre}", image=img or "")

        self.lista.pack(fill=tk.BOTH, expand=True, padx=4, pady=2)
        self.lista.bind("<<TreeviewSelect>>", self._on_seleccion)

        pie = tk.Frame(izq, bg=BG_PANEL)
        pie.pack(fill=tk.X, side=tk.BOTTOM)
        ttk.Separator(pie, orient=tk.HORIZONTAL).pack(fill=tk.X, padx=6, pady=2)
        self._btn_sidebar(pie, "TUTORIAL", MORADO, self._mostrar_tutorial).pack(fill=tk.X, padx=4, pady=(0, 4))

        # ─── Panel derecho ──────────────────────────────────────────────────
        der = tk.Frame(main_frame, bg=BG)
        der.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(4, 0))

        # Header
        hdr = tk.Frame(der, bg=BG_PANEL, height=40, highlightbackground=BORDE,
                       highlightthickness=1)
        hdr.pack(fill=tk.X)
        hdr.pack_propagate(False)

        self.lbl_icono_cia = tk.Label(hdr, bg=BG_PANEL)
        self.lbl_icono_cia.pack(side=tk.LEFT, padx=(14, 4))

        self.lbl_nombre = tk.Label(hdr, text="", bg=BG_PANEL, fg=ACCENT,
                                   font=FUENTE_LG, anchor="w")
        self.lbl_nombre.pack(side=tk.LEFT, padx=(0, 14))

        self.lbl_cis = tk.Label(hdr, text="", bg=BG_PANEL, fg=TEXTO_DIM,
                                font=("JetBrains Mono", 9), padx=10, pady=2)
        self.lbl_cis.pack(side=tk.RIGHT, padx=10)

        # Content area
        self.content_frame = tk.Frame(der, bg=BG)
        self.content_frame.pack(fill=tk.BOTH, expand=True, padx=14, pady=10)

        # README rendering (uses Text widget — no HTMLLabel)

        # Action buttons
        bacc = tk.Frame(der, bg=BG, height=48)
        bacc.pack(fill=tk.X)
        bacc.pack_propagate(False)

        for texto, color, cmd in [
            ("  Setup  ", AMARILLO, self._action_setup),
            (" Simular ", ROJO,     self._action_simular),
            (" Defensa ", AZUL,     self._action_defensa),
            ("  Clean  ", VERDE,    self._action_clean),
            ("  Guía   ", MORADO,   self._action_readme),
            ("  Juego  ", NARANJA,  self._action_juego),
        ]:
            btn = tk.Button(bacc, text=texto, command=cmd,
                            bg=BG_PANEL, fg=color, font=("JetBrains Mono", 10),
                            activebackground=color, activeforeground="#FFFFFF",
                            relief="flat", padx=14, pady=4, cursor="hand2",
                            highlightbackground=BORDE, highlightthickness=1,
                            borderwidth=0)
            btn.pack(side=tk.LEFT, padx=3)
            btn.bind("<Enter>", lambda e, b=btn, c=color: b.configure(bg=c, fg="#FFFFFF"))
            btn.bind("<Leave>", lambda e, b=btn, c=color: b.configure(bg=BG_PANEL, fg=c))

        # Console
        cf = tk.Frame(der, bg=BG, height=150)
        cf.pack(fill=tk.X, pady=(4, 0))
        cf.pack_propagate(False)

        enc = tk.Frame(cf, bg=BG)
        enc.pack(fill=tk.X)
        tk.Label(enc, text="CONSOLA", bg=BG, fg=TEXTO_DIM,
                 font=FUENTE_SM, anchor="w").pack(side=tk.LEFT)
        tk.Button(enc, text="X", command=self._log_clear,
                  bg=BG, fg=TEXTO_DIM, font=("JetBrains Mono", 10, "bold"),
                  relief="flat", padx=8, cursor="hand2").pack(side=tk.RIGHT)

        self.consola = tk.Text(cf, bg="#1A1A1A", fg="#9ECE6A",
                               font=("JetBrains Mono", 9), wrap=tk.WORD,
                               relief="solid", padx=10, pady=6,
                               insertbackground="#9ECE6A", state=tk.DISABLED,
                               height=5, highlightbackground=BORDE, highlightthickness=2)
        self.consola.pack(fill=tk.BOTH, expand=True)

    def _btn_sidebar(self, parent, texto, color, comando):
        btn = tk.Button(parent, text=texto, command=comando,
                        bg=BG_PANEL, fg=color, font=FUENTE_BOLD,
                        activebackground=BG_HOVER, activeforeground=color,
                        relief="flat", anchor="w", padx=14, pady=8,
                        cursor="hand2")
        btn.bind("<Enter>", lambda e: btn.configure(bg=BG_HOVER))
        btn.bind("<Leave>", lambda e: btn.configure(bg=BG_PANEL))
        return btn

    # ── Gestión de contenido ───────────────────────────────────────────────

    def _limpiar_contenido(self):
        for w in self.content_frame.winfo_children():
            w.pack_forget()
            w.destroy()
        self.viendo_readme = False

    def _mostrar_widgets(self, builder_fn, *args):
        self._limpiar_contenido()
        builder_fn(self.content_frame, *args)

    # ── Logs / Consola ─────────────────────────────────────────────────────

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

    # ── Vistas ─────────────────────────────────────────────────────────────

    def _mostrar_dashboard(self):
        self.lbl_icono_cia.configure(image="")
        self.lbl_nombre.configure(text="PANEL")
        self.lbl_cis.configure(text="")
        self._mostrar_widgets(build_dashboard)

    def _mostrar_tutorial(self):
        self.lbl_icono_cia.configure(image="")
        self.lbl_nombre.configure(text="TUTORIAL")
        self.lbl_cis.configure(text="")
        self._mostrar_widgets(build_tutorial)

    def _mostrar_modulo(self, index: int):
        num, nombre, _, cia, cis, _ = MODULOS[index]
        icono_nombre = f"cia_{cia.lower()}"
        img = self._cargar_icono(icono_nombre, size=22, directorio=ASSETS_DIR)
        self.lbl_icono_cia.configure(image=img)
        self.lbl_nombre.configure(text=f"  {nombre}")
        self.lbl_cis.configure(text=cis)
        self._mostrar_widgets(build_modulo_info, index)

    def _mostrar_readme(self, index: int):
        md = leer_readme(index)
        if md is None:
            self._mostrar_widgets(lambda p: tk.Label(p, text="Este modulo no tiene documentacion aun.",
                                     bg=BG, fg=TEXTO_DIM, font=FUENTE).pack(anchor="w"))
            return
        self._mostrar_widgets(build_readme, md)
        self.viendo_readme = True

    def _restaurar(self):
        sel = self.lista.selection()
        if sel:
            self._mostrar_modulo(int(sel[0]))
        else:
            self._mostrar_dashboard()

    # ── Acciones ───────────────────────────────────────────────────────────

    def _action_setup(self):
        self._log_clear()
        self._log("[SETUP] Preparando entorno de pruebas...")
        self.runner.ejecutar(os.path.join(_DIR_RAIZ, "core", "lab_setup.py"), "Setup")

    def _action_simular(self):
        sel = self.lista.selection()
        if not sel:
            return
        idx = int(sel[0])
        _, nombre, script, _, _, _ = MODULOS[idx]
        sp = os.path.join(_DIR_RAIZ, 'modulos', nombre, f"{script}.py")
        self._log_clear()
        self._log(f"[SIMULAR] Ejecutando {nombre}...")
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
        self._log(f"[DEFENSA] Ejecutando mitigacion para {nombre}...")
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
        self._log("[CLEAN] Consola limpiada.")
        self._restaurar()

    def _action_juego(self):
        sel = self.lista.selection()
        if not sel:
            return
        idx = int(sel[0])
        _, nombre = MODULOS[idx][0], MODULOS[idx][1]
        if nombre not in DESAFIOS_POR_MODULO:
            self._log(f"[JUEGO] {nombre} no tiene desafios disponibles.")
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
