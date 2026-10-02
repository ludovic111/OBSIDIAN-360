#!/usr/bin/env python3
"""Inject probe/cleanup failures into actual extracted audio resource functions.

Kernel ownership is simulated, callbacks run serially, and no console is used.
Original-driver failures are retained as diagnostics, not executed on hardware.
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
    match = re.search(r'^static [\w *]+\b' + name + r'\([^;]*?\n\{', source, re.M)
    if not match:
        raise ValueError(name)
    return source[match.start():source.index('\n}', match.end()) + 2]


def harness(source, base, candidate):
    structs = source[source.index('struct playback_device {'):source.index('static void cache_flush(')]
    prelude = 'static void snd_xenon_timer_fn(struct timer_list *t) { (void)t; }\n'
    if candidate:
        names = ['snd_xenon_new_pcm', 'snd_xenon_quiesce', 'snd_xenon_card_free', 'snd_xenon_init', 'snd_xenon_create', 'snd_xenon_probe', 'snd_xenon_remove']
    else:
        prelude += 'static int snd_xenon_interrupt(int irq, void *data) { (void)irq; (void)data; return 1; }\nstatic int snd_xenon_free(struct snd_xenon *);\nstatic int snd_xenon_dev_free(struct snd_device *);\n'
        names = ['snd_xenon_set_irq_flag', 'snd_xenon_new_pcm', 'snd_xenon_init', 'snd_xenon_create', 'snd_xenon_dev_free', 'snd_xenon_free', 'snd_xenon_probe', 'snd_xenon_remove']
    return (base/'audio-lifecycle-stubs.h').read_text() + structs + prelude + '\n'.join(function(source, n) for n in names) + (base/'audio-lifecycle-main.c').read_text()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--original', type=Path, required=True)
    parser.add_argument('--candidate', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    base = Path(__file__).resolve().parent
    original_cases = ['success', 'card', 'pci_enable', 'chip_alloc', 'bar_type', 'regions', 'irq', 'pcm0', 'pcm1', 'lowlevel', 'register', 'dma_handle', 'active_remove']
    candidate_cases = ['success', 'card', 'pci_enable', 'chip_alloc', 'bar_type', 'bar_short', 'dma_mask', 'regions', 'ioremap', 'dma_alloc', 'smc_ready', 'smc_send', 'smc_busy', 'smc_timeout', 'pcm0', 'pcm1', 'register', 'active_remove']
    report = {'scope': 'Actual C resource routines with modeled kernel APIs and serial fault injection; no DMA/cache/IRQ/SMC hardware or concurrent execution.', 'variants': []}
    with tempfile.TemporaryDirectory(prefix='obsidian-audio-lifecycle-') as tmp:
        for name, path in [('original', args.original), ('candidate', args.candidate)]:
            candidate = name == 'candidate'
            src = Path(tmp)/(name+'.c'); binary = Path(tmp)/name
            src.write_text(harness(path.read_text(), base, candidate))
            build = subprocess.run(['clang', '-std=gnu11', '-O1', '-g', '-Wall', '-Wextra', '-Werror', '-Wno-unused-function', '-Wno-unused-parameter', '-Wno-deprecated-declarations', '-fsanitize=address,undefined', str(src), '-o', str(binary)],capture_output=True,text=True,timeout=30)
            record = {'variant': name, 'source_sha256': hashlib.sha256(path.read_bytes()).hexdigest(), 'compile_code': build.returncode, 'compile_diagnostics': build.stderr.replace(tmp, 'HOST_TEST'), 'cases': []}
            report['variants'].append(record)
            if build.returncode:
                continue
            for case in candidate_cases if candidate else original_cases:
                run = subprocess.run([str(binary), case, str(int(candidate))], capture_output=True,text=True,timeout=10,env=dict(os.environ,ASAN_OPTIONS='detect_leaks=0:halt_on_error=1:abort_on_error=0',UBSAN_OPTIONS='halt_on_error=1:print_stacktrace=0'))
                expected_failure = not candidate and case != 'success'
                diagnostics = run.stderr.replace(tmp, 'HOST_TEST')
                expected_diagnostics = {
                    'card': 'MODEL_ASSERT:code==want',
                    'pci_enable': 'member access within null pointer',
                    'chip_alloc': 'member access within null pointer',
                    'bar_type': 'member access within null pointer',
                    'regions': 'member access within null pointer',
                    'irq': 'MODEL_ASSERT:t->initialized',
                    'pcm0': 'MODEL_ASSERT:t->initialized',
                    'pcm1': 'MODEL_ASSERT:t->initialized',
                    'lowlevel': 'MODEL_ASSERT:t->initialized',
                    'register': 'ERROR: AddressSanitizer: heap-use-after-free',
                    'dma_handle': 'MODEL_ASSERT:handle==allocated_handle',
                    'active_remove': 'MODEL_ASSERT:!active_dma',
                }
                recognized = expected_diagnostics.get(case, 'NO_EXPECTED_FAILURE') in diagnostics
                passed = (run.returncode != 0 and recognized) if expected_failure else (run.returncode == 0 and not diagnostics)
                record['cases'].append({'name': case, 'expected_failure': expected_failure, 'returncode': run.returncode, 'passed': passed, 'stdout': run.stdout.strip(), 'diagnostics': diagnostics})
    report['passed'] = all(v['compile_code']==0 and v['cases'] and all(c['passed'] for c in v['cases']) for v in report['variants'])
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({'passed':report['passed'],'variants':[{'name':v['variant'],'compile_code':v['compile_code'],'cases':len(v['cases']),'failures':[c['name'] for c in v['cases'] if not c['passed']]} for v in report['variants']]}))
    raise SystemExit(0 if report['passed'] else 1)


if __name__ == '__main__':
    main()
