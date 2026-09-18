#!/usr/bin/env python3
"""Audita el uso de la API Flet en gui_flet/ contra el Flet instalado.

Detecta la clase de error que ningún test headless atrapa: nombres, props y
métodos que no existen en la versión instalada (ej: page.update_async(),
eliminado en Flet 1.0). Requiere flet instalado (CI lo tiene vía requirements).

Verifica:
  1. Todo ft.Nombre existe en el paquete flet.
  2. Todo kwarg de ft.Clase(...) está en su firma (incluye enums y subclases).
  2b. Ningún ft.Image usa src="" (renderiza cartel rojo: usar visible=False).
  3. Todo método page.algo(...) existe en ft.Page (incluye heredados).
  4. Todo miembro ft.Enums.MIEMBRO existe (Icons, FontWeight, ...).

Uso:
    python scripts/auditar_flet.py          # audita, exit 1 si hay errores
    python scripts/auditar_flet.py --help   # ayuda

Limitación honesta: no verifica atributos de evento (e.control.value) ni
props asignadas post-construcción (dlg.open = ...). Eso se cubre con el
smoke --web y el checklist manual.
"""

import ast
import enum
import inspect
import os
import sys

_RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_DIR_FLET = os.path.join(_RAIZ, "gui_flet")
_ARCHIVOS_EXTRA = [os.path.join(_RAIZ, "flet_main.py")]


def ayuda() -> None:
    print(__doc__)


def _flet():
    try:
        import flet as ft
    except ImportError:
        print("[AUDIT] flet no instalado: imposible auditar (se omite).")
        return None
    return ft


class Visitante(ast.NodeVisitor):
    def __init__(self, ft, ruta: str):
        self.ft = ft
        self.ruta = ruta
        self.errores: list[str] = []

    def _pos(self, node: ast.AST) -> str:
        linea = getattr(node, "lineno", "?")
        return f"{os.path.relpath(self.ruta, _RAIZ)}:{linea}"

    def _resolver_ft(self, node: ast.AST):
        """Resuelve ft.A.B... al objeto real o None."""
        partes: list[str] = []
        actual = node
        while isinstance(actual, ast.Attribute):
            partes.append(actual.attr)
            actual = actual.value
        if not (isinstance(actual, ast.Name) and actual.id == "ft"):
            return None, None
        partes.reverse()
        obj = self.ft
        recorrido = ["ft"]
        for parte in partes:
            if not hasattr(obj, parte):
                return None, ".".join(recorrido + [parte])
            obj = getattr(obj, parte)
            recorrido.append(parte)
        return obj, None

    def visit_Attribute(self, node: ast.Attribute):
        # Caso 4: ft.Algo.MIEMBRO (el padre es el miembro, el valor es ft.Algo)
        if isinstance(node.value, ast.Attribute):
            base, faltante = self._resolver_ft(node.value)
            if faltante:
                self.errores.append(f"{self._pos(node)}: {faltante} no existe")
            elif base is not None and not inspect.isclass(base) \
                    and not inspect.ismodule(base):
                # Es una instancia/enum contenedor: el miembro debe existir
                if not hasattr(base, node.attr):
                    self.errores.append(
                        f"{self._pos(node)}: {type(base).__name__}."
                        f"{node.attr} no existe")
            elif inspect.isclass(base) and issubclass(base, enum.Enum):
                # Enums (FontWeight, ScrollMode, AppView, ...): miembro exacto
                if node.attr not in base.__members__:
                    self.errores.append(
                        f"{self._pos(node)}: {base.__name__}."
                        f"{node.attr} no es miembro")
        elif isinstance(node.value, ast.Name) and node.value.id == "ft":
            # Caso 1: ft.Nombre directo
            if not hasattr(self.ft, node.attr):
                self.errores.append(
                    f"{self._pos(node)}: ft.{node.attr} no existe")
        self.generic_visit(node)

    def visit_Call(self, node: ast.Call):
        func = node.func
        if isinstance(func, ast.Attribute):
            if isinstance(func.value, ast.Name) and func.value.id == "ft":
                # Caso ft.Clase(...): visit_Attribute ya reporta si falta
                obj = getattr(self.ft, func.attr, None)
                faltante = None
            else:
                obj, faltante = self._resolver_ft(func.value)
            if faltante:
                self.errores.append(f"{self._pos(node)}: {faltante} no existe")
            elif obj is not None and inspect.isclass(obj):
                # Caso 2: kwargs del constructor
                try:
                    firma = inspect.signature(obj.__init__)
                except (TypeError, ValueError):
                    firma = None
                if firma is not None:
                    params = firma.parameters
                    acepta_kwargs = any(
                        p.kind == inspect.Parameter.VAR_KEYWORD
                        for p in params.values())
                    if not acepta_kwargs:
                        for kw in node.keywords:
                            if kw.arg and kw.arg not in params:
                                self.errores.append(
                                    f"{self._pos(node)}: {obj.__name__}() "
                                    f"sin prop '{kw.arg}'")
                    # Caso 2b: valores que Flet rechaza al renderizar
                    # (pasan la firma pero rompen la ventana, ej: src="").
                    for kw in node.keywords:
                        if kw.arg == "src" and isinstance(kw.value, ast.Constant) \
                                and kw.value.value == "":
                            self.errores.append(
                                f"{self._pos(node)}: {obj.__name__}(src=\"\") "
                                f"renderiza cartel de error: usar visible=False")
            # Caso 3: page.metodo(...)
            if isinstance(func.value, ast.Name) and func.value.id == "page":
                if not hasattr(self.ft.Page, func.attr):
                    self.errores.append(
                        f"{self._pos(node)}: Page.{func.attr}() no existe")
        self.generic_visit(node)


def auditar_archivo(ft, ruta: str) -> list[str]:
    with open(ruta, "r", encoding="utf-8") as f:
        arbol = ast.parse(f.read(), filename=ruta)
    visitante = Visitante(ft, ruta)
    visitante.visit(arbol)
    return visitante.errores


def main(argv: list[str]) -> int:
    if "--help" in argv or "-h" in argv:
        ayuda()
        return 0
    ft = _flet()
    if ft is None:
        return 0  # sin flet no hay nada que auditar: no bloquear
    print(f"[AUDIT] contra flet {getattr(ft, '__version__', '?')}")
    rutas = sorted(
        os.path.join(_DIR_FLET, f) for f in os.listdir(_DIR_FLET)
        if f.endswith(".py"))
    rutas += [p for p in _ARCHIVOS_EXTRA if os.path.isfile(p)]
    errores: list[str] = []
    for ruta in rutas:
        errores.extend(auditar_archivo(ft, ruta))
    if errores:
        print(f"[AUDIT] {len(errores)} problema(s):")
        for err in errores:
            print(f"  [!] {err}")
        return 1
    print(f"[AUDIT] OK: {len(rutas)} archivos, API válida.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
