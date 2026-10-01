#!/usr/bin/env python3
"""Run on Linux: bounded inventory through existing kernel interfaces, no MMIO."""
import datetime
import gzip
import json
import subprocess
from pathlib import Path


def read(path):
    try:
        return Path(path).read_text().strip()
    except OSError as error:
        return {"unavailable": str(error)}


def command(*args):
    try:
        proc = subprocess.run(args, capture_output=True, text=True, timeout=10)
        return {"code": proc.returncode, "stdout": proc.stdout, "stderr": proc.stderr}
    except (OSError, subprocess.TimeoutExpired) as error:
        return {"unavailable": str(error)}


def main():
    result = {
        "captured_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "kernel": read('/proc/sys/kernel/osrelease'),
        "uptime": read('/proc/uptime'),
        "interrupts": read('/proc/interrupts'),
        "root": command('findmnt', '-no', 'SOURCE,FSTYPE', '/'),
        "failed_units": command('systemctl', '--failed', '--no-pager'),
        "network": {}, "drm": {}, "thermal": {},
        "audio_class_present": Path('/sys/class/sound').exists(),
        "audio_pci_driver": Path('/sys/bus/pci/devices/0000:01:09.0/driver').exists(),
        "framebuffer": read('/sys/class/graphics/fb0/virtual_size'),
    }
    for device in sorted(Path('/sys/class/net').iterdir()):
        if device.name == 'lo':
            continue
        result['network'][device.name] = {
            key: read(device / key) for key in ('operstate', 'carrier', 'speed', 'duplex')
        }
        result['network'][device.name]['statistics'] = {
            p.name: read(p) for p in sorted((device / 'statistics').iterdir())
        }
        result['network'][device.name]['features'] = command('ethtool', '-k', device.name)
    for connector in sorted(Path('/sys/class/drm').glob('card*-*')):
        result['drm'][connector.name] = {
            key: read(connector / key) for key in ('status', 'enabled', 'modes')
        }
    for hwmon in sorted(Path('/sys/class/hwmon').glob('hwmon*')):
        result['thermal'][hwmon.name] = {
            p.name: read(p) for p in sorted(hwmon.glob('temp*_input'))
        }
    try:
        config = gzip.open('/proc/config.gz', 'rt').read().splitlines()
        keys = ('CONFIG_SOUND', 'CONFIG_SND', 'CONFIG_HZ=', 'CONFIG_MTD', 'CONFIG_DRM_XENOS', 'CONFIG_MODVERSIONS')
        result['kernel_config_subset'] = [line for line in config if any(key in line for key in keys)]
    except OSError as error:
        result['kernel_config_subset'] = {"unavailable": str(error)}
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
