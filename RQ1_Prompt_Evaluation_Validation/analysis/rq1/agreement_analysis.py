from __future__ import annotations
"""Reproduce RQ1 annotation agreement and validation results.

This module reproduces two complementary RQ1 analyses:

1. Human--human inter-rater reliability on the independently annotated,
   pre-discussion 30% stratified sample. This analysis compares the two human
   annotator CSVs for Context, Specificity, and Verification and exports
   per-prompt agreement records, disagreements-only records, and summary metrics.

2. Human--LLM annotation reliability using the reconciled human gold-standard
   subset and LLM-v1 annotations. This reproduces the overall agreement metrics,
   class-conditioned kappa values, and class-aware annotation policy reported in
   the paper.

Inputs
------
Dataset_Construction/annotation/validation/human_annotations/human_annotation_<CLASS>_<ANNOTATOR>.csv
    Independent pre-reconciliation human annotations for CL, PN, PA, and NE.
Dataset_Construction/annotation/validation/human_gold_annotations.csv
    The stratified 30% human-consensus annotation subset. It contains the cases
    used as the gold standard for human--LLM validation.
Dataset_Construction/annotation/validation/llm_annotations_v1_combined.csv
    The combined LLM-v1 annotations for all cases. For agreement calculations,
    this script keeps only rows whose Case_ID appears in the human gold subset.

Outputs
-------
results/rq1/rq1_human_human_agreement_records.csv
    One row per category, case, and rubric dimension comparing both annotators.
results/rq1/rq1_human_human_disagreements.csv
    Subset of the above file containing only human--human disagreements.
results/rq1/rq1_human_human_agreement_metrics.csv
    Human--human percent agreement, Cohen's kappa, and quadratic weighted
    Cohen's kappa by category and dimension.
results/rq1/rq1_overall_agreement_metrics.csv
    Overall human--LLM quadratic weighted Cohen's kappa, MAE, and directional
    bias for Context, Specificity, and Verification.
results/rq1/rq1_class_conditioned_kappa.csv
    Per-outcome-class human--LLM quadratic weighted kappa values used in the
    paper.
results/rq1/rq1_annotation_policy.csv
    Exact class-aware policy table used in the paper.

Notes
-----
Human--human agreement is measured before discussion, reconciliation, or senior
adjudication. Human annotators were blinded to LLM-generated labels during both
independent annotation and adjudication.
"""

from pathlib import Path
import numpy as np
import pandas as pd

from RQ2_Prompt_Effectiveness_Modeling.analysis.common import write_csv, write_latex_table

HUMAN_DIMENSIONS = ["Context", "Specificity", "Verification"]
DIMENSIONS = [
    ("Context", "Human_Context", "LLM_Context"),
    ("Specificity", "Human_Specificity", "LLM_Specificity"),
    ("Verification", "Human_Verification", "LLM_Verification"),
]

CLASS_ORDER = ["PA", "PN", "CL", "NE"]
HUMAN_ANNOTATORS = ("richard", "daniel")


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


def _cohen_kappa(y_true: pd.Series, y_pred: pd.Series, min_rating: int = 0, max_rating: int = 2) -> float:
    """Compute unweighted Cohen's kappa without external dependencies."""
    valid = pd.DataFrame({"true": y_true, "pred": y_pred}).dropna()
    if valid.empty:
        return np.nan

    ratings = list(range(min_rating, max_rating + 1))
    n = len(ratings)
    rating_to_index = {rating: idx for idx, rating in enumerate(ratings)}

    observed = np.zeros((n, n), dtype=float)
    for truth, pred in zip(valid["true"].astype(int), valid["pred"].astype(int)):
        observed[rating_to_index[truth], rating_to_index[pred]] += 1

    total = observed.sum()
    observed_agreement = np.trace(observed) / total
    expected = np.outer(observed.sum(axis=1), observed.sum(axis=0)) / total
    expected_agreement = np.trace(expected) / total
    if expected_agreement == 1:
        return 1.0 if observed_agreement == 1 else np.nan
    return (observed_agreement - expected_agreement) / (1 - expected_agreement)


def _mae(y_true: pd.Series, y_pred: pd.Series) -> float:
    """Mean absolute annotation error between human and LLM scores."""
    valid = pd.DataFrame({"true": y_true, "pred": y_pred}).dropna()
    return float((valid["pred"] - valid["true"]).abs().mean())


