#!/usr/bin/env python3
"""
Simulación educativa de Ransomware — Módulo 01.

Modifica archivos invirtiendo su contenido de texto y exige un rescate virtual.
"""

import os
import sys
import shutil
import time
import argparse

# ── Configuración de rutas absolutas robustas ───────────────────────────────
_DIR_RAIZ = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, _DIR_RAIZ)

from core.base_module import BaseThreat
from modulos.common.utils import (
    log, safe_print, color, banner, traverse_lab_files,
    hash_file, cleanup, write_log, is_lab_ready, LOG_LINES, find_lab_dir
)

class RansomwareThreat(BaseThreat):
    def __init__(self):
        self.dir_simulacion = find_lab_dir(_DIR_RAIZ)
        self.extension_locked = '.locked'
        self.nota_rescate = 'README_RESCATE.txt'
        self.extensiones_texto = {'.txt', '.py', '.html', '.csv', '.md'}
        self.archivos_lab = {'documento.txt', 'notas.txt', 'script.py', 'index.html', 'datos.csv', 'leeme.md'}

    def ejecutar(self) -> None:
        banner("RANSOMWARE — SIMULACION EDUCATIVA", "Inversión de texto")
        if not self._verificar_entorno():
            sys.exit(1)

        self._paso_fase(1, "PREPARACION — Copiando archivos objetivo")
        self._preparar_directorio()
        
        self._paso_fase(2, "RECONOCIMIENTO — Enumerando archivos")
        objetivos = self._listar_objetivos()
        
        self._paso_fase(3, "CIFRADO — Invirtiendo contenido")
        self._ejecutar_cifrado(objetivos)
        
        self._paso_fase(4, "RESCATE — Creando nota")
        self._crear_nota_rescate()
        
        # CORRECCIÓN: Forzar ruta absoluta al subdirectorio logs/
        dir_logs = os.path.join(os.path.dirname(self.dir_simulacion), 'logs')
        os.makedirs(dir_logs, exist_ok=True)
        
        write_log(os.path.join(dir_logs, "ransomware_sim"), list(LOG_LINES))
        safe_print(color(f"\n  [+] Historial de ataque guardado en: {dir_logs}/ransomware_sim.log", 'green'))

    def limpiar(self) -> None:
        banner("RANSOMWARE — LIMPIEZA", "Eliminando artefactos de la simulación")
        if os.path.isdir(self.dir_simulacion):
            shutil.rmtree(self.dir_simulacion)
            safe_print(color(f"  eliminado: {self.dir_simulacion}", 'green'))
        
        # Intentar limpiar la nota de rescate si quedó suelta en la raíz o destino
        nota_path_raiz = os.path.join(_DIR_RAIZ, self.nota_rescate)
        if os.path.exists(nota_path_raiz):
            os.remove(nota_path_raiz)
            safe_print(color(f"  eliminado: {self.nota_rescate}", 'green'))

        cleanup(patterns=[self.nota_rescate, 'ransomware_sim.log'])
        safe_print(color("\n  Limpieza completada con éxito.", 'green'))

    # ── Métodos privados de soporte (SRP) ─────────────────────────────────
    def _paso_fase(self, num, titulo):
        safe_print(color(f"\n  [FASE {num}] {titulo}\n  {'─' * 55}", 'yellow'))
        time.sleep(0.3)

    def _verificar_entorno(self):
        return is_lab_ready()

    def _preparar_directorio(self):
        os.makedirs(self.dir_simulacion, exist_ok=True)
        archivos_fuente = traverse_lab_files(_DIR_RAIZ)
        copiados = 0
        
        for ruta_orig in archivos_fuente:
            nombre = os.path.basename(ruta_orig)
            if nombre in self.archivos_lab:
                destino = os.path.join(self.dir_simulacion, nombre)
                if not os.path.exists(destino):
                    shutil.copy2(ruta_orig, destino)
                    copiados += 1
                    
        log(f"Directorio preparado: {self.dir_simulacion} ({copiados} copiados)")
        safe_print(color(f"  Directorio: {self.dir_simulacion}", 'green'))
        safe_print(color(f"  Archivos copiados listos para atacar: {copiados}", 'green'))

    def _listar_objetivos(self):
        if not os.path.isdir(self.dir_simulacion):
            safe_print(color("  [!] Error: El directorio de simulación no existe.", 'red'))
            return []

        archivos = sorted(os.listdir(self.dir_simulacion))
        objetivos = []
        
        for f in archivos:
            ruta_completa = os.path.join(self.dir_simulacion, f)
            if os.path.isfile(ruta_completa) and not f.endswith('.log'):
                _, ext = os.path.splitext(f)
                if ext.lower() in self.extensiones_texto:
                    objetivos.append(ruta_completa)
                    safe_print(color(f"    [+] Detectado objetivo: {f}", 'green'))
                else:
                    safe_print(color(f"    [-] Ignorado (no es texto/código): {f}", 'blue'))
        return objetivos

    def _ejecutar_cifrado(self, objetivos):
        if not objetivos:
            safe_print(color("  [!] No se encontraron archivos válidos para cifrar.", 'yellow'))
            return

        for ruta in objetivos:
            nombre_base = os.path.basename(ruta)
            try:
                with open(ruta, 'r', encoding='utf-8', errors='ignore') as f:
                    contenido = f.read()

                hash_original = hash_file(ruta)

                contenido_cifrado = contenido[::-1]

                ruta_locked = ruta + self.extension_locked
                with open(ruta_locked, 'w', encoding='utf-8') as f:
                    f.write(contenido_cifrado)

                os.remove(ruta)

                hash_nuevo = hash_file(ruta_locked)
                h_orig_disp = (hash_original[:32] + '...') if hash_original else 'N/A'
                h_nuev_disp = (hash_nuevo[:32] + '...') if hash_nuevo else 'N/A'

                safe_print(color(f"    [CIFRADO] {nombre_base} -> {nombre_base}{self.extension_locked}", 'red'))
                safe_print(color(f"      Hash Original: {h_orig_disp}", 'green'))
                safe_print(color(f"      Hash Cifrado:  {h_nuev_disp}", 'red'))
                log(f"Cifrado: {nombre_base} ({h_orig_disp} -> {h_nuev_disp})")

            except Exception as e:
                safe_print(color(f"    [!] Error procesando {nombre_base}: {e}", 'red'))

    def _crear_nota_rescate(self):
        ruta_nota = os.path.join(self.dir_simulacion, self.nota_rescate)
        contenido_nota = (
            "===============================================================================\n"
            "                  ¡TODOS TUS ARCHIVOS HAN SIDO CIFRADOS!                       \n"
            "===============================================================================\n\n"
            " Tu contenido ha sido invertido mediante un algoritmo criptográfico avanzado.\n"
            " Para recuperar tus datos originales, debes utilizar la herramienta defensiva.\n\n"
            " Instrucciones del Laboratorio:\n"
            " 1. Analiza este directorio y observa la extensión de tus archivos.\n"
            " 2. Ve a la TUI y ejecuta la opción de DEFENSA [E].\n"
            " 3. El script defensivo restaurará la integridad calculando los hashes.\n\n"
            " No intentes renombrar los archivos manualmente o podrías corromperlos.\n"
        )
        try:
            with open(ruta_nota, 'w', encoding='utf-8') as f:
                f.write(contenido_nota)
            safe_print(color(f"  [+] Nota de rescate generada con éxito en:\n      {ruta_nota}", 'yellow'))
            log("Nota de rescate creada")
        except Exception as e:
            safe_print(color(f"  [!] No se pudo crear la nota de rescate: {e}", 'red'))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Módulo de Simulación Ransomware")
    parser.add_argument('--clean', action='store_true', help='Limpia el entorno de simulación')
    args = parser.parse_args()

    ataca = RansomwareThreat()
    if args.clean:
        ataca.limpiar()
    else:
        ataca.ejecutar()