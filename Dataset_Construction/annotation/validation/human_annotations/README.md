# Independent Human Annotation CSVs

This directory contains the independent, pre-reconciliation human annotations used
to compute human--human inter-rater agreement for RQ1.

Files are named as:

```text
human_annotation_<CATEGORY>_<ANNOTATOR>.csv
```

where `<CATEGORY>` is one of `CL`, `PN`, `PA`, or `NE`, and `<ANNOTATOR>` is
`richard` or `daniel`.

The agreement analysis script consumes these files and generates:

- `RQ1_Prompt_Evaluation_Validation/results/rq1/rq1_human_human_agreement_records.csv`
- `RQ1_Prompt_Evaluation_Validation/results/rq1/rq1_human_human_disagreements.csv`
- `RQ1_Prompt_Evaluation_Validation/results/rq1/rq1_human_human_agreement_metrics.csv`

Agreement was measured before discussion, reconciliation, or senior adjudication.
Human annotators were blinded to LLM-generated labels during annotation and
adjudication.
