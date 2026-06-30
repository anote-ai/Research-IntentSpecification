# DEPRECATED: System A synthetic dataset helpers.
# Retained so existing imports don't break. New code should use dataset.py.
from __future__ import annotations
from .core import IntentSpec, ToolCall

MULTI_CONSTRAINT_SPECS: list[dict] = []


def make_intent_spec(goal: str = "task", n_constraints: int = 2) -> IntentSpec:
    return IntentSpec(goal=goal)


def make_multi_constraint_spec(index: int = 0) -> IntentSpec:
    return IntentSpec(goal=f"task {index}")


def make_tool_call(tool_name: str = "tool", match_spec: bool = True) -> ToolCall:
    return ToolCall(tool_name=tool_name)


def make_eval_dataset(n: int = 10) -> list[tuple[IntentSpec, ToolCall, ToolCall]]:
    spec = IntentSpec(goal="task")
    call = ToolCall(tool_name="tool")
    return [(spec, call, call)] * n
