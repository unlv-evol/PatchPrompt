# Annotation Policy Notes

This file documents how the annotation artifacts in this replication package should be interpreted relative to the paper.

## Dimensions Scored During Annotation

The original LLM annotation prompt requested four scores:

- Context (C)
- Specificity (S)
- Verification (V)
- Prompt Efficiency (E)

The final downstream analysis uses only Context, Specificity, and Verification. Prompt Efficiency was retained in some annotation artifacts for provenance, but excluded from modeling because the shared ChatGPT conversations do not reliably expose the full sequence of exploratory prompting that may have occurred before developers posted the interaction. As a result, turn count is not treated as a valid measure of actual prompt efficiency.

## Human and LLM Annotation Sources

The RQ1 reliability analysis uses:

- `Dataset_Construction/annotation/validation/human_gold_annotations.csv`: the stratified 30% human-consensus subset.
- `Dataset_Construction/annotation/validation/llm_annotations_v1_combined.csv`: the LLM V1 annotations for all records.

Only records appearing in both files are used for human--LLM agreement calculations.

## LLM Annotation Scope

The replication package treats LLM V1 as the canonical automated annotation source.

## Class-Aware Automation Policy

The final paper uses a class-aware annotation policy derived from agreement metrics and construct-validity judgment:

| Metric | PA | PN | CL | NE |
|---|---|---|---|---|
| Context | Human | Human | Human | Human |
| Specificity | Human | Human | LLM | LLM |
| Verification | Human | LLM | Human | Human |

This policy is reproduced in `RQ1_Prompt_Evaluation_Validation/results/rq1/rq1_annotation_policy.csv`.

## Rationale

Context is retained as human-scored because the LLM showed systematic under-scoring bias. Specificity is automated only for CL and NE, and retained as human-scored for PA and PN. Verification is automated only for PN cases, where explicit evaluation or rejection reasoning made correctness cues more observable; it remains human-scored for PA, CL, and NE due to instability and ambiguity.
