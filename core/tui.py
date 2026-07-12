#!/usr/bin/env python3
"""
TUI interactiva del Laboratorio de Malware Educativo.

Interfaz de usuario de terminal con panel dividido (split-view):
  - Panel izquierdo:  lista navegable de 14 modulos
  - Panel derecho:    metadata del modulo seleccionado (CIA, CIS, descripcion)
  - Barra inferior:   atajos de teclado visuales
  - Vista de logs:    output capturado de simulaciones y defensas

Dependencias: solo curses (estandar de Python 3).
  En Windows se necesita: pip install windows-curses

Uso:
    python -m core.tui
"""
import os
import sys
import curses
import subprocess
import textwrap
import threading
import queue
import time

# ── Rutas del proyecto ──────────────────────────────────────────────────────
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODULOS_DIR = os.path.join(ROOT, 'modulos')

# ── Base de datos de modulos ────────────────────────────────────────────────
# Cada tupla: (id, nombre_directorio, nombre_script, pilar_cia, control_cis, desc_corta)
MODULOS = [
    ("01", "ransomware",      "ransomware",
     "Disponibilidad", "CIS 11 — Recuperacion de Datos",
     "Cifrado de archivos + nota de rescate"),
    ("02", "wiper",           "wiper",
     "Disponibilidad", "CIS 10 — Copias de Seguridad",
     "Corrupcion/eliminacion permanente de archivos"),
    ("03", "keylogger",       "keylogger",
     "Confidencialidad", "CIS 3 — Proteccion de Datos",
     "Captura de pulsaciones de teclado"),
    ("04", "worm",            "worm",
     "Disponibilidad", "CIS 13 — Monitoreo y Defensa de Red",
     "Auto-replicacion entre directorios"),
    ("05", "trojan",          "trojan",
     "Integridad", "CIS 7 — Proteccion Email/Web",
     "Disfraz de legitimo + payload oculto"),
    ("06", "backdoor",        "backdoor",
     "Confidencialidad", "CIS 4 — Seguridad de Dispositivos",
     "Acceso persistente + C2 simulado"),
    ("07", "rootkit",         "rootkit",
     "Integridad", "CIS 8 — Auditoria de Cuentas",
     "Ocultacion de procesos/archivos"),
    ("08", "botnet",          "botnet",
     "Disponibilidad", "CIS 13 — Monitoreo y Defensa de Red",
     "Red de bots + DDoS simulado"),
    ("09", "steganography",   "steganography",
     "Confidencialidad", "CIS 3 — Proteccion de Datos",
     "Ocultacion de datos en imagenes (LSB)"),
    ("10", "fileless",        "fileless",
     "Integridad", "CIS 2 — Inventario de Activos",
     "Ejecucion sin archivos en disco"),
    ("11", "logic_bomb",      "logic_bomb",
     "Disponibilidad", "CIS 7 — Proteccion Email/Web",
     "Payload con detonante condicional"),
    ("12", "cryptominer",     "cryptominer",
     "Disponibilidad", "CIS 8 — Auditoria de Cuentas",
     "Mineria CPU simulada"),
    ("13", "supply_chain",    "supply_chain",
     "Integridad", "CIS 15 — Seguridad de Servidores",
     "Compromiso de dependencias"),
    ("14", "dns_tunneling",   "dns_tunneling",
     "Confidencialidad", "CIS 13 — Monitoreo y Defensa de Red",
     "Exfiltracion via consultas DNS"),
]

# ── Colores ANSI para strips de texto plano ─────────────────────────────────
# Usados al procesar el output de los subprocesos que imprimen con ANSI codes.
ANSI_COLORS = {
    '\033[0m':  '', '\033[1m':  '', '\033[91m': '', '\033[92m': '',
    '\033[93m': '', '\033[94m': '', '\033[95m': '', '\033[96m': '',
    '\033[97m': '', '\033[0;32m': '', '\033[0;33m': '', '\033[0;36m': '',
}


def strip_ansi(text):
    """Elimina secuencias de escape ANSI de un string para mostrarlo en curses."""
    import re
    ansi_re = re.compile(r'\x1b\[[0-9;]*m')
    return ansi_re.sub('', text)


