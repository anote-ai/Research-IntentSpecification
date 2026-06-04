"""IntentSpec: Intent-aligned evaluation of LLM tool-use beyond syntactic matching."""
from .core import IntentSpec, ToolCall, EvalRecord, IntentEvaluator, ConstraintTracker
from .evaluate import (
    score_intent_alignment,
    score_syntactic,
    constraint_satisfaction_rate,
    ambiguity_resolution_score,
    compare_scores,
    divergence_analysis,
)

__version__ = "0.1.0"
__all__ = [
    "IntentSpec",
    "ToolCall",
    "EvalRecord",
    "IntentEvaluator",
    "ConstraintTracker",
    "score_intent_alignment",
    "score_syntactic",
    "constraint_satisfaction_rate",
    "ambiguity_resolution_score",
    "compare_scores",
    "divergence_analysis",
]
