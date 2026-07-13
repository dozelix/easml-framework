# AGENTS.md

## Qué es este repo

Laboratorio educativo de malware en Python. 14 módulos independientes en `modulos/` (cada uno con simulación + defensa + README), una TUI interactiva con Textual, y utilidades compartidas.

## Comandos

```bash
python core/lab_setup.py              # Genera 12 archivos de prueba en directorio_pruebas/
python core/lab_setup.py --clean      # Limpia todos los artefactos generados
python tui.py                         # Lanza la TUI visual (NO usar `python -m core.tui` — no existe)
python -m unittest discover tests     # Tests (unittest, no hay pytest)
```

## Arquitectura (lo que un agente no adivina)

- **Dos paquetes de utilidades compartidas**, no confundir:
  - `modulos/common/` — paths, utils, cleanup, generators (el que usan todos los módulos)
  - `core/` — solo `base_module.py` (ABCs `BaseThreat`/`BaseDefense`) y `lab_setup.py`
- **No existe `core/common.py`** — los imports van desde `modulos.common.*`
- **Cada módulo hace `sys.path.insert(0, _DIR_RAIZ)`** al inicio para resolver rutas absolutas. Copiar este patrón al crear módulos nuevos.
- **Entry point real**: `python tui.py` (raíz) → importa `tui.main.main()`. El README dice `python -m core.tui` pero esa ruta no existe.
- **`tui/views.py` contiene CSS duplicado** de `tui/styles.py` (el que usa `main.py`). No agregar CSS ahí.

## Convenciones

- **Idioma**: código y documentación en español
- **Imports**: desde `modulos.common.utils` y `modulos.common.paths` (NO `core.common`)
- Todo módulo debe soportar `--clean`
- `core/lab_setup.py` es el único generador de archivos de prueba (DRY)
- Cada módulo es autocontenido; no depender de otros módulos

## Tests

```bash
python -m unittest discover tests     # Ejecuta todos
python -m unittest tests.test_common  # Solo test_common
```

**Conocido roto**: `tests/test_common.py` importa `from core.common import find_lab_dir` pero `core/common.py` no existe. Debería importar `from modulos.common.utils import find_lab_dir`.

## Seguridad

- NUNCA ejecutar scripts fuera del directorio del laboratorio
- NUNCA crear payloads o archivos dañinos reales
- NUNCA conexiones de red reales al exterior (solo simulados/localhost)
- TODA acción destructiva debe ser reversible con `--clean`
