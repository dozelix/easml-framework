"""Aplicación principal de la GUI del laboratorio."""

import os
import sys
import tkinter as tk
from tkinter import ttk, messagebox

_DIR_RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _DIR_RAIZ)

from tui.config import MODULOS, NOMBRES_DEFENSA
from tui.laboratorio import DESAFIOS_POR_MODULO
from gui.styles import *
from gui.views import dashboard, tutorial, modulo_info, leer_readme
from gui.runner import ScriptRunner
from gui.desafio import DesafioWindow


ASSETS_DIR = os.path.join(_DIR_RAIZ, 'assets', 'modulos')


class LaboratorioGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("E.A.S.M.L — Laboratorio Educativo de Malware")
        self.geometry("1280x800")
        self.minsize(960, 600)
        self.configure(bg=BG)

        self.runner = ScriptRunner(on_log=self._log, on_done=self._runner_done,
                                   on_error=lambda e: self._log(e))
        self.viendo_readme = False

        configurar_estilos()
        self._construir()
        self._mostrar_dashboard()

    # ── Layout ──────────────────────────────────────────────────────────────

    def _construir(self):
        # Panel principal horizontal
        self.pw = tk.PanedWindow(self, orient=tk.HORIZONTAL, bg=BG,
                                 sashwidth=2, sashrelief=tk.FLAT)
        self.pw.pack(fill=tk.BOTH, expand=True, padx=6, pady=6)

        # ─── Panel izquierdo: lista de módulos ──────────────────────────────
        izq = tk.Frame(self.pw, bg=BG_PANEL, width=240)
        self.pw.add(izq, minsize=180)

        tk.Label(izq, text="MÓDULOS", bg=BG_PANEL, fg=ACCENT,
                 font=FUENTE_BOLD, anchor="w").pack(fill=tk.X, padx=10, pady=(10, 2))

        self.lista = ttk.Treeview(izq, columns=("cis",), show="tree",
                                  selectmode="browse", height=22)
        self.lista.heading("#0", text="Amenaza", anchor="w")
        self.lista.column("#0", width=180)
        self.lista.column("cis", width=50, anchor="center")

        for i, m in enumerate(MODULOS):
            num, nombre, _, cia, cis, _ = m
            cis_num = cis.split("—")[0].strip() if "—" in cis else cis
            icono = {"Confidencialidad": "🔒", "Integridad": "🛡️", "Disponibilidad": "⚡"}.get(cia, "?")
            self.lista.insert("", tk.END, iid=str(i),
                              text=f" {icono}  {nombre}", values=(cis_num,))

        self.lista.pack(fill=tk.BOTH, expand=True, padx=6, pady=4)
        self.lista.bind("<<TreeviewSelect>>", self._on_seleccion)

        # ─── Panel derecho ──────────────────────────────────────────────────
        der = tk.Frame(self.pw, bg=BG)
        self.pw.add(der, minsize=500)

        # Barra de acciones
        bacc = tk.Frame(der, bg=BG, height=52)
        bacc.pack(fill=tk.X, pady=(0, 6))
        bacc.pack_propagate(False)

        btns = [
            ("   Setup   ", "#e0af68", self._action_setup),
            ("  Simular  ", "#f7768e", self._action_simular),
            ("  Defensa  ", "#7aa2f7", self._action_defensa),
            ("  Readme   ", "#bb9af7", self._action_readme),
            ("   Clean   ", "#9ece6a", self._action_clean),
            ("Dashboard  ", "#7dcfff", self._action_dashboard),
            ("   Juego   ", "#ff9e64", self._action_juego),
        ]

        for texto, color, cmd in btns:
            btn = tk.Button(bacc, text=texto, command=cmd,
                           bg=BG_PANEL, fg=color, font=FUENTE_BOLD,
                           activebackground=color, activeforeground=BG,
                           relief="flat", padx=10, pady=5, cursor="hand2")
            btn.pack(side=tk.LEFT, padx=3)
            btn.bind("<Enter>", lambda e, b=btn, c=color: b.configure(bg=c, fg=BG))
            btn.bind("<Leave>", lambda e, b=btn, c=color: b.configure(bg=BG_PANEL, fg=c))

        # Área de contenido
        self.contenido = tk.Text(der, bg=BG_PANEL, fg=TEXTO, font=FUENTE,
                                 wrap=tk.WORD, relief="flat", padx=14, pady=10,
                                 insertbackground=ACCENT, state=tk.DISABLED)
        self.contenido.pack(fill=tk.BOTH, expand=True)

        # Consola
        cf = tk.Frame(der, bg=BG, height=180)
        cf.pack(fill=tk.X, pady=(6, 0))
        cf.pack_propagate(False)

        enc = tk.Frame(cf, bg=BG)
        enc.pack(fill=tk.X)
        tk.Label(enc, text="CONSOLA", bg=BG, fg=TEXTO_DIM,
                 font=FUENTE_SM, anchor="w").pack(side=tk.LEFT)
        tk.Button(enc, text="Limpiar", command=self._log_clear,
                  bg=BG_PANEL, fg=TEXTO_DIM, font=FUENTE_SM,
                  relief="flat", padx=6, cursor="hand2").pack(side=tk.RIGHT)

        self.consola = tk.Text(cf, bg="#0a0c10", fg=VERDE, font=("JetBrains Mono", 9),
                               wrap=tk.WORD, relief="flat", padx=10, pady=6,
                               insertbackground=VERDE, state=tk.DISABLED, height=6)
        self.consola.pack(fill=tk.BOTH, expand=True)

    # ── Métodos de contenido ────────────────────────────────────────────────

    def _set_contenido(self, texto: str):
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
        self._set_contenido(dashboard())

    def _mostrar_tutorial(self):
        self.viendo_readme = False
        self._set_contenido(tutorial())

    def _mostrar_modulo(self, index: int):
        self.viendo_readme = False
        self._set_contenido(modulo_info(index))

    def _mostrar_readme(self, index: int):
        md = leer_readme(index)
        if md is None:
            self._set_contenido("⚠️ Este módulo no tiene documentación aún.")
            return
        self.viendo_readme = True
        num, nombre = MODULOS[index][0], MODULOS[index][1]
        self._set_contenido(f"📖 {nombre}\n{'-'*60}\n\n{md}")

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
        num, nombre, script = MODULOS[idx][0], MODULOS[idx][1], MODULOS[idx][2]
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

    def _action_dashboard(self):
        if self.viendo_readme:
            self._restaurar()
        self._mostrar_dashboard()

    def _action_juego(self):
        sel = self.lista.selection()
        if not sel:
            return
        idx = int(sel[0])
        num, nombre = MODULOS[idx][0], MODULOS[idx][1]
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
