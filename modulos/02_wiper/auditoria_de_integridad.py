#!/usr/bin/env python3
"""
Ejecutar Auditoría de Integridad de Archivos contra simulacion de Wiper — Modulo 02.

Detecta archivos corruptos comparando hashes con el backup (.backup_wiper/),
restaura el contenido original desde backup y muestra verificacion de integridad.

Uso:
    python modulos/02_wiper/defensa.py          Ejecutar escaneo defensivo
    python modulos/02_wiper/defensa.py --clean  Restaurar y limpiar
    python modulos/02_wiper/defensa.py --help   Mostrar ayuda
"""
import os
import sys
import shutil
import argparse

_DIR_RAIZ = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, _DIR_RAIZ)

from modulos.common.utils import (
    log, safe_print, color, banner, traverse_lab_files,
    hash_file, cleanup, write_log,
)

# ── Constantes ──────────────────────────────────────────────────────────────
DIR_SIMULACION = find_lab_dir(_DIR_RAIZ)
DIR_BACKUP = os.path.join(os.path.dirname(DIR_SIMULACION), '.backup_wiper')
LOG_DEFENSA = 'defensa_wiper.log'

# Archivos generados por lab_setup.py
ARCHIVOS_LAB = {
    'documento.txt', 'notas.txt', 'script.py', 'index.html',
    'datos.csv', 'leeme.md', 'imagen.png', 'imagen.jpg',
    'audio.mp3', 'documento.docx', 'planilla.xlsx', 'presentacion.pptx',
}


def paso_fase(fase_num, titulo):
    """Imprime encabezado de fase."""
    safe_print(color(f"\n  [FASE {fase_num}] {titulo}", 'yellow'))
    safe_print(color(f"  {'─' * 55}", 'yellow'))


def verificar_backup():
    """Verifica si existe el directorio de backup con archivos intactos."""
    if not os.path.isdir(DIR_BACKUP):
        return False, []
    archivos = sorted([
        f for f in os.listdir(DIR_BACKUP)
        if os.path.isfile(os.path.join(DIR_BACKUP, f))
    ])
    return True, archivos


def comparar_hashes(archivos_actuales):
    """
    Compara hash SHA-256 de cada archivo actual vs su version en backup.

    Si los hashes difieren, el archivo fue corrompido por el wiper.
    Un SOC analyst usaria esta tecnica en un entorno real para detectar
    alteraciones no autorizadas (baseline vs actual).
    """
    resultados = []
    for ruta in archivos_actuales:
        nombre = os.path.basename(ruta)
        ruta_backup = os.path.join(DIR_BACKUP, nombre)

        hash_actual = hash_file(ruta)
        hash_backup = hash_file(ruta_backup) if os.path.exists(ruta_backup) else None

        corrupto = False
        if hash_backup and hash_actual:
            corrupto = (hash_actual != hash_backup)
        elif hash_backup and not hash_actual:
            corrupto = True

        resultados.append({
            'nombre': nombre,
            'path': ruta,
            'path_backup': ruta_backup,
            'hash_actual': hash_actual,
            'hash_backup': hash_backup,
            'corrupto': corrupto,
            'existe_backup': os.path.exists(ruta_backup),
        })

    return resultados


def restaurar_archivo(resultado):
    """
    Restaura un archivo desde el backup.

    En produccion, esto equivale a:
    1. Aislar la maquina afectada
    2. Verificar integridad del backup
    3. Restaurar desde la copia mas reciente verificada
    """
    try:
        shutil.copy2(resultado['path_backup'], resultado['path'])
        # Verificar que la restauracion fue exitosa
        hash_restaurado = hash_file(resultado['path'])
        return hash_restaurado == resultado['hash_backup']
    except Exception as e:
        safe_print(color(f"    [!] Error restaurando {resultado['nombre']}: {e}", 'red'))
        return False


