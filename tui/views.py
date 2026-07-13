"""Generadores de contenido Markdown para la TUI."""

import os
from tui.config import MODULOS, NOMBRES_DEFENSA

def cia_icon(cia: str) -> str:
    return {"Confidencialidad": "🔒 C", "Integridad": "🛡️ I", "Disponibilidad": "⚡ A"}.get(cia, "?")

def render_dashboard_tutorial() -> str:
    return """
# 📊 CONTROL PANEL & TUTORIAL INICIAL
---
¡Bienvenido al **Laboratorio Educativo de Simulación Avanzada de Malware (E.A.S.M.L)**!

### 🎮 Controles de Navegación Rápida
*   `↑ / ↓` o Rueda del Ratón: Navega por la lista de módulos.
*   **`[W]` Simular:** Lanza el script de malware en el entorno controlado.
*   **`[E]` Defensa:** Ejecuta el script de mitigación o remediación.
*   **`[R]` Readme Max:** Expande la teoría técnica ocupando toda la pantalla derecha.
*   **`[Q]` Setup Lab:** Fuerza la reconstrucción limpia del laboratorio.
*   **`[D]` Clean:** Ejecuta el módulo de limpieza de entorno y vacía la consola.
*   **`[H]` Tutorial:** Regresa a esta pantalla de ayuda.
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