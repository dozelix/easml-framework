#!/usr/bin/env python3
"""
Modulo 13: Defensa contra Supply Chain Attacks — Deteccion y Limpieza

Detecta artefactos generados por la simulacion de supply chain attack en
./directorio_pruebas/:
- Dependencias inyectadas en requirements.txt
- Dependencias sospechosas en package.json
- Lockfiles con paquetes comprometidos
- Scripts de hook de instalacion sospechosos
- SBOM falso con metadatos de ataque
- Verificacion de integridad de archivos criticos

En un entorno de produccion, estas verificaciones se realizarian con:
- npm audit / pip audit para vulnerabilidades conocidas
- SBOM para inventariar dependencias
- Lockfiles para fijar versiones exactas
- Herramientas SCA (Software Composition Analysis)

Uso:
    python defensa.py              Ejecutar deteccion completa
    python defensa.py --clean      Eliminar artefactos detectados
    python defensa.py --help       Mostrar ayuda
"""
import os
import sys
import re
import json
import argparse

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from core.common import log, safe_print, color, banner, traverse_lab_files
from core.common import hash_file, read_file, cleanup, write_log, is_lab_ready

MODULO_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.join(MODULO_DIR, '..', '..')

# Directorio donde la simulacion genera artefactos
DIR_SIMULACION = os.path.join(os.getcwd(), 'directorio_pruebas')

# Paquetes maliciosos conocidos de la simulacion
# En produccion, estas listas vendrian de feeds de inteligencia de amenazas
PAQUETES_MALICIOSOS_PYTHON = [
    'flask-utils', 'flask_utilz', 'enterprise-tool',
    'requests-oauthlib', 'requests_oauthlib2',
]

PAQUETES_MALICIOSOS_NODE = [
    'event-stream', 'ua-parser-js', 'internal-logger',
    'flatmap-stream', 'lod-ash', 'ax1os',
]

# Patrones de deteccion en codigo fuente
PATRONES_SOSPECHOSOS = [
    r'--- DEPENDENCIAS INYECTADAS',
    r'# --- PAQUETES SOSPECHOSOS',
    r'\bexec\s*\(',
    r'\bsubprocess\.call\b',
    r'os\.system\s*\(',
]

# Patrones de versiones anormales
PATRONES_VERSION_ANORMAL = [
    r'==[\d.]+-\w+$',    # sufijo como -mal, -dev
    r'==0\.\d+\.\d+',    # version muy baja para paquete popular
]


def detectar_directorio_pruebas():
    """Verifica si existe el directorio de prueba."""
    if not os.path.isdir(DIR_SIMULACION):
        return False, []
    archivos = [f for f in os.listdir(DIR_SIMULACION) if os.path.isfile(os.path.join(DIR_SIMULACION, f))]
    return True, archivos


def detectar_dependencias_requirements():
    """
    Analiza requirements.txt en busca de dependencias sospechosas.
    En produccion, esto se haria con:
    - pip-audit para buscar vulnerabilidades conocidas
    - Snyk o Dependabot para escaneo continuo
    - Verificacion de hashes contra PyPI
    """
    hallazgos = []
    req_path = os.path.join(DIR_SIMULACION, 'requirements.txt')

    if not os.path.exists(req_path):
        return hallazgos

    with open(req_path, 'r') as f:
        contenido = f.read()

    lineas = contenido.split('\n')
    for i, linea in enumerate(lineas, 1):
        linea_limpia = linea.strip()

        if not linea_limpia or linea_limpia.startswith('#'):
            continue

        # Verificar paquetes conocidos como maliciosos
        for paq in PAQUETES_MALICIOSOS_PYTHON:
            if paq in linea_limpia.lower():
                hallazgos.append({
                    'archivo': req_path,
                    'linea': i,
                    'contenido': linea_limpia,
                    'razon': f'Paquete sospechoso conocido: {paq}',
                    'severidad': 'ALTA',
                })

        # Verificar versiones anormales
        for patron in PATRONES_VERSION_ANORMAL:
            if re.search(patron, linea_limpia):
                hallazgos.append({
                    'archivo': req_path,
                    'linea': i,
                    'contenido': linea_limpia,
                    'razon': 'Version con patron anormal',
                    'severidad': 'MEDIA',
                })

    return hallazgos


