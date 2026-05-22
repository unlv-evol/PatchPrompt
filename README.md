# PatchTrack Prompt Replication Package

This repository is an end-to-end replication package for the PatchTrack prompt-quality study, **Prompt Quality and Pull Request Outcomes: A Stage-Based Empirical Study of LLM-Assisted Development**.

The package preserves the cleaned downstream analysis dataset exactly as used for modeling and regenerates the annotation-reliability results, quantitative tables, diagnostics, qualitative summaries, figures, LaTeX tables, output manifests, and run metadata.

## Abstract

This replication package supports a stage-based empirical study of how developer prompt structure relates to ChatGPT-assisted pull request outcomes. The study operationalizes prompt quality using three dimensions—Context, Specificity, and Verification—and analyzes how these dimensions influence code generation, code adoption, integration depth, and pull request lifecycle behavior. The package includes the final cleaned dataset, human and LLM annotation-validation artifacts, reproducible scripts, notebooks, diagnostics, tables, and figures needed to reproduce the reported results.

## Canonical dataset

The canonical dataset is:

```text
dataset/processed/final_analysis_dataset.csv
```

It contains 273 PR-linked cases and 21 variables. The dataset is intentionally preserved as-is. In particular:

- `Repository` and `PR_Number` are **not** stored as additional canonical columns; they are derived from `PR_Link` inside the pipeline.
- merged/closed state is derived from the existing `Status` field.
- the original `PQS ` column name, including its trailing space, is preserved in the canonical CSV for fidelity. Derived analysis views expose it as `PQS`.

## What this package reproduces

The pipeline covers the empirical workflow described in the paper:

1. dataset preparation from the finalized cleaned dataset;
2. RQ1 annotation reliability analysis using the 30% human gold subset and LLM-v1 annotations;
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
8. paper-ready CSV, PNG, Markdown, and LaTeX outputs.

## Quick start

Recommended Python version: 3.11 (the Makefile accepts 3.9 to 3.12 and allows explicit interpreter override).

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

## Fresh output behavior

- PDF previews under `results/paper_tables_pdf/` are cleared and fully regenerated on each run.
- Other generated outputs are overwritten by filename, but stale files from old naming schemes can remain unless cleaned.

For a fully fresh regeneration of generated artifacts:

```bash
make clean
make PYTHON=.venv/bin/python reproduce
make PYTHON=.venv/bin/python verify
```

## Key outputs

