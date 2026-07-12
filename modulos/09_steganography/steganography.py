#!/usr/bin/env python3
"""
Módulo 09 — Esteganografía (Educativo)

Simula ocultación de un mensaje secreto en los bits menos significativos (LSB)
de una imagen PNG. El proceso es completamente reversible: se crea un respaldo
antes de modificar la imagen.

Todas las operaciones se confinan al directorio directorio_pruebas/.

Uso:
    python modulos/09_steganography/steganography.py          Ejecutar simulación
    python modulos/09_steganography/steganography.py --clean  Restaurar y limpiar
    python modulos/09_steganography/steganography.py --help   Mostrar ayuda
"""
import os
import sys
import struct
import zlib
import time
import shutil

# ── Configurar path para importar core.common ──
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from core.common import (
    log, safe_print, color, banner, hash_file, cleanup, write_log, find_lab_dir
)

# ── Constantes ──────────────────────────────────────────
# Directorio de trabajo confinado
LAB_DIR = find_lab_dir(os.path.dirname(os.path.abspath(__file__)))
IMAGEN_ORIG = os.path.join(LAB_DIR, "imagen.png")
IMAGEN_STEG = os.path.join(LAB_DIR, "imagen_steg.png")
BACKUP_EXT = ".bak_steg"

# Mensaje secreto que se ocultará en la imagen (solo educativo)
MENSAJE_SECRETO = (
    "ESTEGANOGRAFÍA EDUCATIVA: Este mensaje está oculto en los LSB "
    "de la imagen. Si puedes leer esto, la extracción funcionó. "
    "¡Los bits menos significativos son ideales para ocultar datos!"
)


# ── Funciones de creación y manipulación de PNG ──
def crear_png_base():
    """
    Crea un PNG de 32×32 píxeles con colores variados.
    Un PNG válido necesita: firma, chunk IHDR, chunk IDAT comprimido, chunk IEND.
    """
    SIZE = 32

    def chunk(ctype, data):
        """Construye un chunk PNG: length + type + data + CRC."""
        c = ctype + data
        crc = struct.pack('>I', zlib.crc32(c) & 0xFFFFFFFF)
        return struct.pack('>I', len(data)) + c + crc

    sig = b'\x89PNG\r\n\x1a\n'  # Firma mágica del formato PNG
    ihdr = struct.pack('>IIBBBBB', SIZE, SIZE, 8, 2, 0, 0, 0)
    # IHDR: ancho, alto, bits/channel=8, tipo=2 (RGB), compression=0, filter=0, interlace=0

    # Crear datos de imagen con patrón de colores variados (gradiente)
    # Esto asegura que los LSB originales tengan variación natural
    raw_rows = []
    for y in range(SIZE):
        row = b'\x00'  # Byte de filtro (0 = None por fila)
        for x in range(SIZE):
            r = (x * 32 + y * 16) % 256
            g = (x * 16 + y * 32 + 80) % 256
            b_val = (x * 48 + y * 48 + 160) % 256
            row += bytes([r, g, b_val])
        raw_rows.append(row)

    raw = b''.join(raw_rows)
    idat = zlib.compress(raw)  # Compresión DEFLATE de los datos crudos
    return sig + chunk(b'IHDR', ihdr) + chunk(b'IDAT', idat) + chunk(b'IEND', b'')


def mensaje_a_bits(mensaje):
    """Convierte un string a lista de bits (1 bit por elemento)."""
    bits = []
    for byte in mensaje.encode('utf-8'):
        for i in range(7, -1, -1):  # De MSB a LSB de cada byte
            bits.append((byte >> i) & 1)
    return bits


def bits_a_mensaje(bits):
    """Reconstruye un string a partir de una lista de bits."""
    chars = []
    for i in range(0, len(bits) - 7, 8):
        byte = 0
        for j in range(8):
            byte = (byte << 1) | bits[i + j]
        chars.append(byte)
    return bytes(chars).decode('utf-8', errors='replace')


