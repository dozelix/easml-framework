#!/usr/bin/env python3
"""
TUI interactiva del Laboratorio de Malware Educativo — basada en Textual.

Interfaz de usuario de terminal moderna con layout flexbox dinámico:
  - Panel izquierdo:  lista navegable de 14 modulos (ListView) [30% ancho]
  - Panel derecho (70% ancho):
      - Estado Normal (Inicial / Dashboard): 50% Info arriba (1fr) + 50% Logs abajo (1fr)
      - Estado Lectura (R): README expandido al 100% de la altura de la sección derecha.

Uso:
    python -m core.tui
"""
import os
import sys
import re
import asyncio

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
    Markdown,
    RichLog,
)

# ── Rutas del proyecto ──────────────────────────────────────────────────────
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODULOS_DIR = os.path.join(ROOT, 'modulos')
DIR_PRUEBAS = os.path.join(ROOT, 'directorio_pruebas')
SCRIPT_SETUP = os.path.join(ROOT, 'core', 'lab_setup.py')

# ── Base de datos de modulos ────────────────────────────────────────────────
MODULOS = [
    ("01", "ransomware",      "ransomware", "Disponibilidad", "CIS 11 — Recuperacion de Datos", "Cifrado de archivos + nota de rescate"),
    ("02", "wiper",           "wiper", "Disponibilidad", "CIS 10 — Copias de Seguridad", "Corrupcion/eliminacion permanente de archivos"),
    ("03", "keylogger",       "keylogger", "Confidencialidad", "CIS 3 — Proteccion de Datos", "Captura de pulsaciones de teclado"),
    ("04", "worm",            "worm", "Disponibilidad", "CIS 13 — Monitoreo y Defensa de Red", "Auto-replicacion entre directorios"),
    ("05", "trojan",          "trojan", "Integridad", "CIS 7 — Proteccion Email/Web", "Disfraz de legitimo + payload oculto"),
    ("06", "backdoor",        "backdoor", "Confidencialidad", "CIS 4 — Seguridad de Dispositivos", "Acceso persistente + C2 simulado"),
    ("07", "rootkit",         "rootkit", "Integridad", "CIS 8 — Auditoria de Cuentas", "Ocultacion de procesos/archivos"),
    ("08", "botnet",          "botnet", "Disponibilidad", "CIS 13 — Monitoreo y Defensa de Red", "Red de bots + DDoS simulado"),
    ("09", "steganography",   "steganography", "Confidencialidad", "CIS 3 — Proteccion de Datos", "Ocultacion de datos en imagenes (LSB)"),
    ("10", "fileless",        "fileless", "Integridad", "CIS 2 — Inventario de Activos", "Ejecucion sin archivos en disco"),
    ("11", "logic_bomb",      "logic_bomb", "Disponibilidad", "CIS 7 — Proteccion Email/Web", "Payload con detonante condicional"),
    ("12", "cryptominer",     "cryptominer", "Disponibilidad", "CIS 8 — Auditoria de Cuentas", "Mineria CPU simulada"),
    ("13", "supply_chain",    "supply_chain", "Integridad", "CIS 15 — Seguridad de Servidores", "Compromiso de dependencias"),
    ("14", "dns_tunneling",   "dns_tunneling", "Confidencialidad", "CIS 13 — Monitoreo y Defensa de Red", "Exfiltracion via consultas DNS"),
]

ANSI_RE = re.compile(r'\x1b\[[0-9;]*m')

def strip_ansi(text: str) -> str:
    return ANSI_RE.sub('', text)

def _cia_icon(cia: str) -> str:
    return {"Confidencialidad": "C", "Integridad": "I", "Disponibilidad": "A"}.get(cia, "?")

# ════════════════════════════════════════════════════════════════════════════
#  CSS DE TEXTUAL DINÁMICO — Proporción 50/50 y expansión al 100%
# ════════════════════════════════════════════════════════════════════════════
TUI_CSS = """
Screen {
    layout: horizontal;
}

#panel-izquierdo {
    width: 30%;
    min-width: 26;
    height: 100%;
    border: solid $accent;
    padding: 0 1;
}

#panel-derecho {
    width: 70%;
    height: 100%;
}

#info-modulo {
    height: 1fr;
    border: solid $accent;
    padding: 1 2;
    overflow-y: scroll;
}

#consola-logs {
    height: 1fr;
    border: solid $accent;
}

/* Cuando el modo lectura (R) está activo, expandimos la info al 100% */
Screen.modo-lectura #info-modulo {
    height: 100%;
}
Screen.modo-lectura #consola-logs {
    display: none;
}

#lista-modulos {
    height: 1fr;
    overflow-y: scroll;
}

#lista-modulos > ListItem {
    padding: 0 1;
}

#lista-modulos > ListItem.-active {
    background: $accent;
    color: $text;
}

.titulo-panel {
    text-style: bold;
    color: $accent;
    margin-bottom: 0;
}
"""

