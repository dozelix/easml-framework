"""Ventana principal de la GUI Flet (paridad con gui/main.py).

Layout: sidebar (Panel/Tutorial + 14 módulos) | header | contenido |
botonera Setup/Simular/Defensa/Clean/Guía/Juego | consola.
Los scripts se ejecutan con gui_flet/runner_flet.py (asyncio, sin congelar la UI).
"""

import os

import flet as ft

from app.config import MODULOS, NOMBRES_DEFENSA
from app.laboratorio import DESAFIOS_POR_MODULO

from gui_flet import theme as T
from gui_flet.desafio import construir_dialogo
from gui_flet.runner_flet import ejecutar_script
from gui_flet.views import (
    leer_readme_modulo,
    vista_dashboard,
    vista_guia,
    vista_modulo,
    vista_tutorial,
)

_DIR_RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_ASSETS = os.path.join(_DIR_RAIZ, "assets")


class Estado:
    def __init__(self):
        self.vista = "dashboard"  # dashboard | tutorial | modulo
        self.modulo_idx: int | None = None
        self.viendo_guia = False
        self.ejecutando = False


async def main(page: ft.Page):
    page.title = "E.A.S.M.L — Laboratorio Educativo de Malware"
    page.window.width = 1280
    page.window.height = 800
    page.window.min_width = 960
    page.window.min_height = 600

    estado = Estado()

    # ── Consola ──────────────────────────────────────────────────────────
    consola = ft.ListView(auto_scroll=True, spacing=2, padding=8, height=162)

    def log(linea: str):
        color = T.TEXTO_CONSOLA
        if linea.startswith(("[TIMEOUT]", "[ERROR]")):
            color = T.ROJO
        consola.controls.append(
            ft.Text(linea, color=color, size=12, font_family=T.FUENTE))
        page.update()

    def log_sync(linea: str):
        consola.controls.append(
            ft.Text(linea, color=T.TEXTO_CONSOLA, size=12,
                    font_family=T.FUENTE))

    # ── Contenido + header ───────────────────────────────────────────────
    # Icono CIA del header: oculto hasta que haya módulo seleccionado.
    # (visible=False evita que Flet valide el src; src="" renderiza un
    # cartel rojo de error en vez de ignorarse.)
    icono_cia = ft.Image(src=T.icono_cia("Disponibilidad"), width=22,
                         height=22, visible=False,
                         error_content=ft.Text(""))
    lbl_nombre = ft.Text("PANEL", size=16, weight=ft.FontWeight.BOLD,
                         color=T.ACCENT, font_family=T.FUENTE, expand=True)
    lbl_cis = ft.Text("", color=T.TEXTO_DIM, size=12, font_family=T.FUENTE)
    contenido = ft.Container(content=vista_dashboard(), expand=True)

    def mostrar(nueva_vista: ft.Control):
        contenido.content = nueva_vista
        estado.viendo_guia = False

    def refrescar():
        page.update()

    # ── Acciones ─────────────────────────────────────────────────────────
    async def correr(script_path: str, etiqueta: str, inicio: str):
        if estado.ejecutando:
            return
        estado.ejecutando = True
        consola.controls.clear()
        log(inicio)
        await ejecutar_script(script_path, etiqueta, log)
        estado.ejecutando = False

    def acc_setup(e):
        page.run_task(correr, os.path.join(_DIR_RAIZ, "core", "lab_setup.py"),
                      "Setup", "[SETUP] Preparando entorno de pruebas...")

    def acc_simular(e):
        if estado.modulo_idx is None or estado.ejecutando:
            return
        _, nombre, script, _, _, _ = MODULOS[estado.modulo_idx]
        ruta = os.path.join(_DIR_RAIZ, "modulos", nombre, f"{script}.py")
        page.run_task(correr, ruta, f"{nombre}/simulacion",
                      f"[SIMULAR] Ejecutando {nombre}...")

    def acc_defensa(e):
        if estado.modulo_idx is None or estado.ejecutando:
            return
        num, nombre = MODULOS[estado.modulo_idx][0], MODULOS[estado.modulo_idx][1]
        arch = NOMBRES_DEFENSA.get(num, "defensa").lower().replace(" ", "_")
        ruta = os.path.join(_DIR_RAIZ, "modulos", nombre, f"{arch}.py")
        page.run_task(correr, ruta, f"{nombre}/defensa",
                      f"[DEFENSA] Ejecutando mitigación para {nombre}...")

    def acc_clean(e):
        consola.controls.clear()
        log_sync("[CLEAN] Consola limpiada.")
        mostrar_actual()
        page.update()

    def acc_guia(e):
        if estado.modulo_idx is None:
            return
        if estado.viendo_guia:
            mostrar_actual()
        else:
            md = leer_readme_modulo(estado.modulo_idx)
            if md is None:
                contenido.content = ft.Text(
                    "Este módulo no tiene guía disponible.",
                    color=T.TEXTO_DIM, font_family=T.FUENTE)
            else:
                contenido.content = vista_guia(md)
            estado.viendo_guia = True
        page.update()

    def acc_juego(e):
        if estado.modulo_idx is None:
            return
        nombre = MODULOS[estado.modulo_idx][1]
        if nombre not in DESAFIOS_POR_MODULO:
            log_sync(f"[JUEGO] {nombre} no tiene desafíos disponibles.")
            page.update()
            return
        page.show_dialog(construir_dialogo(page, nombre))

    # ── Navegación ───────────────────────────────────────────────────────
    def mostrar_dashboard():
        estado.vista = "dashboard"
        estado.modulo_idx = None
        icono_cia.visible = False
        lbl_nombre.value = "PANEL"
        lbl_cis.value = ""
        mostrar(vista_dashboard())

    def mostrar_tutorial():
        estado.vista = "tutorial"
        estado.modulo_idx = None
        icono_cia.visible = False
        lbl_nombre.value = "TUTORIAL"
        lbl_cis.value = ""
        mostrar(vista_tutorial())

    def mostrar_modulo(idx: int):
        estado.vista = "modulo"
        estado.modulo_idx = idx
        _num, nombre, _script, cia, cis, _ref = MODULOS[idx]
        icono_cia.src = T.icono_cia(cia)
        icono_cia.visible = True
        lbl_nombre.value = f"  {nombre}"
        lbl_cis.value = cis
        mostrar(vista_modulo(idx))
        for tile in lista_modulos.controls:
            tile.selected = (tile.data == idx)

    def mostrar_actual():
        if estado.vista == "tutorial":
            mostrar_tutorial()
        elif estado.vista == "modulo" and estado.modulo_idx is not None:
            mostrar_modulo(estado.modulo_idx)
        else:
            mostrar_dashboard()

    def on_modulo_click(e):
        mostrar_modulo(e.control.data)
        page.update()

    # ── Sidebar ──────────────────────────────────────────────────────────
    def boton_sidebar(texto: str, color: str, handler):
        return ft.Button(texto, color=color, bgcolor=T.BG_PANEL,
                         on_click=handler)

    lista_modulos = ft.ListView(expand=True, spacing=2)
    for i, m in enumerate(MODULOS):
        _num, nombre = m[0], m[1]
        lista_modulos.controls.append(
            ft.ListTile(
                leading=ft.Image(src=T.icono_modulo(nombre), width=28,
                                 height=28,
                                 error_content=ft.Text("·", color=T.TEXTO_DIM)),
                title=ft.Text(nombre, font_family=T.FUENTE, size=13),
                data=i,
                on_click=on_modulo_click,
            )
        )

    sidebar = ft.Container(
        width=240,
        bgcolor=T.BG_PANEL,
        padding=8,
        content=ft.Column([
            boton_sidebar("PANEL", T.CYAN,
                          lambda e: (mostrar_dashboard(), page.update())),
            ft.Divider(height=8, color="transparent"),
            ft.Text("MÓDULOS", color=T.TEXTO_DIM, size=12,
                    font_family=T.FUENTE),
            lista_modulos,
            ft.Divider(height=8),
            boton_sidebar("TUTORIAL", T.MORADO,
                          lambda e: (mostrar_tutorial(), page.update())),
        ], spacing=4, expand=True),
    )

    # ── Ensamblado ───────────────────────────────────────────────────────
    def boton_accion(texto: str, color: str, handler):
        return ft.Button(texto, color=color, bgcolor=T.BG_PANEL,
                         on_click=handler)

    header = ft.Container(
        bgcolor=T.BG_PANEL, padding=10,
        content=ft.Row([icono_cia, lbl_nombre, lbl_cis], spacing=8),
    )
    botonera = ft.Row([
        boton_accion("  Setup  ", T.AMARILLO, acc_setup),
        boton_accion(" Simular ", T.ROJO, acc_simular),
        boton_accion(" Defensa ", T.AZUL, acc_defensa),
        boton_accion("  Clean  ", T.VERDE, acc_clean),
        boton_accion("  Guía   ", T.MORADO, acc_guia),
        boton_accion("  Juego  ", T.NARANJA, acc_juego),
    ], spacing=6)
    consola_cab = ft.Row([
        ft.Text("CONSOLA", color=T.TEXTO_DIM, size=12,
                font_family=T.FUENTE, expand=True),
        ft.TextButton("X", on_click=lambda e: (consola.controls.clear(),
                                               page.update())),
    ], spacing=4)
    caja_consola = ft.Container(content=consola, bgcolor=T.BG_CONSOLA,
                                border_radius=6, padding=4)

    page.add(
        ft.Container(
            bgcolor=T.BG, expand=True, padding=4,
            content=ft.Row([
                sidebar,
                ft.VerticalDivider(width=1),
                ft.Column([
                    header,
                    ft.Container(content=contenido, expand=True, padding=8),
                    botonera,
                    consola_cab,
                    caja_consola,
                ], expand=True, spacing=4),
            ], expand=True, spacing=4),
        )
    )
    refrescar()


def lanzar(web: bool = False, puerto: int = 8550):
    """Punto de entrada gráfico (importa flet solo aquí).

    web=True sirve la app en el navegador local (útil en Wayland, demos en
    aula o smoke tests) en vez de abrir la ventana desktop.
    """
    if web:
        ft.run(main, assets_dir=_ASSETS,
               view=ft.AppView.WEB_BROWSER, port=puerto)
    else:
        ft.run(main, assets_dir=_ASSETS)
