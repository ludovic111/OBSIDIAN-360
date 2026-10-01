#!/usr/bin/env python3
"""Compile a prepared candidate, preserving each attempt's log and exit status.

No installation, console connection, source download or kernel boot is done here.
"""
import argparse
import datetime
import json
from pathlib import Path
import subprocess
import sys


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source',type=Path,required=True)
    parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--jobs',type=int,default=2,choices=range(1,5))
    parser.add_argument('--target',default='vmlinux',choices=['vmlinux','modules','zImage.xenon'])
    parser.add_argument('--localversion',default='-obsidian1')
    args=parser.parse_args()
    source=args.source.resolve();output=args.output.resolve()
    if not (source/'Makefile').is_file() or not (output/'.config').is_file():
        parser.error('Prepared source Makefile and output/.config are required')
    name='obsidian360-kernel-build'
    current=subprocess.run(['docker','inspect','--format','{{.State.Status}}',name],capture_output=True,text=True)
    if current.returncode==0:
        print('Existing build container state: '+current.stdout.strip()+'. Inspect it before another run.')
        return 2
    image=subprocess.run(['docker','image','inspect','obsidian360-kernel:llvm16','--format','{{.Id}}'],capture_output=True,text=True)
    if image.returncode:
        parser.error('Verified kernel toolchain image is absent')
    stamp=datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ')
    log=output.parent/('build-'+stamp+'.log');state=output.parent/'build-state.json'
    if not args.localversion.startswith('-') or not all(c.isalnum() or c in '-._' for c in args.localversion):
        parser.error('localversion must be a hyphen-prefixed release suffix')
    report={'target':args.target,'localversion':args.localversion,'started_utc':stamp,'status':'starting','container':name,'image_id':image.stdout.strip(),'log':log.name,'jobs':args.jobs}
    def save():
        pending=state.with_suffix('.pending');pending.write_text(json.dumps(report,indent=2)+'\n');pending.replace(state)
    save()
    command=['docker','run','--rm','--name',name,'--network','none','--mount',f'type=bind,source={source},target=/src,readonly','--mount',f'type=bind,source={output},target=/build',report['image_id'],'make','-C','/src','O=/build','ARCH=powerpc','LLVM=1','LOCALVERSION='+args.localversion,'-j'+str(args.jobs),args.target]
    with log.open('w') as stream:
        child=subprocess.Popen(command,stdout=stream,stderr=subprocess.STDOUT)
        report.update(status='running',host_pid=child.pid);save()
        code=child.wait()
    report.update(status='succeeded' if code==0 else 'failed',returncode=code,finished_utc=datetime.datetime.now(datetime.timezone.utc).isoformat());save()
    print(json.dumps(report))
    return code


if __name__=='__main__':sys.exit(main())
