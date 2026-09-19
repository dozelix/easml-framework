#!/usr/bin/env python3
"""Genera el índice JSON y las páginas Markdown del sitio docs (web/).

Fuente única: app/config.py (MODULOS, NOMBRES_DEFENSA) + modulos/*/README.md.
Lo generado (web/.../docs/modulos/ y web/src/data/modulos.json) es un
artefacto regenerable: no se edita a mano. La portada (index.mdx) y las
guías (instalacion, interfaz, gobernanza, nuevo-modulo, descargas) son
curadas y viven en el repo.

Uso:
    python scripts/generar_indice.py                # genera artefactos
    python scripts/generar_indice.py --check        # valida consistencia (para CI)
    python scripts/generar_indice.py --check-links  # verifica refs HTTP (manual)
    python scripts/generar_indice.py --clean        # elimina artefactos generados
    python scripts/generar_indice.py --help         # ayuda
"""

import json
import os
import shutil
import sys

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if RAIZ not in sys.path:
    sys.path.insert(0, RAIZ)

from app.config import MODULOS, NOMBRES_DEFENSA  # noqa: E402

DIR_MODULOS = os.path.join(RAIZ, "modulos")
DIR_WEB = os.path.join(RAIZ, "web")
DIR_DOCS = os.path.join(DIR_WEB, "src", "content", "docs", "modulos")
DIR_DATA = os.path.join(DIR_WEB, "src", "data")
PATH_JSON = os.path.join(DIR_DATA, "modulos.json")
PATH_README_RAIZ = os.path.join(RAIZ, "README.md")


def nombre_archivo_defensa(num: str) -> str:
    """Replica la convención de gui_flet (NOMBRES_DEFENSA en minúsculas)."""
    return NOMBRES_DEFENSA.get(num, "defensa").lower().replace(" ", "_") + ".py"


def leer_readme(nombre: str) -> str | None:
    path = os.path.join(DIR_MODULOS, nombre, "README.md")
    if not os.path.isfile(path):
        return None
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def construir_entradas() -> list[dict]:
    """Cruza MODULOS con los README reales y devuelve el índice ordenado por CIS."""
    entradas = []
    for orden, (num, nombre, script, cia, cis, url_ref) in enumerate(MODULOS):
        cuerpo = leer_readme(nombre)
        entradas.append({
            "num": num,
            "nombre": nombre,
            "script": script + ".py",
            "defensa": nombre_archivo_defensa(num),
            "defensa_nombre": NOMBRES_DEFENSA.get(num, "defensa"),
            "cia": cia,
            "cis": cis,
            "ref": url_ref,
            "orden": orden,
            "tiene_readme": cuerpo is not None,
        })
    return entradas


def validar(entradas: list[dict]) -> list[str]:
    """Detecta deriva entre app/config.py y los README. Devuelve lista de errores."""
    errores = []
    for e in entradas:
        if not e["tiene_readme"]:
            errores.append(f"modulos/{e['nombre']}/README.md no existe (listado en config)")
        for campo in ("num", "nombre", "cia", "cis", "ref"):
            if not e[campo]:
                errores.append(f"{e['nombre']}: campo '{campo}' vacío en app/config.py")
    # READMEs huérfanos: existen en disco pero no están en MODULOS
    conocidos = {e["nombre"] for e in entradas}
    for nombre in sorted(os.listdir(DIR_MODULOS)):
        dir_mod = os.path.join(DIR_MODULOS, nombre)
        if not os.path.isdir(dir_mod) or nombre == "common":
            continue
        if nombre not in conocidos:
            errores.append(f"modulos/{nombre}/ existe pero no está en app/config.py")
    if not os.path.isfile(PATH_README_RAIZ):
        errores.append("README.md raíz no existe")
    return errores


def frontmatter_modulo(e: dict) -> str:
    lineas = [
        "---",
        f"title: 'Módulo {e['num']} — {e['nombre']}'",
        f"description: '{e['cia']} · {e['cis']}'",
        "sidebar:",
        f"  order: {e['orden']}",
        "---",
        "",
    ]
    return "\n".join(lineas)


