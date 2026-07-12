#!/usr/bin/env python3
"""
Modulo 05 - Simulacion de troyano educativo.

Crea archivos que parecen legitimos pero contienen marcadores
de payload oculto, demostrando como los troyanos se disfrazan.

SOLO PARA USO EDUCATIVO EN ENTORNO CONTROLADO.

Uso:
    python modulos/05_trojan/trojan.py           Ejecutar simulacion
    python modulos/05_trojan/trojan.py --clean   Limpiar artefactos
    python modulos/05_trojan/trojan.py --help    Mostrar ayuda
"""
import os
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, ROOT)

from core.common import (
    banner, color, safe_print, log, LOG_LINES,
    write_log, cleanup, hash_file as _hash_file,
    find_lab_dir,
)

# ── Ruta del directorio de pruebas ──
LAB_DIR = find_lab_dir(ROOT)

# ── Marcadores de deteccion ──
# Estos marcadores simulan los indicadores de compromiso (IOC)
# que una solucion de seguridad buscaria en un analisis estatico.
PAYLOAD_MARKER = "TROJAN_PAYLOAD_SIMULATION"
STEALTH_MARKER = "HIDDEN_PAYLOAD_SIMULATION"
C2_MARKER = "C2_SERVER_ENDPOINT"


# ══════════════════════════════════════════════════════════════
#  FUNCIONES AUXILIARES
# ══════════════════════════════════════════════════════════════

def _short_hash(path):
    """Devuelve los primeros 16 caracteres del hash SHA-256."""
    h = _hash_file(path)
    return h[:16] + "..." if h else "N/A"


def _paso_fase(num, titulo):
    """Imprime un separador visual de fase."""
    safe_print(color(f"\n  [FASE {num}] {titulo}", 'yellow'))
    safe_print(color(f"  {'─' * 55}", 'yellow'))
    time.sleep(0.3)


# ══════════════════════════════════════════════════════════════
#  FUNCIONES DE CREACION DE TROYANOS SIMULADOS
# ══════════════════════════════════════════════════════════════

def crear_update_exe():
    """
    Crea un archivo que parece un ejecutable de actualizacion.
    Tecnica: El nombre "update.exe" genera confianza porque el
    usuario asocia "actualizacion" con algo necesario y seguro.
    """
    safe_print(color("\n  [1/5] Creando 'update.exe' (disfraz de actualizacion)...", 'cyan'))
    path = os.path.join(LAB_DIR, "update.exe")
    contenido = f"""# update.exe - ACTUALIZACION DE SISTEMA v3.2.1
# Este archivo es una simulacion educativa INOFENSIVA
# No contiene codigo malicioso ejecutable

# === METADATOS FALSOS ===
# Nombre: update.exe
# Tamano simulado: 2.4 MB
# Firma: Microsoft Corporation (FALSA - simulacion)
# Fecha: 2026-01-15
# Descripcion: Paquete de actualizacion critica de Windows

{PAYLOAD_MARKER}
# El payload real contendria:
# - Carga de modulo de persistencia
# - Configuracion de inicio automatico
# - Conexion a servidor C2

def instalador_legitimo():
    \"\"\"Parte visible: el usuario ve esta barra de progreso\"\"\"
    print("Instalando actualizacion...")
    print("  [████████████████████] 100%")
    print("  Reiniciando en 3 segundos...")
    return True

def payload_oculto():
    \"\"\"Parte oculta: aqui se ejecutaria el malware real\"\"\"
    # PAYLOAD BLOQUEADO - SIMULACION
    print("[SIMULACION] Payload no ejecutado")
    pass

if __name__ == "__main__":
    instalador_legitimo()
"""
    with open(path, 'w', encoding='utf-8') as f:
        f.write(contenido)
    safe_print(color(f"    Tamano: {os.path.getsize(path)} bytes", 'yellow'))
    safe_print(color(f"    Hash SHA-256: {_short_hash(path)}", 'yellow'))
    safe_print(color(f"    Tecnica: Nombre de actualizacion para generar confianza", 'cyan'))
    log("Troyano creado: directorio_pruebas/update.exe")
    return path


