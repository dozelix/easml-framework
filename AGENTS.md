# AGENTS.md

## Qué es este repo

Laboratorio educativo de malware en Python. 14 módulos independientes en `modulos/` (cada uno con simulación + defensa + README), una TUI interactiva con Textual, una GUI con tkinter, y utilidades compartidas.

## Comandos

```bash
python core/lab_setup.py              # Genera 12 archivos de prueba en directorio_pruebas/
python core/lab_setup.py --clean      # Limpia todos los artefactos generados
python tui.py                         # Lanza la TUI visual
python gui.py                         # Lanza la GUI gráfica (requiere tkinter)
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
- **GUI tkinter** (`gui.py`): alternativa gráfica independiente. Requiere `tkinter` (no es pip-installable, depende del sistema — ver más abajo).
- **Laboratorio interactivo** (`tui/laboratorio.py` + `tui/desafio.py`): desafíos de opción múltiple con 3 niveles de dificultad (Fácil/Medio/Difícil), accesible con `[C]` en la TUI.

## `lab_data/` — Estructura persistente

```
lab_data/
├── logs/          # write_log() siempre escribe aquí (basename del archivo)
├── samples/       # muestras generadas por módulos
├── output/        # salida de simulaciones
└── temp/          # archivos temporales
```

- `write_log(filename, msg)` en `modulos/common/utils.py` siempre resuelve a `lab_data/logs/{basename}`. No usar para archivos que deban quedar en `directorio_pruebas/`.

## Teclas de la TUI

| Tecla | Acción | Notas |
|-------|--------|-------|
| `Q` | Setup | Genera archivos de prueba |
| `W` | Simular | Ejecuta script de simulación del módulo seleccionado |
| `E` | Defensa | Ejecuta script de defensa |
| `R` | Readme Max | Ocupa 100% de pantalla (oclta panel izquierdo + consola) |
| `D` | Clean | Limpia consola |
| `B` | Dashboard | Panel con datos reales del laboratorio |
| `H` | Tutorial | Flujo guiado paso a paso |
| `C` | Desafío | Modo interactivo con dificultad |
| `ESC` | Salir | Modal de confirmación (Y/N) |
| `↑↓` | Navegar | Flechas o rueda del ratón |

## Convenciones

- **Idioma**: código y documentación en español
- **Imports**: desde `modulos.common.utils` y `modulos.common.paths` (NO `core.common`)
- Todo módulo debe soportar `--clean`
- `core/lab_setup.py` es el único generador de archivos de prueba (DRY)
- Cada módulo es autocontenido; no depender de otros módulos
- Scripts de defensa tienen nombre personalizado por módulo (NO `defensa.py`)
- **Branches**: `main` → `develop` → features/fixes. Cada fix/feature en su propia rama, merge con `--no-ff`, tag con `-a vX.X.X -m "vX.X.X easmlix — descripción"`

## Tests

```bash
python -m unittest discover tests     # Ejecuta todos (37 tests)
python -m unittest tests.test_common  # Solo test_common (paths)
python -m unittest tests.test_smoke   # Smoke tests por módulo (--help)
```

Los smoke tests solo verifican que `--help` funcione en cada script. No hay tests de integración ni de la TUI/GUI.

## Requisitos del sistema

- **Python 3.10+**
- **Textual** (`pip install textual`) — para la TUI
- **tkinter** — para la GUI. **No es pip-installable**, es dependencia del sistema:
  - Arch Linux: `sudo pacman -S tk`
  - Ubuntu/Debian: `sudo apt install python3-tk`
  - Windows: incluido con python.org installer
  - macOS: incluido con python.org installer

## Seguridad

- NUNCA ejecutar scripts fuera del directorio del laboratorio
- NUNCA crear payloads o archivos dañinos reales
- NUNCA conexiones de red reales al exterior (solo simulados/localhost)
- TODA acción destructiva debe ser reversible con `--clean`
