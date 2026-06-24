# Research Design Document: Intent Specification

## Vision Statement

Solve the **specification gap** in AI-assisted software engineering: prove that current LLMs interpret ambiguous specifications in ways that satisfy test suites but violate developer intent in 25–40% of cases, and deliver **IntentBench** plus a **specification quality scorer** that enables developers to detect and resolve ambiguities before code is generated, reducing rework by ≥50%.

---

## Problem Statement & Novelty

As AI coding assistants handle increasingly complex tasks, the quality of the natural language specification becomes the bottleneck. Ambiguous specifications lead to:

1. **Specification gaming**: LLMs find technically correct but intent-violating solutions (e.g., sorting by hardcoding expected outputs).
2. **Specification drift**: In multi-turn refinement, the LLM's understanding of the task drifts from the developer's intent across turns.
3. **Ambiguity blindness**: LLMs proceed confidently on underspecified tasks rather than requesting clarification.
4. **Silent intent violation**: Solutions pass all stated tests but fail on unstated but obvious developer expectations.

Existing work on NL→code focuses on correctness given the specification, not on the quality and precision of the specification itself.

## Related Work

Prior code generation benchmarks (HumanEval, MBPP, BigCodeBench) evaluate functional correctness via test pass rate but do not measure whether passing solutions reflect developer intent; BigCodeBench explicitly notes that ambiguous/underspecified specifications introduce evaluation noise in these benchmarks. ARCADE provides empirical evidence that a large fraction of real-world natural language coding intents are underspecified. ClarifyGPT explores LLM-driven clarification for code generation, and Asuka-Bench and SWE-Bench Pro both incorporate human-in-the-loop clarification of ambiguous tasks, though neither isolates a standalone, reusable specification-quality metric. Recent work on patch validity in automated program repair shows that rubric-based human annotation substantially improves inter-rater reliability over unstructured judgment — a finding that directly motivates our constraint-decomposition approach to IVR. IntentSpec/IntentBench differs from this prior work by treating specification quality as a first-class, independently measurable object rather than a byproduct of evaluating generated code.

### Novel Contributions

| Contribution                    | Description                                                                                |
| ------------------------------- | ------------------------------------------------------------------------------------------ |
| **IntentBench**                 | TBD specification pairs: ambiguous original + clarified gold, with intent-violation labels |
| **SQS metric**                  | Specification Quality Score: measures precision, completeness, and unambiguity             |
| **IVR metric**                  | Intent Violation Rate: fraction of solutions satisfying tests but violating gold intent    |
| **Ambiguity detector**          | LLM-based system that flags under-specified requirements and suggests clarifying questions |
| **\*Specification drift model** | Characterization of how intent drifts across multi-turn coding interactions                |

### Key Metrics

```
IVR = solutions passing original tests and failing >= 1 decomposed gold constraint test / solutions passing original tests

where each gold spec is decomposed during dataset construction into independently checkable constraints (e.g., "preserves duplicates", "does not mutate input")

SQS = w1 × Precision_score + w2 × Completeness_score + w3 × Unambiguity_score

where scores are human-rated 0-1 per specification (serves a ground truth for initial training set)

*Specification drift rate = cosine similarity across spec embeddings across turns
```

> **TODO**: SQS's protocol still describes pure human rating only. Add a line clarifying the two-stage plan: (1) human-rated scores as ground truth on an initial subset, (2) a learned model trained on that subset to predict SQS from text alone, consistent with what's described in Experiment 2.

---

## Research Objectives

1. Quantify **IVR** across specification types and programming domains: establish the baseline rate of intent violation.
2. Build a **Specification Quality Scorer** that predicts IVR from specification text (R² > 0.65) and a learned model can predict SQS from text.
3. Develop an **ambiguity detector** that identifies under-specified requirements with >80% precision via precision/recall against human-labeled ambiguity annotations
4. \*Characterize **specification drift** across multi-turn interactions: how fast does intent drift, and what causes it?
5. \*Demonstrate that **clarification-first workflows** reduce IVR by ≥40% with <20% increase in developer effort.

---

## Dataset Construction

### Specification Types

Algorithm Specifications: self-contained input->output transformations over standard data structures (lists, strings, trees, etc) with no external state, I/O, or side effects. Restricting to pure functions makes constraint decomposition tractable, since correctness can be characterized by input/output.

Subtypes: sorting/ordering, searching/lookup, string manipulation, basic data structure operations. "Simple" is defined as a single function with ≤2-3 implicit constraints beyond those explicitly stated, solvable in under ~20 lines by a competent developer.

