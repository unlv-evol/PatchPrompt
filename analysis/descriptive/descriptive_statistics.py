from __future__ import annotations
"""Reproduce descriptive statistics reported in the paper.

This module generates the descriptive tables used in Section 4.2.1 and Appendix B:

* Table 3(a): Mean and standard deviation of Context, Specificity, and Verification.
* Table 3(b): Prompt Quality Score (PQS) by outcome class.
* Appendix Table 8: Overall PQS distribution.
* Appendix Table 9: Extended PQS statistics by outcome class.
* Appendix Table 10: Pull request size summary.
* Appendix Table 11: Top programming language counts.
* Appendix Table 12: Contributor experience summary.

The canonical input file is not modified. The helper ``load_analysis_dataset`` adds
runtime-only derived variables such as ``Repository`` and ``PQS`` while preserving the
original CSV exactly as provided.
"""

from pathlib import Path
import pandas as pd

from analysis.common import load_analysis_dataset, write_csv, write_latex_table

PAPER_CLASS_ORDER = ["PA", "CL", "PN", "NE"]
PROMPT_DIMENSIONS = ["Context", "Specificity", "Verification"]


def _round_df(df: pd.DataFrame, digits: int = 2) -> pd.DataFrame:
    """Round numeric columns while leaving labels unchanged."""
    out = df.copy()
    numeric_cols = out.select_dtypes(include="number").columns
    out[numeric_cols] = out[numeric_cols].round(digits)
    return out


def prompt_structure_summary(df: pd.DataFrame) -> pd.DataFrame:
    """Return Table 3(a): mean/std. dev. for C, S, and V."""
    summary = pd.DataFrame(
        [
            {"Statistic": "Mean", **{col: df[col].mean() for col in PROMPT_DIMENSIONS}},
            {"Statistic": "Std. Dev.", **{col: df[col].std() for col in PROMPT_DIMENSIONS}},
        ]
    )
    return _round_df(summary, 2)


def pqs_by_outcome(df: pd.DataFrame) -> pd.DataFrame:
    """Return Table 3(b): mean/median/count of PQS by outcome class."""
    grouped = (
        df.groupby("Outcome_Class")["PQS"]
        .agg(Mean="mean", Median="median", N="count")
        .reindex(PAPER_CLASS_ORDER)
        .reset_index()
        .rename(columns={"Outcome_Class": "Class"})
    )
    grouped["Mean"] = grouped["Mean"].round(2)
    grouped["Median"] = grouped["Median"].astype(int)
    grouped["N"] = grouped["N"].astype(int)
    return grouped


def pqs_distribution(df: pd.DataFrame) -> pd.DataFrame:
    """Return Appendix Table 8: overall PQS distribution."""
    q = df["PQS"].dropna()
    rows = [
        ("Mean", q.mean()),
        ("Median", q.median()),
        ("Std. Dev.", q.std()),
        ("Min", q.min()),
        ("25th Percentile", q.quantile(0.25)),
        ("75th Percentile", q.quantile(0.75)),
        ("Max", q.max()),
    ]
    return pd.DataFrame({"Statistic": [r[0] for r in rows], "Value": [round(float(r[1]), 2) for r in rows]})


def extended_pqs_by_outcome(df: pd.DataFrame) -> pd.DataFrame:
    """Return Appendix Table 9: extended PQS statistics by outcome class."""
    out = (
        df.groupby("Outcome_Class")["PQS"]
        .agg(Count="count", Mean="mean", Median="median", **{"Std. Dev.": "std"}, Max="max")
        .reindex(PAPER_CLASS_ORDER)
        .reset_index()
        .rename(columns={"Outcome_Class": "Class"})
    )
    out["Mean"] = out["Mean"].round(2)
    out["Std. Dev."] = out["Std. Dev."].round(2)
    for col in ["Count", "Median", "Max"]:
        out[col] = out[col].astype(int)
    return out


def pr_size_summary(df: pd.DataFrame) -> pd.DataFrame:
    """Return Appendix Table 10: summary statistics for PR size."""
    s = df["PR_Size"].dropna()
    iqr = s.quantile(0.75) - s.quantile(0.25)
    rows = [
        ("Mean", s.mean()),
        ("Median", s.median()),
        ("IQR", iqr),
        ("Max", s.max()),
    ]
    return pd.DataFrame({"Metric": [r[0] for r in rows], "Value": [round(float(r[1]), 2) for r in rows]})


def language_distribution(df: pd.DataFrame, top_n: int = 10) -> pd.DataFrame:
    """Return Appendix Table 11: top programming languages by count."""
    return (
        df["PR_Language"]
        .fillna("Unknown")
        .value_counts()
        .head(top_n)
        .rename_axis("Language")
        .reset_index(name="Count")
    )


