#!/usr/bin/env python3
"""
Simulacion educativa de Ransomware — Modulo 01.

Demuestra el flujo completo de un ataque ransomware usando inversion de texto
como mecanismo de "cifrado" inofensivo. NO usa cifrado real — invierte el
orden de los caracteres de cada linea de archivos .txt dentro de
./directorio_pruebas/.

Uso:
    python modulos/01_ransomware/ransomware.py          Ejecutar simulacion
    python modulos/01_ransomware/ransomware.py --clean  Limpiar artefactos
    python modulos/01_ransomware/ransomware.py --help   Mostrar ayuda
"""
import os
import sys
import shutil
import argparse
import time

# ── Configuracion de rutas absolutas robustas ───────────────────────────────
_DIR_RAIZ = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, _DIR_RAIZ)

from modulos.common.utils import (
    log, safe_print, color, banner, traverse_lab_files,
    hash_file, read_file, cleanup, write_log, is_lab_ready,
    LOG_LINES, find_lab_dir,
)

# ── Constantes fijadas a la raíz ────────────────────────────────────────────
DIR_SIMULACION = find_lab_dir(_DIR_RAIZ)

EXTENSION_LOCKED = '.locked'
NOTA_RESCATE = 'README_RESCATE.txt'

ARCHIVOS_LAB = {
    'documento.txt', 'notas.txt', 'script.py', 'index.html',
    'datos.csv', 'leeme.md', 'imagen.png', 'imagen.jpg',
    'audio.mp3', 'documento.docx', 'planilla.xlsx', 'presentacion.pptx',
}

EXTENSIONES_TEXTO = {'.txt', '.py', '.html', '.csv', '.md'}


# ── Funciones auxiliares ────────────────────────────────────────────────────

def paso_fase(fase_num, titulo):
    """Imprime un encabezado de fase con formato visual llamativo."""
    safe_print(color(f"\n  [FASE {fase_num}] {titulo}", 'yellow'))
    safe_print(color(f"  {'─' * 55}", 'yellow'))
    time.sleep(0.1) # Reducido un poco para mayor fluidez en la TUI


def invertir_texto(texto):
    """Invierte el orden de caracteres de cada linea del texto."""
    lineas = texto.split('\n')
    lineas_invertidas = [linea[::-1] for linea in lineas]
    return '\n'.join(lineas_invertidas)


def preparar_directorio():
    """Crea directorio_pruebas/ de forma absoluta y copia las plantillas."""
    os.makedirs(DIR_SIMULACION, exist_ok=True)

    archivos_lab = traverse_lab_files(_DIR_RAIZ)
    copiados = 0
    for archivo in archivos_lab:
        nombre = os.path.basename(archivo)
        if nombre not in ARCHIVOS_LAB:
            continue
        destino = os.path.join(DIR_SIMULACION, nombre)
        if not os.path.exists(destino):
            shutil.copy2(archivo, destino)
            copiados += 1

    log(f"Directorio preparado: {DIR_SIMULACION} ({copiados} archivos copiados)")
    safe_print(color(f"  Directorio de trabajo: {DIR_SIMULACION}", 'green'))
    safe_print(color(f"  Archivos copiados: {copiados}\n", 'green'))
    return copiados


def crear_nota_rescate():
    """Genera la nota de rescate demostrativa."""
    contenido = (
        "╔══════════════════════════════════════════════════════════════════╗\n"
        "║              ¡¡¡TUS ARCHIVOS HAN SIDO CIFRADOS!!!              ║\n"
        "╠══════════════════════════════════════════════════════════════════╣\n"
        "║                                                                ║\n"
        "║  Todos tus archivos importantes han sido cifrados con un       ║\n"
        "║  algoritmo de cifrado avanzado (SIMULACION EDUCATIVA).         ║\n"
        "║                                                                ║\n"
        "║  Para recuperar tus archivos necesitas:                        ║\n"
        "║                                                                ║\n"
        "║  1. Descargar Tor Browser                                      ║\n"
        "║  2. Visitar la direccion: http://xxx.onion/pagar               ║\n"
        "║  3. Ingresar tu ID de victima: EDUCA-2026-SIM                  ║\n"
        "║  4. Pagar 0.5 BTC a la direccion indicada                      ║\n"
        "║                                                                ║\n"
        "║  ADVERTENCIA: Tienes 72 horas para pagar. Despues de ese       ║\n"
        "║  plazo, la clave de descifrado sera eliminada.                 ║\n"
        "║                                                                ║\n"
        "║  >>> ESTO ES UNA SIMULACION EDUCATIVA <<<                      ║\n"
        "║  No existe deuda real. Ejecuta --clean para restaurar.         ║\n"
        "║                                                                ║\n"
        "╚══════════════════════════════════════════════════════════════════╝\n"
    )
    ruta_nota = os.path.join(DIR_SIMULACION, NOTA_RESCATE)
    with open(ruta_nota, 'w', encoding='utf-8') as f:
        f.write(contenido)
    log(f"Nota de rescate creada: {NOTA_RESCATE}")
    safe_print(color(f"  [!] Nota de rescate creada: {NOTA_RESCATE}", 'red'))


