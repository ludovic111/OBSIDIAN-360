#!/usr/bin/env python3
"""Validate prerequisites and disassemble already acquired kernel files locally.

Does not access Xbox hardware, install packages, or repeat downloads. Failed
stages are recorded; output is published only after the command succeeds.
"""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
IMAGE = 'obsidian360-toolchain:bookworm'
SYMBOLS = ('xenos_enable', 'xenos_update', 'xenos_pci_probe', 'dma_alloc_attrs', 'dma_direct_alloc', 'xenon_ipi_send_mask', 'xenon_cause_IPI', 'iic_unmask', 'xenon_pci_ecam_map_bus')


def run(args, timeout=60):
    try:
        p = subprocess.run(args, capture_output=True, text=True, timeout=timeout)
        return {'returncode': p.returncode, 'stdout': p.stdout, 'stderr': p.stderr}
    except (OSError, subprocess.TimeoutExpired) as error:
        return {'returncode': None, 'stdout': '', 'stderr': str(error)}


def save(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    pending = path.with_name(path.name + '.pending')
    pending.write_text(text)
    pending.replace(path)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--disassemble', action='store_true')
    parser.add_argument('--symbol', action='append', help='Limit disassembly to named functions; repeat as needed.')
    args = parser.parse_args()
    result = {'ready': False, 'checks': {}, 'actions': []}
    checks = result['checks']
    binary = ROOT / '.local/binaries/vmlinux-6.18.11-xenon'
    provenance = ROOT / 'evidence/2026-10-01/binary-audit/remote-provenance.txt'
    if not binary.is_file() or not provenance.is_file():
        checks['binary'] = {'ok': False, 'reason': 'Acquired kernel or its remote hash is absent.'}
    else:
        expected = next((line.split()[0] for line in provenance.read_text().splitlines() if line.endswith('/build/vmlinux')), None)
        data = binary.read_bytes()
        digest = hashlib.sha256(data).hexdigest()
        elf64be_ppc = data[:6] == b'\x7fELF\x02\x02' and int.from_bytes(data[18:20], 'big') == 21
        checks['binary'] = {'ok': digest == expected and elf64be_ppc, 'sha256': digest, 'elf64_big_endian_powerpc': elf64be_ppc}
    checks['docker_cli'] = {'ok': shutil.which('docker') is not None}
    if checks['docker_cli']['ok']:
        server = run(['docker', 'info', '--format', '{{.OSType}} {{.Architecture}}'], 15)
        checks['docker_server'] = {'ok': server['returncode'] == 0, **server}
        if checks['docker_server']['ok']:
            image = run(['docker', 'image', 'inspect', IMAGE, '--format', '{{.Id}}'], 15)
            checks['toolchain_image'] = {'ok': image['returncode'] == 0, **image}
            if checks['toolchain_image']['ok']:
                formats = run(['docker', 'run', '--rm', '--network', 'none', IMAGE, 'objdump', '-i'])
                checks['powerpc64_support'] = {'ok': formats['returncode'] == 0 and 'elf64-powerpc' in formats['stdout'], **formats}
    result['ready'] = bool(checks.get('powerpc64_support', {}).get('ok')) and all(c['ok'] for c in checks.values())
    if result['ready'] and args.disassemble:
        for symbol in (args.symbol or SYMBOLS):
            command = ['docker', 'run', '--rm', '--network', 'none', '--mount', f'type=bind,source={binary.parent},target=/input,readonly', IMAGE, 'objdump', '-d', '--disassemble=' + symbol, '/input/' + binary.name]
            output = run(command)
            ok = output['returncode'] == 0 and f'<{symbol}>:' in output['stdout']
            action = {'symbol': symbol, 'ok': ok, 'returncode': output['returncode'], 'stderr': output['stderr']}
            if ok:
                target = args.output.parent / (symbol + '.asm')
                save(target, output['stdout'])
                action.update(file=target.name, sha256=hashlib.sha256(target.read_bytes()).hexdigest())
            result['actions'].append(action)
        result['ready'] = result['ready'] and all(action['ok'] for action in result['actions'])
    save(args.output, json.dumps(result, indent=2) + '\n')
    if not result['ready']:
        print('Audit prerequisites incomplete; details saved. No download or hardware action restarted.')
        return 2
    print('Kernel hash, ELF architecture and toolchain verified.' + (' Disassembly saved.' if args.disassemble else ''))
    return 0


if __name__ == '__main__':
    sys.exit(main())
