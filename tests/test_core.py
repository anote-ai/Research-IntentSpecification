import pytest
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from intentspec.core import IntentSpec, ToolCall, EvalRecord, IntentEvaluator


def test_intent_spec_construction():
    spec = IntentSpec(goal="Retrieve data", constraints=["use auth"], ambiguity_level=0.3)
    assert spec.goal == "Retrieve data"
    assert len(spec.constraints) == 1
    assert spec.ambiguity_level == 0.3


def test_ambiguity_level_valid():
    spec = IntentSpec(goal="test", ambiguity_level=0.5)
    assert spec.ambiguity_level == 0.5


def test_ambiguity_level_invalid():
    with pytest.raises(Exception):
        IntentSpec(goal="test", ambiguity_level=1.5)


def test_tool_call_construction():
    call = ToolCall(tool_name="my_tool", arguments={"a": 1}, rationale="because")
    assert call.tool_name == "my_tool"
    assert call.arguments == {"a": 1}


def test_eval_record_divergence_computed():
    spec = IntentSpec(goal="test")
    pred = ToolCall(tool_name="tool_a", arguments={"x": 1})
    ref = ToolCall(tool_name="tool_a", arguments={"x": 1})
    record = EvalRecord(
        intent_spec=spec, predicted_call=pred, reference_call=ref,
        intent_score=0.8, syntactic_score=0.6,
    )
    assert abs(record.divergence - 0.2) < 1e-9


def test_intent_evaluator_evaluate_returns_eval_record():
    evaluator = IntentEvaluator()
    spec = IntentSpec(goal="Retrieve data", constraints=["use auth"])
    pred = ToolCall(tool_name="query_db", rationale="use auth to get data")
    ref = ToolCall(tool_name="query_db", arguments={"table": "users"})
    record = evaluator.evaluate(spec, pred, ref)
    assert isinstance(record, EvalRecord)


def test_batch_evaluate_length():
    evaluator = IntentEvaluator()
    specs = [IntentSpec(goal=f"goal {i}") for i in range(5)]
    calls = [ToolCall(tool_name="tool") for _ in range(5)]
    records = evaluator.batch_evaluate(specs, calls, calls)
    assert len(records) == 5


def test_eval_record_intent_score_in_range():
    evaluator = IntentEvaluator()
    spec = IntentSpec(goal="test", constraints=["constraint one"])
    pred = ToolCall(tool_name="tool", rationale="constraint one is satisfied")
    ref = ToolCall(tool_name="tool")
    record = evaluator.evaluate(spec, pred, ref)
    assert 0.0 <= record.intent_score <= 1.0


def test_eval_record_syntactic_score_in_range():
    evaluator = IntentEvaluator()
    spec = IntentSpec(goal="test")
    pred = ToolCall(tool_name="tool_a", arguments={"x": 1})
    ref = ToolCall(tool_name="tool_b", arguments={"y": 2})
    record = evaluator.evaluate(spec, pred, ref)
    assert 0.0 <= record.syntactic_score <= 1.0
