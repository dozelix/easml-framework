"""Progreso de campaña: persistencia separada de la arena (menu-mapa)."""

import os
import unittest

_REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class ProgresoTests(unittest.TestCase):
    def setUp(self):
        os.environ["EASML_HOME"] = os.path.join(_REPO_ROOT, ".tmp-progreso")
        os.makedirs(os.environ["EASML_HOME"], exist_ok=True)

    def tearDown(self):
        import shutil
        shutil.rmtree(os.environ["EASML_HOME"], ignore_errors=True)
        del os.environ["EASML_HOME"]

    def test_ciclo_minijefe_cien_desbloquea_sombra(self):
        from app import progreso as PG
        p = PG.cargar()
        self.assertFalse(p["dlc"])
        PG.marcar_escena(p, "trojan", "simular")
        self.assertIn("simular", p["escenas"]["trojan"])
        nuevo = PG.registrar_minijefe(p, "trojan", True, 0, 0, 3, 3)
        self.assertTrue(nuevo)
        self.assertIn("trojan", p["sombra"])
        # Repetir el 100% no duplica ni re-reporta como nuevo
        self.assertFalse(PG.registrar_minijefe(p, "trojan", True, 0, 0, 3, 3))
        self.assertEqual(p["sombra"].count("trojan"), 1)
        # Aprobado con pistas no es 100%
        self.assertFalse(PG.registrar_minijefe(p, "worm", True, 1, 0, 2, 2))
        self.assertNotIn("worm", p["sombra"])
        self.assertTrue(p["minijefe"]["worm"]["ok"])
        PG.guardar(p)
        p2 = PG.cargar()
        self.assertEqual(p2["minijefe"]["trojan"]["cien"], True)

    def test_primera_vez_y_heroe(self):
        from app import progreso as PG
        p = PG.cargar()
        self.assertTrue(PG.es_primera_vez(p))
        self.assertEqual(p["heroe"], "")
        p["heroe"] = "NOVA"
        p["tutorial_visto"] = True
        PG.guardar(p)
        self.assertFalse(PG.es_primera_vez(PG.cargar()))

    def test_recursos_completos(self):
        from app.recursos import verificar
        self.assertEqual(verificar(), [])

    def test_reset_no_toca_arena(self):
        from app import progreso as PG
        p = PG.cargar()
        PG.marcar_escena(p, "trojan", "setup")
        PG.guardar(p)
        PG.reset()
        p2 = PG.cargar()
        self.assertEqual(p2["escenas"], {})

    def test_siguiente_capitulo(self):
        from app import progreso as PG
        from app.config import orden_campana
        p = PG.cargar()
        camp = orden_campana()
        self.assertEqual(PG.siguiente_capitulo(p, camp), "trojan")
        PG.registrar_minijefe(p, "trojan", True, 0, 1, 2, 3)
        self.assertEqual(PG.siguiente_capitulo(p, camp), camp[1])


if __name__ == "__main__":
    unittest.main()
