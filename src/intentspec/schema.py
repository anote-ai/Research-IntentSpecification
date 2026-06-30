from __future__ import annotations

from typing import Literal

from pydantic import BaseModel


class ConstraintTest(BaseModel):
    """A single executable constraint derived from a gold-clarified specification."""

    id: str
    description: str
    test_code: str  # Python code that calls solution(...) and asserts correctness


class SpecPair(BaseModel):
    """An ambiguous/gold spec pair with decomposed constraint tests.

    stated_test_ids: constraints mentioned (even implicitly) in the ambiguous prompt.
    hidden_test_ids: constraints present only in the gold prompt — these are what IVR measures.
    """

    task_id: str
    spec_type: Literal["algorithm", "data_transformation"]
    ambiguous_prompt: str
    gold_prompt: str
    constraints: list[ConstraintTest]
    stated_test_ids: list[str]
    hidden_test_ids: list[str]


class SolutionResult(BaseModel):
    """Execution results for one LLM-generated solution against a SpecPair."""

    task_id: str
    solution_code: str
    passes_stated_tests: bool
    passed_hidden_ids: list[str]
    failed_hidden_ids: list[str]


class IVRResult(BaseModel):
    """Aggregated Intent Violation Rate for one spec pair across N solutions.

    IVR = n_violating / n_passing_stated
    where n_violating = solutions that pass stated tests but fail >= 1 hidden constraint.
    """

    task_id: str
    ivr_score: float
    n_solutions: int
    n_passing_stated: int
    n_violating: int
    violation_breakdown: dict[str, int]  # hidden_test_id -> count of solutions failing it
