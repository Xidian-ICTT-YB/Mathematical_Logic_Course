"""Download fixed candidates into a NEW v2 input tree; preserve original inputs."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
from urllib.parse import quote

ROOT = Path(__file__).resolve().parents[1]
COMMIT = 'dbb9372541d3c068d970a2b76a92d8fa8f9a9d48'


def digest(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--download', action='store_true')
    args = parser.parse_args()
    design = ROOT / 'experiment-v2/design-20261111'
    rows = json.loads((design / 'tasks50-candidates.json').read_text())
    schedule = json.loads((design / 'case-repeat-schedule.json').read_text())
    assert len(rows) == 50 and len({r['path'] for r in rows}) == 50
    assert len(schedule) == 48
    assert len({(r['task'], r['algorithm'], r['repeat']) for r in schedule}) == 48
    files = set()
    for row in rows:
        path = Path(row['path'])
        assert not path.is_absolute() and '..' not in path.parts
        files.update([path.as_posix(), (path.parent / 'ALL.prp').as_posix()])
    print('Plan verified: 50 tasks; 48 repeated-case runs;', len(files), 'input files.', flush=True)
    if not args.download:
        print('Check only. Add --download to fetch pinned-commit inputs.')
        return
    base = ROOT / 'experiment-v2/inputs/c'
    for i, name in enumerate(sorted(files), 1):
        dest = base / name
        if not dest.exists():
            dest.parent.mkdir(parents=True, exist_ok=True)
            tmp = dest.with_name(dest.name + '.partial')
            url = 'https://raw.githubusercontent.com/sosy-lab/sv-benchmarks/' + COMMIT + '/c/' + quote(name, safe='/')
            subprocess.run(['curl', '--fail', '--location', '--silent', '--show-error',
                            '--retry', '2', '--connect-timeout', '15', '--max-time', '120', url, '-o', str(tmp)], check=True)
            tmp.replace(dest)
        print('INPUT', i, '/', len(files), name, flush=True)
    frozen = []
    for row in rows:
        source = base / row['path']
        prop = source.parent / 'ALL.prp'
        for key, p in [('sha256', source), ('property_sha256', prop)]:
            if row.get(key):
                assert digest(p) == row[key], 'Previously recorded hash differs: ' + str(p)
        assert '__VERIFIER_error' in prop.read_text(), prop
        frozen.append(dict(path=row['path'], expected=row['expected'], sha256=digest(source), property_sha256=digest(prop)))
    out = design / 'tasks50-frozen.json'
    content = json.dumps(frozen, indent=2) + '\n'
    if out.exists():
        assert out.read_text() == content, 'Frozen manifest changed; refusing overwrite'
    else:
        with out.open('x') as f:
            f.write(content)
    provenance = dict(commit=COMMIT, source='sosy-lab/sv-benchmarks', candidate_sha256=digest(design / 'tasks50-candidates.json'),
                      frozen_sha256=digest(out), files={n: digest(base / n) for n in sorted(files)})
    path = design / 'download-provenance.json'
    encoded = json.dumps(provenance, indent=2) + '\n'
    if path.exists():
        assert path.read_text() == encoded
    else:
        with path.open('x') as f:
            f.write(encoded)
    print('READY', out, flush=True)


if __name__ == '__main__':
    main()
