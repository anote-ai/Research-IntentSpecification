"""Tests for intentspec.core."""

import pytest

from intentspec.core import EvalRecord, IntentEvaluator, IntentSpec, ToolCall


# ---------------------------------------------------------------------------
# IntentSpec
# ---------------------------------------------------------------------------

def test_intent_spec_basic_creation() -> None:
    spec = IntentSpec(goal="Fetch stock price", success_criteria="Price returned")
    assert spec.goal == "Fetch stock price"
    assert spec.ambiguity_level == 0.0
    assert spec.constraints == []


def test_intent_spec_with_constraints() -> None:
    spec = IntentSpec(
        goal="Transfer funds",
        constraints=["amount > 0", "currency in USD"],
        success_criteria="Transfer confirmed",
        ambiguity_level=0.2,
    )
    assert len(spec.constraints) == 2
    assert spec.ambiguity_level == 0.2


def test_intent_spec_ambiguity_bounds() -> None:
    with pytest.raises(Exception):
        IntentSpec(goal="X", success_criteria="Y", ambiguity_level=1.5)


# ---------------------------------------------------------------------------
# ToolCall
# ---------------------------------------------------------------------------

def test_tool_call_creation() -> None:
    call = ToolCall(tool_name="get_price", arguments={"symbol": "AAPL"})
    assert call.tool_name == "get_price"
    assert call.arguments["symbol"] == "AAPL"
    assert call.rationale == ""


def test_tool_call_with_rationale() -> None:
    call = ToolCall(
        tool_name="transfer",
        arguments={"amount": 100},
        rationale="The user wants to transfer 100 USD",
    )
    assert "transfer" in call.rationale.lower() or call.rationale != ""


# ---------------------------------------------------------------------------
# EvalRecord
# ---------------------------------------------------------------------------

def _make_spec() -> IntentSpec:
    return IntentSpec(goal="Test", success_criteria="Done")


def _make_call(name: str = "tool") -> ToolCall:
    return ToolCall(tool_name=name)


def test_eval_record_creation() -> None:
    rec = EvalRecord(
        intent_spec=_make_spec(),
        predicted_call=_make_call("predicted"),
        reference_call=_make_call("reference"),
    )
    assert rec.intent_score == 0.0
    assert rec.syntactic_score == 0.0


def test_eval_record_with_scores() -> None:
    rec = EvalRecord(
        intent_spec=_make_spec(),
        predicted_call=_make_call(),
        reference_call=_make_call(),
        intent_score=0.9,
        syntactic_score=0.7,
    )
    assert rec.intent_score == 0.9
    assert rec.syntactic_score == 0.7


# ---------------------------------------------------------------------------
# IntentEvaluator
# ---------------------------------------------------------------------------

def test_intent_evaluator_instantiation() -> None:
    evaluator = IntentEvaluator()
    assert evaluator is not None


def test_intent_evaluator_evaluate_raises() -> None:
    evaluator = IntentEvaluator()
    with pytest.raises(NotImplementedError):
        evaluator.evaluate(_make_spec(), _make_call(), _make_call())
