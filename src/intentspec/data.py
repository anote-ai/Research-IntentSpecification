from __future__ import annotations
from .core import IntentSpec, ToolCall


def make_intent_spec(
    goal: str = "Retrieve quarterly revenue data for analysis",
    n_constraints: int = 2,
) -> IntentSpec:
    constraints = [
        "must use authorized data sources",
        "must return structured JSON output",
        "must complete within 5 seconds",
        "must handle missing values gracefully",
    ][:n_constraints]
    return IntentSpec(
        goal=goal,
        constraints=constraints,
        success_criteria="returns structured data",
        ambiguity_level=0.2,
    )


def make_tool_call(
    tool_name: str = "query_database",
    match_spec: bool = True,
) -> ToolCall:
    if match_spec:
        rationale = (
            "Using authorized data sources to query the database and "
            "returns structured JSON output within the required time frame. "
            "The function returns structured data as required."
        )
        arguments = {"table": "revenue", "quarter": "Q1", "format": "json"}
    else:
        rationale = "Quick lookup without any constraints consideration."
        arguments = {"table": "revenue"}
    return ToolCall(tool_name=tool_name, arguments=arguments, rationale=rationale)


def make_eval_dataset(
    n: int = 10,
) -> list[tuple[IntentSpec, ToolCall, ToolCall]]:
    """Returns list of (spec, predicted_call, reference_call) tuples."""
    dataset = []
    for i in range(n):
        spec = make_intent_spec(
            goal=f"Enterprise task {i}: retrieve and process data",
            n_constraints=2,
        )
        reference = make_tool_call(tool_name="query_database", match_spec=True)
        predicted = make_tool_call(
            tool_name="query_database" if i % 2 == 0 else "wrong_tool",
            match_spec=(i % 2 == 0),
        )
        dataset.append((spec, predicted, reference))
    return dataset
