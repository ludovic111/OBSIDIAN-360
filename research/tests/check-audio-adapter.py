#!/usr/bin/env python3
"""Test extracted snd-xenon submission callbacks and pinned ALSA rollback code.

Registers, scheduling and descriptor completion remain explicit software models.
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
spec = importlib.util.spec_from_file_location('poll_model', BASE/'check-audio-poll.py')
poll = importlib.util.module_from_spec(spec)
spec.loader.exec_module(poll)
pcm = poll.pcm

EXTRA = r'''
typedef long snd_pcm_sframes_t;
#define SNDRV_PCM_INFO_NO_REWINDS 1
#define SNDRV_PCM_INFO_SYNC_APPLPTR 2
#define SNDRV_PCM_INFO_EXPLICIT_SYNC 4
#define SNDRV_PROTOCOL_VERSION(a,b,c) (((a)<<16)|((b)<<8)|(c))
struct snd_pcm_file {struct snd_pcm_substream *substream;unsigned user_pversion;int no_compat_mmap;};
#define SNDRV_PCM_IOCTL1_RESET 19
#define SNDRV_PCM_TRIGGER_DRAIN 2
static int stream_locked, delegated;
#define snd_pcm_stream_lock_irqsave(s,f) do {(void)(s);CHECK(!locked && !stream_locked);stream_locked=1;(f)=0;}while(0)
#define snd_pcm_stream_unlock_irqrestore(s,f) do {(void)(s);(void)(f);CHECK(!locked && stream_locked);stream_locked=0;}while(0)
static int snd_pcm_lib_ioctl(struct snd_pcm_substream *s,unsigned cmd,void *arg){(void)s;(void)cmd;(void)arg;++delegated;return 73;}
static void __snd_pcm_xrun(struct snd_pcm_substream *s){(void)s;atomic_fetch_add(&xruns,1);}
static void trace_applptr(struct snd_pcm_substream *s,unsigned long old,unsigned long now){(void)s;(void)old;(void)now;}
'''

MAIN = poll.MAIN[:poll.MAIN.index('static void set_position')] + r'''
static void status_reg(unsigned channel,u32 value){memcpy(registers+4+channel*16,&value,4);}
static void tick(struct playback_device *d,unsigned index){
    status_reg(d->dev_id,index);atomic_fetch_add(&clock_ns,200000);
    snd_xenon_timer_fn(&d->timer);
}
static int apply(struct snd_pcm_substream *s,unsigned long frames){
    CHECK(!stream_locked);stream_locked=1;int r=pcm_lib_apply_appl_ptr(s,frames);stream_locked=0;return r;
}
static void unchanged_pointer(struct snd_pcm_substream *s,unsigned expected){
    unsigned w=writes,r=reads,b=barriers;
    for(unsigned j=0;j<100;j++)CHECK(snd_xenon_pointer(s)==expected);
    CHECK(writes==w && reads==r && barriers==b);
}
int main(int argc,char **argv){
    if(argc!=2)return 2;
    const char *test=argv[1];
    struct snd_xenon chip={0};shared_chip=&chip;chip.iobase_virt=registers;
    struct control controls[2]={{77},{99}};struct status statuses[2]={{123},{456}};
    struct snd_pcm_runtime runtime[2]={0};struct snd_pcm_substream subs[2]={0};
    struct pcm_ops ops={.ack=snd_xenon_ack};u32 descriptors[128]={0};
    unsigned char memory[2][65568];memset(memory,0xa5,sizeof(memory));
    for(unsigned i=0;i<2;i++){
        runtime[i]=(struct snd_pcm_runtime){.dma_area=memory[i]+16,.dma_bytes=4096,.dma_addr=0x10000+i*65536,.control=&controls[i],.status=&statuses[i],.boundary=1UL<<40,.buffer_size=1024,.info=SNDRV_PCM_INFO_NO_REWINDS};
        subs[i]=(struct snd_pcm_substream){.runtime=&runtime[i],.buffer=4096,.period=512,.ops=&ops};
        struct playback_device *d=&chip.devices[i];d->chip=&chip;d->dev_id=i;d->playback_substream=&subs[i];d->state=1;d->timer.initialized=1;d->descr_base_virt=descriptors+64*i;d->descr_base_phys=0x8000+i*256;
        CHECK(snd_xenon_playback_prepare(&subs[i])==0);
        CHECK(d->appl_ptr==0 && controls[i].appl_ptr!=0);
        CHECK(snd_xenon_ioctl(&subs[i],SNDRV_PCM_IOCTL1_RESET,NULL)==0 && !statuses[i].hw_ptr);
        /* Exact post_prepare assignment, after RESET, as in pinned pcm_native. */
        controls[i].appl_ptr=statuses[i].hw_ptr;
    }
    struct playback_device *d=&chip.devices[0];struct snd_pcm_substream *s=&subs[0];
    writes=reads=barriers=0;
    if(!strcmp(test,"control_mmap")){
        struct snd_pcm_file file={.substream=s,.user_pversion=SNDRV_PROTOCOL_VERSION(2,0,14)};
        runtime[0].hw.info=0;CHECK(pcm_control_mmap_allowed(&file) && pcm_status_mmap_allowed(&file));
        runtime[0].hw.info=SNDRV_PCM_INFO_SYNC_APPLPTR;
        CHECK(!pcm_control_mmap_allowed(&file) && pcm_status_mmap_allowed(&file));
        file.user_pversion=SNDRV_PROTOCOL_VERSION(2,0,13);
        CHECK(!pcm_control_mmap_allowed(&file) && !pcm_status_mmap_allowed(&file));
    }else if(!strcmp(test,"partial_drain")){
        memset(memory[0]+16,0xa5,4096);CHECK(apply(s,1)==0 && !writes && !barriers);
        CHECK(d->queue.tail_bytes==4);unchanged_pointer(s,0);
        CHECK(snd_xenon_trigger(s,SNDRV_PCM_TRIGGER_START)==0 && !active[0] && d->timer.pending);
        CHECK(snd_xenon_trigger(s,SNDRV_PCM_TRIGGER_DRAIN)==0 && active[0]);
        CHECK(d->queue.queued_bytes==128 && d->queue.logical_bytes==4);
        for(unsigned i=0;i<4096;i++)CHECK(memory[0][16+i]==(i>=4 && i<128?0:0xa5));
        unsigned w=writes,b=barriers;CHECK(snd_xenon_trigger(s,SNDRV_PCM_TRIGGER_DRAIN)==0 && writes==w && barriers==b);
        CHECK(apply(s,2)==-EINVAL && controls[0].appl_ptr==1 && d->appl_ptr==1 && writes==w);
        /* Last-index/zero-length is not accepted as completion. */
        tick(d,0);CHECK(d->queue.logical_bytes==4 && !notifications);unchanged_pointer(s,0);
        tick(d,1);CHECK(!d->queue.logical_bytes && notifications==1);unchanged_pointer(s,1);
    }else if(!strcmp(test,"deferred_start")){
        CHECK(apply(s,1)==0 && !writes);
        CHECK(snd_xenon_trigger(s,SNDRV_PCM_TRIGGER_START)==0 && !active[0]);
        CHECK(apply(s,32)==0 && active[0] && d->queue.queued_bytes==128);
        unsigned w=writes,b=barriers;CHECK(snd_xenon_ack(s)==0 && writes==w && barriers==b);
    }else if(!strcmp(test,"bad_start_position")){
        CHECK(apply(s,1)==0);CHECK(snd_xenon_trigger(s,SNDRV_PCM_TRIGGER_START)==0);
        status_reg(0,4);struct obs_audio_queue before=d->queue;unsigned w=writes,b=barriers;
        CHECK(apply(s,32)==-EIO && controls[0].appl_ptr==1 && d->appl_ptr==1);
        CHECK(!memcmp(&before,&d->queue,sizeof(before)) && writes==w && barriers==b);
        CHECK(snd_xenon_trigger(s,SNDRV_PCM_TRIGGER_DRAIN)==-EIO && !memcmp(&before,&d->queue,sizeof(before)) && writes==w);
    }else if(!strcmp(test,"full_ring")){
        CHECK(apply(s,1024)==0 && d->queue.queued_bytes==4096 && writes==1 && barriers==1);
        u32 reg;memcpy(&reg,registers+4,4);CHECK(reg==31*256);
        struct obs_audio_queue before=d->queue;unsigned w=writes;
        CHECK(apply(s,1025)==-EINVAL && controls[0].appl_ptr==1024 && d->appl_ptr==1024 && writes==w && !memcmp(&before,&d->queue,sizeof(before)));
        unchanged_pointer(s,0);CHECK(snd_xenon_trigger(s,SNDRV_PCM_TRIGGER_START)==0);
        tick(d,4);CHECK(notifications==1 && d->queue.logical_bytes==3584);unchanged_pointer(s,128);
        CHECK(apply(s,1152)==0 && d->queue.logical_bytes==4096);
    }else if(!strcmp(test,"rewind_boundary_overflow")){
        CHECK(apply(s,32)==0);unsigned w=writes;
        CHECK(apply(s,31)==-EINVAL && controls[0].appl_ptr==32 && d->appl_ptr==32 && writes==w);
        CHECK(apply(s,runtime[0].boundary)==-EINVAL && writes==w);
        /* Force inconsistent core/adapter snapshots: adapter also rejects. */
        controls[0].appl_ptr=0;CHECK(apply(s,1)==-EINVAL && controls[0].appl_ptr==0 && d->appl_ptr==32 && writes==w);
        CHECK(snd_xenon_playback_prepare(s)==0);controls[0].appl_ptr=0;
        runtime[0].boundary=1UL<<62;d->appl_ptr=controls[0].appl_ptr=(1UL<<58);
        CHECK(apply(s,(1UL<<58)+32)==0 && d->queue.logical_bytes==128);
        CHECK(snd_xenon_playback_prepare(s)==0);
        d->appl_ptr=controls[0].appl_ptr=runtime[0].boundary-1024;
        CHECK(apply(s,0)==0 && d->queue.logical_bytes==4096);
    }else if(!strcmp(test,"reset_prepare")){
        CHECK(snd_xenon_ioctl(s,123,NULL)==73 && delegated==1);
        CHECK(apply(s,32)==0);struct obs_audio_queue before=d->queue;
        statuses[0].hw_ptr=77;runtime[0].hw_ptr_wrap=9;unsigned w=writes;
        CHECK(snd_xenon_ioctl(s,SNDRV_PCM_IOCTL1_RESET,NULL)==-EBUSY && statuses[0].hw_ptr==77 && runtime[0].hw_ptr_wrap==9 && writes==w && !memcmp(&before,&d->queue,sizeof(before)));
        CHECK(snd_xenon_trigger(s,SNDRV_PCM_TRIGGER_START)==0);
        CHECK(snd_xenon_ioctl(s,SNDRV_PCM_IOCTL1_RESET,NULL)==-EBUSY);
        CHECK(snd_xenon_trigger(s,SNDRV_PCM_TRIGGER_STOP)==0);CHECK(snd_xenon_sync_stop(s)==0);
        CHECK(snd_xenon_playback_prepare(s)==0 && d->appl_ptr==0);
        CHECK(snd_xenon_ioctl(s,SNDRV_PCM_IOCTL1_RESET,NULL)==0 && !statuses[0].hw_ptr && !runtime[0].hw_ptr_wrap);
        controls[0].appl_ptr=statuses[0].hw_ptr;CHECK(apply(s,32)==0);
    }else if(!strcmp(test,"free_during_callback")){
        CHECK(apply(s,1024)==0 && snd_xenon_trigger(s,SNDRV_PCM_TRIGGER_START)==0);
        CHECK(apply(&subs[1],1024)==0 && snd_xenon_trigger(&subs[1],SNDRV_PCM_TRIGGER_START)==0);
        block_notification=1;status_reg(0,4);atomic_store(&clock_ns,200000);pthread_t callback,closer;
        CHECK(pthread_create(&callback,NULL,fire_thread,&d->timer)==0);
        pthread_mutex_lock(&gate_mutex);while(!notification_entered)pthread_cond_wait(&gate_cond,&gate_mutex);pthread_mutex_unlock(&gate_mutex);
        CHECK(pthread_create(&closer,NULL,free_thread,s)==0);
        pthread_mutex_lock(&timer_mutex);while(!atomic_load(&cancel_entered))pthread_cond_wait(&timer_cond,&timer_mutex);
        CHECK(d->timer.running && !atomic_load(&free_done));pthread_mutex_unlock(&timer_mutex);
        pthread_mutex_lock(&gate_mutex);release_notification=1;pthread_cond_broadcast(&gate_cond);pthread_mutex_unlock(&gate_mutex);
        CHECK(pthread_join(callback,NULL)==0 && pthread_join(closer,NULL)==0);
        CHECK(atomic_load(&free_done) && !d->timer.pending && chip.devices[1].timer.pending);
        block_notification=0;atomic_store(&released,0);
    }else if(!strcmp(test,"stop_in_notification")){
        CHECK(apply(s,1024)==0 && snd_xenon_trigger(s,SNDRV_PCM_TRIGGER_START)==0);
        stop_in_notify=1;tick(d,4);CHECK(notifications==1 && !active[0] && d->state==4);
    }else if(!strcmp(test,"late_poll")){
        CHECK(apply(s,1024)==0 && snd_xenon_trigger(s,SNDRV_PCM_TRIGGER_START)==0);
        atomic_store(&clock_ns,4096ULL*NSEC_PER_SEC/XENON_BYTES_PER_SECOND);
        CHECK(snd_xenon_timer_fn(&d->timer)==HRTIMER_NORESTART && xruns==1 && !active[0]);
    }else if(!strcmp(test,"invalid_completion")){
        CHECK(apply(s,32)==0 && snd_xenon_trigger(s,SNDRV_PCM_TRIGGER_START)==0);
        struct obs_audio_queue before=d->queue;tick(d,2);
        CHECK(xruns==1 && !active[0] && !memcmp(&before,&d->queue,sizeof(before)));
    }else if(!strcmp(test,"stalled_final")){
        CHECK(apply(s,1)==0 && snd_xenon_trigger(s,SNDRV_PCM_TRIGGER_START)==0 && snd_xenon_trigger(s,SNDRV_PCM_TRIGGER_DRAIN)==0);
        for(unsigned n=0;n<110 && !xruns;n++)tick(d,0);
        CHECK(xruns==1 && !active[0] && !notifications && d->queue.logical_bytes==4);
    }else if(!strcmp(test,"two_channels")){
        CHECK(apply(s,1024)==0 && apply(&subs[1],1024)==0);
        CHECK(snd_xenon_trigger(s,SNDRV_PCM_TRIGGER_START)==0 && snd_xenon_trigger(&subs[1],SNDRV_PCM_TRIGGER_START)==0);
        tick(d,4);unchanged_pointer(s,128);unchanged_pointer(&subs[1],0);
        CHECK(chip.devices[1].queue.logical_bytes==4096);
        CHECK(snd_xenon_trigger(s,SNDRV_PCM_TRIGGER_STOP)==0 && !active[0] && active[1]);
        unsigned w=writes;CHECK(apply(s,1152)==-EINVAL && writes==w && controls[0].appl_ptr==1024);
    }else if(!strcmp(test,"all_geometries")){
        for(unsigned bytes=128;bytes<=65536;bytes+=128){
            runtime[0].dma_bytes=subs[0].buffer=bytes;runtime[0].buffer_size=bytes/4;runtime[0].boundary=(unsigned long)runtime[0].buffer_size*4096;subs[0].period=bytes/2;
            CHECK(snd_xenon_playback_prepare(s)==0);CHECK(snd_xenon_ioctl(s,SNDRV_PCM_IOCTL1_RESET,NULL)==0);controls[0].appl_ptr=0;
            CHECK(apply(s,bytes/4)==0 && d->queue.logical_bytes==bytes);unchanged_pointer(s,0);
            CHECK(snd_xenon_trigger(s,SNDRV_PCM_TRIGGER_START)==0);
            tick(d,1);unchanged_pointer(s,bytes/128);
            CHECK(snd_xenon_trigger(s,SNDRV_PCM_TRIGGER_STOP)==0 && snd_xenon_sync_stop(s)==0);
        }
    }else if(!strcmp(test,"shutdown")){
        chip.shutting_down=true;unsigned w=writes;
        CHECK(apply(s,32)==-EINVAL && writes==w && !controls[0].appl_ptr);
        CHECK(snd_xenon_trigger(s,SNDRV_PCM_TRIGGER_START)==-EINVAL && writes==w);
        CHECK(snd_xenon_ioctl(s,SNDRV_PCM_IOCTL1_RESET,NULL)==-EBUSY);
    }else return 3;
    for(unsigned i=0;i<2;i++)CHECK(snd_xenon_pcm_hw_free(&subs[i])==0);
    for(unsigned i=0;i<16;i++)CHECK(memory[0][i]==0xa5 && memory[1][i]==0xa5 && memory[0][65552+i]==0xa5 && memory[1][65552+i]==0xa5);
    CHECK(!locked && !stream_locked);printf("%s: passed\n",test);return 0;
}
'''


def harness(source, core, native):
    prefix=poll.harness(source,True).split('struct playback_device {')[0]
    prefix=prefix.replace('struct snd_pcm_hardware {int token;};','struct snd_pcm_hardware {int token;unsigned info;};')
    prefix=prefix.replace('struct snd_pcm_runtime {','struct status {unsigned long hw_ptr;};\nstruct snd_pcm_runtime {unsigned long boundary,buffer_size,hw_ptr_wrap;unsigned info;struct status *status;')
    prefix=prefix.replace('struct snd_pcm_substream {','struct snd_pcm_substream;struct pcm_ops {int (*ack)(struct snd_pcm_substream *);};\nstruct snd_pcm_substream {struct pcm_ops *ops;')
    # Register model preserves read-only hardware position on last-valid writes.
    prefix=prefix.replace('memcpy(registers+off,&value,4);', '''if(off==4 || off==0x14){u32 current;memcpy(&current,registers+off,4);value=(current & ~0x1f00U)|(value & 0x1f00U);}
    if((off==8 || off==0x18) && value==0x2000000){u32 zero=0;memcpy(registers+off-4,&zero,4);}
    memcpy(registers+off,&value,4);''')
    structs=source[source.index('struct playback_device {'):source.index('static inline u32 bswap32')]
    names=['bswap32','snd_xenon_position','snd_xenon_timer_fn','snd_xenon_sync_stop','snd_xenon_pcm_hw_free','snd_xenon_playback_prepare','snd_xenon_publish','snd_xenon_start_position_ok','snd_xenon_start_dma','snd_xenon_ack','snd_xenon_ioctl','snd_xenon_trigger','snd_xenon_pointer']
    if 'snd_xenon_control_word' in source:
        prefix+='\n'+'\n'.join(re.findall(r'^#define XENON_(?:CTL_RUN|CTL_IRQS|STATUS_W1C) .+$',source,re.M))+'\n'
        names.insert(0,'snd_xenon_control_word')
    m=re.search(r'^int pcm_lib_apply_appl_ptr\([^;]*?\n\{',core,re.M)
    apply=core[m.start():core.index('\n}',m.end())+2]
    return '#include "pcm_queue.h"\n'+prefix+EXTRA+structs+'\n'.join(pcm.function(source,n) for n in names)+'\n#pragma clang diagnostic push\n#pragma clang diagnostic ignored "-Wsign-compare"\n'+apply+'\n#pragma clang diagnostic pop\n'+pcm.function(native,'pcm_control_mmap_allowed')+pcm.function(native,'pcm_status_mmap_allowed')+MAIN


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--source',type=Path,required=True);p.add_argument('--kernel',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    root=BASE.parent.parent;source=a.source.read_text();core=a.kernel/'sound/core/pcm_lib.c'
    cases=['partial_drain','deferred_start','bad_start_position','full_ring','rewind_boundary_overflow','reset_prepare','invalid_completion','stalled_final','two_channels','all_geometries','shutdown','free_during_callback','stop_in_notification','late_poll','control_mmap']
    report={'scope':'Extracted candidate callbacks plus actual pinned pcm_lib_apply_appl_ptr; modeled registers/time/reset/ALSA services. No audio hardware or general concurrency proof. Final descriptor may stall and is explicitly expected to fail via XRUN.', 'driver_sha256':hashlib.sha256(a.source.read_bytes()).hexdigest(),'pcm_lib_sha256':hashlib.sha256(core.read_bytes()).hexdigest(),'cases':[]}
    report['wiring']={name:source.count(name)==2 for name in ['SNDRV_PCM_INFO_NO_REWINDS','SNDRV_PCM_INFO_DRAIN_TRIGGER','SNDRV_PCM_INFO_SYNC_APPLPTR']}
    report['wiring']['both_ack']=len(re.findall(r'\.ack\s*=\s*snd_xenon_ack',source))==2
    report['wiring']['both_ioctl']=len(re.findall(r'\.ioctl\s*=\s*snd_xenon_ioctl',source))==2
    with tempfile.TemporaryDirectory(prefix='obsidian-adapter-') as tmp:
        src=Path(tmp)/'test.c';binary=Path(tmp)/'test';src.write_text(harness(source,core.read_text(),(a.kernel/'sound/core/pcm_native.c').read_text()))
        cmd=['clang','-std=gnu11','-O1','-g','-Wall','-Wextra','-Werror','-Wno-unused-parameter','-Wno-unused-function','-Wno-unused-variable','-fsanitize=address,undefined','-pthread','-I',str(root/'research/audio'),str(root/'research/audio/pcm_queue.c'),str(src),'-o',str(binary)]
        r=subprocess.run(cmd,capture_output=True,text=True,timeout=30)
        scrub=lambda s:s.replace(str(root),'REPO').replace(tmp,'HOST_TEST')
        report['compile']={'code':r.returncode,'diagnostics':scrub(r.stderr)}
        if not r.returncode:
            for case in cases:
                r=subprocess.run([str(binary),case],capture_output=True,text=True,timeout=15,env=dict(os.environ,ASAN_OPTIONS='detect_leaks=0:halt_on_error=1',UBSAN_OPTIONS='halt_on_error=1'))
                report['cases'].append({'name':case,'code':r.returncode,'stdout':r.stdout.strip(),'diagnostics':scrub(r.stderr)})
    report['passed']=all(report['wiring'].values()) and report['compile']['code']==0 and len(report['cases'])==len(cases) and all(c['code']==0 and not c['diagnostics'] for c in report['cases'])
    a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report));raise SystemExit(0 if report['passed'] else 1)


if __name__=='__main__':main()
