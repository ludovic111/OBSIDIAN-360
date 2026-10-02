#!/usr/bin/env python3
"""Validate locally built kernel payloads and selected module metadata.

Does not boot or install anything. This is file validation, not hardware testing.
"""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--build', type=Path, required=True)
parser.add_argument('--output', type=Path, required=True)
parser.add_argument('--kernel-only', action='store_true',
                    help='Validate vmlinux and modules without requiring a boot image')
args = parser.parse_args()
root = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('kernel_elf', root/'tools/compare-kernel-images.py')
elf = importlib.util.module_from_spec(spec)
spec.loader.exec_module(elf)
release = (args.build/'include/config/kernel.release').read_text().strip()
report = {'release': release, 'artifacts': {}, 'modules': [], 'booted': False, 'deployed': False}
artifacts = ['vmlinux', 'System.map', 'Module.symvers', '.config']
if not args.kernel_only:
    artifacts.append('arch/powerpc/boot/zImage.xenon')
report['boot_image_checked'] = not args.kernel_only
for name in artifacts:
    data = (args.build/name).read_bytes()
    report['artifacts'][name] = {'bytes': len(data), 'sha256': hashlib.sha256(data).hexdigest()}

def check_arch(data, elf_class, machine):
    if data[:6] != b'\x7fELF'+bytes([elf_class, 2]) or int.from_bytes(data[18:20], 'big') != machine:
        raise ValueError('Unexpected ELF class, byte order or machine')

kernel = (args.build/'vmlinux').read_bytes()
check_arch(kernel, 2, 21)
report['payload_sections'] = {}
if not args.kernel_only:
    boot = (args.build/'arch/powerpc/boot/zImage.xenon').read_bytes()
    check_arch(boot, 1, 20)
    a, b = elf.sections(kernel), elf.sections(boot)
    for name in ['.head.text', '.text', '.rodata', '.init.text', '.data', '.notes']:
        if name not in a or name not in b or a[name] != b[name]:
            raise ValueError('Missing or altered payload section: '+name)
        report['payload_sections'][name] = {'bytes': len(a[name]), 'sha256': hashlib.sha256(a[name]).hexdigest()}

selected = [Path(line).with_suffix('.ko') for line in (args.build/'modules.order').read_text().splitlines() if line]
if len(set(selected)) != len(selected):
    raise ValueError('Duplicate module in modules.order')
for name in selected:
    if name.is_absolute() or '..' in name.parts:
        raise ValueError('Module path escapes build directory')
    data = (args.build/name).read_bytes()
    check_arch(data, 2, 21)
    info = elf.sections(data)['.modinfo'].split(b'\0')
    magic = [item.decode() for item in info if item.startswith(b'vermagic=')]
    if len(magic) != 1 or not magic[0].startswith('vermagic='+release+' '):
        raise ValueError('Module release mismatch: '+str(name))
    report['modules'].append({'path': str(name), 'sha256': hashlib.sha256(data).hexdigest(), 'vermagic': magic[0][9:]})
report['module_count'] = len(selected)
report['verified'] = True
args.output.parent.mkdir(parents=True, exist_ok=True)
pending = args.output.with_suffix('.pending')
pending.write_text(json.dumps(report, indent=2)+'\n')
pending.replace(args.output)
scope = 'kernel only; boot image not checked' if args.kernel_only else 'six payload sections match'
print(release+': '+scope+'; '+str(len(selected))+' PowerPC64 modules match release')
