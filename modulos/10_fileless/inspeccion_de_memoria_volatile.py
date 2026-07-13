#!/usr/bin/env python3
"""
Módulo 10 — Defensa contra Malware Fileless (Educativo)

Detecta rastros de ejecución fileless: archivos temporales, artefactos
residuales y logs de la simulación.

En un entorno de producción, un analista SOC usaría Sysmon, PowerShell
Logging y EDR behavior-based para detectar ejecución fileless.

Uso:
    python modulos/10_fileless/defensa.py          Ejecutar escaneo
    python modulos/10_fileless/defensa.py --help   Mostrar ayuda
"""
import os
import sys
import glob

# ── Configurar path para importar core.common ──
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from modulos.common.utils import log, safe_print, color, banner, cleanup, write_log, find_lab_dir

# ── Directorio de trabajo de la simulación ──
LAB_DIR = find_lab_dir(os.path.dirname(os.path.abspath(__file__)))

# Artefactos conocidos que genera la simulación fileless
ARTIFACTOS = {
    "archivos": [os.path.join(LAB_DIR, "fileless.log")],
    "patrones_temporales": [
        os.path.join(LAB_DIR, "fileless_sim_*.py"),
        os.path.join(LAB_DIR, "fileless_payload_*.py"),
    ],
}


def paso_fase(fase_num, titulo):
    """Muestra un separador visual de fase en la consola."""
    safe_print(color(f"\n  [FASE {fase_num}] {titulo}", 'yellow'))
    safe_print(color(f"  {'─' * 55}", 'yellow'))


def buscar_archivos_temporales():
    """
    Busca scripts fileless residuales en el directorio de trabajo.
    En un sistema real, buscaríamos procesos PowerShell con scripts en memoria,
    suscriptores WMI anómalos, y modificaciones al registro.
    """
    encontrados = []
    for patron in ARTIFACTOS["patrones_temporales"]:
        for f in glob.glob(patron):
            encontrados.append(f)
            try:
                tam = os.path.getsize(f)
                safe_print(color(f"  [!] Temp residual: {os.path.basename(f)} ({tam} bytes)", 'red'))
            except Exception:
                safe_print(color(f"  [!] Temp residual: {os.path.basename(f)}", 'red'))
    return encontrados


def detectar():
    """
    Fase de detección: escanea en busca de artefactos fileless.
    En producción, esto equivaldría a:
    - Analizar logs de Sysmon (Event IDs 1, 8, 10)
    - Revisar ScriptBlock Logging de PowerShell
    - Buscar suscriptores WMI no autorizados
    - Verificar procesos con memoria modificada
    """
    banner("DEFENSA — FILELESS — DETECCIÓN DE EJECUCIÓN SIN ARCHIVOS",
           "Escaneando artefactos residuales de ejecución fileless")

    hallazgos = []

    # ── FASE 1: Buscar logs de la simulación ──
    paso_fase(1, "BÚSQUEDA — Escaneando logs de ejecución fileless")
    for archivo in ARTIFACTOS["archivos"]:
        if os.path.exists(archivo):
            hallazgos.append(archivo)
            safe_print(color(f"  [!] Detectado: {os.path.basename(archivo)}", 'red'))

    # ── FASE 2: Buscar scripts temporales residuales ──
    paso_fase(2, "BÚSQUEDA — Buscando scripts temporales residuales")
    temporales = buscar_archivos_temporales()
    hallazgos.extend(temporales)

    if not hallazgos:
        safe_print(color("  [OK] No se encontraron artefactos fileless.", 'green'))

    # ── FASE 3: Información sobre detección en entorno real ──
    paso_fase(3, "INFORMACIÓN — Cómo detectar fileless en producción")
    safe_print(color("  En un sistema real, buscaría:", 'cyan'))
    safe_print(color("    - Procesos PowerShell con ScriptBlock Logging habilitado", 'white'))
    safe_print(color("    - Suscriptores WMI no autorizados (Sysmon Event ID 19-21)", 'white'))
    safe_print(color("    - Claves de registro Run/RunOnce modificadas recientemente", 'white'))
    safe_print(color("    - Procesos con memoria modificada (process hollowing)", 'white'))
    safe_print(color("    - DLLs cargadas desde ubicaciones inusuales", 'white'))
    safe_print(color("    - AMSI (Antimalware Scan Interface) para PowerShell", 'white'))
    safe_print(color("    - ETW (Event Tracing for Windows) para monitoreo en tiempo real", 'white'))

    return hallazgos


def ejecutar():
    """Ejecuta el proceso completo de detección y recomendaciones."""
    os.makedirs(LAB_DIR, exist_ok=True)
    hallazgos = detectar()

    # ── FASE 4: Resumen ──
    paso_fase(4, "RESUMEN — Hallazgos y recomendaciones")
    if hallazgos:
        safe_print(color(f"\n  Total de artefactos encontrados: {len(hallazgos)}", 'yellow'))
    else:
        safe_print(color("\n  [OK] No se encontraron artefactos fileless.\n", 'green'))

    safe_print(color("  RECOMENDACIONES PARA ENTORNO PRODUCTIVO:", 'bold'))
    safe_print(color("  - Habilitar PowerShell ScriptBlock Logging y Module Logging", 'cyan'))
    safe_print(color("  - Instalar Sysmon para monitoreo detallado de procesos", 'cyan'))
    safe_print(color("  - Usar EDR con detección de comportamiento (no solo firmas)", 'cyan'))
    safe_print(color("  - Habilitar AMSI para inspección de scripts en tiempo real", 'cyan'))
    safe_print(color("  - Monitorear procesos con ETW para detección en memoria\n", 'cyan'))

    write_log("defensa_fileless", [
        f"Escaneo defensivo completado",
        f"Artefactos encontrados: {len(hallazgos)}",
    ], os.path.join(LAB_DIR, "defensa_fileless.log"))


if __name__ == "__main__":
    if "--help" in sys.argv:
        print(__doc__)
        sys.exit(0)
    ejecutar()
