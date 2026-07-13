#!/usr/bin/env python3
"""
Módulo de inicialización y despliegue del entorno del laboratorio.
Mantiene las pruebas aisladas, reciclando muestras inmutables desde lab_data/samples/.
"""

import os
import sys
import shutil
import glob

# ── Configuración de rutas absolutas robustas ───────────────────────────────
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from modulos.common.paths import ensure_lab_data_dirs, resolve_lab_paths
from modulos.common import generators


GENERATOR_MAP = {
    'documento.txt': generators.make_documento_txt,
    'notas.txt': generators.make_notas_txt,
    'script.py': generators.make_script_py,
    'index.html': generators.make_index_html,
    'datos.csv': generators.make_datos_csv,
    'leeme.md': generators.make_leeme_md,
    'imagen.png': generators.make_png,
    'imagen.jpg': generators.make_jpeg,
    'audio.mp3': generators.make_mp3,
    'documento.docx': generators.make_docx,
    'planilla.xlsx': generators.make_xlsx,
    'presentacion.pptx': generators.make_pptx,
}


def deploy_sandbox(paths):
    """Copia las muestras persistentes de samples/ al directorio_pruebas (sandbox)."""
    os.makedirs(paths.lab_dir, exist_ok=True)
    
    # Asegurar que existan todas las plantillas en 'samples/'
    for name, make_func in GENERATOR_MAP.items():
        sample_path = os.path.join(paths.samples_dir, name)
        if not os.path.exists(sample_path):
            data = make_func()
            mode = 'w' if isinstance(data, str) else 'wb'
            encoding = 'utf-8' if mode == 'w' else None
            with open(sample_path, mode, encoding=encoding) as f:
                f.write(data)
            print(f"  [+] Plantilla generada: {name}")

    # Desplegar al laboratorio de pruebas
    deployed = 0
    for name in GENERATOR_MAP.keys():
        src = os.path.join(paths.samples_dir, name)
        dst = os.path.join(paths.lab_dir, name)
        if not os.path.exists(dst):
            shutil.copy2(src, dst)
            deployed += 1
            print(f"  [+] Desplegado en lab: {name}")

    if deployed > 0:
        print(f"\n[OK] {deployed} archivos desplegados con éxito en:\n     {paths.lab_dir}")
    else:
        print("\n[!] El laboratorio de pruebas ya tiene todos los archivos sanos.")


def clean_lab(paths):
    """Limpia los entornos asociados y vacía el sandbox."""
    cleaned = 0
    
    # 1. Vaciar el directorio de simulación activo
    if os.path.exists(paths.lab_dir):
        for f in os.listdir(paths.lab_dir):
            path = os.path.join(paths.lab_dir, f)
            try:
                if os.path.isdir(path):
                    shutil.rmtree(path)
                else:
                    os.remove(path)
                cleaned += 1
                print(f"  [-] Eliminado del lab: {f}")
            except Exception as e:
                print(f"  [!] Error al eliminar {f}: {e}")

    # 2. Eliminar logs residuales
    for path_log in glob.glob(os.path.join(paths.logs_dir, '*.log')):
        try:
            os.remove(path_log)
            cleaned += 1
            print(f"  [-] Log eliminado: {os.path.basename(path_log)}")
        except Exception:
            pass

    print(f"\nLimpieza completada: {cleaned} recursos removidos.")


def main():
    paths = ensure_lab_data_dirs(BASE_DIR)
    
    if '--clean' in sys.argv:
        print("Iniciando saneamiento completo del laboratorio...\n")
        clean_lab(paths)
    else:
        print("Desplegando entorno controlado de pruebas...\n")
        deploy_sandbox(paths)


if __name__ == "__main__":
    main()