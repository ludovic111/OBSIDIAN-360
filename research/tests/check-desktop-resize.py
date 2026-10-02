#!/usr/bin/env python3
"""Reproduce outline-resize/XTest deadlock only on our own disposable Xvfb.

Requires the desktop-test image. Never connects to an existing DISPLAY and
never forwards Xbox, host X sockets or input devices into the container.
"""
import argparse
import datetime
import json
import os
from pathlib import Path
import select
import signal
import subprocess
import tempfile
import time

ROOT = Path(__file__).resolve().parents[2]


def command(args, env, timeout=3):
    try:
        result = subprocess.run(args, env=env, capture_output=True, text=True, timeout=timeout)
        return {'code': result.returncode, 'stdout': result.stdout, 'stderr': result.stderr}
    except subprocess.TimeoutExpired as exc:
        return {'timeout': True, 'stdout': (exc.stdout or b'').decode(),
                'stderr': (exc.stderr or b'').decode()}


def geometry(window, env):
    result = command(['xdotool', 'getwindowgeometry', '--shell', window], env)
    if result.get('code') != 0:
        return result
    return {k: int(v) for k, v in (line.split('=', 1) for line in result['stdout'].splitlines())}


HELPER = '''
import sys,time,json,ctypes as C
sys.path.insert(0,sys.argv[1])
from xbox_desktop import X11
x=X11()
# Resolve XTEST and flush before any window-manager grab starts.
x.move(0,0);x.flush();x.focus()
left,top,width,height=map(int,sys.argv[2:6])
window=int(sys.argv[6])
x.warp(left+width+1,top+height+1);x.flush();x.focus()
x.button(1,True)
# Explicit EWMH bottom-right resize avoids guessing theme border coordinates.
class Data(C.Union):
 _fields_=[('b',C.c_char*20),('s',C.c_short*10),('l',C.c_long*5)]
class Client(C.Structure):
 _fields_=[('type',C.c_int),('serial',C.c_ulong),('send_event',C.c_int),
           ('display',C.c_void_p),('window',C.c_ulong),('message_type',C.c_ulong),
           ('format',C.c_int),('data',Data)]
class Event(C.Union):
 _fields_=[('client',Client),('pad',C.c_long*24)]
x.x.XInternAtom.argtypes=[C.c_void_p,C.c_char_p,C.c_int]
x.x.XInternAtom.restype=C.c_ulong
x.x.XSendEvent.argtypes=[C.c_void_p,C.c_ulong,C.c_int,C.c_long,C.c_void_p]
e=Event();e.client.type=33;e.client.display=x.d;e.client.window=window
atom=x.x.XInternAtom(x.d,b'_NET_WM_MOVERESIZE',False)
e.client.message_type=atom;e.client.format=32
e.client.data.l[:]=[left+width+1,top+height+1,4,1,1]
x.x.XSendEvent(x.d,x.x.XDefaultRootWindow(x.d),False,(1<<19)|(1<<20),C.byref(e))
x.flush()
print(json.dumps({'resize_requested':True}),flush=True)
time.sleep(.25)
x.move(-60,-40);x.flush()
x.button(1,False);x.flush()
print(json.dumps({'release_request_sent':True}),flush=True)
# A synchronous reply proves the server processed this connection again.
x.focus()
print(json.dumps({'roundtrip_after_release':True}),flush=True)
'''


def case(opaque):
    children = []
    with tempfile.TemporaryDirectory(prefix='obsidian-resize-') as temp:
        temp = Path(temp)
        env = dict(os.environ, HOME=str(temp), LC_ALL='C')
        env.pop('DISPLAY', None)
        env.pop('XAUTHORITY', None)
        log = (temp / 'processes.log').open('w+')
        read_fd, write_fd = os.pipe()
        try:
            xvfb = subprocess.Popen(['Xvfb', '-displayfd', str(write_fd), '-screen', '0',
                                     '1280x720x24', '-nolisten', 'tcp'], pass_fds=(write_fd,),
                                    stdout=log, stderr=log, start_new_session=True)
            children.append(xvfb)
            os.close(write_fd)
            write_fd = None
            if not select.select([read_fd], [], [], 8)[0]:
                raise RuntimeError('Isolated Xvfb startup timed out')
            display = os.read(read_fd, 64).decode().strip()
            if not display.isdigit():
                raise RuntimeError('Xvfb did not allocate a display')
            env['DISPLAY'] = ':' + display
            settings = temp / '.icewm'
            settings.mkdir()
            (settings / 'preferences').write_text(
                f'OpaqueMove={opaque}\nOpaqueResize={opaque}\nShowTaskBar=0\n')
            wm = subprocess.Popen(['/opt/icewm/icewm'], env=env, stdout=log,
                                  stderr=log, start_new_session=True)
            children.append(wm)
            time.sleep(.5)
            launcher = subprocess.Popen(['python3', str(ROOT / 'desktop/xbox_desktop.py')],
                                        env=env, stdout=log, stderr=log, start_new_session=True)
            children.append(launcher)
            window = None
            for _ in range(30):
                found = command(['xdotool', 'search', '--onlyvisible', '--class', 'XboxLauncher'], env)
                if found.get('code') == 0:
                    window = found['stdout'].splitlines()[0]
                    break
                time.sleep(.1)
            if not window:
                raise RuntimeError('Launcher window not found')
            time.sleep(.5)
            before = geometry(window, env)
            if not all(k in before for k in ('X', 'Y', 'WIDTH', 'HEIGHT')):
                raise RuntimeError('Cannot inspect initial geometry')
            injection = command(['python3', '-c', HELPER, str(ROOT / 'desktop'),
                                 *(str(before[k]) for k in ('X', 'Y', 'WIDTH', 'HEIGHT')), window], env)
            observer = command(['xdpyinfo'], env, timeout=1)
            after = geometry(window, env) if observer.get('code') == 0 else None
            state = temp / '.local/state/xbox-desktop/input.json'
            report = {'opaque': opaque, 'before': before, 'after': after,
                      'injection': injection, 'observer_responsive': observer.get('code') == 0,
                      'observer_timeout': bool(observer.get('timeout')),
                      'launcher_running': launcher.poll() is None,
                      'wm_running': wm.poll() is None,
                      'state_present': state.exists()}
            return report
        finally:
            if write_fd is not None:
                os.close(write_fd)
            os.close(read_fd)
            # SIGKILL is deliberate: the old mode is expected to deadlock.
            for process in reversed(children):
                if process.poll() is None:
                    os.killpg(process.pid, signal.SIGKILL)
                process.wait(timeout=3)
            log.flush()
            log.seek(0)
            text = log.read()
            log.close()
            if 'report' in locals():
                report['process_log'] = text


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', required=True)
    args = parser.parse_args()
    report = {'utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
              'scope': 'Native host architecture, isolated Xvfb, IceWM 4.0.0, actual launcher/XTest class',
              'version': command(['/opt/icewm/icewm', '--version'], dict(os.environ)),
              'cases': [case(0), case(1)]}
    old, fixed = report['cases']
    report['passed'] = bool(old['injection'].get('timeout') and old['observer_timeout']
                            and fixed['injection'].get('code') == 0
                            and fixed['observer_responsive']
                            and fixed['after']['WIDTH'] < fixed['before']['WIDTH']
                            and fixed['after']['HEIGHT'] < fixed['before']['HEIGHT'])
    Path(args.output).write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(report, indent=2))
    raise SystemExit(0 if report['passed'] else 1)


if __name__ == '__main__':
    main()