# ════════════════════════════════════════════════════════════════════════════
#  CLASE PRINCIPAL: LaboratorioTUI
# ════════════════════════════════════════════════════════════════════════════
class LaboratorioTUI:
    """
    Interfaz de terminal dividida en paneles para el laboratorio.

    Layout de pantalla:
    ┌──────────────────────────────────────────────────────────┐
    │  TITULO / HEADER                                         │
    ├────────────────────┬─────────────────────────────────────┤
    │                    │                                     │
    │   LISTA DE         │   INFO DEL MODULO SELECCIONADO     │
    │   MODULOS          │   - Pilar CIA                      │
    │   (panel izq)      │   - Control CIS                    │
    │                    │   - Descripcion                     │
    │                    │                                     │
    ├────────────────────┴─────────────────────────────────────┤
    │  [Enter] Simular  [D] Defensa  [C] Limpiar  [Q] Salir  │
    └──────────────────────────────────────────────────────────┘

    Cuando se ejecuta un modulo, se sobrepone una vista de logs:
    ┌──────────────────────────────────────────────────────────┐
    │  LOG DE EJECUCION — [nombre_modulo]                      │
    ├──────────────────────────────────────────────────────────┤
    │  [output en tiempo real del subproceso]                  │
    │  ...                                                     │
    ├──────────────────────────────────────────────────────────┤
    │  [Enter] Volver   [Q] Salir                             │
    └──────────────────────────────────────────────────────────┘
    """

    def __init__(self, stdscr):
        self.stdscr = stdscr
        self.selected = 0          # Indice del modulo seleccionado
        self.log_mode = False      # True = estamos viendo logs de ejecucion
        self.log_lines = []        # Lineas de output del subproceso
        self.log_scroll = 0        # Offset de scroll en vista de logs
        self.running_proc = None   # Referencia al subproceso activo
        self.output_queue = queue.Queue()  # Cola thread-safe para output
        self.done_event = threading.Event()  # Senal de fin de subproceso

        # Configuracion inicial de curses
        curses.curs_set(0)         # Ocultar cursor
        curses.use_default_colors()# Usar colores default del terminal
        self.stdscr.keypad(True)   # Capturar teclas especiales (flechas, etc.)
        self.stdscr.timeout(-1)    # Bloquear en getch() hasta recibir input

        # Definir pares de colores
        curses.init_pair(1, curses.COLOR_CYAN, -1)     # Titulos
        curses.init_pair(2, curses.COLOR_GREEN, -1)     # Texto positivo
        curses.init_pair(3, curses.COLOR_YELLOW, -1)    # Advertencias
        curses.init_pair(4, curses.COLOR_RED, -1)       # Errores/seleccion
        curses.init_pair(5, curses.COLOR_WHITE, curses.COLOR_BLUE)  # Barra de estado
        curses.init_pair(6, curses.COLOR_BLACK, curses.COLOR_CYAN)  # Header
        curses.init_pair(7, curses.COLOR_WHITE, curses.COLOR_RED)   # Ejecutando
        curses.init_pair(8, curses.COLOR_MAGENTA, -1)   # CIS Control
        curses.init_pair(9, curses.COLOR_BLACK, curses.COLOR_GREEN) # Seleccion

    # ── Utilidades de dibujo ────────────────────────────────────────────────

    def safe_addstr(self, y, x, text, attr=0):
        """
        Escribe texto en la pantalla de forma segura.
        Si el texto no cabe, lo trunca en vez de lanzar异常.
        Esto evita errores cuando la terminal es mas chica de lo esperado.
        """
        max_y, max_x = self.stdscr.getmaxyx()
        if y < 0 or y >= max_y or x < 0 or x >= max_x:
            return
        # Truncar texto si no cabe en la linea
        available = max_x - x - 1
        if available <= 0:
            return
        text = text[:available]
        try:
            self.stdscr.addstr(y, x, text, attr)
        except curses.error:
            pass  # Ignorar errores de escritura al borde de pantalla

    def get_layout(self):
        """
        Calcula las dimensiones de cada panel basado en el tamanho de la terminal.

        Retorna: (ancho_izq, ancho_der, alto_header, alto_status, alto_log, y_log)
        """
        max_y, max_x = self.stdscr.getmaxyx()

        # El panel izquierdo ocupa ~35% del ancho, minimo 20 cols
        ancho_izq = max(20, min(35, max_x // 3))
        ancho_der = max_x - ancho_izq - 1  # -1 para el separador vertical

        alto_header = 3   # Lineas del titulo
        alto_status = 2   # Lineas de la barra de hotkeys
        alto_log = 2      # Lineas extra para el footer del log

        y_log = max_y - alto_status - alto_log

        return ancho_izq, ancho_der, alto_header, alto_status, alto_log, y_log

    # ── Dibujo de paneles ───────────────────────────────────────────────────

    def draw_header(self):
        """Dibuja la barra de titulo superior."""
        max_y, max_x = self.stdscr.getmaxyx()
        header = " E.A.S.M.L — Educational Advanced Simulation Malware Laboratory "
        # Centrar el header
        x_start = max(0, (max_x - len(header)) // 2)
        self.safe_addstr(0, 0, " " * max_x, curses.color_pair(6) | curses.A_BOLD)
        self.safe_addstr(0, x_start, header, curses.color_pair(6) | curses.A_BOLD)
        # Subtitulo
        subtitle = " Panel de Control — Laboratorio Educativo de Ciberseguridad "
        x_sub = max(0, (max_x - len(subtitle)) // 2)
        self.safe_addstr(1, 0, " " * max_x, curses.color_pair(6))
        self.safe_addstr(1, x_sub, subtitle, curses.color_pair(6))

    def draw_module_list(self, ancho):
        """
        Dibuja el panel izquierdo con la lista de modulos.

        El modulo seleccionado se resalta con fondo verde.
        Muestra el numero y nombre de cada modulo.
        """
        alto_header = 3
        alto_status = 2
        alto_log = 2
        max_y = self.stdscr.getmaxyx()[0]
        alto_disponible = max_y - alto_header - alto_status - alto_log - 1

        # Titulo del panel
        self.safe_addstr(alto_header, 1, " MODULOS ",
                         curses.color_pair(1) | curses.A_BOLD)
        self.safe_addstr(alto_header, 10, "─" * (ancho - 12),
                         curses.color_pair(1))

        # Calcular rango visible (scroll si hay mas modulos que espacio)
        start = max(0, self.selected - alto_disponible + 3)
        end = min(len(MODULOS), start + alto_disponible - 1)

        for i in range(start, end):
            num, nombre, script, cia, cis, desc = MODULOS[i]
            y = alto_header + 1 + (i - start)

            if i == self.selected:
                # Modulo seleccionado: fondo verde, texto negro
                label = f" ▸ {num}_{nombre} "
                self.safe_addstr(y, 0, " " * ancho, curses.color_pair(9))
                self.safe_addstr(y, 0, label[:ancho], curses.color_pair(9) | curses.A_BOLD)
            else:
                # Modulo normal
                label = f"   {num}_{nombre} "
                self.safe_addstr(y, 0, label[:ancho], curses.A_NORMAL)

    def draw_separator(self, ancho_izq):
        """Dibuja la linea vertical separadora entre paneles."""
        max_y = self.stdscr.getmaxyx()[0]
        for y in range(3, max_y - 3):
            self.safe_addstr(y, ancho_izq, "│",
                             curses.color_pair(1) | curses.A_DIM)

    def draw_module_info(self, x_start, ancho):
        """
        Dibuja el panel derecho con la informacion del modulo seleccionado.

        Muestra:
          - Nombre del modulo
          - Pilar CIA afectado (con indicador visual)
          - Control CIS asociado
          - Descripcion de la amenaza
          - Ruta del script
        """
        alto_header = 3
        num, nombre, script, cia, cis, desc = MODULOS[self.selected]

        # Titulo del panel
        self.safe_addstr(alto_header, x_start + 1, " INFORMACION DEL MODULO ",
                         curses.color_pair(1) | curses.A_BOLD)
        self.safe_addstr(alto_header, x_start + 25, "─" * (ancho - 27),
                         curses.color_pair(1))

        y = alto_header + 2

        # Nombre del modulo
        self.safe_addstr(y, x_start + 2, "Modulo:", curses.A_BOLD)
        self.safe_addstr(y, x_start + 12, f"{num}_{nombre} ({script}.py)")
        y += 2

        # Pilar CIA con indicador de color
        self.safe_addstr(y, x_start + 2, "Pilar CIA:", curses.A_BOLD)
        y += 1
        # Icono visual segun el pilar
        if cia == "Confidencialidad":
            icono = "🔒"
            color_cia = curses.color_pair(8)
        elif cia == "Integridad":
            icono = "🛡"
            color_cia = curses.color_pair(3)
        else:  # Disponibilidad
            icono = "⚡"
            color_cia = curses.color_pair(4)
        self.safe_addstr(y, x_start + 4, f"{cia}", color_cia | curses.A_BOLD)
        y += 2

        # Control CIS
        self.safe_addstr(y, x_start + 2, "Control CIS:", curses.A_BOLD)
        y += 1
        # Envolver texto largo del CIS control
        cis_wrapped = textwrap.wrap(cis, ancho - 8)
        for line in cis_wrapped:
            self.safe_addstr(y, x_start + 4, line, curses.color_pair(8))
            y += 1
        y += 1

        # Separador
        self.safe_addstr(y, x_start + 2, "─" * (ancho - 6), curses.A_DIM)
        y += 1

        # Descripcion
        self.safe_addstr(y, x_start + 2, "Descripcion:", curses.A_BOLD)
        y += 1
        desc_wrapped = textwrap.wrap(desc, ancho - 8)
        for line in desc_wrapped:
            self.safe_addstr(y, x_start + 4, line)
            y += 1
        y += 2

        # Ruta del script
        dir_modulo = os.path.join(MODULOS_DIR, f"{num}_{nombre}")
        script_path = os.path.join(dir_modulo, f"{script}.py")
        defensa_path = os.path.join(dir_modulo, "defensa.py")

        self.safe_addstr(y, x_start + 2, "Archivos:", curses.A_BOLD)
        y += 1
        # Verificar existencia
        sim_ok = "✓" if os.path.exists(script_path) else "✗"
        def_ok = "✓" if os.path.exists(defensa_path) else "✗"
        self.safe_addstr(y, x_start + 4,
                         f"  {sim_ok} {script}.py  (simulacion)",
                         curses.color_pair(2) if os.path.exists(script_path) else curses.color_pair(4))
        y += 1
        self.safe_addstr(y, x_start + 4,
                         f"  {def_ok} defensa.py  (defensa)",
                         curses.color_pair(2) if os.path.exists(defensa_path) else curses.color_pair(4))
        y += 2

        # Leyenda CIA
        self.safe_addstr(y, x_start + 2, "─" * (ancho - 6), curses.A_DIM)
        y += 1
        self.safe_addstr(y, x_start + 2, "Tríada CIA:", curses.A_BOLD)
        y += 1
        for pillar, icon in [("Confidencialidad", "C"), ("Integridad", "I"),
                              ("Disponibilidad", "A")]:
            activo = pillar == cia
            marca = "●" if activo else "○"
            attr = curses.A_BOLD if activo else curses.A_DIM
            self.safe_addstr(y, x_start + 4, f" {marca} {pillar} ({icon})",
                             attr)
            y += 1

    def draw_status_bar(self):
        """Dibuja la barra de atajos de teclado en la parte inferior."""
        max_y, max_x = self.stdscr.getmaxyx()
        y = max_y - 2

        # Fondo azul para toda la barra
        barra = " " * max_x
        self.safe_addstr(y, 0, barra, curses.color_pair(5))

        if self.log_mode:
            hotkeys = " [Enter] Volver  │  [Q] Salir del Laboratorio  "
        else:
            hotkeys = " [Enter] Simular  │  [D] Defensa  │  [C] Limpiar  │  [Q] Salir  "

        x_start = max(0, (max_x - len(hotkeys)) // 2)
        self.safe_addstr(y, x_start, hotkeys, curses.color_pair(5) | curses.A_BOLD)

    def draw_executing_banner(self):
        """Muestra banner animado de ejecucion en la ultima linea."""
        max_y, max_x = self.stdscr.getmaxyx()
        y = max_y - 1
        msg = " ⏳ Ejecutando... "
        x = max(0, (max_x - len(msg)) // 2)
        self.safe_addstr(y, 0, " " * max_x, curses.color_pair(7))
        self.safe_addstr(y, x, msg, curses.color_pair(7) | curses.A_BOLD | curses.A_BLINK)

    # ── Vista de logs ───────────────────────────────────────────────────────

    def draw_log_view(self):
        """
        Dibuja la vista de logs de ejecucion.

        Muestra el output capturado del subproceso en tiempo real.
        Soporta scroll con flechas arriba/abajo.
        """
        max_y, max_x = self.stdscr.getmaxyx()
        alto_header = 3
        alto_status = 2

        # Titulo del log
        num, nombre, script, cia, cis, desc = MODULOS[self.selected]
        log_title = f" LOG DE EJECUCION — {num}_{nombre} "
        self.safe_addstr(alto_header, 1, log_title,
                         curses.color_pair(7) | curses.A_BOLD)
        remaining = max_x - len(log_title) - 2
        if remaining > 0:
            self.safe_addstr(alto_header, len(log_title) + 1,
                             "─" * remaining, curses.color_pair(7))

        # Calcular area de logs
        y_start = alto_header + 1
        y_end = max_y - alto_status - 3
        alto_log = y_end - y_start

        if alto_log <= 0:
            return

        # Calcular scroll
        total_lines = len(self.log_lines)
        max_scroll = max(0, total_lines - alto_log)
        self.log_scroll = min(self.log_scroll, max_scroll)
        self.log_scroll = max(0, self.log_scroll)

        # Dibujar lineas visibles
        visible = self.log_lines[self.log_scroll:self.log_scroll + alto_log]
        for i, line in enumerate(visible):
            y = y_start + i
            # Limpiar la linea completa primero
            self.safe_addstr(y, 0, " " * (max_x - 1))
            # Escribir la linea (sin ANSI codes)
            clean = strip_ansi(line)
            # Colorear segun contenido
            if "[CIFRADO]" in line or "[ELIMINADO]" in line or "[CORROMPIDO]" in line:
                attr = curses.color_pair(4)  # Rojo
            elif "[OK]" in line or "[+] " in line or "eliminado:" in line:
                attr = curses.color_pair(2)  # Verde
            elif "[!]" in line or "ADVERTENCIA" in line:
                attr = curses.color_pair(3)  # Amarillo
            elif "FASE" in line or "===" in line:
                attr = curses.color_pair(1) | curses.A_BOLD  # Cyan bold
            else:
                attr = curses.A_NORMAL
            self.safe_addstr(y, 1, clean[:max_x - 3], attr)

        # Indicador de scroll
        if total_lines > alto_log:
            pct = int((self.log_scroll + alto_log) / total_lines * 100)
            scroll_info = f" {pct}% "
            self.safe_addstr(y_end + 1, max_x - len(scroll_info) - 1,
                             scroll_info, curses.A_DIM)

        # Footer del log
        if self.done_event.is_set():
            status = " ✓ Ejecucion completada — Presiona [Enter] para volver "
        else:
            status = " ⏳ Ejecutando... presiona [C] para cancelar "
        self.safe_addstr(y_end + 1, 0, " " * max_x, curses.color_pair(3))
        x = max(0, (max_x - len(status)) // 2)
        self.safe_addstr(y_end + 1, x, status,
                         curses.color_pair(3) | curses.A_BOLD)

    # ── Ejecucion de subprocesos ────────────────────────────────────────────

    def _run_subprocess(self, script_path, args=None):
        """
        Ejecuta un script Python como subproceso y captura su output linea a linea.

        Usa un hilo separado (thread) para leer el output sin bloquear la TUI.
        El output se envia a una cola thread-safe (queue.Queue) y se procesa
        en el ciclo principal de la interfaz.

        Args:
            script_path: Ruta absoluta al script .py a ejecutar
            args: Lista de argumentos adicionales (ej: ['--clean'])
        """
        self.log_lines = []
        self.log_scroll = 0
        self.done_event.clear()

        cmd = [sys.executable, script_path]
        if args:
            cmd.extend(args)

        def reader_thread():
            """Hilo que lee stdout/stderr del subproceso linea por linea."""
            try:
                proc = subprocess.Popen(
                    cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    cwd=ROOT,
                    universal_newlines=True,
                    bufsize=1,  # Buffering linea por linea
                )
                self.running_proc = proc

                for line in proc.stdout:
                    self.output_queue.put(line.rstrip('\n'))

                proc.wait()
                self.output_queue.put(f"\n═══ Proceso terminado (codigo: {proc.returncode}) ═══")
            except Exception as e:
                self.output_queue.put(f"\n═══ ERROR: {e} ═══")
            finally:
                self.done_event.set()
                self.running_proc = None

        t = threading.Thread(target=reader_thread, daemon=True)
        t.start()

    def _cancel_process(self):
        """Cancela el subproceso activo si esta corriendo."""
        if self.running_proc and self.running_proc.poll() is None:
            try:
                self.running_proc.terminate()
                self.log_lines.append("\n═══ Proceso cancelado por el usuario ═══")
            except Exception:
                pass
        self.done_event.set()

    def _drain_queue(self):
        """
        Drena la cola de output y agrega las lineas al buffer de logs.
        Retorna True si hay nuevas lineas (para actualizar la pantalla).
        """
        new_data = False
        while not self.output_queue.empty():
            try:
                line = self.output_queue.get_nowait()
                self.log_lines.append(line)
                new_data = True
            except queue.Empty:
                break
        return new_data

    # ── Ejecucion de acciones ───────────────────────────────────────────────

    def ejecutar_simulacion(self):
        """Prepara y ejecuta la simulacion del modulo seleccionado."""
        num, nombre, script, cia, cis, desc = MODULOS[self.selected]
        dir_modulo = os.path.join(MODULOS_DIR, f"{num}_{nombre}")
        script_path = os.path.join(dir_modulo, f"{script}.py")

        if not os.path.exists(script_path):
            self.log_lines = [f"═══ ERROR: {script_path} no encontrado ═══"]
            self.done_event.set()
            self.log_mode = True
            return

        self.log_mode = True
        self._run_subprocess(script_path)

    def ejecutar_defensa(self):
        """Prepara y ejecuta la defensa del modulo seleccionado."""
        num, nombre, script, cia, cis, desc = MODULOS[self.selected]
        dir_modulo = os.path.join(MODULOS_DIR, f"{num}_{nombre}")
        script_path = os.path.join(dir_modulo, "defensa.py")

        if not os.path.exists(script_path):
            self.log_lines = [f"═══ ERROR: {script_path} no encontrado ═══"]
            self.done_event.set()
            self.log_mode = True
            return

        self.log_mode = True
        self._run_subprocess(script_path)

    def ejecutar_clean(self):
        """Prepara y ejecuta la limpieza del modulo seleccionado."""
        num, nombre, script, cia, cis, desc = MODULOS[self.selected]
        dir_modulo = os.path.join(MODULOS_DIR, f"{num}_{nombre}")
        script_path = os.path.join(dir_modulo, f"{script}.py")

        if not os.path.exists(script_path):
            self.log_lines = [f"═══ ERROR: {script_path} no encontrado ═══"]
            self.done_event.set()
            self.log_mode = True
            return

        self.log_mode = True
        self._run_subprocess(script_path, args=['--clean'])

    # ── Loop principal ──────────────────────────────────────────────────────

    def run(self):
        """
        Loop principal de la TUI.

        Flujo:
          1. Capturar input del teclado
          2. Procesar acciones (navegar, ejecutar, salir)
          3. Drenar output del subproceso activo (si hay)
          4. Redibujar toda la pantalla
          5. Repetir

        El metodo curses.wrapper() se encarga de inicializar y restaurar
        el estado de la terminal automaticamente.
        """
        while True:
            # ── 1. Capturar input ───────────────────────────────────────
            key = self.stdscr.getch()

            # ── 2. Procesar teclas ──────────────────────────────────────
            if self.log_mode:
                # Modo log: solo permitir volver o salir
                if key == ord('q') or key == ord('Q'):
                    self._cancel_process()
                    break
                elif key == 10:  # Enter
                    if self.done_event.is_set():
                        self.log_mode = False
                        self.log_lines = []
                    else:
                        self._cancel_process()
                elif key == ord('c') or key == ord('C'):
                    self._cancel_process()
                elif key == curses.KEY_UP:
                    self.log_scroll = max(0, self.log_scroll - 1)
                elif key == curses.KEY_DOWN:
                    self.log_scroll += 1
                elif key == curses.KEY_PPAGE:  # Page Up
                    self.log_scroll = max(0, self.log_scroll - 10)
                elif key == curses.KEY_NPAGE:  # Page Down
                    self.log_scroll += 10
            else:
                # Modo navegacion
                if key == ord('q') or key == ord('Q'):
                    break
                elif key == curses.KEY_UP or key == ord('k'):
                    self.selected = max(0, self.selected - 1)
                elif key == curses.KEY_DOWN or key == ord('j'):
                    self.selected = min(len(MODULOS) - 1, self.selected + 1)
                elif key == curses.KEY_PPAGE:  # Page Up
                    self.selected = max(0, self.selected - 10)
                elif key == curses.KEY_NPAGE:  # Page Down
                    self.selected = min(len(MODULOS) - 1, self.selected + 1)
                elif key == curses.KEY_HOME:
                    self.selected = 0
                elif key == curses.KEY_END:
                    self.selected = len(MODULOS) - 1
                elif key == 10:  # Enter -> Ejecutar simulacion
                    self.ejecutar_simulacion()
                elif key == ord('d') or key == ord('D'):
                    self.ejecutar_defensa()
                elif key == ord('c') or key == ord('C'):
                    self.ejecutar_clean()

            # ── 3. Drenar output del subproceso ─────────────────────────
            if self.log_mode:
                self._drain_queue()

            # ── 4. Redibujar pantalla ──────────────────────────────────
            self.stdscr.erase()  # Limpiar buffer de pantalla completo

            if self.log_mode:
                self.draw_header()
                self.draw_log_view()
                self.draw_status_bar()
                if not self.done_event.is_set():
                    self.draw_executing_banner()
            else:
                max_y, max_x = self.stdscr.getmaxyx()
                ancho_izq, ancho_der, alto_header, alto_status, alto_log, _ = \
                    self.get_layout()

                self.draw_header()
                self.draw_module_list(ancho_izq)
                self.draw_separator(ancho_izq)
                self.draw_module_info(ancho_izq + 2, ancho_der)
                self.draw_status_bar()

            self.stdscr.refresh()

            # ── 5. Pausa breve para no consumir 100% CPU ────────────────
            # Cuando hay subproceso activo, polls mas frecuente para
            # mostrar output en tiempo real. Sin subproceso, espera
            # indefinidamente en getch() (ya configurado con timeout -1).


# ════════════════════════════════════════════════════════════════════════════
#  PUNTO DE ENTRADA
# ════════════════════════════════════════════════════════════════════════════
def main():
    """
    Punto de entrada de la TUI.

    curses.wrapper() se encarga de:
      1. Inicializar el modo curses
      2. Restaurar la terminal al salir (incluso si hay excepcion)
      3. Pasar el objeto stdscr a la funcion lambda
    """
    try:
        curses.wrapper(lambda stdscr: LaboratorioTUI(stdscr).run())
    except KeyboardInterrupt:
        pass
    finally:
        # Restaurar terminal limpio despues de salir de curses
        print("\n  Laboratorio cerrado. Ejecuta 'python -m core.tui' para reabrir.\n")


if __name__ == "__main__":
    main()
