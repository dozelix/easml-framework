# Modulo 07 - Rootkit

## 1. Definicion Teorica y Contexto Historico

Un **rootkit** es un conjunto de herramientas malware disenadas para ocultar la presencia de un proceso, archivo o conexion maliciosa del sistema operativo. El nombre combina "root" (acceso de administrador en Unix/Linux) y "kit" (conjunto de herramientas), indicando su objetivo: obtener y ocultar acceso de administrador.

### Diferencia fundamental con otros malware

Mientras un virus, gusano o troyano buscan causar un efecto visible (cifrar, destruir, robar), el rootkit tiene un objetivo mucho mas peligroso: **permanecer invisible**. Un rootkit exitoso puede estar activo en un sistema durante anios sin ser detectado.

### Niveles de operacion

| Nivel | Nombre | Capacidades | Dificultad de deteccion |
|-------|--------|-------------|------------------------|
| Ring 3 | User-mode | Interceptar APIs del SO | Media |
| Ring 0 | Kernel-mode | Manipular estructuras del kernel | Alta |
| -1 | Bootkit | Modificar MBR/UEFI | Muy alta |
| -2 | Hypervisor | Controlar desde maquina virtual | Extrema |

### Ejemplos historicos relevantes

| Ano | Nombre | Nivel | Descripcion |
|-----|--------|-------|-------------|
| 2000 | HackerDefender | User-mode | Ocultaba procesos, archivos y puertos en Windows |
| 2005 | Sony Rootkit | User-mode | DRM oculto en CDs que instalaba un rootkit |
| 2008 | Necurs | Kernel-mode | Botnet con rootkit kernel que comprometio millones |
| 2010 | TDSS/Reaven | Kernel-mode | TDL4: uno de los rootkits kernel mas avanzados |
| 2012 | ZeroAccess | Kernel-mode | Botnet P2P con rootkit para mineria y fraude |
| 2014 | Rovnix | Bootkit | Modificaba el VBR (Volume Boot Record) |

### TDL4: el rootkit mas avanzado

TDSS (tambien conocido como Reaven o Alureon) representaba la vanguardia de los rootkits kernel:

1. **Infeccion del MBR**: Se instalaba antes del arranque del SO, siendo invisible para cualquier herramienta dentro del sistema.
2. **Filtrado de drivers**: Interceptaba las llamadas al sistema para ocultar archivos .sys maliciosos.
3. **Redireccion DNS**: Redirigia consultas DNS para inyectar publicidad y robar credenciales.
4. **Botnet P2P**: Utilizaba una red peer-to-peer para comunicarse, sin servidor C2 centralizable.
5. **Defensa activa**: Detectaba y deshabilitaba antivirus y herramientas de limpieza.

## 2. Mecanismo de Funcionamiento Tecnologico (Flujo Logico)

El flujo de operacion de un rootkit se describe en los siguientes pasos:

1. **Obtencion de privilegios**: El rootkit necesita acceso de administrador/root para operar a nivel kernel.

2. **Carga del driver**: Se carga un modulo en el kernel del SO que intercepta las llamadas al sistema (syscalls).

3. **Hooking de syscalls**: Modifica las tablas de syscall para filtrar los resultados antes de que lleguen al usuario:
   - `NtQueryDirectoryFile`: Filtra archivos del directorio (oculta archivos .sys maliciosos)
   - `NtQuerySystemInformation`: Filtra la lista de procesos (oculta procesos malware)
   - `NtDeviceIoControlFile`: Filtra conexiones de red (oculta conexiones C2)

4. **Ocultamiento**: Los archivos, procesos y conexiones maliciosos desaparecen de todas las herramientas del sistema (ls, tasklist, netstat).

5. **Proteccion**: El rootkit puede detectar intentos de desinfeccion y protegerse contra ellos.

```
 [Espacio de Usuario]          [User-mode Rootkit]           [Kernel Ring 0]
        |                            |                             |
   Llamadas al SO  ----->   Hook de APIs + Filtrado ----->   System Calls
        |                            |                             |
   Resultados visibles       Archivos filtrados             Hook de syscalls
   (sin rootkit)             Procesos filtrados             DKOM + Manipulacion
                            Conexiones filtradas            Resultados filtrados
                                                                          |
                                                                 [Hardware/MBR]
                                                                      |
                                                                   Bootkit
```

### Tecnicas de ocultamiento