def detectar_dependencias_package_json():
    """
    Analiza package.json en busca de dependencias sospechosas.
    En produccion, npm audit detectaria paquetes con vulnerabilidades.
    """
    hallazgos = []
    pkg_path = os.path.join(DIR_SIMULACION, 'package.json')

    if not os.path.exists(pkg_path):
        return hallazgos

    try:
        with open(pkg_path, 'r') as f:
            contenido = json.load(f)
    except json.JSONDecodeError:
        return hallazgos

    deps = contenido.get('dependencies', {})
    for nombre, version in deps.items():
        # Verificar paquetes conocidos como maliciosos
        for paq in PAQUETES_MALICIOSOS_NODE:
            if paq in nombre.lower():
                hallazgos.append({
                    'archivo': pkg_path,
                    'linea': 0,
                    'contenido': f'{nombre}: {version}',
                    'razon': f'Paquete sospechoso conocido: {paq}',
                    'severidad': 'ALTA',
                })

        # Verificar versiones con sufijos maliciosos
        if isinstance(version, str) and ('mal' in version.lower() or 'hack' in version.lower()):
            hallazgos.append({
                'archivo': pkg_path,
                'linea': 0,
                'contenido': f'{nombre}: {version}',
                'razon': 'Version contiene sufijo malicioso',
                'severidad': 'CRITICA',
            })

    return hallazgos


def detectar_lockfile_sospechoso():
    """
    Analiza package-lock.json en busca de paquetes sospechosos.
    El lockfile es critico porque fija versiones exactas — si esta
    comprometido, todas las instalaciones futuras seran maliciosas.
    """
    hallazgos = []
    lock_path = os.path.join(DIR_SIMULACION, 'package-lock.json')

    if not os.path.exists(lock_path):
        return hallazgos

    try:
        with open(lock_path, 'r') as f:
            contenido = json.load(f)
    except json.JSONDecodeError:
        return hallazgos

    packages = contenido.get('packages', {})
    for ruta, info in packages.items():
        nombre = ruta.split('/')[-1] if '/' in ruta else ruta

        for paq in PAQUETES_MALICIOSOS_NODE:
            if paq in nombre.lower():
                hallazgos.append({
                    'archivo': lock_path,
                    'linea': 0,
                    'contenido': f'{nombre}: {info.get("version", "?")}',
                    'razon': f'Paquete sospechoso en lockfile: {paq}',
                    'severidad': 'ALTA',
                })

    return hallazgos


def detectar_scripts_sospechosos():
    """
    Busca scripts de hook de instalacion sospechosos.
    Los scripts post-install son un vector comun de supply chain attacks.
    En npm, se ejecutan automaticamente durante 'npm install'.
    """
    hallazgos = []

    scripts_sospechosos = ['install_hook.py', 'post_install.py', 'pre_install.py']

    for script in scripts_sospechosos:
        ruta = os.path.join(DIR_SIMULACION, script)
        if not os.path.exists(ruta):
            continue

        with open(ruta, 'r') as f:
            contenido = f.read()

        hallazgos.append({
            'archivo': ruta,
            'linea': 1,
            'contenido': script,
            'razon': 'Script de hook de instalacion encontrado',
            'severidad': 'MEDIA',
        })

        # Verificar si contiene patrones sospechosos
        for patron in PATRONES_SOSPECHOSOS:
            if re.search(patron, contenido):
                hallazgos.append({
                    'archivo': ruta,
                    'linea': 0,
                    'contenido': patron,
                    'razon': f'Patron sospechoso detectado: {patron}',
                    'severidad': 'ALTA',
                })

    return hallazgos


