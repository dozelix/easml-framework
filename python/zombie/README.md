# Zombie — Python

Simulación educativa del virus Zombie (variante Minecraft) en Python 3.

## Requisitos

- Python 3.7+
- Sin dependencias externas

## Ejecución

```bash
python zombie.py
```

No necesita compilación. Se ejecuta directamente con el intérprete de Python.

## Prueba rápida

```bash
# 1. Generar archivos de prueba (12 archivos)
python setup_lab.py

# 2. Ejecutar el virus (fuera de horario laboral para ver todas las fases)
python zombie.py

# 3. Ver resultado
type infection.log

# 4. Limpiar
Remove-Item infection.log, "BRAINS*txt.py" -ErrorAction SilentlyContinue
python setup_lab.py   # regenera archivos limpios
```

## Salida esperada

```
BRAINS... I MEAN, FILES. THE ZOMBIE WALKS.

── FASE 1: RECON (HAMBRE) ──
[zombie] leyendo: documento.txt (1234 bytes, 32 lineas)
[zombie] leyendo: datos.csv (parseado 11 filas)
...

── FASE 4: EVASION UV (EVITAR LUZ SOLAR) ──
[zombie] EVASION UV: noche detectada (hora=21) — zombie activo

── FASE 2: INFECTAR (MORDIDA) ──
[zombie] infectado: script.py (codigo zombie antepuesto)
[zombie] infectado: notas.txt (sobrescrito con zombie)
...

── FASE 3: RTL SPAWN (REPRODUCCION ZOMBIE) ──
[zombie] creado: 'BRAINS0\u202Etxt.py'
        (parece BRAINS0.txt en Explorer)

── FASE 5: ENRUTAMIENTO MANHATTAN (ESCANEO ORTOGONAL) ──
[zombie] salto: documento.txt -> script.py (distancia=42)
...

── FASE 6: PERFILAMIENTO DE RENDIMIENTO (ACTIVIDAD DE LA HORDA) ──
[zombie] MODO ALTA ACTIVIDAD (escaneo rapido, alto CPU, ALTO riesgo de deteccion)
[zombie] alta actividad: 125.43ms — riesgo SIEM: 85/100
...
```

## Comportamiento del virus

### Fase 1 — RECON (Hambre)
Lee los 12 archivos de usuario e imprime metadata por tipo.

### Fase 2 — INFECTAR (Mordida)
| Ext | Metodo |
|-----|--------|
| `.py` | Antepone codigo fuente del zombie |
| `.txt` | Sobrescribe con codigo fuente |
| `.jpg` | Inserta marcador antes de `FF D9` (EOI) |
| `.png` | Inserta marcador despues de chunk IEND |
| `.mp3` | Agrega marcador al final |
| `.docx`, `.xlsx`, `.pptx` | Inyecta marcador oculto dentro del ZIP |

### Fase 3 — RTL Spawn
Crea 3 archivos `BRAINS{N}‮txt.py` (usan U+202E). En Windows Explorer se ven como `BRAINS{N}.txt` pero son scripts Python ejecutables.

### Fase 4 — Evasion UV (Evitar Luz Solar)
**Hora 9-17**: El zombie detecta "luz diurna" y se autodestruye — elimina todos los rastros (archivos infectados, RTL clones, infection.log) y aborta la ejecucion.

**Fuera de 9-17**: El zombie permanece activo y continua con las demas fases.

Esto simula la ejecucion fileless: el payload reside en memoria y evita persistir cuando hay alta supervision.

### Fase 5 — Enrutamiento Manhattan
Simula escaneo de red ortogonal (distancia Manhattan): cada salto es horizontal o vertical, nunca diagonal. Esto es predecible y colisiona con topologias segmentadas, VLANs aisladas o honeypots.

### Fase 6 — Perfilamiento de Rendimiento
Demuestra la correlacion entre actividad del CPU y riesgo de deteccion:
- **Alta actividad**: Alto uso de CPU → firma grande → SIEM lo detecta facil
- **Baja actividad**: Bajo uso de CPU → firma pequena → evasion exitosa

## Archivos infectables

| Ext | Metodo | Marcador |
|-----|--------|----------|
| `.py` | Anteponer | `# === INFECTED BY ZOMBIE ===` |
| `.txt` | Sobrescribir | Codigo fuente completo |
| `.png` | Insertar despues de IEND | `[ZOMBIE-INFECTED]` |
| `.jpg` | Insertar antes de EOI | `[ZOMBIE-INFECTED]` |
| `.mp3` | Agregar | `[ZOMBIE-INFECTED]` |
| `.docx/.xlsx/.pptx` | Inyeccion ZIP | `zombie_infection/.zombie_marker.txt` |

## Limpieza total

```bash
Remove-Item *.exe, infection.log, "BRAINS*txt.py" -ErrorAction SilentlyContinue
python setup_lab.py
```