Data Transformation Specifications: Operations on structured/tabular data (e.g., Dataframes, JSON) involving cleaning, filtering, aggregation, etc.

Subtypes: missing value handling, type coercion/preservation, schema/column expectations, aggregation semantics.

| Type                      | Count | Examples                                                        |
| ------------------------- | ----- | --------------------------------------------------------------- |
| Algorithm specifications  | TBD   | "Sort this list efficiently" → ambiguous about stability, order |
| Data transformation specs | TBD   | "Clean this dataset" → ambiguous about NaN handling, types      |

**Total: TBD specification pairs** (count depends on annotation bandwidth and whether specs are derived from existing benchmarks (ARCADE, HumanEval/MBPP) vs. authored from scratch)

> **TODO**: finalize exact counts per type, and confirm whether IntentBench should be fully original or derived from existing benchmarks (see Dataset Sourcing below) — this also determines the complexity range of examples included.

### Dataset Sourcing

Rather than authoring TBD specifications fully from scratch, IntentBench will be derived from existing benchmarks where possible: algorithm specifications from HumanEval/MBPP (which already provide function-level specs and executable test infrastructure), and data transformation specifications from ARCADE (which provides empirically-grounded, naturally underspecified data science intents — ~45% of ARCADE intents are underspecified per prior annotation). For each sourced spec, we add: a gold clarified version, decomposed atomic constraints, and constraint-level tests. This reduces construction cost and improves comparability with prior benchmarks; specs not adequately covered by existing sources will be authored directly.

### Annotation Protocol

```
For each ambiguous specification:
1. Developer writes original (intentionally underspecified)
2. Gold clarified version written by same developer (explicit, unambiguous)
3. LLM generates 5 solutions for the original spec
4. Human expert labels each solution: passes_tests, violates_gold_intent, violation_type
5. Specification Quality Score rated by 2 annotators on 3 dimensions
```

> **TODO**: Step 5 still describes pure human rating. Update to reflect the human-seed + learned-model plan for SQS (same gap noted under Key Metrics above).

### Constraint Decomposition (used for IVR, SQS, and Ambiguity Detector ground truth)

For each spec pair, the gold clarified version is broken into a list of atomic, independently-checkable constraints — the specific implicit requirements that distinguish it from the ambiguous original. Each constraint maps to one executable test isolating that requirement.

**Example** ("sort this list" → gold: "sort ascending, preserve duplicates, do not mutate input, return a new list, empty input returns empty output"):

| Constraint ID | Constraint                 | Test                                                |
| ------------- | -------------------------- | --------------------------------------------------- |
| C1            | Output is sorted ascending | Assert output is non-decreasing                     |
| C2            | Duplicates preserved       | Assert output length equals input length            |
| C3            | Input not mutated          | Assert input list unchanged after call              |
| C4            | New list returned          | Assert output is not the same object as input       |
| C5            | Empty input handled        | Assert empty list in → empty list out, no exception |

This constraint list is the single source of truth used across the framework: IVR checks generated solutions against it, SQS's completeness/unambiguity sub-scores are computed from it, and the ambiguity detector's ground truth is the set of constraints missing from the original spec.

### Violation Types

```yaml
violation_types:
  - gaming: 'Solution satisfies letter but not spirit of spec'
  - edge_case_ignore: 'Ignores unstated but obvious edge cases'
  - over_generalization: 'Solves a superset of the requested problem'
  - under_specification: 'Missing required functionality not in tests'
  - assumption_violation: 'Makes wrong assumption about unstated constraint'
```

---

## Systems Under Evaluation

| System                      | Model     | Clarification      | Notes             |
| --------------------------- | --------- | ------------------ | ----------------- |
| GPT-4o (zero-shot)          | OpenAI    | None               | Frontier baseline |
| Claude Sonnet 4 (zero-shot) | Anthropic | None               | Our primary       |
| Claude + clarification      | Anthropic | Ambiguity detector | Proposed approach |
| Codex (if available)        | OpenAI    | None               | Code-specialized  |
| Human developers            | —         | Self-directed      | Gold standard     |

---

## Experimental Design

### Experiment 1: IVR by Specification Type

**Hypothesis**: Data transformation specs have higher IVR than algorithm specs, because the former have more implicit conventions around missing data and schema.

**Protocol**:

1. Run GPT-4o and Claude zero-shot on all TBD specs.
2. Human expert rates each passing solution for intent violation.
3. Compute IVR per spec type.
4. Categorize violations by type (gaming/edge case/etc.).

**Expected results**:

| Spec Type           | GPT-4o pass@1 | GPT-4o IVR | Claude IVR |
| ------------------- | ------------- | ---------- | ---------- |
| Algorithm           | 0.85          | 0.22       | 0.20       |
| Data transformation | 0.82          | 0.31       | 0.28       |

