#!/usr/bin/env python3
"""Prepare an explicit, reviewed text-only export. Never commits or pushes."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess

ROOTS = {'docs', 'tools', 'desktop', 'research', 'evidence', 'LICENSES', 'game-analysis'}
TOP = {'README.md', 'AGENTS.md', '.gitignore', '.gitattributes', 'LICENSE',
       'THIRD_PARTY.md', 'CONTRIBUTING.md'}
SUFFIXES = {'.md', '.py', '.c', '.h', '.patch', '.txt', '.json', '.log', '.config',
            '.csv', '.asm', '.sh', '.conf', '.hook', '.example', '.sha256', '.rs', '.toml', '.lock'}
EXCLUDE = {
    'docs/historique-installation.txt', 'docs/rapport-initial.txt',
    'research/metadata/installed-state.json',
    'research/patches/0002-xell-allocate-physical-page.patch',
    'evidence/2026-10-01/boot-preflight/candidate-init.txt',
    'evidence/2026-10-01/boot-preflight/candidate-udev-hook.txt',
}
PATTERNS = {
    'private-key': r'-----BEGIN (?:OPENSSH |RSA |EC |DSA )?PRIVATE KEY-----',
    'github-token': r'\b(?:gh[pousr]_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{20,})\b',
    'cloud-key': r'\bAKIA[A-Z0-9]{16}\b',
    'local-home': r'/Users/[A-Za-z0-9_.-]+/',
    'private-ip': r'\b(?:192\.168\.\d{1,3}\.\d{1,3}|10\.\d{1,3}\.\d{1,3}\.\d{1,3}|172\.(?:1[6-9]|2\d|3[01])\.\d{1,3}\.\d{1,3})\b',
    'mac-address': r'(?i)\b(?!(?:ff:){5}ff\b|(?:00:){5}00\b)(?:[0-9a-f]{2}:){5}[0-9a-f]{2}\b',
    'secret-assignment': r'(?i)(?:cpu.?key|dvd.?key|api.?key|access.?token|password)\s*[=:]\s*["\x27]?[A-Za-z0-9+/=_-]{16,}',
}


def digest(data):
    return hashlib.sha256(data).hexdigest()


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--output', required=True, type=Path)
    p.add_argument('--policy', required=True, type=Path,
                   help='Local-only JSON with replacements and forbidden_literals; never exported')
    a = p.parse_args()
    if a.output.exists():
        p.error('Output must not exist; do not overwrite a prior reviewed export')
    policy = json.loads(a.policy.read_text())
    paths = subprocess.check_output(['git', 'ls-files', '-z']).decode().split('\0')
    manifest = {'scope': 'Reviewed public text snapshot; original local history is not included.',
                'source_commit': subprocess.check_output(['git', 'rev-parse', 'HEAD'], text=True).strip(),
                'files': [], 'excluded': [], 'limitations':
                ['Pattern scanning complements review; it is not proof that arbitrary secrets are absent.',
                 'Sanitized evidence is a publication derivative, not the byte-identical original capture.',
                 'The source history and excluded originals remain in the local research repository.']}
    staged = {}
    problems = []
    for name in sorted(filter(None, paths)):
        f = Path(name)
        allowed = ((f.parts[0] in ROOTS or name in TOP)
                   and not name.startswith(('research/archive/', 'research/blocked/'))
                   and name not in EXCLUDE and f.name != 'SHA256SUMS'
                   and (f.suffix in SUFFIXES or name in TOP or
                        f.name.startswith('Dockerfile.') or name == 'tools/ssh-xbox'))
        if not allowed:
            manifest['excluded'].append(name)
            continue
        if f.is_symlink():
            raise RuntimeError(f'Symlink requires manual review: {name}')
        original = f.read_bytes()
        text = original.decode('utf-8')  # Reject binary content instead of guessing.
        for old, new in policy['replacements'].items():
            text = text.replace(old, new)
        for label, pattern in PATTERNS.items():
            if re.search(pattern, text):
                problems.append({'path': name, 'finding': label})
        for literal in policy.get('forbidden_literals', []):
            if literal.casefold() in text.casefold():
                problems.append({'path': name, 'finding': 'local-policy-literal'})
        data = text.encode()
        staged[name] = data
        manifest['files'].append(dict(path=name, source_sha256=digest(original),
                                     public_sha256=digest(data), sanitized=data != original))
    if problems:
        print(json.dumps({'passed': False, 'findings': problems}, indent=2))
        raise SystemExit(1)
    a.output.mkdir(parents=True)
    for name, data in staged.items():
        dest = a.output/name
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes(data)
        dest.chmod(Path(name).stat().st_mode & 0o777)
    for date in sorted((a.output/'evidence').glob('*')):
        if date.is_dir():
            items = [f'{digest(f.read_bytes())}  {f.relative_to(date)}'
                     for f in sorted(date.rglob('*')) if f.is_file()]
            (date/'SHA256SUMS').write_text('\n'.join(items)+'\n')
    (a.output/'PUBLICATION-MANIFEST.json').write_text(json.dumps(manifest, indent=2)+'\n')
    print(json.dumps({'passed': True, 'files': len(staged),
                      'excluded': len(manifest['excluded']),
                      'sanitized': sum(f['sanitized'] for f in manifest['files'])}))


if __name__ == '__main__':
    main()
