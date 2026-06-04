from __future__ import annotations
from pydantic import BaseModel, Field, field_validator
from typing import Any

from .evaluate import (
    score_intent_alignment,
    score_syntactic,
    constraint_satisfaction_rate,
    ambiguity_resolution_score,
)


class IntentSpec(BaseModel):
    goal: str
    constraints: list[str] = Field(default_factory=list)
    success_criteria: str = ""
    ambiguity_level: float = 0.0
    # Optional: clarification questions the agent should resolve
    ambiguities: list[str] = Field(default_factory=list)

    @field_validator("ambiguity_level")
    @classmethod
    def check_ambiguity(cls, v: float) -> float:
        if not (0.0 <= v <= 1.0):
            raise ValueError(f"ambiguity_level must be in [0, 1], got {v}")
        return v


class ToolCall(BaseModel):
    tool_name: str
    arguments: dict[str, Any] = Field(default_factory=dict)
    rationale: str = ""
    # Clarifications the agent provided before making the call
    clarifications: list[str] = Field(default_factory=list)


class ConstraintTracker(BaseModel):
    """Tracks which constraints from a spec were satisfied by a tool call."""

    spec: IntentSpec
    call: ToolCall

    def satisfied_constraints(self) -> list[str]:
        rationale_lower = self.call.rationale.lower()
        return [
            c for c in self.spec.constraints
            if c.lower() in rationale_lower
        ]

    def unsatisfied_constraints(self) -> list[str]:
        satisfied = set(self.satisfied_constraints())
        return [c for c in self.spec.constraints if c not in satisfied]

    def satisfaction_rate(self) -> float:
        if not self.spec.constraints:
            return 1.0
        return len(self.satisfied_constraints()) / len(self.spec.constraints)


class EvalRecord(BaseModel):
    intent_spec: IntentSpec
    predicted_call: ToolCall
    reference_call: ToolCall
    intent_score: float
    syntactic_score: float
    constraint_sat_rate: float = 0.0
    ambiguity_res_score: float = 0.0
    divergence: float = 0.0

    def model_post_init(self, __context: Any) -> None:
        object.__setattr__(self, "divergence", abs(self.intent_score - self.syntactic_score))


class IntentEvaluator:
    def evaluate(
        self,
        spec: IntentSpec,
        predicted: ToolCall,
        reference: ToolCall,
    ) -> EvalRecord:
        i_score = score_intent_alignment(spec, predicted)
        s_score = score_syntactic(predicted, reference)
        csr = constraint_satisfaction_rate(spec, predicted)
        ars = ambiguity_resolution_score(spec, predicted)
        return EvalRecord(
            intent_spec=spec,
            predicted_call=predicted,
            reference_call=reference,
            intent_score=i_score,
            syntactic_score=s_score,
            constraint_sat_rate=csr,
            ambiguity_res_score=ars,
        )

    def batch_evaluate(
        self,
        specs: list[IntentSpec],
        predicteds: list[ToolCall],
        references: list[ToolCall],
    ) -> list[EvalRecord]:
        return [
            self.evaluate(s, p, r)
            for s, p, r in zip(specs, predicteds, references)
        ]