def detectar_sbom_falso():
    """
    Verifica si hay un SBOM falso con metadatos de tipo de ataque.
    En produccion, el SBOM real ayudaria a identificar dependencias
    comprometidas y rastrear la cadena de suministro.
    """
    sbom_path = os.path.join(DIR_SIMULACION, 'sbom', 'sbom.json')

    if not os.path.exists(sbom_path):
        return []

    try:
        with open(sbom_path, 'r') as f:
            contenido = json.load(f)
    except json.JSONDecodeError:
        return [{'archivo': sbom_path, 'linea': 0,
                'contenido': 'SBOM corrupto', 'razon': 'SBOM falso encontrado',
                'severidad': 'BAJA'}]

    hallazgos = []
    components = contenido.get('components', [])
    for comp in components:
        props = comp.get('properties', [])
        for prop in props:
            if prop.get('name') == 'attack_type':
                hallazgos.append({
                    'archivo': sbom_path,
                    'linea': 0,
                    'contenido': f'{comp["name"]}: {comp.get("version", "?")}',
                    'razon': f'SBOM contiene paquete con tipo de ataque: {prop["value"]}',
                    'severidad': 'ALTA',
                })

    return hallazgos


def detectar_integridad_archivos():
    """
    Verifica la integridad de archivos criticos del proyecto.
    En produccion, se usaria:
    - Hashes SHA-256 pre-calculados
    - GPG signatures para paquetes
    - Herramientas como sigstore para verificacion de supply chain
    """
    hallazgos = []

    # Verificar script.py si existe en directorio_pruebas/
    script_path = os.path.join(DIR_SIMULACION, 'script.py')
    if os.path.exists(script_path):
        with open(script_path, 'r') as f:
            contenido = f.read()

        patrones_infeccion = [
            r'import\s+hashlib\s+as\s+_h',
            r'def\s+_mine\(\)',
            r'Thread\(target=_mine',
        ]

        for patron in patrones_infeccion:
            if re.search(patron, contenido):
                hallazgos.append({
                    'archivo': script_path,
                    'linea': 0,
                    'contenido': patron,
                    'razon': 'Codigo de minado detectado en archivo',
                    'severidad': 'CRITICA',
                })

    return hallazgos


def ejecutar_deteccion():
    """Ejecuta todas las verificaciones de supply chain."""
    banner("DEFENSA SUPPLY CHAIN -- DETECCION", "Analizando artefactos de supply chain attack")

    total_hallazgos = []

    # 0. Verificar directorio de prueba
    safe_print(color("--- Verificacion 0: Directorio de prueba ---", 'cyan'))
    existe, archivos = detectar_directorio_pruebas()
    if existe:
        safe_print(f"  {color('!', 'yellow')} directorio_pruebas/ encontrado: {len(archivos)} archivos")
    else:
        safe_print(f"  {color('[OK]', 'green')} directorio_pruebas/ no existe")

    # 1. Requirements.txt
    safe_print(color("\n--- Verificacion 1: requirements.txt ---", 'cyan'))
    h1 = detectar_dependencias_requirements()
    if h1:
        safe_print(f"  {color('!', 'red')} {len(h1)} hallazgo(s) encontrado(s):")
        for h in h1:
            safe_print(f"    [{color(h['severidad'], 'red')}] Linea {h['linea']}: {h['contenido']}")
            safe_print(f"      Razon: {h['razon']}")
        total_hallazgos.extend(h1)
    else:
        safe_print(f"  {color('[OK]', 'green')} requirements.txt limpio")

    # 2. package.json
    safe_print(color("\n--- Verificacion 2: package.json ---", 'cyan'))
    h2 = detectar_dependencias_package_json()
    if h2:
        safe_print(f"  {color('!', 'red')} {len(h2)} hallazgo(s) encontrado(s):")
        for h in h2:
            safe_print(f"    [{color(h['severidad'], 'red')}] {h['contenido']}")
            safe_print(f"      Razon: {h['razon']}")
        total_hallazgos.extend(h2)
    else:
        safe_print(f"  {color('[OK]', 'green')} package.json limpio")

    # 3. Lockfile
    safe_print(color("\n--- Verificacion 3: package-lock.json ---", 'cyan'))
    h3 = detectar_lockfile_sospechoso()
    if h3:
        safe_print(f"  {color('!', 'red')} {len(h3)} hallazgo(s) encontrado(s):")
        for h in h3:
            safe_print(f"    [{color(h['severidad'], 'red')}] {h['contenido']}")
            safe_print(f"      Razon: {h['razon']}")
        total_hallazgos.extend(h3)
    else:
        safe_print(f"  {color('[OK]', 'green')} package-lock.json limpio")

    # 4. Scripts
    safe_print(color("\n--- Verificacion 4: Scripts de hook ---", 'cyan'))
    h4 = detectar_scripts_sospechosos()
    if h4:
        safe_print(f"  {color('!', 'red')} {len(h4)} hallazgo(s) encontrado(s):")
        for h in h4:
            safe_print(f"    [{color(h['severidad'], 'red')}] {h['contenido']}")
            safe_print(f"      Razon: {h['razon']}")
        total_hallazgos.extend(h4)
    else:
        safe_print(f"  {color('[OK]', 'green')} No se encontraron scripts de hook sospechosos")

    # 5. SBOM
    safe_print(color("\n--- Verificacion 5: SBOM ---", 'cyan'))
    h5 = detectar_sbom_falso()
    if h5:
        safe_print(f"  {color('!', 'red')} {len(h5)} hallazgo(s) en SBOM:")
        for h in h5:
            safe_print(f"    [{color(h['severidad'], 'red')}] {h['contenido']}")
            safe_print(f"      Razon: {h['razon']}")
        total_hallazgos.extend(h5)
    else:
        safe_print(f"  {color('[OK]', 'green')} SBOM no encontrado o limpio")

    # 6. Integridad
    safe_print(color("\n--- Verificacion 6: Integridad de archivos ---", 'cyan'))
    h6 = detectar_integridad_archivos()
    if h6:
        safe_print(f"  {color('!', 'red')} {len(h6)} hallazgo(s) de integridad:")
        for h in h6:
            safe_print(f"    [{color(h['severidad'], 'red')}] {h['archivo']}")
            safe_print(f"      Razon: {h['razon']}")
        total_hallazgos.extend(h6)
    else:
        safe_print(f"  {color('[OK]', 'green')} Integridad de archivos verificada")

    # Resumen
    safe_print(color("\n" + "="*50, 'cyan'))
    if total_hallazgos:
        severidades = {}
        for h in total_hallazgos:
            s = h['severidad']
            severidades[s] = severidades.get(s, 0) + 1

        safe_print(color(f"  RESULTADO: {len(total_hallazgos)} hallazgo(s) detectado(s)", 'red'))
        for s, c in severidades.items():
            safe_print(f"    {s}: {c}")
        safe_print(color("  Ejecuta con --clean para eliminar artefactos.", 'yellow'))
    else:
        safe_print(color("  RESULTADO: Sin artefactos de supply chain attack detectados", 'green'))

    log(f"Deteccion completada: {len(total_hallazgos)} hallazgos")
    return total_hallazgos