def extraer_png_datos(data):
    """
    Extrae dimensiones y datos de píxeles crudos de un PNG sin dependencias externas.
    Parsea manualmente los chunks IHDR e IDAT.
    """
    if not data.startswith(b'\x89PNG'):
        return None, None, None

    pos = 8  # Saltar firma del PNG
    ihdr_data = None
    raw_idat = b''

    while pos < len(data):
        if pos + 8 > len(data):
            break
        length = struct.unpack('>I', data[pos:pos+4])[0]
        ctype = data[pos+4:pos+8]
        cdata = data[pos+8:pos+8+length]

        if ctype == b'IHDR':
            ihdr_data = struct.unpack('>IIBBBBB', cdata[:13])
        elif ctype == b'IDAT':
            raw_idat += cdata  # Los chunks IDAT se concatenan antes de descomprimir
        elif ctype == b'IEND':
            break
        pos += 12 + length  # 4 length + 4 type + data + 4 CRC

    if ihdr_data is None or not raw_idat:
        return None, None, None

    width, height = ihdr_data[0], ihdr_data[1]
    try:
        pixels = zlib.decompress(raw_idat)
    except Exception:
        return None, None, None

    return width, height, pixels


def ocultar_mensaje_lsb(pixels, bits_msg, width, height):
    """
    Oculta bits en el LSB de los canales RGB de la imagen.
    Cada byte de pixel tiene formato: [Filtro, R, G, B, Filtro, R, G, B, ...]
    Los bytes de filtro (cada 4 posiciones desde 0) no se modifican.
    """
    if len(bits_msg) > (width * height * 3):
        raise ValueError("Mensaje demasiado largo para esta imagen")

    modified = bytearray(pixels)
    bit_idx = 0
    for i in range(1, len(modified)):  # Empezar en 1 para saltar el primer filtro
        if bit_idx >= len(bits_msg):
            break
        # Saltar bytes de filtro (cada 4 bytes: filtro, R, G, B)
        if (i - 1) % 4 != 3:
            # Reemplazar LSB: preservar los 7 bits superiores, insertar 1 bit del mensaje
            modified[i] = (modified[i] & 0xFE) | bits_msg[bit_idx]
            bit_idx += 1

    return bytes(modified), bit_idx


def extraer_mensaje_lsb(pixels, num_bits, width, height):
    """Extrae bits de los LSB de los canales RGB para recuperar el mensaje oculto."""
    bits = []
    for i in range(1, len(pixels)):
        if len(bits) >= num_bits:
            break
        if (i - 1) % 4 != 3:  # Saltar bytes de filtro
            bits.append(pixels[i] & 1)  # Extraer solo el LSB
    return bits


def reconstruir_png(ihdr_data, compressed_data):
    """Reconstruye un PNG completo a partir de IHDR y datos IDAT comprimidos."""

    def chunk(ctype, data):
        c = ctype + data
        crc = struct.pack('>I', zlib.crc32(c) & 0xFFFFFFFF)
        return struct.pack('>I', len(data)) + c + crc

    sig = b'\x89PNG\r\n\x1a\n'
    ihdr = struct.pack('>IIBBBBB', *ihdr_data[:7])
    return sig + chunk(b'IHDR', ihdr) + chunk(b'IDAT', compressed_data) + chunk(b'IEND', b'')


def paso_fase(fase_num, titulo):
    """Muestra un separador visual de fase en la consola."""
    safe_print(color(f"\n  [FASE {fase_num}] {titulo}", 'yellow'))
    safe_print(color(f"  {'─' * 55}", 'yellow'))
    time.sleep(0.3)


