# Reproduction Steps

This package uses the command-line pipeline as the canonical reproduction path. Notebooks are explanatory companions and should reproduce the same files when run from the repository root.

## Full reproduction

```bash
python3.11 -m pip install -r requirements-lock.txt
make PYTHON=python3.11 reproduce
make PYTHON=python3.11 verify
```

The full run performs preprocessing, RQ1 annotation-reliability analysis, descriptive statistics, table generation, model fitting, diagnostics, qualitative summaries, figure generation, manifest generation, and output verification.

For a fully fresh run from scratch:

```bash
make clean
make PYTHON=python3.11 reproduce
make PYTHON=python3.11 verify
```

## Smoke reproduction

```bash
make PYTHON=python3.11 smoke
```

Smoke mode uses the same contract but is intended for a quick artifact-evaluation pass.
The Makefile enforces a supported interpreter range (Python 3.9 to 3.12) and exits with a hint when the selected Python version is outside that range.
Smoke mode intentionally skips methodological-alignment sensitivity artifacts to reduce runtime.

## Main pipeline stages

The canonical orchestration is implemented in `replication/reproduce_all.py` and described in `replication/pipeline_manifest.yaml`.

1. **Prepare derived datasets** from `Dataset_Construction/processed_data/final_analysis_dataset.csv` without modifying the canonical dataset.
2. **Reproduce RQ1 annotation reliability** from the independent human annotation CSVs in `Dataset_Construction/annotation/validation/human_annotations/`, the reconciled `human_gold_annotations.csv`, and `llm_annotations_v1_combined.csv`.
3. **Reproduce descriptive statistics** for Section 4.2.1 and Appendix B.
4. **Run gate-level quantitative models** for Gate 0, Gate 1, Gate 2, and Axis B.
5. **Run model diagnostics and sensitivity checks**.
6. **Run qualitative summaries and triangulation outputs**.
7. **Generate figures, LaTeX tables, manifests, logs, and validation metadata**.

## RQ1 reproduction

Section 4.1 of the paper is reproduced by:

```bash
python -m RQ1_Prompt_Evaluation_Validation.analysis.rq1.agreement_analysis
```

Inputs:

```text
Dataset_Construction/annotation/validation/human_annotations/human_annotation_CL_richard.csv
Dataset_Construction/annotation/validation/human_annotations/human_annotation_CL_daniel.csv
Dataset_Construction/annotation/validation/human_annotations/human_annotation_PN_richard.csv
Dataset_Construction/annotation/validation/human_annotations/human_annotation_PN_daniel.csv
Dataset_Construction/annotation/validation/human_annotations/human_annotation_PA_richard.csv
Dataset_Construction/annotation/validation/human_annotations/human_annotation_PA_daniel.csv
Dataset_Construction/annotation/validation/human_annotations/human_annotation_NE_richard.csv
Dataset_Construction/annotation/validation/human_annotations/human_annotation_NE_daniel.csv
Dataset_Construction/annotation/validation/human_gold_annotations.csv
Dataset_Construction/annotation/validation/llm_annotations_v1_combined.csv
Dataset_Construction/annotation/rubric/human_annotation_codebook.csv
Dataset_Construction/annotation/rubric/human_annotation_codebook.md
```

Outputs:

```text
RQ1_Prompt_Evaluation_Validation/results/rq1/rq1_human_human_agreement_records.csv
RQ1_Prompt_Evaluation_Validation/results/rq1/rq1_human_human_disagreements.csv
RQ1_Prompt_Evaluation_Validation/results/rq1/rq1_human_human_agreement_metrics.csv
RQ1_Prompt_Evaluation_Validation/results/rq1/rq1_overall_agreement_metrics.csv
RQ1_Prompt_Evaluation_Validation/results/rq1/rq1_class_conditioned_kappa.csv
RQ1_Prompt_Evaluation_Validation/results/rq1/rq1_annotation_policy.csv
RQ1_Prompt_Evaluation_Validation/results/rq1/rq1_human_llm_validation_pairs.csv
RQ1_Prompt_Evaluation_Validation/results/rq1/rq1_summary.md
```

The human--human agreement outputs are computed before discussion/reconciliation and include per-prompt records, disagreements-only records, and category-by-dimension agreement metrics. The policy table is intentionally class-aware and reproduces the paper's Table 2. It uses agreement statistics plus construct-validity judgment rather than a blind threshold rule.

## Descriptive statistics reproduction

Section 4.2.1 and Appendix B are reproduced by:

```bash
python -m RQ2_Prompt_Effectiveness_Modeling.analysis.descriptive.descriptive_statistics
```

This regenerates Table 3(a), Table 3(b), the combined Table 3 LaTeX file, Appendix Tables 8--12, and the PQS distribution figure.

## Replacing the canonical dataset

Place the real study data at:

```text
Dataset_Construction/processed_data/final_analysis_dataset.csv
```

The required schema is documented in `Dataset_Construction/schema/dataset_schema.md` and enforced by `replication/verify_outputs.py`.

The canonical dataset is intentionally preserved as supplied. Repository, PR number, merged status, closed status, and normalized `PQS` are derived during preprocessing and written to derived outputs, not added back to the canonical file.


## Qualitative Illustrative Evidence

The package includes a traceable qualitative evidence dataset at `RQ2_Prompt_Effectiveness_Modeling/results/qualitative/illustrative_examples_dataset.csv` and gate-specific qualitative evidence outputs in `RQ2_Prompt_Effectiveness_Modeling/results/qualitative/gate0/`, `RQ2_Prompt_Effectiveness_Modeling/results/qualitative/gate1/`, and `RQ2_Prompt_Effectiveness_Modeling/results/qualitative/gate2/`. Each gate directory contains curated pattern tables (CSV/XLSX/PDF), full-record case CSV files, and README notes, and a cross-gate index is written to `RQ2_Prompt_Effectiveness_Modeling/results/qualitative/qualitative_examples_manifest.csv`.

## Appendix B Extended Descriptive Analysis

The reproduction pipeline also regenerates the richer Appendix B descriptive layer. These outputs are written under `RQ2_Prompt_Effectiveness_Modeling/results/descriptive/` and include distribution summaries, skewness diagnostics, outlier summaries, repository/language frequency tables, prompt-structure correlations, and supporting figures.

The relevant scripts are located in `RQ2_Prompt_Effectiveness_Modeling/analysis/descriptive/`:

```text
RQ2_Prompt_Effectiveness_Modeling/analysis/descriptive/
├── descriptive_statistics.py
├── appendix_b_descriptives.py
├── distribution_analysis.py
├── skewness_outlier_analysis.py
├── repository_distribution_analysis.py
├── language_distribution_analysis.py
└── prompt_structure_correlations.py
```

These outputs support the paper's Appendix B discussion and the modeling rationale that PR size and contributor experience are right-skewed, motivating log-transformed controls and robustness checks.