def _bias(y_true: pd.Series, y_pred: pd.Series) -> float:
    """Directional bias: positive values mean LLM over-scoring vs. humans."""
    valid = pd.DataFrame({"true": y_true, "pred": y_pred}).dropna()
    return float((valid["pred"] - valid["true"]).mean())


def _read_human_annotation(path: Path, annotator: str, category: str) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(f"Missing human annotation file: {path}")

    df = pd.read_csv(path)
    if "Case ID" not in df.columns:
        raise ValueError(f"{path} is missing required column 'Case ID'")

    keep_cols = ["Case ID", "PR_Link", "Conversation_Link", "Classification", *HUMAN_DIMENSIONS]
    missing = [c for c in keep_cols if c not in df.columns]
    if missing:
        raise ValueError(f"{path} is missing required columns: {missing}")

    out = df[keep_cols].copy()
    out = out[out["Case ID"].notna()].copy()
    out["Case ID"] = out["Case ID"].astype(str).str.strip()
    out = out[out["Case ID"].ne("")].copy()
    out = out.dropna(subset=HUMAN_DIMENSIONS, how="any")
    out["Classification"] = out["Classification"].fillna(category).astype(str).str.strip()

    rename = {dim: f"{annotator}_{dim}" for dim in HUMAN_DIMENSIONS}
    out = out.rename(columns=rename)
    for dim in HUMAN_DIMENSIONS:
        out[f"{annotator}_{dim}"] = pd.to_numeric(out[f"{annotator}_{dim}"], errors="coerce")

    out = out.dropna(subset=[f"{annotator}_{dim}" for dim in HUMAN_DIMENSIONS], how="any")
    return out


def load_human_human_annotations(root: Path) -> pd.DataFrame:
    """Load and align independent human annotations for all prompt categories."""
    annotation_dir = root / "Dataset_Construction" / "annotation" / "validation" / "human_annotations"
    aligned = []

    for category in CLASS_ORDER:
        richard_path = annotation_dir / f"human_annotation_{category}_richard.csv"
        daniel_path = annotation_dir / f"human_annotation_{category}_daniel.csv"
        richard = _read_human_annotation(richard_path, "richard", category)
        daniel = _read_human_annotation(daniel_path, "daniel", category)

        daniel_scores = daniel[["Case ID", *[f"daniel_{dim}" for dim in HUMAN_DIMENSIONS]]]
        merged = richard.merge(daniel_scores, on="Case ID", how="inner")
        if merged.empty:
            raise ValueError(f"No overlapping cases found for category {category}")
        merged["Classification"] = category
        aligned.append(merged)

    return pd.concat(aligned, ignore_index=True)


def compute_human_human_agreement_records(human_df: pd.DataFrame) -> pd.DataFrame:
    """Create one row per category/case/dimension human--human comparison."""
    rows = []
    for _, row in human_df.iterrows():
        for dim in HUMAN_DIMENSIONS:
            score_1 = row[f"richard_{dim}"]
            score_2 = row[f"daniel_{dim}"]
            rows.append({
                "Category": row["Classification"],
                "Case_ID": row["Case ID"],
                "PR_Link": row.get("PR_Link"),
                "Conversation_Link": row.get("Conversation_Link"),
                "Dimension": dim,
                "Annotator_1": "Richard",
                "Annotator_2": "Daniel",
                "Annotator_1_Score": int(score_1),
                "Annotator_2_Score": int(score_2),
                "Agreement": bool(score_1 == score_2),
                "Score_Difference": int(score_1 - score_2),
                "Absolute_Difference": int(abs(score_1 - score_2)),
                "Measured_Before_Discussion": True,
            })
    return pd.DataFrame(rows)


