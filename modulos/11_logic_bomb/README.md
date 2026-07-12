# Módulo 11 — Bomba Lógica

## 📖 1. Definición Teórica y Contexto Histórico

Una **bomba lógica** (logic bomb) es código malicioso insertado en un programa
legítimo que permanece latente hasta que se cumple una condición específica de
activación. A diferencia de un virus o worm, no se propaga — espera pacientemente
a que el "disparador" (trigger) se active.

### Bomba lógica vs Time bomb

| Característica    | Logic Bomb                         | Time Bomb                           |
|-------------------|------------------------------------|-------------------------------------|
| Disparador        | Condición lógica arbitraria        | Fecha/hora específica               |
| Detección         | Muy difícil (código parece legítimo)| Relativamente fácil (cron/timer)   |
| Ejemplo           | "Si me borran del sistema, borro todo" | "Activar el 25 de diciembre"   |
| Persistencia      | Integrada en software legítimo     | Puede ser externa al programa       |

### Tipos de condiciones de activación

1. **Fecha/hora** — Se activa en un momento específico (time bomb).
2. **Archivo** — Se activa si (o si no) existe un archivo determinado.
3. **Variable de entorno** — Depende de una configuración del sistema.
4. **Umbral numérico** — Número de usuarios, archivos, conexiones, etc.
5. **Acción del usuario** — Login de usuario específico, borrado, modificación.
6. **Combinación AND/OR** — Múltiples condiciones deben cumplirse simultáneamente.

### Ejemplos históricos

| Año  | Víctima              | Descripción                                                         |
|------|----------------------|---------------------------------------------------------------------|
| 1985 | SIEMENS              | Empleado insertó bomba en nómina que borraba registros si aparecía en lista de despedidos |
| 1990 | Bull ( Francia)      | Empleado insertó código destructivo antes de ser despedido           |
| 1992 | London Ambulance     | Código con defectos ocultos causó fallo catastrófico del sistema    |
| 1998 | CSX Corporation      | Analista programó bomba que se activaba si su ID no estaba en payroll |

### ¿Por qué son peligrosas?

- **Difíciles de detectar**: El código puede parecer completamente legítimo.
- **Insider threat**: Frecuentemente creadas por empleados con acceso privilegiado.
- **Daño irreversible**: Pueden activarse después de que el atacante se fue.
- **Condición ambiental**: Se activan solo bajo circunstancias específicas, evitando detección en entornos de prueba.

## ⚙️ 2. Mecanismo de Funcionamiento Tecnológico (Flujo Lógico)

```
1. INSERCIÓN: El atacante (insider) inserta código condicional en un programa legítimo.
2. LATENCIA: El código permanece inactivo, formando parte del programa normal.
3. MONITOREO: En cada ejecución del programa, se evalúan las condiciones de activación.
4. EVALUACIÓN: Las condiciones se comparan contra el estado actual del sistema.
5. ACTIVACIÓN: Si se cumple el umbral de condiciones (ej: ≥2 de 5), se activa la bomba.
6. PAYLOAD: Se ejecuta la carga maliciosa (borrado, cifrado, exfiltración).
7. CONSECUENCIA: El daño se produce de forma irreversible sin advertencia previa.
```

## 🔺 3. Alineación con la Tríada CIA

* **Pilar Afectado: Disponibilidad (Availability)**
* **Justificación Técnica:** Una bomba lógica compromete la disponibilidad al
  activarse en un momento crítico y destruir datos, corromper bases de datos
  o deshabilitar servicios esenciales. El impacto es especialmente severo porque
  la activación es inesperada y el código ha pasado todas las revisiones de
  seguridad previas (estaba "oculto a simple vista" en código legítimo).

## 🛡️ 4. Mitigación bajo la Norma de Controles CIS

* **CIS Control 7: Protección de Correo Electrónico y Navegador Web (Email and Web Browser Protections):**
  Incluye controles de integridad de código, revisiones de código fuente y
  segregación de deberes para prevenir la inserción de código malicioso por
  empleados internos.

* **Implementación Práctica en Laboratorio:**
  `defensa.py` detecta el archivo de marcador JSON que contiene las condiciones
  de activación de la bomba, analiza qué condiciones están cumplidas y
  neutraliza la bomba eliminando todos los artefactos generados.

## 🚀 5. Detalles de la Simulación Educativa (Python)

### Qué hace `logic_bomb.py`

```
1. Define 5 condiciones de activación con clases CondicionBomba:
   - Fecha/hora: siempre se cumple (para demostración).
   - Archivo trigger: busca _trigger_bomb.txt en directorio actual.
   - Variable de entorno: verifica si BOMB_ACTIVE=1.
   - Umbral de archivos: cuenta archivos en directorio actual.
   - Horario laboral: verifica si la hora es entre 9:00 y 17:00.
2. Evalúa cada condición individualmente mostrando resultado (cumplida/no).
3. Determina si la bomba se activa (≥2 condiciones cumplidas = umbral).
4. Si se activa, ejecuta el payload inofensivo (solo imprime mensaje).
5. Guarda el estado completo de la bomba en logic_bomb_marker.json.
6. Registra cada condición y su resultado en logic_bomb.log.
```

### Qué hace `defensa.py`

```
1. Escanea en busca de logic_bomb_marker.json y logic_bomb.log.
2. Analiza el JSON para mostrar: nombre, tipo, estado, condiciones.
3. Indica qué condiciones están cumplidas y cuáles no.
4. Muestra si el payload fue ejecutado o está pendiente.
5. Neutraliza la bomba eliminando marker, log y archivos trigger.
6. Ofrece recomendaciones para detección en entorno productivo.
```

---

## Ejecución

```bash
# Generar archivos de laboratorio
python core/lab_setup.py

# Ejecutar simulación
python modulos/11_logic_bomb/logic_bomb.py

# Ver ayuda
python modulos/11_logic_bomb/logic_bomb.py --help

# Limpiar artefactos de la simulación
python modulos/11_logic_bomb/logic_bomb.py --clean

# Analizar y neutralizar desde defensa
python modulos/11_logic_bomb/defensa.py
```

> **NOTA:** La detonación de la bomba en esta simulación es completamente
> inofensiva — solo imprime un mensaje. En un escenario real, las bombas
> lógicas pueden causar pérdidas de datos catastróficas. Todos los archivos
> se generan y gestionan dentro de `directorio_pruebas/`.
