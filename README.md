# IntentSpec

[![CI](https://github.com/anote-ai/research-intentspecification/actions/workflows/ci.yml/badge.svg)](https://github.com/anote-ai/research-intentspecification/actions/workflows/ci.yml)
![Python](https://img.shields.io/badge/python-3.10%20%7C%203.11-blue)
![License](https://img.shields.io/badge/license-MIT-green)

> **Intent Specification as a First-Class Evaluation Object for Tool-Calling Agents**

## Motivation

Existing tool-calling benchmarks measure **syntactic accuracy** — whether the model produces the correct tool name and parameter keys. This is necessary but insufficient: a model can produce a syntactically correct call while completely misunderstanding the user's intent, or satisfy the user's goal with a different-but-correct tool.

`intentspec` introduces *intent specification* as a first-class evaluation object, separating:

- **Intent-alignment score** — Does the agent's rationale and chosen tool satisfy the user's stated goal and constraints?
- **Syntactic score** — Does the tool call structurally match the reference?

By comparing both, we can detect the **divergence gap**: cases where syntactic accuracy overstates real reliability.

## Evaluation Framework

```
┌────────────────────────────────────────┐
│           IntentSpec                   │
│  goal, constraints, success_criteria   │
│  ambiguity_level                       │
└───────────────┬────────────────────────┘
                │
        ┌───────▼────────┐
        │  Agent Under   │
        │  Evaluation    │
        └───────┬────────┘
                │  ToolCall (tool_name, arguments, rationale)
     ┌──────────▼───────────┐
     │   IntentEvaluator    │
     │  ┌────────────────┐  │
     │  │ Intent Score   │  │  ← score_intent_alignment()
     │  └────────────────┘  │
     │  ┌────────────────┐  │
     │  │ Syntactic Score│  │  ← score_syntactic()
     │  └────────────────┘  │
     └──────────┬───────────┘
                │
        ┌───────▼────────┐
        │   EvalRecord   │
        │  + Divergence  │
        └────────────────┘
```

## Example Intent Spec

```json
{
  "goal": "Retrieve the current EUR/USD exchange rate",
  "constraints": [
    "Use a real-time data source",
    "Return rate as a float"
  ],
  "success_criteria": "A float exchange rate is returned within 200ms",
  "ambiguity_level": 0.1
}
```

## Divergence Analysis

The `compare_scores` function computes:

| Metric | Description |
|--------|-------------|
| `correlation` | Pearson correlation between intent and syntactic scores |
| `mean_divergence` | Average absolute difference per sample |
| `mean_intent` | Average intent-alignment score |
| `mean_syntactic` | Average syntactic score |

A high `mean_syntactic` with a high `mean_divergence` indicates that syntactic accuracy **overstates** real reliability.

## Quickstart

```bash
git clone https://github.com/anote-ai/research-intentspecification
cd research-intentspecification
pip install -e ".[dev]"
pytest tests/ -v
```

## Citation

```bibtex
@misc{anoteai2025intentspec,
  title        = {Intent Specification as a First-Class Evaluation Object for Tool-Calling Agents},
  author       = {Anote AI Research},
  year         = {2025},
  howpublished = {\url{https://github.com/anote-ai/research-intentspecification}},
}
```

## License

MIT
