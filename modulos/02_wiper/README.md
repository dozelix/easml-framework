# Modulo 02 - Wiper

## 📖 1. Definicion Teorica y Contexto Historico

Un **wiper** (limpiador) es un tipo de malware disenado para **destruir datos de
forma permanente**, sin posibilidad de recuperacion sin un backup. A diferencia del
ransomware, el wiper **no busca rescate monetario**: su objetivo es causar el mayor
dano posible al sistema victima, generalmente en contextos de ciberguerra o
sabotaje corporativo.

### Diferencia clave con ransomware

| Caracteristica | Ransomware | Wiper |
| --------------- | ----------- | ------- |
| Objetivo | Extorsion monetaria | Destruccion / sabotaje |
| Cifrado | Si (reversible con clave) | No (corrupcion irreversible) |
| Nota de rescate | Si | No |
| Recuperacion | Posible con clave o backup | Solo con backup |
| Motivacion | Economica | Politica / geopolitica |
| Velocidad | Lenta (cifrado) | Rapida (sobrescritura) |

### Variantes historicas

| Año | Nombre | Contexto |
| ----- | -------- | ---------- |
| 2012 | Shamoon | Ataco Saudi Aramco, destruyo datos de 35.000+ computadoras con imagen de bandera de EEUU |
| 2016 | Shamoon 2 | Segundo ataque a Saudi Aramco y otras empresas del Golfo |
| 2022 | WhisperGate | Previo a la invasion rusa de Ucrania; se disfrazo como ransomware pero era un wiper |
| 2022 | HermeticWiper | Ataco sistemas ucranianos con driver firmado legítimo (WinMon32.sys) |
| 2022 | CaddyWiper | Desplegado en Ucrania durante la invasion; evitaba dispositivos con WinPE |
| 2022 | AcidRain | Wiper para routers/modems Viasat usado el dia de la invasion |

### Contexto geopolitico

Los wipers son el arma de ciberguerra preferida para degradar la capacidad
operativa del adversario. En 2022, Ucrania fue blanco de **cuatro wipers
diferentes** en semanas: WhisperGate, HermeticWiper, CaddyWiper y IsaacWiper,
representando el mayor despliegue coordinado de armas ciberneticas jamas visto.

---

## ⚙️ 2. Mecanismo de Funcionamiento Tecnologico (Flujo Logico)

### Flujo detallado de un ataque wiper

```text
1. INFECCION INICIAL
   El wiper se instala en el sistema via: supply chain comprometida,
   phishing dirigido, explotacion de vulnerabilidad, o USB malicioso.

2. ESCALAMIENTO DE PRIVILEGIOS
   El malware obtiene permisos de administrador/root para poder
   sobreescribir archivos criticos y accesos al disco.

3. RECONOCIMIENTO
   Identifica archivos y sistemas objetivo:
   - Tipos de archivo (.docx, .xlsx, .pdf, .jpg, .sql, etc.)
   - Unidades de disco y particiones
   - Sistemas de archivos montados

4. CORRUPCION / SOBRESCRITURA
   Para cada archivo objetivo:
   a) Sobreescribe los primeros N bytes con datos aleatorios o ceros
   b) En wipers avanzados: sobreescribe TODO el archivo
   c) Shamoon usaba una imagen de bandera de 19KB
   d) NotPetya cifraba el MBR con una clave hardcodeada

5. ELIMINACION DE BACKUPS
   - vssadmin delete shadows /all /quiet
   - bcdedit /set {default} recoveryenabled No
   - wbadmin delete catalog -quiet
   - Elimina puntos de restauracion del sistema

6. SOBRESCRITURA DEL MBR / GPT
   Algunos wipers (Shamoon, NotPetya) sobreescriben el Master Boot
   Record para hacer el disco completamente inoperativo.

7. RESULTADO
   El sistema queda inoperativo. Sin backup = perdida total.
```

### En esta simulacion educativa

El algoritmo de `wiper.py` sobreescribe los **primeros 64 bytes** de cada
archivo con datos aleatorios generados por `random.randint(0, 255)`. Esto corrompe
la estructura del archivo (headers de imagenes, metadatos, etc.) demostrando como
un wiper destruye datos sin necesidad de cifrarlos.

---

## 🔺 3. Alineacion con la Trisada CIA

* **Pilar Afectado:** Disponibilidad (Availability)
* **Justificacion Tecnica:** El wiper ataca la Disponibilidad de forma mas agresiva
  que el ransomware: mientras el ransomware cifra (reversible con clave), el wiper
  **destruye** los datos sobreescribiendo sus bytes con basura. El resultado es
  que los archivos dejan de ser legibles — no solo inaccesibles, sino
  **irrecuperables** sin un backup externo. A diferencia del ransomware, no hay
  "clave" que pagar. La unica defensa es un backup offline que el wiper no pueda
  alcanzar. El wiper es el ataque mas puro contra la Disponibilidad porque su
  efecto es permanente e irreversible.

---

## 🛡️ 4. Mitigacion bajo la Norma de Controles CIS

* **CIS Control 10 — Copias de Seguridad (Data Recovery):**
  Este control exige establecer y mantener un proceso de copias de seguridad
  regulares, con prueba periodica de restauracion. Las copias deben estar
  protegidas contra acceso no autorizado, cifrado por malware, y eliminacion
  por wipers. Los backups deben ser **inmutables** (WORM) y mantener al menos
  una copia offline o air-gapped.