def crear_imagen_jpg_exe():
    """
    Crea un ejecutable disfrazado de imagen usando extension dual.
    Tecnica: Windows oculta extensiones conocidas por defecto,
    mostrando solo "imagen.jpg" al usuario.
    """
    safe_print(color("\n  [2/5] Creando 'imagen.jpg.exe' (disfraz de imagen)...", 'cyan'))
    path = os.path.join(LAB_DIR, "imagen.jpg.exe")
    contenido = f"""# imagen.jpg.exe - Visor de imagenes v2.0
# Este archivo es una simulacion educativa INOFENSIVA

# === TRUCO DE EXTENSION DUAL ===
# El nombre usa doble extension (.jpg.exe) para enganar.
# Windows oculta la extension real por defecto.
# Si "Mostrar extensiones" esta desactivado, el usuario ve solo "imagen.jpg"

{PAYLOAD_MARKER}
{STEALTH_MARKER}

# Truco: en Windows, si las extensiones conocidas estan ocultas,
# "imagen.jpg.exe" se muestra como "imagen.jpg" con icono de imagen.

def mostrar_imagen():
    \"\"\"Parte visible: el usuario cree que abre una imagen\"\"\"
    print("Abriendo imagen...")
    print("  Cargando vista previa...")
    return True

def ejecutar_payload():
    \"\"\"Parte oculta: ejecucion del malware\"\"\"
    # PAYLOAD BLOQUEADO - SIMULACION
    print("[SIMULACION] Payload oculto detectado")
    pass
"""
    with open(path, 'w', encoding='utf-8') as f:
        f.write(contenido)
    safe_print(color(f"    Tamano: {os.path.getsize(path)} bytes", 'yellow'))
    safe_print(color(f"    Hash SHA-256: {_short_hash(path)}", 'yellow'))
    safe_print(color(f"    Tecnica: Extension dual (.jpg.exe) para ocultar la ejecutable", 'cyan'))
    log("Troyano creado: directorio_pruebas/imagen.jpg.exe")
    return path


def crear_factura_pdf_exe():
    """
    Crea un archivo disfrazado de factura PDF urgente.
    Tecnica: El nombre sugiere un documento financiero pendiente,
    activando el miedo del usuario a consecuencias economicas.
    """
    safe_print(color("\n  [3/5] Creando 'factura_2026.pdf.exe' (disfraz de factura)...", 'cyan'))
    path = os.path.join(LAB_DIR, "factura_2026.pdf.exe")
    contenido = f"""# factura_2026.pdf.exe - Visor de documentos v5.1
# Este archivo es una simulacion educativa INOFENSIVA

# === MODULO DE INGENIERIA SOCIAL ===
# Nombre sugiere documento urgente para que el usuario lo abra rapido.
# El ".pdf" es parte del nombre, no de la extension real.
# El usuario ve "factura_2026.pdf" y piensa en una factura pendiente.

{PAYLOAD_MARKER}
{STEALTH_MARKER}
{C2_MARKER}://servidor-simulado.ejemplo.com:443

# Cadena de entrega tipica:
# 1. Email urgente con asunto "Factura pendiente de pago"
# 2. Usuario ejecuta el archivo
# 3. Se muestra una "factura" falsa como distraccion
# 4. Payload se ejecuta en segundo plano
# 5. Conexion C2 establecida con el servidor del atacante

def mostrar_factura_falsa():
    \"\"\"Parte visible: factura que distrae al usuario\"\"\"
    print("╔══════════════════════════════════════╗")
    print("║        FACTURA #2026-001547          ║")
    print("║  Monto: $15.420,00                   ║")
    print("║  Estado: PENDIENTE DE PAGO           ║")
    print("║  Vencimiento: 20/01/2026             ║")
    print("╚══════════════════════════════════════╝")
    return True

def stealth_payload():
    \"\"\"Parte oculta: exfiltracion de datos\"\"\"
    # PAYLOAD BLOQUEADO - SIMULACION
    print("[SIMULACION] Payload de exfiltracion no ejecutado")
    pass
"""
    with open(path, 'w', encoding='utf-8') as f:
        f.write(contenido)
    safe_print(color(f"    Tamano: {os.path.getsize(path)} bytes", 'yellow'))
    safe_print(color(f"    Hash SHA-256: {_short_hash(path)}", 'yellow'))
    safe_print(color(f"    Tecnica: Urgencia financiera + extension dual", 'cyan'))
    log("Troyano creado: directorio_pruebas/factura_2026.pdf.exe")
    return path