- `results/rq1/rq1_overall_agreement_metrics.csv`
- `results/rq1/rq1_class_conditioned_kappa.csv`
- `results/rq1/rq1_annotation_policy.csv`
- `dataset/processed/gate_model_dataset.csv`
- `dataset/processed/prompt_scores.csv`
- `dataset/processed/qualitative_dataset.csv`
- `results/tables/gate0_generation_model.csv`
- `results/tables/gate1_adoption_model.csv`
- `results/tables/gate2_integration_model.csv`
- `results/tables/axisb_lifecycle_model.csv`
- `results/diagnostics/vif_results.csv`
- `results/diagnostics/separation_checks.csv`
- `results/diagnostics/schoenfeld_residual_tests.csv`
- `results/diagnostics/sensitivity_analysis.csv`
- `results/qualitative/*.csv`
- `results/figures/*.png`
- `paper/tables/*.tex`
- `paper/figures/*.png`
- `results/manifests/*_manifest.csv`
- `results/logs/last_run_metadata.json`

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
├── dataset/
│   ├── processed/
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
│   └── raw/
│       ├── github/                        ← raw GitHub-side extracted artifacts
│       ├── chatgpt/                       ← raw ChatGPT-side extracted artifacts
│       └── metadata/                      ← supplemental metadata for raw collection
│
├── annotation/
│   ├── rubric/
│   │   ├── prompt_quality_rubric.md       ← Context/Specificity/Verification rubric
│   │   ├── PA_PN_NE_CL_definitions.md     ← outcome-class definitions
│   │   ├── annotation_guidelines.md       ← annotation instructions
│   │   ├── prompt_dimension_definitions.md← detailed prompt-dimension definitions
│   │   ├── annotation_policy_notes.md     ← annotation policy rationale and notes
│   │   └── llm_annotation_prompt_full.md  ← full LLM annotation prompt template
│   ├── coding/
│   │   ├── qualitative_codebook.md        ← qualitative coding definitions
│   │   ├── coding_examples.csv            ← example coded cases
│   │   └── theme_mapping.csv              ← theme-to-dimension mapping
│   └── validation/
│       ├── README.md                      ← validation artifact usage notes
│       ├── human_gold_annotations.csv     ← 30% human-consensus validation subset
│       ├── llm_annotations_v1_combined.csv← combined LLM-v1 annotations
│       ├── agreement_checks.py            ← legacy/simple agreement checks
│       └── adjudication_notes.md          ← adjudication notes placeholder
│
├── analysis/
│   ├── common.py                          ← shared data-loading/output-writing helpers
│   ├── rq1/
│   │   └── agreement_analysis.py          ← Section 4.1 reliability and policy analysis
│   ├── descriptive/
│   │   ├── descriptive_statistics.py      ← Table 3 and Appendix descriptive statistics
│   │   ├── appendix_b_descriptives.py     ← Appendix B combined descriptive pipeline
│   │   ├── distribution_analysis.py       ← core distributional summaries and plots
│   │   ├── skewness_outlier_analysis.py   ← skewness and outlier diagnostics
│   │   ├── repository_distribution_analysis.py ← repository concentration analysis
│   │   ├── language_distribution_analysis.py   ← language concentration analysis
│   │   └── prompt_structure_correlations.py    ← prompt-dimension correlation analysis
│   ├── quantitative/
│   │   ├── gate0_generation.py            ← Gate 0 logistic model
│   │   ├── gate1_adoption.py              ← Gate 1 logistic model
│   │   ├── gate2_integration.py           ← Gate 2 fractional/integration model
│   │   ├── axisB_lifecycle.py             ← lifecycle outcome models
│   │   └── effect_sizes.py                ← supporting effect-size summaries
│   ├── diagnostics/
│   │   ├── vif_analysis.py                ← multicollinearity diagnostics
│   │   ├── separation_checks.py           ← logistic separation checks
│   │   ├── schoenfeld_tests.py            ← proportional hazards diagnostics record
│   │   ├── sensitivity_analysis.py        ← baseline robustness/sensitivity checks
│   │   ├── methodological_alignment_outputs.py ← clustered/mixed/holdout diagnostic layer
│   │   ├── robustness_sensitivity_outputs.py   ← full robustness-sensitivity result suite
│   │   └── diagnostic_plots_summary.py    ← diagnostic plots and narrative summary
│   └── qualitative/
│       ├── code_frequency_analysis.py     ← code frequency summaries
│       ├── thematic_analysis.py           ← directed qualitative summary
│       ├── triangulation_analysis.py      ← quantitative/qualitative triangulation
│       └── illustrative_examples.py       ← illustrative case extraction and summaries
│
├── results/
│   ├── rq1/                               ← generated Section 4.1 RQ1 outputs
│   ├── tables/                            ← generated CSV tables
│   ├── figures/                           ← generated figures
│   ├── diagnostics/                       ← generated diagnostic outputs
│   ├── descriptive/                       ← generated Appendix B descriptive outputs
│   ├── qualitative/                       ← generated qualitative outputs
│   ├── manifests/                         ← generated output manifests
│   ├── paper_tables_pdf/                  ← rendered PDF previews of generated tables
│   ├── runtime/                           ← runtime environment and timing outputs
│   ├── logs/                              ← run logs and metadata
│   └── reproduction_report.md             ← concise artifact-evaluation run report
│
├── paper/
│   ├── figures/                           ← paper-ready figure copies
│   ├── tables/                            ← paper-ready LaTeX tables
│   └── generated_sections/                ← generated text/summary sections
│
├── notebooks/
│   ├── rq1_annotation_reliability.ipynb   ← RQ1 reliability walkthrough
│   ├── descriptive_statistics_walkthrough.ipynb ← descriptive statistics walkthrough
│   ├── appendix_b_descriptive_walkthrough.ipynb ← Appendix B descriptive walkthrough
│   ├── exploratory_analysis.ipynb         ← exploratory analysis notebook
│   ├── modeling_walkthrough.ipynb         ← gate and lifecycle modeling walkthrough
│   ├── diagnostics_walkthrough.ipynb      ← diagnostics and model checks walkthrough
│   ├── robustness_sensitivity_walkthrough.ipynb ← robustness and sensitivity walkthrough
│   ├── qualitative_walkthrough.ipynb      ← qualitative coding and summary walkthrough
│   ├── illustrative_examples_walkthrough.ipynb ← illustrative case-trace walkthrough
│   ├── reproduction_driver.ipynb          ← notebook-driven pipeline reproduction runner
│   └── README.md                          ← notebook reproducibility policy
│
├── docs/
│   ├── reproduction_steps.md              ← full reproduction instructions
│   ├── quickstart_artifact_eval.md        ← short evaluator path
│   ├── computational_requirements.md      ← hardware/software assumptions
│   ├── threats_to_validity.md             ← validity discussion
│   ├── artifact_evaluation.md             ← artifact-evaluation guidance
│   ├── troubleshooting.md                 ← common issues and fixes
│   ├── reproducibility_policy.md          ← environment and pinning policy
│   ├── output_validation.md               ← validation rules and interpretation
│   ├── docker_reproduction.md             ← Docker and docker-compose reproduction path
│   └── results_expected_from_current_paper.md ← expected results mapping for evaluators
│
├── mining/
│   └── preprocessing/
│       └── build_processed_datasets.py    ← canonical processed-dataset builder
│
└── environment/
   ├── pip_freeze.txt                     ← captured pip snapshot from reproduction run
   ├── conda_env_frozen.yml               ← frozen conda-style environment export
   └── runtime_capture.json               ← captured runtime environment metadata
