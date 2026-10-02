#!/usr/bin/env python3
"""Test real bounded SMC post/probe/remove plus Linux atomic polling macros.

Serial model of locks, IRQ flags, MMIO and delays; no hardware and no timing claim.
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
    match = re.search(r'^(?:static )?[\w *]+\b' + name + r'\s*\([^;]*?\n\{', source, re.M)
    if not match:
        raise ValueError(name)
    return source[match.start():source.index('\n}', match.end())+2]


def macro(source, name):
    lines = source.splitlines(True)
    for index, line in enumerate(lines):
        if line.startswith('#define ' + name + '('):
            result = line
            while lines[index].rstrip().endswith('\\'):
                index += 1
                result += lines[index]
            return result
    raise ValueError(name)


PREFIX = r'''
#include <stdint.h>
#include <stdbool.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <errno.h>
typedef uint64_t u64; typedef int64_t s64; typedef uint32_t u32;
typedef int spinlock_t; typedef int wait_queue_head_t;
#define __iomem
#define NSEC_PER_USEC 1000
#define DEFINE_MUTEX(n) int n
#define CHECK(c) do { if(!(c)) {fprintf(stderr,"MODEL_ASSERT:%s\n",#c);exit(97);} } while(0)
#define barrier() ((void)0)
#define cpu_relax() ((void)0)
#define KERN_INFO ""
#define KERN_ERR ""
#define DRV_NAME "xenon_smc_core"
#define DRV_VERSION "0.1"
#define dev_printk(...) ((void)0)
#define printk(...) ((void)0)
#define IRQF_SHARED 1
static int reads, delays, writes, sent, ready_after=1, fifo_held, irq_disabled;
static int enabled, reserved, mapped, irq_owned, intx, lifecycle_acquired;
static const char *fault;
static unsigned char regs[256], transmitted[16];
static int fail(const char *s) { return fault && strcmp(fault,s)==0; }
static int mutex_trylock(int *m) { if(*m)return 0;*m=1;++lifecycle_acquired;return 1; }
static void mutex_lock(int *m) { CHECK(mutex_trylock(m)); }
static void mutex_unlock(int *m) { CHECK(*m);*m=0;--lifecycle_acquired; }
static int fifo_trylock(spinlock_t *p, unsigned long *flags) {
    CHECK(*p);*flags=irq_disabled;irq_disabled=1;
    if(fifo_held) {irq_disabled=*flags;return 0;}
    fifo_held=1;return 1;
}
#define spin_trylock_irqsave(p,f) fifo_trylock((p),&(f))
#define spin_unlock_irqrestore(p,f) do {CHECK(*(p));CHECK(fifo_held);fifo_held=0;irq_disabled=(f);}while(0)
static void spin_lock_init(spinlock_t *p) { *p=1; }
static void init_waitqueue_head(wait_queue_head_t *p) { *p=1; }
static void udelay(unsigned long us) { CHECK(us==1);++delays; }
static u32 readl(void *p) {CHECK(mapped);CHECK(fifo_held);CHECK(irq_disabled);CHECK(p==regs+0x84);++reads;CHECK(reads<=1002);return ready_after>0 && reads>=ready_after?4:0;}
static void writel(u32 value,void *p) {
    CHECK(mapped);CHECK(fifo_held);CHECK(p==regs+0x84);
    CHECK((writes==0 && value==4 && sent==0)||(writes==1 && value==0 && sent==1));++writes;
}
static void writesl(void *p,const void *data,int count) {
    CHECK(mapped);CHECK(fifo_held);CHECK(p==regs+0x80);CHECK(count==4);CHECK(writes==1);CHECK(!sent);
    CHECK(((uintptr_t)data % _Alignof(u32))==0);memcpy(transmitted,data,16);++sent;
}
struct device { int unused; }; struct pci_dev {struct device dev;int irq;}; struct pci_device_id {int unused;};
static int pci_enable_device(struct pci_dev *p) {(void)p;if(fail("enable"))return -EIO;enabled=1;return 0;}
static void pci_disable_device(struct pci_dev *p) {(void)p;CHECK(enabled);enabled=0;}
static int pci_request_regions(struct pci_dev *p,const char *s) {(void)p;(void)s;if(fail("regions"))return -EBUSY;reserved=1;return 0;}
static void pci_release_regions(struct pci_dev *p) {(void)p;CHECK(reserved);reserved=0;}
static void pci_intx(struct pci_dev *p,int value) {(void)p;intx=value;}
static unsigned long pci_resource_start(struct pci_dev *p,int bar) {(void)p;(void)bar;return 0x1000;}
static void *ioremap(unsigned long addr,int size) {CHECK(addr==0x1000);CHECK(size==256);if(fail("map"))return NULL;mapped=1;return regs;}
static void iounmap(void *p) {CHECK(p==regs);CHECK(mapped);CHECK(!irq_owned);mapped=0;}
static int request_irq(int irq,int (*fn)(int,void *),int flags,const char *name,void *dev) {(void)irq;(void)fn;(void)flags;(void)name;(void)dev;CHECK(mapped);if(fail("irq"))return -EBUSY;irq_owned=1;return 0;}
static void free_irq(int irq,void *dev) {(void)irq;(void)dev;CHECK(!intx);CHECK(irq_owned);irq_owned=0;}
static int xenon_smc_irq(int irq,void *dev) {(void)irq;(void)dev;return 0;}
static void _xenon_smc_send(void *msg) {(void)msg;}
static void _xenon_smc_wait(void *msg) {(void)msg;}
static int _xenon_smc_reply(void *msg) {(void)msg;return 0;}
static int _xenon_smc_cached_reply(void *msg) {(void)msg;return 0;}
'''

MAIN = r'''
int main(int argc,char **argv) {
    if(argc!=2)return 2;fault=argv[1];
    struct pci_dev dev={.irq=5};struct pci_device_id id={0};
    unsigned char buffer[20] __attribute__((aligned(4)));unsigned char *msg=buffer+1;
    for(unsigned i=0;i<16;i++)msg[i]=(unsigned char)(0x80+i);
    msg[0]=0x8d;
    if(fail("enable")||fail("regions")||fail("map")||fail("irq")) {
        int want=fail("enable")?-EIO:fail("map")?-ENOMEM:-EBUSY;
        CHECK(xenon_smc_init_one(&dev,&id)==want);
        CHECK(!smc.base);CHECK(!smc.send);CHECK(!mapped);CHECK(!reserved);CHECK(!enabled);CHECK(!irq_owned);CHECK(!smc_lifecycle_lock);
        CHECK(xenon_smc_post(msg,1000)==-ENODEV);
        printf("%s: partial probe clean, post rejected\n",fault);return 0;
    }
    if(fail("preprobe")) { CHECK(xenon_smc_post(msg,1000)==-ENODEV);CHECK(!reads);CHECK(!writes);return 0; }
    CHECK(xenon_smc_init_one(&dev,&id)==0);
    if(fail("double_probe")) {CHECK(xenon_smc_init_one(&dev,&id)==-EBUSY);xenon_smc_remove(&dev);CHECK(!mapped);CHECK(!enabled);return 0;}
    unsigned budget=1000;int want=0, initial_irq=fail("irq_disabled");irq_disabled=initial_irq;
    const unsigned char *input=msg;
    if(fail("null")){input=NULL;want=-EINVAL;}
    if(fail("reply")){msg[0]=0x01;want=-EINVAL;}
    if(fail("zero")){budget=0;want=-EINVAL;}
    if(fail("too_large")){budget=1001;want=-EINVAL;}
    if(fail("lifecycle_busy")){smc_lifecycle_lock=1;want=-EBUSY;}
    if(fail("fifo_busy")){fifo_held=1;want=-EBUSY;}
    if(fail("ready_later"))ready_after=500;
    if(fail("ready_last"))ready_after=1001;
    if(fail("never")){ready_after=0;want=-ETIMEDOUT;}
    if(fail("short_never")){ready_after=0;budget=1;want=-ETIMEDOUT;}
    if(fail("short_ready_last")){ready_after=2;budget=1;}
    CHECK(xenon_smc_post(input,budget)==want);
    CHECK(irq_disabled==initial_irq);
    if(want==0){CHECK(writes==2);CHECK(sent==1);CHECK(memcmp(msg,transmitted,16)==0);}
    else {CHECK(writes==0);CHECK(sent==0);}
    if(want==-ETIMEDOUT){CHECK(reads==(int)budget+1);CHECK(delays==(int)budget);}
    if(want==-EINVAL||want==-EBUSY)CHECK(reads==0);
    if(fail("lifecycle_busy")){CHECK(smc_lifecycle_lock);smc_lifecycle_lock=0;}
    else CHECK(!smc_lifecycle_lock);
    if(fail("fifo_busy")){CHECK(fifo_held);fifo_held=0;}
    else CHECK(!fifo_held);
    xenon_smc_remove(&dev);
    CHECK(!smc.base && !smc.send && !smc.wait && !smc.reply && !smc.cached);
    CHECK(!mapped && !enabled && !reserved && !irq_owned && !lifecycle_acquired);
    int old_reads=reads;CHECK(xenon_smc_post(msg,1000)==(msg[0]&0x80?-ENODEV:-EINVAL));CHECK(reads==old_reads);
    printf("%s: ret=%d reads=%d delays=%d writes=%d payloads=%d\n",fault,want,reads,delays,writes,sent);
    return 0;
}
'''


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--source',type=Path,required=True)
    p.add_argument('--iopoll',type=Path,required=True)
    p.add_argument('--output',type=Path,required=True)
    a = p.parse_args()
    source = a.source.read_text(); polling = a.iopoll.read_text()
    structs = source[source.index('struct xenon_smc\n'):source.index('static unsigned char smc_reply')]
    macros = '\n'.join(macro(polling,n) for n in ['poll_timeout_us_atomic','read_poll_timeout_atomic','readx_poll_timeout_atomic','readl_poll_timeout_atomic'])
    functions = '\n'.join(function(source,n) for n in ['xenon_smc_post','xenon_smc_init_one','xenon_smc_remove'])
    cases = ['enable','regions','map','irq','preprobe','double_probe','null','reply','zero','too_large','lifecycle_busy','fifo_busy','ready','ready_later','ready_last','never','short_never','short_ready_last','irq_disabled']
    r = {'scope':'Actual C post/probe/remove and actual Linux atomic poll macros, with serial lock/MMIO/delay model; no hardware timing or concurrent schedule validation. Legacy send/wait paths unchanged and not tested here.', 'source_sha256':hashlib.sha256(a.source.read_bytes()).hexdigest(),'iopoll_sha256':hashlib.sha256(a.iopoll.read_bytes()).hexdigest(),'cases':[]}
    with tempfile.TemporaryDirectory(prefix='obsidian-smc-post-') as tmp:
        src=Path(tmp)/'test.c';binary=Path(tmp)/'test'
        src.write_text(PREFIX+structs+macros+functions+MAIN)
        build=subprocess.run(['clang','-std=gnu11','-O1','-g','-Wall','-Wextra','-Werror','-Wno-unused-parameter','-fsanitize=address,undefined',str(src),'-o',str(binary)],capture_output=True,text=True,timeout=30)
        r['compile']={'code':build.returncode,'diagnostics':build.stderr.replace(tmp,'HOST_TEST')}
        if build.returncode==0:
            for case in cases:
                result=subprocess.run([str(binary),case],capture_output=True,text=True,timeout=10,env=dict(os.environ,ASAN_OPTIONS='detect_leaks=0:halt_on_error=1',UBSAN_OPTIONS='halt_on_error=1'))
                r['cases'].append({'name':case,'code':result.returncode,'stdout':result.stdout.strip(),'diagnostics':result.stderr.replace(tmp,'HOST_TEST')})
    r['passed']=r['compile']['code']==0 and len(r['cases'])==len(cases) and all(c['code']==0 and not c['diagnostics'] for c in r['cases'])
    a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(r,indent=2)+'\n')
    print(json.dumps({'passed':r['passed'],'cases':len(r['cases']),'failed':[c['name'] for c in r['cases'] if c['code']]}))
    raise SystemExit(0 if r['passed'] else 1)


if __name__=='__main__':main()
