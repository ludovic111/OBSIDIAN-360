#!/usr/bin/env python3
"""Audit a publication checkout's selected files, manifest and reachable history."""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import subprocess


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--repo', required=True, type=Path)
    p.add_argument('--policy', type=Path, help='Optional local-only forbidden_literals policy')
    a = p.parse_args()
    repo = a.repo.resolve()
    spec = importlib.util.spec_from_file_location('export_public', Path(__file__).with_name('export-public.py'))
    rules = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(rules)
    private = json.loads(a.policy.read_text()).get('forbidden_literals', []) if a.policy else []

    def git(*args):
        return subprocess.check_output(['git', '-C', str(repo), *args])

    def scan(data, label):
        text = data.decode('utf-8')
        if '\x00' in text:
            raise ValueError(f'binary/NUL content: {label}')
        for name, pattern in rules.PATTERNS.items():
            if re.search(pattern, text):
                raise ValueError(f'{name}: {label}')
        if any(s.casefold() in text.casefold() for s in private):
            raise ValueError(f'private policy match: {label}')

    paths = set(filter(None, git('ls-files', '-z', '--cached', '--others', '--exclude-standard').decode().split('\0')))
    manifest = json.loads((repo/'PUBLICATION-MANIFEST.json').read_text())
    expected = {e['path'] for e in manifest['files']}
    sums = sorted((repo/'evidence').glob('*/SHA256SUMS'))
    expected |= {'PUBLICATION-MANIFEST.json'} | {str(s.relative_to(repo)) for s in sums}
    if paths != expected:
        raise ValueError(f'file selection mismatch: {sorted(paths ^ expected)}')
    for name in sorted(paths):
        f = repo/name
        if f.is_symlink():
            raise ValueError(f'symlink: {name}')
        scan(f.read_bytes(), name)
    for entry in manifest['files']:
        if hashlib.sha256((repo/entry['path']).read_bytes()).hexdigest() != entry['public_sha256']:
            raise ValueError(f'manifest hash mismatch: {entry["path"]}')
    for sums_file in sums:
        for line in sums_file.read_text().splitlines():
            expected_hash, name = line.split('  ', 1)
            path = (sums_file.parent/name).resolve()
            if not path.is_relative_to(sums_file.parent.resolve()):
                raise ValueError('evidence path escapes its directory')
            if hashlib.sha256(path.read_bytes()).hexdigest() != expected_hash:
                raise ValueError(f'evidence hash mismatch: {name}')
    checked = 0
    for line in git('rev-list', '--objects', '--all').decode().splitlines():
        oid = line.split(' ', 1)[0]
        kind = git('cat-file', '-t', oid).decode().strip()
        if kind in ('blob', 'commit', 'tag'):
            scan(git('cat-file', '-p', oid), f'git object {oid}')
            checked += 1
    print(json.dumps({'passed': True, 'selected_files': len(paths),
                      'reachable_text_objects': checked,
                      'history_commits': int(git('rev-list', '--count', '--all')),
                      'local_private_policy_used': a.policy is not None,
                      'limitations': 'Pattern scanning supplements content/provenance review; not a universal secret detector.'}, indent=2))


if __name__ == '__main__':
    main()
