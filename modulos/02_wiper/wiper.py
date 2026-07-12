#!/usr/bin/env python3
"""
Simulacion educativa de Wiper — Modulo 02.

Demuestra el comportamiento de un malware destructivo que corrompe archivos
sobreescribiendo los primeros 64 bytes con datos basura. A diferencia del
ransomware, el wiper NO busca rescate — su objetivo es la destruccion.

Los archivos originales se preservan en .backup_wiper/ para poder restaurar.

Uso:
    python modulos/02_wiper/wiper.py          Ejecutar simulacion
    python modulos/02_wiper/wiper.py --clean  Limpiar artefactos
    python modulos/02_wiper/wiper.py --help   Mostrar ayuda
"""
import os
import sys
import shutil
import random
import argparse
import time

_DIR_RAIZ = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, _DIR_RAIZ)

from core.common import (
    log, safe_print, color, banner, traverse_lab_files,
    hash_file, read_file, cleanup, write_log, is_lab_ready,
    LOG_LINES,
)

# ── Constantes ──────────────────────────────────────────────────────────────
# Directorio donde se trabaja la simulacion
DIR_SIMULACION = os.path.join(os.getcwd(), 'directorio_pruebas')

# Backup seguro de los originales ANTES de la corrupcion
DIR_BACKUP = os.path.join(os.getcwd(), '.backup_wiper')

# Cantidad de bytes a sobreescribir con basura (de 64 a total del archivo)
BYTES_A_CORROMPER = 64

# Extensiones objetivo — el wiper corrompe TODO, no solo texto
EXTENSIONES_OBJETIVO = {
    '.txt', '.py', '.html', '.csv', '.md',
    '.png', '.jpg', '.mp3', '.docx', '.xlsx', '.pptx',
}


# ── Funciones auxiliares ────────────────────────────────────────────────────

def paso_fase(fase_num, titulo):
    """Imprime encabezado de fase con formato visual."""
    safe_print(color(f"\n  [FASE {fase_num}] {titulo}", 'yellow'))
    safe_print(color(f"  {'─' * 55}", 'yellow'))
    time.sleep(0.3)


def preparar_directorio():
    """
    Crea directorio_pruebas/ y copia los archivos del laboratorio.

    Seguridad: los originales NUNCA se modifican — siempre trabajamos
    sobre copias en directorio_pruebas/.
    """
    os.makedirs(DIR_SIMULACION, exist_ok=True)

    archivos_lab = traverse_lab_files(_DIR_RAIZ)
    lab_files = {
        'documento.txt', 'notas.txt', 'script.py', 'index.html',
        'datos.csv', 'leeme.md', 'imagen.png', 'imagen.jpg',
        'audio.mp3', 'documento.docx', 'planilla.xlsx', 'presentacion.pptx',
    }
    copiados = 0
    for archivo in archivos_lab:
        nombre = os.path.basename(archivo)
        if nombre not in lab_files:
            continue
        destino = os.path.join(DIR_SIMULACION, nombre)
        if not os.path.exists(destino):
            shutil.copy2(archivo, destino)
            copiados += 1

    log(f"Directorio preparado: {DIR_SIMULACION} ({copiados} archivos)")
    safe_print(color(f"  Directorio de trabajo: {DIR_SIMULACION}", 'green'))
    safe_print(color(f"  Archivos copiados: {copiados}\n", 'green'))
    return copiados


def crear_backup_seguro(archivos_objetivo):
    """
    Crea copias de seguridad en .backup_wiper/ ANTES de corromper.

    En un entorno real, esta funcion representaria un sistema de backup
    WORM (Write Once Read Many) o air-gapped que resistiria el wiper.
    """
    if os.path.exists(DIR_BACKUP):
        shutil.rmtree(DIR_BACKUP)
    os.makedirs(DIR_BACKUP, exist_ok=True)

    for ruta in archivos_objetivo:
        nombre = os.path.basename(ruta)
        destino = os.path.join(DIR_BACKUP, nombre)
        shutil.copy2(ruta, destino)

    log(f"Backup seguro creado: {DIR_BACKUP} ({len(archivos_objetivo)} archivos)")
    safe_print(color(f"  Backup creado: {len(archivos_objetivo)} archivos en .backup_wiper/", 'green'))


def corromper_archivo(ruta, n_bytes):
    """
    Sobreescribe los primeros N bytes de un archivo con datos aleatorios.

    Retorna (hash_original, datos_corruptos).
    En un wiper real (Shamoon), se sobreescribia TODO el archivo con ceros
    o con una imagen (como la bandera de EEUU en Shamoon 2012).
    """
    datos_originales = read_file(ruta)
    if datos_originales is None:
        return None, None

    hash_original = hash_file(ruta)

    # Crear copia corrupta: reemplazar primeros N bytes con basura
    datos_corruptos = bytearray(datos_originales)
    tamano_corromper = min(n_bytes, len(datos_corruptos))
    basura = bytes([random.randint(0, 255) for _ in range(tamano_corromper)])
    datos_corruptos[:tamano_corromper] = basura

    return hash_original, bytes(datos_corruptos)


