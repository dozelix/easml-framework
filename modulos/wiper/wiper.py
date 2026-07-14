#!/usr/bin/env python3
"""
Simulación educativa de Wiper — Módulo 02.

Demuestra el comportamiento de un malware destructivo que corrompe archivos
sobreescribiendo los primeros 64 bytes con datos basura.
"""

import os
import sys
import shutil
import random
import argparse
import time

# ── Configuración de rutas absolutas robustas ───────────────────────────────
_DIR_RAIZ = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, _DIR_RAIZ)

from core.base_module import BaseThreat
from modulos.common.utils import (
    log, safe_print, color, banner, traverse_lab_files,
    hash_file, read_file, cleanup, write_log, is_lab_ready,
    LOG_LINES, find_lab_dir,
)

class WiperThreat(BaseThreat):
    def __init__(self):
        self.dir_simulacion = find_lab_dir(_DIR_RAIZ)
        self.dir_backup = os.path.join(os.path.dirname(self.dir_simulacion), '.backup_wiper')
        self.bytes_a_corromper = 64
        self.extensiones_objetivo = {
            '.txt', '.py', '.html', '.csv', '.md',
            '.png', '.jpg', '.mp3', '.docx', '.xlsx', '.pptx',
        }

    def ejecutar(self) -> None:
        banner(
            "WIPER — SIMULACION EDUCATIVA",
            "Malware destructivo: corrompe archivos sin buscar rescate",
        )
        safe_print(color(
            "  Este script simula un wiper (Shamoon, HermeticWiper, etc.)\n"
            "  Los archivos originales se preservan en .backup_wiper/ para restaurar.\n",
            'cyan',
        ))

        if not is_lab_ready():
            safe_print(color("  [!] No se encontraron archivos del laboratorio.", 'red'))
            safe_print(color("  Ejecuta primero: python core/lab_setup.py", 'red'))
            sys.exit(1)

        # FASE 1: Preparación
        self._paso_fase(1, "PREPARACION — Copiando archivos a directorio de prueba")
        log("Fase 1: Preparación del entorno")
        self._preparar_directorio()

        # FASE 2: Infección
        self._paso_fase(2, "INFECCION — El wiper se activa en el sistema")
        log("Fase 2: Infección")
        self._imprimir_contexto_historico()

        # FASE 3: Backup de originales
        self._paso_fase(3, "BACKUP — Creando copia segura antes de la destrucción")
        log("Fase 3: Backup de originales")
        archivos_lab = traverse_lab_files(self.dir_simulacion)
        self._crear_backup_seguro(archivos_lab)

        # FASE 4: Reconocimiento
        self._paso_fase(4, "RECONOCIMIENTO — Identificando archivos objetivo")
        log("Fase 4: Reconocimiento")
        archivos_objetivo = self._filtrar_objetivos(archivos_lab)

        # FASE 5: Corrupción masiva
        self._paso_fase(5, "CORRUPCION — Sobreescribiendo datos con basura aleatoria")
        log("Fase 5: Corrupción de archivos")
        self._ejecutar_corrupcion(archivos_objetivo)

        # FASE 6: Eliminación de copias de seguridad virtuales
        self._paso_fase(6, "ELIMINACION DE BACKUPS — Comandos típicos del wiper")
        log("Fase 6: Eliminación de backups del sistema")
        self._simular_eliminacion_backups()

        # FASE 7: Diferencia Ransomware vs Wiper
        self._paso_fase(7, "COMPARACION: RANSOMWARE vs WIPER")
        self._imprimir_comparativa()

        write_log("wiper_sim", list(LOG_LINES))

    def limpiar(self) -> None:
        banner("WIPER — LIMPIEZA", "Eliminando artefactos de la simulación")
        removed = 0

        if os.path.isdir(self.dir_simulacion):
            shutil.rmtree(self.dir_simulacion)
            safe_print(color(f"  eliminado: directorio_pruebas/", 'green'))
            removed += 1

        if os.path.isdir(self.dir_backup):
            shutil.rmtree(self.dir_backup)
            safe_print(color(f"  eliminado: .backup_wiper/", 'green'))
            removed += 1

        removed += cleanup(patterns=['wiper_sim.log'])

        safe_print(color(f"\n  Limpieza completada: {removed} artefactos eliminados.", 'green'))
        safe_print(color("  Para restaurar archivos ejecuta: python core/lab_setup.py\n", 'cyan'))

    # ── Métodos de Soporte Internos (SRP) ─────────────────────────────────

    def _paso_fase(self, fase_num: int, titulo: str) -> None:
        safe_print(color(f"\n  [FASE {fase_num}] {titulo}", 'yellow'))
        safe_print(color(f"  {'─' * 55}", 'yellow'))
        time.sleep(0.3)

    def _preparar_directorio(self) -> None:
        os.makedirs(self.dir_simulacion, exist_ok=True)
        archivos_lab = traverse_lab_files(_DIR_RAIZ)
        lab_files = {
            'documento.txt', 'notas.txt', 'script.py', 'index.html',
            'datos.csv', 'leeme.md', 'imagen.png', 'imagen.jpg',
            'audio.mp3', 'documento.docx', 'planilla.xlsx', 'presentacion.pptx',
        }
        copiados = 0
        for archivo in archivos_lab:
            nombre = os.path.basename(archivo)
            if nombre not in lab_files:
                continue
            destino = os.path.join(self.dir_simulacion, nombre)
            if not os.path.exists(destino):
                shutil.copy2(archivo, destino)
                copiados += 1

        log(f"Directorio preparado: {self.dir_simulacion} ({copiados} archivos)")
        safe_print(color(f"  Directorio de trabajo: {self.dir_simulacion}", 'green'))
        safe_print(color(f"  Archivos copiados: {copiados}\n", 'green'))

    def _imprimir_contexto_historico(self) -> None:
        safe_print(color(
            "  En un ataque real (Shamoon 2012), el wiper se activa en una\n"
            "  hora programada (3:08 AM) y sobreescribe archivos con una\n"
            "  imagen de bandera estadounidense.\n", 'cyan'
        ))
        safe_print(color(
            "  HermeticWiper (2022) usaba un driver legítimo firmado (WinMon32.sys)\n"
            "  para causar corrupción a nivel de disco.\n", 'cyan'
        ))
        time.sleep(0.5)

    def _crear_backup_seguro(self, archivos_objetivo: list) -> None:
        if os.path.exists(self.dir_backup):
            shutil.rmtree(self.dir_backup)
        os.makedirs(self.dir_backup, exist_ok=True)

        for ruta in archivos_objetivo:
            nombre = os.path.basename(ruta)
            destino = os.path.join(self.dir_backup, nombre)
            shutil.copy2(ruta, destino)

        log(f"Backup seguro creado: {self.dir_backup} ({len(archivos_objetivo)} archivos)")
        safe_print(color(f"  Backup creado: {len(archivos_objetivo)} archivos en .backup_wiper/", 'green'))

    def _filtrar_objetivos(self, archivos_lab: list) -> list:
        safe_print(color("  El wiper enumera todos los archivos accesibles:\n", 'cyan'))
        objetivos = []
        for archivo in archivos_lab:
            nombre = os.path.basename(archivo)
            _, ext = os.path.splitext(nombre)
            if ext.lower() in self.extensiones_objetivo:
                objetivos.append(archivo)
                safe_print(color(f"    [+] {nombre} ({os.path.getsize(archivo)} bytes) — OBJETIVO", 'green'))
            else:
                safe_print(color(f"    [-] {nombre} — ignorado", 'blue'))
        return objetivos

    def _ejecutar_corrupcion(self, objetivos: list) -> None:
        safe_print(color(
            f"  Sobreescribiendo los primeros {self.bytes_a_corromper} bytes de cada archivo.\n"
            "  En un wiper real se sobreescribiria TODO el archivo.\n", 'cyan'
        ))

        for ruta in objetivos:
            nombre = os.path.basename(ruta)
            datos_originales = read_file(ruta)
            if datos_originales is None:
                safe_print(color(f"    [!] No se pudo corromper: {nombre}", 'red'))
                continue

            hash_orig = hash_file(ruta)
            datos_corruptos = bytearray(datos_originales)
            tamano_corromper = min(self.bytes_a_corromper, len(datos_corruptos))
            basura = bytes([random.randint(0, 255) for _ in range(tamano_corromper)])
            datos_corruptos[:tamano_corromper] = basura

            with open(ruta, 'wb') as f:
                f.write(datos_corruptos)

            hash_corr = hash_file(ruta)
            hash_orig_disp = (hash_orig[:32] + '...') if hash_orig else 'N/A'
            hash_corr_disp = (hash_corr[:32] + '...') if hash_corr else 'N/A'

            safe_print(color(f"    [CORROMPIDO] {nombre}", 'red'))
            safe_print(color(f"      Hash original:  {hash_orig_disp}", 'green'))
            safe_print(color(f"      Hash corrupto:  {hash_corr_disp}", 'red'))
            log(f"  Corrupto: {nombre} (hash: {hash_orig_disp} -> {hash_corr_disp})")

    def _simular_eliminacion_backups(self) -> None:
        safe_print(color("  En un ataque real, el wiper ejecutaría:\n", 'cyan'))
        comandos_wiper = [
            ("vssadmin delete shadows /all /quiet", "Elimina shadow copies de Windows"),
            ("bcdedit /set {default} recoveryenabled No", "Deshabilita recuperación"),
            ("wbadmin delete catalog -quiet", "Elimina catálogo de backups"),
        ]
        for cmd, desc in comandos_wiper:
            safe_print(color(f"    $ {cmd}", 'red'))
            safe_print(color(f"      -> {desc}", 'yellow'))
        safe_print(color("\n  Aquí solo simulamos la acción. Nada se ejecuta realmente.\n", 'cyan'))

    def _imprimir_comparativa(self) -> None:
        safe_print(color("\n  RANSOMWARE (Módulo 01):", 'green'))
        safe_print(color("    - Cifra archivos (reversible con clave)\n    - Deja nota de rescate\n    - Objetivo: extorsión monetaria", 'cyan'))
        safe_print(color("\n  WIPER (Módulo 02):", 'red'))
        safe_print(color("    - Corrompe/destruye archivos (irreversible sin backup)\n    - NO deja nota de rescate\n    - Objetivo: destrucción / sabotaje político", 'red'))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Simulación educativa de Wiper")
    parser.add_argument('--clean', action='store_true', help='Limpiar artefactos')
    args = parser.parse_args()

    wiper = WiperThreat()
    if args.clean:
        wiper.limpiar()
    else:
        wiper.ejecutar()