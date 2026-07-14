#!/usr/bin/env python3
"""
Modulo 06 - Simulacion de puerta trasera (backdoor) educativa.

Crea archivos de configuracion con direcciones C2 falsas, un log
de reverse shell simulado y artefactos de persistencia.
No se realizan conexiones de red reales.

SOLO PARA USO EDUCATIVO EN ENTORNO CONTROLADO.

Uso:
    python modulos/06_backdoor/backdoor.py           Ejecutar simulacion
    python modulos/06_backdoor/backdoor.py --clean   Limpiar artefactos
    python modulos/06_backdoor/backdoor.py --help    Mostrar ayuda
"""
import os
import sys
import json
import time

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, ROOT)

from modulos.common.utils import (
    banner, color, safe_print, log, LOG_LINES,
    write_log, cleanup, hash_file as _hash_file, find_lab_dir,
)

# ── Ruta del directorio de pruebas ──
LAB_DIR = find_lab_dir(ROOT)

# ── Marcadores de IOC ──
C2_MARKER = "C2_BACKDOOR_SIMULATION"
SHELL_MARKER = "SHELL_SIMULATION"


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
#  FUNCIONES DE CREACION DE ARTEFACTOS
# ══════════════════════════════════════════════════════════════

def crear_config_c2():
    """
    Crea un archivo de configuracion C2 simulado.

    En un backdoor real, este archivo contendria las direcciones
    de los servidores C2, intervalos de heartbeat, y configuracion
    de cifrado para las comunicaciones.
    """
    safe_print(color("\n  [1/4] Creando configuracion C2...\n", 'cyan'))
    os.makedirs(LAB_DIR, exist_ok=True)
    config_path = os.path.join(LAB_DIR, "c2_config.json")

    config = {
        "_marker": C2_MARKER,
        "_tipo": "CONFIGURACION C2 SIMULADA - No es malware real",
        "servidores_c2": [
            {
                "direccion": "192.168.1.100",
                "puerto": 443,
                "protocolo": "HTTPS",
                "prioridad": 1,
                "activo": True,
                "nota": "Servidor primario simulado",
            },
            {
                "direccion": "10.0.0.50",
                "puerto": 8443,
                "protocolo": "HTTPS",
                "prioridad": 2,
                "activo": True,
                "nota": "Servidor de respaldo simulado",
            },
            {
                "direccion": "172.16.0.25",
                "puerto": 80,
                "protocolo": "HTTP",
                "prioridad": 3,
                "activo": False,
                "nota": "Servidor fallback (desactivado)",
            },
        ],
        "configuracion": {
            "intervalo_heartbeat": 30,
            "max_reintentos": 5,
            "timeoutConexion": 10,
            "cifrado": "AES-256-GCM",
            "compress": True,
            "jitter": 0.2,
        },
        "persistencia": {
            "metodo": "TareaProgramada",
            "nombre_tarea": "SystemUpdateCheck",
            "frecuencia": "Al inicio de sesion",
            "registro_clave": "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Run",
            "valor_registro": "WindowsUpdate",
        },
        "comandos_soportados": [
            "shell", "upload", "download", "screenshot",
            "keylog_start", "keylog_stop", "persist", "exit",
        ],
    }

    with open(config_path, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=2, ensure_ascii=False)

    safe_print(color(f"    Archivo: directorio_pruebas/c2_config.json", 'yellow'))
    safe_print(color(f"    Tamano: {os.path.getsize(config_path)} bytes", 'yellow'))
    safe_print(color(f"    Hash SHA-256: {_short_hash(config_path)}", 'yellow'))
    safe_print(color(
        f"    Servidores C2 configurados: {len(config['servidores_c2'])}",
        'cyan'
    ))
    for srv in config['servidores_c2']:
        estado = "ACTIVO" if srv['activo'] else "DESACTIVADO"
        safe_print(color(
            f"      - {srv['direccion']}:{srv['puerto']} "
            f"({srv['protocolo']}) [{estado}]",
            'red' if srv['activo'] else 'yellow'
        ))
    log("Configuracion C2 creada: directorio_pruebas/c2_config.json")
    return config_path


