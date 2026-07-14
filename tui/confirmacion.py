"""Modal de confirmación para prevenir cierre accidental de la TUI."""

from textual.app import ComposeResult
from textual.screen import ModalScreen
from textual.widgets import Button, Label, Static
from textual.containers import Vertical


class ConfirmacionSalida(ModalScreen[bool]):
    """Pantalla modal que pregunta si el usuario quiere salir."""

    CSS = """
    ConfirmacionSalida {
        align: center middle;
    }

    #dialogo-salida {
        width: 50;
        height: auto;
        max-height: 12;
        border: thick $accent;
        background: $surface;
        padding: 1 2;
    }

    #dialogo-salida Label {
        text-align: center;
        width: 100%;
        margin-bottom: 1;
    }

    #dialogo-salida Horizontal {
        width: 100%;
        align: center middle;
        height: auto;
    }

    #dialogo-salida Button {
        min-width: 12;
        margin: 0 1;
    }
    """

    def compose(self) -> ComposeResult:
        with Vertical(id="dialogo-salida"):
            yield Static("⚠️  ¿Seguro que quieres salir del laboratorio?")
            with Horizontal():
                yield Button("Sí, salir [Y]", id="btn-si", variant="error")
                yield Button("No, quedarme [N]", id="btn-no", variant="primary")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn-si":
            self.dismiss(True)
        else:
            self.dismiss(False)

    def on_key(self, event) -> None:
        if event.key == "y":
            self.dismiss(True)
        elif event.key == "n" or event.key == "escape":
            self.dismiss(False)
