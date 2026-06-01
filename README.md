# Patch Prompt Replication Package

This repository is an end-to-end replication package for the PatchPrompt prompt-quality study, **Prompt Quality and Pull Request Outcomes: A Stage-Based Empirical Study of LLM-Assisted Development**.

The package preserves the cleaned downstream analysis dataset exactly as used for modeling and regenerates the annotation-reliability results, quantitative tables, diagnostics, qualitative summaries, figures, output manifests, and run metadata.

## Abstract

This replication package supports a stage-based empirical study of how developer prompt structure relates to ChatGPT-assisted pull request outcomes. The study operationalizes prompt quality using three dimensions—Context, Specificity, and Verification—and analyzes how these dimensions influence code generation, code adoption, integration depth, and pull request lifecycle behavior. The package includes the final cleaned dataset, human and LLM annotation-validation artifacts, reproducible scripts, notebooks, diagnostics, tables, and figures needed to reproduce the reported results.

## Canonical dataset

The canonical dataset is:

```text
Dataset_Construction/processed_data/final_analysis_dataset.csv
```

It contains 273 PR-linked cases and 21 variables. The dataset is intentionally preserved as-is. In particular:

- `Repository` and `PR_Number` are **not** stored as additional canonical columns; they are derived from `PR_Link` inside the pipeline.
- merged/closed state is derived from the existing `Status` field.
- the original `PQS ` column name, including its trailing space, is preserved in the canonical CSV for fidelity. Derived analysis views expose it as `PQS`.

## What this package reproduces

The pipeline covers the empirical workflow described in the paper:

1. dataset preparation from the finalized cleaned dataset;
2. RQ1 annotation reliability analysis, including human--human inter-rater agreement from the independent 30% human annotations and human--LLM validation using the reconciled human gold subset and LLM-v1 annotations;
3. prompt scoring using Context, Specificity, Verification, and PQS;
4. outcome classes PA, PN, NE, and CL;
5. gate-level modeling:
   - Gate 0: code generation, PA/PN vs NE;
   - Gate 1: code adoption, PA vs PN among generated-code cases;
   - Gate 2: integration depth among PA cases;
   - Axis B: PR lifecycle outcomes using merge and close hazards;
6. model diagnostics:
   - VIF checks;
   - logistic separation screening;
   - proportional-hazards diagnostics record;
   - sensitivity analyses;
7. qualitative code-frequency, thematic, and triangulation summaries;
8. paper-ready CSV, PNG, Markdown, and PDF review outputs.

## Quick start

Recommended Python version: 3.11 (tested and supported range is 3.10 to 3.12; the Makefile enforces this and allows explicit interpreter override).

Create and use a virtual environment (recommended):

macOS:

```bash
python3.11 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements-lock.txt
```

Linux:

```bash
python3.11 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements-lock.txt
```

Windows (PowerShell):

```powershell
py -3.11 -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements-lock.txt
```

Windows (Command Prompt):

```bat
py -3.11 -m venv .venv
.venv\Scripts\activate.bat
python -m pip install --upgrade pip
python -m pip install -r requirements-lock.txt
```

Run replication with the same interpreter:

```bash
make PYTHON=.venv/bin/python reproduce
make PYTHON=.venv/bin/python verify
```

If you do not use a virtual environment, run with an explicit interpreter:

```bash
python3.11 -m pip install -r requirements-lock.txt
make PYTHON=python3.11 reproduce
make PYTHON=python3.11 verify
```

One-command shell wrapper:

```bash
bash run_all.sh
```

## Full vs smoke runs

- `make ... reproduce` runs the full pipeline and generates all configured outputs.
- `make ... smoke` runs a faster evaluator path and skips methodological-alignment sensitivity artifacts.

To generate all outputs:

```bash
make PYTHON=.venv/bin/python reproduce
make PYTHON=.venv/bin/python verify
```

## Docker (optional)

Docker is not required for replication. If you prefer containerized execution, use the optional path documented in `docs/docker_reproduction.md`.

## Fresh output behavior

- PDF previews under `RQ2_Prompt_Effectiveness_Modeling/results/paper_tables_pdf/` are cleared and fully regenerated on each run.
- Other generated outputs are overwritten by filename, but stale files from old naming schemes can remain unless cleaned.

For a fully fresh regeneration of generated artifacts:

```bash
make clean
make PYTHON=.venv/bin/python reproduce
make PYTHON=.venv/bin/python verify
```

## Key outputs

