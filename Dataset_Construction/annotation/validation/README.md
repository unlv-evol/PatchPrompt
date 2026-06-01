# Annotation Validation Artifacts

This directory contains the human and LLM annotation artifacts used to reproduce
RQ1: Reliability of LLM-Based Prompt Annotation.

## Included artifacts

- `human_gold_annotations.csv`: the 30% stratified human-annotated gold-standard subset.
- `llm_annotations_v1_combined.csv`: the combined LLM V1 annotations across PA, PN, NE, and CL cases.
- `agreement_checks.py`: helper script for agreement validation checks.
- `adjudication_notes.md`: notes on human adjudication and consensus handling.

## LLM annotation versions

Only LLM V1 annotation outputs were used for the agreement analyses, class-conditioned
kappa results, annotation-policy derivation, and downstream validation reported in the
paper.

## Relationship to paper results

These files reproduce the Section 4.1 results, including:

- overall quadratic weighted Cohen's kappa, MAE, and directional bias;
- outcome-conditioned agreement by PA, PN, NE, and CL;
- the class-aware annotation policy used for the final dataset.
