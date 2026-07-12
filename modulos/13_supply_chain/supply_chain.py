#!/usr/bin/env python3
"""
Modulo 13: Simulacion de Supply Chain Attack

Simula un ataque a la cadena de suministro de software:
- Inyecta dependencias falsas en requirements.txt y package.json
- Muestra como los atacantes comprometen dependencias
- Demuestra typosquatting, dependency confusion y account takeover
- NO instala paquetes reales ni ejecuta codigo malicioso
- Opera exclusivamente dentro de ./directorio_pruebas/

Uso:
    python supply_chain.py              Ejecutar simulacion
    python supply_chain.py --clean      Eliminar artefactos generados
    python supply_chain.py --help       Mostrar ayuda
    python supply_chain.py --tipo X     Tipo de ataque (typosquat|confusion|takeover)
"""
import os
import sys
import re
import json
import time
import random
import hashlib
import argparse
import shutil

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from core.common import log, safe_print, color, banner, traverse_lab_files
from core.common import hash_file, read_file, cleanup, write_log, is_lab_ready

MODULO_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.join(MODULO_DIR, '..', '..')

# Directorio de trabajo confinado
DIR_SIMULACION = os.path.join(os.getcwd(), 'directorio_pruebas')

# Dependencias ficticias del proyecto (legitimas)
DEPS_PYTHON = {
    'flask': '2.3.2',
    'requests': '2.31.0',
    'sqlalchemy': '2.0.19',
    'numpy': '1.24.3',
    'pandas': '2.0.3',
    'pillow': '10.0.0',
}

DEPS_NODE = {
    'express': '4.18.2',
    'lodash': '4.17.21',
    'axios': '1.4.0',
    'react': '18.2.0',
    'webpack': '5.88.2',
    'eslint': '8.45.0',
}

# Dependencias maliciosas simuladas
DEPS_MALICIOSAS_PYTHON = [
    {
        'nombre': 'flask-utils',
        'version': '1.0.0',
        'tipo': 'typosquatting',
        'simula': 'flask_utilz',
        'descripcion': 'Paquete con nombre similar a "flask" (typosquatting)',
    },
    {
        'nombre': 'enterprise-tool',
        'version': '2.1.0',
        'tipo': 'dependency_confusion',
        'simula': 'acme-corp-tool',
        'descripcion': 'Nombre igual a paquete interno ficticio (dependency confusion)',
    },
    {
        'nombre': 'requests-oauthlib',
        'version': '0.99',
        'tipo': 'typosquatting',
        'simula': 'requests_oauthlib2',
        'descripcion': 'Version falsa con version inusual (account takeover)',
    },
]

DEPS_MALICIOSAS_NODE = [
    {
        'nombre': 'event-stream',
        'version': '4.0.1-mal',
        'tipo': 'typosquatting',
        'simula': 'flatmap-stream',
        'descripcion': 'Compromiso de maintainer (similar a incidente real)',
    },
    {
        'nombre': 'ua-parser-js',
        'version': '0.7.29',
        'tipo': 'typosquatting',
        'simula': 'ua-parser-js',
        'descripcion': 'Version comprometida del paquete real',
    },
    {
        'nombre': 'internal-logger',
        'version': '1.0.0',
        'tipo': 'dependency_confusion',
        'simula': 'internal-logger',
        'descripcion': 'Paquete interno publicado accidentalmente en registry publico',
    },
]


def preparar_directorio():
    """Crea directorio_pruebas/ y copia archivos de prueba del laboratorio."""
    os.makedirs(DIR_SIMULACION, exist_ok=True)
    safe_print(color("  Preparando directorio de trabajo...", 'cyan'))

    archivos_lab = [
        'documento.txt', 'notas.txt', 'script.py', 'index.html',
        'datos.csv', 'leeme.md', 'imagen.png', 'imagen.jpg',
        'audio.mp3', 'documento.docx', 'planilla.xlsx', 'presentacion.pptx',
    ]

    copiados = 0
    for nombre in archivos_lab:
        origen = os.path.join(ROOT_DIR, nombre)
        destino = os.path.join(DIR_SIMULACION, nombre)
        if os.path.exists(origen) and not os.path.exists(destino):
            shutil.copy2(origen, destino)
            copiados += 1

    safe_print(color(f"  Archivos copiados a directorio_pruebas/: {copiados}", 'green'))
    log(f"Directorio preparado: {copiados} archivos copiados")
    return copiados


