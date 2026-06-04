from __future__ import annotations
import math
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .core import IntentSpec, ToolCall, EvalRecord


def score_intent_alignment(spec: "IntentSpec", call: "ToolCall") -> float:
    """Fraction of spec.constraints found in call.rationale + bonus for success_criteria."""
    rationale_lower = call.rationale.lower()
    if not spec.constraints:
        matched = 0
        total = 1
    else:
        matched = sum(
            1 for c in spec.constraints if c.lower() in rationale_lower
        )
        total = len(spec.constraints)
    base = matched / total
    # Bonus if success_criteria keyword found (up to 0.2 extra, capped at 1.0)
    bonus = 0.0
    if spec.success_criteria and spec.success_criteria.lower() in rationale_lower:
        bonus = 0.2
    return min(1.0, base + bonus)


def score_syntactic(predicted: "ToolCall", reference: "ToolCall") -> float:
    """Name match (0.5 weight) + argument key Jaccard (0.5 weight)."""
    name_match = float(predicted.tool_name == reference.tool_name)
    pred_keys = set(predicted.arguments.keys())
    ref_keys = set(reference.arguments.keys())
    union = pred_keys | ref_keys
    key_jaccard = len(pred_keys & ref_keys) / len(union) if union else 1.0
    return 0.5 * name_match + 0.5 * key_jaccard


def compare_scores(
    intent_scores: list[float],
    syntactic_scores: list[float],
) -> dict:
    """Pearson r, mean divergence, cases where syntactic overstates intent."""
    n = len(intent_scores)
    if n == 0:
        return {"pearson_r": 0.0, "mean_divergence": 0.0, "cases_where_syntactic_overstates": 0}

    def _pearson(xs: list[float], ys: list[float]) -> float:
        mean_x = sum(xs) / len(xs)
        mean_y = sum(ys) / len(ys)
        num = sum((x - mean_x) * (y - mean_y) for x, y in zip(xs, ys))
        den = math.sqrt(
            sum((x - mean_x) ** 2 for x in xs) * sum((y - mean_y) ** 2 for y in ys)
        )
        return num / den if den > 1e-12 else 0.0

    r = _pearson(intent_scores, syntactic_scores)
    divergences = [abs(i - s) for i, s in zip(intent_scores, syntactic_scores)]
    overstates = sum(1 for i, s in zip(intent_scores, syntactic_scores) if s > i)
    return {
        "pearson_r": r,
        "mean_divergence": sum(divergences) / n,
        "cases_where_syntactic_overstates": overstates,
    }


def divergence_analysis(records: list["EvalRecord"]) -> dict:
    """Summary statistics over a list of EvalRecord objects."""
    if not records:
        return {
            "mean_intent": 0.0, "mean_syntactic": 0.0,
            "mean_divergence": 0.0, "max_divergence": 0.0, "overstatement_rate": 0.0,
        }
    n = len(records)
    intent_scores = [r.intent_score for r in records]
    syntactic_scores = [r.syntactic_score for r in records]
    divergences = [r.divergence for r in records]
    overstatements = sum(1 for r in records if r.syntactic_score > r.intent_score)
    return {
        "mean_intent": sum(intent_scores) / n,
        "mean_syntactic": sum(syntactic_scores) / n,
        "mean_divergence": sum(divergences) / n,
        "max_divergence": max(divergences),
        "overstatement_rate": overstatements / n,
    }
