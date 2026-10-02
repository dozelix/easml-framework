"""Capa juego en app/config.py: slugs, core/DLC, orden, alias (config-slug)."""

import os
import unittest

_REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class ConfigJuegoTests(unittest.TestCase):
    def test_meta_cubre_los_14_slugs(self):
        from app.config import MODULOS, META_POR_SLUG
        slugs = [m[1] for m in MODULOS]
        self.assertEqual(len(slugs), 14)
        self.assertEqual(set(slugs), set(META_POR_SLUG))

    def test_core_6_dlc_8(self):
        from app.config import CORE_SLUGS, es_core, orden_campana
        self.assertEqual(len(CORE_SLUGS), 6)
        self.assertEqual(
            sorted(CORE_SLUGS),
            ["cryptominer", "keylogger", "ransomware", "trojan", "wiper", "worm"],
        )
        self.assertTrue(es_core("trojan"))
        self.assertFalse(es_core("rootkit"))
        campana = orden_campana()
        self.assertEqual(len(campana), 14)
        self.assertEqual(campana[0], "trojan")  # tutorial primero
        self.assertEqual(len(set(campana)), 14)

    def test_alias_sin_numeros_y_mundo_coherente(self):
        from app.config import MODULOS, META_POR_SLUG
        for _num, nombre, _s, cia, _cis, _url in MODULOS:
            m = META_POR_SLUG[nombre]
            self.assertTrue(m["alias"] and len(m["alias"]) >= 3)
            self.assertNotIn("CIS", m["alias"])
            self.assertIn(m["era"], ("oxido", "cinta", "neon", "nube"))
            self.assertIn(m["dificultad"], (1, 2, 3))
            self.assertTrue(m["salon"])
        self.assertEqual(META_POR_SLUG["trojan"]["alias"], "EISENHORSE")

    def test_defensa_arch_existe_en_disco(self):
        from app.config import MODULOS, defensa_arch
        for _num, nombre, _script, _cia, _cis, _url in MODULOS:
            arch = defensa_arch(nombre)
            self.assertTrue(arch.endswith(".py"), arch)
            ruta = os.path.join(_REPO_ROOT, "modulos", nombre, arch)
            self.assertTrue(os.path.isfile(ruta), f"falta {ruta}")

    def test_mundos_suman_14(self):
        from app.config import modulos_por_mundo
        mundos = modulos_por_mundo()
        self.assertEqual(
            set(mundos),
            {"Confidencialidad", "Integridad", "Disponibilidad"},
        )
        total = sum(len(v) for v in mundos.values())
        self.assertEqual(total, 14)


if __name__ == "__main__":
    unittest.main()
