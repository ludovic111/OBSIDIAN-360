#!/usr/bin/env python3
"""Check publication gates in a disposable Git repository with fake data only."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile


def main():
    tool = Path(__file__).resolve().parents[2]/'tools/audit-public.py'
    results = []
    with tempfile.TemporaryDirectory(prefix='obsidian-public-audit-') as tmp:
        repo = Path(tmp)

        def git(*args):
            subprocess.run(['git', '-C', tmp, *args], check=True, capture_output=True)

        def check(name, passed, message=None):
            p = subprocess.run([sys.executable, str(tool), '--repo', tmp],
                               capture_output=True, text=True, timeout=20)
            assert (p.returncode == 0) == passed, (name, p.stderr)
            if message:
                assert message in p.stderr, (name, p.stderr)
            results.append({'case': name, 'expected_pass': passed, 'passed': True})

        git('init', '-b', 'main')
        git('config', 'user.name', 'Synthetic fixture')
        git('config', 'user.email', 'fixture@example.invalid')
        content = b'Synthetic public text\n'
        readme = repo/'README.md'; readme.write_bytes(content)
        manifest = {'files': [{'path': 'README.md', 'public_sha256': hashlib.sha256(content).hexdigest()}]}
        (repo/'PUBLICATION-MANIFEST.json').write_text(json.dumps(manifest))
        check('clean_unborn_checkout', True)
        readme.write_bytes(b'changed without updating manifest\n')
        check('manifest_detects_content_change', False, 'manifest hash mismatch')
        readme.write_bytes(content)
        extra = repo/'unreviewed.txt'; extra.write_text('Unexpected file')
        check('unreviewed_file_rejected', False, 'file selection mismatch')
        extra.unlink()
        # Construct a nonfunctional marker. No credential is accessed or used.
        fake = ('gh' + 'p_' + 'A' * 24 + '\n').encode()
        readme.write_bytes(fake)
        check('synthetic_token_pattern_rejected', False, 'github-token')
        git('add', '.')
        git('commit', '-m', 'Synthetic bad historical fixture')
        readme.write_bytes(content)
        git('add', 'README.md')
        git('commit', '-m', 'Restore clean current fixture')
        check('removed_marker_still_detected_in_history', False, 'github-token: git object')
    print(json.dumps({'scope': 'Disposable synthetic repository; no real secrets', 'results': results}, indent=2))


if __name__ == '__main__':
    main()