def limpiar_artefactos():
    """
    Elimina todos los artefactos de supply chain attack.
    En produccion, esto equivaleria a:
    - Revertir dependencias comprometidas
    - Regenerar lockfiles con versiones seguras
    - Eliminar scripts de hook maliciosos
    - Notificar al equipo de desarrollo
    """
    banner("DEFENSA SUPPLY CHAIN -- LIMPIEZA", "Eliminando artefactos detectados")

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
    banner("DEFENSA SUPPLY CHAIN -- AYUDA", "Deteccion y limpieza de supply chain attacks")

    safe_print("""
  Uso:
    python defensa.py [OPCIONES]

  Opciones:
    --clean     Elimina directorio_pruebas/ y todos los artefactos
    --help      Muestra esta ayuda

  Descripcion:
    Detecta y elimina artefactos generados por la simulacion de
    supply chain attack (modulo 13). Realiza 7 verificaciones:
    0. Existencia de directorio_pruebas/
    1. Dependencias en requirements.txt
    2. Dependencias en package.json
    3. Paquetes en package-lock.json
    4. Scripts de hook de instalacion
    5. SBOM con metadatos de ataque
    6. Integridad de archivos criticos

  Paquetes detectados:
    Python: flask-utils, enterprise-tool, requests-oauthlib
    Node: event-stream, ua-parser-js, internal-logger

  Severidades:
    CRITICA - Codigo malicioso ejecutable encontrado
    ALTA    - Dependencia maliciosa confirmada
    MEDIA   - Patron sospechoso detectado
    BAJA    - Artefacto inofensivo encontrado
""")


def main():
    parser = argparse.ArgumentParser(
        description='Defensa contra supply chain attacks',
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
