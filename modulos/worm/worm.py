#!/usr/bin/env python3
"""
Modulo 04 - Simulacion de gusano (worm) educativo.

Simula un gusano que se replica entre directorios compartidos
simulados (nodos de red), mostrando el patron de propagacion.

SOLO PARA USO EDUCATIVO EN ENTORNO CONTROLADO.

Uso:
    python modulos/04_worm/worm.py           Ejecutar simulacion
    python modulos/04_worm/worm.py --clean   Limpiar artefactos
    python modulos/04_worm/worm.py --help    Mostrar ayuda
"""
import os
import sys
import shutil
import time

# ── Configuracion de rutas ──
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, ROOT)

from modulos.common.utils import (
    banner, color, safe_print, log, LOG_LINES,
    write_log, cleanup, hash_file as _hash_file,
    find_lab_dir,
)

# ── Ruta del directorio de pruebas ──
LAB_DIR = find_lab_dir(ROOT)

# ── Configuracion de la simulacion ──
# Cada "nodo" representa un host en la red simulada
NODES = ["shareA", "shareB", "shareC"]

# Nombre del archivo gusano que se replica
WORM_NAME = "worm_sim.py"

# Marcador insertado en cada copia para que la defensa lo detecte
WORM_MARKER = "# WORM_PAYLOAD_SIMULATION"

# Maximo de rondas de propagacion (limitado para la demostracion)
MAX_ROUNDS = 3


# ══════════════════════════════════════════════════════════════
#  FUNCIONES AUXILIARES
# ══════════════════════════════════════════════════════════════

def _short_hash(path):
    """Devuelve los primeros 16 caracteres del hash SHA-256 para mostrar en consola."""
    h = _hash_file(path)
    return h[:16] + "..." if h else "N/A"


def _paso_fase(num, titulo):
    """Imprime un separador visual de fase."""
    safe_print(color(f"\n  [FASE {num}] {titulo}", 'yellow'))
    safe_print(color(f"  {'─' * 55}", 'yellow'))
    time.sleep(0.3)


# ══════════════════════════════════════════════════════════════
#  FUNCIONES DE SIMULACION
# ══════════════════════════════════════════════════════════════

def crear_nodos():
    """
    Crea los directorios compartidos simulados.
    Cada nodo representa un host en la red con una carpeta compartida
    (simulando una ruta SMB compartida).
    """
    _paso_fase(1, "CREANDO NODOS DE RED SIMULADOS")

    for node in NODES:
        share_path = os.path.join(LAB_DIR, node)
        os.makedirs(share_path, exist_ok=True)
        # Archivo de metadatos que simula la configuracion de la comparticion
        meta_path = os.path.join(share_path, ".share_info")
        with open(meta_path, 'w', encoding='utf-8') as f:
            f.write(f"Nodo: {node}\n")
            f.write(f"Tipo: Compartida SMB simulada\n")
            f.write(f"Estado: ACTIVA\n")
        safe_print(color(f"  [+] Nodo creado: directorio_pruebas/{node}/", 'green'))
        log(f"Nodo creado: {node}")

    time.sleep(0.3)
    safe_print(color(f"\n  Total nodos creados: {len(NODES)}", 'cyan'))


def crear_gusano_origen(directorio_nodo, nombre_nodo):
    """
    Crea una copia del gusano en el nodo origen.
    En un gusano real, este archivo contendria codigo que escanea
    la red y se replica automaticamente. Aqui es solo texto educativo
    con un marcador de deteccion.
    """
    worm_path = os.path.join(directorio_nodo, WORM_NAME)

    # El contenido incluye el marcador para que la defensa lo detecte,
    # y metadatos sobre el nodo de origen para reconstruir la propagacion.
    contenido = f"""#!/usr/bin/env python3
{WORM_MARKER}
# Nodo origen: {nombre_nodo}
# Tipo: GUSANO EDUCATIVO - No es malware real
# Este archivo simula un gusano para fines educativos.

import os
import shutil

ORIGEN = "{nombre_nodo}"
MARKER = "{WORM_MARKER}"

def propagar(destino):
    \"\"\"Simula la propagacion del gusano a un nuevo nodo.\"\"\"
    if os.path.exists(destino) and not os.path.exists(
        os.path.join(destino, "{WORM_NAME}")
    ):
        shutil.copy2(__file__, os.path.join(destino, "{WORM_NAME}"))
        return True
    return False

if __name__ == "__main__":
    print(f"[SIMULACION] Gusano ejecutado desde nodo: " + ORIGEN)
    print(f"[SIMULACION] Este es un archivo educativo inofensivo.")
"""
    with open(worm_path, 'w', encoding='utf-8') as f:
        f.write(contenido)

    return worm_path


