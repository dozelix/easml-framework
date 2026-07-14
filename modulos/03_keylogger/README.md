# Modulo 03 - Keylogger

## 📖 1. Definicion Teorica y Contexto Historico

Un **keylogger** (registrador de teclas o keystroke logger) es un software o
hardware que captura cada tecla presionada por el usuario en un teclado.
Es una de las herramientas de espionaje y robo de informacion mas antiguas
y efectivas en ciberseguridad, utilizada tanto por actores de amenaza
estatales como por cibercriminales comunes.

### Tipos de keyloggers

**Hardware:**
Dispositivo fisico conectado entre el teclado y la PC (o integrado en un dongle
USB). Son extremadamente dificiles de detectar con software porque operan a nivel
de capa fisica. La unica defensa efectiva es la inspeccion fisica del equipo.

**Software — API-based:**
Utilizan la API de Windows `SetWindowsHookEx` con el hook `WH_KEYBOARD` para
interceptar teclas antes de que lleguen a la aplicacion destino. Son los mas
comunes y relativamente faciles de detectar con antivirus modernos.

**Software — Driver-based:**
Instalan un driver de teclado virtual que intercepta las pulsaciones a nivel
de kernel. Mas dificiles de detectar que los API-based porque operan por debajo
del nivel de las aplicaciones de usuario.

**Kernel-level (rootkit):**
Se integran directamente en el kernel del sistema operativo, interceptando las
interrupciones de hardware del teclado (IRQ). Extremadamente dificiles de
detectar sin herramientas forenses especializadas.

**Form-based (web injection):**
Capturan contenido de formularios web usando JavaScript inyectado en el
navegador. No capturan todas las teclas, solo los datos introducidos en
campos de formulario (login, checkout, etc.).

### Ejemplos historicos

| Ano | Nombre | Contexto |
|-----|--------|----------|
| 2000 | Perfect Keylogger | Primer keylogger commercial masivo, vendido como "herramienta de monitoreo parental" |
| 2007 | ZeuS/Zbot | Banking trojan con keylogger integrado, robo de $100M+ en credenciales bancarias |
| 2014 | DarkComet | RAT con keylogger, usado en ataques APT contra gobiernos |
| 2015 | Pawn Storm (APT28) | Grupo rususado keyloggers en ataques a la OTAN y gobiernos europeos |
| 2020 | Agent Tesla | .NET keylogger usado en campañas de phishing contra empresas energéticas |
| 2023 | Ongoing campaigns | Keyloggers siguen siendo el top 3 de malware en detections globales |

---

## ⚙️ 2. Mecanismo de Funcionamiento Tecnologico (Flujo Logico)

### Flujo detallado de un keylogger

```
1. INSTALACION
   El keylogger se instala en el sistema via:
   - Trojan disfrazado de software legitimo
   - Phishing con archivo adjunto malicioso
   - Vulnerabilidad de ejecucion remota de codigo (RCE)
   - Dispositivo USB malicioso (hardware keylogger)

2. REGISTRO DE HOOK (modo API)
   a) Llama a SetWindowsHookEx(WH_KEYBOARD_LL, callback, hMod, 0)
   b) El sistema operativo ejecuta el callback del keylogger
      ANTES de entregar la tecla a la aplicacion destino
   c) El callback registra la tecla y la keycode en un buffer

3. CAPTURA DE TECLAS
   Para cada evento de teclado:
   a) Recibe la virtual key code (VK_CODE)
   b) Convierte a caracter usando GetKeyNameText / MapVirtualKey
   c) Detecta teclas especiales: ENTER, TAB, SHIFT, CTRL, etc.
   d) Almacena timestamp + keycode + caracter en buffer

4. FILTRADO Y ALMACENAMIENTO
   a) Filtra por ventana activa (titulo de la ventana actual)
   b) Si la ventana contiene "bank", "login", "gmail" -> alta prioridad
   c) Almacena en archivo de log cifrado o en memoria

5. EXFILTRACION
   Los datos capturados se envian al atacante via:
   a) Email cifrado periodico
   b) Conexion HTTP/HTTPS a servidor C2
   c) DNS tunneling (oculto en consultas DNS)
   d) Almacenamiento local para acceso fisico

6. IMPACTO
   El atacante obtiene:
   - Credenciales de acceso (email, redes sociales, VPN)
   - Datos bancarios (DNI, tarjeta, clave)
   - Mensajes privados (chats, emails)
   - Informacion corporativa (secretos, propiedad intelectual)
```

