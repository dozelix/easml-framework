#!/usr/bin/env python3
"""
Modulo 06 - Defensa contra puerta trasera (backdoor) educativa.

Detecta archivos de configuracion C2, registros de reverse shell
y artefactos de persistencia. Realiza limpieza completa.

SOLO PARA USO EDUCATIVO EN ENTORNO CONTROLADO.

Uso:
    python modulos/06_backdoor/defensa.py           Ejecutar defensa
    python modulos/06_backdoor/defensa.py --help    Mostrar ayuda
"""
import os
import sys
import json

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, ROOT)

from modulos.common.utils import (
    banner, color, safe_print, log, LOG_LINES,
    write_log, hash_file, traverse_lab_files, find_lab_dir,
)

# ── Ruta del directorio de pruebas ──
LAB_DIR = find_lab_dir(ROOT)

# ── Marcadores de IOC ──
C2_MARKER = "C2_BACKDOOR_SIMULATION"
SHELL_MARKER = "SHELL_SIMULATION"

# ── IPs y puertos comunmente usados por backdoors ──
SUSPICIOUS_PORTS = [443, 8443, 80, 4444, 5555, 1337, 31337]
SUSPICIOUS_IPS = [
    "192.168.1.100", "10.0.0.50", "172.16.0.25",
    "127.0.0.1", "0.0.0.0",
]


# ══════════════════════════════════════════════════════════════
#  FUNCIONES AUXILIARES
# ══════════════════════════════════════════════════════════════

def _short_hash(path):
    h = hash_file(path)
    return h[:16] + "..." if h else "N/A"


# ══════════════════════════════════════════════════════════════
#  FUNCIONES DE DETECCION
# ══════════════════════════════════════════════════════════════

def escanear_marcadores():
    """
    Busca archivos con marcadores de backdoor en su contenido.

    En un entorno real, esto equivale a reglas YARA o IOC
    que buscan patrones conocidos de backdoors.
    """
    hallazgos = []
    if not os.path.isdir(LAB_DIR):
        return hallazgos

    for fname in os.listdir(LAB_DIR):
        fpath = os.path.join(LAB_DIR, fname)
        if not os.path.isfile(fpath):
            continue
        try:
            with open(fpath, 'r', encoding='utf-8', errors='ignore') as f:
                contenido = f.read(8192)
            marcadores = []
            if C2_MARKER in contenido:
                marcadores.append('C2_CONFIG')
            if SHELL_MARKER in contenido:
                marcadores.append('SHELL_LOG')
            if marcadores:
                hallazgos.append({
                    'path': fpath,
                    'nombre': fname,
                    'marcadores': marcadores,
                    'hash': _short_hash(fpath),
                    'size': os.path.getsize(fpath),
                })
        except Exception:
            pass
    return hallazgos


def escanear_config_c2():
    """
    Analiza archivos JSON buscando configuraciones C2.

    En un entorno real, un analista de SOC buscaria:
    - IPs de servidores conocidos maliciosos
    - Puertos no estandar o inusuales
    - Patrones de comunicacion C2 en JSON/XML
    """
    hallazgos = []
    if not os.path.isdir(LAB_DIR):
        return hallazgos

    for fname in os.listdir(LAB_DIR):
        if not fname.endswith('.json'):
            continue
        fpath = os.path.join(LAB_DIR, fname)
        try:
            with open(fpath, 'r', encoding='utf-8') as f:
                data = json.load(f)

            ips_sospechosas = []
            puertos_sospechosos = []

            if isinstance(data, dict):
                for srv in data.get('servidores_c2', []):
                    addr = srv.get('direccion', '')
                    port = srv.get('puerto', 0)
                    if addr in SUSPICIOUS_IPS:
                        ips_sospechosas.append(addr)
                    if port in SUSPICIOUS_PORTS:
                        puertos_sospechosos.append(port)

            if ips_sospechosas or puertos_sospechosos:
                hallazgos.append({
                    'path': fpath,
                    'nombre': fname,
                    'ips_sospechosas': ips_sospechosas,
                    'puertos_sospechosos': puertos_sospechosos,
                    'hash': _short_hash(fpath),
                })
        except Exception:
            pass
    return hallazgos


