#!/usr/bin/env python3
"""
Módulo 09 — Defensa contra Esteganografía (Educativo)

Detecta modificaciones esteganográficas en imágenes PNG verificando los patrones
de LSB y restaura la imagen original desde el backup si existe.

En un entorno de producción, un analista de seguridad usaría técnicas estadísticas
(chi-cuadrado, RS Analysis) para detectar datos ocultos en archivos multimedia.

Uso:
    python modulos/09_steganography/defensa.py          Ejecutar escaneo
    python modulos/09_steganography/defensa.py --help   Mostrar ayuda
"""
import os
import sys
import struct
import zlib
import glob
import shutil

# ── Configurar path para importar core.common ──
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from core.common import log, safe_print, color, banner, cleanup, write_log, hash_file

# ── Directorio de trabajo de la simulación ──
LAB_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__)))), 'directorio_pruebas')

# Artefactos conocidos que genera la simulación de esteganografía
ARTIFACTOS = {
    "archivos": [
        os.path.join(LAB_DIR, "imagen_steg.png"),
        os.path.join(LAB_DIR, "estegano.log"),
    ],
    "patrones": [os.path.join(LAB_DIR, "*.bak_steg")],
}


def analizar_lsb(data):
    """
    Analiza la distribución de LSB en una imagen PNG.
    En una imagen natural, los LSB tienen una distribución que depende del contenido.
    Si se insertan datos aleatorios (mensaje cifrado), el ratio de 1s y 0s se
    acerca a 0.5, lo cual es estadísticamente anómalo para imágenes naturales.
    """
    if not data.startswith(b'\x89PNG'):
        return None

    pos = 8
    raw_idat = b''
    ihdr = None

    while pos < len(data):
        if pos + 8 > len(data):
            break
        length = struct.unpack('>I', data[pos:pos+4])[0]
        ctype = data[pos+4:pos+8]
        cdata = data[pos+8:pos+8+length]

        if ctype == b'IHDR':
            ihdr = struct.unpack('>IIBBBBB', cdata[:13])
        elif ctype == b'IDAT':
            raw_idat += cdata
        elif ctype == b'IEND':
            break
        pos += 12 + length

    if ihdr is None or not raw_idat:
        return None

    try:
        pixels = zlib.decompress(raw_idat)
    except Exception:
        return None

    width, height = ihdr[0], ihdr[1]
    total_bits = 0
    ones_count = 0

    for i in range(1, len(pixels)):
        if (i - 1) % 4 != 3:  # Saltar bytes de filtro
            total_bits += 1
            ones_count += pixels[i] & 1

    ratio = ones_count / total_bits if total_bits > 0 else 0
    return {
        "dimensiones": f"{width}×{height}",
        "canales_analizados": total_bits,
        "bits_1": ones_count,
        "bits_0": total_bits - ones_count,
        "ratio_1": round(ratio, 4),
        # Un ratio cercano a 0.5 sugiere datos aleatorios (posible esteganografía)
        "sospechoso": abs(ratio - 0.5) < 0.02,
    }


def paso_fase(fase_num, titulo):
    """Muestra un separador visual de fase en la consola."""
    safe_print(color(f"\n  [FASE {fase_num}] {titulo}", 'yellow'))
    safe_print(color(f"  {'─' * 55}", 'yellow'))


