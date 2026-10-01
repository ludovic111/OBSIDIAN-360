#!/usr/bin/env python3
"""Exercise the actual IPI callback with simulated MMIO; no hardware access."""
import argparse
import difflib
import hashlib
import json
from pathlib import Path
import subprocess
import tempfile

HEADER = r'''
#include <stdint.h>
#include <stdio.h>
struct irq_data { unsigned long hwirq; };
struct cpumask { unsigned long bits[1]; };
static char registers[6*0x1000];
static void *iic_base=registers;
static uint64_t sent;
static int address_error;
static int hard_smp_processor_id(void) { return 2; }
static const unsigned long *cpumask_bits(const struct cpumask *p) { return p->bits; }
static void out_be64(void *p,uint64_t value) {
    if(p != registers+0x2010) address_error=1;
    sent=value;
}
'''
MAIN = r'''
int main(void) {
    const unsigned long priorities[]={8,16,112,120};
    int mismatches=0;
    for(unsigned long mask=0;mask<64;mask++) {
        struct cpumask dest={{mask}};
        for(int i=0;i<4;i++) {
            struct irq_data irq={priorities[i]};
            xenon_ipi_send_mask(&irq,&dest);
            uint64_t expected=(mask<<16)|priorities[i];
            if(sent!=expected) mismatches++;
        }
    }
    printf("%d %d\n",mismatches,address_error);
    return 0;
}
'''


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', type=Path, required=True)
    parser.add_argument('--patch', type=Path, required=True)
    args = parser.parse_args()
    original = args.source.read_text()
    bad = '(cpumask_bits(dest)[0] << 16) & 0x3F'
    good = '(cpumask_bits(dest)[0] & 0x3F) << 16'
    if original.count(bad) != 1:
        raise ValueError('Unexpected source: re-audit before applying a change')
    fixed = original.replace(bad, good)
    results = []
    with tempfile.TemporaryDirectory(prefix='obsidian-ipi-') as tmp:
        for name, source, expected_errors in [('original', original, 252), ('candidate', fixed, 0)]:
            function = source[source.index('static void xenon_ipi_send_mask('):source.index('static struct irq_chip xenon_pic')]
            path = Path(tmp) / (name+'.c');binary=Path(tmp)/name
            path.write_text(HEADER+function+MAIN)
            subprocess.run(['clang','-O2','-std=gnu11',str(path),'-o',str(binary)],check=True,capture_output=True,timeout=30)
            result=subprocess.run([str(binary)],check=True,capture_output=True,text=True,timeout=10)
            mismatches,address_error=map(int,result.stdout.split())
            results.append({'variant':name,'cases':256,'target_mismatches':mismatches,'address_error':address_error,'passed':mismatches==expected_errors and address_error==0})
    args.patch.parent.mkdir(parents=True,exist_ok=True)
    args.patch.write_text(''.join(difflib.unified_diff(original.splitlines(True),fixed.splitlines(True),fromfile='a/arch/powerpc/platforms/xenon/interrupt.c',tofile='b/arch/powerpc/platforms/xenon/interrupt.c')))
    print(json.dumps({'scope':'Real callback on host; MMIO simulated. Expected target encoding follows xenon_cause_IPI, not a new hardware measurement.','source_sha256':hashlib.sha256(original.encode()).hexdigest(),'results':results},indent=2))
    if not all(result['passed'] for result in results):
        raise SystemExit(1)


if __name__ == '__main__':
    main()
