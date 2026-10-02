#!/usr/bin/env python3
"""Exercise extracted Xenon timer/PCM code with modeled registers and time.

Pthread interleavings cover a callback held across hw_free; not kernel SMP proof.
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
spec = importlib.util.spec_from_file_location('pcm_model', BASE/'check-audio-pcm.py')
pcm = importlib.util.module_from_spec(spec)
spec.loader.exec_module(pcm)

EXTRA = r'''
#include <pthread.h>
#include <stdatomic.h>
#include <stddef.h>
#define NSEC_PER_SEC 1000000000ULL
#define XENON_BYTES_PER_SECOND (48000 * 2 * 2)
#define container_of(p,type,member) ((type *)((char *)(p)-offsetof(type,member)))
#define timer_container_of(v,p,member) container_of(p,struct snd_xenon,member)
static pthread_mutex_t chip_mutex=PTHREAD_MUTEX_INITIALIZER;
static pthread_mutex_t timer_mutex=PTHREAD_MUTEX_INITIALIZER;
static pthread_cond_t timer_cond=PTHREAD_COND_INITIALIZER;
static pthread_mutex_t gate_mutex=PTHREAD_MUTEX_INITIALIZER;
static pthread_cond_t gate_cond=PTHREAD_COND_INITIALIZER;
static atomic_int_fast64_t clock_ns;
static atomic_int notifications, xruns, cancel_entered, free_done, released;
static int block_notification, notification_entered, release_notification, stop_in_notify;
static uint64_t div_u64(uint64_t n,unsigned d){return n/d;}
static ktime_t ktime_sub(ktime_t a,ktime_t b){return a-b;}
static int64_t ktime_to_ns(ktime_t t){return t;}
'''
TIMERS = r'''
static void hrtimer_start(struct hrtimer *t,ktime_t delay,int mode){
    CHECK(t->initialized && delay==XENON_POLL_NS && mode==HRTIMER_MODE_REL_SOFT);
    pthread_mutex_lock(&timer_mutex);t->pending=1;pthread_mutex_unlock(&timer_mutex);
}
static int hrtimer_cancel(struct hrtimer *t){
    CHECK(!locked && t->initialized);
    pthread_mutex_lock(&timer_mutex);atomic_fetch_add(&cancel_entered,1);pthread_cond_broadcast(&timer_cond);
    while(t->running)pthread_cond_wait(&timer_cond,&timer_mutex);
    t->pending=0;pthread_mutex_unlock(&timer_mutex);return 0;
}
static void hrtimer_forward_now(struct hrtimer *t,ktime_t delay){(void)t;CHECK(delay==XENON_POLL_NS);}
static unsigned jiffies;
static unsigned usecs_to_jiffies(unsigned u){return u/1000+1;}
static void mod_timer(struct timer_list *t,unsigned when){(void)when;t->pending=1;}
static int snd_xenon_trigger(struct snd_pcm_substream *,int);
static void snd_pcm_period_elapsed(struct snd_pcm_substream *s){
    CHECK(!locked && !atomic_load(&released));atomic_fetch_add(&notifications,1);
    if(block_notification){
        pthread_mutex_lock(&gate_mutex);notification_entered=1;pthread_cond_broadcast(&gate_cond);
        while(!release_notification)pthread_cond_wait(&gate_cond,&gate_mutex);
        pthread_mutex_unlock(&gate_mutex);
    }
    CHECK(!atomic_load(&released));
    if(stop_in_notify)CHECK(snd_xenon_trigger(s,SNDRV_PCM_TRIGGER_STOP)==0);
}
static void snd_pcm_stop_xrun(struct snd_pcm_substream *s){
    CHECK(!locked);atomic_fetch_add(&xruns,1);CHECK(snd_xenon_trigger(s,SNDRV_PCM_TRIGGER_STOP)==0);
}
'''
MAIN = r'''
#if HAS_POLL
static enum hrtimer_restart fire(struct hrtimer *t){
    pthread_mutex_lock(&timer_mutex);CHECK(t->initialized && t->pending);t->pending=0;t->running=1;pthread_mutex_unlock(&timer_mutex);
    enum hrtimer_restart ret=snd_xenon_timer_fn(t);
    pthread_mutex_lock(&timer_mutex);t->pending=ret==HRTIMER_RESTART;t->running=0;pthread_cond_broadcast(&timer_cond);pthread_mutex_unlock(&timer_mutex);return ret;
}
static void *fire_thread(void *arg){fire(arg);return NULL;}
static void *free_thread(void *arg){CHECK(snd_xenon_pcm_hw_free(arg)==0);atomic_store(&released,1);atomic_store(&free_done,1);return NULL;}
#endif
static void set_position(unsigned id,unsigned pos){spin_lock_irq(NULL);memcpy(registers+4+id*16,&pos,4);spin_unlock_irq(NULL);}
int main(int argc,char **argv){
    if(argc!=2)return 2;
    const char *test=argv[1];struct snd_xenon chip={0};shared_chip=&chip;chip.iobase_virt=registers;
    struct control controls[2]={{0},{0}};struct snd_pcm_runtime runtime[2]={{.control=&controls[0]},{.control=&controls[1]}};
    struct snd_pcm_substream subs[2]={{.runtime=&runtime[0],.buffer=4096,.period=512},{.runtime=&runtime[1],.buffer=4096,.period=512}};
    for(unsigned i=0;i<2;i++){
        struct playback_device *d=&chip.devices[i];d->playback_substream=&subs[i];d->state=2;d->buffer_bytes=4096;d->period_bytes=512;d->descr_bytes=128;
#if HAS_POLL
        d->chip=&chip;d->dev_id=i;d->timer.initialized=1;
#endif
    }
#if !HAS_POLL
    CHECK(snd_xenon_trigger(&subs[0],SNDRV_PCM_TRIGGER_START)==0);
    CHECK(!chip.timer.pending && !chip.timer_in_use);
    snd_xenon_timer_fn(&chip.timer);snd_xenon_timer_fn(&chip.timer);
    CHECK(atomic_load(&notifications)==2);
    puts("reproduced: START does not arm timer; unchanged zero status yields two false notifications");return 0;
#else
    if(!strcmp(test,"nonzero_start"))set_position(0,11);
    CHECK(snd_xenon_trigger(&subs[0],SNDRV_PCM_TRIGGER_START)==0);
    CHECK(chip.devices[0].timer.pending && !chip.devices[1].timer.pending && active[0]);
    CHECK(snd_xenon_trigger(&subs[1],SNDRV_PCM_TRIGGER_START)==0 && chip.devices[1].timer.pending);
    if(!strcmp(test,"stationary") || !strcmp(test,"nonzero_start")){
        for(unsigned n=0;n<10;n++){atomic_fetch_add(&clock_ns,200000);CHECK(fire(&chip.devices[0].timer)==HRTIMER_RESTART);}
        CHECK(!atomic_load(&notifications) && !atomic_load(&xruns));
    }else if(!strcmp(test,"progress")){
        const unsigned positions[]={1,3,4,4,12};const unsigned expected[]={0,0,1,1,2};
        for(unsigned n=0;n<5;n++){set_position(0,positions[n]);atomic_fetch_add(&clock_ns,200000);fire(&chip.devices[0].timer);CHECK(atomic_load(&notifications)==(int)expected[n]);}
        CHECK(chip.devices[0].period_progress==0);
    }else if(!strcmp(test,"wrap")){
        chip.devices[0].last_position=30*128;set_position(0,2);atomic_store(&clock_ns,200000);fire(&chip.devices[0].timer);CHECK(atomic_load(&notifications)==1);
    }else if(!strcmp(test,"remainder")){
        set_position(0,5);atomic_store(&clock_ns,200000);fire(&chip.devices[0].timer);CHECK(atomic_load(&notifications)==1 && chip.devices[0].period_progress==128);
        set_position(0,8);atomic_store(&clock_ns,400000);fire(&chip.devices[0].timer);CHECK(atomic_load(&notifications)==2 && !chip.devices[0].period_progress);
    }else if(!strcmp(test,"stop_one")){
        CHECK(snd_xenon_trigger(&subs[0],SNDRV_PCM_TRIGGER_STOP)==0);CHECK(!active[0] && active[1]);
        unsigned before=reads;CHECK(fire(&chip.devices[0].timer)==HRTIMER_NORESTART && reads==before);CHECK(chip.devices[1].timer.pending);
    }else if(!strcmp(test,"sync_one")){
        snd_xenon_trigger(&subs[0],SNDRV_PCM_TRIGGER_STOP);snd_xenon_sync_stop(&subs[0]);CHECK(!chip.devices[0].timer.pending && chip.devices[1].timer.pending);
    }else if(!strcmp(test,"stop_inside_notify")){
        stop_in_notify=1;set_position(0,4);atomic_store(&clock_ns,200000);CHECK(fire(&chip.devices[0].timer)==HRTIMER_NORESTART && !active[0] && active[1]);
    }else if(!strcmp(test,"late") || !strcmp(test,"late_boundary") || !strcmp(test,"before_boundary") || !strcmp(test,"clock_reverse")){
        int64_t boundary=4096ULL*NSEC_PER_SEC/XENON_BYTES_PER_SECOND;
        atomic_store(&clock_ns,!strcmp(test,"clock_reverse")?-1:boundary+(!strcmp(test,"late")?1:!strcmp(test,"before_boundary")?-1:0));
        int ret=fire(&chip.devices[0].timer);
        if(!strcmp(test,"before_boundary"))CHECK(ret==HRTIMER_RESTART && !atomic_load(&xruns));
        else CHECK(ret==HRTIMER_NORESTART && atomic_load(&xruns)==1 && !atomic_load(&notifications) && !active[0]);
    }else if(!strcmp(test,"zero_period")){
        chip.devices[0].period_bytes=0;unsigned before=reads;CHECK(fire(&chip.devices[0].timer)==HRTIMER_NORESTART && reads==before);
    }else if(!strcmp(test,"shutdown")){
        chip.shutting_down=true;unsigned before=reads;CHECK(fire(&chip.devices[0].timer)==HRTIMER_NORESTART && reads==before);
        chip.devices[0].state=2;CHECK(snd_xenon_trigger(&subs[0],SNDRV_PCM_TRIGGER_START)==-EINVAL);
    }else if(!strcmp(test,"free_during_callback")){
        block_notification=1;set_position(0,4);atomic_store(&clock_ns,200000);pthread_t callback,closer;
        CHECK(pthread_create(&callback,NULL,fire_thread,&chip.devices[0].timer)==0);
        pthread_mutex_lock(&gate_mutex);while(!notification_entered)pthread_cond_wait(&gate_cond,&gate_mutex);pthread_mutex_unlock(&gate_mutex);
        CHECK(pthread_create(&closer,NULL,free_thread,&subs[0])==0);
        pthread_mutex_lock(&timer_mutex);while(!atomic_load(&cancel_entered))pthread_cond_wait(&timer_cond,&timer_mutex);
        CHECK(chip.devices[0].timer.running && !atomic_load(&free_done));pthread_mutex_unlock(&timer_mutex);
        pthread_mutex_lock(&gate_mutex);release_notification=1;pthread_cond_broadcast(&gate_cond);pthread_mutex_unlock(&gate_mutex);
        CHECK(pthread_join(callback,NULL)==0 && pthread_join(closer,NULL)==0);
        CHECK(atomic_load(&free_done) && !chip.devices[0].timer.pending && chip.devices[1].timer.pending);
    }else return 3;
    atomic_store(&released,0);block_notification=0;
    CHECK(snd_xenon_pcm_hw_free(&subs[0])==0 && snd_xenon_pcm_hw_free(&subs[1])==0);
    CHECK(!chip.devices[0].timer.pending && !chip.devices[1].timer.pending && !locked);
    printf("%s: passed\n",test);return 0;
#endif
}
'''


def harness(source, candidate):
    prefix = pcm.PREFIX.replace('#include <stdint.h>', '#include <stdint.h>\n#include <pthread.h>\n#include <stdatomic.h>')
    prefix = prefix.replace('struct timer_list {int unused;};', 'struct timer_list {int pending;};')
    prefix = prefix.replace('struct hrtimer {int initialized,pending;};', 'enum hrtimer_restart {HRTIMER_NORESTART,HRTIMER_RESTART};\nstruct hrtimer {int initialized,pending,running;};')
    prefix = prefix.replace('static ktime_t ktime_get(void){return 0;}', EXTRA+'\nstatic ktime_t ktime_get(void){return atomic_load(&clock_ns);}')
    prefix = prefix.replace('fail_constraint,locked,active[2]', 'fail_constraint,active[2];static _Thread_local int locked')
    prefix = prefix.replace('CHECK(!locked);locked=1;', 'CHECK(!locked);pthread_mutex_lock(&chip_mutex);locked=1;')
    prefix = prefix.replace('CHECK(locked);locked=0;', 'CHECK(locked);locked=0;pthread_mutex_unlock(&chip_mutex);')
    prefix = re.sub(r'static void hrtimer_start\([^\n]+\nstatic int hrtimer_cancel\([^\n]+\n', TIMERS+'\n', prefix)
    structs=source[source.index('struct playback_device {'):source.index('static inline u32 bswap32')]
    names=['snd_xenon_position','snd_xenon_timer_fn','snd_xenon_sync_stop','snd_xenon_pcm_hw_free','snd_xenon_trigger'] if candidate else ['snd_xenon_timer_fn','snd_xenon_trigger']
    return '#define HAS_POLL '+str(int(candidate))+'\n'+prefix+structs+'\n'.join(pcm.function(source,n) for n in names)+MAIN


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--previous',type=Path,required=True);p.add_argument('--candidate',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    cases=['stationary','nonzero_start','progress','wrap','remainder','stop_one','sync_one','stop_inside_notify','late','late_boundary','before_boundary','clock_reverse','zero_period','shutdown','free_during_callback']
    report={'scope':'Extracted C; register/time/ALSA/timer models with one deterministic pthread interleaving; no real hardware, real-time guarantees or general SMP proof.','variants':[]}
    with tempfile.TemporaryDirectory(prefix='obsidian-poll-') as tmp:
        for name,path,candidate in [('previous',a.previous,False),('candidate',a.candidate,True)]:
            src=Path(tmp)/(name+'.c');binary=Path(tmp)/name;src.write_text(harness(path.read_text(),candidate))
            build=subprocess.run(['clang','-std=gnu11','-O1','-g','-Wall','-Wextra','-Werror','-Wno-unused-parameter','-Wno-unused-function','-Wno-unused-variable','-fsanitize=address,undefined','-pthread',str(src),'-o',str(binary)],capture_output=True,text=True,timeout=30)
            row={'variant':name,'source_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'compile_code':build.returncode,'diagnostics':build.stderr.replace(tmp,'HOST_TEST'),'cases':[]};report['variants'].append(row)
            if build.returncode:continue
            for case in cases if candidate else ['missing_start_false_notifications']:
                try:
                    r=subprocess.run([str(binary),case],capture_output=True,text=True,timeout=10,env=dict(os.environ,ASAN_OPTIONS='detect_leaks=0:halt_on_error=1',UBSAN_OPTIONS='halt_on_error=1'))
                    row['cases'].append({'name':case,'code':r.returncode,'stdout':r.stdout.strip(),'diagnostics':r.stderr.replace(tmp,'HOST_TEST')})
                except subprocess.TimeoutExpired:row['cases'].append({'name':case,'code':124,'diagnostics':'10-second harness deadline exceeded'})
    report['passed']=all(v['compile_code']==0 and len(v['cases'])==(len(cases) if v['variant']=='candidate' else 1) and all(c['code']==0 and not c.get('diagnostics') for c in v['cases']) for v in report['variants'])
    a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'passed':report['passed'],'variants':[{'name':v['variant'],'compile_code':v['compile_code'],'cases':len(v['cases']),'failures':[c['name'] for c in v['cases'] if c['code']]} for v in report['variants']]}));raise SystemExit(0 if report['passed'] else 1)


if __name__=='__main__':main()
