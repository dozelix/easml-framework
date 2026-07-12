#!/usr/bin/env python3
"""
TUI interactiva del Laboratorio de Malware Educativo — basada en Textual.

Interfaz de usuario de terminal moderna con layout flexbox:
  - Panel izquierdo:  lista navegable de 14 modulos (ListView)
  - Panel derecho superior: metadata del modulo seleccionado (CIA, CIS, desc)
  - Panel derecho inferior: consola de logs con output en tiempo real (RichLog)
  - Barra inferior:   Footer nativo de Textual con atajos de teclado

Dependencias:
  pip install textual

Uso:
    python -m core.tui
"""
import os
import sys
import re
import asyncio
import textwrap

from textual import on
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, Vertical
from textual.reactive import reactive
from textual.widgets import (
    Footer,
    Header,
    Label,
    ListItem,
    ListView,
    RichLog,
    Static,
)

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

# ── Regex para limpiar ANSI codes ──────────────────────────────────────────
ANSI_RE = re.compile(r'\x1b\[[0-9;]*m')


def strip_ansi(text: str) -> str:
    """Elimina secuencias de escape ANSI de un string."""
    return ANSI_RE.sub('', text)


def _cia_icon(cia: str) -> str:
    """Retorna un simbolo visual segun el pilar CIA."""
    return {"Confidencialidad": "C", "Integridad": "I", "Disponibilidad": "A"}.get(cia, "?")


# ════════════════════════════════════════════════════════════════════════════
#  CSS DE TEXTUAL — Estilos declarativos para el layout
# ════════════════════════════════════════════════════════════════════════════
TUI_CSS = """
Screen {
    layout: horizontal;
}

#panel-izquierdo {
    width: 30%;
    min-width: 24;
    height: 100%;
    border: solid $accent;
    padding: 0 1;
}

#panel-derecho {
    width: 1fr;
    height: 100%;
}

#info-modulo {
    height: 2fr;
    border: solid $accent;
    padding: 1 2;
}

#consola-logs {
    height: 3fr;
    border: solid $accent;
}

/* ── Lista de modulos ─────────────────────────────────────── */
#lista-modulos {
    height: 1fr;
}

#lista-modulos > ListItem {
    padding: 0 1;
}

#lista-modulos > ListItem.-active {
    background: $accent;
    color: $text;
}

/* ── Header del panel izquierdo ────────────────────────────── */
.titulo-panel {
    text-style: bold;
    color: $accent;
    margin-bottom: 0;
}

/* ── Campo de info ─────────────────────────────────────────── */
.campo-label {
    text-style: bold;
    color: $accent;
}
"""


