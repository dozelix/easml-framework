# Creeper — Rust

Réplica educativa del virus Creeper (1971) en Rust.

## Requisitos

- Rust toolchain (`rustc` + `cargo`)
- Usar toolchain **GNU** (no MSVC): `rustup default stable-x86_64-pc-windows-gnu`

## Compilar

```bash
rustc creeper.rs -o creeper.exe
```

O con optimización:

```bash
rustc -C opt-level=3 creeper.rs -o creeper.exe
```

## Ejecutar

```bash
creeper.exe
```

## Test rápido

```powershell
# 1. Generar archivos de prueba
python setup_lab.py

# 2. Compilar
rustc creeper.rs -o creeper.exe

# 3. Ejecutar
creeper.exe

# 4. Ver log
Get-Content infection.log

# 5. Limpiar
Remove-Item creeper.exe, infection.log, "README*txt.py"
python setup_lab.py
```

## Salida esperada

```
I'M THE CREEPER: CATCH ME IF YOU CAN.

[creep] reading: audio.mp3 (498 bytes, binary)
...
[creep] infected: script.py (prepended virus code)
[creep] RTL-spawned: ...
[creep] files read:     12
[creep] files infected: 9  (6 regular + 3 RTL)
```

## Archivos infectables

| Ext | Método |
|-----|--------|
| `.py` | Antepone código fuente |
| `.txt` | Sobrescribe con código fuente |
| `.jpg` | Inserta marcador antes de `FF D9` (EOI) |
| `.png` | Inserta marcador después de chunk IEND |
| `.mp3` | Appendea marcador al final |

## Notas

- Requiere toolchain GNU porque MSVC `link.exe` no está disponible en el laboratorio
- La infección de PNG usa `pos + 8` (final del chunk IEND, que incluye CRC de 4 bytes)

## Limpieza total

```powershell
Remove-Item *.exe, infection.log, "README*txt.py"
python setup_lab.py
```
