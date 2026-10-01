#!/usr/bin/env python3
"""Compile the real candidate driver with host resource/SMC stubs and ASan.

Tests ownership, error propagation and LED bit mapping; does not emulate IRQs,
SMP interleavings, physical LEDs or the real device framework.
"""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import tempfile

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--source', type=Path, required=True)
parser.add_argument('--output', type=Path, required=True)
args = parser.parse_args()
base = Path(__file__).resolve().parent
raw = args.source.read_text()
source = '\n'.join(line for line in raw.splitlines() if not line.startswith('#include'))
report = {'source_sha256': hashlib.sha256(args.source.read_bytes()).hexdigest(),
          'scope': 'Real candidate driver, mocked kernel resources and SMC; no hardware',
          'cases': []}
with tempfile.TemporaryDirectory(prefix='obsidian-led-test-') as temp:
    folder = Path(temp)
    c = folder/'driver.c'
    c.write_text((base/'led-lifecycle-stubs.h').read_text()+'\n'+source+'\n'+
                 (base/'led-lifecycle-main.c').read_text())
    binary = folder/'driver-test'
    p = subprocess.run(['clang', '-std=gnu11', '-O1', '-g', '-Wall', '-Wextra',
                        '-Werror', '-fsanitize=address,undefined', str(c), '-o', str(binary)],
                       capture_output=True, text=True)
    report['compile'] = {'returncode': p.returncode, 'diagnostics': p.stderr}
    if p.returncode == 0:
        cases = [('success', 0), ('driver', 0), ('device', 0), ('defer', 0)]
        cases += [('alloc', i) for i in range(9)] + [('led', i) for i in range(8)]
        for kind, index in cases:
            p = subprocess.run([str(binary), kind, str(index)], capture_output=True, text=True)
            report['cases'].append({'kind': kind, 'index': index, 'returncode': p.returncode,
                                    'stdout': p.stdout.strip(), 'diagnostics': p.stderr})
report['passed'] = report['compile']['returncode'] == 0 and len(report['cases']) == 21 and all(
    case['returncode'] == 0 for case in report['cases'])
args.output.parent.mkdir(parents=True, exist_ok=True)
args.output.write_text(json.dumps(report, indent=2)+'\n')
print('LED lifecycle tests: '+('21 passed' if report['passed'] else 'FAILED; inspect report'))
raise SystemExit(0 if report['passed'] else 1)