def crear_log_reverse_shell():
    """
    Crea un log simulado de reverse shell.

    En un incidente real, este log mostraria la actividad del atacante:
    comandos ejecutados, archivos descargados, datos exfiltrados.
    """
    safe_print(color("\n  [2/4] Creando registro de reverse shell...\n", 'cyan'))
    log_path = os.path.join(LAB_DIR, "shell_log.txt")

    contenido = f"""=== REGISTRO DE REVERSE SHELL SIMULADO ===
Tipo: {SHELL_MARKER}
Fecha: 2026-01-15 14:30:00
Victima: 192.168.1.50 (simulada)
Atacante: 192.168.1.100:443 (simulado)

--- Sesion iniciada ---
[14:30:01] Conexion entrante desde 192.168.1.100:443
[14:30:01] Protocolo: HTTPS (tunel cifrado simulado)
[14:30:02] Sesion establecida correctamente
[14:30:05] > whoami
[14:30:05] < usuario_simulado (SIMULACION)
[14:30:08] > hostname
[14:30:08] < PC-VICTIMA-SIM (SIMULACION)
[14:30:12] > ipconfig
[14:30:12] < IPv4: 192.168.1.50 (SIMULACION)
[14:30:15] > dir
[14:30:15] < Directorio: C:\\Users\\usuario (SIMULACION)
[14:30:20] > systeminfo
[14:30:20] < SO: Windows 10 Pro (SIMULACION)
[14:30:25] > tasklist
[14:30:25] < Procesos activos: 45 (SIMULACION)
[14:30:30] > exit
[14:30:30] Sesion cerrada por el atacante

--- Estadisticas de sesion ---
Duracion: 30 segundos
Comandos ejecutados: 7
Bytes transferidos: 2.4 KB (SIMULADO)
Metodo de persistencia: Tarea programada

FIN DEL REGISTRO - SIMULACION EDUCATIVA
"""
    with open(log_path, 'w', encoding='utf-8') as f:
        f.write(contenido)

    safe_print(color(f"    Archivo: directorio_pruebas/shell_log.txt", 'yellow'))
    safe_print(color(f"    Tamano: {os.path.getsize(log_path)} bytes", 'yellow'))
    safe_print(color(f"    Hash SHA-256: {_short_hash(log_path)}", 'yellow'))
    safe_print(color(f"    Comandos simulados en log: 7", 'cyan'))
    log("Registro de reverse shell creado: directorio_pruebas/shell_log.txt")
    return log_path


def crear_persistencia_reg():
    """
    Crea un archivo .reg simulado de persistencia.

    En un ataque real, estas claves de registro fuerzan la ejecucion
    del backdoor cada vez que el usuario inicia sesion en Windows.
    """
    safe_print(color("\n  [3/4] Creando clave de persistencia...\n", 'cyan'))
    reg_path = os.path.join(LAB_DIR, "persistence.reg")

    contenido = f"""Windows Registry Editor Version 5.00

; {C2_MARKER}
; SIMULACION EDUCATIVA - No es malware real
; Este archivo simula una clave de registro de persistencia

[HKEY_CURRENT_USER\\Software\\Microsoft\\Windows\\CurrentVersion\\Run]
"WindowsUpdate"="C:\\\\Windows\\\\System32\\\\cmd.exe /c start /min updater.exe"
; La linea anterior simularia el inicio automatico del backdoor

[HKEY_CURRENT_USER\\Software\\Microsoft\\Windows\\CurrentVersion\\RunOnce]
"SystemCheck"="powershell.exe -WindowStyle Hidden -File update.ps1"
; Simulacion de ejecucion oculta de PowerShell

; --- Fin de la simulacion ---
"""
    with open(reg_path, 'w', encoding='utf-8') as f:
        f.write(contenido)

    safe_print(color(f"    Archivo: directorio_pruebas/persistence.reg", 'yellow'))
    safe_print(color(f"    Tamano: {os.path.getsize(reg_path)} bytes", 'yellow'))
    safe_print(color(f"    Hash SHA-256: {_short_hash(reg_path)}", 'yellow'))
    safe_print(color(f"    Claves simuladas: Run + RunOnce", 'cyan'))
    log("Clave de persistencia creada: directorio_pruebas/persistence.reg")
    return reg_path


