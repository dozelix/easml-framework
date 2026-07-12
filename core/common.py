#!/usr/bin/env python3
"""
Funciones compartidas para todos los modulos del laboratorio.
"""
import os
import sys
import datetime
import hashlib
import glob


COLORS = {
    'reset':   '\033[0m',
    'red':     '\033[91m',
    'green':   '\033[92m',
    'yellow':  '\033[93m',
    'blue':    '\033[94m',
    'magenta': '\033[95m',
    'cyan':    '\033[96m',
    'bold':    '\033[1m',
}

LOG_LINES = []


def log(msg):
    ts = datetime.datetime.now().strftime("%H:%M:%S")
    LOG_LINES.append(f"[{ts}] {msg}")


def safe_print(msg):
    try:
        print(msg)
    except UnicodeEncodeError:
        print(msg.encode('ascii', errors='replace').decode('ascii'))


def color(text, c):
    return f"{COLORS.get(c, '')}{text}{COLORS['reset']}"


def banner(modulo_name, descripcion):
    safe_print(color(f"\n{'='*60}", 'cyan'))
    safe_print(color(f"  {modulo_name}", 'bold'))
    safe_print(color(f"  {descripcion}", 'cyan'))
    safe_print(color(f"{'='*60}\n", 'cyan'))


def traverse_lab_files(directory=None):
    if directory is None:
        directory = os.getcwd()
    files = []
    for f in sorted(os.listdir(directory)):
        path = os.path.join(directory, f)
        if os.path.isfile(path) and f != '__init__.py':
            files.append(path)
    return files


def hash_file(path):
    h = hashlib.sha256()
    try:
        with open(path, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b''):
                h.update(chunk)
        return h.hexdigest()
    except Exception:
        return None


def read_file(path):
    try:
        with open(path, 'rb') as f:
            return f.read()
    except Exception:
        return None


def is_lab_ready():
    required = ['documento.txt', 'script.py', 'imagen.png']
    return all(os.path.exists(f) for f in required)


def cleanup(files_to_remove=None, patterns=None):
    removed = 0
    if files_to_remove:
        for f in files_to_remove:
            if os.path.exists(f):
                try:
                    os.remove(f)
                    safe_print(color(f"  eliminado: {f}", 'green'))
                    removed += 1
                except Exception as e:
                    safe_print(color(f"  error al eliminar {f}: {e}", 'red'))
    if patterns:
        for pattern in patterns:
            for f in glob.glob(pattern):
                try:
                    if os.path.isdir(f):
                        import shutil
                        shutil.rmtree(f)
                    else:
                        os.remove(f)
                    safe_print(color(f"  eliminado: {f}", 'green'))
                    removed += 1
                except Exception:
                    pass
    return removed


def write_log(modulo_name, log_lines, filename=None):
    if filename is None:
        filename = f"{modulo_name}.log"
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(f"=== {modulo_name.upper()} - REGISTRO ===\n")
        f.write(f"Ejecucion: {datetime.datetime.now()}\n\n")
        for line in log_lines:
            f.write(line + "\n")
        f.write(f"{'='*40}\n")
    safe_print(color(f"\n  registro guardado en: {filename}", 'green'))
