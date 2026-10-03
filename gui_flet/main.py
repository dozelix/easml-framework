"""Ventana principal de la GUI Flet (paridad con gui/main.py).

Layout: sidebar (Panel/Tutorial + 14 módulos) | header | contenido |
botonera Setup/Simular/Defensa/Clean/Guía/Juego | consola.
Los scripts se ejecutan con gui_flet/runner_flet.py (asyncio, sin congelar la UI).
"""

import os

import flet as ft

from app.combate import Combate
from app.mochila import gastar, inventario
from app.config import (
    MODULOS,
    defensa_arch,
    es_core,
    meta,
    modulos_por_mundo,
    orden_campana,
)
from app.laboratorio import DESAFIOS_POR_MODULO
from app import progreso as PG
from modulos.common.utils import is_lab_ready

from gui_flet import theme as T
from gui_flet.desafio import construir_dialogo
from gui_flet.views import (
    leer_readme_modulo,
    vista_ajustes,
    vista_avalancha,
    vista_combate,
    vista_progreso,
    vista_datos,
    vista_guia,
    vista_jefes,
    vista_mapa,
    vista_menu,
    vista_modulo,
    vista_portada,
    vista_tutorial,
)

_DIR_RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_ASSETS = os.path.join(_DIR_RAIZ, "assets")


class EstadoApp:
    def __init__(self):
        self.vista = "dashboard"  # dashboard | mapa | tutorial | modulo | jefes | ajustes
        self.modulo_idx: int | None = None
        self.mapa_mundo: str | None = None
        self.viendo_guia = False
        self.ejecutando = False
        self.prog = PG.cargar()
        self.mundos = modulos_por_mundo()
        self.campana = orden_campana()
        self.slug_por_idx = {i: m[1] for i, m in enumerate(MODULOS)}
        self.idx_por_slug = {m[1]: i for i, m in enumerate(MODULOS)}
        self.combate: Combate | None = None


