# Módulo 10 — Malware Fileless

## 📖 1. Definición Teórica y Contexto Histórico

El **malware fileless** es una categoría de amenazas que ejecutan código
directamente en memoria RAM sin escribir artefactos persistentes en disco.
Aprovecha herramientas legítimas del sistema operativo (PowerShell, WMI,
regsvr32, mshta) para ejecutar código malicioso sin ser detectado por
antivirus tradicionales basados en firmas de archivos.

### ¿Por qué evade el antivirus tradicional?

1. **Sin firma en disco** — No hay archivo estático que escanear con firmas.
2. **Herramientas legítimas (LOLBins)** — Usa binarios del sistema como vehículos.
3. **Ejecución en memoria** — Solo existe durante la ejecución del proceso.
4. **Ofuscación** — Código codificado en Base64 o cifrado en runtime.

### Técnicas fileless principales

| Técnica                     | Descripción                                      | Persistencia |
|-----------------------------|--------------------------------------------------|--------------|
| PowerShell en memoria       | Ejecuta scripts codificados directamente         | Temporal     |
| WMI Event Subscription      | Se ejecuta al cumplirse condición del evento     | Permanente   |
| Registry-based execution    | Código almacenado en claves Run/RunOnce           | Permanente   |
| Process hollowing           | Inyecta código en proceso legítimo en ejecución  | Temporal     |
| DLL search order hijacking  | Carga DLL maliciosa antes que la legítima        | Semi-perm.   |

### Ejemplos históricos

| Año  | Malware    | Técnica fileless utilizada                              |
|------|-----------|----------------------------------------------------------|
| 2017 | PowerGhost | Minero fileless propagado por WMI en servidores          |
| 2018 | Emotet     | PowerShell para descargar payloads en memoria            |
| 2019 | Astaroth   | Cadena de LOLBins: mshta → wscript → regsvr32            |
| 2020 | SUNBURST   | Backdoor fileless en actualizaciones SolarWinds           |

## ⚙️ 2. Mecanismo de Funcionamiento Tecnológico (Flujo Lógico)

```
1. VECTOR DE ENTRADA: El atacante envía el payload inicial (email, USB, exploit).
2. ACTIVACIÓN: Un LOLBin (PowerShell, WMI, mshta) ejecuta el código desde memoria.
3. DESCARGA: El código en memoria descarga etapas adicionales sin tocar disco.
4. EJECUCIÓN: El payload opera exclusivamente en RAM (robo de credenciales, etc.).
5. PERSISTENCIA OPCIONAL: Puede escribir al registro o WMI para reiniciarse.
6. LIMPIEZA: El código se auto-elimina de memoria al completar su objetivo.
7. EVASIÓN: Sin archivos en disco, los antivirus basados en firmas no lo detectan.
```

## 🔺 3. Alineación con la Tríada CIA

* **Pilar Afectado: Integridad (Integrity)**
* **Justificación Técnica:** El malware fileless compromete la integridad al
  ejecutar código no autorizado que modifica el comportamiento de procesos
  legítimos del sistema. Al inyectarse en procesos existentes (process hollowing)
  o usar herramientas del sistema (PowerShell), altera la integridad del entorno
  de ejecución sin dejar rastro verificable en disco, haciendo imposible la
  auditoría post-incidente con herramientas tradicionales.

## 🛡️ 4. Mitigación bajo la Norma de Controles CIS

* **CIS Control 2: Inventario y Control de Activos Empresariales (Inventory and Control of Enterprise Assets):**
  Mantener un inventario completo de todos los activos de red permite identificar
  dispositivos no autorizados o procesos anómalos que podrían indicar ejecución
  fileless.

* **Implementación Práctica en Laboratorio:**
  `defensa.py` verifica la existencia de archivos temporales residuales en `/tmp`,
  analiza timestamps de ejecución y muestra cómo un analista SOC buscaría rastros
  de ejecución fileless en un sistema real (logs de PowerShell, eventos WMI,
  procesos en memoria).

## 🚀 5. Detalles de la Simulación Educativa (Python)

### Qué hace `fileless.py`

```
1. Muestra una tabla de las 5 técnicas fileless más conocidas con ejemplos.
2. Crea un script Python temporal en /tmp (simula la carga en memoria).
3. Ejecuta el script inmediatamente via subprocess (simula ejecución en RAM).
4. El payload solo imprime un mensaje educativo (NO realiza acciones maliciosas).
5. Elimina el script temporal INMEDIATAMENTE después de la ejecución.
6. Verifica que no queda ningún archivo en disco (simula la limpieza fileless).
7. Registra la ejecución en fileless.log para análisis educativo.
```

### Qué hace `defensa.py`

```
1. Busca archivos temporales residuales de la simulación en /tmp.
2. Analiza si quedaron scripts fileless sin eliminar (fallo de limpieza).
3. Muestra las 5 técnicas fileless reales y cómo detectar cada una.
4. Elimina todos los artefactos temporales y logs de la simulación.
5. Recomienda herramientas reales de detección: Sysmon, AMSI, EDR behavior-based.
```

---

## Ejecución

```bash
# Generar archivos de laboratorio
python core/lab_setup.py

# Ejecutar simulación
python modulos/10_fileless/fileless.py

# Ver ayuda
python modulos/10_fileless/fileless.py --help

# Eliminar artefactos residuales
python modulos/10_fileless/fileless.py --clean

# Detectar y limpiar desde defensa
python modulos/10_fileless/defensa.py
```

> **NOTA:** En un sistema real, este tipo de malware es extremadamente difícil de
> detectar porque no deja archivos en disco. La detección requiere monitoreo en
> tiempo real de procesos, memoria y eventos del sistema. Todos los archivos
> se generan y gestionan dentro de `directorio_pruebas/`.
