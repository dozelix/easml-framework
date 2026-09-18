"""Juego de desafíos para la GUI Flet.

ControladorQuiz es lógica pura (misma máquina de estados que gui/desafio.py:
selector → pregunta → responder → avanzar → finalizar, aprobado con 60%).
construir_dialogo() monta el AlertDialog que la vista principal muestra.
"""

import asyncio
import time

import flet as ft

from app.laboratorio import (
    CONFIG_DIFICULTADES,
    DESAFIOS_POR_MODULO,
    LaboratorioInteractivo,
)

from gui_flet import theme as T

DEMORA_AVANCE_SEGUNDOS = 2


class ControladorQuiz:
    """Estado del juego, sin dependencia de widgets (testeable)."""

    def __init__(self, modulo_key: str):
        self.modulo_key = modulo_key
        self.motor = LaboratorioInteractivo()
        self.desafios = DESAFIOS_POR_MODULO.get(modulo_key, [])
        self.indice = 0
        self.correctas = 0
        self.pistas = 0
        self.fallos = 0
        self.tiempo_inicio = 0.0
        self.respondiendo = False

    def iniciar(self, dificultad: str) -> None:
        self.motor.dificultad = dificultad
        self.indice = 0
        self.correctas = 0
        self.pistas = 0
        self.fallos = 0
        self.tiempo_inicio = time.time()
        self.respondiendo = True

    def pregunta_actual(self):
        if self.indice >= len(self.desafios):
            return None
        return self.desafios[self.indice]

    def pistas_restantes(self) -> int:
        return self.motor.obtener_config()["max_pistas"] - self.pistas

    def responder(self, idx: int):
        """Retorna (correcto, mensaje) o None si no se puede responder."""
        if not self.respondiendo:
            return None
        d = self.pregunta_actual()
        if d is None:
            return None
        correcto, mensaje = self.motor.evaluar_respuesta(d, idx, self.pistas)
        if correcto:
            self.correctas += 1
        else:
            self.fallos += 1
        self.respondiendo = False
        return correcto, mensaje

    def pedir_pista(self):
        d = self.pregunta_actual()
        if d is None or self.pistas >= self.motor.obtener_config()["max_pistas"]:
            return None
        self.pistas += 1
        return d.pista

    def avanzar(self) -> bool:
        """Avanza a la siguiente pregunta. Retorna False si terminó."""
        self.indice += 1
        self.pistas = 0
        self.respondiendo = True
        return self.indice < len(self.desafios)

    def finalizar(self) -> dict:
        tiempo = time.time() - self.tiempo_inicio
        puntos = self.motor.calcular_puntuacion(
            self.pistas, self.fallos, len(self.desafios), self.correctas)
        aprobado = self.correctas >= len(self.desafios) * 0.6
        self.motor.guardar_resultado(
            self.modulo_key, self.pistas, self.fallos, tiempo, puntos, aprobado)
        return {
            "correctas": self.correctas,
            "total": len(self.desafios),
            "puntos": puntos,
            "tiempo": tiempo,
            "aprobado": aprobado,
            "resumen": self.motor.resumen_general(),
        }


def _texto_resultado(ctrl: ControladorQuiz) -> ft.Text:
    return ft.Text("", color=T.TEXTO, font_family=T.FUENTE)


