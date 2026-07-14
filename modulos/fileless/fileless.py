#!/usr/bin/env python3
"""
Módulo 10 — Malware Fileless (Educativo)

Simula un ataque fileless creando código temporal en directorio_pruebas/,
ejecutándolo y eliminándolo inmediatamente para evadir la detección basada en disco.
El código ejecutado solo imprime un mensaje educativo inofensivo.

Todas las operaciones se confinan al directorio directorio_pruebas/.

Uso:
    python modulos/10_fileless/fileless.py          Ejecutar simulación
    python modulos/10_fileless/fileless.py --clean  Limpiar artefactos
    python modulos/10_fileless/fileless.py --help   Mostrar ayuda
"""
import os
import sys
import time
import datetime
import subprocess

# ── Configurar path para importar core.common ──
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from modulos.common.utils import (
    log, safe_print, color, banner, cleanup, write_log, find_lab_dir
)

# ── Constantes ──────────────────────────────────────────
# Directorio de trabajo confinado
LAB_DIR = find_lab_dir(os.path.dirname(os.path.abspath(__file__)))
FILELESS_LOG = os.path.join(LAB_DIR, "fileless.log")


# ── Código payload educativo ──
# Este es el "malware" que se ejecutará y eliminará inmediatamente.
# En un ataque real, este código realizaría robo de credenciales,
# descarga de payloads, o propagación. Aquí solo imprime un mensaje.
PAYLOAD_CODE = '''#!/usr/bin/env python3
"""Payload fileless educativo — solo imprime un mensaje."""
import os
import datetime

# Este código existió solo en memoria y en /tmp momentáneamente
mensaje = (
    "ESTO ES UNA SIMULACION FILELESS EDUCATIVA!\\n"
    "Este codigo:\\n"
    "  1. Fue escrito a un archivo temporal\\n"
    "  2. Se ejecuto inmediatamente\\n"
    "  3. Sera eliminado despues de esta salida\\n"
    "En un ataque real, este codigo nunca tocaria el disco de forma persistente."
)

print("=" * 55)
print("  PAYLOAD FILELESS — SIMULACION EDUCATIVA")
print("=" * 55)
print(mensaje)
print("=" * 55)
print(f"  PID: {os.getpid()}")
print(f"  Timestamp: {datetime.datetime.now().isoformat()}")
print("=" * 55)
'''


# ── Técnicas fileless simuladas (tabla educativa) ──
TECNICAS_FILELESS = [
    {
        "nombre": "PowerShell en memoria",
        "descripcion": "Ejecuta código codificado en Base64 directamente en RAM",
        "comando_ejemplo": "powershell -enc JABjAD0...",
        "deteccion": "Monitoreo de procesos PowerShell, ScriptBlock Logging",
    },
    {
        "nombre": "WMI Event Subscription",
        "descripcion": "Registra suscriptores WMI que ejecutan código al activarse",
        "comando_ejemplo": "wmic /namespace:\\\\root\\subscription ...",
        "deteccion": "Auditoría de suscriptores WMI, Sysmon Event ID 19-21",
    },
    {
        "nombre": "Registry-based execution",
        "descripcion": "Almacena código en claves del registro y lo ejecuta al inicio",
        "comando_ejemplo": "HKCU\\Software\\...\\CurrentVersion\\Run",
        "deteccion": "Monitoreo de claves Run/RunOnce, análisis de binarios referenciados",
    },
    {
        "nombre": "Process hollowing",
        "descripcion": "Inyecta código en un proceso legítimo ya en ejecución",
        "comando_ejemplo": "CreateProcess + NtUnmapViewOfSection + WriteProcessMemory",
        "deteccion": "Comparación de memoria del proceso vs imagen en disco",
    },
    {
        "nombre": "DLL search order hijacking",
        "descripcion": "Carga una DLL maliciosa antes que la legítima",
        "comando_ejemplo": "Colocar evil.dll en directorio del ejecutable",
        "deteccion": "Monitoreo de carga de DLLs, verificación de firmas",
    },
]