### En esta simulacion educativa

`keylogger.py` **NO captura teclas reales**. Genera un `keylog.log` con
5 sesiones ficticias que simulan a un usuario escribiendo:
- Login de correo electronico (gmail.com + contrasena)
- Mensajes de chat de trabajo (Slack/Teams)
- Login de portal bancario (DNI + contrasena)
- Busquedas en Google
- Checkout con tarjeta de credito

Cada sesion incluye timestamps, teclas individuales con keycodes, y
teclas especiales (ENTER, TAB) para demostrar como un keylogger real
reconstruye la actividad del usuario.

---

## 🔺 3. Alineacion con la Trisada CIA

* **Pilar Afectado:** Confidencialidad (Confidentiality)
* **Justificacion Tecnica:** El keylogger ataca directamente la Confidencialidad
  al capturar informacion que el usuario introduce con la expectativa de que
  solo la aplicacion destino la recibira. Cada tecla presionada — desde una
  contrasena hasta un mensaje privado o un numero de tarjeta de credito — queda
  expuesta a un tercero no autorizado. El usuario no tiene forma de saber que
  su entradas estan siendo monitoreadas, lo que viola el principio de Confidencialidad
  de que la informacion solo sea accesible para autorizados. A diferencia del
  ransomware (Disponibilidad) o el wiper (Disponibilidad), el keylogger no
  destruye ni bloquea datos: los **lee sin autorizacion**.

---

## 🛡️ 4. Mitigacion bajo la Norma de Controles CIS

* **CIS Control 3 — Proteccion de Datos (Data Protection):**
  Este control exige desarrollar procesos y controles para clasificar datos,
  asignar dueños, y proteger la informacion confidencial. Incluye el uso de
  cifrado, DLP (Data Loss Prevention), y controles de acceso que garanticen
  que solo personas autorizadas accedan a datos sensibles. La proteccion
  contra keyloggers se implementa evitando que los datos sensibles viajen
  por canales inseguros (como un teclado monitoreado).

* **Implementacion Practica en Laboratorio:**
  `cazador_de_amenazas.py` implementa la deteccion analizando archivos de log en busca de
  patrones de datos sensibles: expresiones regulares para DNIs, numeros de
  tarjeta, emails, y contrasenas. Tambien monitorea procesos sospechosos
  y recomienda medidas preventivas como 2FA, gestores de contrasenas, y
  teclados virtuales.

### Cuándo aplicar esta defensa

- **Deteccion de hooks de teclado no autorizados**: Cuando un EDR reporta que un proceso ha registrado un hook de teclado (`SetWindowsHookEx` con `WH_KEYBOARD_LL`) que no corresponde a un software legitimo conocido
- **Archivos de log con datos sensibles**: Cuando se descubren archivos de log que contienen patrones de DNIs, numeros de tarjeta de credito, credenciales de acceso o mensajes privados — esto indica que un keylogger esta capturando la actividad del usuario
- **Procesos sospechosos en memoria**: Procesos sin firma digital, con nombres genéricos (svchost.exe duplicados), o que consumen recursos de forma inusual pueden alojar keyloggers
- **Alertas de red inusuales**: Conexiones salientes periodicas a servidores desconocidos, especialmente via DNS tunneling o HTTPS a IPs no estandar, pueden indicar exfiltracion de datos capturados por un keylogger
- **Escenario real**: Un departamento de finanzas reporta que su portal bancario detecta accesos sospechosos desde ubicaciones desconocidas. El equipo de seguridad sospecha de un keylogger y activa la busqueda de artefactos

### Por qué funciona esta defensa

