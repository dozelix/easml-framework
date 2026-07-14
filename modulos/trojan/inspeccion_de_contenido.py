#!/usr/bin/env python3
"""
Modulo 05 - Defensa contra troyano educativo.

Detecta archivos troyano simulados por marcadores de payload,
nombres sospechosos y extensiones ocultas. Realiza limpieza.

SOLO PARA USO EDUCATIVO EN ENTORNO CONTROLADO.

Uso:
    python modulos/05_trojan/defensa.py           Ejecutar defensa
    python modulos/05_trojan/defensa.py --help    Mostrar ayuda
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

# ── Marcadores de IOC (Indicators of Compromise) ──
PAYLOAD_MARKER = "TROJAN_PAYLOAD_SIMULATION"
STEALTH_MARKER = "HIDDEN_PAYLOAD_SIMULATION"
C2_MARKER = "C2_SERVER_ENDPOINT"

# ── Extensiones ejecutables sospechosas ──
SUSPICIOUS_EXTENSIONS = ['.exe', '.scr', '.bat', '.cmd', '.vbs', '.js', '.pif', '.com']

# ── Nombres de troyanos conocidos ──
SUSPICIOUS_NAMES = [
    'update.exe', 'setup.exe', 'install.exe', 'flash.exe',
    'invoice.pdf.exe', 'document.pdf.exe',
    'factura_2026.pdf.exe', 'imagen.jpg.exe',
]


# ══════════════════════════════════════════════════════════════
#  FUNCIONES DE DETECCION
# ══════════════════════════════════════════════════════════════

def escanear_marcadores():
    """
    Escanea archivos en busca de marcadores de payload.

    En un entorno real, esto equivale a un analisis de firmas
    YARA o una regla DLP (Data Loss Prevention) que busca
    patrones conocidos de malware.
    """
    hallazgos = []
    # Buscar en archivos del directorio de pruebas
    if os.path.isdir(LAB_DIR):
        for fname in os.listdir(LAB_DIR):
            fpath = os.path.join(LAB_DIR, fname)
            if not os.path.isfile(fpath):
                continue
            try:
                with open(fpath, 'r', encoding='utf-8', errors='ignore') as f:
                    contenido = f.read(8192)
                marcadores = []
                if PAYLOAD_MARKER in contenido:
                    marcadores.append('PAYLOAD')
                if STEALTH_MARKER in contenido:
                    marcadores.append('STEALTH')
                if C2_MARKER in contenido:
                    marcadores.append('C2')
                if marcadores:
                    hallazgos.append({
                        'path': fpath,
                        'nombre': fname,
                        'marcadores': marcadores,
                        'hash': hash_file(fpath),
                        'size': os.path.getsize(fpath),
                    })
            except Exception:
                pass
    return hallazgos


def escanear_nombres_sospechosos():
    """
    Busca archivos con nombres tipicos de troyanos.

    En un entorno real, esto equivale a un watchlist de IOC
    que monitorea el filesystem en busca de nombres conocidos
    de malware.
    """
    hallazgos = []
    if not os.path.isdir(LAB_DIR):
        return hallazgos

    for fname in os.listdir(LAB_DIR):
        fpath = os.path.join(LAB_DIR, fname)
        if not os.path.isfile(fpath):
            continue

        sospechoso = False
        razones = []

        # Verificar contra lista de nombres conocidos
        for sus_name in SUSPICIOUS_NAMES:
            if fname.lower() == sus_name.lower():
                sospechoso = True
                razones.append(f"Nombre conocido: {sus_name}")

        # Verificar extension ejecutable
        if any(fname.lower().endswith(ext) for ext in SUSPICIOUS_EXTENSIONS):
            sospechoso = True
            ext = os.path.splitext(fname)[1]
            razones.append(f"Extension ejecutable: {ext}")

        # Verificar extension multiple (disfraz)
        parts = fname.split('.')
        if len(parts) > 2:
            sospechoso = True
            razones.append("Extension multiple (posible disfraz de troyano)")

        if sospechoso:
            hallazgos.append({
                'path': fpath,
                'nombre': fname,
                'razones': razones,
                'hash': hash_file(fpath),
            })
    return hallazgos


# ══════════════════════════════════════════════════════════════
#  FUNCIONES DE VISUALIZACION
# ══════════════════════════════════════════════════════════════

def mostrar_resultados(hallazgos_marcadores, hallazgos_nombres):
    """Muestra los resultados del escaneo de forma visual."""
    safe_print(color("\n  Resultados del escaneo:\n", 'bold'))

    total = len(hallazgos_marcadores) + len(hallazgos_nombres)
    if total == 0:
        safe_print(color(
            "  [OK] No se detectaron artefactos del troyano.\n", 'green'
        ))
        return False

    # Marcadores de payload
    if hallazgos_marcadores:
        safe_print(color(
            f"  [!] Archivos con marcadores de payload: {len(hallazgos_marcadores)}\n",
            'red'
        ))
        for i, h in enumerate(hallazgos_marcadores, 1):
            safe_print(color(f"    {i}. {h['nombre']}", 'red'))
            safe_print(color(f"       Marcadores: {', '.join(h['marcadores'])}", 'yellow'))
            safe_print(color(f"       Hash SHA-256: {h['hash'][:32]}...", 'yellow'))
            safe_print(color(f"       Tamano: {h['size']} bytes", 'yellow'))
            log(f"Marcador detectado en {h['nombre']}: {h['marcadores']}")

    # Nombres sospechosos
    if hallazgos_nombres:
        safe_print(color(
            f"\n  [!] Archivos con nombres sospechosos: {len(hallazgos_nombres)}\n",
            'red'
        ))
        for i, h in enumerate(hallazgos_nombres, 1):
            safe_print(color(f"    {i}. {h['nombre']}", 'red'))
            for razon in h['razones']:
                safe_print(color(f"       - {razon}", 'yellow'))
            safe_print(color(f"       Hash SHA-256: {h['hash'][:32]}...", 'yellow'))
            log(f"Nombre sospechoso: {h['nombre']} ({', '.join(h['razones'])})")

    return True


# ══════════════════════════════════════════════════════════════
#  FUNCIONES DE LIMPIEZA
# ══════════════════════════════════════════════════════════════

def limpiar_troyano(hallazgos_marcadores, hallazgos_nombres):
    """
    Elimina los artefactos del troyano detectados.

    En un entorno real, esto incluiria:
    1. Quarantinar el archivo malicioso
    2. Buscar persistencia en claves de registro
    3. Buscar conexiones C2 activas y bloquearlas
    4. Restaurar archivos modificados
    5. Realizar analisis forense
    """
    safe_print(color("\n  Limpiando artefactos del troyano...\n", 'bold'))
    eliminados = 0

    # Recopilar todas las rutas unicas
    rutas = set()
    for h in hallazgos_marcadores:
        rutas.add(h['path'])
    for h in hallazgos_nombres:
        rutas.add(h['path'])

    for fpath in rutas:
        try:
            rel = os.path.relpath(fpath, ROOT)
            os.remove(fpath)
            safe_print(color(f"  [+] Eliminado: {rel}", 'green'))
            eliminados += 1
            log(f"Eliminado: {rel}")
        except Exception as e:
            safe_print(color(f"  [-] Error al eliminar {fpath}: {e}", 'red'))

    # Eliminar logs en lab_data/logs/
    log_dir = os.path.join(find_lab_dir(ROOT), '..', 'logs')
    sim_log = os.path.join(log_dir, "05_trojan.log")
    if os.path.exists(sim_log):
        os.remove(sim_log)
        safe_print(color("  [+] Eliminado: 05_trojan.log", 'green'))
        eliminados += 1

    def_log = os.path.join(log_dir, "05_trojan_defensa.log")
    if os.path.exists(def_log):
        os.remove(def_log)
        safe_print(color("  [+] Eliminado: 05_trojan_defensa.log", 'green'))
        eliminados += 1

    safe_print(color(f"\n  Total eliminado: {eliminados} artefactos", 'green'))
    return eliminados


# ══════════════════════════════════════════════════════════════
#  RESUMEN DE DEFENSA
# ══════════════════════════════════════════════════════════════

def mostrar_consejos_defensa():
    """Muestra recomendaciones de defensa contra troyanos."""
    safe_print(color("\n  ═══ CONSEJOS DE DEFENSA ═══\n", 'bold'))
    safe_print(color("  Herramientas y practicas recomendadas:", 'cyan'))
    safe_print("  1. Mostrar SIEMPRE las extensiones reales de archivos")
    safe_print("  2. Verificar firmas digitales de ejecutables")
    safe_print("  3. Usar antivirus con analisis de comportamiento (EDR)")
    safe_print("  4. No abrir adjuntos de emails no solicitados")
    safe_print("  5. Descargar software solo de fuentes oficiales")
    safe_print("  6. Mantener el sistema operativo actualizado y parchado")
    safe_print("  7. Implementar listas blancas de aplicaciones")
    safe_print("  8. Capacitar usuarios sobre ingenieria social\n")


# ══════════════════════════════════════════════════════════════
#  PUNTO DE ENTRADA
# ══════════════════════════════════════════════════════════════

def mostrar_ayuda():
    safe_print(color("\nUso: python defensa.py [opcion]", 'cyan'))
    safe_print(color("\nOpciones:", 'bold'))
    safe_print("  (sin args)  Ejecutar la defensa contra troyanos")
    safe_print("  --help      Mostrar esta ayuda")
    safe_print(color("\nDescripcion:", 'bold'))
    safe_print("  Detecta archivos con marcadores de payload, extensiones")
    safe_print("  duales y nombres sospechosos. Elimina todos los artefactos.\n")


def main():
    if '--help' in sys.argv or '-h' in sys.argv:
        mostrar_ayuda()
        return

    banner("DEFENSA - MODULO 05 (TROYANO)",
           "Deteccion y limpieza de artefactos de troyano")
    safe_print(color("  Entorno: laboratorio educativo controlado\n", 'cyan'))

    # ── FASE 1: Escaneo por marcadores de payload ──
    safe_print(color(
        "\n  [FASE 1] Escaneando archivos por marcadores de payload...\n",
        'bold'
    ))
    hallazgos_marcadores = escanear_marcadores()
    safe_print(color(
        f"  Archivos con marcadores: {len(hallazgos_marcadores)}", 'yellow'
    ))

    # ── FASE 2: Escaneo por nombres sospechosos ──
    safe_print(color(
        "\n  [FASE 2] Escaneando por nombres sospechosos...\n",
        'bold'
    ))
    hallazgos_nombres = escanear_nombres_sospechosos()
    safe_print(color(
        f"  Archivos con nombres sospechosos: {len(hallazgos_nombres)}",
        'yellow'
    ))

    # ── FASE 3: Mostrar resultados ──
    hay_artefactos = mostrar_resultados(hallazgos_marcadores, hallazgos_nombres)

    # ── FASE 4: Limpiar si hay artefactos ──
    if hay_artefactos:
        safe_print(color("\n  [FASE 3] Limpiando artefactos...\n", 'bold'))
        limpiar_troyano(hallazgos_marcadores, hallazgos_nombres)

    # ── Resumen ──
    mostrar_consejos_defensa()

    write_log(
        "05_trojan_defensa", list(LOG_LINES)
    )
    safe_print(color("  Defensa completada.\n", 'green'))


if __name__ == "__main__":
    main()
