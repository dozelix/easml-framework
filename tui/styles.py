"""Estilos CSS para la interfaz Textual."""

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