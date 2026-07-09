#!/usr/bin/env python3
"""Generate user files for the Creeper lab"""
import os
import sys
import struct
import zlib
import zipfile
import io

DIR = os.getcwd()

def write(name, data):
    path = os.path.join(DIR, name)
    if isinstance(data, str):
        with open(path, 'w', encoding='utf-8') as f:
            f.write(data)
    else:
        with open(path, 'wb') as f:
            f.write(data)
    print(f"  created: {name}  ({len(data)} bytes)")


# ── DOCUMENTS ──────────────────────────────────────────

def make_documento_txt():
    return """CONTRATO DE TRABAJO INDIVIDUAL

En la ciudad de Buenos Aires, a los 15 dias del mes de marzo de 2026, entre
el Sr. Juan Carlos Martinez, DNI 23.456.789, en adelante "EL EMPLEADOR", y
la Sra. Maria Elena Rodriguez, DNI 30.123.456, en adelante "EL EMPLEADO",
se celebra el presente Contrato de Trabajo.

CLAUSULA PRIMERA: EL EMPLEADO se desempenara como Analista de Sistemas
Senior en el Departamento de Tecnologia de la empresa.

CLAUSULA SEGUNDA: La relacion laboral tendra una duracion indeterminada a
partir del 1 de abril de 2026.

CLAUSULA TERCERA: La remuneracion convenida es de $580.000 (pesos quinientos
ochenta mil) mensuales, con los incrementos que disponga la legislacion.

CLAUSULA CUARTA: La jornada laboral sera de lunes a viernes de 9:00 a 18:00
horas, con una hora de descanso para almuerzo.

CLAUSULA QUINTA: EL EMPLEADO gozara de 15 dias habiles de vacaciones anuales
remuneradas conforme al regimen legal vigente.

CLAUSULA SEXTA: Cualquier modificacion al presente contrato debera constar
por escrito y ser firmada por ambas partes.

En prueba de conformidad, se firman dos ejemplares de un mismo tenor y a un
solo efecto en el lugar y fecha indicados.

_________________________              _________________________
    EL EMPLEADOR                           EL EMPLEADO
    Juan Carlos Martinez                   Maria Elena Rodriguez
"""

def make_notas_txt():
    return """=== NOTAS PERSONALES ===

* Compras del supermercado:
  - Leche (2)
  - Pan integral
  - Huevos (docena)
  - Frutas variadas
  - Cafe molido
  - Arroz

* Tareas pendientes:
  - Llamar al medico para turno anual
  - Pagar impuestos (vencen el 20/07)
  - Enviar informe al jefe antes del viernes
  - Comprar regalo cumpleanos de mama

* Ideas para el proyecto:
  - Implementar autenticacion 2FA
  - Optimizar consultas a la base de datos
  - Revisar vulnerabilidades de seguridad

* Recordatorios:
  - Renovar certificado SSL del servidor
  - Backup semanal de la base de datos
  - Actualizar dependencias del proyecto
  - Password: mi_clave_segura_2026 (NO COMPARTIR)
"""

def make_script_py():
    return """#!/usr/bin/env python3
\"\"\"Calculadora simple - Herramienta de usuario legitima\"\"\"
import sys

def suma(a, b): return a + b
def resta(a, b): return a - b
def mult(a, b): return a * b
def div(a, b): return a / b if b != 0 else float('inf')

OP = {'+': suma, '-': resta, '*': mult, '/': div}

def main():
    print("=== CALCULADORA v1.0 ===")
    print("Operaciones: +, -, *, /")
    while True:
        try:
            cmd = input(">>> ").strip()
            if cmd.lower() in ('exit', 'quit', 'q'):
                break
            partes = cmd.split()
            if len(partes) != 3:
                print("Formato: a + b")
                continue
            a, op, b = float(partes[0]), partes[1], float(partes[2])
            if op in OP:
                print(f"= {OP[op](a, b)}")
            else:
                print(f"Operacion '{op}' no soportada")
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    main()
"""

def make_index_html():
    return """<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8">
  <title>Mi Pagina Personal</title>
  <style>
    body { font-family: Arial; margin: 40px; background: #f0f0f0; }
    h1 { color: #333; }
    .container { max-width: 800px; margin: 0 auto; background: white; padding: 20px; border-radius: 8px; }
  </style>
</head>
<body>
  <div class="container">
    <h1>Bienvenido a mi sitio</h1>
    <p>Hola, soy Maria Elena. Esta es mi pagina personal donde comparto
    informacion sobre mis proyectos y experiencias laborales.</p>
    <h2>Proyectos Recientes</h2>
    <ul>
      <li>Sistema de gestion de inventarios</li>
      <li>Portal de empleados</li>
      <li>API REST para clientes externos</li>
    </ul>
    <h2>Contacto</h2>
    <p>Email: maria.rodriguez@correo.com</p>
    <p>Telefono: +54 11 5555-1234</p>
    <p>&copy; 2026 - Todos los derechos reservados</p>
  </div>
</body>
</html>
"""