> **TODO**: These numbers are inherited from the original 5-type design under the old holistic-judgment IVR definition. Treat as placeholders/directional hypotheses until re-baselined under constraint-based IVR.

- Key finding: pass@1 and IVR are nearly uncorrelated (r ≈ 0.12) — high pass rate does not mean low intent violation rate.

---

### Experiment 2: Specification Quality Score Validation

**Hypothesis**: SQS predicts IVR with R² > 0.65 (SQS is a useful pre-generation quality gate).

**Protocol**:

1. Compute SQS for all TBD specifications (human raters).
2. Compute IVR for same specifications.
3. Fit regression: IVR ~ f(SQS).
4. Cross-validate with 5-fold CV.

> **TODO**: Add a step distinguishing (a) human-rated SQS used to validate the IVR regression here, from (b) a separate, later validation of whether the learned SQS model (trained on the human-rated subset) also predicts IVR comparably well.

**Expected results**:

- SQS-IVR correlation: r ≈ −0.74 (higher quality spec → lower violation rate)
- Linear regression R²: 0.71
- Actionable threshold: SQS < 0.6 predicts IVR > 0.35 with 79% precision
- Key finding: SQS is a reliable pre-generation quality gate

> **TODO**: Same caveat as Experiment 1 — these expected values predate the constraint-based IVR redefinition and narrowed scope; treat as placeholders.

---

### Experiment 3: Ambiguity Detector

**Hypothesis**: An LLM-based ambiguity detector identifies under-specified requirements with >80% precision and >75% recall, enabling proactive clarification.

**Protocol**:

1. Build ambiguity detector: LLM prompted to identify specific ambiguities in specifications.
2. Evaluate against human-labeled ambiguity annotations.
3. Measure: precision, recall, F1; are detected ambiguities actionable (can developer resolve them)?
4. Test: does resolving detector-flagged ambiguities reduce IVR?

**Ground-truth ambiguity annotations**: derived directly from the constraint decomposition used for IVR (see Key Metrics). For each spec, the atomic constraints absent from the ambiguous original but present in the gold clarified version constitute the ground-truth ambiguities. A detector flag is a true positive if it corresponds to one of these missing constraint categories, a false positive if it flags something not in the constraint list, and a false negative if a missing constraint category is never flagged. This reuses dataset construction work already required for IVR rather than requiring a separate human-labeling pass for ambiguity specifically.

**Expected results**:

- Ambiguity detector: precision 0.82, recall 0.77, F1 = 0.79
- Resolving flagged ambiguities: IVR − 18 pp on resolved specs
- Actionability: 85% of detected ambiguities result in developer clarification within 2 min
- Most common detected ambiguities: edge case handling (38%), default values (29%), error handling (21%), type constraints (12%)

```python
# Ambiguity detector prompt structure
def detect_ambiguities(specification: str) -> list[Ambiguity]:
    prompt = f"""
    Analyze this software specification for ambiguities that could lead to incorrect implementations.
    For each ambiguity found, provide:
    1. The ambiguous phrase or requirement
    2. Multiple valid interpretations
    3. A clarifying question the developer should answer

    Specification: {specification}
    """
    # Returns structured list of ambiguities with clarifying questions
```

---

### Note: The following experiments are leftover from the suggested design doc provided. They are low priority currently (unless otherwise deemed) and will only be planned to be done if time allows or if scope takes us in this direction

### Experiment 4: Specification Drift in Multi-Turn Interactions

**Hypothesis**: In 5-turn coding interactions, intent violation rate at turn 5 is ≥15 pp higher than at turn 1, due to accumulated specification drift.

**Protocol**:

1. Construct 100 multi-turn coding tasks (5 turns each): initial spec → clarification → refinement → extension → bug fix.
2. At each turn, have human expert rate: does current solution still align with original intent?
3. Compute drift rate: how fast does intent alignment decay.

**Expected results**:

- Turn 1 IVR: 0.28
- Turn 3 IVR: 0.38 (+10 pp)
- Turn 5 IVR: 0.45 (+17 pp)
- Drift model: `IVR(k) = IVR(1) + α × log(k)` (α ≈ 0.09)
- Primary cause: LLM loses track of original constraints when new requirements are added
- Mitigation: anchoring to original specification in each turn's context reduces drift by 60%

---

### Experiment 5: Clarification-First Workflow

**Hypothesis**: A clarification-first workflow (detect ambiguities → ask developer → then generate) reduces IVR by ≥40% with <20% increase in developer effort (measured in time).

