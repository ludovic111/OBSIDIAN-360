#!/usr/bin/env python3
"""Exercise the built CLI using original synthetic data, never a game binary."""
import argparse
import hashlib
import json
from pathlib import Path
import struct
import subprocess
import tempfile


def sample():
    b = bytearray(0x340)
    struct.pack_into('>6I', b, 0, 0x58455832, 1, 0x300, 0, 0x80, 2)
    struct.pack_into('>4I', b, 24, 0x10100, 0x82001000, 0x3ff, 0x40)
    struct.pack_into('>IHH', b, 0x40, 8, 1, 2)
    struct.pack_into('>2I', b, 0x80, 0x184, 4096)
    marker = b'SYNTHETIC_OPAQUE_MARKER'
    b[0x88:0x88 + len(marker)] = marker
    b[0x300:] = b'Z' * 0x40
    return b


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--binary', required=True, type=Path)
    args = p.parse_args()
    binary = args.binary.resolve()
    results = []
    with tempfile.TemporaryDirectory(prefix='obsidian-xex-cli-') as tmp:
        path = Path(tmp)/'PRIVATE_NAME_SENTINEL.fixture'
        base = sample()
        cases = [('valid', base, 0), ('truncated', base[:100], 2)]
        bad_magic = base.copy(); bad_magic[:4] = b'XEX1'
        cases.append(('unsupported_xex1', bad_magic, 2))
        bad_length = base.copy(); struct.pack_into('>I', bad_length, 0x40, 0)
        cases.append(('zero_variable_length', bad_length, 2))
        alias = base.copy(); struct.pack_into('>I', alias, 36, 0x88)
        cases.append(('security_alias', alias, 2))
        for name, data, expected in cases:
            path.write_bytes(data)
            before = hashlib.sha256(data).hexdigest()
            r = subprocess.run([str(binary), str(path)], capture_output=True, text=True, timeout=5)
            assert r.returncode == expected, (name, r.returncode, r.stderr)
            assert hashlib.sha256(path.read_bytes()).hexdigest() == before, name
            assert 'PRIVATE_NAME_SENTINEL' not in r.stdout + r.stderr
            assert 'SYNTHETIC_OPAQUE_MARKER' not in r.stdout + r.stderr
            if expected == 0:
                report = json.loads(r.stdout)
                assert report['format'] == 'XEX2'
                assert report['signature_verified'] is False
                assert report['file_size'] == len(data)
                assert report['file_format'] == {'encryption_type': 1, 'compression_type': 2}
                assert report['optional_headers'][0]['value'] == 0x82001000
                assert not r.stderr
            else:
                assert not r.stdout and r.stderr.startswith('xex-inspect: ')
            results.append({'case': name, 'code': r.returncode, 'input_unchanged': True})
        for name, argv in [('directory', [tmp]), ('missing_file', [str(Path(tmp)/'absent')]),
                           ('missing_argument', []), ('extra_argument', [str(path), 'extra'])]:
            r = subprocess.run([str(binary), *argv], capture_output=True, text=True, timeout=5)
            assert r.returncode == 2 and not r.stdout, name
            results.append({'case': name, 'code': r.returncode})
    print(json.dumps({'scope': 'Synthetic CLI checks only; no authentic XEX file used',
                      'results': results}, indent=2))


if __name__ == '__main__':
    main()
