#!/usr/bin/env python3
"""Compare ELF payload sections without executing either kernel image."""
import argparse
import hashlib
import json
from pathlib import Path
import struct


def sections(data):
    if len(data) < 64 or data[:4] != b'\x7fELF' or data[4] not in (1,2) or data[5] not in (1,2):
        raise ValueError('Unsupported or truncated ELF header')
    order = '>' if data[5] == 2 else '<'
    is64 = data[4] == 2
    offset = struct.unpack_from(order+('Q' if is64 else 'I'),data,40 if is64 else 32)[0]
    stride,count,names = struct.unpack_from(order+'HHH',data,58 if is64 else 46)
    fmt=order+('IIQQQQIIQQ' if is64 else 'IIIIIIIIII')
    if not count or count>8192 or names>=count or stride<struct.calcsize(fmt) or offset+stride*count>len(data):
        raise ValueError('Invalid section table; extended indexes not supported')
    headers=[struct.unpack_from(fmt,data,offset+i*stride) for i in range(count)]
    def contents(header):
        start,size=header[4],header[5]
        if start+size>len(data):raise ValueError('Section outside input')
        return data[start:start+size]
    strings=contents(headers[names]);result={}
    for header in headers:
        end=strings.find(b'\0',header[0])
        if end<0:raise ValueError('Invalid section name')
        name=strings[header[0]:end].decode('ascii')
        if name and header[1]!=8:result[name]=contents(header)
    return result


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('symbol_image',type=Path)
    parser.add_argument('boot_image',type=Path)
    args=parser.parse_args()
    a=args.symbol_image.read_bytes();b=args.boot_image.read_bytes()
    sa,sb=sections(a),sections(b)
    selected=['.head.text','.text','.rodata','.init.text','.data','.notes']
    comparisons={}
    for name in selected:
        if name not in sa or name not in sb:raise ValueError('Missing required section '+name)
        comparisons[name]={'identical':sa[name]==sb[name], 'symbol_bytes':len(sa[name]), 'boot_bytes':len(sb[name]), 'symbol_sha256':hashlib.sha256(sa[name]).hexdigest(), 'boot_sha256':hashlib.sha256(sb[name]).hexdigest()}
    print(json.dumps({'symbol_image_sha256':hashlib.sha256(a).hexdigest(),'boot_image_sha256':hashlib.sha256(b).hexdigest(),'symbol_elf_class':a[4],'boot_elf_class':b[4],'sections':comparisons},indent=2))
    if not all(entry['identical'] for entry in comparisons.values()):raise SystemExit(1)


if __name__=='__main__':main()
