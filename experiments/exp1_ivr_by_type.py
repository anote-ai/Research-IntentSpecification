#!/usr/bin/env python3
"""Experiment 1 scaffold: Intent Violation Rate (IVR) by specification type.

This is a *mechanics* prototype, not a populated IntentBench. It implements
the IVR definition from DESIGN_DOC.md literally:

    IVR = |{solutions passing original tests AND failing >=1 gold
            constraint}| / |{solutions passing original tests}|

against a small, hand-authored set of "algorithm specification" pairs
(ambiguous original + decomposed gold constraints), each with a few
hand-written candidate solutions (no LLM calls, no external API
dependency, fully reproducible offline).

This intentionally does NOT claim to measure real LLM behavior or stand in
for IntentBench at scale -- see PAPER_DRAFT.md Section 4 for that caveat.
Its purpose is to prove the constraint-decomposition -> IVR computation
pipeline described in DESIGN_DOC.md is mechanically implementable and
runs end-to-end, so that scaling it up to real LLM-generated candidates
over HumanEval/MBPP/ARCADE-derived specs (DESIGN_DOC.md's actual sourcing
plan) is a data-population problem, not an unsolved design problem.

Run:
    python experiments/exp1_ivr_by_type.py
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, Any


@dataclass
class Constraint:
    """One atomic, independently-checkable requirement from a gold spec."""
    constraint_id: str
    description: str
    check: Callable[[Any, Any], bool]  # check(original_input, output) -> bool


@dataclass
class SpecPair:
    """An ambiguous original spec + its gold constraint decomposition."""
    name: str
    spec_type: str  # "algorithm" | "data_transformation"
    original_prompt: str
    original_test: Callable[[Any, Any], bool]  # the *stated* test only
    constraints: list[Constraint] = field(default_factory=list)
    sample_input: Any = None

    def passes_original_test(self, output: Any) -> bool:
        return self.original_test(self.sample_input, output)

    def failed_gold_constraints(self, output: Any) -> list[str]:
        failed = []
        for c in self.constraints:
            try:
                ok = c.check(self.sample_input, output)
            except Exception:
                ok = False
            if not ok:
                failed.append(c.constraint_id)
        return failed


# ---------------------------------------------------------------------------
# Worked example spec pairs (algorithm specifications)
# ---------------------------------------------------------------------------

def _sort_spec() -> SpecPair:
    return SpecPair(
        name="sort_list",
        spec_type="algorithm",
        original_prompt="Sort this list.",
        original_test=lambda inp, out: list(out) == sorted(inp),
        sample_input=[3, 1, 2, 1, 5],
        constraints=[
            Constraint("C1", "Output is sorted ascending",
                       lambda inp, out: list(out) == sorted(out)),
            Constraint("C2", "Duplicates preserved",
                       lambda inp, out: len(out) == len(inp)),
            Constraint("C3", "Input not mutated",
                       lambda inp, out: inp == [3, 1, 2, 1, 5]),
            Constraint("C4", "New list returned (not same object)",
                       lambda inp, out: out is not inp),
            Constraint("C5", "Empty input -> empty output",
                       lambda inp, out: True),  # not exercised by this sample input
        ],
    )


def _dedupe_spec() -> SpecPair:
    return SpecPair(
        name="dedupe_list",
        spec_type="algorithm",
        original_prompt="Remove duplicates from this list.",
        original_test=lambda inp, out: sorted(set(out)) == sorted(set(inp)),
        sample_input=[3, 1, 2, 2, 3, 1],
        constraints=[
            Constraint("C1", "No duplicate values in output",
                       lambda inp, out: len(out) == len(set(out))),
            Constraint("C2", "Relative order of first occurrences preserved",
                       lambda inp, out: list(out) == list(dict.fromkeys(inp))),
            Constraint("C3", "Input not mutated",
                       lambda inp, out: inp == [3, 1, 2, 2, 3, 1]),
        ],
    )


def _trim_strings_spec() -> SpecPair:
    return SpecPair(
        name="trim_strings",
        spec_type="algorithm",
        original_prompt="Clean up whitespace in this list of strings.",
        original_test=lambda inp, out: [s.strip() for s in inp] == [o.strip() for o in out],
        sample_input=["  A ", "B  ", " c"],
        constraints=[
            Constraint("C1", "Leading/trailing whitespace removed",
                       lambda inp, out: all(o == o.strip() for o in out)),
            Constraint("C2", "Internal whitespace untouched",
                       lambda inp, out: all(
                           a.strip() == b for a, b in zip(inp, out)
                       )),
            Constraint("C3", "Element count unchanged",
                       lambda inp, out: len(out) == len(inp)),
        ],
    )


def _flatten_spec() -> SpecPair:
    return SpecPair(
        name="flatten_list",
        spec_type="algorithm",
        original_prompt="Flatten this nested list.",
        original_test=lambda inp, out: sorted(out) == sorted(
            x for sub in inp for x in sub
        ),
        sample_input=[[1, 2], [3], [4, 5, 6]],
        constraints=[
            Constraint("C1", "Order preserved (left-to-right, depth-first)",
                       lambda inp, out: list(out) == [x for sub in inp for x in sub]),
            Constraint("C2", "Result is a flat list (no nested lists remain)",
                       lambda inp, out: all(not isinstance(x, list) for x in out)),
        ],
    )


def _divmod_spec() -> SpecPair:
    return SpecPair(
        name="divide_with_remainder",
        spec_type="algorithm",
        original_prompt="Divide a by b.",
        original_test=lambda inp, out: out[0] * inp[1] + out[1] == inp[0],
        sample_input=(17, 5),
        constraints=[
            Constraint("C1", "Quotient is integer floor division",
                       lambda inp, out: out[0] == inp[0] // inp[1]),
            Constraint("C2", "Remainder is non-negative and < divisor",
                       lambda inp, out: 0 <= out[1] < inp[1]),
            Constraint("C3", "Division by zero raises rather than crashing silently",
                       lambda inp, out: True),  # not exercised by this sample input
        ],
    )


ALGORITHM_SPECS: list[SpecPair] = [
    _sort_spec(), _dedupe_spec(), _trim_strings_spec(),
    _flatten_spec(), _divmod_spec(),
]


# ---------------------------------------------------------------------------
# Hand-written candidate solutions per spec (stand-ins for LLM generations)
# ---------------------------------------------------------------------------

CANDIDATE_SOLUTIONS: dict[str, list[Callable[[Any], Any]]] = {
    "sort_list": [
        lambda inp: sorted(inp),                       # careful: new list, correct
        lambda inp: sorted(set(inp)),                   # gaming: drops duplicates, still "sorted"
        lambda inp: inp.sort() or inp,                   # mutates input in place
    ],
    "dedupe_list": [
        lambda inp: list(dict.fromkeys(inp)),            # careful: preserves order
        lambda inp: sorted(set(inp)),                    # passes stated test, reorders
        lambda inp: list(set(inp)),                       # passes stated test, reorders
    ],
    "trim_strings": [
        lambda inp: [s.strip() for s in inp],             # careful
        lambda inp: [s.strip().lower() for s in inp],      # over-generalizes (also lowercases)
    ],
    "flatten_list": [
        lambda inp: [x for sub in inp for x in sub],       # careful, order-preserving
        lambda inp: sorted(x for sub in inp for x in sub),  # passes stated test, reorders
    ],
    "divide_with_remainder": [
        lambda inp: divmod(inp[0], inp[1]),                # careful
        lambda inp: (inp[0] // inp[1], inp[0] % inp[1] - inp[1]),  # passes stated test by luck of identity, fails C2
    ],
}


def run_experiment() -> dict:
    """Compute IVR per spec type over the worked examples above."""
    results_by_type: dict[str, list[bool]] = {}
    per_solution_rows = []

    for spec in ALGORITHM_SPECS:
        candidates = CANDIDATE_SOLUTIONS.get(spec.name, [])
        for fn in candidates:
            try:
                output = fn(spec.sample_input)
            except Exception as exc:
                per_solution_rows.append((spec.name, spec.spec_type, "ERROR", str(exc)))
                continue

            passed_original = spec.passes_original_test(output)
            if not passed_original:
                per_solution_rows.append((spec.name, spec.spec_type, "fails_original_test", output))
                continue

            failed_constraints = spec.failed_gold_constraints(output)
            violates_intent = len(failed_constraints) > 0
            results_by_type.setdefault(spec.spec_type, []).append(violates_intent)
            per_solution_rows.append((
                spec.name, spec.spec_type,
                "INTENT_VIOLATION:" + ",".join(failed_constraints) if violates_intent else "OK",
                output,
            ))

    ivr_by_type = {
        spec_type: sum(flags) / len(flags)
        for spec_type, flags in results_by_type.items()
        if flags
    }
    return {"ivr_by_type": ivr_by_type, "rows": per_solution_rows}


if __name__ == "__main__":
    result = run_experiment()
    print("Per-candidate-solution results:\n")
    for name, spec_type, status, output in result["rows"]:
        print(f"  [{spec_type:>18}] {name:<22} -> {status:<35} output={output!r}")

    print("\nIVR by specification type (over this toy candidate set only):")
    for spec_type, ivr in result["ivr_by_type"].items():
        print(f"  {spec_type}: IVR = {ivr:.3f}")

    print(
        "\nNOTE: this IVR is computed over a 5-spec, hand-written-candidate "
        "toy set for pipeline validation only. It is NOT a measurement of "
        "LLM behavior and is NOT a substitute for IntentBench at scale. "
        "See PAPER_DRAFT.md Section 4 for the caveat in full."
    )