def generar_requirements_txt(deps_normales, deps_maliciosas):
    """Genera un archivo requirements.txt con dependencias normales y maliciosas."""
    lineas = ["# Dependencias del proyecto -- generado por simulacion\n\n"]

    for nombre, version in sorted(deps_normales.items()):
        lineas.append(f"{nombre}=={version}\n")

    if deps_maliciosas:
        lineas.append("\n# --- PAQUETES INYECTADOS (simulacion) ---\n")
        for dep in deps_maliciosas:
            lineas.append(f"{dep['nombre']}=={dep['version']}  # {dep['descripcion']}\n")

    return ''.join(lineas)


def generar_package_json(deps_normales, deps_maliciosas):
    """Genera un package.json con dependencias normales y maliciosas."""
    deps = {}
    for nombre, version in deps_normales.items():
        deps[nombre] = f"^{version}"

    if deps_maliciosas:
        for dep in deps_maliciosas:
            deps[dep['nombre']] = dep['version']

    contenido = {
        "name": "proyecto-ejemplo",
        "version": "1.0.0",
        "description": "Proyecto de ejemplo para simulacion de supply chain attack",
        "main": "index.js",
        "dependencies": deps,
        "devDependencies": {
            "typescript": "^5.1.6",
            "jest": "^29.6.1"
        }
    }

    return json.dumps(contenido, indent=2) + '\n'


def generar_lockfile(deps_normales, deps_maliciosas):
    """Genera un lockfile simplificado."""
    lock = {
        "lockfileVersion": 3,
        "packages": {}
    }

    for nombre, version in deps_normales.items():
        lock["packages"][f"node_modules/{nombre}"] = {
            "version": version,
            "resolved": f"https://registry.npmjs.org/{nombre}/-/{nombre}-{version}.tgz",
            "integrity": f"sha512-{hashlib.sha256(nombre.encode()).hexdigest()[:40]}="
        }

    if deps_maliciosas:
        for dep in deps_maliciosas:
            lock["packages"][f"node_modules/{dep['nombre']}"] = {
                "version": dep['version'],
                "resolved": f"https://registry.npmjs.org/{dep['nombre']}/-/{dep['nombre']}-{dep['version']}.tgz",
                "integrity": f"sha512-{hashlib.sha256(dep['nombre'].encode()).hexdigest()[:40]}="
            }

    return json.dumps(lock, indent=2) + '\n'


def simular_typosquatting():
    """Simula un ataque de typosquatting — paquetes con nombres similares."""
    safe_print(color("\n--- Ataque: Typosquatting ---", 'cyan'))
    safe_print(color("  El atacante publica paquetes con nombres similares a los populares.", 'yellow'))
    log("Simulando ataque de typosquatting")

    ejemplos = [
        ('flask', 'flask-utils', 'flask_utilz', 'Guion bajo en vez de guion'),
        ('lodash', 'lod-ash', 'lod-ash', 'Abrevia el nombre'),
        ('requests', 'requests-oauthlib', 'requests_oauthlib2', 'Sufijo numerico'),
        ('axios', 'ax1os', 'ax1os', 'Sustituye i por 1'),
    ]

    safe_print(f"\n  {'Original':<15} {'Malicioso':<20} {'Simula':<20} {'Tecnica'}")
    safe_print(f"  {'-'*15} {'-'*20} {'-'*20} {'-'*30}")
    for orig, mal, sim, tech in ejemplos:
        safe_print(f"  {color(orig, 'green'):<15} {color(mal, 'red'):<20} {sim:<20} {tech}")

    safe_print(color("\n  El atacante espera que el usuario escriba mal el nombre.", 'yellow'))
    log(f"Ejemplos de typosquatting mostrados: {len(ejemplos)}")


