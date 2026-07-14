# Módulo 08 — Botnet

## 📖 1. Definición Teórica y Contexto Histórico

Una **botnet** es una red de dispositivos comprometidos ("bots" o "zombies") controlados
remotamente por un atacante (botmaster) mediante un servidor **Command & Control (C2)**.
Cada dispositivo infectado ejecuta órdenes del atacante sin conocimiento del usuario
legítimo, convirtiéndose en un nodo de una infraestructura distribuida de ataque.

### Protocolos de C2

| Protocolo  | Características                     | Ejemplo histórico |
|------------|-------------------------------------|-------------------|
| IRC        | Simple, bajo perfil, canales        | GTBot (2000s)     |
| HTTP/HTTPS | Se mezcla con tráfico normal        | Zeus (2007)       |
| P2P        | Sin punto central, resiliente       | Storm Worm (2007) |
| DNS        | Evade firewalls estrictos           | BredoLab (2009)   |

### Ejemplos históricos

| Año  | Botnet       | Impacto                                                      |
|------|-------------|--------------------------------------------------------------|
| 2007 | Cutwail      | Generaba ~50% del spam global en su punto máximo             |
| 2009 | BredoLab     | 30 millones de PCs, usaba DNS para canal C2                  |
| 2014 | Emotet       | Botnet bancaria, redistribuía TrickBot y Ryuk (2014-2021)    |
| 2016 | Mirai        | Infectó cámaras IoT, atacó Dyn DNS con 1.2 Tbps de tráfico  |

### Tipos de ataque DDoS

- **UDP Flood** — Inunda con paquetes UDP aleatorios al puerto objetivo.
- **HTTP Flood** — Solicitudes HTTP/HTTPS masivas que saturan el servidor web.
- **SYN Flood** — Abre conexiones TCP sin completar el handshake three-way.
- **DNS Amplification** — Usa servidores DNS como amplificador de tráfico spoofado.

## ⚙️ 2. Mecanismo de Funcionamiento Tecnológico (Flujo Lógico)

```
1. PROPAGACIÓN: El botmaster compromete dispositivos mediante phishing, exploits o IoT desprotegido.
2. CONEXIÓN C2: Cada bot se conecta al servidor C2 y se registra en canales (IRC/HTTP).
3. RECONOCIMIENTO: El botmaster identifica capacidades de cada bot (CPU, ancho de banda, OS).
4. COMANDOS: Se envían órdenes a los canales: SCAN, ATTACK, UPDATE, SLEEP, EXFIL.
5. EJECUCIÓN DDoS: Los bots coordinan ataques simultáneos contra el objetivo.
6. MÉTRICAS: Se miden paquetes/segundo, ancho de banda consumido, duración del ataque.
7. PERSISTENCIA: Los bots mantienen heartbeat periódico para confirmar disponibilidad.
```

## 🔺 3. Alineación con la Tríada CIA

* **Pilar Afectado: Disponibilidad (Availability)**
* **Justificación Técnica:** Un ataque DDoS orquestado por una botnet satura los recursos
  de la víctima (CPU, memoria, ancho de banda), impidiendo que servicios legítimos
  respondan a usuarios reales. La disponibilidad se pierde cuando el sistema deja de
  poder prestar el servicio para el que fue diseñado. Una botnet de 10,000 bots con
  1 Mbps cada uno genera 10 Gbps de tráfico malicioso, suficiente para colapsar
  la mayoría de los servidores.

## 🛡️ 4. Mitigación bajo la Norma de Controles CIS

* **CIS Control 13: Monitoreo y Defensa de Red:**
  Implementa monitoreo continuo de tráfico de red para detectar patrones anómalos
  como beaconing C2, picos de tráfico saliente, y conexiones a destinos conocidos
  maliciosos.

* **Implementación Práctica en Laboratorio:**
  `mitigacion_ddos_filtros.py` analiza el archivo `bot_config.json` generado por la simulación,
  extrae IPs, canales C2 y métricas de ataque, mostrando cómo un analista SOC
  correlacionaría estos artefactos para identificar la infraestructura de la botnet.

### Cuándo aplicar esta defensa

- **Tráfico C2 periódico (beaconing):** Cuando se detecta un host que realiza
  conexiones regulares a un mismo destino IP o dominio cada pocos segundos
  (heartbeat), es un indicador fuerte de un bot registrado en una botnet.
