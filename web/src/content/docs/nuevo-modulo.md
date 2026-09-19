---
title: 'Desarrollo de nuevos módulos'
description: 'Cómo extender el laboratorio con otra amenaza'
---

El framework es extensible. Para mantener la consistencia, todo módulo nuevo sigue esta arquitectura (sin excepciones).

## Estructura obligatoria

Carpeta propia en `modulos/` **sin prefijo numérico** (ej. `modulos/mi_amenaza/`):

```text
modulos/<nombre>/
├── README.md        # Teoría, Tríada CIA, Controles CIS, diagramas Mermaid
├── <nombre>.py      # Simulación (threat)
└── <defensa>.py     # Detección + mitigación + limpieza (nombre propio por módulo)
```

El nombre del script de defensa se registra en `app/config.py` → `NOMBRES_DEFENSA` (en minúsculas con guiones bajos, ej. `respuesta_a_incidentes.py`). El módulo se registra en `MODULOS` ordenado por control CIS.

## Estándar de código

### 1. Confinamiento absoluto (SAFE)

* Prohibido actuar fuera de `directorio_pruebas/`.
* Rutas siempre vía `modulos.common.paths` (`resolve_lab_paths`) y `modulos.common.utils` (`find_lab_dir`). No existe `core/common.py`.
* Cada script arranca con `sys.path.insert(0, _DIR_RAIZ)` (3 niveles desde `modulos/<nombre>`).
* Sin payloads reales, sin red externa: todo simulado/localhost.

### 2. CLI obligatoria

Todo script soporta (vía `argparse` o condicionales):

* `--help` / `-h`: vector de ataque y fases (los smoke tests lo verifican).
* `--clean`: elimina solo sus artefactos, restaurando el laboratorio.

### 3. Salida explicativa (EDU)

* `stdout` paso a paso, una fase por línea con `\n` (la consola Flet y los logs lo consumen línea a línea).
* Sin animaciones que rompan el buffer; `strip_ansi` limpia colores.

## README del módulo

1. **Descripción técnica** del vector a nivel SO.
2. **Impacto CIA:** qué pilar se degrada y por qué.
3. **Mitigación CIS:** control aplicado en `<defensa>.py`.
4. **Diagramas Mermaid** de amenaza y defensa (la wiki los renderiza).

Tras crearlo, valida: `python scripts/generar_indice.py --check`, `python -m unittest discover tests` y `python scripts/auditar_flet.py` si tocaste la GUI.
