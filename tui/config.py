"""Configuración y base de datos de módulos para la TUI."""

MODULOS = [
    ("01", "ransomware",      "ransomware", "Disponibilidad", "CIS 11 — Recuperacion de Datos", 
     "https://es.wikipedia.org/wiki/Ransomware"),
    
    ("02", "wiper",           "wiper", "Disponibilidad", "CIS 10 — Copias de Seguridad", 
     "https://www.redhat.com/es/topics/security/claves-para-protegerse-del-malware-wiper"),
    
    ("03", "keylogger",       "keylogger", "Confidencialidad", "CIS 3 — Proteccion de Datos", 
     "https://es.wikipedia.org/wiki/Capturador_de_teclado"),
    
    ("04", "worm",            "worm", "Disponibilidad", "CIS 13 — Monitoreo y Defensa de Red", 
     "https://es.wikipedia.org/wiki/Gusano_inform%C3%A1tico"),
    
    ("05", "trojan",          "trojan", "Integridad", "CIS 7 — Proteccion Email/Web", 
     "https://www.redhat.com/es/topics/security/what-is-a-trojan-horse"),
    
    ("06", "backdoor",        "backdoor", "Confidencialidad", "CIS 4 — Seguridad de Dispositivos", 
     "https://owasp.org/www-community/attacks/Backdoor"),
    
    ("07", "rootkit",         "rootkit", "Integridad", "CIS 8 — Auditoria de Cuentas", 
     "https://es.wikipedia.org/wiki/Rootkit"),
    
    ("08", "botnet",          "botnet", "Disponibilidad", "CIS 13 — Monitoreo y Defensa de Red", 
     "https://www.redhat.com/es/topics/security/what-is-a-botnet"),
    
    ("09", "steganography",   "steganography", "Confidencialidad", "CIS 3 — Proteccion de Datos", 
     "https://owasp.org/www-community/attacks/Steganography"),
    
    ("10", "fileless",        "fileless", "Integridad", "CIS 2 — Inventario de Activos", 
     "https://es.wikipedia.org/wiki/Malware_sin_ficheros"),
    
    ("11", "logic_bomb",      "logic_bomb", "Disponibilidad", "CIS 7 — Proteccion Email/Web", 
     "https://es.wikipedia.org/wiki/Bomba_l%C3%B3gica"),
    
    ("12", "cryptominer",     "cryptominer", "Disponibilidad", "CIS 8 — Auditoria de Cuentas", 
     "https://es.wikipedia.org/wiki/Criptominer%C3%ADa_maliciosa"),
    
    ("13", "supply_chain",    "supply_chain", "Integridad", "CIS 15 — Seguridad de Servidores", 
     "https://owasp.org/www-project-top-10-ci-cd-security-risks/CICD-SEC-02-Insecure-Software-Supply-Chain"),
    
    ("14", "dns_tunneling",   "dns_tunneling", "Confidencialidad", "CIS 13 — Monitoreo y Defensa de Red", 
     "https://infosecwriteups.com/dns-tunneling-exfiltration-owasp-46f5296839f2"),
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