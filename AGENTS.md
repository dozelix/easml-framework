# AGENTS.md

## ¿Qué es este repo?

Laboratorio educativo de malware en Python con 14 módulos independientes, cada uno con simulación + defensa + README. GUI funcional con tkinter. El README describe una TUI con Textual que aún no existe — el entry point real es `gui.py`.

## Comandos esenciales

```bash
python core/lab_setup.py              # Genera 12 archivos de prueba en directorio_pruebas/
python core/lab_setup.py --clean      # Limpia artefactos (lab_data/logs, output, samples, temp + directorio_pruebas)
python gui.py                         # GUI funcional (requiere tkinter, opcional: Pillow, tkhtmlview, markdown)
python -m unittest discover tests     # 38 tests (unittest, no pytest)
python -m unittest tests.test_common  # Solo test_common (paths)
python -m unittest tests.test_smoke   # Smoke tests: --help en cada script
```

Los smoke tests solo verifican que `--help` funcione. No hay tests de integración ni de GUI.

## Arquitectura (lo que un agente no adivina)

- **Dos paquetes de utilidades compartidas**, NO confundir:
  - `modulos/common/` — paths, utils, cleanup, generators, strip_ansi (usado por todos los módulos)
  - `core/` — solo `base_module.py` (ABCs `BaseThreat`/`BaseDefense`) y `lab_setup.py`
- **No existe `core/common.py`** — los imports van desde `modulos.common.*`
- **Cada módulo y script** hace `sys.path.insert(0, _DIR_RAIZ)` al inicio para resolver rutas absolutas. Copiar este patrón al crear módulos nuevos.
- **Entry point**: `python gui.py` → `gui.main.main()`.

### Estructura persistente (`lab_data/`)

```
lab_data/
├── logs/       # write_log() siempre escribe aquí
├── samples/    # plantillas inmutables que lab_setup.py copia a directorio_pruebas/
├── output/     # salida de simulaciones
└── temp/       # archivos temporales
```

`write_log(filename, msg)` en `modulos/common/utils.py` siempre resuelve a `lab_data/logs/{basename}`. NO usar para archivos que deban quedar en `directorio_pruebas/`.

- `directorio_pruebas/` es el sandbox activo donde operan las simulaciones
- `lab_data/samples/` contiene las plantillas originales; `lab_setup.py` las copia a `directorio_pruebas/` (no las mueve)
- Hay un `logs/` residual en la raíz del repo (logs viejos) — ignorar, no forma parte de la arquitectura actual

## Convenciones

- **Idioma**: código y documentación en español
- **Imports**: desde `modulos.common.*`, `gui.*`; NO desde `core.common`
- **Cada módulo es autocontenido**, no depende de otros módulos
- **Scripts de defensa** tienen nombre personalizado por módulo (definido en `gui/config.py` como `NOMBRES_DEFENSA`)
- **Estructura de módulo**: `modulos/XX_nombre/` → `{nombre}.py` (simulación) + `{defensa}.py` (defensa) + `README.md`
- `core/lab_setup.py` es el único generador de archivos de prueba (DRY)
- **Branches**: `main` → `develop` → features/fixes. Merge con `--no-ff`, tag con `-a vX.X.X easmlix`

## Seguridad

- NUNCA ejecutar scripts fuera del directorio del laboratorio
- NUNCA crear payloads o archivos dañinos reales
- NUNCA conexiones de red reales al exterior (solo simulados/localhost)
- TODA acción destructiva debe ser reversible con `--clean`

## Assets

- `assets/modulos/*.png` — 14 iconos PNG 100×100 para la GUI
- Para regenerar: `python assets/generate_icons.py`

## Requisitos

- **Python 3.10+**, **tkinter** (incluido en python.org installer Windows/macOS, `apt install python3-tk` en Linux)
- Opcionales: `pip install Pillow tkhtmlview markdown` (mejoran la GUI pero no son obligatorios)
- Dependencia base: `pip install textual` (para la TUI descrita en README, no implementada aún)
