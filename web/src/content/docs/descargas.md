---
title: 'Descargas'
description: 'Ejecutables del laboratorio sin instalar Python'
---

Usar el laboratorio **sin clonar ni instalar Python**: cada release publica
binarios listos en [GitHub Releases](https://github.com/dozelix/easml-framework/releases).

| Sistema | Archivo | Formato |
|---|---|---|
| Windows 10/11 (64-bit) | `EASML.exe` | Ejecutable único: doble clic |
| Linux (64-bit) | `easml-linux.tar.gz` | Descomprimir y ejecutar `EASML` |
| macOS (Apple Silicon) | `easml-macos.zip` | Descomprimir y abrir `EASML` |

```bash
# Linux / macOS
tar -xzf easml-linux.tar.gz   # o: unzip easml-macos.zip
./EASML
```

El laboratorio portable guarda `directorio_pruebas/` y `lab_data/` **junto al
ejecutable** (no ensucia el sistema). Todo es reversible desde el botón
*Clean* de la propia app.

> Nota: Windows SmartScreen y Gatekeeper pueden advertir por ser un binario
> sin firmar. Es el build automático del propio repositorio (ver workflow
> `release.yml`); el código es 100% auditable aquí mismo.