def simular_dependency_confusion():
    """Simula un ataque de dependency confusion — paquetes internos en registry publico."""
    safe_print(color("\n--- Ataque: Dependency Confusion ---", 'cyan'))
    safe_print(color("  Paquete interno publicado en registry publico con version mas alta.", 'yellow'))
    log("Simulando ataque de dependency confusion")

    internos = [
        ('acme-internal-tool', '3.0.0', 'Herramienta interna de Acme Corp'),
        ('corp-logger', '1.2.1', 'Sistema de logging corporativo'),
        ('enterprise-auth', '2.0.0', 'Modulo de autenticacion interno'),
    ]

    safe_print(f"\n  {'Paquete interno':<25} {'Version':<10} {'Descripcion'}")
    safe_print(f"  {'-'*25} {'-'*10} {'-'*35}")
    for nombre, ver, desc in internos:
        safe_print(f"  {color(nombre, 'yellow'):<25} {ver:<10} {desc}")

    safe_print(color("\n  El atacante publica versiones mas altas en el registry publico:", 'yellow'))
    for nombre, ver, _ in internos:
        nueva_ver = int(ver.split('.')[0]) + 1
        safe_print(f"    {color(f'publica: {nombre}=={nueva_ver}.0.0', 'red')}")

    safe_print(color("\n  El instalador prefiere la version publica sobre la interna.", 'yellow'))
    log("Dependency confusion demostrada")


def simular_account_takeover():
    """Simula un ataque de account takeover de maintainer."""
    safe_print(color("\n--- Ataque: Account Takeover ---", 'cyan'))
    safe_print(color("  El atacante compromete la cuenta del maintainer de un paquete popular.", 'yellow'))
    log("Simulando ataque de account takeover")

    timeline = [
        ("00:00", "Atacante compromete cuenta del maintainer via phishing"),
        ("00:15", "Atacante obtiene acceso al repositorio del paquete"),
        ("01:00", "Publica nueva version con codigo malicioso"),
        ("01:30", "Los usuarios automaticos descargan la actualizacion"),
        ("02:00", "El codigo malicioso comienza a ejecutarse"),
        ("24:00", "Comunidad detecta comportamiento anomalo"),
        ("48:00", "Paquete removido del registry, investigacion abierta"),
    ]

    safe_print(f"\n  {'Tiempo':<10} {'Evento'}")
    safe_print(f"  {'-'*10} {'-'*55}")
    for tiempo, evento in timeline:
        safe_print(f"  {color(tiempo, 'cyan'):<10} {evento}")

    log(f"Timeline de account takeover mostrada: {len(timeline)} eventos")


def simular_build_compromise():
    """Simula un ataque de compromise del build pipeline (SolarWinds-style)."""
    safe_print(color("\n--- Ataque: Build Pipeline Compromise ---", 'cyan'))
    safe_print(color("  El atacante compromete el servidor de build/CI-CD.", 'yellow'))
    log("Simulando ataque de build compromise")

    pasos = [
        "1. Atacante accede al servidor de build de la empresa",
        "2. Modifica el script de compilacion para inyectar backdoor",
        "3. El backdoor se compila junto con el codigo legitimo",
        "4. La firma digital se aplica al binario comprometido",
        "5. La actualizacion se distribuye via canal oficial",
        "6. Los clientes instalan la actualizacion confiando en la firma",
        "7. El backdoor se activa en el sistema del cliente",
        "8. Datos exfiltrados al servidor C2 del atacante",
    ]

    for paso in pasos:
        safe_print(f"  {color('>', 'yellow')} {paso}")
        log(paso)

    safe_print(color("\n  Este es el vector utilizado en el ataque SolarWinds (2020).", 'red'))
    safe_print(color("  18,000+ organizaciones fueron comprometidas.\n", 'red'))


