#!/usr/bin/env python3
"""Offline comparison only. Never opens a device or writes video registers."""
import argparse
import hashlib
import json
import re
import struct
from pathlib import Path


def parse_tables(source):
    text = re.sub(r'/\*.*?\*/|//[^\n]*', '', source, flags=re.S)
    tables = {}
    for name, body in re.findall(r'uint32_t\s+(ana_\w+)\s*\[[^]]*\]\s*=\s*\{(.*?)\};', text, re.S):
        values = [int(v.strip(), 0) for v in body.split(',') if v.strip()]
        if len(values) != 256:
            raise ValueError(f'{name}: expected 256 registers, got {len(values)}')
        tables[name] = values
    if not tables:
        raise ValueError('No ANA tables found')
    return tables


def compare(capture, table):
    # Sentinel values occur in the source tables; equality there is not evidence
    # that a programmable register or a complete timing sequence matches.
    useful = [i for i, value in enumerate(table) if value not in (0xffffffff, 0xdeadbeef)]
    changes = [i for i in useful if capture[i] != table[i]]
    return {
        'compared_registers': len(useful),
        'matching_registers': len(useful) - len(changes),
        'differences': [dict(register=f'0x{i:02x}', captured=f'0x{capture[i]:08x}', table=f'0x{table[i]:08x}') for i in changes],
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--ana', required=True, type=Path)
    parser.add_argument('--tables', required=True, type=Path)
    parser.add_argument('--gpu', required=True, type=Path)
    args = parser.parse_args()
    data = args.ana.read_bytes()
    if len(data) != 1024:
        raise ValueError('ANA capture must contain exactly 1024 bytes')
    capture = struct.unpack('>256I', data)  # PPC native order from ana_read()
    table_data = args.tables.read_bytes()
    tables = parse_tables(table_data.decode())
    gpu = json.loads(args.gpu.read_text())
    reg = lambda name: int(gpu[name]['value'], 0)
    horizontal = reg('D1CRTC_H_BLANK_START_END')
    comparisons = {name: compare(capture, values) for name, values in tables.items()}
    result = {
        'scope': 'Offline correlation, not a hardware modesetting validation',
        'ana_sha256': hashlib.sha256(data).hexdigest(),
        'tables_sha256': hashlib.sha256(table_data).hexdigest(),
        'gpu': {
            'width': reg('D1GRPH_X_END'), 'height': reg('D1GRPH_Y_END'),
            'pitch_pixels': reg('D1GRPH_PITCH'),
            'horizontal_total_from_libxenon': reg('D1CRTC_H_TOTAL') + 1,
            'horizontal_offset': horizontal >> 16,
            'horizontal_active': (horizontal & 0xffff) - (horizontal >> 16),
            'vertical_total': None,
            'vertical_total_reason': 'libxenon writes total_height-1 at 0x6010, absent from this capture; 0x6020 is deliberately zero.',
        },
        'comparisons': comparisons,
        'limitations': ['ANA read driver does not validate the SMC response status.', 'Zeros and equal registers are not a proof of board identity.', 'Actual pixel clock and refresh rate are not measured.'],
    }
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
