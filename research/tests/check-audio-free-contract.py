#!/usr/bin/env python3
"""Execute actual ALSA stop/free core functions under injected callback errors."""
import argparse,hashlib,json,re,subprocess,tempfile
from pathlib import Path

def function(source,name):
    m=re.search(r'^(?:static )?[\w *]+\b'+name+r'\([^;]*?\n\{',source,re.M)
    if not m:raise ValueError(name)
    return source[m.start():source.index('\n}',m.end())+2]

PREFIX=r'''
#include <assert.h>
#include <stdbool.h>
#include <stdio.h>
#include <stdlib.h>
#include <errno.h>
struct snd_dma_buffer { void *area; };
struct snd_card { int sync_irq; };
struct snd_pcm { struct snd_card *card; };
struct snd_pcm_runtime { bool stop_operating; void *dma_area; struct snd_dma_buffer *dma_buffer_p; };
struct snd_pcm_substream;
struct snd_pcm_ops { int (*sync_stop)(struct snd_pcm_substream *); int (*hw_free)(struct snd_pcm_substream *); };
struct snd_pcm_substream { struct snd_pcm_runtime *runtime; struct snd_pcm_ops *ops; struct snd_pcm *pcm; bool managed_buffer_alloc; struct snd_dma_buffer dma_buffer; };
static unsigned sync_calls,hw_calls,releases,detaches,info_frees,irq_calls;
static int sync_error,hw_error;
#define PCM_RUNTIME_CHECK(s) (!(s)->runtime)
static void synchronize_irq(int irq) { assert(irq>0);++irq_calls; }
static void do_free_pages(struct snd_card *c,struct snd_dma_buffer *b) { (void)c;++releases;free(b->area); }
static void kfree(void *p) { ++info_frees;free(p); }
static void snd_pcm_set_runtime_buffer(struct snd_pcm_substream *s,struct snd_dma_buffer *b) { assert(!b);++detaches;s->runtime->dma_buffer_p=NULL;s->runtime->dma_area=NULL; }
static int callback_sync(struct snd_pcm_substream *s) { (void)s;++sync_calls;return sync_error; }
static int callback_free(struct snd_pcm_substream *s) { (void)s;++hw_calls;return hw_error; }
'''
MAIN=r'''
int main(void) {
    unsigned cases=0,detached_after_error=0,released_after_error=0;
    const int errors[]={0,-EIO,-ETIMEDOUT};
    for(unsigned managed=0;managed<2;managed++)
    for(unsigned kind=0;kind<3;kind++)
    for(unsigned syncfail=0;syncfail<2;syncfail++)
    for(unsigned hwfail=0;hwfail<3;hwfail++)
    for(unsigned pending=0;pending<2;pending++)
    for(unsigned have_hw=0;have_hw<2;have_hw++) {
        sync_calls=hw_calls=releases=detaches=info_frees=irq_calls=0;
        sync_error=syncfail?-ETIMEDOUT:0;hw_error=errors[hwfail];
        struct snd_card card={.sync_irq=1};struct snd_pcm pcm={.card=&card};
        struct snd_pcm_ops ops={.sync_stop=callback_sync,.hw_free=have_hw?callback_free:NULL};
        struct snd_pcm_runtime runtime={.stop_operating=pending};
        struct snd_pcm_substream sub={.runtime=&runtime,.ops=&ops,.pcm=&pcm,.managed_buffer_alloc=managed};
        unsigned char preallocated[32];struct snd_dma_buffer *dynamic=NULL;
        if(kind==1) {sub.dma_buffer.area=preallocated;runtime.dma_buffer_p=&sub.dma_buffer;runtime.dma_area=preallocated;}
        if(kind==2) {dynamic=malloc(sizeof(*dynamic));assert(dynamic);dynamic->area=malloc(32);assert(dynamic->area);runtime.dma_buffer_p=dynamic;runtime.dma_area=dynamic->area;}
        int rc=do_hw_free(&sub);
        assert(rc==(have_hw?hw_error:0));assert(sync_calls==pending && hw_calls==have_hw && !irq_calls);
        assert(!runtime.stop_operating);assert(detaches==(managed&&kind!=0));
        assert(releases==(managed&&kind==2) && info_frees==releases);
        if(managed&&kind)assert(!runtime.dma_area && !runtime.dma_buffer_p);
        bool error=(pending&&syncfail)||(have_hw&&hwfail);
        if(error){detached_after_error+=detaches;released_after_error+=releases;}
        if(kind==2&&!managed){free(dynamic->area);free(dynamic);}
        ++cases;
    }
    printf("{\"cases\":%u,\"detachments_after_callback_error\":%u,\"dynamic_releases_after_callback_error\":%u}\n",cases,detached_after_error,released_after_error);
    return 0;
}
'''
parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--kernel',type=Path,required=True);parser.add_argument('--output',type=Path,required=True);args=parser.parse_args()
native=args.kernel/'sound/core/pcm_native.c';memory=args.kernel/'sound/core/pcm_memory.c'
sources={'snd_pcm_sync_stop':function(native.read_text(),'snd_pcm_sync_stop'),'snd_pcm_lib_free_pages':function(memory.read_text(),'snd_pcm_lib_free_pages'),'do_hw_free':function(native.read_text(),'do_hw_free')}
with tempfile.TemporaryDirectory(prefix='obsidian-free-contract-') as tmp:
 tmp=Path(tmp);(tmp/'test.c').write_text(PREFIX+'\n'.join(sources.values())+MAIN)
 r=subprocess.run(['clang','-std=c11','-O1','-Wall','-Wextra','-Werror','-fsanitize=address,undefined',str(tmp/'test.c'),'-o',str(tmp/'test')],capture_output=True,text=True)
 assert r.returncode==0,r.stderr
 r=subprocess.run([str(tmp/'test')],capture_output=True,text=True);assert r.returncode==0 and not r.stderr,(r.returncode,r.stderr)
 report={'scope':'Three actual ALSA core C functions, modeled callbacks and allocator. Contract test, not an ALSA bug claim or hardware DMA simulation.','passed':True,'source_sha256':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in (native,memory)},'extracted_function_sha256':{k:hashlib.sha256(v.encode()).hexdigest() for k,v in sources.items()},'result':json.loads(r.stdout),'sanitizers':'ASan/UBSan'}
 args.output.parent.mkdir(parents=True,exist_ok=True);args.output.write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report))
