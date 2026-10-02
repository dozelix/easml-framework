"""Vistas de contenido de la GUI Flet (paridad con gui/views.py).

Diferencia principal: la guía se lee desde README.md (Markdown nativo para
ft.Markdown) en vez de guia.html, así la GUI nueva no depende del HTML.
"""

import os
import sys

import flet as ft

from app.config import (
    MODULOS,
    defensa_arch,
    es_core,
    meta,
    modulos_por_mundo,
)

from gui_flet import theme as T

_RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _RAIZ not in sys.path:
    sys.path.insert(0, _RAIZ)

from modulos.common.paths import base_recursos


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
    path = os.path.join(base_recursos(), "modulos", MODULOS[index][1], "README.md")
    if not os.path.isfile(path):
        return None
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def vista_dashboard() -> ft.Control:
    """Compat: el antiguo dashboard hoy ES el menú (una sola fuente)."""
    return vista_menu(
        {"minijefe": {}, "sombra": [], "dlc": False},
        modulos_por_mundo(), "trojan")


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
                              color=T.TEXTO, font_family=T.FUENTE)]),
             ft.Text("FLUJO DE TRABAJO", weight=ft.FontWeight.BOLD,
                     color=T.TEXTO, font_family=T.FUENTE)]
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
    arch_defensa = defensa_arch(nombre).removesuffix(".py")
    dir_modulo = os.path.join(base_recursos(), "modulos", nombre)

    sim_ok = os.path.isfile(os.path.join(dir_modulo, f"{script}.py"))
    def_ok = os.path.isfile(os.path.join(dir_modulo, f"{arch_defensa}.py"))
    md_ok = os.path.isfile(os.path.join(dir_modulo, "README.md"))

    bloques: list = [titulo("INFORMACIÓN DEL MÓDULO")]
    bloques.append(tarjeta([
        ft.Text("PILAR CIA", color=T.TEXTO_DIM, size=12, font_family=T.FUENTE),
        ft.Text(cia, color=T.COLOR_CIA.get(cia, T.TEXTO), size=16,
                weight=ft.FontWeight.BOLD, font_family=T.FUENTE),
    ]))
    bloques.append(ft.Text("ARCHIVOS DEL MÓDULO", weight=ft.FontWeight.BOLD, color=T.TEXTO,
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
        bloques.append(ft.Text("REFERENCIA", weight=ft.FontWeight.BOLD, color=T.TEXTO,
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
                    md_style_sheet=T.hoja_markdown(),
                    auto_follow_links=True,
                    selectable=True,
                ),
                bgcolor=T.BG_CARD, padding=12, border_radius=8,
            )
        ],
        scroll=ft.ScrollMode.AUTO, expand=True, spacing=8,
    )


# ── Menú de juego (v1.0.0.0-alpha) ───────────────────────────────────────────

def _pct(p: dict, slugs: list[str]) -> int:
    if not slugs:
        return 0
    ok = sum(1 for s in slugs if p.get("minijefe", {}).get(s, {}).get("ok"))
    return round(ok / len(slugs) * 100)


def vista_menu(p: dict, mundos: dict, siguiente: str,
               on_jugar=None, on_mapa=None) -> ft.Control:
    """Menú principal: JUGAR/CONTINUAR + 3 historias CIA con %."""
    bloques: list = [titulo("EASML — MODO HISTORIA")]
    bloques.append(tarjeta([
        ft.Text("Todo lo que rompas vive en directorio_pruebas/ y se "
                "restaura con un botón. Juega sin miedo.",
                font_family=T.FUENTE, color=T.TEXTO),
    ]))
    alias = meta(siguiente)["alias"]
    bloques.append(
        ft.Container(
            content=ft.Row([
                ft.Text(f"CONTINUAR: {alias} ({siguiente})",
                        weight=ft.FontWeight.BOLD, font_family=T.FUENTE,
                        color=T.TEXTO, expand=True),
                ft.Button("JUGAR", bgcolor=T.ACCENT,
                          color=T.TEXTO_SOBRE_NEON,
                          on_click=lambda e: on_jugar() if on_jugar else None),
            ], spacing=8),
            bgcolor=T.BG_CARD, padding=14, border_radius=8,
        )
    )
    tarjetas = []
    for mundo, slugs in mundos.items():
        tarjetas.append(
            ft.Container(
                content=ft.Column([
                    ft.Text(mundo.upper(), color=T.TEXTO_DIM, size=12,
                            font_family=T.FUENTE),
                    ft.Text(f"{_pct(p, slugs)}%", size=28, color=T.TEXTO,
                            weight=ft.FontWeight.BOLD, font_family=T.FUENTE),
                    ft.Button("MAPA", color=T.ACCENT, bgcolor=T.BG_PANEL,
                              on_click=lambda e, m=mundo: on_mapa(m) if on_mapa else None),
                ], spacing=4, tight=True),
                bgcolor=T.BG_CARD, padding=14, border_radius=8, expand=True,
            )
        )
    bloques.append(ft.Row(tarjetas, spacing=8))
    return ft.Column(bloques, spacing=8, scroll=ft.ScrollMode.AUTO, expand=True)


