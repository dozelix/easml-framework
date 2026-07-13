#!/usr/bin/env python3
"""
Módulo 11 — Bomba Lógica (Educativo)

Simula una bomba lógica con múltiples condiciones de activación (fecha,
existencia de archivo, variable de entorno, umbral de archivos, horario).
El payload es solo un mensaje educativo inofensivo impreso por pantalla.

Todas las operaciones se confinan al directorio directorio_pruebas/.

Uso:
    python modulos/11_logic_bomb/logic_bomb.py          Ejecutar simulación
    python modulos/11_logic_bomb/logic_bomb.py --clean  Limpiar artefactos
    python modulos/11_logic_bomb/logic_bomb.py --help   Mostrar ayuda
"""
import os
import sys
import json
import time
import datetime

# ── Configurar path para importar core.common ──
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from modulos.common.utils import (
    log, safe_print, color, banner, cleanup, write_log, find_lab_dir
)

# ── Constantes ──────────────────────────────────────────
# Directorio de trabajo confinado
LAB_DIR = find_lab_dir(os.path.dirname(os.path.abspath(__file__)))
BOMB_MARKER = os.path.join(LAB_DIR, "logic_bomb_marker.json")
BOMB_LOG = os.path.join(LAB_DIR, "logic_bomb.log")
TRIGGER_FILE = os.path.join(LAB_DIR, "_trigger_bomb.txt")


# ── Clase para condiciones de activación ──
class CondicionBomba:
    """
    Representa una condición de activación de la bomba lógica.
    Cada condición tiene un nombre, descripción y función de verificación.
    """

    def __init__(self, nombre, descripcion, verificar_fn):
        self.nombre = nombre
        self.descripcion = descripcion
        self.verificar = verificar_fn
        self.cumplida = False

    def evaluar(self):
        """Evalúa la condición y almacena el resultado."""
        self.cumplida = self.verificar()
        return self.cumplida


def crear_condiciones():
    """
    Crea las 5 condiciones de activación de la bomba lógica.
    Cada condición simula un disparador diferente que una bomba real podría usar.
    """
    ahora = datetime.datetime.now()

    # Condición 1: Fecha/hora específica
    # En una time bomb real, la fecha sería futura y el programa la verificaría
    # en cada ejecución hasta que se alcance la fecha objetivo.
    fecha_objetivo = ahora  # Se activa "ahora" para demostración
    def verificar_fecha():
        return datetime.datetime.now() >= fecha_objetivo

    # Condición 2: Existencia de archivo trigger
    # Un empleado podría configurar la bomba para activarse si se crea un
    # archivo específico (ej: si lo despiden y crean un archivo de baja).
    def verificar_archivo():
        return os.path.exists(TRIGGER_FILE)

    # Condición 3: Variable de entorno específica
    # La bomba verifica una variable de entorno que el atacante podría
    # configurar remotamente para activar la bomba.
    var_trigger = "BOMB_ACTIVE"
    def verificar_entorno():
        return os.environ.get(var_trigger) == "1"

    # Condición 4: Número de archivos en directorio
    # Simula una condición basada en umbral: si se eliminan muchos archivos
    # (posible desinstalación), la bomba se activa como represalia.
    umbral_archivos = 5
    def verificar_archivos():
        return len([f for f in os.listdir(LAB_DIR)
                    if os.path.isfile(os.path.join(LAB_DIR, f))]) > umbral_archivos

    # Condición 5: Horario del día
    # La bomba solo se activa durante horario laboral para maximizar daño.
    hora_inicio, hora_fin = 9, 17
    def verificar_hora():
        return hora_inicio <= datetime.datetime.now().hour <= hora_fin

    return [
        CondicionBomba(
            "fecha_hora",
            f"Fecha/hora actual >= {fecha_objetivo.strftime('%Y-%m-%d %H:%M:%S')}",
            verificar_fecha
        ),
        CondicionBomba(
            "archivo_trigger",
            f"Archivo '_trigger_bomb.txt' existe en directorio de trabajo",
            verificar_archivo
        ),
        CondicionBomba(
            "variable_entorno",
            f"Variable de entorno BOMB_ACTIVE=1",
            verificar_entorno
        ),
        CondicionBomba(
            "umbral_archivos",
            f"Más de {umbral_archivos} archivos en directorio de trabajo",
            verificar_archivos
        ),
        CondicionBomba(
            "horario_laboral",
            f"Hora actual entre {hora_inicio}:00 y {hora_fin}:00",
            verificar_hora
        ),
    ]


