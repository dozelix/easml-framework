"""Configuración y base de datos de módulos para la GUI y laboratorio."""

# Ordenado por número de control CIS (ascendente). Múltiples módulos del mismo
# CIS van en orden alfabético dentro del grupo.

MODULOS = [
    ("10", "fileless",        "fileless", "Integridad", "CIS 2 — Inventario de Activos", 
     "https://en.wikipedia.org/wiki/Fileless_malware"),

    ("03", "keylogger",       "keylogger", "Confidencialidad", "CIS 3 — Proteccion de Datos", 
     "https://attack.mitre.org/techniques/T1056/001/"),

    ("09", "steganography",   "steganography", "Confidencialidad", "CIS 3 — Proteccion de Datos", 
     "https://en.wikipedia.org/wiki/Steganography"),

    ("06", "backdoor",        "backdoor", "Confidencialidad", "CIS 4 — Seguridad de Dispositivos", 
     "https://en.wikipedia.org/wiki/Backdoor_(computing)"),

    ("05", "trojan",          "trojan", "Integridad", "CIS 7 — Proteccion Email/Web", 
     "https://en.wikipedia.org/wiki/Trojan_horse_(computing)"),

    ("11", "logic_bomb",      "logic_bomb", "Disponibilidad", "CIS 7 — Proteccion Email/Web", 
     "https://es.wikipedia.org/wiki/Bomba_l%C3%B3gica"),

    ("07", "rootkit",         "rootkit", "Integridad", "CIS 8 — Auditoria de Cuentas", 
     "https://es.wikipedia.org/wiki/Rootkit"),

    ("12", "cryptominer",     "cryptominer", "Disponibilidad", "CIS 8 — Auditoria de Cuentas", 
     "https://en.wikipedia.org/wiki/Cryptojacking"),

    ("02", "wiper",           "wiper", "Disponibilidad", "CIS 10 — Copias de Seguridad", 
     "https://attack.mitre.org/techniques/T1485/"),

    ("01", "ransomware",      "ransomware", "Disponibilidad", "CIS 11 — Recuperacion de Datos", 
     "https://es.wikipedia.org/wiki/Ransomware"),

    ("04", "worm",            "worm", "Disponibilidad", "CIS 13 — Monitoreo y Defensa de Red", 
     "https://es.wikipedia.org/wiki/Gusano_inform%C3%A1tico"),

    ("08", "botnet",          "botnet", "Disponibilidad", "CIS 13 — Monitoreo y Defensa de Red", 
     "https://en.wikipedia.org/wiki/Botnet"),

    ("14", "dns_tunneling",   "dns_tunneling", "Confidencialidad", "CIS 13 — Monitoreo y Defensa de Red", 
     "https://attack.mitre.org/techniques/T1071/004/"),

    ("13", "supply_chain",    "supply_chain", "Integridad", "CIS 15 — Seguridad de Servidores", 
     "https://en.wikipedia.org/wiki/Supply_chain_attack"),
]

NOMBRES_DEFENSA = {
    "01": "Respuesta a Incidentes",
    "02": "Auditoria de Integridad",
    "03": "Cazador de Amenazas",
    "04": "Monitoreo de Red",
    "05": "Inspeccion de Contenido",
    "06": "Auditoria de Persistencia",
    "07": "Monitoreo del Kernel Ganchos",
    "08": "Mitigacion DDoS Filtros",
    "09": "Analisis Esteganografico",
    "10": "Inspeccion de Memoria Volatile",
    "11": "Analisis de Desencadenadores",
    "12": "Monitoreo de Recursos CPU",
    "13": "Verificacion de Dependencias SCA",
    "14": "Deteccion de Anomalias DNS",
}

# ── Capa juego (v1.0.0.0-alpha): metadatos por slug ──────────────────────────
# MODULOS y NOMBRES_DEFENSA se conservan intactos (compat con GUI, wiki y
# scripts). Todo lo nuevo vive aquí, llaveado por slug.

# Núcleo activo por defecto (efecto visible en <1 min) vs DLC bloqueado
# (técnicas de red/memoria/kernel, más abstractas).
CORE_SLUGS = frozenset({
    "trojan", "keylogger", "ransomware", "wiper", "worm", "cryptominer",
})

