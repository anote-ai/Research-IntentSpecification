from __future__ import annotations
from .core import IntentSpec, ToolCall


MULTI_CONSTRAINT_SPECS: list[dict] = [
    {
        "goal": "Retrieve quarterly revenue data for analysis",
        "constraints": [
            "must use authorized data sources",
            "must return structured JSON output",
            "must complete within 5 seconds",
            "must handle missing values gracefully",
        ],
        "success_criteria": "returns structured data",
        "ambiguity_level": 0.1,
        "ambiguities": [],
    },
    {
        "goal": "Schedule a cross-timezone meeting with external partners",
        "constraints": [
            "must respect participant availability windows",
            "must send calendar invites with agenda",
            "must use corporate video-conferencing platform",
        ],
        "success_criteria": "meeting invite sent",
        "ambiguity_level": 0.3,
        "ambiguities": ["which timezone is primary", "which conferencing platform"],
    },
    {
        "goal": "Generate a compliance report for SOC-2 audit",
        "constraints": [
            "must cover the last 12 months",
            "must include access control events",
            "must redact PII fields",
            "must be signed by CISO",
        ],
        "success_criteria": "report generated and signed",
        "ambiguity_level": 0.2,
        "ambiguities": ["date range start"],
    },
    {
        "goal": "Onboard a new enterprise customer to the SaaS platform",
        "constraints": [
            "must provision isolated tenant environment",
            "must configure SSO with customer IdP",
            "must send welcome email with setup guide",
            "must assign dedicated customer success manager",
        ],
        "success_criteria": "tenant provisioned and SSO configured",
        "ambiguity_level": 0.4,
        "ambiguities": ["customer IdP type", "data residency region"],
    },
    {
        "goal": "Perform automated regression testing after deployment",
        "constraints": [
            "must run full test suite in under 10 minutes",
            "must report failures with stack traces",
            "must gate production rollout on passing tests",
        ],
        "success_criteria": "test suite passed",
        "ambiguity_level": 0.15,
        "ambiguities": [],
    },
    {
        "goal": "Summarise and route customer support tickets by severity",
        "constraints": [
            "must classify tickets as P1/P2/P3",
            "must route P1 tickets to on-call engineer within 5 minutes",
            "must log all routing decisions for audit",
        ],
        "success_criteria": "tickets routed and logged",
        "ambiguity_level": 0.25,
        "ambiguities": ["P1 definition threshold"],
    },
]


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


def make_multi_constraint_spec(index: int = 0) -> IntentSpec:
    """Return a realistic multi-constraint IntentSpec from the curated set."""
    entry = MULTI_CONSTRAINT_SPECS[index % len(MULTI_CONSTRAINT_SPECS)]
    return IntentSpec(**entry)


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
