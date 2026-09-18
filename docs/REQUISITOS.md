# Requisitos EASML — Funcionales y No Funcionales

Fuente única de qué debe hacer el laboratorio. Regla: **lo que no tiene test,
auditoría o ítem de checklist, no está probado**. Este archivo se actualiza
antes de dar por cerrado cada PR, no después.

Alcance: GUI Flet (`gui_flet/` + `flet_main.py`), CLI de laboratorio
(`core/lab_setup.py`, scripts de módulo), empaquetado y wiki. La GUI tkinter
(`gui/`) está en transición: se mantiene funcional hasta el cierre de PR3.

## Requisitos funcionales

| ID | Requisito | Verificación |
|----|-----------|--------------|
| RF-01 | Sidebar lista los 14 módulos ordenados por CIS + accesos a Panel y Tutorial | `TestLayout` (14 tiles) |
| RF-02 | Dashboard muestra estado (activo/vacío), nº archivos, nº logs y conteo por pilar CIA | `TestVistas` + manual |
| RF-03 | Tutorial describe el flujo Setup → Simular → Defensa → Clean | `TestVistas` |
| RF-04 | Vista de módulo muestra pilar CIA, existencia de sim/defensa/guía y link de referencia vivo (abre pestaña nueva) | `TestVistas` + `--check-links` (14/14 vivas el 2026-09-18) |
| RF-05 | Setup genera los 12 archivos de prueba vía `lab_setup.py` sin congelar la UI | `TestRunnerSinFlet` + manual |
| RF-06 | Simular ejecuta `{script}.py` del módulo y vuelca la salida en la consola en tiempo real | manual |
| RF-07 | Defensa ejecuta el script de mitigación y restaura archivos | manual |
| RF-08 | Clean vacía la consola y restaura la vista actual | manual |
| RF-09 | Guía renderiza el README del módulo en Markdown con scroll completo, sin solaparse con la botonera | `TestVistas` (scroll) + manual |
| RF-10 | Header muestra icono CIA solo con módulo seleccionado, sin carteles de error | manual (bug cartel rojo, corregido) |
| RF-11 | Juego abre diálogo modal con selector de dificultad (fácil/medio/difícil) | `TestQuiz` + manual |
| RF-12 | Juego evalúa respuestas, da pistas según dificultad y calcula puntaje (aprobado ≥ 60%) | `TestQuiz` |
| RF-13 | Consola con autoscroll, fondo oscuro y texto verde; errores/timeout en rojo | manual |
| RF-14 | `flet_main.py --help` y `--clean` funcionan sin abrir ventana ni requerir flet | `TestFletMain` |
| RF-15 | `flet_main.py --web [--port]` sirve la app en navegador local | smoke `--web` |
| RF-16 | Ejecuciones concurrentes se ignoran (una a la vez, flag `ejecutando`) | manual |

## Requisitos no funcionales

| ID | Requisito | Verificación |
|----|-----------|--------------|
| RNF-01 | Python 3.10+ (CI: 3.10–3.12; local 3.14); dependencias fijadas (`flet==1.0.0`) | CI matriz + `pip-audit` |
| RNF-02 | 100% offline: sin red externa, guías e iconos bundelados en `assets/` | revisión (sin telemetría en código) |
| RNF-03 | Usable en máquina modesta (Celeron, 4GB): builds pesados en CI, no en local | CI `docs` + `release` |
| RNF-04 | Toda acción destructiva es reversible con `--clean` | `TestFletMain.test_clean`, smoke `--clean` |
| RNF-05 | Seguridad del lab: sin payloads reales, sin red externa, solo dentro del directorio del laboratorio | `security.yml` (bandit+review) |
| RNF-06 | Ventana 1280×800, mínima 960×600; toda vista larga tiene scroll propio | manual |
| RNF-07 | Cero carteles rojos de framework en ejecución: la API usada existe en el Flet instalado | `auditar_flet.py` (nombres, props, enums, métodos `Page`, `src=""`) |
| RNF-08 | Arranque sin excepciones en desktop y web | smoke `--web` + checklist |
| RNF-09 | Paleta neobrutalista de `gui/styles.py` (mismos hex en `gui_flet/theme.py`) | `TestTema` |
| RNF-10 | Cada script de `scripts/` soporta `--help`; generadores son idempotentes | `--help` + `--check` |

## Trazabilidad de bugs (histórico, no borrar)

| Bug | Causa | Fix | Guard |
|-----|-------|-----|-------|
| `Page.update_async() missing` | API 0.x asumida, eliminada en Flet 1.0 | `page.update()` sync | auditor caso 3 + stub sin `update_async` |
| Cartel rojo "valid src" en header | `Image(src="")` inválido en 1.0 | `visible=False` + src real | auditor caso 2b |
| Guía sin scroll, botonera pisando texto | `Markdown(expand)` sin ancestro scrollable | `Column(scroll=AUTO)` | assert scroll en `TestVistas` |
| Links de referencia muertos (10/14: OWASP migró, RedHat cambió slugs, wiki ES inexistente) | URLs sin verificación desde su alta | 10 reemplazos verificados (Wikipedia EN + MITRE ATT&CK) + `url_target=BLANK` | `--check-links` manual |

## Checklist manual (5 min, obligatorio antes de cerrar PR3)

1. `python flet_main.py --web` abre sin excepciones; dashboard limpio.
2. Click en ransomware: header con icono CIA, sin cartel rojo.
3. Simular → consola con salida; Guía → scroll de punta a punta.
4. Juego → dificultad media → responder → pista → finalizar con puntaje.
5. Clean → consola vacía; `--clean` deja el lab vacío.

## Fuera de alcance (ver roadmap)

- `.exe`/tar.gz y Releases (PR4). Producción Vercel (pausado). Firma de binarios macOS.