- `RQ1_Prompt_Evaluation_Validation/results/rq1/rq1_human_human_agreement_records.csv`
- `RQ1_Prompt_Evaluation_Validation/results/rq1/rq1_human_human_disagreements.csv`
- `RQ1_Prompt_Evaluation_Validation/results/rq1/rq1_human_human_agreement_metrics.csv`
- `RQ1_Prompt_Evaluation_Validation/results/rq1/rq1_overall_agreement_metrics.csv`
- `RQ1_Prompt_Evaluation_Validation/results/rq1/rq1_class_conditioned_kappa.csv`
- `RQ1_Prompt_Evaluation_Validation/results/rq1/rq1_annotation_policy.csv`
- `Dataset_Construction/processed_data/gate_model_dataset.csv`
- `Dataset_Construction/processed_data/prompt_scores.csv`
- `Dataset_Construction/processed_data/qualitative_dataset.csv`
- `RQ2_Prompt_Effectiveness_Modeling/results/tables/gate0_generation_model.csv`
- `RQ2_Prompt_Effectiveness_Modeling/results/tables/gate1_adoption_model.csv`
- `RQ2_Prompt_Effectiveness_Modeling/results/tables/gate2_integration_model.csv`
- `RQ2_Prompt_Effectiveness_Modeling/results/tables/axisb_lifecycle_model.csv`
- `RQ2_Prompt_Effectiveness_Modeling/results/diagnostics/vif_results.csv`
- `RQ2_Prompt_Effectiveness_Modeling/results/diagnostics/separation_checks.csv`
- `RQ2_Prompt_Effectiveness_Modeling/results/diagnostics/schoenfeld_residual_tests.csv`
- `RQ2_Prompt_Effectiveness_Modeling/results/diagnostics/sensitivity_analysis.csv`
- `RQ2_Prompt_Effectiveness_Modeling/results/diagnostics/full_robustness_sensitivity_results.csv`
- `RQ2_Prompt_Effectiveness_Modeling/results/diagnostics/robustness_summary_table.csv`
- `RQ2_Prompt_Effectiveness_Modeling/results/diagnostics/clustered_se_models.csv`
- `RQ2_Prompt_Effectiveness_Modeling/results/diagnostics/mixed_effects_models.csv`
- `RQ2_Prompt_Effectiveness_Modeling/results/diagnostics/holdout_stability_checks.csv`
- `RQ2_Prompt_Effectiveness_Modeling/results/diagnostics/prompt_length_control_models.csv`
- `RQ2_Prompt_Effectiveness_Modeling/results/diagnostics/gate2_reuse_level_counts.csv`
- `RQ2_Prompt_Effectiveness_Modeling/results/qualitative/*.csv`
- `RQ2_Prompt_Effectiveness_Modeling/results/figures/*.png`
- `RQ2_Prompt_Effectiveness_Modeling/results/manifests/*_manifest.csv`
- `RQ2_Prompt_Effectiveness_Modeling/results/logs/last_run_metadata.json`

## Repository layout