def ejecutar_escaneo():
    """Ejecuta el proceso defensivo completo contra el wiper."""
    banner(
        "DEFENSA WIPER — DETECCION Y RESTAURACION",
        "Detecta archivos corruptos y restaura desde backup",
    )
    safe_print(color(
        "  Herramienta defensiva para detectar y remediar artefactos\n"
        "  del modulo 02 (wiper).\n",
        'cyan',
    ))

    # ── FASE 1: Verificar backup ────────────────────────────────────────────
    paso_fase(1, "VERIFICACION — Comprobando disponibilidad de backup")
    tiene_backup, archivos_backup = verificar_backup()

    if not tiene_backup:
        safe_print(color(
            "  [!] No se encontro directorio de backup (.backup_wiper/).\n",
            'red',
        ))
        safe_print(color(
            "  Esto puede significar que:\n"
            "  - La simulacion wiper no se ejecuto\n"
            "  - El backup fue eliminado\n"
            "  - Los archivos no fueron corrompidos\n",
            'yellow',
        ))
        safe_print(color(
            "  Para restaurar archivos, ejecuta: python core/lab_setup.py\n",
            'cyan',
        ))
        return

    safe_print(color(f"  [OK] Backup encontrado: {len(archivos_backup)} archivos\n", 'green'))

    # ── FASE 2: Verificar directorio de simulacion ──────────────────────────
    paso_fase(2, "VERIFICACION — Comprobando directorio de prueba")
    if not os.path.isdir(DIR_SIMULACION):
        safe_print(color(
            "  [OK] Directorio directorio_pruebas/ no existe.\n"
            "  No hay archivos que analizar.\n",
            'green',
        ))
        return

    safe_print(color(f"  Directorio encontrado: {DIR_SIMULACION}\n", 'cyan'))

    # ── FASE 3: Comparar hashes ─────────────────────────────────────────────
    paso_fase(3, "COMPARACION — Verificando integridad archivos vs backup")
    archivos_actuales = [
        os.path.join(DIR_SIMULACION, f)
        for f in sorted(os.listdir(DIR_SIMULACION))
        if os.path.isfile(os.path.join(DIR_SIMULACION, f))
        and f in ARCHIVOS_LAB
    ]

    resultados = comparar_hashes(archivos_actuales)
    corruptos = [r for r in resultados if r['corrupto']]
    intactos = [r for r in resultados if not r['corrupto']]

    if corruptos:
        safe_print(color(
            f"  [!] ALERTA: {len(corruptos)} archivos CORROMPIDOS detectados\n",
            'red',
        ))
        for r in corruptos:
            safe_print(color(f"    [CORROMPIDO] {r['nombre']}", 'red'))
            hash_act_display = (r['hash_actual'][:40] + '...') if r['hash_actual'] else 'N/A'
            hash_bak_display = (r['hash_backup'][:40] + '...') if r['hash_backup'] else 'N/A'
            safe_print(color(f"      Hash actual:   {hash_act_display}", 'yellow'))
            safe_print(color(f"      Hash backup:   {hash_bak_display}", 'green'))
    else:
        safe_print(color("  [OK] Todos los archivos estan intactos (hashes coinciden).\n", 'green'))

    if intactos:
        safe_print(color(f"\n  Archivos intactos: {len(intactos)}", 'green'))
        for r in intactos:
            safe_print(color(f"    [OK] {r['nombre']}", 'green'))

    # ── FASE 4: Restauracion ────────────────────────────────────────────────
    if corruptos:
        paso_fase(4, "RESTAURACION — Copiando originales desde backup")
        safe_print(color(
            "  Cada archivo corrupto se reemplaza con su version del backup.\n"
            "  Se verifica hash post-restauracion para confirmar integridad.\n",
            'cyan',
        ))
        restaurados = 0
        for r in corruptos:
            print(
                color(f"    Restaurando {r['nombre']}...", 'cyan'),
                end=' ',
                flush=True,
            )
            if restaurar_archivo(r):
                safe_print(color("OK", 'green'))
                restaurados += 1
            else:
                safe_print(color("ERROR", 'red'))

        safe_print(color(
            f"\n  Archivos restaurados: {restaurados}/{len(corruptos)}",
            'green' if restaurados == len(corruptos) else 'yellow',
        ))

    # ── FASE 5: Verificacion final ──────────────────────────────────────────
    paso_fase(5, "VERIFICACION — Hashes post-restauracion")
    if os.path.isdir(DIR_SIMULACION):
        safe_print(color("\n  Hashes SHA-256 de archivos en directorio_pruebas/:\n", 'cyan'))
        for nombre in sorted(os.listdir(DIR_SIMULACION)):
            ruta = os.path.join(DIR_SIMULACION, nombre)
            if os.path.isfile(ruta) and not nombre.endswith('.log'):
                h = hash_file(ruta)
                safe_print(color(
                    f"    {nombre:30s} {(h[:48] + '...') if h else 'N/A'}",
                    'green',
                ))

    # ── FASE 6: Resumen ─────────────────────────────────────────────────────
    paso_fase(6, "RESUMEN DE DEFENSA")
    safe_print(color(f"  Archivos analizados:   {len(resultados)}", 'cyan'))
    safe_print(color(f"  Archivos corruptos:    {len(corruptos)}", 'red' if corruptos else 'green'))
    safe_print(color(f"  Archivos intactos:     {len(intactos)}", 'green'))
    safe_print(color(f"  Backup disponible:     Si\n", 'green'))

    safe_print(color("  DIFERENCIA CON RANSOMWARE:", 'bold'))
    safe_print(color("  - Ransomware: cifra archivos (reversible con clave)", 'cyan'))
    safe_print(color("  - Wiper: corrompe archivos (irreversible sin backup)\n", 'cyan'))

    safe_print(color("  RECOMENDACIONES PARA PRODUCCION:", 'bold'))
    safe_print(color("  - Backups inmutables (WORM) contra wipers", 'cyan'))
    safe_print(color("  - Copias offline y air-gapped", 'cyan'))
    safe_print(color("  - Pruebas de restauracion periodicas", 'cyan'))
    safe_print(color("  - Monitoreo de operaciones de escritura masivas (bulk writes)", 'cyan'))
    safe_print(color("  - Alertas sobre eliminacion de shadow copies", 'cyan'))
    safe_print(color("  - Deteccion de drivers firmados usados de forma anomala\n", 'cyan'))

    write_log("defensa_wiper", [
        "Escaneo defensivo completado",
        f"Archivos analizados: {len(resultados)}",
        f"Archivos corruptos: {len(corruptos)}",
        f"Archivos restaurados: {len(corruptos) if corruptos else 0}",
    ])


