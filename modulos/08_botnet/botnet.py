#!/usr/bin/env python3
"""
Módulo 08 — Botnet (Educativo)

Simula una botnet con comandos IRC ficticios, generando una lista de bots
simulados y un registro de comandos C2 (Command & Control). Incluye métricas
simuladas de ataque DDoS (paquetes/seg, ancho de banda).

Todas las operaciones se confinan al directorio directorio_pruebas/.

Uso:
    python modulos/08_botnet/botnet.py          Ejecutar simulación
    python modulos/08_botnet/botnet.py --clean  Limpiar artefactos
    python modulos/08_botnet/botnet.py --help   Mostrar ayuda
"""
import os
import sys
import json
import time
import random
import datetime

# ── Configurar path para importar core.common ──
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from modulos.common.utils import (
    log, safe_print, color, banner, cleanup, write_log, LOG_LINES, find_lab_dir
)

# ── Constantes ──────────────────────────────────────────
# Directorio de trabajo confinado para la simulación
LAB_DIR = find_lab_dir(os.path.dirname(os.path.abspath(__file__)))
BOTNET_CONFIG = os.path.join(LAB_DIR, "bot_config.json")
BOTNET_LOG = os.path.join(LAB_DIR, "botnet_c2.log")

# IPs ficticias para generar la red de bots (rangos privados, nunca públicos)
FAKE_IPS = [
    "192.168.1.{}", "10.0.0.{}", "172.16.0.{}",
    "192.168.2.{}", "10.0.1.{}", "172.16.1.{}",
]

# Canales IRC simulados donde el botmaster envía comandos
C2_CHANNELS = ["#control", "#attacks", "#loot", "#beacon"]

# Estados posibles de cada bot en la red
BOT_STATUSES = ["activo", "idle", "escaneando", "atrapando"]

# Tipos de ataque DDoS que puede orquestar la botnet
DDOS_TYPES = ["UDP flood", "HTTP flood", "SYN flood", "DNS amplification"]


# ── Funciones auxiliares ────────────────────────────────
def generar_bots(n):
    """
    Genera n bots ficticios con IPs, puertos y sistemas operativos aleatorios.
    Cada bot simula un dispositivo comprometido en la red.
    """
    bots = []
    for i in range(n):
        ip_tpl = random.choice(FAKE_IPS)
        ip = ip_tpl.format(random.randint(2, 254))
        bots.append({
            "id": f"bot_{i+1:03d}",
            "ip": ip,
            "puerto": random.randint(40000, 65000),
            "sistema_operativo": random.choice(["Linux", "Windows", "RTOS"]),
            "estado": random.choice(BOT_STATUSES),
            "canal": random.choice(C2_CHANNELS),
            "uptime_seg": random.randint(60, 86400),
            "conexion": datetime.datetime.now().isoformat(),
        })
    return bots


def simular_ddos(bots_activos):
    """
    Simula métricas de un ataque DDoS basado en el número de bots activos.
    Calcula paquetes/segundo, ancho de banda y objetivo ficticio.
    """
    paq_seg = bots_activos * random.randint(500, 2000)
    bw_mbps = paq_seg * random.uniform(0.5, 3.0)
    return {
        "tipo": random.choice(DDOS_TYPES),
        "bots_participantes": bots_activos,
        "paquetes_por_segundo": paq_seg,
        "ancho_banda_mbps": round(bw_mbps, 2),
        "duracion_seg": random.randint(5, 30),
        "objetivo": f"10.99.{random.randint(1, 254)}.{random.randint(1, 254)}",
    }


