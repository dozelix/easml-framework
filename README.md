# Laboratorio de Malware Educativo

Repositorio académico para el estudio de amenazas de seguridad informática.
14 módulos independientes en Python, cada uno con simulación, defensa y documentación.

> **Solo para uso educativo en entorno controlado.**

## Arquitectura del Laboratorio

```mermaid
graph TB
    subgraph "Punto de entrada"
        TUI["python -m core.tui<br/>Interfaz visual interactiva (Textual)"]
    end

    subgraph "core/ — Utilidades compartidas"
        COMMON["common.py<br/>log, colores, traversal, hashing"]
        SETUP["lab_setup.py<br/>generador de archivos de prueba"]
        TUIMOD["tui.py<br/>interfaz panel dividido (Textual)"]
    end

    subgraph "modulos/ — 14 amenazas"
        M01["01_ransomware"]
        M02["02_wiper"]
        M03["03_keylogger"]
        M04["04_worm"]
        M05["05_trojan"]
        M06["06_backdoor"]
        M07["07_rootkit"]
        M08["08_botnet"]
        M09["09_steganography"]
        M10["10_fileless"]
        M11["11_logic_bomb"]
        M12["12_cryptominer"]
        M13["13_supply_chain"]
        M14["14_dns_tunneling"]
    end

    TUI --> TUIMOD
    TUIMOD --> M01 & M02 & M03 & M04 & M05 & M06 & M07
    TUIMOD --> M08 & M09 & M10 & M11 & M12 & M13 & M14
    M01 & M02 & M03 & M04 & M05 & M06 & M07 --> COMMON
    M08 & M09 & M10 & M11 & M12 & M13 & M14 --> COMMON
    COMMON --> SETUP

```

## Requisitos

* Python 3.10+
* `textual`: `pip install textual`

## Inicio rápido

```bash
# 1. Generar archivos de prueba
python core/lab_setup.py

# 2. Abrir la interfaz visual interactiva
python -m core.tui

# 3. Limpiar todo el entorno al finalizar
python core/lab_setup.py --clean

```

## Módulos y Matriz de Gobernanza (CIA vs. CIS)

Cada módulo es autocontenido e incluye el script de emulación (`{nombre}.py`), el script de remediación (`defensa.py`) y su documentación teórica profunda.

| # | Módulo | Vector de Amenaza | Pilar CIA Afectado | Control CIS de Mitigación |
| :--- | :--- | :--- | :---: | :--- |
| **01** | [ransomware](modulos/01_ransomware/) | Cifrado criptográfico de archivos locales | **Disponibilidad** | **CIS 11:** Recuperación de Datos (Backups) |
| **02** | [wiper](modulos/02_wiper/) | Destrucción y corrupción masiva del disco | **Disponibilidad** | **CIS 11:** Resiliencia y Restauración |
| **03** | [keylogger](modulos/03_keylogger/) | Intercepción de periféricos de entrada | **Confidencialidad** | **CIS 05:** Protección de Credenciales |
| **04** | [worm](modulos/04_worm/) | Autoreplicación lateral en red local | **Disponibilidad** | **CIS 12:** Gestión de Infraestructura de Red |
| **05** | [trojan](modulos/05_trojan/) | Ofuscación de carga útil en binario legítimo | **Integridad** | **CIS 02:** Inventario de Activos de Software |
| **06** | [backdoor](modulos/06_backdoor/) | Persistencia oculta y conexión reversa C2 | **Confidencialidad** | **CIS 04:** Gestión de Accesos Seguros |
| **07** | [rootkit](modulos/07_rootkit/) | Evasión por manipulación de llamadas al sistema | **Integridad** | **CIS 10:** Defensas ante Malware (EDR/Heurística) |
| **08** | [botnet](modulos/08_botnet/) | Reclutamiento zombi y orquestación DDoS | **Disponibilidad** | **CIS 13:** Monitoreo y Control de Redes |
| **09** | [steganography](modulos/09_steganography/) | Exfiltración encubierta de datos en medios | **Confidencialidad** | **CIS 03:** Protección de Datos (DLP) |
| **10** | [fileless](modulos/10_fileless/) | Ejecución volátil residente en memoria | **Integridad** | **CIS 10:** Monitoreo del Comportamiento en Memoria |
| **11** | [logic_bomb](modulos/11_logic_bomb/) | Detonación de carga por condición lógica/tiempo | **Disponibilidad** | **CIS 08:** Gestión de Registros de Auditoría |
| **12** | [cryptominer](modulos/12_cryptominer/) | Secuestro y degradación de recursos de CPU | **Disponibilidad** | **CIS 08:** Auditoría y Monitoreo de Procesos |
| **13** | [supply_chain](modulos/13_supply_chain/) | Inyección maliciosa en dependencias | **Integridad** | **CIS 15:** Gestión de Proveedores de Servicio |
| **14** | [dns_tunneling](modulos/14_dns_tunneling/) | Canal encubierto de C2 saltando el Firewall | **Confidencialidad** | **CIS 13:** Filtrado de Conexiones y DNS |

## Flujo de ejecución

```mermaid
sequenceDiagram
    participant E as Estudiante
    participant T as core/tui.py (Textual)
    participant S as core/lab_setup.py
    participant M as modulos/XX/

    E->>T: python -m core.tui
    T->>E: Renderiza interfaz visual (Paneles + Datos CIA/CIS)
    E->>T: Selecciona módulo y presiona [Enter]
    T->>S: Verifica que existan archivos de prueba
    T->>M: Ejecuta subproceso (simulacion.py) de forma asíncrona
    M-->>T: Envía salida estándar en tiempo real
    T->>E: Muestra output en el panel de logs
    E->>T: Presiona [D] para mitigar
    T->>M: Ejecuta subproceso (defensa.py)
    M-->>T: Limpieza y restauración completada
    T->>E: Actualiza panel de logs con éxito

```

## Estructura de cada módulo

```text
modulos/XX_nombre/
├── README.md         # Teoría profunda (Tríada CIA + Controles CIS)
├── {nombre}.py       # Código educativo ejecutable
└── defensa.py        # Detección + mitigación + limpieza

```

Cada script de simulación soporta de forma interna:

* `--help` — muestra ayuda
* `--clean` — elimina artefactos generados

## Principios de diseño

```mermaid
flowchart LR
    DRY["DRY<br/>core/ compartido"]
    SAFE["SAFE<br/>solo en directorio lab"]
    EDU["EDU<br/>paso a paso explicado"]
    MOD["MODULAR<br/>14 modulos independientes"]

    DRY --> SETUP["lab_setup.py unico"]
    DRY --> COMMON["common.py unico"]
    SAFE --> CHECK["verifica archivos de prueba"]
    SAFE --> CLEAN["TUI/Setup reversa todo"]
    EDU --> BANNER["información en panel TUI"]
    EDU --> STEP["output asíncrono en logs"]
    MOD --> ISOLATE["cada modulo autocontenido"]

```

## Uso en aula

1. Clonar el repositorio.
2. Ejecutar `python core/lab_setup.py` para generar el entorno seguro con archivos de prueba.
3. Navegar el laboratorio visual interactivo mediante `python -m core.tui`.
4. Cada módulo cuenta con documentación que profundiza en la teoría del malware, su impacto de gobernanza y bibliografía.
5. Al finalizar la práctica, limpiar el entorno con: `python core/lab_setup.py --clean`.

## Licencia

MIT — Uso exclusivamente educativo y académico
