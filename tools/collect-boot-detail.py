#!/usr/bin/env python3
"""Targeted Linux boot/memory follow-up; no configuration changes."""
import datetime
import gzip
import json
import platform
from pathlib import Path
import subprocess


def command(args, timeout=30):
    try:
        p = subprocess.run(args, capture_output=True, text=True, timeout=timeout)
        return dict(code=p.returncode, stdout=p.stdout, stderr=p.stderr)
    except (OSError, subprocess.TimeoutExpired) as e:
        return {'unavailable': str(e)}


def main():
    result = dict(captured_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
                  kernel=platform.release(), checks={})
    try:
        result['slabinfo'] = Path('/proc/slabinfo').read_text()
    except OSError as e:
        result['slabinfo'] = {'unavailable': str(e)}
    try:
        with gzip.open('/proc/config.gz', 'rt') as f:
            result['slab_config'] = [l.strip() for l in f if 'CONFIG_SLAB' in l or 'CONFIG_SLUB' in l]
    except OSError as e:
        result['slab_config'] = {'unavailable': str(e)}
    result['checks']['targets'] = command(['systemctl', 'show', 'graphical.target',
        'multi-user.target', 'getty@tty1.service',
        '--property=Id,ActiveEnterTimestampMonotonic,InactiveExitTimestampMonotonic'])
    log = command(['dmesg'])
    if log.get('code') == 0:
        log['stdout'] = '\n'.join(l for l in log['stdout'].splitlines() if any(v in l for v in
            ['Run /init', 'Run /sbin/init', 'Freeing unused', 'systemd[1]', 'EXT4-fs',
             'clocksource', 'random: crng']))
    result['checks']['boot_log'] = log
    result['checks']['process_names'] = command(['ps', '-eo', 'pid,comm,rss'])
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
