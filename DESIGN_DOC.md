# Research Design Document: Intent Specification

## Vision Statement

Solve the **specification gap** in AI-assisted software engineering: prove that current LLMs interpret ambiguous specifications in ways that satisfy test suites but violate developer intent in 25–40% of cases, and deliver **IntentBench** plus a **specification quality scorer** that enables developers to detect and resolve ambiguities before code is generated, reducing rework by ≥50%.

---

## Scope for EACL 2027 (deadlines: abstract Jul 21, paper Jul 28, code Jul 31)

**This section is the single source of truth for what's actually being attempted before submission. Everything below in this doc describes the full research vision; this section says what's real for this cycle.**

Target deadline is ~2 weeks out. A full benchmark-paper pipeline (large dataset, multi-turn drift study, developer RCT) is not achievable in that window — even the core scope below is aggressive and assumes no major blockers. Likely EACL 2027 track fit: main track as a short methodology paper given the specification-gaming/RSI framing (see RSI / Recursive Self-Improvement Connection), though this should be confirmed against the actual CFP track list once published, since track names can shift year to year.

**In scope (Phase 1 / core paper)**:
- Research Objectives 1–3 only (IVR baseline, SQS scorer, ambiguity detector + question selection)
- Two spec types: Algorithm + Data transformation (sourced from HumanEval/MBPP + ARCADE)
- A small IntentBench slice — realistically 20–40 spec pairs, not a large-scale benchmark; size is bounded by what can be authored/decomposed/annotated in ~1 week
- Experiments 1, 2, 3 only
- Statistical rigor scoped to what's meaningful at small N (bootstrap CIs, significance testing where powered; explicit caveat where it isn't)
- Ethics & Broader Impact and Related Work sections (writing-only, no added research time)
- Minimal artifact release (public repo, README, code + small dataset) — no Docker container or formal badge submission this cycle

