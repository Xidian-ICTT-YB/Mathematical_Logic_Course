"""Linux serial runner. Default is read-only preflight; --run explicitly starts work."""
import argparse
import contextlib
import fcntl
import hashlib
import json
import os
from pathlib import Path
import re
import resource
import signal
import subprocess
import time
import uuid
import xml.etree.ElementTree as ET
from v2_evidence import parse_log

ALGORITHMS = ['bmc', 'k-induction', 'predicateAnalysis', 'impact']


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def save(path, data):
    temp = path.with_name(path.name + '.tmp')
    temp.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n')
    temp.replace(path)


def inside(root, path):
    path = path.resolve()
    if path == root or root not in path.parents:
        raise ValueError('Path must be strictly inside project: ' + str(path))
    return path


@contextlib.contextmanager
def locked(path):
    with path.open('a') as f:
        fcntl.flock(f, fcntl.LOCK_EX | fcntl.LOCK_NB)
        yield


def usage(pgid):
    cpu = rss = 0
    for path in Path('/proc').glob('[0-9]*/stat'):
        try:
            fields = path.read_text().rsplit(')', 1)[1].split()
            if int(fields[2]) == pgid:
                cpu += sum(int(fields[i]) for i in (11, 12, 13, 14)) / os.sysconf('SC_CLK_TCK')
                rss += int(fields[21]) * os.sysconf('SC_PAGE_SIZE')
        except (OSError, ValueError, IndexError):
            pass
    return cpu, rss


def stop_group(p, grace=2):
    # Only this process's newly created session/group is targeted.
    try:
        os.killpg(p.pid, signal.SIGTERM)
    except ProcessLookupError:
        p.wait()
        return
    until = time.monotonic() + grace
    while time.monotonic() < until:
        p.poll()
        try:
            os.killpg(p.pid, 0)
        except ProcessLookupError:
            p.wait()
            return
        time.sleep(.05)
    try:
        os.killpg(p.pid, signal.SIGKILL)
    except ProcessLookupError:
        pass
    p.wait()


def execute(cmd, cwd, env, attempt, limits, cpus, sampler=usage):
    def setup():
        os.nice(10)
        if cpus:
            os.sched_setaffinity(0, cpus)
        resource.setrlimit(resource.RLIMIT_CPU, (limits['cpu_hard'], limits['cpu_hard']))
    save(attempt / 'command.json', cmd)
    start = time.monotonic()
    reason = ''
    peak_cpu = peak_rss = 0
    with (attempt / 'run.log').open('w') as log:
        p = subprocess.Popen(cmd, cwd=cwd, env=env, stdout=log, stderr=subprocess.STDOUT,
                             start_new_session=True, preexec_fn=setup)
        try:
            while p.poll() is None:
                cpu, rss = sampler(p.pid)
                peak_cpu, peak_rss = max(cpu, peak_cpu), max(rss, peak_rss)
                if rss > limits['memory_bytes']:
                    reason = 'MEMORY_LIMIT'
                elif cpu > limits['cpu_hard']:
                    reason = 'CPU_HARD_LIMIT'
                elif time.monotonic() - start > limits['wall_seconds']:
                    reason = 'WALL_SAFETY_LIMIT'
                if reason:
                    break
                time.sleep(.2)
        except BaseException:
            # Result is not marked complete; resume creates a new attempt.
            save(attempt / 'interrupted.json', dict(pid=p.pid, elapsed=time.monotonic() - start))
            raise
        finally:
            stop_group(p)
    text = (attempt / 'run.log').read_text(errors='replace')
    result = parse_log(text, p.returncode, reason)
    cpu_matches = re.findall(r'^Total CPU time for CPAchecker:\s+([0-9.]+)s', text, re.M)
    result.update(wall_seconds=time.monotonic() - start, peak_group_rss=peak_rss,
                  sampled_group_cpu_peak_seconds=peak_cpu,
                  cpa_cpu_seconds=float(cpu_matches[0]) if len(cpu_matches) == 1 else None,
                  log=str(attempt / 'run.log'))
    return result


