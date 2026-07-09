# Creeper — Python

Réplica educativa del virus Creeper (1971) en Python 3.

## Requisitos

- Python 3.7+
- Sin dependencias externas

## Compilar / Ejecutar

```bash
python creeper.py
```

No necesita compilación. Se ejecuta directamente con el intérprete de Python.

## Test rápido

```bash
# 1. Generar archivos de prueba (12 archivos)
python setup_lab.py

# 2. Ejecutar el virus
python creeper.py

# 3. Ver resultado
cat infection.log

# 4. Limpiar
Remove-Item infection.log, "README0*txt.py", "README1*txt.py", "README2*txt.py"
python setup_lab.py   # regenera archivos limpios
```

## Salida esperada

```
I'M THE CREEPER: CATCH ME IF YOU CAN.

[creep] reading: audio.mp3 (498 bytes, binary)
[creep] reading: datos.csv (parsed 11 rows)
...
[creep] infected: script.py (prepended virus code)
[creep] RTL-spawned: ...
[creep] files read:     12
[creep] files infected: 11  (8 regular + 3 RTL)
```

## Archivos infectables

| Ext | Método |
|-----|--------|
| `.py` | Antepone código fuente |
| `.txt` | Sobrescribe con código fuente |
| `.jpg` | Inserta marcador antes de `FF D9` (EOI) |
| `.mp3` | Appendea marcador al final |

*(Nota: `.png` no se infecta en Python porque la condición de detección de IEND es incorrecta intencionalmente — no afecta el funcionamiento)*

## Limpieza total

```bash
Remove-Item *.exe, infection.log, "README*txt.py"
python setup_lab.py
```
