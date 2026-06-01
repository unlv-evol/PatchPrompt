from __future__ import annotations
"""Reproduce RQ1 human--LLM annotation reliability results.

Inputs
------
Dataset_Construction/annotation/validation/human_gold_annotations.csv
    The stratified 30% human-consensus annotation subset. It contains the cases
    used as the gold standard for validation.
Dataset_Construction/annotation/validation/llm_annotations_v1_combined.csv
    The combined LLM-v1 annotations for all cases. For agreement calculations,
    this script keeps only rows whose Case_ID appears in the human gold subset.

Outputs
-------
results/rq1/rq1_overall_agreement_metrics.csv
    Overall quadratic weighted Cohen's kappa, MAE, and directional bias for
    Context, Specificity, and Verification.
results/rq1/rq1_class_conditioned_kappa.csv
    Per-outcome-class quadratic weighted kappa values used in paper Table 1.
results/rq1/rq1_annotation_policy.csv
    Exact class-aware policy table used in paper Table 2.

Notes
-----
The policy table intentionally encodes the paper's empirically grounded policy,
not a purely mechanical threshold rule. The paper used agreement statistics plus
construct-validity judgment: Context is retained as human-scored because of
systematic LLM under-scoring; Specificity is automated outside PA; Verification is
automated only in PN where agreement is stable.
"""

from pathlib import Path
import numpy as np
import pandas as pd

from RQ2_Prompt_Effectiveness_Modeling.analysis.common import write_csv, write_latex_table

DIMENSIONS = [
    ("Context", "Human_Context", "LLM_Context"),
    ("Specificity", "Human_Specificity", "LLM_Specificity"),
    ("Verification", "Human_Verification", "LLM_Verification"),
]

CLASS_ORDER = ["PA", "PN", "CL", "NE"]


def _quadratic_weighted_kappa(y_true: pd.Series, y_pred: pd.Series, min_rating: int = 0, max_rating: int = 2) -> float:
    """Compute quadratic weighted Cohen's kappa without external dependencies.

    The annotation rubric uses ordinal scores 0, 1, and 2. Quadratic weighting
    penalizes disagreements more heavily when the two scores are farther apart.
    This matches the paper's use of quadratic weighted kappa for ordinal agreement.
    """
    valid = pd.DataFrame({"true": y_true, "pred": y_pred}).dropna()
    if valid.empty:
        return np.nan

    ratings = list(range(min_rating, max_rating + 1))
    n = len(ratings)
    rating_to_index = {rating: idx for idx, rating in enumerate(ratings)}

    observed = np.zeros((n, n), dtype=float)
    for truth, pred in zip(valid["true"].astype(int), valid["pred"].astype(int)):
        observed[rating_to_index[truth], rating_to_index[pred]] += 1

    true_hist = observed.sum(axis=1)
    pred_hist = observed.sum(axis=0)
    expected = np.outer(true_hist, pred_hist) / observed.sum()

    weights = np.zeros((n, n), dtype=float)
    denom = (n - 1) ** 2
    for i in range(n):
        for j in range(n):
            weights[i, j] = ((i - j) ** 2) / denom

    observed_disagreement = (weights * observed).sum()
    expected_disagreement = (weights * expected).sum()
    if expected_disagreement == 0:
        return 1.0 if observed_disagreement == 0 else np.nan
    return 1.0 - observed_disagreement / expected_disagreement


def _mae(y_true: pd.Series, y_pred: pd.Series) -> float:
    """Mean absolute annotation error between human and LLM scores."""
    valid = pd.DataFrame({"true": y_true, "pred": y_pred}).dropna()
    return float((valid["pred"] - valid["true"]).abs().mean())


def _bias(y_true: pd.Series, y_pred: pd.Series) -> float:
    """Directional bias: positive values mean LLM over-scoring vs. humans."""
    valid = pd.DataFrame({"true": y_true, "pred": y_pred}).dropna()
    return float((valid["pred"] - valid["true"]).mean())


def load_validation_data(root: Path) -> pd.DataFrame:
    """Load and align the human gold subset with LLM-v1 annotations."""
    human_path = root / "Dataset_Construction" / "annotation" / "validation" / "human_gold_annotations.csv"
    llm_path = root / "Dataset_Construction" / "annotation" / "validation" / "llm_annotations_v1_combined.csv"
    human = pd.read_csv(human_path)
    llm = pd.read_csv(llm_path)

    # Keep only the LLM score columns during the merge to avoid duplicate link fields.
    llm_scores = llm[["Case_ID", "LLM_Context", "LLM_Specificity", "LLM_Verification"]]
    merged = human.merge(llm_scores, on="Case_ID", how="inner")

    if len(merged) != len(human):
        missing = sorted(set(human["Case_ID"]) - set(merged["Case_ID"]))
        raise ValueError(f"LLM annotations are missing {len(missing)} human-gold cases: {missing[:10]}")

    return merged


