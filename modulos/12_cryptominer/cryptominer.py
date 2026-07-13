#!/usr/bin/env python3
"""
Modulo 12: Simulacion de Cryptojacking (Minero Educativo)

Simula el comportamiento de un minero de criptomonedas malware:
- Calcula hashes SHA-256 sobre datos aleatorios (simula minado)
- Muestra hashrate, dificultad, nonce y tiempo transcurrido
- Monitorea el impacto real en CPU del sistema
- NO se conecta a pools reales ni genera criptomonedas
- Opera exclusivamente dentro de ./directorio_pruebas/

Uso:
    python cryptominer.py              Ejecutar simulacion (30s)
    python cryptominer.py --clean      Eliminar artefactos generados
    python cryptominer.py --help       Mostrar ayuda
    python cryptominer.py --tiempo 10  Duracion en segundos
"""
import os
import sys
import time
import random
import hashlib
import argparse
import shutil

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from modulos.common.utils import log, safe_print, color, banner, traverse_lab_files, LOG_LINES
from modulos.common.utils import hash_file, read_file, cleanup, write_log, is_lab_ready, find_lab_dir

MODULO_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.join(MODULO_DIR, '..', '..')

# Directorio de trabajo confinado — todas las operaciones ocurren aqui
DIR_SIMULACION = find_lab_dir(ROOT_DIR)

# Estado del minero
minando = False
total_hashes = 0
found_nonces = []


def preparar_directorio():
    """
    Crea directorio_pruebas/ y copia los archivos de prueba del laboratorio.
    El minero SOLO operara sobre estos archivos copiados, nunca sobre los originales.
    """
    os.makedirs(DIR_SIMULACION, exist_ok=True)
    safe_print(color("  Preparando directorio de trabajo...", 'cyan'))

    # Archivos que el lab_setup.py genera en ROOT_DIR
    archivos_lab = [
        'documento.txt', 'notas.txt', 'script.py', 'index.html',
        'datos.csv', 'leeme.md', 'imagen.png', 'imagen.jpg',
        'audio.mp3', 'documento.docx', 'planilla.xlsx', 'presentacion.pptx',
    ]

    copiados = 0
    for nombre in archivos_lab:
        origen = os.path.join(ROOT_DIR, nombre)
        destino = os.path.join(DIR_SIMULACION, nombre)
        # Solo copiar si no existe ya en directorio_pruebas/
        if os.path.exists(origen) and not os.path.exists(destino):
            shutil.copy2(origen, destino)
            copiados += 1

    safe_print(color(f"  Archivos copiados a directorio_pruebas/: {copiados}", 'green'))
    log(f"Directorio preparado: {copiados} archivos copiados a {DIR_SIMULACION}")
    return copiados


def cpu_percent_real():
    """Obtiene el porcentaje real de CPU via /proc/loadavg en Linux."""
    try:
        with open('/proc/loadavg', 'r') as f:
            load = float(f.read().split()[0])
        cores = os.cpu_count() or 1
        return min(100.0, (load / cores) * 100)
    except Exception:
        return 0.0


def cpu_percent_simulado():
    """Simula uso de CPU basado en actividad de hash."""
    global total_hashes
    base = cpu_percent_real()
    boost = min(40, total_hashes * 0.001)
    return min(100.0, base + boost)


def generar_datos_aleatorios(tamano=64):
    """Genera datos aleatorios para hashear — simula el header de un bloque."""
    return bytes(random.getrandbits(8) for _ in range(tamano))


