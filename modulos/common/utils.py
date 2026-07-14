import datetime
import glob
import hashlib
import os
import shutil
from typing import Iterable, Optional

# Importación relativa para resolver rutas del laboratorio
from .paths import resolve_lab_paths

# Paleta de colores ANSI para la consola de la TUI
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

# Líneas globales para acumular el historial de ejecución
LOG_LINES = []


def find_lab_dir(start=None):
    """
    Devuelve la ruta absoluta de directorio_pruebas desde la raíz del laboratorio.
    Se apoya en resolve_lab_paths para obtener direccionamiento dinámico.
    """
    return resolve_lab_paths(start)['lab_dir']


def log(msg):
    """Agrega un mensaje con marca de tiempo al registro en memoria."""
    ts = datetime.datetime.now().strftime('%H:%M:%S')
    LOG_LINES.append(f'[{ts}] {msg}')


def safe_print(msg):
    """Imprime mensajes en consola protegiendo la codificación de caracteres."""
    try:
        print(msg)
    except UnicodeEncodeError:
        print(msg.encode('ascii', errors='replace').decode('ascii'))


def color(text, c):
    """Aplica color ANSI a una cadena de texto."""
    return f"{COLORS.get(c, '')}{text}{COLORS['reset']}"


def banner(modulo_name, descripcion):
    """Dibuja un banner formateado para separar fases y módulos en la interfaz."""
    safe_print(color(f"\n{'=' * 60}", 'cyan'))
    safe_print(color(f"  {modulo_name}", 'bold'))
    safe_print(color(f"  {descripcion}", 'cyan'))
    safe_print(color(f"{'=' * 60}\n", 'cyan'))


def traverse_lab_files(directory=None):
    """Retorna una lista ordenada de archivos del directorio objetivo, omitiendo inicializadores."""
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
    """Calcula el hash SHA-256 de un archivo para auditorías de integridad."""
    h = hashlib.sha256()
    try:
        with open(path, 'rb') as handle:
            for chunk in iter(lambda: handle.read(4096), b''):
                h.update(chunk)
        return h.hexdigest()
    except Exception:
        return None


def read_file(path):
    """Lee el contenido binario crudo de un archivo de forma segura."""
    try:
        with open(path, 'rb') as handle:
            return handle.read()
    except Exception:
        return None


def is_lab_ready():
    """Comprueba si los tres archivos esenciales del laboratorio base existen."""
    lab_dir = find_lab_dir()
    required = ['documento.txt', 'script.py', 'imagen.png']
    return all(os.path.exists(os.path.join(lab_dir, name)) for name in required)


def cleanup(files_to_remove: Optional[Iterable[str]] = None, patterns: Optional[Iterable[str]] = None):
    """Elimina de forma segura archivos temporales, directorios o patrones del entorno."""
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
    """
    Escribe el registro de ejecución dentro de lab_data/logs/.
    
    Siempre resuelve la ruta destino a lab_data/logs/ sin importar
    la ruta que se pase en 'filename'. Solo se usa el nombre base
    del archivo para determinar el nombre del log.
    """
    # Encontrar el directorio base de lab_data dinámicamente
    lab_dir = find_lab_dir()
    lab_data_root = os.path.dirname(lab_dir)
    dir_logs = os.path.join(lab_data_root, 'logs')
    os.makedirs(dir_logs, exist_ok=True)

    # Extraer solo el nombre base del archivo (sin ruta)
    if filename is not None:
        nombre_base = os.path.basename(filename).replace('.log', '')
    else:
        nombre_base = os.path.basename(str(modulo_name)).replace('.log', '')

    path_final_log = os.path.join(dir_logs, f"{nombre_base}.log")

    # Escribir el reporte en disco
    with open(path_final_log, 'w', encoding='utf-8') as handle:
        handle.write(f'=== {modulo_name.upper()} - REGISTRO ===\n')
        handle.write(f'Ejecucion: {datetime.datetime.now()}\n\n')
        for line in log_lines:
            handle.write(line + '\n')
        handle.write(f"{'='*40}\n")

    safe_print(color(f"\n  registro guardado en: {path_final_log}", 'green'))