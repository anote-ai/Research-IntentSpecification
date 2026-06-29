# When AI Passes the Test but Misses the Point

## The problem in one sentence

Your AI coding assistant can write code that passes every test you gave it
and still do the wrong thing — because the tests never said what you actually
meant.

## A simple example

Ask an AI to "sort this list." It writes a function that sorts ascending.
Looks correct. But did you want:

- Duplicates preserved, or removed?
- The original list left untouched, or is mutating it in place fine?
- A new list returned, or is sorting in place acceptable?
- An empty list to return an empty list, or raise an error?

None of that was in your one-line request. The AI had to guess, and most
of the time you won't notice the guess was wrong until much later — your
tests passed, so everything *looked* fine.

We call this gap between "passes the tests" and "does what you meant"
**intent violation**. Our research project, IntentSpec, asks: how often
does this actually happen, and can we catch it before the code ships?

## Why this matters now

AI coding tools are graded today almost entirely on pass rates: did the
generated code pass the unit tests? That's a reasonable thing to measure,
but it has a blind spot. A test suite is itself a specification, and
specifications written in a hurry — "clean this dataset," "validate this
input," "sort this list" — are often ambiguous. An AI can satisfy the
letter of an ambiguous spec while violating its spirit, the same way a
clever student can "satisfy" a poorly worded exam question without
actually answering what the teacher meant.

As AI assistants take on more autonomous, multi-step coding work, this
distinction stops being a curiosity and starts being a real cost:
rework, debugging time, and trust erosion when "passing" code turns out
to be wrong code.

## What we're building

Two things, as described in our design doc:

1. **IntentBench** — a benchmark of specification pairs: a deliberately
   ambiguous version of a coding task next to a clarified "gold" version,
   with the implicit requirements that distinguish them spelled out as
   independently checkable tests (e.g., "does not mutate the input list").
2. **A Specification Quality Score (SQS)** — a way to flag, before any
   code is generated, that a specification is likely to be ambiguous
   enough to cause trouble, so a developer can fix the spec instead of
   debugging the consequences later.

We also want to measure the **Intent Violation Rate (IVR)**: of the
solutions that pass the stated tests, what fraction still violate at
least one of the implicit, "obvious" requirements a human would have
expected? Prior annotation work on a related benchmark (ARCADE) found
that roughly 45% of real-world data-science coding intents are
underspecified in this way. Whether that translates into a comparably
high IVR for generated *code* is exactly what this project sets out to
measure — it is a hypothesis we are testing, not yet a result we have.

## What we have today, honestly

This is an early-stage research project and we want to be straightforward
about where it stands relative to the design doc's full vision:

- We have a working, open-source evaluation library (`src/intentspec`)
  with a passing test suite. It scores the gap between *syntactic*
  correctness (did an agent call the right tool/function with sensible
  arguments?) and *intent alignment* (did the agent's stated rationale
  actually address the spec's constraints?) for **tool-use** tasks,
  using a small, hand-written synthetic dataset.
- That tool-use evaluator is a useful, runnable instrument, but it is
  **not yet** the code-generation IVR/SQS/IntentBench system the design
  doc describes. We have not yet: populated IntentBench with real
  specification pairs derived from HumanEval/MBPP/ARCADE, built the
  constraint-decomposition pipeline, run any LLM against it, or
  measured a real IVR number for generated code.
- Any IVR/SQS percentages that appear in the design doc (e.g. "22-44%
  of AI-generated code") are explicitly marked there as placeholder
  hypotheses inherited from an earlier draft, not measured results.

## What's next

We are prioritizing closing that gap: building a first slice of
IntentBench from existing coding benchmarks, running real models against
it, and reporting actual IVR numbers — good or bad — instead of
projected ones. See `experiments/exp1_ivr_by_type.py` in this repository
for a first runnable scaffold of that experiment, and
`PAPER_DRAFT.md` for the current state of the write-up.
