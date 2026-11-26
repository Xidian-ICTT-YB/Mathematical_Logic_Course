"""Preserve independent verdict, termination and diagnostic evidence."""
import re


def parse_log(text, exit_code=0, stop_reason=''):
    verdicts = re.findall(r'^Verification result: (TRUE|FALSE|UNKNOWN)', text, re.M)
    diagnostics = []
    for line_no, line in enumerate(text.splitlines(), 1):
        if re.search(r'Unsupported feature \(recursion\)|Recursion detected|^Error:|Exception in thread|OutOfMemoryError|OUT OF NATIVE MEMORY', line):
            diagnostics.append(dict(line=line_no, text=line))
    internal_timeout = bool(re.search(r'CPU[- ]time limit.*(?:elapsed|exceeded)', text, re.I))
    raw = verdicts[-1] if verdicts else None
    if stop_reason:
        status = {'MEMORY_LIMIT': 'MEMORY_LIMIT', 'CPU_HARD_LIMIT': 'TIMEOUT', 'WALL_SAFETY_LIMIT': 'TIMEOUT'}.get(stop_reason, 'INTERRUPTED')
    elif internal_timeout:
        status = 'TIMEOUT'
    elif re.search(r'OUT OF NATIVE MEMORY|Native memory allocation.*failed|unable to allocate native memory', text, re.I):
        status = 'NATIVE_MEMORY_ERROR'
    elif 'OutOfMemoryError' in text:
        status = 'JAVA_MEMORY_ERROR'
    elif exit_code != 0:
        status = 'ERROR'
    elif raw in ('TRUE', 'FALSE'):
        status = {'TRUE': 'SAFE', 'FALSE': 'UNSAFE'}[raw]
    elif diagnostics:
        status = 'ERROR'
    else:
        status = 'UNKNOWN' if raw == 'UNKNOWN' else 'ERROR'
    # Preserve all matching statistic lines, including parallel subanalyses.
    metrics = []
    pattern = r'Number of abstractions:|Number of predicates discovered:|Number of successful refinements:|Attempted forced coverings:|Successful forced coverings:|Time for abstraction:|Total CPU time|Successful analysis:'
    for line_no, line in enumerate(text.splitlines(), 1):
        if re.search(pattern, line):
            metrics.append(dict(line=line_no, text=line))
    return dict(status=status, raw_verdict=raw, all_verdicts=verdicts,
                exit_code=exit_code, runner_stop_reason=stop_reason,
                internal_cpu_timeout=internal_timeout, diagnostics=diagnostics, metric_evidence=metrics)