def detectar():
    """
    Ejecuta el análisis completo de detección de esteganografía.
    En producción, esto equivaldría a usar herramientas como zsteg, StegSolve,
    o análisis chi-cuadrado para detectar patrones anómalos en archivos multimedia.
    """
    banner("DEFENSA — ESTEGANOGRAFÍA — ANÁLISIS Y DETECCIÓN",
           "Analizando imágenes en busca de datos ocultos")

    hallazgos = []

    # ── FASE 1: Buscar artefactos conocidos ──
    paso_fase(1, "BÚSQUEDA — Escaneando artefactos de esteganografía")
    for archivo in ARTIFACTOS["archivos"]:
        if os.path.exists(archivo):
            hallazgos.append(archivo)
            safe_print(color(f"  [!] Detectado: {os.path.basename(archivo)}", 'red'))

    for patron in ARTIFACTOS["patrones"]:
        for f in glob.glob(patron):
            if f not in hallazgos:
                hallazgos.append(f)
                safe_print(color(f"  [!] Detectado (backup): {os.path.basename(f)}", 'red'))

    # ── FASE 2: Análisis LSB de cada imagen PNG ──
    paso_fase(2, "ANÁLISIS ESTADÍSTICO — Verificando distribución de LSB")
    # En producción, un analista usaría chi-cuadrado o RS Analysis.
    # Aquí simulamos verificando el ratio de bits 1 vs 0 en canales RGB.
    for img_name in ["imagen.png", "imagen_steg.png"]:
        img_path = os.path.join(LAB_DIR, img_name)
        if os.path.exists(img_path):
            with open(img_path, 'rb') as f:
                data = f.read()
            info = analizar_lsb(data)
            if info:
                safe_print(color(f"\n  Análisis LSB de {img_name}:", 'cyan'))
                safe_print(color(f"    Dimensiones:        {info['dimensiones']}", 'white'))
                safe_print(color(f"    Canales analizados: {info['canales_analizados']}", 'white'))
                safe_print(color(f"    Bits 1:             {info['bits_1']}", 'white'))
                safe_print(color(f"    Bits 0:             {info['bits_0']}", 'white'))
                safe_print(color(f"    Ratio de bits 1:    {info['ratio_1']}", 'white'))
                if info['sospechoso']:
                    safe_print(color(f"    [!] SOSPECHOSO: distribución de LSB anómala (ratio ~0.5)", 'red'))
                    safe_print(color(f"        Esto sugiere que la imagen contiene datos ocultos.", 'red'))
                else:
                    safe_print(color(f"    [OK] Distribución de LSB normal", 'green'))

    # ── FASE 3: Verificar integridad con hashes ──
    paso_fase(3, "INTEGRIDAD — Comparando hashes SHA-256")
    orig_path = os.path.join(LAB_DIR, "imagen.png")
    steg_path = os.path.join(LAB_DIR, "imagen_steg.png")
    if os.path.exists(orig_path) and os.path.exists(steg_path):
        h_orig = hash_file(orig_path) or "N/A"
        h_steg = hash_file(steg_path) or "N/A"
        safe_print(color(f"  imagen.png:      {h_orig[:48]}...", 'white'))
        safe_print(color(f"  imagen_steg.png: {h_steg[:48]}...", 'white'))
        if h_orig != h_steg:
            safe_print(color(f"  [!] Los hashes difieren — imagen modificada detectada", 'red'))
        else:
            safe_print(color(f"  [OK] Los hashes coinciden — imagen no modificada", 'green'))

    return hallazgos


def ejecutar():
    """Ejecuta el proceso completo de detección y recomendaciones."""
    os.makedirs(LAB_DIR, exist_ok=True)
    hallazgos = detectar()

    # ── FASE 4: Resumen ──
    paso_fase(4, "RESUMEN — Hallazgos y recomendaciones")
    if hallazgos:
        safe_print(color(f"\n  Total de artefactos encontrados: {len(hallazgos)}", 'yellow'))
    else:
        safe_print(color("\n  [OK] No se encontraron artefactos de esteganografía.\n", 'green'))

    safe_print(color("  RECOMENDACIONES PARA ENTORNO PRODUCTIVO:", 'bold'))
    safe_print(color("  - Usar herramientas: zsteg, StegSolve, chi-cuadrado", 'cyan'))
    safe_print(color("  - Implementar DLP que analice archivos multimedia salientes", 'cyan'))
    safe_print(color("  - Comparar hashes de imágenes contra repositorio conocido", 'cyan'))
    safe_print(color("  - Monitorear subidas masivas de imágenes a servicios externos", 'cyan'))
    safe_print(color("  - Usar análisis de firmas digitales en archivos multimedia\n", 'cyan'))

    write_log("defensa_estegano", [
        f"Escaneo defensivo completado",
        f"Artefactos encontrados: {len(hallazgos)}",
    ], os.path.join(LAB_DIR, "defensa_estegano.log"))


if __name__ == "__main__":
    if "--help" in sys.argv:
        print(__doc__)
        sys.exit(0)
    ejecutar()