def resume_check(out, identity):
    if json.loads((out / 'metadata.json').read_text())['identity'] != identity:
        raise ValueError('Inputs, tools, runner or limits changed; refusing mixed results')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, required=True)
    parser.add_argument('--manifest', default='experiment-v2/design-20261111/tasks50-frozen.json')
    parser.add_argument('--schedule', default='experiment-v2/design-20261111/case-repeat-schedule.json')
    parser.add_argument('--inputs', default='experiment-v2/inputs/c')
    parser.add_argument('--cpu-soft', type=int, default=900)
    parser.add_argument('--cpu-hard', type=int, default=1000)
    parser.add_argument('--memory-bytes', type=int, default=15000000000)
    parser.add_argument('--wall-seconds', type=int, default=2000)
    parser.add_argument('--heap', default='10000M')
    parser.add_argument('--cpus', help='Two allowed logical CPU ids, e.g. 0,1')
    parser.add_argument('--run', action='store_true')
    parser.add_argument('--resume', help='Existing v2-* directory name')
    args = parser.parse_args()
    root = args.root.resolve()
    manifest = inside(root, root / args.manifest)
    schedule_file = inside(root, root / args.schedule)
    inputs = inside(root, root / args.inputs)
    cpa = inside(root, root / 'tools/supplements-vstte/CPAchecker')
    java = inside(root, root / 'tools/java8/bin/java')
    if not (0 < args.cpu_soft < args.cpu_hard and args.memory_bytes > 0 and args.wall_seconds > 0):
        parser.error('Invalid resource limits')
    if not re.fullmatch(r'[1-9][0-9]*[MG]', args.heap):
        parser.error('Heap must be a positive M/G value')
    if args.resume and not args.run:
        parser.error('--resume requires --run')
    tasks_list = json.loads(manifest.read_text())
    tasks = {t['path']: t for t in tasks_list}
    if len(tasks) != len(tasks_list):
        raise ValueError('Duplicate tasks')
    for name, t in tasks.items():
        source = inside(inputs, inputs / name)
        prop = inside(inputs, source.parent / 'ALL.prp')
        if sha(source) != t['sha256'] or sha(prop) != t['property_sha256']:
            raise ValueError('Input checksum differs: ' + name)
    schedule = json.loads(schedule_file.read_text())
    keys = [(r['task'], r['algorithm'], r['repeat']) for r in schedule]
    if not keys or len(set(keys)) != len(keys):
        raise ValueError('Empty or duplicate schedule')
    for task, a, repeat in keys:
        if task not in tasks or a not in ALGORITHMS or not isinstance(repeat, int) or repeat < 1:
            raise ValueError('Invalid schedule entry')
    configs = {}
    for a in ALGORITHMS:
        path = cpa / ('test/test-sets/' + a + '-bitprecise.xml')
        options = []
        for e in ET.parse(path).getroot().find('rundefinition').findall('option'):
            options.append(e.get('name'))
            if e.text:
                options.append(e.text.strip())
        configs[a] = options
    allowed = sorted(os.sched_getaffinity(0))
    cpus = [int(c) for c in args.cpus.split(',')] if args.cpus else allowed[:2]
    if len(set(cpus)) != 2 or not set(cpus) <= set(allowed):
        parser.error('Select exactly two allowed logical CPUs')
    limits = dict(cpu_soft=args.cpu_soft, cpu_hard=args.cpu_hard, memory_bytes=args.memory_bytes,
                  wall_seconds=args.wall_seconds, heap=args.heap)
    # Hash actual configs/libraries as well as script; stable no-output tool trees.
    tool_hashes = {}
    for directory in ['config', 'lib', 'scripts']:
        for path in sorted((cpa / directory).rglob('*')):
            if path.is_file():
                tool_hashes[str(path.relative_to(cpa))] = sha(path)
    java_version = subprocess.check_output([str(java), '-version'], stderr=subprocess.STDOUT).decode()
    identity = dict(manifest_sha256=sha(manifest), schedule_sha256=sha(schedule_file),
                    limits=limits, cpus=cpus, configs=configs, tool_hashes=tool_hashes,
                    java_version=java_version, runner_sha256=sha(Path(__file__)),
                    parser_sha256=sha(Path(__file__).with_name('v2_evidence.py')),
                    inputs=str(inputs), root=str(root))
    print('CHECK OK:', len(tasks), 'hashed tasks;', len(schedule), 'scheduled runs; cpus', cpus, flush=True)
    if not args.run:
        print('Read-only preflight. No verification started.')
        return
    results = inside(root, root / 'results')
    results.mkdir(exist_ok=True)
    with locked(results / 'batch.lock'):
        if args.resume:
            if not re.fullmatch(r'v2-[A-Za-z0-9_-]+', args.resume):
                raise ValueError('Invalid resume directory name')
            out = inside(results, results / args.resume)
            resume_check(out, identity)
        else:
            out = results / ('v2-' + time.strftime('%Y%m%d-%H%M%S') + '-' + uuid.uuid4().hex[:6])
            out.mkdir()
            save(out / 'metadata.json', dict(identity=identity, host=os.uname().nodename,
                platform=list(os.uname()), limits_note='Polling summed RSS and process-group CPU, not cgroups. Shared pages may be double-counted; CPU samples may miss exits. RLIMIT_CPU is per process, not a group limit. CPUs nonexclusive. Swap unchanged.',
                proc_meminfo=Path('/proc/meminfo').read_text(), proc_swaps=Path('/proc/swaps').read_text()))
            save(out / 'schedule.json', schedule)
        print('OUTPUT', out, flush=True)
        rows = []
        for index, entry in enumerate(schedule, 1):
            run = inside(out, out / ('%03d' % index))
            run.mkdir(exist_ok=True)
            result_file = run / 'result.json'
            if result_file.exists():
                result = json.loads(result_file.read_text())
                if result['entry'] != entry:
                    raise ValueError('Stored result does not match schedule')
                rows.append(result)
                continue
            attempt = run / ('attempt-' + uuid.uuid4().hex)
            attempt.mkdir()
            (attempt / 'tmp').mkdir()
            source = inputs / entry['task']
            cmd = ['scripts/cpa.sh', '-heap', args.heap, '-noout', '-64', *configs[entry['algorithm']],
                   '-timelimit', str(args.cpu_soft) + 's', '-stats', '-outputpath', str(attempt / 'output'),
                   '-spec', str(source.parent / 'ALL.prp'), str(source)]
            env = dict(os.environ, JAVA=str(java), TMPDIR=str(attempt / 'tmp'),
                       JAVA_TOOL_OPTIONS='-XX:-UsePerfData -Djava.io.tmpdir=' + str(attempt / 'tmp'))
            print('START', index, '/', len(schedule), entry, flush=True)
            result = execute(cmd, cpa, env, attempt, limits, cpus)
            result['entry'] = entry
            result['expected'] = tasks[entry['task']]['expected']
            result['wrong_result'] = result['status'] in ('SAFE', 'UNSAFE') and result['status'] != result['expected']
            save(result_file, result)
            rows.append(result)
            save(out / 'results.json', rows)
            print('DONE', index, '/', len(schedule), result['status'], flush=True)
        save(out / 'results.json', rows)
        (out / 'COMPLETE').touch()
        print('COMPLETE', out, flush=True)


if __name__ == '__main__':
    def interrupt(signum, frame):
        raise KeyboardInterrupt
    signal.signal(signal.SIGTERM, interrupt)
    main()
