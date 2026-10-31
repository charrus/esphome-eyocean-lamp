"""Validate real examples in an isolated tree with disposable test secrets."""
import base64
from pathlib import Path
import secrets
import shutil
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
EXAMPLES = ('t-embed-cc1101.yaml', 'esp32s3-cc1101.yaml', 't-embed-cc1101-with-proxy.yaml')

class ExampleTests(unittest.TestCase):
    def test_examples_validate_with_esphome(self):
        self.assertIsNotNone(shutil.which('esphome'), 'Install requirements-dev.txt first')
        with tempfile.TemporaryDirectory(prefix='eyocean-config-') as temp:
            tree = Path(temp)
            for directory in ('examples', 'packages'):
                shutil.copytree(ROOT/directory, tree/directory, ignore=shutil.ignore_patterns('secrets.yaml', '.esphome'))
            key = base64.b64encode(secrets.token_bytes(32)).decode()
            (tree/'examples/secrets.yaml').write_text(
                'wifi_ssid: "SYNTHETIC_TEST_SSID"\n'
                'wifi_password: "SYNTHETIC_TEST_PASSWORD"\n'
                f'api_key: "{key}"\n'
            )
            for example in EXAMPLES:
                with self.subTest(example=example):
                    result = subprocess.run(['esphome', 'config', str(tree/'examples'/example)], text=True, capture_output=True)
                    self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

if __name__ == '__main__':
    unittest.main()
