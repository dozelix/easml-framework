"""Vistas de contenido de la GUI Flet (paridad con gui/views.py).

Diferencia principal: la guía se lee desde README.md (Markdown nativo para
ft.Markdown) en vez de guia.html, así la GUI nueva no depende del HTML.
"""

import os
from collections import Counter

import flet as ft

from app.config import MODULOS, NOMBRES_DEFENSA

from gui_flet import theme as T

_RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def tarjeta(controles, expand=False) -> ft.Container:
    return ft.Container(
        content=ft.Column(controles, spacing=6, tight=True),
        bgcolor=T.BG_CARD, padding=14, border_radius=8, expand=expand,
    )


def titulo(texto: str) -> ft.Text:
    return ft.Text(texto, size=20, weight=ft.FontWeight.BOLD,
                   color=T.TEXTO, font_family=T.FUENTE)


def leer_readme_modulo(index: int) -> str | None:
    if index < 0 or index >= len(MODULOS):
        return None
    path = os.path.join(_RAIZ, "modulos", MODULOS[index][1], "README.md")
    if not os.path.isfile(path):
        return None
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def vista_dashboard() -> ft.Control:
    dir_lab = os.path.join(_RAIZ, "directorio_pruebas")
    dir_logs = os.path.join(_RAIZ, "lab_data", "logs")

    archivos = len([f for f in os.listdir(dir_lab)
                    if os.path.isfile(os.path.join(dir_lab, f))]) if os.path.isdir(dir_lab) else 0
    logs = len([f for f in os.listdir(dir_logs)
                if f.endswith(".log")]) if os.path.isdir(dir_logs) else 0
    contador_cia = Counter(m[3] for m in MODULOS)
    activo = archivos > 0

    stats = []
    for tit, val, color in [
        ("ESTADO", "ACTIVO" if activo else "VACÍO", T.VERDE if activo else T.ROJO),
        ("ARCHIVOS", str(archivos), T.TEXTO),
        ("LOGS", str(logs), T.TEXTO),
    ]:
        stats.append(
            ft.Container(
                content=ft.Column([
                    ft.Text(tit, color=T.TEXTO_DIM, size=12, font_family=T.FUENTE),
                    ft.Text(val, color=color, size=28,
                            weight=ft.FontWeight.BOLD, font_family=T.FUENTE),
                ], spacing=4, tight=True),
                bgcolor=T.BG_CARD, padding=14, border_radius=8, expand=True,
            )
        )

    cias = []
    for cia_nombre in ("Confidencialidad", "Integridad", "Disponibilidad"):
        cias.append(
            ft.Container(
                content=ft.Column([
                    ft.Text(cia_nombre, color=T.TEXTO_DIM, size=12,
                            font_family=T.FUENTE),
                    ft.Text(str(contador_cia.get(cia_nombre, 0)), size=28,
                            weight=ft.FontWeight.BOLD, font_family=T.FUENTE),
                ], spacing=4, tight=True),
                bgcolor=T.BG_CARD, padding=14, border_radius=8, expand=True,
            )
        )

    return ft.Column([
        titulo("DASHBOARD"),
        ft.Row(stats, spacing=8),
        ft.Divider(height=16, color="transparent"),
        ft.Text("MÓDULOS POR PILAR CIA", weight=ft.FontWeight.BOLD,
                font_family=T.FUENTE),
        ft.Row(cias, spacing=8),
    ], spacing=8, scroll=ft.ScrollMode.AUTO, expand=True)


