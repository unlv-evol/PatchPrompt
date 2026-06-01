# PatchTrack-Prompt Dimension Definitions

This file summarizes the prompt-quality dimensions used in the replication package. The full operational LLM prompt is available in `llm_annotation_prompt_full.md`.

## Context (C: 0--2)

Context measures whether the developer prompt is grounded in concrete technical artifacts or execution details.

- **2**: Explicit locus of change and concrete evidence are both present, such as a file path, function/API name, code snippet, YAML fragment, error log, or environment detail.
- **1**: Partial grounding is present, meaning either a technical locus or supporting evidence is provided, but not both.
- **0**: No concrete locus or evidence is provided; the prompt is generic.

## Specificity (S: 0--2)

Specificity measures whether the prompt clearly defines the intended goal, scope, and constraints.

- **2**: The prompt includes an explicit goal, bounded scope, and constraints such as expected input/output, rules, invariants, output format, type signature, or reasoning instructions.
- **1**: The prompt has a clear goal but incomplete scope or constraints.
- **0**: The prompt is vague, broad, or underspecified.

## Verification (V: 0--2)

Verification measures whether the prompt defines, implies, or enables correctness checking.

- **2**: The prompt contains explicit correctness criteria, such as test-like expectations, input/output examples, behavioral rules, type/static constraints, or documented policy requirements.
- **1**: The prompt contains implicit correctness cues, such as maintaining API stability, preserving existing behavior, producing valid syntax, or avoiding regressions.
- **0**: The prompt contains no correctness cues.

## Prompt Efficiency (E: 0--5)

Prompt Efficiency was included in the original annotation prompt but excluded from downstream analysis because posted conversations may omit earlier exploratory turns. The score is preserved only as provenance when available.

## Downstream Use

The modeling pipeline uses C, S, and V as separate predictors and computes Prompt Quality Score as:

```text
PQS = Context + Specificity + Verification
```

PQS is used for descriptive statistics and sensitivity analyses, while the main models use the individual dimensions to preserve interpretability.
