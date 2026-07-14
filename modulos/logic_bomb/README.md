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
  `analisis_de_desencadenadores.py` detecta el archivo de marcador JSON que contiene las condiciones
  de activación de la bomba, analiza qué condiciones están cumplidas y
  neutraliza la bomba eliminando todos los artefactos generados.

### Cuándo aplicar esta defensa

- **Cambios en código fuente por empleados en proceso de desvinculación:** Cuando
  un empleado notificado de baja realiza modificaciones inusuales al código
  fuente o a archivos de configuración, activar la revisión de integridad de
  código de forma inmediata.
- **Archivos de marcador o configuración anómalos:** La presencia de archivos
  JSON o de configuración con estructuras de condiciones de activación (fechas,
  archivos trigger, variables de entorno) en directorios de producción es un
  IOC directo de bomba lógica.
- **Disparadores de condiciones ambientales:** Si se detecta la creación de
  archivos trigger (archivos vacíos o de marcador) en directorios críticos,
  o modificaciones a variables de entorno del sistema, activar la inspección
  completa de código.
- **Auditorías de código periódicas:** En organizaciones con acceso privilegiado
  al código fuente, las revisiones periódicas de diff contra la última versión
  conocida pueden revelar condicionales maliciosos insertados silenciosamente.

### Por qué funciona esta defensa

- **Detección de la condición latente:** La bomba lógica requiere que su
  condición de activación sea evaluada en cada ejecución del programa. Al
  identificar estos marcadores (archivos JSON de estado, archivos trigger), se
  puede neutralizar la bomba antes de que se cumplan las condiciones de
  activación.
- **Principio de segregación de deberes:** La combinación de revisión de código
  fuente con monitoreo de integridad asegura que ningún individuo pueda insertar
  código malicioso sin ser detectado por al menos otro revisor, reduciendo
  significativamente el riesgo de insider threat.
- **Desarticulación del payload:** Al eliminar los archivos de marcador, los
  trigger y los logs asociados, se corta la cadena de evaluación de condiciones,
  haciendo que la bomba nunca se active independientemente de si las condiciones
  ambientales se cumplen.

### Ejercicios prácticos de defensa

1. **Análisis de condiciones:** Ejecuta `logic_bomb.py` y revisa
   `logic_bomb_marker.json`. Identifica cuáles de las 5 condiciones están
   marcadas como cumplidas. Luego ejecuta `analisis_de_desencadenadores.py` y
   verifica que neutraliza correctamente la bomba eliminando el marcador.
2. **Evaluación del umbral:** La bomba se activa con ≥2 condiciones cumplidas.
   Modifica el entorno (crear/eliminar archivos trigger, cambiar variables de
   entorno) y re-ejecuta la simulación para observar cómo cambia el estado de
   activación. Esto demuestra la sensibilidad de las bombas lógicas a su
   entorno.
3. **Auditoría de integridad:** Después de ejecutar `--clean`, verifica que no
   quedan archivos `logic_bomb_marker.json`, `logic_bomb.log` ni archivos
   trigger. En un entorno real, un sistema de integridad de archivos (AIDE,
   Tripwire) detectaría la creación de estos marcadores.

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

### Qué hace `analisis_de_desencadenadores.py`

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
python modulos/11_logic_bomb/analisis_de_desencadenadores.py
```

> **NOTA:** La detonación de la bomba en esta simulación es completamente
> inofensiva — solo imprime un mensaje. En un escenario real, las bombas
> lógicas pueden causar pérdidas de datos catastróficas. Todos los archivos
> se generan y gestionan dentro de `directorio_pruebas/`.