def simular_propagacion():
    """
    Simula la propagacion del gusano entre nodos.

    ALGORITMO:
    1. El gusano aparece primero en el nodo origen (shareA).
    2. En cada ronda, cada nodo infectado intenta copiar el gusano
       a todos los nodos aun no infectados.
    3. La propagacion se repite hasta completar las rondas maximas
       o hasta que todos los nodos esten infectados.

    Esto simula el comportamiento de un worm de red real que escanea
    subredes y se replica a traves de comparticiones SMB/SSH.
    """
    _paso_fase(2, "PROPAGACION DEL GUSANO")
    log("Inicio de propagacion")
    historial = []

    # ── Paso 2.1: El gusano inicia en el nodo origen ──
    nodo_origen = NODES[0]
    dir_origen = os.path.join(LAB_DIR, nodo_origen)
    worm_path = crear_gusano_origen(dir_origen, nodo_origen)

    safe_print(color(
        f"  [!] GUSANO detectado en {nodo_origen}/{WORM_NAME}",
        'red'
    ))
    safe_print(color(
        f"      Hash SHA-256: {_short_hash(worm_path)}",
        'yellow'
    ))
    historial.append({
        "tipo": "ORIGEN",
        "origen": nodo_origen,
        "destino": nodo_origen,
        "hash": _hash_file(worm_path),
    })
    log(f"Gusano detectado en nodo origen: {nodo_origen}")

    # ── Paso 2.2: Rondas de propagacion ──
    nodos_infectados = [nodo_origen]

    for ronda in range(1, MAX_ROUNDS + 1):
        safe_print(color(f"\n  ═══ Ronda de propagacion {ronda} ═══", 'cyan'))
        nuevas_infecciones = []

        for nodo_fuente in list(nodos_infectados):
            for nodo_objetivo in NODES:
                # Saltar nodos ya infectados
                if nodo_objetivo in nodos_infectados:
                    continue

                dir_fuente = os.path.join(LAB_DIR, nodo_fuente)
                dir_objetivo = os.path.join(LAB_DIR, nodo_objetivo)

                if not os.path.isdir(dir_objetivo):
                    continue

                # Simular el escaneo de red (en un real se probarian puertos)
                safe_print(color(
                    f"    [>] Escaneando desde {nodo_fuente}...",
                    'blue'
                ))
                time.sleep(0.15)

                # Replicar el gusano al nodo destino
                worm_destino = crear_gusano_origen(dir_objetivo, nodo_fuente)

                safe_print(color(
                    f"    [!!] PROPAGACION: {nodo_fuente} --> {nodo_objetivo}",
                    'red'
                ))
                safe_print(color(
                    f"        Copia: {nodo_objetivo}/{WORM_NAME} "
                    f"(SHA: {_short_hash(worm_destino)})",
                    'yellow'
                ))

                historial.append({
                    "tipo": "PROPAGACION",
                    "ronda": ronda,
                    "origen": nodo_fuente,
                    "destino": nodo_objetivo,
                    "hash": _hash_file(worm_destino),
                })
                log(f"Propagacion R{ronda}: {nodo_fuente} -> {nodo_objetivo}")
                nuevas_infecciones.append(nodo_objetivo)
                time.sleep(0.15)

        nodos_infectados.extend(nuevas_infecciones)

        # Mostrar estado de infeccion
        safe_print(color(
            f"    [*] Nodos infectados: {len(nodos_infectados)}/{len(NODES)}",
            'cyan'
        ))

    return historial


def mostrar_grafo(historial):
    """Muestra un grafo ASCII de la propagacion del gusano."""
    _paso_fase(3, "GRAFO DE PROPAGACION")

    safe_print(color("  Nodo Origen                  Nodo Destino", 'cyan'))
    safe_print(color("  " + "=" * 55, 'cyan'))

    for entrada in historial:
        if entrada["tipo"] == "ORIGEN":
            safe_print(color(
                f"  [*] {entrada['origen']:<28} {entrada['destino']} (ORIGEN)",
                'red'
            ))
        else:
            ronda = entrada.get("ronda", "?")
            safe_print(color(
                f"  R{ronda}: {entrada['origen']:<26} {entrada['destino']}",
                'yellow'
            ))

    safe_print(color("  " + "=" * 55, 'cyan'))

    # Estadisticas
    destinos = set(e["destino"] for e in historial)
    safe_print(color(
        f"\n  Total nodos infectados: {len(destinos)}/{len(NODES)}",
        'red'
    ))
    safe_print(color(
        f"  Total rondas ejecutadas: {MAX_ROUNDS}",
        'cyan'
    ))
    safe_print(color(
        f"  Total copias del gusano: {len(historial)}",
        'cyan'
    ))