def simular_comando_c2(bots):
    """
    Simula un comando C2 enviado por el botmaster a los bots.
    Elige un comando aleatorio de la lista y lo asocia a un canal y bot origen.
    """
    comandos = [
        ("SCAN", "escaneando rangos objetivo"),
        ("ATTACK", "iniciando ataque DDoS"),
        ("UPDATE", "actualizando payload en bots"),
        ("SLEEP", "entrando en modo dormido"),
        ("EXFIL", "exfiltrando datos simulados"),
        ("BEACON", "heartbeat recibido de todos los bots"),
        ("SELFDESTRUCT", "orden de autodestricción cancelada"),
    ]
    cmd, desc = random.choice(comandos)
    canal = random.choice(C2_CHANNELS)
    bot_origen = random.choice(bots)["id"]
    ts = datetime.datetime.now().strftime("%H:%M:%S")
    return f"[{ts}] -> {canal} | {bot_origen}: {cmd} — {desc}"


def paso_fase(fase_num, titulo):
    """Muestra un separador visual de fase en la consola."""
    safe_print(color(f"\n  [FASE {fase_num}] {titulo}", 'yellow'))
    safe_print(color(f"  {'─' * 55}", 'yellow'))
    time.sleep(0.3)


# ── Limpieza ────────────────────────────────────────────
def limpiar():
    """Elimina todos los artefactos generados por la simulación de botnet."""
    banner("MÓDULO 08 — BOTNET — LIMPIEZA",
           "Eliminando artefactos de la simulación")
    removidos = cleanup(
        files_to_remove=[BOTNET_CONFIG, BOTNET_LOG],
        patterns=[
            os.path.join(LAB_DIR, "bot_config*.json"),
            os.path.join(LAB_DIR, "botnet_*.log"),
        ]
    )
    safe_print(color(f"\n  Limpieza completada: {removidos} archivos eliminados.\n", 'green'))