```text
PatchTrack-Replication-Package/
├── .github/                               ← CI and automation configuration
│   └── workflows/
│       └── smoke-reproduction.yml         ← smoke-reproduction workflow for CI checks
├── README.md                              ← replication overview and quick start
├── LICENSE                                ← MIT license
├── CITATION.cff                           ← citation metadata
├── requirements.txt                       ← human-maintained dependency ranges
├── requirements-lock.txt                  ← pinned dependency lockfile
├── environment.yml                        ← optional conda environment
├── Dockerfile                             ← containerized replication environment
├── docker-compose.yml                     ← docker-compose based reproduction entrypoint
├── Makefile                               ← canonical evaluator entrypoint
├── run_all.sh                             ← wrapper around `make reproduce` and `make verify`
│
├── replication/
│   ├── reproduce_all.py                   ← full pipeline orchestrator
│   ├── reproduce_tables.py                ← table-generation orchestrator
│   ├── reproduce_figures.py               ← figure-generation orchestrator
│   ├── verify_outputs.py                  ← output validation checks
│   ├── collect_run_metadata.py            ← runtime metadata capture
│   ├── capture_runtime.py                 ← environment/runtime snapshot writer
│   ├── export_tables_to_pdf.py            ← rendered PDF export of generated CSV tables
│   ├── write_reproduction_report.py       ← evaluator-facing reproduction report generator
│   ├── pipeline_manifest.yaml             ← machine-readable pipeline description
│   ├── expected_outputs.yaml              ← expected outputs and validation rules
│   └── run_config.yaml                    ← seed, paths, and run configuration
│
├── Dataset_Construction/
│   ├── annotation/
│   │   ├── rubric/
│   │   ├── coding/
│   │   └── validation/
│   ├── raw_data/
│   │   ├── github/                        ← raw GitHub-side extracted artifacts
│   │   ├── chatgpt/                       ← raw ChatGPT-side extracted artifacts
│   │   └── metadata/                      ← supplemental metadata for raw collection
│   ├── processed_data/
│   │   ├── final_analysis_dataset.csv     ← canonical cleaned downstream dataset
│   │   ├── gate_model_dataset.csv         ← derived modeling view
│   │   ├── qualitative_dataset.csv        ← derived qualitative-analysis view
│   │   └── prompt_scores.csv              ← prompt-score extract
│   ├── schema/
│   │   ├── dataset_schema.md              ← schema and derived-field documentation
│   │   └── field_descriptions.csv         ← field-level descriptions
│   ├── provenance/
│   │   ├── data_manifest.csv              ← source/data manifest
│   │   ├── lineage.md                     ← raw/intermediate/processed lineage
│   │   └── checksums.sha256               ← dataset checksums
│   └── mining/
│       └── preprocessing/
│
├── RQ2_Prompt_Effectiveness_Modeling/results/
│   ├── tables/                            ← generated CSV tables
│   ├── figures/                           ← generated figures
│   ├── diagnostics/                       ← generated diagnostic outputs
│   ├── descriptive/                       ← generated Appendix B descriptive outputs
│   ├── qualitative/                       ← generated qualitative outputs
│   │   ├── README.md                      ← qualitative output documentation
│   │   ├── gate0/                         ← Gate 0 qualitative tables and full records
│   │   ├── gate1/                         ← Gate 1 qualitative tables and full records
│   │   ├── gate2/                         ← Gate 2 qualitative tables and full records
│   │   └── (top-level qualitative summary CSV/manifest files)
│   ├── manifests/                         ← generated output manifests
│   ├── paper_tables_pdf/                  ← rendered PDF previews of generated tables
│   ├── runtime/                           ← runtime environment and timing outputs
│   ├── logs/                              ← run logs and metadata
│   └── reproduction_report.md             ← concise artifact-evaluation run report
│
├── RQ1_Prompt_Evaluation_Validation/
│   ├── analysis/
│   │   └── rq1/                         ← agreement-analysis script
│   ├── results/
│   │   └── rq1/                          ← generated RQ1 CSVs, including human--human agreement outputs
│   └── notebooks/
│       └── rq1_annotation_reliability.ipynb  ← RQ1 reliability walkthrough
│
├── RQ2_Prompt_Effectiveness_Modeling/
│   ├── analysis/
│   ├── results/
│   └── notebooks/
│       ├── descriptive_statistics_walkthrough.ipynb
│       ├── appendix_b_descriptive_walkthrough.ipynb
│       ├── exploratory_analysis.ipynb
│       ├── modeling_walkthrough.ipynb
│       ├── diagnostics_walkthrough.ipynb
│       ├── robustness_sensitivity_walkthrough.ipynb
│       ├── qualitative_walkthrough.ipynb
│       ├── illustrative_examples_walkthrough.ipynb
│       ├── reproduction_driver.ipynb
│       └── README.md
│
├── docs/
│   ├── reproduction_steps.md              ← full reproduction instructions
│   ├── quickstart_artifact_eval.md        ← short evaluator path
│   ├── robustness_sensitivity_analysis.md ← guideline-based robustness and sensitivity documentation
│   ├── computational_requirements.md      ← hardware/software assumptions
│   ├── threats_to_validity.md             ← validity discussion
│   ├── artifact_evaluation.md             ← artifact-evaluation guidance
│   ├── troubleshooting.md                 ← common issues and fixes
│   ├── reproducibility_policy.md          ← environment and pinning policy
│   ├── output_validation.md               ← validation rules and interpretation
│   ├── docker_reproduction.md             ← Docker and docker-compose reproduction path
│   └── results_expected_from_current_paper.md ← expected results mapping for evaluators
│
└── environment/
   ├── pip_freeze.txt                     ← captured pip snapshot from reproduction run
   ├── conda_env_frozen.yml               ← frozen conda-style environment export
   └── runtime_capture.json               ← captured runtime environment metadata
```

## Qualitative Illustrative Evidence

The package includes a traceable qualitative evidence dataset at `RQ2_Prompt_Effectiveness_Modeling/results/qualitative/illustrative_examples_dataset.csv` and gate-specific qualitative evidence bundles under `RQ2_Prompt_Effectiveness_Modeling/results/qualitative/gate0/`, `RQ2_Prompt_Effectiveness_Modeling/results/qualitative/gate1/`, and `RQ2_Prompt_Effectiveness_Modeling/results/qualitative/gate2/`. Each gate folder includes curated pattern tables in CSV/XLSX/PDF, full-record case CSV files, and a README, with a cross-gate index in `RQ2_Prompt_Effectiveness_Modeling/results/qualitative/qualitative_examples_manifest.csv`. The illustrative selection process is documented in `RQ2_Prompt_Effectiveness_Modeling/notebooks/illustrative_examples_walkthrough.ipynb`.

## License

This repository is MIT licensed. See the [LICENSE](./LICENSE) file for more information.