"""Tests for schema.py — core data structures for System B (IVR pipeline)."""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

import pytest
from intentspec.schema import ConstraintTest, IVRResult, SpecPair, SolutionResult


# --- ConstraintTest ---

def test_constraint_test_construction():
    ct = ConstraintTest(id="C1", description="Output sorted", test_code="assert solution([2,1]) == [1,2]")
    assert ct.id == "C1"
    assert ct.description == "Output sorted"
    assert "solution" in ct.test_code


def test_constraint_test_requires_all_fields():
    with pytest.raises(Exception):
        ConstraintTest(id="C1")  # missing description and test_code


# --- SpecPair ---

def test_spec_pair_construction():
    pair = SpecPair(
        task_id="HE_001",
        spec_type="algorithm",
        ambiguous_prompt="Sort a list.",
        gold_prompt="Sort a list ascending, preserve duplicates, do not mutate input.",
        constraints=[
            ConstraintTest(id="C1", description="Sorted", test_code="assert solution([2,1])==[1,2]"),
            ConstraintTest(id="C2", description="No mutation", test_code="inp=[2,1];solution(inp);assert inp==[2,1]"),
        ],
        stated_test_ids=["C1"],
        hidden_test_ids=["C2"],
    )
    assert pair.task_id == "HE_001"
    assert pair.spec_type == "algorithm"
    assert len(pair.constraints) == 2
    assert pair.stated_test_ids == ["C1"]
    assert pair.hidden_test_ids == ["C2"]


def test_spec_pair_invalid_spec_type():
    with pytest.raises(Exception):
        SpecPair(
            task_id="X",
            spec_type="unsupported_type",
            ambiguous_prompt="p",
            gold_prompt="g",
            constraints=[],
            stated_test_ids=[],
            hidden_test_ids=[],
        )


def test_spec_pair_data_transformation_type():
    pair = SpecPair(
        task_id="ARC_001",
        spec_type="data_transformation",
        ambiguous_prompt="Clean a list.",
        gold_prompt="Remove None and NaN.",
        constraints=[],
        stated_test_ids=[],
        hidden_test_ids=[],
    )
    assert pair.spec_type == "data_transformation"


# --- SolutionResult ---

def test_solution_result_construction():
    result = SolutionResult(
        task_id="HE_001",
        solution_code="def solution(lst): return sorted(lst)",
        passes_stated_tests=True,
        passed_hidden_ids=["C2"],
        failed_hidden_ids=["C3"],
    )
    assert result.passes_stated_tests is True
    assert "C2" in result.passed_hidden_ids
    assert "C3" in result.failed_hidden_ids


# --- IVRResult ---

def test_ivr_result_construction():
    ivr = IVRResult(
        task_id="HE_001",
        ivr_score=0.6,
        n_solutions=5,
        n_passing_stated=5,
        n_violating=3,
        violation_breakdown={"C2": 3, "C3": 1},
    )
    assert abs(ivr.ivr_score - 0.6) < 1e-9
    assert ivr.n_violating == 3
    assert ivr.violation_breakdown["C2"] == 3


def test_ivr_score_range():
    # ivr_score should be in [0, 1]
    ivr = IVRResult(
        task_id="X", ivr_score=1.0, n_solutions=3,
        n_passing_stated=3, n_violating=3, violation_breakdown={},
    )
    assert 0.0 <= ivr.ivr_score <= 1.0
