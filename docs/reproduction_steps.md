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

1. **Prepare derived datasets** from `dataset/processed/final_analysis_dataset.csv` without modifying the canonical dataset.
2. **Reproduce RQ1 annotation reliability** from `annotation/validation/human_gold_annotations.csv` and `annotation/validation/llm_annotations_v1_combined.csv`.
3. **Reproduce descriptive statistics** for Section 4.2.1 and Appendix B.
4. **Run gate-level quantitative models** for Gate 0, Gate 1, Gate 2, and Axis B.
5. **Run model diagnostics and sensitivity checks**.
6. **Run qualitative summaries and triangulation outputs**.
7. **Generate figures, LaTeX tables, manifests, logs, and validation metadata**.

## RQ1 reproduction

Section 4.1 of the paper is reproduced by:

```bash
python -m analysis.rq1.agreement_analysis
```

Inputs:

```text
annotation/validation/human_gold_annotations.csv
annotation/validation/llm_annotations_v1_combined.csv
```

Outputs:

```text
results/rq1/rq1_overall_agreement_metrics.csv
results/rq1/rq1_class_conditioned_kappa.csv
results/rq1/rq1_annotation_policy.csv
results/rq1/rq1_human_llm_validation_pairs.csv
results/rq1/rq1_summary.md
paper/tables/table_rq1a_overall_agreement.tex
paper/tables/table_rq1b_class_conditioned_kappa.tex
paper/tables/table_rq1c_annotation_policy.tex
```

The policy table is intentionally class-aware and reproduces the paper's Table 2. It uses agreement statistics plus construct-validity judgment rather than a blind threshold rule.

## Descriptive statistics reproduction

Section 4.2.1 and Appendix B are reproduced by:

```bash
python -m analysis.descriptive.descriptive_statistics
```

This regenerates Table 3(a), Table 3(b), the combined Table 3 LaTeX file, Appendix Tables 8--12, and the PQS distribution figure.

## Replacing the canonical dataset

Place the real study data at:

```text
dataset/processed/final_analysis_dataset.csv
```

The required schema is documented in `dataset/schema/dataset_schema.md` and enforced by `replication/verify_outputs.py`.

The canonical dataset is intentionally preserved as supplied. Repository, PR number, merged status, closed status, and normalized `PQS` are derived during preprocessing and written to derived outputs, not added back to the canonical file.


## Qualitative Illustrative Evidence

The package includes a traceable qualitative evidence dataset at `results/qualitative/illustrative_examples_dataset.csv` and gate-specific qualitative evidence outputs in `results/qualitative/gate0/`, `results/qualitative/gate1/`, and `results/qualitative/gate2/`. Each gate directory contains curated pattern tables (CSV/XLSX/PDF), full-record case CSV files, and README notes. Matching reviewer-facing copies are mirrored under `qualitative_examples/`, and a cross-gate index is written to `results/qualitative/qualitative_examples_manifest.csv`.

## Appendix B Extended Descriptive Analysis

The reproduction pipeline also regenerates the richer Appendix B descriptive layer. These outputs are written under `results/descriptive/` and include distribution summaries, skewness diagnostics, outlier summaries, repository/language frequency tables, prompt-structure correlations, and supporting figures.

The relevant scripts are located in `analysis/descriptive/`:

```text
analysis/descriptive/
├── descriptive_statistics.py
├── appendix_b_descriptives.py
├── distribution_analysis.py
├── skewness_outlier_analysis.py
├── repository_distribution_analysis.py
├── language_distribution_analysis.py
└── prompt_structure_correlations.py
```

These outputs support the paper's Appendix B discussion and the modeling rationale that PR size and contributor experience are right-skewed, motivating log-transformed controls and robustness checks.