def construir_dialogo(page: ft.Page, modulo_key: str) -> ft.AlertDialog:
    """Crea el diálogo de desafío para un módulo (modal, como el Toplevel)."""
    ctrl = ControladorQuiz(modulo_key)
    if not ctrl.desafios:
        return ft.AlertDialog(
            modal=True,
            title=ft.Text(f"Desafío — {modulo_key}", font_family=T.FUENTE),
            content=ft.Text("Este módulo no tiene desafíos disponibles.",
                            font_family=T.FUENTE),
            actions=[ft.Button("Cerrar", on_click=lambda e: cerrar())],
        )

    titulo = ft.Text(f"DESAFÍO: {modulo_key}", color=T.ACCENT,
                     weight=ft.FontWeight.BOLD, font_family=T.FUENTE)
    info = ft.Text("", color=T.TEXTO_DIM, size=12, font_family=T.FUENTE)
    area = ft.Column([], spacing=6, scroll=ft.ScrollMode.AUTO,
                     width=560, height=380)
    resultado = _texto_resultado(ctrl)
    barra = ft.ProgressBar(value=0, color=T.ACCENT, bgcolor=T.BG_HOVER)
    dificultad = {"valor": "facil"}

    dlg = ft.AlertDialog(modal=True, title=titulo,
                         content=ft.Column([info, area, resultado, barra],
                                           spacing=8, tight=True))

    def cerrar():
        dlg.open = False
        page.update()

    def refrescar():
        if ctrl.indice < len(ctrl.desafios):
            barra.value = ctrl.indice / len(ctrl.desafios)
        else:
            barra.value = 1.0
        page.update()

    def mostrar_selector():
        area.controls.clear()
        resultado.value = "Selecciona la dificultad:"
        for clave, cfg in CONFIG_DIFICULTADES.items():
            area.controls.append(
                ft.Container(
                    content=ft.Radio(
                        value=clave,
                        label=f"{cfg['nombre']}  —  {cfg['descripcion']}",
                    ),
                    bgcolor=T.BG_CARD, padding=8, border_radius=6,
                )
            )
        radios = ft.RadioGroup(
            content=ft.Column(list(area.controls), spacing=6),
            value="facil",
            on_change=lambda e: dificultad.update(valor=e.control.value),
        )
        area.controls.clear()
        area.controls.append(radios)
        area.controls.append(
            ft.Button("Comenzar", bgcolor=T.ACCENT, color="#FFFFFF",
                      on_click=lambda e: iniciar()))
        refrescar()

    def iniciar():
        ctrl.iniciar(dificultad["valor"])
        mostrar_pregunta()

    def mostrar_pregunta():
        d = ctrl.pregunta_actual()
        if d is None:
            mostrar_final()
            return
        cfg = ctrl.motor.obtener_config()
        info.value = (f"Dificultad: {cfg['nombre']}  |  "
                      f"Pregunta {ctrl.indice + 1}/{len(ctrl.desafios)}")
        resultado.value = ""
        area.controls.clear()
        area.controls.append(
            ft.Container(
                content=ft.Text(d.pregunta, weight=ft.FontWeight.BOLD,
                                font_family=T.FUENTE),
                bgcolor=T.BG_CARD, padding=12, border_radius=6,
            )
        )
        for i, opcion in enumerate(d.opciones):
            area.controls.append(
                ft.Button(f"{i + 1}. {opcion}",
                          on_click=lambda e, idx=i: responder(idx)))
        if ctrl.pistas_restantes() <= 0:
            area.controls.append(ft.Text("[PISTA] Agotada", color=T.TEXTO_DIM,
                                         size=12, font_family=T.FUENTE))
        else:
            area.controls.append(
                ft.TextButton(
                    f"[PISTA] Pedir pista ({ctrl.pistas_restantes()} restantes)",
                    on_click=lambda e: pedir_pista()))
        refrescar()

    def responder(idx: int):
        res = ctrl.responder(idx)
        if res is None:
            return
        correcto, mensaje = res
        if correcto:
            resultado.value = f"[OK] Correcto!  {mensaje}"
            resultado.color = T.VERDE
        else:
            resultado.value = f"[--] {mensaje}"
            resultado.color = T.ROJO
        page.update()

        async def _avanzar():
            await asyncio.sleep(DEMORA_AVANCE_SEGUNDOS)
            if ctrl.avanzar():
                mostrar_pregunta()
            else:
                mostrar_final()

        page.run_task(_avanzar)

    def pedir_pista():
        pista = ctrl.pedir_pista()
        if pista is None:
            return
        resultado.value = f"[PISTA] {pista}"
        resultado.color = T.AMARILLO
        mostrar_pista_actualizada()

    def mostrar_pista_actualizada():
        # Re-render simple: solo actualiza el contador re-mostrando la pregunta
        # sin resetear el estado (índice y respondiendo se conservan).
        d = ctrl.pregunta_actual()
        if d is None:
            return
        # Elimina el botón de pista anterior (último control si es TextButton)
        if area.controls and isinstance(area.controls[-1], ft.TextButton):
            area.controls.pop()
        if ctrl.pistas_restantes() <= 0:
            area.controls.append(ft.Text("[PISTA] Agotada", color=T.TEXTO_DIM,
                                         size=12, font_family=T.FUENTE))
        else:
            area.controls.append(
                ft.TextButton(
                    f"[PISTA] Pedir pista ({ctrl.pistas_restantes()} restantes)",
                    on_click=lambda e: pedir_pista()))
        page.update()

    def mostrar_final():
        datos = ctrl.finalizar()
        estado = "[OK] APROBADO" if datos["aprobado"] else "[--] NO APROBADO"
        color_estado = T.VERDE if datos["aprobado"] else T.ROJO
        info.value = ""
        resultado.value = ""
        area.controls.clear()
        filas = [
            ("Correctas", f"{datos['correctas']}/{datos['total']}"),
            ("Puntos", str(datos["puntos"])),
            ("Tiempo", f"{datos['tiempo']:.1f}s"),
            ("Estado", estado),
        ]
        tarjeta = [ft.Text("RESULTADO", color=T.ACCENT,
                            weight=ft.FontWeight.BOLD, font_family=T.FUENTE)]
        for lbl, val in filas:
            tarjeta.append(
                ft.Row([ft.Text(lbl, color=T.TEXTO_DIM, width=110,
                                font_family=T.FUENTE),
                        ft.Text(val, weight=ft.FontWeight.BOLD,
                                color=color_estado if lbl == "Estado" else T.TEXTO,
                                font_family=T.FUENTE)],
                       spacing=8))
        area.controls.append(
            ft.Container(content=ft.Column(tarjeta, spacing=4),
                         bgcolor=T.BG_CARD, padding=14, border_radius=6))
        dlg.actions = [ft.Button("Cerrar", bgcolor=T.ACCENT, color="#FFFFFF",
                                 on_click=lambda e: cerrar())]
        refrescar()

    mostrar_selector()
    return dlg
