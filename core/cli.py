#!/usr/bin/env python3
"""
CLI interactivo del laboratorio de malware educa tivo.
Permite navegar y ejecutar los 14 modulos desde un unico punto de entrada.

Uso:
    python -m core.cli
    python -m core.cli --list
    python -m core.cli 01
    python -m core.cli 01 --defensa
"""
import os
import sys
import subprocess
import importlib.util

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODULOS_DIR = os.path.join(ROOT, 'modulos')

MODULOS = [
    ("01", "ransomware",      "Cifrado de archivos + nota de rescate"),
    ("02", "wiper",           "Corrupcion/eliminacion de archivos"),
    ("03", "keylogger",       "Captura de pulsaciones de teclado"),
    ("04", "worm",            "Auto-replicacion entre directorios"),
    ("05", "trojan",          "Disfraz de legitimo + payload oculto"),
    ("06", "backdoor",        "Acceso persistente + C2 simulado"),
    ("07", "rootkit",         "Ocultacion de procesos/archivos"),
    ("08", "botnet",          "Red de bots + DDoS simulado"),
    ("09", "steganography",   "Ocultacion de datos en imagenes"),
    ("10", "fileless",        "Ejecucion sin archivos en disco"),
    ("11", "logic_bomb",      "Payload con detonante condicional"),
    ("12", "cryptominer",     "Mineria CPU simulada"),
    ("13", "supply_chain",    "Compromiso de dependencias"),
    ("14", "dns_tunneling",   "Exfiltracion via consultas DNS"),
]


def banner():
    print("\033[96m" + "=" * 60 + "\033[0m")
    print("\033[1m  LABORATORIO DE MALWARE EDUCATIVO\033[0m")
    print("\033[96m  14 modulos de simulacion + defensa\033[0m")
    print("\033[96m" + "=" * 60 + "\033[0m")


def listar_modulos():
    print(f"\n{'#':<4} {'Modulo':<18} {'Descripcion'}")
    print("-" * 60)
    for num, nombre, desc in MODULOS:
        print(f"  {num}   {nombre:<18} {desc}")
    print(f"\n  Uso: python -m core.cli <numero>")
    print(f"  Defensa: python -m core.cli <numero> --defensa")
    print(f"  Setup: python core/lab_setup.py\n")


def ejecutar_modulo(numero, defensa=False):
    match = [m for m in MODULOS if m[0] == numero]
    if not match:
        print(f"\033[91m  Error: modulo '{numero}' no encontrado\033[0m")
        listar_modulos()
        return

    _, nombre, _ = match[0]
    dir_modulo = os.path.join(MODULOS_DIR, f"{numero}_{nombre}")

    if defensa:
        script = os.path.join(dir_modulo, "defensa.py")
    else:
        script = os.path.join(dir_modulo, f"{nombre}.py")

    if not os.path.exists(script):
        print(f"\033[91m  Error: {script} no encontrado\033[0m")
        return

    print(f"\n\033[93m  Ejecutando: {script}\033[0m\n")
    result = subprocess.run(
        [sys.executable, script],
        cwd=ROOT,
    )
    if result.returncode != 0:
        print(f"\n\033[91m  El script termino con codigo {result.returncode}\033[0m")


def setup_lab():
    script = os.path.join(ROOT, "core", "lab_setup.py")
    print(f"\n\033[93m  Ejecutando: {script}\033[0m\n")
    subprocess.run([sys.executable, script], cwd=ROOT)


def main():
    args = sys.argv[1:]

    if not args:
        banner()
        listar_modulos()
        return

    if args[0] in ('--list', '-l', 'list'):
        banner()
        listar_modulos()
        return

    if args[0] in ('--setup', '-s'):
        setup_lab()
        return

    if args[0] in ('--help', '-h', 'help'):
        banner()
        print("  Uso:")
        print("    python -m core.cli              Mostrar menu")
        print("    python -m core.cli --list       Listar modulos")
        print("    python -m core.cli --setup      Generar archivos de prueba")
        print("    python -m core.cli <numero>     Ejecutar simulacion")
        print("    python -m core.cli <numero> --defensa  Ejecutar defensa")
        print("    python -m core.cli <numero> --clean    Limpiar artefactos")
        print("    python -m core.cli all          Ejecutar todos los modulos")
        print("    python -m core.cli all --clean  Limpiar todos los modulos\n")
        return

    if args[0] == 'all':
        banner()
        defensa = '--defensa' in args
        clean = '--clean' in args
        for num, nombre, desc in MODULOS:
            print(f"\n\033[95m{'='*60}\033[0m")
            print(f"\033[1m  [{num}] {nombre}\033[0m")
            print(f"\033[95m{'='*60}\033[0m")
            dir_modulo = os.path.join(MODULOS_DIR, f"{num}_{nombre}")
            if clean:
                script = os.path.join(dir_modulo, f"{nombre}.py")
                subprocess.run([sys.executable, script, '--clean'], cwd=ROOT)
            elif defensa:
                script = os.path.join(dir_modulo, "defensa.py")
                subprocess.run([sys.executable, script], cwd=ROOT)
            else:
                script = os.path.join(dir_modulo, f"{nombre}.py")
                subprocess.run([sys.executable, script], cwd=ROOT)
        return

    numero = args[0].zfill(2)
    defensa = '--defensa' in args
    ejecutar_modulo(numero, defensa)


if __name__ == "__main__":
    main()