def compute_human_human_agreement_metrics(records: pd.DataFrame) -> pd.DataFrame:
    """Compute human--human reliability metrics by category and dimension."""
    rows = []
    for category in CLASS_ORDER:
        for dim in HUMAN_DIMENSIONS:
            subset = records[(records["Category"] == category) & (records["Dimension"] == dim)]
            n = len(subset)
            agreements = int(subset["Agreement"].sum())
            disagreements = int(n - agreements)
            rows.append({
                "Category": category,
                "Dimension": dim,
                "N": n,
                "Agreements": agreements,
                "Disagreements": disagreements,
                "Percent_Agreement": round(agreements / n * 100, 1) if n else np.nan,
                "Cohens_Kappa": round(_cohen_kappa(subset["Annotator_1_Score"], subset["Annotator_2_Score"]), 3),
                "Quadratic_Weighted_Kappa": round(_quadratic_weighted_kappa(subset["Annotator_1_Score"], subset["Annotator_2_Score"]), 3),
                "Measured_Before_Discussion": True,
            })
    return pd.DataFrame(rows)


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
    """Compute RQ1a overall human--LLM agreement metrics across all gold cases."""
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
    """Compute RQ1b per-class human--LLM kappa values reported in the paper."""
    rows = []
    for outcome_class in CLASS_ORDER:
        subset = validation_df[validation_df["Classification"] == outcome_class]
        row = {"Class": outcome_class, "N": len(subset)}
        for dim, hcol, lcol in DIMENSIONS:
            row[f"kappa_{dim[0]}"] = round(_quadratic_weighted_kappa(subset[hcol], subset[lcol]), 3)
        rows.append(row)
    return pd.DataFrame(rows)


def derive_policy_table() -> pd.DataFrame:
    """Return the exact annotation policy table reported in the paper.

    This is intentionally class-aware. It reflects the paper's interpretation of
    agreement statistics and construct-validity concerns rather than applying a
    blind threshold independently to every cell.
    """
    return pd.DataFrame([
        {"Metric": "Context", "PA": "Human", "PN": "Human", "CL": "Human", "NE": "Human"},
        {"Metric": "Specificity", "PA": "Human", "PN": "LLM", "CL": "LLM", "NE": "LLM"},
        {"Metric": "Verification", "PA": "Human", "PN": "LLM", "CL": "Human", "NE": "Human"},
    ])


def _markdown_table(
    df: pd.DataFrame,
    *,
    headers: dict[str, str] | None = None,
    formatters: dict[str, callable] | None = None,
) -> str:
    """Render a dataframe as stable pipe-table markdown for the summary file."""
    display_df = df.copy()

    if formatters:
        for column, formatter in formatters.items():
            if column in display_df.columns:
                display_df[column] = display_df[column].map(lambda value: "" if pd.isna(value) else formatter(value))

    if headers:
        display_df = display_df.rename(columns=headers)

    header_row = "| " + " | ".join(str(column) for column in display_df.columns) + " |"
    separator_row = "|" + "|".join("---" for _ in display_df.columns) + "|"

    body_rows = []
    for row in display_df.itertuples(index=False, name=None):
        body_rows.append("| " + " | ".join(str(value) for value in row) + " |")

    return "\n".join([header_row, separator_row, *body_rows])


def _write_human_human_readme(out_dir: Path) -> None:
    readme = """# RQ1 Human--Human Inter-Rater Agreement Artifacts

This directory includes derived human--human reliability outputs generated by
`RQ1_Prompt_Evaluation_Validation/analysis/rq1/agreement_analysis.py` from the
independent human annotation CSVs in
`Dataset_Construction/annotation/validation/human_annotations/`.

## Files

- `rq1_human_human_agreement_records.csv`: one row per prompt, category, and rubric
  dimension comparing Richard and Daniel's independent scores.
- `rq1_human_human_disagreements.csv`: subset of records where the two human
  annotators assigned different scores.
- `rq1_human_human_agreement_metrics.csv`: category-by-dimension summary including
  number of prompts, agreements, disagreements, percent agreement, Cohen's kappa,
  and quadratic weighted Cohen's kappa.

Agreement was measured before discussion, reconciliation, or senior adjudication.
Human annotators were blinded to LLM-generated labels during annotation and
adjudication.
"""
    (out_dir / "README_human_human_agreement.md").write_text(readme, encoding="utf-8")