def crear_readme_txt():
    """
    Crea un archivo de texto aparentemente inofensivo con payload.
    Tecnica: Los archivos .txt rara vez son bloqueados por antivirus
    porque se consideran inseguros por naturaleza.
    """
    safe_print(color("\n  [4/5] Creando 'README.txt' (payload en texto)...", 'cyan'))
    path = os.path.join(LAB_DIR, "README.txt")
    contenido = f"""# Leeme - Instalacion del software

Gracias por descargar nuestro software.

Pasos de instalacion:
1. Ejecutar setup.exe como administrador
2. Seguir el asistente de instalacion
3. Reiniciar el equipo cuando se solicite

NOTA: Si tiene problemas, ejecutar el archivo adjunto.

Soporte tecnico: soporte@ejemplo-falso.com
Telefono: +54 11 5555-0000

---

{PAYLOAD_MARKER}
# Payload de descarga embebido:
# El malware real descargaria componentes adicionales
# desde un servidor remoto
{C2_MARKER}://download-simulado.ejemplo.com/payloads/

# Los archivos .txt son ideales para evadir antivirus
# porque contienen solo texto, no codigo ejecutable.
# En un ataque real, el archivo ejecutable estaria en un .zip adjunto.
"""
    with open(path, 'w', encoding='utf-8') as f:
        f.write(contenido)
    safe_print(color(f"    Tamano: {os.path.getsize(path)} bytes", 'yellow'))
    safe_print(color(f"    Hash SHA-256: {_short_hash(path)}", 'yellow'))
    safe_print(color(f"    Tecnica: Texto inofensivo con instrucciones para ejecutar malware", 'cyan'))
    log("Troyano creado: directorio_pruebas/README.txt")
    return path


def crear_config_ini():
    """
    Crea un archivo de configuracion con marcadores C2.
    Tecnica: Los archivos .ini suelen ignorarse en analisis porque
    se consideran datos, no ejecutables.
    """
    safe_print(color("\n  [5/5] Creando 'config.ini' (configuracion con C2)...", 'cyan'))
    path = os.path.join(LAB_DIR, "config.ini")
    contenido = f"""# Configuracion del sistema v2.1
# Archivo de configuracion del sistema (disfraz)

[general]
version=2.1.0
idioma=es_AR
directorio_logs=/var/log/sistema

[servidores]
# Estos campos contienen los marcadores C2 simulados
{C2_MARKER}=192.168.1.100:443
heartbeat_interval=30
retry_count=3
encrypted=true

[persistence]
# Configuracion de persistencia simulada
auto_start=true
registry_key=HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Run
scheduled_task=true
service_name=SysUpdateService

[payload]
# Payload configurado pero no ejecutado
{PAYLOAD_MARKER}
type=download_execute
target=http://simulado.ejemplo.com/payload.bin
execute_after=true
"""
    with open(path, 'w', encoding='utf-8') as f:
        f.write(contenido)
    safe_print(color(f"    Tamano: {os.path.getsize(path)} bytes", 'yellow'))
    safe_print(color(f"    Hash SHA-256: {_short_hash(path)}", 'yellow'))
    safe_print(color(f"    Tecnica: Configuracion aparente con configuracion C2 embebida", 'cyan'))
    log("Troyano creado: directorio_pruebas/config.ini")
    return path


# ══════════════════════════════════════════════════════════════
#  ANALISIS DE DETECCION
# ══════════════════════════════════════════════════════════════

def analizar_deteccion(archivos_creados):
    """Explica como se detectarian estos troyanos en un entorno real."""
    _paso_fase(2, "ANALISIS DE DETECCION — Que buscaria un antivirus/EDR")

    for path in archivos_creados:
        nombre = os.path.basename(path)
        safe_print(color(f"\n  {nombre}:", 'cyan'))

        if '.exe' in nombre:
            safe_print(color(f"    [!] Extension dual detectada — .exe oculto", 'red'))
        if 'pdf' in nombre.lower() and 'exe' in nombre:
            safe_print(color(f"    [!] Disfraz de documento PDF", 'yellow'))
        if 'jpg' in nombre.lower() and 'exe' in nombre:
            safe_print(color(f"    [!] Disfraz de imagen", 'yellow'))
        if 'update' in nombre.lower():
            safe_print(color(f"    [!] Nombre de actualizacion sospechoso", 'yellow'))
        if 'config' in nombre.lower():
            safe_print(color(f"    [!] Configuracion con datos C2 incrustados", 'yellow'))

        # Analisis de contenido
        try:
            with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                contenido = f.read(4096)
            marcadores = []
            if PAYLOAD_MARKER in contenido:
                marcadores.append('PAYLOAD')
            if STEALTH_MARKER in contenido:
                marcadores.append('STEALTH')
            if C2_MARKER in contenido:
                marcadores.append('C2')
            if marcadores:
                safe_print(color(
                    f"    [i] Marcadores de contenido: {', '.join(marcadores)}", 'magenta'
                ))
        except Exception:
            pass