- **Picos de tráfico saliente inusuales:** Un aumento repentino de tráfico
  saliente desde un servidor o estación de trabajo que normalmente no genera
  tráfico externo sugiere que está participando en un ataque DDoS o exfiltrando
  datos.
- **Alertas de DDoS en capa 7:** Cuando un servidor web reporta saturación de
  conexiones HTTP/HTTPS con patrones repetitivos (mismo User-Agent, mismo
  intervalo), activar la inspección de hosts internos que puedan ser bots.
- **Detección de canales C2 conocidos:** Si el IDS/IPS identifica tráfico hacia
  IPs o dominios en listas de threat intelligence (Feodo Tracker, AlienVault OTX),
  activar el análisis forense de los hosts involucrados.

### Por qué funciona esta defensa

- **Visibilidad del tráfico:** El monitoreo continuo de red (CIS Control 13)
  proporciona la capacidad de ver patrones de tráfico que de otra forma pasarían
  desapercibidos. La correlación de flujos de red permite identificar la
  infraestructura C2 sin depender de firmas antivirus.
- **Desarticulación de la cadena de mando:** Al detectar y bloquear las
  comunicaciones C2, se corta el canal entre el botmaster y los bots, eliminando
  la capacidad del atacante de enviar comandos de ataque DDoS o exfiltración.
- **Principio de defensa en profundidad:** La combinación de monitoreo de
  tráfico, análisis de logs y correlación de eventos permite detectar la botnet
  en múltiples capas, haciendo que la evasión sea significativamente más difícil.

### Ejercicios prácticos de defensa

1. **Análisis de artefactos C2:** Ejecuta `botnet.py` y luego analiza el
   archivo `bot_config.json` con `mitigacion_ddos_filtros.py`. Observa las IPs,
   canales y métricas extraídas. Intenta identificar qué patrones de beaconing
   indicarían un bot activo en un entorno real.
2. **Correlación de logs:** Revisa `botnet_c2.log` y busca comandos del tipo
   `ATTACK` o `SCAN`. En un entorno real, estos registros se correlacionarían
   con alertas de IDS para determinar el momento exacto del ataque y los bots
   participantes.
3. **Evaluación de impacto:** Con las métricas generadas (paq/seg, Mbps, bots),
   calcula el ancho de banda total del ataque simulado. Compara con la capacidad
   de enlace de tu red para dimensionar la mitigación necesaria.

## 🚀 5. Detalles de la Simulación Educativa (Python)

### Qué hace `botnet.py`

```
1. Genera una lista de 15-40 bots ficticios con IPs, puertos, OS y estados aleatorios.
2. Asigna cada bot a uno de 4 canales IRC simulados (#control, #attacks, #loot, #beacon).
3. Simula la ejecución de 8 comandos C2: SCAN, ATTACK, UPDATE, SLEEP, EXFIL, BEACON.
4. Calcula métricas simuladas de DDoS: tipo, bots participantes, paq/seg, Mbps.
5. Guarda toda la configuración en bot_config.json (lista de bots + métricas).
6. Registra los comandos C2 en botnet_c2.log con timestamps y canales.
7. Muestra resumen visual paso a paso con colores en consola.
```

### Qué hace `mitigacion_ddos_filtros.py`

```
1. Escanea directorio actual en busca de bot_config.json y botnet_c2.log.
2. Analiza el contenido del JSON: nombre de red, servidor C2, total de bots.
3. Muestra las IPs, canales y estados de los bots encontrados.
4. Ofrece eliminación de todos los artefactos de la simulación.
5. Registra el hallazgo en defensa_botnet.log para auditoría.
```

---

## Ejecución

```bash
# Generar archivos de laboratorio
python core/lab_setup.py

# Ejecutar simulación
python modulos/08_botnet/botnet.py

# Ver ayuda
python modulos/08_botnet/botnet.py --help

# Limpiar artefactos de la simulación
python modulos/08_botnet/botnet.py --clean

# Ejecutar defensa (detectar y limpiar)
python modulos/08_botnet/mitigacion_ddos_filtros.py
```

> **NOTA:** No se generan conexiones de red reales ni se contactan servidores externos.
> Todos los datos son ficticios y operan dentro de `directorio_pruebas/`.
