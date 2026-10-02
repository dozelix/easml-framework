"""Progreso de campaña (juego por turnos v1.0.0.0-alpha).

Persiste en lab_data/progreso.json, separado de la arena: Reset Arena
(--clean) nunca borra el progreso y Reset Progreso nunca toca la arena.
"""

import json
import os
import sys

_DIR_RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _DIR_RAIZ not in sys.path:
    sys.path.insert(0, _DIR_RAIZ)

from modulos.common.paths import find_lab_data_dir  # noqa: E402


def _ruta() -> str:
    return os.path.join(find_lab_data_dir(), "progreso.json")


def vacio() -> dict:
    return {
        "heroe": "",        # nombre elegido por el jugador
        "tutorial_visto": False,
        "escenas": {},      # slug -> ["setup", "simular", "defensa"]
        "minijefe": {},     # slug -> {"ok": bool, "cien": bool}
        "megajefe": {},     # mundo CIA -> bool
        "sombra": [],       # slugs reclutados (minijefe al 100%)
        "panteon": {},      # mundo CIA -> True (avalancha superada)
        "dlc": False,       # módulos avanzados activados
        "anim": True,       # animaciones (off en hardware corto)
    }


def cargar() -> dict:
    p = vacio()
    try:
        with open(_ruta(), "r", encoding="utf-8") as f:
            data = json.load(f)
        if isinstance(data, dict):
            for k in p:
                if k in data:
                    p[k] = data[k]
    except (OSError, ValueError):
        pass
    return p


def guardar(p: dict) -> None:
    os.makedirs(find_lab_data_dir(), exist_ok=True)
    tmp = _ruta() + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(p, f, ensure_ascii=False, indent=2)
    os.replace(tmp, _ruta())


def reset() -> None:
    if os.path.isfile(_ruta()):
        os.remove(_ruta())


def marcar_escena(p: dict, slug: str, escena: str) -> None:
    hechas = set(p["escenas"].get(slug, []))
    hechas.add(escena)
    p["escenas"][slug] = sorted(hechas)


def registrar_minijefe(p: dict, slug: str, aprobado: bool,
                       pistas: int, fallos: int,
                       correctas: int, total: int) -> bool:
    """Registra el minijefe (quiz del capítulo). Retorna True si es 100%."""
    cien = (aprobado and pistas == 0 and fallos == 0
            and total > 0 and correctas == total)
    anterior = p["minijefe"].get(slug, {})
    p["minijefe"][slug] = {
        "ok": anterior.get("ok", False) or aprobado,
        "cien": anterior.get("cien", False) or cien,
    }
    if cien and slug not in p["sombra"]:
        p["sombra"].append(slug)
    return cien and not anterior.get("cien", False)


def registrar_megajefe(p: dict, mundo: str) -> None:
    p["megajefe"][mundo] = True


def es_primera_vez(p: dict) -> bool:
    """True si nunca se vio el tutorial ni se venció nada."""
    return not p.get("tutorial_visto", False) and not p.get("minijefe")


def siguiente_capitulo(p: dict, campana: list[str]) -> str:
    for slug in campana:
        if not p["minijefe"].get(slug, {}).get("ok"):
            return slug
    return campana[-1]
