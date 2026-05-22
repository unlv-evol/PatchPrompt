# Reproduction Report

Generated: 2026-05-22T04:20:08Z

## Dataset

- Canonical dataset: `dataset/processed/final_analysis_dataset.csv`
- Observations: 273
- Outcome-class counts: `{'PA': 89, 'NE': 84, 'PN': 53, 'CL': 47}`

## Runtime Environment

- Python: 3.9.6
- Platform: macOS-26.2-arm64-arm-64bit
- Machine: arm64
- Package snapshot: `environment/pip_freeze.txt`
- Frozen conda-style environment: `environment/conda_env_frozen.yml`

## Generated Output Counts

- Tables: 14
- Figures: 3
- Descriptive artifacts: 25
- Diagnostic artifacts: 36
- Qualitative artifacts: 7
- RQ1 artifacts: 5
- PDF table exports: 41

## Verification Status

- Status: generated; run `make verify` for validation
- Expected-output rules: `replication/expected_outputs.yaml`
- Validation script: `replication/verify_outputs.py`

## Notes on Determinism

Most outputs are deterministic given the provided processed dataset. Some robustness
checks involving holdout resampling use the seed in `replication/run_config.yaml`.
Small numerical differences may occur across platform/library versions for regression
standard errors and floating-point optimization routines.
