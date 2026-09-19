---
title: 'Instalación y despliegue'
description: 'Entorno en 3 pasos o binario portable'
---

El laboratorio está diseñado para ejecutarse sin fricciones ni permisos de administrador: la GUI Flet no pide nada del sistema y la única dependencia es `flet`.

Si no quieres instalar nada, usa directamente los [binarios portables](/descargas/).

## Requisitos previos

* **Python 3.10** o superior.
* **pip** actualizado.
* Sin dependencias de sistema (Flet trae su runtime).

## Configuración en 3 pasos

### 1. Clonar el repositorio

```bash
git clone https://github.com/dozelix/easml-framework.git
cd easml-framework
```

### 2. Crear y activar un entorno virtual (`.venv`)

Aislar dependencias evita conflictos con librerías globales del sistema.

* **Linux / macOS:**

```bash
python3 -m venv .venv
source .venv/bin/activate
```

* **Windows (PowerShell):**

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

> Si Windows bloquea scripts, en esa terminal: `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process`.

### 3. Instalar la dependencia

```bash
pip install -r requirements.txt
```

## Preparación del terreno de pruebas

Antes de abrir la interfaz, inicializa el entorno seguro donde operan las amenazas: genera `directorio_pruebas/` con archivos sintéticos que sirven de "víctimas".

```bash
python core/lab_setup.py
```

Al finalizar, purga artefactos, logs y rastros:

```bash
python core/lab_setup.py --clean
```

Siguiente paso: [manual de la interfaz](/interfaz/).
