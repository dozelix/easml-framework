"""Combate por turnos v1.0.0.0-alpha (lógica pura, testeable sin Flet).

Héroe (analista) vs Bicho (malware). HP del héroe = % de archivos sanos en
la arena; HP del enemigo = 100 - daño verificado. Todo daño exige mejora
real en directorio_pruebas/ (anti-trampa): sin verificación no hay daño.

El runner real (subprocess) lo inyecta la GUI; los tests usan stubs.
"""

import os
import random
import sys

_DIR_RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _DIR_RAIZ not in sys.path:
    sys.path.insert(0, _DIR_RAIZ)

from core.lab_setup import GENERATOR_MAP  # noqa: E402
from modulos.common.paths import resolve_lab_paths  # noqa: E402
from modulos.common.utils import hash_file  # noqa: E402

DEBILIDADES = {
    "trojan": "Ingenuidad: disfrazado, pero firma conocida. ATACAR rinde +5.",
    "keylogger": "Ruido: deja keylog.log. ANALIZAR siempre lo encuentra.",
    "steganography": "Peso: la imagen crece al ocultar. Compara tamaños.",
    "backdoor": "Persistencia: busca .reg/.bat y config C2.",
    "dns_tunneling": "Volumen: miles de consultas raras en el log.",
    "fileless": "Huellas: scripts fileless_sim_*.py residuales.",
    "rootkit": "Lista oculta: process_list.txt no cuadra.",
    "supply_chain": "Hash distinto: verifica dependencias (SCA).",
    "ransomware": "Extensión .locked + nota de rescate. Aísla y restaura.",
    "wiper": "Sin rescate: la única defensa es copia previa (Setup).",
    "worm": "Nodos shareA/B/C: corta la red, limpia uno por uno.",
    "cryptominer": "CPU al 100%: config minero + stats delatan.",
    "logic_bomb": "Condición oculta: marker json + trigger.",
    "botnet": "Manada: muchos nodos, un C2. Filtra el centro.",
}

BONUS_DEBILIDAD = {"trojan", "worm", "ransomware"}


def medir_sanos() -> tuple[int, int]:
    """Retorna (sanos, total) comparando arena contra samples."""
    rutas = resolve_lab_paths()
    sanos = 0
    total = 0
    for nombre in GENERATOR_MAP:
        total += 1
        arena = os.path.join(rutas["lab_dir"], nombre)
        muestra = os.path.join(rutas["samples_dir"], nombre)
        if (os.path.isfile(arena) and os.path.isfile(muestra)
                and hash_file(arena) == hash_file(muestra)):
            sanos += 1
    return sanos, total


class Combate:
    """Estado de un combate. `ejecutar` corre amenaza/defensa/setup reales."""

    def __init__(self, slug: str, rng: random.Random | None = None):
        self.slug = slug
        self.rng = rng or random.Random()
        self.enemigo_hp = 100
        self.turno = 0
        self.analizado = False
        self.terminado: str | None = None  # None | "victoria" | "derrota" | "captura" | "huida"
        self.bitacora: list[str] = []

    @property
    def heroe_hp(self) -> int:
        sanos, total = medir_sanos()
        return round(sanos / total * 100) if total else 0

    def _registrar(self, linea: str) -> None:
        self.bitacora.append(linea)

    def atacar(self, ejecutar_defensa) -> int:
        """Ejecuta la defensa real. Daño 25 si restaura, 5 si no."""
        _s0, _t = medir_sanos()
        sanos_antes = _s0
        ok = ejecutar_defensa()
        sanos_despues, _t = medir_sanos()
        mejora = sanos_despues - sanos_antes
        dano = 25 if (ok and mejora > 0) else 5
        if self.slug in BONUS_DEBILIDAD and self.analizado:
            dano += 5
        self.enemigo_hp = max(0, self.enemigo_hp - dano)
        self._registrar(
            f"[ATACAR] Defensa {'restauró ' + str(mejora) + ' archivos' if mejora > 0 else 'sin restauración'}: -{dano} HP.")
        self._chequear_fin()
        return dano

    def analizar(self) -> str:
        """Escanea la arena (gratis 1 vez por combate con bonus)."""
        sanos, total = medir_sanos()
        bonus = ""
        if not self.analizado:
            self.analizado = True
            bonus = " (próximo ATACAR +5 si explotas su debilidad)"
        pista = DEBILIDADES.get(self.slug, "Observa la arena y deduce.")
        texto = (f"[ANALIZAR] Integridad {sanos}/{total}. "
                 f"Debilidad: {pista}{bonus}")
        self._registrar(texto)
        return texto

    def parchar(self, ejecutar_setup) -> int:
        """Re-despliega samples sanos. Cura héroe, -10 al enemigo."""
        ejecutar_setup()
        self.enemigo_hp = max(0, self.enemigo_hp - 10)
        self._registrar("[PARCHEAR] Arena restaurada desde samples: -10 HP rival.")
        self._chequear_fin()
        return self.heroe_hp

    def capturar(self) -> bool:
        """Solo con rival <20% HP y héroe >=50%. Éxito 70%."""
        if self.enemigo_hp >= 20 or self.heroe_hp < 50:
            self._registrar("[CAPTURAR] Falló: debilítalo bajo 20% y mantén tu integridad sobre 50%.")
            return False
        exito = self.rng.random() < 0.70
        if exito:
            self.terminado = "captura"
            self._registrar("[CAPTURAR] Purificado: el bicho se une como SOMBRA.")
        else:
            self._registrar("[CAPTURAR] Se resistió... sigue debilitándolo.")
        return exito

    def turno_enemigo(self, ejecutar_amenaza) -> None:
        """El bicho contraataca con su script real."""
        if self.terminado:
            return
        self.turno += 1
        ejecutar_amenaza()
        self._registrar(f"[TURNO {self.turno}] El bicho ataca la arena...")
        if self.heroe_hp <= 0:
            self.terminado = "derrota"
            self._registrar("[DERROTA] Arena totalmente corrupta. Resetea y reintenta.")

    def _chequear_fin(self) -> None:
        if self.enemigo_hp <= 0 and not self.terminado:
            self.terminado = "victoria"
            self._registrar("[VICTORIA] Bicho neutralizado. Reclama tu minijefe en JUEGO.")
