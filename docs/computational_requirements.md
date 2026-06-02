# Computational Requirements

This document describes the expected environment for reproducing the replication package.

## Supported Platforms

The package is intended to run on:

- macOS
- Linux
- Windows with WSL or Docker

Docker is recommended for artifact evaluation when the evaluator wants to avoid local dependency conflicts.

## Python Version

Recommended:

```text
Python 3.11
```

The package includes:

```text
requirements.txt
requirements-lock.txt
environment.yml
```

`requirements-lock.txt` is the preferred dependency reference for strict reproduction.

## Hardware Requirements

Recommended minimum:

```text
CPU: 2 cores
RAM: 8 GB
Disk: 2 GB free space
```

Recommended for comfortable notebook execution:

```text
CPU: 4 cores
RAM: 16 GB
Disk: 5 GB free space
```

The analysis is not GPU-dependent.

## Runtime Expectations

Typical expected runtime on a standard laptop:

| Task | Expected Runtime |
|---|---:|
| Setup environment | 2–10 minutes |
| Full reproduction | under 5 minutes |
| Verification | under 1 minute |
| Notebook walkthroughs | variable, usually under 10 minutes total |

Runtime may vary depending on package installation speed and platform.

## Software Dependencies

Main Python libraries include:

- pandas
- numpy
- scipy
- statsmodels
- scikit-learn
- matplotlib
- lifelines or equivalent survival-analysis tooling, if installed
- jupyter / nbformat for notebook inspection or execution

The scripts are designed to rely on common scientific Python packages.

## Docker Use

To use Docker:

```bash
docker build -t patchprompt-replication .
docker run --rm patchprompt-replication
```

If Docker is unavailable, use:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements-lock.txt
make reproduce
make verify
```

## Memory and Storage Notes

The CSV datasets and generated outputs are small. The largest storage contribution may come from raw PDF artifacts in `Dataset_Construction/raw_data/chatgpt/`.

If storage is constrained, evaluators may inspect processed-data reproduction without opening every raw PDF.

## Reproducibility Environment Assumptions

The default reproduction pipeline assumes:

- all required processed datasets are present,
- annotation validation datasets are present,
- no external API calls are required,
- no GitHub credentials are required,
- no ChatGPT access is required,
- the current working directory is the repository root.

## Generated Run Metadata

Each run records metadata in:

```text
RQ2_Prompt_Effectiveness_Modeling/results/logs/last_run_metadata.json
```

This file captures environment information, timestamps, and configuration details useful for debugging and artifact review.

## Container and CI Requirements

The package includes a Dockerfile and `docker-compose.yml` for containerized reproduction. A GitHub Actions smoke workflow is provided for CI environments. The smoke workflow is intended to verify installation, the smoke reproduction path, and expected output presence rather than to serve as a full performance benchmark.

Runtime benchmark outputs are written to `RQ2_Prompt_Effectiveness_Modeling/results/runtime/` after a full reproduction run.
