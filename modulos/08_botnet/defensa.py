#!/usr/bin/env python3
"""
Módulo 08 — Defensa contra artefactos de Botnet (Educativo)

Detecta y elimina los archivos generados por la simulación de botnet:
bot_config.json, botnet_c2.log, y cualquier archivo derivado.

En un entorno de producción, un analista SOC usaría herramientas similares
para correlacionar indicadores de compromiso (IOCs) de una botnet real.

Uso:
    python modulos/08_botnet/defensa.py          Ejecutar escaneo defensivo
    python modulos/08_botnet/defensa.py --help   Mostrar ayuda
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

# Artefactos conocidos que genera la simulación de botnet
ARTIFACTOS = {
    "archivos": [
        os.path.join(LAB_DIR, "bot_config.json"),
        os.path.join(LAB_DIR, "botnet_c2.log"),
    ],
    "patrones": [
        os.path.join(LAB_DIR, "bot_config*.json"),
        os.path.join(LAB_DIR, "botnet_*.log"),
    ],
}


def paso_fase(fase_num, titulo):
    """Muestra un separador visual de fase en la consola."""
    safe_print(color(f"\n  [FASE {fase_num}] {titulo}", 'yellow'))
    safe_print(color(f"  {'─' * 55}", 'yellow'))


def detectar():
    """
    Fase de detección: escanea el directorio en busca de artefactos de botnet.
    En producción, esto equivaldría a analizar logs de firewall, DNS y NetFlow
    para identificar patrones de beaconing y tráfico C2 sospechoso.
    """
    banner("DEFENSA — BOTNET — DETECCIÓN Y ANÁLISIS",
           "Escaneando artefactos de la simulación de botnet")

    hallazgos = []

    # ── FASE 1: Buscar archivos de configuración de la botnet ──
    paso_fase(1, "ANÁLISIS — Buscando configuración de la botnet")
    # En producción: analizaríamos logs de proxy, DNS y firewall para detectar
    # conexiones a dominios/puertos conocidos de C2.
    for archivo in ARTIFACTOS["archivos"]:
        if os.path.exists(archivo):
            tam = os.path.getsize(archivo)
            hallazgos.append(archivo)
            safe_print(color(f"  [!] Detectado: {os.path.basename(archivo)} ({tam} bytes)", 'red'))

    # ── FASE 2: Buscar por patrones de archivos ──
    paso_fase(2, "BÚSQUEDA — Escaneando por patrones conocidos de botnet")
    for patron in ARTIFACTOS["patrones"]:
        for f in glob.glob(patron):
            if f not in hallazgos:
                hallazgos.append(f)
                safe_print(color(f"  [!] Detectado (patrón): {os.path.basename(f)}", 'red'))

    # ── FASE 3: Análisis del archivo de configuración ──
    if os.path.exists(os.path.join(LAB_DIR, "bot_config.json")):
        paso_fase(3, "CORRELACIÓN — Analizando configuración de la botnet")
        try:
            with open(os.path.join(LAB_DIR, "bot_config.json"), 'r', encoding='utf-8') as f:
                cfg = json.load(f)
            safe_print(color(f"    Red:          {cfg.get('nombre_red', '?')}", 'yellow'))
            safe_print(color(f"    Servidor C2:  {cfg.get('servidor_c2', '?')}:{cfg.get('puerto_irc', '?')}", 'yellow'))
            safe_print(color(f"    Canales:      {', '.join(cfg.get('canales', []))}", 'yellow'))
            safe_print(color(f"    Total bots:   {cfg.get('total_bots', '?')}", 'yellow'))

            # Analizar métricas del último ataque
            ataque = cfg.get('ultimo_ataque', {})
            if ataque:
                safe_print(color(f"\n    Último ataque DDoS registrado:", 'red'))
                safe_print(color(f"      Tipo:          {ataque.get('tipo', '?')}", 'red'))
                safe_print(color(f"      Bots:          {ataque.get('bots_participantes', '?')}", 'red'))
                safe_print(color(f"      Paq/seg:       {ataque.get('paquetes_por_segundo', '?')}", 'red'))
                safe_print(color(f"      Ancho de banda: {ataque.get('ancho_banda_mbps', '?')} Mbps", 'red'))
                safe_print(color(f"      Objetivo:      {ataque.get('objetivo', '?')}", 'red'))
        except Exception as e:
            safe_print(color(f"  Error al analizar config: {e}", 'yellow'))

    if not hallazgos:
        safe_print(color("\n  [OK] No se encontraron artefactos de botnet en el directorio.", 'green'))

    return hallazgos


def ejecutar():
    """Ejecuta el proceso completo de detección y recomendaciones."""
    os.makedirs(LAB_DIR, exist_ok=True)
    hallazgos = detectar()

    # ── FASE 4: Resumen y recomendaciones ──
    paso_fase(4, "RESUMEN — Hallazgos y recomendaciones")
    if hallazgos:
        safe_print(color(f"\n  Total de artefactos encontrados: {len(hallazgos)}", 'yellow'))
        safe_print(color("  Ejecuta con --clean para eliminarlos.\n", 'yellow'))
    else:
        safe_print(color("\n  [OK] Sistema limpio — no se detectaron artefactos de botnet.\n", 'green'))

    safe_print(color("  RECOMENDACIONES PARA ENTORNO PRODUCTIVO:", 'bold'))
    safe_print(color("  - Monitorear tráfico IRC/HTTP para detectar patrones de beaconing", 'cyan'))
    safe_print(color("  - Implementar sinkholing DNS para dominios C2 conocidos", 'cyan'))
    safe_print(color("  - Analizar NetFlow para identificar hosts con tráfico anómalo", 'cyan'))
    safe_print(color("  - Segmentar la red para limitar movimiento lateral de bots", 'cyan'))
    safe_print(color("  - Actualizar firmware en dispositivos IoT (Mirai-style)", 'cyan'))
    safe_print(color("  - Usar EDR con detección de comportamiento C2\n", 'cyan'))

    write_log("defensa_botnet", [
        f"Escaneo defensivo completado",
        f"Artefactos encontrados: {len(hallazgos)}",
    ], os.path.join(LAB_DIR, "defensa_botnet.log"))


if __name__ == "__main__":
    if "--help" in sys.argv:
        print(__doc__)
        sys.exit(0)
    ejecutar()
