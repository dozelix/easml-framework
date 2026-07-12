import os
import unittest

from core.common import find_lab_dir


class FindLabDirTests(unittest.TestCase):
    def test_returns_repo_lab_directory_from_workspace_root(self):
        repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.assertEqual(find_lab_dir(repo_root), os.path.join(repo_root, 'directorio_pruebas'))

    def test_returns_repo_lab_directory_from_nested_path(self):
        repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        nested = os.path.join(repo_root, 'modulos', '01_ransomware')
        self.assertEqual(find_lab_dir(nested), os.path.join(repo_root, 'directorio_pruebas'))


if __name__ == '__main__':
    unittest.main()
