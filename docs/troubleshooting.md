# Troubleshooting

This guide lists common issues that may arise while running the replication package.

## `make reproduce` cannot find the dataset

Check that the following file exists:

```text
dataset/processed/final_analysis_dataset.csv
```

The canonical downstream analysis starts from this cleaned dataset.

## RQ1 scripts cannot find annotation files

Check that these files exist:

```text
annotation/validation/human_gold_annotations.csv
annotation/validation/llm_annotations_v1_combined.csv
```

These files are required to reproduce Section 4.1 agreement metrics and annotation policy tables.

## Dependency installation fails

Try installing from the pinned lockfile:

```bash
pip install -r requirements-lock.txt
```

If that fails, create a fresh virtual environment:

```bash
python -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements-lock.txt
```

On Windows, use WSL or Docker if package compilation fails.

## Makefile exits with unsupported Python version

The Makefile now checks the Python interpreter version before `setup`, `reproduce`, `verify`, and `smoke`.
Supported range is Python 3.9 to 3.12.

Run with an explicit interpreter, for example:

```bash
make PYTHON=python3.11 smoke
```

or install dependencies with the same interpreter:

```bash
python3.11 -m pip install -r requirements-lock.txt
```

## `make PYTHON=python3.11 ...` fails with `No such file or directory`

Your shell may not have a `python3.11` executable on PATH. Use one of:

```bash
make PYTHON=.venv/bin/python reproduce
make PYTHON=.venv/bin/python verify
```

or use a discovered Python path directly:

```bash
make PYTHON=/usr/bin/python3 reproduce
make PYTHON=/usr/bin/python3 verify
```

## Notebook execution fails

The notebooks are explanatory walkthroughs. The canonical reproduction path is the script-based pipeline:

```bash
make reproduce
make verify
```

If a notebook fails, first confirm the corresponding script succeeds.

## Matplotlib figure export fails

Confirm the output directory exists:

```text
results/figures/
```

The scripts should create missing directories automatically, but permission issues can prevent writing.

## PDF table export fails with `No module named reportlab`

The table preview exporter requires ReportLab. Install pinned dependencies:

```bash
pip install -r requirements-lock.txt
```

If you are using an existing environment, upgrade/install ReportLab explicitly:

```bash
pip install "reportlab>=4.2,<5"
```

## LaTeX output looks different

Generated LaTeX tables are intended to reproduce values and structure, not necessarily exact final camera-ready formatting. Minor formatting differences can be adjusted in the paper source.

## Verification fails because an output is missing

Run:

```bash
make reproduce
```

then:

```bash
make verify
```

If the error persists, inspect:

```text
replication/expected_outputs.yaml
results/logs/reproduction.log
```

The expected-output manifest lists the files that verification checks.

## Verification fails due to numeric mismatch

Small differences can occur due to package versions or platform-specific floating-point behavior. Check whether the affected file uses exact hash validation or tolerance validation.

See:

```text
docs/output_validation.md
```

## Pandas or statsmodels version mismatch

If model summaries differ in formatting but not values, this is usually due to package-version differences. Use the pinned dependencies in `requirements-lock.txt` for closer reproduction.

## Survival model diagnostics fail

If a Cox-model dependency is unavailable, install the required survival-analysis package listed in the lockfile or run the Docker workflow.

## Raw artifact paths look nested

Some uploaded ZIP files may preserve their original top-level folder names. This is acceptable as long as the raw artifacts remain under:

```text
dataset/raw/github/
dataset/raw/chatgpt/
```

The processed-data pipeline does not depend on exact raw-folder nesting.

## Platform-specific path errors

Run commands from the repository root. Avoid spaces in cloned path names if using shell scripts on Windows.

## Still stuck?

Open these files first:

```text
results/logs/reproduction.log
results/logs/last_run_metadata.json
replication/run_config.yaml
replication/expected_outputs.yaml
```

They usually identify the missing path, dependency, or failed pipeline stage.