# ════════════════════════════════════════════════════════════════════════════
#  APP PRINCIPAL
# ════════════════════════════════════════════════════════════════════════════
class LaboratorioTUI(App):
    """
    Interfaz TUI para el Laboratorio de Malware Educativo.

    Layout:
    ┌────────────────────┬─────────────────────────────────────┐
    │  TITULO / HEADER                                         │
    ├────────────────────┬─────────────────────────────────────┤
    │                    │  INFO DEL MODULO SELECCIONADO       │
    │   LISTA DE         │  - Pilar CIA                       │
    │   MODULOS          │  - Control CIS                     │
    │   (ListView)       │  - Descripcion                     │
    │                    ├─────────────────────────────────────┤
    │                    │  CONSOLA DE LOGS (RichLog)          │
    │                    │  [output en tiempo real]            │
    ├────────────────────┴─────────────────────────────────────┤
    │  [Enter] Simular  [D] Defensa  [C] Limpiar  [Q] Salir  │
    └──────────────────────────────────────────────────────────┘
    """

    # ── Atajos de teclado ────────────────────────────────────────────────
    BINDINGS = [
        Binding("enter", "ejecutar_simulacion", "Simular", show=True),
        Binding("d",     "ejecutar_defensa",    "Defensa", show=True),
        Binding("c",     "ejecutar_clean",      "Limpiar", show=True),
        Binding("q",     "quit",                "Salir",   show=True),
        Binding("j",     "cursor_down",  "Abajo",  show=False, key_display="↓"),
        Binding("k",     "cursor_up",    "Arriba", show=False, key_display="↑"),
    ]

    # ── CSS ──────────────────────────────────────────────────────────────
    CSS = TUI_CSS

    # ── Estado reactivo ──────────────────────────────────────────────────
    # El indice seleccionado se observa para actualizar el panel de info
    selected_index: reactive[int] = reactive(0)
    # Flag para indicar si un subproceso esta corriendo
    ejecutando: reactive[bool] = reactive(False)

    def compose(self) -> ComposeResult:
        """
        Construye el arbol de widgets de la interfaz.

        Estructura:
          Header
          Horizontal
            Vertical (panel-izquierdo)
              Label (titulo)
              ListView (lista de modulos)
            Vertical (panel-derecho)
              Static (info del modulo)
              RichLog (consola de logs)
          Footer
        """
        yield Header(show_clock=True)

        # ── Construir items de la lista ──────────────────────────────────
        list_items = []
        for num, nombre, script, _cia, _cis, _desc in MODULOS:
            list_items.append(
                ListItem(Label(f" {num}_{nombre}"), name=f"{num}_{nombre}")
            )

        with Horizontal():
            # ── Panel izquierdo: lista de modulos ────────────────────────
            with Vertical(id="panel-izquierdo"):
                yield Label(" MODULOS ", classes="titulo-panel")
                yield ListView(*list_items, id="lista-modulos")

            # ── Panel derecho ────────────────────────────────────────────
            with Vertical(id="panel-derecho"):
                yield Static(
                    self._render_modulo_info(0),
                    id="info-modulo",
                )
                yield RichLog(
                    id="consola-logs",
                    highlight=True,
                    markup=True,
                    wrap=True,
                    auto_scroll=True,
                    max_lines=500,
                )

        yield Footer()

    def on_mount(self) -> None:
        """
        Se ejecuta despues de montar la interfaz.
        Verifica si existe el directorio de pruebas y muestra advertencia.
        """
        lab_dir = os.path.join(ROOT, 'directorio_pruebas')
        log = self.query_one("#consola-logs", RichLog)
        log.write("[bold cyan]E.A.S.M.L — Educational Advanced Simulation Malware Laboratory[/]")
        log.write("[dim]Panel de Control — Laboratorio Educativo de Ciberseguridad[/]")
        log.write("")

        if not os.path.isdir(lab_dir):
            log.write(
                "[bold yellow]ADVERTENCIA:[/] No se encontro el directorio de pruebas "
                f"[bold]{lab_dir}[/]."
            )
            log.write(
                "[dim]Ejecuta [bold]python core/lab_setup.py[/bold] para generar "
                "los archivos de prueba antes de usar las simulaciones.[/]"
            )
        else:
            # Contar archivos de prueba
            count = sum(1 for f in os.listdir(lab_dir)
                        if os.path.isfile(os.path.join(lab_dir, f)))
            log.write(
                f"[green]Directorio de pruebas encontrado:[/] {count} archivos"
            )

        log.write("[dim]Presiona [bold]Enter[/bold] para simular, "
                  "[bold]D[/bold] para defensa, [bold]C[/bold] para limpiar[/]")
        log.write("")

    # ── Renderizado del panel de info ────────────────────────────────────

    def _render_modulo_info(self, index: int) -> str:
        """
        Genera el texto formateado para el panel de info del modulo.

        Retorna un string con formato Rich markup para el widget Static.
        """
        if index < 0 or index >= len(MODULOS):
            return "[dim]Selecciona un modulo[/]"

        num, nombre, script, cia, cis, desc = MODULOS[index]
        icono = _cia_icon(cia)

        # Verificar existencia de archivos
        dir_modulo = os.path.join(MODULOS_DIR, f"{num}_{nombre}")
        script_path = os.path.join(dir_modulo, f"{script}.py")
        defensa_path = os.path.join(dir_modulo, "defensa.py")
        sim_ok = "[green]v[/]" if os.path.exists(script_path) else "[red]x[/]"
        def_ok = "[green]v[/]" if os.path.exists(defensa_path) else "[red]x[/]"

        # Indicadores de la triada CIA
        triada_lines = []
        for pillar, letra in [("Confidencialidad", "C"), ("Integridad", "I"),
                              ("Disponibilidad", "A")]:
            if pillar == cia:
                triada_lines.append(f"  [bold green]* {pillar} ({letra})[/]")
            else:
                triada_lines.append(f"  [dim]  {pillar} ({letra})[/]")

        lines = [
            f"[bold cyan]Modulo:[/] {num}_{nombre} [dim]({script}.py)[/]",
            "",
            f"[bold cyan]Pilar CIA:[/] [bold]{cia}[/] ({icono})",
            f"[bold cyan]Control CIS:[/] {cis}",
            "",
            "[bold cyan]Descripcion:[/]",
            f"  {desc}",
            "",
            "─" * 40,
            "[bold cyan]Archivos:[/]",
            f"  {sim_ok} {script}.py  [dim](simulacion)[/]",
            f"  {def_ok} defensa.py  [dim](defensa)[/]",
            "",
            "─" * 40,
            "[bold cyan]Triada CIA:[/]",
            *triada_lines,
        ]

        return "\n".join(lines)

    def _actualizar_info(self) -> None:
        """Actualiza el panel de info del modulo seleccionado."""
        info = self.query_one("#info-modulo", Static)
        info.update(self._render_modulo_info(self.selected_index))

    # ── Evento de seleccion en ListView ──────────────────────────────────

    @on(ListView.Selected)
    def on_list_selected(self, event: ListView.Selected) -> None:
        """
        Se dispara cuando el usuario selecciona un modulo en la lista.
        Actualiza el panel de info y registra en la consola.
        """
        self.selected_index = event.index

    @on(ListView.Highlighted)
    def on_list_highlighted(self, event: ListView.Highlighted) -> None:
        """
        Se dispara cuando se resalta un item (flechas arriba/abajo).
        Actualiza el panel de info sin cambiar el indice seleccionado.
        """
        if event.item is not None and event.index is not None:
            info = self.query_one("#info-modulo", Static)
            info.update(self._render_modulo_info(event.index))

    # ── Acciones de teclado ──────────────────────────────────────────────

    def action_cursor_up(self) -> None:
        """Mueve el cursor un item hacia arriba en la lista."""
        lv = self.query_one("#lista-modulos", ListView)
        if lv.index is not None and lv.index > 0:
            lv.index = lv.index - 1

    def action_cursor_down(self) -> None:
        """Mueve el cursor un item hacia abajo en la lista."""
        lv = self.query_one("#lista-modulos", ListView)
        total = len(MODULOS)
        if lv.index is not None and lv.index < total - 1:
            lv.index = lv.index + 1

    # ── Ejecucion de modulos ─────────────────────────────────────────────

    def _get_selected_module(self) -> tuple:
        """Retorna la tupla del modulo actualmente seleccionado."""
        lv = self.query_one("#lista-modulos", ListView)
        idx = lv.index if lv.index is not None else 0
        return MODULOS[idx], idx

    def action_ejecutar_simulacion(self) -> None:
        """Ejecuta la simulacion del modulo seleccionado."""
        if self.ejecutando:
            return
        modulo, _idx = self._get_selected_module()
        num, nombre, script, _cia, _cis, _desc = modulo
        script_path = os.path.join(MODULOS_DIR, f"{num}_{nombre}", f"{script}.py")
        self._ejecutar_script(script_path, f"{num}_{nombre}/simulacion")

    def action_ejecutar_defensa(self) -> None:
        """Ejecuta la defensa del modulo seleccionado."""
        if self.ejecutando:
            return
        modulo, _idx = self._get_selected_module()
        num, nombre, _script, _cia, _cis, _desc = modulo
        defensa_path = os.path.join(MODULOS_DIR, f"{num}_{nombre}", "defensa.py")
        self._ejecutar_script(defensa_path, f"{num}_{nombre}/defensa")

    def action_ejecutar_clean(self) -> None:
        """Ejecuta la limpieza del modulo seleccionado (--clean)."""
        if self.ejecutando:
            return
        modulo, _idx = self._get_selected_module()
        num, nombre, script, _cia, _cis, _desc = modulo
        script_path = os.path.join(MODULOS_DIR, f"{num}_{nombre}", f"{script}.py")
        self._ejecutar_script(script_path, f"{num}_{nombre}/clean", args=["--clean"])

    def _ejecutar_script(
        self, script_path: str, label: str, args: list[str] | None = None
    ) -> None:
        """
        Inicia la ejecucion asincrona de un script Python como subproceso.

        No bloquea la interfaz. El output se captura linea a linea y se
        muestra en el RichLog en tiempo real.

        Args:
            script_path: Ruta absoluta al script .py
            label: Etiqueta descriptiva para el log
            args: Argumentos adicionales (ej: ['--clean'])
        """
        if not os.path.exists(script_path):
            log = self.query_one("#consola-logs", RichLog)
            log.write(f"[bold red]ERROR:[/] Script no encontrado: {script_path}")
            return

        self.ejecutando = True
        log = self.query_one("#consola-logs", RichLog)
        log.write(f"[bold yellow]{'='*50}[/]")
        log.write(f"[bold yellow]Ejecutando:[/] {label}")
        log.write(f"[dim]{script_path}{' ' + ' '.join(args) if args else ''}[/]")
        log.write(f"[bold yellow]{'='*50}[/]")

        self.run_worker(
            self._run_subprocess(script_path, args),
            group="subprocess",
            exclusive=True,
        )

    async def _run_subprocess(
        self, script_path: str, args: list[str] | None = None
    ) -> None:
        """
        Ejecuta un subproceso de forma asincrona y escribe su output al RichLog.

        Lee stdout/stderr linea por linea y las escribe inmediatamente
        en el panel de logs para mostrar progreso en tiempo real.
        """
        log = self.query_one("#consola-logs", RichLog)
        cmd = [sys.executable, script_path]
        if args:
            cmd.extend(args)

        try:
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.STDOUT,
                cwd=ROOT,
            )

            # Leer output linea por linea
            assert process.stdout is not None
            while True:
                raw_line = await process.stdout.readline()
                if not raw_line:
                    break
                line = raw_line.decode("utf-8", errors="replace").rstrip("\n")
                clean = strip_ansi(line)

                # Colorizar segun contenido
                if any(tag in line for tag in ("[CIFRADO]", "[ELIMINADO]", "[CORROMPIDO]")):
                    log.write(f"[red]{clean}[/]")
                elif any(tag in line for tag in ("[OK]", "[+] ", "eliminado:", "CREADO")):
                    log.write(f"[green]{clean}[/]")
                elif any(tag in line for tag in ("[!]", "ADVERTENCIA", "ERROR")):
                    log.write(f"[yellow]{clean}[/]")
                elif "FASE" in line or "===" in line:
                    log.write(f"[bold cyan]{clean}[/]")
                elif clean.strip():
                    log.write(clean)

            await process.wait()
            rc = process.returncode
            if rc == 0:
                log.write(f"[bold green]Proceso terminado (codigo: {rc})[/]")
            else:
                log.write(f"[bold red]Proceso terminado con error (codigo: {rc})[/]")

        except Exception as e:
            log.write(f"[bold red]ERROR:[/] {e}")
        finally:
            self.ejecutando = False


# ════════════════════════════════════════════════════════════════════════════
#  PUNTO DE ENTRADA
# ════════════════════════════════════════════════════════════════════════════
def main():
    """
    Punto de entrada de la TUI.

    Ejecuta la aplicacion Textual. La terminal se restaura automaticamente
    al salir (incluso con Ctrl+C o excepciones).
    """
    try:
        app = LaboratorioTUI()
        app.run()
    except KeyboardInterrupt:
        pass
    finally:
        print("\n  Laboratorio cerrado. Ejecuta 'python -m core.tui' para reabrir.\n")


if __name__ == "__main__":
    main()
