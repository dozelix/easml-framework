---
title: 'Gobernanza CIA/CIS'
description: 'Qué pilar rompe cada amenaza y qué control la mitiga'
---

Cada módulo impacta un pilar de la **Tríada CIA** y se mitiga con un **Control CIS**. La GUI muestra ambos en el header de cada módulo.

## Tríada CIA

* **Confidencialidad:** keylogger, steganography, backdoor, dns_tunneling.
* **Integridad:** trojan, rootkit, fileless, supply_chain.
* **Disponibilidad:** ransomware, wiper, worm, botnet, logic_bomb, cryptominer.

## Matriz de módulos

| # | Módulo | Pilar CIA | Control CIS |
|---|---|---|---|
| 10 | [fileless](/modulos/fileless/) | Integridad | CIS 2 — Inventario de Activos |
| 03 | [keylogger](/modulos/keylogger/) | Confidencialidad | CIS 3 — Protección de Datos |
| 09 | [steganography](/modulos/steganography/) | Confidencialidad | CIS 3 — Protección de Datos |
| 06 | [backdoor](/modulos/backdoor/) | Confidencialidad | CIS 4 — Seguridad de Dispositivos |
| 05 | [trojan](/modulos/trojan/) | Integridad | CIS 7 — Protección Email/Web |
| 11 | [logic_bomb](/modulos/logic_bomb/) | Disponibilidad | CIS 7 — Protección Email/Web |
| 07 | [rootkit](/modulos/rootkit/) | Integridad | CIS 8 — Auditoría de Cuentas |
| 12 | [cryptominer](/modulos/cryptominer/) | Disponibilidad | CIS 8 — Auditoría de Cuentas |
| 02 | [wiper](/modulos/wiper/) | Disponibilidad | CIS 10 — Copias de Seguridad |
| 01 | [ransomware](/modulos/ransomware/) | Disponibilidad | CIS 11 — Recuperación de Datos |
| 04 | [worm](/modulos/worm/) | Disponibilidad | CIS 13 — Monitoreo y Defensa de Red |
| 08 | [botnet](/modulos/botnet/) | Disponibilidad | CIS 13 — Monitoreo y Defensa de Red |
| 14 | [dns_tunneling](/modulos/dns_tunneling/) | Confidencialidad | CIS 13 — Monitoreo y Defensa de Red |
| 13 | [supply_chain](/modulos/supply_chain/) | Integridad | CIS 15 — Seguridad de Servidores |

Fuente de verdad: `app/config.py` (`MODULOS`, `NOMBRES_DEFENSA`). Si agregas un módulo, sigue la [guía](/nuevo-modulo/).
