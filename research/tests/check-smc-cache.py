#!/usr/bin/env python3
"""Test the SMC cache's real C lookup on the host, without SMC messages."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import tempfile

PREFIX = '#include <stdio.h>\n#include <stddef.h>\n#define ARRAY_SIZE(a) (sizeof(a)/sizeof((a)[0]))\n'
MAIN = r'''
int main(int argc, char **argv) {
    if(argc!=2) return 2;
    unsigned char msg[16]={0};
    if(argv[1][0]=='k') {
        for(unsigned i=0;i<ARRAY_SIZE(smc_reply);i++) {
            msg[0]=smc_reply[i][0];
            if(_xenon_smc_cache_lookup(msg)!=smc_reply[i]) return 3;
        }
        printf("13 known reply IDs preserved\n");
    } else {
        unsigned found=0;
        for(unsigned i=0;i<256;i++) {
            msg[0]=i;
            unsigned char *p=_xenon_smc_cache_lookup(msg);
            if(p) {
                int known=0;
                for(unsigned j=0;j<ARRAY_SIZE(smc_reply);j++) if(p==smc_reply[j]) known=1;
                if(!known || p[0]!=i) return 4;
                found++;
            }
        }
        if(found!=13) return 5;
        printf("256 IDs checked; exactly 13 cache hits\n");
    }
    return 0;
}
'''


def code(source):
    table=source[source.index('static unsigned char smc_reply'):source.index('int xenon_smc_ready')]
    lookup=source[source.index('static unsigned char * _xenon_smc_cache_lookup('):source.index('static int _xenon_smc_cached_reply(')]
    return PREFIX+table+lookup+MAIN


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--original',type=Path,required=True)
    parser.add_argument('--candidate',type=Path,required=True)
    args=parser.parse_args()
    results=[]
    with tempfile.TemporaryDirectory(prefix='obsidian-smc-') as tmp:
        for name,path in [('original',args.original),('candidate',args.candidate)]:
            src=Path(tmp)/(name+'.c');binary=Path(tmp)/name
            src.write_text(code(path.read_text()))
            subprocess.run(['clang','-O0','-g','-fsanitize=address',str(src),'-o',str(binary)],capture_output=True,check=True,timeout=30)
            for scope in ('known','all'):
                p=subprocess.run([str(binary),scope],capture_output=True,text=True,timeout=10,env=dict(os.environ,ASAN_OPTIONS='detect_leaks=0:halt_on_error=1:abort_on_error=0'))
                diagnosis=re.findall(r'(?:ERROR|SUMMARY): AddressSanitizer: [^\n]+',p.stderr)
                expected_failure=name=='original' and scope=='all'
                passed=(p.returncode!=0 and any('global-buffer-overflow' in d for d in diagnosis)) if expected_failure else (p.returncode==0 and not diagnosis)
                results.append({'variant':name,'scope':scope,'expected_failure':expected_failure,'passed':passed,'returncode':p.returncode,'stdout':p.stdout.strip(),'diagnostics':[line.replace(tmp,'HOST_TEST') for line in diagnosis]})
    print(json.dumps({'scope':'Real cache table and lookup compiled on host; no message sent to SMC.','source_sha256':hashlib.sha256(args.original.read_bytes()).hexdigest(),'candidate_sha256':hashlib.sha256(args.candidate.read_bytes()).hexdigest(),'results':results},indent=2))
    if not all(r['passed'] for r in results):raise SystemExit(1)


if __name__=='__main__':main()
