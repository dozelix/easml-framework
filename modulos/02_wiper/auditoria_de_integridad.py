#!/usr/bin/env python3
"""
Auditoría de Integridad de Archivos contra simulación de Wiper — Módulo 02.

Detecta archivos corruptos comparando hashes con el baseline del backup,
restaura el contenido original y realiza la auditoría post-mitigación.
"""

import os
import sys
import shutil
import argparse

# ── Configuración de rutas absolutas robustas ───────────────────────────────
_DIR_RAIZ = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, _DIR_RAIZ)

from core.base_module import BaseDefense
from modulos.common.utils import (
    log, safe_print, color, banner, hash_file, cleanup, write_log, find_lab_dir
)

class WiperDefense(BaseDefense):
    def __init__(self):
        self.dir_simulacion = find_lab_dir(_DIR_RAIZ)
        self.dir_backup = os.path.join(os.path.dirname(self.dir_simulacion), '.backup_wiper')
        self.log_defensa = 'defensa_wiper.log'
        self.archivos_lab = {
            'documento.txt', 'notas.txt', 'script.py', 'index.html',
            'datos.csv', 'leeme.md', 'imagen.png', 'imagen.jpg',
            'audio.mp3', 'documento.docx', 'planilla.xlsx', 'presentacion.pptx',
        }

    def analizar_y_mitigar(self) -> None:
        banner(
            "DEFENSA WIPER — DETECCION Y RESTAURACION",
            "Detecta archivos corruptos y restaura desde backup",
        )
        safe_print(color(
            "  Herramienta defensiva para detectar y remediar artefactos\n"
            "  del módulo 02 (wiper).\n", 'cyan',
        ))

        # FASE 1: Verificar backup
        self._paso_fase(1, "VERIFICACION — Comprobando disponibilidad de backup")
        tiene_backup, archivos_backup = self._verificar_backup()
        if not tiene_backup:
            self._imprimir_error_backup()
            return
        safe_print(color(f"  [OK] Backup encontrado: {len(archivos_backup)} archivos\n", 'green'))

        # FASE 2: Verificar directorio de simulación
        self._paso_fase(2, "VERIFICACION — Comprobando directorio de prueba")
        if not os.path.isdir(self.dir_simulacion):
            safe_print(color("  [OK] Directorio pruebas/ no existe. Nada que analizar.\n", 'green'))
            return
        safe_print(color(f"  Directorio encontrado: {self.dir_simulacion}\n", 'cyan'))

        # FASE 3: Comparar hashes (Análisis Baseline)
        self._paso_fase(3, "COMPARACION — Verificando integridad archivos vs backup")
        resultados = self._auditar_hashes()
        corruptos = [r for r in resultados if r['corrupto']]
        intactos = [r for r in resultados if not r['corrupto']]

        self._imprimir_analisis_hashes(corruptos, intactos)

        # FASE 4: Restauración
        if corruptos:
            self._paso_fase(4, "RESTAURACION — Copiando originales desde backup")
            self._restaurar_incidentes(corruptos)

        # FASE 5: Verificación post-mitigación
        self._paso_fase(5, "VERIFICACION — Hashes post-restauración")
        self._verificar_hashes_finales()

        # FASE 6: Resumen y Conclusiones del SOC
        self._paso_fase(6, "RESUMEN DE DEFENSA")
        self._imprimir_conclusiones_soc(resultados, corruptos, intactos)

        write_log("defensa_wiper", [
            "Escaneo defensivo completado",
            f"Archivos analizados: {len(resultados)}",
            f"Archivos corruptos: {len(corruptos)}",
        ])

    def limpiar_entorno(self) -> None:
        banner("DEFENSA WIPER — LIMPIEZA", "Eliminando artefactos de la simulación")
        removed = 0

        if os.path.isdir(self.dir_simulacion):
            shutil.rmtree(self.dir_simulacion)
            safe_print(color(f"  eliminado: directorio_pruebas/", 'green'))
            removed += 1

        if os.path.isdir(self.dir_backup):
            shutil.rmtree(self.dir_backup)
            safe_print(color(f"  eliminado: .backup_wiper/", 'green'))
            removed += 1

        removed += cleanup(patterns=[self.log_defensa, 'wiper_sim.log'])
        safe_print(color(f"\n  Limpieza completada: {removed} artefactos eliminados.", 'green'))
        safe_print(color("  Para restaurar archivos ejecuta: python core/lab_setup.py\n", 'cyan'))

    # ── Métodos de Soporte Internos (SRP) ─────────────────────────────────

    def _paso_fase(self, fase_num: int, titulo: str) -> None:
        safe_print(color(f"\n  [FASE {fase_num}] {titulo}", 'yellow'))
        safe_print(color(f"  {'─' * 55}", 'yellow'))

    def _verificar_backup(self) -> tuple:
        if not os.path.isdir(self.dir_backup):
            return False, []
        archivos = sorted([f for f in os.listdir(self.dir_backup) if os.path.isfile(os.path.join(self.dir_backup, f))])
        return True, archivos

    def _imprimir_error_backup(self) -> None:
        safe_print(color("  [!] No se encontró directorio de backup (.backup_wiper/).\n", 'red'))
        safe_print(color("  Esto significa que el wiper no corrió o el backup fue borrado.\n", 'yellow'))

    def _auditar_hashes(self) -> list:
        archivos_actuales = [
            os.path.join(self.dir_simulacion, f)
            for f in sorted(os.listdir(self.dir_simulacion))
            if os.path.isfile(os.path.join(self.dir_simulacion, f)) and f in self.archivos_lab
        ]
        resultados = []
        for ruta in archivos_actuales:
            nombre = os.path.basename(ruta)
            ruta_backup = os.path.join(self.dir_backup, nombre)

            h_actual = hash_file(ruta)
            h_backup = hash_file(ruta_backup) if os.path.exists(ruta_backup) else None

            corrupto = (h_actual != h_backup) if (h_backup and h_actual) else True
            resultados.append({
                'nombre': nombre, 'path': ruta, 'path_backup': ruta_backup,
                'hash_actual': h_actual, 'hash_backup': h_backup, 'corrupto': corrupto
            })
        return resultados

    def _imprimir_analisis_hashes(self, corruptos: list, intactos: list) -> None:
        if corruptos:
            safe_print(color(f"  [!] ALERTA: {len(corruptos)} archivos CORROMPIDOS detectados\n", 'red'))
            for r in corruptos:
                safe_print(color(f"    [CORROMPIDO] {r['nombre']}", 'red'))
                h_act = (r['hash_actual'][:40] + '...') if r['hash_actual'] else 'N/A'
                h_bak = (r['hash_backup'][:40] + '...') if r['hash_backup'] else 'N/A'
                safe_print(color(f"      Hash actual:   {h_act}", 'yellow'))
                safe_print(color(f"      Hash backup:   {h_bak}", 'green'))
        else:
            safe_print(color("  [OK] Todos los archivos están intactos (hashes coinciden).\n", 'green'))

        if intactos:
            safe_print(color(f"\n  Archivos intactos: {len(intactos)}", 'green'))

    def _restaurar_incidentes(self, corruptos: list) -> None:
        restaurados = 0
        for r in corruptos:
            print(color(f"    Restaurando {r['nombre']}...", 'cyan'), end=' ', flush=True)
            try:
                shutil.copy2(r['path_backup'], r['path'])
                if hash_file(r['path']) == r['hash_backup']:
                    safe_print(color("OK", 'green'))
                    restaurados += 1
                else:
                    safe_print(color("ERROR", 'red'))
            except Exception as e:
                safe_print(color(f"ERROR: {e}", 'red'))

    def _verificar_hashes_finales(self) -> None:
        if os.path.isdir(self.dir_simulacion):
            for nombre in sorted(os.listdir(self.dir_simulacion)):
                ruta = os.path.join(self.dir_simulacion, nombre)
                if os.path.isfile(ruta) and not nombre.endswith('.log'):
                    h = hash_file(ruta)
                    safe_print(color(f"    {nombre:30s} {(h[:48] + '...') if h else 'N/A'}", 'green'))

    def _imprimir_conclusiones_soc(self, resultados, corruptos, intactos) -> None:
        safe_print(color(f"  Archivos analizados:   {len(resultados)}", 'cyan'))
        safe_print(color(f"  Archivos corruptos:    {len(corruptos)}", 'red' if corruptos else 'green'))
        safe_print(color("  - Ransomware: cifra archivos (reversible con clave)\n  - Wiper: destruye archivos (irreversible sin backup)\n", 'cyan'))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Defensa contra simulación de Wiper")
    parser.add_argument('--clean', action='store_true', help='Limpiar el entorno')
    args = parser.parse_args()

    defensa = WiperDefense()
    if args.clean:
        defensa.limpiar_entorno()
    else:
        defensa.analizar_y_mitigar()