def paso_fase(fase_num, titulo):
    """Muestra un separador visual de fase en la consola."""
    safe_print(color(f"\n  [FASE {fase_num}] {titulo}", 'yellow'))
    safe_print(color(f"  {'─' * 55}", 'yellow'))
    time.sleep(0.3)


# ── Limpieza ──
def limpiar():
    """Elimina artefactos residuales de la simulación fileless."""
    banner("MÓDULO 10 — FILELESS — LIMPIEZA",
           "Eliminando artefactos de la simulación")

    # Buscar y eliminar scripts temporales residuales
    removidos = 0
    import glob
    for patron in [
        os.path.join(LAB_DIR, "fileless_sim_*.py"),
        os.path.join(LAB_DIR, "fileless_payload_*.py"),
        os.path.join(LAB_DIR, "fileless_sim_*.py"),
    ]:
        for f in glob.glob(patron):
            try:
                os.remove(f)
                safe_print(color(f"  Eliminado: {os.path.basename(f)}", 'green'))
                removidos += 1
            except Exception as e:
                safe_print(color(f"  Error al eliminar {f}: {e}", 'red'))

    removidos += cleanup(
        files_to_remove=[FILELESS_LOG],
        patterns=[]
    )
    safe_print(color(f"\n  Limpieza completada: {removidos} archivos eliminados.\n", 'green'))


