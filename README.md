# Proyecto Creeper — Virus Educativo Multi-Lenguaje

Implementación del primer virus informático de la historia (Creeper, 1971) en 6 lenguajes de programación, para fines educativos en entornos de laboratorio controlados.

> ⚠ **ADVERTENCIA**: Este código es SOLO para fines educativos. Ejecutar únicamente en entornos aislados (máquinas virtuales, laboratorios). El virus opera exclusivamente dentro de su propio directorio y nunca escapa.

---

## Estructura

```
malwares/
├── python/creeper/   — Implementación original (Python 3.7+)
├── rust/creeper/     — Versión Rust (rustc 1.97+)
├── go/creeper/       — Versión Go (go 1.26+)
├── nim/creeper/      — Versión Nim (nim 2.0+)
├── c/creeper/        — Versión C (C11 / C17)
├── cpp/creeper/      — Versión C++ (C++17)
├── python/creeper/setup_lab.py  — Generador de archivos de prueba (compartido)
└── README.md
```

Cada directorio `*/creeper/` contiene:
- `setup_lab.py` — enlace simbólico o copia del generador
- 12 archivos de usuario: `.txt`, `.csv`, `.html`, `.md`, `.py`, `.png`, `.jpg`, `.mp3`, `.docx`, `.xlsx`, `.pptx`
- El virus compilado/interpretado correspondiente

---

## Requisitos (toolchains)

| Lenguaje | Comando | Instalación (Windows) |
|----------|---------|-----------------------|
| Python   | `python` | Ya incluido |
| Rust     | `rustc`  | `winget install Rustlang.Rustup` → `rustup default stable-x86_64-pc-windows-gnu` |
| Go       | `go`     | `winget install GoLang.Go` |
| Nim      | `nim`    | `winget install nim.nim` + MinGW |
| C        | `gcc`    | `winget install MartinStorsjo.LLVM-MinGW.UCRT` |
| C++      | `g++`    | (incluido con LLVM MinGW) |

---

## Cómo usar

### 1. Generar archivos de prueba (12 archivos de usuario)

```bash
# Desde cualquier directorio */creeper/:
python ../../python/creeper/setup_lab.py
```

Esto crea 12 archivos: 2 `.txt`, 1 `.csv`, 1 `.html`, 1 `.md`, 1 `.py`, 1 `.png`, 1 `.jpg`, 1 `.mp3`, 1 `.docx`, 1 `.xlsx`, 1 `.pptx`.

### 2. Ejecutar el virus

```bash
# Python
cd python/creeper
python creeper.py

# Rust
cd rust/creeper
rustc creeper.rs -o creeper.exe && creeper.exe

# Go
cd go/creeper
go build -o creeper.exe creeper.go && creeper.exe

# Nim
cd nim/creeper
nim c -d:release --opt:size creeper.nim && creeper.exe

# C
cd c/creeper
gcc creeper.c -o creeper.exe && creeper.exe

# C++
cd cpp/creeper
g++ -std=c++17 creeper.cpp -o creeper.exe && creeper.exe
```

### 3. Limpiar después de la ejecución

```bash
# Eliminar archivos infectados y RTL clones:
rm infection.log
rm "README0<U+202E>txt.py" "README1<U+202E>txt.py" "README2<U+202E>txt.py"

# Regenerar archivos limpios:
python ../../python/creeper/setup_lab.py
```

---

## Comportamiento del virus

Cada réplica sigue el mismo patrón del Creeper original:

### Fase 1 — RECON (lectura)
Lee los 12 archivos de usuario (excluye `.exe`, `setup_lab.py` y su propio fuente) e imprime metadata:
- `.txt` → bytes y líneas
- `.csv` → filas
- `.html` → tags HTML
- `.md` → headers
- `.py` → líneas de script
- `.png`, `.jpg`, `.mp3` → tipo y tamaño
- `.docx`, `.xlsx`, `.pptx` → tipo y tamaño

### Fase 2 — INFECT (infección)
- `.py` → antepone el código fuente del virus
- `.txt` → sobrescribe con el código fuente
- `.jpg` → inserta marcador antes del EOI (`FF D9`)
- `.png` → inserta marcador después del chunk IEND
- `.mp3` → appendea marcador al final
- `.docx`, `.xlsx`, `.pptx` → solo en Go (ZIP injection: agrega marcador dentro del archivo ZIP)

Cada archivo infectado recibe un marcador `[CREEPER-INFECTED]` con timestamp para evitar reinfección.

### Fase 3 — RTL clones
Crea 3 archivos con nombre `README{N}‮txt.py`

(usan el carácter U+202E RIGHT-TO-LEFT OVERRIDE). En Windows Explorer se ven como `README{N}.txt` pero en realidad son scripts Python ejecutables.

### Fase 4 — LOG
Escribe `infection.log` con resumen de la operación.

---

## Diferencias entre lenguajes

| Característica        | Python | Rust | Go | Nim | C | C++ |
|-----------------------|--------|------|----|-----|----|-----|
| ZIP injection         | ✗      | ✗    | ✅ | ✗   | ✗  | ✗   |
| Binario compilado     | ✗      | ✅   | ✅ | ✅  | ✅ | ✅  |
| Dependencias externas | ninguna| rustc | go | nim+gcc | gcc | g++ |
| Infecta Office docs   | ✗      | ✗    | ✅ | ✗   | ✗  | ✗   |

---

## Notas

- Python 3.7.9 es la versión disponible en el laboratorio
- Rust usa toolchain `stable-x86_64-pc-windows-gnu` (no MSVC) porque el linker MSVC no está instalado
- LLVM MinGW es compartido por Nim, C y C++
- El generador `setup_lab.py` usa `os.getcwd()` para crear archivos en cualquier directorio
