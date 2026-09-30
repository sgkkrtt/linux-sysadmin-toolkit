import contextlib
import hashlib
import io
from pathlib import Path
import shutil
import tarfile
import tempfile
import unittest
from unittest.mock import patch
from sysadmin_toolkit.__main__ import backup, disk_report, main


class ToolkitTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.source = self.root / 'data'
        self.dest = self.root / 'archives'
        self.source.mkdir()
        self.dest.mkdir()
        (self.source / 'hello.txt').write_text('bonjour\n')

    def test_simulation_writes_nothing(self):
        self.assertEqual(backup(self.source, self.dest)['mode'], 'dry-run')
        self.assertEqual(list(self.dest.iterdir()), [])

    def test_archive_content_checksum_permissions_and_unique_names(self):
        first = backup(self.source, self.dest, True)
        archive = Path(first['archive'])
        self.assertEqual(archive.stat().st_mode & 0o777, 0o600)
        self.assertEqual(first['sha256'], hashlib.sha256(archive.read_bytes()).hexdigest())
        checksum = archive.with_suffix('.gz.sha256')
        self.assertEqual(checksum.stat().st_mode & 0o777, 0o600)
        self.assertEqual(checksum.read_text(), first['sha256'] + '  ' + archive.name + '\n')
        with tarfile.open(archive) as tar:
            self.assertEqual(tar.extractfile('data/hello.txt').read(), b'bonjour\n')
        self.assertNotEqual(first['archive'], backup(self.source, self.dest, True)['archive'])

    def test_nested_destination_refused(self):
        nested = self.source / 'nested'
        nested.mkdir()
        with self.assertRaises(ValueError):
            backup(self.source, nested, True)
        self.assertEqual(list(nested.iterdir()), [])

    def test_root_and_same_directory_refused(self):
        for source, dest in [('/', self.dest), (self.source, self.source)]:
            with self.assertRaises(ValueError):
                backup(source, dest)

    def test_missing_destination_refused(self):
        with self.assertRaises(FileNotFoundError):
            backup(self.source, self.root / 'missing')

    def test_symlinks_and_fifo_excluded(self):
        import os
        (self.source / 'link').symlink_to('/etc/passwd')
        (self.source / 'directory-link').symlink_to(self.dest, target_is_directory=True)
        os.mkfifo(self.source / 'fifo')
        result = backup(self.source, self.dest, True)
        with tarfile.open(result['archive']) as tar:
            self.assertEqual(set(tar.getnames()), {'data', 'data/hello.txt'})

    def test_failed_archive_is_removed(self):
        with patch('tarfile.TarFile.add', side_effect=OSError('lecture impossible')):
            with self.assertRaises(OSError):
                backup(self.source, self.dest, True)
        self.assertEqual(list(self.dest.iterdir()), [])

    @patch('shutil.disk_usage', return_value=shutil._ntuple_diskusage(100, 85, 15))
    def test_disk_threshold_boundary(self, usage):
        self.assertTrue(disk_report(self.source, 85)['alert'])
        self.assertFalse(disk_report(self.source, 86)['alert'])
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(main(['disk', '--threshold', '85']), 1)
            self.assertEqual(main(['disk', '--threshold', '86']), 0)

    def test_invalid_threshold_and_missing_path_exit_two(self):
        with contextlib.redirect_stderr(io.StringIO()):
            self.assertEqual(main(['disk', '--threshold', '101']), 2)
            self.assertEqual(main(['disk', '--path', str(self.root / 'missing')]), 2)

    def test_inventory_json(self):
        import json
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            self.assertEqual(main(['inventory']), 0)
        self.assertIn('kernel', json.loads(output.getvalue()))


if __name__ == '__main__':
    unittest.main()
