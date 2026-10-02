#!/usr/bin/env python3
"""Synthetic sense decoding only; never opens a device."""
import importlib.util
from pathlib import Path
import unittest

path = Path(__file__).resolve().parents[2] / 'tools/optical-ready.py'
spec = importlib.util.spec_from_file_location('optical_ready', path)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class SenseTests(unittest.TestCase):
    def test_empty(self):
        self.assertIsNone(module.decode_sense(b''))

    def test_fixed_absent_medium(self):
        result = module.decode_sense(bytes.fromhex('700002000000000a000000003a0000000000'))
        self.assertEqual(result, {'response': 0x70, 'key': 2, 'asc': 0x3a, 'ascq': 0})

    def test_descriptor(self):
        self.assertEqual(module.decode_sense(bytes.fromhex('72020401')),
                         {'response': 0x72, 'key': 2, 'asc': 4, 'ascq': 1})

    def test_truncations(self):
        data = bytes.fromhex('700002000000000a000000003a00')
        for length in range(1, 14):
            self.assertTrue(module.decode_sense(data[:length])['unrecognized_or_truncated'])

    def test_unknown_response(self):
        self.assertTrue(module.decode_sense(b'\x01\x02\x03\x04')['unrecognized_or_truncated'])


if __name__ == '__main__':
    unittest.main()
