#!/usr/bin/env python3
"""
Modulo 14: Defensa contra DNS Tunneling — Deteccion y Limpieza

Detecta artefactos generados por la simulacion de DNS tunneling en
./directorio_pruebas/:
- Logs de trafico DNS simulado
- Scripts payload de tunneling
- Subdominios inusualmente largos en archivos
- Secuencias base32/base64 sospechosas

En un entorno de produccion, estas verificaciones se realizarian con:
- Suricata con reglas de DNS tunneling
- Zeek/Bro para analisis de trafico DNS
- Passive DNS para historial de consultas
- Machine Learning sobre patrones DNS

Uso:
    python defensa.py              Ejecutar deteccion completa
    python defensa.py --clean      Eliminar artefactos detectados
    python defensa.py --help       Mostrar ayuda
"""
import os
import sys
import re
import base64
import argparse
import glob

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from modulos.common.utils import log, safe_print, color, banner, traverse_lab_files
from modulos.common.utils import hash_file, read_file, cleanup, write_log, is_lab_ready, find_lab_dir

MODULO_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.join(MODULO_DIR, '..', '..')

# Directorio donde la simulacion genera artefactos
DIR_SIMULACION = find_lab_dir(ROOT_DIR)

# ── Patrones de deteccion ──────────────────────────────────

# Subdominios con base32 (caracteres A-Z, 2-7, padding =)
# Un IDS como Suricata usaria reglas similares para detectar DNS tunneling
PATRON_BASE32 = re.compile(r'[A-Z2-7]{16,}={0,6}')

# Subdominios con base64 (caracteres A-Z, a-z, 0-9, -, _)
PATRON_BASE64 = re.compile(r'[A-Za-z0-9\-_]{20,}={0,2}')

# Labels DNS largos (>30 chars es sospechoso, normales son 5-15)
PATRON_LABEL_LARGO = re.compile(
    r'([a-zA-Z0-9\-\.]{31,}\.[a-zA-Z0-9\-]+\.[a-zA-Z]{2,})'
)

# Queries DNS con patron de codificacion (d00, d01, d02...)
PATRON_QUERY_TUNNEL = re.compile(
    r'd[0-9]{2}\.'       # Prefijo d00, d01...
    r'[a-z0-9\-]+\.'     # Subdominio
    r'[a-zA-Z0-9\-]+'    # Dominio
)


def detectar_directorio_pruebas():
    """Verifica si existe el directorio de prueba."""
    if not os.path.isdir(DIR_SIMULACION):
        return False, []
    archivos = [f for f in os.listdir(DIR_SIMULACION) if os.path.isfile(os.path.join(DIR_SIMULACION, f))]
    return True, archivos


def detectar_archivos_dns_tunnel():
    """
    Busca archivos generados por la simulacion de DNS tunneling.
    En produccion, un SOC buscaria archivos con patrones de exfiltracion DNS
    en ubicaciones inusuales del sistema.
    """
    hallazgos = []

    # Buscar en directorio_pruebas/
    if not os.path.isdir(DIR_SIMULACION):
        return hallazgos

    for nombre in os.listdir(DIR_SIMULACION):
        ruta = os.path.join(DIR_SIMULACION, nombre)
        if not os.path.isfile(ruta):
            continue

        with open(ruta, 'r', errors='ignore') as f:
            contenido = f.read(1024)

        # Detectar logs de trafico DNS
        if 'evil' in contenido.lower() or 'dns traffic' in contenido.lower():
            hallazgos.append({
                'archivo': ruta,
                'tipo': 'Log de trafico DNS',
                'severidad': 'ALTA',
                'razon': 'Contiene registros de DNS tunneling simulado',
            })

        # Detectar scripts payload
        if nombre.endswith('.py') and ('dns' in contenido.lower() or
                                        'payload' in contenido.lower() or
                                        'codificar_dns' in contenido):
            hallazgos.append({
                'archivo': ruta,
                'tipo': 'Script payload DNS',
                'severidad': 'MEDIA',
                'razon': 'Script de simulacion DNS tunneling',
            })

    return hallazgos


def detectar_dns_log_content():
    """
    Analiza el contenido de archivos DNS en busca de trafico tunneled.
    Un analista SOC buscaria estos patrones en logs de DNS:
    - Labels inusualmente largos
    - Multiples consultas al mismo dominio
    - Presencia de base32/base64 en subdominios
    """
    hallazgos = []

    if not os.path.isdir(DIR_SIMULACION):
        return hallazgos

    for nombre in os.listdir(DIR_SIMULACION):
        ruta = os.path.join(DIR_SIMULACION, nombre)
        if not os.path.isfile(ruta):
            continue

        with open(ruta, 'r', errors='ignore') as f:
            lineas = f.readlines()

        labels_largos = 0
        queries_evil = 0
        base32_detectado = 0

        for linea in lineas:
            # Buscar labels largos (>30 caracteres)
            if PATRON_LABEL_LARGO.search(linea):
                labels_largos += 1

            # Buscar dominios evil/sospechosos
            if 'evil' in linea.lower() or '.mal.' in linea.lower():
                queries_evil += 1

            # Buscar secuencias base32 validas
            for match in re.finditer(r'[A-Z2-7]{16,}', linea):
                texto = match.group()
                try:
                    padding = (8 - len(texto) % 8) % 8
                    base64.b32decode(texto + '=' * padding)
                    base32_detectado += 1
                except Exception:
                    pass

        if labels_largos > 0 or queries_evil > 0 or base32_detectado > 3:
            hallazgos.append({
                'archivo': ruta,
                'tipo': 'Contenido DNS tunnel',
                'severidad': 'ALTA' if base32_detectado > 3 else 'MEDIA',
                'razon': (f'{labels_largos} labels largos, '
                         f'{queries_evil} queries sospechosas, '
                         f'{base32_detectado} base32 detectados'),
            })

    return hallazgos


