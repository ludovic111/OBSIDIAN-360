#!/usr/bin/env python3
"""Test the actual observer address calculation without mapping hardware."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import tempfile

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--output', type=Path, required=True)
args = parser.parse_args()
source = Path(__file__).resolve().parents[1] / 'audio/read_status_once.c'
harness = r'''
#define main observer_main
#include "read_status_once.c"
#undef main
#include <assert.h>
int main(void) {
    size_t offset = 999;
    unsigned cases = 0;
    for (long page = 4096; page <= 65536; page *= 2) {
        for (unsigned low = 0; low < (unsigned)page; low += 4) {
            uint64_t start = UINT64_C(0x200ea000000) + low;
            offset = 999;
            int rc = bar_offset(start, start + 63, page, &offset);
            if (low + 64 <= (unsigned)page) {
                assert(rc == 0 && offset == low);
                assert((start & ~((uint64_t)page - 1)) + offset + 0x18 == start + 0x18);
            } else { assert(rc == -1 && offset == 999); }
            ++cases;
        }
    }
    assert(bar_offset(UINT64_C(0x200ea001600), UINT64_C(0x200ea00163f), 65536, &offset) == 0);
    assert(offset == 0x1600);
    const long invalid[] = {-1, 0, 3, 65535};
    for (unsigned i = 0; i < sizeof(invalid)/sizeof(invalid[0]); ++i)
        assert(bar_offset(0,63,invalid[i],&offset) == -1);
    assert(bar_offset(1,64,65536,&offset) == -1);
    assert(bar_offset(100,99,65536,&offset) == -1);
    assert(bar_offset(0,62,65536,&offset) == -1);
    printf("{\"aligned_geometry_cases\":%u,\"invalid_cases\":7,\"console_offset\":5632}\n", cases);
    return 0;
}
'''
with tempfile.TemporaryDirectory(prefix='obsidian-observer-') as tmp:
    tmp = Path(tmp)
    (tmp/'test.c').write_text(harness)
    cmd=['clang','-std=c11','-Wall','-Wextra','-Werror','-fsanitize=address,undefined','-I',str(source.parent),str(tmp/'test.c'),'-o',str(tmp/'test')]
    build=subprocess.run(cmd,capture_output=True,text=True)
    if build.returncode: raise RuntimeError(build.stderr)
    run=subprocess.run([str(tmp/'test')],capture_output=True,text=True,check=True)
    report={'scope':'Actual pure address calculation, no hardware access; ASan/UBSan','source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'result':json.loads(run.stdout),'stderr':run.stderr}
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report))
