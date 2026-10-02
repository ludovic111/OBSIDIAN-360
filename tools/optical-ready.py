#!/usr/bin/env python3
"""One standard TEST UNIT READY on /dev/sr0, with bounded SCSI timeout.

No data transfer, vendor commands, reset, eject, firmware or memory access.
Run under an outer timeout as well; kernel error recovery can outlast a command.
ABI: Linux include/scsi/sg.h. Sense bytes contain status, not media content.
"""
import ctypes as C
import datetime
import fcntl
import json
import os
from pathlib import Path
import platform
import stat


class Header(C.Structure):
    _fields_ = [('interface_id', C.c_int), ('direction', C.c_int),
                ('cmd_len', C.c_ubyte), ('max_sense', C.c_ubyte),
                ('iov_count', C.c_ushort), ('data_len', C.c_uint),
                ('data', C.c_void_p), ('cmd', C.c_void_p), ('sense', C.c_void_p),
                ('timeout', C.c_uint), ('flags', C.c_uint), ('pack_id', C.c_int),
                ('user', C.c_void_p), ('status', C.c_ubyte),
                ('masked_status', C.c_ubyte), ('msg_status', C.c_ubyte),
                ('sense_len', C.c_ubyte), ('host_status', C.c_ushort),
                ('driver_status', C.c_ushort), ('resid', C.c_int),
                ('duration', C.c_uint), ('info', C.c_uint)]


def decode_sense(data):
    if not data:
        return None
    response = data[0] & 0x7f
    if response in (0x70, 0x71) and len(data) >= 14:
        return {'response': response, 'key': data[2] & 15,
                'asc': data[12], 'ascq': data[13]}
    if response in (0x72, 0x73) and len(data) >= 4:
        return {'response': response, 'key': data[1] & 15,
                'asc': data[2], 'ascq': data[3]}
    return {'response': response, 'unrecognized_or_truncated': True}


def main():
    if platform.system() != 'Linux':
        raise RuntimeError('Linux required')
    if Path('/sys/class/block/sr0/device/type').read_text().strip() != '5':
        raise RuntimeError('sr0 is not an optical device')
    if not stat.S_ISBLK(os.stat('/dev/sr0').st_mode):
        raise RuntimeError('sr0 is not a block device')
    assert C.sizeof(Header) == (64 if C.sizeof(C.c_void_p) == 4 else 88)
    command = (C.c_ubyte * 6)()  # opcode 0x00: TEST UNIT READY
    sense = (C.c_ubyte * 64)()
    request = Header(interface_id=ord('S'), direction=-1, cmd_len=6,
                     max_sense=64, cmd=C.addressof(command),
                     sense=C.addressof(sense), timeout=5000)
    data = bytearray(bytes(request))
    fd = os.open('/dev/sr0', os.O_RDONLY | os.O_NONBLOCK)
    try:
        fcntl.ioctl(fd, 0x2285, data, True)  # SG_IO
    finally:
        os.close(fd)
    result = Header.from_buffer_copy(data)
    raw = bytes(sense[:result.sense_len])
    print(json.dumps({'utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
                      'kernel': platform.release(), 'abi_bytes': C.sizeof(Header),
                      'command': 'TEST UNIT READY', 'status': result.status,
                      'host_status': result.host_status, 'driver_status': result.driver_status,
                      'duration_ms': result.duration, 'sense_hex': raw.hex(),
                      'sense': decode_sense(raw)}), flush=True)


if __name__ == '__main__':
    main()
