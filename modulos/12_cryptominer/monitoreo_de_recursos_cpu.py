#!/usr/bin/env python3
"""
Modulo 12: Defensa contra Cryptojacking — Deteccion y Limpieza

Detecta artefactos generados por la simulacion de cryptojacking en
./directorio_pruebas/:
- Archivos de configuracion de minero (miner_config.json)
- Codigo de minado inyectado (minero_oculto.py)
- Logs de estadisticas de minado
- Patron de CPU anormal
- Procesos de minado activos
- Conexiones a puertos tipicos de minado

En un entorno de produccion, un analista SOC aplicaria estas mismas
verificaciones como parte del flujo de respuesta a incidentes.

Uso:
    python defensa.py              Ejecutar deteccion completa
    python defensa.py --clean      Eliminar artefactos detectados
    python defensa.py --help       Mostrar ayuda
"""
import os
import sys
import re
import argparse
import glob

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from modulos.common.utils import log, safe_print, color, banner, traverse_lab_files
from modulos.common.utils import hash_file, read_file, cleanup, write_log, is_lab_ready, find_lab_dir

MODULO_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.join(MODULO_DIR, '..', '..')

# Directorio donde la simulacion genera artefactos
DIR_SIMULACION = find_lab_dir(ROOT_DIR)

# Patrones que indican codigo de minado inyectado (en .py)
# Un analista SOC buscaria estos patrones en scripts sospechosos
PATRONES_MINADO = [
    r'import\s+hashlib\s+as\s+_h.*import\s+random\s+as\s+_r',
    r'def\s+_mine\(\)',
    r'_h\.sha256\(d\)\.hexdigest',
    r'Thread\(target=_mine.*daemon=True\)',
]

# Patrones de configuracion de minero en archivos JSON
PATRONES_CONFIG = [
    r'"pool":\s*"pool-ejemplo',
    r'"wallet":\s*"monero:',
    r'"algorithm":\s*"randomx"',
]

# Puertos tipicos de pools de minado conocidos
# Un firewall o IDS monitorearia estas conexiones
PUERTOS_MINADO = {3333, 4444, 5555, 7777, 8888, 9999, 14444, 45560}

# Nombres de procesos de minero conocidos (como los veria un EDR)
MINEROS_CONOCIDOS = [
    'xmrig', 'xmr-stak', 'minerd', 'cpuminer', 'ethminer',
    'ccminer', 'cgminer', 'bfgminer', 'minergate',
]


def detectar_directorio_pruebas():
    """Verifica si existe el directorio de prueba con artefactos."""
    if not os.path.isdir(DIR_SIMULACION):
        return False, []
    archivos = [f for f in os.listdir(DIR_SIMULACION) if os.path.isfile(os.path.join(DIR_SIMULACION, f))]
    return True, archivos


def detectar_cpu_anormal():
    """
    Verifica uso anormal de CPU via /proc/loadavg.
    En produccion, un SOC monitorearia esto con herramientas como:
    - top/htop en Linux
    - Performance Monitor en Windows
    - Prometheus + Grafana para alertas
    """
    try:
        with open('/proc/loadavg', 'r') as f:
            load = float(f.read().split()[0])
        cores = os.cpu_count() or 1
        porcentaje = (load / cores) * 100
        return porcentaje > 80.0, porcentaje
    except Exception:
        return False, 0.0


def detectar_archivos_config():
    """Busca archivos de configuracion de minero en directorio_pruebas/."""
    encontrados = []
    if not os.path.isdir(DIR_SIMULACION):
        return encontrados

    for nombre in os.listdir(DIR_SIMULACION):
        ruta = os.path.join(DIR_SIMULACION, nombre)
        if not os.path.isfile(ruta):
            continue
        # Verificar archivos JSON de configuracion
        if nombre.endswith('.json') and 'miner' in nombre.lower():
            with open(ruta, 'r', errors='ignore') as f:
                contenido = f.read()
            coincide = any(re.search(p, contenido) for p in PATRONES_CONFIG)
            if coincide:
                encontrados.append(ruta)
        # Verificar logs de estadisticas
        elif nombre.endswith('.log') and 'miner' in nombre.lower():
            with open(ruta, 'r', errors='ignore') as f:
                contenido = f.read(512)
            if 'hashrate' in contenido.lower() or 'hashes' in contenido.lower():
                encontrados.append(ruta)

    return encontrados


