"""Tests for execute.py (run_solution, evaluate_solution) and ivr.py (compute_ivr, compute_ivr_by_type)."""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from intentspec.execute import evaluate_solution, run_solution
from intentspec.ivr import compute_ivr, compute_ivr_by_type
from intentspec.schema import ConstraintTest, IVRResult, SpecPair, SolutionResult


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_spec(
    task_id: str = "T001",
    spec_type: str = "algorithm",
    stated: list[str] | None = None,
    hidden: list[str] | None = None,
    constraints: list[ConstraintTest] | None = None,
) -> SpecPair:
    if constraints is None:
        constraints = [
            ConstraintTest(id="C1", description="Sorted", test_code="assert solution([2,1])==[1,2]"),
            ConstraintTest(id="C2", description="No mutation", test_code="inp=[2,1];solution(inp);assert inp==[2,1]"),
        ]
    return SpecPair(
        task_id=task_id,
        spec_type=spec_type,
        ambiguous_prompt="Sort a list.",
        gold_prompt="Sort ascending, preserve duplicates, no mutation.",
        constraints=constraints,
        stated_test_ids=stated or ["C1"],
        hidden_test_ids=hidden or ["C2"],
    )


_GOOD_SOLUTION = "def solution(lst): return sorted(lst)"
_MUTATING_SOLUTION = "def solution(lst): lst.sort(); return lst"
_BROKEN_SOLUTION = "def solution(lst): return lst"  # identity, not sorted


# ---------------------------------------------------------------------------
# run_solution
# ---------------------------------------------------------------------------

def test_run_solution_passing():
    assert run_solution(
        "def solution(x): return x + 1",
        "assert solution(1) == 2",
    ) is True


def test_run_solution_failing_assertion():
    assert run_solution(
        "def solution(x): return x",
        "assert solution(1) == 2",
    ) is False


def test_run_solution_syntax_error():
    assert run_solution("def solution(: pass", "solution()") is False


def test_run_solution_runtime_exception():
    assert run_solution(
        "def solution(): raise ValueError('boom')",
        "solution()",
    ) is False


def test_run_solution_empty_list_constraint():
    assert run_solution(
        _GOOD_SOLUTION,
        "assert solution([]) == []",
    ) is True


# ---------------------------------------------------------------------------
# evaluate_solution
# ---------------------------------------------------------------------------

def test_evaluate_solution_good_solution_passes_stated():
    spec = _make_spec()
    result = evaluate_solution(_GOOD_SOLUTION, spec)
    assert isinstance(result, SolutionResult)
    assert result.passes_stated_tests is True


def test_evaluate_solution_good_solution_passes_hidden():
    # sorted() does not mutate, so C2 should pass
    spec = _make_spec()
    result = evaluate_solution(_GOOD_SOLUTION, spec)
    assert "C2" in result.passed_hidden_ids
    assert result.failed_hidden_ids == []


def test_evaluate_solution_mutating_solution_fails_hidden():
    # list.sort() mutates input — C2 should fail
    spec = _make_spec()
    result = evaluate_solution(_MUTATING_SOLUTION, spec)
    assert result.passes_stated_tests is True  # still produces sorted output
    assert "C2" in result.failed_hidden_ids


def test_evaluate_solution_broken_solution_fails_stated():
    # reverse is not sorted ascending — C1 fails
    spec = _make_spec()
    result = evaluate_solution(_BROKEN_SOLUTION, spec)
    assert result.passes_stated_tests is False


def test_evaluate_solution_task_id_propagated():
    spec = _make_spec(task_id="MY_TASK")
    result = evaluate_solution(_GOOD_SOLUTION, spec)
    assert result.task_id == "MY_TASK"


# ---------------------------------------------------------------------------
# compute_ivr
# ---------------------------------------------------------------------------

def test_compute_ivr_empty_list():
    ivr = compute_ivr([])
    assert ivr.ivr_score == 0.0
    assert ivr.n_solutions == 0
    assert ivr.n_passing_stated == 0


def test_compute_ivr_no_solutions_pass_stated():
    results = [
        SolutionResult(task_id="T", solution_code="", passes_stated_tests=False,
                       passed_hidden_ids=[], failed_hidden_ids=["C2"]),
    ]
    ivr = compute_ivr(results)
    assert ivr.ivr_score == 0.0
    assert ivr.n_passing_stated == 0