def detectar_script_payload():
    """
    Analiza scripts en busca de patron de DNS tunneling.
    Un EDR detectaria patrones como:
    - Funciones de codificacion base32/base64
    - Dominios C2 hardcodeados
    - Consultas DNS programaticas
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

        patrones_maliciosos = [
            (r'codificar_dns', 'Funcion de codificacion DNS'),
            (r'DOMINIO_C2\s*=', 'Dominio C2 hardcodeado'),
            (r'base32encode', 'Uso de base32 para codificar'),
            (r'\.evil\.', 'Dominio sospechoso .evil.'),
        ]

        for patron, desc in patrones_maliciosos:
            if re.search(patron, contenido):
                hallazgos.append({
                    'archivo': ruta,
                    'tipo': 'Script payload',
                    'severidad': 'MEDIA',
                    'razon': desc,
                })

    return hallazgos


def detectar_subdominios_largos():
    """
    Busca archivos con subdominios DNS inusualmente largos.
    En DNS normal, los labels tienen 5-15 caracteres.
    Labels de >30 caracteres sugieren datos ocultos.
    """
    hallazgos = []

    if not os.path.isdir(DIR_SIMULACION):
        return hallazgos

    for nombre in os.listdir(DIR_SIMULACION):
        ruta = os.path.join(DIR_SIMULACION, nombre)
        if not os.path.isfile(ruta):
            continue

        try:
            with open(ruta, 'r', errors='ignore') as f:
                contenido = f.read()
        except Exception:
            continue

        for match in PATRON_LABEL_LARGO.finditer(contenido):
            label = match.group()
            hallazgos.append({
                'archivo': ruta,
                'tipo': 'Subdominio largo',
                'severidad': 'MEDIA',
                'razon': f'Label DNS de {len(label)} caracteres: {label[:40]}...',
            })

    return hallazgos


def detectar_base32_en_archivos():
    """
    Busca secuencias base32 sospechosas en archivos del proyecto.
    En un ataque real de DNS tunneling, los datos se codifican en base32
    porque es DNS-safe (solo usa A-Z y 2-7).
    """
    hallazgos = []

    if not os.path.isdir(DIR_SIMULACION):
        return hallazgos

    for nombre in os.listdir(DIR_SIMULACION):
        ruta = os.path.join(DIR_SIMULACION, nombre)
        if not os.path.isfile(ruta):
            continue

        try:
            with open(ruta, 'r', errors='ignore') as f:
                contenido = f.read()
        except Exception:
            continue

        # Buscar secuencias base32 largas
        matches = PATRON_BASE32.findall(contenido)
        for match in matches:
            if len(match) > 20:  # Solo secuencias significativas
                hallazgos.append({
                    'archivo': ruta,
                    'tipo': 'Base32 detectado',
                    'severidad': 'MEDIA',
                    'razon': f'Secuencia base32 de {len(match)} chars',
                })

    return hallazgos


def ejecutar_deteccion():
    """Ejecuta todas las verificaciones de DNS tunneling."""
    banner("DEFENSA DNS TUNNELING -- DETECCION",
           "Analizando artefactos de DNS tunneling")

    total_hallazgos = []

    # 0. Verificar directorio de prueba
    safe_print(color("--- Verificacion 0: Directorio de prueba ---", 'cyan'))
    existe, archivos = detectar_directorio_pruebas()
    if existe:
        safe_print(f"  {color('!', 'yellow')} directorio_pruebas/ encontrado: {len(archivos)} archivos")
    else:
        safe_print(f"  {color('[OK]', 'green')} directorio_pruebas/ no existe")

    # 1. Archivos de DNS tunneling
    safe_print(color("\n--- Verificacion 1: Archivos de DNS tunnel ---", 'cyan'))
    h1 = detectar_archivos_dns_tunnel()
    if h1:
        safe_print(f"  {color('!', 'red')} {len(h1)} archivo(s) encontrado(s):")
        for h in h1:
            safe_print(f"    [{color(h['severidad'], 'red')}] {h['tipo']}")
            safe_print(f"      Archivo: {h['archivo']}")
            safe_print(f"      Razon: {h['razon']}")
        total_hallazgos.extend(h1)
    else:
        safe_print(f"  {color('[OK]', 'green')} No se encontraron archivos de DNS tunnel")

    # 2. Contenido de logs DNS
    safe_print(color("\n--- Verificacion 2: Contenido de logs DNS ---", 'cyan'))
    h2 = detectar_dns_log_content()
    if h2:
        safe_print(f"  {color('!', 'red')} {len(h2)} log(s) con trafico tunneled:")
        for h in h2:
            safe_print(f"    [{color(h['severidad'], 'red')}] {h['archivo']}")
            safe_print(f"      Razon: {h['razon']}")
        total_hallazgos.extend(h2)
    else:
        safe_print(f"  {color('[OK]', 'green')} No se detecto trafico DNS tunneled")

    # 3. Scripts payload
    safe_print(color("\n--- Verificacion 3: Scripts payload ---", 'cyan'))
    h3 = detectar_script_payload()
    if h3:
        safe_print(f"  {color('!', 'red')} {len(h3)} script(s) payload encontrado(s):")
        for h in h3:
            safe_print(f"    [{color(h['severidad'], 'red')}] {h['archivo']}")
            safe_print(f"      Razon: {h['razon']}")
        total_hallazgos.extend(h3)
    else:
        safe_print(f"  {color('[OK]', 'green')} No se encontraron scripts payload")

    # 4. Subdominios largos
    safe_print(color("\n--- Verificacion 4: Subdominios largos ---", 'cyan'))
    h4 = detectar_subdominios_largos()
    if h4:
        safe_print(f"  {color('!', 'red')} {len(h4)} subdominio(s) largo(s) detectado(s):")
        for h in h4[:5]:  # Mostrar maximo 5
            safe_print(f"    [{color(h['severidad'], 'red')}] {h['razon']}")
        if len(h4) > 5:
            safe_print(f"    ... y {len(h4) - 5} mas")
        total_hallazgos.extend(h4)
    else:
        safe_print(f"  {color('[OK]', 'green')} No se detectaron subdominios largos")

    # 5. Base32 en archivos
    safe_print(color("\n--- Verificacion 5: Codigo base32 ---", 'cyan'))
    h5 = detectar_base32_en_archivos()
    if h5:
        safe_print(f"  {color('!', 'red')} {len(h5)} secuencia(s) base32 detectada(s):")
        for h in h5[:5]:
            safe_print(f"    [{color(h['severidad'], 'red')}] {h['archivo']}: {h['razon']}")
        if len(h5) > 5:
            safe_print(f"    ... y {len(h5) - 5} mas")
        total_hallazgos.extend(h5)
    else:
        safe_print(f"  {color('[OK]', 'green')} No se detectaron secuencias base32 sospechosas")

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
        safe_print(color("  RESULTADO: Sin artefactos de DNS tunneling detectados", 'green'))

    log(f"Deteccion DNS tunnel completada: {len(total_hallazgos)} hallazgos")
    return total_hallazgos


def limpiar_artefactos():
    """
    Elimina todos los artefactos de DNS tunneling.
    En produccion, esto equivaleria a:
    - Bloquear el dominio C2 en el firewall/DNS
    - Eliminar el payload del sistema
    - Rotar credenciales comprometidas
    - Analizar logs para determinar alcance
    """
    banner("DEFENSA DNS TUNNELING -- LIMPIEZA", "Eliminando artefactos detectados")

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
    banner("DEFENSA DNS TUNNELING -- AYUDA",
           "Deteccion y limpieza de DNS tunneling")

    safe_print("""
  Uso:
    python defensa.py [OPCIONES]

  Opciones:
    --clean     Elimina directorio_pruebas/ y todos los artefactos
    --help      Muestra esta ayuda

  Descripcion:
    Detecta y elimina artefactos generados por la simulacion de
    DNS tunneling (modulo 14). Realiza 6 verificaciones:
    0. Existencia de directorio_pruebas/
    1. Archivos de DNS tunnel (logs, scripts)
    2. Contenido de logs DNS con trafico tunneled
    3. Scripts payload de DNS tunneling
    4. Subdominios inusualmente largos
    5. Secuencias base32 sospechosas

  Indicadores detectados:
    - Labels DNS > 30 caracteres
    - Dominios .evil o .mal
    - Codigo base32/base64 en archivos
    - Scripts con funciones de codificacion DNS
    - Logs con queries DNS a dominios sospechosos

  Severidades:
    ALTA   - Trafico DNS tunnel confirmado
    MEDIA  - Patron sospechoso de tunneling
    BAJA   - Artefacto inofensivo

  Herramientas de produccion recomendadas:
    - Suricata: reglas DNS tunneling
    - Zeek/Bro: analisis de trafico DNS
    - Passive DNS: historial de consultas
    - DNS analytics: ML sobre patrones
""")


def main():
    parser = argparse.ArgumentParser(
        description='Defensa contra DNS tunneling',
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
