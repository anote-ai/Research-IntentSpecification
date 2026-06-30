# DEPRECATED: System A (tool-call rationale/syntactic divergence scoring).
# This file is retained only so that any external code that imported from it
# does not break with an ImportError. All active research code uses the
# System B modules: schema.py, dataset.py, generate.py, execute.py, ivr.py.
#
# Do not add new functionality here.

from __future__ import annotations
from typing import Any
from pydantic import BaseModel, Field, field_validator


class IntentSpec(BaseModel):
    goal: str
    constraints: list[str] = Field(default_factory=list)
    success_criteria: str = ""
    ambiguity_level: float = 0.0
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
    clarifications: list[str] = Field(default_factory=list)


class ConstraintTracker(BaseModel):
    spec: IntentSpec
    call: ToolCall

    def satisfied_constraints(self) -> list[str]:
        rationale_lower = self.call.rationale.lower()
        return [c for c in self.spec.constraints if c.lower() in rationale_lower]

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
    def evaluate(self, spec: IntentSpec, predicted: ToolCall, reference: ToolCall) -> EvalRecord:
        from .evaluate import (
            score_intent_alignment,
            score_syntactic,
            constraint_satisfaction_rate,
            ambiguity_resolution_score,
        )
        return EvalRecord(
            intent_spec=spec,
            predicted_call=predicted,
            reference_call=reference,
            intent_score=score_intent_alignment(spec, predicted),
            syntactic_score=score_syntactic(predicted, reference),
            constraint_sat_rate=constraint_satisfaction_rate(spec, predicted),
            ambiguity_res_score=ambiguity_resolution_score(spec, predicted),
        )

    def batch_evaluate(
        self,
        specs: list[IntentSpec],
        predicteds: list[ToolCall],
        references: list[ToolCall],
    ) -> list[EvalRecord]:
        return [self.evaluate(s, p, r) for s, p, r in zip(specs, predicteds, references)]
