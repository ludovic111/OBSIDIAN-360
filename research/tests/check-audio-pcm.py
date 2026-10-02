#!/usr/bin/env python3
"""Run actual PCM callbacks against managed-memory/register/constraint models.

Serial execution only. No real ALSA negotiation, device, cache or DMA operations.
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
    match=re.search(r'^static (?:inline )?[\w *]+\b'+name+r'\([^;]*?\n\{',source,re.M)
    if not match:raise ValueError(name)
    return source[match.start():source.index('\n}',match.end())+2]


PREFIX=r'''
#include <stdint.h>
#include <stdbool.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <errno.h>
typedef uint32_t u32;typedef uint64_t dma_addr_t;typedef unsigned long snd_pcm_uframes_t;typedef int spinlock_t;
struct timer_list {int unused;};struct snd_xenon;
typedef uint64_t u64;typedef int64_t s64;typedef int64_t ktime_t;
struct hrtimer {int initialized,pending;};
static int high_resolution=1;
static int hrtimer_is_hres_active(struct hrtimer *t){(void)t;return high_resolution;}
#define HRTIMER_MODE_REL_SOFT 1
#define XENON_POLL_NS 200000
static ktime_t ktime_get(void){return 0;}
static ktime_t ns_to_ktime(int64_t ns){return ns;}
struct snd_pcm_hardware {int token;};
struct control {unsigned long appl_ptr;};
struct snd_pcm_runtime {struct snd_pcm_hardware hw;void *dma_area;dma_addr_t dma_addr;unsigned dma_bytes;struct control *control;};
struct snd_pcm_substream {struct snd_pcm_runtime *runtime;unsigned buffer,period;};
struct snd_pcm_hw_params {int bytes;};
static struct snd_xenon *shared_chip;
static unsigned char registers[64];
static unsigned barriers,writes,reads,constraints;static int fail_constraint,locked,active[2];
#define CHECK(c) do {if(!(c)){fprintf(stderr,"MODEL_ASSERT:%s\n",#c);exit(97);}}while(0)
#define DESCRIPTOR_BUFFER_SIZE 256
#define DMA_BIT_MASK(n) ((1ULL<<(n))-1)
#define SNDRV_PCM_HW_PARAM_BUFFER_BYTES 17
#define SNDRV_PCM_TRIGGER_START 1
#define SNDRV_PCM_TRIGGER_STOP 0
static struct snd_xenon *snd_pcm_substream_chip(struct snd_pcm_substream *s){(void)s;return shared_chip;}
static void spin_lock_irq(spinlock_t *p){(void)p;CHECK(!locked);locked=1;}
static void spin_unlock_irq(spinlock_t *p){(void)p;CHECK(locked);locked=0;}
#define spin_lock spin_lock_irq
#define spin_unlock spin_unlock_irq
#define spin_lock_irqsave(p,f) do {(f)=0;spin_lock_irq(p);}while(0)
#define spin_unlock_irqrestore(p,f) do {(void)(f);spin_unlock_irq(p);}while(0)
static void hrtimer_start(struct hrtimer *t,ktime_t delay,int mode){(void)delay;(void)mode;CHECK(t->initialized);t->pending=1;}
static int hrtimer_cancel(struct hrtimer *t){CHECK(!locked && t->initialized);t->pending=0;return 0;}
static unsigned snd_pcm_lib_buffer_bytes(struct snd_pcm_substream *s){return s->buffer;}
static unsigned snd_pcm_lib_period_bytes(struct snd_pcm_substream *s){return s->period;}
static int params_buffer_bytes(struct snd_pcm_hw_params *p){return p->bytes;}
static unsigned long frames_to_bytes(struct snd_pcm_runtime *r,unsigned long frames){(void)r;return frames*4;}
static unsigned long bytes_to_frames(struct snd_pcm_runtime *r,unsigned long bytes){(void)r;return bytes/4;}
static void dma_wmb(void){++barriers;}
static unsigned offset(void *p){CHECK(p>=(void *)registers && p<(void *)(registers+sizeof(registers)));return (unsigned)((unsigned char *)p-registers);}
static void writel(u32 value,void *p){
    unsigned off=offset(p);CHECK(locked);++writes;
    if(off==0 || off==0x10)CHECK(barriers);
    if(off==8 || off==0x18){active[off==0x18]=!!(value & 0x1000000);if(active[off==0x18])CHECK(barriers);}
    memcpy(registers+off,&value,4);
}
static u32 readl(void *p){u32 value;unsigned off=offset(p);CHECK(locked);++reads;memcpy(&value,registers+off,4);return value;}
static int snd_pcm_hw_constraint_minmax(struct snd_pcm_runtime *r,int param,unsigned min,unsigned max){
    (void)r;CHECK(param==SNDRV_PCM_HW_PARAM_BUFFER_BYTES && min==128 && max==65536);++constraints;return fail_constraint==(int)constraints?-ENOMEM:0;
}
static int snd_pcm_hw_constraint_step(struct snd_pcm_runtime *r,unsigned cond,int param,unsigned long step){
    (void)r;CHECK(!cond && param==SNDRV_PCM_HW_PARAM_BUFFER_BYTES && step==128);++constraints;return fail_constraint==(int)constraints?-ENOMEM:0;
}
/* Mapping/free helpers deliberately absent: using them would fail compilation. */
'''

MAIN=r'''
int main(int argc,char **argv){
    if(argc!=2)return 2;
    const char *test=argv[1];struct snd_xenon chip={0};shared_chip=&chip;
    u32 descriptors[128]={0};chip.descr_base_virt=descriptors;chip.descr_base_phys=0x8000;chip.iobase_virt=registers;
    struct control controls[2]={{0},{0}};
    struct snd_pcm_runtime runtime[2]={{.dma_addr=0x10000,.dma_bytes=65536,.control=&controls[0]},{.dma_addr=0x30000,.dma_bytes=128,.control=&controls[1]}};
    struct snd_pcm_substream subs[2]={{.runtime=&runtime[0],.buffer=65536,.period=4096},{.runtime=&runtime[1],.buffer=128,.period=64}};
    struct snd_pcm_hardware hw={.token=42};
#if HAS_POLL
    for(unsigned i=0;i<2;i++){chip.devices[i].chip=&chip;chip.devices[i].dev_id=i;chip.devices[i].timer.initialized=1;}
#endif
    if(!strcmp(test,"coarse_timer"))high_resolution=0;
    if(!strcmp(test,"constraint_first"))fail_constraint=1;
    if(!strcmp(test,"constraint_second"))fail_constraint=2;
    int code=snd_xenon_playback_open(&subs[0],0,&hw);
    if(!high_resolution){CHECK(code==-ENODEV && !writes && !constraints);return 0;}
    if(fail_constraint){CHECK(code==-ENOMEM && writes==0 && !chip.devices[0].playback_substream);return 0;}
    CHECK(code==0 && constraints==2 && runtime[0].hw.token==42);
    CHECK(snd_xenon_playback_open(&subs[1],1,&hw)==0 && constraints==4);
    unsigned char *allocations[2];
    for(unsigned i=0;i<2;i++){
        allocations[i]=malloc(runtime[i].dma_bytes+32);CHECK(allocations[i]);memset(allocations[i],0xa5,runtime[i].dma_bytes+32);
        runtime[i].dma_area=allocations[i]+16;
        struct snd_pcm_hw_params params={.bytes=(int)runtime[i].dma_bytes};CHECK(snd_xenon_pcm_hw_params(&subs[i],&params)==0);
    }
    unsigned long saved_addr=runtime[0].dma_addr;void *saved_area=runtime[0].dma_area;
    if(!strcmp(test,"no_area"))runtime[0].dma_area=NULL;
    if(!strcmp(test,"zero_period"))subs[0].period=0;
    if(!strcmp(test,"large_period"))subs[0].period=65540;
    if(!strcmp(test,"short_buffer")){runtime[0].dma_bytes=64;subs[0].buffer=64;}
    if(!strcmp(test,"unaligned_size")){runtime[0].dma_bytes=132;subs[0].buffer=132;}
    if(!strcmp(test,"mismatched_size"))subs[0].buffer=128;
    if(!strcmp(test,"address_high"))runtime[0].dma_addr=1ULL<<29;
    if(!strcmp(test,"address_crossing"))runtime[0].dma_addr=(1ULL<<29)-32768;
    if(!strcmp(test,"address_overflow"))runtime[0].dma_addr=UINT64_MAX;
    if(!strcmp(test,"unknown_stream"))chip.devices[0].playback_substream=NULL;
    writes=reads=barriers=0;
    if(strcmp(test,"normal") && strcmp(test,"repeat_prepare")){
        CHECK(snd_xenon_playback_prepare(&subs[0])==-EINVAL);CHECK(writes==0 && barriers==0 && !locked);
        runtime[0].dma_addr=saved_addr;runtime[0].dma_area=saved_area;
    }else{
        unsigned repeats=!strcmp(test,"repeat_prepare")?10:1;
        for(unsigned n=0;n<repeats;n++){
            memset(runtime[0].dma_area,0xa5,runtime[0].dma_bytes);barriers=0;
            CHECK(snd_xenon_playback_prepare(&subs[0])==0 && barriers==1);
            for(unsigned j=0;j<65536;j++)CHECK(((unsigned char *)runtime[0].dma_area)[j]==0);
            for(unsigned j=0;j<16;j++)CHECK(allocations[0][j]==0xa5 && allocations[0][65552+j]==0xa5);
        }
        CHECK(snd_xenon_playback_prepare(&subs[1])==0);
        barriers=0;CHECK(snd_xenon_trigger(&subs[0],SNDRV_PCM_TRIGGER_START)==0 && active[0] && barriers==1);
        CHECK(snd_xenon_trigger(&subs[1],SNDRV_PCM_TRIGGER_START)==0 && active[1]);
        u32 status=5;memcpy(registers+4,&status,4);controls[0].appl_ptr=512;
        CHECK(snd_xenon_pointer(&subs[0])==2560);
        CHECK(snd_xenon_pcm_hw_free(&subs[0])==0 && !active[0] && active[1]);
        /* Simulate ALSA freeing after hw_free; the driver must not free it. */
        free(allocations[0]);allocations[0]=NULL;runtime[0].dma_area=NULL;runtime[0].dma_bytes=0;
        CHECK(snd_xenon_pointer(&subs[0])==0);
        unsigned old_writes=writes;CHECK(snd_xenon_trigger(&subs[0],SNDRV_PCM_TRIGGER_START)==-EINVAL && writes==old_writes);
    }
    CHECK(snd_xenon_playback_close(&subs[0])==0 && !chip.devices[0].playback_substream);
    CHECK(snd_xenon_playback_close(&subs[1])==0 && !chip.devices[1].playback_substream);
    CHECK(!active[0] && !active[1] && !locked);
    free(allocations[0]);free(allocations[1]);
    printf("%s: managed CPU mapping, bounds, barriers and serial callback cleanup passed\n",test);
    return 0;
}
'''


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--source',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    source=a.source.read_text();structs=source[source.index('struct playback_device {'):source.index('static inline u32 bswap32')]
    poll='struct hrtimer timer;' in source
    names=['bswap32','snd_xenon_playback_open','snd_xenon_pcm_hw_params','snd_xenon_pcm_hw_free','snd_xenon_playback_close','snd_xenon_playback_prepare','snd_xenon_trigger','snd_xenon_pointer']
    if poll:names=['snd_xenon_position','snd_xenon_sync_stop']+names
    cases=['constraint_first','constraint_second','no_area','short_buffer','unaligned_size','mismatched_size','address_high','address_crossing','address_overflow','unknown_stream','normal','repeat_prepare']
    if poll:cases+=['zero_period','large_period','coarse_timer']
    report={'scope':'Actual PCM callbacks, coherent CPU area and managed allocation modeled; no real ALSA refinement, DMA/coherency, timers or concurrent callbacks. Descriptor encoding remains the historical Linux model.','source_sha256':hashlib.sha256(a.source.read_bytes()).hexdigest(),'cases':[]}
    with tempfile.TemporaryDirectory(prefix='obsidian-pcm-') as tmp:
        src=Path(tmp)/'test.c';binary=Path(tmp)/'test';src.write_text('#define HAS_POLL '+str(int(poll))+'\n'+PREFIX+structs+'\n'.join(function(source,n) for n in names)+MAIN)
        build=subprocess.run(['clang','-std=gnu11','-O1','-g','-Wall','-Wextra','-Werror','-Wno-unused-parameter','-Wno-unused-function','-fsanitize=address,undefined',str(src),'-o',str(binary)],capture_output=True,text=True,timeout=30)
        report['compile']={'code':build.returncode,'diagnostics':build.stderr.replace(tmp,'HOST_TEST')}
        if build.returncode==0:
            for case in cases:
                r=subprocess.run([str(binary),case],capture_output=True,text=True,timeout=10,env=dict(os.environ,ASAN_OPTIONS='detect_leaks=0:halt_on_error=1',UBSAN_OPTIONS='halt_on_error=1'))
                report['cases'].append({'name':case,'code':r.returncode,'stdout':r.stdout.strip(),'diagnostics':r.stderr.replace(tmp,'HOST_TEST')})
    report['passed']=report['compile']['code']==0 and len(report['cases'])==len(cases) and all(c['code']==0 and not c['diagnostics'] for c in report['cases'])
    a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({'passed':report['passed'],'cases':len(report['cases']),'failed':[c['name'] for c in report['cases'] if c['code']]}));raise SystemExit(0 if report['passed'] else 1)


if __name__=='__main__':main()
