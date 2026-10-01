#!/usr/bin/env python3
"""Convert a TrueColor XWD screen capture to PNG using only the standard library."""
import struct, sys, zlib
from pathlib import Path

data=Path(sys.argv[1]).read_bytes()
h=struct.unpack('>25I',data[:100])
header,version,fmt,depth,w,height,xoffset,order,unit,bitorder,pad,bpp,stride,visual,red,green,blue,bits,entries,ncolors,*_=h
assert version==7 and fmt==2 and bpp in (16,24,32) and xoffset==0
offset=header+ncolors*12
assert len(data)>=offset+height*stride
def shift(mask): return (mask&-mask).bit_length()-1
channels=[(mask,shift(mask)) for mask in (red,green,blue)]
raw=bytearray()
for y in range(height):
    raw.append(0)
    row=data[offset+y*stride:offset+(y+1)*stride]
    for x in range(w):
        pixel=int.from_bytes(row[x*(bpp//8):(x+1)*(bpp//8)],'little' if order==0 else 'big')
        raw.extend(((pixel&mask)>>s)*255//(mask>>s) for mask,s in channels)
def chunk(kind,payload):
    return struct.pack('>I',len(payload))+kind+payload+struct.pack('>I',zlib.crc32(kind+payload)&0xffffffff)
png=b'\x89PNG\r\n\x1a\n'+chunk(b'IHDR',struct.pack('>2I5B',w,height,8,2,0,0,0))+chunk(b'IDAT',zlib.compress(raw))+chunk(b'IEND',b'')
Path(sys.argv[2]).write_bytes(png)
print(f'{w}x{height}, depth={depth}, {len(png)} PNG bytes')
