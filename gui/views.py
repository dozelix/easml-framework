"""Generadores de contenido para la GUI."""

import os
from collections import Counter
from tui.config import MODULOS, NOMBRES_DEFENSA


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _contar_archivos(directorio: str) -> int:
    if not os.path.isdir(directorio):
        return 0
    return len([f for f in os.listdir(directorio) if os.path.isfile(os.path.join(directorio, f))])


def dashboard() -> str:
    dir_lab = os.path.join(ROOT, 'directorio_pruebas')
    dir_logs = os.path.join(ROOT, 'lab_data', 'logs')

    archivos_lab = _contar_archivos(dir_lab)
    logs_lab = len([f for f in os.listdir(dir_logs) if f.endswith('.log')]) if os.path.isdir(dir_logs) else 0

    cia_counter = Counter(m[3] for m in MODULOS)
    estado = "🟢 Activo" if archivos_lab > 0 else "🔴 Vacío"

    return (
        "📊 DASHBOARD — Laboratorio E.A.S.M.L\n\n"
        f"  Estado: {estado} — {archivos_lab} archivos en directorio_pruebas/\n"
        f"  Logs:   {logs_lab} registros en lab_data/logs/\n\n"
        f"  MÓDULOS POR PILAR CIA\n\n"
        f"  🔒 Confidencialidad  {cia_counter.get('Confidencialidad', 0):2d}\n"
        f"  🛡️  Integridad         {cia_counter.get('Integridad', 0):2d}\n"
        f"  ⚡ Disponibilidad     {cia_counter.get('Disponibilidad', 0):2d}\n\n"
        f"  Total: {len(MODULOS)} módulos ordenados por CIS\n\n"
        "  Setup · Simular · Defensa · Readme · Clean · Dashboard · Juego"
    )


def tutorial() -> str:
    return (
        "🎓 TUTORIAL RÁPIDO\n\n"
        "  ¡Bienvenido! Este laboratorio te permite ejecutar 14 tipos de amenazas\n"
        "  de forma segura en un entorno aislado (directorio_pruebas/).\n\n"
        "  FLUJO DE TRABAJO\n\n"
        "  Preparar → Simular → Defender → Limpiar\n\n"
        "  1. Setup   — Genera archivos de prueba\n"
        "  2. Simular — Ejecuta la simulación del módulo seleccionado\n"
        "  3. Defensa — Mitiga la amenaza y restaura archivos\n"
        "  4. Clean   — Limpia consola y entorno\n\n"
        "  Los módulos están ordenados por control CIS (2→15) para\n"
        "  facilitar el aprendizaje progresivo de los estándares."
    )


def modulo_info(index: int) -> str:
    if index < 0 or index >= len(MODULOS):
        return "Selecciona un módulo de la lista."

    num, nombre, script, cia, cis, url_ref = MODULOS[index]
    nombre_defensa = NOMBRES_DEFENSA.get(num, "defensa")
    icono_cia = {"Confidencialidad": "🔒", "Integridad": "🛡️", "Disponibilidad": "⚡"}.get(cia, "?")
    dir_modulo = os.path.join(ROOT, 'modulos', nombre)
    arch_defensa = nombre_defensa.lower().replace(' ', '_')

    sim_ok = "✓" if os.path.exists(os.path.join(dir_modulo, f"{script}.py")) else "✗"
    def_ok = "✓" if os.path.exists(os.path.join(dir_modulo, f"{arch_defensa}.py")) else "✗"
    md_ok = "✓" if os.path.exists(os.path.join(dir_modulo, "README.md")) else "—"

    return (
        f"🔍 {nombre}\n\n"
        f"  {icono_cia}  {cia}\n"
        f"  {cis}\n\n"
        f"  {sim_ok}  Simulación: {script}.py\n"
        f"  {def_ok}  Defensa:     {arch_defensa}.py\n"
        f"  {md_ok}  Documentación\n\n"
        f"  {url_ref}"
    )


def leer_readme(index: int) -> str | None:
    if index < 0 or index >= len(MODULOS):
        return None
    num, nombre = MODULOS[index][0], MODULOS[index][1]
    readme_path = os.path.join(ROOT, 'modulos', nombre, "README.md")
    if os.path.exists(readme_path):
        with open(readme_path, "r", encoding="utf-8") as f:
            return f.read()
    return None
