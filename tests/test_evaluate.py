import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from intentspec.core import IntentSpec, ToolCall, EvalRecord, ConstraintTracker
from intentspec.evaluate import (
    score_intent_alignment,
    score_syntactic,
    constraint_satisfaction_rate,
    ambiguity_resolution_score,
    compare_scores,
    divergence_analysis,
)


def test_score_intent_alignment_with_matching_constraints():
    spec = IntentSpec(goal="test", constraints=["use authorized sources", "return json"])
    call = ToolCall(
        tool_name="query",
        rationale="I will use authorized sources and return json output",
    )
    score = score_intent_alignment(spec, call)
    assert score > 0.0


def test_score_syntactic_perfect_match():
    pred = ToolCall(tool_name="tool_a", arguments={"x": 1, "y": 2})
    ref = ToolCall(tool_name="tool_a", arguments={"x": 1, "y": 2})
    assert score_syntactic(pred, ref) == 1.0


def test_score_syntactic_wrong_name():
    pred = ToolCall(tool_name="wrong_tool", arguments={"x": 1})
    ref = ToolCall(tool_name="right_tool", arguments={"x": 1})
    assert score_syntactic(pred, ref) < 0.6


def test_compare_scores_structure():
    result = compare_scores([0.8, 0.6, 0.9], [0.7, 0.8, 0.85])
    assert "pearson_r" in result
    assert "mean_divergence" in result
    assert "cases_where_syntactic_overstates" in result


def test_divergence_analysis_has_correct_keys():
    spec = IntentSpec(goal="test")
    call = ToolCall(tool_name="tool")
    records = [
        EvalRecord(
            intent_spec=spec,
            predicted_call=call,
            reference_call=call,
            intent_score=0.8,
            syntactic_score=0.6,
        ),
        EvalRecord(
            intent_spec=spec,
            predicted_call=call,
            reference_call=call,
            intent_score=0.5,
            syntactic_score=0.9,
        ),
    ]
    result = divergence_analysis(records)
    for key in [
        "mean_intent",
        "mean_syntactic",
        "mean_divergence",
        "max_divergence",
        "overstatement_rate",
        "mean_constraint_sat_rate",
        "mean_ambiguity_res_score",
    ]:
        assert key in result


def test_pearson_r_identical_arrays():
    scores = [0.1, 0.5, 0.9, 0.3, 0.7]
    result = compare_scores(scores, scores)
    assert abs(result["pearson_r"] - 1.0) < 1e-9


# --- constraint_satisfaction_rate ---

def test_csr_all_satisfied():
    spec = IntentSpec(
        goal="g",
        constraints=["use authorized sources", "return json"],
    )
    call = ToolCall(
        tool_name="tool",
        rationale="I use authorized sources and return json data",
    )
    assert constraint_satisfaction_rate(spec, call) == 1.0


def test_csr_none_satisfied():
    spec = IntentSpec(
        goal="g",
        constraints=["must encrypt data", "must log audit trail"],
    )
    call = ToolCall(tool_name="tool", rationale="just fetching the data")
    assert constraint_satisfaction_rate(spec, call) == 0.0


def test_csr_partial():
    spec = IntentSpec(
        goal="g",
        constraints=["must encrypt data", "must return json"],
    )
    call = ToolCall(tool_name="tool", rationale="must return json output")
    csr = constraint_satisfaction_rate(spec, call)
    assert csr == 0.5


def test_csr_no_constraints_returns_one():
    spec = IntentSpec(goal="g")
    call = ToolCall(tool_name="tool", rationale="anything")
    assert constraint_satisfaction_rate(spec, call) == 1.0


# --- ambiguity_resolution_score ---

def test_ars_no_ambiguity_returns_one():
    spec = IntentSpec(goal="g", ambiguity_level=0.0)
    call = ToolCall(tool_name="tool")
    assert ambiguity_resolution_score(spec, call) == 1.0


def test_ars_high_ambiguity_no_resolution_penalised():
    spec = IntentSpec(goal="g", ambiguity_level=0.9)
    call = ToolCall(tool_name="tool", rationale="doing stuff")
    score = ambiguity_resolution_score(spec, call)
    assert score < 0.5


def test_ars_explicit_ambiguities_resolved_in_rationale():
    spec = IntentSpec(
        goal="g",
        ambiguity_level=0.5,
        ambiguities=["which timezone is primary", "which conferencing platform"],
    )
    call = ToolCall(
        tool_name="tool",
        rationale="I assume which timezone is primary is UTC and which conferencing platform is Zoom",
    )
    score = ambiguity_resolution_score(spec, call)
    assert score >= 0.9


def test_ars_clarifications_provide_bonus():
    spec = IntentSpec(goal="g", ambiguity_level=0.5, ambiguities=["date range"])
    call = ToolCall(
        tool_name="tool",
        rationale="I resolved the date range to last quarter",
        clarifications=["date range set to Q1 2024"],
    )
    score = ambiguity_resolution_score(spec, call)
    assert score >= 1.0 or score > 0.9


# --- ConstraintTracker ---

def test_constraint_tracker_satisfied():
    spec = IntentSpec(
        goal="g",
        constraints=["use authorized sources", "return json"],
    )
    call = ToolCall(
        tool_name="tool",
        rationale="use authorized sources and return json",
    )
    tracker = ConstraintTracker(spec=spec, call=call)
    assert tracker.satisfaction_rate() == 1.0
    assert tracker.unsatisfied_constraints() == []


def test_constraint_tracker_unsatisfied():
    spec = IntentSpec(
        goal="g",
        constraints=["must encrypt", "must log"],
    )
    call = ToolCall(tool_name="tool", rationale="must log the operation")
    tracker = ConstraintTracker(spec=spec, call=call)
    assert "must encrypt" in tracker.unsatisfied_constraints()
    assert tracker.satisfaction_rate() == 0.5
