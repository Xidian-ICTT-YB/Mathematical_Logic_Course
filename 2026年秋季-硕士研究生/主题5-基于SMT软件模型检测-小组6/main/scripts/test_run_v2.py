import json
import os
from pathlib import Path
import signal
import sys
import tempfile
import threading
import unittest
from run_v2 import execute, inside, locked, resume_check, save


class RunnerTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name).resolve()
        self.limits = dict(cpu_hard=20, memory_bytes=10000000, wall_seconds=2)

    def tearDown(self):
        self.tmp.cleanup()

    def run_program(self, code, sampler=lambda group: (0, 0)):
        return execute([sys.executable, '-c', code], self.root, dict(os.environ), self.root,
                       self.limits, [], sampler)

    def test_success(self):
        r = self.run_program('print("Verification result: TRUE")')
        self.assertEqual(r['status'], 'SAFE')

    def test_wall(self):
        self.limits['wall_seconds'] = .1
        r = self.run_program('import time; time.sleep(10)')
        self.assertEqual(r['runner_stop_reason'], 'WALL_SAFETY_LIMIT')

    def test_memory(self):
        r = self.run_program('import time; time.sleep(10)', lambda group: (0, 10000001))
        self.assertEqual(r['runner_stop_reason'], 'MEMORY_LIMIT')

    def test_cpu(self):
        r = self.run_program('import time; time.sleep(10)', lambda group: (21, 0))
        self.assertEqual(r['runner_stop_reason'], 'CPU_HARD_LIMIT')

    def test_boundary(self):
        with self.assertRaises(ValueError):
            inside(self.root, self.root / '../outside')
        with self.assertRaises(ValueError):
            inside(self.root, self.root)

    def test_lock(self):
        with locked(self.root / 'lock'):
            with self.assertRaises(BlockingIOError):
                with locked(self.root / 'lock'):
                    pass

    def test_resume_identity(self):
        save(self.root / 'metadata.json', {'identity': {'version': 1}})
        resume_check(self.root, {'version': 1})
        with self.assertRaises(ValueError):
            resume_check(self.root, {'version': 2})

    def test_sigterm_cleanup(self):
        self.check_signal(signal.SIGTERM)

    def test_sigint_cleanup(self):
        self.check_signal(signal.SIGINT)

    def check_signal(self, sig):
        def interrupted(signum, frame):
            raise KeyboardInterrupt
        old = signal.signal(sig, interrupted)
        timer = threading.Timer(.3, lambda: os.kill(os.getpid(), sig))
        timer.start()
        try:
            with self.assertRaises(KeyboardInterrupt):
                self.run_program('import time; time.sleep(10)')
            pid = json.loads((self.root / 'interrupted.json').read_text())['pid']
            with self.assertRaises(ProcessLookupError):
                os.kill(pid, 0)
            self.assertFalse((self.root / 'result.json').exists())
        finally:
            timer.cancel()
            signal.signal(sig, old)

    @unittest.skipUnless(sys.platform.startswith('linux'), 'Linux /proc evidence')
    def test_descendant_cleanup(self):
        self.limits['wall_seconds'] = .5
        code = 'import subprocess,sys,time; p=subprocess.Popen([sys.executable,"-c","import signal,time; signal.signal(signal.SIGTERM, signal.SIG_IGN); time.sleep(20)"]); print(p.pid,flush=True); time.sleep(20)'
        result = self.run_program(code)
        pid = int((self.root / 'run.log').read_text().strip())
        path = Path('/proc') / str(pid) / 'stat'
        # A terminated child may briefly remain a zombie until adopted/reaped.
        if path.exists():
            self.assertEqual(path.read_text().rsplit(')', 1)[1].split()[0], 'Z')
        self.assertEqual(result['runner_stop_reason'], 'WALL_SAFETY_LIMIT')


if __name__ == '__main__':
    unittest.main()
