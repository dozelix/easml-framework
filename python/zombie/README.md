# Zombie — Python

Simulación educativa del virus Zombie (variante Minecraft) en Python 3.

## Requisitos

- Python 3.7+
- Sin dependencias externas

## Compilar / Ejecutar

```bash
python zombie.py
```

No necesita compilación. Se ejecuta directamente con el intérprete de Python.

## Test rápido

```bash
# 1. Generar archivos de prueba (12 archivos)
python setup_lab.py

# 2. Ejecutar el virus (fuera de horario laboral para ver todas las fases)
python zombie.py

# 3. Ver resultado
cat infection.log

# 4. Limpiar
Remove-Item infection.log, "BRAINS*txt.py" -ErrorAction SilentlyContinue
python setup_lab.py   # regenera archivos limpios
```

## Salida esperada

```
BRAINS... I MEAN, FILES. THE ZOMBIE WALKS.

── PHASE 1: RECON (HUNGER) ──
[zombie] reading: documento.txt (1234 bytes, 32 lines)
[zombie] reading: datos.csv (parsed 11 rows)
...

── PHASE 4: UV EVASION (SUNLIGHT AVOIDANCE) ──
[zombie] UV EVASION: nighttime (hour=21) — zombie is active

── PHASE 2: INFECT (BITE) ──
[zombie] infected: script.py (prepended zombie code)
[zombie] infected: notas.txt (overwritten with zombie)
...

── PHASE 3: RTL SPAWN (ZOMBIE SPAWN) ──
[zombie] spawned: 'BRAINS0\u202Etxt.py'
        (looks like BRAINS0.txt in Explorer)

── PHASE 5: MANHATTAN ROUTING (ORTHOGONAL SCANNING) ──
[zombie] hop: documento.txt -> script.py (distance=42)
...

── PHASE 6: PERFORMANCE PROFILING (HORDE ACTIVITY) ──
[zombie] HIGH ACTIVITY MODE (fast scan, high CPU, HIGH detection risk)
[zombie] high activity: 125.43ms — SIEM detection risk: 85/100
...
```

## Comportamiento del virus

### Fase 1 — RECON (Hunger)
Lee los 12 archivos de usuario e imprime metadata por tipo.

### Fase 2 — INFECT (Bite)
| Ext | Método |
|-----|--------|
| `.py` | Antepone código fuente del zombie |
| `.txt` | Sobrescribe con código fuente |
| `.jpg` | Inserta marcador antes de `FF D9` (EOI) |
| `.png` | Inserta marcador después de chunk IEND |
| `.mp3` | Appendea marcador al final |
| `.docx`, `.xlsx`, `.pptx` | Inyecta marcador oculto dentro del ZIP |

### Fase 3 — RTL Spawn
Crea 3 archivos `BRAINS{N}‮txt.py` (usan U+202E). En Windows Explorer se ven como `BRAINS{N}.txt` pero son scripts Python ejecutables.

### Fase 4 — UV Evasion (Sunlight Avoidance)
**Hora 9-17**: El zombie detecta "luz diurna" y se autodestruye — elimina todos los rastros (archivos infectados, RTL clones, infection.log) y aborta la ejecución.

**Fuera de 9-17**: El zombie permanece activo y continúa con las demás fases.

Esto simula la ejecución fileless: el payload reside en memoria y evita persistir cuando hay alta supervisión.

### Fase 5 — Manhattan Routing
Simula escaneo de red ortogonal (distancia Manhattan): cada salto es horizontal o vertical, nunca diagonal. Esto es predecible y colisiona con topologías segmentadas, VLANs aisladas o honeypots.

### Fase 6 — Performance Profiling
Demuestra la correlación entre actividad del CPU y riesgo de detección:
- **Alta actividad**: Alto uso de CPU → firma grande → SIEM lo detecta fácil
- **Baja actividad**: Bajo uso de CPU → firma pequeña → evasión exitosa

## Archivos infectables

| Ext | Método | Marcador |
|-----|--------|----------|
| `.py` | Prepend | `# === INFECTED BY ZOMBIE ===` |
| `.txt` | Overwrite | Código fuente completo |
| `.png` | Insert after IEND | `[ZOMBIE-INFECTED]` |
| `.jpg` | Insert before EOI | `[ZOMBIE-INFECTED]` |
| `.mp3` | Append | `[ZOMBIE-INFECTED]` |
| `.docx/.xlsx/.pptx` | ZIP injection | `zombie_infection/.zombie_marker.txt` |

## Limpieza total

```bash
Remove-Item *.exe, infection.log, "BRAINS*txt.py" -ErrorAction SilentlyContinue
python setup_lab.py
```