def contributor_experience_summary(df: pd.DataFrame) -> pd.DataFrame:
    """Return Appendix Table 12: contributor experience summary."""
    s = df["Exp_Author_Repo"].dropna()
    rows = [
        ("Mean", s.mean()),
        ("Median", s.median()),
        ("Std. Dev.", s.std()),
        ("Skewness", s.skew()),
        ("Max", s.max()),
        ("Q1", s.quantile(0.25)),
        ("Q3", s.quantile(0.75)),
        ("IQR", s.quantile(0.75) - s.quantile(0.25)),
    ]
    return pd.DataFrame({"Metric": [r[0] for r in rows], "Value": [round(float(r[1]), 2) for r in rows]})


def write_combined_table3_tex(table3a: pd.DataFrame, table3b: pd.DataFrame, path: Path) -> None:
    """Write a paper-ready LaTeX table containing Table 3(a) and Table 3(b).

    The paper currently displays the two subtables side by side. This generated file
    keeps them in one LaTeX artifact while the CSV outputs remain separate for easier
    automated validation.
    """
    left = table3a.rename(columns={"Context": "C", "Specificity": "S", "Verification": "V"}).to_latex(index=False, escape=True)
    right = table3b.to_latex(index=False, escape=True)
    tex = rf"""\begin{{table}}[t]
\centering
\begin{{minipage}}{{0.45\linewidth}}
\centering
{left}
\vspace{{-0.75em}}
\caption*{{(a) Prompt structure (C, S, V)}}
\end{{minipage}}
\hfill
\begin{{minipage}}{{0.45\linewidth}}
\centering
{right}
\vspace{{-0.75em}}
\caption*{{(b) PQS by outcome class}}
\end{{minipage}}
\caption{{Prompt structure dimensions and PQS by outcome class.}}
\label{{tab:prompt-structure-pqs}}
\end{{table}}
"""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(tex, encoding="utf-8")


def run(root: Path) -> list[pd.DataFrame]:
    """Generate all descriptive CSV and LaTeX artifacts.

    Returns the generated dataframes so callers or notebooks can inspect them without
    re-reading files from disk.
    """
    df = load_analysis_dataset(root)

    table3a = prompt_structure_summary(df)
    table3b = pqs_by_outcome(df)
    appendix8 = pqs_distribution(df)
    appendix9 = extended_pqs_by_outcome(df)
    appendix10 = pr_size_summary(df)
    appendix11 = language_distribution(df)
    appendix12 = contributor_experience_summary(df)

    outputs = {
        "table_3a_prompt_structure.csv": table3a,
        "table_3b_pqs_by_outcome.csv": table3b,
        "appendix_table_8_pqs_distribution.csv": appendix8,
        "appendix_table_9_extended_pqs_by_outcome.csv": appendix9,
        "appendix_table_10_pr_size.csv": appendix10,
        "appendix_table_11_language_distribution.csv": appendix11,
        "appendix_table_12_contributor_experience.csv": appendix12,
    }
    for filename, table in outputs.items():
        write_csv(table, root / "results" / "tables" / filename)

    write_latex_table(table3a.rename(columns={"Context": "C", "Specificity": "S", "Verification": "V"}), root / "paper" / "tables" / "table_3a_prompt_structure.tex", "Prompt structure dimensions", "tab:prompt-structure")
    write_latex_table(table3b, root / "paper" / "tables" / "table_3b_pqs_by_outcome.tex", "PQS by outcome class", "tab:pqs-by-outcome")
    write_combined_table3_tex(table3a, table3b, root / "paper" / "tables" / "table_3_prompt_structure_and_pqs.tex")
    write_latex_table(appendix8, root / "paper" / "tables" / "appendix_table_8_pqs_distribution.tex", "Overall distribution of PQS", "tab:pqs-distribution")
    write_latex_table(appendix9, root / "paper" / "tables" / "appendix_table_9_extended_pqs_by_outcome.tex", "Extended PQS statistics by outcome class", "tab:extended-pqs-by-outcome")
    write_latex_table(appendix10, root / "paper" / "tables" / "appendix_table_10_pr_size.tex", "Summary statistics for PR size", "tab:pr-size-summary")
    write_latex_table(appendix11, root / "paper" / "tables" / "appendix_table_11_language_distribution.tex", "Top programming languages", "tab:language-distribution")
    write_latex_table(appendix12, root / "paper" / "tables" / "appendix_table_12_contributor_experience.tex", "Summary statistics for contributor experience", "tab:contributor-experience")

    return [table3a, table3b, appendix8, appendix9, appendix10, appendix11, appendix12]


if __name__ == "__main__":
    run(Path("."))