# Alias con aura por era punk + salón de combate. Subtítulo ES en README.
META_POR_SLUG = {
    "trojan": {"alias": "EISENHORSE", "era": "oxido", "dificultad": 1,
               "orden": 0, "salon": "Garaje"},
    "keylogger": {"alias": "GHOSTTAPE", "era": "cinta", "dificultad": 1,
                  "orden": 1, "salon": "Cabina VHS"},
    "steganography": {"alias": "HAGAKURE", "era": "neon", "dificultad": 2,
                      "orden": 2, "salon": "Callejón Tinta"},
    "backdoor": {"alias": "ROSTTOR", "era": "oxido", "dificultad": 2,
                 "orden": 3, "salon": "Sótano de Calderas"},
    "dns_tunneling": {"alias": "SUBDOMINUS", "era": "nube", "dificultad": 3,
                      "orden": 4, "salon": "Alcantarilla de Fibra"},
    "fileless": {"alias": "INANIS", "era": "nube", "dificultad": 3,
                 "orden": 5, "salon": "Cámara de Niebla"},
    "rootkit": {"alias": "RING_ZERO", "era": "cinta", "dificultad": 3,
                "orden": 6, "salon": "Sótano CRT"},
    "supply_chain": {"alias": "VENENUM CHAIN", "era": "nube", "dificultad": 3,
                     "orden": 7, "salon": "Almacén Fantasma"},
    "ransomware": {"alias": "RUSTLOCK", "era": "neon", "dificultad": 2,
                   "orden": 8, "salon": "Casa de Empeño"},
    "wiper": {"alias": "HEADCRASH", "era": "cinta", "dificultad": 1,
              "orden": 9, "salon": "Sala Magnética"},
    "worm": {"alias": "GRAUWURM", "era": "oxido", "dificultad": 2,
             "orden": 10, "salon": "Túnel Remachado"},
    "cryptominer": {"alias": "FUMUS FORGE", "era": "nube", "dificultad": 2,
                    "orden": 11, "salon": "Fundición Solar Rota"},
    "logic_bomb": {"alias": "ZEITZUNDER", "era": "oxido", "dificultad": 2,
                   "orden": 12, "salon": "Relojería"},
    "botnet": {"alias": "KAGE ARMY", "era": "neon", "dificultad": 3,
               "orden": 13, "salon": "Azotea Antenas"},
}

_NUM_POR_SLUG = {nombre: num for num, nombre, _s, _cia, _cis, _url in MODULOS}

MUNDO_POR_SLUG = {nombre: cia for _num, nombre, _s, cia, _cis, _url in MODULOS}


def arena_de(slug: str) -> str:
    """Arena del capítulo: garaje tutorial, resto por mundo CIA."""
    if slug == "trojan":
        return "garaje"
    return MUNDO_POR_SLUG[slug].lower()


def slug_de(indice: int) -> str:
    """Slug del módulo en la posición `indice` de MODULOS."""
    return MODULOS[indice][1]


def es_core(slug: str) -> bool:
    """True si el módulo viene activo por defecto (no DLC)."""
    return slug in CORE_SLUGS


def defensa_arch(slug: str) -> str:
    """Nombre de archivo de defensa (ej: respuesta_a_incidentes.py)."""
    num = _NUM_POR_SLUG[slug]
    return NOMBRES_DEFENSA[num].lower().replace(" ", "_") + ".py"


def meta(slug: str) -> dict:
    """Metadatos de juego (alias, era, dificultad, orden, salón)."""
    return META_POR_SLUG[slug]


def orden_campana() -> list[str]:
    """Slugs en orden pedagógico (tutorial trojan primero)."""
    return sorted(META_POR_SLUG, key=lambda s: META_POR_SLUG[s]["orden"])


def modulos_por_mundo() -> dict[str, list[str]]:
    """Slugs agrupados por pilar CIA, en orden de campaña."""
    mundos: dict[str, list[str]] = {}
    for _num, nombre, _s, cia, _cis, _url in MODULOS:
        mundos.setdefault(cia, []).append(nombre)
    for lista in mundos.values():
        lista.sort(key=lambda s: META_POR_SLUG[s]["orden"])
    return mundos