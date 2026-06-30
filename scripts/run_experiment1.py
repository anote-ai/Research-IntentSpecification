#!/usr/bin/env python3
"""Experiment 1: IVR by specification type.

Usage (from repo root):
    python scripts/run_experiment1.py

Loads spec pairs from data/specs/spec_pairs.jsonl, generates 5 solutions per
spec pair using the Anthropic API (claude-sonnet-4-6), evaluates each solution
against stated and hidden constraint tests, and reports IVR overall and by
spec type. Results are saved to results/experiment1.json.

Set ANTHROPIC_API_KEY in your environment before running.
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(REPO_ROOT / "src"))

from intentspec.dataset import load_spec_pairs
from intentspec.execute import evaluate_solution
from intentspec.generate import generate_solutions
from intentspec.ivr import compute_ivr, compute_ivr_by_type
from intentspec.schema import SolutionResult

SPECS_PATH = REPO_ROOT / "data" / "specs" / "spec_pairs.jsonl"
CACHE_DIR = REPO_ROOT / "data" / "generations"
RESULTS_DIR = REPO_ROOT / "results"
N_SOLUTIONS = 5
MODEL = "claude-sonnet-4-6"


def main() -> None:
    if not SPECS_PATH.exists():
        print(f"Error: spec pairs file not found at {SPECS_PATH}", file=sys.stderr)
        sys.exit(1)

    spec_pairs = load_spec_pairs(SPECS_PATH)
    print(f"Loaded {len(spec_pairs)} spec pairs from {SPECS_PATH.relative_to(REPO_ROOT)}")

    all_results: dict[str, list[SolutionResult]] = {}

    for spec_pair in spec_pairs:
        print(f"\n[{spec_pair.task_id}] ({spec_pair.spec_type}) Generating {N_SOLUTIONS} solutions...")
        solutions = generate_solutions(spec_pair, model=MODEL, n=N_SOLUTIONS, cache_dir=CACHE_DIR)

        results: list[SolutionResult] = []
        for i, solution_code in enumerate(solutions):
            result = evaluate_solution(solution_code, spec_pair)
            stated_label = "PASS" if result.passes_stated_tests else "FAIL"
            n_hidden_failed = len(result.failed_hidden_ids)
            n_hidden_total = len(spec_pair.hidden_test_ids)
            print(
                f"  Solution {i + 1}: stated={stated_label}, "
                f"hidden_failed={n_hidden_failed}/{n_hidden_total}"
                + (f" ({result.failed_hidden_ids})" if result.failed_hidden_ids else "")
            )
            results.append(result)

        all_results[spec_pair.task_id] = results

    print("\n--- IVR Results ---")
    overall_scores: list[float] = []
    for task_id, results in all_results.items():
        ivr = compute_ivr(results)
        if ivr.n_passing_stated > 0:
            overall_scores.append(ivr.ivr_score)
        print(
            f"  {task_id}: IVR={ivr.ivr_score:.3f} "
            f"({ivr.n_violating}/{ivr.n_passing_stated} passing-stated solutions violate >= 1 hidden constraint)"
        )

    overall_ivr = sum(overall_scores) / len(overall_scores) if overall_scores else 0.0
    print(f"\nOverall IVR (mean across tasks with >= 1 passing-stated solution): {overall_ivr:.3f}")

    ivr_by_type = compute_ivr_by_type(spec_pairs, all_results)
    print("\nIVR by spec type:")
    for stype, ivr_mean in ivr_by_type.items():
        print(f"  {stype}: {ivr_mean:.3f}")

    RESULTS_DIR.mkdir(exist_ok=True)
    output = {
        "model": MODEL,
        "n_solutions_per_spec": N_SOLUTIONS,
        "overall_ivr": overall_ivr,
        "ivr_by_type": ivr_by_type,
        "per_task": {
            tid: [
                {
                    "passes_stated": r.passes_stated_tests,
                    "passed_hidden": r.passed_hidden_ids,
                    "failed_hidden": r.failed_hidden_ids,
                }
                for r in task_results
            ]
            for tid, task_results in all_results.items()
        },
    }
    output_path = RESULTS_DIR / "experiment1.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2)
    print(f"\nFull results saved to {output_path.relative_to(REPO_ROOT)}")


if __name__ == "__main__":
    main()
