"""Mochila de combate: items consumibles (lógica pura, testeable).

- copia: restaura la arena desde samples (cura total, sin daño).
- antivirus: +15 al próximo ATACAR.
- senuelo: el rival pierde su próximo contraataque.
Usar un item gasta el turno, salvo el señuelo que lo roba.
"""

ITEMS = {
    "copia": {"nombre": "Copia de seguridad",
              "efecto": "Restaura toda la arena. Gasta el turno."},
    "antivirus": {"nombre": "Antivirus portátil",
                  "efecto": "+15 al próximo ATACAR. Gasta el turno."},
    "senuelo": {"nombre": "Señuelo",
                "efecto": "El rival pierde su contraataque."},
}

INICIAL = {"copia": 2, "antivirus": 2, "senuelo": 2}
TOPE = 9


def inventario(p: dict) -> dict:
    """Mochila del progreso (la crea con dotación inicial si falta)."""
    mochila = p.setdefault("mochila", dict(INICIAL))
    for clave, cantidad in INICIAL.items():
        mochila.setdefault(clave, cantidad)
    return mochila


def hay(p: dict, item: str) -> bool:
    return inventario(p).get(item, 0) > 0


def gastar(p: dict, item: str) -> bool:
    mochila = inventario(p)
    if mochila.get(item, 0) <= 0:
        return False
    mochila[item] -= 1
    return True


def premiar(p: dict) -> None:
    """+1 de cada item al vencer un minijefe (hasta el tope)."""
    mochila = inventario(p)
    for clave in INICIAL:
        mochila[clave] = min(TOPE, mochila.get(clave, 0) + 1)
