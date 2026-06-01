# Artifact Evaluation

This document explains how to evaluate the replication package for the study **Prompt Quality and Pull Request Outcomes: A Stage-Based Empirical Study of LLM-Assisted Development**.

## Artifact Goals

The package is designed to support three levels of evaluation:

1. **Availability**: all datasets, scripts, notebooks, and generated outputs needed for the study are included.
2. **Reproducibility**: the main empirical outputs can be regenerated from the packaged datasets using the provided scripts.
3. **Traceability**: raw artifacts, annotation data, processed datasets, and paper outputs are linked through manifests and documentation.

The package supports both the RQ1 annotation-reliability analysis and the RQ2 stage-based modeling analysis.

## Quick Evaluator Workflow

For a short artifact review, run:

```bash
make reproduce
make verify
```

This executes the canonical reproduction pipeline and verifies that the expected outputs were generated.

For a lighter inspection path, read:

```text
docs/quickstart_artifact_eval.md
docs/reproduction_steps.md
docs/output_validation.md
```

## Expected Outputs

The reproduction pipeline writes outputs to:

```text
RQ2_Prompt_Effectiveness_Modeling/results/
├── tables/
├── figures/
├── diagnostics/
├── qualitative/
├── rq1/
├── manifests/
└── logs/
```

## Reproducibility Guarantees

The package follows the following reproducibility rules:

- The canonical downstream dataset is preserved as `Dataset_Construction/processed_data/final_analysis_dataset.csv`.
- Derived variables such as repository and PR number are computed from `PR_Link` rather than duplicated in the dataset.
- Merge/closure information is derived from the status field already present in the dataset.
- Random seeds and run settings are centralized in `replication/run_config.yaml`.
- Output validation is controlled by `replication/expected_outputs.yaml`.
- Run metadata is recorded in `RQ2_Prompt_Effectiveness_Modeling/results/logs/last_run_metadata.json`.

## Deterministic Execution Policy

The package prioritizes deterministic reproduction of reported tables and figures. Where exact numerical equality is inappropriate due to floating-point or package-version differences, validation uses tolerance-based checks.

The verification script checks that required outputs exist and, where configured, that values fall within acceptable tolerances.

## RQ1 Evaluation Scope

The RQ1 component evaluates human–LLM agreement for prompt-quality scoring. It uses:

```text
Dataset_Construction/annotation/validation/human_gold_annotations.csv
Dataset_Construction/annotation/validation/llm_annotations_v1_combined.csv
Dataset_Construction/annotation/rubric/human_annotation_codebook.csv
Dataset_Construction/annotation/rubric/human_annotation_codebook.md
```

and regenerates:

```text
RQ1_Prompt_Evaluation_Validation/results/rq1/rq1_overall_agreement_metrics.csv
RQ1_Prompt_Evaluation_Validation/results/rq1/rq1_class_conditioned_kappa.csv
RQ1_Prompt_Evaluation_Validation/results/rq1/rq1_annotation_policy.csv
```

These outputs correspond to the paper’s Section 4.1, including Table 1 and Table 2.

## RQ2 Evaluation Scope

The RQ2 component uses the cleaned processed dataset to regenerate:

- descriptive statistics,
- PQS distributions,
- Gate 0 code-generation models,
- Gate 1 adoption models,
- Gate 2 integration-depth models,
- Axis B lifecycle models,
- model diagnostics,
- sensitivity/robustness summaries,
- LaTeX tables and figures.

## Validation Expectations

A successful artifact evaluation should confirm that:

1. `make reproduce` completes without errors.
2. `make verify` confirms all expected outputs.
3. the RQ1 agreement values match the paper’s Section 4.1 values.
4. the descriptive statistics match the paper’s Table 3 and Appendix tables.
5. model outputs are regenerated from the packaged dataset rather than manually inserted.
6. documentation explains the raw, intermediate, and processed data layers.

## Notes for Evaluators

Some raw artifacts may be included for traceability but are not required for the default reproduction path. The canonical pipeline starts from the cleaned processed dataset and validation annotation datasets because those are the datasets used for downstream analysis in the paper.


## Robustness and sensitivity artifacts

Artifact evaluators can inspect robustness outputs in `RQ2_Prompt_Effectiveness_Modeling/results/diagnostics/`. These files demonstrate that the stage-dependent conclusions are not driven solely by one dominant repository, extremely large pull requests, the dominant programming language, or the choice between individual prompt dimensions and aggregate PQS. The primary interpretation is qualitative stability of the main effects rather than exact coefficient equality across all subsets.

## Diagnostic Evaluation Path

Artifact evaluators can inspect the diagnostic layer after running `make reproduce`:

```bash
ls RQ2_Prompt_Effectiveness_Modeling/results/diagnostics/
ls RQ2_Prompt_Effectiveness_Modeling/results/diagnostics/schoenfeld_residual_plots/
cat RQ2_Prompt_Effectiveness_Modeling/results/diagnostics/diagnostics_summary.md
```

The diagnostic layer includes VIF results, logistic separation checks, Schoenfeld
residual diagnostics, robustness/sensitivity outputs, and summary notes. These outputs
support the modeling validity claims reported in the paper and are included in the
verification manifest.


## Qualitative Illustrative Evidence

The package includes a traceable qualitative evidence dataset at `RQ2_Prompt_Effectiveness_Modeling/results/qualitative/illustrative_examples_dataset.csv`, gate-specific qualitative evidence bundles under `RQ2_Prompt_Effectiveness_Modeling/results/qualitative/gate0/`, `RQ2_Prompt_Effectiveness_Modeling/results/qualitative/gate1/`, and `RQ2_Prompt_Effectiveness_Modeling/results/qualitative/gate2/`. Each gate bundle provides CSV/XLSX/PDF pattern tables, full-record case CSV files, and a README. A cross-gate index is provided in `RQ2_Prompt_Effectiveness_Modeling/results/qualitative/qualitative_examples_manifest.csv`, and the illustrative-case selection process is documented in `RQ2_Prompt_Effectiveness_Modeling/notebooks/illustrative_examples_walkthrough.ipynb`.

## Final Reproducibility Support Artifacts

The package includes several evaluator-facing support artifacts in addition to the main reproduced tables and figures:

- `RQ2_Prompt_Effectiveness_Modeling/results/reproduction_report.md` summarizes the latest run, dataset size, generated output counts, runtime environment, and verification status.
- `RQ2_Prompt_Effectiveness_Modeling/results/runtime/runtime_environment.json` and `environment/runtime_capture.json` capture OS, Python, and selected package-version details.
- `environment/pip_freeze.txt` and `environment/conda_env_frozen.yml` provide frozen environment snapshots for long-term archival.
- `RQ2_Prompt_Effectiveness_Modeling/results/runtime/runtime_benchmarks.csv` and `RQ2_Prompt_Effectiveness_Modeling/results/runtime/reproduction_timing_summary.md` record step-level runtime benchmarks.
- `RQ2_Prompt_Effectiveness_Modeling/results/paper_tables_pdf/` contains quick PDF previews of generated LaTeX table files.
- `Dataset_Construction/provenance/data_manifest.csv` and `Dataset_Construction/provenance/checksums.sha256` provide file-level integrity records.

A smoke CI workflow is included at `.github/workflows/smoke-reproduction.yml`. It installs dependencies, runs `make smoke`, and verifies expected outputs.

## Docker Path

Containerized reproduction is documented in `docs/docker_reproduction.md`. The Docker path runs the same canonical commands as the local evaluator path:

```bash
make reproduce
make verify
```