def mostrar_notas_educativas():
    """Explica al estudiante por que los gusanos son peligrosos."""
    safe_print(color("\n  ═══ NOTAS EDUCATIVAS ═══\n", 'bold'))

    safe_print(color("  Un gusano real se diferencia de un virus porque:", 'cyan'))
    safe_print("  1. No necesita un archivo hospedero para ejecutarse")
    safe_print("  2. Se propaga automaticamente sin accion del usuario")
    safe_print("  3. Puede explotar vulnerabilidades de red")
    safe_print("  4. Consuma ancho de banda y recursos del sistema")

    safe_print(color("\n  Vectores de propagacion comunes:", 'cyan'))
    safe_print("  - SMB/NETBIOS (puerto 445): Conficker, WannaCry")
    safe_print("  - SSH (puerto 22): gusanos de credenciales por defecto")
    safe_print("  - Email: ILOVEYOU, Mydoom")
    safe_print("  - USB/removibles: Stuxnet")

    safe_print(color("\n  En esta simulacion:", 'cyan'))
    safe_print("  - No se conecto a ninguna red real")
    safe_print("  - No se explotaron vulnerabilidades reales")
    safe_print("  - Los archivos creados son texto plano inofensivo")
    safe_print("  - Todo puede limpiarse con --clean\n")


# ══════════════════════════════════════════════════════════════
#  LIMPIEZA
# ══════════════════════════════════════════════════════════════

def limpiar():
    """Elimina todos los artefactos generados por la simulacion."""
    banner("MODULO 04 - GUSANO (WORM)", "LIMPIEZA DE ARTEFACTOS")
    removed = 0

    for node in NODES:
        share_path = os.path.join(LAB_DIR, node)
        if os.path.isdir(share_path):
            shutil.rmtree(share_path)
            safe_print(color(f"  [+] Eliminado: directorio_pruebas/{node}/", 'green'))
            removed += 1

    # Eliminar log de la simulacion en lab_data/logs/
    log_path = os.path.join(find_lab_dir(ROOT), '..', 'logs', "04_worm.log")
    if os.path.exists(log_path):
        os.remove(log_path)
        safe_print(color("  [+] Eliminado: 04_worm.log", 'green'))
        removed += 1

    safe_print(color(f"\n  Limpieza completada: {removed} directorios/archivos eliminados.\n", 'green'))


# ══════════════════════════════════════════════════════════════
#  AYUDA
# ══════════════════════════════════════════════════════════════

def mostrar_ayuda():
    safe_print(color("\nUso: python worm.py [opcion]", 'cyan'))
    safe_print(color("\nOpciones:", 'bold'))
    safe_print("  (sin args)  Ejecutar la simulacion del gusano")
    safe_print("  --clean     Eliminar todos los artefactos generados")
    safe_print("  --help      Mostrar esta ayuda")
    safe_print(color("\nDescripcion:", 'bold'))
    safe_print("  Simula un gusano que se replica entre directorios")
    safe_print("  compartidos simulados, mostrando propagacion de red.")
    safe_print("  Los archivos generados son INOFENSIVOS y operan")
    safe_print("  exclusivamente dentro de directorio_pruebas/.")
    safe_print(color("\nEjemplo:", 'bold'))
    safe_print("  python modulos/04_worm/worm.py")
    safe_print("  python modulos/04_worm/worm.py --clean\n")


# ══════════════════════════════════════════════════════════════
#  PUNTO DE ENTRADA
# ══════════════════════════════════════════════════════════════

def main():
    if '--help' in sys.argv or '-h' in sys.argv:
        mostrar_ayuda()
        return

    if '--clean' in sys.argv:
        limpiar()
        return

    banner("MODULO 04 - GUSANO (WORM)",
           "Simulacion de propagacion entre nodos de red")
    safe_print(color("  Entorno: laboratorio educativo controlado", 'cyan'))
    safe_print(color("  Los archivos generados son INOFENSIVOS\n", 'yellow'))

    # Crear nodo origen y nodos destino
    crear_nodos()

    # Simular la propagacion del gusano
    historial = simular_propagacion()

    # Mostrar grafo de propagacion
    mostrar_grafo(historial)

    # Notas educativas
    mostrar_notas_educativas()

    # Guardar registro
    write_log("04_worm", list(LOG_LINES))
    safe_print(color("  Simulacion completada.\n", 'green'))


if __name__ == "__main__":
    main()
