"""Pantalla de desafío interactivo para la TUI."""

import time
from textual import on, work
from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, Vertical
from textual.screen import ModalScreen
from textual.widgets import Button, Label, Markdown, ProgressBar, Static

from tui.laboratorio import LaboratorioInteractivo, DESAFIOS_POR_MODULO, CONFIG_DIFICULTADES


class DesafioScreen(ModalScreen[None]):
    """Pantalla modal de desafío interactivo."""

    CSS = """
    DesafioScreen {
        align: center middle;
    }
    #dialogo-desafio {
        width: 90%;
        height: 90%;
        background: $surface;
        border: solid $accent;
        padding: 1 2;
    }
    #titulo-desafio {
        text-style: bold;
        color: $accent;
        width: 100%;
        text-align: center;
        margin-bottom: 1;
    }
    #texto-pregunta {
        width: 100%;
        height: auto;
        min-height: 3;
        margin-bottom: 1;
    }
    #info-dificultad {
        color: $warning;
        width: 100%;
        margin-bottom: 1;
    }
    .botones-opciones {
        width: 100%;
        height: auto;
    }
    .botones-opciones Button {
        width: 100%;
        margin: 0 0 1 0;
    }
    #mensaje-resultado {
        width: 100%;
        min-height: 3;
        margin-top: 1;
    }
    #barra-progreso {
        width: 100%;
        margin-top: 1;
    }
    """

    BINDINGS = [
        Binding("escape", "cancelar", "Volver"),
    ]

    def __init__(self, modulo_key: str, dificultad: str = "facil"):
        super().__init__()
        self.modulo_key = modulo_key
        self.dificultad = dificultad
        self.motor = LaboratorioInteractivo()
        self.motor.dificultad = dificultad
        self.desafios = DESAFIOS_POR_MODULO.get(modulo_key, [])
        self.indice_actual = 0
        self.correctas = 0
        self.pistas_usadas = 0
        self.intentos_fallidos = 0
        self.tiempo_inicio = 0.0
        self.respondiendo = False

    def compose(self) -> ComposeResult:
        config = CONFIG_DIFICULTADES[self.dificultad]
        with Vertical(id="dialogo-desafio"):
            yield Label(f"🎯 DESAFÍO: {self.modulo_key}", id="titulo-desafio")
            yield Label(
                f"Dificultad: {config['nombre']} — {config['descripcion']}",
                id="info-dificultad"
            )
            yield Label(
                f"Preguntas: {len(self.desafios)} — Pistas: {config['max_pistas']} — Reintentos: {config['max_intentos']}",
                id="info-reglas"
            )
            yield Label("", id="texto-pregunta")
            with Vertical(id="contenedor-opciones", classes="botones-opciones"):
                yield Button("Opción 1", id="opt-0", variant="default")
                yield Button("Opción 2", id="opt-1", variant="default")
                yield Button("Opción 3", id="opt-2", variant="default")
                yield Button("Opción 4", id="opt-3", variant="default")
            yield Button("💡 Pedir pista", id="btn-pista", variant="warning")
            yield Label("", id="mensaje-resultado")
            yield ProgressBar(total=len(self.desafios), show_eta=False, id="barra-progreso")

    def on_mount(self):
        self.tiempo_inicio = time.time()
        self._mostrar_desafio()

    def _mostrar_desafio(self):
        if self.indice_actual >= len(self.desafios):
            self._finalizar_desafio()
            return

        desafio = self.desafios[self.indice_actual]
        self.query_one("#texto-pregunta", Label).update(
            f"Pregunta {self.indice_actual + 1}/{len(self.desafios)}:\n\n{desafio.pregunta}"
        )
        self.query_one("#mensaje-resultado", Label).update("")

        for i, btn_id in enumerate(["opt-0", "opt-1", "opt-2", "opt-3"]):
            btn = self.query_one(f"#{btn_id}", Button)
            if i < len(desafio.opciones):
                btn.label = desafio.opciones[i]
                btn.disabled = False
                btn.variant = "default"
            else:
                btn.label = ""
                btn.disabled = True

        self.query_one("#barra-progreso", ProgressBar).update(progress=self.indice_actual)
        self.respondiendo = True

    @on(Button.Pressed, ".botones-opciones Button")
    def on_opcion_presionada(self, event: Button.Pressed):
        if not self.respondiendo or not event.button.id.startswith("opt-"):
            return

        idx = int(event.button.id.split("-")[1])
        desafio = self.desafios[self.indice_actual]
        config = self.motor.obtener_config()

        correcto, mensaje = self.motor.evaluar_respuesta(desafio, idx, self.pistas_usadas)

        if correcto:
            self.correctas += 1
            self.query_one("#mensaje-resultado", Label).update(f"✅ ¡Correcto!\n{mensaje}")
            event.button.variant = "success"
        else:
            self.intentos_fallidos += 1
            self.query_one("#mensaje-resultado", Label).update(mensaje)
            event.button.variant = "error"
            event.button.disabled = True

        # Deshabilitar todas las opciones tras responder
        for btn_id in ["opt-0", "opt-1", "opt-2", "opt-3"]:
            self.query_one(f"#{btn_id}", Button).disabled = True

        self.respondiendo = False

        # Avanzar después de un breve delay
        self.set_timer(2.0, self._siguiente_pregunta)

    def _siguiente_pregunta(self):
        self.indice_actual += 1
        self.pistas_usadas = 0
        self._mostrar_desafio()

    @on(Button.Pressed, "#btn-pista")
    def on_pista_presionada(self):
        config = self.motor.obtener_config()
        if self.pistas_usadas >= config["max_pistas"]:
            self.query_one("#mensaje-resultado", Label).update(
                f"⚠️ No te quedan pistas. (Máximo: {config['max_pistas']})"
            )
            return

        desafio = self.desafios[self.indice_actual]
        self.pistas_usadas += 1
        restantes = config["max_pistas"] - self.pistas_usadas
        self.query_one("#mensaje-resultado", Label).update(
            f"💡 Pista ({restantes} restantes): {desafio.pista}"
        )
        self.query_one("#btn-pista", Button).disabled = restantes <= 0

    def _finalizar_desafio(self):
        tiempo = time.time() - self.tiempo_inicio
        puntos = self.motor.calcular_puntuacion(
            self.pistas_usadas, self.intentos_fallidos,
            len(self.desafios), self.correctas
        )
        aprobado = self.correctas >= len(self.desafios) * 0.6

        self.motor.guardar_resultado(
            self.modulo_key, self.pistas_usadas, self.intentos_fallidos,
            tiempo, puntos, aprobado
        )

        estado = "✅ APROBADO" if aprobado else "❌ NO APROBADO"
        resumen = (
            f"# 🏆 Resultado del Desafío\n\n"
            f"**Módulo:** {self.modulo_key}\n"
            f"**Dificultad:** {CONFIG_DIFICULTADES[self.dificultad]['nombre']}\n\n"
            f"**Respuestas correctas:** {self.correctas}/{len(self.desafios)}\n"
            f"**Pistas usadas:** {self.pistas_usadas}\n"
            f"**Intentos fallidos:** {self.intentos_fallidos}\n"
            f"**Tiempo:** {tiempo:.1f} segundos\n\n"
            f"**Puntos:** {puntos}\n"
            f"**Estado:** {estado}\n\n"
            f"Presiona **ESC** para volver al laboratorio."
        )

        # Limpiar y mostrar resultado
        for widget in self.query("Button, #texto-pregunta, #info-dificultad, #info-reglas"):
            widget.remove()

        self.query_one("#titulo-desafio", Label).update("🏆 DESAFÍO COMPLETADO")
        self.query_one("#mensaje-resultado", Label).update(resumen)
        self.query_one("#barra-progreso", ProgressBar).update(progress=len(self.desafios))

    def action_cancelar(self):
        self.dismiss()
