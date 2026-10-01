#!/usr/bin/env python3
"""Verify pinned local checkouts and extract newly added driver files for tests."""
import hashlib
import json
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[1]


def main():
    manifest = json.loads((ROOT / 'evidence/2026-10-01/deep-audit/sources.json').read_text())
    for name in ('libxenon', 'xell-reloaded', 'linux-kernel-xbox360'):
        base = ROOT / '.local/upstream' / name
        spec = manifest[name]
        commit = subprocess.check_output(['git', '-C', str(base), 'rev-parse', 'HEAD'], text=True).strip()
        if commit != spec['commit']:
            raise ValueError(f'{name}: unexpected commit {commit}')
        for relative, metadata in spec['files'].items():
            digest = hashlib.sha256((base / relative).read_bytes()).hexdigest()
            if digest != metadata['sha256']:
                raise ValueError(f'{name}/{relative}: unexpected contents')
    patch = (ROOT / '.local/upstream/linux-kernel-xbox360/patch-6.18-xenon0.30.diff').read_text()
    output = ROOT / '.local/analysis-source'
    output.mkdir(parents=True, exist_ok=True)
    for target in ('drivers/gpu/drm/tiny/xenos.c', 'sound/pci/snd-xenon.c'):
        blocks = [block for block in patch.split('diff --git ')[1:] if block.startswith(f'a/{target} b/{target}\n')]
        if len(blocks) != 1 or '--- /dev/null\n' not in blocks[0]:
            raise ValueError(f'{target}: expected a newly added source file')
        lines = [line[1:] for line in blocks[0].splitlines() if line.startswith('+') and not line.startswith('+++')]
        (output / Path(target).name).write_text('\n'.join(lines) + '\n')
    print('Pinned sources verified; xenos.c and snd-xenon.c extracted into .local/analysis-source.')


if __name__ == '__main__':
    main()
