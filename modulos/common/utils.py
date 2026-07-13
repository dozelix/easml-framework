import datetime
import glob
import hashlib
import os
import shutil
from typing import Iterable, Optional

from .paths import resolve_lab_paths


COLORS = {
    'reset': '\033[0m',
    'red': '\033[91m',
    'green': '\033[92m',
    'yellow': '\033[93m',
    'blue': '\033[94m',
    'magenta': '\033[95m',
    'cyan': '\033[96m',
    'bold': '\033[1m',
}

LOG_LINES = []


def find_lab_dir(start=None):
    """Devuelve la ruta absoluta de directorio_pruebas desde la raíz del laboratorio."""
    return resolve_lab_paths(start)['lab_dir']


def log(msg):
    ts = datetime.datetime.now().strftime('%H:%M:%S')
    LOG_LINES.append(f'[{ts}] {msg}')


def safe_print(msg):
    try:
        print(msg)
    except UnicodeEncodeError:
        print(msg.encode('ascii', errors='replace').decode('ascii'))


def color(text, c):
    return f"{COLORS.get(c, '')}{text}{COLORS['reset']}"


def banner(modulo_name, descripcion):
    safe_print(color(f"\n{'=' * 60}", 'cyan'))
    safe_print(color(f"  {modulo_name}", 'bold'))
    safe_print(color(f"  {descripcion}", 'cyan'))
    safe_print(color(f"{'=' * 60}\n", 'cyan'))


def traverse_lab_files(directory=None):
    if directory is None:
        directory = find_lab_dir()
    if not os.path.isdir(directory):
        return []
    files = []
    for entry in sorted(os.listdir(directory)):
        path = os.path.join(directory, entry)
        if os.path.isfile(path) and entry != '__init__.py':
            files.append(path)
    return files


def hash_file(path):
    h = hashlib.sha256()
    try:
        with open(path, 'rb') as handle:
            for chunk in iter(lambda: handle.read(4096), b''):
                h.update(chunk)
        return h.hexdigest()
    except Exception:
        return None


def read_file(path):
    try:
        with open(path, 'rb') as handle:
            return handle.read()
    except Exception:
        return None


def is_lab_ready():
    lab_dir = find_lab_dir()
    required = ['documento.txt', 'script.py', 'imagen.png']
    return all(os.path.exists(os.path.join(lab_dir, name)) for name in required)


def cleanup(files_to_remove: Optional[Iterable[str]] = None, patterns: Optional[Iterable[str]] = None):
    removed = 0
    if files_to_remove:
        for path in files_to_remove:
            if os.path.exists(path):
                try:
                    if os.path.isdir(path):
                        shutil.rmtree(path)
                    else:
                        os.remove(path)
                    safe_print(color(f"  eliminado: {path}", 'green'))
                    removed += 1
                except Exception as exc:
                    safe_print(color(f"  error al eliminar {path}: {exc}", 'red'))
    if patterns:
        for pattern in patterns:
            for path in glob.glob(pattern):
                try:
                    if os.path.isdir(path):
                        shutil.rmtree(path)
                    else:
                        os.remove(path)
                    safe_print(color(f"  eliminado: {path}", 'green'))
                    removed += 1
                except Exception:
                    pass
    return removed


def write_log(modulo_name, log_lines, filename=None):
    if filename is None:
        filename = f'{modulo_name}.log'
    with open(filename, 'w', encoding='utf-8') as handle:
        handle.write(f'=== {modulo_name.upper()} - REGISTRO ===\n')
        handle.write(f'Ejecucion: {datetime.datetime.now()}\n\n')
        for line in log_lines:
            handle.write(line + '\n')
        handle.write(f"{'='*40}\n")
    safe_print(color(f"\n  registro guardado en: {filename}", 'green'))
