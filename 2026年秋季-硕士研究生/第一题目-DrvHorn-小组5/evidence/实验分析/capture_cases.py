import json
import subprocess
from pathlib import Path

base = Path(__file__).resolve().parent
image = 'joehattori/drvhorn@sha256:536168e391d7c08c8247276dafc4a518ac68a1a5fcea44068f5c03b5b345f80c'
cases = [
    ('tpm_bios_measurements_ops', '--file-operations=tpm_bios_measurements_ops'),
    ('ged_driver', '--platform-driver=ged_driver'),
    ('acpi_wmi_driver', '--platform-driver=acpi_wmi_driver'),
]
records = []
for name, option in cases:
    directory = base / 'ir' / name
    directory.mkdir(parents=True, exist_ok=True)
    linux_directory = '/mnt/d/数理逻辑/实验分析/ir/' + name
    args = [
        'wsl.exe', '-d', 'DrvHorn-Ubuntu22.04', '-u', 'drvhorn', '--exec',
        'docker', 'run', '--rm', '--network', 'none',
        '--mount', 'type=bind,source=' + linux_directory + ',target=/analysis',
        '--workdir', '/analysis', image, 'timeout', '--kill-after=10s', '500',
        '/drvhorn/build/run/bin/sea', 'kernel', '--save-temps',
        '--temp-dir=/analysis/tmp', '--out-dir=/analysis/outpp',
        '--out-ll=/analysis/instrumented.ll', '--show-invars',
        option, '/drvhorn/simple_kernel.bc',
    ]
    print('Capturing ' + name, flush=True)
    result = subprocess.run(args, capture_output=True, timeout=550)
    (directory / 'stdout.txt').write_bytes(result.stdout)
    (directory / 'stderr.bin').write_bytes(result.stderr)
    record = {'case': name, 'exit_code': result.returncode,
              'command': args, 'directory': str(directory)}
    records.append(record)
    (base / 'capture-results.json').write_text(json.dumps(records, ensure_ascii=False, indent=2), encoding='utf-8')
    print(name + ': exit=' + str(result.returncode), flush=True)
    if result.returncode:
        print(result.stdout.decode('utf-8', errors='replace')[-3000:], flush=True)
        print(result.stderr.decode('utf-8', errors='replace').replace('\x00', '')[-3000:], flush=True)
        raise SystemExit(result.returncode)
