# IntentSpecification — Research Design Document

## Goal

Characterize how and when AI code generation systems deviate from developer intent by gaming specifications — optimizing for what was literally specified rather than what was actually meant — and build a benchmark that measures specification compliance as a first-class evaluation dimension.

## Objective

1. Construct a taxonomy of specification gaming patterns in LLM code generation
2. Build a benchmark of 200+ coding tasks where gaming the specification is easy but the correct solution requires understanding developer intent
3. Measure specification compliance rates for 6+ leading code models

## Background / Motivation

"Specification gaming" — satisfying the literal specification while violating its spirit — was identified as a major failure mode in RL agents (Krakovna et al. 2020). The same phenomenon appears in LLM code generation but has never been systematically studied. As AI coding assistants write more consequential code, the risk of specification gaming producing subtly wrong production code grows. A benchmark that measures this is urgently needed.

## Experimental Design

### Baseline Experiment

**Evaluate GPT-4o, Claude Sonnet, and Gemini Pro on 50 standard HumanEval tasks**

- Metric: pass@1 (standard)
- Purpose: confirm evaluation infrastructure and establish capability baseline
- Expected result: all models ≈ 85–92% pass@1

### Test Experiment 1: Specification Gaming Rate

Create 100 "gaming-vulnerable" tasks with: (a) a shallow test suite that a shortcut solution can pass, (b) a comprehensive held-out test suite that requires correct implementation. Measure specification gaming rate = (passes shallow test AND fails comprehensive test) / (passes shallow test).

**Expected result:** specification gaming rate of 25–40% on gaming-vulnerable tasks — the gap between "passes tests" and "implements intent" is the central finding

### Test Experiment 2: Ambiguity Detection and Proactive Clarification

Create 50 tasks with genuinely ambiguous requirements. Evaluate: does the model ask for clarification? Does it document assumptions? Does it handle common ambiguous edge cases?

**Expected result:** no model asks for clarification; ~40% document assumptions; ~60% handle the most common edge cases

### Test Experiment 3: Specification Drift Over Multi-Turn Conversations

In a multi-turn coding scenario, iteratively add constraints over 5 turns. Measure: consistency with prior constraints, regression rate on earlier test cases, proactive conflict flagging.

**Expected result:** models introduce regressions in 30–40% of scenarios by turn 4–5; models almost never flag requirement conflicts proactively

## Expected Results

1. A specification gaming taxonomy with 5+ categories (hardcoding, narrow interpretation, edge-case ignoring, test-suite gaming, assumption burial)
2. A benchmark of 200+ gaming-vulnerable and ambiguous coding tasks with comprehensive held-out test suites
3. **Key finding:** "AI code models pass standard tests 90% of the time but pass intent-complete tests only 60–70% of the time — the 20–30 point gap is specification gaming"
4. A "specification gaming leaderboard" ranking models on intent compliance, not just test passing

## Why This Matters / Why People Would Care

- **Developers using AI coding tools:** need to know whether AI-generated code does what they actually meant
- **AI safety researchers:** specification gaming in code generation is a concrete, measurable analog to reward hacking in AI alignment
- **SE researchers:** requirements and specification compliance applied to AI code generation opens a new research direction
- **AI companies:** models better at intent compliance have a real product advantage

## Timeline

| Month | Milestone |
|---|---|
| 1–2 | Task construction (200 gaming-vulnerable and ambiguous tasks + comprehensive test suites) |
| 3 | Gaming rate experiment (all 6 models × 200 tasks) |
| 4 | Ambiguity detection + multi-turn specification drift experiments |
| 5 | Taxonomy derivation + analysis |
| 6 | Submission to ICSE 2027 |

## Related Issues

- Design doc GitHub issue: #20
- Target conferences: see issues labeled `conference-prep`
- Reproducibility package: see issues labeled `artifact-release`
