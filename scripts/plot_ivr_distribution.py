#!/usr/bin/env python3
"""Visualize the distribution of per-task IVR scores from an experiment run.

Usage (from repo root):
    python scripts/plot_ivr_distribution.py [results/experiment1.json]

Reads a results JSON produced by run_experiment1.py (model, per_task solution
outcomes), recomputes per-task IVR, and plots a histogram of per-task IVR scores.

Saves the figure next to the input file as <name>_ivr_distribution.png.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import matplotlib.pyplot as plt

from intentspec.ivr import compute_ivr
from intentspec.schema import SolutionResult

REPO_ROOT = Path(__file__).parent.parent


def load_per_task_ivr(results_path: Path) -> dict[str, float]:
    with open(results_path, encoding="utf-8") as f:
        data = json.load(f)

    per_task_ivr: dict[str, float] = {}
    for task_id, solutions in data["per_task"].items():
        results = [
            SolutionResult(
                task_id=task_id,
                solution_code="",
                passes_stated_tests=s["passes_stated"],
                passed_hidden_ids=s["passed_hidden"],
                failed_hidden_ids=s["failed_hidden"],
            )
            for s in solutions
        ]
        ivr = compute_ivr(results)
        if ivr.n_passing_stated > 0:
            per_task_ivr[task_id] = ivr.ivr_score
    return per_task_ivr


def main() -> None:
    results_path = Path(sys.argv[1]) if len(sys.argv) > 1 else REPO_ROOT / "results" / "experiment1.json"
    if not results_path.exists():
        print(f"Error: results file not found at {results_path}", file=sys.stderr)
        sys.exit(1)

    per_task_ivr = load_per_task_ivr(results_path)
    if not per_task_ivr:
        print("No tasks with passing-stated solutions found; nothing to plot.", file=sys.stderr)
        sys.exit(1)

    scores = list(per_task_ivr.values())

    fig, ax1 = plt.subplots(figsize=(7, 5))

    bins = [i / 10 for i in range(11)]
    ax1.hist(scores, bins=bins, edgecolor="black", color="#4C72B0")
    ax1.set_xlabel("IVR Score")
    ax1.set_ylabel("Number of Tasks")
    ax1.set_title(f"Distribution of per-task IVR (n={len(scores)})")
    ax1.axvline(sum(scores) / len(scores), color="red", linestyle="--", label=f"mean = {sum(scores) / len(scores):.2f}")
    ax1.legend()

    fig.suptitle("Intent Violation Rate")
    fig.tight_layout()

    out_path = results_path.parent / f"{results_path.stem}_ivr_distribution.png"
    fig.savefig(out_path, dpi=150)
    print(f"Saved plot to {out_path.relative_to(REPO_ROOT)}")
    plt.show()


if __name__ == "__main__":
    main()
