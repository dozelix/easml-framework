#!/usr/bin/env python3
"""
Modulo 07 - Simulacion de rootkit educativo.

Crea archivos ocultos y manipula una lista de procesos simulada
para demostrar como los rootkits se ocultan del sistema.

SOLO PARA USO EDUCATIVO EN ENTORNO CONTROLADO.

Uso:
    python modulos/07_rootkit/rootkit.py           Ejecutar simulacion
    python modulos/07_rootkit/rootkit.py --clean   Limpiar artefactos
    python modulos/07_rootkit/rootkit.py --help    Mostrar ayuda
"""
import os
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, ROOT)

from core.common import (
    banner, color, safe_print, log, LOG_LINES,
    write_log, cleanup, hash_file, find_lab_dir,
)

# ── Ruta del directorio de pruebas ──
LAB_DIR = find_lab_dir(ROOT)

# ── Marcador de deteccion ──
ROOTKIT_MARKER = "ROOTKIT_SIMULATION"

# ── Archivos ocultos que crea el rootkit simulado ──
ARCHIVOS_OCULTOS = [
    (".hidden_system", "Archivo de configuracion del rootkit"),
    (".config_sys.dat", "Base de datos de configuracion oculta"),
    (".rootkit_payload", "Payload del rootkit (simulado)"),
    (".driver_sim.sys", "Driver falso del rootkit"),
]

# ── Lista de procesos: ANTES del rootkit ──
PROCESOS_NORMAL = [
    ("PID 001", "System", "NT Kernel & System", "4.2 MB"),
    ("PID 004", "smss.exe", "Session Manager", "89 KB"),
    ("PID 224", "explorer.exe", "Windows Explorer", "4.1 MB"),
    ("PID 340", "svchost.exe", "Service Host", "28.3 MB"),
    ("PID 512", "chrome.exe", "Google Chrome", "187 MB"),
    ("PID 680", "code.exe", "Visual Studio Code", "94 MB"),
    ("PID 725", "alacritty.exe", "Terminal", "12 MB"),
    ("PID 842", "python.exe", "Python Interpreter", "18 MB"),
]

# ── Lista de procesos: DESPUES del rootkit (incluye ocultos) ──
PROCESOS_CON_ROOTKIT = [
    ("PID 001", "System", "NT Kernel & System", "4.2 MB"),
    ("PID 004", "smss.exe", "Session Manager", "89 KB"),
    ("PID 224", "explorer.exe", "Windows Explorer", "4.1 MB"),
    ("PID 340", "svchost.exe", "Service Host", "28.3 MB"),
    ("PID 512", "chrome.exe", "Google Chrome", "187 MB"),
    ("PID 680", "code.exe", "Visual Studio Code", "94 MB"),
    ("PID 725", "alacritty.exe", "Terminal", "12 MB"),
    ("PID 842", "python.exe", "Python Interpreter", "18 MB"),
    # Los siguientes estarian OCULTOS por el rootkit:
    ("PID 1024", "rootkit_svc.exe", "Rootkit Service", "2.1 MB"),
    ("PID 1025", "c2_beacon.exe", "C2 Beacon", "890 KB"),
    ("PID 1026", "keylog_drv.sys", "Keylogger Driver", "156 KB"),
]

# Nombres de procesos que el rootkit oculta
PROC_OULTOS_NOMBRES = ["rootkit_svc.exe", "c2_beacon.exe", "keylog_drv.sys"]


# ══════════════════════════════════════════════════════════════
#  FUNCIONES AUXILIARES
# ══════════════════════════════════════════════════════════════

def _paso_fase(num, titulo):
    safe_print(color(f"\n  [FASE {num}] {titulo}", 'yellow'))
    safe_print(color(f"  {'─' * 55}", 'yellow'))
    time.sleep(0.3)


# ══════════════════════════════════════════════════════════════
#  FUNCIONES DE SIMULACION
# ══════════════════════════════════════════════════════════════

