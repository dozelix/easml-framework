"""No-duplicación de rutas: mismo lab_dir sin importar el cwd (fix/rutas-duplicadas)."""

import os
import unittest

_REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class RutasDeterministasTests(unittest.TestCase):
    def test_mismo_lab_dir_desde_cualquier_cwd(self):
        import modulos.common.paths as P
        suelos = [
            _REPO_ROOT,
            os.path.join(_REPO_ROOT, 'modulos', 'worm'),
            os.path.join(_REPO_ROOT, 'core'),
        ]
        labs = set()
        for suelo in suelos:
            anterior = os.getcwd()
            try:
                os.chdir(suelo)
                labs.add(P.resolve_lab_paths()['lab_dir'])
                # find_lab_dir() sin args tampoco debe depender del cwd
                from modulos.common.utils import find_lab_dir
                labs.add(find_lab_dir())
            finally:
                os.chdir(anterior)
        self.assertEqual(len(labs), 1, f"lab_dir duplicado según cwd: {labs}")
        self.assertEqual(
            next(iter(labs)),
            os.path.join(_REPO_ROOT, 'directorio_pruebas'),
        )

    def test_logs_dentro_de_lab_data(self):
        from modulos.common.paths import resolve_lab_paths
        from modulos.common.utils import find_logs_dir
        rutas = resolve_lab_paths()
        self.assertEqual(
            rutas['logs_dir'],
            os.path.join(_REPO_ROOT, 'lab_data', 'logs'),
        )
        self.assertEqual(find_logs_dir(), rutas['logs_dir'])

    def test_write_log_no_crea_logs_huerfano(self):
        import shutil
        import tempfile
        from modulos.common import utils
        huerfano = os.path.join(_REPO_ROOT, 'logs')
        respaldo = None
        if os.path.isdir(huerfano):
            respaldo = tempfile.mkdtemp()
            for nombre in os.listdir(huerfano):
                src = os.path.join(huerfano, nombre)
                if os.path.isfile(src):
                    shutil.copy2(src, os.path.join(respaldo, nombre))
            shutil.rmtree(huerfano)
        try:
            utils.write_log("test_rutas_tmp", ["linea"])
            self.assertFalse(
                os.path.isdir(huerfano),
                "write_log recreó el directorio huérfano repo_root/logs/",
            )
            esperado = os.path.join(_REPO_ROOT, 'lab_data', 'logs', 'test_rutas_tmp.log')
            self.assertTrue(os.path.isfile(esperado), f"falta {esperado}")
        finally:
            for nombre in ('test_rutas_tmp.log',):
                cand = os.path.join(_REPO_ROOT, 'lab_data', 'logs', nombre)
                if os.path.isfile(cand):
                    os.remove(cand)
            if respaldo is not None:
                os.makedirs(huerfano, exist_ok=True)
                for nombre in os.listdir(respaldo):
                    shutil.copy2(os.path.join(respaldo, nombre),
                                os.path.join(huerfano, nombre))
                shutil.rmtree(respaldo)


if __name__ == '__main__':
    unittest.main()
