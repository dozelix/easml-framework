# Laboratorio de Malware Educativo

Repositorio academico para el estudio de amenazas de seguridad informatica.
14 modulos independientes en Python, cada uno con simulacion, defensa y documentacion.

> **Solo para uso educativo en entorno controlado.**

## Arquitectura del Laboratorio

```mermaid
graph TB
    subgraph "Puntos de entrada"
        TUI["python -m core.tui<br/>Interfaz visual (TUI)"]
        CLI["python -m core.cli<br/>Linea de comandos"]
    end

    subgraph "core/ — Utilidades compartidas"
        COMMON["common.py<br/>log, colores, traversal, hashing"]
        SETUP["lab_setup.py<br/>generador de archivos de prueba"]
        TUIMOD["tui.py<br/>interfaz panel dividido"]
        CLIMOD["cli.py<br/>navegador por comandos"]
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
    CLI --> CLIMOD
    TUIMOD --> M01 & M02 & M03 & M04 & M05 & M06 & M07
    TUIMOD --> M08 & M09 & M10 & M11 & M12 & M13 & M14
    CLIMOD --> M01 & M02 & M03 & M04 & M05 & M06 & M07
    CLIMOD --> M08 & M09 & M10 & M11 & M12 & M13 & M14
    M01 & M02 & M03 & M04 & M05 & M06 & M07 --> COMMON
    M08 & M09 & M10 & M11 & M12 & M13 & M14 --> COMMON
    COMMON --> SETUP
```

## Requisitos

- Python 3.7+
- Sin dependencias externas

## Inicio rapido

```bash
# 1. Generar archivos de prueba
python core/lab_setup.py

# 2. Abrir la interfaz visual (recomendado para estudiantes)
python -m core.tui

# 3. O usar el CLI por comandos
python -m core.cli

# 4. Ejecutar un modulo directamente
python modulos/01_ransomware/ransomware.py

# 5. Ejecutar defensa
python modulos/01_ransomware/defensa.py

# 6. Limpiar
python modulos/01_ransomware/ransomware.py --clean
```

## Modulos

| # | Modulo | Tipo de amenaza | Archivos |
| --- | -------- | ----------------- | ---------- |
| 01 | [ransomware](modulos/01_ransomware/) | Cifrado de archivos + rescate | simulacion, defensa, README |
| 02 | [wiper](modulos/02_wiper/) | Corrupcion/eliminacion de datos | simulacion, defensa, README |
| 03 | [keylogger](modulos/03_keylogger/) | Captura de pulsaciones | simulacion, defensa, README |
| 04 | [worm](modulos/04_worm/) | Auto-replicacion en red | simulacion, defensa, README |
| 05 | [trojan](modulos/05_trojan/) | Disfraz + payload oculto | simulacion, defensa, README |
| 06 | [backdoor](modulos/06_backdoor/) | Acceso persistente + C2 | simulacion, defensa, README |
| 07 | [rootkit](modulos/07_rootkit/) | Ocultacion de procesos | simulacion, defensa, README |
| 08 | [botnet](modulos/08_botnet/) | Red de bots + DDoS | simulacion, defensa, README |
| 09 | [steganography](modulos/09_steganography/) | Datos ocultos en imagenes | simulacion, defensa, README |
| 10 | [fileless](modulos/10_fileless/) | Sin archivos en disco | simulacion, defensa, README |
| 11 | [logic_bomb](modulos/11_logic_bomb/) | Payload condicional | simulacion, defensa, README |
| 12 | [cryptominer](modulos/12_cryptominer/) | Mineria CPU fraudulenta | simulacion, defensa, README |
| 13 | [supply_chain](modulos/13_supply_chain/) | Compromiso de dependencias | simulacion, defensa, README |
| 14 | [dns_tunneling](modulos/14_dns_tunneling/) | Exfiltracion via DNS | simulacion, defensa, README |

## Flujo de ejecucion

```mermaid
sequenceDiagram
    participant E as Estudiante
    participant C as core/cli.py
    participant S as core/lab_setup.py
    participant M as modulos/XX/

    E->>C: python -m core.cli
    C->>E: Lista 14 modulos
    E->>C: Selecciona modulo 01
    C->>S: Verifica archivos de prueba
    S-->>C: Archivos listos
    C->>M: Ejecuta script del modulo
    M->>E: Muestra fase por fase
    E->>C: Selecciona defensa
    C->>M: Ejecuta defensa.py
    M->>E: Detecta + limpia artefactos
```

## Estructura de cada modulo

```text
modulos/XX_nombre/
├── README.md         # Teoria profunda + Mermaid diagrams
├── {nombre}.py       # Codigo educativo ejecutable
└── defensa.py        # Deteccion + mitigacion + limpieza
```

Cada script de simulacion soporta:

- `--help` — muestra ayuda
- `--clean` — elimina artefactos generados

## Principios de diseno

```mermaid
flowchart LR
    DRY["DRY<br/>core/ compartido"]
    SAFE["SAFE<br/>solo en directorio lab"]
    EDU["EDU<br/>paso a paso explicado"]
    MOD["MODULAR<br/>14 modulos independientes"]

    DRY --> SETUP["lab_setup.py unico"]
    DRY --> COMMON["common.py unico"]
    SAFE --> CHECK["verifica archivos de prueba"]
    SAFE --> CLEAN["--clean reversa todo"]
    EDU --> BANNER["banner informativo"]
    EDU --> STEP["output fase por fase"]
    MOD --> ISOLATE["cada modulo autocontenido"]
```

## Uso en aula

1. Clonar el repositorio
2. Ejecutar `python core/lab_setup.py` para generar archivos de prueba
3. Navegar modulos con `python -m core.cli` o ejecutar directamente
4. Cada modulo incluye README con teoria, diagramas Mermaid y bibliografia
5. Al finalizar: `python core/lab_setup.py --clean` para limpiar

## Licencia

MIT — Uso exclusivamente educativo y academico.
