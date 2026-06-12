"""Tests for intentspec.evaluate."""

import pytest

from intentspec.core import IntentSpec, ToolCall
from intentspec.evaluate import compare_scores, score_intent_alignment, score_syntactic


# ---------------------------------------------------------------------------
# score_intent_alignment
# ---------------------------------------------------------------------------

def test_alignment_no_constraints() -> None:
    spec = IntentSpec(goal="Do something", success_criteria="Done")
    call = ToolCall(tool_name="anything")
    assert score_intent_alignment(spec, call) == 1.0


def test_alignment_all_constraints_met() -> None:
    spec = IntentSpec(
        goal="Transfer",
        constraints=["usd", "positive amount"],
        success_criteria="OK",
    )
    call = ToolCall(
        tool_name="transfer",
        rationale="Send USD with a positive amount from account",
    )
    assert score_intent_alignment(spec, call) == 1.0


def test_alignment_partial_constraints() -> None:
    spec = IntentSpec(
        goal="Transfer",
        constraints=["usd", "positive amount"],
        success_criteria="OK",
    )
    call = ToolCall(tool_name="transfer", rationale="Send USD")
    score = score_intent_alignment(spec, call)
    assert 0.0 < score < 1.0


# ---------------------------------------------------------------------------
# score_syntactic
# ---------------------------------------------------------------------------

def test_syntactic_perfect_match() -> None:
    pred = ToolCall(tool_name="get_price", arguments={"symbol": "AAPL"})
    ref = ToolCall(tool_name="get_price", arguments={"symbol": "MSFT"})
    assert score_syntactic(pred, ref) == 1.0


def test_syntactic_name_mismatch() -> None:
    pred = ToolCall(tool_name="wrong", arguments={"symbol": "AAPL"})
    ref = ToolCall(tool_name="get_price", arguments={"symbol": "AAPL"})
    assert score_syntactic(pred, ref) < 1.0


def test_syntactic_both_empty_args() -> None:
    pred = ToolCall(tool_name="ping")
    ref = ToolCall(tool_name="ping")
    assert score_syntactic(pred, ref) == 1.0


# ---------------------------------------------------------------------------
# compare_scores
# ---------------------------------------------------------------------------

def test_compare_scores_identical() -> None:
    scores = [0.8, 0.6, 0.9]
    result = compare_scores(scores, scores)
    assert result["mean_divergence"] == pytest.approx(0.0)


def test_compare_scores_divergent() -> None:
    intent = [0.9, 0.9, 0.9]
    syntactic = [0.3, 0.3, 0.3]
    result = compare_scores(intent, syntactic)
    assert result["mean_divergence"] == pytest.approx(0.6)
    assert result["mean_intent"] == pytest.approx(0.9)
    assert result["mean_syntactic"] == pytest.approx(0.3)


def test_compare_scores_length_mismatch() -> None:
    with pytest.raises(ValueError, match="same length"):
        compare_scores([0.5, 0.6], [0.5])


def test_compare_scores_empty_raises() -> None:
    with pytest.raises(ValueError):
        compare_scores([], [])
