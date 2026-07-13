"""Validate benchmark soundness: run gold reference solutions against every
constraint (stated + hidden) for each spec pair and confirm IVR == 0.

Read-only validation. Never modifies specs, test_code, or canonicals.jsonl.
Gold references come only from gold_refs/<task_id>.py files or from
canonicals.jsonl (entry_point aliased to `solution`) -- never from an LLM.
"""

from __future__ import annotations

import json
import subprocess
import sys
import textwrap
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))

from intentspec.execute import run_solution  # noqa: E402

REPO_ROOT = Path(__file__).parent
SPEC_PAIRS_PATH = REPO_ROOT / "data" / "specs" / "spec_pairs.jsonl"
CANONICALS_PATH = REPO_ROOT / "data" / "specs" / "canonicals.jsonl"
GOLD_REFS_DIR = REPO_ROOT / "gold_refs"

TIMEOUT = 5.0


def load_jsonl(path: Path) -> list[dict]:
    records = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                records.append(json.loads(line))
    return records


def sanitize_task_id(task_id: str) -> str:
    return task_id.replace("/", "_")


def capture_failure_message(solution_code: str, test_code: str, timeout: float = TIMEOUT) -> str:
    """Re-runs the exact same subprocess mechanism as run_solution, but returns
    stderr so the assertion message can be reported. Only called when
    run_solution has already determined the constraint failed."""
    combined = textwrap.dedent(solution_code) + "\n\n" + textwrap.dedent(test_code) + "\n"
    try:
        result = subprocess.run(
            [sys.executable, "-c", combined],
            timeout=timeout,
            capture_output=True,
            text=True,
        )
        return result.stderr.strip()
    except subprocess.TimeoutExpired:
        return f"Timed out after {timeout}s"


def resolve_gold_reference(task_id: str, canonicals_by_id: dict[str, dict]) -> tuple[str | None, str]:
    """Returns (solution_code, source_label) or (None, reason) if unresolvable."""
    gold_ref_path = GOLD_REFS_DIR / f"{sanitize_task_id(task_id)}.py"
    if gold_ref_path.exists():
        return gold_ref_path.read_text(encoding="utf-8"), "gold_ref"

    canonical = canonicals_by_id.get(task_id)
    if canonical is None:
        return None, "MISSING_CANONICAL"

    solution_code = canonical["full_source"] + f"\nsolution = {canonical['entry_point']}\n"
    return solution_code, "canonical"


def main() -> None:
    spec_pairs = load_jsonl(SPEC_PAIRS_PATH)
    canonicals = load_jsonl(CANONICALS_PATH)
    canonicals_by_id = {c["task_id"]: c for c in canonicals}

    total = len(spec_pairs)
    sound: list[str] = []
    unsound: list[dict] = []
    missing_canonical: list[str] = []

    for spec in spec_pairs:
        task_id = spec["task_id"]
        solution_code, source = resolve_gold_reference(task_id, canonicals_by_id)

        if solution_code is None:
            missing_canonical.append(task_id)
            continue

        constraint_map = {ct["id"]: ct for ct in spec["constraints"]}
        all_ids = list(spec["stated_test_ids"]) + list(spec["hidden_test_ids"])

        failures = []
        for tid in all_ids:
            constraint = constraint_map.get(tid)
            if constraint is None:
                failures.append((tid, "CONSTRAINT_ID_NOT_FOUND", ""))
                continue
            passed = run_solution(solution_code, constraint["test_code"], timeout=TIMEOUT)
            if not passed:
                message = capture_failure_message(solution_code, constraint["test_code"])
                failures.append((tid, constraint["description"], message))

        if failures:
            unsound.append({
                "task_id": task_id,
                "source": source,
                "failures": failures,
            })
        else:
            sound.append(task_id)

    # --- Report ---
    print("=" * 70)
    print("BENCHMARK SOUNDNESS VALIDATION REPORT")
    print("=" * 70)
    print(f"Total specs:   {total}")
    print(f"SOUND:         {len(sound)}")
    print(f"UNSOUND:       {len(unsound)}")
    if missing_canonical:
        print(f"MISSING CANONICAL (skipped): {len(missing_canonical)}")
    print()

    if unsound:
        print("-" * 70)
        print("UNSOUND SPECS")
        print("-" * 70)
        for entry in unsound:
            print(f"\ntask_id: {entry['task_id']}  (source: {entry['source']})")
            for tid, desc, message in entry["failures"]:
                print(f"  [{tid}] {desc}")
                if message:
                    print(f"      {message}")

    needs_gold_ref = [e["task_id"] for e in unsound if e["source"] == "canonical"]
    print()
    print("-" * 70)
    print("NEEDS GOLD REFERENCE")
    print("-" * 70)
    if needs_gold_ref:
        for task_id in needs_gold_ref:
            print(f"  {task_id}")
    else:
        print("  (none)")

    if missing_canonical:
        print()
        print("-" * 70)
        print("MISSING CANONICALS (task_id in spec_pairs.jsonl but not in canonicals.jsonl)")
        print("-" * 70)
        for task_id in missing_canonical:
            print(f"  {task_id}")


if __name__ == "__main__":
    main()
