"""Combate por turnos: daño verificado y captura (combate-turnos)."""

import os
import random
import shutil
import unittest

_REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


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

    def test_analizar_parchar_y_captura(self):
        from app.combate import Combate
        c = Combate("trojan")
        texto = c.analizar()
        self.assertIn("Debilidad", texto)
        self.assertTrue(c.analizado)
        c.enemigo_hp = 50
        c.parchar(lambda: True)
        self.assertEqual(c.enemigo_hp, 40)
        # Captura exige rival <20 y héroe >=50
        self.assertFalse(c.capturar())
        # semilla 1 -> 0.134 < 0.70: captura exitosa
        c2 = Combate("trojan", rng=random.Random(1))
        c2.enemigo_hp = 10
        self.assertTrue(c2.capturar())
        self.assertEqual(c2.terminado, "captura")

    def test_derrota_con_arena_destruida(self):
        from app.combate import Combate
        c = Combate("trojan")

        def _arrasar():
            for f in os.listdir(self.paths.lab_dir):
                os.remove(os.path.join(self.paths.lab_dir, f))
            return True

        c.turno_enemigo(_arrasar)
        self.assertEqual(c.terminado, "derrota")

    def test_vista_combate_existe(self):
        from gui_flet.views import vista_combate
        v = vista_combate("trojan", 100, 80, ["[TURNO 1] hola"], None)
        self.assertIsNotNone(v)


if __name__ == "__main__":
    unittest.main()
