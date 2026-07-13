#!/usr/bin/env python3 cazador de amenazas
"""
Defensa contra simulacion de Keylogger — Modulo 03.

Detecta archivos de log sospechosos (keylog.log), analiza patrones de datos
sensibles capturados (contrasenas, datos bancarios, credenciales) y ofrece
limpieza segura.

Uso:
    python modulos/03_keylogger/defensa.py          Ejecutar escaneo defensivo
    python modulos/03_keylogger/defensa.py --clean  Limpiar artefactos
    python modulos/03_keylogger/defensa.py --help   Mostrar ayuda
"""
import os
import sys
import re
import glob
import argparse

_DIR_RAIZ = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, _DIR_RAIZ)

from core.common import (
    log, safe_print, color, banner, cleanup, write_log,    find_lab_dir,)

# ── Constantes ──────────────────────────────────────────────────────────────
DIR_SIMULACION = find_lab_dir(_DIR_RAIZ)
LOG_KEYLOG = 'keylog.log'
LOG_DEFENSA = 'defensa_keylogger.log'


# ── Funciones auxiliales ────────────────────────────────────────────────────

def paso_fase(fase_num, titulo):
    """Imprime encabezado de fase."""
    safe_print(color(f"\n  [FASE {fase_num}] {titulo}", 'yellow'))
    safe_print(color(f"  {'─' * 55}", 'yellow'))


def escanear_keylog():
    """
    Busca archivos de log con patrones de keylogger.

    Un SOC analyst buscaria:
    1. Archivos .log con patrones 'tecla=' o 'keycode='
    2. Archivos en directorios inusuales
    3. Procesos que escriben logs de forma persistente
    """
    hallazgos = []

    # Buscar en directorio_pruebas/
    if os.path.isdir(DIR_SIMULACION):
        ruta_log = os.path.join(DIR_SIMULACION, LOG_KEYLOG)
        if os.path.exists(ruta_log):
            tamano = os.path.getsize(ruta_log)
            with open(ruta_log, 'r', encoding='utf-8', errors='replace') as f:
                lineas = f.readlines()
            hallazgos.append({
                'nombre': LOG_KEYLOG,
                'ruta': ruta_log,
                'tamano': tamano,
                'lineas': len(lineas),
            })

    # Buscar otros .log sospechosos en el directorio actual
    for archivo in glob.glob('*.log'):
        if archivo in (LOG_KEYLOG, LOG_DEFENSA, 'keylogger_sim.log'):
            continue
        try:
            with open(archivo, 'r', encoding='utf-8', errors='replace') as f:
                contenido = f.read(8192)
            patrones_keylogger = ['tecla=', 'keycode=', 'KEYLOG', 'keystroke']
            if any(p in contenido for p in patrones_keylogger):
                hallazgos.append({
                    'nombre': archivo,
                    'ruta': archivo,
                    'tamano': os.path.getsize(archivo),
                    'lineas': contenido.count('\n'),
                })
        except Exception:
            pass

    return hallazgos


