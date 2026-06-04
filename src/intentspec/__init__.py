"""intentspec: Intent Specification as a First-Class Evaluation Object for Tool-Calling Agents."""

from .core import EvalRecord, IntentEvaluator, IntentSpec, ToolCall
from .evaluate import compare_scores, score_intent_alignment, score_syntactic

__all__ = [
    "IntentSpec",
    "ToolCall",
    "EvalRecord",
    "IntentEvaluator",
    "score_intent_alignment",
    "score_syntactic",
    "compare_scores",
]
__version__ = "0.1.0"