def vista_mapa(mundo: str, slugs: list[str], p: dict,
               on_capitulo=None) -> ft.Control:
    """Mapa de capítulos de una historia (alias + estado, sin números CIS)."""
    bloques: list = [titulo(f"HISTORIA: {mundo.upper()}")]
    for slug in slugs:
        m = meta(slug)
        mj = p.get("minijefe", {}).get(slug, {})
        bloqueado = not es_core(slug) and not p.get("dlc", False)
        if bloqueado:
            marca, color = "[DLC]", T.TEXTO_DIM
        elif mj.get("ok"):
            marca = "[SOMBRA]" if slug in p.get("sombra", []) else "[OK]"
            color = T.MORADO if slug in p.get("sombra", []) else T.VERDE
        else:
            marca, color = "[···]", T.TEXTO
        bloques.append(
            ft.Container(
                content=ft.Row([
                    ft.Text(f"{marca}  {m['alias']}  ({slug})",
                            weight=ft.FontWeight.BOLD, color=color,
                            font_family=T.FUENTE, expand=True),
                    ft.Text(m["salon"], color=T.TEXTO_DIM, size=12,
                            font_family=T.FUENTE),
                    ft.Button("IR", color=T.ACCENT, bgcolor=T.BG_PANEL,
                              disabled=bloqueado,
                              on_click=lambda e, s=slug: on_capitulo(s) if on_capitulo else None),
                ], spacing=8),
                bgcolor=T.BG_CARD, padding=12, border_radius=8,
            )
        )
    return ft.Column(bloques, spacing=8, scroll=ft.ScrollMode.AUTO, expand=True)


def vista_jefes(p: dict, mundos: dict, on_rejugar=None,
                on_panteon=None) -> ft.Control:
    """Jefes superados, sombras reclutadas y panteones."""
    bloques: list = [titulo("JEFES Y PANTEÓN")]
    for mundo, slugs in mundos.items():
        sup = [s for s in slugs if p.get("minijefe", {}).get(s, {}).get("ok")]
        if not sup:
            continue
        filas = []
        for slug in sup:
            estrella = "SOMBRA" if slug in p.get("sombra", []) else "vencido"
            filas.append(ft.Row([
                ft.Text(f"{meta(slug)['alias']} — {estrella}", color=T.TEXTO,
                        font_family=T.FUENTE, expand=True),
                ft.Button("REJUGAR", color=T.ACCENT, bgcolor=T.BG_PANEL,
                          on_click=lambda e, s=slug: on_rejugar(s) if on_rejugar else None),
            ], spacing=8))
        bloques.append(tarjeta(
            [ft.Text(mundo.upper(), weight=ft.FontWeight.BOLD, color=T.TEXTO,
                     font_family=T.FUENTE)] + filas))
    for mundo, slugs in mundos.items():
        pct = _pct(p, slugs)
        listo = pct == 100
        bloques.append(
            ft.Container(
                content=ft.Row([
                    ft.Text(f"{'PANTEÓN' if listo else 'PANTEÓN ???'} — {mundo} ({pct}%)",
                            weight=ft.FontWeight.BOLD, font_family=T.FUENTE,
                            color=T.TEXTO, expand=True),
                    ft.Button("INICIAR", bgcolor=T.ROJO,
                              color=T.TEXTO_SOBRE_NEON, disabled=not listo,
                              on_click=lambda e, m=mundo: on_panteon(m) if on_panteon else None),
                ], spacing=8),
                bgcolor=T.BG_CARD, padding=12, border_radius=8,
            )
        )
    if len(bloques) == 1:
        bloques.append(tarjeta([ft.Text("Aún no vences ningún jefe. "
                                        "Completa capítulos desde el mapa.",
                                        color=T.TEXTO_DIM, font_family=T.FUENTE)]))
    return ft.Column(bloques, spacing=8, scroll=ft.ScrollMode.AUTO, expand=True)