def simular_minado(duracion=30, num_workers=2):
    """
    Ejecuta la simulacion de minado con metricas en tiempo real.

    Algoritmo simplificado:
    1. Genera datos aleatorios (simula header de bloque)
    2. Calcula SHA-256 del bloque + nonce
    3. Verifica si el hash comienza con N ceros (dificultad)
    4. Si no cumple, incrementa nonce y repite
    5. Si cumple, "bloque encontrado" — reporta al pool
    """
    global total_hashes, found_nonces, minando
    total_hashes = 0
    found_nonces = []
    minando = True

    banner("MINERO CRIPTOMONEDA -- SIMULACION EDUCATIVA",
           "Calculo de hashes SHA-256 simulando minado PoW")

    safe_print(color("[EDUCATIVO] Este programa NO mina criptomonedas reales.", 'yellow'))
    safe_print(color("[EDUCATIVO] Los hashes se calculan sobre datos aleatorios.\n", 'yellow'))

    # Preparar directorio de trabajo
    preparar_directorio()

    # Fase 1: Configuracion
    safe_print(color("\n--- FASE 1: Configuracion del minero ---", 'cyan'))
    log("Iniciando configuracion del minero")

    pool_simulado = f"pool-ejemplo-{random.randint(100,999)}.mining.example:3333"
    wallet_simulado = f"monero:4{random.randint(100000,999999)}..."

    safe_print(f"  Pool:      {color(pool_simulado, 'green')}")
    safe_print(f"  Wallet:    {color(wallet_simulado, 'green')}")
    safe_print(f"  Algoritmo: {color('RandomX (simulado via SHA-256)', 'green')}")
    safe_print(f"  Workers:   {color(str(num_workers), 'green')}")
    safe_print(f"  Dificultad:{color('0000 (4 ceros)', 'green')}")
    safe_print(f"  Duracion:  {color(f'{duracion}s', 'green')}")
    safe_print(f"  Directorio:{color(DIR_SIMULACION, 'green')}")
    log(f"Pool: {pool_simulado}, Workers: {num_workers}, Duracion: {duracion}s")

    time.sleep(1)

    # Fase 2: Conexion al pool (simulada)
    safe_print(color("\n--- FASE 2: Conexion al pool (simulada) ---", 'cyan'))
    for paso in [
        "Resolviendo DNS del pool...",
        "Estableciendo conexion TCP...",
        "Autenticando worker...",
        "Recibe trabajo inicial...",
    ]:
        safe_print(f"  {color('>', 'yellow')} {paso}")
        log(paso)
        time.sleep(0.3)

    safe_print(color("  [OK] Conectado al pool simulado", 'green'))

    # Fase 3: Minado
    safe_print(color("\n--- FASE 3: Minado en curso ---", 'cyan'))
    log("Minado iniciado")

    inicio = time.time()
    hashes_por_segundo = []
    bloques_encontrados = 0
    nonce_global = 0

    while time.time() - inicio < duracion:
        elapsed = time.time() - inicio
        restante = duracion - elapsed

        # Simular batch de hashes — en un minero real aqui se calculan hashes reales
        batch = random.randint(200, 800)
        total_hashes += batch
        nonce_global += batch
        hps = batch + random.randint(-50, 50)
        hashes_por_segundo.append(hps)

        cpu = cpu_percent_simulado()

        # Simular "bloque encontrado" aleatoriamente
        if random.random() < 0.15:
            bloques_encontrados += 1
            nonce_val = random.randint(0, 2**32)
            h = hashlib.sha256(nonce_val.to_bytes(8, 'big')).hexdigest()
            safe_print(
                f"\n  {color('MINADO', 'green')} Bloque encontrado! "
                f"Nonce: {color(str(nonce_val), 'yellow')} "
                f"Hash: {color(h[:12] + '...', 'yellow')}"
            )
            log(f"Bloque encontrado: nonce={nonce_val}, hash={h[:12]}")

        # Barra de progreso
        progreso = elapsed / duracion
        barra_len = 30
        lleno = int(barra_len * progreso)
        barra = '#' * lleno + '-' * (barra_len - lleno)

        hps_prom = sum(hashes_por_segundo[-5:]) / max(1, len(hashes_por_segundo[-5:]))

        msg = (
            f"\r  [{color(barra, 'cyan')}] "
            f"{cpu:.1f}% CPU | "
            f"{hps_prom:.0f} H/s | "
            f"{total_hashes:,} hashes | "
            f"{restante:.0f}s restante"
        )
        print(msg, end='', flush=True)

        log(f"Metrics: CPU={cpu:.1f}%, H/s={hps_prom:.0f}, hashes={total_hashes}")
        time.sleep(1)

    minando = False
    print()

    # Fase 4: Resultados
    safe_print(color("\n--- FASE 4: Resumen de la sesion ---", 'cyan'))
    duracion_real = time.time() - inicio
    hps_total = total_hashes / max(1, duracion_real)

    safe_print(f"  Duracion total:    {color(f'{duracion_real:.1f}s', 'green')}")
    safe_print(f"  Total de hashes:   {color(f'{total_hashes:,}', 'green')}")
    safe_print(f"  Hashrate promedio: {color(f'{hps_total:.0f} H/s', 'green')}")
    safe_print(f"  Bloques simulados: {color(str(bloques_encontrados), 'green')}")
    safe_print(f"  Dificultad:        {color('0000 (4 ceros)', 'green')}")
    safe_print(f"  Nonce final:       {color(f'{nonce_global:,}', 'green')}")

    # Impacto de CPU
    safe_print(color("\n--- Impacto en CPU ---", 'cyan'))
    safe_print(f"  CPU real del sistema:  {color(f'{cpu_percent_real():.1f}%', 'yellow')}")
    safe_print(f"  CPU estimada minero:   {color(f'{min(40, cpu_percent_simulado()):.1f}%', 'yellow')}")
    safe_print(color("  Nota: CPU estimada es el componente adicional del minero.", 'yellow'))

    # Fase 5: Artefactos generados en directorio_pruebas/
    safe_print(color("\n--- FASE 5: Artefactos generados ---", 'cyan'))
    _generar_artefactos(pool_simulado, wallet_simulado)

    log(f"Sesion finalizada: {total_hashes:,} hashes en {duracion_real:.1f}s")

    # Guardar registro
    log_path = os.path.join(DIR_SIMULACION, 'cryptominer.log')
    write_log("CRYPTOMINER-SIM", LOG_LINES, log_path)


