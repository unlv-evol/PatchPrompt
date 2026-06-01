# Reproducibility Policy

- Canonical environment definition: `requirements-lock.txt`
- `requirements.txt` is for human-readable top-level dependencies.
- Pin changes must be intentional and documented.


## Documentation Synchronization

The package documentation distinguishes between three artifact layers:

- `Dataset_Construction/raw_data/`: immutable source artifacts such as PatchTrack exports and ChatGPT PDFs.
- `Dataset_Construction/processed_data/`: canonical datasets used by the analysis scripts.

The reproducible analysis path begins from processed and validation datasets, while raw artifacts are preserved for traceability and future extension.

## LLM Annotation Version Policy

Only LLM V1 annotation outputs are part of the final reproducible analysis. LLM V2
annotations were not used in the final agreement analysis, annotation-policy derivation,
or downstream modeling. The package therefore does not require V2 files for a complete
reproduction of the reported results.

## Diagnostic Artifact Policy

Diagnostic plots are regenerated from the canonical processed dataset during
`make reproduce`. They are treated as interpretive artifacts rather than exact numerical
claims; the corresponding CSV tables remain the canonical machine-readable diagnostic
outputs. The plots help artifact evaluators visually inspect VIF patterns and
Schoenfeld residual behavior for the Axis B Cox models.

## Environment and Runtime Capture Policy

Every full reproduction run captures runtime metadata in `RQ2_Prompt_Effectiveness_Modeling/results/runtime/` and `environment/`. These files are intended to make the computational environment auditable without requiring artifact evaluators to infer package versions manually.

The package records:

- Python version and platform information,
- selected scientific package versions,
- a complete `pip freeze` snapshot,
- a conda-style frozen environment export,
- step-level reproduction timings.

The generated `RQ2_Prompt_Effectiveness_Modeling/results/reproduction_report.md` should be treated as the human-readable summary of the latest reproduction run.

## Prompt-Length Control Note

The final processed dataset does not include full developer prompt text as a separate column. Therefore, prompt-length control models are documented in `RQ2_Prompt_Effectiveness_Modeling/results/diagnostics/prompt_length_control_models.csv` as not estimated from the canonical processed dataset. The raw ChatGPT PDFs are included for traceability and future extension.
