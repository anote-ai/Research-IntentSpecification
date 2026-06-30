from __future__ import annotations

import json
from pathlib import Path

from .schema import SpecPair

_PROMPT_TEMPLATE = """\
Write a Python function named `solution` that solves the following task.

{prompt}

Requirements:
- Name the function exactly `solution`.
- Return only the function definition — no explanation, no markdown, no imports unless the function itself needs them.
"""


def generate_solutions(
    spec_pair: SpecPair,
    model: str = "claude-sonnet-4-6",
    n: int = 5,
    cache_dir: str | Path | None = None,
) -> list[str]:
    """Generate n solutions for spec_pair.ambiguous_prompt using the Anthropic API.

    Results are written to cache_dir/{task_id}.jsonl (one JSON object per line).
    If the cache file already contains >= n solutions, generation is skipped entirely.
    """
    try:
        import anthropic  # type: ignore[import]
    except ImportError as exc:
        raise ImportError(
            "anthropic is not installed. Run: pip install anthropic"
        ) from exc

    resolved_cache = Path(cache_dir) if cache_dir is not None else Path("data/generations")
    resolved_cache.mkdir(parents=True, exist_ok=True)
    cache_path = resolved_cache / f"{spec_pair.task_id}.jsonl"

    cached: list[str] = []
    if cache_path.exists():
        with open(cache_path, encoding="utf-8") as f:
            cached = [json.loads(line)["solution"] for line in f if line.strip()]
        if len(cached) >= n:
            return cached[:n]

    client = anthropic.Anthropic()
    prompt = _PROMPT_TEMPLATE.format(prompt=spec_pair.ambiguous_prompt)

    solutions: list[str] = list(cached)
    remaining = n - len(solutions)

    with open(cache_path, "a", encoding="utf-8") as f:
        for _ in range(remaining):
            message = client.messages.create(
                model=model,
                max_tokens=1024,
                messages=[{"role": "user", "content": prompt}],
            )
            solution: str = message.content[0].text  # type: ignore[union-attr]
            solutions.append(solution)
            f.write(json.dumps({"solution": solution}) + "\n")

    return solutions
