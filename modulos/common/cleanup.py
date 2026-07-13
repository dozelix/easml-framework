#!/usr/bin/env python3
"""
Módulo de limpieza y restauración para el entorno del laboratorio.
Proporciona utilidades para eliminar de forma segura los archivos generados y restaurar el estado inicial.
"""

import glob
import os
import shutil
from typing import Iterable, Optional

# Importando resolutores de rutas del subpaquete common
from .paths import ensure_lab_data_dirs, resolve_lab_paths


def cleanup_artifacts(files_to_remove: Optional[Iterable[str]] = None, patterns: Optional[Iterable[str]] = None) -> int:
    """Elimina archivos y patrones dentro del laboratorio de forma segura."""
    removed = 0
    # ensure_lab_data_dirs() retorna un objeto de la dataclass LabPaths
    paths = ensure_lab_data_dirs()

    # Eliminar lista explícita de archivos proporcionados
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

    # Eliminar archivos según patrones de búsqueda (wildcards)
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

    # Acceso por atributos corregido para evitar TypeError al interactuar con la dataclass LabPaths
    volatile_dirs = (paths.logs_dir, paths.output_dir, paths.samples_dir, paths.temp_dir)
    for directory in volatile_dirs:
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
    # resolve_lab_paths() retorna un diccionario Dict[str, str], por ende usamos acceso por llaves
    paths = resolve_lab_paths()
    removed = cleanup_artifacts(patterns=[os.path.join(paths['lab_dir'], '*')])
    ensure_lab_data_dirs()
    return removed