def run(root: Path) -> dict[str, pd.DataFrame]:
    """Run all RQ1 validation analyses and write CSV/LaTeX outputs."""
    out_dir = root / "RQ1_Prompt_Evaluation_Validation" / "results" / "rq1"
    paper_dir = root / "RQ1_Prompt_Evaluation_Validation" / "results" / "rq1_tex"

    human_human_df = load_human_human_annotations(root)
    human_human_records = compute_human_human_agreement_records(human_human_df)
    human_human_disagreements = human_human_records[~human_human_records["Agreement"]].copy()
    human_human_metrics = compute_human_human_agreement_metrics(human_human_records)

    validation_df = load_validation_data(root)
    overall = compute_overall_agreement(validation_df)
    class_kappa = compute_class_conditioned_kappa(validation_df)
    policy = derive_policy_table()

    write_csv(human_human_records, out_dir / "rq1_human_human_agreement_records.csv")
    write_csv(human_human_disagreements, out_dir / "rq1_human_human_disagreements.csv")
    write_csv(human_human_metrics, out_dir / "rq1_human_human_agreement_metrics.csv")
    _write_human_human_readme(out_dir)

    write_csv(overall, out_dir / "rq1_overall_agreement_metrics.csv")
    write_csv(class_kappa, out_dir / "rq1_class_conditioned_kappa.csv")
    write_csv(policy, out_dir / "rq1_annotation_policy.csv")

    # Also store the aligned validation subset so evaluators can inspect exactly
    # which human/LLM pairs were used for the calculations.
    write_csv(validation_df, out_dir / "rq1_human_llm_validation_pairs.csv")

    write_latex_table(overall, paper_dir / "table_rq1a_overall_agreement.tex", "Overall human--LLM agreement metrics", "tab:rq1-overall-agreement")
    write_latex_table(class_kappa, paper_dir / "table_rq1b_class_conditioned_kappa.tex", "Per-class quadratic weighted kappa values", "tab:rq1-class-kappa")
    write_latex_table(policy, paper_dir / "table_rq1c_annotation_policy.tex", "Empirically grounded evaluation policy", "tab:rq1-policy")

    human_human_table = _markdown_table(
        human_human_metrics,
        headers={
            "Percent_Agreement": "Percent Agreement",
            "Cohens_Kappa": "Cohen's Kappa",
            "Quadratic_Weighted_Kappa": "Quadratic Weighted Kappa",
            "Measured_Before_Discussion": "Measured Before Discussion",
        },
        formatters={
            "Percent_Agreement": lambda value: f"{value:.1f}",
            "Cohens_Kappa": lambda value: f"{value:.3f}",
            "Quadratic_Weighted_Kappa": lambda value: f"{value:.3f}",
        },
    )
    overall_table = _markdown_table(
        overall,
        headers={
            "Quadratic_Weighted_Kappa": "Quadratic Weighted Kappa",
            "Directional_Bias": "Directional Bias",
        },
        formatters={
            "Quadratic_Weighted_Kappa": lambda value: f"{value:.3f}",
            "MAE": lambda value: f"{value:.3f}",
            "Directional_Bias": lambda value: f"{value:.3f}",
        },
    )
    class_kappa_table = _markdown_table(
        class_kappa,
        formatters={
            "kappa_C": lambda value: f"{value:.3f}",
            "kappa_S": lambda value: f"{value:.3f}",
            "kappa_V": lambda value: f"{value:.3f}",
        },
    )
    policy_table = _markdown_table(policy)

    summary = (
        "# RQ1 Annotation Reliability Summary\n\n"
        "This file is generated by `RQ1_Prompt_Evaluation_Validation/analysis/rq1/agreement_analysis.py`. "
        "It summarizes the human--human reliability outputs and the human--LLM outputs used to reproduce Section 4.1 of the paper.\n\n"
        "## Human--Human Agreement Metrics\n\n"
        "Agreement was measured before discussion/reconciliation. Human annotators were blinded to LLM-generated labels.\n\n"
        f"{human_human_table}\n\n"
        "## Human--LLM Overall Agreement Metrics\n\n"
        f"{overall_table}\n\n"
        "## Human--LLM Outcome-Conditioned Agreement\n\n"
        f"{class_kappa_table}\n\n"
        "## Annotation Policy\n\n"
        f"{policy_table}\n"
    )
    (out_dir / "rq1_summary.md").write_text(summary, encoding="utf-8")

    return {
        "human_human_records": human_human_records,
        "human_human_disagreements": human_human_disagreements,
        "human_human_metrics": human_human_metrics,
        "overall": overall,
        "class_kappa": class_kappa,
        "policy": policy,
        "validation_pairs": validation_df,
    }


if __name__ == "__main__":
    run(Path(".").resolve())
