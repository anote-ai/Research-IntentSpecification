#!/usr/bin/env python3
# LEGACY: System A syntactic/intent divergence demo. Use run_experiment1.py instead.
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from intentspec.core import IntentEvaluator
from intentspec.data import make_eval_dataset
from intentspec.evaluate import divergence_analysis


def main():
    print("NOTE: run_eval.py runs the deprecated System A pipeline.")
    print("For the current IVR pipeline, run: python scripts/run_experiment1.py\n")
    dataset = make_eval_dataset(10)
    evaluator = IntentEvaluator()
    specs = [d[0] for d in dataset]
    predicteds = [d[1] for d in dataset]
    references = [d[2] for d in dataset]
    records = evaluator.batch_evaluate(specs, predicteds, references)
    print(f"Evaluated {len(records)} records.")
    analysis = divergence_analysis(records)
    for k, v in analysis.items():
        print(f"  {k}: {v:.3f}")


if __name__ == "__main__":
    main()