**Explicitly deferred to future work (not in this submission)**:
- Experiment 4 (specification drift, multi-turn) — logistics- and annotation-heavy, demoted back to stretch goal
- Experiment 5 (clarification-first workflow user study) — requires developer recruitment, demoted back to stretch goal
- Adversarial/safety specification type and the real-issue-tracker mining pipeline for it — cut entirely for this cycle, not just descoped, since it requires a new sourcing pipeline with no existing infrastructure
- 3-seed LLM variance analysis — single-seed only this cycle, noted as a limitation
- Full artifact-evaluation badge submission, Docker reproducibility container
- Internal mock peer review (#18) — no runway before the deadline; move to a pre-camera-ready step if the paper is accepted, or do a lightweight internal-only pass if a reviewer is available in the final 2–3 days

**Honest risk flag**: even the "in scope" list above is tight for 2 weeks, and a 20–40 spec dataset is small for a benchmark claim — treat statistical results as a pilot/proof-of-concept, not a definitive large-N result, and frame the paper's contribution accordingly (the metric + constraint-decomposition methodology is the contribution; the numbers from this small a sample are illustrative). If Phase 1 scope turns out to be infeasible even at this size by ~July 8, the fallback is to submit to an EACL 2027 workshop or related NLP/ACL workshop or treat this cycle as a dry run for a later full submission rather than forcing a thin paper into the main track.

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

### Related Work Audit (anticipating reviewer objections)

| Work | Venue/Year | Approach to intent/spec | Evaluates spec gaming? | Key gap vs. IntentSpec |
| --- | --- | --- | --- | --- |
| HumanEval / MBPP | OpenAI 2021 / Google 2021 | Formal test cases per function | No | Test-pass rate only; no intent-quality measurement |
| BigCodeBench | 2024 | Broader test suites | No (notes ambiguity as noise) | Treats ambiguity as confound, not a measured object |
| ARCADE | Google 2023 | Natural-language data-science intents | No | Empirical underspecification evidence, no benchmark/metric |
| ClarifyGPT | 2023 | LLM-driven clarification questions | Partial | No standalone spec-quality metric |
| Asuka-Bench / SWE-Bench Pro | 2024–2025 | Human-in-the-loop clarification | Partial | Clarification embedded in pipeline, not isolated/reusable |
| Krakovna et al., specification gaming examples | DeepMind 2020 | RL agent reward-spec mismatch | Yes (foundational) | RL agents, not LLM code generation |
| Perez et al., reward hacking in code models | (verify exact citation before submission) | Reward-model/code-model misalignment | Yes | Model-training focus, not a spec-quality benchmark |
| CoNaLa / MBXP | 2018 / 2022 | Docstring-to-code | No | Functional correctness benchmarks, not intent-quality |
| NFR datasets (requirements engineering) | RE community | Non-functional requirement classification | No | Human-process RE, not LLM code-generation behavior |
| AmbigNQ | 2020 | Ambiguous question answering | No | QA domain, not code generation |

**Anticipated objection 1**: "Requirements engineering already studies specification ambiguity." Rebuttal: RE work targets human analyst processes for eliciting requirements from stakeholders; IntentSpec targets LLM behavior at code-generation time given a spec that's already been elicited — a different point in the pipeline with different failure modes (gaming a test suite vs. miscommunication between humans).

**Anticipated objection 2**: "Krakovna et al. already documented specification gaming." Rebuttal: those are RL agent examples (e.g., a boat racing agent looping for points instead of finishing the race); IntentSpec is the first to systematically apply the specification-gaming frame to LLM code generation with an executable, constraint-decomposed metric (IVR) rather than anecdotal examples.

> **TODO**: this table is a starting audit. Before submission: verify the Perez et al. citation; search AAAI/NeurIPS/ICML/ACL proceedings 2020–2025 for specification-gaming, alignment, and LLM-code-generation papers not yet listed; check whether ClarifyGPT has been superseded. The full `related_work_audit.md` per #17's deliverable spec is a post-submission background task (see Related Deliverables & Process Gates).

### Novel Contributions

| Contribution                    | Description                                                                                                      |
| ------------------------------- | ------------------------------------------------------------------------------------------------------------------ |
| **IntentBench**                 | TBD specification pairs: ambiguous original + clarified gold, with intent-violation labels                      |
| **SQS metric**                  | Specification Quality Score: measures precision, completeness, and unambiguity                                  |
| **IVR metric**                  | Intent Violation Rate: fraction of solutions satisfying tests but violating gold intent                          |
| **Ambiguity detector**          | LLM-based system that flags under-specified requirements and ranks them by expected information gain for asking |
| **Specification drift model**   | Characterization of how intent drifts across multi-turn coding interactions                                     |

### Key Metrics

```
IVR = solutions passing original tests and failing >= 1 decomposed gold constraint test / solutions passing original tests

where each gold spec is decomposed during dataset construction into independently checkable constraints (e.g., "preserves duplicates", "does not mutate input")

SQS = w1 × Precision_score + w2 × Completeness_score + w3 × Unambiguity_score

where scores are human-rated 0-1 per specification (serves a ground truth for initial training set)

Specification drift rate = cosine similarity across spec embeddings across turns
```

> **TODO**: SQS's protocol still describes pure human rating only. Add a line clarifying the two-stage plan: (1) human-rated scores as ground truth on an initial subset, (2) a learned model trained on that subset to predict SQS from text alone, consistent with what's described in Experiment 2.

---

## Research Objectives

1. Quantify **IVR** across specification types and programming domains: establish the baseline rate of intent violation.
2. Build a **Specification Quality Scorer** that predicts IVR from specification text (R² > 0.65) and a learned model can predict SQS from text.
3. Develop an **ambiguity detector** that identifies under-specified requirements with >80% precision via precision/recall against human-labeled ambiguity annotations, and ranks competing ambiguities by expected information gain so the highest-value clarifying question is asked first.

*Stretch goals (deferred — see Scope for EACL 2027)*:

4. Characterize **specification drift** across multi-turn interactions: how fast does intent drift, and what causes it?
5. Demonstrate that **clarification-first workflows** reduce IVR by ≥40% with <20% increase in developer effort.

---

## Dataset Construction

### Specification Types

Algorithm Specifications: self-contained input->output transformations over standard data structures (lists, strings, trees, etc) with no external state, I/O, or side effects. Restricting to pure functions makes constraint decomposition tractable, since correctness can be characterized by input/output.

Subtypes: sorting/ordering, searching/lookup, string manipulation, basic data structure operations. "Simple" is defined as a single function with ≤2-3 implicit constraints beyond those explicitly stated, solvable in under ~20 lines by a competent developer.

Data Transformation Specifications: Operations on structured/tabular data (e.g., Dataframes, JSON) involving cleaning, filtering, aggregation, etc.

Subtypes: missing value handling, type coercion/preservation, schema/column expectations, aggregation semantics.

| Type                          | Count  | Examples                                                         |
| ------------------------------ | ------ | ----------------------------------------------------------------- |
| Algorithm specifications      | 10–20  | "Sort this list efficiently" → ambiguous about stability, order |
| Data transformation specs     | 10–20  | "Clean this dataset" → ambiguous about NaN handling, types      |

> Adversarial/safety specifications (security boundary, idempotency, performance, backward-compat) are a natural extension of this work and motivate the `violation_types` taxonomy (see Violation Types), but are deferred from this submission cycle — see Scope for EACL 2027 above.

**Total: 20–40 specification pairs** for this submission cycle (constrained by ~1 week of annotation time; sourced from existing benchmarks to reduce construction time)

> **TODO**: finalize exact counts per type, and confirm whether IntentBench should be fully original or derived from existing benchmarks (see Dataset Sourcing below) — this also determines the complexity range of examples included.

### Dataset Sourcing

Rather than authoring TBD specifications fully from scratch, IntentBench will be derived from existing benchmarks where possible: algorithm specifications from HumanEval/MBPP (which already provide function-level specs and executable test infrastructure), and data transformation specifications from ARCADE (which provides empirically-grounded, naturally underspecified data science intents — ~45% of ARCADE intents are underspecified per prior annotation). For each sourced spec, we add: a gold clarified version, decomposed atomic constraints, and constraint-level tests. This reduces construction cost and improves comparability with prior benchmarks; specs not adequately covered by existing sources will be authored directly.

> The real-issue-tracker mining pipeline for adversarial/safety specifications is deferred — see Scope for EACL 2027. It remains a planned sourcing track for the post-submission IntentBench expansion (Phase 2) and is a direct response to issue #5 and #11.

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

> **TODO**: These numbers are placeholders — treat as directional hypotheses until re-baselined under constraint-based IVR on the actual 20–40 spec dataset. At this sample size, expect wide CIs; the table shape matters more than the exact values for the initial submission.

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

**Hypothesis**: An LLM-based ambiguity detector identifies under-specified requirements with >80% precision and >75% recall, and when multiple ambiguities are flagged for the same spec, ranking them by expected information gain surfaces the IVR-reducing question first more often than asking in detector-output order.

**Protocol**:

1. Build ambiguity detector: LLM prompted to identify specific ambiguities in specifications.
2. Evaluate against human-labeled ambiguity annotations.
3. Measure: precision, recall, F1; are detected ambiguities actionable (can developer resolve them)?
4. **Question selection**: when a spec has multiple flagged ambiguities, rank them by expected information gain — approximated as each ambiguity's marginal effect on IVR, estimated by the fraction of solutions in the constraint-decomposition data that fail specifically because of that missing constraint (a proxy for entropy reduction over plausible gold constraints, without requiring a full Bayesian model). This follows the framing in Ask-before-Plan / Active Task Disambiguation: clarification should be posed as which question reduces uncertainty most, not a generic "anything else?" prompt.
5. Test: does resolving detector-flagged ambiguities reduce IVR? Does asking in information-gain-ranked order reduce IVR faster (per question asked) than asking in arbitrary/detector-output order?

**Ground-truth ambiguity annotations**: derived directly from the constraint decomposition used for IVR (see Key Metrics). For each spec, the atomic constraints absent from the ambiguous original but present in the gold clarified version constitute the ground-truth ambiguities. A detector flag is a true positive if it corresponds to one of these missing constraint categories, a false positive if it flags something not in the constraint list, and a false negative if a missing constraint category is never flagged. This reuses dataset construction work already required for IVR rather than requiring a separate human-labeling pass for ambiguity specifically.

**Expected results**:

- Ambiguity detector: precision 0.82, recall 0.77, F1 = 0.79
- Resolving flagged ambiguities: IVR − 18 pp on resolved specs
- Information-gain-ranked question order reduces IVR per question asked by ~1.4x vs. arbitrary order on specs with ≥2 flagged ambiguities
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

### Experiments 4 & 5: Deferred Stretch Goals

> The following experiments were promoted to first-class status during the design doc rebuild, but are demoted back to explicit stretch goals given the July 15, 2026 EACL 2027 deadline — see Scope for EACL 2027. They remain in this doc as the planned post-submission Phase 2 work, not as items blocking submission.

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

## Statistical Rigor

EACL (ACL-family venues) expects confidence intervals and significance tests on benchmark claims. The following apply to Experiments 1–3; given the 20–40 spec dataset size this cycle, CIs will be wide and some tests will be underpowered — that should be stated as a limitation explicitly rather than hidden.

1. **Bootstrap confidence intervals**: 95% bootstrap CIs (10,000 resamples) for IVR, SQS-IVR R², and ambiguity detector P/R/F1 — resampled at the specification level (a spec's 5 solutions always resampled together). Report as `mean ± CI` in all results tables; wide CIs at small N are expected and should be disclosed.
2. **Significance testing for model comparisons**: paired bootstrap or Wilcoxon signed-rank for every model-vs-model comparison in Experiment 1; Bonferroni-correct across comparisons actually run, mark results with `†`. Note explicitly where N is too small to reach conventional power.
3. **Spec-type stratification**: report IVR and detector F1 separately for algorithm vs. data-transformation specs — this is the literal comparison Experiment 1's hypothesis tests, not an extra analysis.
4. **Human evaluation reliability**: Cohen's κ for the 2-annotator SQS + violation-type labeling; Wilson score CIs (not normal-approximation, which misbehave near 0/1) on any human-rated rate.

> **Deferred**: 3-seed LLM variance analysis — single seed only this cycle; noted as a limitation. Re-run with 3 seeds in the Phase 2 full-benchmark expansion.

> **Note on small-N framing**: at 20–40 specs the paper's claim is best framed as "proof-of-concept for the IVR/SQS framework with a pilot dataset" rather than a definitive large-scale benchmark result. This is honest and defensible for EACL if the methodology (constraint decomposition, IVR definition, detector design) is the primary contribution.

---

## Expected Results Summary

| Metric                      | Baseline | Best Result       | Key Finding                     |
| ---------------------------- | -------- | ------------------ | --------------------------------- |
| SQS-IVR R²                  | —        | 0.71              | SQS is valid quality gate       |
| Ambiguity detector F1       | —        | 0.79              | Actionable pre-generation check |
| Drift at turn 5             | +17 pp   | +7 pp (anchoring) | Drift is real but manageable    |
| Clarification workflow IVR  | 0.34     | 0.19              | −44% at only +14% time cost     |

**Primary claim**: Intent violation is distinct from test failure and affects 22–44% of AI-generated code depending on specification type; SQS and the ambiguity detector enable proactive mitigation before code generation.

> **TODO**: The 22–44% range is from the original 5-type, non-constraint-based IVR design. Update once re-baselined on the narrowed algorithm + data transformation scope.

---

## Why This Matters

**For researchers**: Intent specification is a fundamentally important and understudied problem in AI-SE research.

**For practitioners**: IVR provides a new KPI for AI coding tool evaluation; the ambiguity detector is immediately deployable in IDE integrations.

**For Anote products**: Integration into Anote's AI coding tools is a direct product improvement opportunity (see Related Deliverables & Process Gates, #13, for the scoped investigation plan).

### RSI / Recursive Self-Improvement Connection

Specification gaming in code generation — a model satisfying the stated tests while violating the gold intent — is a direct analog of the central unsolved problem in RSI safety: "what does 'improve yourself' actually mean, and how do you prevent the system from gaming that specification?" The failure modes are structurally identical; the stakes differ by orders of magnitude. Three of the existing `violation_types` (see Violation Types) map directly onto RSI-specific gaming patterns: `gaming` ↔ metric hacking (improving a benchmark score without improving underlying capability), `assumption_violation` ↔ evaluation capture (the system's unchecked assumption about what's being measured shifts in its own favor), and `under_specification`/`edge_case_ignore` ↔ scope narrowing (the system gradually restricts its objective to what it already does well rather than what was asked).

This connection motivates one concrete, scoped deliverable beyond the core IntentSpec pipeline: validate the ambiguity detector (Experiment 3) as a general-purpose **alignment monitor** — applying it not just to one-shot code specs, but at each iteration of a long-horizon agent loop, to flag when the agent's stated objective and its actual behavior are diverging. This is left as a follow-on validation (Phase 2, see Implementation Plan) rather than a core Phase 1 experiment, since it requires a simulated multi-iteration RSI loop as a test harness that doesn't yet exist; the core Phase 1 contribution is the taxonomy and detector themselves, built and validated on the code-generation IntentBench tasks.

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

**Note on scope**: the ambiguity detector and SQS scorer are built in Phase 1 as research instruments required to compute the framework's metrics (Objectives 2–3) and are evaluated with the same rigor as IVR itself. Phase 2 (post-paper) consists of productizing these same components into a standalone, documented library for external use, plus the one exception noted under RSI / Recursive Self-Improvement Connection: validating the ambiguity detector as an alignment monitor over a simulated multi-iteration agent loop, which is new evaluation work (not new detector implementation) deferred past the core paper.

---

## Artifact Release Plan

AAAI's reproducibility expectations are follows NeurIPS/ICML-style reproducibility expectations rather than ICSE/FSE/ASE artifact badges — no formal artifact-evaluation track with Available/Functional/Reusable badges. The goal for this cycle is minimal but honest: code and data publicly available at submission time, results reproducible from the README.

**This cycle (before July 15, 2026)**:
- Clean repo: remove debug prints, internal paths, credentials
- Public GitHub release with tagged commit matching paper submission
- `README.md`: install in ≤5 commands, reproduce core numbers in <15 minutes
- Pinned `requirements.txt`; `LICENSE` (Apache 2.0)
- The 20–40 spec IntentBench slice committed to the repo or released on HuggingFace Datasets (`anote-ai/intentspecification`)
- ACL reproducibility checklist completed and attached to submission

**Deferred to Phase 2 / post-acceptance**:
- Full dataset card, annotation-process documentation, inter-annotator agreement stats
- One-command `run_all.sh` reproducing every table
- Docker reproducibility container
- Framework-agnostic evaluation harness for external model evaluation
- Expanded IntentBench release covering the Phase 2 full-benchmark size

---

## Ethics & Broader Impact

> Statement outline per issue #16; full prose to be drafted closer to submission, but the dual-use risk below is load-bearing enough to flag now rather than late.

- **Intended use and benefits**: more faithful code generation from ambiguous specs reduces both developer rework and security vulnerabilities caused by models resolving ambiguity in unsafe ways (e.g., silently weakening an access check because the spec didn't say to keep it).
- **Alignment connection**: this work is alignment research in miniature — ensuring systems do what's intended, not just what's literally specified — and should be framed as a safety property of capability, not a separate add-on (see RSI / Recursive Self-Improvement Connection above).
- **Dual-use risk (the one that actually matters here)**: a system that's very good at inferring *implicit* developer intent could, in principle, infer that a stated safety constraint isn't what the user "really" wants, and route around it. Mitigation: scope all claims to alignment with stated developer intent *within* policy/safety constraints; explicitly distinguish "better intent inference" from "overriding constraints because intent was inferred to differ from them." This distinction should appear in the paper's limitations section, not just here.
- **Dataset bias**: IntentBench specs are sourced from HumanEval/MBPP/ARCADE plus mined GitHub issues (see Dataset Sourcing) — likely skews toward popular OSS languages/ecosystems and English-language issue text. Document this explicitly; do not claim cross-lingual or cross-cultural generalization without evidence.
- **Labor impact**: better intent-handling shifts more of the specification/design burden onto AI, with the human role moving toward higher-level intent articulation — net effect on junior-developer roles is genuinely uncertain and should be stated as such, not resolved rhetorically.
- **Environmental impact**: report CO2 estimates for all model evaluation runs (the 3-seed variance analysis from Statistical Rigor triples inference volume — factor that into the estimate).

> **TODO**: have a non-author with an AI-safety background review this section for the dual-use framing before submission, per #16's checklist.

---

## Timeline

**Target venue**: EACL 2027. Venue decided — closes issue #8.

| Phase | Target dates | Deliverable |
| --- | --- | --- |
| Dataset construction | Jun 30 – Jul 5 | 20–40 spec pairs authored/sourced (HumanEval/MBPP + ARCADE); constraints decomposed; constraint tests written |
| Detector + scorer dev | Jun 30 – Jul 5 | Ambiguity detector + SQS scorer implemented (parallel to dataset work) |
| Experiments 1–3 | Jul 6 – Jul 10 | IVR by spec type, SQS-IVR regression, ambiguity detector + question-selection eval; statistical analysis |
| Paper writing | Jul 11 – Jul 14 | Related work, ethics, framing, results tables; ACL reproducibility checklist |
| Buffer / submission | Jul 15 | Submit |

> Experiments 4 & 5 and adversarial spec type are not in this plan — see Scope for EACL 2027 and the deferred note before Experiment 4.

> **Post-submission (Phase 2)**: expand IntentBench to full scale, run adversarial/safety spec type with real issue-tracker mining, run 3-seed variance analysis, conduct developer user study, produce full artifact release — target a later venue (NeurIPS Datasets & Benchmarks, ACL Findings, or a future EACL/EMNLP cycle, depending on what Phase 1 reviewers flag).

**Workshop fallback**: if the core paper isn't sufficiently complete for EACL main track by July 8, pivot to a co-located EACL workshop where a shorter contribution is acceptable — a workshop paper still closes the cycle and generates reviewer feedback to improve the full-length version.

---

## Open Questions & Risks

| Risk                                       | Likelihood | Mitigation                                  |
| ------------------------------------------ | ---------- | ------------------------------------------- |
| 2-week timeline too tight for Experiments 1–3 | High   | If dataset construction slips past Jul 5, cut dataset size further (minimum viable: ~10 specs per type is enough to demonstrate the IVR/SQS framework exists; not enough for a strong claim, but enough for a workshop) |
| Small dataset N undermines statistical claims | High    | Frame as pilot/proof-of-concept explicitly; wide CIs are expected and should be disclosed, not hidden; methodology + constraint-decomposition framework is the contribution, not the point estimates |
| IVR construct validity                     | Medium     | Mitigated by tying IVR to executable constraint tests rather than holistic judgment; validate against a small human-rubric-rated subsample |
| Intent violation subjectivity              | High       | Detailed rubric + 2-annotator adjudication; report Cohen's κ |
| SQS inter-rater agreement                  | Medium     | 2 annotators; given small N this cycle, run pilot annotation on all specs rather than a 50-spec subset |
| LLM rate limits during experiment runs     | Low        | Batching + caching; budget for ~2 × 40 specs × 5 solutions = 400 LLM calls |
| EACL track framing                   | Medium     | EACL main track; frame as NL specification quality and ambiguity in code generation prompts (NLP framing), not as an SE empirical benchmark |

---

## Related Deliverables & Process Gates

These are separate deliverables that depend on this design doc but live outside it — tracked here so the doc stays the single source of truth for "what's planned" even though the artifacts themselves aren't markdown sections.

| Deliverable | Issue | Status / timing |
| --- | --- | --- |
| Paper draft (`PAPER_DRAFT.md`) | #7 | Due Jul 11–14 per Timeline sprint — gated on Experiment 1–3 results |
| Developer community blog post + specification-gaming gallery | #10 | Post-submission (needs real gaming examples from Experiment 1 results) |
| Marketing/virality strategy | #12 | Post-submission; after blog (#10) and public dataset sample exist |
| Product integration investigation (AI-Assisted-Coding-Tool) | #13 | Post-submission; gated on Experiment 3 (ambiguity detector) reaching stable P/R |
| Internal mock peer review | #18 | No pre-deadline runway; lightweight 1–2 person team pass on Jul 13–14 if anyone available; full external mock review targets post-submission for the next cycle |
| Related work audit (`related_work_audit.md`) | #17 | Inline in paper draft; full systematic survey of EACL/EMNLP/NAACL/ACL/NeurIPS/ICML alignment + code-gen literature is a post-submission background task |
