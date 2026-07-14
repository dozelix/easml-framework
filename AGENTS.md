# AGENTS.md

## Qué es este repo

Laboratorio educativo de malware en Python. 14 módulos independientes en `modulos/` (cada uno con simulación + defensa + README), una GUI con tkinter, y utilidades compartidas. Los módulos están ordenados por control CIS (2→15).

## Comandos

```bash
python core/lab_setup.py              # Genera 12 archivos de prueba en directorio_pruebas/
python core/lab_setup.py --clean      # Limpia todos los artefactos generados
python gui.py                         # Lanza la GUI gráfica (requiere tkinter)
python -m unittest discover tests     # Tests (unittest, no hay pytest)
```

## Arquitectura (lo que un agente no adivina)

- **Dos paquetes de utilidades compartidas**, no confundir:
  - `modulos/common/` — paths, utils, cleanup, generators, strip_ansi (el que usan todos los módulos)
  - `core/` — solo `base_module.py` (ABCs `BaseThreat`/`BaseDefense`) y `lab_setup.py`
- **No existe `core/common.py`** — los imports van desde `modulos.common.*`
- **Cada módulo hace `sys.path.insert(0, _DIR_RAIZ)`** al inicio para resolver rutas absolutas. Copiar este patrón al crear módulos nuevos.
- **Entry point**: `python gui.py` → `gui.main.main()`.
- **Paquete `gui/`** con estructura modular:
  - `main.py` — `LaboratorioGUI` (tk.Tk), layout Zen+Brutalista, sidebar con iconos, área de contenido, barra de acciones con colores semánticos, consola
  - `config.py` — `MODULOS` (ordenado por CIS, 14 módulos) y `NOMBRES_DEFENSA`
  - `views.py` — generadores de contenido (dashboard, tutorial, modulo_info, leer_readme, md_to_html)
  - `styles.py` — paleta de colores, fuentes, estilos ttk
  - `runner.py` — `ScriptRunner` (ejecución asíncrona con subprocess + thread)
  - `desafio.py` — `DesafioWindow` (toplevel de quiz con 3 niveles de dificultad)
  - `laboratorio.py` — `LaboratorioInteractivo` y `DESAFIOS_POR_MODULO`
- **Los iconos de módulos** están en `assets/modulos/` como PNG 100×100 generados con Pillow.
- **Markdown** se renderiza como HTML via `tkhtmlview.HTMLLabel` + librería `markdown` (fallback a texto plano si no están instalados).

## `lab_data/` — Estructura persistente

```
lab_data/
├── logs/          # write_log() siempre escribe aquí (basename del archivo)
├── samples/       # muestras generadas por módulos
├── output/        # salida de simulaciones
└── temp/          # archivos temporales
```

- `write_log(filename, msg)` en `modulos/common/utils.py` siempre resuelve a `lab_data/logs/{basename}`. No usar para archivos que deban quedar en `directorio_pruebas/`.

## Diseño de la GUI

- **Inspiración**: Zen Browser + Brutalism
- **Sidebar** vertical angosta (~200px) con iconos PNG de cada módulo
- **Panel derecho**: header con nombre + badge CIS, área de contenido, barra de acciones, consola
- **Colores semánticos**:
  - Rojo (`#f7768e`) — Simular
  - Azul (`#7aa2f7`) — Defensa
  - Verde (`#9ece6a`) — Clean
  - Amarillo (`#e0af68`) — Setup
  - Púrpura (`#bb9af7`) — Readme
  - Naranja (`#ff9e64`) — Juego
- **Fondo**: `#0d0f14` / paneles `#1a1d27`
- **Consola**: fondo casi negro (`#0a0c10`), texto verde monoespaciado

## Convenciones

- **Idioma**: código y documentación en español
- **Imports**: desde `modulos.common.*`, `gui.*`; NO desde `core.common`
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

Los smoke tests solo verifican que `--help` funcione en cada script. No hay tests de integración ni de la GUI.

## Requisitos del sistema

- **Python 3.10+**
- **tkinter** — para la GUI. **No es pip-installable**, es dependencia del sistema:
  - Arch Linux: `sudo pacman -S tk`
  - Ubuntu/Debian: `sudo apt install python3-tk`
  - Windows: incluido con python.org installer
  - macOS: incluido con python.org installer
- **Pillow** (`pip install Pillow`) — para iconos PNG en la GUI
- **tkhtmlview** (`pip install tkhtmlview`) — para renderizar READMEs como HTML
- **markdown** (`pip install markdown`) — para convertir Markdown a HTML

## Assets

- `assets/modulos/*.png` — 14 iconos (100×100) para cada módulo
- Para regenerar: `python assets/generate_icons.py`

## Seguridad

- NUNCA ejecutar scripts fuera del directorio del laboratorio
- NUNCA crear payloads o archivos dañinos reales
- NUNCA conexiones de red reales al exterior (solo simulados/localhost)
- TODA acción destructiva debe ser reversible con `--clean`
