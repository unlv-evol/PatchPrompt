from __future__ import annotations
"""Processed-dataset builder.

This preprocessing script reads the canonical final analysis dataset and creates
modeling views used by the rest of the replication pipeline. It intentionally keeps
the canonical CSV unchanged while deriving analysis-only fields from PR_Link and
Status.
"""
import argparse
from pathlib import Path
import sys
import pandas as pd
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from RQ2_Prompt_Effectiveness_Modeling.analysis.common import load_canonical_dataset, derive_analysis_dataset, write_csv, sha256_file


def run(root: Path):
    df = load_canonical_dataset(root)
    analysis = derive_analysis_dataset(df)
    write_csv(analysis, root / "Dataset_Construction" / "processed_data" / "gate_model_dataset.csv")
    write_csv(df[["Case ID", "PR_Link", "Conversation_Link", "Outcome_Class", "Context", "Specificity", "Verification", "Rationale", "PQS "]], root / "Dataset_Construction" / "processed_data" / "prompt_scores.csv")
    write_csv(df[["Case ID", "Outcome_Class", "Context", "Specificity", "Verification", "Rationale", "PR_Link", "Conversation_Link"]], root / "Dataset_Construction" / "processed_data" / "qualitative_dataset.csv")
    prov = root / "Dataset_Construction" / "provenance"
    prov.mkdir(parents=True, exist_ok=True)
    checksum = sha256_file(root / "Dataset_Construction" / "processed_data" / "final_analysis_dataset.csv")
    (prov / "checksums.sha256").write_text(f"{checksum}  Dataset_Construction/processed_data/final_analysis_dataset.csv\n", encoding="utf-8")
    manifest = pd.DataFrame([{
        "path": "Dataset_Construction/processed_data/final_analysis_dataset.csv",
        "role": "canonical cleaned downstream analysis dataset",
        "records": len(df),
        "columns": len(df.columns),
        "sha256": checksum,
        "notes": "Dataset is preserved as provided; Repository and PR_Number are derived from PR_Link; Merged/Closed are derived from Status."
    }])
    write_csv(manifest, prov / "data_manifest.csv")
    return analysis

if __name__ == "__main__":
    parser = argparse.ArgumentParser(); parser.add_argument("--root", default=".")
    run(Path(parser.parse_args().root).resolve())