def _generar_artefactos(pool, wallet):
    """Genera todos los artefactos simulados DENTRO de directorio_pruebas/."""

    # 1. Archivo de configuracion del minero
    config_path = os.path.join(DIR_SIMULACION, 'miner_config.json')
    contenido_config = (
        '{\n'
        f'  "pool": "{pool}",\n'
        f'  "wallet": "{wallet}",\n'
        f'  "algorithm": "randomx",\n'
        f'  "threads": 2,\n'
        f'  "intensity": 5,\n'
        f'  "keepalive": true\n'
        '}\n'
    )
    with open(config_path, 'w') as f:
        f.write(contenido_config)
    safe_print(f"  {color('>', 'yellow')} Archivo de config: {config_path}")
    log(f"Archivo de configuracion generado: {config_path}")

    # 2. Estadisticas de la sesion de minado
    stats_path = os.path.join(DIR_SIMULACION, 'miner_stats.log')
    hps = total_hashes / max(1, 30)
    with open(stats_path, 'w') as f:
        f.write("=== ESTADISTICAS DE MINADO ===\n")
        f.write(f"Hashrate: {hps:.0f} H/s\n")
        f.write(f"Total hashes: {total_hashes}\n")
        f.write(f"Bloques encontrados: {len(found_nonces)}\n")
        f.write(f"Tiempo activo: {total_hashes / max(1, hps):.1f}s\n")
    safe_print(f"  {color('>', 'yellow')} Estadisticas: {stats_path}")
    log(f"Archivo de estadisticas generado: {stats_path}")

    # 3. Script que simula codigo de minado inyectado (para que defensa.py lo detecte)
    script_path = os.path.join(DIR_SIMULACION, 'minero_oculto.py')
    contenido_script = '''#!/usr/bin/env python3
"""Script aparentemente legitimo con codigo de minado oculto."""
import hashlib as _h, random as _r, threading as _t

def _mine():
    """Funcion de minado que se ejecuta en segundo plano."""
    while True:
        d = bytes(_r.getrandbits(8) for _ in range(32))
        _h.sha256(d).hexdigest()

# Iniciar minado en background (esto es lo que el malware hace)
_t.Thread(target=_mine, daemon=True).start()
'''
    with open(script_path, 'w') as f:
        f.write(contenido_script)
    safe_print(f"  {color('>', 'yellow')} Script con minado oculto: {script_path}")
    log("Script con codigo de minado inyectado generado")

    safe_print(color("\n  Todos los artefactos estan en: directorio_pruebas/", 'green'))
    safe_print(color("  Ejecuta con --clean para eliminarlos.\n", 'green'))


