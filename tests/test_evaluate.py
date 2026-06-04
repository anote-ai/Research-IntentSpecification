import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from intentspec.core import IntentSpec, ToolCall, EvalRecord
from intentspec.evaluate import (
    score_intent_alignment, score_syntactic, compare_scores, divergence_analysis
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
        EvalRecord(intent_spec=spec, predicted_call=call, reference_call=call,
                   intent_score=0.8, syntactic_score=0.6),
        EvalRecord(intent_spec=spec, predicted_call=call, reference_call=call,
                   intent_score=0.5, syntactic_score=0.9),
    ]
    result = divergence_analysis(records)
    for key in ["mean_intent", "mean_syntactic", "mean_divergence", "max_divergence", "overstatement_rate"]:
        assert key in result


def test_pearson_r_identical_arrays():
    scores = [0.1, 0.5, 0.9, 0.3, 0.7]
    result = compare_scores(scores, scores)
    assert abs(result["pearson_r"] - 1.0) < 1e-9