def make_datos_csv():
    return """nombre,email,departamento,rol,antiguedad
Maria Rodriguez,maria.rodriguez@empresa.com,Tecnologia,Analista Senior,5
Carlos Lopez,carlos.lopez@empresa.com,Marketing,Coordinador,3
Ana Martinez,ana.martinez@empresa.com,RRHH,Analista,2
Pedro Garcia,pedro.garcia@empresa.com,Finanzas,Contador,8
Laura Fernandez,laura.fernandez@empresa.com,Tecnologia,Desarrolladora,4
Diego Sanchez,diegosanchez@empresa.com,Operaciones,Supervisor,6
Sofia Diaz,sofia.diaz@empresa.com,Ventas,Ejecutiva,1
Martin Torres,martin.torres@empresa.com,Tecnologia,Soporte,3
Valeria Acosta,valeria.acosta@empresa.com,Legal,Abogada,7
Jorge Ramirez,jorge.ramirez@empresa.com,Logistica,Jefe de Deposito,9
"""

def make_leeme_md():
    return """# Laboratorio Creeper Virus

## Descripcion
Laboratorio educativo para demostrar el concepto del primer virus
informatico de la historia: el Creeper (1971).

## Archivos incluidos
- `documento.txt` - Contrato laboral de ejemplo
- `notas.txt` - Notas personales del usuario
- `script.py` - Calculadora simple (blanco de infeccion)
- `index.html` - Pagina web personal
- `datos.csv` - Registro de empleados
- `imagen.png` - Imagen PNG de 1x1 pixel
- `imagen.jpg` - Imagen JPEG de 1x1 pixel
- `audio.mp3` - Archivo de audio con metadatos
- `documento.docx` - Documento Word
- `planilla.xlsx` - Planilla de calculo
- `presentacion.pptx` - Presentacion

## Uso
1. Ejecutar `setup_lab.py` para generar los archivos
2. Ejecutar `python creeper.py` para simular el virus

## Advertencia
SOLO PARA USO EDUCATIVO EN ENTORNO CONTROLADO.
"""


# ── BINARY FILES ───────────────────────────────────────

def make_png():
    """Valid 1x1 red pixel PNG"""
    def chunk(ctype, data):
        c = ctype + data
        crc = struct.pack('>I', zlib.crc32(c) & 0xFFFFFFFF)
        return struct.pack('>I', len(data)) + c + crc

    sig = b'\x89PNG\r\n\x1a\n'
    ihdr = struct.pack('>IIBBBBB', 1, 1, 8, 2, 0, 0, 0)
    raw = b'\x00\xff\x00\x00'
    idat = zlib.compress(raw)
    iend = b''

    return sig + chunk(b'IHDR', ihdr) + chunk(b'IDAT', idat) + chunk(b'IEND', iend)