def crear_archivos_ocultos():
    """
    Crea archivos ocultos simulando un rootkit.

    En Linux, los archivos que comienzan con punto (.) no se
    muestran con 'ls' sin la opcion '-a'. Un rootkit real
    usaria tecnicas mucho mas sofisticadas (intercepcion de
    syscalls) para ocultar archivos.
    """
    _paso_fase(1, "CREANDO ARCHIVOS OCULTOS DEL ROOTKIT")
    os.makedirs(LAB_DIR, exist_ok=True)
    creados = []

    for fname, desc in ARCHIVOS_OCULTOS:
        fpath = os.path.join(LAB_DIR, fname)
        contenido = f"""{ROOTKIT_MARKER}
# Archivo: {fname}
# Descripcion: {desc}
# Este es un archivo educativo INOFENSIVO
# Simula como un rootkit oculta archivos con prefijo dot

import os
def persistir():
    # En un rootkit real, este archivo se ocultaria
    # manipulando las llamadas al sistema
    pass

def ocultar_procesos():
    # Filtraria la lista de procesos para no mostrar
    # los procesos maliciosos
    pass
"""
        with open(fpath, 'w', encoding='utf-8') as f:
            f.write(contenido)
        creados.append(fpath)
        safe_print(color(f"  [+] {fname}", 'yellow'))
        safe_print(color(f"      Descripcion: {desc}", 'cyan'))
        safe_print(color(
            f"      Visible con: ls -la (archivos ocultos)", 'cyan'
        ))
        log(f"Archivo oculto creado: directorio_pruebas/{fname}")
        time.sleep(0.1)

    safe_print(color(
        f"\n  Total archivos ocultos creados: {len(creados)}", 'green'
    ))
    return creados


def mostrar_procesos_antes():
    """Muestra la lista de procesos normal (sin rootkit)."""
    _paso_fase(2, "LISTA DE PROCESOS ANTES DEL ROOTKIT")
    safe_print(color(
        f"  {'PID':<8} {'Nombre':<25} {'Descripcion':<30} {'RAM':<10}",
        'bold'
    ))
    safe_print(color("  " + "=" * 73, 'cyan'))
    for pid, name, desc, ram in PROCESOS_NORMAL:
        safe_print(color(
            f"  {pid:<8} {name:<25} {desc:<30} {ram:<10}", 'green'
        ))
    safe_print(color(
        f"\n  Total procesos visibles: {len(PROCESOS_NORMAL)}", 'green'
    ))
    safe_print(color(
        "  (Todos los procesos son legitimos y visibles)", 'cyan'
    ))


def mostrar_procesos_despues():
    """
    Muestra la lista de procesos DESPUES de la infeccion por rootkit.

    El rootkit oculta 3 procesos maliciosos de la vista del usuario.
    En un sistema real, esto se logra interceptando las llamadas
    NtQuerySystemInformation y filtrando los resultados.
    """
    _paso_fase(3, "LISTA DE PROCESOS DESPUES DEL ROOTKIT")

    visibles = []
    ocultos = []
    for proc in PROCESOS_CON_ROOTKIT:
        es_oculto = any(h in proc[1] for h in PROC_OULTOS_NOMBRES)
        if es_oculto:
            ocultos.append(proc)
        else:
            visibles.append(proc)

    safe_print(color(
        f"  {'PID':<8} {'Nombre':<25} {'Descripcion':<30} {'RAM':<10}",
        'bold'
    ))
    safe_print(color("  " + "=" * 73, 'cyan'))
    for pid, name, desc, ram in visibles:
        safe_print(color(
            f"  {pid:<8} {name:<25} {desc:<30} {ram:<10}", 'green'
        ))

    safe_print(color(
        f"\n  Total procesos visibles: {len(visibles)}", 'green'
    ))
    safe_print(color(
        f"  Procesos OCULTOS por rootkit: {len(ocultos)}", 'red'
    ))

    for pid, name, desc, ram in ocultos:
        safe_print(color(
            f"    [OCULTO] {name} ({desc}) - {ram}", 'red'
        ))

    return ocultos


