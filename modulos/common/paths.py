import os
import sys
from dataclasses import dataclass
from typing import Dict, Optional


def es_ejecutable_congelado() -> bool:
    """True bajo flet pack / PyInstaller (sys.frozen)."""
    return getattr(sys, "frozen", False)


def base_recursos() -> str:
    """Recursos de solo lectura (.py de módulos, assets, READMEs).

    En ejecutable congelado viven en sys._MEIPASS; en desarrollo, en la raíz
    del repo (3 niveles sobre modulos/common/paths.py).
    """
    if es_ejecutable_congelado():
        base = getattr(sys, "_MEIPASS", None)
        if base:
            return base
    return os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def raiz_por_archivo() -> str:
    """Raíz del repo deducida de la ubicación de este archivo.

    Determinista: no depende del cwd desde el que se lance el proceso.
    """
    return os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def base_trabajo() -> str:
    """Directorios escribibles (directorio_pruebas, lab_data).

    En ejecutable congelado van junto al .exe (el bundle es efímero y no debe
    ensuciarse); en desarrollo, en la raíz del repo. EASML_HOME lo sobrescribe
    (útil en tests y aulas con home redirigido).
    """
    if es_ejecutable_congelado():
        return os.path.dirname(os.path.abspath(sys.executable))
    override = os.environ.get("EASML_HOME")
    if override and os.path.isdir(override):
        return os.path.abspath(override)
    return raiz_por_archivo()


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
    Resuelve de manera dinámica todas las rutas necesarias del laboratorio.

    En ejecutable congelado (flet pack): los recursos se leen de _MEIPASS y
    lo escribible (directorio_pruebas, lab_data) va junto al .exe.

    En desarrollo la raíz es determinista (ubicación de este archivo,
    sobrescribible con EASML_HOME) y NO depende del cwd: lanzar Setup desde
    la raíz, desde modulos/x/ o desde la GUI produce la misma lab_dir y evita
    el bug de directorio_pruebas duplicado. `start` solo se honra si apunta
    a un árbol que ya contiene directorio_pruebas (compat con callers y tests).
    """
    if es_ejecutable_congelado():
        trabajo = base_trabajo()
        lab_data_dir = os.path.join(trabajo, 'lab_data')
        return {
            'repo_root': base_recursos(),
            'lab_dir': os.path.join(trabajo, 'directorio_pruebas'),
            'lab_data_dir': lab_data_dir,
            'logs_dir': os.path.join(lab_data_dir, 'logs'),
            'output_dir': os.path.join(lab_data_dir, 'output'),
            'samples_dir': os.path.join(lab_data_dir, 'samples'),
            'temp_dir': os.path.join(lab_data_dir, 'temp'),
        }

    repo_root = base_trabajo()

    if start is not None:
        base = start
        if os.path.isfile(base):
            base = os.path.dirname(base)
        current = os.path.abspath(base)
        while True:
            candidate = os.path.join(current, 'directorio_pruebas')
            if os.path.isdir(candidate):
                repo_root = current
                break
            parent = os.path.dirname(current)
            if parent == current:
                break
            current = parent

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


def find_lab_data_dir(start: Optional[str] = None) -> str:
    """Ruta de lab_data/ (persistente: samples, logs, output, temp)."""
    return resolve_lab_paths(start)['lab_data_dir']


def find_logs_dir(start: Optional[str] = None) -> str:
    """Ruta de lab_data/logs/. Única fuente para logs (no repo_root/logs/)."""
    return resolve_lab_paths(start)['logs_dir']


def ensure_lab_data_dirs(start: Optional[str] = None) -> LabPaths:
    """
    Verifica y genera todos los directorios requeridos en lab_data si no existen,
    devolviendo un objeto de tipo LabPaths.

    Migra una sola vez el directorio huérfano repo_root/logs/*.log (bug
    histórico: varios módulos resolvían dirname(lab_dir)/logs en vez de
    lab_data/logs) hacia lab_data/logs/ para no duplicar.
    """
    paths = resolve_lab_paths(start)
    for key in ('lab_data_dir', 'logs_dir', 'output_dir', 'samples_dir', 'temp_dir'):
        os.makedirs(paths[key], exist_ok=True)
    if not es_ejecutable_congelado():
        _migrar_logs_huerfanos(paths['repo_root'], paths['logs_dir'])
    return LabPaths(**paths)


def _migrar_logs_huerfanos(repo_root: str, logs_dir: str) -> int:
    """Mueve repo_root/logs/*.log a lab_data/logs/. Retorna nº migrados."""
    huerfano = os.path.join(repo_root, 'logs')
    if os.path.abspath(huerfano) == os.path.abspath(logs_dir):
        return 0
    if not os.path.isdir(huerfano):
        return 0
    migrados = 0
    try:
        for nombre in sorted(os.listdir(huerfano)):
            src = os.path.join(huerfano, nombre)
            if not os.path.isfile(src) or not nombre.endswith('.log'):
                continue
            dst = os.path.join(logs_dir, nombre)
            if os.path.exists(dst):
                continue
            os.replace(src, dst)
            migrados += 1
        if not os.listdir(huerfano):
            os.rmdir(huerfano)
    except OSError:
        pass
    return migrados