# ── Simulación principal ────────────────────────────────
def ejecutar():
    """Ejecuta la simulación completa de botnet educativa."""
    banner("MÓDULO 08 — BOTNET — SIMULACIÓN EDUCATIVA",
           "Simula una red de bots ficticia con comandos C2 y métricas DDoS")

    # Crear directorio de trabajo si no existe
    os.makedirs(LAB_DIR, exist_ok=True)
    safe_print(color(f"  Directorio de trabajo: {LAB_DIR}\n", 'cyan'))

    # ── FASE 1: Generar bots ──
    paso_fase(1, "PROPAGACIÓN — Creando dispositivos comprometidos simulados")
    # En un ataque real, los bots se comprometerían mediante phishing, exploits o
    # contraseñas débiles en dispositivos IoT. Aquí simulamos la lista resultante.
    num_bots = random.randint(15, 40)
    bots = generar_bots(num_bots)
    safe_print(color(f"  Se generaron {num_bots} bots ficticios (simula dispositivos comprometidos).\n", 'green'))
    log(f"Fase 1: {num_bots} bots generados")

    # ── FASE 2: Mostrar topología de la botnet ──
    paso_fase(2, "RECONOCIMIENTO — Topología de la botnet")
    # El botmaster consulta qué dispositivos están disponibles y en qué estado.
    # Cada bot reporta su IP, puerto, OS y canal C2 asignado.
    safe_print(color("  Topología de la botnet (primeros 8 bots):\n", 'cyan'))
    for b in bots[:8]:
        safe_print(color(
            f"    {b['id']:>10} | {b['ip']:>15}:{b['puerto']} | "
            f"{b['sistema_operativo']:<8} | {b['estado']:<12} | {b['canal']}",
            'white'
        ))
    if num_bots > 8:
        safe_print(color(f"    ... y {num_bots - 8} bots más\n", 'yellow'))
    log(f"Fase 2: Topología mostrada ({num_bots} bots)")

    # ── FASE 3: Enviar comandos C2 ──
    paso_fase(3, "COMMAND & CONTROL — Enviando comandos a los bots")
    # El botmaster envía comandos a través de canales IRC simulados.
    # Cada comando es recibido por los bots suscritos a ese canal.
    comandos_log = []
    for i in range(8):
        cmd = simular_comando_c2(bots)
        comandos_log.append(cmd)
        safe_print(color(f"    {cmd}", 'magenta'))
        time.sleep(0.15)
    log(f"Fase 3: {len(comandos_log)} comandos C2 enviados")

    # ── FASE 4: Simular ataque DDoS ──
    paso_fase(4, "ATAQUE — Simulando DDoS coordinado")
    # Los bots en estado "activo" o "escaneando" participan en el ataque.
    # Se calculan métricas simuladas de volumen y velocidad.
    bots_activos = sum(1 for b in bots if b["estado"] in ("activo", "escaneando"))
    ddos = simular_ddos(bots_activos)
    safe_print(color(f"    Tipo de ataque:     {ddos['tipo']}", 'red'))
    safe_print(color(f"    Bots participantes: {ddos['bots_participantes']}", 'yellow'))
    safe_print(color(f"    Paquetes/segundo:   {ddos['paquetes_por_segundo']:,}", 'yellow'))
    safe_print(color(f"    Ancho de banda:     {ddos['ancho_banda_mbps']} Mbps", 'yellow'))
    safe_print(color(f"    Objetivo ficticio:  {ddos['objetivo']}", 'red'))
    safe_print(color(f"    Duración:           {ddos['duracion_seg']} segundos", 'yellow'))
    log(f"Fase 4: DDoS simulado — {ddos['tipo']}, {ddos['paquetes_por_segundo']} pps")

    # ── FASE 5: Guardar configuración de la botnet ──
    paso_fase(5, "PERSISTENCIA — Guardando configuración de la botnet")
    # En un escenario real, el servidor C2 mantendría esta información en memoria
    # o en base de datos. Aquí la guardamos en JSON para análisis educativo.
    config = {
        "nombre_red": "SimNet-IRC",
        "servidor_c2": f"irc.{random.randint(1000, 9999)}.sim.lab",
        "puerto_irc": 6667,
        "canales": C2_CHANNELS,
        "total_bots": num_bots,
        "bots": bots,
        "ultimo_ataque": ddos,
        "creado": datetime.datetime.now().isoformat(),
    }
    with open(BOTNET_CONFIG, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=2, ensure_ascii=False)
    safe_print(color(f"  → {BOTNET_CONFIG} guardado ({os.path.getsize(BOTNET_CONFIG)} bytes)", 'green'))

    # ── FASE 6: Guardar log C2 ──
    write_log("BOTNET_C2", comandos_log, BOTNET_LOG)
    safe_print(color(f"  → {BOTNET_LOG} guardado", 'green'))

    # ── RESUMEN ──
    safe_print(color("\n" + "=" * 60, 'cyan'))
    safe_print(color("  RESUMEN DE LA SIMULACIÓN DE BOTNET", 'bold'))
    safe_print(color("=" * 60, 'cyan'))
    safe_print(color(f"  Bots generados:     {num_bots}", 'white'))
    safe_print(color(f"  Canales C2:         {len(C2_CHANNELS)}", 'white'))
    safe_print(color(f"  Comandos enviados:  {len(comandos_log)}", 'white'))
    safe_print(color(f"  Tipo de DDoS:       {ddos['tipo']}", 'red'))
    safe_print(color(f"  Archivos generados: bot_config.json, botnet_c2.log", 'white'))
    safe_print(color("=" * 60, 'cyan'))
    safe_print(color(
        "\n  NOTA: Todo es ficticio. No se contactan servidores reales.\n"
        "  Los datos se almacenan en directorio_pruebas/ para análisis.\n",
        'yellow'
    ))
    log("Simulación de botnet completada")
    write_log("botnet_sim", list(LOG_LINES))


if __name__ == "__main__":
    if "--help" in sys.argv:
        print(__doc__)
        sys.exit(0)
    if "--clean" in sys.argv:
        limpiar()
        sys.exit(0)
    ejecutar()
