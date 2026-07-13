import os
from dataclasses import dataclass
from typing import Dict, Optional


@dataclass(frozen=True)
class LabPaths:
    """Clase inmutable para almacenar la estructura completa de rutas del laboratorio."""
    repo_root: str
    lab_dir: str
    lab_data_dir: str
    logs_dir: str
    output_dir: str
    samples_dir: str
    temp_dir: str


def resolve_lab_paths(start: Optional[str] = None) -> Dict[str, str]:
    """
    Resuelve de manera dinámica todas las rutas necesarias del laboratorio
    buscando la carpeta 'directorio_pruebas' hacia arriba.
    """
    base = start or os.getcwd()
    if os.path.isfile(base):
        base = os.path.dirname(base)

    current = os.path.abspath(base)
    repo_root = None
    
    # 1. Buscar hacia arriba la carpeta de simulación activa para hallar la raíz
    while True:
        candidate = os.path.join(current, 'directorio_pruebas')
        if os.path.isdir(candidate):
            repo_root = current
            break
        parent = os.path.dirname(current)
        if parent == current:
            break
        current = parent
            
    # 2. Fallback robusto (subir 3 niveles desde modulos/common/paths.py para llegar a MALWARES/)
    if not repo_root:
        # Nivel 1: modulos/common -> Nivel 2: modulos -> Nivel 3: MALWARES (Raíz Real)
        repo_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

    lab_dir = os.path.join(repo_root, 'directorio_pruebas')
    lab_data_dir = os.path.join(repo_root, 'lab_data')
    
    return {
        'repo_root': repo_root,
        'lab_dir': lab_dir,
        'lab_data_dir': lab_data_dir,
        'logs_dir': os.path.join(lab_data_dir, 'logs'),
        'output_dir': os.path.join(lab_data_dir, 'output'),
        'samples_dir': os.path.join(lab_data_dir, 'samples'),
        'temp_dir': os.path.join(lab_data_dir, 'temp'),
    }


def ensure_lab_data_dirs(start: Optional[str] = None) -> LabPaths:
    """
    Verifica y genera todos los directorios requeridos en lab_data si no existen,
    devolviendo un objeto de tipo LabPaths.
    """
    paths = resolve_lab_paths(start)
    for key in ('lab_data_dir', 'logs_dir', 'output_dir', 'samples_dir', 'temp_dir'):
        os.makedirs(paths[key], exist_ok=True)
    return LabPaths(**paths)
