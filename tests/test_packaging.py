"""Packaging checks: fail closed before sharing examples publicly."""
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch
import yaml
from test_protocol import ConfigLoader

ROOT = Path(__file__).resolve().parents[1]

class PackagingTests(unittest.TestCase):
    def test_default_lamp_transmission_requires_opt_in_and_identity(self):
        data = yaml.load((ROOT/'packages/eyocean.yaml').read_text(), Loader=ConfigLoader)
        self.assertEqual(int(data['substitutions']['remote_id'], 0), 0)
        self.assertEqual(int(data['substitutions']['xor_key'], 0), 0)
        switch = next(s for s in data['switch'] if s['id'] == 'tx_enabled')
        self.assertEqual(switch['restore_mode'], 'ALWAYS_OFF')
        script = next(s for s in data['script'] if s['id'] == 'send_command')
        self.assertEqual(script['then'][0]['if']['condition']['lambda'], 'return id(tx_enabled).state && ${remote_id} != 0;')
        self.assertFalse(any(k in data for k in ('on_boot', 'interval')))

    def test_custom_recording_and_playback_are_absent(self):
        for path in (ROOT/'packages').glob('*.yaml'):
            text = path.read_text()
            for token in ('recorded_raw', 'recording_state', 'arm_recording', 'replay_recording', 'Record RF', 'Transmit recording'):
                self.assertNotIn(token, text)

    def test_ignored_private_secrets_are_accepted(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            subprocess.run(['git', 'init', '-q', str(root)], check=True)
            (root / '.gitignore').write_text('examples/secrets.yaml\n')
            (root / 'examples').mkdir()
            (root / 'examples/secrets.yaml').write_text('test_host: 192.168.1.2\n')
            subprocess.run(
                ['git', '-C', str(root), 'check-ignore', '-q', 'examples/secrets.yaml'],
                check=True,
            )
            with patch(__name__ + '.ROOT', root):
                self.test_examples_have_no_personal_identity_or_network_details()

    def test_tracked_secrets_are_rejected_even_when_ignored(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            subprocess.run(['git', 'init', '-q', str(root)], check=True)
            (root / '.gitignore').write_text('examples/secrets.yaml\n')
            (root / 'examples').mkdir()
            (root / 'examples/secrets.yaml').write_text('test_value: synthetic-only\n')
            subprocess.run(
                ['git', '-C', str(root), 'add', '-f', 'examples/secrets.yaml'],
                check=True,
            )
            with patch(__name__ + '.ROOT', root):
                with self.assertRaisesRegex(AssertionError, 'secrets.yaml must not be tracked'):
                    self.test_examples_have_no_personal_identity_or_network_details()

    def test_examples_have_no_personal_identity_or_network_details(self):
        tracked_paths = subprocess.run(
            ['git', '-C', str(ROOT), 'ls-files', '-z'],
            check=True, capture_output=True, text=True,
        ).stdout.split('\0')
        self.assertFalse(
            any(Path(path).name == 'secrets.yaml' for path in tracked_paths if path),
            'secrets.yaml must not be tracked',
        )
        for directory in ('examples', 'packages'):
            for path in (ROOT/directory).glob('*.yaml'):
                if path == ROOT / 'examples/secrets.yaml':
                    continue
                self.assertNotEqual(path.name, 'secrets.yaml')
                self.assertNotRegex(path.read_text(), r'\b(?:10\.\d+|172\.(?:1[6-9]|2\d|3[01])|192\.168)\.\d+\.\d+\b')

if __name__ == '__main__':
    unittest.main()
