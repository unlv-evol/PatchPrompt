from __future__ import annotations
"""Extract paper-referenced illustrative qualitative cases.

The paper uses selected cases in the Stage-Based Modeling section to illustrate
mechanisms behind the quantitative results. This script retrieves the full records
for those examples from the canonical processed dataset and writes them as a
traceable qualitative evidence artifact.
"""
import argparse
from pathlib import Path
import pandas as pd
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from RQ2_Prompt_Effectiveness_Modeling.analysis.common import load_analysis_dataset, write_csv

ILLUSTRATIVE_CASES = [
    {
        "Case ID": "PN-19",
        "Paper_Section": "4.3.1 Gate 0: Code Generation",
        "Gate_or_Axis": "Gate 0",
        "Illustrative_Role": "Implementation-oriented prompt enabling code generation despite non-adoption",
        "Paper_Label": "Implementation-oriented prompts enabling code generation",
        "Paper_Interpretation": "A bounded implementation objective can elicit actionable code even when verification remains lightweight and the generated code is not ultimately adopted.",
    },
    {
        "Case ID": "NE-3",
        "Paper_Section": "4.3.1 Gate 0: Code Generation",
        "Gate_or_Axis": "Gate 0",
        "Illustrative_Role": "Conceptual/naming-oriented prompt limiting code generation",
        "Paper_Label": "Conceptual and naming-oriented prompts often limit code generation",
        "Paper_Interpretation": "Technical domain context alone is insufficient when the prompt does not request a bounded implementation artifact.",
    },
    {
        "Case ID": "PA-22",
        "Paper_Section": "4.3.2 Gate 1: Code Adoption",
        "Gate_or_Axis": "Gate 1",
        "Illustrative_Role": "Explicit constraints and observable correctness supporting adoption",
        "Paper_Label": "Explicit constraints and observable correctness enabling code adoption",
        "Paper_Interpretation": "High specificity and explicit verification cues make generated code easier to evaluate and trust for adoption.",
    },
    {
        "Case ID": "PN-19",
        "Paper_Section": "4.3.2 Gate 1: Code Adoption",
        "Gate_or_Axis": "Gate 1",
        "Illustrative_Role": "Generated but weakly evaluable code limiting adoption",
        "Paper_Label": "Generated but weakly evaluable code limiting adoption",
        "Paper_Interpretation": "A prompt can generate plausible code but still provide insufficient acceptance conditions for confident integration.",
    },
    {
        "Case ID": "PA-78",
        "Paper_Section": "4.3.3 Gate 2: Integration Depth",
        "Gate_or_Axis": "Gate 2",
        "Illustrative_Role": "Strong contextual grounding enabling deep integration",
        "Paper_Label": "Strong contextual grounding enabling deep integration",
        "Paper_Interpretation": "Rich surrounding implementation context aligns the generated solution with the existing codebase, supporting deeper reuse.",
    },
    {
        "Case ID": "PA-24",
        "Paper_Section": "4.3.3 Gate 2: Integration Depth",
        "Gate_or_Axis": "Gate 2",
        "Illustrative_Role": "High specificity without sufficient contextual grounding limiting integration depth",
        "Paper_Label": "High specificity without contextual grounding limiting integration depth",
        "Paper_Interpretation": "A highly specific prompt can still produce generic output when the surrounding implementation context is weak, resulting in limited reuse.",
    },
]


def run(root: Path) -> pd.DataFrame:
    df = load_analysis_dataset(root).copy()
    df = df.rename(columns={"Case_ID": "Case ID"}) if "Case_ID" in df.columns and "Case ID" not in df.columns else df
    metadata = pd.DataFrame(ILLUSTRATIVE_CASES)
    examples = metadata.merge(df, on="Case ID", how="left", validate="many_to_one")
    missing = examples[examples["PR_Link"].isna()]["Case ID"].tolist() if "PR_Link" in examples else []
    if missing:
        raise ValueError(f"Illustrative case IDs not found in canonical dataset: {missing}")

    # Normalize the PQS column name for the qualitative evidence artifact while preserving other fields.
    if "PQS " in examples.columns and "PQS" not in examples.columns:
        examples = examples.rename(columns={"PQS ": "PQS"})

    out_dir = root / "RQ2_Prompt_Effectiveness_Modeling" / "results" / "qualitative"
    out_dir.mkdir(parents=True, exist_ok=True)
    write_csv(examples, out_dir / "illustrative_examples_dataset.csv")

    manifest = pd.DataFrame([
        {"artifact": "illustrative_examples_dataset.csv", "description": "Full canonical records for paper-referenced illustrative qualitative examples", "case_count": len(examples), "unique_cases": examples["Case ID"].nunique()},
    ])
    write_csv(manifest, out_dir / "illustrative_case_manifest.csv")
    return examples


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Extract paper-referenced illustrative qualitative examples.")
    parser.add_argument("--root", default=".", help="Replication package root directory")
    args = parser.parse_args()
    run(Path(args.root).resolve())
