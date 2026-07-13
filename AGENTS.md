# AGENTS.md

## Qué es este repo

Laboratorio educativo de malware en Python. 14 módulos independientes en `modulos/` (cada uno con simulación + defensa + README), una TUI interactiva con Textual, y utilidades compartidas.

## Comandos

```bash
python core/lab_setup.py              # Genera 12 archivos de prueba en directorio_pruebas/
python core/lab_setup.py --clean      # Limpia todos los artefactos generados
python tui.py                         # Lanza la TUI visual
python -m unittest discover tests     # Tests (unittest, no hay pytest)
```

## Arquitectura (lo que un agente no adivina)

- **Dos paquetes de utilidades compartidas**, no confundir:
  - `modulos/common/` — paths, utils, cleanup, generators (el que usan todos los módulos)
  - `core/` — solo `base_module.py` (ABCs `BaseThreat`/`BaseDefense`) y `lab_setup.py`
- **No existe `core/common.py`** — los imports van desde `modulos.common.*`
- **Cada módulo hace `sys.path.insert(0, _DIR_RAIZ)`** al inicio para resolver rutas absolutas. Copiar este patrón al crear módulos nuevos.
- **Entry point real**: `python tui.py` (raíz) → importa `tui.main.main()`.
- **CSS está exclusivamente en `tui/styles.py`**. `tui/views.py` solo contiene funciones que generan strings Markdown.

## Convenciones

- **Idioma**: código y documentación en español
- **Imports**: desde `modulos.common.utils` y `modulos.common.paths` (NO `core.common`)
- Todo módulo debe soportar `--clean`
- `core/lab_setup.py` es el único generador de archivos de prueba (DRY)
- Cada módulo es autocontenido; no depender de otros módulos
- Scripts de defensa tienen nombre personalizado por módulo (NO `defensa.py`)

## Tests

```bash
python -m unittest discover tests     # Ejecuta todos
python -m unittest tests.test_common  # Solo test_common
python -m unittest tests.test_smoke   # Smoke tests por módulo
```

## Seguridad

- NUNCA ejecutar scripts fuera del directorio del laboratorio
- NUNCA crear payloads o archivos dañinos reales
- NUNCA conexiones de red reales al exterior (solo simulados/localhost)
- TODA acción destructiva debe ser reversible con `--clean`