def escanear_persistencia():
    """
    Detecta archivos de persistencia (.reg, .bat, .ps1, .cmd).

    En un entorno real, un analista verificaria:
    - Claves de registro Run/RunOnce
    - Tareas programadas sospechosas
    - Servicios del sistema modificados
    - Scripts de inicio de sesion
    """
    hallazgos = []
    if not os.path.isdir(LAB_DIR):
        return hallazgos

    for fname in os.listdir(LAB_DIR):
        if fname.endswith(('.reg', '.bat', '.ps1', '.cmd')):
            fpath = os.path.join(LAB_DIR, fname)
            try:
                with open(fpath, 'r', encoding='utf-8', errors='ignore') as f:
                    contenido = f.read(4096)
                patrones = ['Run', 'RunOnce', 'startup', 'auto_start']
                if any(p in contenido for p in patrones):
                    hallazgos.append({
                        'path': fpath,
                        'nombre': fname,
                        'hash': _short_hash(fpath),
                    })
            except Exception:
                pass
    return hallazgos


# ══════════════════════════════════════════════════════════════
#  FUNCIONES DE VISUALIZACION
# ══════════════════════════════════════════════════════════════

def mostrar_resultados(hallazgos_marcadores, hallazgos_c2, hallazgos_persistencia):
    """Muestra los resultados del escaneo de forma visual."""
    safe_print(color("\n  Resultados del escaneo:\n", 'bold'))

    total = (
        len(hallazgos_marcadores) + len(hallazgos_c2) + len(hallazgos_persistencia)
    )
    if total == 0:
        safe_print(color(
            "  [OK] No se detectaron artefactos de backdoor.\n", 'green'
        ))
        return False

    # Marcadores de backdoor
    if hallazgos_marcadores:
        safe_print(color(
            f"  [!] Archivos con marcadores de backdoor: {len(hallazgos_marcadores)}\n",
            'red'
        ))
        for i, h in enumerate(hallazgos_marcadores, 1):
            safe_print(color(f"    {i}. {h['nombre']}", 'red'))
            safe_print(color(
                f"       Marcadores: {', '.join(h['marcadores'])}", 'yellow'
            ))
            safe_print(color(f"       Hash SHA-256: {h['hash']}", 'yellow'))
            log(f"Marcador backdoor: {h['nombre']}")

    # Configuraciones C2
    if hallazgos_c2:
        safe_print(color(
            f"\n  [!] Configuraciones C2 sospechosas: {len(hallazgos_c2)}\n",
            'red'
        ))
        for i, h in enumerate(hallazgos_c2, 1):
            safe_print(color(f"    {i}. {h['nombre']}", 'red'))
            safe_print(color(
                f"       IPs sospechosas: {h['ips_sospechosas']}", 'yellow'
            ))
            safe_print(color(
                f"       Puertos sospechosos: {h['puertos_sospechosos']}", 'yellow'
            ))
            log(f"Config C2: {h['nombre']} (IPs: {h['ips_sospechosas']})")

    # Persistencia
    if hallazgos_persistencia:
        safe_print(color(
            f"\n  [!] Archivos de persistencia: {len(hallazgos_persistencia)}\n",
            'red'
        ))
        for i, h in enumerate(hallazgos_persistencia, 1):
            safe_print(color(
                f"    {i}. {h['nombre']} (Hash: {h['hash']})", 'red'
            ))
            log(f"Persistencia: {h['nombre']}")

    return True


# ══════════════════════════════════════════════════════════════
#  FUNCIONES DE LIMPIEZA
# ══════════════════════════════════════════════════════════════

def limpiar_backdoor(hallazgos_marcadores, hallazgos_c2, hallazgos_persistencia):
    """
    Elimina todos los artefactos de backdoor detectados.

    En un entorno real, esto incluiria:
    1. Aislar el sistema de la red
    2. Terminar procesos de backdoor activos
    3. Eliminar persistencia (servicios, tareas, registro)
    4. Bloquear IPs C2 en el firewall
    5. Realizar analisis forense completo
    """
    safe_print(color("\n  Limpiando artefactos de backdoor...\n", 'bold'))
    eliminados = 0

    rutas = set()
    for h in hallazgos_marcadores + hallazgos_persistencia:
        rutas.add(h['path'])
    for h in hallazgos_c2:
        rutas.add(h['path'])

    for fpath in rutas:
        try:
            rel = os.path.relpath(fpath, ROOT)
            os.remove(fpath)
            safe_print(color(f"  [+] Eliminado: {rel}", 'green'))
            eliminados += 1
            log(f"Eliminado: {rel}")
        except Exception as e:
            safe_print(color(f"  [-] Error: {fpath}: {e}", 'red'))

    # Eliminar logs
    for log_name in ['06_backdoor.log', '06_backdoor_defensa.log']:
        log_path = os.path.join(ROOT, log_name)
        if os.path.exists(log_path):
            os.remove(log_path)
            safe_print(color(f"  [+] Eliminado: {log_name}", 'green'))
            eliminados += 1

    safe_print(color(f"\n  Total eliminado: {eliminados} artefactos", 'green'))
    return eliminados


