"""IntentSpec: Intent-aligned evaluation of LLM tool-use beyond syntactic matching."""
from .core import IntentSpec, ToolCall, EvalRecord, IntentEvaluator
from .evaluate import (
    score_intent_alignment, score_syntactic, compare_scores, divergence_analysis
)

__version__ = "0.1.0"
__all__ = [
    "IntentSpec", "ToolCall", "EvalRecord", "IntentEvaluator",
    "score_intent_alignment", "score_syntactic", "compare_scores", "divergence_analysis",
]
