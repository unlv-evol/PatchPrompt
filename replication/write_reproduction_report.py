from __future__ import annotations
"""Create a concise reproduction report for artifact evaluators."""
import json, time
from pathlib import Path
import pandas as pd


def _count_files(path: Path, suffixes: tuple[str, ...]) -> int:
    if not path.exists():
        return 0
    return sum(1 for p in path.rglob("*") if p.is_file() and p.suffix.lower() in suffixes)


def write_report(root: Path, verification_status: str = "not run") -> None:
    dataset = root / "dataset" / "processed" / "final_analysis_dataset.csv"
    n = "unknown"
    classes = "unknown"
    if dataset.exists():
        df = pd.read_csv(dataset)
        n = len(df)
        if "Outcome_Class" in df.columns:
            classes = df["Outcome_Class"].value_counts().to_dict()
    runtime_json = root / "results" / "runtime" / "runtime_environment.json"
    runtime = {}
    if runtime_json.exists():
        runtime = json.loads(runtime_json.read_text(encoding="utf-8"))
    md = f"""# Reproduction Report

Generated: {time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())}

## Dataset

- Canonical dataset: `dataset/processed/final_analysis_dataset.csv`
- Observations: {n}
- Outcome-class counts: `{classes}`

## Runtime Environment

- Python: {runtime.get('python_version', 'unknown')}
- Platform: {runtime.get('platform', 'unknown')}
- Machine: {runtime.get('machine', 'unknown')}
- Package snapshot: `environment/pip_freeze.txt`
- Frozen conda-style environment: `environment/conda_env_frozen.yml`

## Generated Output Counts

- Tables: {_count_files(root / 'results' / 'tables', ('.csv',))}
- Figures: {_count_files(root / 'results' / 'figures', ('.png',))}
- Descriptive artifacts: {_count_files(root / 'results' / 'descriptive', ('.csv', '.md', '.png'))}
- Diagnostic artifacts: {_count_files(root / 'results' / 'diagnostics', ('.csv', '.md', '.png'))}
- Qualitative artifacts: {_count_files(root / 'results' / 'qualitative', ('.csv', '.md'))}
- RQ1 artifacts: {_count_files(root / 'results' / 'rq1', ('.csv', '.md'))}
- PDF table exports: {_count_files(root / 'results' / 'paper_tables_pdf', ('.pdf',))}

## Verification Status

- Status: {verification_status}
- Expected-output rules: `replication/expected_outputs.yaml`
- Validation script: `replication/verify_outputs.py`

## Notes on Determinism

Most outputs are deterministic given the provided processed dataset. Some robustness
checks involving holdout resampling use the seed in `replication/run_config.yaml`.
Small numerical differences may occur across platform/library versions for regression
standard errors and floating-point optimization routines.
"""
    (root / "results" / "reproduction_report.md").write_text(md, encoding="utf-8")


if __name__ == "__main__":
    write_report(Path(__file__).resolve().parent.parent, verification_status="generated")
