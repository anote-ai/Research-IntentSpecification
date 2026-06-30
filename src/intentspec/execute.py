from __future__ import annotations

import subprocess
import sys
import textwrap

from .schema import SpecPair, SolutionResult


def run_solution(solution_code: str, test_code: str, timeout: float = 5.0) -> bool:
    """Execute solution_code followed by test_code in a subprocess.

    Returns True if the combined script exits with code 0, False on assertion
    failure, exception, syntax error, or timeout.
    """
    combined = textwrap.dedent(solution_code) + "\n\n" + textwrap.dedent(test_code) + "\n"
    try:
        result = subprocess.run(
            [sys.executable, "-c", combined],
            timeout=timeout,
            capture_output=True,
            text=True,
        )
        return result.returncode == 0
    except subprocess.TimeoutExpired:
        return False


def evaluate_solution(solution_code: str, spec_pair: SpecPair) -> SolutionResult:
    """Run solution_code against all stated and hidden constraint tests in spec_pair.

    A solution qualifies for IVR measurement only if it passes all stated tests.
    """
    constraint_map = {ct.id: ct for ct in spec_pair.constraints}

    passes_stated = all(
        run_solution(solution_code, constraint_map[tid].test_code)
        for tid in spec_pair.stated_test_ids
        if tid in constraint_map
    )

    passed_hidden: list[str] = []
    failed_hidden: list[str] = []
    for tid in spec_pair.hidden_test_ids:
        if tid not in constraint_map:
            continue
        if run_solution(solution_code, constraint_map[tid].test_code):
            passed_hidden.append(tid)
        else:
            failed_hidden.append(tid)

    return SolutionResult(
        task_id=spec_pair.task_id,
        solution_code=solution_code,
        passes_stated_tests=passes_stated,
        passed_hidden_ids=passed_hidden,
        failed_hidden_ids=failed_hidden,
    )