def listar_objetivos():
    """Enumera archivos de texto del laboratorio en directorio_pruebas/."""
    objetivos = []
    if not os.path.isdir(DIR_SIMULACION):
        return objetivos
    for nombre in sorted(os.listdir(DIR_SIMULACION)):
        ruta = os.path.join(DIR_SIMULACION, nombre)
        if not os.path.isfile(ruta):
            continue
        _, ext = os.path.splitext(nombre)
        if nombre in ARCHIVOS_LAB and ext.lower() in EXTENSIONES_TEXTO and nombre != NOTA_RESCATE:
            objetivos.append(ruta)
    return objetivos


# ── Simulacion principal ────────────────────────────────────────────────────

def ejecutar_simulacion():
    """Ejecuta la simulacion completa paso a paso."""
    banner(
        "RANSOMWARE — SIMULACION EDUCATIVA",
        "Inversion de texto como cifrado simulado en directorio_pruebas/",
    )
    safe_print(color(
        "  Este script simula un ataque ransomware sobre archivos copiados\n"
        "  a ./directorio_pruebas/. NO toca los archivos originales del lab.\n",
        'cyan',
    ))

# Comprobación robusta adaptada al entorno de ejecución de la TUI
    # Si ya tienes los archivos en directorio_pruebas o si el lab base está listo, el entorno es válido.
    lab_listo = False
    try:
        # Intenta pasarle la raíz fija si la función lo soporta
        lab_listo = is_lab_ready(_DIR_RAIZ)
    except TypeError:
        # Si la función no acepta argumentos, revisa si ya tienes archivos en el directorio de pruebas
        if os.path.exists(DIR_SIMULACION) and len(os.listdir(DIR_SIMULACION)) >= 12:
            lab_listo = True
        else:
            lab_listo = is_lab_ready()

    if not lab_listo:
        safe_print(color("  [!] No se encontraron los archivos base del laboratorio.", 'red'))
        safe_print(color("  Ejecuta la inicialización manual usando la tecla [Q] en la TUI.", 'red'))
        sys.exit(1)

    # ── FASE 1: Preparacion del entorno ─────────────────────────────────────
    paso_fase(1, "PREPARACION — Copiando archivos objetivo a directorio de prueba")
    log("Fase 1: Preparacion del entorno")
    safe_print(color(
        "  El ransomware primero identifica y copia los archivos que va a\n"
        "  cifrar. En un ataque real, esto ocurre en silencio.\n",
        'cyan',
    ))
    preparar_directorio()
    time.sleep(0.3)

    # ── FASE 2: Reconocimiento ──────────────────────────────────────────────
    paso_fase(2, "RECONOCIMIENTO — Enumerando archivos de texto")
    log("Fase 2: Reconocimiento")
    safe_print(color("  El ransomware busca archivos con extensiones objetivo:\n", 'cyan'))
    
    # CORREGIDO: Eliminado el typo que causaba fallos en el parser
    objetivos = listar_objetivos()
    
    for ruta in objetivos:
        nombre = os.path.basename(ruta)
        tamano = os.path.getsize(ruta)
        safe_print(color(f"    [+] {nombre} ({tamano} bytes) — OBJETIVO", 'green'))
    safe_print(color(f"\n  Total archivos objetivo: {len(objetivos)}", 'yellow'))
    time.sleep(0.3)

    # ── FASE 3: Cifrado simulado (inversion de texto) ───────────────────────
    paso_fase(3, "CIFRADO — Invirtiendo contenido de archivos de texto")
    log("Fase 3: Cifrado de archivos")
    safe_print(color(
        "  Metodo: inversion de caracteres por linea (NO es cifrado real).\n"
        "  En un ransom real se usaria AES-256 + RSA-2048.\n",
        'cyan',
    ))
    archivos_cifrados = []
    for ruta in objetivos:
        nombre = os.path.basename(ruta)
        with open(ruta, 'r', encoding='utf-8', errors='replace') as f:
            contenido_original = f.read()

        hash_original = hash_file(ruta)
        contenido_invertido = invertir_texto(contenido_original)

        ruta_locked = ruta + EXTENSION_LOCKED
        with open(ruta_locked, 'w', encoding='utf-8') as f:
            f.write(contenido_invertido)

        archivos_cifrados.append((ruta, ruta_locked, hash_original))
        hash_display = (hash_original[:32] + '...') if hash_original else 'N/A'
        safe_print(color(f"    [CIFRADO] {nombre} → {nombre}{EXTENSION_LOCKED}", 'red'))
        safe_print(color(f"             SHA-256 original: {hash_display}", 'blue'))
        log(f"  Cifrado: {nombre} -> {nombre}{EXTENSION_LOCKED} (hash: {hash_display})")

    time.sleep(0.3)

    # ── FASE 4: Dejar nota de rescate ───────────────────────────────────────
    paso_fase(4, "RESCATE — Dejando nota para la victima")
    log("Fase 4: Dejar nota de rescate")
    safe_print(color(
        "  El ransomware deja un archivo de texto con instrucciones\n"
        "  de pago. Este es el sello mas distintivo de un ransomware.\n",
        'cyan',
    ))
    crear_nota_rescate()
    time.sleep(0.3)

    # ── FASE 5: Resumen ─────────────────────────────────────────────────────
    paso_fase(5, "RESUMEN DEL ATAQUE")
    safe_print(color(f"\n  Archivos cifrados (invertidos):  {len(archivos_cifrados)}", 'red'))
    safe_print(color(f"  Copias .locked creadas:          {len(archivos_cifrados)}", 'yellow'))
    safe_print(color(f"  Nota de rescate:                 {NOTA_RESCATE}", 'yellow'))
    safe_print(color(f"  Directorio de trabajo:           {DIR_SIMULACION}\n", 'cyan'))

    safe_print(color("  LECCION EDUCATIVA:", 'bold'))
    safe_print(color("  - El ransomware NO destruye archivos: los CIFRA y guarda la clave.", 'cyan'))
    safe_print(color("  - El verdadero dano es la PERDIDA DE ACCESO, no la destruccion.", 'cyan'))
    safe_print(color("  - Un backup actualizado es la mejor defensa contra ransomware.", 'cyan'))
    safe_print(color("  - La nota de rescate es el indicador clave para identificarlo.\n", 'cyan'))

    write_log("ransomware_sim", list(LOG_LINES))


def limpiar():
    """Elimina todos los artefactos generados por la simulacion."""
    banner("RANSOMWARE — LIMPIEZA", "Eliminando artefactos de la simulacion")
    removed = 0

    if os.path.isdir(DIR_SIMULACION):
        shutil.rmtree(DIR_SIMULACION)
        safe_print(color(f"  eliminado: directorio_pruebas/ (entero)", 'green'))
        removed += 1

    removed += cleanup(patterns=[NOTA_RESCATE, 'ransomware_sim.log'])
    safe_print(color(f"\n  Limpieza completada: {removed} artefactos eliminados.\n", 'green'))


def main():
    parser = argparse.ArgumentParser(
        description="Simulacion educativa de Ransomware (inversion de texto)",
        epilog=(
            "Este script NO genera dano real. Copia archivos a directorio_pruebas/\n"
            "y crea copias .locked con el texto invertido. Ejecuta --clean para restaurar."
        ),
    )
    parser.add_argument(
        '--clean',
        action='store_true',
        help='Eliminar el directorio directorio_pruebas/ y todos los artefactos',
    )
    args = parser.parse_args()

    if args.clean:
        limpiar()
    else:
        ejecutar_simulacion()


if __name__ == "__main__":
    main()