def analizar_contenido_log(ruta_log):
    """
    Analiza el contenido del keylog buscando patrones de datos sensibles.

    En un entorno SOC real, este analisis se automatizaria con:
    - SIEM con reglas de DLP (Data Loss Prevention)
    - EDR con deteccion de acceso a formularios web
    - Monitoreo de trafico de red para exfiltracion
    """
    try:
        with open(ruta_log, 'r', encoding='utf-8', errors='replace') as f:
            contenido = f.read()
    except Exception as e:
        safe_print(color(f"    Error leyendo log: {e}", 'red'))
        return {}

    resultados = {
        'total_teclas': contenido.count("tecla='"),
        'enter_keys': contenido.count('[ENTER]'),
        'tab_keys': contenido.count('[TAB]'),
        'sesiones': contenido.count('SESION'),
    }

    # Reconstruir el texto escrito a partir de las entradas de tecla
    # Formato: tecla='x' keycode=NN  o  [ENTER]  o  [TAB]
    texto_reconstruido = []
    for linea in contenido.split('\n'):
        match = re.search(r"tecla='([^']*)'", linea)
        if match:
            texto_reconstruido.append(match.group(1))
        elif '[ENTER]' in linea:
            texto_reconstruido.append(' ')
        elif '[TAB]' in linea:
            texto_reconstruido.append(' ')
    texto_completo = ''.join(texto_reconstruido)

    # Detectar patrones de datos sensibles en el texto reconstruido
    patrones_sensibles = {
        'Credenciales de email': [
            (r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}", "Email completo"),
            (r"gmail\.com", "Dominio Gmail"),
            (r"hotmail\.com", "Dominio Hotmail"),
            (r"yahoo\.com", "Dominio Yahoo"),
        ],
        'Contrasenas / Credenciales': [
            (r"contrase", "Patron 'contrase' (contrasena)"),
            (r"clave", "Patron 'clave'"),
            (r"password", "Patron 'password'"),
            (r"login", "Patron 'login'"),
            (r"usuario", "Patron 'usuario'"),
        ],
        'Datos bancarios': [
            (r"[0-9]{2}\.[0-9]{3}\.[0-9]{3}", "DNI formato XX.XXX.XXX"),
            (r"[0-9]{4}\s?[0-9]{4}\s?[0-9]{4}\s?[0-9]{4}", "Tarjeta de credito (16 digitos)"),
            (r"[0-9]{2}/[0-9]{2}/[0-9]{4}", "Fecha DD/MM/AAAA"),
            (r"banco", "Palabra 'banco'"),
            (r"tarjeta", "Palabra 'tarjeta'"),
        ],
    }

    encontrados = {}
    for categoria, lista_patrones in patrones_sensibles.items():
        hallazgos_categoria = []
        for patron, desc in lista_patrones:
            matches = re.findall(patron, texto_completo, re.IGNORECASE)
            if matches:
                hallazgos_categoria.append(f"{desc} ({len(matches)} ocurrencias)")
        if hallazgos_categoria:
            encontrados[categoria] = hallazgos_categoria

    resultados['datos_sensibles'] = encontrados
    resultados['texto_reconstruido'] = texto_completo
    return resultados


def mostrar_procesos_sospechosos():
    """
    Muestra informacion sobre procesos que podrian ser keyloggers.

    En un entorno real, un SOC analyst usaria:
    - Process Monitor (Sysinternals) para Windows
    - lsof / ps en Linux
    - EDR corporativo con monitoreo de hooks
    """
    safe_print(color("  Tipos de proceso que podrian ocultar un keylogger:\n", 'cyan'))
    procesos = [
        ('svchost.exe (fake)', 'Nombre comun para inyectar codigo malicioso', 'MEDIA'),
        ('csrss.exe (fake)', 'Proceso critico del sistema, objetivo de rootkits', 'ALTA'),
        ('winlogon.exe (fake)', 'Puede ser reemplazado para persistencia', 'ALTA'),
        ('[sin ventana visible]', 'Procesos sin GUI sospechosos', 'MEDIA'),
        ('[nombre aleatorio]', 'Nombres como xk29d.exe, tmp8473.exe', 'BAJA'),
    ]
    for nombre, desc, nivel in procesos:
        c = 'red' if nivel == 'ALTA' else 'yellow'
        safe_print(color(f"    {nombre:30s} — {desc:45s} [riesgo: {nivel}]", c))

    safe_print(color(
        "\n  En Linux/Mac los keyloggers usan /dev/input/ o X11 hooks.",
        'cyan',
    ))
    safe_print(color(
        "  Usa 'lsof /dev/input/*' o 'xinput list' para inspeccionar.\n",
        'cyan',
    ))