* **Implementacion Practica en Laboratorio:**
  `auditoria_de_integridad.py` implementa la verificacion de integridad comparando hashes
  SHA-256 de los archivos actuales contra una copia segura en `.backup_wiper/`.
  Si detecta diferencias, restaura los archivos desde el backup y verifica
  que los hashes coincidan post-restauracion. Esto demuestra el flujo que un
  equipo de respuesta a incidentes seguiria en produccion.

### Cuándo aplicar esta defensa

- **Corrupcion masiva de archivos**: Cuando se detecta que multiples archivos tienen sus primeros bytes sobrescritos con datos aleatorios, o cuando archivos de sistema pierden su formato (headers corruptos, imagenes que no se abren)
- **Eliminacion de copias de seguridad**: Igual que en ransomware, la ejecucion de comandos de eliminacion de shadow copies es un indicador critico, pero en el contexto de wiper se ejecuta inmediatamente antes de la destruccion
- **Alertas de integridad de archivos**: Herramientas FIM (File Integrity Monitoring) que reportan cambios en archivos criticos del sistema o de datos en lote
- **Destruccion de MBR/GPT**: Cuando el sistema no puede arrancar o reporta corrupcion del Master Boot Record — esto indica un wiper avanzado que destruye la tabla de particiones
- **Escenario real**: Durante un incidente geopolitico, un equipo de TI detecta que archivos en multiples servidores tienen headers corruptos y no se pueden abrir. Se activa inmediatamente el protocolo de recuperacion desde backups offline

### Por qué funciona esta defensa

- **Backup inmutable (WORM)**: Un backup WORM (Write Once Read Many) no puede ser modificado ni eliminado ni siquiera por un usuario con privilegios de administrador, porque esta diseniado para ser grabado una sola vez. El wiper no tiene capacidad de destruir algo que no puede modificar
- **Deteccion temprana por comparacion de hashes**: La comparacion SHA-256 entre archivos actuales y su copia segura revela exactamente cuales archivos fueron corrompidos, permitiendo una recuperacion quirurgica en lugar de una restauracion ciega completa
- **Irreversibilidad del ataque**: A diferencia del ransomware, el wiper no tiene punto de retorno — los datos destruidos estan perdidos para siempre sin backup. Esto hace que el backup offline sea la **unica** defensa efectiva, no una opcion
- **Restauracion verificable**: El proceso de restaurar desde backup y verificar hashes garantiza que el sistema queda exactamente como estaba antes del ataque, sin residuos de corrupcion

### Ejercicios practicos de defensa

1. **Observar la destruccion en accion**: Ejecuta `python wiper.py` y observa como los primeros 64 bytes de cada archivo son sobrescritos con datos aleatorios. Luego intenta abrir los archivos corruptos (imagenes, CSVs) y documenta que tipo de danio observas en cada formato
2. **Verificacion de integridad con auditoria**: Ejecuta `python auditoria_de_integridad.py` y analiza el reporte de hashes. Identifica cuales archivos fueron corrompidos (hash diferente al backup) y cuales sobrevivieron intactos. Compara los hashes antes/despues de la restauracion
3. **Diseno de estrategia de backup**: Basandote en los resultados del laboratorio, diseña un plan de backups WORM para una empresa de 50 empleados. Define frecuencia, retencion, ubicacion (offline/on-premise/nube) y prueba de restauracion. Justifica cada decision usando los principios CIS

---

## 🚀 5. Detalles de la Simulacion Educativa (Python)

### Que hace `wiper.py`

```text
1. PREPARACION
   - Crea directorio_pruebas/ y copia los 12 archivos del lab

2. BACKUP SEGURO
   - Crea .backup_wiper/ con copias intactas antes de corromper
   - Representa un backup WORM/air-gapped

3. RECONOCIMIENTO
   - Enumera todos los archivos con extensiones objetivo
   - Muestra tamano y nombre de cada archivo

4. CORRUPCION
   - Para cada archivo: sobreescribe primeros 64 bytes con basura
   - Genera datos aleatorios con random.randint(0, 255)
   - Registra hashes antes/despues de la corrupcion

5. ELIMINACION DE BACKUPS (simulada)
   - Muestra comandos reales que un wiper ejecutaria
   - No ejecuta nada realmente

6. COMPARACION RANSOMWARE vs WIPER
   - Explica las diferencias clave entre ambos tipos
```

### Que hace `auditoria_de_integridad.py`

```text
1. VERIFICACION DE BACKUP
   - Comprueba que .backup_wiper/ existe y tiene archivos

2. ESCANEO DE ARCHIVOS
   - Lista archivos en directorio_pruebas/

3. COMPARACION DE HASHES
   - Calcula SHA-256 de cada archivo actual vs backup
   - Los archivos con hashes diferentes estan corruptos

4. RESTAURACION
   - Copia archivos intactos desde .backup_wiper/
   - Verifica hash post-restauracion

5. VERIFICACION FINAL
   - Muestra hashes SHA-256 de todos los archivos restaurados
   - Confirma integridad

6. RECOMENDACIONES
   - Backups inmutables (WORM)
   - Copias offline/air-gapped
   - Pruebas de restauracion periodicas
```