def ejecutar_payload():
    """
    Payload completamente inofensivo: solo imprime un mensaje.
    En un escenario malicioso, aquí se ejecutaría la carga dañina:
    borrado de archivos, cifrado, exfiltración de datos, etc.
    """
    safe_print(color("\n" + "=" * 60, 'red'))
    safe_print(color("  ¡BOMBA LÓGICA ACTIVADA! (Simulación educativa)", 'red'))
    safe_print(color("=" * 60, 'red'))
    safe_print(color(
        "  Este es el PAYLOAD de una bomba lógica simulada.\n"
        "  En un escenario malicioso, aquí se ejecutaría la\n"
        "  carga dañina (borrado de archivos, cifrado, etc.)\n"
        "  Pero en esta simulación, solo imprimimos este mensaje.", 'yellow'
    ))
    safe_print(color("=" * 60, 'red'))


def paso_fase(fase_num, titulo):
    """Muestra un separador visual de fase en la consola."""
    safe_print(color(f"\n  [FASE {fase_num}] {titulo}", 'yellow'))
    safe_print(color(f"  {'─' * 55}", 'yellow'))
    time.sleep(0.3)


# ── Limpieza ──
def limpiar():
    """Elimina todos los artefactos generados por la simulación de bomba lógica."""
    banner("MÓDULO 11 — BOMBA LÓGICA — LIMPIEZA",
           "Eliminando artefactos de la simulación")

    removidos = cleanup(
        files_to_remove=[BOMB_MARKER, BOMB_LOG, TRIGGER_FILE],
        patterns=[os.path.join(LAB_DIR, "logic_bomb_*.log")]
    )
    safe_print(color(f"\n  Limpieza completada: {removidos} archivos eliminados.\n", 'green'))


