"""TUI interactiva del Laboratorio de Malware Educativo — basada en Textual."""

import os
from textual import on
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.reactive import reactive
from textual.widgets import Footer, Header, Label, ListItem, ListView, Markdown, RichLog
from textual.containers import Horizontal, Vertical

# Módulos internos heredados y nuevos
from tui.config import MODULOS
from tui.styles import TUI_CSS
from tui.views import render_tutorial, render_dashboard, render_modulo_info
from tui.runner import run_lab_script
from tui.desafio import DesafioScreen
from tui.laboratorio import DESAFIOS_POR_MODULO

# ── Configuración de Entorno ────────────────────────────────────────────────
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODULOS_DIR = os.path.join(ROOT, 'modulos')
DIR_PRUEBAS = os.path.join(ROOT, 'directorio_pruebas')
SCRIPT_SETUP = os.path.join(ROOT, 'core', 'lab_setup.py')


class LaboratorioTUI(App):
    """Interfaz de Usuario de Terminal (TUI) para control del laboratorio."""

    BINDINGS = [
        Binding("q",      "crear_setup",        "Setup",      show=True),
        Binding("w",      "ejecutar_simulacion", "Simular",    show=True),
        Binding("e",      "ejecutar_defensa",    "Defensa",    show=True),
        Binding("r",      "explicar_modulo",     "Readme Max", show=True),
        Binding("d",      "limpiar_consola",     "Clean",      show=True),
        Binding("h",      "mostrar_tutorial",    "Tutorial",   show=True),
        Binding("escape", "confirmar_salida",    "Salir",      show=True),
        Binding("b",      "mostrar_dashboard",   "Dashboard",  show=True),
        Binding("c",      "iniciar_desafio",     "Desafío",    show=True),
        Binding("up",     "scroll_lista(-1)",    "Subir",      show=False),
        Binding("down",   "scroll_lista(1)",     "Bajar",      show=False),
    ]

    CSS = TUI_CSS
    ejecutando: reactive[bool] = reactive(False)
    leyendo_readme: reactive[bool] = reactive(False)
    viendo_tutorial: reactive[bool] = reactive(False)
    viendo_dashboard: reactive[bool] = reactive(True)

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        
        list_items = [ListItem(Label(f" {m[0]}_{m[1]}"), name=f"{m[0]}_{m[1]}") for m in MODULOS]
        
        with Horizontal():
            with Vertical(id="panel-izquierdo"):
                yield Label(" MÓDULOS ", classes="titulo-panel")
                yield ListView(*list_items, id="lista-modulos")
            with Vertical(id="panel-derecho"):
                yield Markdown(id="info-modulo")
                yield RichLog(id="consola-logs", highlight=True, markup=True, wrap=True, auto_scroll=True, max_lines=500)
                
        yield Footer()

    def on_mount(self) -> None:
        self.query_one("#lista-modulos", ListView).index = None
        self.action_mostrar_dashboard()

    # ── Manejo de Eventos Reactivos ──────────────────────────────────────

    @on(ListView.Selected)
    @on(ListView.Highlighted)
    def manejar_cambio_seleccion(self, event: ListView.Selected | ListView.Highlighted) -> None:
        if event.item is not None:
            self.viendo_tutorial = False
            self.viendo_dashboard = False
            self.leyendo_readme = False
            self.remove_class("modo-lectura")
            self.remove_class("modo-readme")
            
            lv = self.query_one("#lista-modulos", ListView)
            if lv.index is not None:
                self.query_one("#info-modulo", Markdown).update(render_modulo_info(lv.index, MODULOS_DIR))

    def _restaurar_vista_info(self) -> None:
        """Restaura la vista normal de información del módulo sin depender de un evento de interfaz."""
        self.viendo_tutorial = False
        self.viendo_dashboard = False
        self.leyendo_readme = False
        self.remove_class("modo-lectura")
        self.remove_class("modo-readme")
        lv = self.query_one("#lista-modulos", ListView)
        if lv.index is not None:
            self.query_one("#info-modulo", Markdown).update(render_modulo_info(lv.index, MODULOS_DIR))

    # ── Atajos de Teclado (Acciones) ─────────────────────────────────────

    def action_mostrar_tutorial(self) -> None:
        self.viendo_tutorial, self.viendo_dashboard = True, False
        self.leyendo_readme = False
        self.remove_class("modo-lectura")
        self.remove_class("modo-readme")
        self.query_one("#info-modulo", Markdown).update(render_tutorial())

    def action_mostrar_dashboard(self) -> None:
        self.viendo_dashboard, self.viendo_tutorial = True, False
        self.leyendo_readme = False
        self.remove_class("modo-lectura")
        self.remove_class("modo-readme")
        self.query_one("#info-modulo", Markdown).update(render_dashboard())

    def action_iniciar_desafio(self) -> None:
        lv = self.query_one("#lista-modulos", ListView)
        if lv.index is None:
            return
        num, nombre = MODULOS[lv.index][0], MODULOS[lv.index][1]
        clave = f"{num}_{nombre}"
        if clave not in DESAFIOS_POR_MODULO:
            self.query_one("#info-modulo", Markdown).update(
                f"# ⚠️ Sin desafíos\n\nEl módulo **{clave}** aún no tiene desafíos disponibles."
            )
            return
        self.push_screen(DesafioScreen(clave, dificultad="facil"))

    def action_explicar_modulo(self) -> None:
        lv = self.query_one("#lista-modulos", ListView)
        if lv.index is None or self.viendo_tutorial:
            return

        md_widget = self.query_one("#info-modulo", Markdown)
        if self.leyendo_readme:
            self._restaurar_vista_info()  # SOLUCIÓN ERROR N2: Evita pasar 'lv' directamente
            return

        num, nombre = MODULOS[lv.index][0], MODULOS[lv.index][1]
        readme_path = os.path.join(MODULOS_DIR, f"{num}_{nombre}", "README.md")
        
        if os.path.exists(readme_path):
            with open(readme_path, "r", encoding="utf-8") as f:
                self.leyendo_readme = True
                self.add_class("modo-readme")
                md_widget.update(f"# 📖 TEORÍA Y CONOCIMIENTO: {num}_{nombre}\n---\n{f.read()}")
        else:
            md_widget.update(f"# Aviso\n\nEl módulo **{num}_{nombre}** no cuenta con un archivo README.md todavía.")

    def action_crear_setup(self) -> None:
        if not self.ejecutando:
            self.run_worker(self._orquestar_setup_manual(), group="subprocess", exclusive=True)

    def action_ejecutar_simulacion(self) -> None:
        lv = self.query_one("#lista-modulos", ListView)
        if self.ejecutando or lv.index is None:
            return
        num, nombre, script = MODULOS[lv.index][0], MODULOS[lv.index][1], MODULOS[lv.index][2]
        self.run_worker(self._preparar_y_lanzar(os.path.join(MODULOS_DIR, f"{num}_{nombre}", f"{script}.py"), f"{num}_{nombre}/simulacion"), group="subprocess", exclusive=True)

    def action_ejecutar_defensa(self) -> None:
        lv = self.query_one("#lista-modulos", ListView)
        if self.ejecutando or lv.index is None:
            return
        
        num, nombre = MODULOS[lv.index][0], MODULOS[lv.index][1]
        
        # SOLUCIÓN ERROR N1: Mapeamos dinámicamente al nombre real usando NOMBRES_DEFENSA
        from tui.config import NOMBRES_DEFENSA
        nombre_defensa = NOMBRES_DEFENSA.get(num, "defensa").lower().replace(' ', '_')
        defensa_path = os.path.join(MODULOS_DIR, f"{num}_{nombre}", f"{nombre_defensa}.py")
        
        self.run_worker(self._preparar_y_lanzar(defensa_path, f"{num}_{nombre}/defensa"), group="subprocess", exclusive=True)

    def action_limpiar_consola(self) -> None:
        self.query_one("#consola-logs", RichLog).clear()
        try:
            from modulos.common.cleanup import reset_lab_environment
            reset_lab_environment()
            self.query_one("#consola-logs", RichLog).write("[bold green]🧹 Entorno limpiado desde el módulo dedicado.[/]")
        except Exception as exc:
            self.query_one("#consola-logs", RichLog).write(f"[bold red]Error al limpiar el entorno:[/] {exc}")

    def action_scroll_lista(self, direccion: int) -> None:
        """Desplaza la lista de módulos hacia arriba (-1) o abajo (+1)."""
        lv = self.query_one("#lista-modulos", ListView)
        if lv.index is None:
            lv.index = 0
        else:
            nuevo = max(0, min(len(lv.children) - 1, lv.index + direccion))
            lv.index = nuevo

    def on_mouse_scroll_up(self, event) -> None:
        """Rueda del ratón hacia arriba — desplazar lista de módulos."""
        self.action_scroll_lista(-1)

    def on_mouse_scroll_down(self, event) -> None:
        """Rueda del ratón hacia abajo — desplazar lista de módulos."""
        self.action_scroll_lista(1)

    async def action_confirmar_salida(self) -> None:
        """Muestra modal de confirmación antes de cerrar la TUI."""
        from tui.confirmacion import ConfirmacionSalida
        resultado = await self.push_screen_wait(ConfirmacionSalida())
        if resultado:
            self.exit()

    # ── Controladores Asíncronos Internos (Delegadores) ──────────────────

    async def _orquestar_setup_manual(self) -> None:
        self.ejecutando = True
        log = self.query_one("#consola-logs", RichLog)
        log.write("[bold yellow]🛠️ Ejecutando inicialización manual del entorno...[/]")
        await run_lab_script(SCRIPT_SETUP, ROOT, log)
        self.ejecutando = False

    async def _preparar_y_lanzar(self, script_path: str, label: str) -> None:
        log = self.query_one("#consola-logs", RichLog)
        if not os.path.exists(script_path):
            log.write(f"[bold red]ERROR:[/] Archivo ejecutable ausente: {script_path}")
            return

        self.ejecutando = True
        if not os.path.exists(DIR_PRUEBAS) or not os.listdir(DIR_PRUEBAS):
            log.write("[bold yellow]⚠️ 'directorio_pruebas' vacío. Autogenerando laboratorio...[/]")
            if (await run_lab_script(SCRIPT_SETUP, ROOT, log)) != 0:
                log.write("[bold red]❌ Cancelado: No se pudo preparar el escenario de pruebas.[/]")
                self.ejecutando = False
                return

        log.write(f"[bold yellow]{'='*50}[/]\n[bold yellow]Lanzando Acción:[/] {label}\n[bold yellow]{'='*50}[/]")
        rc = await run_lab_script(script_path, ROOT, log)
        log.write(f"[bold green]Proceso completado (código: {rc})[/]" if rc == 0 else f"[bold red]Proceso cerrado con anomalías (código: {rc})[/]")
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