def guardar_lista_procesos(procesos_ocultos):
    """
    Guarda la lista de procesos simulada en un archivo.
    El archivo contiene el marcador ROOTKIT_SIMULATION para
    que la defensa lo detecte.
    """
    _paso_fase(4, "GUARDANDO LISTA DE PROCESOS MANIPULADA")
    process_file = os.path.join(LAB_DIR, "process_list.txt")

    with open(process_file, 'w', encoding='utf-8') as f:
        f.write("=== LISTA DE PROCESOS DEL SISTEMA (SIMULADA) ===\n")
        f.write("Fecha: 2026-01-15 15:00:00\n")
        f.write("SO: Windows 10 Pro (SIMULACION)\n\n")

        f.write("Lista visible (sin rootkit):\n")
        for pid, name, desc, ram in PROCESOS_NORMAL:
            f.write(f"  {pid:<8} {name:<25} {desc:<30} {ram:<10}\n")
        f.write(f"\n  Total: {len(PROCESOS_NORMAL)} procesos\n\n")

        f.write("Lista completa (con rootkit):\n")
        for pid, name, desc, ram in PROCESOS_CON_ROOTKIT:
            oculto = any(h in name for h in PROC_OULTOS_NOMBRES)
            marca = " [OCULTO]" if oculto else ""
            f.write(
                f"  {pid:<8} {name:<25} {desc:<30} {ram:<10}{marca}\n"
            )
        f.write(
            f"\n  Total real: {len(PROCESOS_CON_ROOTKIT)} procesos\n"
        )
        f.write(
            f"  Ocultos: {len(procesos_ocultos)}\n"
        )
        f.write(f"\n{ROOTKIT_MARKER}\n")

    safe_print(color(f"    Archivo: directorio_pruebas/process_list.txt", 'yellow'))
    safe_print(color(f"    Tamano: {os.path.getsize(process_file)} bytes", 'yellow'))
    h = hash_file(process_file)
    safe_print(color(
        f"    Hash SHA-256: {h[:16]}..." if h else "    Hash: N/A", 'yellow'
    ))
    log("Lista de procesos manipulada guardada")
    return process_file


def mostrar_tecnicas_ocultamiento():
    """Explica las tecnicas de ocultamiento de rootkits."""
    _paso_fase(5, "TECNICAS DE OCULTAMIENTO SIMULADAS")

    tecnicas = [
        ("Prefijo dot (.)",
         "Archivos como .hidden_system no se muestran con ls sin -a"),
        ("Filtrado de procesos",
         "El rootkit interceptaria tasklist/ps y ocultaria procesos"),
        ("Intercepcion de API",
         "Hook de FindFirstFile/FindNextFile para filtrar archivos"),
        ("DKOM",
         "Manipulacion directa de estructuras del kernel"),
        ("SSDT hooking",
         "Modificacion de la System Service Descriptor Table"),
        ("MBR/UEFI infection",
         "Bootkit que se ejecuta antes del SO"),
    ]

    for i, (tech, desc) in enumerate(tecnicas, 1):
        safe_print(color(f"    {i}. {tech}", 'yellow'))
        safe_print(color(f"       {desc}", 'cyan'))
    safe_print("")


def mostrar_notas_educativas():
    """Explica al estudiante por que los rootkits son peligrosos."""
    safe_print(color("\n  ═══ NOTAS EDUCATIVAS ═══\n", 'bold'))

    safe_print(color("  Por que los rootkits son peligrosos:", 'cyan'))
    safe_print("  - Se ejecutan a nivel kernel, con control total del SO")
    safe_print("  - Ocultan otros malware del sistema")
    safe_print("  - Son extremadamente dificiles de detectar")
    safe_print("  - Pueden sobrevivir a reinstalaciones (bootkits)")
    safe_print("  - Pueden manipular el hardware (Hypervisor rootkits)")

    safe_print(color("\n  Deteccion de rootkits reales:", 'cyan'))
    safe_print("  - Herramientas offline (GMER, TDSSKiller)")
    safe_print("  - Comparar listas de procesos desde USB booteable")
    safe_print("  - Monitorear consumo inusual de recursos")
    safe_print("  - Verificar integridad del MBR/UEFI")

    safe_print(color("\n  En esta simulacion:", 'cyan'))
    safe_print("  - Los archivos ocultos son texto plano inofensivo")
    safe_print("  - La lista de procesos es ficticia")
    safe_print("  - No se modifico ningun sistema real")
    safe_print("  - Todo puede limpiarse con --clean\n")


