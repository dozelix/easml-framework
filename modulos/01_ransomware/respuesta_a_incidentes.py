#!/usr/bin/env python3
"""
Módulo de Defensa contra Ransomware — Módulo 01 (POO).

Detecta archivos con extensión .locked, revierte la inversión de texto
para recuperar los archivos originales y genera reportes en lab_data/logs/.
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

class RansomwareDefense(BaseDefense):
    def __init__(self):
        self.dir_simulacion = find_lab_dir(_DIR_RAIZ)
        # Forzar que el log vaya estrictamente a lab_data/logs/
        self.dir_logs = os.path.join(os.path.dirname(self.dir_simulacion), 'logs')
        self.extension_locked = '.locked'
        self.nota_rescate = 'README_RESCATE.txt'

    def analizar_y_mitigar(self) -> None:
        banner(
            "DEFENSA RANSOMWARE — REMEDIACION Y DESCRIPTACION",
            "Detecta archivos .locked y revierte la inversión de texto",
        )

        if not os.path.isdir(self.dir_simulacion):
            safe_print(color("  [!] El directorio de simulación no existe. ¿Ya atacaste?.\n", 'red'))
            return

        # FASE 1: Análisis del entorno afectado
        self._paso_fase(1, "ANALISIS — Buscando archivos afectados y notas de rescate")
        archivos_locked, nota_encontrada = self._analizar_sistema()

        # FASE 2: Mitigación / Desencriptación
        if archivos_locked:
            self._paso_fase(2, "MITIGACION — Revirtiendo el cifrado de texto")
            self._desencriptar_archivos(archivos_locked)
        else:
            safe_print(color("  [OK] No se encontraron archivos `.locked` para procesar.", 'green'))

        # FASE 3: Eliminación de persistencia / Nota de rescate
        if nota_encontrada:
            self._paso_fase(3, "ELIMINACION DE ARTEFACTOS — Removiendo nota de rescate")
            self._eliminar_nota()

        # FASE 4: Reporte y Logs
        self._paso_fase(4, "AUDITORIA — Guardando reporte en logs/")
        os.makedirs(self.dir_logs, exist_ok=True)
        
        # Guardamos el log dentro de lab_data/logs/ de forma explícita
        lineas_log = [
            "Escaneo y mitigacion de ransomware completado.",
            f"Archivos recuperados: {len(archivos_locked)}",
            f"Nota de rescate eliminada: {nota_encontrada}"
        ]
        write_log(os.path.join(self.dir_logs, "ransomware_defensa"), lineas_log)
        safe_print(color(f"  [+] Log de auditoría guardado en: {self.dir_logs}/ransomware_defensa.log", 'green'))

    def limpiar_entorno(self) -> None:
        banner("DEFENSA RANSOMWARE — LIMPIEZA TOTAL", "Eliminando laboratorio de ransomware")
        if os.path.isdir(self.dir_simulacion):
            shutil.rmtree(self.dir_simulacion)
            safe_print(color(f"  eliminado: {self.dir_simulacion}", 'green'))

        # Limpiar logs específicos de este módulo dentro de lab_data/logs/
        log_ataque = os.path.join(self.dir_logs, "ransomware_sim.log")
        log_defensa = os.path.join(self.dir_logs, "ransomware_defensa.log")
        
        for path_log in [log_ataque, log_defensa]:
            if os.path.exists(path_log):
                os.remove(path_log)
                safe_print(color(f"  eliminado: {os.path.basename(path_log)}", 'green'))

        safe_print(color("\n  Limpieza completada. Usa core/lab_setup.py para rearmar.", 'cyan'))

    # ── Métodos de Soporte Internos ───────────────────────────────────────
    def _paso_fase(self, num, titulo):
        safe_print(color(f"\n  [FASE {num}] {titulo}\n  {'─' * 55}", 'yellow'))

    def _analizar_sistema(self):
        archivos = os.listdir(self.dir_simulacion)
        archivos_locked = []
        nota_encontrada = False

        for f in sorted(archivos):
            ruta_completa = os.path.join(self.dir_simulacion, f)
            if f == self.nota_rescate:
                nota_encontrada = True
                safe_print(color(f"    [!] Amenaza Activa: Nota de rescate detectada -> {f}", 'red'))
            elif f.endswith(self.extension_locked):
                archivos_locked.append(ruta_completa)
                safe_print(color(f"    [!] Archivo Cifrado: Detectado -> {f}", 'yellow'))
        
        return archivos_locked, nota_encontrada

    def _desencriptar_archivos(self, objetivos):
        for ruta_locked in objetivos:
            nombre_locked = os.path.basename(ruta_locked)
            nombre_original = nombre_locked.replace(self.extension_locked, '')
            ruta_original = os.path.join(self.dir_simulacion, nombre_original)

            try:
                # Leer el contenido "cifrado" (invertido)
                with open(ruta_locked, 'r', encoding='utf-8', errors='ignore') as f:
                    contenido_cifrado = f.read()

                # Deshacer la inversión de texto
                contenido_restaurado = contenido_cifrado[::-1]

                # Guardar el archivo recuperado con su nombre original
                with open(ruta_original, 'w', encoding='utf-8') as f:
                    f.write(contenido_restaurado)

                # Eliminar el archivo .locked del malware
                os.remove(ruta_locked)

                hash_restaurado = hash_file(ruta_original)
                h_disp = (hash_restaurado[:32] + '...') if hash_restaurado else 'N/A'

                safe_print(color(f"    [REMEDIADO] {nombre_locked} -> {nombre_original}", 'green'))
                safe_print(color(f"      Hash Verificado: {h_disp}", 'green'))
                log(f"Restaurado con éxito: {nombre_original}")

            except Exception as e:
                safe_print(color(f"    [!] Error al desencriptar {nombre_locked}: {e}", 'red'))

    def _eliminar_nota(self):
        ruta_nota = os.path.join(self.dir_simulacion, self.nota_rescate)
        try:
            if os.path.exists(ruta_nota):
                os.remove(ruta_nota)
                safe_print(color(f"    [+] {self.nota_rescate} eliminada de forma segura.", 'green'))
                log("Nota de rescate destruida por el sistema de defensa.")
        except Exception as e:
            safe_print(color(f"    [!] No se pudo eliminar la nota: {e}", 'red'))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Módulo de Defensa Ransomware")
    parser.add_argument('--clean', action='store_true', help='Limpia los entornos asociados')
    args = parser.parse_args()

    defensa = RansomwareDefense()
    if args.clean:
        defensa.limpiar_entorno()
    else:
        defensa.analizar_y_mitigar()