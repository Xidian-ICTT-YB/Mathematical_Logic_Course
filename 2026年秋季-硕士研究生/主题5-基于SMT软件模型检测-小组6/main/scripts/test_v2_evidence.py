import unittest
from v2_evidence import parse_log


class EvidenceTests(unittest.TestCase):
    def test_final_verdicts(self):
        for v, expected in [('TRUE', 'SAFE'), ('FALSE', 'UNSAFE'), ('UNKNOWN', 'UNKNOWN')]:
            self.assertEqual(parse_log('Verification result: ' + v)['status'], expected)

    def test_resource_precedence(self):
        self.assertEqual(parse_log('Verification result: FALSE', stop_reason='MEMORY_LIMIT')['status'], 'MEMORY_LIMIT')
        self.assertEqual(parse_log('Verification result: UNKNOWN', stop_reason='WALL_SAFETY_LIMIT')['status'], 'TIMEOUT')
        self.assertEqual(parse_log('The CPU-time limit of 900s has elapsed.\nVerification result: UNKNOWN')['status'], 'TIMEOUT')

    def test_parallel_diagnostics(self):
        text = 'Unsupported feature (recursion)\nError: An unexpected exception occured\nVerification result: UNKNOWN'
        result = parse_log(text)
        self.assertEqual(result['status'], 'ERROR')
        self.assertEqual(len(result['diagnostics']), 2)
        self.assertEqual(result['raw_verdict'], 'UNKNOWN')

    def test_success_despite_auxiliary_failure(self):
        self.assertEqual(parse_log('Unsupported feature (recursion)\nVerification result: TRUE')['status'], 'SAFE')

    def test_memory_and_missing_verdict(self):
        self.assertEqual(parse_log('OutOfMemoryError')['status'], 'JAVA_MEMORY_ERROR')
        self.assertEqual(parse_log('')['status'], 'ERROR')
        self.assertEqual(parse_log('Verification result: TRUE', -9)['status'], 'ERROR')

    def test_all_statistics_preserved(self):
        result = parse_log('Number of abstractions: 1\nNumber of abstractions: 2')
        self.assertEqual(len(result['metric_evidence']), 2)

    def test_native_memory(self):
        self.assertEqual(parse_log('OUT OF NATIVE MEMORY')['status'], 'NATIVE_MEMORY_ERROR')


if __name__ == '__main__':
    unittest.main()