# ══════════════════════════════════════════════════════════════
#  LIMPIEZA
# ══════════════════════════════════════════════════════════════

def limpiar():
    """Elimina todos los artefactos generados por la simulacion."""
    banner("MODULO 07 - ROOTKIT", "LIMPIEZA DE ARTEFACTOS")
    removed = 0

    # Eliminar archivos ocultos
    for fname, _ in ARCHIVOS_OCULTOS:
        fpath = os.path.join(LAB_DIR, fname)
        if os.path.exists(fpath):
            try:
                os.remove(fpath)
                safe_print(color(f"  [+] Eliminado: directorio_pruebas/{fname}", 'green'))
                removed += 1
            except Exception:
                pass

    # Eliminar lista de procesos
    proc_file = os.path.join(LAB_DIR, "process_list.txt")
    if os.path.exists(proc_file):
        os.remove(proc_file)
        safe_print(color("  [+] Eliminado: directorio_pruebas/process_list.txt", 'green'))
        removed += 1

    # Eliminar log
    log_path = os.path.join(ROOT, "07_rootkit.log")
    if os.path.exists(log_path):
        os.remove(log_path)
        safe_print(color("  [+] Eliminado: 07_rootkit.log", 'green'))
        removed += 1

    safe_print(color(f"\n  Limpieza completada: {removed} archivos eliminados.\n", 'green'))


# ══════════════════════════════════════════════════════════════
#  AYUDA
# ══════════════════════════════════════════════════════════════

def mostrar_ayuda():
    safe_print(color("\nUso: python rootkit.py [opcion]", 'cyan'))
    safe_print(color("\nOpciones:", 'bold'))
    safe_print("  (sin args)  Ejecutar la simulacion de rootkit")
    safe_print("  --clean     Eliminar todos los artefactos generados")
    safe_print("  --help      Mostrar esta ayuda")
    safe_print(color("\nDescripcion:", 'bold'))
    safe_print("  Simula un rootkit que oculta archivos y procesos.")
    safe_print("  Los archivos generados son INOFENSIVOS.")
    safe_print("  Opera exclusivamente dentro de directorio_pruebas/.")
    safe_print(color("\nEjemplo:", 'bold'))
    safe_print("  python modulos/07_rootkit/rootkit.py")
    safe_print("  python modulos/07_rootkit/rootkit.py --clean\n")


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

    banner("MODULO 07 - ROOTKIT",
           "Simulacion de ocultamiento de archivos y procesos")
    safe_print(color("  Entorno: laboratorio educativo controlado", 'cyan'))
    safe_print(color("  Los archivos generados son INOFENSIVOS\n", 'yellow'))

    # Crear archivos ocultos del rootkit
    crear_archivos_ocultos()

    # Mostrar procesos antes y despues del rootkit
    mostrar_procesos_antes()
    ocultos = mostrar_procesos_despues()

    # Guardar lista de procesos manipulada
    guardar_lista_procesos(ocultos)

    # Mostrar tecnicas y notas
    mostrar_tecnicas_ocultamiento()
    mostrar_notas_educativas()

    write_log("07_rootkit", list(LOG_LINES), os.path.join(ROOT, "07_rootkit.log"))
    safe_print(color("  Simulacion completada.\n", 'green'))


if __name__ == "__main__":
    main()