def limpiar():
    """Elimina directorio_pruebas/, backup y logs."""
    banner("DEFENSA WIPER — LIMPIEZA", "Eliminando artefactos de la simulacion")
    removed = 0

    if os.path.isdir(DIR_SIMULACION):
        shutil.rmtree(DIR_SIMULACION)
        safe_print(color(f"  eliminado: directorio_pruebas/", 'green'))
        removed += 1

    if os.path.isdir(DIR_BACKUP):
        shutil.rmtree(DIR_BACKUP)
        safe_print(color(f"  eliminado: .backup_wiper/", 'green'))
        removed += 1

    removed += cleanup(patterns=[LOG_DEFENSA, 'wiper_sim.log'])

    safe_print(color(f"\n  Limpieza completada: {removed} artefactos eliminados.", 'green'))
    safe_print(color(
        "  Para restaurar archivos ejecuta: python core/lab_setup.py\n",
        'cyan',
    ))


def main():
    parser = argparse.ArgumentParser(
        description="Defensa contra simulacion de Wiper",
        epilog="Detecta archivos corruptos, restaura desde backup y limpia artefactos.",
    )
    parser.add_argument(
        '--clean',
        action='store_true',
        help='Restaurar archivos y eliminar directorio_pruebas/ + backup',
    )
    args = parser.parse_args()

    if args.clean:
        limpiar()
    else:
        ejecutar_escaneo()


if __name__ == "__main__":
    main()
