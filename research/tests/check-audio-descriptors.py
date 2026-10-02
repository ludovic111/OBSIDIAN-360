#!/usr/bin/env python3
"""Compare actual descriptor preparation under the literal-byte-count hypothesis.

Also exercise LibXenon completion helpers against explicitly modeled registers.
No hardware is accessed, and returned DMA counts do not prove audible drain.
"""
import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import re
import subprocess
import tempfile

BASE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('adapter', BASE/'check-audio-adapter.py')
adapter = importlib.util.module_from_spec(spec)
spec.loader.exec_module(adapter)

MAIN = r'''
int main(void){
    struct snd_xenon chip={0};shared_chip=&chip;chip.iobase_virt=registers;
    struct control control={0};struct status status={0};
    unsigned char memory[65568];u32 descriptors[64];
    struct snd_pcm_runtime runtime={.control=&control,.status=&status,.dma_area=memory+16,.dma_addr=0x10000};
    struct snd_pcm_substream sub={.runtime=&runtime};
    struct playback_device *d=&chip.devices[0];d->chip=&chip;d->playback_substream=&sub;d->dev_id=0;d->descr_base_virt=descriptors;d->descr_base_phys=0x8000;
    /* SiS swaps SR and PICB; these are reference-layout comparisons only. */
    CHECK(ICH_REG_OFF_CIV==4 && ICH_REG_OFF_LVI==5);
    CHECK(ICH_REG_OFF_SR==6 && ICH_REG_OFF_PICB==8);
    CHECK(ICH_REG_OFF_PIV==10 && ICH_REG_OFF_CR==11);
    CHECK((ICH_STARTBM<<24)==0x01000000 && (ICH_RESETREGS<<24)==0x02000000);
    CHECK((ICH_FIFOE|ICH_BCIS|ICH_LVBCI)==0x1c);
    CHECK((ICH_IOCE|ICH_FEIE|ICH_LVBIE)==0x1c);
    unsigned sizes=0,entries=0,unaligned=0,total_shortfall=0;
    for(unsigned bytes=128;bytes<=65536;bytes+=128){
        memset(memory,0xa5,sizeof(memory));memset(descriptors,0xa5,sizeof(descriptors));
        runtime.dma_bytes=sub.buffer=bytes;sub.period=bytes/2;
        CHECK(snd_xenon_playback_prepare(&sub)==0);unsigned total=0;
        u32 init;memcpy(&init,registers+8,4);
        CHECK((init>>24)==(ICH_IOCE|ICH_FEIE|ICH_LVBIE));
        CHECK((init&0xffff)==(ICH_FIFOE|ICH_BCIS|ICH_LVBCI));
        for(unsigned i=0;i<32;i++){
            u32 address=bswap32(descriptors[2*i]),word=bswap32(descriptors[2*i+1]);
            unsigned count=word & 0xffff;
            CHECK(address==runtime.dma_addr+i*(bytes/32));CHECK((word & 0xffff0000)==0x80000000);
#if PREVIOUS
            CHECK(count==bytes/32-1);
#else
            CHECK(count==bytes/32);
#endif
            CHECK(address+count<=runtime.dma_addr+bytes);total+=count;++entries;unaligned+=!!(count%4);
        }
        CHECK(total==bytes-(PREVIOUS?32:0));total_shortfall+=bytes-total;
        for(unsigned i=0;i<16;i++)CHECK(memory[i]==0xa5 && memory[65552+i]==0xa5);
        ++sizes;
    }
    /* Before fetch and after completion may present the same modeled word.
     * These helpers have no epoch/status input with which to distinguish them.
     */
    unsigned ambiguity_cases=0;
    for(unsigned index=0;index<32;index++){
        reference_word=index|(index<<8);wptr=((index+1)%32)*2048;
        CHECK(xenon_sound_get_unplayed()==0 && xenon_sound_get_free()==65536);
        ++ambiguity_cases;
        reference_word|=128U<<16;CHECK(xenon_sound_get_unplayed()==128);
    }
    printf("{\"sizes\":%u,\"descriptors\":%u,\"counts_not_frame_aligned\":%u,\"aggregate_shortfall_bytes_under_literal_count_model\":%u,\"zero_residual_ambiguity_cases\":%u}\n",sizes,entries,unaligned,total_shortfall,ambiguity_cases);
    return 0;
}
'''


def reference(source):
    prefix=r'''
static int snd_base=0x1000,wptr,buffer_len=65536;
static uint32_t reference_word;
static uint32_t read32(int address){CHECK(address==snd_base+4);return reference_word;}
'''
    for name in ['xenon_sound_get_free','xenon_sound_get_unplayed']:
        m=re.search(r'^int '+name+r'\([^;]*?\n\{',source,re.M)
        prefix+=source[m.start():source.index('\n}',m.end())+2]+'\n'
    return prefix


def main():
    p=argparse.ArgumentParser(description=__doc__)
    for name in ['previous','candidate','kernel','libxenon','output']:p.add_argument('--'+name,type=Path,required=True)
    a=p.parse_args();root=BASE.parent.parent;lib=a.libxenon/'libxenon/drivers/xenon_sound/sound.c'
    core=(a.kernel/'sound/core/pcm_lib.c').read_text();native=(a.kernel/'sound/core/pcm_native.c').read_text()
    intel=(a.kernel/'sound/pci/intel8x0.c').read_text()
    layout=intel[intel.index('#define DEFINE_REGSET'):intel.index('/* global block */')]
    report={'scope':'Actual candidate/previous prepare callbacks; literal byte count interpretation from source/history, not observed hardware. LibXenon helpers run on modeled raw words; no proof of FIFO empty or audible playback.','libxenon_sha256':hashlib.sha256(lib.read_bytes()).hexdigest(),'intel8x0_sha256':hashlib.sha256(intel.encode()).hexdigest(),'register_layout_scope':'Actual SiS reference defines and Xenon prepare constant agree on ten offset/mask comparisons; device identity unproven.','variants':[]}
    with tempfile.TemporaryDirectory(prefix='obsidian-descriptors-') as tmp:
        for label,path,previous in [('previous',a.previous,1),('candidate',a.candidate,0)]:
            source=path.read_text();prefix=adapter.harness(source,core,native);assert prefix.endswith(adapter.MAIN);prefix=prefix[:-len(adapter.MAIN)]
            src=Path(tmp)/(label+'.c');binary=Path(tmp)/label;src.write_text('#define PREVIOUS '+str(previous)+'\n'+prefix+'\n'+layout+'\n'+reference(lib.read_text())+MAIN)
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