def make_jpeg():
    """Minimal 1x1 grayscale JPEG (valid)"""
    buf = bytearray()

    # SOI
    buf += b'\xff\xd8'

    # APP0 JFIF
    buf += b'\xff\xe0\x00\x10JFIF\x00\x01\x01\x00\x00\x01\x00\x01\x00\x00'

    # DQT (quantization table 0, all ones - max quality)
    buf += b'\xff\xdb\x00\x43\x00' + bytes([1] * 64)

    # SOF0 (1x1, 8-bit, 1 component grayscale)
    buf += b'\xff\xc0\x00\x0b\x08\x00\x01\x00\x01\x01\x11\x00'

    # DHT DC luminance (standard K.3)
    dc_bits = bytes([0x00, 0x01, 0x05, 0x01, 0x01, 0x01, 0x01, 0x01,
                     0x01, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00])
    dc_vals = bytes(range(12))
    buf += b'\xff\xc4\x00\x1f\x00' + dc_bits + dc_vals

    # DHT AC luminance (standard K.5)
    ac_bits = bytes([0x00, 0x02, 0x01, 0x03, 0x03, 0x02, 0x04, 0x03,
                     0x05, 0x05, 0x04, 0x04, 0x00, 0x00, 0x01, 0x7d])
    ac_vals = bytes([
        0x01, 0x02, 0x03, 0x00, 0x04, 0x11, 0x05, 0x12, 0x21, 0x31,
        0x41, 0x06, 0x13, 0x51, 0x61, 0x07, 0x22, 0x71, 0x14, 0x32,
        0x81, 0x91, 0xa1, 0x08, 0x23, 0x42, 0xb1, 0xc1, 0x15, 0x52,
        0xd1, 0xf0, 0x24, 0x33, 0x62, 0x72, 0x82, 0x09, 0x0a, 0x16,
        0x17, 0x18, 0x19, 0x1a, 0x25, 0x26, 0x27, 0x28, 0x29, 0x2a,
        0x34, 0x35, 0x36, 0x37, 0x38, 0x39, 0x3a, 0x43, 0x44, 0x45,
        0x46, 0x47, 0x48, 0x49, 0x4a, 0x53, 0x54, 0x55, 0x56, 0x57,
        0x58, 0x59, 0x5a, 0x63, 0x64, 0x65, 0x66, 0x67, 0x68, 0x69,
        0x6a, 0x73, 0x74, 0x75, 0x76, 0x77, 0x78, 0x79, 0x7a, 0x83,
        0x84, 0x85, 0x86, 0x87, 0x88, 0x89, 0x8a, 0x92, 0x93, 0x94,
        0x95, 0x96, 0x97, 0x98, 0x99, 0x9a, 0xa2, 0xa3, 0xa4, 0xa5,
        0xa6, 0xa7, 0xa8, 0xa9, 0xaa, 0xb2, 0xb3, 0xb4, 0xb5, 0xb6,
        0xb7, 0xb8, 0xb9, 0xba, 0xc2, 0xc3, 0xc4, 0xc5, 0xc6, 0xc7,
        0xc8, 0xc9, 0xca, 0xd2, 0xd3, 0xd4, 0xd5, 0xd6, 0xd7, 0xd8,
        0xd9, 0xda, 0xe1, 0xe2, 0xe3, 0xe4, 0xe5, 0xe6, 0xe7, 0xe8,
        0xe9, 0xea, 0xf1, 0xf2, 0xf3, 0xf4, 0xf5, 0xf6, 0xf7, 0xf8,
        0xf9, 0xfa,
    ])
    buf += b'\xff\xc4\x00\xb5\x10' + ac_bits + ac_vals

    # SOS (start of scan) + entropy-coded data + EOI
    # DC=0 (cat 0 -> "00") + AC EOB ("1010") -> padded: 00101011 = 0x2B
    buf += b'\xff\xda\x00\x08\x01\x01\x00\x00\x3f\x00' + b'\x2b'

    # EOI
    buf += b'\xff\xd9'

    return bytes(buf)


def make_mp3():
    """MP3 with ID3v2.3 tag + one silent MPEG1 Layer3 frame"""
    frames_data = b''

    # ID3v2.3 header
    id3_ver = b'ID3\x03\x00\x00'

    # Frames: TIT2 (title), TPE1 (artist), TALB (album)
    tit2_data = b'\x03Silent Track'
    tit2 = b'TIT2' + struct.pack('>I', len(tit2_data)) + b'\x00\x00' + tit2_data

    tpe1_data = b'\x03Creeper Lab'
    tpe1 = b'TPE1' + struct.pack('>I', len(tpe1_data)) + b'\x00\x00' + tpe1_data

    talb_data = b'\x03Malware Studies'
    talb = b'TALB' + struct.pack('>I', len(talb_data)) + b'\x00\x00' + talb_data

    all_frames = tit2 + tpe1 + talb
    tag_size_no_header = len(all_frames)

    # Syncsafe size (7 bits per byte)
    ss = tag_size_no_header
    syncsafe = bytes([
        (ss >> 21) & 0x7f,
        (ss >> 14) & 0x7f,
        (ss >> 7) & 0x7f,
        ss & 0x7f,
    ])
    id3_tag = id3_ver + syncsafe + all_frames

    # MPEG1 Layer3 frame: 128kbps, 44100Hz, stereo, no padding
    # Frame sync: 0xFF 0xFB
    # Byte 2: bitrate=9(128k), samplerate=0(44100), padding=0, private=0 = 0x90
    # Byte 3: mode=0(stereo), mode_ext=0, copyright=0, original=1, emph=0 = 0x04
    frame_header = b'\xff\xfb\x90\x04'
    frame_size = 417
    frame_data = frame_header + bytes(frame_size - 4)
    id3_tag_sz = len(id3_tag)

    return id3_tag + frame_data


def make_docx():
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, 'w', zipfile.ZIP_DEFLATED) as z:
        z.writestr('[Content_Types].xml', (
            '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
            '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
            '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
            '<Default Extension="xml" ContentType="application/xml"/>'
            '<Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>'
            '</Types>'))
        z.writestr('word/document.xml', (
            '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
            '<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">'
            '<w:body><w:p><w:r><w:t>Hola Mundo - Documento de prueba</w:t></w:r></w:p>'
            '<w:p><w:r><w:t>Este archivo fue creado para el laboratorio Creeper.</w:t></w:r></w:p>'
            '</w:body></w:document>'))
        z.writestr('_rels/.rels', (
            '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
            '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
            '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/>'
            '</Relationships>'))
    return buf.getvalue()


