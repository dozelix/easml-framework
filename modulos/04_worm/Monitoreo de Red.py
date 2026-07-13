#!/usr/bin/env python3
"""
Modulo 04 - Defensa contra gusano (worm) educativo.

Detecta y elimina las copias del gusano simulado en directorios
compartidos. Reconstruye el grafo de propagacion y muestra
estadisticas del incidente.

SOLO PARA USO EDUCATIVO EN ENTORNO CONTROLADO.

Uso:
    python modulos/04_worm/defensa.py           Ejecutar defensa
    python modulos/04_worm/defensa.py --help    Mostrar ayuda
"""
import os
import sys
import shutil

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, ROOT)

from core.common import (
    banner, color, safe_print, log, LOG_LINES,
    write_log, hash_file, traverse_lab_files,
)

# ── Ruta del directorio de pruebas ──
LAB_DIR = find_lab_dir(ROOT)

# ── Marcadores que inserta worm.py ──
WORM_NAME = "worm_sim.py"
WORM_MARKER = "# WORM_PAYLOAD_SIMULATION"


# ══════════════════════════════════════════════════════════════
#  FUNCIONES DE DETECCION
# ══════════════════════════════════════════════════════════════

def buscar_copias_gusano():
    """
    Busca todas las copias del gusano en directorio_pruebas/.
    Extrae el hash SHA-256 y el nodo de origen de cada copia.

    En un entorno real, un SOC analyst usaria YARA rules o
    hashes de IOC (Indicators of Compromise) para detectar
    artefactos de gusanos conocidos.
    """
    encontrados = []
    if not os.path.isdir(LAB_DIR):
        return encontrados

    for dirpath, dirnames, filenames in os.walk(LAB_DIR):
        for fname in filenames:
            fpath = os.path.join(dirpath, fname)
            if fname == WORM_NAME:
                h = hash_file(fpath)
                rel_path = os.path.relpath(fpath, ROOT)
                size = os.path.getsize(fpath)

                # Extraer nodo de origen desde el contenido
                origen = "desconocido"
                try:
                    with open(fpath, 'r', encoding='utf-8', errors='ignore') as f:
                        for linea in f:
                            if linea.startswith('# Nodo origen:'):
                                origen = linea.split(':', 1)[1].strip()
                                break
                except Exception:
                    pass

                encontrados.append({
                    'path': fpath,
                    'rel_path': rel_path,
                    'hash': h,
                    'size': size,
                    'origen': origen,
                })
    return encontrados


def detectar_marcadores_en_archivos():
    """
    Escanea archivos del laboratorio buscando el marcador del gusano.
    Simula como un EDR detectaria la presencia del malware en archivos
    legitimos que fueron modificados o infectados.
    """
    hallazgos = []
    for fpath in traverse_lab_files(LAB_DIR):
        try:
            with open(fpath, 'r', encoding='utf-8', errors='ignore') as f:
                contenido = f.read(4096)
            if WORM_MARKER in contenido:
                hallazgos.append(fpath)
        except Exception:
            pass
    return hallazgos


# ══════════════════════════════════════════════════════════════
#  FUNCIONES DE VISUALIZACION
# ══════════════════════════════════════════════════════════════

def construir_grafo(copias):
    """
    Reconstruye el grafo de propagacion a partir de los datos
    extraidos de cada copia. En un incidente real, esto se haria
    con logs de firewall, netflow y telemetry de EDR.
    """
    safe_print(color("\n  Grafo de propagacion detectado:\n", 'bold'))

    nodos = set()
    aristas = []
    for copia in copias:
        origen = copia['origen']
        destino_dir = os.path.relpath(
            os.path.dirname(copia['path']), LAB_DIR
        )
        nodos.add(origen)
        nodos.add(destino_dir)
        aristas.append((origen, destino_dir))

    for nodo in sorted(nodos):
        safe_print(color(f"  [NODO] {nodo}", 'cyan'))
    safe_print("")

    for src, dst in aristas:
        if src != dst:
            safe_print(color(f"  {src}  ────>  {dst}", 'yellow'))
        else:
            safe_print(color(f"  {src}  [ORIGEN]", 'red'))
    safe_print("")


def mostrar_resultados(copias, marcadores):
    """Muestra los resultados del escaneo de forma visual."""
    safe_print(color("\n  Resultados del escaneo:\n", 'bold'))

    if not copias and not marcadores:
        safe_print(color(
            "  [OK] No se detectaron artefactos del gusano.\n", 'green'
        ))
        return False

    # Copias del gusano encontradas
    if copias:
        safe_print(color(
            f"  [!] Copias del gusano encontradas: {len(copias)}\n", 'red'
        ))
        for i, copia in enumerate(copias, 1):
            safe_print(color(f"    {i}. {copia['rel_path']}", 'red'))
            safe_print(color(f"       Hash SHA-256: {copia['hash'][:32]}...", 'yellow'))
            safe_print(color(f"       Tamano: {copia['size']} bytes", 'yellow'))
            safe_print(color(f"       Nodo origen: {copia['origen']}", 'yellow'))
            log(f"Copia detectada: {copia['rel_path']} (origen: {copia['origen']})")

    # Archivos con marcador
    if marcadores:
        safe_print(color(
            f"\n  [!] Archivos con marcador del gusano: {len(marcadores)}",
            'red'
        ))
        for fpath in marcadores:
            safe_print(color(
                f"    - {os.path.relpath(fpath, ROOT)}", 'yellow'
            ))

    # Mostrar grafo si hay copias
    if copias:
        construir_grafo(copias)

    return True


