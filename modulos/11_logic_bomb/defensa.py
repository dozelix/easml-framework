#!/usr/bin/env python3
"""
Módulo 11 — Defensa contra Bomba Lógica (Educativo)

Detecta condiciones de activación de bombas lógicas simuladas, examina
archivos de configuración y elimina los artefactos de la simulación.

En un entorno de producción, un analista SOC usaría análisis estático de código,
auditoría de cambios y monitoreo de integridad para detectar bombas lógicas.

Uso:
    python modulos/11_logic_bomb/defensa.py          Ejecutar escaneo
    python modulos/11_logic_bomb/defensa.py --help   Mostrar ayuda
"""
import os
import sys
import json
import glob

# ── Configurar path para importar core.common ──
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from core.common import log, safe_print, color, banner, cleanup, write_log

# ── Directorio de trabajo de la simulación ──
LAB_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__)))), 'directorio_pruebas')

# Artefactos conocidos que genera la simulación de bomba lógica
ARTIFACTOS = {
    "archivos": [
        os.path.join(LAB_DIR, "logic_bomb_marker.json"),
        os.path.join(LAB_DIR, "logic_bomb.log"),
        os.path.join(LAB_DIR, "_trigger_bomb.txt"),
    ],
    "patrones": [os.path.join(LAB_DIR, "logic_bomb_*.log")],
}


def paso_fase(fase_num, titulo):
    """Muestra un separador visual de fase en la consola."""
    safe_print(color(f"\n  [FASE {fase_num}] {titulo}", 'yellow'))
    safe_print(color(f"  {'─' * 55}", 'yellow'))


def detectar():
    """
    Fase de detección: escanea en busca de artefactos de bomba lógica.
    En producción, esto equivaldría a:
    - Análisis estático de código fuente buscando condicionales sospechosos
    - Auditoría de cambios de empleados antes de ser despedidos
    - Monitoreo de integridad con hashes de archivos críticos
    - Git blame para identificar autores de cambios sospechosos
    """
    banner("DEFENSA — BOMBA LÓGICA — DETECCIÓN Y NEUTRALIZACIÓN",
           "Analizando marcadores y condiciones de activación")

    hallazgos = []

    # ── FASE 1: Buscar artefactos conocidos ──
    paso_fase(1, "BÚSQUEDA — Escaneando artefactos de bomba lógica")
    for archivo in ARTIFACTOS["archivos"]:
        if os.path.exists(archivo):
            hallazgos.append(archivo)
            safe_print(color(f"  [!] Detectado: {os.path.basename(archivo)}", 'red'))

    for patron in ARTIFACTOS["patrones"]:
        for f in glob.glob(patron):
            if f not in hallazgos:
                hallazgos.append(f)
                safe_print(color(f"  [!] Detectado (patrón): {os.path.basename(f)}", 'red'))

    # ── FASE 2: Analizar el marker de la bomba ──
    marker_path = os.path.join(LAB_DIR, "logic_bomb_marker.json")
    if os.path.exists(marker_path):
        paso_fase(2, "ANÁLISIS — Examining la configuración de la bomba")
        try:
            with open(marker_path, 'r', encoding='utf-8') as f:
                estado = json.load(f)

            safe_print(color(f"\n  Análisis de la bomba lógica:", 'cyan'))
            safe_print(color(f"    Nombre:     {estado.get('nombre', '?')}", 'white'))
            safe_print(color(f"    Tipo:       {estado.get('tipo', '?')}", 'white'))
            safe_print(color(f"    Creada:     {estado.get('creada', '?')}", 'white'))
            safe_print(color(f"    Activa:     {estado.get('activa', '?')}",
                             'red' if estado.get('activa') else 'green'))
            safe_print(color(f"    Payload:    {'Ejecutado' if estado.get('payload_ejecutado') else 'Pendiente'}",
                             'yellow'))

            # Mostrar cada condición con su estado
            conds = estado.get('condiciones', [])
            safe_print(color(f"\n  Condiciones evaluadas ({len(conds)}):", 'cyan'))
            for c in conds:
                marca = "X" if c.get('cumplida') else " "
                safe_print(color(
                    f"    [{marca}] {c.get('nombre', '?')}: {c.get('descripcion', '?')}",
                    'red' if c.get('cumplida') else 'white'
                ))

            safe_print(color(f"\n  Umbral de activación: >= {estado.get('umbral_activacion', '?')} condiciones", 'yellow'))
            safe_print(color(f"  Condiciones cumplidas: {estado.get('condiciones_cumplidas', '?')}", 'yellow'))
        except Exception as e:
            safe_print(color(f"  Error al analizar marker: {e}", 'yellow'))

    if not hallazgos:
        safe_print(color("  [OK] No se encontraron artefactos de bomba lógica.", 'green'))

    return hallazgos


def ejecutar():
    """Ejecuta el proceso completo de detección, análisis y neutralización."""
    os.makedirs(LAB_DIR, exist_ok=True)
    hallazgos = detectar()

    # ── FASE 3: Neutralizar ──
    if hallazgos:
        paso_fase(3, "NEUTRALIZACIÓN — Eliminando artefactos de la bomba")
        removidos = cleanup(
            files_to_remove=[os.path.join(LAB_DIR, a) for a in [
                "logic_bomb_marker.json", "logic_bomb.log", "_trigger_bomb.txt"
            ]],
            patterns=[os.path.join(LAB_DIR, "logic_bomb_*.log")]
        )
        safe_print(color(f"\n  Bomba neutralizada: {removidos} artefactos eliminados.", 'green'))
    else:
        removidos = 0

    # ── FASE 4: Resumen ──
    paso_fase(4, "RESUMEN — Hallazgos y recomendaciones")
    if hallazgos:
        safe_print(color(f"\n  Total de artefactos encontrados: {len(hallazgos)}", 'yellow'))
    else:
        safe_print(color("\n  [OK] No se encontraron artefactos de bomba lógica.\n", 'green'))

    safe_print(color("  RECOMENDACIONES PARA ENTORNO PRODUCTIVO:", 'bold'))
    safe_print(color("  - Análisis estático de código buscando condicionales sospechosos", 'cyan'))
    safe_print(color("  - Auditoría de cambios antes de despidos (insider threat)", 'cyan'))
    safe_print(color("  - Monitoreo de integridad con hashes de archivos críticos", 'cyan'))
    safe_print(color("  - Git blame para identificar autores de cambios sospechosos", 'cyan'))
    safe_print(color("  - Segregación de duties: un empleado no debería tener acceso total", 'cyan'))
    safe_print(color("  - Honeypots: archivos trampa que alertan si son modificados\n", 'cyan'))

    write_log("defensa_logic_bomb", [
        f"Escaneo defensivo completado",
        f"Artefactos encontrados: {len(hallazgos)}",
        f"Artefactos eliminados: {removidos}",
        f"Bomba neutralizada: SI",
    ], os.path.join(LAB_DIR, "defensa_logic_bomb.log"))


if __name__ == "__main__":
    if "--help" in sys.argv:
        print(__doc__)
        sys.exit(0)
    ejecutar()
