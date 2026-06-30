"""Dataset loading utilities for IntentSpec.

JSONL schema for data/specs/spec_pairs.jsonl — each line must be a JSON object:
{
  "task_id": "HE_001",                       // unique identifier
  "spec_type": "algorithm",                  // "algorithm" | "data_transformation"
  "ambiguous_prompt": "Sort a list.",        // what the developer actually wrote
  "gold_prompt": "Sort a list ascending ...",// explicit, fully-clarified version
  "constraints": [                           // all atomic constraints (stated + hidden)
    {
      "id": "C1",
      "description": "Output is sorted ascending",
      "test_code": "result = solution([3,1,2])\nassert result == [1,2,3]"
    }
  ],
  "stated_test_ids": ["C1"],                 // constraint ids present in ambiguous_prompt
  "hidden_test_ids": ["C2", "C3"]            // constraint ids only in gold_prompt (IVR target)
}
"""

from __future__ import annotations

import json
from pathlib import Path

from .schema import SpecPair


def load_humaneval_plus() -> list[dict]:
    """Load HumanEval+ entries via evalplus. Returns raw dicts keyed by task id."""
    try:
        from evalplus.data import get_human_eval_plus  # type: ignore[import]
    except ImportError as exc:
        raise ImportError(
            "evalplus is not installed. Run: pip install evalplus"
        ) from exc
    return list(get_human_eval_plus().values())


def load_spec_pairs(path: str | Path) -> list[SpecPair]:
    """Load SpecPair objects from a JSONL file (one JSON object per line)."""
    pairs: list[SpecPair] = []
    with open(path, encoding="utf-8") as f:
        for lineno, line in enumerate(f, 1):
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            try:
                d = json.loads(line)
            except json.JSONDecodeError as exc:
                raise ValueError(f"Invalid JSON on line {lineno} of {path}: {exc}") from exc
            pairs.append(SpecPair.model_validate(d))
    return pairs