def simular_ataque(tipo=None):
    """Ejecuta la simulacion completa de supply chain attack."""
    banner("SUPPLY CHAIN ATTACK -- SIMULACION EDUCATIVA",
           "Inyeccion de dependencias en cadena de suministro de software")

    safe_print(color("[EDUCATIVO] Este programa NO instala paquetes reales.", 'yellow'))
    safe_print(color("[EDUCATIVO] NO ejecuta codigo malicioso.\n", 'yellow'))

    # Preparar directorio
    preparar_directorio()

    # Fase 1: Analisis del proyecto
    safe_print(color("\n--- FASE 1: Analisis del proyecto objetivo ---", 'cyan'))
    log("Iniciando analisis del proyecto")

    safe_print(f"  Analizando {color(DIR_SIMULACION, 'green')}...")
    safe_print(f"  Dependencias Python: {color(str(len(DEPS_PYTHON)), 'green')}")
    safe_print(f"  Dependencias Node.js: {color(str(len(DEPS_NODE)), 'green')}")
    log(f"Proyecto analizado: {len(DEPS_PYTHON)} deps Python, {len(DEPS_NODE)} deps Node")

    time.sleep(1)

    # Fase 2: Tipos de ataque
    if tipo == 'typosquat' or tipo is None:
        simular_typosquatting()
    if tipo == 'confusion' or tipo is None:
        simular_dependency_confusion()
    if tipo == 'takeover' or tipo is None:
        simular_account_takeover()
    if tipo is None:
        simular_build_compromise()

    time.sleep(1)

    # Fase 3: Inyeccion de dependencias en directorio_pruebas/
    safe_print(color("\n--- FASE 3: Inyeccion de dependencias maliciosas ---", 'cyan'))

    # requirements.txt
    req_path = os.path.join(DIR_SIMULACION, 'requirements.txt')
    contenido_req = generar_requirements_txt(DEPS_PYTHON, DEPS_MALICIOSAS_PYTHON)
    with open(req_path, 'w') as f:
        f.write(contenido_req)
    safe_print(f"  {color('>', 'yellow')} requirements.txt generado: {req_path}")
    log(f"requirements.txt generado: {req_path}")

    # package.json
    pkg_path = os.path.join(DIR_SIMULACION, 'package.json')
    contenido_pkg = generar_package_json(DEPS_NODE, DEPS_MALICIOSAS_NODE)
    with open(pkg_path, 'w') as f:
        f.write(contenido_pkg)
    safe_print(f"  {color('>', 'yellow')} package.json generado: {pkg_path}")
    log(f"package.json generado: {pkg_path}")

    # package-lock.json
    lock_path = os.path.join(DIR_SIMULACION, 'package-lock.json')
    contenido_lock = generar_lockfile(DEPS_NODE, DEPS_MALICIOSAS_NODE)
    with open(lock_path, 'w') as f:
        f.write(contenido_lock)
    safe_print(f"  {color('>', 'yellow')} package-lock.json generado: {lock_path}")
    log(f"package-lock.json generado: {lock_path}")

    # Script de hook simulado
    hook_path = os.path.join(DIR_SIMULACION, 'install_hook.py')
    hook_contenido = (
        '#!/usr/bin/env python3\n'
        '"""Script de ejemplo -- aparenta ser un hook de instalacion legitimo"""\n'
        '# En un ataque real, este script ejecutaria codigo malicioso\n'
        'import subprocess\n'
        'import os\n\n'
        '# Simulacion: este codigo NO es malicioso\n'
        'def post_install():\n'
        '    print("Ejecutando post-install... (SIMULADO)")\n'
        '    # En un ataque real, aqui iria:\n'
        '    # - Descarga de payload\n'
        '    # - Exfiltracion de datos\n'
        '    # - Instalacion de backdoor\n'
        '    pass\n\n'
        'if __name__ == "__main__":\n'
        '    post_install()\n'
    )
    with open(hook_path, 'w') as f:
        f.write(hook_contenido)
    safe_print(f"  {color('>', 'yellow')} Script de hook: {hook_path}")

    # SBOM falso
    safe_print(color("\n--- FASE 4: Generacion de SBOM ---", 'cyan'))
    sbom_dir = os.path.join(DIR_SIMULACION, 'sbom')
    os.makedirs(sbom_dir, exist_ok=True)

    sbom = {
        "format": "CycloneDX",
        "specVersion": "1.4",
        "components": []
    }

    for nombre, version in {**DEPS_PYTHON, **DEPS_NODE}.items():
        sbom["components"].append({
            "type": "library",
            "name": nombre,
            "version": version,
            "hashes": [{"algorithm": "SHA-256", "value": hashlib.sha256(f"{nombre}{version}".encode()).hexdigest()}]
        })

    for dep in DEPS_MALICIOSAS_PYTHON + DEPS_MALICIOSAS_NODE:
        sbom["components"].append({
            "type": "library",
            "name": dep['nombre'],
            "version": dep['version'],
            "hashes": [{"algorithm": "SHA-256", "value": hashlib.sha256(dep['nombre'].encode()).hexdigest()}],
            "properties": [
                {"name": "attack_type", "value": dep['tipo']},
                {"name": "simulates", "value": dep['simula']}
            ]
        })

    sbom_path = os.path.join(sbom_dir, 'sbom.json')
    with open(sbom_path, 'w') as f:
        json.dump(sbom, f, indent=2)
    safe_print(f"  {color('>', 'yellow')} SBOM generado: {sbom_path}")

    # Fase 5: Resumen
    safe_print(color("\n--- FASE 5: Resumen del ataque ---", 'cyan'))

    safe_print(color("\n  Paquetes maliciosos inyectados:", 'red'))
    safe_print(color("\n  Python:", 'yellow'))
    for dep in DEPS_MALICIOSAS_PYTHON:
        safe_print(f"    {color(dep['nombre'], 'red')}=={dep['version']} "
                   f"({dep['tipo']}: {dep['simula']})")

    safe_print(color("\n  Node.js:", 'yellow'))
    for dep in DEPS_MALICIOSAS_NODE:
        safe_print(f"    {color(dep['nombre'], 'red')}@{dep['version']} "
                   f"({dep['tipo']}: {dep['simula']})")

    safe_print(color("\n  Archivos generados en directorio_pruebas/:", 'green'))
    artefactos = ['requirements.txt', 'package.json', 'package-lock.json',
                  'install_hook.py', 'sbom/sbom.json']
    for artefacto in artefactos:
        ruta = os.path.join(DIR_SIMULACION, artefacto)
        existe = "[OK]" if os.path.exists(ruta) else "[--]"
        safe_print(f"    {existe} {artefacto}")

    safe_print(color("\n  Ejecuta defensa.py para detectar estos artefactos.", 'yellow'))
    safe_print(color("  Ejecuta con --clean para eliminarlos.\n", 'yellow'))

    log("Simulacion de supply chain completada")