async def main(page: ft.Page):
    page.title = "EASML — Modo Historia"
    page.window.width = 1280
    page.window.height = 800
    page.window.min_width = 960
    page.window.min_height = 600

    estado = EstadoApp()

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
    lbl_nombre = ft.Text("PROGRESO", size=16, weight=ft.FontWeight.BOLD,
                         color=T.ACCENT, font_family=T.FUENTE, expand=True)
    lbl_cis = ft.Text("", color=T.TEXTO_DIM, size=12, font_family=T.FUENTE)
    contenido = ft.Container(content=None, expand=True)

    def mostrar(nueva_vista: ft.Control):
        contenido.content = nueva_vista
        estado.viendo_guia = False

    def _botonera_para(vista: str):
        botonera.visible = vista in ("modulo", "combate")

    def _consola_para(vista: str):
        # En combate manda la bitácora integrada (sin consola duplicada).
        for caja in (consola_cab, caja_consola):
            caja.visible = vista != "combate"

    def refrescar():
        page.update()

    # ── Acciones (la escena se juega en combate; sin botones duplicados) ──
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

    def al_cerrar_quiz(slug: str, datos: dict):
        nuevo_cien = PG.registrar_minijefe(
            estado.prog, slug, datos["aprobado"], datos["pistas_total"],
            datos["fallos"], datos["correctas"], datos["total"])
        PG.guardar(estado.prog)
        if nuevo_cien:
            log_sync(f"[SOMBRA] {meta(slug)['alias']} se une a tu equipo. "
                      "Puedes rejugarlo desde JEFES.")
        for mundo, slugs in estado.mundos.items():
            if all(estado.prog["minijefe"].get(s, {}).get("ok") for s in slugs):
                if not estado.prog["megajefe"].get(mundo):
                    estado.prog["megajefe"][mundo] = True
                    PG.guardar(estado.prog)
                    log_sync(f"[MEGAJEFE] Historia {mundo} superada. "
                             f"Panteón desbloqueado en JEFES.")
        mostrar_actual()
        page.update()

    def acc_juego(e):
        if estado.modulo_idx is None:
            return
        nombre = MODULOS[estado.modulo_idx][1]
        if nombre not in DESAFIOS_POR_MODULO:
            log_sync(f"[JUEGO] {nombre} no tiene desafíos disponibles.")
            page.update()
            return
        page.show_dialog(construir_dialogo(
            page, nombre,
            on_finalizar=lambda slug, datos: al_cerrar_quiz(slug, datos)))

    def iniciar_panteon(mundo: str):
        cola = [s for s in estado.mundos[mundo] if s in DESAFIOS_POR_MODULO]
        if not cola:
            return
        log_sync(f"[PANTEÓN] Avalancha {mundo}: {len(cola)} jefes en difícil, "
                 "sin piedad.")

        def _siguiente(restantes: list[str]):
            if not restantes:
                estado.prog["panteon"][mundo] = True
                PG.guardar(estado.prog)
                log_sync(f"[PANTEÓN] {mundo} superado. Leyenda de la red.")
                mostrar_actual()
                page.update()
                return

            def _fin(slug: str, datos: dict):
                al_cerrar_quiz(slug, datos)
                if datos["aprobado"]:
                    _siguiente(restantes[1:])
                else:
                    log_sync(f"[PANTEÓN] Caíste ante {meta(slug)['alias']}. "
                             "Reintenta desde JEFES.")

            page.show_dialog(construir_dialogo(
                page, restantes[0], dificultad_fija="dificil",
                on_finalizar=_fin))

        _siguiente(cola)

    # ── Navegación ───────────────────────────────────────────────────────
    def jugar_siguiente():
        """Un solo helper JUGAR (portada + sidebar, sin duplicar)."""
        if not estado.prog.get("heroe", ""):
            pedir_nombre(lambda: jugar_siguiente())
            return
        if PG.es_primera_vez(estado.prog):
            entrar()
            mostrar_tutorial()
            page.update()
            return
        mostrar_modulo(estado.idx_por_slug[
            PG.siguiente_capitulo(estado.prog, estado.campana)])
        page.update()

    def pedir_nombre(al_continuar):
        campo = ft.TextField(
            label="Nombre del héroe", autofocus=True,
            color=T.TEXTO, bgcolor=T.BG_CARD, border_color=T.BORDE,
            on_submit=lambda e: _guardar_nombre(e.control.value))

        def _guardar_nombre(valor: str):
            nombre = (valor or "").strip().upper()[:16] or "ANALISTA"
            estado.prog["heroe"] = nombre
            PG.guardar(estado.prog)
            dlg.open = False
            page.update()
            al_continuar()

        dlg = ft.AlertDialog(
            modal=True, bgcolor=T.BG_PANEL,
            title=ft.Text("¿CÓMO TE LLAMAS, ANALISTA?", color=T.ACCENT,
                           weight=ft.FontWeight.BOLD, font_family=T.FUENTE),
            content=campo,
            actions=[ft.Button("EMPEZAR", bgcolor=T.ACCENT,
                               color=T.TEXTO_SOBRE_NEON,
                               on_click=lambda e: _guardar_nombre(campo.value))],
        )
        page.show_dialog(dlg)

    def mostrar_progreso():
        estado.vista = "dashboard"
        _botonera_para("dashboard")
        _consola_para("dashboard")
        estado.modulo_idx = None
        icono_cia.visible = False
        lbl_nombre.value = "PROGRESO"
        lbl_cis.value = ""
        mostrar(vista_menu(
            estado.prog, estado.mundos,
            PG.siguiente_capitulo(estado.prog, estado.campana),
            on_jugar=lambda: (mostrar_modulo(estado.idx_por_slug[
                PG.siguiente_capitulo(estado.prog, estado.campana)]),
                page.update()),
            on_mapa=lambda m: (mostrar_mapa(m), page.update()),
        ))

    def mostrar_mapa(mundo: str):
        estado.vista = "mapa"
        _botonera_para("mapa")
        _consola_para("mapa")
        estado.mapa_mundo = mundo
        estado.modulo_idx = None
        icono_cia.visible = False
        lbl_nombre.value = f"MAPA: {mundo.upper()}"
        lbl_cis.value = ""
        mostrar(vista_mapa(
            mundo, estado.mundos[mundo], estado.prog,
            on_capitulo=lambda s: (mostrar_modulo(estado.idx_por_slug[s]),
                                   page.update()),
        ))

    def mostrar_jefes():
        estado.vista = "jefes"
        _botonera_para("jefes")
        _consola_para("jefes")
        estado.modulo_idx = None
        icono_cia.visible = False
        lbl_nombre.value = "JEFES"
        lbl_cis.value = ""
        mostrar(vista_jefes(
            estado.prog, estado.mundos,
            on_rejugar=lambda s: (mostrar_modulo(estado.idx_por_slug[s]),
                                  page.update()),
        ))

    def mostrar_avalancha():
        estado.vista = "avalancha"
        _botonera_para("avalancha")
        _consola_para("avalancha")
        estado.modulo_idx = None
        icono_cia.visible = False
        lbl_nombre.value = "AVALANCHA"
        lbl_cis.value = ""
        mostrar(vista_avalancha(
            estado.prog, estado.mundos,
            on_panteon=lambda m: iniciar_panteon(m),
        ))

    def mostrar_ajustes():
        estado.vista = "ajustes"
        _botonera_para("ajustes")
        _consola_para("ajustes")
        estado.modulo_idx = None
        icono_cia.visible = False
        lbl_nombre.value = "CONFIGURACIÓN"
        lbl_cis.value = ""

        def _dlc(valor: bool):
            estado.prog["dlc"] = valor
            PG.guardar(estado.prog)
            construir_lista()
            mostrar_ajustes()
            page.update()

        def _anim(valor: bool):
            estado.prog["anim"] = valor
            PG.guardar(estado.prog)

        def _nombre(valor: str):
            nombre = (valor or "").strip().upper()[:16] or "ANALISTA"
            estado.prog["heroe"] = nombre
            PG.guardar(estado.prog)
            mostrar_ajustes()
            page.update()

        mostrar(vista_ajustes(
            estado.prog, on_dlc=_dlc, on_anim=_anim, on_nombre=_nombre,
        ))

    def mostrar_datos():
        from modulos.common.paths import resolve_lab_paths
        estado.vista = "datos"
        _botonera_para("datos")
        _consola_para("datos")
        estado.modulo_idx = None
        icono_cia.visible = False
        lbl_nombre.value = "DATOS"
        lbl_cis.value = ""
        rutas = resolve_lab_paths()
        total = 0
        for base, _dirs, fich in os.walk(rutas["lab_dir"]):
            for f in fich:
                try:
                    total += os.path.getsize(os.path.join(base, f))
                except OSError:
                    pass

        async def _reset_arena_clean():
            import subprocess
            import sys as _sys
            proc = await __import__("asyncio").to_thread(
                subprocess.run,
                [_sys.executable, os.path.join(_DIR_RAIZ, "core", "lab_setup.py"),
                 "--clean"],
                capture_output=True, text=True, cwd=_DIR_RAIZ, timeout=120)
            for linea in proc.stdout.strip().split("\n"):
                if linea.strip():
                    log_sync(linea.strip())
            page.update()

        def _reset_progreso():
            PG.reset()
            estado.prog = PG.cargar()
            construir_lista()
            mostrar_datos()
            page.update()

        mostrar(vista_datos(
            rutas, f"{total // 1024} KB",
            on_reset_arena=lambda: page.run_task(_reset_arena_clean),
            on_reset_progreso=_reset_progreso,
        ))

    def mostrar_tutorial():
        estado.vista = "tutorial"
        _botonera_para("tutorial")
        _consola_para("tutorial")
        estado.modulo_idx = None
        icono_cia.visible = False
        lbl_nombre.value = "CÓMO JUGAR"
        lbl_cis.value = ""

        def _entendido():
            estado.prog["tutorial_visto"] = True
            PG.guardar(estado.prog)
            jugar_siguiente()

        mostrar(vista_tutorial(on_entendido=_entendido))

    def mostrar_modulo(idx: int):
        estado.vista = "modulo"
        _botonera_para("modulo")
        _consola_para("modulo")
        estado.modulo_idx = idx
        _num, nombre, _script, cia, _cis, _ref = MODULOS[idx]
        icono_cia.src = T.icono_cia(cia)
        icono_cia.visible = True
        lbl_nombre.value = f"  {meta(nombre)['alias']} ({nombre})"
        lbl_cis.value = cia
        mostrar(vista_modulo(idx, estado.prog))
        for tile in lista_modulos.controls:
            if isinstance(tile, ft.ListTile):
                tile.selected = (tile.data == idx)

    def mostrar_actual():
        if estado.vista == "tutorial":
            mostrar_tutorial()
        elif estado.vista == "modulo" and estado.modulo_idx is not None:
            mostrar_modulo(estado.modulo_idx)
        elif estado.vista == "mapa" and estado.mapa_mundo is not None:
            mostrar_mapa(estado.mapa_mundo)
        elif estado.vista == "jefes":
            mostrar_jefes()
        elif estado.vista == "avalancha":
            mostrar_avalancha()
        elif estado.vista == "ajustes":
            mostrar_ajustes()
        elif estado.vista == "datos":
            mostrar_datos()
        elif estado.vista == "combate" and estado.combate is not None:
            mostrar_combate()
        else:
            mostrar_progreso()

    # ── Combate por turnos ───────────────────────────────────────────────
    def _rutas_scripts(slug: str) -> tuple[str, str]:
        from app.config import MODULOS as _M
        script = next(m[2] for m in _M if m[1] == slug)
        return (os.path.join(_DIR_RAIZ, "modulos", slug, f"{script}.py"),
                os.path.join(_DIR_RAIZ, "modulos", slug, defensa_arch(slug)))

    def _sync_run(script: str) -> bool:
        import subprocess
        import sys as _sys
        try:
            proc = subprocess.run(
                [_sys.executable, script], capture_output=True, text=True,
                cwd=_DIR_RAIZ, timeout=120)
        except Exception:
            return False
        return proc.returncode == 0

    def mostrar_combate():
        estado.vista = "combate"
        _botonera_para("combate")
        _consola_para("combate")
        c = estado.combate
        assert c is not None
        icono_cia.visible = False
        lbl_nombre.value = f"COMBATE: {meta(c.slug)['alias']}"
        lbl_cis.value = meta(c.slug)["salon"]

        def _escena(*nombres: str):
            for nombre_esc in nombres:
                PG.marcar_escena(estado.prog, c.slug, nombre_esc)
            PG.guardar(estado.prog)

        def _revisar_captura():
            if c.terminado == "captura":
                PG.registrar_minijefe(estado.prog, c.slug, True, 0, 0, 1, 1)
                if c.slug not in estado.prog["sombra"]:
                    estado.prog["sombra"].append(c.slug)
                PG.guardar(estado.prog)
                log_sync(f"[SOMBRA] {meta(c.slug)['alias']} purificado. "
                         "Búscalo en JEFES.")

        async def _mover_ataque(cual: str):
            import asyncio as _aio
            _am, _de = _rutas_scripts(c.slug)
            if cual == "atacar":
                dano = await _aio.to_thread(c.atacar, lambda: _sync_run(_de))
                if dano >= 25:
                    _escena("defensa")
            elif cual == "analizar":
                c.analizar()
            elif cual == "parchar":
                await _aio.to_thread(
                    c.parchar,
                    lambda: _sync_run(os.path.join(_DIR_RAIZ, "core", "lab_setup.py")))
                _escena("setup")
            elif cual == "guardia":
                c.guardia()
            if c.terminado is None:
                await _aio.to_thread(c.turno_enemigo, lambda: _sync_run(_am))
            _revisar_captura()
            _ir(None)

        async def _usar_item(clave: str):
            import asyncio as _aio
            if not gastar(estado.prog, clave):
                return
            PG.guardar(estado.prog)
            _am, _de = _rutas_scripts(c.slug)
            if clave == "copia":
                await _aio.to_thread(
                    _sync_run, os.path.join(_DIR_RAIZ, "core", "lab_setup.py"))
                c.bitacora.append("[MOCHILA] Copia restaurada: arena sana.")
                _escena("setup")
            elif clave == "antivirus":
                c.activar_antivirus()
            elif clave == "senuelo":
                c.activar_senuelo()
            if c.terminado is None:
                # El señuelo se cobra dentro del turno enemigo (lo salta).
                await _aio.to_thread(c.turno_enemigo, lambda: _sync_run(_am))
            _revisar_captura()
            _ir(None)

        def _huir():
            log_sync("[HUIDA] Te repliegas al capítulo. La arena queda como está.")
            estado.submenu = None
            mostrar_modulo(estado.modulo_idx if estado.modulo_idx is not None else 0)
            page.update()

        def _ir(slot: str | None):
            estado.submenu = slot
            mostrar_combate()
            page.update()

        mostrar(vista_combate(
            c.slug, c.heroe_hp, c.enemigo_hp, c.bitacora, c.terminado,
            heroe=estado.prog.get("heroe", "") or "HÉROE",
            submenu=getattr(estado, "submenu", None),
            mochila=inventario(estado.prog),
            sombras=estado.prog.get("sombra", []),
            es_sombra=c.slug in estado.prog.get("sombra", []),
            on_menu=_ir,
            on_volver=lambda: _ir(None),
            on_movimiento=lambda cual: page.run_task(_mover_ataque, cual),
            on_item=lambda clave: page.run_task(_usar_item, clave),
            on_huir=_huir,
        ))

    def acc_luchar(e):
        if estado.modulo_idx is None or estado.ejecutando:
            return
        slug = estado.slug_por_idx[estado.modulo_idx]
        estado.combate = Combate(slug, aliadas=len(estado.prog.get("sombra", [])))
        estado.submenu = None
        c = estado.combate
        c.bitacora.append(
            f"[{meta(slug)['alias']}] {meta(slug)['salon']}. "
            "El bicho emerge en la arena...")

        async def _emerger():
            import asyncio as _aio
            if not is_lab_ready():
                await _aio.to_thread(
                    _sync_run, os.path.join(_DIR_RAIZ, "core", "lab_setup.py"))
            _am, _de = _rutas_scripts(slug)
            await _aio.to_thread(_sync_run, _am)
            for esc in ("setup", "simular"):
                PG.marcar_escena(estado.prog, slug, esc)
            PG.guardar(estado.prog)
            mostrar_combate()
            page.update()

        page.run_task(_emerger)

    def on_modulo_click(e):
        mostrar_modulo(e.control.data)
        page.update()

    # ── Sidebar ──────────────────────────────────────────────────────────
    def boton_sidebar(texto: str, color: str, handler):
        return ft.Button(texto, color=color, bgcolor=T.BG_PANEL,
                         on_click=handler)

    lista_modulos = ft.ListView(expand=True, spacing=2)

    def construir_lista():
        lista_modulos.controls.clear()
        dlc = estado.prog.get("dlc", False)
        for mundo, slugs in estado.mundos.items():
            lista_modulos.controls.append(
                ft.Text(mundo.upper(), color=T.TEXTO_DIM, size=T.TAM_MINIMO,
                        font_family=T.FUENTE))
            for slug in slugs:
                idx = estado.idx_por_slug[slug]
                bloqueado = not es_core(slug) and not dlc
                marca = "[DLC] " if bloqueado else ""
                tile = ft.ListTile(
                    leading=ft.Image(src=T.icono_modulo(slug), width=28,
                                     height=28,
                                     error_content=ft.Text("·", color=T.TEXTO_DIM)),
                    title=ft.Text(f"{marca}{meta(slug)['alias']}",
                                  font_family=T.FUENTE, size=13,
                                  color=T.TEXTO_DIM if bloqueado else T.TEXTO),
                    subtitle=ft.Text(slug, size=T.TAM_MINIMO, color=T.TEXTO_DIM,
                                     font_family=T.FUENTE),
                    data=idx,
                    disabled=bloqueado,
                    selected=(estado.modulo_idx == idx),
                    on_click=on_modulo_click,
                )
                lista_modulos.controls.append(tile)

    construir_lista()

    sidebar = ft.Container(
        width=240,
        bgcolor=T.BG_PANEL,
        padding=8,
        content=ft.Column([
            boton_sidebar("PROGRESO", T.CYAN,
                          lambda e: (mostrar_progreso(), page.update())),
            ft.Divider(height=8, color="transparent"),
            boton_sidebar("JUGAR", T.VERDE,
                          lambda e: (entrar(), jugar_siguiente())),
            ft.Divider(height=8, color="transparent"),
            ft.Text("HISTORIAS", color=T.TEXTO_DIM, size=12,
                    font_family=T.FUENTE),
            lista_modulos,
            ft.Divider(height=8),
            boton_sidebar("JEFES", T.ROJO,
                          lambda e: (mostrar_jefes(), page.update())),
            boton_sidebar("AVALANCHA", T.ROJO,
                          lambda e: (mostrar_avalancha(), page.update())),
            boton_sidebar("CONFIG", T.AMARILLO,
                          lambda e: (mostrar_ajustes(), page.update())),
            boton_sidebar("DATOS", T.VERDE,
                          lambda e: (mostrar_datos(), page.update())),
            boton_sidebar("CÓMO JUGAR", T.MORADO,
                          lambda e: (mostrar_tutorial(), page.update())),
            boton_sidebar("MENÚ", T.TEXTO_DIM,
                          lambda e: mostrar_portada()),
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
        boton_accion(" Luchar  ", T.CYAN, acc_luchar),
        boton_accion("Minijefe ", T.NARANJA, acc_juego),
        boton_accion(" Archivo ", T.MORADO, acc_guia),
    ], spacing=6)
    consola_cab = ft.Row([
        ft.Text("CONSOLA", color=T.TEXTO_DIM, size=12,
                font_family=T.FUENTE, expand=True),
        ft.TextButton("X", on_click=lambda e: (consola.controls.clear(),
                                               page.update())),
    ], spacing=4)
    caja_consola = ft.Container(content=consola, bgcolor=T.BG_CONSOLA,
                                border_radius=6, padding=4)

    lab = ft.Container(
        bgcolor=T.BG, expand=True, padding=4, visible=False,
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
    portada = ft.Container(expand=True)

    def mostrar_portada():
        from app.recursos import verificar
        estado.vista = "portada"
        estado.modulo_idx = None
        faltan = verificar()
        alerta = (f"[ALERTA] Faltan {len(faltan)} recursos empaquetados. "
                  "Reinstala el juego." if faltan else None)
        if faltan:
            log_sync(f"[ALERTA] Recursos faltantes: {', '.join(faltan[:5])}")
        portada.content = vista_portada(
            PG.siguiente_capitulo(estado.prog, estado.campana),
            estado.prog,
            primera=PG.es_primera_vez(estado.prog),
            alerta=alerta,
            on_jugar=jugar_siguiente,
            on_historias=lambda: (entrar(), mostrar_progreso(),
                                  page.update()),
            on_avalancha=lambda: (entrar(), mostrar_avalancha(), page.update()),
            on_config=lambda: (entrar(), mostrar_ajustes(), page.update()),
            on_datos=lambda: (entrar(), mostrar_datos(), page.update()),
            on_como=lambda: (entrar(), mostrar_tutorial(), page.update()),
            on_salir=lambda: page.run_task(page.window.close),
        )
        portada.visible = True
        lab.visible = False
        page.update()

    def entrar():
        portada.visible = False
        lab.visible = True

    page.add(lab, portada)
    mostrar_portada()
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