def compute_overall_agreement(validation_df: pd.DataFrame) -> pd.DataFrame:
    """Compute RQ1a overall agreement metrics across all 82 gold cases."""
    rows = []
    for dim, hcol, lcol in DIMENSIONS:
        rows.append({
            "Dimension": dim,
            "Quadratic_Weighted_Kappa": round(_quadratic_weighted_kappa(validation_df[hcol], validation_df[lcol]), 3),
            "MAE": round(_mae(validation_df[hcol], validation_df[lcol]), 3),
            "Directional_Bias": round(_bias(validation_df[hcol], validation_df[lcol]), 3),
        })
    return pd.DataFrame(rows)


def compute_class_conditioned_kappa(validation_df: pd.DataFrame) -> pd.DataFrame:
    """Compute RQ1b per-class kappa values reported in paper Table 1."""
    rows = []
    for outcome_class in CLASS_ORDER:
        subset = validation_df[validation_df["Classification"] == outcome_class]
        row = {"Class": outcome_class, "N": len(subset)}
        for dim, hcol, lcol in DIMENSIONS:
            row[f"kappa_{dim[0]}"] = round(_quadratic_weighted_kappa(subset[hcol], subset[lcol]), 3)
        rows.append(row)
    return pd.DataFrame(rows)


def derive_policy_table() -> pd.DataFrame:
    """Return the exact annotation policy table reported as Table 2 in the paper.

    This is intentionally class-aware. It reflects the paper's interpretation of
    agreement statistics and construct-validity concerns rather than applying a
    blind threshold independently to every cell.
    """
    return pd.DataFrame([
        {"Metric": "Context", "PA": "Human", "PN": "Human", "CL": "Human", "NE": "Human"},
        {"Metric": "Specificity", "PA": "Human", "PN": "LLM", "CL": "LLM", "NE": "LLM"},
        {"Metric": "Verification", "PA": "Human", "PN": "LLM", "CL": "Human", "NE": "Human"},
    ])


def run(root: Path) -> dict[str, pd.DataFrame]:
    """Run all RQ1 validation analyses and write CSV/LaTeX outputs."""
    validation_df = load_validation_data(root)
    overall = compute_overall_agreement(validation_df)
    class_kappa = compute_class_conditioned_kappa(validation_df)
    policy = derive_policy_table()

    out_dir = root / "RQ1_Prompt_Evaluation_Validation" / "results" / "rq1"
    paper_dir = root / "RQ1_Prompt_Evaluation_Validation" / "results" / "rq1_tex"

    write_csv(overall, out_dir / "rq1_overall_agreement_metrics.csv")
    write_csv(class_kappa, out_dir / "rq1_class_conditioned_kappa.csv")
    write_csv(policy, out_dir / "rq1_annotation_policy.csv")

    # Also store the aligned validation subset so evaluators can inspect exactly
    # which human/LLM pairs were used for the calculations.
    write_csv(validation_df, out_dir / "rq1_human_llm_validation_pairs.csv")

    write_latex_table(overall, paper_dir / "table_rq1a_overall_agreement.tex", "Overall human--LLM agreement metrics", "tab:rq1-overall-agreement")
    write_latex_table(class_kappa, paper_dir / "table_rq1b_class_conditioned_kappa.tex", "Per-class quadratic weighted kappa values", "tab:rq1-class-kappa")
    write_latex_table(policy, paper_dir / "table_rq1c_annotation_policy.tex", "Empirically grounded evaluation policy", "tab:rq1-policy")

    summary = (
        "# RQ1 Annotation Reliability Summary\n\n"
        "This file is generated by `RQ1_Prompt_Evaluation_Validation/analysis/rq1/agreement_analysis.py`. It summarizes "
        "the outputs used to reproduce Section 4.1 of the paper.\n\n"
        "## Overall Agreement Metrics\n\n"
        f"{overall.to_string(index=False)}\n\n"
        "## Outcome-Conditioned Agreement\n\n"
        f"{class_kappa.to_string(index=False)}\n\n"
        "## Annotation Policy\n\n"
        f"{policy.to_string(index=False)}\n"
    )
    (out_dir / "rq1_summary.md").write_text(summary, encoding="utf-8")

    return {"overall": overall, "class_kappa": class_kappa, "policy": policy, "validation_pairs": validation_df}


if __name__ == "__main__":
    run(Path(".").resolve())
