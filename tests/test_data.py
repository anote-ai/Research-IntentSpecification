import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from intentspec.data import (
    make_intent_spec,
    make_multi_constraint_spec,
    make_tool_call,
    make_eval_dataset,
    MULTI_CONSTRAINT_SPECS,
)
from intentspec.core import IntentSpec, ToolCall


def test_make_intent_spec_returns_correct_type():
    spec = make_intent_spec()
    assert isinstance(spec, IntentSpec)


def test_make_intent_spec_n_constraints():
    spec = make_intent_spec(n_constraints=3)
    assert len(spec.constraints) == 3


def test_make_multi_constraint_spec_all_indices():
    for i in range(len(MULTI_CONSTRAINT_SPECS)):
        spec = make_multi_constraint_spec(i)
        assert isinstance(spec, IntentSpec)
        assert len(spec.constraints) >= 2


def test_make_multi_constraint_spec_has_ambiguities_when_present():
    # Index 1 has ambiguities
    spec = make_multi_constraint_spec(1)
    assert len(spec.ambiguities) > 0


def test_make_tool_call_matching():
    call = make_tool_call(match_spec=True)
    assert isinstance(call, ToolCall)
    assert "format" in call.arguments


def test_make_eval_dataset_length():
    dataset = make_eval_dataset(n=6)
    assert len(dataset) == 6


def test_make_eval_dataset_tuples():
    dataset = make_eval_dataset(n=4)
    for spec, pred, ref in dataset:
        assert isinstance(spec, IntentSpec)
        assert isinstance(pred, ToolCall)
        assert isinstance(ref, ToolCall)
