"""Scoring utilities for intent-specification evaluation."""

from __future__ import annotations

import numpy as np

from .core import IntentSpec, ToolCall


def score_intent_alignment(spec: IntentSpec, call: ToolCall) -> float:
    """Score how well a tool call's rationale satisfies the intent spec constraints.

    Each constraint in ``spec.constraints`` is checked for keyword presence in
    ``call.rationale``.  The score is the fraction of constraints covered.

    Args:
        spec: The intent specification containing constraints.
        call: The tool call whose rationale is checked.

    Returns:
        Float in [0.0, 1.0].  Returns 1.0 when there are no constraints.
    """
    if not spec.constraints:
        return 1.0
    rationale_lower = call.rationale.lower()
    hits = sum(
        1 for constraint in spec.constraints if constraint.lower() in rationale_lower
    )
    return hits / len(spec.constraints)


def score_syntactic(predicted: ToolCall, reference: ToolCall) -> float:
    """Score syntactic correctness of a predicted tool call vs a reference.

    Checks tool name match and parameter key overlap (Jaccard similarity).

    Args:
        predicted: The tool call produced by the agent.
        reference: The ground-truth reference call.

    Returns:
        Float in [0.0, 1.0].
    """
    name_match = float(predicted.tool_name == reference.tool_name)
    pred_keys = set(predicted.arguments.keys())
    ref_keys = set(reference.arguments.keys())
    if not pred_keys and not ref_keys:
        key_score = 1.0
    elif not pred_keys or not ref_keys:
        key_score = 0.0
    else:
        key_score = len(pred_keys & ref_keys) / len(pred_keys | ref_keys)
    return (name_match + key_score) / 2.0


def compare_scores(
    intent_scores: list[float],
    syntactic_scores: list[float],
) -> dict[str, float]:
    """Compare intent-alignment scores against syntactic scores.

    Computes Pearson correlation and mean divergence between the two score
    sequences, quantifying the gap between syntactic accuracy and true intent
    alignment.

    Args:
        intent_scores: Intent alignment scores per sample.
        syntactic_scores: Syntactic correctness scores per sample.

    Returns:
        Dict with keys ``correlation``, ``mean_divergence``, ``mean_intent``,
        ``mean_syntactic``.

    Raises:
        ValueError: If the input lists differ in length or are empty.
    """
    if len(intent_scores) != len(syntactic_scores):
        raise ValueError("intent_scores and syntactic_scores must have the same length")
    if not intent_scores:
        raise ValueError("score lists must be non-empty")
    ia = np.array(intent_scores, dtype=float)
    sa = np.array(syntactic_scores, dtype=float)
    if ia.std() == 0 or sa.std() == 0:
        correlation = float("nan")
    else:
        correlation = float(np.corrcoef(ia, sa)[0, 1])
    return {
        "correlation": correlation,
        "mean_divergence": float(np.abs(ia - sa).mean()),
        "mean_intent": float(ia.mean()),
        "mean_syntactic": float(sa.mean()),
    }
