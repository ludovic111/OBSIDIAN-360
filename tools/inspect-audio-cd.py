#!/usr/bin/env python3
"""Linux CD metadata and four one-sector audio reads; emit hashes, never audio.

Run with an outer timeout: timeout -k 2 45 python3 inspect-audio-cd.py
Uses only standard CDROM ioctls on the fixed optical device /dev/sr0.
No eject, playback, firmware, vendor commands or raw controller access.
"""
import ctypes as C
import datetime
import fcntl
import hashlib
import json
import os
from pathlib import Path
import platform
import stat
import struct
import time


class AudioRead(C.Structure):
    _fields_ = [('lba', C.c_int), ('format', C.c_ubyte),
                ('nframes', C.c_int), ('buffer', C.c_void_p)]


def emit(event, **values):
    print(json.dumps({'event': event, **values}), flush=True)


def toc_entry(fd, track):
    # linux/cdrom.h: 12-byte cdrom_tocentry; native int LBA at offset 4.
    # Do not decode the ABI-dependent packed control/ADR bitfields.
    data = bytearray(12)
    data[0], data[2] = track, 1  # CDROM_LBA
    fcntl.ioctl(fd, 0x5306, data, True)
    return {'track': track, 'lba': struct.unpack_from('@i', data, 4)[0],
            'data_track': bool(data[8])}


def read_sector(fd, lba):
    data = C.create_string_buffer(2352)
    request = AudioRead(lba, 1, 1, C.addressof(data))
    started = time.monotonic()
    fcntl.ioctl(fd, 0x530e, bytearray(bytes(request)), True)
    return {'lba': lba, 'bytes': len(data.raw),
            'sha256': hashlib.sha256(data.raw).hexdigest(),
            'all_zero': not any(data.raw),
            'seconds': time.monotonic() - started}


def main():
    if platform.system() != 'Linux':
        raise RuntimeError('Linux CDROM driver required')
    if Path('/sys/class/block/sr0/device/type').read_text().strip() != '5':
        raise RuntimeError('sr0 is not a SCSI optical device')
    if not stat.S_ISBLK(os.stat('/dev/sr0').st_mode):
        raise RuntimeError('sr0 is not a block device')
    assert C.sizeof(C.c_int) == 4
    assert AudioRead.nframes.offset == 8
    assert AudioRead.buffer.offset == (12 if C.sizeof(C.c_void_p) == 4 else 16)
    emit('start', utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
         kernel=platform.release(), pointer_bytes=C.sizeof(C.c_void_p),
         audio_request_bytes=C.sizeof(AudioRead))
    fd = os.open('/dev/sr0', os.O_RDONLY | os.O_NONBLOCK)
    try:
        status = fcntl.ioctl(fd, 0x5326, 0x7fffffff)
        emit('drive_status', value=status)
        if status != 4:
            raise RuntimeError('Driver does not report disc ready')
        header = bytearray(2)
        fcntl.ioctl(fd, 0x5305, header, True)
        first, last = header
        if not 1 <= first <= last <= 99:
            raise RuntimeError('Invalid TOC range')
        entries = [toc_entry(fd, n) for n in range(first, last + 1)]
        leadout = toc_entry(fd, 0xaa)
        emit('toc', entries=entries, leadout=leadout)
        bounds = entries + [leadout]
        if any(b['lba'] <= a['lba'] for a, b in zip(bounds, bounds[1:])):
            raise RuntimeError('Non-increasing TOC')
        samples = []
        for index in sorted({0, len(entries) // 2, len(entries) - 1}):
            entry = entries[index]
            if entry['data_track']:
                continue
            lba = entry['lba'] + min(150, (bounds[index + 1]['lba'] - entry['lba']) // 2)
            if lba < 0:
                raise RuntimeError('Negative sample LBA')
            result = read_sector(fd, lba)
            samples.append(result)
            emit('sample', **result)
        if samples:
            result = read_sector(fd, samples[0]['lba'])
            emit('repeat', **result, matches_first=result['sha256'] == samples[0]['sha256'])
        emit('complete', sampled_positions=len(samples), full_disc_verified=False)
    finally:
        os.close(fd)


if __name__ == '__main__':
    try:
        main()
    except (OSError, RuntimeError) as exc:
        emit('error', kind=type(exc).__name__, errno=getattr(exc, 'errno', None), message=str(exc))
        raise SystemExit(1)
