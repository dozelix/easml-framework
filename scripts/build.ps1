# Empaqueta la GUI Flet en .exe local (reproducible).
# Canónico: workflow release.yml (CI). Esto es solo para probar en tu máquina.
Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"
Set-Location (Split-Path $PSScriptRoot -Parent)

pip install -r requirements.txt
flet pack flet_main.py -n EASML `
  --product-name EASML `
  --add-data "assets:assets" `
  --add-data "modulos:modulos" `
  --add-data "core:core" `
  --distpath dist

Write-Host ""
Write-Host "[OK] Ejecutable en dist\EASML.exe"
