# Módulo 09 — Esteganografía

## 📖 1. Definición Teórica y Contexto Histórico

La **esteganografía** es la técnica de ocultar información dentro de otros datos
(imágenes, audio, video, texto) de forma que un observador no sospeche de su
existencia. A diferencia del cifrado (que hace el mensaje ilegible), la
esteganografía **oculta la existencia misma del mensaje**.

### Diferencia fundamental con el cifrado

| Aspecto           | Cifrado                          | Esteganografía                        |
|-------------------|----------------------------------|---------------------------------------|
| Objetivo          | Hacer el mensaje ilegible        | Ocultar que existe un mensaje         |
| Visible           | Se ve texto cifrado              | No se ve nada sospechoso              |
| Detección         | Fácil (texto anómalo)            | Difícil (apariencia normal)           |
| Uso combinado     | Cifrar + luego esteganografiar   | Capa adicional de ocultación          |

### Técnicas principales

| Técnica  | Medio        | Descripción                                  | Detección |
|----------|-------------|----------------------------------------------|-----------|
| **LSB**  | Imágenes    | Modifica bit menos significativo de cada canal RGB | Muy baja |
| **DCT**  | JPEG        | Modifica coeficientes en dominio de frecuencia | Baja    |
| **Palette** | PNG indexada | Reordena colores en la paleta             | Media     |
| **ECC**  | Cualquier medio | Usa corrección de errores para inserción  | Baja      |
| **Audio** | WAV/MP3     | Oculta datos en frecuencias imperceptibles   | Baja      |

### Herramientas conocidas

- **Steghide** — Inserción en JPEG/BMP con passphrase.
- **zsteg** — Detección automática de LSB en PNG y BMP.
- **StegSolve** — Análisis visual por planos de bits (Java).
- **OpenStego** — Implementación open-source de LSB con marca de agua.

### Ejemplos históricos

- **2010:** Se descubrió que el grupo Anonymous usaba esteganografía en imágenes de
  foros para coordinar operaciones sin ser detectados.
- **2013:** El malware Duqu 2.0 (atribuido a la NSA) usaba esteganografía para
  ocultar datos en archivos de sistema de Windows.
- **2017:** Se detectó tráfico C2 de botnets oculto en la cabecera de imágenes
  JPEG compartidas en redes sociales.
- **2020:** Actores APT usaban LSB en imágenes PNG para exfiltrar credenciales
  capturadas fuera de la red corporativa.

## ⚙️ 2. Mecanismo de Funcionamiento Tecnológico (Flujo Lógico)

```
1. CAPTURA: El atacante obtiene una imagen/portadora (cover image) legítima.
2. CONVERSIÓN: El mensaje secreto se convierte a una secuencia de bits.
3. INSERCIÓN LSB: Se reemplaza el bit menos significativo (LSB) de cada canal
   RGB de la imagen con cada bit del mensaje secreto.
4. REEMPLAZO: El LSB de un pixel (ej: 11010010 → 11010011) cambia en ±1,
   lo cual es invisible al ojo humano pero almacena un bit de información.
5. GUARDADO: La imagen modificada se guarda como nuevo archivo.
6. EXTRACCIÓN: El destinatario conoce la técnica y extrae los LSB para
   reconstruir el mensaje oculto.
7. REVERSIBILIDAD: Si se creó un backup, la imagen original puede restaurarse.
```

### Capacidad de inserción LSB

Una imagen de 32×32 píxeles con 3 canales (RGB) ofrece:
- 32 × 32 × 3 = 3,072 bits de capacidad
- 3,072 / 8 = 384 bytes de mensaje oculto
- Aproximadamente 384 caracteres ASCII

## 🔺 3. Alineación con la Tríada CIA

* **Pilar Afectado: Confidencialidad (Confidentiality)**
* **Justificación Técnica:** La esteganografía compromete la confidencialidad al
  permitir la exfiltración de datos sensibles a través de canales aparentemente
  legítimos. Un empleado malicioso puede ocultar listas de contraseñas, planos
  o información clasificada dentro de imágenes compartidas en redes sociales,
  evadiendo los controles DLP (Data Loss Prevention) que solo inspeccionan
  metadatos y contenido visible.

## 🛡️ 4. Mitigación bajo la Norma de Controles CIS

* **CIS Control 3: Protección de Datos (Data Protection):**
  Establece políticas y procedimientos para clasificar, etiquetar y proteger
  datos sensibles, incluyendo controles contra exfiltración no autorizada.

* **Implementación Práctica en Laboratorio:**
  `analisis_esteganografico.py` analiza la distribución estadística de LSB en imágenes PNG para
  detectar patrones anómalos (ratio ~0.5 sugiere datos ocultos). También
  restaura la imagen original desde un backup y elimina las copias modificadas,
  demostrando cómo un equipo de seguridad verificaría la integridad de archivos
  multimedia en un entorno corporativo.

## 🚀 5. Detalles de la Simulación Educativa (Python)

### Qué hace `steganography.py`

```
1. Crea una imagen PNG de 32×32 píxeles con colores variados (o usa imagen existente).
2. Lee la estructura IHDR/IDAT del PNG para extraer los datos de píxeles crudos.
3. Convierte un mensaje secreto educativo a una secuencia de bits.
4. Crea un backup de la imagen original (imagen.png.bak_steg).
5. Aplica LSB embedding: reemplaza el bit menos significativo de cada canal RGB.
6. Reconstruye el PNG modificado y lo guarda como imagen_steg.png.
7. Verifica la extracción reversiva: lee los LSB de la imagen modificada y
   reconstruye el mensaje para confirmar integridad.
8. Compara hashes SHA-256 de original vs modificada para demostrar diferencias.
```

### Qué hace `analisis_esteganografico.py`

```
1. Escanea el directorio en busca de imagen_steg.png y backups .bak_steg.
2. Analiza la distribución de LSB de cada imagen PNG encontrada.
3. Calcula el ratio de bits 1 vs bits 0 en los canales RGB.
4. Detecta anomalías: un ratio cercano a 0.5 sugiere datos ocultos (aleatorización).
5. Restaura la imagen original desde el backup si existe.
6. Elimina todas las copias modificadas y artefactos de la simulación.
```

---

## Ejecución

```bash
# Generar archivos de laboratorio
python core/lab_setup.py

# Ejecutar simulación
python modulos/09_steganography/steganography.py

# Ver ayuda
python modulos/09_steganography/steganography.py --help

# Restaurar imagen y limpiar
python modulos/09_steganography/steganography.py --clean

# Analizar y limpiar desde defensa
python modulos/09_steganography/analisis_esteganografico.py
```

> **NOTA:** La imagen modificada es visualmente idéntica a la original. La técnica
> LSB es prácticamente indetectable sin análisis estadístico. Todos los archivos
> se generan y gestionan dentro de `directorio_pruebas/`.