# ══════════════════════════════════════════════════════════════
#  RESUMEN DE DEFENSA
# ══════════════════════════════════════════════════════════════

def mostrar_consejos_defensa():
    """Muestra recomendaciones de defensa contra backdoors."""
    safe_print(color("\n  ═══ CONSEJOS DE DEFENSA ═══\n", 'bold'))
    safe_print(color("  Herramientas y practicas recomendadas:", 'cyan'))
    safe_print("  1. MONITORIZAR conexiones salientes con EDR/IDS/IPS")
    safe_print("  2. REVISAR tareas programadas y servicios periodicamente")
    safe_print("  3. FIREWALL con inspeccion de estado y filtrado de IPs")
    safe_print("  4. LISTAS BLANCAS de aplicaciones (AppLocker/WDAC)")
    safe_print("  5. SEGMENTACION de red para limitar movilidad lateral")
    safe_print("  6. AUDITAR claves de registro de inicio automatico")
    safe_print("  7. HERRAMIENTAS de analisis de integridad de archivos")
    safe_print("  8. RESPUESTA: Aislar, quarantinar, analisis forense\n")


# ══════════════════════════════════════════════════════════════
#  PUNTO DE ENTRADA
# ══════════════════════════════════════════════════════════════

def mostrar_ayuda():
    safe_print(color("\nUso: python defensa.py [opcion]", 'cyan'))
    safe_print(color("\nOpciones:", 'bold'))
    safe_print("  (sin args)  Ejecutar la defensa contra backdoors")
    safe_print("  --help      Mostrar esta ayuda")
    safe_print(color("\nDescripcion:", 'bold'))
    safe_print("  Detecta configuraciones C2, registros de reverse shell")
    safe_print("  y archivos de persistencia. Elimina todos los artefactos.\n")


def main():
    if '--help' in sys.argv or '-h' in sys.argv:
        mostrar_ayuda()
        return

    banner("DEFENSA - MODULO 06 (BACKDOOR)",
           "Deteccion y limpieza de artefactos de backdoor")
    safe_print(color("  Entorno: laboratorio educativo controlado\n", 'cyan'))

    # ── FASE 1: Escaneo de marcadores ──
    safe_print(color(
        "\n  [FASE 1] Escaneando marcadores de backdoor...\n", 'bold'
    ))
    hallazgos_marcadores = escanear_marcadores()
    safe_print(color(
        f"  Marcadores encontrados: {len(hallazgos_marcadores)}", 'yellow'
    ))

    # ── FASE 2: Analisis de configuraciones C2 ──
    safe_print(color(
        "\n  [FASE 2] Escaneando configuraciones C2...\n", 'bold'
    ))
    hallazgos_c2 = escanear_config_c2()
    safe_print(color(
        f"  Configuraciones C2: {len(hallazgos_c2)}", 'yellow'
    ))

    # ── FASE 3: Deteccion de persistencia ──
    safe_print(color(
        "\n  [FASE 3] Escaneando persistencia...\n", 'bold'
    ))
    hallazgos_persistencia = escanear_persistencia()
    safe_print(color(
        f"  Archivos de persistencia: {len(hallazgos_persistencia)}",
        'yellow'
    ))

    # ── FASE 4: Mostrar resultados ──
    hay_artefactos = mostrar_resultados(
        hallazgos_marcadores, hallazgos_c2, hallazgos_persistencia
    )

    # ── FASE 5: Limpiar si hay artefactos ──
    if hay_artefactos:
        safe_print(color("\n  [FASE 4] Limpiando artefactos...\n", 'bold'))
        limpiar_backdoor(
            hallazgos_marcadores, hallazgos_c2, hallazgos_persistencia
        )

    # ── Resumen ──
    mostrar_consejos_defensa()

    write_log(
        "06_backdoor_defensa", list(LOG_LINES),
        os.path.join(ROOT, "06_backdoor_defensa.log")
    )
    safe_print(color("  Defensa completada.\n", 'green'))


if __name__ == "__main__":
    main()