def vista_ajustes(p: dict, rutas: dict, on_dlc=None, on_anim=None,
                  on_reset_arena=None, on_reset_progreso=None) -> ft.Control:
    """Ajustes: DLC, animaciones, resets separados, rutas activas."""
    bloques: list = [titulo("AJUSTES")]
    bloques.append(
        ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Text("Módulos avanzados (DLC)", font_family=T.FUENTE,
                            color=T.TEXTO, expand=True),
                    ft.Switch(value=p.get("dlc", False),
                              on_change=lambda e: on_dlc(e.control.value) if on_dlc else None),
                ], spacing=8),
                ft.Text("Desbloquea los 8 capítulos difíciles incluidos en "
                        "el exe. Pueden generar más alertas en Defender.",
                        color=T.TEXTO_DIM, size=12, font_family=T.FUENTE),
                ft.Row([
                    ft.Text("Animaciones", font_family=T.FUENTE, color=T.TEXTO, expand=True),
                    ft.Switch(value=p.get("anim", True),
                              on_change=lambda e: on_anim(e.control.value) if on_anim else None),
                ], spacing=8),
            ], spacing=6),
            bgcolor=T.BG_CARD, padding=14, border_radius=8,
        )
    )
    bloques.append(
        ft.Container(
            content=ft.Row([
                ft.Button("RESET ARENA", color=T.VERDE, bgcolor=T.BG_PANEL,
                          on_click=lambda e: on_reset_arena() if on_reset_arena else None,
                          expand=True),
                ft.Button("RESET PROGRESO", color=T.ROJO, bgcolor=T.BG_PANEL,
                          on_click=lambda e: on_reset_progreso() if on_reset_progreso else None,
                          expand=True),
            ], spacing=8),
            bgcolor=T.BG_CARD, padding=14, border_radius=8,
        )
    )
    bloques.append(tarjeta([
        ft.Text("RUTAS ACTIVAS", color=T.TEXTO_DIM, size=12,
                font_family=T.FUENTE),
        ft.Text(f"arena: {rutas.get('lab_dir', '')}", size=12, color=T.TEXTO_DIM,
                font_family=T.FUENTE),
        ft.Text(f"logs:  {rutas.get('logs_dir', '')}", size=12, color=T.TEXTO_DIM,
                font_family=T.FUENTE),
    ]))
    return ft.Column(bloques, spacing=8, scroll=ft.ScrollMode.AUTO, expand=True)


def vista_combate(slug: str, heroe_hp: int, enemigo_hp: int,
                  bitacora: list[str], terminado: str | None,
                  on_atacar=None, on_analizar=None,
                  on_parchar=None, on_capturar=None) -> ft.Control:
    """Pantalla de combate por turnos (barras HP + 4 acciones)."""
    bloques: list = [titulo(f"COMBATE: {meta(slug)['alias']} ({slug})")]

    def _barra(valor: int, color: str) -> ft.ProgressBar:
        return ft.ProgressBar(value=max(0, min(100, valor)) / 100,
                              color=color, bgcolor=T.BG_HOVER)

    bloques.append(tarjeta([
        ft.Text(f"RIVAL — {enemigo_hp}%", color=T.ROJO, size=12,
                font_family=T.FUENTE),
        _barra(enemigo_hp, T.ROJO),
        ft.Text(f"HÉROE (integridad arena) — {heroe_hp}%", color=T.VERDE,
                size=12, font_family=T.FUENTE),
        _barra(heroe_hp, T.VERDE),
    ]))
    fin = terminado is not None
    bloques.append(
        ft.Row([
            ft.Button("ATACAR", bgcolor=T.ROJO, color=T.TEXTO_SOBRE_NEON,
                      disabled=fin,
                      on_click=lambda e: on_atacar() if on_atacar else None),
            ft.Button("ANALIZAR", color=T.AZUL, bgcolor=T.BG_PANEL,
                      disabled=fin,
                      on_click=lambda e: on_analizar() if on_analizar else None),
            ft.Button("PARCHEAR", color=T.VERDE, bgcolor=T.BG_PANEL,
                      disabled=fin,
                      on_click=lambda e: on_parchar() if on_parchar else None),
            ft.Button("CAPTURAR", color=T.MORADO, bgcolor=T.BG_PANEL,
                      disabled=fin or enemigo_hp >= 20,
                      on_click=lambda e: on_capturar() if on_capturar else None),
        ], spacing=6)
    )
    lineas = [ft.Text(l, size=12, font_family=T.FUENTE,
                      color=T.TEXTO_CONSOLA) for l in bitacora[-8:]]
    bloques.append(
        ft.Container(content=ft.Column(lineas or [ft.Text(
            "El bicho emerge... elige tu movimiento.", color=T.TEXTO_DIM,
            size=12, font_family=T.FUENTE)], spacing=2),
            bgcolor=T.BG_CONSOLA, padding=10, border_radius=6))
    return ft.Column(bloques, spacing=8, scroll=ft.ScrollMode.AUTO, expand=True)


