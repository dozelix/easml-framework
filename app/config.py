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
#
NOMBRES_DEFENSA_INTERACTIVO: dict[str, str] = {
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