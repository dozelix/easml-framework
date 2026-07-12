#!/usr/bin/env python3
"""
Simulacion educativa de Keylogger — Modulo 03.

Demuestra el comportamiento de un registrador de teclas generando sesiones
ficticias de escritura (correo electronico, banca en linea, chat, busquedas).
NO captura teclas reales del sistema — genera un keylog.log con eventos
simulados que muestran como un keylogger real captura datos sensibles.

Uso:
    python modulos/03_keylogger/keylogger.py          Ejecutar simulacion
    python modulos/03_keylogger/keylogger.py --clean  Limpiar artefactos
    python modulos/03_keylogger/keylogger.py --help   Mostrar ayuda
"""
import os
import sys
import time
import argparse

_DIR_RAIZ = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, _DIR_RAIZ)

from core.common import (
    log, safe_print, color, banner, cleanup, write_log, LOG_LINES,
    find_lab_dir,
)

# ── Constantes ──────────────────────────────────────────────────────────────
# Directorio donde se genera el keylog
DIR_SIMULACION = find_lab_dir(_DIR_RAIZ)

# Nombre del archivo de log del keylogger
LOG_KEYLOG = 'keylog.log'


# ── Sesiones simuladas ──────────────────────────────────────────────────────
# Cada sesion representa un escenario tipico que un keylogger real capturaria.
# Los teclas incluyen texto normal y especiales ([ENTER], [TAB]).

SESIONES = [
    {
        'id': 1,
        'descripcion': 'Inicio de sesion en correo electronico',
        'contexto': 'Navegador web — Gmail',
        'timestamp': '2026-07-10 14:13:00',
        'teclas': [
            ('u', 0.07), ('s', 0.06), ('u', 0.08), ('a', 0.07), ('r', 0.06),
            ('i', 0.07), ('o', 0.08), ('.', 0.05), ('g', 0.07), ('m', 0.09),
            ('a', 0.07), ('i', 0.06), ('l', 0.08), ('.', 0.05), ('c', 0.07),
            ('o', 0.06), ('m', 0.09),
            ('[ENTER]', 0.15),
            ('[TAB]', 0.10),
            ('c', 0.07), ('l', 0.08), ('a', 0.07), ('v', 0.06), ('e', 0.08),
            ('1', 0.05), ('2', 0.07), ('3', 0.06), ('!', 0.08),
            ('[ENTER]', 0.20),
        ],
    },
    {
        'id': 2,
        'descripcion': 'Mensaje en chat de trabajo',
        'contexto': 'Slack / Teams',
        'timestamp': '2026-07-10 14:16:30',
        'teclas': [
            ('H', 0.06), ('o', 0.07), ('l', 0.08), ('a', 0.07), (',', 0.05),
            (' ', 0.04), ('t', 0.07), ('o', 0.06), ('d', 0.08), ('o', 0.07),
            ('s', 0.06), (' ', 0.04), ('b', 0.07), ('i', 0.08), ('e', 0.07),
            ('n', 0.06), ('?', 0.05),
            ('[ENTER]', 0.15),
            ('E', 0.06), ('l', 0.07), (' ', 0.04), ('i', 0.07), ('n', 0.06),
            ('f', 0.08), ('o', 0.07), ('r', 0.06), ('m', 0.08), ('e', 0.07),
            (' ', 0.04), ('d', 0.07), ('e', 0.06), ('l', 0.08), (' ', 0.04),
            ('Q', 0.06), ('2', 0.07), (' ', 0.04), ('e', 0.06), ('s', 0.07),
            ('t', 0.06), ('a', 0.08), (' ', 0.04), ('l', 0.07), ('i', 0.06),
            ('s', 0.08), ('t', 0.07), ('o', 0.06),
            ('[ENTER]', 0.15),
        ],
    },
    {
        'id': 3,
        'descripcion': 'Login en portal bancario',
        'contexto': 'Banco online — Formulario de acceso',
        'timestamp': '2026-07-10 14:20:15',
        'teclas': [
            ('[TAB]', 0.10),
            ('D', 0.08), ('N', 0.07), ('I', 0.09), (' ', 0.04),
            ('3', 0.06), ('0', 0.07), ('.', 0.05), ('1', 0.08), ('2', 0.07),
            ('3', 0.09), ('.', 0.05), ('4', 0.08), ('5', 0.07), ('6', 0.09),
            ('[TAB]', 0.10),
            ('c', 0.08), ('o', 0.07), ('n', 0.09), ('t', 0.07), ('r', 0.06),
            ('a', 0.08), ('s', 0.07), ('e', 0.09), ('n', 0.07), ('a', 0.08),
            ('B', 0.06), ('a', 0.07), ('n', 0.09), ('c', 0.07), ('o', 0.06),
            ('!', 0.08),
            ('[ENTER]', 0.20),
        ],
    },
    {
        'id': 4,
        'descripcion': 'Busqueda en Google',
        'contexto': 'Navegador web',
        'timestamp': '2026-07-10 14:23:40',
        'teclas': [
            ('[TAB]', 0.10),
            ('c', 0.08), ('o', 0.07), ('m', 0.09), ('o', 0.07),
            (' ', 0.04), ('p', 0.07), ('r', 0.06), ('o', 0.08), ('t', 0.07),
            ('e', 0.06), ('g', 0.08), ('e', 0.07), ('r', 0.06),
            (' ', 0.04), ('u', 0.07), ('n', 0.08), (' ', 0.04),
            ('r', 0.06), ('e', 0.08), ('d', 0.07), (' ', 0.04),
            ('c', 0.07), ('o', 0.06), ('r', 0.08), ('p', 0.07),
            ('o', 0.06), ('r', 0.07), ('a', 0.08), ('t', 0.07), ('i', 0.06),
            ('v', 0.08), ('a', 0.07),
            ('[ENTER]', 0.15),
        ],
    },
    {
        'id': 5,
        'descripcion': 'Compra online con tarjeta de credito',
        'contexto': 'Tienda en linea — Checkout',
        'timestamp': '2026-07-10 14:27:10',
        'teclas': [
            ('[TAB]', 0.10),
            ('4', 0.06), ('5', 0.07), ('3', 0.08), ('2', 0.07),
            (' ', 0.04),
            ('1', 0.06), ('2', 0.07), ('3', 0.08), ('4', 0.07),
            (' ', 0.04),
            ('5', 0.06), ('6', 0.07), ('7', 0.08), ('8', 0.07),
            (' ', 0.04),
            ('9', 0.06), ('0', 0.07), ('1', 0.08), ('2', 0.07),
            ('[TAB]', 0.10),
            ('1', 0.06), ('2', 0.07), ('/', 0.05), ('2', 0.08),
            ('8', 0.07), ('/', 0.05), ('2', 0.08), ('0', 0.07),
            ('2', 0.08), ('9', 0.07),
            ('[TAB]', 0.10),
            ('1', 0.06), ('2', 0.07), ('3', 0.08),
            ('[ENTER]', 0.20),
        ],
    },
]


