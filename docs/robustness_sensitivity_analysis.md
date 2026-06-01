# Robustness and Sensitivity Analysis

This document summarizes the reviewer-oriented robustness and sensitivity workflow implemented in `RQ2_Prompt_Effectiveness_Modeling/analysis/diagnostics/robustness_sensitivity_outputs.py`.

## Purpose

The robustness analysis evaluates whether the Gate 0, Gate 1, and Gate 2 findings remain qualitatively stable under reasonable modeling and sampling variations. The goal is not to discover new effects, but to test whether the stage-specific interpretation is robust to repository dependence, dominant repositories/languages, skewed pull-request size distributions, alternative Gate 2 outcome definitions, aggregate prompt-quality specifications, prompt length, and hold-out splits.

## Implemented checks

1. **Repository-level dependence**: re-estimates Gate 0, Gate 1, and Gate 2 with repository-clustered robust standard errors.
2. **Dominant repository sensitivity**: excludes the largest repository and then the top five repositories within each gate sample.
3. **Language sensitivity**: excludes the dominant language and then the top two languages within each gate sample.
4. **PR-size outlier sensitivity**: excludes the top 1% and top 5% largest PRs for Gate 1, Gate 2, and Axis B where feasible.
5. **Alternative Gate 2 operationalization**: converts `Fraction_Adopted` into reuse terciles and estimates ordinal and high-vs-low reuse models.
6. **Aggregate PQS robustness**: replaces Context, Specificity, and Verification with the aggregate PQS predictor.
7. **Prompt-length control**: extracts an approximate prompt length from the raw ChatGPT PDFs where possible and adds `log_prompt_tokens` as a control.
8. **Hold-out stability**: performs a stratified 80/20 split and checks whether coefficient directions remain consistent.

## Main outputs

Generated outputs are written to `RQ2_Prompt_Effectiveness_Modeling/results/diagnostics/`, including:

- `RQ2_Prompt_Effectiveness_Modeling/results/diagnostics/full_robustness_sensitivity_results.csv`
- `RQ2_Prompt_Effectiveness_Modeling/results/diagnostics/robustness_summary_table.csv`
- `RQ2_Prompt_Effectiveness_Modeling/results/diagnostics/robustness_core_finding_stability.csv`
- `RQ2_Prompt_Effectiveness_Modeling/results/diagnostics/robustness_exclusion_details.csv`
- `RQ2_Prompt_Effectiveness_Modeling/results/diagnostics/pr_size_outlier_thresholds.csv`
- `RQ2_Prompt_Effectiveness_Modeling/results/diagnostics/gate2_alternative_operationalization.csv`
- `RQ2_Prompt_Effectiveness_Modeling/results/diagnostics/prompt_tokens.csv`
- `RQ2_Prompt_Effectiveness_Modeling/results/diagnostics/prompt_length_control_models.csv`
- `RQ2_Prompt_Effectiveness_Modeling/results/diagnostics/holdout_stability_checks.csv`
- `RQ2_Prompt_Effectiveness_Modeling/results/diagnostics/robustness_memo.md`

Diagnostic artifacts also include:

```text
RQ2_Prompt_Effectiveness_Modeling/results/diagnostics/
├── diagnostics_summary.md
├── vif_diagnostics.png
├── vif_correlation_heatmap.png
└── schoenfeld_residual_plots/
```

Together, these outputs support model-validity checks for multicollinearity, separation, proportional hazards, and robustness stability.

## Interpretation policy

The analysis focuses on directional consistency, approximate effect stability, and whether significance patterns materially change. Exact p-value replication across all restricted samples is not required. Meaningful deviations are documented transparently, especially for Gate 2, where the PA-only sample becomes small under repository and language exclusions.