| Tecnica | Nivel | Descripcion |
|---------|-------|-------------|
| API hooking | User-mode | Intercepts FindFirstFile, OpenProcess, etc. |
| IAT hooking | User-mode | Modifica la Import Address Table de procesos |
| Inline hooking | Kernel-mode | Reprime instrucciones de funcion del kernel |
| DKOM | Kernel-mode | Manipula directamente estructuras del kernel |
| SSDT hooking | Kernel-mode | Modifica la System Service Descriptor Table |
| MBR infection | Bootkit | Reemplaza el cargador de arranque |

## 3. Alineacion con la Triada CIA

* **Pilar Afectado: Integridad (Integrity)**
* **Justificacion Tecnica:** El rootkit compromete la integridad de multiples maneras:
  - **Manipulacion del kernel**: Modifica las estructuras fundamentales del sistema operativo, invalidando toda garantia de integridad del SO.
  - **Falsificacion de resultados**: Al filtrar la salida de herramientas del sistema (tasklist, ls, netstat), el rootkit presenta una vision falsa del estado del sistema.
  - **Escudo para otros malware**: Un rootkit protege a virus, troyanos y backdoors de la deteccion, manteniendo su presencia sin ser descubierto.
  - **Verificacion comprometida**: Ninguna herramienta dentro del sistema puede ser considerada confiable si hay un rootkit activo, porque el rootkit puede modificar su salida.
  - **Escalamiento de privilegios**: El rootkit puede crear cuentas ocultas, modificar permisos y alterar politicas de seguridad sin que el administrador lo note.

## 4. Mitigacion bajo la Norma de Controles CIS

* **CIS Control 8: Auditoria de Cuentas (Audit Log Management)**
* **Concepto:** Este control establece la necesidad de recopilar, almacenar, revisar y responder a registros de auditoria del sistema. Los logs son esenciales para detectar la presencia de rootkits, ya que un rootkit que manipula las vistas en tiempo real puede no poder alterar los logs que ya fueron escritos en disco.
* **Implementacion Practica en Laboratorio:** El script `defensa.py` implementa este control de las siguientes formas:
  - **Deteccion de archivos ocultos**: Lista todos los archivos con prefijo dot (.) en el directorio de pruebas, revelando archivos que un rootkit intentaria ocultar de una vista normal.
  - **Deteccion de marcadores de rootkit**: Escanea archivos buscando el marcador `ROOTKIT_SIMULATION`, similar a como un analista buscaria IOC de rootkits conocidos.
  - **Deteccion de manipulacion de procesos**: Identifica archivos que contienen referencias a procesos maliciosos ocultos, reconstruyendo la lista real de procesos.
  - **Limpieza automatizada**: Elimina todos los artefactos y genera un registro forense con hashes.

## 5. Detalles de la Simulacion Educativa (Python)

* **Que hace `rootkit.py`:**
  1. Crea 4 archivos ocultos con prefijo dot (.) dentro de `directorio_pruebas/`:
     - `.hidden_system` - Configuracion del rootkit
     - `.config_sys.dat` - Base de datos de configuracion oculta
     - `.rootkit_payload` - Payload simulado
     - `.driver_sim.sys` - Driver falso del rootkit
  2. Muestra la lista de procesos ANTES del rootkit (8 procesos normales).
  3. Muestra la lista DESPUES del rootkit (8 normales + 3 ocultos marcados).
  4. Guarda la lista de procesos manipulada en un archivo con el marcador `ROOTKIT_SIMULATION`.
  5. Explica las tecnicas de ocultamiento: prefijo dot, filtrado de procesos, intercepcion de API, DKOM.

* **Que hace `defensa.py`:**
  1. Lista todos los archivos ocultos (prefijo dot) en el directorio de pruebas.
  2. Escanea archivos buscando el marcador `ROOTKIT_SIMULATION`.
  3. Detecta archivos con procesos ocultos simulados (rootkit_svc.exe, c2_beacon.exe, keylog_drv.sys).
  4. Muestra hallazgos con hashes SHA-256 de cada artefacto.
  5. Elimina todos los artefactos detectados.
  6. Muestra recomendaciones: EDR con proteccion kernel, Secure Boot, analisis offline desde USB.

---
> **Disclaimer:** Este modulo es estrictamente educativo. Los archivos creados son texto plano inofensivo. No se modifican procesos reales del sistema ni se cargan drivers en el kernel.
