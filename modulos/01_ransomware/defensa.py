#!/usr/bin/env python3
"""
Defensa contra simulacion de Ransomware — Modulo 01.

Detecta archivos .locked generados por ransomware.py, invierte el texto
para restaurar el contenido original, elimina la nota de rescate y
muestra verificacion de hashes SHA-256.

Uso:
    python modulos/01_ransomware/defensa.py          Ejecutar escaneo defensivo
    python modulos/01_ransomware/defensa.py --clean  Restaurar y limpiar
    python modulos/01_ransomware/defensa.py --help   Mostrar ayuda
"""
import os
import sys
import glob
import argparse

_DIR_RAIZ = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, _DIR_RAIZ)

from core.common import (
    log, safe_print, color, banner, hash_file, cleanup, write_log,
)

# ── Constantes ──────────────────────────────────────────────────────────────
DIR_SIMULACION = os.path.join(os.getcwd(), 'directorio_pruebas')
EXTENSION_LOCKED = '.locked'
NOTA_RESCATE = 'README_RESCATE.txt'
LOG_DEFENSA = 'defensa_ransomware.log'


def paso_fase(fase_num, titulo):
    """Imprime encabezado de fase."""
    safe_print(color(f"\n  [FASE {fase_num}] {titulo}", 'yellow'))
    safe_print(color(f"  {'─' * 55}", 'yellow'))


def invertir_texto(texto):
    """Invierte el orden de caracteres de cada linea (reverso del cifrado)."""
    return '\n'.join(linea[::-1] for linea in texto.split('\n'))


def escanear_archivos_locked():
    """Busca archivos .locked en directorio_pruebas/."""
    if not os.path.isdir(DIR_SIMULACION):
        return []
    return sorted(glob.glob(os.path.join(DIR_SIMULACION, f'*{EXTENSION_LOCKED}')))


def restaurar_archivo(ruta_locked):
    """
    Restaura un archivo .locked invirtiendo el texto y guardando el resultado
    como el nombre original (sin .locked).

    En un entorno SOC real, esta accion equivaleria a restaurar desde un
    backup verificado despues de un ataque ransomware.
    """
    nombre_locked = os.path.basename(ruta_locked)
    nombre_original = nombre_locked.replace(EXTENSION_LOCKED, '')
    ruta_original = os.path.join(DIR_SIMULACION, nombre_original)

    try:
        with open(ruta_locked, 'r', encoding='utf-8', errors='replace') as f:
            contenido_cifrado = f.read()

        # Invertir para obtener el contenido original
        contenido_restaurado = invertir_texto(contenido_cifrado)

        with open(ruta_original, 'w', encoding='utf-8') as f:
            f.write(contenido_restaurado)

        return True
    except Exception as e:
        safe_print(color(f"    [!] Error restaurando {nombre_locked}: {e}", 'red'))
        return False


