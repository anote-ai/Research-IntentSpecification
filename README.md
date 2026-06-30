# IntentSpec

[![CI](https://github.com/anote-ai/research-intentspecification/actions/workflows/ci.yml/badge.svg)](https://github.com/anote-ai/research-intentspecification/actions/workflows/ci.yml)
[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## Abstract

IntentSpec introduces **Intent Violation Rate (IVR)**: a metric that measures how often LLM-generated code passes the tests a developer explicitly stated while failing hidden gold-constraint tests derived from a fully-clarified version of the same specification. Given an ambiguous prompt, a gold clarified prompt, and a set of atomic constraint tests (some stated, some hidden), IVR is the fraction of solutions that satisfy the stated tests yet violate at least one hidden constraint — quantifying the gap between test-pass rate and true developer intent. The pipeline generates solutions via the Anthropic API, executes each candidate against stated and hidden tests in a sandboxed subprocess, and reports IVR overall and by specification type (algorithm vs. data transformation).

## Quick Start

```bash
pip install -e ".[dev]"
# set ANTHROPIC_API_KEY in your environment
python scripts/run_experiment1.py
```

## Pipeline

```
data/specs/spec_pairs.jsonl          ANTHROPIC_API_KEY
        |                                   |
        v                                   v
  load_spec_pairs()          generate_solutions() → data/generations/{task_id}.jsonl
        |                                   |
        +------------------+----------------+
                           |
                           v
                  evaluate_solution()      ← subprocess execution, 5s timeout
                    (stated tests + hidden constraint tests)
                           |
                           v
                    compute_ivr()          ← IVR = violating / passing_stated
                    compute_ivr_by_type()
                           |
                           v
                  results/experiment1.json
```

## JSONL Schema (`data/specs/spec_pairs.jsonl`)

```json
{
  "task_id": "HE_001",
  "spec_type": "algorithm",
  "ambiguous_prompt": "Sort a list.",
  "gold_prompt": "Sort ascending, preserve duplicates, do not mutate input, handle empty.",
  "constraints": [
    {"id": "C1", "description": "Sorted ascending", "test_code": "assert solution([2,1])==[1,2]"},
    {"id": "C2", "description": "No mutation",      "test_code": "inp=[2,1];solution(inp);assert inp==[2,1]"}
  ],
  "stated_test_ids": ["C1"],
  "hidden_test_ids": ["C2"]
}
```

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