def crear_startup_script():
    """
    Crea un script de inicio simulado.

    En un ataque real, este script se ejecutaria al iniciar Windows
    para establecer la conexion C2 automaticamente.
    """
    safe_print(color("\n  [4/4] Creando script de inicio...\n", 'cyan'))
    bat_path = os.path.join(LAB_DIR, "startup.bat")

    contenido = f"""@echo off
REM === {C2_MARKER} ===
REM SIMULACION EDUCATIVA - No es malware real
REM Este script simula un mecanismo de persistencia

REM Simulacion: verificar si el backdoor ya esta activo
echo [SIMULACION] Verificando estado del backdoor...

REM Simulacion: iniciar conexion C2
echo [SIMULACION] Conectando a servidor C2...
echo [SIMULACION] Servidor: 192.168.1.100:443 (SIMULADO)

REM Simulacion: establecer tunel
echo [SIMULACION] Tunel cifrado establecido

REM Simulacion: ejecutar payload oculto
echo [SIMULACION] Payload ejecutado correctamente

echo [SIMULACION] Script completado - No se ejecuto nada real
"""
    with open(bat_path, 'w', encoding='utf-8') as f:
        f.write(contenido)

    safe_print(color(f"    Archivo: directorio_pruebas/startup.bat", 'yellow'))
    safe_print(color(f"    Tamano: {os.path.getsize(bat_path)} bytes", 'yellow'))
    safe_print(color(f"    Hash SHA-256: {_short_hash(bat_path)}", 'yellow'))
    log("Script de inicio creado: directorio_pruebas/startup.bat")
    return bat_path


# ══════════════════════════════════════════════════════════════
#  VISUALIZACION EDUCATIVA
# ══════════════════════════════════════════════════════════════

def mostrar_flujo_c2():
    """Muestra una representacion visual de la comunicacion C2."""
    safe_print(color("\n  ═══ FLUJO DE COMUNICACION C2 SIMULADO ═══\n", 'bold'))
    safe_print(color(
        "  Victima (simulada)                 Servidor C2 (simulado)",
        'cyan'
    ))
    safe_print(color("  " + "=" * 60, 'cyan'))
    safe_print(color(
        "  [Backdoor] --Heartbeat (30s)-----> [C2 Server]",
        'red'
    ))
    safe_print(color(
        "  [Backdoor] <------- Comando ------ [C2 Server]",
        'yellow'
    ))
    safe_print(color(
        "  [Backdoor] ---- Respuesta -------> [C2 Server]",
        'red'
    ))
    safe_print(color(
        "  [Backdoor] ---- Datos exfil. ----> [C2 Server]",
        'magenta'
    ))
    safe_print(color("  " + "=" * 60, 'cyan'))
    safe_print(color(
        "  * Todo esto es SIMULADO. No hay conexiones reales.\n",
        'yellow'
    ))


def mostrar_notas_educativas():
    """Explica al estudiante por que las backdoors son peligrosas."""
    safe_print(color("\n  ═══ NOTAS EDUCATIVAS ═══\n", 'bold'))

    safe_print(color("  Por que las backdoors son peligrosas:", 'cyan'))
    safe_print("  - Mantienen acceso persistente al sistema comprometido")
    safe_print("  - Permiten movilidad lateral en la red")
    safe_print("  - Evaden firewalls usando conexiones salientes (HTTPS)")
    safe_print("  - Pueden permanecer ocultas por meses o anios")
    safe_print("  - Son el punto de entrada para ransomware y exfiltracion")

    safe_print(color("\n  Tecnicas de evasion comunes:", 'cyan'))
    safe_print("  - Comunicacion via HTTPS (443) para camuflarse")
    safe_print("  - Jitter en heartbeat para evadir deteccion temporal")
    safe_print("  - Encriptacion AES-256-GCM para evadir IDS")
    safe_print("  - Domain Fronting para esconder el C2 real")

    safe_print(color("\n  En esta simulacion:", 'cyan'))
    safe_print("  - No se establecio ninguna conexion de red real")
    safe_print("  - Todos los archivos son texto plano inofensivo")
    safe_print("  - Las direcciones IP y puertos son ficticios")
    safe_print("  - Todo puede limpiarse con --clean\n")


