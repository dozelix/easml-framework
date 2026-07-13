# Modulo 01 - Ransomware

## 📖 1. Definicion Teorica y Contexto Historico

El **ransomware** es un tipo de malware que cifra los archivos de la victima usando
algoritmos criptograficos y exige un rescate — generalmente en criptomonedas como
Bitcoin o Monero — a cambio de la clave de descifrado. Es actualmente una de las
amenazas mas destructivas y lucrativas del panorama de ciberseguridad global.

### Mecanismo general

Un ransomware tipico opera en dos fases criptograficas:

1. **Cifrado simetrico**: genera una clave unica por archivo (AES-256 o ChaCha20)
   y cifra el contenido. Esto es rapido y eficiente para archivos grandes.
2. **Cifrado asimetrico**: cifra la clave simetrica con una clave publica RSA
   incrustada en el binario del malware. Solo el atacante posee la clave privada
   correspondiente.

Este esquema hibrido garantiza que **ningun tercero** pueda descifrar los archivos
sin la clave privada del atacante.

### Ejemplos historicos

| Ano | Nombre | Impacto |
|-----|--------|---------|
| 2013 | CryptoLocker | Pionero del modelo RaaS (Ransomware-as-a-Service), cifro 500.000+ sistemas |
| 2017 | WannaCry | Exploto EternalBlue (MS17-010), infecto 200.000+ equipos en 150 paises incluyendo NHS (UK) |
| 2017 | NotPetya | Disfrazado de ransomware pero en realidad era un wiper; causo $10B+ en danos globales |
| 2019 | Ryuk | Ataques dirigidos a hospitales y grandes corporaciones, promedio de rescate $1.5M |
| 2021 | REvil/Sodinokibi | Doble extorsion: cifrado + amenaza de publicacion de datos robados (Kaseya VSA) |
| 2023 | Cl0p | Exploto MOVEit Transfer (CVE-2023-34362), afecto a 2.500+ organizaciones |

### WannaCry: el caso mas emblematico

El 12 de mayo de 2017, WannaCry se propago automaticamente explotando la
vulnerabilidad **EternalBlue** (un exploit para el protocolo SMBv1 de Windows,
filtrado por el grupo Equation Group). En cuestion de horas, infecto mas de
200.000 computadoras en 150 paises, afectando hospitales del NHS en Reino Unido,
fabricas de Renault en Francia, y Telefonica en Espana. La propagacion se detuvo
gracias a un investigador britanico (MalwareTech) que registro un dominio "kill
switch" contenido en el codigo del malware.

---

## ⚙️ 2. Mecanismo de Funcionamiento Tecnologico (Flujo Logico)

### Flujo detallado de un ataque ransomware

```
1. VECTOR DE ENTRADA
   El payload del ransomware se ejecuta en el sistema victima, tipicamente
   via: email phishing con macro maliciosa, exploit de vulnerabilidad
   remota (RCE), o drive-by download.

2. EJECUCION Y PERSISTENCIA
   El malware se instala en el sistema (AppData, ProgramData, etc.)
   y configura persistencia mediante Registro de Windows o tareas
   programadas.

3. RECONOCIMIENTO DEL SISTEMA
   El ransomware enumera: tipo de disco, espacio disponible, idioma
   del sistema (evita CIS), procesos de seguridad activos, y software
   de backup instalado.

4. BUSQUEDA DE ARCHIVOS
   Recorre todos los directorios accesibles buscando extensiones
   objetivo (.txt, .docx, .pdf, .jpg, .xlsx, etc.) usando APIs
   como FindFirstFile/FindNextFile (Windows) o os.walk() (Python).

5. CIFRADO
   Para cada archivo:
   a) Genera una clave simetrica aleatoria (AES-256)
   b) Cifra el contenido del archivo con esa clave
   c) Cifra la clave simetrica con la clave publica RSA del atacante
   d) Almacena la clave cifrada junto al archivo (en un .key o metadata)

6. ELIMINACION DE BACKUPS
   Ejecuta comandos para eliminar copias de seguridad:
   - vssadmin delete shadows /all /quiet
   - bcdedit /set {default} recoveryenabled No
   - wbadmin delete catalog -quiet

7. NOTA DE RESCATE
   Deja un archivo de texto o HTML en cada directorio afectado
   con instrucciones de pago via Tor/onion.

8. EXFILTRACION (opcional, doble extorsion)
   Antes del cifrado, exfiltra datos sensibles a servidores del
   atacante para amenazar con publicarlos si no se paga.
```

