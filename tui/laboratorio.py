"""Módulo de laboratorio interactivo con dificultad y desafíos."""

import os
import sys
import time
import json
import random
from dataclasses import dataclass, field
from typing import Optional

_DIR_RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _DIR_RAIZ)

from tui.config import MODULOS, NOMBRES_DEFENSA


@dataclass
class Puntuacion:
    """Resultado de una sesión de desafío."""
    modulo: str
    dificultad: str
    pistas_usadas: int = 0
    intentos_fallidos: int = 0
    tiempo_segundos: float = 0.0
    puntos: int = 0
    aprobado: bool = False


@dataclass
class Desafio:
    """Un desafío individual dentro de un módulo."""
    pregunta: str
    opciones: list[str]
    respuesta_correcta: int
    pista: str
    explicacion: str


# ── Base de desafíos por módulo ─────────────────────────────────────────────

DESAFIOS_POR_MODULO: dict[str, list[Desafio]] = {
    "ransomware": [
        Desafio(
            pregunta="¿Qué algoritmo cifra la clave simétrica en un ransomware híbrido?",
            opciones=["AES-256", "RSA (asimétrico)", "MD5", "SHA-256"],
            respuesta_correcta=1,
            pista="Piensa en un algoritmo que use pareja de claves pública/privada.",
            explicacion="RSA cifra la clave simétrica (AES) con la clave pública del atacante. Solo la privada descifra."
        ),
        Desafio(
            pregunta="¿Qué comando elimina las sombras de volumen en Windows?",
            opciones=["del /s", "vssadmin delete shadows /all /quiet", "format C:", "taskkill /f"],
            respuesta_correcta=1,
            pista="Es un comando de Windows que administra servicios de volumen.",
            explicacion="vssadmin elimina las copias de sombra (Volume Shadow Copy), impidiendo la recuperación desde backups del sistema."
        ),
        Desafio(
            pregunta="¿Qué kill switch detuvo WannaCry?",
            opciones=["Un firewall de Microsoft", "Un dominio DNS registrado por MalwareTech", "Un antivirus", "Un parche de SMB"],
            respuesta_correcta=1,
            pista="El investigador registró algo en internet que el malware verificaba antes de cifrar.",
            explicacion="WannaCry verificaba si existía un dominio específico. Al registrarlo, se activaba el kill switch y el malware se detenía."
        ),
    ],
    "wiper": [
        Desafio(
            pregunta="¿Qué diferencia principal tiene un wiper respecto a un ransomware?",
            opciones=["Usa cifrado más fuerte", "Destruye datos irrecuperablemente", "Pide un rescate", "Se propaga por red"],
            respuesta_correcta=1,
            pista="No hay posibilidad de recuperación... a diferencia del ransomware.",
            explicacion="Un wiper sobrescribe o elimina datos de forma permanente. No hay clave de descifrado porque no cifra — destruye."
        ),
        Desafio(
            pregunta="¿Qué famoso ataque fue disfrazado de ransomware pero era un wiper?",
            opciones=["WannaCry", "NotPetya", "CryptoLocker", "Ryuk"],
            respuesta_correcta=1,
            pista="Afectó masivamente a Ucrania en 2017 y causó $10B+ en daños globales.",
            explicacion="NotPetya usó EternalBlue como WannaCry pero su objetivo real era la destrucción, no el rescate."
        ),
    ],
    "keylogger": [
        Desafio(
            pregunta="¿Qué API de Windows captura teclas globalmente en un keylogger?",
            opciones=["FindFirstFile", "GetAsyncKeyState", "CreateProcess", "RegSetValue"],
            respuesta_correcta=1,
            pista="Es una API que verifica el estado del teclado de forma asíncrona.",
            explicacion="GetAsyncKeyState permite a un proceso verificar si una tecla está presionada, incluso si no tiene foco."
        ),
        Desafio(
            pregunta="¿Qué控 (control) CIS se relaciona con la detección de keyloggers?",
            opciones=["CIS 1: Hardware assets", "CIS 8: Audit Log Management", "CIS 14: Wireless", "CIS 2: Software assets"],
            respuesta_correcta=1,
            pista="Un keylogger genera registros de actividad que deben ser monitoreados.",
            explicacion="CIS 8 establece que los logs de auditoría son esenciales para detectar actividad sospechosa como keyloggers."
        ),
    ],
    "worm": [
        Desafio(
            pregunta="¿Qué vulnerabilidad explotó EternalBlue?",
            opciones=["HTTP/HTTPS", "SMBv1 (MS17-010)", "SSH", "DNS"],
            respuesta_correcta=1,
            pista="Es un protocolo de compartición de archivos de Windows.",
            explicacion="EternalBlue explotaba una vulnerabilidad en SMBv1 que permitía ejecución remota de código sin autenticación."
        ),
    ],
    "trojan": [
        Desafio(
            pregunta="¿Qué hace un troyano diferente a un virus?",
            opciones=["Se auto-replica", "Se disfraza de software legítimo", "Cifra archivos", "Ataca la red"],
            respuesta_correcta=1,
            pista="Su nombre viene de la estrategia griega del caballo de Troya.",
            explicacion="Un troyano se presenta como programa útil o legítimo mientras ejecuta funciones maliciosas ocultas."
        ),
    ],
    "backdoor": [
        Desafio(
            pregunta="¿Qué permite una backdoor al atacante?",
            opciones=["Cifrar archivos remotamente", "Acceso remoto continuo y no autorizado", "Eliminar antivirus", "Generar tráfico DDoS"],
            respuesta_correcta=1,
            pista="Es una puerta trasera... literally.",
            explicacion="Una backdoor proporciona al atacante acceso persistente al sistema comprometido, evitando mecanismos de autenticación normales."
        ),
    ],
    "rootkit": [
        Desafio(
            pregunta="¿Qué técnica usa un rootkit para ocultar procesos?",
            opciones=["Cifrado de disco", "Filtrado de API (DKOM, hooking)", "Eliminación de archivos", "Encriptación de red"],
            respuesta_correcta=1,
            pista="Intercepta las llamadas del sistema operativo antes de que lleguen a las herramientas de monitoreo.",
            explicacion="DKOM (Direct Kernel Object Manipulation) y hooking interceptan APIs del SO para ocultar archivos, procesos y conexiones."
        ),
    ],
    "botnet": [
        Desafio(
            pregunta="¿Qué protocolo usaba Mirai para su canal C2?",
            opciones=["IRC", "HTTP", "DNS", "SMTP"],
            respuesta_correcta=0,
            pista="Es uno de los protocolos de chat más antiguos de internet.",
            explicacion="Mirai usaba IRC (Internet Relay Chat) para el Command & Control, permitiendo que los bots se conectaran a canales específicos."
        ),
        Desafio(
            pregunta="¿Cuánto tráfico generó Mirai contra Dyn DNS?",
            opciones=["100 Mbps", "1.2 Tbps", "50 Gbps", "10 Mbps"],
            respuesta_correcta=1,
            pista="Fue suficiente para tumbar servicios de Twitter, Netflix y Reddit.",
            explicacion="El ataque DDoS de Mirai contra Dyn en 2016 alcanzó 1.2 Tbps, uno de los ataques DDoS más grandes de la historia."
        ),
    ],
    "steganography": [
        Desafio(
            pregunta="¿Qué capa del modelo OSI se relaciona con esteganografía en red?",
            opciones=["Física", "Transporte", "Aplicación", "Enlace"],
            respuesta_correcta=2,
            pista="Es donde operan HTTP, DNS y otros protocolos de nivel superior.",
            explicacion="La esteganografía en red oculta datos dentro de protocolos de aplicación (HTTP headers, DNS queries, ICMP payloads)."
        ),
    ],
    "fileless": [
        Desafio(
            pregunta="¿Por qué son difíciles de detectar los ataques fileless?",
            opciones=["Usan cifrado fuerte", "No escriben archivos en disco", "Son muy rápidos", "Atacan el hardware"],
            respuesta_correcta=1,
            pista="Operan directamente en memoria RAM.",
            explicacion="Al ejecutar todo en memoria (PowerShell, WMI, registry), no hay archivos que el antivirus pueda escanear en disco."
        ),
    ],
    "logic_bomb": [
        Desafio(
            pregunta="¿Qué activa típicamente una lógica bomb?",
            opciones=["Un antivirus", "Una condición lógica o fecha específica", "Un ataque de red", "Una actualización"],
            respuesta_correcta=1,
            pista="Es una condición programada... como una fecha o un evento específico.",
            explicacion="Una lógica bomb se activa cuando se cumple una condición predefinida: fecha específica, acción del usuario, o estado del sistema."
        ),
    ],
    "cryptominer": [
        Desafio(
            pregunta="¿Qué recurso del sistema consume principalmente un cryptominer?",
            opciones=["Disco duro", "CPU/GPU", "RAM", "Ancho de banda"],
            respuesta_correcta=1,
            pista="La minería requiere cálculos matemáticos intensivos.",
            explicacion="Los cryptominers utilizan CPU y/o GPU para resolver algoritmos de proof-of-work, consumiendo electricidad y generando calor excesivo."
        ),
    ],
    "supply_chain": [
        Desafio(
            pregunta="¿Qué ataque de supply chain comprometió SolarWinds?",
            opciones=["Phishing masivo", "Inyección de código en actualizaciones legítimas", "DDoS", "Ransomware"],
            respuesta_correcta=1,
            pista="El malware venía incluido en una actualización oficial del software.",
            explicacion="Los atacantes insertaron código malicioso en las actualizaciones de Orion, que se distribuyeron a 18.000+ organizaciones."
        ),
    ],
    "dns_tunneling": [
        Desafio(
            pregunta="¿Qué tipo de registros DNS se usan comúnmente para DNS tunneling?",
            opciones=["A y AAAA", "TXT y CNAME", "SOA y NS", "MX y PTR"],
            respuesta_correcta=1,
            pista="TXT puede contener texto arbitrario, y CNAME redirige dominios.",
            explicacion="Los registros TXT permiten almacenar datos codificados, y CNAME puede usarse para exfiltración. Ambos son ideales para tunneling."
        ),
    ],
}