def ejecutar_escaneo():
    """Ejecuta el proceso defensivo completo contra el keylogger."""
    banner(
        "DEFENSA KEYLOGGER — DETECCION Y ANALISIS",
        "Detecta logs de keylogger y analiza datos sensibles capturados",
    )
    safe_print(color(
        "  Herramienta defensiva para detectar artefactos del modulo 03.\n",
        'cyan',
    ))

    # ── FASE 1: Escaneo de archivos de log ──────────────────────────────────
    paso_fase(1, "ESCANEADO — Buscando archivos de log sospechosos")
    hallazgos = escanear_keylog()

    if hallazgos:
        safe_print(color(
            f"  [!] ALERTA: {len(hallazgos)} archivo(s) sospechoso(s) detectado(s)\n",
            'red',
        ))
        for h in hallazgos:
            safe_print(color(
                f"    [!] {h['nombre']} — {h['tamano']} bytes, {h['lineas']} lineas",
                'red',
            ))
            safe_print(color(f"        Ruta: {h['ruta']}", 'blue'))
    else:
        safe_print(color(
            "  [OK] No se encontraron archivos de log sospechosos.\n",
            'green',
        ))
        return

    # ── FASE 2: Analisis de contenido ───────────────────────────────────────
    paso_fase(2, "ANALISIS — Inspeccionando contenido del keylog")
    safe_print(color(
        "  Buscando patrones de datos sensibles capturados...\n",
        'cyan',
    ))

    for h in hallazgos:
        safe_print(color(f"\n  Analisis de {h['nombre']}:", 'cyan'))
        resultados = analizar_contenido_log(h['ruta'])

        safe_print(color(f"    Total teclas registradas:  {resultados.get('total_teclas', 0)}", 'yellow'))
        safe_print(color(f"    Teclas ENTER capturadas:   {resultados.get('enter_keys', 0)}", 'yellow'))
        safe_print(color(f"    Teclas TAB capturadas:     {resultados.get('tab_keys', 0)}", 'yellow'))
        safe_print(color(f"    Sesiones de escritura:     {resultados.get('sesiones', 0)}", 'yellow'))

        # Mostrar texto reconstruido (primeros 200 chars)
        texto = resultados.get('texto_reconstruido', '')
        if texto:
            fragmento = texto[:200].strip()
            if len(texto) > 200:
                fragmento += '...'
            safe_print(color(f"\n    Texto reconstruido (muestra):", 'cyan'))
            safe_print(color(f"      \"{fragmento}\"", 'blue'))

        datos = resultados.get('datos_sensibles', {})
        if datos:
            safe_print(color(
                f"\n    [!] DATOS SENSIBLES DETECTADOS:",
                'red',
            ))
            for categoria, hallazgos_cat in datos.items():
                safe_print(color(f"      {categoria}:", 'red'))
                for desc in hallazgos_cat:
                    safe_print(color(f"        - {desc}", 'yellow'))
        else:
            safe_print(color(
                "    [OK] No se detectaron patrones de datos sensibles.\n",
                'green',
            ))

    # ── FASE 3: Monitoreo de procesos ───────────────────────────────────────
    paso_fase(3, "MONITOREO — Procesos que podrian ser keyloggers")
    mostrar_procesos_sospechosos()

    # ── FASE 4: Resumen ─────────────────────────────────────────────────────
    paso_fase(4, "RESUMEN DE DEFENSA")
    safe_print(color(f"\n  Artefactos encontrados: {len(hallazgos)}", 'red'))

    if hallazgos:
        safe_print(color(
            "  Ejecuta con --clean para eliminar los logs del keylogger.\n",
            'yellow',
        ))

    safe_print(color("  PREVENCION — Como protegerse en produccion:", 'bold'))
    prevencion = [
        "Usar gestor de contrasenas con autocompletado (nunca escribir a mano)",
        "Autenticacion de dos factores (2FA) en todas las cuentas criticas",
        "Teclado virtual (on-screen keyboard) para datos financieros",
        "Inspecion fisica de dispositivos USB conectados al equipo",
        "EDR corporativo con monitoreo de hooks de teclado",
        "Actualizaciones regulares del sistema operativo",
        "No instalar software de fuentes no verificadas",
    ]
    for p in prevencion:
        safe_print(color(f"    - {p}", 'cyan'))

    write_log("defensa_keylogger", [
        "Escaneo defensivo completado",
        f"Archivos sospechosos: {len(hallazgos)}",
    ])


def limpiar():
    """Elimina directorio_pruebas/ y logs residuales."""
    banner("DEFENSA KEYLOGGER — LIMPIEZA", "Eliminando artefactos de la simulacion")
    removed = 0

    if os.path.isdir(DIR_SIMULACION):
        import shutil
        shutil.rmtree(DIR_SIMULACION)
        safe_print(color(f"  eliminado: directorio_pruebas/", 'green'))
        removed += 1

    removed += cleanup(patterns=[LOG_DEFENSA, 'keylogger_sim.log'])

    safe_print(color(f"\n  Limpieza completada: {removed} artefactos eliminados.\n", 'green'))


def main():
    parser = argparse.ArgumentParser(
        description="Defensa contra simulacion de Keylogger",
        epilog=(
            "Detecta logs de keylogger, analiza datos sensibles capturados\n"
            "y elimina artefactos."
        ),
    )
    parser.add_argument(
        '--clean',
        action='store_true',
        help='Eliminar directorio_pruebas/ y logs residuales',
    )
    args = parser.parse_args()

    if args.clean:
        limpiar()
    else:
        ejecutar_escaneo()


if __name__ == "__main__":
    main()