# ── Simulación principal ──
def ejecutar():
    """Ejecuta la simulación completa de ataque fileless educativo."""
    banner("MÓDULO 10 — MALWARE FILELESS — SIMULACIÓN EDUCATIVA",
           "Simulación de ataque sin artefactos persistentes en disco")

    # Crear directorio de trabajo si no existe
    os.makedirs(LAB_DIR, exist_ok=True)
    safe_print(color(f"  Directorio de trabajo: {LAB_DIR}\n", 'cyan'))

    # ── FASE 1: Explicar el concepto ──
    paso_fase(1, "CONCEPTO — ¿Qué es un ataque fileless?")
    safe_print(color(
        "  Un malware fileless NO escribe código persistente en disco.\n"
        "  Se ejecuta directamente en memoria, usando herramientas del\n"
        "  sistema (PowerShell, WMI, regsvr32) para evitar la detección\n"
        "  por antiviruses basados en firmas.\n", 'white'
    ))
    safe_print(color(
        "  Características clave:", 'cyan'
    ))
    safe_print(color("  - Sin archivos en disco = sin firmas que escanear", 'white'))
    safe_print(color("  - Usa LOLBins (Living Off the Land Binaries)", 'white'))
    safe_print(color("  - Solo existe en memoria durante la ejecución", 'white'))
    safe_print(color("  - Difícil de detectar sin monitoreo en tiempo real\n", 'white'))
    time.sleep(0.5)

    # ── FASE 2: Mostrar técnicas fileless ──
    paso_fase(2, "TÉCNICAS — Métodos fileless conocidos")
    for i, tech in enumerate(TECNICAS_FILELESS, 1):
        safe_print(color(f"\n  [{i}] {tech['nombre']}", 'yellow'))
        safe_print(color(f"      Descripción:  {tech['descripcion']}", 'white'))
        safe_print(color(f"      Ejemplo:      {tech['comando_ejemplo']}", 'magenta'))
        safe_print(color(f"      Detección:    {tech['deteccion']}", 'green'))
    time.sleep(0.3)

    # ── FASE 3: Crear script temporal ──
    paso_fase(3, "CARGA — Creando payload en archivo temporal")
    # En un ataque real, el código se inyectaría directamente en memoria
    # usando API calls como VirtualAlloc + WriteProcessMemory.
    # Aquí usamos un archivo temporal como paso intermedio educativo.
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    temp_script = os.path.join(LAB_DIR, f"fileless_sim_{timestamp}.py")

    with open(temp_script, 'w', encoding='utf-8') as f:
        f.write(PAYLOAD_CODE)
    safe_print(color(f"  → Script creado: {os.path.basename(temp_script)}", 'yellow'))
    safe_print(color(f"  → Tamaño: {os.path.getsize(temp_script)} bytes", 'white'))
    safe_print(color("  NOTA: Este archivo existirá solo por fracciones de segundo.", 'cyan'))
    time.sleep(0.2)

    # ── FASE 4: Ejecutar código ──
    paso_fase(4, "EJECUCIÓN — Ejecutando payload (simula ejecución en memoria)")
    safe_print(color("  El código se ejecuta y produce salida, luego se elimina.\n", 'white'))

    try:
        resultado = subprocess.run(
            [sys.executable, temp_script],
            capture_output=True, text=True, timeout=10
        )
        if resultado.stdout:
            for linea in resultado.stdout.strip().split('\n'):
                safe_print(color(f"    {linea}", 'magenta'))
        if resultado.returncode != 0 and resultado.stderr:
            safe_print(color(f"  stderr: {resultado.stderr.strip()}", 'red'))
    except subprocess.TimeoutExpired:
        safe_print(color("  Timeout — ejecución simulada como exitosa", 'yellow'))
    except Exception as e:
        safe_print(color(f"  Error en ejecución: {e}", 'yellow'))

    # ── FASE 5: Eliminar inmediatamente ──
    paso_fase(5, "LIMPIEZA — Eliminando script INMEDIATAMENTE")
    time.sleep(0.1)
    if os.path.exists(temp_script):
        os.remove(temp_script)
        safe_print(color(f"  → Eliminado: {os.path.basename(temp_script)}", 'green'))
        safe_print(color("  El archivo existió solo por fracciones de segundo.", 'white'))
    else:
        safe_print(color("  → El archivo ya no existe (auto-eliminado).", 'green'))

    # ── FASE 6: Verificar ausencia ──
    paso_fase(6, "VERIFICACIÓN — Confirmando que no quedan rastros en disco")
    time.sleep(0.2)
    if os.path.exists(temp_script):
        safe_print(color("  [!] El archivo aún existe (inesperado)", 'red'))
    else:
        safe_print(color("  [OK] Ningún archivo temporal encontrado en disco.", 'green'))

    # ── FASE 7: Guardar log ──
    log_entries = [
        f"Ejecución fileless simulada",
        f"Timestamp: {datetime.datetime.now().isoformat()}",
        f"Script temporal: {os.path.basename(temp_script)}",
        f"Estado: eliminado exitosamente",
        f"Técnicas mostradas: {len(TECNICAS_FILELESS)}",
    ]
    write_log("FILELESS", log_entries)

    # ── RESUMEN ──
    safe_print(color("\n" + "=" * 60, 'cyan'))
    safe_print(color("  RESUMEN DE LA SIMULACIÓN FILELESS", 'bold'))
    safe_print(color("=" * 60, 'cyan'))
    safe_print(color(f"  Código creado en:     {os.path.basename(temp_script)}", 'white'))
    safe_print(color(f"  Estado:               ELIMINADO (sin persistencia)", 'green'))
    safe_print(color(f"  Artefactos en disco:  0", 'green'))
    safe_print(color(f"  Técnicas mostradas:   {len(TECNICAS_FILELESS)}", 'white'))
    safe_print(color("=" * 60, 'cyan'))
    safe_print(color(
        "\n  NOTA: En un ataque fileless real, el código nunca tocaría\n"
        "  el disco de forma persistente. Aquí usamos un archivo temporal\n"
        "  como paso intermedio para fines educativos.\n",
        'yellow'
    ))
    log("Simulación fileless completada")


if __name__ == "__main__":
    if "--help" in sys.argv:
        print(__doc__)
        sys.exit(0)
    if "--clean" in sys.argv:
        limpiar()
        sys.exit(0)
    ejecutar()