def vista_portada(siguiente: str, progreso: dict | None = None,
                  on_jugar=None, on_historias=None, on_avalancha=None,
                  on_config=None, on_como=None, on_salir=None) -> ft.Control:
    """Pantalla título: fondo de red + 6 botones (máx 2 clicks a todo)."""
    alias = meta(siguiente)["alias"]
    glow = (progreso or {}).get("anim", True)

    def _btn(texto, color, fondo, handler, expand=False):
        return ft.Button(texto, color=color, bgcolor=fondo,
                         expand=expand,
                         on_click=lambda e: handler() if handler else None)

    menu = ft.Column([
        ft.Container(expand=True),
        ft.Text("EASML", size=72, weight=ft.FontWeight.BOLD,
                color=T.ACCENT, font_family=T.FUENTE,
                text_align=ft.TextAlign.CENTER),
        ft.Text("LABORATORIO-JUEGO EDUCATIVO DE CIBERSEGURIDAD",
                color=T.TEXTO, size=14, font_family=T.FUENTE,
                text_align=ft.TextAlign.CENTER),
        ft.Text("100% simulado: nada sale de directorio_pruebas/",
                color=T.AMARILLO, size=T.TAM_CUERPO, font_family=T.FUENTE,
                text_align=ft.TextAlign.CENTER),
        ft.Container(height=12),
        ft.Row([
            ft.Container(
                content=ft.Image(src=T.icono_modulo(siguiente), width=96,
                                 height=96,
                                 error_content=ft.Text("·", color=T.TEXTO_DIM)),
                width=104, height=104, border_radius=52,
                border=T.borde_neon(T.CYAN), bgcolor=T.BG_TARJETA,
                shadow=T.brillo(T.CYAN, glow),
            ),
            ft.Column([
                _btn(f"JUGAR: {alias}", T.TEXTO_SOBRE_NEON, T.ACCENT, on_jugar),
                ft.Text(f"continúa en {siguiente}", color=T.TEXTO_DIM,
                        size=T.TAM_MINIMO, font_family=T.FUENTE),
            ], spacing=4, expand=True),
        ], spacing=16, alignment=ft.MainAxisAlignment.CENTER),
        ft.Container(height=8),
        ft.Row([
            _btn("HISTORIAS", T.ACCENT, T.BG_PANEL, on_historias, expand=True),
            _btn("AVALANCHA", T.ROJO, T.BG_PANEL, on_avalancha, expand=True),
        ], spacing=8),
        ft.Row([
            _btn("CONFIGURACIÓN", T.AMARILLO, T.BG_PANEL, on_config, expand=True),
            _btn("CÓMO JUGAR", T.MORADO, T.BG_PANEL, on_como, expand=True),
        ], spacing=8),
        ft.Row([
            _btn("SALIR", T.TEXTO_DIM, T.BG_PANEL, on_salir),
        ], alignment=ft.MainAxisAlignment.CENTER),
        ft.Container(expand=True),
        ft.Text("v1.0.0.0-alpha — alpha cerrada, todo puede romperse",
                color=T.TEXTO_DIM, size=T.TAM_MINIMO, font_family=T.FUENTE,
                text_align=ft.TextAlign.CENTER),
    ], spacing=6, expand=True,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER)

    return ft.Container(
        expand=True,
        image=ft.DecorationImage(src=T.fondo_portada(),
                                 fit=ft.BoxFit.COVER),
        content=ft.Container(content=menu, padding=24, expand=True),
    )
