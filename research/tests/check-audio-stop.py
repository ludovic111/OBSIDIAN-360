#!/usr/bin/env python3
"""Verify actual one-shot STOP gate and write footprint, on ordinary memory."""
import hashlib,json,subprocess,tempfile
from pathlib import Path
root=Path(__file__).resolve().parents[2]
source=root/'research/audio/stop_analog_once.c'
harness=r'''
#define main observer_main
#include "stop_analog_once.c"
#undef main
#include <assert.h>
int main(void) {
    uint32_t value=0;
    assert(stop_value(0x1d08001c,0x1d08001c,&value)==0);
    assert(value==0x00080000 && !(value&0x1f00001c));
    unsigned refusals=0;
    for(unsigned bit=0;bit<32;bit++) {
        value=0xdeadbeef;
        assert(stop_value(0x1d08001c^(UINT32_C(1)<<bit),0x1d08001c,&value)==-1);
        assert(value==0xdeadbeef);++refusals;
        assert(stop_value(0x1d08001c,0x1d08001c^(UINT32_C(1)<<bit),&value)==-1);
        assert(value==0xdeadbeef);++refusals;
    }
    assert(refusals==64);
    uint32_t memory[16];memset(memory,0xa5,sizeof(memory));
    assert(stop_value(0x1d08001c,0x1d08001c,&value)==0);
    write_stop((volatile unsigned char *)memory,value);
    unsigned char *bytes=(unsigned char *)memory;
    for(unsigned i=0;i<sizeof(memory);i++)
        assert(bytes[i]==(i==10?8:(i>=8&&i<=11?0:0xa5)));
    size_t offset;assert(bar_offset(UINT64_C(0x200ea001600),UINT64_C(0x200ea00163f),65536,&offset)==0 && offset==0x1600);
    char *argv[]={"stop_analog_once",NULL};assert(observer_main(1,argv)==2);
    puts("{\"eligible_state\":1,\"single_bit_refusals\":64,\"write_offset\":8,\"write_bytes\":4,\"write_value\":\"0x00080000\",\"no_argument_code\":2}");
    return 0;
}
'''
with tempfile.TemporaryDirectory(prefix='obsidian-stop-') as t:
 t=Path(t);(t/'test.c').write_text(harness)
 r=subprocess.run(['clang','-std=c11','-O1','-Wall','-Wextra','-Werror','-fsanitize=address,undefined','-I',str(source.parent),str(t/'test.c'),'-o',str(t/'test')],capture_output=True,text=True)
 assert r.returncode==0,r.stderr
 r=subprocess.run([str(t/'test')],capture_output=True,text=True)
 assert r.returncode==0 and r.stderr=='Usage: stop_analog_once --stop-analog-once\n',(r.returncode,r.stderr)
 data={'scope':'Actual C gate and store on ordinary memory with guards; no hardware semantics validated','source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'passed':True,'sanitizers':'ASan/UBSan','result':json.loads(r.stdout)}
 p=root/'evidence/2026-10-02/audio-stop/host-validation.json';p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(data,indent=2)+'\n');print(json.dumps(data))