# ── Simulacion principal ────────────────────────────────────────────────────

def ejecutar_simulacion():
    """Ejecuta la simulacion completa de un ataque wiper."""
    banner(
        "WIPER — SIMULACION EDUCATIVA",
        "Malware destructivo: corrompe archivos sin buscar rescate",
    )
    safe_print(color(
        "  Este script simula un wiper (Shamoon, HermeticWiper, etc.)\n"
        "  Los archivos originales se preservan en .backup_wiper/ para restaurar.\n",
        'cyan',
    ))

    if not is_lab_ready():
        safe_print(color("  [!] No se encontraron archivos del laboratorio.", 'red'))
        safe_print(color("  Ejecuta primero: python core/lab_setup.py", 'red'))
        sys.exit(1)

    # ── FASE 1: Preparacion ─────────────────────────────────────────────────
    paso_fase(1, "PREPARACION — Copiando archivos a directorio de prueba")
    log("Fase 1: Preparacion del entorno")
    preparar_directorio()
    time.sleep(0.5)

    # ── FASE 2: Infeccion ───────────────────────────────────────────────────
    paso_fase(2, "INFECCION — El wiper se activa en el sistema")
    log("Fase 2: Infeccion")
    safe_print(color(
        "  En un ataque real (Shamoon 2012), el wiper se activa en una\n"
        "  hora programada (3:08 AM) y sobreescribe archivos con una\n"
        "  imagen de bandera estadounidense.\n",
        'cyan',
    ))
    safe_print(color(
        "  HermeticWiper (2022) usaba un driver legitimo firmado (WinMon32.sys)\n"
        "  para causar corrupcion a nivel de disco.\n",
        'cyan',
    ))
    time.sleep(0.5)

    # ── FASE 3: Backup de originales ────────────────────────────────────────
    paso_fase(3, "BACKUP — Creando copia segura antes de la destruccion")
    log("Fase 3: Backup de originales")
    safe_print(color(
        "  Antes de corromper, guardamos copias en .backup_wiper/.\n"
        "  Esto representa un backup WORM/air-gapped que el wiper NO podria\n"
        "  eliminar en un entorno real.\n",
        'cyan',
    ))
    archivos_lab = traverse_lab_files(DIR_SIMULACION)
    crear_backup_seguro(archivos_lab)
    time.sleep(0.5)

    # ── FASE 4: Reconocimiento ──────────────────────────────────────────────
    paso_fase(4, "RECONOCIMIENTO — Identificando archivos objetivo")
    log("Fase 4: Reconocimiento")
    safe_print(color("  El wiper enumera todos los archivos accesibles:\n", 'cyan'))

    archivos_objetivo = []
    for archivo in archivos_lab:
        nombre = os.path.basename(archivo)
        _, ext = os.path.splitext(nombre)
        if ext.lower() in EXTENSIONES_OBJETIVO:
            tamano = os.path.getsize(archivo)
            archivos_objetivo.append(archivo)
            safe_print(color(f"    [+] {nombre} ({tamano} bytes) — OBJETIVO", 'green'))
        else:
            safe_print(color(f"    [-] {nombre} — ignorado", 'blue'))

    time.sleep(0.5)

    # ── FASE 5: Corrupcion masiva ───────────────────────────────────────────
    paso_fase(5, "CORRUPCION — Sobreescribiendo datos con basura aleatoria")
    log("Fase 5: Corrupcion de archivos")
    safe_print(color(
        f"  Sobreescribiendo los primeros {BYTES_A_CORROMPER} bytes de cada archivo.\n"
        "  En un wiper real se sobreescribiria TODO el archivo.\n",
        'cyan',
    ))

    archivos_corruptos = []
    for ruta in archivos_objetivo:
        nombre = os.path.basename(ruta)
        hash_orig, datos_corruptos = corromper_archivo(ruta, BYTES_A_CORROMPER)

        if datos_corruptos is None:
            safe_print(color(f"    [!] No se pudo corromper: {nombre}", 'red'))
            continue

        # Sobreescribir el archivo con la version corrupta
        with open(ruta, 'wb') as f:
            f.write(datos_corruptos)

        hash_corrupto = hash_file(ruta)
        hash_orig_display = (hash_orig[:32] + '...') if hash_orig else 'N/A'
        hash_corrupt_display = (hash_corrupto[:32] + '...') if hash_corrupto else 'N/A'
        archivos_corruptos.append((ruta, hash_orig, hash_corrupto))

        safe_print(color(f"    [CORROMPIDO] {nombre}", 'red'))
        safe_print(color(f"      Hash original:  {hash_orig_display}", 'green'))
        safe_print(color(f"      Hash corrupto:  {hash_corrupt_display}", 'red'))
        log(f"  Corrupto: {nombre} (hash: {hash_orig_display} -> {hash_corrupt_display})")

    time.sleep(0.5)

    # ── FASE 6: Eliminacion de copias de seguridad del sistema ──────────────
    paso_fase(6, "ELIMINACION DE BACKUPS — Comandos tipicos del wiper")
    log("Fase 6: Eliminacion de backups del sistema")
    safe_print(color("  En un ataque real, el wiper ejecutaria:\n", 'cyan'))
    comandos_wiper = [
        ("vssadmin delete shadows /all /quiet", "Elimina shadow copies de Windows"),
        ("bcdedit /set {default} recoveryenabled No", "Deshabilita recuperacion"),
        ("wbadmin delete catalog -quiet", "Elimina catalogo de backups"),
    ]
    for cmd, desc in comandos_wiper:
        safe_print(color(f"    $ {cmd}", 'red'))
        safe_print(color(f"      -> {desc}", 'yellow'))
    safe_print(color(
        "\n  Aqui solo simulamos la accion. Nada se ejecuta realmente.\n",
        'cyan',
    ))
    time.sleep(0.5)

    # ── FASE 7: Diferencia Ransomware vs Wiper ──────────────────────────────
    paso_fase(7, "COMPARACION: RANSOMWARE vs WIPER")
    safe_print(color("\n  RANSOMWARE (Modulo 01):", 'green'))
    safe_print(color("    - Cifra archivos (reversible con clave)", 'cyan'))
    safe_print(color("    - Deja nota de rescate", 'cyan'))
    safe_print(color("    - Objetivo: extorsion monetaria", 'cyan'))
    safe_print(color("    - Los archivos NO se destruyen", 'cyan'))
    safe_print(color("    - El usuario pierde ACCESO pero no DATOS\n", 'cyan'))

    safe_print(color("  WIPER (Modulo 02):", 'red'))
    safe_print(color("    - Corrompe/destruye archivos (irreversible sin backup)", 'red'))
    safe_print(color("    - NO deja nota de rescate", 'red'))
    safe_print(color("    - Objetivo: destruccion / sabotaje politico", 'red'))
    safe_print(color("    - Los archivos SI se destruyen permanentemente", 'red'))
    safe_print(color("    - El usuario pierde DATOS, no solo acceso\n", 'red'))

    # ── Resumen ─────────────────────────────────────────────────────────────
    safe_print(color("  RESUMEN:", 'bold'))
    safe_print(color(f"  Archivos corrompidos:  {len(archivos_corruptos)}", 'red'))
    safe_print(color(f"  Bytes sobreescritos:   {BYTES_A_CORROMPER} por archivo", 'yellow'))
    safe_print(color(f"  Backup disponible:     .backup_wiper/", 'green'))
    safe_print(color(f"  Nota: los originales estan seguros en el backup.\n", 'green'))

    write_log("wiper_sim", list(LOG_LINES))