```


### Robustness and sensitivity analyses

The replication package includes full robustness checks for the stage-based models. These checks exclude the dominant repository, exclude extreme PR sizes, exclude the dominant programming language, and compare aggregate PQS models against individual Context/Specificity/Verification specifications. Outputs are generated under `results/diagnostics/` and summarized in `results/diagnostics/robustness_sensitivity_summary.md`.

## License

This repository is MIT licensed. See the [LICENSE](./LICENSE) file for more information.

### Diagnostic plots and model-validity summaries

The package includes generated diagnostic plots and a narrative diagnostics summary in:

```text
results/diagnostics/
├── diagnostics_summary.md
├── vif_diagnostics.png
├── vif_correlation_heatmap.png
└── schoenfeld_residual_plots/
```

These artifacts complement the tabular VIF, separation, Schoenfeld, and robustness
outputs used to support the paper's model-validity discussion.

### LLM annotation versions

Only LLM V1 annotation outputs were used in the final paper analyses. LLM V2 files
were not used and are not required for reproduction.


## Qualitative Illustrative Evidence

The package includes a traceable qualitative evidence dataset at `results/qualitative/illustrative_examples_dataset.csv`. It extracts the full canonical records for the paper-referenced illustrative cases used in the stage-based qualitative discussion, including PN-19, NE-3, PA-22, PA-78, and PA-24. A companion markdown summary is available at `results/qualitative/illustrative_examples_summary.md`, and the selection process is documented in `notebooks/illustrative_examples_walkthrough.ipynb`.

## Appendix B Descriptive Evidence

The package includes an expanded descriptive-analysis layer beyond the main paper tables. The scripts in `analysis/descriptive/` regenerate Appendix B summaries for PR-size distributions, contributor experience, repository/language concentration, prompt-score distributions, skewness, outliers, and prompt-structure correlations. Outputs are written to:

```text
results/descriptive/
├── appendix_b_summary_statistics.csv
├── prompt_dimension_distributions.csv
├── repository_distribution.csv
├── language_distribution.csv
├── skewness_analysis.csv
├── outlier_summary.csv
├── prompt_structure_correlations.csv
├── contributor_experience_summary.csv
├── pr_size_distribution_summary.csv
├── appendix_b_tables/
├── appendix_b_figures/
└── appendix_b_summary.md
```

The walkthrough notebook is available at `notebooks/appendix_b_descriptive_walkthrough.ipynb`.

## Final Artifact-Evaluation Additions

This package also includes several final reproducibility-support artifacts:

- `results/reproduction_report.md` — concise run report with dataset counts, generated-output counts, runtime environment, and verification notes.
- `results/runtime/` — runtime environment capture and timing benchmark outputs.
- `environment/` — frozen package snapshots, including `pip_freeze.txt`, `conda_env_frozen.yml`, and `runtime_capture.json`.
- `results/paper_tables_pdf/` — quick rendered PDF previews of generated table artifacts for evaluator inspection.
- `dataset/provenance/data_manifest.csv` and `dataset/provenance/checksums.sha256` — file-level provenance and integrity records.
- `.github/workflows/smoke-reproduction.yml` — a smoke-reproduction workflow for continuous integration.
- `docs/docker_reproduction.md` and `docker-compose.yml` — containerized reproduction instructions.

The methodological-alignment outputs under `results/diagnostics/` include repository-clustered standard-error variants, mixed-effects approximations, holdout stability checks, and a documented prompt-length-control feasibility record.
