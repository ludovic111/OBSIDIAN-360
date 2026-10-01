#!/usr/bin/env python3
"""Trace real libxenon f1/f2 on the host. No device access, no mode installation."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess
import tempfile

STUB = r'''
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#define FB_BASE 0x1e000000
static unsigned reads, writes;
static void xenos_write32(int reg, uint32_t val) {
    if (reg < 0 || reg >= 0x10000 || reg % 4 || ++writes > 256) abort();
    printf("W %x %x\n", reg, val);
}
static uint32_t xenos_read32(int reg) {
    if (reg != DC_LUT_AUTOFILL || ++reads > 1) abort();
    return 2; /* Explicit simulation: LUT fill completes immediately. */
}
'''
MAIN = r'''
int main(void) {
    struct mode_s *families[] = {xenos_modes, xenos_modes_corona};
    size_t counts[] = {sizeof(xenos_modes)/sizeof(xenos_modes[0]),
                      sizeof(xenos_modes_corona)/sizeof(xenos_modes_corona[0])};
    for (unsigned f=0; f<2; f++) for (size_t i=0; i<counts[f]; i++) {
        struct mode_s *m = &families[f][i];
        reads=writes=0;
        printf("M %u %zu %d %d %d %d %d %s\n", f, i, m->width, m->height,
               m->total_width, m->total_height, m->is_progressive, m->name);
        xenos_set_mode_f1(m);
        xenos_set_mode_f2(m);
        printf("E %u %u\n", writes, reads);
    }
    return 0;
}
'''


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--source-dir', required=True, type=Path)
    p.add_argument('--capture', required=True, type=Path)
    p.add_argument('--output', required=True, type=Path)
    a = p.parse_args()
    files = {n: (a.source_dir/n).read_bytes() for n in
             ('xenos.c', 'xenos.h', 'xenos_videomodesdata.h')}
    files['xetypes.h'] = (a.source_dir.parent.parent/'include/xetypes.h').read_bytes()
    source = files['xenos.c'].decode()
    # Extract both functions verbatim, bounded by the next function declaration.
    functions = source[source.index('void xenos_set_mode_f1('):
                       source.index('void xenos_set_mode(struct mode_s *mode)')]
    definitions = '\n'.join(re.findall(
        r'^#define\s+\w+\s+0x[0-9a-fA-F]+\s*$', files['xenos.h'].decode(), re.M))
    generated = definitions+'\n'+STUB+'\n'+files['xenos_videomodesdata.h'].decode()+'\n'+functions+MAIN
    with tempfile.TemporaryDirectory(prefix='obsidian-video-') as tmp:
        c = Path(tmp)/'trace.c'
        exe = Path(tmp)/'trace'
        (Path(tmp)/'xetypes.h').write_bytes(files['xetypes.h'])
        c.write_text(generated)
        flags = ['-O0', '-g', '-fsanitize=address,undefined', '-fno-sanitize-recover=all']
        build = subprocess.run(['clang', *flags, '-I', tmp, str(c), '-o', str(exe)],
                               capture_output=True, text=True, timeout=45)
        if build.returncode:
            raise RuntimeError(build.stderr)
        run = subprocess.run([str(exe)], capture_output=True, text=True, timeout=15)
        if run.returncode or run.stderr:
            raise RuntimeError(f'trace failed: {run.returncode}\n{run.stderr}')
    modes = []
    for line in run.stdout.splitlines():
        if line.startswith('M '):
            _, fam, idx, w, h, ht, vt, prog, name = line.split(' ', 8)
            mode = dict(family=('standard', 'corona')[int(fam)], index=int(idx),
                        name=name, width=int(w), height=int(h), htotal=int(ht),
                        vtotal=int(vt), progressive=bool(int(prog)), writes=[])
            modes.append(mode)
        elif line.startswith('W '):
            _, reg, val = line.split()
            mode['writes'].append(dict(offset=f'0x{int(reg,16):04x}', value=f'0x{int(val,16):08x}'))
        elif line.startswith('E '):
            _, writes, reads = line.split()
            assert len(mode['writes']) == int(writes)
            mode['simulated_reads'] = int(reads)
        else:
            raise ValueError(line)
    capture_bytes = a.capture.read_bytes()
    capture = json.loads(capture_bytes)
    for mode in modes:
        final = {int(w['offset'], 16): int(w['value'], 16) for w in mode['writes']}
        mode['capture_comparison'] = []
        for name, reg in capture.items():
            value = final.get(int(reg['offset'], 16))
            mode['capture_comparison'].append(dict(
                name=name, offset=reg['offset'], captured=reg['value'],
                traced=None if value is None else f'0x{value:08x}',
                matches=None if value is None else value == int(reg['value'], 16)))
    report = dict(scope='Host execution of unmodified f1/f2; not GPU emulation or hardware validation.',
                  source_sha256={n: hashlib.sha256(b).hexdigest() for n, b in files.items()},
                  capture_sha256=hashlib.sha256(capture_bytes).hexdigest(),
                  harness_sha256=hashlib.sha256(generated.encode()).hexdigest(),
                  compiler=subprocess.check_output(['clang', '--version'], text=True).splitlines()[0],
                  flags=flags, compile_diagnostics=build.stderr,
                  limitations=['LUT completion is stubbed, not measured.',
                               'ANA/HANA programming, PLLs and other xenos_set_mode stages are not executed.',
                               'Captured registers are an earlier snapshot, not current console state.',
                               'The source revision is not proven identical to the installed XeLL binary.'],
                  modes=modes)
    a.output.parent.mkdir(parents=True, exist_ok=True)
    a.output.write_text(json.dumps(report, indent=2)+'\n')
    print(f'{len(modes)} modes traced; result: {a.output}')


if __name__ == '__main__':
    main()
