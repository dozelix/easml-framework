"""Combate por turnos: daño verificado y captura (combate-turnos)."""

import os
import random
import shutil
import unittest
from importlib.util import find_spec

_REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

REQUIERE_FLET = find_spec("flet") is None


class CombateTests(unittest.TestCase):
    def setUp(self):
        os.environ["EASML_HOME"] = os.path.join(_REPO_ROOT, ".tmp-combate")
        if os.path.isdir(os.environ["EASML_HOME"]):
            shutil.rmtree(os.environ["EASML_HOME"])
        os.makedirs(os.environ["EASML_HOME"], exist_ok=True)
        from modulos.common.paths import ensure_lab_data_dirs
        from core.lab_setup import deploy_sandbox
        import io
        from contextlib import redirect_stdout
        self.paths = ensure_lab_data_dirs()
        with redirect_stdout(io.StringIO()):
            deploy_sandbox(self.paths)

    def tearDown(self):
        shutil.rmtree(os.environ["EASML_HOME"], ignore_errors=True)
        os.environ.pop("EASML_HOME", None)

    def _corromper(self, nombre="documento.txt"):
        with open(os.path.join(self.paths.lab_dir, nombre), "w") as f:
            f.write("CORRUPTO")

    def _restaurar(self, nombre="documento.txt"):
        shutil.copy2(os.path.join(self.paths.samples_dir, nombre),
                     os.path.join(self.paths.lab_dir, nombre))

    def test_hp_es_integridad_real(self):
        from app.combate import Combate, medir_sanos
        sanos, total = medir_sanos()
        self.assertEqual((sanos, total), (12, 12))
        c = Combate("trojan")
        self.assertEqual(c.heroe_hp, 100)
        self._corromper()
        self.assertEqual(c.heroe_hp, 92)

    def test_atacar_solo_dana_si_restaura(self):
        from app.combate import Combate
        self._corromper()
        c = Combate("trojan")
        c.atacar(lambda: (self._restaurar(), True)[1])
        self.assertEqual(c.enemigo_hp, 75)
        c2 = Combate("trojan")
        c2.atacar(lambda: False)
        self.assertEqual(c2.enemigo_hp, 95)

    def test_analizar_parchar_y_guardia(self):
        from app.combate import Combate, medir_sanos
        c = Combate("trojan")
        texto = c.analizar()
        self.assertIn("Debilidad", texto)
        self.assertTrue(c.analizado)
        c.enemigo_hp = 50
        c.parchar(lambda: True)
        self.assertEqual(c.enemigo_hp, 40)
        # Guardia: 1.º siempre entra, gasta turno enemigo a la mitad
        g = Combate("trojan", rng=random.Random(1))
        self.assertTrue(g.guardia())
        self.assertTrue(g.protegido)
        self._corromper()
        self._corromper("notas.txt")
        g.turno_enemigo(lambda: True)
        sanos, _t = medir_sanos()
        self.assertEqual(sanos, 11)  # mitad de 2 restaurados
        self.assertFalse(g.protegido)
        # Abuso: 2.ª seguida solo 50% (semilla 0 -> 0.844 falla)
        g2 = Combate("trojan", rng=random.Random(0))
        self.assertTrue(g2.guardia())
        self.assertFalse(g2.guardia())
        # Otro movimiento resetea la racha
        g2.analizar()
        self.assertEqual(g2.guardias_seguidas, 0)

    def test_rival_a_cero_es_captura_automatica(self):
        from app.combate import Combate
        c = Combate("trojan")
        c.enemigo_hp = 5
        c.atacar(lambda: (self._corromper("notas.txt"), False)[1])
        self.assertEqual(c.terminado, "captura")

    def test_derrota_con_arena_destruida(self):
        from app.combate import Combate
        c = Combate("trojan")

        def _arrasar():
            for f in os.listdir(self.paths.lab_dir):
                os.remove(os.path.join(self.paths.lab_dir, f))
            return True

        c.turno_enemigo(_arrasar)
        self.assertEqual(c.terminado, "derrota")

    @unittest.skipIf(REQUIERE_FLET, "flet no instalado")
    def test_vista_combate_existe(self):
        from gui_flet.views import vista_combate
        v = vista_combate("trojan", 100, 80, ["[TURNO 1] hola"], None)
        self.assertIsNotNone(v)
        for submenu in ("ataques", "mochila", "equipo"):
            self.assertIsNotNone(vista_combate(
                "trojan", 100, 80, ["hola"], None, submenu=submenu,
                mochila={"copia": 1, "antivirus": 0, "senuelo": 2},
                sombras=["trojan"]))

    def test_mochila_items(self):
        from app.combate import Combate, medir_sanos
        from app.mochila import gastar, hay, inventario, premiar
        p = {"mochila": {}}
        inv = inventario(p)
        self.assertEqual((inv["copia"], inv["antivirus"], inv["senuelo"]),
                         (2, 2, 2))
        self.assertTrue(hay(p, "copia"))
        self.assertTrue(gastar(p, "copia"))
        self.assertEqual(inventario(p)["copia"], 1)
        premiar(p)
        self.assertEqual(inventario(p)["copia"], 2)
        # Antivirus potencia el próximo ataque
        c = Combate("trojan")
        self._corromper()
        c.activar_antivirus()
        c.atacar(lambda: (self._restaurar(), True)[1])
        self.assertEqual(c.enemigo_hp, 100 - 25 - 15)
        self.assertFalse(c.antivirus)
        # Señuelo roba el contraataque (la arena queda intacta)
        c2 = Combate("trojan")
        c2.activar_senuelo()
        c2.turno_enemigo(lambda: (self._corromper(), True)[1])
        self.assertEqual(medir_sanos()[0], 12)
        self.assertEqual(c2.turno, 1)
        # Equipo suma +5 por aliada
        c3 = Combate("trojan", aliadas=2)
        self._corromper()
        c3.atacar(lambda: (self._restaurar(), True)[1])
        self.assertEqual(c3.enemigo_hp, 100 - 25 - 10)


if __name__ == "__main__":
    unittest.main()