# ══════════════════════════════════════════════════════════════
#  FUNCIONES DE LIMPIEZA
# ══════════════════════════════════════════════════════════════

def limpiar_gusano(copias):
    """
    Elimina todas las copias del gusano y los directorios compartidos.
    En un entorno real, esto equivaleria a:
    1. Aislar el segmento de red afectado
    2. Eliminar las copias del malware de todos los hosts
    3. Restaurar desde backups limpios
    4. Parchar la vulnerabilidad explotada
    """
    safe_print(color("\n  Limpiando artefactos del gusano...\n", 'bold'))
    eliminados = 0

    # Eliminar cada copia del gusano
    for copia in copias:
        try:
            os.remove(copia['path'])
            safe_print(color(f"  [+] Eliminado: {copia['rel_path']}", 'green'))
            eliminados += 1
            log(f"Eliminado: {copia['rel_path']}")
        except Exception as e:
            safe_print(color(
                f"  [-] Error al eliminar {copia['rel_path']}: {e}", 'red'
            ))

    # Eliminar directorios compartidos completos
    for node in ["shareA", "shareB", "shareC"]:
        share_path = os.path.join(LAB_DIR, node)
        if os.path.isdir(share_path):
            shutil.rmtree(share_path)
            safe_print(color(
                f"  [+] Directorio eliminado: {node}/", 'green'
            ))
            eliminados += 1

    # Eliminar log de la simulacion
    log_path = os.path.join(ROOT, "04_worm.log")
    if os.path.exists(log_path):
        os.remove(log_path)
        safe_print(color("  [+] Eliminado: 04_worm.log", 'green'))
        eliminados += 1

    # Eliminar log de defensa
    def_log = os.path.join(ROOT, "04_worm_defensa.log")
    if os.path.exists(def_log):
        os.remove(def_log)
        safe_print(color("  [+] Eliminado: 04_worm_defensa.log", 'green'))
        eliminados += 1

    safe_print(color(
        f"\n  Total eliminado: {eliminados} artefactos", 'green'
    ))
    return eliminados


# ══════════════════════════════════════════════════════════════
#  RESUMEN DE DEFENSA
# ══════════════════════════════════════════════════════════════

def mostrar_resumen_defensa():
    """Muestra recomendaciones de defensa contra gusanos reales."""
    safe_print(color("\n  ═══ RESUMEN DE DEFENSA ═══\n", 'bold'))

    safe_print(color("  Herramientas y practicas recomendadas:", 'cyan'))
    safe_print("  1. FIREWALL: Filtrar puertos SMB (445), RPC (135), SSH (22)")
    safe_print("  2. IDS/IPS: Detectar patrones de escaneo de red y replicacion")
    safe_print("  3. EDR: Monitorear comportamiento de replicacion de archivos")
    safe_print("  4. SEGMENTACION: Aislar segmentos de red criticos con VLANs")
    safe_print("  5. PARCHADO: Actualizar parches de seguridad urgentemente")
    safe_print("  6. AUTENTICACION: Credenciales robustas + 2FA en todos los servicios")
    safe_print("  7. RESPUESTA: Aislar hosts, quarantinar, analisis forense\n")


# ══════════════════════════════════════════════════════════════
#  PUNTO DE ENTRADA
# ══════════════════════════════════════════════════════════════

def mostrar_ayuda():
    safe_print(color("\nUso: python defensa.py [opcion]", 'cyan'))
    safe_print(color("\nOpciones:", 'bold'))
    safe_print("  (sin args)  Ejecutar la defensa contra el gusano")
    safe_print("  --help      Mostrar esta ayuda")
    safe_print(color("\nDescripcion:", 'bold'))
    safe_print("  Detecta copias del gusano, reconstruye el grafo de")
    safe_print("  propagacion y elimina todos los artefactos.\n")


def main():
    if '--help' in sys.argv or '-h' in sys.argv:
        mostrar_ayuda()
        return

    banner("DEFENSA - MODULO 04 (GUSANO)",
           "Deteccion y limpieza de artefactos de gusano")
    safe_print(color("  Entorno: laboratorio educativo controlado\n", 'cyan'))

    # ── FASE 1: Buscar copias del gusano ──
    safe_print(color("\n  [FASE 1] Escaneando directorios compartidos...\n", 'bold'))
    copias = buscar_copias_gusano()
    safe_print(color(f"  Copias encontradas: {len(copias)}", 'yellow'))

    # ── FASE 2: Buscar marcadores en archivos ──
    safe_print(color("\n  [FASE 2] Escaneando archivos del laboratorio...\n", 'bold'))
    marcadores = detectar_marcadores_en_archivos()
    safe_print(color(
        f"  Archivos con marcador del gusano: {len(marcadores)}", 'yellow'
    ))

    # ── FASE 3: Mostrar resultados ──
    hay_artefactos = mostrar_resultados(copias, marcadores)

    # ── FASE 4: Limpiar si hay artefactos ──
    if hay_artefactos:
        safe_print(color("\n  [FASE 3] Limpiando artefactos...\n", 'bold'))
        limpiar_gusano(copias)

    # ── Resumen ──
    mostrar_resumen_defensa()

    write_log(
        "04_worm_defensa", list(LOG_LINES),
        os.path.join(ROOT, "04_worm_defensa.log")
    )
    safe_print(color("  Defensa completada.\n", 'green'))


if __name__ == "__main__":
    main()