def mostrar_notas_educativas():
    """Explica al estudiante como identificar troyanos reales."""
    safe_print(color("\n  ═══ NOTAS EDUCATIVAS ═══\n", 'bold'))

    safe_print(color("  Como identificar un troyano real:", 'cyan'))
    safe_print("  1. Extension dual: archivo.pdf.exe, imagen.jpg.exe")
    safe_print("  2. Tamano incoherente: imagen de 2KB o factura de 5MB")
    safe_print("  3. Firma digital ausente o invalida")
    safe_print("  4. Nombre sugiere urgencia o accion inmediata")
    safe_print("  5. Icono generico o incompatible con la extension real")

    safe_print(color("\n  Estadisticas relevantes:", 'cyan'))
    safe_print("  - El 91% de los ciberataques inician con phishing (Verizon DBIR)")
    safe_print("  - Emotet causo $2.8 mil millones en perdidas (2015-2021)")
    safe_print("  - El 75% de los troyanos usan email como vector de entrega")

    safe_print(color("\n  En esta simulacion:", 'cyan'))
    safe_print("  - Ningun archivo contiene codigo malicioso ejecutable")
    safe_print("  - Todos los archivos son texto plano inofensivo")
    safe_print("  - Los marcadores muestran donde iria el payload real")
    safe_print("  - Todo puede limpiarse con --clean\n")


# ══════════════════════════════════════════════════════════════
#  LIMPIEZA
# ══════════════════════════════════════════════════════════════

def limpiar():
    """Elimina todos los artefactos generados por la simulacion."""
    banner("MODULO 05 - TROYANO (TROJAN)", "LIMPIEZA DE ARTEFACTOS")

    trojan_files = [
        'update.exe', 'imagen.jpg.exe', 'factura_2026.pdf.exe',
        'README.txt', 'config.ini',
    ]
    removed = 0
    for fname in trojan_files:
        fpath = os.path.join(LAB_DIR, fname)
        if os.path.exists(fpath):
            try:
                os.remove(fpath)
                safe_print(color(f"  [+] Eliminado: directorio_pruebas/{fname}", 'green'))
                removed += 1
            except Exception as e:
                safe_print(color(f"  [-] Error al eliminar {fname}: {e}", 'red'))

    # Eliminar log
    log_path = os.path.join(ROOT, "05_trojan.log")
    if os.path.exists(log_path):
        os.remove(log_path)
        safe_print(color("  [+] Eliminado: 05_trojan.log", 'green'))
        removed += 1

    safe_print(color(f"\n  Limpieza completada: {removed} archivos eliminados.\n", 'green'))


# ══════════════════════════════════════════════════════════════
#  AYUDA
# ══════════════════════════════════════════════════════════════

def mostrar_ayuda():
    safe_print(color("\nUso: python trojan.py [opcion]", 'cyan'))
    safe_print(color("\nOpciones:", 'bold'))
    safe_print("  (sin args)  Ejecutar la simulacion del troyano")
    safe_print("  --clean     Eliminar todos los artefactos generados")
    safe_print("  --help      Mostrar esta ayuda")
    safe_print(color("\nDescripcion:", 'bold'))
    safe_print("  Simula troyanos que se disfrazan de archivos legitimos.")
    safe_print("  Crea 5 archivos con tecnicas de ingenieria social.")
    safe_print("  Los archivos generados son INOFENSIVOS.")
    safe_print("  Operan exclusivamente dentro de directorio_pruebas/.")
    safe_print(color("\nEjemplo:", 'bold'))
    safe_print("  python modulos/05_trojan/trojan.py")
    safe_print("  python modulos/05_trojan/trojan.py --clean\n")


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

    banner("MODULO 05 - TROYANO (TROJAN)",
           "Simulacion de archivos disfrazados con payload oculto")
    safe_print(color("  Entorno: laboratorio educativo controlado", 'cyan'))
    safe_print(color("  Los archivos generados son INOFENSIVOS\n", 'yellow'))

    # ── FASE 1: Crear archivos troyano simulados ──
    _paso_fase(1, "CREANDO ARCHIVOS TROYANO SIMULADOS")
    safe_print(color(
        "  Creando 5 archivos con tecnicas de disfraz diferentes...\n",
        'cyan'
    ))

    archivos_creados = [
        crear_update_exe(),
        crear_imagen_jpg_exe(),
        crear_factura_pdf_exe(),
        crear_readme_txt(),
        crear_config_ini(),
    ]

    safe_print(color(f"\n  Total archivos creados: {len(archivos_creados)}", 'green'))

    # ── FASE 2: Analisis de deteccion ──
    analizar_deteccion(archivos_creados)

    # ── FASE 3: Notas educativas ──
    mostrar_notas_educativas()

    # Guardar registro
    write_log("05_trojan", list(LOG_LINES), os.path.join(ROOT, "05_trojan.log"))
    safe_print(color("  Simulacion completada.\n", 'green'))


if __name__ == "__main__":
    main()
