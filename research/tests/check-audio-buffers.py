#!/usr/bin/env python3
"""Exercise actual audio C buffer routines; substitute MMIO and cache instructions.

No console, DMA device, sound output or PowerPC cache instruction is accessed.
The bounded cache hook longjmps before a flush outside the requested span.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import tempfile


def function(source, name):
    match = re.search(r'^static (?:inline )?[\w *]+\b' + name + r'\([^;]*?\n\{', source, re.M)
    if not match:
        raise ValueError('Function absent: ' + name)
    end = source.index('\n}', match.end()) + 2
    return source[match.start():end]


PREFIX = r'''
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <setjmp.h>
#include <errno.h>
typedef uint32_t u32;
static jmp_buf escape;
static unsigned cache_calls, cache_limit, io_calls, allocation_calls, barriers;
static unsigned char memory[131072] __attribute__((aligned(128)));
static void cache_line(void *p) {
    if (++cache_calls > cache_limit) longjmp(escape, 1);
    if ((unsigned char *)p != memory + (cache_calls - 1) * 128) abort();
}
static void cache_barrier(void) {}
struct snd_pcm_runtime { uint64_t dma_addr; unsigned dma_bytes; void *dma_area; };
struct snd_pcm_substream { struct snd_pcm_runtime *runtime; unsigned buffer, period; };
struct snd_pcm_hw_params { int bytes; };
struct playback_device {
    struct snd_pcm_substream *playback_substream;
    void *dma_base_virt; unsigned descr_base_phys; u32 *descr_base_virt;
    int state, period_bytes, buffer_bytes, descr_bytes, gap, wptr;
};
struct snd_xenon { struct playback_device devices[2]; unsigned char *iobase_virt; int lock; };
static struct snd_xenon chip;
static struct snd_xenon *snd_pcm_substream_chip(struct snd_pcm_substream *s) { (void)s; return &chip; }
static int params_buffer_bytes(struct snd_pcm_hw_params *p) { return p->bytes; }
static int snd_pcm_lib_malloc_pages(struct snd_pcm_substream *s, int bytes) {
    ++allocation_calls; s->runtime->dma_bytes = bytes; return 1;
}
static unsigned snd_pcm_lib_buffer_bytes(struct snd_pcm_substream *s) { return s->buffer; }
static unsigned snd_pcm_lib_period_bytes(struct snd_pcm_substream *s) { return s->period; }
static void spin_lock_irq(int *lock) { (void)lock; }
static void spin_unlock_irq(int *lock) { (void)lock; }
static void *ioremap(unsigned addr, unsigned size) {
    (void)addr; if(size > 65536) abort(); ++io_calls; return memory;
}
static void writel(unsigned value, void *addr) { (void)value; (void)addr; if(MANAGED && !barriers) abort(); ++io_calls; }
static void dma_wmb(void) { ++barriers; }
#define DMA_BIT_MASK(n) ((1ULL<<(n))-1)
static void simulated_flush(void *addr, int bytes) { (void)addr; (void)bytes; }
#define DESCRIPTOR_BUFFER_SIZE 256
'''

MAIN = r'''
int main(int argc, char **argv) {
    if (argc != 2) return 2;
    int candidate = atoi(argv[1]);
    unsigned sizes[] = {64,68,128,132,192,256,65532,65536};
    unsigned cache_failures=0, tested=0, accepted=0, rejected=0, bad=0;
    unsigned first_bad=0, first_bad_word=0, out_of_span=0, split_frames=0, first_out_of_span=0, first_out_word=0;
#if HAS_CACHE
    for(unsigned i=0;i<sizeof(sizes)/sizeof(*sizes);i++) {
        cache_calls=0; cache_limit=(sizes[i]+127)/128;
        int overrun=setjmp(escape);
        if(!overrun) cache_flush(memory, sizes[i]);
        cache_failures += !!overrun;
        int expected = !candidate && sizes[i]%128;
        if(!!overrun != !!expected || (!overrun && cache_calls != cache_limit)) return 3;
    }
#else
    (void)sizes;
#endif
    unsigned char registers[64]={0}; u32 descriptors[64];
    struct snd_pcm_runtime runtime={.dma_addr=0x10000,.dma_area=memory};
    struct snd_pcm_substream sub={.runtime=&runtime};
    for(unsigned size=64;size<=65536;size+=4) {
        ++tested; io_calls=allocation_calls=barriers=0;
        struct snd_pcm_hw_params params={.bytes=(int)size};
        int expected_valid=!candidate || (size>=128 && size%128==0);
        int ret=snd_xenon_pcm_hw_params(&sub, &params);
        if(expected_valid ? ret!=(MANAGED?0:1) || allocation_calls!=(MANAGED?0:1) : ret!=-EINVAL || allocation_calls!=0) return 4;
        /* Also call prepare directly with rejected sizes, to test its own guard. */
        runtime.dma_bytes=size; sub.buffer=size; sub.period=size;
        memset(&chip,0,sizeof(chip)); memset(descriptors,0,sizeof(descriptors));
        chip.iobase_virt=registers;
        chip.devices[0].playback_substream=&sub;
        chip.devices[0].descr_base_virt=descriptors;
        ret=snd_xenon_playback_prepare(&sub);
        if(!expected_valid) {
            ++rejected; if(ret!=-EINVAL || io_calls) return 5; continue;
        }
        ++accepted; if(ret || !io_calls) return 6;
        uint64_t offset=0; int invalid=0, outside=0, unaligned=0;
        for(unsigned i=0;i<32;i++) {
            uint32_t address=bswap32(descriptors[2*i]);
            uint32_t word=bswap32(descriptors[2*i+1]);
            uint64_t length=(word & 0x7fffffffU)+1ULL;
            if(!(word & 0x80000000U) || address!=0x10000+offset ||
               length%4 || offset+length>size) invalid=1;
            if(offset+length>size) outside=1;
            if(length%4 || (address-0x10000)%4) unaligned=1;
            offset+=length;
        }
        if(offset!=size) invalid=outside=1;
        if(outside) { ++out_of_span; if(!first_out_of_span) { first_out_of_span=size; first_out_word=bswap32(descriptors[63]); } }
        split_frames += unaligned;
        if(invalid) { ++bad; if(!first_bad) {first_bad=size;first_bad_word=bswap32(descriptors[63]);} }
    }
    /* Defensive check: prepare must reject runtime/ALSA size disagreement. */
    if(candidate) {
        sub.buffer=256; runtime.dma_bytes=128; io_calls=0;
        if(snd_xenon_playback_prepare(&sub)!=-EINVAL || io_calls) return 7;
    }
    printf("{\"tested_sizes\":%u,\"accepted\":%u,\"rejected\":%u,"
           "\"invalid_descriptor_geometries\":%u,\"first_invalid_size\":%u,"
           "\"first_invalid_last_word\":%u,\"cache_cases\":%u,\"cache_span_overruns\":%u,\"descriptor_out_of_span\":%u,\"split_frame_geometries\":%u,\"first_out_of_span_size\":%u,\"first_out_of_span_last_word\":%u}\n",
           tested,accepted,rejected,bad,first_bad,first_bad_word,HAS_CACHE?8:0,cache_failures,out_of_span,split_frames,first_out_of_span,first_out_word);
    return candidate ? (bad || accepted!=512 || cache_failures) : (!bad || cache_failures!=5);
}
'''


def harness(source):
    managed = 'snd_pcm_set_managed_buffer_all' in source
    has_cache = 'static void cache_flush(' in source
    if not has_cache and ('cache_flush(' in source or not managed):
        raise ValueError('Unexpected partial cache removal')
    cache = function(source, 'cache_flush') if has_cache else ''
    cache, n = re.subn(r'__asm__ __volatile__ \("dcbst 0,%0" :: "r" \(p\)\);', 'cache_line(p);', cache)
    if has_cache and n != 1:
        raise ValueError('Unexpected cache instruction')
    cache, n = re.subn(r'__asm__ __volatile__ \("sync" ::: "memory"\);', 'cache_barrier();', cache)
    if has_cache and n != 1:
        raise ValueError('Unexpected barrier')
    prepare = function(source, 'snd_xenon_playback_prepare').replace('cache_flush(', 'simulated_flush(')
    return '#define MANAGED '+str(int(managed))+'\n#define HAS_CACHE '+str(int(has_cache))+'\n' + PREFIX + cache + '\n' + function(source, 'bswap32') + '\n' + function(source, 'snd_xenon_pcm_hw_params') + '\n' + prepare + MAIN


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--original', type=Path, required=True)
    parser.add_argument('--candidate', type=Path, required=True)
    args = parser.parse_args()
    results = []
    with tempfile.TemporaryDirectory(prefix='obsidian-audio-') as tmp:
        for name, path in [('original', args.original), ('candidate', args.candidate)]:
            source = Path(tmp) / (name + '.c')
            binary = Path(tmp) / name
            source.write_text(harness(path.read_text()))
            build = subprocess.run(['clang', '-std=gnu11', '-O0', '-g', '-Wall', '-Wextra', '-Werror', '-Wno-unused-function', '-Wno-unused-variable', '-Wno-unused-parameter', '-fsanitize=address,undefined', str(source), '-o', str(binary)], capture_output=True, text=True, timeout=30)
            if build.returncode:
                raise RuntimeError(build.stderr)
            test = subprocess.run([str(binary), '1' if name == 'candidate' else '0'], capture_output=True, text=True, timeout=30, env=dict(os.environ, ASAN_OPTIONS='detect_leaks=0:halt_on_error=1', UBSAN_OPTIONS='halt_on_error=1'))
            results.append({'variant': name, 'source_sha256': hashlib.sha256(path.read_bytes()).hexdigest(), 'returncode': test.returncode, 'result': json.loads(test.stdout) if test.stdout else None, 'diagnostics': test.stderr.replace(tmp, 'HOST_TEST')})
    print(json.dumps({'scope': 'Actual extracted C; hardware/cache instructions replaced; cache span watchdog; all four-byte frame sizes 64..65536. No ALSA negotiation or hardware validation.', 'results': results}, indent=2))
    if any(r['returncode'] or r['diagnostics'] for r in results):
        raise SystemExit(1)


if __name__ == '__main__':
    main()