- **Clasificacion reduce la superficie de ataque**: Si los datos sensibles (credenciales, datos financieros) nunca viajan por canales que un keylogger pueda monitorear (teclado fisico), la captura se vuelve inutil. Gestores de contrasenas y autenticadores 2FA eliminan la necesidad de escribir credenciales
- **DLP bloquea la exfiltracion**: Incluso si un keylogger captura datos, un sistema DLP (Data Loss Prevention) puede detectar y bloquear el envio de informacion clasificada a destinos no autorizados, cortando la cadena de robo
- **Deteccion por patrones regulatorios**: Las expresiones regulares para DNIs, tarjetas y emails funcionan porque estos datos tienen formatos estandarizados. Un keylogger que capture este tipo de informacion inevitablemente creara patrones detectables en sus logs
- **2FA mitiga el impacto**: Si la autenticacion de dos factores esta habilitada, las credenciales robadas por un keylogger son insuficientes para acceder a las cuentas, reduciendo dramaticamente el valor del ataque

### Ejercicios practicos de defensa

1. **Caza de datos sensibles en logs**: Ejecuta `python keylogger.py` para generar el log simulado. Luego ejecuta `python cazador_de_amenazas.py` y analiza los patrones detectados: emails, DNIs, numeros de tarjeta, contrasenas. Documenta que tipo de informacion se revelaria en un escenario real y que dano causaria
2. **Evaluacion de controles preventivos**: Revisa el informe generado por `cazador_de_amenazas.py` sobre procesos sospechosos. Para cada tipo de proceso identificado, investiga como se veria en un sistema real (nombre, consumo de recursos, puertos abiertos) y que herramienta de deteccion lo identificaria
3. **Diseno de politica de datos sensibles**: Basandote en los patrones detectados por la herramienta, diseña una politica de proteccion de datos para un equipo de 20 personas. Incluye: cuales datos se clasifican como sensibles, que herramientas se usan para protegerlos (gestor de contrasenas, 2FA, teclado virtual), y como se entrena a los usuarios

---

## 🚀 5. Detalles de la Simulacion Educativa (Python)

### Que hace `keylogger.py`

```
1. PREPARACION
   - Crea directorio_pruebas/ si no existe

2. INSTALACION (informativa)
   - Muestra los vectores de infeccion tipicos
   - Explica los 4 tipos de keylogger (API, driver, kernel, hardware)

3. CAPTURA DE TECLAS
   - Genera 5 sesiones ficticias de escritura:
     * Sesion 1: Login de correo (gmail.com + contrasena)
     * Sesion 2: Mensaje de chat de trabajo
     * Sesion 3: Login bancario (DNI + contrasena)
     * Sesion 4: Busqueda en Google
     * Sesion 5: Checkout con tarjeta de credito
   - Cada tecla se registra con timestamp y keycode
   - Guarda todo en directorio_pruebas/keylog.log

4. EXFILTRACION (informativa)
   - Muestra los metodos que un keylogger real usaria
   - Email cifrado, DNS tunneling, HTTP/HTTPS, almacenamiento local

5. ANALISIS
   - Resume que tipo de datos se revelarian
   - Credenciales, datos bancarios, mensajes privados
```

### Que hace `cazador_de_amenazas.py`

```
1. ESCANEO DE ARCHIVOS
   - Busca keylog.log en directorio_pruebas/
   - Detecta otros archivos .log con patrones de keylogger

2. ANALISIS DE CONTENIDO
   - Cuenta teclas totales, ENTER, TAB, sesiones
   - Usa regex para detectar patrones sensibles:
     * Emails (usuario@dominio.com)
     * Contrasenas (palabras clave)
     * DNI argentino (XX.XXX.XXX)
     * Tarjetas de credito (XXXX XXXX XXXX XXXX)
     * Fechas (DD/MM/AAAA)

3. MONITOREO DE PROCESOS
   - Muestra procesos tipicos que pueden ocultar keyloggers
   - Niveles de riesgo por tipo de proceso

4. PREVENCION
   - Recomienda 2FA, gestor de contrasenas
   - Teclado virtual para datos sensibles
   - Inspeccion fisica de USB
   - EDR con monitoreo de hooks
```
