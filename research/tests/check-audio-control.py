#!/usr/bin/env python3
"""Exercise actual START/STOP/prepare under an explicitly assumed SiS W1C model."""
import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import tempfile

BASE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('adapter',BASE/'check-audio-adapter.py')
adapter=importlib.util.module_from_spec(spec);spec.loader.exec_module(adapter)

MAIN=r'''
int main(void){
    struct snd_xenon chip={0};shared_chip=&chip;chip.iobase_virt=registers;
    struct control controls[2]={{0},{0}};struct status statuses[2]={{0},{0}};
    struct snd_pcm_runtime runtime[2]={0};struct snd_pcm_substream subs[2]={0};
    unsigned char memory[2][4096];u32 descriptors[128]={0};
    for(unsigned id=0;id<2;id++){
        runtime[id]=(struct snd_pcm_runtime){.control=&controls[id],.status=&statuses[id],.boundary=1UL<<40,.buffer_size=1024,.dma_area=memory[id],.dma_bytes=4096,.dma_addr=0x10000+id*4096};
        subs[id]=(struct snd_pcm_substream){.runtime=&runtime[id],.buffer=4096,.period=512};
        struct playback_device *d=&chip.devices[id];d->chip=&chip;d->dev_id=id;d->timer.initialized=1;d->playback_substream=&subs[id];d->descr_base_virt=descriptors+id*64;d->descr_base_phys=0x8000+id*256;
    }
    unsigned transitions=0,cleared=0,irq_enabled=0;
    for(unsigned id=0;id<2;id++)for(unsigned prefetched=0;prefetched<32;prefetched++)for(unsigned pending=0;pending<32;pending++){
        struct playback_device *d=&chip.devices[id];struct snd_pcm_substream *s=&subs[id];unsigned off=8+id*16;
        u32 injected=(prefetched<<16)|pending;memcpy(registers+off,&injected,4);
        CHECK(snd_xenon_playback_prepare(s)==0);u32 value;memcpy(&value,registers+off,4);
        CHECK((value&0x1c)==0 && (value&3)==(pending&3));
        CHECK(((value>>16)&31)==prefetched); /* PIV is read-only in this model. */
#if PREVIOUS
        CHECK((value&0x1c000000)==0x1c000000);
#else
        CHECK(!(value&0x1c000000));
#endif
        controls[id].appl_ptr=1024;CHECK(snd_xenon_ack(s)==0);
        /* Simulate a latched status arriving after preparation. */
        injected=0x1c000000|(prefetched<<16)|pending;memcpy(registers+off,&injected,4);
        u32 other;memcpy(&other,registers+8+(1-id)*16,4);
        CHECK(snd_xenon_trigger(s,SNDRV_PCM_TRIGGER_START)==0);
        memcpy(&value,registers+off,4);CHECK(value&0x01000000);
        CHECK(((value>>16)&31)==prefetched && (value&3)==(pending&3));
#if PREVIOUS
        CHECK(!(value&0x1c) && (value&0x1c000000)==0x1c000000);
#else
        CHECK((value&0x1c)==(pending&0x1c) && !(value&0x1c000000));
#endif
        cleared+=((pending&0x1c)!=(value&0x1c));irq_enabled+=!!(value&0x1c000000);++transitions;
        u32 other_after;memcpy(&other_after,registers+8+(1-id)*16,4);CHECK(other==other_after);
        injected=0x1d000000|(prefetched<<16)|pending;memcpy(registers+off,&injected,4);
        CHECK(snd_xenon_trigger(s,SNDRV_PCM_TRIGGER_STOP)==0);memcpy(&value,registers+off,4);CHECK(!(value&0x01000000));
#if PREVIOUS
        CHECK(!(value&0x1c) && (value&0x1c000000)==0x1c000000);
#else
        CHECK((value&0x1c)==(pending&0x1c) && !(value&0x1c000000));
#endif
        CHECK(((value>>16)&31)==prefetched && (value&3)==(pending&3));
        cleared+=((pending&0x1c)!=(value&0x1c));irq_enabled+=!!(value&0x1c000000);++transitions;
        CHECK(snd_xenon_sync_stop(s)==0 && !d->timer.pending);
    }
    printf("{\"channels\":2,\"prefetch_values\":32,\"status_values\":32,\"transitions\":%u,\"transitions_clearing_pending_status\":%u,\"transitions_with_interrupts_enabled\":%u}\n",transitions,cleared,irq_enabled);
    return 0;
}
'''


def harness(source,core,native):
    s=adapter.harness(source,core,native);assert s.endswith(adapter.MAIN);s=s[:-len(adapter.MAIN)]
    old='    memcpy(registers+off,&value,4);'
    assert s.count(old)==1
    new='''    if(off==8 || off==0x18){
        u32 before;memcpy(&before,registers+off,4);
        /* SR low16: only bits 2..4 writable, and one clears. PIV read-only.
         * CR high8 stores requested controls. Other hardware effects are not
         * modeled; status fields are supplied explicitly by the test. */
        value=(value&0xff000000U)|(before&0x00ff0000U)|((before&0xffffU)&~(value&0x1cU));
    }
    memcpy(registers+off,&value,4);'''
    return s.replace(old,new)+MAIN


def main():
    p=argparse.ArgumentParser(description=__doc__)
    for n in ['previous','candidate','kernel','output']:p.add_argument('--'+n,type=Path,required=True)
    a=p.parse_args();root=BASE.parent.parent
    core=(a.kernel/'sound/core/pcm_lib.c').read_text();native=(a.kernel/'sound/core/pcm_native.c').read_text()
    report={'scope':'Actual prepare, ack, START and STOP; assumed SiS W1C/RO/CR behavior with injected status, not measured Xenon behavior. No DMA, FIFO drain, electrical or hardware validation.','variants':[]}
    with tempfile.TemporaryDirectory(prefix='obsidian-control-') as tmp:
        for label,path,previous in [('previous',a.previous,1),('candidate',a.candidate,0)]:
            src=Path(tmp)/(label+'.c');binary=Path(tmp)/label;src.write_text('#define PREVIOUS '+str(previous)+'\n'+harness(path.read_text(),core,native))
            cmd=['clang','-std=gnu11','-O1','-g','-Wall','-Wextra','-Werror','-Wno-unused-function','-Wno-unused-variable','-Wno-unused-parameter','-fsanitize=address,undefined','-pthread','-I',str(root/'research/audio'),str(root/'research/audio/pcm_queue.c'),str(src),'-o',str(binary)]
            r=subprocess.run(cmd,capture_output=True,text=True,timeout=30);scrub=lambda s:s.replace(str(root),'REPO').replace(tmp,'HOST_TEST')
            row={'variant':label,'source_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'compile':{'code':r.returncode,'diagnostics':scrub(r.stderr)}};report['variants'].append(row)
            if r.returncode:continue
            r=subprocess.run([str(binary)],capture_output=True,text=True,timeout=30,env=dict(os.environ,ASAN_OPTIONS='detect_leaks=0:halt_on_error=1',UBSAN_OPTIONS='halt_on_error=1'))
            row['run']={'code':r.returncode,'diagnostics':scrub(r.stderr),'stdout':r.stdout.strip()}
            if not r.returncode:row['run']['result']=json.loads(r.stdout)
    report['passed']=all(v['compile']['code']==0 and v.get('run',{}).get('code')==0 and not v['run']['diagnostics'] for v in report['variants'])
    a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report));raise SystemExit(0 if report['passed'] else 1)


if __name__=='__main__':main()