# ── Funciones auxiliares ────────────────────────────────────────────────────

def paso_fase(fase_num, titulo):
    """Imprime encabezado de fase."""
    safe_print(color(f"\n  [FASE {fase_num}] {titulo}", 'yellow'))
    safe_print(color(f"  {'─' * 55}", 'yellow'))
    time.sleep(0.3)


def preparar_directorio():
    """Crea directorio_pruebas/ si no existe."""
    os.makedirs(DIR_SIMULACION, exist_ok=True)
    log(f"Directorio de trabajo: {DIR_SIMULACION}")
    safe_print(color(f"  Directorio: {DIR_SIMULACION}\n", 'green'))


def simular_sesion(sesion):
    """
    Simula la captura de teclas para una sesion del usuario.

    Retorna el texto acumulado (para mostrar en consola) y las lineas
    del log (para escribir en keylog.log).

    En un keylogger REAL, la captura se haria via:
    - SetWindowsHookEx(WH_KEYBOARD) en Windows
    - /dev/input/eventX en Linux
    - Driver de teclado a nivel kernel
    """
    lineas_sesion = []
    captura = ""

    for tecla, delay in sesion['teclas']:
        if tecla == '[ENTER]':
            captura += " ↵"
            # Registrar ENTER como evento especial
            lineas_sesion.append(
                f"  [{sesion['timestamp']}] [ENTER]\n"
            )
            # Mostrar la linea completa en consola
            safe_print(color(f"    → {captura.strip()}", 'green'))
            captura = ""
        elif tecla == '[TAB]':
            captura += " →TAB← "
            lineas_sesion.append(
                f"  [{sesion['timestamp']}] [TAB]\n"
            )
        else:
            captura += tecla
            # Registrar cada tecla individual con su keycode
            key_code = ord(tecla.lower()) if len(tecla) == 1 else 0
            lineas_sesion.append(
                f"  [{sesion['timestamp']}] tecla='{tecla}' keycode={key_code}\n"
            )

        # Simular delay de escritura humana (~50-100ms entre teclas)
        time.sleep(0.015)

    # Si queda texto sin ENTER al final
    if captura.strip():
        safe_print(color(f"    → {captura.strip()}", 'green'))

    return lineas_sesion