**Protocol**:

1. A/B test: 50 developers use standard workflow; 50 use clarification-first.
2. Measure: IVR of generated code, developer time per task, developer satisfaction.
3. Compare IVR reduction vs. time overhead.

**Expected results**:

- Standard workflow IVR: 0.34
- Clarification-first IVR: 0.19 (−44%)
- Developer time increase: +14% (2.3 min additional per task)
- Developer satisfaction: +28% (fewer back-and-forth cycles after generation)
- Key finding: 44% IVR reduction at 14% time cost is strongly positive ROI

---

## Expected Results Summary

| Metric                       | Baseline | Best Result       | Key Finding                     |
| ---------------------------- | -------- | ----------------- | ------------------------------- |
| SQS-IVR R²                   | —        | 0.71              | SQS is valid quality gate       |
| Ambiguity detector F1        | —        | 0.79              | Actionable pre-generation check |
| \*Drift at turn 5            | +17 pp   | +7 pp (anchoring) | Drift is real but manageable    |
| \*Clarification workflow IVR | 0.34     | 0.19              | −44% at only +14% time cost     |

**Primary claim**: Intent violation is distinct from test failure and affects 22–44% of AI-generated code depending on specification type; SQS and the ambiguity detector enable proactive mitigation before code generation.

> **TODO**: The 22–44% range is from the original 5-type, non-constraint-based IVR design. Update once re-baselined on the narrowed algorithm + data transformation scope.

---

## Why This Matters

**For researchers**: Intent specification is a fundamentally important and understudied problem in AI-SE research.

**For practitioners**: IVR provides a new KPI for AI coding tool evaluation; the ambiguity detector is immediately deployable in IDE integrations.

**For Anote products**: Integration into Anote's AI coding tools is a direct product improvement opportunity.

**RSI connection**: An AI that can detect and resolve specification ambiguities in its own task descriptions is a key RSI capability — self-directed task clarification before execution.

---

## Implementation Plan

```
research-intentspecification/
├── data/
│   ├── specifications/  # TBD spec pairs (ambiguous + gold)
│   ├── solutions/       # LLM-generated solutions
│   └── annotations/     # IVR labels, SQS scores
├── detector/
│   ├── ambiguity_detector.py
│   └── sqs_scorer.py
├── evaluation/
│   ├── ivr.py
│   └── drift_model.py
├── experiments/
│   ├── exp0_baseline.py
│   ├── exp1_ivr_by_type.py
│   ├── exp2_sqs_validation.py
│   ├── exp3_ambiguity_detector.py
│   ├── exp4_drift.py
│   └── exp5_workflow.py
```

**Note on scope**: the ambiguity detector and SQS scorer are built in Phase 1 as research instruments required to compute the framework's metrics (Objectives 2–3) and are evaluated with the same rigor as IVR itself. Phase 2 (post-paper) consists only of productizing these same components into a standalone, documented library for external use — not new implementation work.

---

## Timeline

> **TODO**: This timeline and target venue are unchanged from the original ICSE/FSE-oriented plan. Needs to be rebuilt around EACL 2027 or AAAI 2027

| Phase                | Duration | Deliverable                     |
| -------------------- | -------- | ------------------------------- |
| Dataset construction | 8 weeks  | TBD spec pairs with annotations |
| Detector development | 4 weeks  | Ambiguity detector + SQS scorer |
| Experiments          | 5 weeks  | All results                     |
| User study (Exp 5)   | 3 weeks  | A/B workflow comparison         |
| Paper writing        | 4 weeks  | ICSE 2027 submission            |

**Target venue**: ICSE 2027 or FSE 2027

---

## Open Questions & Risks

> **TODO**: Add a row for IVR construct validity — the risk that IVR may not be reliably measurable without costly annotation, mitigated by tying IVR to executable constraint tests rather than holistic judgment, validated against a small human-rubric-rated sample before scaling.

| Risk                                       | Likelihood | Mitigation                                  |
| ------------------------------------------ | ---------- | ------------------------------------------- |
| Developer recruitment for user study       | Medium     | University CS departments; MTurk developers |
| Intent violation subjectivity              | High       | Detailed rubric + 2-annotator adjudication  |
| SQS inter-rater agreement                  | Medium     | Pilot on 50 specs before full annotation    |
| LLM rate limits for large-scale generation | Low        | Batching + caching                          |

---

## Related Issues

- Product integration: AI coding tools ambiguity detection
- Related work audit: NL4SE, GitHub Copilot evaluation papers
- Reproducibility: human study IRB approval
- CodeBench connection: specification gaming is related to IVR