# ── Dificultades ────────────────────────────────────────────────────────────

CONFIG_DIFICULTADES = {
    "facil": {
        "nombre": "Fácil",
        "descripcion": "Muestra pistas, permite reintentos, sin penalización",
        "max_pistas": 999,
        "max_intentos": 999,
        "penalizacion_fallo": 0,
        "puntos_respuesta": 100,
        "bonus_sin_pista": 0,
    },
    "medio": {
        "nombre": "Medio",
        "descripcion": "3 pistas, 2 reintentos, -25 puntos por fallo",
        "max_pistas": 3,
        "max_intentos": 2,
        "penalizacion_fallo": 25,
        "puntos_respuesta": 100,
        "bonus_sin_pista": 50,
    },
    "dificil": {
        "nombre": "Difícil",
        "descripcion": "Sin pistas, 1 intento, -50 puntos por fallo",
        "max_pistas": 0,
        "max_intentos": 1,
        "penalizacion_fallo": 50,
        "puntos_respuesta": 100,
        "bonus_sin_pista": 100,
    },
}


class LaboratorioInteractivo:
    """Motor de desafíos interactivos con dificultad."""

    def __init__(self):
        self.dificultad: str = "facil"
        self.puntuaciones: list[Puntuacion] = []
        self.puntos_totales: int = 0
        self.desafios_completados: int = 0

    def obtener_config(self) -> dict:
        return CONFIG_DIFICULTADES[self.dificultad]

    def listar_modulos_disponibles(self) -> list[tuple[int, str, str]]:
        """Retorna lista de (índice, num_nombre, tiene_desafios)."""
        resultado = []
        for i, m in enumerate(MODULOS):
            num, nombre = m[0], m[1]
            clave = nombre
            tiene = clave in DESAFIOS_POR_MODULO
            resultado.append((i, nombre, tiene))
        return resultado

    def obtener_desafios(self, num_nombre: str) -> list[Desafio]:
        return DESAFIOS_POR_MODULO.get(num_nombre, [])

    def calcular_puntuacion(self, pistas_usadas: int, intentos_fallidos: int,
                            total_preguntas: int, correctas: int) -> int:
        config = self.obtener_config()
        base = correctas * config["puntos_respuesta"]
        penalizacion = intentos_fallidos * config["penalizacion_fallo"]
        bonus = 0
        if pistas_usadas == 0 and correctas == total_preguntas:
            bonus = config["bonus_sin_pista"] * correctas
        return max(0, base - penalizacion + bonus)

    def evaluar_respuesta(self, desafio: Desafio, respuesta: int,
                          pistas_usadas: int) -> tuple[bool, str]:
        config = self.obtener_config()
        if respuesta == desafio.respuesta_correcta:
            return True, desafio.explicacion
        else:
            if pistas_usadas < config["max_pistas"]:
                return False, f"❌ Incorrecto. Pista: {desafio.pista}"
            else:
                return False, f"❌ Incorrecto. La respuesta correcta era: {desafio.opciones[desafio.respuesta_correcta]}"

    def guardar_resultado(self, num_nombre: str, pistas: int, fallos: int,
                          tiempo: float, puntos: int, aprobado: bool):
        p = Puntuacion(
            modulo=num_nombre,
            dificultad=self.dificultad,
            pistas_usadas=pistas,
            intentos_fallidos=fallos,
            tiempo_segundos=tiempo,
            puntos=puntos,
            aprobado=aprobado,
        )
        self.puntuaciones.append(p)
        self.puntos_totales += puntos
        self.desafios_completados += 1

    def resumen_general(self) -> str:
        if not self.puntuaciones:
            return "No hay resultados aún."

        config = self.obtener_config()
        total = len(self.puntuaciones)
        aprobados = sum(1 for p in self.puntuaciones if p.aprobado)
        puntos_max = total * config["puntos_respuesta"]

        lineas = [
            f"📊 RESUMEN — Dificultad: {config['nombre']}",
            f"   Desafíos completados: {total}",
            f"   Aprobados: {aprobados}/{total} ({aprobados*100//total if total else 0}%)",
            f"   Puntos totales: {self.puntos_totales}/{puntos_max}",
            "",
        ]
        for p in self.puntuaciones:
            estado = "✅" if p.aprobado else "❌"
            lineas.append(f"   {estado} {p.modulo} — {p.puntos} pts — {p.tiempo_segundos:.1f}s")

        return "\n".join(lineas)
