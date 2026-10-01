#!/usr/bin/env python3
"""Linux baseline via standard interfaces; optional bounded userspace workloads."""
import argparse
import datetime
import json
import os
from pathlib import Path
import platform
import subprocess
import sys


def read(path):
    try:
        return Path(path).read_text().strip()
    except OSError as e:
        return {'unavailable': str(e)}


def command(*args, timeout=12):
    try:
        p = subprocess.run(args, capture_output=True, text=True, timeout=timeout,
                           env=dict(os.environ, LC_ALL='C', SYSTEMD_COLORS='0'))
        return dict(code=p.returncode, stdout=p.stdout, stderr=p.stderr)
    except (OSError, subprocess.TimeoutExpired) as e:
        return {'unavailable': str(e)}


def snapshot():
    return {name: read('/proc/'+name) for name in
            ('uptime', 'meminfo', 'loadavg', 'stat', 'vmstat', 'pressure/cpu',
             'pressure/memory', 'pressure/io')} | {
        'temperatures_millidegrees': {
            str(p): read(p) for p in sorted(Path('/sys/class/hwmon').glob('hwmon*/temp*_input'))}}


WORKLOAD = r'''
import hashlib,json,ssl,time
size=8*1024*1024
src=b'\x5a'*size
dst=bytearray(size)
result={'buffer_bytes':size, 'iterations_per_sample':4, 'openssl':ssl.OPENSSL_VERSION,
        'sha256_provider':type(hashlib.sha256()).__module__, 'samples':[]}
for n in range(3):
    start=time.perf_counter()
    for i in range(4): digest=hashlib.sha256(src).hexdigest()
    hash_elapsed=time.perf_counter()-start
    start=time.perf_counter()
    for i in range(4): dst[:]=src
    copy_elapsed=time.perf_counter()-start
    if dst!=src: raise RuntimeError('copy mismatch')
    result['samples'].append({'sha256_seconds':hash_elapsed,
        'sha256_MiB_s':32/hash_elapsed, 'copy_seconds':copy_elapsed,
        'copy_payload_MiB_s':32/copy_elapsed,'digest':digest})
assert len({s['digest'] for s in result['samples']})==1
print(json.dumps(result))
'''


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--workloads', action='store_true')
    args = p.parse_args()
    if sys.platform != 'linux':
        raise SystemExit('Run on Linux; this collector does not connect to the console itself.')
    report = dict(captured_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
                  kernel=platform.release(), machine=platform.machine(),
                  python=sys.version, page_size=os.sysconf('SC_PAGE_SIZE'),
                  affinity=sorted(os.sched_getaffinity(0)), before=snapshot())
    report['cpuinfo'] = read('/proc/cpuinfo')
    report['topology'] = {str(p): read(p) for pattern in
        ('cpu*/topology/core_id', 'cpu*/topology/physical_package_id',
         'cpu*/topology/thread_siblings_list')
        for p in sorted(Path('/sys/devices/system/cpu').glob(pattern))}
    report['storage_scheduler'] = {str(p): read(p) for p in
        Path('/sys/class/block').glob('sd*/queue/scheduler')}
    report['boot'] = {name: command('systemd-analyze', name) for name in
                      ('time', 'blame', 'critical-chain')}
    report['desktop_memory'] = []
    for d in Path('/proc').glob('[0-9]*'):
        name = read(d/'comm')
        if name not in ('Xorg', 'icewm', 'icewm-session', 'python3', 'xterm'):
            continue
        # Only status fields and aggregate maps; no process arguments/environment.
        status = read(d/'status')
        report['desktop_memory'].append(dict(pid=int(d.name), name=name,
            status='\n'.join(l for l in status.splitlines() if l.startswith(
                ('Name:', 'VmRSS:', 'VmSize:', 'RssAnon:', 'RssFile:', 'Threads:')))
                if isinstance(status, str) else status,
            smaps_rollup=read(d/'smaps_rollup')))
    if args.workloads:
        run = command(sys.executable, '-c', WORKLOAD, timeout=20)
        if run.get('code') == 0:
            run['result'] = json.loads(run.pop('stdout'))
        report['userspace_workloads'] = run
    report['after'] = snapshot()
    report['failed_units'] = command('systemctl', '--failed', '--no-pager')
    report['limitations'] = [
        'Boot timings exclude dashboard, game exploit and XeLL; graphical target is not visible desktop readiness.',
        'One boot and three short samples are not long-term stability or a before/after comparison.',
        'Copy is a Python bytearray payload rate, including interpreter/allocation overhead, not raw RAM bandwidth.',
        'SHA256 uses the installed Python provider; no CPU affinity or scheduling changes.',
        'No raw disk access, cache dropping, power changes, MMIO, NAND, firmware writes or packages installed.',
        'Collection and concurrent desktop/SSH activity influence memory and timing results.']
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
