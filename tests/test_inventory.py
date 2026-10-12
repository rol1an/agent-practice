import importlib.util
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


SCRIPT = Path(__file__).resolve().parents[1] / 'skills/research-materials/scripts/inventory.py'
spec = importlib.util.spec_from_file_location('inventory', SCRIPT)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class InventoryTests(unittest.TestCase):
    def test_duplicates_are_reported_without_changing_originals(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / '原始数据').mkdir()
            (root / '原始数据/a.csv').write_bytes(b'time,value\n1,2\n')
            (root / 'copy.csv').write_bytes((root / '原始数据/a.csv').read_bytes())
            (root / 'different.csv').write_bytes(b'time,value\n1,3\n')
            before = {p.relative_to(root): (p.read_bytes(), p.stat().st_mtime_ns)
                      for p in root.rglob('*') if p.is_file()}
            report = module.inventory(root, True)
            self.assertEqual(report['file_count'], 3)
            self.assertEqual(len(report['byte_identical_groups']), 1)
            self.assertEqual(set(report['byte_identical_groups'][0]), {'copy.csv', '原始数据/a.csv'})
            after = {p.relative_to(root): (p.read_bytes(), p.stat().st_mtime_ns)
                     for p in root.rglob('*') if p.is_file()}
            self.assertEqual(before, after)

    def test_links_and_credential_files_are_not_read(self):
        with tempfile.TemporaryDirectory() as directory, tempfile.TemporaryDirectory() as external:
            root = Path(directory)
            (Path(external) / 'private.txt').write_text('OUTSIDE')
            (root / 'external').symlink_to(external, target_is_directory=True)
            (root / 'link.txt').symlink_to(Path(external) / 'private.txt')
            (root / '.env').write_text('SECRET')
            (root / 'credentials.json').write_text('SECRET')
            (root / 'a.txt').write_text('public')
            report = module.inventory(root, True)
            self.assertEqual([f['path'] for f in report['files']], ['a.txt'])
            self.assertEqual(len(report['skipped']), 4)

    def test_default_scan_does_not_hash_and_handles_empty_project(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.assertEqual(module.inventory(root)['file_count'], 0)
            (root / 'data.ibw').write_bytes(b'opaque binary')
            report = module.inventory(root)
            self.assertFalse(report['hashes_computed'])
            self.assertNotIn('sha256', report['files'][0])

    def test_invalid_or_symlink_root_fails(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            link = root / 'linked'
            link.symlink_to(root, target_is_directory=True)
            with self.assertRaises(ValueError):
                module.inventory(link)
            run = subprocess.run([sys.executable, str(SCRIPT), str(root / 'missing')],
                                 capture_output=True, text=True)
            self.assertNotEqual(run.returncode, 0)
            self.assertEqual(run.stdout, '')


if __name__ == '__main__':
    unittest.main()