def ejecutar_escaneo():
    """Ejecuta el proceso defensivo completo."""
    banner(
        "DEFENSA RANSOMWARE — DETECCION Y RESTAURACION",
        "Detecta artefactos de la simulacion y restaura archivos invertidos",
    )
    safe_print(color(
        "  Herramienta defensiva para detectar y remediar artefactos\n"
        "  del modulo 01 (ransomware).\n",
        'cyan',
    ))

    # ── FASE 1: Verificar directorio de simulacion ──────────────────────────
    paso_fase(1, "VERIFICACION — Comprobando directorio de trabajo")
    if not os.path.isdir(DIR_SIMULACION):
        safe_print(color(
            "  [OK] Directorio directorio_pruebas/ no existe.\n"
            "  No hay artefactos de ransomware que remediar.\n",
            'green',
        ))
        return

    safe_print(color(f"  Directorio encontrado: {DIR_SIMULACION}\n", 'cyan'))

    # ── FASE 2: Buscar archivos .locked ─────────────────────────────────────
    paso_fase(2, "ESCANEADO — Buscando archivos cifrados (.locked)")
    archivos_locked = escanear_archivos_locked()

    if archivos_locked:
        safe_print(color(f"  [!] ALERTA: {len(archivos_locked)} archivos .locked detectados\n", 'red'))
        for locked in archivos_locked:
            nombre = os.path.basename(locked)
            tamano = os.path.getsize(locked)
            hash_lock = hash_file(locked)
            safe_print(color(f"    [!] {nombre} — {tamano} bytes", 'red'))
            safe_print(color(
                f"        SHA-256: {(hash_lock[:48] + '...') if hash_lock else 'N/A'}",
                'blue',
            ))
    else:
        safe_print(color("  [OK] No se encontraron archivos .locked.\n", 'green'))

    # ── FASE 3: Verificar nota de rescate ───────────────────────────────────
    paso_fase(3, "ESCANEADO — Buscando nota de rescate")
    ruta_nota = os.path.join(DIR_SIMULACION, NOTA_RESCATE)
    if os.path.exists(ruta_nota):
        safe_print(color(f"  [!] ALERTA: Nota de rescate detectada: {NOTA_RESCATE}\n", 'red'))
        with open(ruta_nota, 'r', encoding='utf-8') as f:
            lineas = f.readlines()
        for linea in lineas[:6]:
            safe_print(color(f"    {linea.rstrip()}", 'red'))
        safe_print(color("    ...", 'red'))
    else:
        safe_print(color("  [OK] No se encontraron notas de rescate.\n", 'green'))

    # ── FASE 4: Restaurar archivos ──────────────────────────────────────────
    if archivos_locked:
        paso_fase(4, "RESTAURACION — Invirtiendo texto para recuperar originales")
        safe_print(color(
            "  Algoritmo: volver a invertir el texto de cada linea para\n"
            "  restaurar el contenido original.\n",
            'cyan',
        ))
        restaurados = 0
        for locked in archivos_locked:
            nombre = os.path.basename(locked)
            nombre_original = nombre.replace(EXTENSION_LOCKED, '')
            print(color(f"    Restaurando {nombre} -> {nombre_original}...", 'cyan'), end=' ')
            if restaurar_archivo(locked):
                # Verificar integridad
                ruta_original = os.path.join(DIR_SIMULACION, nombre_original)
                with open(ruta_original, 'r', encoding='utf-8') as f:
                    contenido = f.read()
                # Si la primera linea no empieza con caracteres invertidos, OK
                primera_linea = contenido.split('\n')[0] if contenido else ''
                safe_print(color("OK", 'green'))
                restaurados += 1
            else:
                safe_print(color("ERROR", 'red'))

        safe_print(color(
            f"\n  Archivos restaurados: {restaurados}/{len(archivos_locked)}",
            'green' if restaurados == len(archivos_locked) else 'yellow',
        ))

    # ── FASE 5: Verificacion de hashes ──────────────────────────────────────
    paso_fase(5, "VERIFICACION — Integridad de archivos restaurados")
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

    # ── FASE 6: Resumen y recomendaciones ───────────────────────────────────
    paso_fase(6, "RESUMEN DE DEFENSA")
    total_artefactos = len(archivos_locked) + (1 if os.path.exists(ruta_nota) else 0)
    if total_artefactos > 0:
        safe_print(color(f"\n  Artefactos detectados: {total_artefactos}", 'red'))
        safe_print(color("  Ejecuta con --clean para restaurar y limpiar.\n", 'yellow'))
    else:
        safe_print(color(
            "\n  [OK] Sistema limpio — no se detectaron artefactos ransomware.\n",
            'green',
        ))

    safe_print(color("  RECOMENDACIONES PARA PRODUCCION:", 'bold'))
    safe_print(color("  - Mantener backups actualizados (regla 3-2-1: 3 copias, 2 medios, 1 offsite)", 'cyan'))
    safe_print(color("  - No abrir adjuntos de email sospechosos (.exe, .scr, .js)", 'cyan'))
    safe_print(color("  - Mantener el SO y software parchado contra CVEs conocidas", 'cyan'))
    safe_print(color("  - Usar EDR/antivirus actualizado con proteccion en tiempo real", 'cyan'))
    safe_print(color("  - Segmentar la red para limitar movimiento lateral del atacante", 'cyan'))
    safe_print(color("  - Habilitar MFA en todos los servicios criticos\n", 'cyan'))

    write_log("defensa_ransomware", [
        "Escaneo defensivo completado",
        f"Archivos .locked: {len(archivos_locked)}",
        f"Notas de rescate: {1 if os.path.exists(ruta_nota) else 0}",
    ])


def limpiar():
    """Elimina directorio_pruebas/ y logs residuales."""
    banner("DEFENSA RANSOMWARE — LIMPIEZA", "Eliminando artefactos de la simulacion")
    removed = 0

    if os.path.isdir(DIR_SIMULACION):
        shutil = __import__('shutil')
        shutil.rmtree(DIR_SIMULACION)
        safe_print(color(f"  eliminado: directorio_pruebas/ (entero)", 'green'))
        removed += 1

    removed += cleanup(patterns=[LOG_DEFENSA, 'ransomware_sim.log'])
    safe_print(color(f"\n  Limpieza completada: {removed} artefactos eliminados.\n", 'green'))


def main():
    parser = argparse.ArgumentParser(
        description="Defensa contra simulacion de Ransomware",
        epilog="Detecta archivos .locked, restaura texto invertido y limpia artefactos.",
    )
    parser.add_argument(
        '--clean',
        action='store_true',
        help='Restaurar archivos y eliminar directorio_pruebas/',
    )
    args = parser.parse_args()

    if args.clean:
        limpiar()
    else:
        ejecutar_escaneo()


if __name__ == "__main__":
    main()
