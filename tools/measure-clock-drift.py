#!/usr/bin/env python3
"""Compare console clocks to the Mac over bounded read-only SSH exchanges.

No time, frequency, NTP, clocksource or hardware configuration is changed.
Transport diagnostics remain under ignored .local/; reports contain no host IP.
"""
import argparse
import datetime
import json
from pathlib import Path
import select
import shlex
import subprocess
import time

REMOTE = r'''
import sys,time,json,pathlib,os
base=pathlib.Path('/proc/device-tree/cpus')
frequencies={}
if base.exists():
 for p in base.glob('*/timebase-frequency'):
  frequencies[p.parent.name]=int.from_bytes(p.read_bytes(),'big')
clock=pathlib.Path('/sys/devices/system/clocksource/clocksource0/current_clocksource')
print(json.dumps({'kind':'identity','kernel':os.uname().release,'timebase_frequencies':frequencies,'clocksource':clock.read_text().strip() if clock.exists() else None}),flush=True)
for line in sys.stdin:
 if line.strip()!='sample':break
 raw=time.clock_gettime_ns(time.CLOCK_MONOTONIC_RAW)
 mono=time.monotonic_ns();wall=time.time_ns()
 print(json.dumps({'raw_ns':raw,'monotonic_ns':mono,'wall_ns':wall}),flush=True)
'''


def analyze(report):
    if report.get('state') != 'succeeded' or report.get('transport_code') != 0:
        raise ValueError('Collection is not confirmed complete')
    rows = report['samples']
    if len(rows) < 2:
        raise ValueError('At least two samples are required')
    previous = None
    for row in rows:
        a, b = row['host_send_monotonic_ns'], row['host_receive_monotonic_ns']
        if b < a or (previous is not None and a <= previous):
            raise ValueError('Invalid host clock brackets')
        previous = b
    first, last = rows[0], rows[-1]
    low = last['host_send_monotonic_ns'] - first['host_receive_monotonic_ns']
    high = last['host_receive_monotonic_ns'] - first['host_send_monotonic_ns']
    if low <= 0:
        raise ValueError('Overlapping end-point clock brackets')
    rates = {}
    for key in ('raw_ns', 'monotonic_ns', 'wall_ns'):
        delta = last['console'][key] - first['console'][key]
        if delta <= 0:
            raise ValueError('Console clock did not advance: ' + key)
        ratio = [delta / high, delta / low]
        rates[key] = {'console_seconds': delta / 1e9, 'ratio_bounds': ratio,
                      'error_ppm_bounds': [(x - 1) * 1e6 for x in ratio]}
    result = {
        'scope': 'Relative to Mac monotonic clock; SSH brackets bound observation times, not absolute oscillator accuracy.',
        'sample_count': len(rows),
        'host_interval_seconds_bounds': [low / 1e9, high / 1e9],
        'clock_rates': rates,
        'last_wall_offset_seconds_bounds': [
            (last['console']['wall_ns'] - last['host_receive_wall_ns']) / 1e9,
            (last['console']['wall_ns'] - last['host_send_wall_ns']) / 1e9],
    }
    freqs = set(report['identity'].get('timebase_frequencies', {}).values())
    if report['identity'].get('clocksource') == 'timebase' and len(freqs) == 1:
        freq = next(iter(freqs))
        if not isinstance(freq, int) or freq <= 0:
            raise ValueError('Invalid advertised timebase frequency')
        result['advertised_timebase_hz'] = freq
        result['effective_timebase_hz_bounds'] = [freq * x for x in rates['raw_ns']['ratio_bounds']]
    return result


def collect(args):
    root = Path(__file__).resolve().parents[1]
    private = root / '.local'
    private.mkdir(exist_ok=True)
    diagnostic = private / ('clock-transport-' + str(time.time_ns()) + '.log')
    report = {'state': 'starting', 'started_host_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
              'scope': 'Persistent read-only SSH samples; no clock or hardware changes', 'samples': []}
    def save():
        args.output.write_text(json.dumps(report, indent=2) + '\n')
    save()
    with diagnostic.open('w') as err:
        proc = subprocess.Popen([str(root / 'tools/ssh-xbox'), 'python3 -u -c ' + shlex.quote(REMOTE)],
                                stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=err, text=True, bufsize=1)
        def read():
            if not select.select([proc.stdout], [], [], 15)[0]:
                raise TimeoutError('SSH response timeout; no automatic retry')
            return json.loads(proc.stdout.readline())
        try:
            report['identity'] = read()
            report['state'] = 'running'
            for i in range(args.samples):
                if i:
                    time.sleep(args.interval)
                a = time.monotonic_ns()
                wa = time.time_ns()
                proc.stdin.write('sample\n')
                proc.stdin.flush()
                row = read()
                b = time.monotonic_ns()
                wb = time.time_ns()
                report['samples'].append({'host_send_monotonic_ns': a, 'host_receive_monotonic_ns': b,
                                          'host_send_wall_ns': wa, 'host_receive_wall_ns': wb, 'console': row})
                save()
                print(f'Sample {i + 1}/{args.samples}, round trip {(b-a)/1e6:.3f} ms', flush=True)
            proc.stdin.close()
            report['transport_code'] = proc.wait(timeout=10)
            report['state'] = 'succeeded' if proc.returncode == 0 else 'failed'
            report['analysis'] = analyze(report)
        except BaseException as exc:
            report['state'] = 'failed'
            report['failure_type'] = type(exc).__name__
            proc.terminate()
            try:
                proc.wait(timeout=5)
            except subprocess.TimeoutExpired:
                proc.kill()
                proc.wait()
            raise
        finally:
            save()
    return report


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--output', type=Path, required=True)
    p.add_argument('--samples', type=int, default=7)
    p.add_argument('--interval', type=float, default=10)
    p.add_argument('--analyze', type=Path, help='Analyze an existing capture without SSH')
    args = p.parse_args()
    if args.output.exists():
        p.error('Use a new output path to preserve previous observations')
    if not 2 <= args.samples <= 61 or not 1 <= args.interval <= 60:
        p.error('Require 2..61 samples and 1..60 seconds between samples')
    args.output.parent.mkdir(parents=True, exist_ok=True)
    if args.analyze:
        result = analyze(json.loads(args.analyze.read_text()))
        args.output.write_text(json.dumps(result, indent=2) + '\n')
    else:
        result = collect(args)['analysis']
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
