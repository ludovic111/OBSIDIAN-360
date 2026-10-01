#!/usr/bin/env python3
"""Exercise real upstream C on the host with mocked hardware and AddressSanitizer.

No network or device access. Inputs are local source files; no Xbox deployment.
The graphics test extracts the upstream blitter unchanged. The XeLL test compiles
the complete upstream HTTP flash handler with a simulated 528-byte raw page.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import tempfile

GRAPHICS_HEADER = r'''
#include <stdint.h>
#include <stdlib.h>
#include <stdio.h>
#include <string.h>
typedef uint32_t u32;
struct iosys_map { void *vaddr; };
struct drm_rect { int x1, y1, x2, y2; };
struct drm_framebuffer { int width; int pitches[1]; };
#define swab32 __builtin_bswap32
'''
GRAPHICS_MAIN = r'''
int main(int argc, char **argv) {
    if (argc != 4) return 2;
    int w=atoi(argv[1]), h=atoi(argv[2]), padded=atoi(argv[3]);
    if (w<=0 || h<=0 || w%32 || w>4096 || h>4096) return 3;
    size_t linear=(size_t)w*h*4;
    size_t bytes=padded ? (size_t)((w+31)&~31)*((h+31)&~31)*4 : linear;
    struct iosys_map src={malloc(linear)}, dst={malloc(bytes)};
    if (!src.vaddr || !dst.vaddr) return 4;
    memset(src.vaddr, 0x5a, linear); memset(dst.vaddr, 0, bytes);
    struct drm_rect rect={0,0,w,h};
    struct drm_framebuffer fb={w,{w*4}};
    xenos_blit(dst,src,rect,&fb);
    printf("blit completed: %dx%d, allocation=%zu\n",w,h,bytes);
    free(src.vaddr); free(dst.vaddr); return 0;
}
'''
XELL_HEADER = r'''
#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#include <stdint.h>
#define SFCX_INITIALIZED 1
#define HTTPD_SERVER_CLOSE 2
#define MMC_FLASH_SIZE 0x3000000
struct http_state { void *response_priv; int code; };
struct sfc { int initialized, size_pages, page_sz_phys, page_sz; };
struct sfc sfc={SFCX_INITIALIZED,2,528,512};
static int sent=0, reads=0, bad=0;
static void *mem_malloc(size_t n) { return malloc(n); }
static void mem_free(void *p) { free(p); }
static int httpd_available_sendbuffer(struct http_state *s) { return 1056; }
static void httpd_put_sendbuffer_string(struct http_state *s,const char *v) {}
static int httpd_do_std_header(struct http_state *s) { return 0; }
static void httpd_put_sendbuffer(struct http_state *s,void *p,int n) {
    if (n!=528) bad=1;
    for(int i=0;i<n;i++) if(((unsigned char*)p)[i]!=(unsigned char)(reads-1)) bad=1;
    sent+=n;
}
static int sfcx_read_page(unsigned char *p,int address,int raw) {
    if(!raw || address!=reads*512) bad=1;
    memset(p,reads,528); reads++; return 0;
}
static void xenon_get_logical_nand_data(void *p,int a,int n) { memset(p,0,n); }
'''
XELL_MAIN = r'''
int main(void) {
    struct http_state state={0};
    if(response_flash_process_request(&state,"GET","/FLASH")!=1 || state.code!=200) return 2;
    if(response_flash_do_data(&state)!=0) return 3;
    response_flash_finish(&state);
    if(reads!=2 || sent!=1056 || bad) return 4;
    printf("two raw pages transferred: %d bytes\n",sent); return 0;
}
'''


def build_and_run(directory, name, source, args, expect_failure):
    path = directory / (name + '.c')
    path.write_text(source)
    binary = directory / name
    build = subprocess.run(['clang', '-std=gnu11', '-O0', '-g', '-fsanitize=address', '-fno-omit-frame-pointer', '-I', str(directory), str(path), '-o', str(binary)], capture_output=True, text=True, timeout=60)
    if build.returncode:
        raise RuntimeError(build.stderr)
    env = dict(os.environ, ASAN_OPTIONS='detect_leaks=0:halt_on_error=1:abort_on_error=0')
    run = subprocess.run([str(binary), *args], capture_output=True, text=True, timeout=20, env=env)
    findings = re.findall(r'(?:ERROR|SUMMARY): AddressSanitizer: [^\n]+', run.stderr)
    valid = run.returncode != 0 and bool(findings) if expect_failure else run.returncode == 0 and not findings
    result = {'case': name, 'passed': valid, 'returncode': run.returncode, 'expected_sanitizer_failure': expect_failure, 'diagnostics': findings, 'stdout': run.stdout.strip()}
    # Host temporary paths carry no analytical value.
    result['diagnostics'] = [line.replace(str(directory), 'HOST_TEST') for line in findings]
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--xenos', type=Path, required=True)
    parser.add_argument('--xell', type=Path, required=True)
    args = parser.parse_args()
    xenos = args.xenos.read_text()
    blitter = xenos[xenos.index('static void xenos_blit('):xenos.index('static void xenos_update(')]
    xell = args.xell.read_text()
    needle = 'unsigned char buffer[sfc.page_sz];'
    if xell.count(needle) != 1:
        raise ValueError('Unexpected XeLL source; re-audit before testing')
    if 'xenos->real_framebuffer.size = width * height * cpp;' not in xenos:
        raise ValueError('Unexpected graphics allocation; re-audit before testing')
    cases = []
    with tempfile.TemporaryDirectory(prefix='obsidian-asan-') as tmp:
        directory = Path(tmp)
        for w,h in [(640,480),(1280,720),(1920,1080),(1280,768)]:
            for padded in (0,1):
                cases.append(build_and_run(directory, f'xenos_{w}x{h}_padded{padded}', GRAPHICS_HEADER+blitter+GRAPHICS_MAIN, [str(w),str(h),str(padded)], not padded and h%32!=0))
        for header in re.findall(r'#include [<"]([^>"]+)[>"]', xell):
            if header in ('string.h','stdio.h'):
                continue
            target=directory/header
            target.parent.mkdir(parents=True,exist_ok=True)
            target.write_text('/* Interface supplied by the host test harness. */\n')
        for fixed in (False,True):
            code=xell.replace(needle,'unsigned char buffer[sfc.page_sz_phys];') if fixed else xell
            cases.append(build_and_run(directory, f'xell_fixed{int(fixed)}', XELL_HEADER+code+XELL_MAIN, [], not fixed))
    report = {
        'scope': 'Actual upstream C, host ASan, mocked hardware; no deployed binary or hardware validation',
        'xenos_sha256': hashlib.sha256(args.xenos.read_bytes()).hexdigest(),
        'xell_sha256': hashlib.sha256(args.xell.read_bytes()).hexdigest(),
        'compiler': subprocess.check_output(['clang','--version'],text=True).splitlines()[0],
        'cases':cases,
    }
    print(json.dumps(report,indent=2))
    if not all(case['passed'] for case in cases):
        raise SystemExit(1)


if __name__ == '__main__':
    main()
