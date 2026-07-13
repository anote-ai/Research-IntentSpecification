# IntentSpec

[![CI](https://github.com/anote-ai/research-intentspecification/actions/workflows/ci.yml/badge.svg)](https://github.com/anote-ai/research-intentspecification/actions/workflows/ci.yml)
[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## Overview

IntentSpec introduces **Intent Violation Rate (IVR)**: a metric measuring how
often LLM-generated code passes the tests a developer explicitly stated while
violating unstated developer intent captured by hidden gold-constraint tests.

This repository contains:

- **A benchmark of 49 algorithm spec pairs** derived from HumanEval+
  (`data/specs/spec_pairs.jsonl`), each with:
  - an **ambiguous prompt** (what a developer might actually write),
  - a **gold prompt** (the fully-clarified version),
  - a stated test (**C1**), and
  - 1–3 hidden constraint tests (**C2–C4**) that only the gold prompt implies.
- **Canonical reference solutions** (`data/specs/canonicals.jsonl`) used to
  validate that the benchmark itself is sound (see
  [Validating the Benchmark](#validating-the-benchmark)).
- **A pipeline** that generates candidate solutions with the Anthropic API,
  executes each one against the stated and hidden tests in a sandboxed
  subprocess, and computes IVR overall and by specification type.

IVR for a spec pair is the fraction of solutions that pass the stated test(s)
yet fail at least one hidden constraint:

```
IVR = n_violating / n_passing_stated
```

## Requirements & Installation

- Python 3.10 or 3.11

```bash
pip install -e ".[dev]"
```

This installs the `intentspec` package plus its runtime dependencies
(`anthropic`, `evalplus`, `pydantic`, `numpy`, `pandas`, `rich`, `matplotlib`)
and dev tools (`pytest`, `ruff`, `mypy`) declared in `pyproject.toml`.

## API Key Setup

> **Generation requires `ANTHROPIC_API_KEY` to be set in your environment.**
> `scripts/run_experiment1.py` will fail as soon as it needs to call the
> Anthropic API if this is not set. It is **not required** if you only run
> against the cached generations already committed to this repo (see below).

```bash
export ANTHROPIC_API_KEY=sk-ant-XXX
```

## Repository Structure

```
data/
  specs/
    spec_pairs.jsonl          # 49 spec pairs (ambiguous/gold prompts + constraint tests)
    canonicals.jsonl          # canonical reference solutions, keyed by task_id
  generations/                # cached LLM solutions, one file per model/task_id
src/intentspec/
  schema.py                   # SpecPair, ConstraintTest, SolutionResult, IVRResult (pydantic)
  dataset.py                  # load_spec_pairs(), load_humaneval_plus()
  generate.py                 # generate_solutions() — calls Anthropic/OpenAI, caches to disk
  execute.py                  # run_solution(), evaluate_solution() — sandboxed subprocess exec
  ivr.py                      # compute_ivr(), compute_ivr_by_type()
scripts/
  run_experiment1.py          # main entry point: generate -> evaluate -> compute IVR
  validate_benchmark.py       # soundness check: canonical solutions vs. all constraint tests
  plot_ivr_distribution.py    # histogram of per-task IVR from a results file
  flatten_specs.py            # maintenance utility: dedupe spec_pairs.jsonl by task_id
results/
  experiment1.json            # full results from the last run_experiment1.py run
  experiment1_ivr_distribution.png
tests/                        # unit tests for schema/dataset/execute/ivr
```

## Reproducing the Results

```bash
pip install -e ".[dev]"
python scripts/run_experiment1.py
```

`run_experiment1.py` takes no arguments. It loads all 49 spec pairs from
`data/specs/spec_pairs.jsonl`, generates 5 solutions per spec pair with
`claude-sonnet-4-6`, evaluates each solution against its stated and hidden
constraint tests, prints per-task and overall IVR, and writes full results to
`results/experiment1.json`.

**This repository ships with the cached generations used for the paper**
(`data/generations/claude-sonnet-4-6__<task_id>.jsonl`, 5 solutions per task).
`generate_solutions()` checks this cache before calling the API: if a cache
file already has ≥5 solutions for a task, generation is skipped entirely and
the cached solutions are reused.

- **Running against the committed cache (default) reproduces the paper's
  reported IVR of 54.5% exactly**, and does not require `ANTHROPIC_API_KEY`.
- **If you delete or empty `data/generations/`, generation will run fresh**
  against the Anthropic API. Fresh generation calls the API at its default
  temperature (1.0, nondeterministic) — a fresh run will **not** reproduce
  54.5% exactly, since it draws a different sample of completions each time.

To force fresh generation for reproducibility experiments of your own:

```bash
rm -rf data/generations
export ANTHROPIC_API_KEY=sk-ant-...
python scripts/run_experiment1.py
```

## Validating the Benchmark

```bash
python scripts/validate_benchmark.py
```

Takes no arguments. For every spec pair, it resolves a gold reference
solution — from `gold_refs/<task_id>.py` if present, otherwise from
`canonicals.jsonl` (aliasing `entry_point` to `solution`) — and runs it
against every constraint test (stated **and** hidden). It confirms that
correct, canonical solutions pass all constraints (IVR = 0 across all specs),
which shows the hidden tests are satisfiable by correct code rather than
being spuriously unsatisfiable or contradictory. It never modifies specs,
test code, or `canonicals.jsonl`.

## Expected Output

Running `python scripts/run_experiment1.py` against the committed cache
prints one line per spec pair, e.g.:

```
[HumanEval/26] (algorithm) Generating 5 solutions...
  Solution 1: stated=PASS, hidden_failed=1/2 (['C2'])
  ...

--- IVR Results ---
  HumanEval/26: IVR=0.400 (2/5 passing-stated solutions violate >= 1 hidden constraint)
  ...

Overall IVR (mean across tasks with >= 1 passing-stated solution): 0.545

IVR by spec type:
  algorithm: 0.545

Full results saved to results/experiment1.json
```

- **Overall IVR ≈ 0.545** (54.5%), averaged over the **47** of 49 spec pairs
  that had at least one solution pass the stated test. The other **2**
  (`HumanEval/101`, `HumanEval/112`) had zero solutions pass their stated
  test in any of the 5 samples and are excluded from the mean, since IVR is
  undefined without at least one stated-passing solution.
- All 49 spec pairs are `spec_type = "algorithm"` in this release, so the
  by-type breakdown currently has a single entry equal to the overall IVR.
- `results/experiment1.json` records, per task and per solution, whether the
  stated test passed and which hidden constraint IDs (C2/C3/C4) passed or
  failed. From this you can derive per-constraint fail rates; for the
  committed cache, out of 231 stated-passing solutions: C2 fails 42.9% of the
  time, C3 25.1%, C4 4.3%.
- `python scripts/plot_ivr_distribution.py [results/experiment1.json]`
  (results file argument optional, defaults to `results/experiment1.json`)
  renders this as a histogram, saved as `<name>_ivr_distribution.png` next to
  the input file.

## Target Venue

EACL 2027 main track (short methodology paper).

## Citation

```bibtex
@misc{intentspec2026,
  title        = {IntentSpec: Measuring Intent Violation Rate in LLM Code Generation},
  author       = {Anote AI Research},
  year         = {2026},
  howpublished = {\url{https://github.com/anote-ai/research-intentspecification}},
  note         = {Preprint}
}
```
