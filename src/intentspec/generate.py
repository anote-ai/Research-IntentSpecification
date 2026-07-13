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

# Map model name prefixes to provider. Extend this as needed.
_ANTHROPIC_PREFIXES = ("claude",)
_OPENAI_PREFIXES = ("gpt", "o1", "o3", "codex")


def _infer_provider(model: str) -> str:
    """Infer which API provider a model string belongs to."""
    lowered = model.lower()
    if any(lowered.startswith(p) for p in _ANTHROPIC_PREFIXES):
        return "anthropic"
    if any(lowered.startswith(p) for p in _OPENAI_PREFIXES):
        return "openai"
    raise ValueError(
        f"Could not infer provider for model '{model}'. "
        f"Expected a name starting with one of {_ANTHROPIC_PREFIXES + _OPENAI_PREFIXES}."
    )


def _clean_solution_code(raw: str) -> str:
    """Strip markdown code fences from LLM-generated code."""
    if "```" in raw:
        lines = raw.split("\n")
        lines = [line for line in lines if not line.strip().startswith("```")]
        return "\n".join(lines).strip()
    return raw.strip()


def _call_anthropic(prompt: str, model: str) -> str:
    try:
        import anthropic  # type: ignore[import]
    except ImportError as exc:
        raise ImportError(
            "anthropic is not installed. Run: pip install anthropic"
        ) from exc
    client = anthropic.Anthropic()
    message = client.messages.create(
        model=model,
        max_tokens=1024,
        messages=[{"role": "user", "content": prompt}],
    )
    return message.content[0].text  # type: ignore[union-attr]


def _call_openai(prompt: str, model: str) -> str:
    try:
        import openai  # type: ignore[import]
    except ImportError as exc:
        raise ImportError(
            "openai is not installed. Run: pip install openai"
        ) from exc
    client = openai.OpenAI()
    response = client.chat.completions.create(
        model=model,
        max_tokens=1024,
        messages=[{"role": "user", "content": prompt}],
    )
    content = response.choices[0].message.content
    if content is None:
        raise ValueError("OpenAI response contained no content")
    return content


_PROVIDER_DISPATCH = {
    "anthropic": _call_anthropic,
    "openai": _call_openai,
}


def generate_solutions(
    spec_pair: SpecPair,
    model: str = "claude-sonnet-4-6",
    n: int = 5,
    cache_dir: str | Path | None = None,
) -> list[str]:
    """Generate n solutions for spec_pair.ambiguous_prompt using the given model.

    Supports Anthropic (claude-*) and OpenAI (gpt-*, o1-*, o3-*, codex-*) models.
    Results are written to cache_dir/{model}__{task_id}.jsonl (one JSON object per line),
    so the same spec pair can be cached separately per model.
    If the cache file already contains >= n solutions, generation is skipped entirely.
    """
    provider = _infer_provider(model)
    call_fn = _PROVIDER_DISPATCH[provider]

    resolved_cache = Path(cache_dir) if cache_dir is not None else Path("data/generations")
    resolved_cache.mkdir(parents=True, exist_ok=True)

    safe_task_id = spec_pair.task_id.replace("/", "_")
    safe_model = model.replace("/", "_").replace(".", "_")
    cache_path = resolved_cache / f"{safe_model}__{safe_task_id}.jsonl"

    cached: list[str] = []
    if cache_path.exists():
        with open(cache_path, encoding="utf-8") as f:
            cached = [json.loads(line)["solution"] for line in f if line.strip()]
        if len(cached) >= n:
            return cached[:n]

    prompt = _PROMPT_TEMPLATE.format(prompt=spec_pair.ambiguous_prompt)
    solutions: list[str] = list(cached)
    remaining = n - len(solutions)

    with open(cache_path, "a", encoding="utf-8") as f:
        for _ in range(remaining):
            raw = call_fn(prompt, model)
            solution = _clean_solution_code(raw)
            solutions.append(solution)
            f.write(json.dumps({"solution": solution}) + "\n")

    return solutions
