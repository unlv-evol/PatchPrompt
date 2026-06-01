# Data Lineage

The replication package uses the cleaned final downstream dataset as the canonical analysis artifact.

```text
PatchTrack validated corpus
    ↓
Prompt availability filtering
    ↓
Prompt extraction and case mapping
    ↓
Human/LLM prompt-quality scoring
    ↓
Merged PR metadata and lifecycle variables
    ↓
Dataset_Construction/processed_data/final_analysis_dataset.csv
    ↓
Derived modeling view: gate_model_dataset.csv
    ↓
Gate models, diagnostics, qualitative summaries, tables, and figures
```

## Dataset fidelity rule

The canonical dataset is not modified to add redundant metadata. Repository and PR number are derived from `PR_Link`; merged and closed indicators are derived from `Status`.
