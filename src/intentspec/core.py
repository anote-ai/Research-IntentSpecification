"""Core pydantic models and evaluation orchestration for intentspec."""

from __future__ import annotations

from pydantic import BaseModel, Field


class IntentSpec(BaseModel):
    """Structured representation of a user intent."""

    goal: str = Field(..., description="High-level goal the user wants to achieve.")
    constraints: list[str] = Field(
        default_factory=list,
        description="Constraints that a valid tool call must satisfy.",
    )
    success_criteria: str = Field(
        ..., description="Human-readable description of what constitutes success."
    )
    ambiguity_level: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
        description="Degree of ambiguity in the intent (0 = fully specified, 1 = highly ambiguous).",
    )


class ToolCall(BaseModel):
    """A tool call produced or expected from an agent."""

    tool_name: str = Field(..., description="Name of the tool to invoke.")
    arguments: dict = Field(default_factory=dict, description="Arguments passed to the tool.")
    rationale: str = Field(
        default="", description="Agent's stated rationale for choosing this tool/arguments."
    )


class EvalRecord(BaseModel):
    """Full evaluation record pairing an intent spec with agent and reference tool calls."""

    intent_spec: IntentSpec
    predicted_call: ToolCall
    reference_call: ToolCall
    intent_score: float = Field(default=0.0, ge=0.0, le=1.0)
    syntactic_score: float = Field(default=0.0, ge=0.0, le=1.0)


class IntentEvaluator:
    """Evaluates tool calls against intent specifications."""

    def evaluate(
        self,
        intent_spec: IntentSpec,
        predicted_call: ToolCall,
        reference_call: ToolCall,
    ) -> EvalRecord:
        """Evaluate a predicted tool call against an intent spec and reference call (stub).

        Args:
            intent_spec: The structured intent specification.
            predicted_call: The tool call produced by the agent under evaluation.
            reference_call: The ground-truth reference tool call.

        Returns:
            An :class:`EvalRecord` with populated scores.
        """
        # TODO: call score_intent_alignment and score_syntactic from evaluate module
        raise NotImplementedError("evaluate is not yet implemented")
