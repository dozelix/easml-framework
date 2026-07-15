# Changelog

## [3.2.3] - 2026-07-14

### Added
- nuevo renderizador de guias con Text widget + tags estilizados (fondo crema)
- etiquetado semantico de markdown: encabezados, negritas, codigo inline, bloques de codigo

### Changed
- boton "Readme" renombrado a "Guia" (espanol)
- README se renderiza con Text widget directamente, sin pasar por HTML/tkhtmlview
- fondo de documentacion cambiado de blanco puro (#FFFFFF) a crema suave (#FAF7F2)

### Removed
- dependencia `tkhtmlview` de requirements.txt y documentacion
- funcion `md_to_html()` (obsoleta por el nuevo renderizador directo)
- import de HTMLLabel en gui/main.py

## [3.2.0] - 2026-07-14

### Added
- generacion de iconos PNG para CIA, estado y checks en assets/
- URLs clickables en panel de contenido (webbrowser + tag_bind)
- changelog.md para historial de cambios

### Changed
- migracion a modo claro neobrutalista con bordes #1A1A1A
- dashboard, tutorial e info de modulos ahora usan widgets (Frame, Label, Card)
  en vez de texto plano en Text widget
- consola cambia a fondo oscuro #1A1A1A con texto verde #9ECE6A
- reemplazo de todos los emojis Unicode por iconos PNG o texto semantico
- eliminacion de CIS redundante en cuerpo del modulo (solo en header)
- correccion de caracter chino en desafio de keylogger

### Removed
- dependencia `textual` de requirements.txt
- todas las referencias a TUI/Textual en documentacion y diagramas

## [3.1.0] - 2026-07-14

### Added
- flujo de bugs documentado en AGENTS.md

### Changed
- requirements.txt: pillow, tkhtmlview, markdown como obligatorios
- AGENTS.md: entry point actualizado, requisitos sin opcionales

### Removed
- referencias TUI/Textual de README.md y AGENTS.md

## [3.0.0] - 2026-07-14

### Changed
- migracion completa de TUI (Textual) a GUI (tkinter)
