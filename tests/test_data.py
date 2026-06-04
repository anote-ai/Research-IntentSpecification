import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from intentspec.core import IntentSpec, ToolCall
from intentspec.data import make_intent_spec, make_tool_call, make_eval_dataset


def test_make_intent_spec_returns_intent_spec():
    spec = make_intent_spec()
    assert isinstance(spec, IntentSpec)


def test_make_tool_call_returns_tool_call():
    call = make_tool_call()
    assert isinstance(call, ToolCall)


def test_make_eval_dataset_length():
    dataset = make_eval_dataset(10)
    assert len(dataset) == 10


def test_all_specs_have_at_least_one_constraint():
    dataset = make_eval_dataset(5)
    for spec, _, _ in dataset:
        assert len(spec.constraints) >= 1
