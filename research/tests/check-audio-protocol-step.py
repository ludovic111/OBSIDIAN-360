#!/usr/bin/env python3
"""Exercise the real gated ACK/reset code on ordinary memory, never hardware."""
import hashlib,json,subprocess,tempfile
from pathlib import Path
root=Path(__file__).resolve().parents[2];source=root/'research/audio/analog_protocol_step.c'
harness=r'''
#define main observer_main
#include "analog_protocol_step.c"
#undef main
#include <assert.h>
int main(void) {
    unsigned refusals=0;
    const uint32_t expected[]={4,8,16,0x02000000};
    for(unsigned i=0;i<4;i++) {
        const struct protocol_step *s=select_step(steps[i].option);assert(s==&steps[i]);
        uint32_t words[]={s->before,0x1d08001c,0,0x9616},value=0;
        assert(step_value(s,words[0],words[1],words[2],words[3],&value)==0);
        assert(value==expected[i] && !(value&0x1d000000));
        if(i<3)assert(!(value&0x02000000));
        for(unsigned j=0;j<4;j++)for(unsigned b=0;b<32;b++) {
            words[j]^=UINT32_C(1)<<b;value=0xdeadbeef;
            assert(step_value(s,words[0],words[1],words[2],words[3],&value)==-1 && value==0xdeadbeef);
            words[j]^=UINT32_C(1)<<b;++refusals;
        }
        uint32_t memory[16];memset(memory,0xa5,sizeof(memory));
        write_step((volatile unsigned char *)memory,expected[i]);
        unsigned char *bytes=(unsigned char *)memory;
        for(unsigned j=0;j<sizeof(memory);j++)assert(bytes[j]==(j>=8&&j<12?((expected[i]>>(8*(j-8)))&255):0xa5));
    }
    uint32_t value=123;assert(step_value(NULL,0,0,0,0,&value)==-1 && value==123);
    assert(!select_step("--start") && !select_step("--ack-bit1") && !select_step(""));
    size_t offset;assert(bar_offset(UINT64_C(0x200ea001600),UINT64_C(0x200ea00163f),65536,&offset)==0 && offset==0x1600);
    assert(refusals==512);
    puts("{\"steps\":4,\"single_bit_refusals\":512,\"stores_per_step\":1,\"store_offset\":8,\"store_bytes\":4,\"run_and_irq_bits_never_set\":true}");
    return 0;
}
'''
with tempfile.TemporaryDirectory(prefix='obsidian-ack-') as t:
 t=Path(t);(t/'test.c').write_text(harness)
 r=subprocess.run(['clang','-std=c11','-O1','-Wall','-Wextra','-Werror','-fsanitize=address,undefined','-I',str(source.parent),str(t/'test.c'),'-o',str(t/'test')],capture_output=True,text=True);assert r.returncode==0,r.stderr
 r=subprocess.run([str(t/'test')],capture_output=True,text=True);assert r.returncode==0 and not r.stderr,(r.returncode,r.stderr)
 data={'scope':'Actual step selector, preconditions and aligned store on ordinary memory; hardware ACK/reset semantics untested by this harness','passed':True,'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'result':json.loads(r.stdout),'sanitizers':'ASan/UBSan'}
 p=root/'evidence/2026-10-02/audio-ack/host-validation.json';p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(data,indent=2)+'\n');print(json.dumps(data))
