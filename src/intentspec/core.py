from __future__ import annotations
from pydantic import BaseModel, Field, field_validator
from typing import Any

from .evaluate import score_intent_alignment, score_syntactic


class IntentSpec(BaseModel):
    goal: str
    constraints: list[str] = Field(default_factory=list)
    success_criteria: str = ""
    ambiguity_level: float = 0.0

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


class EvalRecord(BaseModel):
    intent_spec: IntentSpec
    predicted_call: ToolCall
    reference_call: ToolCall
    intent_score: float
    syntactic_score: float
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
        return EvalRecord(
            intent_spec=spec,
            predicted_call=predicted,
            reference_call=reference,
            intent_score=i_score,
            syntactic_score=s_score,
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
