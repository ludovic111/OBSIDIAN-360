/* Original test scaffolding, MIT. Models ownership, not hardware semantics. */
#include <assert.h>
#include <errno.h>
#include <stdbool.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#define index card_index
typedef uint32_t u32;
typedef uint64_t dma_addr_t;
typedef int spinlock_t;
struct timer_list { int initialized, pending; };
struct device { int unused; };
struct pci_dev { struct device dev; int irq; void *data; };
struct pci_device_id { int unused; };
struct snd_pcm_substream { int unused; };
struct snd_device;
struct snd_device_ops { int (*dev_free)(struct snd_device *); };
struct snd_device { void *device_data; struct snd_device_ops *ops; };
struct snd_pcm { void *private_data; char name[32]; int index; void *managed_buffer; };
struct snd_card {
    void *private_data;
    void (*private_free)(struct snd_card *);
    struct snd_device *lowlevel;
    struct snd_pcm *pcms[2]; int pcm_count;
    char driver[32], shortname[32], longname[80];
};
static const char *fault;
static int live_allocs, enabled, regions, mapped, irq_owned, dma_owned;
static int bus_master, locked, active_dma, active_timer, smc_calls;
static dma_addr_t allocated_handle;
static uint64_t dma_mask;
static unsigned char registers[4096];
static int index[1], enable[1]={1}; static char *id[1];
static int snd_xenon_ana_playback_ops, snd_xenon_spdif_playback_ops;
#define GFP_KERNEL 1
#define IORESOURCE_MEM 0x200
#define EPROBE_DEFER 517
#define DMA_BIT_MASK(n) ((1ULL<<(n))-1)
#define SNDRV_CARDS 1
#define SNDRV_PCM_DEFAULT_CON_SPDIF 0
#define SNDRV_PCM_STREAM_PLAYBACK 0
#define SNDRV_DMA_TYPE_DEV 0
#define SNDRV_DEV_LOWLEVEL 0
#define IRQF_SHARED 0
#define IRQ_ENABLE 1
#define IRQ_DISABLE 0
#define THIS_MODULE NULL
#define KERN_ERR ""
#define KERN_WARNING ""
#define DESCRIPTOR_BUFFER_SIZE (32 * sizeof(u32) * 2)
#define CHECK(c) do { if(!(c)) { fprintf(stderr,"MODEL_ASSERT:%s\n",#c); exit(97); } } while(0)
#define printk(...) ((void)0)
#define snd_printk(...) ((void)0)
#define dev_err(...) ((void)0)
static int fail(const char *s) { return strcmp(fault,s)==0; }
static void *alloc(size_t bytes) { void *p=calloc(1,bytes); CHECK(p); ++live_allocs; return p; }
static void drop(void *p) { if(p) { --live_allocs; free(p); } }
static void *kzalloc(size_t size,int flags) { (void)flags; return fail("chip_alloc")?NULL:alloc(size); }
static void kfree(void *p) { drop(p); }
static void spin_lock_init(spinlock_t *p) { *p=1; }
static void spin_lock_irq(spinlock_t *p) { CHECK(*p==1); CHECK(!locked); locked=1; }
static void spin_unlock_irq(spinlock_t *p) { CHECK(*p==1); CHECK(locked); locked=0; }
#define spin_lock_irqsave(p, f) do { (f)=0; spin_lock_irq(p); } while(0)
#define spin_unlock_irqrestore(p, f) do { (void)(f); spin_unlock_irq(p); } while(0)
static void timer_setup(struct timer_list *t,void (*fn)(struct timer_list *),int flags) {
    (void)fn; (void)flags; t->initialized=1;
}
static int timer_shutdown_sync(struct timer_list *t) {
    CHECK(t->initialized); CHECK(!locked); t->pending=0; active_timer=0; return 0;
}
static int del_timer_sync(struct timer_list *t) { return timer_shutdown_sync(t); }
static int pci_enable_device(struct pci_dev *p) { (void)p; if(fail("pci_enable")) return -EBUSY; enabled=1; return 0; }
static void pci_disable_device(struct pci_dev *p) { (void)p; CHECK(enabled); enabled=0; bus_master=0; }
static void pci_set_master(struct pci_dev *p) { (void)p; CHECK(enabled); bus_master=1; }
static void pci_clear_master(struct pci_dev *p) { (void)p; CHECK(enabled); bus_master=0; }
static unsigned long pci_resource_flags(struct pci_dev *p,int i) { (void)p; (void)i; return fail("bar_type")?0:IORESOURCE_MEM; }
static unsigned long pci_resource_len(struct pci_dev *p,int i) { (void)p; (void)i; return fail("bar_short")?16:4096; }
static unsigned long pci_resource_start(struct pci_dev *p,int i) { (void)p; (void)i; return 0x200ea001000UL; }
static int dma_set_mask_and_coherent(struct device *d,uint64_t mask) {
    (void)d; CHECK(mask==DMA_BIT_MASK(29)); if(fail("dma_mask")) return -EIO; dma_mask=mask; return 0;
}
static int pci_request_regions(struct pci_dev *p,const char *name) { (void)p;(void)name;if(fail("regions")) return -EBUSY;regions=1;return 0; }
static void pci_release_regions(struct pci_dev *p) { (void)p;CHECK(regions);regions=0; }
static void *ioremap(unsigned long addr,unsigned long size) { (void)addr;(void)size;if(fail("ioremap"))return NULL;CHECK(!mapped);mapped=1;return registers; }
static void iounmap(void *p) { CHECK(p==registers);CHECK(mapped);mapped=0; }
static void writel(uint64_t value,void *p) {
    CHECK(mapped); CHECK(p>= (void *)registers && p<(void *)(registers+4096));
    if(p==registers+0x08 || p==registers+0x18) { if(value==0) active_dma=0; }
}
static unsigned readl(void *p) { CHECK(mapped);(void)p;return 0; }
static void *dma_alloc_coherent(struct device *d,size_t size,dma_addr_t *handle,int flags) {
    (void)d;(void)flags;CHECK(!locked);if(fail("dma_alloc"))return NULL;
    CHECK(dma_mask==DMA_BIT_MASK(29));*handle=allocated_handle=0x01000000;dma_owned=1;return alloc(size);
}
static void dma_free_coherent(struct device *d,size_t size,void *p,dma_addr_t handle) {
    (void)d;(void)size;CHECK(dma_owned);CHECK(handle==allocated_handle);CHECK(!active_dma);dma_owned=0;drop(p);
}
static void *pci_alloc_consistent(struct pci_dev *p,size_t size,dma_addr_t *handle) {
    (void)p;if(fail("dma_alloc"))return NULL;
    *handle=allocated_handle=fail("dma_handle")?0x61000000:0x01000000;dma_owned=1;return alloc(size);
}
static void pci_free_consistent(struct pci_dev *p,size_t size,void *addr,dma_addr_t handle) {
    dma_free_coherent(&p->dev,size,addr,handle);
}
static int request_irq(int irq,int (*fn)(int,void *),int flags,const char *name,void *data) {
    (void)irq;(void)fn;(void)flags;(void)name;(void)data;if(fail("irq"))return -EBUSY;irq_owned=1;return 0;
}
static void free_irq(int irq,void *data) { (void)irq;(void)data;CHECK(irq_owned);irq_owned=0; }
static void pci_intx(struct pci_dev *p,int flag) { (void)p;(void)flag; }
static int xenon_smc_ready(void) { return !fail("smc_ready"); }
static int xenon_smc_message(void *msg) { CHECK(((unsigned char *)msg)[0]==0x8d);++smc_calls;return fail("smc_send")?-EIO:fail("smc_busy")?-EBUSY:fail("smc_timeout")?-ETIMEDOUT:0; }
static int xenon_smc_post(const unsigned char *msg,unsigned budget) { CHECK(budget==1000);return xenon_smc_message((void *)msg); }
static void xenon_smc_send_message(void *msg) { (void)xenon_smc_message(msg); }
static int snd_card_new(struct device *d,int index,const char *id,void *module,int extra,struct snd_card **out) {
    (void)d;(void)index;(void)id;(void)module;(void)extra;if(fail("card"))return -ENOSPC;*out=alloc(sizeof(**out));return 0;
}
static int snd_pcm_new(struct snd_card *card,const char *name,int device,int playback,int capture,struct snd_pcm **out) {
    (void)name;(void)playback;(void)capture;
    if((device==0 && fail("pcm0"))||(device==1 && fail("pcm1")))return -ENOMEM;
    *out=alloc(sizeof(**out));(*out)->index=device;card->pcms[card->pcm_count++]=*out;return 0;
}
static void snd_pcm_set_ops(struct snd_pcm *p,int stream,void *ops) { (void)p;(void)stream;(void)ops; }
static void snd_pcm_lib_preallocate_pages_for_all(struct snd_pcm *p,int type,struct device *d,size_t min,size_t max) { (void)p;(void)type;(void)d;(void)min;(void)max; }
static int snd_pcm_set_managed_buffer_all(struct snd_pcm *p,int type,struct device *d,size_t min,size_t max) {
    (void)type;(void)d;CHECK(min==65536 && max==65536);
    if((p->index==0 && fail("buffer0")) || (p->index==1 && fail("buffer1")))return -ENOMEM;
    p->managed_buffer=alloc(min);return 0;
}
static int snd_device_new(struct snd_card *card,int type,void *chip,struct snd_device_ops *ops) {
    (void)type;if(fail("lowlevel"))return -ENOMEM;card->lowlevel=alloc(sizeof(*card->lowlevel));card->lowlevel->device_data=chip;card->lowlevel->ops=ops;return 0;
}
static void snd_card_set_dev(struct snd_card *c,struct device *d) { (void)c;(void)d; }
static int snd_card_register(struct snd_card *c) { (void)c;return fail("register")?-EIO:0; }
static void snd_card_free(struct snd_card *card) {
    if(!card)return;
    CHECK(!active_dma);CHECK(!active_timer);
    for(int i=0;i<card->pcm_count;i++){drop(card->pcms[i]->managed_buffer);drop(card->pcms[i]);}
    if(card->lowlevel) { card->lowlevel->ops->dev_free(card->lowlevel);drop(card->lowlevel); }
    if(card->private_free)card->private_free(card);
    drop(card);
}
static void pci_set_drvdata(struct pci_dev *p,void *data) { p->data=data; }
static void *pci_get_drvdata(struct pci_dev *p) { return p->data; }
