# IntentSpec: Measuring Intent Violation in AI-Generated Code Beyond Test-Pass Rate

*Draft — Anote AI Research. Status: early draft, scaffolding stage. Sections
marked "(projected, pending full experiment run)" describe planned
experiments from `DESIGN_DOC.md` that have not yet been executed at scale;
sections marked "(measured)" report numbers actually produced by code in
this repository.*

## Abstract

Code generation benchmarks such as HumanEval, MBPP, and BigCodeBench
evaluate functional correctness via test-pass rate, but pass rate cannot
detect when a generated solution satisfies the letter of an ambiguous
specification while violating the developer's actual intent. We introduce
**IntentSpec**, a framework for separating specification quality from code
correctness, built around three components: (1) a constraint-decomposition
protocol that turns a clarified "gold" specification into a set of
independently checkable atomic constraints, (2) the **Intent Violation
Rate (IVR)** — the fraction of test-passing solutions that fail at least
one decomposed gold constraint, and (3) a **Specification Quality Score
(SQS)** intended to predict IVR directly from specification text before
any code is generated. This draft documents the current state of the
project: a runnable constraint-decomposition and IVR-computation pipeline
for algorithm-style specifications (Section 4), a separate, already-shipped
tool-use evaluation library that measures a related but distinct
syntactic/intent divergence for agentic tool calls (Section 5), and a
concrete plan for the remaining experiments in `DESIGN_DOC.md` that have
not yet been run (Section 6).

## 1. Introduction

(See `DESIGN_DOC.md` for the full problem statement, related work
discussion, and novelty claims; this section will summarize that material
once Experiment 1 has been run on a non-trivial sample size. Not yet
written.)

## 2. The Specification Gap

Restating the core claims under audit:

- LLMs can produce solutions that pass stated tests while violating
  unstated but "obvious" developer expectations (specification gaming,
  edge-case ignoring, over-generalization, under-specification, wrong
  assumptions — see `DESIGN_DOC.md` § Violation Types).
- Pass rate and intent violation are claimed to be nearly uncorrelated
  (r ≈ 0.12 in the design doc's expected-results table). **This
  correlation has not yet been measured in this repository — it is a
  hypothesis carried over from the design doc, not a result.**

## 3. IntentBench (status: not yet populated)

`DESIGN_DOC.md` specifies IntentBench as TBD specification pairs sourced
from HumanEval/MBPP (algorithm specs) and ARCADE (data-transformation
specs), each with a gold clarified version and a constraint decomposition.

**Current state**: zero specification pairs exist in this repository.
`experiments/exp1_ivr_by_type.py` (added alongside this draft) ships a
small, hand-authored set of 5 algorithm-spec pairs (sorting, deduplication,
string-trimming, list-flattening, division-with-remainder) as a worked
example of the constraint-decomposition format, and computes IVR for a
handful of hand-written candidate solutions against them. This is meant to
validate the *mechanics* of the IVR pipeline end-to-end, not to stand in
for IntentBench itself — 5 examples is several orders of magnitude short
of a usable benchmark, and no LLM was called to generate the candidate
solutions (they were written directly, to keep this step free of API
dependencies and cost). Scaling this to real HumanEval/MBPP/ARCADE-derived
pairs with LLM-generated candidates is the immediate next step (Section 6).

## 4. IVR Computation: Implemented and Runnable

`experiments/exp1_ivr_by_type.py` implements the IVR definition from
`DESIGN_DOC.md` literally:

```
IVR = |{solutions passing original tests AND failing >=1 gold constraint}|
      / |{solutions passing original tests}|
```

Running it against the 5 worked examples and a handful of intentionally
varied candidate solutions per example (some "naive," some "careful")
produces a real, computed IVR — see the script's `__main__` output. This
number is **not** a claim about LLM behavior in general; it only
characterizes the specific hand-written candidate solutions included in
the script, and exists to prove the constraint-decomposition-to-IVR
pipeline is mechanically correct before spending API budget on LLM
generations.

**(measured, by running `experiments/exp1_ivr_by_type.py` in this repo on
2026-06-29)**: over the 5 hand-authored algorithm specs and their
hand-written candidate solutions (3 candidates for sort and dedupe, 2 each
for trim/flatten/divmod), 12 candidates were generated, 3 failed the
*stated* test outright, and of the 9 that passed the stated test, 3
violated at least one decomposed gold constraint while still passing —
**IVR = 0.333** for this toy candidate set. The violations were exactly
the ones the example was designed to surface: a sort that mutates the
input list in place (fails C3/C4), and two dedupe solutions that pass the
stated test (same *set* of elements) but silently reorder the output
(fails C2, "relative order of first occurrences preserved"). This is a
useful sanity check that the pipeline correctly distinguishes "passes
tests" from "respects intent," but 12 hand-written candidates is not a
sample anyone should generalize from.

## 5. The Shipped Tool-Use Evaluator (a related, narrower, already-built system)

Independently of the code-generation IVR/SQS work above, this repository
ships a complete, tested library (`src/intentspec/`) for a related but
distinct problem: scoring **agentic tool-use** calls along two axes —
*syntactic* correctness (right tool name, right argument keys) and
*intent alignment* (does the agent's rationale address the spec's stated
constraints) — and reporting the divergence between the two. This is the
system documented in the current `README.md`.

This is real, working code with a passing test suite (`tests/test_core.py`,
`tests/test_data.py`, `tests/test_evaluate.py`) and a runnable demo
(`scripts/run_eval.py`) against a small synthetic dataset
(`src/intentspec/data.py`). It is a reasonable, shippable artifact in its
own right, but it should not be confused with the IntentBench/IVR/SQS
code-generation research program in `DESIGN_DOC.md` — the constraint
matching there is substring-based rationale matching, not constraint
decomposition over executable tests, and the "specifications" are
tool-call specs, not code-generation specs. Reconciling these two strands
(or explicitly scoping the paper to one of them) is flagged as an open
question in Section 6.

## 6. Remaining Work Before This Is a Submittable Paper

The following are not yet done, in priority order:

1. **Scope decision**: decide whether the paper targets the tool-use
   divergence framing (README, already implemented) or the code-generation
   IVR/SQS/IntentBench framing (DESIGN_DOC.md, partially scaffolded by this
   draft) — currently the repository contains artifacts for both and they
   are not the same research project. *(open question, not implemented)*
2. **Populate IntentBench** with specification pairs derived from
   HumanEval/MBPP and ARCADE per the design doc's sourcing plan, at a
   sample size large enough to report a confidence interval on IVR.
   *(projected, pending full experiment run)*
3. **Run real LLMs** (GPT-4o, Claude) against IntentBench and compute IVR,
   SQS-IVR correlation, and ambiguity-detector precision/recall as specified
   in Experiments 1-3 of `DESIGN_DOC.md`. *(projected, pending full
   experiment run)*
4. **Human annotation pass** for SQS ground truth and ambiguity labels
   (Annotation Protocol, `DESIGN_DOC.md`). *(projected, pending full
   experiment run — requires recruiting annotators per the Open
   Questions & Risks table)*
5. **Re-baseline the design doc's "expected results" tables** — those
   numbers predate the constraint-based IVR redefinition and are marked
   TBD/placeholder in the design doc itself; they should not be cited as
   results anywhere, including in this draft.

## 7. Related Work

See `DESIGN_DOC.md` § Related Work for the current literature positioning
(HumanEval, MBPP, BigCodeBench, ARCADE, ClarifyGPT, Asuka-Bench, SWE-Bench
Pro, automated program repair patch-validity annotation). Not yet expanded
into full paper prose.