def test_compute_ivr_all_violate():
    results = [
        SolutionResult(task_id="T", solution_code="", passes_stated_tests=True,
                       passed_hidden_ids=[], failed_hidden_ids=["C2"]),
        SolutionResult(task_id="T", solution_code="", passes_stated_tests=True,
                       passed_hidden_ids=[], failed_hidden_ids=["C2"]),
    ]
    ivr = compute_ivr(results)
    assert abs(ivr.ivr_score - 1.0) < 1e-9
    assert ivr.n_violating == 2


def test_compute_ivr_none_violate():
    results = [
        SolutionResult(task_id="T", solution_code="", passes_stated_tests=True,
                       passed_hidden_ids=["C2"], failed_hidden_ids=[]),
        SolutionResult(task_id="T", solution_code="", passes_stated_tests=True,
                       passed_hidden_ids=["C2"], failed_hidden_ids=[]),
    ]
    ivr = compute_ivr(results)
    assert ivr.ivr_score == 0.0
    assert ivr.n_violating == 0


def test_compute_ivr_partial():
    results = [
        SolutionResult(task_id="T", solution_code="", passes_stated_tests=True,
                       passed_hidden_ids=[], failed_hidden_ids=["C2"]),  # violates
        SolutionResult(task_id="T", solution_code="", passes_stated_tests=True,
                       passed_hidden_ids=["C2"], failed_hidden_ids=[]),  # ok
        SolutionResult(task_id="T", solution_code="", passes_stated_tests=False,
                       passed_hidden_ids=[], failed_hidden_ids=[]),      # excluded
    ]
    ivr = compute_ivr(results)
    # 1 violating / 2 passing_stated = 0.5
    assert abs(ivr.ivr_score - 0.5) < 1e-9
    assert ivr.n_passing_stated == 2
    assert ivr.n_violating == 1


def test_compute_ivr_violation_breakdown():
    results = [
        SolutionResult(task_id="T", solution_code="", passes_stated_tests=True,
                       passed_hidden_ids=[], failed_hidden_ids=["C2", "C3"]),
        SolutionResult(task_id="T", solution_code="", passes_stated_tests=True,
                       passed_hidden_ids=["C3"], failed_hidden_ids=["C2"]),
    ]
    ivr = compute_ivr(results)
    assert ivr.violation_breakdown["C2"] == 2
    assert ivr.violation_breakdown.get("C3", 0) == 1


# ---------------------------------------------------------------------------
# compute_ivr_by_type
# ---------------------------------------------------------------------------

def test_compute_ivr_by_type_single_type():
    specs = [_make_spec("T1", "algorithm"), _make_spec("T2", "algorithm")]
    all_results = {
        "T1": [SolutionResult(task_id="T1", solution_code="", passes_stated_tests=True,
                              passed_hidden_ids=[], failed_hidden_ids=["C2"])],
        "T2": [SolutionResult(task_id="T2", solution_code="", passes_stated_tests=True,
                              passed_hidden_ids=["C2"], failed_hidden_ids=[])],
    }
    by_type = compute_ivr_by_type(specs, all_results)
    assert "algorithm" in by_type
    assert abs(by_type["algorithm"] - 0.5) < 1e-9


def test_compute_ivr_by_type_two_types():
    spec_alg = _make_spec("T1", "algorithm")
    spec_dt = _make_spec("T2", "data_transformation")
    all_results = {
        "T1": [SolutionResult(task_id="T1", solution_code="", passes_stated_tests=True,
                              passed_hidden_ids=[], failed_hidden_ids=["C2"])],
        "T2": [SolutionResult(task_id="T2", solution_code="", passes_stated_tests=True,
                              passed_hidden_ids=["C2"], failed_hidden_ids=[])],
    }
    by_type = compute_ivr_by_type([spec_alg, spec_dt], all_results)
    assert "algorithm" in by_type
    assert "data_transformation" in by_type
    assert abs(by_type["algorithm"] - 1.0) < 1e-9
    assert abs(by_type["data_transformation"] - 0.0) < 1e-9


def test_compute_ivr_by_type_excludes_no_passing_stated():
    spec = _make_spec("T1", "algorithm")
    all_results = {
        "T1": [SolutionResult(task_id="T1", solution_code="", passes_stated_tests=False,
                              passed_hidden_ids=[], failed_hidden_ids=[])],
    }
    by_type = compute_ivr_by_type([spec], all_results)
    # T1 has no passing-stated solutions; should be excluded → type absent or 0 entries
    assert by_type.get("algorithm") is None or len(by_type) == 0
