#!/usr/bin/env python3
"""Compile and exercise the original software PCM queue against sample sequences."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import tempfile


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    root=Path(__file__).resolve().parents[2]
    files=[root/'research/audio/pcm_queue.c',root/'research/audio/pcm_queue.h',root/'research/tests/audio-queue-main.c']
    report={'scope':'Original software queue; byte/sample oracle, modeled publication and physical-block completion. No ALSA adapter, hardware protocol, DMA, timing or concurrent execution.','sources':{f.relative_to(root).as_posix():hashlib.sha256(f.read_bytes()).hexdigest() for f in files}}
    with tempfile.TemporaryDirectory(prefix='obsidian-queue-') as tmp:
        binary=Path(tmp)/'test'
        cmd=['clang','-std=c11','-O1','-g','-Wall','-Wextra','-Werror','-fsanitize=address,undefined','-I',str(files[0].parent),str(files[0]),str(files[2]),'-o',str(binary)]
        r=subprocess.run(cmd,capture_output=True,text=True,timeout=30)
        scrub=lambda s:s.replace(str(root),'REPO').replace(tmp,'HOST_TEST')
        report['compile']={'code':r.returncode,'diagnostics':scrub(r.stderr)}
        if r.returncode==0:
            r=subprocess.run([str(binary)],capture_output=True,text=True,timeout=60,env=dict(os.environ,ASAN_OPTIONS='detect_leaks=0:halt_on_error=1',UBSAN_OPTIONS='halt_on_error=1'))
            report['run']={'code':r.returncode,'diagnostics':scrub(r.stderr),'stdout':r.stdout.strip()}
            if r.returncode==0:report['run']['result']=json.loads(r.stdout)
    report['passed']=report['compile']['code']==0 and report.get('run',{}).get('code')==0 and not report['run']['diagnostics']
    a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report));raise SystemExit(0 if report['passed'] else 1)


if __name__=='__main__':main()
