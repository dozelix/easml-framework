import os
import unittest

from core.common import find_lab_dir
from modulos.common.paths import resolve_lab_paths


class FindLabDirTests(unittest.TestCase):
    def test_returns_repo_lab_directory_from_workspace_root(self):
        repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.assertEqual(find_lab_dir(repo_root), os.path.join(repo_root, 'directorio_pruebas'))

    def test_returns_repo_lab_directory_from_nested_path(self):
        repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        nested = os.path.join(repo_root, 'modulos', '01_ransomware')
        self.assertEqual(find_lab_dir(nested), os.path.join(repo_root, 'directorio_pruebas'))

    def test_resolve_lab_paths_uses_lab_data_for_generated_artifacts(self):
        repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        paths = resolve_lab_paths(repo_root)
        self.assertEqual(paths['repo_root'], repo_root)
        self.assertEqual(paths['lab_dir'], os.path.join(repo_root, 'directorio_pruebas'))
        self.assertEqual(paths['lab_data_dir'], os.path.join(repo_root, 'lab_data'))
        self.assertEqual(paths['logs_dir'], os.path.join(repo_root, 'lab_data', 'logs'))
        self.assertEqual(paths['output_dir'], os.path.join(repo_root, 'lab_data', 'output'))


if __name__ == '__main__':
    unittest.main()