def vista_tutorial() -> ft.Control:
    pasos = [
        ("[1] Setup   — Genera archivos de prueba", T.AMARILLO),
        ("[2] Simular — Ejecuta la simulación del módulo", T.ROJO),
        ("[3] Defensa — Mitiga la amenaza y restaura archivos", T.AZUL),
        ("[4] Clean   — Limpia consola y entorno", T.VERDE),
    ]
    flujo = [titulo("TUTORIAL RÁPIDO"),
             tarjeta([ft.Text("Bienvenido! Este laboratorio te permite ejecutar 14 tipos "
                              "de amenazas de forma segura en un entorno aislado.",
                              font_family=T.FUENTE)]),
             ft.Text("FLUJO DE TRABAJO", weight=ft.FontWeight.BOLD,
                     font_family=T.FUENTE)]
    for paso, color in pasos:
        flujo.append(tarjeta([ft.Text(paso, color=color,
                                      weight=ft.FontWeight.BOLD,
                                      font_family=T.FUENTE)]))
    flujo.append(ft.Text("Los módulos están ordenados por control CIS (2 → 15) para "
                         "facilitar el aprendizaje progresivo de los estándares.",
                         color=T.TEXTO_DIM, size=12, font_family=T.FUENTE))
    return ft.Column(flujo, spacing=8, scroll=ft.ScrollMode.AUTO, expand=True)


def vista_modulo(index: int) -> ft.Control:
    if index < 0 or index >= len(MODULOS):
        return ft.Text("Selecciona un módulo de la lista.",
                       color=T.TEXTO_DIM, font_family=T.FUENTE)

    num, nombre, script, cia, _cis, url_ref = MODULOS[index]
    nombre_defensa = NOMBRES_DEFENSA.get(num, "defensa")
    arch_defensa = nombre_defensa.lower().replace(" ", "_")
    dir_modulo = os.path.join(_RAIZ, "modulos", nombre)

    sim_ok = os.path.isfile(os.path.join(dir_modulo, f"{script}.py"))
    def_ok = os.path.isfile(os.path.join(dir_modulo, f"{arch_defensa}.py"))
    md_ok = os.path.isfile(os.path.join(dir_modulo, "README.md"))

    bloques: list = [titulo("INFORMACIÓN DEL MÓDULO")]
    bloques.append(tarjeta([
        ft.Text("PILAR CIA", color=T.TEXTO_DIM, size=12, font_family=T.FUENTE),
        ft.Text(cia, color=T.COLOR_CIA.get(cia, T.TEXTO), size=16,
                weight=ft.FontWeight.BOLD, font_family=T.FUENTE),
    ]))
    bloques.append(ft.Text("ARCHIVOS DEL MÓDULO", weight=ft.FontWeight.BOLD,
                           font_family=T.FUENTE))
    for etiqueta, existe in [
        (f"Simulación: {script}.py", sim_ok),
        (f"Defensa:    {arch_defensa}.py", def_ok),
        ("Guía (README.md)", md_ok),
    ]:
        marca = "[OK]" if existe else "[--]"
        bloques.append(tarjeta([ft.Text(f"{marca}  {etiqueta}",
                                        color=T.VERDE if existe else T.ROJO,
                                        weight=ft.FontWeight.BOLD,
                                        font_family=T.FUENTE)]))
    if url_ref:
        bloques.append(ft.Text("REFERENCIA", weight=ft.FontWeight.BOLD,
                               font_family=T.FUENTE))
        # BLANK: abre pestaña nueva; SELF navegaría la app y parecería rota.
        bloques.append(ft.Button(
            url_ref,
            url=ft.Url(url_ref, target=ft.UrlTarget.BLANK),
            color=T.ACCENT, bgcolor=T.BG_CARD))
    return ft.Column(bloques, spacing=8, scroll=ft.ScrollMode.AUTO, expand=True)


def vista_guia(markdown_texto: str) -> ft.Control:
    # Column con scroll propio: Markdown con expand dentro de un Container
    # pide altura infinita, desborda el área y la botonera lo pisa.
    return ft.Column(
        [
            ft.Container(
                content=ft.Markdown(
                    markdown_texto,
                    extension_set=ft.MarkdownExtensionSet.GITHUB_WEB,
                    auto_follow_links=True,
                    selectable=True,
                ),
                bgcolor=T.BG_CARD, padding=12, border_radius=8,
            )
        ],
        scroll=ft.ScrollMode.AUTO, expand=True, spacing=8,
    )