def limpiar():
    """Elimina directorio_pruebas/, backup y logs."""
    banner("WIPER — LIMPIEZA", "Eliminando artefactos de la simulacion")
    removed = 0

    if os.path.isdir(DIR_SIMULACION):
        shutil.rmtree(DIR_SIMULACION)
        safe_print(color(f"  eliminado: directorio_pruebas/", 'green'))
        removed += 1

    if os.path.isdir(DIR_BACKUP):
        shutil.rmtree(DIR_BACKUP)
        safe_print(color(f"  eliminado: .backup_wiper/", 'green'))
        removed += 1

    removed += cleanup(patterns=['wiper_sim.log'])

    safe_print(color(f"\n  Limpieza completada: {removed} artefactos eliminados.", 'green'))
    safe_print(color(
        "  Para restaurar archivos ejecuta: python core/lab_setup.py\n",
        'cyan',
    ))


def main():
    parser = argparse.ArgumentParser(
        description="Simulacion educativa de Wiper malware",
        epilog=(
            "Corrompe primeros 64 bytes de archivos en directorio_pruebas/.\n"
            "Los originales se preservan en .backup_wiper/. Ejecuta --clean para restaurar."
        ),
    )
    parser.add_argument(
        '--clean',
        action='store_true',
        help='Eliminar directorio_pruebas/, backup y logs',
    )
    args = parser.parse_args()

    if args.clean:
        limpiar()
    else:
        ejecutar_simulacion()


if __name__ == "__main__":
    main()
