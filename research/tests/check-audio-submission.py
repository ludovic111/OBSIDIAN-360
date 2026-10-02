#!/usr/bin/env python3
"""Reproduce submission side effects in the historical Xenon pointer callback.

Extracts the real pointer and ALSA conversion helpers. Registers are modeled;
last-valid descriptor interpretation is a source-derived hypothesis, not a probe.
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

spec=importlib.util.spec_from_file_location('pcm_model',Path(__file__).with_name('check-audio-pcm.py'))
pcm=importlib.util.module_from_spec(spec);spec.loader.exec_module(pcm)
MAIN=r'''
int main(int argc,char **argv){
    if(argc!=2)return 2;
    struct snd_xenon chip={0};shared_chip=&chip;chip.iobase_virt=registers;
    struct control control={0};struct snd_pcm_runtime runtime={.control=&control,.frame_bits=32};
    struct snd_pcm_substream sub={.runtime=&runtime,.buffer=4096,.period=512};
    chip.devices[0].playback_substream=&sub;chip.devices[0].buffer_bytes=4096;chip.devices[0].descr_bytes=128;chip.devices[0].wptr=-1;
    if(!strcmp(argv[1],"overflow")){
        /* This value is below a power-of-two ALSA boundary near LONG_MAX/2. */
        control.appl_ptr=(unsigned long)LONG_MAX/32+1;
        snd_xenon_pointer(&sub);return 3;
    }
    if(!strcmp(argv[1],"partial")){
        control.appl_ptr=1;u32 initial=(3<<8)|7;memcpy(registers+4,&initial,4);
        CHECK(snd_xenon_pointer(&sub)==224);u32 value;memcpy(&value,registers+4,4);
        CHECK(((value>>8)&31)==0);
        puts("conditional: descriptor 0 advertised with 4/128 bytes committed under last-valid interpretation");return 0;
    }
    unsigned unstable=0;
    for(unsigned descriptor=0;descriptor<32;descriptor++){
        unsigned offsets[]={0,1,31};
        for(unsigned n=0;n<3;n++){
            control.appl_ptr=descriptor*32+offsets[n];u32 initial=(descriptor<<8)|7;memcpy(registers+4,&initial,4);writes=0;
            unsigned values[3];
            for(unsigned k=0;k<3;k++){
                CHECK(snd_xenon_pointer(&sub)==224);u32 value;memcpy(&value,registers+4,4);values[k]=(value>>8)&31;
            }
            CHECK(writes==3 && values[0]==((descriptor+31)&31) && values[1]==descriptor && values[2]==values[0]);++unstable;
        }
    }
    CHECK(unstable==96);printf("reproduced: %u unchanged-application cases alternate advertised descriptor across three identical position queries\n",unstable);return 0;
}
'''


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--source',type=Path,required=True);p.add_argument('--pcm-header',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    source=a.source.read_text();header=a.pcm_header.read_text()
    prefix=pcm.PREFIX.replace('#include <stdint.h>','#include <stdint.h>\n#include <limits.h>\n#include <sys/types.h>\ntypedef long snd_pcm_sframes_t;')
    prefix=prefix.replace('struct snd_pcm_runtime {','struct snd_pcm_runtime {unsigned frame_bits;')
    for name in ['frames_to_bytes','bytes_to_frames']:
        prefix=re.sub(r'^static unsigned long '+name+r'\([^\n]+\n',lambda _:pcm.function(header,name)+'\n',prefix,flags=re.M)
    # Model only the writable queue-index field, leaving the read position intact.
    prefix=prefix.replace('memcpy(registers+off,&value,4);','if(off==4 || off==0x14){u32 prior;memcpy(&prior,registers+off,4);value=(prior & ~0x1f00U)|(value & 0x1f00U);}\n    memcpy(registers+off,&value,4);')
    structs=source[source.index('struct playback_device {'):source.index('static inline u32 bswap32')]
    report={'scope':'Actual pointer and ALSA unit helpers; modeled MMIO, no hardware. Partial-block interpretation conditional on LibXenon last-valid semantics. Overflow uses native signed long width.','source_sha256':hashlib.sha256(a.source.read_bytes()).hexdigest(),'pcm_header_sha256':hashlib.sha256(a.pcm_header.read_bytes()).hexdigest(),'cases':[]}
    with tempfile.TemporaryDirectory(prefix='obsidian-submit-') as tmp:
        src=Path(tmp)/'test.c';binary=Path(tmp)/'test';src.write_text(prefix+structs+pcm.function(source,'snd_xenon_pointer')+MAIN)
        build=subprocess.run(['clang','-std=gnu11','-O1','-g','-Wall','-Wextra','-Werror','-Wno-unused-function','-Wno-unused-variable','-Wno-unused-parameter','-fsanitize=address,undefined',str(src),'-o',str(binary)],capture_output=True,text=True,timeout=30)
        report['compile']={'code':build.returncode,'diagnostics':build.stderr.replace(tmp,'HOST_TEST')}
        if build.returncode==0:
            for name in ['repeated_query','partial','overflow']:
                r=subprocess.run([str(binary),name],capture_output=True,text=True,timeout=10,env=dict(os.environ,ASAN_OPTIONS='detect_leaks=0:halt_on_error=1',UBSAN_OPTIONS='halt_on_error=1'))
                expected=name=='overflow';ok=(r.returncode!=0 and 'runtime error: signed integer overflow' in r.stderr) if expected else (r.returncode==0 and not r.stderr)
                report['cases'].append({'name':name,'code':r.returncode,'expected_failure':expected,'passed':ok,'stdout':r.stdout.strip(),'diagnostics':r.stderr.replace(tmp,'HOST_TEST')})
    report['passed']=report['compile']['code']==0 and len(report['cases'])==3 and all(c['passed'] for c in report['cases'])
    a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'passed':report['passed'],'cases':len(report['cases'])}));raise SystemExit(0 if report['passed'] else 1)


if __name__=='__main__':main()
