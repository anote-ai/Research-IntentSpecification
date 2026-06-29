# IntentSpec

[![CI](https://github.com/anote-ai/research-intentspecification/actions/workflows/ci.yml/badge.svg)](https://github.com/anote-ai/research-intentspecification/actions/workflows/ci.yml)
[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## Abstract

Syntactic benchmarks for LLM tool-use evaluate whether an agent selects the correct function name and argument keys — but they cannot detect when an agent produces a syntactically correct call that violates the user's actual intent. IntentSpec introduces a structured intent specification format and a dual-score evaluation protocol that separately measures *syntactic accuracy* and *intent alignment*, quantifying the divergence between the two.

This divergence metric reveals cases where syntactic evaluation overstates agent capability: an agent may match the expected tool call exactly while ignoring safety constraints, user preferences, or contextual success criteria. IntentSpec provides a lightweight, reproducible evaluation library that requires no external APIs and is designed to integrate into existing CI pipelines.

## Project status / scope note

This repository currently contains two related but distinct things, and we
want to be explicit about which is which:

1. **A shipped, tested tool-use evaluator** (`src/intentspec/`, this
   README, `scripts/run_eval.py`) — scores divergence between syntactic
   correctness and intent alignment for agentic *tool calls*, using simple
   rationale-substring matching against a small synthetic dataset. This is
   real, runnable code with passing tests.
2. **A broader code-generation research program** described in
   [`DESIGN_DOC.md`](DESIGN_DOC.md) — IntentBench, the Intent Violation
   Rate (IVR), the Specification Quality Score (SQS), an ambiguity
   detector, and a specification-drift model, aimed at measuring intent
   violation in AI-generated *code* (not tool calls), sourced from
   HumanEval/MBPP/ARCADE. **This program is not yet implemented at scale.**
   [`experiments/exp1_ivr_by_type.py`](experiments/exp1_ivr_by_type.py) is
   a first runnable scaffold (5 hand-authored spec pairs, no LLM calls) that
   validates the constraint-decomposition-to-IVR pipeline mechanically;
   see [`PAPER_DRAFT.md`](PAPER_DRAFT.md) for the current, honest state of
   that work and what is measured vs. projected.

If you are looking for the code-generation IVR/SQS/IntentBench system
described in the design doc, it does not exist yet beyond the small
scaffold above — see `PAPER_DRAFT.md` Section 6 for the prioritized list
of what is missing. For a plain-language summary of the overall research
direction, see [`BLOG.md`](BLOG.md).

## Why Intent Specification Matters

```
User Goal
    |
    v
+-------------------------+
| IntentSpec              |
|  goal: "..."            |
|  constraints: [...]     |
|  success_criteria: "..."|
|  ambiguity_level: 0.2   |
+-------------------------+
    |              |
    v              v
 Syntactic      Intent
  Score         Score
  (0..1)        (0..1)
    |              |
    +------+-------+
           |
           v
      Divergence
  (overstatement risk)
```

When `syntactic_score >> intent_score`, a syntactic-only benchmark would *overstate* agent quality. IntentSpec surfaces this gap.

## Quick Start

```bash
pip install -e ".[dev]"
python scripts/run_eval.py
```

```python
from intentspec.core import IntentSpec, ToolCall, IntentEvaluator

spec = IntentSpec(
    goal="Retrieve quarterly revenue data",
    constraints=["must use authorized data sources", "must return JSON"],
    success_criteria="returns structured data",
    ambiguity_level=0.1,
)

predicted = ToolCall(
    tool_name="query_database",
    arguments={"table": "revenue", "format": "json"},
    rationale="Using authorized data sources to return structured data as JSON",
)
reference = ToolCall(
    tool_name="query_database",
    arguments={"table": "revenue", "quarter": "Q1", "format": "json"},
)

evaluator = IntentEvaluator()
record = evaluator.evaluate(spec, predicted, reference)
print(f"intent={record.intent_score:.3f} syntactic={record.syntactic_score:.3f} divergence={record.divergence:.3f}")
```

## IntentSpec JSON Format

```json
{
  "goal": "Retrieve quarterly revenue data for analysis",
  "constraints": [
    "must use authorized data sources",
    "must return structured JSON output"
  ],
  "success_criteria": "returns structured data",
  "ambiguity_level": 0.2
}
```

## Evaluation Output Example

```
Evaluated 10 records.
  [0] intent=1.00 syntactic=1.00 divergence=0.000
  [1] intent=0.00 syntactic=0.25 divergence=0.250
  [2] intent=1.00 syntactic=1.00 divergence=0.000
  ...

Divergence Analysis:
  mean_intent: 0.500
  mean_syntactic: 0.625
  mean_divergence: 0.125
  max_divergence: 0.250
  overstatement_rate: 0.500
```

Note: the numbers in this specific example block are illustrative output
shapes from running `scripts/run_eval.py` against the synthetic dataset in
`src/intentspec/data.py` — not a claim about real LLM tool-use behavior.
Run the script yourself (`python scripts/run_eval.py`) to reproduce.

## Code-generation IVR scaffold

```bash
python experiments/exp1_ivr_by_type.py
```

Runs the constraint-decomposition / Intent Violation Rate pipeline from
`DESIGN_DOC.md` against 5 hand-authored algorithm specification pairs.
See `PAPER_DRAFT.md` Section 4 for what this does and does not demonstrate.

## Target Venues

- EACL 2027 (European Chapter of the ACL)
- AAAI 2027 Workshop on Enterprise AI Evaluation

## Citation

```bibtex
@misc{intentspec2026,
  title        = {IntentSpec: Beyond Syntactic Matching in LLM Tool-Use Evaluation},
  author       = {Anote AI Research},
  year         = {2026},
  howpublished = {\url{https://github.com/anote-ai/research-intentspecification}},
  note         = {Preprint}
}
```
