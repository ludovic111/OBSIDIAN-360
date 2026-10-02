/* SPDX-License-Identifier: MIT */
#include "pcm_queue.h"
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define CHECK(c) do { if (!(c)) { fprintf(stderr, "FAIL:%d:%s\n", __LINE__, #c); exit(1); } } while (0)
struct fixture {
    struct obs_audio_queue q;
    uint32_t memory[16384];
    uint32_t expected[16384];
    unsigned ready[32];
    unsigned head, count, sequence;
};
static uint32_t rng = 0x721da883;
static unsigned operations, rejected, drains, publications;
static uint64_t frames_read;
static uint32_t random32(void) { rng = rng * 1664525U + 1013904223U; return rng; }
static void init(struct fixture *f, unsigned bytes) {
    memset(f, 0, sizeof(*f));memset(f->memory, 0xa5, sizeof(f->memory));
    CHECK(obs_audio_queue_init(&f->q, bytes) == OBS_AUDIO_OK);
}
static void publish(struct fixture *f, const struct obs_audio_queue *before,
                    const struct obs_audio_plan *p) {
    unsigned complete=f->q.queued_bytes-before->queued_bytes;
    CHECK(!!complete == !!p->publish);
    if(p->zero_bytes) {
        CHECK(f->q.draining && p->zero_bytes < f->q.block_bytes);
        CHECK(p->zero_offset==before->write_pos);
        CHECK(p->zero_offset+p->zero_bytes <= f->q.buffer_bytes);
        memset((unsigned char *)f->memory+p->zero_offset,0,p->zero_bytes);
    }
    unsigned end=before->published_pos;
    for(unsigned n=0;n<complete;n+=f->q.block_bytes) {
        unsigned slot=end/f->q.block_bytes;CHECK(!f->ready[slot]);f->ready[slot]=1;
        CHECK(end+f->q.block_bytes<=f->q.buffer_bytes);
        if(n+f->q.block_bytes==complete)CHECK(p->last_descriptor==slot);
        end=(end+f->q.block_bytes)%f->q.buffer_bytes;
    }
    CHECK(end==f->q.published_pos);publications+=p->publish;
}
static void push(struct fixture *f, unsigned frames) {
    struct obs_audio_queue before=f->q;
    struct obs_audio_plan p={0x55555555,0x55555555,0x55555555,0x55555555}, saved=p;
    int result=obs_audio_queue_push(&f->q,frames*4,&p);++operations;
    if(result!=OBS_AUDIO_OK) {
        CHECK(!memcmp(&before,&f->q,sizeof(before)) && !memcmp(&p,&saved,sizeof(p)));
        CHECK(result==(before.draining?OBS_AUDIO_DRAINING:OBS_AUDIO_FULL));++rejected;return;
    }
    CHECK(!p.zero_bytes && f->count+frames <= f->q.buffer_bytes/4);
    for(unsigned n=0;n<frames;n++) {
        uint32_t sample=(++f->sequence*2654435761U)|1U;
        f->memory[(before.write_pos/4+n)%(f->q.buffer_bytes/4)]=sample;
        f->expected[(f->head+f->count)%16384]=sample;++f->count;
    }
    publish(f,&before,&p);CHECK(f->q.logical_bytes==f->count*4);
}
static void consume(struct fixture *f,unsigned blocks) {
    struct obs_audio_queue before=f->q;
    unsigned bytes=blocks*f->q.block_bytes, logical=0xabcdef01;
    int result=obs_audio_queue_consume(&f->q,bytes,&logical);++operations;
    if(bytes>before.queued_bytes) {
        CHECK(result==OBS_AUDIO_INVALID && logical==0xabcdef01);
        CHECK(!memcmp(&before,&f->q,sizeof(before)));++rejected;return;
    }
    CHECK(result==OBS_AUDIO_OK);
    unsigned count=bytes/4 < f->count ? bytes/4 : f->count;
    CHECK(logical==count*4);
    for(unsigned n=0;n<bytes/4;n++) {
        unsigned physical=(before.read_pos/4+n)%(before.buffer_bytes/4);
        CHECK(f->ready[physical/(before.block_bytes/4)]);
        if(n<count) {
            CHECK(f->memory[physical]==f->expected[f->head]);f->head=(f->head+1)%16384;--f->count;++frames_read;
        }else CHECK(before.draining && f->memory[physical]==0);
    }
    for(unsigned n=0;n<blocks;n++)f->ready[(before.read_pos/before.block_bytes+n)%32]=0;
    CHECK(f->q.logical_bytes==f->count*4);
    CHECK(f->q.logical_read_pos==(before.logical_read_pos+logical)%before.buffer_bytes);
}
static void drain(struct fixture *f) {
    struct obs_audio_queue before=f->q;struct obs_audio_plan p;
    CHECK(obs_audio_queue_drain(&f->q,&p)==OBS_AUDIO_OK);++operations;++drains;
    publish(f,&before,&p);CHECK(f->q.tail_bytes==0 && f->q.logical_bytes==f->count*4);
}
static void delta_tests(void) {
    unsigned out=0;
    CHECK(obs_audio_forward_delta(0,1024,1ULL<<62,1024,&out)==0 && out==1024);
    CHECK(obs_audio_forward_delta((1ULL<<62)-16,16,1ULL<<62,1024,&out)==0 && out==32);
    CHECK(obs_audio_forward_delta((1ULL<<58)+17,(1ULL<<58)+21,1ULL<<62,1024,&out)==0 && out==4);
    CHECK(obs_audio_forward_delta(UINT64_MAX-7,0,UINT64_MAX-3,4,&out)==0 && out==4);
    CHECK(obs_audio_forward_delta(17,17,4096,1024,&out)==0 && out==0);
    const uint64_t bad[][4]={{10,9,4096,1024},{0,1025,4096,1024},{0,4096,4096,1024},{4096,0,4096,1024},{0,0,0,0},{0,0,1024,1024},{0,0,4095,1024},{0,0,1ULL<<62,32768}};
    for(unsigned i=0;i<sizeof(bad)/sizeof(*bad);i++) {
        out=0x12345678;CHECK(obs_audio_forward_delta(bad[i][0],bad[i][1],bad[i][2],(unsigned)bad[i][3],&out)==OBS_AUDIO_INVALID && out==0x12345678);
    }
    CHECK(obs_audio_forward_delta(0,0,4096,1024,NULL)==OBS_AUDIO_INVALID);
}
static void invalid_tests(void) {
    struct obs_audio_queue q, before;struct obs_audio_plan p={1,2,3,4}, psaved=p;
    CHECK(obs_audio_queue_init(&q,4096)==0);before=q;
    unsigned bad[]={0,4,64,132,65540,UINT32_MAX};
    for(unsigned i=0;i<sizeof(bad)/sizeof(*bad);i++)CHECK(obs_audio_queue_init(&q,bad[i])==OBS_AUDIO_INVALID && !memcmp(&q,&before,sizeof(q)));
    CHECK(obs_audio_queue_init(NULL,4096)==OBS_AUDIO_INVALID);
    CHECK(obs_audio_queue_push(&q,1,&p)==OBS_AUDIO_INVALID && !memcmp(&q,&before,sizeof(q)) && !memcmp(&p,&psaved,sizeof(p)));
    CHECK(obs_audio_queue_push(&q,4,NULL)==OBS_AUDIO_INVALID);
    CHECK(obs_audio_queue_drain(&q,NULL)==OBS_AUDIO_INVALID);
    unsigned out=42;CHECK(obs_audio_queue_consume(&q,4,&out)==OBS_AUDIO_INVALID && out==42);
    CHECK(obs_audio_queue_consume(&q,0,NULL)==OBS_AUDIO_INVALID);
    /* An uninitialized/corrupted accounting state must not divide by zero. */
    memset(&q,0,sizeof(q));before=q;
    CHECK(obs_audio_queue_push(&q,4,&p)==OBS_AUDIO_INVALID && !memcmp(&q,&before,sizeof(q)));
    q=before;CHECK(obs_audio_queue_drain(&q,&p)==OBS_AUDIO_INVALID);
    q=before;CHECK(obs_audio_queue_consume(&q,0,&out)==OBS_AUDIO_INVALID);
}
int main(void) {
    struct fixture *a=calloc(1,sizeof(*a)),*b=calloc(1,sizeof(*b));CHECK(a && b);
    delta_tests();invalid_tests();
    for(unsigned bytes=128;bytes<=65536;bytes+=128) {
        init(a,bytes);push(a,bytes/4);CHECK(a->q.queued_bytes==bytes && !a->q.tail_bytes);
        push(a,1);consume(a,32);drain(a);drain(a);CHECK(!a->q.logical_bytes && !a->q.queued_bytes);
        init(a,bytes);push(a,1);drain(a);drain(a);push(a,1);consume(a,1);
        CHECK(!a->count && !a->q.queued_bytes && a->q.logical_read_pos==4);
    }
    const unsigned sizes[]={128,256,384,512,640,1024,2048,3968,4096,8192,16384,32768,65408,65536};
    for(unsigned size=0;size<sizeof(sizes)/sizeof(*sizes);size++) {
        for(unsigned seed=0;seed<8;seed++) {
            init(a,sizes[size]);init(b,sizes[(size+5)%(sizeof(sizes)/sizeof(*sizes))]);
            for(unsigned step=0;step<400;step++) {
                struct fixture *f=(random32()&0x80)?a:b;
                if(random32()&0x100) {
                    unsigned free_frames=(f->q.buffer_bytes-f->q.logical_bytes)/4;
                    push(f,random32()%(free_frames+2));
                }else consume(f,random32()%(f->q.queued_bytes/f->q.block_bytes+2));
            }
            struct fixture *both[]={a,b};
            for(unsigned n=0;n<2;n++) {
                struct fixture *f=both[n];drain(f);drain(f);
                while(f->q.queued_bytes)consume(f,1);
                CHECK(f->count==0 && f->q.logical_bytes==0);
                for(unsigned k=0;k<32;k++)CHECK(!f->ready[k]);
            }
        }
    }
    printf("{\"all_buffer_sizes\":512,\"randomized_steps\":44800,\"operations\":%u,\"rejections\":%u,\"drains\":%u,\"publications\":%u,\"logical_frames_checked\":%llu}\n",operations,rejected,drains,publications,(unsigned long long)frames_read);
    free(a);free(b);return 0;
}
