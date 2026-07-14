#!/usr/bin/env python3
"""
Modulo 07 - Defensa contra rootkit educativo.

Lista archivos ocultos, detecta artefactos de rootkit y limpia
todo el sistema.

SOLO PARA USO EDUCATIVO EN ENTORNO CONTROLADO.

Uso:
    python modulos/07_rootkit/defensa.py           Ejecutar defensa
    python modulos/07_rootkit/defensa.py --help    Mostrar ayuda
"""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, ROOT)

from modulos.common.utils import (
    banner, color, safe_print, log, LOG_LINES,
    write_log, hash_file, traverse_lab_files, find_lab_dir,
)

# ── Ruta del directorio de pruebas ──
LAB_DIR = find_lab_dir(ROOT)

# ── Marcador de deteccion ──
ROOTKIT_MARKER = "ROOTKIT_SIMULATION"

# ── Nombres de archivos ocultos tipicos de rootkit ──
ARCHIVOS_OCULTOS_NOMBRES = [
    ".hidden_system", ".config_sys.dat",
    ".rootkit_payload", ".driver_sim.sys",
]

# ── Procesos que el rootkit oculta ──
PROCESOS_SOSPECHOSOS = [
    "rootkit_svc.exe", "c2_beacon.exe", "keylog_drv.sys",
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

def escanear_archivos_ocultos():
    """
    Busca archivos ocultos (prefijo dot) en el directorio de pruebas.

    En un entorno real, un rootkit usaria intercepcion de syscalls
    para que 'ls -a' no muestre estos archivos. La unica forma
    confiable de detectarlos es desde un sistema operativo externo
    (USB booteable, analisis offline).
    """
    hallazgos = []
    if not os.path.isdir(LAB_DIR):
        return hallazgos

    for fname in os.listdir(LAB_DIR):
        if fname.startswith('.') and fname != '.':
            fpath = os.path.join(LAB_DIR, fname)
            if os.path.isfile(fpath):
                hallazgos.append({
                    'path': fpath,
                    'nombre': fname,
                    'hash': _short_hash(fpath),
                    'size': os.path.getsize(fpath),
                })
    return hallazgos


def escanear_marcadores_rootkit():
    """
    Escanea archivos en busca del marcador ROOTKIT_SIMULATION.

    En un entorno real, esto equivale a usar reglas YARA o
    firmas de antivirus para detectar rootkits conocidos.
    """
    hallazgos = []
    if not os.path.isdir(LAB_DIR):
        return hallazgos

    for fname in os.listdir(LAB_DIR):
        fpath = os.path.join(LAB_DIR, fname)
        if not os.path.isfile(fpath):
            continue
        if fname.startswith('.'):
            continue  # Ya escaneados por escanear_archivos_ocultos()
        try:
            with open(fpath, 'r', encoding='utf-8', errors='ignore') as f:
                contenido = f.read(4096)
            if ROOTKIT_MARKER in contenido:
                hallazgos.append({
                    'path': fpath,
                    'nombre': fname,
                    'hash': _short_hash(fpath),
                    'size': os.path.getsize(fpath),
                })
        except Exception:
            pass
    return hallazgos


def escanear_manipulacion_procesos():
    """
    Detecta archivos con procesos ocultos simulados.

    En un entorno real, esto se haria comparando la lista de
    procesos vista desde el SO comprometido vs. desde un SO
    externo (diferencias revelarian la presencia del rootkit).
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
                contenido = f.read(4096)
            procs_ocultos = [
                p for p in PROCESOS_SOSPECHOSOS if p in contenido
            ]
            if procs_ocultos:
                hallazgos.append({
                    'path': fpath,
                    'nombre': fname,
                    'procesos_ocultos': procs_ocultos,
                    'hash': _short_hash(fpath),
                })
        except Exception:
            pass
    return hallazgos


# ══════════════════════════════════════════════════════════════
#  FUNCIONES DE VISUALIZACION
# ══════════════════════════════════════════════════════════════

def mostrar_resultados(hallazgos_ocultos, hallazgos_marcadores, hallazgos_procesos):
    """Muestra los resultados del escaneo de forma visual."""
    safe_print(color("\n  Resultados del escaneo:\n", 'bold'))

    total = (
        len(hallazgos_ocultos) +
        len(hallazgos_marcadores) +
        len(hallazgos_procesos)
    )
    if total == 0:
        safe_print(color(
            "  [OK] No se detectaron artefactos de rootkit.\n", 'green'
        ))
        return False

    # Archivos ocultos
    if hallazgos_ocultos:
        safe_print(color(
            f"  [!] Archivos ocultos encontrados: {len(hallazgos_ocultos)}\n",
            'red'
        ))
        for i, h in enumerate(hallazgos_ocultos, 1):
            safe_print(color(f"    {i}. {h['nombre']}", 'red'))
            safe_print(color(f"       Tamano: {h['size']} bytes", 'yellow'))
            safe_print(color(f"       Hash SHA-256: {h['hash']}", 'yellow'))
            log(f"Archivo oculto: directorio_pruebas/{h['nombre']}")

    # Marcadores de rootkit
    if hallazgos_marcadores:
        safe_print(color(
            f"\n  [!] Archivos con marcador de rootkit: "
            f"{len(hallazgos_marcadores)}\n", 'red'
        ))
        for i, h in enumerate(hallazgos_marcadores, 1):
            rel = os.path.relpath(h['path'], ROOT)
            safe_print(color(f"    {i}. {rel}", 'red'))
            safe_print(color(f"       Hash SHA-256: {h['hash']}", 'yellow'))
            log(f"Marcador rootkit: {rel}")

    # Manipulacion de procesos
    if hallazgos_procesos:
        safe_print(color(
            f"\n  [!] Manipulacion de procesos detectada: "
            f"{len(hallazgos_procesos)}\n", 'red'
        ))
        for i, h in enumerate(hallazgos_procesos, 1):
            rel = os.path.relpath(h['path'], ROOT)
            safe_print(color(f"    {i}. {rel}", 'red'))
            for proc in h['procesos_ocultos']:
                safe_print(color(
                    f"       Proceso oculto detectado: {proc}", 'yellow'
                ))
            log(f"Manipulacion de procesos: {rel}")

    return True


# ══════════════════════════════════════════════════════════════
#  FUNCIONES DE LIMPIEZA
# ══════════════════════════════════════════════════════════════

def limpiar_rootkit(hallazgos_ocultos, hallazgos_marcadores, hallazgos_procesos):
    """
    Elimina los artefactos del rootkit detectados.

    En un entorno real, la limpieza de un rootkit kernel es
    extremadamente dificil. Las opciones incluyen:
    1. Formateo completo y reinstalacion desde cero
    2. Analisis offline desde USB booteable
    3. Restaurar desde backup verificado
    4. Usar herramientas especializadas (GMER, TDSSKiller)
    """
    safe_print(color("\n  Limpiando artefactos del rootkit...\n", 'bold'))
    eliminados = 0

    rutas = set()
    for h in hallazgos_ocultos + hallazgos_marcadores + hallazgos_procesos:
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

    # Eliminar logs en lab_data/logs/
    log_dir = os.path.join(find_lab_dir(ROOT), '..', 'logs')
    for log_name in ['07_rootkit.log', '07_rootkit_defensa.log']:
        log_path = os.path.join(log_dir, log_name)
        if os.path.exists(log_path):
            os.remove(log_path)
            safe_print(color(f"  [+] Eliminado: {log_name}", 'green'))
            eliminados += 1

    safe_print(color(
        f"\n  Total eliminado: {eliminados} artefactos", 'green'
    ))
    return eliminados


# ══════════════════════════════════════════════════════════════
#  RESUMEN DE DEFENSA
# ══════════════════════════════════════════════════════════════

def mostrar_consejos_defensa():
    """Muestra recomendaciones de defensa contra rootkits."""
    safe_print(color("\n  ═══ CONSEJOS DE DEFENSA ═══\n", 'bold'))
    safe_print(color("  Herramientas y practicas recomendadas:", 'cyan'))
    safe_print("  1. EDR con proteccion a nivel kernel")
    safe_print("  2. Verificar integridad del MBR/UEFI periodicamente")
    safe_print("  3. Activar Secure Boot y TPM en BIOS/UEFI")
    safe_print("  4. Escanear desde USB booteable (modo offline)")
    safe_print("  5. Monitorear consumo de CPU/RAM inusual")
    safe_print("  6. Verificar firmas digitales de todos los drivers")
    safe_print("  7. Usar herramientas: GMER, TDSSKiller, Kaspersky TDSS")
    safe_print("  8. Mantener actualizado el firmware del BIOS/UEFI")
    safe_print("  9. Comparar listas de procesos desde SO externo\n")


# ══════════════════════════════════════════════════════════════
#  PUNTO DE ENTRADA
# ══════════════════════════════════════════════════════════════

def mostrar_ayuda():
    safe_print(color("\nUso: python defensa.py [opcion]", 'cyan'))
    safe_print(color("\nOpciones:", 'bold'))
    safe_print("  (sin args)  Ejecutar la defensa contra rootkits")
    safe_print("  --help      Mostrar esta ayuda")
    safe_print(color("\nDescripcion:", 'bold'))
    safe_print("  Detecta archivos ocultos, marcadores de rootkit")
    safe_print("  y manipulacion de procesos. Elimina todos los artefactos.\n")


def main():
    if '--help' in sys.argv or '-h' in sys.argv:
        mostrar_ayuda()
        return

    banner("DEFENSA - MODULO 07 (ROOTKIT)",
           "Deteccion y limpieza de artefactos de rootkit")
    safe_print(color("  Entorno: laboratorio educativo controlado\n", 'cyan'))

    # ── FASE 1: Buscar archivos ocultos ──
    safe_print(color(
        "\n  [FASE 1] Buscando archivos ocultos (prefijo dot)...\n",
        'bold'
    ))
    hallazgos_ocultos = escanear_archivos_ocultos()
    safe_print(color(
        f"  Archivos ocultos encontrados: {len(hallazgos_ocultos)}",
        'yellow'
    ))

    # ── FASE 2: Escaneo de marcadores ──
    safe_print(color(
        "\n  [FASE 2] Escaneando marcadores de rootkit...\n", 'bold'
    ))
    hallazgos_marcadores = escanear_marcadores_rootkit()
    safe_print(color(
        f"  Archivos con marcador: {len(hallazgos_marcadores)}",
        'yellow'
    ))

    # ── FASE 3: Deteccion de manipulacion ──
    safe_print(color(
        "\n  [FASE 3] Detectando manipulacion de procesos...\n", 'bold'
    ))
    hallazgos_procesos = escanear_manipulacion_procesos()
    safe_print(color(
        f"  Archivos con procesos ocultos: {len(hallazgos_procesos)}",
        'yellow'
    ))

    # ── FASE 4: Mostrar resultados ──
    hay_artefactos = mostrar_resultados(
        hallazgos_ocultos, hallazgos_marcadores, hallazgos_procesos
    )

    # ── FASE 5: Limpiar si hay artefactos ──
    if hay_artefactos:
        safe_print(color("\n  [FASE 4] Limpiando artefactos...\n", 'bold'))
        limpiar_rootkit(
            hallazgos_ocultos, hallazgos_marcadores, hallazgos_procesos
        )

    # ── Resumen ──
    mostrar_consejos_defensa()

    write_log(
        "07_rootkit_defensa", list(LOG_LINES)
    )
    safe_print(color("  Defensa completada.\n", 'green'))


if __name__ == "__main__":
    main()
