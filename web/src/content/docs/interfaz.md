---
title: 'Manual de la interfaz Flet'
description: 'Panel, consola, guía y juego'
---

El núcleo interactivo (`gui_flet/main.py`) corre sobre **Flet** con ejecución asíncrona (`asyncio`): la interfaz nunca se congela mientras las simulaciones corren en segundo plano.

```bash
python flet_main.py           # ventana desktop
python flet_main.py --web     # en el navegador (ideal para aula/Wayland)
```

## Anatomía de la pantalla

* **Sidebar (módulos):** lista los 14 módulos con icono, más accesos a Panel y Tutorial. Click para seleccionar.
* **Header:** nombre del módulo, icono del pilar CIA y control CIS asociado.
* **Contenido:** dashboard, tutorial, ficha del módulo o guía Markdown con scroll propio.
* **Botonera:** `Setup` (amarillo), `Simular` (rojo), `Defensa` (azul), `Clean` (verde), `Guía` (morado), `Juego` (naranja).
* **Consola:** salida en tiempo real, fondo oscuro y texto verde; errores y timeouts en rojo, con autoscroll.

## Flujo de trabajo

| Botón | Acción |
|---|---|
| Setup | Genera los archivos de prueba (`lab_setup.py`) |
| Simular | Ejecuta `{script}.py` del módulo seleccionado |
| Defensa | Ejecuta el script de mitigación y restaura archivos |
| Clean | Vacía la consola y restaura la vista |
| Guía | Muestra/oculta el README del módulo |
| Juego | Abre el diálogo de desafíos del módulo |

> Cada script de módulo además soporta `--clean` por CLI para resetear solo sus artefactos.

## Juego de desafíos

Cada módulo con desafíos ofrece selector de dificultad (fácil/medio/difícil), pistas limitadas, puntaje (aprobado con ≥ 60%) y resumen de sesión. Ver [gobernanza](/gobernanza/) para el marco teórico.
