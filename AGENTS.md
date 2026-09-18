# AGENTS.md

## Qué es este repo

Laboratorio educativo de malware en Python con 14 módulos independientes, cada uno con simulación + defensa + README. GUI Flet (`gui_flet/`, entry point `flet_main.py`); tkinter (`gui.py`) en transición. Wiki/docs en `web/` (Astro Starlight).

## Comandos

```bash
python core/lab_setup.py              # Genera 12 archivos de prueba en directorio_pruebas/
python core/lab_setup.py --clean      # Limpia artefactos (lab_data/logs, output, samples, temp + directorio_pruebas)
python gui.py                         # GUI tkinter legacy (requiere tkinter)
python flet_main.py                   # GUI Flet (requiere flet==1.0.0)
python flet_main.py --web             # Flet en navegador local (puerto 8550)
python scripts/generar_indice.py --check       # Sincronía config ↔ READMEs (CI)
python scripts/generar_indice.py --check-links # Refs HTTP vivas (manual, con red)
python scripts/auditar_flet.py        # API Flet válida contra instalado (CI)
bash scripts/build.sh                 # Empaquetado local (canónico: release.yml en CI)
python -m unittest discover tests     # 51 tests (unittest, no pytest)
python -m unittest tests.test_common  # Solo test_common (paths)
python -m unittest tests.test_smoke   # Smoke tests: --help en cada script
python -m unittest tests.test_flet    # GUI Flet (omite lo que requiere flet si falta)
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
- **gui.py es el único entrypoint**. No existe `tui.py`.

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
- **Branches**: `main` → `develop` → features/fixes. Merge con `--no-ff`, tag con `-a vX.X.X easmlix`
- **Flujo de bugs**:
  1. **Bug en develop**: rama `fix/<descripcion>` desde `develop`. Ejecutar tests y PR → `develop`.
  2. **Bug en main** (producción): rama `hotfix/<descripcion>` desde `main`. PR → `main`, luego merge `main` → `develop` para sincronizar.
  3. **Formato commits**: `fix: descripción corta del bug`
  4. **QA previo al PR**: ejecutar `python -m unittest discover tests`. Usar `@bluehat` para revisión funcional y `@debugfix` para corrección automatizada. `@redhat` solo si el bug tiene implicaciones de seguridad.

## Tests

```bash
python -m unittest discover tests     # 51 tests
python -m unittest tests.test_common  # Solo paths
python -m unittest tests.test_smoke   # Smoke tests: --help en cada script + lab_setup --clean
```

Smoke tests solo verifican que `--help` funcione. `tests/test_flet.py` cubre la GUI
Flet headless (runner, quiz, vistas, layout, modo frozen). Requisitos funcionales
en `docs/REQUISITOS.md` (trazabilidad test ↔ requisito).

## Requisitos

- **Python 3.10+**, **tkinter** solo para `gui.py` legacy (`apt install python3-tk` en Linux)
- `pip install -r requirements.txt` (pillow, tkhtmlview, markdown, flet==1.0.0)

## Seguridad

- NUNCA ejecutar scripts fuera del directorio del laboratorio
- NUNCA crear payloads o archivos dañinos reales
- NUNCA conexiones de red reales al exterior (solo simulados/localhost)
- TODA acción destructiva debe ser reversible con `--clean`

## Assets

- `assets/modulos/*.png` — 14 iconos PNG 100×100 para la GUI
- Para regenerar: `python assets/generate_icons.py`