### En esta simulacion educativa

El algoritmo de `ransomware.py` reemplaza el cifrado real con un **inversion de
texto**: invierte el orden de caracteres de cada linea del archivo. Esto es
trivialmente reversible (volver a invertir restaura el contenido) pero demuestra
el concepto de "perder acceso" al contenido original.

---

## 🔺 3. Alineacion con la Trisada CIA

* **Pilar Afectado:** Disponibilidad (Availability)
* **Justificacion Tecnica:** El ransomware ataca directamente la Disponibilidad
  al hacer que los archivos sean inaccesibles para el usuario legitimo. Aunque
  los bytes siguen fisicamente en disco, el contenido queda cifrado (o invertido,
  en esta simulacion) de forma que el usuario no puede leer ni usar sus archivos
  sin la clave de descifrado. La perdida de Disponibilidad es el mecanismo de
  extorsion: el atacante ofrece restaurarla a cambio de un pago. Ademas, la
  eliminacion de copias de seguridad (shadow copies, etc.) refuerza este efecto
  al bloquear los mecanismos nativos de recuperacion.

---

## 🛡️ 4. Mitigacion bajo la Norma de Controles CIS

* **CIS Control 11 — Recuperacion de Datos (Data Recovery):**
  Este control exige implementar y mantener procesos de respaldo de datos,
  probar regularmente la recuperacion, y garantizar que las copias de
  seguridad esten protegidas contra acceso no autorizado y cifrado por malware.
  La regla **3-2-1** es el estandar: 3 copias de los datos, en 2 medios
  diferentes, con 1 copia fuera de linea o remota.

* **Implementacion Practica en Laboratorio:**
  `respuesta_a_incidentes.py` implementa la fase de recuperacion verificando la integridad
  de los archivos y restaurando el contenido original mediante la inversion
  del texto (reverso del cifrado simulado). Luego muestra hashes SHA-256
  para confirmar que los archivos restaurados son correctos. En produccion,
  esto equivale a restaurar desde un backup verificado despues de un ataque
  ransomware.

---

## 🚀 5. Detalles de la Simulacion Educativa (Python)

### Que hace `ransomware.py`

```
1. PREPARACION
   - Crea el directorio ./directorio_pruebas/
   - Copia los 12 archivos del laboratorio ahi (nunca toca los originales)

2. RECONOCIMIENTO
   - Enumera archivos con extensiones de texto (.txt, .py, .html, .csv, .md)
   - Muestra tamano y nombre de cada archivo objetivo

3. CIFRADO SIMULADO
   - Lee cada archivo de texto
   - Invierte el orden de caracteres de cada linea (texto[::-1])
   - Guarda el resultado como "nombre.txt.locked"
   - Registra hash SHA-256 original para verificacion

4. NOTA DE RESCATE
   - Genera README_RESCATE.txt con instrucciones ficticias de pago
   - Simula el modelo de extorsion real

5. RESUMEN
   - Muestra estadisticas del ataque
   - Explica la diferencia entre cifrado real e inversion de texto
```

### Que hace `respuesta_a_incidentes.py`

```
1. VERIFICACION
   - Comprueba si existe directorio_pruebas/

2. ESCANEO
   - Busca archivos .locked en directorio_pruebas/
   - Detecta notas de rescate README_RESCATE.txt
   - Muestra hashes SHA-256 de archivos detectados

3. RESTAURACION
   - Para cada .locked: invierte el texto para obtener el contenido original
   - Guarda el resultado como el nombre original (sin .locked)
   - Verifica integridad post-restauracion

4. VERIFICACION DE HASHES
   - Muestra hashes SHA-256 de todos los archivos restaurados
   - Confirma que la restauracion fue exitosa

5. RECOMENDACIONES
   - Regla 3-2-1 para backups
   - Parchado de vulnerabilidades
   - Segmentacion de red
   - Uso de EDR/antivirus
```