# ══════════════════════════════════════════════════════════════
#  LIMPIEZA
# ══════════════════════════════════════════════════════════════

def limpiar():
    """Elimina todos los artefactos generados por la simulacion."""
    banner("MODULO 06 - PUERTA TRASERA (BACKDOOR)", "LIMPIEZA DE ARTEFACTOS")

    backdoor_files = [
        'c2_config.json', 'shell_log.txt', 'persistence.reg', 'startup.bat',
    ]
    removed = 0
    for fname in backdoor_files:
        fpath = os.path.join(LAB_DIR, fname)
        if os.path.exists(fpath):
            try:
                os.remove(fpath)
                safe_print(color(f"  [+] Eliminado: directorio_pruebas/{fname}", 'green'))
                removed += 1
            except Exception as e:
                safe_print(color(f"  [-] Error al eliminar {fname}: {e}", 'red'))

    # Eliminar logs en lab_data/logs/
    for log_name in ['06_backdoor.log']:
        log_path = os.path.join(find_lab_dir(ROOT), '..', 'logs', log_name)
        if os.path.exists(log_path):
            os.remove(log_path)
            safe_print(color(f"  [+] Eliminado: {log_name}", 'green'))
            removed += 1

    safe_print(color(f"\n  Limpieza completada: {removed} archivos eliminados.\n", 'green'))


# ══════════════════════════════════════════════════════════════
#  AYUDA
# ══════════════════════════════════════════════════════════════

def mostrar_ayuda():
    safe_print(color("\nUso: python backdoor.py [opcion]", 'cyan'))
    safe_print(color("\nOpciones:", 'bold'))
    safe_print("  (sin args)  Ejecutar la simulacion de backdoor")
    safe_print("  --clean     Eliminar todos los artefactos generados")
    safe_print("  --help      Mostrar esta ayuda")
    safe_print(color("\nDescripcion:", 'bold'))
    safe_print("  Simula una puerta trasera con configuracion C2,")
    safe_print("  reverse shell y persistencia. NO realiza conexiones")
    safe_print("  de red reales. Los archivos son texto inofensivo.")
    safe_print("  Opera exclusivamente dentro de directorio_pruebas/.")
    safe_print(color("\nEjemplo:", 'bold'))
    safe_print("  python modulos/06_backdoor/backdoor.py")
    safe_print("  python modulos/06_backdoor/backdoor.py --clean\n")


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

    banner("MODULO 06 - PUERTA TRASERA (BACKDOOR)",
           "Simulacion de C2 y reverse shell")
    safe_print(color("  Entorno: laboratorio educativo controlado", 'cyan'))
    safe_print(color("  No se realizan conexiones de red reales\n", 'yellow'))

    # ── FASE 1: Crear artefactos de backdoor ──
    _paso_fase(1, "CREANDO ARTEFACTOS DE BACKDOOR")
    safe_print(color(
        "  Creando 4 artefactos de backdoor simulados...\n",
        'cyan'
    ))

    archivos = [
        crear_config_c2(),
        crear_log_reverse_shell(),
        crear_persistencia_reg(),
        crear_startup_script(),
    ]

    safe_print(color(f"\n  Total artefactos creados: {len(archivos)}", 'green'))

    # ── FASE 2: Visualizacion del flujo C2 ──
    _paso_fase(2, "FLUJO DE COMUNICACION C2 SIMULADO")
    mostrar_flujo_c2()

    # ── FASE 3: Notas educativas ──
    mostrar_notas_educativas()

    # Guardar registro
    write_log("06_backdoor", list(LOG_LINES))
    safe_print(color("  Simulacion completada.\n", 'green'))


if __name__ == "__main__":
    main()