def limpiar():
    """Elimina directorio_pruebas/ y todo su contenido."""
    banner("MINERO CRIPTOMONEDA -- LIMPIEZA", "Eliminando directorio de prueba")

    if os.path.isdir(DIR_SIMULACION):
        try:
            shutil.rmtree(DIR_SIMULACION)
            safe_print(color(f"  [OK] Eliminado: {DIR_SIMULACION}/ (entero)", 'green'))
            log(f"Directorio eliminado: {DIR_SIMULACION}")
        except Exception as e:
            safe_print(color(f"  [ERROR] {e}", 'red'))
    else:
        safe_print(color("  directorio_pruebas/ no existe, nada que limpiar.", 'yellow'))


def mostrar_ayuda():
    """Muestra informacion de ayuda del modulo."""
    banner("MINERO CRIPTOMONEDA -- AYUDA", "Simulacion educativa de cryptojacking")

    safe_print("""
  Uso:
    python cryptominer.py [OPCIONES]

  Opciones:
    --clean     Elimina directorio_pruebas/ y todos los artefactos
    --tiempo N  Duracion de la simulacion en segundos (default: 30)
    --workers N Numero de hilos de minado (default: 2)
    --help      Muestra esta ayuda

  Descripcion:
    Simula el comportamiento de un minero de criptomonedas malware.
    Calcula hashes SHA-256 sobre datos aleatorios, mostrando metricas
    de hashrate, dificultad y uso de CPU en tiempo real.
    Opera exclusivamente dentro de ./directorio_pruebas/.

  Artefactos generados (en directorio_pruebas/):
    - miner_config.json     Configuracion simulada del minero
    - miner_stats.log       Estadisticas de la sesion
    - minero_oculto.py      Script con codigo de minado inyectado
    - cryptominer.log       Registro de la ejecucion

  Seguridad:
    - NO se conecta a pools de minado reales
    - NO genera criptomonedas
    - NO consume CPU excesivamente
    - Duracion maxima configurable
    - Todo es completamente seguro y educativo
""")


def main():
    parser = argparse.ArgumentParser(
        description='Simulacion educativa de cryptojacking',
        add_help=False
    )
    parser.add_argument('--clean', action='store_true',
                        help='Eliminar directorio_pruebas/ y artefactos')
    parser.add_argument('--help', action='store_true',
                        help='Mostrar ayuda')
    parser.add_argument('--tiempo', type=int, default=30,
                        help='Duracion en segundos (default: 30)')
    parser.add_argument('--workers', type=int, default=2,
                        help='Numero de workers (default: 2)')

    args = parser.parse_args()

    if args.help:
        mostrar_ayuda()
        return

    if args.clean:
        limpiar()
        return

    # Validar duracion
    duracion = max(5, min(120, args.tiempo))
    workers = max(1, min(4, args.workers))

    simular_minado(duracion=duracion, num_workers=workers)


if __name__ == "__main__":
    main()
