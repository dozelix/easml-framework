"""Generadores de contenido Markdown para la TUI."""

import os
from tui.config import MODULOS, NOMBRES_DEFENSA

def cia_icon(cia: str) -> str:
    return {"Confidencialidad": "🔒 C", "Integridad": "🛡️ I", "Disponibilidad": "⚡ A"}.get(cia, "?")


def render_tutorial() -> str:
    """Tutorial guiado paso a paso — se muestra al inicio y con [H]."""
    return """
# 🎓 Tutorial Rápido — Laboratorio E.A.S.M.L

---

## Paso 1: Bienvenida

¡Bienvenido al **Laboratorio Educativo de Simulación Avanzada de Malware**!

Este laboratorio te permite ejecutar 14 tipos de amenazas de forma segura
y controlada, dentro de un entorno aislado (`directorio_pruebas/`).
Todo es una simulación educativa — **no se genera malware real**.

---

## Paso 2: ¿Cómo funciona?

El flujo es simple:

```
Preparar → Simular → Defender → Limpiar
```

1. **Preparas** el entorno con archivos de prueba (`[Q]`)
2. **Seleccionas** un módulo de la lista izquierda (flechas o ratón)
3. **Simulas** el ataque con `[W]`
4. **Defiendes** con `[E]` para ver cómo se mitiga
5. **Limpias** todo con `[D]`

---

## Paso 3: Guía de controles paso a paso

### `[Q]` — Setup (Preparar entorno)
Genera 12 archivos de prueba (texto, imágenes, documentos) en `directorio_pruebas/`.
Ejecútalo **antes** de simular por primera vez.

### `[W]` — Simular (Lanzar amenaza)
Ejecuta el script de simulación del módulo seleccionado.
Verás en tiempo real cómo el malware afecta los archivos de prueba.

### `[E]` — Defensa (Mitigar)
Ejecuta el script de defensa del mismo módulo.
Detecta los artefactos, los analiza y restaura el entorno.

### `[R]` — Readme Max (Documentación)
Expande el README del módulo para leer la teoría completa
(historia, Tríada CIA, Controles CIS, ejercicios).

### `[D]` — Clean (Limpiar)
Vacía la consola y restablece el entorno de pruebas a su estado original.

### `[H]` — Tutorial (Volver aquí)
Regresa a este tutorial en cualquier momento.

### `↑ / ↓` — Navegar
Usa las flechas del teclado o la rueda del ratón para navegar la lista.

### `ESC` — Salir
Abre una ventana de confirmación para cerrar la TUI de forma segura.

---

## Paso 4: Listo para empezar

Selecciona un módulo de la lista izquierda y presiona `[Q]` para preparar el entorno.
Luego `[W]` para simular, y `[E]` para defenderte.

> **Recuerda:** Puedes volver a este tutorial en cualquier momento presionando **`[H]`**.
"""


def render_modulo_info(index: int, modulos_dir: str) -> str:
    if index < 0 or index >= len(MODULOS):
        return "# Error\n\n_Selecciona un módulo válido._"

    num, nombre, script, cia, cis, url_referencia = MODULOS[index]
    icono_cia = cia_icon(cia)
    nombre_defensa_tecnico = NOMBRES_DEFENSA.get(num, "defensa")

    nombre_defensa_archivo = NOMBRES_DEFENSA.get(num, "defensa").lower().replace(' ', '_')

    dir_modulo = os.path.join(modulos_dir, f"{num}_{nombre}")
    sim_ok = "🟢" if os.path.exists(os.path.join(dir_modulo, f"{script}.py")) else "🔴"
    def_ok = "🟢" if os.path.exists(os.path.join(dir_modulo, f"{nombre_defensa_archivo}.py")) else "🔴"
    md_ok  = "🟢" if os.path.exists(os.path.join(dir_modulo, "README.md")) else "🟡"

    return f"""
# 🔍 Análisis de Módulo: {num}_{nombre}
---

### 🛡️ Clasificación de Seguridad (Frameworks)
*   **Dimensión Crítica (Tríada CIA):** {icono_cia} ({cia})
*   **Control de Mitigación Asociado:** {cis}

### 📂 Estado de Componentes Locales
*   {sim_ok} `{script}.py` *(Tecla [W] — Simular ataque)*
*   {def_ok} `{nombre_defensa_tecnico.lower().replace(' ', '_')}.py` *(Tecla [E] — Desplegar contramedida)*
*   {md_ok} `README.md` *(Tecla [R] — Documentación extendida)*

---
### 🌐 Documentación Técnica de Referencia
Para estudiar en profundidad los vectores globales y contramedidas de este tipo de amenaza, consulta la base de conocimiento oficial de la comunidad:

👉 **[Consultar documentación en línea (OWASP / Red Hat / Wikipedia)]({url_referencia})**
"""