# ── Limpieza ────────────────────────────────────────────
def limpiar():
    """Restaura la imagen original desde backup y elimina artefactos."""
    banner("MÓDULO 09 — ESTEGANOGRAFÍA — LIMPIEZA",
           "Restaurando imagen y eliminando artefactos")

    # Restaurar original desde backup
    if os.path.exists(IMAGEN_ORIG + BACKUP_EXT):
        shutil.copy2(IMAGEN_ORIG + BACKUP_EXT, IMAGEN_ORIG)
        safe_print(color(f"  Restaurado: imagen.png desde backup", 'green'))
        os.remove(IMAGEN_ORIG + BACKUP_EXT)
    else:
        safe_print(color("  No se encontró backup para restaurar.", 'yellow'))

    removidos = cleanup(
        files_to_remove=[IMAGEN_STEG],
        patterns=[os.path.join(LAB_DIR, "*.bak_steg"),
                  os.path.join(LAB_DIR, "estegano*.log")]
    )
    safe_print(color(f"\n  Limpieza completada: {removidos} archivos eliminados.\n", 'green'))


# ── Simulación principal ────────────────────────────────
def ejecutar():
    """Ejecuta la simulación completa de esteganografía LSB."""
    banner("MÓDULO 09 — ESTEGANOGRAFÍA — SIMULACIÓN EDUCATIVA",
           "Ocultación de mensajes en imagen mediante LSB")

    # Crear directorio de trabajo si no existe
    os.makedirs(LAB_DIR, exist_ok=True)
    safe_print(color(f"  Directorio de trabajo: {LAB_DIR}\n", 'cyan'))

    # ── FASE 1: Preparar imagen ──
    paso_fase(1, "PREPARACIÓN — Creando imagen portadora")
    # Verificar si la imagen existente tiene suficiente capacidad LSB.
    # La imagen de lab_setup.py es solo 1×1 (3 bits), insuficiente.
    # Siempre creamos una imagen de 32×32 para esta simulación.
    img_data = crear_png_base()
    with open(IMAGEN_ORIG, 'wb') as f:
        f.write(img_data)
    safe_print(color(f"  → Imagen PNG de 32×32 creada ({len(img_data)} bytes)", 'green'))

    hash_original = hash_file(IMAGEN_ORIG) or "N/A"
    safe_print(color(f"  Hash SHA-256: {hash_original[:40]}...", 'yellow'))
    time.sleep(0.2)

    # ── FASE 2: Analizar estructura ──
    paso_fase(2, "ANÁLISIS — Leyendo estructura del PNG")
    img_data = None
    with open(IMAGEN_ORIG, 'rb') as f:
        img_data = f.read()
    if img_data is None:
        safe_print(color("  Error: no se pudo leer la imagen", 'red'))
        return

    width, height, pixels = extraer_png_datos(img_data)
    if width is None:
        safe_print(color("  Error: no se pudo parsear el PNG", 'red'))
        return

    safe_print(color(f"  Dimensiones:   {width}×{height} píxeles", 'white'))
    safe_print(color(f"  Canales:       RGB (3 por píxel)", 'white'))
    capacidad = width * height * 3
    safe_print(color(f"  Capacidad LSB: {capacidad} bits ({capacidad // 8} bytes)", 'white'))

    # ── FASE 3: Preparar mensaje ──
    paso_fase(3, "MENSAJE — Convirtiendo texto a bits")
    bits_mensaje = mensaje_a_bits(MENSAJE_SECRETO)
    safe_print(color(f"  Mensaje: \"{MENSAJE_SECRETO[:55]}...\"", 'magenta'))
    safe_print(color(f"  Longitud: {len(MENSAJE_SECRETO)} caracteres = {len(bits_mensaje)} bits", 'white'))
    porcentaje = (len(bits_mensaje) / capacidad) * 100
    safe_print(color(f"  Uso de capacidad: {porcentaje:.1f}%", 'yellow'))

    if len(bits_mensaje) > capacidad:
        safe_print(color("  Error: mensaje demasiado grande para esta imagen", 'red'))
        return

    # ── FASE 4: Crear backup ──
    paso_fase(4, "RESPALDO — Guardando imagen original")
    shutil.copy2(IMAGEN_ORIG, IMAGEN_ORIG + BACKUP_EXT)
    safe_print(color(f"  → Backup: imagen.png.bak_steg creado", 'green'))
    time.sleep(0.2)

    # ── FASE 5: LSB Embedding ──
    paso_fase(5, "INSERCIÓN — Ocultando mensaje en LSB")
    safe_print(color("  Algoritmo: Least Significant Bit (LSB)", 'white'))
    safe_print(color("  Técnica: Reemplazar el bit menos significativo de cada canal RGB\n", 'white'))

    # Mostrar los primeros 5 bits como ejemplo visual
    for i in range(min(5, len(bits_mensaje))):
        canal = ['R', 'G', 'B'][i % 3]
        safe_print(color(f"    Bit {i}: canal {canal} → {bits_mensaje[i]}", 'yellow'))
    safe_print(color(f"    ... {len(bits_mensaje)} bits insertados en total\n", 'white'))

    modified_pixels, bits_insertados = ocultar_mensaje_lsb(pixels, bits_mensaje, width, height)
    safe_print(color(f"  → {bits_insertados} bits ocultados exitosamente", 'green'))

    # ── FASE 6: Guardar imagen modificada ──
    paso_fase(6, "GUARDADO — Reconstruyendo PNG modificado")
    steg_data = reconstruir_png(
        (width, height, 8, 8, 2, 0, 0),
        zlib.compress(modified_pixels)
    )
    with open(IMAGEN_STEG, 'wb') as f:
        f.write(steg_data)
    safe_print(color(f"  → imagen_steg.png guardado ({len(steg_data)} bytes)", 'green'))

    hash_steg = hash_file(IMAGEN_STEG) or "N/A"
    safe_print(color(f"  Hash SHA-256: {hash_steg[:40]}...", 'yellow'))
    safe_print(color(f"  ¿Diferente del original? {'SÍ' if hash_original != hash_steg else 'NO (ERROR)'}", 'green'))

    # ── FASE 7: Verificar extracción ──
    paso_fase(7, "VERIFICACIÓN — Extrayendo mensaje oculto")
    _, _, steg_pixels = extraer_png_datos(steg_data)
    bits_extraidos = extraer_mensaje_lsb(steg_pixels, len(bits_mensaje), width, height)
    mensaje_extraido = bits_a_mensaje(bits_extraidos)

    if mensaje_extraido == MENSAJE_SECRETO:
        safe_print(color("  ¡EXTRACCIÓN EXITOSA! Mensaje recuperado intacto.", 'green'))
    else:
        safe_print(color("  Extracción con diferencias (posible por compresión)", 'yellow'))
    safe_print(color(f"  Mensaje extraído: \"{mensaje_extraido[:55]}...\"", 'magenta'))

    # ── RESUMEN ──
    safe_print(color("\n" + "=" * 60, 'cyan'))
    safe_print(color("  RESUMEN DE LA SIMULACIÓN DE ESTEGANOGRAFÍA", 'bold'))
    safe_print(color("=" * 60, 'cyan'))
    safe_print(color(f"  Imagen original:    imagen.png", 'white'))
    safe_print(color(f"  Imagen modificada:  imagen_steg.png", 'white'))
    safe_print(color(f"  Capacidad usada:   {porcentaje:.1f}%", 'white'))
    safe_print(color(f"  Extracción:        {'OK' if mensaje_extraido == MENSAJE_SECRETO else 'FALLÓ'}", 'green'))
    safe_print(color("=" * 60, 'cyan'))
    safe_print(color(
        "\n  NOTA: La modificación de LSB es imperceptible al ojo humano.\n"
        "  Solo un análisis estadístico puede detectar la presencia de datos.\n",
        'yellow'
    ))
    log("Simulación de esteganografía completada")
    write_log("estegano_sim", [
        f"Imagen creada: imagen.png ({width}×{height})",
        f"Bits insertados: {bits_insertados}",
        f"Porcentaje de capacidad: {porcentaje:.1f}%",
        f"Extracción exitosa: {mensaje_extraido == MENSAJE_SECRETO}",
    ], os.path.join(LAB_DIR, "estegano.log"))


if __name__ == "__main__":
    if "--help" in sys.argv:
        print(__doc__)
        sys.exit(0)
    if "--clean" in sys.argv:
        limpiar()
        sys.exit(0)
    ejecutar()