def limpiar():
    """Elimina directorio_pruebas/ y todo su contenido."""
    banner("SUPPLY CHAIN ATTACK -- LIMPIEZA", "Eliminando directorio de prueba")

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
    """Muestra informacion de ayuda."""
    banner("SUPPLY CHAIN ATTACK -- AYUDA", "Simulacion de ataque a cadena de suministro")

    safe_print("""
  Uso:
    python supply_chain.py [OPCIONES]

  Opciones:
    --clean         Elimina directorio_pruebas/ y todos los artefactos
    --tipo TIPO     Tipo de ataque a simular:
                      typosquat  - Solo typosquatting
                      confusion  - Solo dependency confusion
                      takeover   - Solo account takeover
                      (default: todos los tipos)
    --help          Muestra esta ayuda

  Descripcion:
    Simula un ataque a la cadena de suministro de software, inyectando
    dependencias maliciosas en archivos de proyecto dentro de
    directorio_pruebas/. Demuestra como los atacantes comprometen
    dependencias para distribuir malware.

  Artefactos generados (en directorio_pruebas/):
    - requirements.txt         Dependencias Python con paquetes maliciosos
    - package.json             Dependencias Node.js con paquetes maliciosos
    - package-lock.json        Lockfile con paquetes comprometidos
    - install_hook.py          Script de hook simulado
    - sbom/sbom.json           Software Bill of Materials falso

  Casos reales simulados:
    - Typosquatting: flask-utils, requests-oauthlib
    - Dependency confusion: enterprise-tool
    - Account takeover: event-stream, ua-parser-js
    - Build compromise: SolarWinds (solo descripcion)
""")


def main():
    parser = argparse.ArgumentParser(
        description='Simulacion de supply chain attack',
        add_help=False
    )
    parser.add_argument('--clean', action='store_true',
                        help='Eliminar directorio_pruebas/ y artefactos')
    parser.add_argument('--help', action='store_true',
                        help='Mostrar ayuda')
    parser.add_argument('--tipo', type=str, default=None,
                        choices=['typosquat', 'confusion', 'takeover'],
                        help='Tipo de ataque a simular')

    args = parser.parse_args()

    if args.help:
        mostrar_ayuda()
        return

    if args.clean:
        limpiar()
        return

    simular_ataque(tipo=args.tipo)


if __name__ == "__main__":
    main()
