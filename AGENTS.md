# AGENTS.md

## Qué es este repo

Laboratorio educativo de malware en Python. 14 módulos independientes en `modulos/` (cada uno con simulación + defensa + README), una GUI con tkinter. Los módulos están ordenados por control CIS (2→15) en `gui/config.py`.

## Comandos

```bash
python core/lab_setup.py              # Genera 12 archivos de prueba en directorio_pruebas/
python core/lab_setup.py --clean      # Limpia todos los artefactos generados
python gui.py                         # Lanza la GUI (tkinter, entrypoint: gui.main.main())
python -m unittest discover tests     # Tests (38 tests, unittest, no hay pytest)
```

## Arquitectura

- **Dos paquetes de utilidades**, no confundir:
  - `modulos/common/` — paths, utils, cleanup, generators, strip_ansi (usado por todos los módulos)
  - `core/` — solo `base_module.py` (ABCs `BaseThreat`/`BaseDefense`) y `lab_setup.py`
- **No existe `core/common.py`** — los imports van desde `modulos.common.*`
- **`modulos/` NO es un paquete** (no tiene `__init__.py`). Solo `modulos/common/` lo es.
- **Cada módulo hace `sys.path.insert(0, _DIR_RAIZ)`** al inicio — los scripts suben desde `modulos/{nombre}` (3 niveles) o `gui/` (2 niveles) para resolver rutas absolutas.
- **Módulo = 3 archivos**: `{nombre}.py` (threat), `{defensa}.py` (defense), `README.md`. Nombres de defensa en `gui/config.py` → `NOMBRES_DEFENSA`.
- **Los directorios NO tienen prefijo numérico**: `modulos/ransomware/`, no `01_ransomware/`.
- **gui.py es el único entrypoint**. No existe `tui.py`. El README describe una interfaz TUI/Textual aspiracional que no coincide con el código actual.

## `lab_data/` — Estructura persistente

`write_log(filename, msg)` en `modulos/common/utils.py` escribe a `lab_data/logs/{basename}`.

## Diseño de la GUI

- **Inspiración**: Zen Browser + Brutalism
- **Fondo**: `#0d0f14` / paneles `#1a1d27` — **Consola**: `#0a0c10` con texto verde
- **Colores semánticos**: Rojo (`#f7768e`) Simular / Azul (`#7aa2f7`) Defensa / Verde (`#9ece6a`) Clean / Amarillo (`#e0af68`) Setup / Púrpura (`#bb9af7`) Readme / Naranja (`#ff9e64`) Juego

## Convenciones

- **Idioma**: código y documentación en español
- **Imports**: desde `modulos.common.*`, `gui.*`; NO desde `core.common`
- Todo script de módulo debe soportar `--help` y `--clean`
- `core/lab_setup.py` es el único generador de archivos de prueba (DRY)
- Cada módulo es autocontenido; no depender de otros módulos
- Scripts de defensa tienen nombre personalizado por módulo (NO `defensa.py`)
- **Branches**: `main` → `develop` → features/fixes. Cada fix/feature en rama propia, merge `--no-ff`, tag `-a`

## Tests

```bash
python -m unittest discover tests     # 38 tests
python -m unittest tests.test_common  # Solo paths
python -m unittest tests.test_smoke   # Smoke tests: --help en cada script + lab_setup --clean
```

Smoke tests solo verifican que `--help` funcione. No hay tests de integración ni de la GUI.

## Dependencias

- **Python 3.10+**
- Sin dependencias obligatorias (tkinter viene con CPython)
- Opcionales: `Pillow` (iconos PNG), `tkhtmlview` + `markdown` (renderizar READMEs como HTML)
- `requirements.txt` lista `textual>=8.0` pero no se usa — legacy aspiracional

## Assets

`assets/modulos/*.png` — 14 iconos (100×100). Regenerar con `python assets/generate_icons.py` (ignorado por git).

## Seguridad

- NUNCA ejecutar scripts fuera del directorio del laboratorio
- NUNCA crear payloads o archivos dañinos reales
- NUNCA conexiones de red reales al exterior (solo simulados/localhost)
- TODA acción destructiva debe ser reversible con `--clean`
