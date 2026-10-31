"""Synthetic tests of the actual C++ lambdas embedded in the ESPHome package."""
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest
import yaml

ROOT = Path(__file__).resolve().parents[1]

class ConfigLoader(yaml.SafeLoader):
    pass

ConfigLoader.add_constructor('!lambda', lambda loader, node: loader.construct_scalar(node))

class ProtocolTests(unittest.TestCase):
    def test_synthetic_roundtrip_uses_real_firmware_lambdas(self):
        package = ROOT / 'packages/eyocean.yaml'
        self.assertTrue(package.exists(), 'Reusable EYOCEAN package is missing')
        data = yaml.load(package.read_text(), Loader=ConfigLoader)
        decode = data['remote_receiver']['on_raw']['then'][0]['lambda']
        script = next(s for s in data['script'] if s['id'] == 'send_command')
        encode = script['then'][0]['if']['then'][0]['remote_transmitter.transmit_raw']['code']
        encode = encode.replace('${remote_id}', '0x1234').replace('${xor_key}', '0x56')
        source = r'''
#include <cassert>
#include <cstdint>
#include <vector>
#include <cstdio>
#define id(x) x
#define ESP_LOGI(...) ((void)0)
static uint32_t millis() { return 100; }
bool has_decoded = false;
uint16_t decoded_remote_id = 0;
uint8_t decoded_xor_key = 0, decoded_command = 0;
uint32_t decoded_count = 0, decoded_ms = 0;
std::vector<int32_t> encode(int command) {
''' + encode + '\n}\nvoid decode(const std::vector<int32_t>& x) {\n' + decode + r'''
}
int main() {
    const auto raw = encode(0x51);
    assert(raw.size() == 66);
    assert(raw[0] == 250 && raw[1] == -6250);
    uint32_t frame = 0;
    for (unsigned i=2; i<raw.size(); i+=2) {
        const bool one = raw[i] == 750;
        assert(raw[i] == (one ? 750 : 250));
        assert(raw[i+1] == (one ? -250 : -750));
        frame = (frame << 1) | one;
    }
    assert(frame == 0x12345107U);  // Explicitly synthetic identity/key.
    for (int cmd : {0x51, 0x5B, 0x5A, 0x49, 0x41, 0x4D}) {
        has_decoded = false;
        decode(encode(cmd));
        assert(has_decoded);
        assert(decoded_remote_id == 0x1234 && decoded_xor_key == 0x56);
        assert(decoded_command == cmd && decoded_ms == 100);
    }
    assert(decoded_count == 6);
    has_decoded = false;
    decode(encode(0x00));  // Unknown commands are not candidates.
    assert(!has_decoded);
    decode({250, -750});  // Truncated data is ignored.
    assert(!has_decoded);
    auto broken = encode(0x51);
    broken[2] = 10000;
    decode(broken);
    assert(!has_decoded);
    auto wrong_polarity = encode(0x51);
    wrong_polarity[3] = 750;
    decode(wrong_polarity);
    assert(!has_decoded);
    auto noisy = encode(0x5B);
    noisy.insert(noisy.begin(), {100, -100, 100, -10000});
    decode(noisy);
    assert(has_decoded && decoded_command == 0x5B);
    assert(decoded_count == 7);
    std::puts("Synthetic roundtrip (six commands), noise and malformed-frame checks passed");
}
'''
        self.assertIsNotNone(shutil.which('g++'), 'Install g++ to run protocol tests')
        with tempfile.TemporaryDirectory(prefix='eyocean-test-') as temp:
            cpp, exe = Path(temp)/'protocol.cpp', Path(temp)/'protocol'
            cpp.write_text(source)
            subprocess.run(['g++', '-std=c++17', '-Wall', '-Wextra', '-Werror', str(cpp), '-o', str(exe)], check=True)
            subprocess.run([str(exe)], check=True)

if __name__ == '__main__':
    unittest.main()