def generar(entradas: list[dict]) -> None:
    os.makedirs(DIR_DOCS, exist_ok=True)
    os.makedirs(DIR_DATA, exist_ok=True)

    for e in entradas:
        cuerpo = leer_readme(e["nombre"]) or "_Sin documentación._\n"
        # Enlaces relativos entre módulos (../otro) no existen en el sitio;
        # el sidebar de Starlight ya provee la navegación.
        destino = os.path.join(DIR_DOCS, e["nombre"] + ".md")
        with open(destino, "w", encoding="utf-8") as f:
            f.write(frontmatter_modulo(e) + cuerpo)
        print(f"  [+] modulos/{e['nombre']}.md")

    publicas = [{k: v for k, v in e.items() if k != "tiene_readme"} for e in entradas]
    with open(PATH_JSON, "w", encoding="utf-8") as f:
        json.dump(publicas, f, ensure_ascii=False, indent=2)
        f.write("\n")
    print("  [+] data/modulos.json")


def verificar_links(entradas: list[dict], timeout: int = 15) -> list[str]:
    """Comprueba que cada URL de referencia responde 2xx/3xx.

    Solo stdlib (urllib). No corre en CI push (falsos rojos por muros
    anti-bots): es verificación manual documentada, ver docs/REQUISITOS.md.
    """
    import urllib.error
    import urllib.parse
    import urllib.request

    fallos = []
    for e in entradas:
        url = e["ref"]
        # B310: solo se permiten esquemas http/https (nada de file:/custom).
        esquema = urllib.parse.urlsplit(url).scheme.lower()
        if esquema not in ("http", "https"):
            fallos.append(f"{e['nombre']}: esquema no permitido en {url}")
            continue
        try:
            req = urllib.request.Request(
                url, headers={"User-Agent": "EASML-check/1.0"})
            # Esquema restringido a http/https arriba: el B310 no aplica.
            with urllib.request.urlopen(  # nosec B310
                    req, timeout=timeout) as resp:
                codigo = resp.status
        except urllib.error.HTTPError as err:
            codigo = err.code
        except Exception as err:  # noqa: BLE001 - cualquier fallo de red cuenta
            fallos.append(f"{e['nombre']}: {url} -> {err}")
            continue
        print(f"  [{codigo}] {e['nombre']}: {url}")
        if codigo >= 400:
            fallos.append(f"{e['nombre']}: {url} -> HTTP {codigo}")
    return fallos


def limpiar() -> None:
    for path in (DIR_DOCS, PATH_JSON):
        if os.path.isdir(path):
            shutil.rmtree(path)
            print(f"  [-] {os.path.relpath(path, RAIZ)}/")
        elif os.path.isfile(path):
            os.remove(path)
            print(f"  [-] {os.path.relpath(path, RAIZ)}")


def ayuda() -> None:
    print(__doc__)


def main(argv: list[str]) -> int:
    if "--help" in argv or "-h" in argv:
        ayuda()
        return 0
    if "--clean" in argv:
        limpiar()
        return 0
    entradas = construir_entradas()
    errores = validar(entradas)
    if "--check-links" in argv:
        fallos = verificar_links(entradas)
        if fallos:
            print("[CHECK-LINKS] links rotos:")
            for f in fallos:
                print(f"  [!] {f}")
            return 1
        print(f"[CHECK-LINKS] OK: {len(entradas)} referencias vivas.")
        return 0
    if "--check" in argv:
        if errores:
            print("[CHECK] inconsistencias detectadas:")
            for err in errores:
                print(f"  [!] {err}")
            return 1
        print(f"[CHECK] OK: {len(entradas)} módulos sincronizados "
              f"(config ↔ README).")
        return 0
    if errores:
        print("[!] Advertencias (se genera igual):")
        for err in errores:
            print(f"  [!] {err}")
    generar(entradas)
    print(f"\n[OK] {len(entradas)} módulos generados en web/.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