# ════════════════════════════════════════════════════════════════════════════
#  APP PRINCIPAL
# ════════════════════════════════════════════════════════════════════════════
class LaboratorioTUI(App):
    """Interfaz TUI optimizada y expansiva para E.A.S.M.L."""

    BINDINGS = [
        Binding("q",      "forzar_setup",        "Q: Setup",      show=True),
        Binding("w",      "ejecutar_simulacion", "W: Simular",    show=True),
        Binding("e",      "ejecutar_defensa",    "E: Defensa",    show=True),
        Binding("r",      "explicar_modulo",     "R: Readme Max", show=True),
        Binding("d",      "limpiar_consola",     "D: Clean",      show=True),
        Binding("h",      "mostrar_tutorial",    "H: Tutorial",   show=True),
        Binding("escape", "quit",                "Esc: Salir",    show=True),
        Binding("j",      "cursor_down",         "Abajo",         show=False),
        Binding("k",      "cursor_up",           "Arriba",        show=False),
    ]

    CSS = TUI_CSS

    ejecutando: reactive[bool] = reactive(False)
    leyendo_readme: reactive[bool] = reactive(False)
    viendo_tutorial: reactive[bool] = reactive(True)

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)

        list_items = []
        for num, nombre, _, _, _, _ in MODULOS:
            list_items.append(ListItem(Label(f" {num}_{nombre}"), name=f"{num}_{nombre}"))

        with Horizontal():
            with Vertical(id="panel-izquierdo"):
                yield Label(" MÓDULOS ", classes="titulo-panel")
                yield ListView(*list_items, id="lista-modulos")

            with Vertical(id="panel-derecho"):
                yield Markdown(id="info-modulo")
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
        """Inicialización limpia sin logs redundantes."""
        self.query_one("#lista-modulos", ListView).index = None
        self.action_mostrar_tutorial()

    # ── Contenido de las Vistas (Markdown Nativos) ───────────────────────

    def _render_dashboard_tutorial(self) -> str:
        return """
# 📊 CONTROL PANEL & TUTORIAL INICIAL
---
¡Bienvenido al **Laboratorio Educativo de Simulación Avanzada de Malware (E.A.S.M.L)**!
Este entorno interactivo te permite analizar de forma segura el comportamiento de amenazas cibernéticas y desplegar contramedidas defensivas inmediatas.

### 🎮 Controles de Navegación Rápida (Estilo MOBA)
*   `↑ / ↓` o la Rueda del Ratón: Navega por la lista de los **14 módulos** disponibles a la izquierda.
*   **`[W]` Simular:** Lanza el script del malware en un entorno controlado (`directorio_pruebas`).
*   **`[E]` Defensa:** Ejecuta el script de mitigación, remediación o auditoría para contrarrestar el ataque.
*   **`[R]` Explicar / README:** Cambia la vista superior para mostrar la teoría extendida. **Al presionarlo se expandirá ocupando toda la sección derecha**. Pulsa `R` de nuevo para volver al balance 50/50.
*   **`[Q]` Setup Lab:** Fuerza la reconstrucción e inicialización limpia de los archivos simulados.
*   **`[D]` Clean:** Limpia todos los logs generados en la consola inferior.
*   **`[H]` Tutorial:** Te trae de vuelta a este Dashboard informativo en cualquier momento.

### 🧪 ¿Cómo empezar un experimento?
1. Selecciona un módulo en la barra de la izquierda (por ejemplo, `01_ransomware`).
2. Presiona **`W`** para ver cómo actúa en tiempo real sobre la consola inferior.
3. Analiza los cambios y presiona **`E`** para desplegar las contramedidas.
4. Presiona **`R`** si necesitas sumergirte en la documentación completa del ataque.
"""

    def _render_modulo_info(self, index: int) -> str:
        if index < 0 or index >= len(MODULOS):
            return "# Error\n\n_Selecciona un módulo válido de la lista._"

        num, nombre, script, cia, cis, desc = MODULOS[index]
        icono = _cia_icon(cia)

        dir_modulo = os.path.join(MODULOS_DIR, f"{num}_{nombre}")
        sim_ok = "✓" if os.path.exists(os.path.join(dir_modulo, f"{script}.py")) else "✗"
        def_ok = "✓" if os.path.exists(os.path.join(dir_modulo, "defensa.py")) else "✗"
        md_ok = "✓" if os.path.exists(os.path.join(dir_modulo, "README.md")) else "?"

        triada_lines = []
        for pillar, letra in [("Confidencialidad", "C"), ("Integridad", "I"), ("Disponibilidad", "A")]:
            triada_lines.append(f"* **{pillar} ({letra})**" if pillar == cia else f"* {pillar} ({letra})")

        return f"""
# Módulo: {num}_{nombre} ({script}.py)

**Pilar CIA:** {cia} ({icono})  
**Control CIS:** {cis}

### Descripción:
{desc}

---
### Mapeo de Archivos:
*   **{sim_ok}** {script}.py *(W - Simulación)*
*   **{def_ok}** defensa.py *(E - Defensa)*
*   **{md_ok}** README.md *(R - Explicación)*

---
### Tríada CIA:
{chr(10).join(triada_lines)}
"""

    # ── Manejo de Eventos y Reactividad ──────────────────────────────────

    @on(ListView.Selected)
    def on_list_selected(self, event: ListView.Selected) -> None:
        self.viendo_tutorial = False
        self._actualizar_info_basica()

    @on(ListView.Highlighted)
    def on_list_highlighted(self, event: ListView.Highlighted) -> None:
        if event.item is not None:
            self.viendo_tutorial = False
            self._actualizar_info_basica()

    def _actualizar_info_basica(self) -> None:
        """Saca el modo lectura al cambiar de módulo, restaurando el layout 50/50 original."""
        self.leyendo_readme = False
        self.remove_class("modo-lectura")
        
        lv = self.query_one("#lista-modulos", ListView)
        if lv.index is not None:
            md_widget = self.query_one("#info-modulo", Markdown)
            md_widget.update(self._render_modulo_info(lv.index))
            md_widget.scroll_to(0, 0, animate=False)

    def action_cursor_up(self) -> None:
        lv = self.query_one("#lista-modulos", ListView)
        if lv.index is not None and lv.index > 0:
            lv.index -= 1
        elif lv.index is None:
            lv.index = len(MODULOS) - 1

    def action_cursor_down(self) -> None:
        lv = self.query_one("#lista-modulos", ListView)
        if lv.index is not None and lv.index < len(MODULOS) - 1:
            lv.index += 1
        elif lv.index is None:
            lv.index = 0

    # ── Lógica de los Atajos de Teclado (QWER + D + H) ───────────────────

    def action_mostrar_tutorial(self) -> None:
        """[Tecla H] Fuerza el Dashboard instructivo en formato 50/50."""
        self.viendo_tutorial = True
        self.leyendo_readme = False
        self.remove_class("modo-lectura")
        
        md_widget = self.query_one("#info-modulo", Markdown)
        md_widget.update(self._render_dashboard_tutorial())
        md_widget.scroll_to(0, 0, animate=False)

    def action_explicar_modulo(self) -> None:
        """[Tecla R] Alterna el README al 100% de la altura de la sección."""
        lv = self.query_one("#lista-modulos", ListView)
        
        if lv.index is None or self.viendo_tutorial:
            return

        md_widget = self.query_one("#info-modulo", Markdown)

        # Toggle de cerrado/abierto
        if self.leyendo_readme:
            self.leyendo_readme = False
            self.remove_class("modo-lectura")
            md_widget.update(self._render_modulo_info(lv.index))
            md_widget.scroll_to(0, 0, animate=False)
            return

        modulo = MODULOS[lv.index]
        num, nombre = modulo[0], modulo[1]
        readme_path = os.path.join(MODULOS_DIR, f"{num}_{nombre}", "README.md")
        
        if os.path.exists(readme_path):
            try:
                with open(readme_path, "r", encoding="utf-8") as f:
                    contenido = f.read()
                
                vista_readme = f"# 📖 TEORÍA Y CONOCIMIENTO: {num}_{nombre}\n---\n{contenido}"
                
                self.leyendo_readme = True
                self.add_class("modo-lectura")
                
                md_widget.update(vista_readme)
                md_widget.scroll_to(0, 0, animate=False)
            except Exception as e:
                md_widget.update(f"# Error\n\nNo se pudo leer el archivo: {e}")
        else:
            md_widget.update(f"# Aviso\n\nEl módulo **{num}_{nombre}** no cuenta con un archivo README.md todavía.")

    def _get_selected_module(self) -> tuple:
        lv = self.query_one("#lista-modulos", ListView)
        idx = lv.index if lv.index is not None else 0
        return MODULOS[idx], idx

    def action_forzar_setup(self) -> None:
        if self.ejecutando:
            return
        self.run_worker(self._reconstruir_entorno_manual(), group="subprocess", exclusive=True)

    def action_ejecutar_simulacion(self) -> None:
        if self.ejecutando:
            return
        if self.query_one("#lista-modulos", ListView).index is None:
            return
        modulo, _idx = self._get_selected_module()
        num, nombre, script, _, _, _ = modulo
        script_path = os.path.join(MODULOS_DIR, f"{num}_{nombre}", f"{script}.py")
        self.run_worker(self._verificar_entorno_y_lanzar(script_path, f"{num}_{nombre}/simulacion"), group="subprocess", exclusive=True)

    def action_ejecutar_defensa(self) -> None:
        if self.ejecutando:
            return
        if self.query_one("#lista-modulos", ListView).index is None:
            return
        modulo, _idx = self._get_selected_module()
        num, nombre, _, _, _, _ = modulo
        defensa_path = os.path.join(MODULOS_DIR, f"{num}_{nombre}", "defensa.py")
        self.run_worker(self._verificar_entorno_y_lanzar(defensa_path, f"{num}_{nombre}/defensa"), group="subprocess", exclusive=True)

    def action_limpiar_consola(self) -> None:
        log = self.query_one("#consola-logs", RichLog)
        log.clear()

    # ── Controladores Asíncronos de Procesos ──────────────────────────────

    async def _reconstruir_entorno_manual(self) -> None:
        self.ejecutando = True
        log = self.query_one("#consola-logs", RichLog)
        log.write("[bold yellow]🛠️ Ejecutando inicialización manual del entorno...[/]")
        await self._correr_setup_script(log)
        self.ejecutando = False

    async def _correr_setup_script(self, log: RichLog) -> bool:
        setup_cmd = [sys.executable, SCRIPT_SETUP]
        try:
            process_setup = await asyncio.create_subprocess_exec(
                *setup_cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.STDOUT, cwd=ROOT,
            )
            assert process_setup.stdout is not None
            while True:
                linea = await process_setup.stdout.readline()
                if not linea:
                    break
                texto = linea.decode("utf-8", errors="replace").rstrip("\n")
                if texto.strip():
                    log.write(f"[dim][Setup] {strip_ansi(texto)}[/]")
            await process_setup.wait()
            return process_setup.returncode == 0
        except Exception as e:
            log.write(f"[bold red]Error crítico de Setup:[/] {e}")
            return False

    async def _verificar_entorno_y_lanzar(self, script_path: str, label: str, args: list[str] | None = None) -> None:
        if not os.path.exists(script_path):
            log = self.query_one("#consola-logs", RichLog)
            log.write(f"[bold red]ERROR:[/] Archivo ejecutable ausente: {script_path}")
            return

        self.ejecutando = True
        log = self.query_one("#consola-logs", RichLog)

        if not os.path.exists(DIR_PRUEBAS) or not os.listdir(DIR_PRUEBAS):
            log.write("[bold yellow]⚠️ 'directorio_pruebas' vacío. Autogenerando laboratorio...[/]")
            exito = await self._correr_setup_script(log)
            if not exito:
                log.write("[bold red]❌ Cancelado: No se pudo preparar el escenario de pruebas.[/]")
                self.ejecutando = False
                return
            log.write("[bold green]✅ Escenario listo.[/]")

        log.write(f"[bold yellow]{'='*50}[/]")
        log.write(f"[bold yellow]Lanzando Acción:[/] {label}")
        log.write(f"[bold yellow]{'='*50}[/]")

        await self._run_subprocess(script_path, args)

    async def _run_subprocess(self, script_path: str, args: list[str] | None = None) -> None:
        log = self.query_one("#consola-logs", RichLog)
        cmd = [sys.executable, script_path]
        if args: cmd.extend(args)

        try:
            process = await asyncio.create_subprocess_exec(
                *cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.STDOUT, cwd=ROOT,
            )
            assert process.stdout is not None
            while True:
                raw_line = await process.stdout.readline()
                if not raw_line: break
                line = raw_line.decode("utf-8", errors="replace").rstrip("\n")
                clean = strip_ansi(line)

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
                log.write(f"[bold green]Proceso completado correctamente (código: {rc})[/]")
            else:
                log.write(f"[bold red]Proceso cerrado con anomalías (código: {rc})[/]")
        except Exception as e:
            log.write(f"[bold red]ERROR DE PROCESO:[/] {e}")
        finally:
            self.ejecutando = False

def main():
    try:
        app = LaboratorioTUI()
        app.run()
    except KeyboardInterrupt:
        pass
    finally:
        print("\n  Laboratorio cerrado correctamente.\n")

if __name__ == "__main__":
    main()