def make_xlsx():
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, 'w', zipfile.ZIP_DEFLATED) as z:
        z.writestr('[Content_Types].xml', (
            '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
            '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
            '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
            '<Default Extension="xml" ContentType="application/xml"/>'
            '<Override PartName="/xl/workbook.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml"/>'
            '<Override PartName="/xl/worksheets/sheet1.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/>'
            '</Types>'))
        z.writestr('_rels/.rels', (
            '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
            '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
            '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="xl/workbook.xml"/>'
            '</Relationships>'))
        z.writestr('xl/workbook.xml', (
            '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
            '<workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">'
            '<sheets><sheet name="Datos" sheetId="1" r:id="rId1" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"/></sheets>'
            '</workbook>'))
        z.writestr('xl/worksheets/sheet1.xml', (
            '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
            '<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">'
            '<sheetData><row r="1"><c r="A1" t="inlineStr"><is><t>Nombre</t></is></c><c r="B1" t="inlineStr"><is><t>Valor</t></is></c></row>'
            '<row r="2"><c r="A2" t="inlineStr"><is><t>Item 1</t></is></c><c r="B2"><v>100</v></c></row>'
            '<row r="3"><c r="A3" t="inlineStr"><is><t>Item 2</t></is></c><c r="B3"><v>200</v></c></row>'
            '<row r="4"><c r="A4" t="inlineStr"><is><t>Item 3</t></is></c><c r="B4"><v>300</v></c></row>'
            '</sheetData></worksheet>'))
        z.writestr('xl/_rels/workbook.xml.rels', (
            '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
            '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
            '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" Target="worksheets/sheet1.xml"/>'
            '</Relationships>'))
    return buf.getvalue()


def make_pptx():
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, 'w', zipfile.ZIP_DEFLATED) as z:
        z.writestr('[Content_Types].xml', (
            '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
            '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
            '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
            '<Default Extension="xml" ContentType="application/xml"/>'
            '<Override PartName="/ppt/presentation.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.presentation.main+xml"/>'
            '<Override PartName="/ppt/slides/slide1.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.slide+xml"/>'
            '</Types>'))
        z.writestr('_rels/.rels', (
            '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
            '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
            '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="ppt/presentation.xml"/>'
            '</Relationships>'))
        z.writestr('ppt/presentation.xml', (
            '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
            '<p:presentation xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main">'
            '<p:sldIdLst><p:sldId id="256" r:id="rId1" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"/></p:sldIdLst>'
            '<p:sldSz cx="9144000" cy="6858000"/>'
            '<p:notesSz cx="6858000" cy="9144000"/>'
            '</p:presentation>'))
        z.writestr('ppt/slides/slide1.xml', (
            '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
            '<p:sld xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main">'
            '<p:cSld><p:spTree>'
            '<p:nvGrpSpPr><p:nvPr><p:cNvPr id="1" name=""/></p:nvPr></p:nvGrpSpPr>'
            '<p:grpSpPr><a:xfrm xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main"><a:off x="0" y="0"/><a:ext cx="0" cy="0"/></a:xfrm></p:grpSpPr>'
            '<p:sp><p:nvSpPr><p:cNvPr id="2" name="Title"/><p:nvSpPrType spPr="true"/></p:nvSpPr>'
            '<p:spPr><a:xfrm xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main"><a:off x="685800" y="457200"/><a:ext cx="7772400" cy="1219200"/></a:xfrm></p:spPr>'
            '<p:txBody><a:bodyPr/><a:p><a:r><a:rPr lang="es-AR" sz="4400"/><a:t>Creeper Virus Lab</a:t></a:r></a:p></p:txBody>'
            '</p:sp></p:spTree></p:cSld>'
            '</p:sld>'))
        z.writestr('ppt/_rels/presentation.xml.rels', (
            '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
            '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
            '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slide" Target="slides/slide1.xml"/>'
            '</Relationships>'))
    return buf.getvalue()


# ── MAIN ───────────────────────────────────────────────

def main():
    print("Generating user files for Creeper lab...\n")

    write('documento.txt', make_documento_txt())
    write('notas.txt', make_notas_txt())
    write('script.py', make_script_py())
    write('index.html', make_index_html())
    write('datos.csv', make_datos_csv())
    write('leeme.md', make_leeme_md())
    write('imagen.png', make_png())
    write('imagen.jpg', make_jpeg())
    write('audio.mp3', make_mp3())
    write('documento.docx', make_docx())
    write('planilla.xlsx', make_xlsx())
    write('presentacion.pptx', make_pptx())

    print(f"\nDone. {12} files created in:")
    print(f"  {DIR}")


if __name__ == "__main__":
    main()