# ── Simulación principal ──
def ejecutar():
    """Ejecuta la simulación completa de bomba lógica educativa."""
    banner("MÓDULO 11 — BOMBA LÓGICA — SIMULACIÓN EDUCATIVA",
           "Simulación de bomba lógica con múltiples condiciones de activación")

    # Crear directorio de trabajo si no existe
    os.makedirs(LAB_DIR, exist_ok=True)
    safe_print(color(f"  Directorio de trabajo: {LAB_DIR}\n", 'cyan'))

    # ── FASE 1: Explicar el concepto ──
    paso_fase(1, "CONCEPTO — ¿Qué es una bomba lógica?")
    safe_print(color(
        "  Una bomba lógica es código malicioso que se activa cuando\n"
        "  se cumple una condición específica. A diferencia de un virus,\n"
        "  no se propaga — espera pacientemente a que se cumpla el\n"
        "  disparador (trigger).", 'white'
    ))
    safe_print(color(
        "  Tipos principales:", 'cyan'
    ))
    safe_print(color("    • Time bomb: Se activa en una fecha/hora específica", 'white'))
    safe_print(color("    • Logic bomb: Se activa por una condición lógica", 'white'))
    safe_print(color("    • Combo bomb: Combina múltiples condiciones", 'white'))
    time.sleep(0.3)

    # ── FASE 2: Definir condiciones ──
    paso_fase(2, "CONFIGURACIÓN — Definiendo condiciones de activación")
    condiciones = crear_condiciones()
    for i, cond in enumerate(condiciones, 1):
        safe_print(color(f"  [{i}] {cond.nombre}", 'yellow'))
        safe_print(color(f"      Descripción: {cond.descripcion}", 'white'))
    time.sleep(0.3)

    # ── FASE 3: Evaluar condiciones ──
    paso_fase(3, "EVALUACIÓN — Verificando cada condición")
    resultados = []
    for i, cond in enumerate(condiciones, 1):
        resultado = cond.evaluar()
        resultados.append(resultado)
        estado = "CUMPLIDA" if resultado else "NO CUMPLIDA"
        estilo = 'red' if resultado else 'green'
        safe_print(color(f"  [{i}] {cond.nombre}: {estado}", estilo))
        time.sleep(0.15)

    # ── FASE 4: Determinar activación ──
    paso_fase(4, "ANÁLISIS — Determinando si la bomba se activa")
    cumplen = sum(resultados)
    total = len(resultados)
    safe_print(color(f"  Condiciones cumplidas: {cumplen}/{total}", 'yellow'))

    # La bomba se activa si al menos 2 condiciones se cumplen (umbral configurable)
    umbral_activacion = 2
    activa = cumplen >= umbral_activacion

    if activa:
        safe_print(color(f"  Umbral de activación: >= {umbral_activacion} condiciones", 'red'))
        safe_print(color(f"  RESULTADO: BOMBA ACTIVA", 'red'))
    else:
        safe_print(color(f"  Umbral de activación: >= {umbral_activacion} condiciones", 'green'))
        safe_print(color(f"  RESULTADO: BOMBA INACTIVA", 'green'))

    # ── FASE 5: Ejecutar payload si activa ──
    if activa:
        paso_fase(5, "DETENCIÓN — Ejecutando payload de la bomba")
        ejecutar_payload()
    else:
        paso_fase(5, "SEGURIDAD — Bomba no activada")
        safe_print(color("  El payload NO se ejecutó porque la bomba está inactiva.", 'green'))

    # ── FASE 6: Guardar estado ──
    paso_fase(6, "REGISTRO — Guardando estado de la bomba")
    estado_bomb = {
        "nombre": "SimLogicBomb-01",
        "tipo": "logica",
        "creada": datetime.datetime.now().isoformat(),
        "condiciones": [
            {
                "nombre": c.nombre,
                "descripcion": c.descripcion,
                "cumplida": c.cumplida,
            }
            for c in condiciones
        ],
        "umbral_activacion": umbral_activacion,
        "condiciones_cumplidas": cumplen,
        "activa": activa,
        "payload_ejecutado": activa,
    }
    with open(BOMB_MARKER, 'w', encoding='utf-8') as f:
        json.dump(estado_bomb, f, indent=2, ensure_ascii=False)
    safe_print(color(f"  → logic_bomb_marker.json guardado", 'green'))

    # ── FASE 7: Guardar log ──
    log_entries = [
        f"Bomba lógica evaluada",
        f"Condiciones definidas: {total}",
        f"Condiciones cumplidas: {cumplen}",
        f"Bomba activa: {activa}",
        f"Payload ejecutado: {activa}",
    ]
    for c in condiciones:
        log_entries.append(
            f"  {c.nombre}: {'SI' if c.cumplida else 'NO'} — {c.descripcion}"
        )
    write_log("LOGIC_BOMB", log_entries, BOMB_LOG)
    safe_print(color(f"  → logic_bomb.log guardado", 'green'))

    # ── RESUMEN ──
    safe_print(color("\n" + "=" * 60, 'cyan'))
    safe_print(color("  RESUMEN DE LA SIMULACIÓN DE BOMBA LÓGICA", 'bold'))
    safe_print(color("=" * 60, 'cyan'))
    safe_print(color(f"  Condiciones evaluadas:  {total}", 'white'))
    safe_print(color(f"  Condiciones cumplidas:  {cumplen}", 'white'))
    safe_print(color(f"  Umbral de activación:   {umbral_activacion}", 'white'))
    safe_print(color(f"  Estado:                 {'ACTIVA' if activa else 'INACTIVA'}",
                      'red' if activa else 'green'))
    safe_print(color(f"  Payload:                {'EJECUTADO' if activa else 'NO EJECUTADO'}",
                      'red' if activa else 'green'))
    safe_print(color("=" * 60, 'cyan'))
    safe_print(color(
        "\n  NOTA: Las bombas lógicas son difíciles de detectar porque\n"
        "  el código legítimo puede contener condicionales ocultos.\n"
        "  Los ataques de insiders frecuentemente usan esta técnica.\n",
        'yellow'
    ))
    log("Simulación de bomba lógica completada")


if __name__ == "__main__":
    if "--help" in sys.argv:
        print(__doc__)
        sys.exit(0)
    if "--clean" in sys.argv:
        limpiar()
        sys.exit(0)
    ejecutar()
