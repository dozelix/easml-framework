import os
import subprocess
import sys
import unittest

_REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

MODULOS = [
    ("01_ransomware", "ransomware.py", "respuesta_a_incidentes.py"),
    ("02_wiper", "wiper.py", "auditoria_de_integridad.py"),
    ("03_keylogger", "keylogger.py", "cazador_de_amenazas.py"),
    ("04_worm", "worm.py", "monitoreo_de_red.py"),
    ("05_trojan", "trojan.py", "inspeccion_de_contenido.py"),
    ("06_backdoor", "backdoor.py", "auditoria_de_persistencia.py"),
    ("07_rootkit", "rootkit.py", "monitoreo_del_kernel_ganchos.py"),
    ("08_botnet", "botnet.py", "mitigacion_ddos_filtros.py"),
    ("09_steganography", "steganography.py", "analisis_esteganografico.py"),
    ("10_fileless", "fileless.py", "inspeccion_de_memoria_volatile.py"),
    ("11_logic_bomb", "logic_bomb.py", "analisis_de_desencadenadores.py"),
    ("12_cryptominer", "cryptominer.py", "monitoreo_de_recursos_cpu.py"),
    ("13_supply_chain", "supply_chain.py", "verificacion_de_dependencias_sca.py"),
    ("14_dns_tunneling", "dns_tunneling.py", "deteccion_de_anomalias_dns.py"),
]


def _run_script(relative_path, timeout=30):
    cmd = [sys.executable, os.path.join(_REPO_ROOT, relative_path), "--help"]
    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        timeout=timeout,
        cwd=_REPO_ROOT,
    )
    return result


class TestArchivosExistentes(unittest.TestCase):
    def test_lab_setup_exists(self):
        path = os.path.join(_REPO_ROOT, "core", "lab_setup.py")
        self.assertTrue(os.path.isfile(path), f"No existe: {path}")

    def test_tui_entry_exists(self):
        path = os.path.join(_REPO_ROOT, "tui.py")
        self.assertTrue(os.path.isfile(path), f"No existe: {path}")

    def test_tui_styles_exists(self):
        path = os.path.join(_REPO_ROOT, "tui", "styles.py")
        self.assertTrue(os.path.isfile(path), f"No existe: {path}")

    def test_common_utils_exists(self):
        path = os.path.join(_REPO_ROOT, "modulos", "common", "utils.py")
        self.assertTrue(os.path.isfile(path), f"No existe: {path}")

    def test_common_paths_exists(self):
        path = os.path.join(_REPO_ROOT, "modulos", "common", "paths.py")
        self.assertTrue(os.path.isfile(path), f"No existe: {path}")


class TestSimulacionHelp(unittest.TestCase):
    pass


class TestDefensaHelp(unittest.TestCase):
    pass


for _carpeta, _sim, _def in MODULOS:

    def _make_sim_test(carpeta, sim):
        def test(self):
            rel = os.path.join("modulos", carpeta, sim)
            result = _run_script(rel)
            self.assertEqual(
                result.returncode, 0,
                f"{sim} --help fallo (exit {result.returncode}):\n{result.stderr}"
            )
        return test

    def _make_def_test(carpeta, defensa):
        def test(self):
            rel = os.path.join("modulos", carpeta, defensa)
            result = _run_script(rel)
            self.assertEqual(
                result.returncode, 0,
                f"{defensa} --help fallo (exit {result.returncode}):\n{result.stderr}"
            )
        return test

    test_name_sim = f"test_{_carpeta}_simulacion"
    setattr(TestSimulacionHelp, test_name_sim, _make_sim_test(_carpeta, _sim))

    test_name_def = f"test_{_carpeta}_defensa"
    setattr(TestDefensaHelp, test_name_def, _make_def_test(_carpeta, _def))


class TestLabSetup(unittest.TestCase):
    def test_lab_setup_clean(self):
        cmd = [sys.executable, os.path.join(_REPO_ROOT, "core", "lab_setup.py"), "--clean"]
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=30,
            cwd=_REPO_ROOT,
        )
        self.assertEqual(
            result.returncode, 0,
            f"lab_setup.py --clean fallo (exit {result.returncode}):\n{result.stderr}"
        )


if __name__ == "__main__":
    unittest.main()
