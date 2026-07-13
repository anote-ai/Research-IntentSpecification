#!/usr/bin/env python3
"""Visualize the distribution of per-task IVR scores from an experiment run.

Usage (from repo root):
    python scripts/plot_ivr_distribution.py [results/experiment1.json]

Reads a results JSON produced by run_experiment1.py (model, per_task solution
outcomes), recomputes per-task IVR, and plots:
  1. A histogram of per-task IVR scores.
  2. A bar chart of mean IVR by spec_type (with per-task points overlaid).

Saves the figure next to the input file as <name>_ivr_distribution.png.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import matplotlib.pyplot as plt

from intentspec.dataset import load_spec_pairs
from intentspec.ivr import compute_ivr
from intentspec.schema import SolutionResult

REPO_ROOT = Path(__file__).parent.parent
SPECS_PATH = REPO_ROOT / "data" / "specs" / "spec_pairs.jsonl"


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

    task_to_type: dict[str, str] = {}
    if SPECS_PATH.exists():
        for spec_pair in load_spec_pairs(SPECS_PATH):
            task_to_type[spec_pair.task_id] = spec_pair.spec_type

    scores = list(per_task_ivr.values())
    by_type: dict[str, list[float]] = {}
    for task_id, score in per_task_ivr.items():
        stype = task_to_type.get(task_id, "unknown")
        by_type.setdefault(stype, []).append(score)

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))

    bins = [i / 10 for i in range(11)]
    ax1.hist(scores, bins=bins, edgecolor="black", color="#4C72B0")
    ax1.set_xlabel("IVR score")
    ax1.set_ylabel("Number of tasks")
    ax1.set_title(f"Distribution of per-task IVR (n={len(scores)})")
    ax1.axvline(sum(scores) / len(scores), color="red", linestyle="--", label=f"mean = {sum(scores) / len(scores):.2f}")
    ax1.legend()

    types = sorted(by_type)
    means = [sum(by_type[t]) / len(by_type[t]) for t in types]
    ax2.bar(types, means, color="#55A868", alpha=0.7, label="mean IVR")
    for i, t in enumerate(types):
        jitter = [i + (j % 5 - 2) * 0.03 for j in range(len(by_type[t]))]
        ax2.scatter(jitter, by_type[t], color="black", s=15, zorder=3, label="per-task IVR" if i == 0 else None)
    ax2.set_ylabel("IVR score")
    ax2.set_title("IVR by spec type")
    ax2.set_ylim(0, 1)
    ax2.legend()

    fig.suptitle(f"Intent Violation Rate — {results_path.name}")
    fig.tight_layout()

    out_path = results_path.parent / f"{results_path.stem}_ivr_distribution.png"
    fig.savefig(out_path, dpi=150)
    print(f"Saved plot to {out_path.relative_to(REPO_ROOT)}")
    plt.show()


if __name__ == "__main__":
    main()