def detectar_codigo_inyectado():
    """
    Verifica si hay scripts con codigo de minado inyectado.
    En produccion, un EDR detectaria patrones como:
    - Hilos en background calculando hashes
    - Importaciones inusuales (hashlib + threading + random)
    - Consumo de CPU persistente sin actividad de usuario
    """
    hallazgos = []
    if not os.path.isdir(DIR_SIMULACION):
        return hallazgos

    for nombre in os.listdir(DIR_SIMULACION):
        if not nombre.endswith('.py'):
            continue
        ruta = os.path.join(DIR_SIMULACION, nombre)
        with open(ruta, 'r', errors='ignore') as f:
            contenido = f.read()

        lineas_sospechosas = []
        for i, linea in enumerate(contenido.split('\n'), 1):
            for patron in PATRONES_MINADO:
                if re.search(patron, linea):
                    lineas_sospechosas.append((i, linea.strip()))
                    break

        if lineas_sospechosas:
            hallazgos.append({
                'archivo': ruta,
                'lineas': lineas_sospechosas,
            })

    return hallazgos


def detectar_procesos_sospechosos():
    """
    Busca procesos con nombres tipicos de minero en Linux.
    En produccion, un EDR monitorearia la creacion de procesos
    y alertaria sobre nombres inusuales.
    """
    procesos_encontrados = []
    try:
        for pid_dir in glob.glob('/proc/[0-9]*'):
            try:
                with open(os.path.join(pid_dir, 'comm'), 'r') as f:
                    comm = f.read().strip().lower()
                if comm in MINEROS_CONOCIDOS:
                    procesos_encontrados.append((pid_dir.split('/')[-1], comm))
            except (PermissionError, FileNotFoundError):
                continue
    except Exception:
        pass
    return procesos_encontrados


def detectar_conexiones_sospechosas():
    """
    Verifica conexiones de red a puertos tipicos de minado.
    En produccion, un IDS/IPS como Snort o Suricata monitorearia
    estas conexiones y generaria alertas.
    """
    conexiones = []
    try:
        with open('/proc/net/tcp', 'r') as f:
            for linea in f:
                partes = linea.strip().split()
                if len(partes) < 3:
                    continue
                puerto_hex = partes[1].split(':')[-1]
                try:
                    puerto = int(puerto_hex, 16)
                    if puerto in PUERTOS_MINADO:
                        conexiones.append(puerto)
                except ValueError:
                    continue
    except Exception:
        pass
    return list(set(conexiones))


def ejecutar_deteccion():
    """Ejecuta todas las verificaciones de deteccion."""
    banner("DEFENSA CRYPTOJACKING -- DETECCION", "Buscando artefactos de minero")

    hallazgos = []

    # 0. Verificar directorio de prueba
    safe_print(color("--- Verificacion 0: Directorio de prueba ---", 'cyan'))
    existe, archivos = detectar_directorio_pruebas()
    if existe:
        safe_print(f"  {color('!', 'yellow')} directorio_pruebas/ encontrado: {len(archivos)} archivos")
        log(f"directorio_pruebas/ encontrado: {len(archivos)} archivos")
    else:
        safe_print(f"  {color('[OK]', 'green')} directorio_pruebas/ no existe")
        log("directorio_pruebas/ no encontrado")

    # 1. CPU anormal
    safe_print(color("\n--- Verificacion 1: Uso de CPU ---", 'cyan'))
    cpu_anormal, cpu_pct = detectar_cpu_anormal()
    if cpu_anormal:
        safe_print(f"  {color('!', 'red')} CPU anormal detectada: {cpu_pct:.1f}%")
        log(f"CPU anormal: {cpu_pct:.1f}%")
        hallazgos.append(f"CPU anormal: {cpu_pct:.1f}%")
    else:
        safe_print(f"  {color('[OK]', 'green')} CPU normal: {cpu_pct:.1f}%")
        log(f"CPU normal: {cpu_pct:.1f}%")

    # 2. Archivos de configuracion de minero
    safe_print(color("\n--- Verificacion 2: Archivos de configuracion ---", 'cyan'))
    archivos_minero = detectar_archivos_config()
    if archivos_minero:
        safe_print(f"  {color('!', 'red')} {len(archivos_minero)} archivo(s) de minero encontrado(s):")
        for ruta in archivos_minero:
            safe_print(f"    - {ruta}")
            log(f"Archivo de minero encontrado: {ruta}")
        hallazgos.extend(archivos_minero)
    else:
        safe_print(f"  {color('[OK]', 'green')} No se encontraron archivos de configuracion de minero")

    # 3. Codigo inyectado
    safe_print(color("\n--- Verificacion 3: Codigo inyectado ---", 'cyan'))
    inyectados = detectar_codigo_inyectado()
    if inyectados:
        for item in inyectados:
            safe_print(f"  {color('!', 'red')} Codigo de minado en {item['archivo']}:")
            for num, linea in item['lineas']:
                safe_print(f"    Linea {num}: {color(linea[:60], 'yellow')}")
            log(f"Codigo inyectado en {item['archivo']}: {len(item['lineas'])} lineas")
        hallazgos.append(f"Scripts inyectados: {len(inyectados)}")
    else:
        safe_print(f"  {color('[OK]', 'green')} No se detecto codigo de minado inyectado")

    # 4. Procesos sospechosos
    safe_print(color("\n--- Verificacion 4: Procesos activos ---", 'cyan'))
    procesos = detectar_procesos_sospechosos()
    if procesos:
        safe_print(f"  {color('!', 'red')} Procesos de minado detectados:")
        for pid, nombre in procesos:
            safe_print(f"    PID {pid}: {color(nombre, 'red')}")
        log(f"Procesos sospechosos: {procesos}")
        hallazgos.append(f"Procesos: {procesos}")
    else:
        safe_print(f"  {color('[OK]', 'green')} No se detectaron procesos de minado activos")

    # 5. Conexiones de red
    safe_print(color("\n--- Verificacion 5: Conexiones de red ---", 'cyan'))
    conexiones = detectar_conexiones_sospechosas()
    if conexiones:
        safe_print(f"  {color('!', 'red')} Conexiones a puertos de minado:")
        for puerto in conexiones:
            safe_print(f"    Puerto {color(str(puerto), 'red')}")
        log(f"Puertos de minado activos: {conexiones}")
        hallazgos.append(f"Puertos: {conexiones}")
    else:
        safe_print(f"  {color('[OK]', 'green')} No se detectaron conexiones a puertos de minado")

    # Resumen
    safe_print(color("\n" + "="*50, 'cyan'))
    if hallazgos:
        safe_print(color(f"  RESULTADO: {len(hallazgos)} hallazgo(s) detectado(s)", 'red'))
        safe_print(color("  Ejecuta con --clean para eliminar artefactos.", 'yellow'))
    else:
        safe_print(color("  RESULTADO: Sistema limpio -- sin artefactos de minero", 'green'))

    log(f"Deteccion completada: {len(hallazgos)} hallazgos")
    return hallazgos


