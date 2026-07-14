"""GUI gráfica del Laboratorio de Malware Educativo — basada en tkinter."""

import os
import sys
import threading
import subprocess
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
from collections import Counter

# ── Configuración de rutas ──────────────────────────────────────────────────
_DIR_RAIZ = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _DIR_RAIZ)

from tui.config import MODULOS, NOMBRES_DEFENSA
from tui.utils import strip_ansi

# ── Colores del tema oscuro ─────────────────────────────────────────────────
COLOR_BG = "#1a1b26"
COLOR_BG_PANEL = "#24283b"
COLOR_BG_HOVER = "#414868"
COLOR_BG_ACTIVO = "#7aa2f7"
COLOR_TEXTO = "#c0caf5"
COLOR_TEXTO_DIM = "#565f89"
COLOR_ACCENT = "#7aa2f7"
COLOR_VERDE = "#9ece6a"
COLOR_ROJO = "#f7768e"
COLOR_AMARILLO = "#e0af68"
COLOR_CYAN = "#7dcfff"
COLOR_MORADO = "#bb9af7"


class GUI(tk.Tk):
    """Interfaz gráfica del laboratorio con tkinter."""

    def __init__(self):
        super().__init__()
        self.title("E.A.S.M.L — Laboratorio Educativo de Malware")
        self.geometry("1200x800")
        self.minsize(900, 600)
        self.configure(bg=COLOR_BG)

        self.ejecutando = False
        self.viendo_tutorial = False
        self.viendo_dashboard = True
        self.leyendo_readme = False
        self._animacion_id = None

        self._configurar_estilos()
        self._construir_interfaz()
        self._mostrar_dashboard()

    # ── Configuración de estilos ttk ────────────────────────────────────────

    def _configurar_estilos(self):
        estilo = ttk.Style()
        estilo.theme_use("clam")

        estilo.configure("TFrame", background=COLOR_BG)
        estilo.configure("Panel.TFrame", background=COLOR_BG_PANEL)
        estilo.configure("TLabel", background=COLOR_BG, foreground=COLOR_TEXTO,
                         font=("JetBrains Mono", 10))
        estilo.configure("Titulo.TLabel", background=COLOR_BG_PANEL, foreground=COLOR_ACCENT,
                         font=("JetBrains Mono", 11, "bold"))
        estilo.configure("Modulo.TLabel", background=COLOR_BG_PANEL, foreground=COLOR_TEXTO,
                         font=("JetBrains Mono", 10))
        estilo.configure("ModuloActivo.TLabel", background=COLOR_BG_ACTIVO, foreground=COLOR_BG,
                         font=("JetBrains Mono", 10, "bold"))

        estilo.configure("Accion.TButton", background=COLOR_BG_HOVER, foreground=COLOR_TEXTO,
                         font=("JetBrains Mono", 10, "bold"), padding=(12, 8))
        estilo.map("Accion.TButton",
                    background=[("active", COLOR_ACCENT), ("disabled", COLOR_BG_HOVER)],
                    foreground=[("active", COLOR_BG), ("disabled", COLOR_TEXTO_DIM)])

        estilo.configure("Treeview", background=COLOR_BG_PANEL, foreground=COLOR_TEXTO,
                         font=("JetBrains Mono", 10), rowheight=28, fieldbackground=COLOR_BG_PANEL)
        estilo.configure("Treeview.Heading", background=COLOR_BG_HOVER, foreground=COLOR_ACCENT,
                         font=("JetBrains Mono", 10, "bold"))
        estilo.map("Treeview", background=[("selected", COLOR_BG_ACTIVO)],
                    foreground=[("selected", COLOR_BG)])

    # ── Construcción de la interfaz ─────────────────────────────────────────

    def _construir_interfaz(self):
        # Panel principal horizontal
        self.panel_principal = tk.PanedWindow(self, orient=tk.HORIZONTAL, bg=COLOR_BG,
                                              sashwidth=4, sashrelief=tk.FLAT)
        self.panel_principal.pack(fill=tk.BOTH, expand=True, padx=4, pady=4)

        # ── Panel izquierdo: Lista de módulos ───────────────────────────────
        panel_izq = tk.Frame(self.panel_principal, bg=COLOR_BG_PANEL, width=280)
        self.panel_principal.add(panel_izq, minsize=220)

        tk.Label(panel_izq, text=" MÓDULOS ", bg=COLOR_BG_PANEL, fg=COLOR_ACCENT,
                 font=("JetBrains Mono", 11, "bold"), anchor="w").pack(fill=tk.X, padx=8, pady=(8, 4))

        # Treeview para la lista de módulos
        self.lista_modulos = ttk.Treeview(panel_izq, columns=("cia",), show="tree",
                                          selectmode="browse", height=20)
        self.lista_modulos.heading("#0", text="Módulo", anchor="w")
        self.lista_modulos.column("#0", width=200)
        self.lista_modulos.column("cia", width=50, anchor="center")

        for i, m in enumerate(MODULOS):
            num, nombre, _, cia, _, _ = m
            icono = {"Confidencialidad": "🔒", "Integridad": "🛡️", "Disponibilidad": "⚡"}.get(cia, "?")
            self.lista_modulos.insert("", tk.END, iid=str(i),
                                      text=f" {num}_{nombre}", values=(icono,))

        self.lista_modulos.pack(fill=tk.BOTH, expand=True, padx=4, pady=4)
        self.lista_modulos.bind("<<TreeviewSelect>>", self._on_modulo_seleccionado)

        # ── Panel derecho: Contenido + Consola ──────────────────────────────
        panel_der = tk.Frame(self.panel_principal, bg=COLOR_BG)
        self.panel_principal.add(panel_der, minsize=500)

        # Barra de acciones
        barra_acciones = tk.Frame(panel_der, bg=COLOR_BG_PANEL, height=48)
        barra_acciones.pack(fill=tk.X, padx=4, pady=(4, 0))
        barra_acciones.pack_propagate(False)

        acciones = [
            ("[Q] Setup", self._action_setup),
            ("[W] Simular", self._action_simular),
            ("[E] Defensa", self._action_defensa),
            ("[R] Readme", self._action_readme),
            ("[D] Clean", self._action_clean),
            ("[B] Dashboard", self._action_dashboard),
            ("[H] Tutorial", self._action_tutorial),
        ]

        for texto, comando in acciones:
            btn = tk.Button(barra_acciones, text=texto, command=comando,
                           bg=COLOR_BG_HOVER, fg=COLOR_TEXTO,
                           font=("JetBrains Mono", 9, "bold"),
                           activebackground=COLOR_ACCENT, activeforeground=COLOR_BG,
                           relief=tk.FLAT, padx=10, pady=4, cursor="hand2")
            btn.pack(side=tk.LEFT, padx=4, pady=6)
            btn.bind("<Enter>", lambda e, b=btn: b.configure(bg=COLOR_ACCENT))
            btn.bind("<Leave>", lambda e, b=btn: b.configure(bg=COLOR_BG_HOVER))

        # Área de contenido (texto con scroll)
        self.contenido_texto = scrolledtext.ScrolledText(
            panel_der, bg=COLOR_BG_PANEL, fg=COLOR_TEXTO,
            font=("JetBrains Mono", 10), wrap=tk.WORD,
            insertbackground=COLOR_TEXTO, selectbackground=COLOR_ACCENT,
            relief=tk.FLAT, padx=12, pady=8, state=tk.DISABLED
        )
        self.contenido_texto.pack(fill=tk.BOTH, expand=True, padx=4, pady=4)

        # Consola de logs
        consola_frame = tk.Frame(panel_der, bg=COLOR_BG, height=150)
        consola_frame.pack(fill=tk.X, padx=4, pady=(0, 4))
        consola_frame.pack_propagate(False)

        tk.Label(consola_frame, text=" 📋 CONSOLA ", bg=COLOR_BG_PANEL, fg=COLOR_CYAN,
                 font=("JetBrains Mono", 9, "bold"), anchor="w").pack(fill=tk.X)

        self.consola = scrolledtext.ScrolledText(
            consola_frame, bg="#0d1117", fg=COLOR_VERDE,
            font=("JetBrains Mono", 9), wrap=tk.WORD,
            insertbackground=COLOR_TEXTO, relief=tk.FLAT,
            padx=8, pady=4, state=tk.DISABLED, height=6
        )
        self.consola.pack(fill=tk.BOTH, expand=True)

    # ── Métodos de contenido ────────────────────────────────────────────────

    def _set_contenido(self, texto: str):
        """Actualiza el área de contenido con texto (soporta markdown básico)."""
        self.contenido_texto.configure(state=tk.NORMAL)
        self.contenido_texto.delete("1.0", tk.END)
        self.contenido_texto.insert("1.0", texto)
        self.contenido_texto.configure(state=tk.DISABLED)

    def _log(self, mensaje: str):
        """Escribe en la consola."""
        self.consola.configure(state=tk.NORMAL)
        self.consola.insert(tk.END, mensaje + "\n")
        self.consola.see(tk.END)
        self.consola.configure(state=tk.DISABLED)

    def _log_clear(self):
        self.consola.configure(state=tk.NORMAL)
        self.consola.delete("1.0", tk.END)
        self.consola.configure(state=tk.DISABLED)

    # ── Dashboard ───────────────────────────────────────────────────────────

    def _mostrar_dashboard(self):
        self.viendo_dashboard = True
        self.viendo_tutorial = False
        self.leyendo_readme = False

        dir_lab = os.path.join(_DIR_RAIZ, 'directorio_pruebas')
        dir_logs = os.path.join(_DIR_RAIZ, 'lab_data', 'logs')

        archivos_lab = len([f for f in os.listdir(dir_lab)
                           if os.path.isfile(os.path.join(dir_lab, f))]) if os.path.isdir(dir_lab) else 0
        logs_lab = len([f for f in os.listdir(dir_logs)
                       if f.endswith('.log')]) if os.path.isdir(dir_logs) else 0

        cia_counter = Counter(m[3] for m in MODULOS)

        estado = "🟢 Activo" if archivos_lab > 0 else "🔴 Vacío"
        barra_c = "█" * cia_counter.get("Confidencialidad", 0) + "░" * (14 - cia_counter.get("Confidencialidad", 0))
        barra_i = "█" * cia_counter.get("Integridad", 0) + "░" * (14 - cia_counter.get("Integridad", 0))
        barra_a = "█" * cia_counter.get("Disponibilidad", 0) + "░" * (14 - cia_counter.get("Disponibilidad", 0))

        contenido = f"""📊 DASHBOARD — Laboratorio E.A.S.M.L

═══════════════════════════════════════════════════════════════════

  Estado: {estado} — {archivos_lab} archivos en directorio_pruebas/
  Logs:   {logs_lab} registros en lab_data/logs/

═══════════════════════════════════════════════════════════════════

  MÓDULOS POR PILAR CIA

  🔒 Confidencialidad  {cia_counter.get('Confidencialidad', 0):2d}  {barra_c}
  🛡️  Integridad         {cia_counter.get('Integridad', 0):2d}  {barra_i}
  ⚡ Disponibilidad     {cia_counter.get('Disponibilidad', 0):2d}  {barra_a}

═══════════════════════════════════════════════════════════════════

  Total: {len(MODULOS)} módulos de simulación + defensa

═══════════════════════════════════════════════════════════════════

  [Q] Setup  ·  [W] Simular  ·  [E] Defensa  ·  [R] Readme
  [D] Clean  ·  [B] Dashboard ·  [H] Tutorial"""
        self._set_contenido(contenido)

    # ── Tutorial ────────────────────────────────────────────────────────────

    def _mostrar_tutorial(self):
        self.viendo_tutorial = True
        self.viendo_dashboard = False
        self.leyendo_readme = False

        contenido = """🎓 TUTORIAL RÁPIDO — Laboratorio E.A.S.M.L

═══════════════════════════════════════════════════════════════════

  PASO 1: BIENVENIDA

  ¡Bienvenido al Laboratorio Educativo de Simulación Avanzada de Malware!
  Este laboratorio te permite ejecutar 14 tipos de amenazas de forma segura
  y controlada, dentro de un entorno aislado (directorio_pruebas/).
  Todo es una simulación educativa — NO se genera malware real.

═══════════════════════════════════════════════════════════════════

  PASO 2: ¿CÓMO FUNCIONA?

  El flujo es simple:

  Preparar → Simular → Defender → Limpiar

  1. Preparas el entorno con archivos de prueba ([Q])
  2. Seleccionas un módulo de la lista izquierda (clic o flechas)
  3. Simulas el ataque con [W]
  4. Defiendes con [E] para ver cómo se mitiga
  5. Limpias todo con [D]

═══════════════════════════════════════════════════════════════════

  PASO 3: CONTROLES PASO A PASO

  [Q] Setup    — Genera 12 archivos de prueba en directorio_pruebas/
                  Ejecútalo ANTES de simular por primera vez.

  [W] Simular  — Ejecuta el script de simulación del módulo seleccionado.
                  Verás en tiempo real cómo el malware afecta los archivos.

  [E] Defensa  — Ejecuta el script de defensa del mismo módulo.
                  Detecta artefactos, los analiza y restaura el entorno.

  [R] Readme   — Expande el README del módulo para leer la teoría completa
                  (historia, Tríada CIA, Controles CIS, ejercicios).

  [D] Clean    — Vacía la consola y restablece el entorno de pruebas.

  [B] Dashboard — Muestra el panel de control con datos reales del lab.

  [H] Tutorial — Regresa a este tutorial en cualquier momento.

  [ESC] Salir  — Abre una ventana de confirmación para cerrar la GUI.

═══════════════════════════════════════════════════════════════════

  PASO 4: LISTO PARA EMPEZAR

  Selecciona un módulo de la lista izquierda y presiona [Q] para preparar.
  Luego [W] para simular, y [E] para defenderte.

  > Recuerda: Puedes volver a este tutorial con [H]."""
        self._set_contenido(contenido)

    # ── Info de módulo ──────────────────────────────────────────────────────

    def _mostrar_modulo(self, index: int):
        if index < 0 or index >= len(MODULOS):
            return

        self.viendo_tutorial = False
        self.viendo_dashboard = False
        self.leyendo_readme = False

        num, nombre, script, cia, cis, url_ref = MODULOS[index]
        nombre_defensa = NOMBRES_DEFENSA.get(num, "defensa")
        icono_cia = {"Confidencialidad": "🔒 C", "Integridad": "🛡️ I", "Disponibilidad": "⚡ A"}.get(cia, "?")

        dir_modulo = os.path.join(_DIR_RAIZ, 'modulos', f"{num}_{nombre}")
        sim_ok = "🟢" if os.path.exists(os.path.join(dir_modulo, f"{script}.py")) else "🔴"
        def_ok = "🟢" if os.path.exists(os.path.join(dir_modulo, f"{nombre_defensa.lower().replace(' ', '_')}.py")) else "🔴"
        md_ok = "🟢" if os.path.exists(os.path.join(dir_modulo, "README.md")) else "🟡"

        contenido = f"""🔍 ANÁLISIS DE MÓDULO: {num}_{nombre}

═══════════════════════════════════════════════════════════════════

  🛡️  CLASIFICACIÓN DE SEGURIDAD

  Tríada CIA:        {icono_cia} ({cia})
  Control CIS:       {cis}

═══════════════════════════════════════════════════════════════════

  📂 ESTADO DE COMPONENTES

  {sim_ok}  {script}.py          (Tecla [W] — Simular ataque)
  {def_ok}  {nombre_defensa.lower().replace(' ', '_')}.py  (Tecla [E] — Defensa)
  {md_ok}  README.md            (Tecla [R] — Documentación)

═══════════════════════════════════════════════════════════════════

  🌐 DOCUMENTACIÓN DE REFERENCIA

  Consulta la documentación oficial para profundizar:
  {url_ref}"""
        self._set_contenido(contenido)

    # ── README expandido ────────────────────────────────────────────────────

    def _mostrar_readme(self, index: int):
        if index < 0 or index >= len(MODULOS):
            return

        num, nombre = MODULOS[index][0], MODULOS[index][1]
        readme_path = os.path.join(_DIR_RAIZ, 'modulos', f"{num}_{nombre}", "README.md")

        if os.path.exists(readme_path):
            with open(readme_path, "r", encoding="utf-8") as f:
                contenido = f.read()
            self.leyendo_readme = True
            self.viendo_tutorial = False
            self.viendo_dashboard = False
            self._set_contenido(f"📖 TEORÍA Y CONOCIMIENTO: {num}_{nombre}\n{'='*70}\n\n{contenido}")
        else:
            self._set_contenido(f"⚠️ El módulo {num}_{nombre} no tiene README.md todavía.")

    # ── Acciones de botones ─────────────────────────────────────────────────

    def _action_setup(self):
        if self.ejecutando:
            return
        self._log_clear()
        self._log("⚙️ Preparando entorno de pruebas...")
        self._ejecutar_script("core/lab_setup.py", "Setup")

    def _action_simular(self):
        sel = self.lista_modulos.selection()
        if not sel or self.ejecutando:
            return
        idx = int(sel[0])
        num, nombre, script = MODULOS[idx][0], MODULOS[idx][1], MODULOS[idx][2]
        script_path = os.path.join(_DIR_RAIZ, 'modulos', f"{num}_{nombre}", f"{script}.py")
        self._log_clear()
        self._log(f"🦠 Simulando {num}_{nombre}...")
        self._ejecutar_script(script_path, f"{num}_{nombre}/simulacion")

    def _action_defensa(self):
        sel = self.lista_modulos.selection()
        if not sel or self.ejecutando:
            return
        idx = int(sel[0])
        num, nombre = MODULOS[idx][0], MODULOS[idx][1]
        nombre_defensa = NOMBRES_DEFENSA.get(num, "defensa")
        script_path = os.path.join(_DIR_RAIZ, 'modulos', f"{num}_{nombre}",
                                   f"{nombre_defensa.lower().replace(' ', '_')}.py")
        self._log_clear()
        self._log(f"🛡️ Ejecutando defensa de {num}_{nombre}...")
        self._ejecutar_script(script_path, f"{num}_{nombre}/defensa")

    def _action_readme(self):
        sel = self.lista_modulos.selection()
        if not sel:
            return
        idx = int(sel[0])
        if self.leyendo_readme:
            self._restaurar_vista()
        else:
            self._mostrar_readme(idx)

    def _action_clean(self):
        self._log_clear()
        self._log("🧹 Limpiando entorno...")
        self._restaurar_vista()
        self._set_contenido("🧹 Consola limpiada. Presiona [Q] para preparar el entorno.")

    def _action_dashboard(self):
        self._mostrar_dashboard()

    def _action_tutorial(self):
        self._mostrar_tutorial()

    def _restaurar_vista(self):
        self.viendo_tutorial = False
        self.viendo_dashboard = False
        self.leyendo_readme = False
        sel = self.lista_modulos.selection()
        if sel:
            self._mostrar_modulo(int(sel[0]))
        else:
            self._mostrar_dashboard()

    # ── Eventos ─────────────────────────────────────────────────────────────

    def _on_modulo_seleccionado(self, event):
        sel = self.lista_modulos.selection()
        if sel:
            idx = int(sel[0])
            self._mostrar_modulo(idx)

    def on_closing(self):
        if messagebox.askyesno("Salir", "¿Seguro que quieres salir del laboratorio?"):
            self.destroy()

    # ── Ejecución de scripts ────────────────────────────────────────────────

    def _ejecutar_script(self, script_path: str, etiqueta: str):
        self.ejecutando = True

        def _hilo():
            try:
                proc = subprocess.run(
                    [sys.executable, script_path],
                    capture_output=True, text=True, cwd=_DIR_RAIZ, timeout=120
                )
                salida = proc.stdout + proc.stderr
                self.after(0, lambda: self._procesar_salida(salida, etiqueta))
            except subprocess.TimeoutExpired:
                self.after(0, lambda: self._log(f"⏱️ Timeout en {etiqueta} (120s)"))
            except Exception as e:
                self.after(0, lambda: self._log(f"❌ Error: {e}"))
            finally:
                self.after(0, lambda: setattr(self, 'ejecutando', False))

        threading.Thread(target=_hilo, daemon=True).start()

    def _procesar_salida(self, salida: str, etiqueta: str):
        limpia = strip_ansi(salida)
        for linea in limpia.strip().split("\n"):
            if linea.strip():
                self._log(linea)
        self._log(f"✅ {etiqueta} completado.\n")


def main():
    app = GUI()
    app.protocol("WM_DELETE_WINDOW", app.on_closing)
    app.mainloop()


if __name__ == "__main__":
    main()
