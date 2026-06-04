#!/usr/bin/env python3
"""Demo: run IntentSpec evaluation with synthetic data."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from intentspec.core import IntentEvaluator
from intentspec.data import make_eval_dataset
from intentspec.evaluate import divergence_analysis


def main():
    dataset = make_eval_dataset(10)
    evaluator = IntentEvaluator()

    specs = [d[0] for d in dataset]
    predicteds = [d[1] for d in dataset]
    references = [d[2] for d in dataset]

    records = evaluator.batch_evaluate(specs, predicteds, references)

    print(f"Evaluated {len(records)} records.")
    for i, r in enumerate(records):
        print(f"  [{i}] intent={r.intent_score:.3f} syntactic={r.syntactic_score:.3f} divergence={r.divergence:.3f}")

    analysis = divergence_analysis(records)
    print("\nDivergence Analysis:")
    for k, v in analysis.items():
        print(f"  {k}: {v:.3f}")


if __name__ == "__main__":
    main()