def limpiar_artefactos():
    """
    Elimina todos los artefactos de la simulacion.
    En produccion, esto equivaleria a:
    - Matar procesos de minado
    - Eliminar archivos maliciosos
    - Restaurar configuraciones originales
    - Revocar accesos comprometidos
    """
    banner("DEFENSA CRYPTOJACKING -- LIMPIEZA", "Eliminando artefactos detectados")

    if os.path.isdir(DIR_SIMULACION):
        try:
            import shutil
            shutil.rmtree(DIR_SIMULACION)
            safe_print(color(f"  [OK] Eliminado: {DIR_SIMULACION}/ (entero)", 'green'))
            log(f"Directorio eliminado: {DIR_SIMULACION}")
        except Exception as e:
            safe_print(color(f"  [ERROR] {e}", 'red'))
    else:
        safe_print(color("  directorio_pruebas/ no existe, nada que limpiar.", 'yellow'))

    safe_print(color("\n  Limpieza completada.", 'green'))


def mostrar_ayuda():
    """Muestra informacion de ayuda."""
    banner("DEFENSA CRYPTOJACKING -- AYUDA", "Deteccion y limpieza de cryptojacking")

    safe_print("""
  Uso:
    python defensa.py [OPCIONES]

  Opciones:
    --clean     Elimina directorio_pruebas/ y todos los artefactos
    --help      Muestra esta ayuda

  Descripcion:
    Detecta y elimina artefactos generados por la simulacion de
    cryptojacking (modulo 12). Realiza 6 verificaciones:
    0. Existencia de directorio_pruebas/
    1. Uso de CPU anormal via /proc/loadavg
    2. Archivos de configuracion de minero (JSON, logs)
    3. Codigo de minado inyectado en scripts Python
    4. Procesos de minado activos en el sistema
    5. Conexiones a puertos tipicos de minado

  Patrones detectados:
    - Configuracion: pool-ejemplo, wallet monero:, algorithm randomx
    - Codigo: hashlib as _h, random as _r, def _mine()
    - Puertos: 3333, 4444, 5555, 7777, 8888, 9999
    - Procesos: xmrig, xmr-stak, minerd, cpuminer
""")


def main():
    parser = argparse.ArgumentParser(
        description='Defensa contra cryptojacking',
        add_help=False
    )
    parser.add_argument('--clean', action='store_true',
                        help='Eliminar artefactos detectados')
    parser.add_argument('--help', action='store_true',
                        help='Mostrar ayuda')

    args = parser.parse_args()

    if args.help:
        mostrar_ayuda()
        return

    if args.clean:
        limpiar_artefactos()
        return

    ejecutar_deteccion()


if __name__ == "__main__":
    main()