def ejecutar_simulacion():
    """Ejecuta la simulacion completa del keylogger."""
    banner(
        "KEYLOGGER — SIMULACION EDUCATIVA",
        "Genera sesiones ficticias de escritura para demostrar captura de teclas",
    )
    safe_print(color(
        "  Este script NO captura teclas reales del sistema.\n"
        "  Genera un keylog.log con eventos ficticios que simulan\n"
        "  como un keylogger real captura datos sensibles.\n",
        'cyan',
    ))

    # ── FASE 1: Preparacion ─────────────────────────────────────────────────
    paso_fase(1, "PREPARACION — Preparando directorio de trabajo")
    log("Fase 1: Preparacion")
    preparar_directorio()
    time.sleep(0.5)

    # ── FASE 2: Instalacion ─────────────────────────────────────────────────
    paso_fase(2, "INSTALACION — El keylogger se activa en el sistema")
    log("Fase 2: Instalacion del keylogger")
    safe_print(color(
        "  En un ataque real, el keylogger se instalaria via:\n",
        'cyan',
    ))
    vectores = [
        "Trojan disfrazado de software legitimo (ej: keygen, crack)",
        "Phishing con archivo adjunto malicioso (.docm, .exe)",
        "Exploit que inyecta un hook en la API de teclado",
        "Driver de teclado malicioso cargado a nivel de kernel",
        "Dispositivo de hardware inline entre teclado y PC",
    ]
    for v in vectores:
        safe_print(color(f"    - {v}", 'red'))
    safe_print(color(
        "\n  Tipos de keylogger segun su nivel de intervencion:\n",
        'cyan',
    ))
    tipos = [
        ("API-based", "SetWindowsHookEx(WH_KEYBOARD)", "Nivel de usuario"),
        ("Driver", "Driver de teclado virtual interceptado", "Kernel"),
        ("Kernel", "Rootkit que intercepta IRQ del teclado", "Ring 0"),
        ("Hardware", "Dispositivo fisico inline USB/PS2", "Fisico"),
    ]
    for nombre, metodo, nivel in tipos:
        safe_print(color(
            f"    [{nombre:12s}] {metodo:50s} ({nivel})",
            'blue',
        ))
    safe_print(color(
        "\n  Modo de captura simulado: API-based (nivel de usuario)\n",
        'green',
    ))
    time.sleep(0.5)

    # ── FASE 3: Captura de teclas ───────────────────────────────────────────
    paso_fase(3, "CAPTURA — Monitoreando eventos de teclado")
    log("Fase 3: Captura de eventos")
    safe_print(color(
        "  Simulando actividad de un usuario real...\n",
        'cyan',
    ))

    # Preparar encabezado del log
    lineas_log = []
    encabezado = (
        f"{'='*65}\n"
        f"KEYLOG SIMULADO — REGISTRO DE CAPTURA DE TECLAS\n"
        f"{'='*65}\n"
        f"[SIMULACION EDUCATIVA — NO CAPTURA TECLAS REALES]\n"
        f"Este archivo fue generado con fines educativos.\n"
        f"Directorio: {DIR_SIMULACION}\n"
        f"{'='*65}\n\n"
    )
    lineas_log.append(encabezado)

    total_teclas = 0

    for sesion in SESIONES:
        safe_print(color(
            f"\n  Sesion {sesion['id']}: {sesion['descripcion']}",
            'cyan',
        ))
        safe_print(color(f"  Contexto: {sesion['contexto']}\n", 'blue'))

        # Encabezado de sesion en el log
        lineas_log.append(
            f"{'─'*50}\n"
            f"[{sesion['timestamp']}] SESION {sesion['id']}: {sesion['contexto']}\n"
            f"{'─'*50}\n"
        )

        # Simular captura de teclas
        lineas_sesion = simular_sesion(sesion)
        lineas_log.extend(lineas_sesion)
        total_teclas += len(sesion['teclas'])

        safe_print(color(
            f"    [!] {len(sesion['teclas'])} teclas capturadas",
            'yellow',
        ))
        time.sleep(0.4)

    # Guardar el log
    ruta_log = os.path.join(DIR_SIMULACION, LOG_KEYLOG)
    with open(ruta_log, 'w', encoding='utf-8') as f:
        f.writelines(lineas_log)

    log(f"Keylog generado: {ruta_log} ({total_teclas} teclas)")
    safe_print(color(f"\n  Log generado: {ruta_log}", 'yellow'))
    time.sleep(0.5)

    # ── FASE 4: Exfiltracion ────────────────────────────────────────────────
    paso_fase(4, "EXFILTRACION — Envio de datos capturados al atacante")
    log("Fase 4: Exfiltracion")
    safe_print(color(
        "  En un ataque real, los datos capturados se enviarian via:\n",
        'cyan',
    ))
    metodos = [
        ("Email cifrado", "Envio periodico a buzon del atacante"),
        ("DNS tunneling", "Exfiltracion oculta en consultas DNS"),
        ("HTTP/HTTPS POST", "Conexion a servidor C2 (Command & Control)"),
        ("Almacenamiento local", "Para acceso fisico directo al equipo"),
    ]
    for metodo, desc in metodos:
        safe_print(color(f"    - {metodo:25s} — {desc}", 'red'))
    safe_print(color(
        f"\n  Aqui los datos se almacenan localmente en: {ruta_log}\n",
        'cyan',
    ))
    time.sleep(0.5)

    # ── FASE 5: Analisis de datos capturados ────────────────────────────────
    paso_fase(5, "ANALISIS — Informacion que se revelaria al atacante")
    safe_print(color(
        "  Los datos capturados por un keylogger real incluirian:\n",
        'cyan',
    ))
    datos_riesgo = [
        ("Credenciales de acceso", "usuario + contrasena de email, redes sociales", "ALTO"),
        ("Datos bancarios", "DNI, numeros de cuenta, tarjeta de credito, PIN", "CRITICO"),
        ("Mensajes privados", "chats de trabajo, emails personales, DMs", "MEDIO"),
        ("Busquedas sensibles", "consultas medicas, legales, financieras", "MEDIO"),
        ("Documentos corporativos", "secretos comerciales, propiedad intelectual", "ALTO"),
    ]
    for nombre, desc, nivel in datos_riesgo:
        color_nivel = 'red' if nivel in ('ALTO', 'CRITICO') else 'yellow'
        safe_print(color(
            f"    [{nivel:8s}] {nombre:30s} — {desc}",
            color_nivel,
        ))

    safe_print(color(
        "\n  LECCION EDUCATIVA:",
        'bold',
    ))
    safe_print(color(
        "  - Los keyloggers son una de las herramientas de espionaje mas antiguas.\n"
        "  - La mejor defensa es 2FA + gestor de contrasenas con autocompletado.\n"
        "  - Monitorear procesos sin interfaz y alto uso de CPU.\n"
        "  - Inspecionar fisicamente los dispositivos USB conectados.\n"
        "  - Usar teclado virtual (on-screen keyboard) para datos sensibles.\n",
        'cyan',
    ))

    write_log("keylogger_sim", list(LOG_LINES))


def limpiar():
    """Elimina directorio_pruebas/ y logs residuales."""
    banner("KEYLOGGER — LIMPIEZA", "Eliminando artefactos de la simulacion")
    removed = 0

    if os.path.isdir(DIR_SIMULACION):
        import shutil
        shutil.rmtree(DIR_SIMULACION)
        safe_print(color(f"  eliminado: directorio_pruebas/", 'green'))
        removed += 1

    removed += cleanup(patterns=['keylogger_sim.log'])

    safe_print(color(f"\n  Limpieza completada: {removed} artefactos eliminados.\n", 'green'))


def main():
    parser = argparse.ArgumentParser(
        description="Simulacion educativa de Keylogger",
        epilog=(
            "NO captura teclas reales. Genera sesiones ficticias en\n"
            "directorio_pruebas/keylog.log con fines educativos."
        ),
    )
    parser.add_argument(
        '--clean',
        action='store_true',
        help='Eliminar directorio_pruebas/ y logs',
    )
    args = parser.parse_args()

    if args.clean:
        limpiar()
    else:
        ejecutar_simulacion()


if __name__ == "__main__":
    main()
