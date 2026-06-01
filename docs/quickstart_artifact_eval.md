# 10-Minute Artifact Evaluation Path

1. Install dependencies:

```bash
python3.11 -m pip install -r requirements-lock.txt
```

2. Run smoke reproduction:

```bash
make PYTHON=python3.11 smoke
```

3. Check outputs:

```bash
ls RQ2_Prompt_Effectiveness_Modeling/results/tables RQ2_Prompt_Effectiveness_Modeling/results/diagnostics RQ2_Prompt_Effectiveness_Modeling/results/figures RQ2_Prompt_Effectiveness_Modeling/results/qualitative
cat RQ2_Prompt_Effectiveness_Modeling/results/logs/last_run_metadata.json
```

Expected success message:

```text
All expected replication outputs verified successfully.
```

Notes:

- Smoke mode skips methodological-alignment sensitivity models to keep evaluator runs fast.
- PDF previews under `RQ2_Prompt_Effectiveness_Modeling/results/paper_tables_pdf/` are rendered tables generated from CSV outputs (not raw LaTeX source text).
- The Makefile enforces a supported interpreter range (Python 3.9 to 3.12) and prints a hint if an unsupported interpreter is used.
