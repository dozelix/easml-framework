import glob
import os
import shutil
from typing import Iterable, Optional

from .paths import ensure_lab_data_dirs, resolve_lab_paths


def cleanup_artifacts(files_to_remove: Optional[Iterable[str]] = None, patterns: Optional[Iterable[str]] = None) -> int:
    """Elimina archivos y patrones dentro del laboratorio de forma segura."""
    removed = 0
    paths = ensure_lab_data_dirs()

    if files_to_remove:
        for path in files_to_remove:
            if os.path.exists(path):
                try:
                    if os.path.isdir(path):
                        shutil.rmtree(path)
                    else:
                        os.remove(path)
                    removed += 1
                except Exception:
                    pass

    if patterns:
        for pattern in patterns:
            for path in glob.glob(pattern):
                try:
                    if os.path.isdir(path):
                        shutil.rmtree(path)
                    else:
                        os.remove(path)
                    removed += 1
                except Exception:
                    pass

    # Limpiar artefactos de laboratorio generados por el flujo del TUI si existen.
    for directory in (paths['logs_dir'], paths['output_dir'], paths['samples_dir'], paths['temp_dir']):
        if os.path.isdir(directory):
            for child in os.listdir(directory):
                child_path = os.path.join(directory, child)
                if os.path.isfile(child_path):
                    try:
                        os.remove(child_path)
                        removed += 1
                    except Exception:
                        pass
    return removed


def reset_lab_environment() -> int:
    """Limpia los artefactos del laboratorio y deja el entorno listo para recrear el setup."""
    paths = resolve_lab_paths()
    removed = cleanup_artifacts(patterns=[os.path.join(paths['lab_dir'], '*')])
    ensure_lab_data_dirs()
    return removed
